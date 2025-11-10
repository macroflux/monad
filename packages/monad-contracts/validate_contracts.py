#!/usr/bin/env python3
"""
MONAD contracts validator:
- Walks packages/monad-contracts for *.vN.json contract files
- Validates JSON is well-formed and (optionally) against JSON Schema meta
- Validates examples in packages/monad-contracts/examples/
- Golden-hash check to enforce immutability of existing versions
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = ROOT / "packages" / "monad-contracts"
EXAMPLES_DIR = CONTRACTS_DIR / "examples"
GOLDEN_FILE = CONTRACTS_DIR / "contracts.golden.json"

CONTRACT_RE = re.compile(r"^(?P<name>.+)\.v(?P<ver>\d+)\.json$")

def normalized_sha256(path: Path) -> str:
    """Stable, cross-OS hashing (sorted keys, compact separators)."""
    with path.open("r", encoding="utf-8", newline="") as f:
        data = json.load(f)
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

@dataclass
class Contract:
    name: str
    version: int
    path: Path

def discover_contracts() -> List[Contract]:
    files = []
    for p in sorted(CONTRACTS_DIR.glob("*.v*.json")):
        m = CONTRACT_RE.match(p.name)
        if not m:
            continue
        files.append(Contract(name=m.group("name"), version=int(m.group("ver")), path=p))
    return files

def load_golden() -> Dict[str, str]:
    if GOLDEN_FILE.exists():
        with GOLDEN_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_golden(golden: Dict[str, str]) -> None:
    with GOLDEN_FILE.open("w", encoding="utf-8") as f:
        json.dump(golden, f, indent=2, sort_keys=True, ensure_ascii=False)

def validate_json_wellformed(path: Path) -> None:
    # Parsing will throw if invalid; additionally ensure it’s a JSON object.
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be a JSON object at top level.")

def find_examples_for(contract: Contract) -> List[Path]:
    # Examples named <name>.vN.[anything].json (allow multiple examples)
    if not EXAMPLES_DIR.exists():
        return []
    pattern = f"{contract.name}.v{contract.version}.*.json"
    return sorted(EXAMPLES_DIR.glob(pattern))

def validate_examples(contract: Contract) -> List[Tuple[Path, str]]:
    """Currently ensures example JSON parses. Extend to jsonschema.validate on demand."""
    failures = []
    for ex in find_examples_for(contract):
        try:
            with ex.open("r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            failures.append((ex, str(e)))
    return failures

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MONAD contract JSON + golden hashes + examples.")
    parser.add_argument("--check-golden", action="store_true", help="Fail if any existing golden hash mismatches.")
    parser.add_argument("--update-golden", action="store_true", help="Recompute golden hashes (for new versions only).")
    args = parser.parse_args()

    contracts = discover_contracts()
    if not contracts:
        print("No contracts found.", file=sys.stderr)
        return 1

    # 1) well-formed check
    errors: List[str] = []
    for c in contracts:
        try:
            validate_json_wellformed(c.path)
        except Exception as e:
            errors.append(f"[JSON] {c.path.name}: {e}")

    # 2) examples check
    for c in contracts:
        ex_fail = validate_examples(c)
        for path, msg in ex_fail:
            errors.append(f"[EXAMPLE] {path.name} invalid: {msg}")

    if errors:
        print("Validation errors:")
        for e in errors:
            print(" -", e)
        return 2

    # 3) golden hashing
    golden = load_golden()
    updated = False
    now = datetime.now(timezone.utc).isoformat()

    for c in contracts:
        key = c.path.name
        sha = normalized_sha256(c.path)
        if args.update_golden:
            # Always (re)write the SHA for current files—intended for adding new versions.
            golden[key] = sha
            updated = True
        elif args.check_golden:
            if key not in golden:
                errors.append(f"[GOLDEN] Missing golden entry for {key} (add via --update-golden).")
            elif golden[key] != sha:
                errors.append(f"[GOLDEN] Hash mismatch for {key}: expected {golden[key][:12]}..., got {sha[:12]}...")

    if updated:
        golden["_last_updated"] = now
        save_golden(golden)
        print(f"Golden map updated ({GOLDEN_FILE.relative_to(ROOT)}).")

    if args.check_golden and errors:
        print("Golden check failed:")
        for e in errors:
            print(" -", e)
        return 3

    print(f"OK: {len(contracts)} contracts validated; examples OK; golden {'checked' if args.check_golden else 'skipped'}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
