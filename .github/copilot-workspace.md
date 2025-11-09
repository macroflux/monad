# Copilot Workspace Context — MONAD Omnibus

**Prime Directive:** Generate code and docs that strengthen the MONAD charter without drifting. Favor *molecules* (small, composable units) with clear contracts, tests, and telemetry.

## Repository Mission (for Copilot)
- Unify AI/robotics/simulation/hardware work under shared contracts and patterns.
- Every contribution must be measurable (metrics), reproducible (run ledger), and reviewable (ADRs).

## Guardrails
- **Do NOT modify** `docs/charter.md` or any *Accepted* ADR. Propose a new ADR or supersede instead.
- **Contracts are versioned.** If a schema changes, create `*.v2.json` (do not edit `*.v1.json`) and add golden tests.
- **Safety-first.** Control code must include threshold checks, watchdogs, and an e-stop pathway.
- **Telemetry by default.** Emit metrics/events for new molecules.

## Branch Policy
- `main`: protected, release-quality only
- `dev`: integration
- `feat/*`: implementation tracks (scoped, testable)
- `exp/*`: research sandboxes (documented in run ledgers)

## File & Folder Conventions
- Contracts: `packages/monad-contracts/<name>.vX.json`
- Telemetry utilities: `packages/monad-telemetry/`
- Services (FastAPI, etc.): `services/<service-name>/`
- Unity assets: `unity/`
- ADRs: `docs/adr/ADR-XXXX-<slug>.md`
- Templates: `docs/templates/`

## Required Artifacts per Molecule
- Molecule Spec in PR (`docs/templates/MOLECULE_SPEC.md` filled and included)
- Tests (unit/integration as applicable)
- Telemetry instrumentation (metrics + events)
- Demo script or short README with usage
- Run ledger artifact for experiments

## Commit & PR Conventions
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- PR title example: `feat(contracts): add imu.v2 schema and golden tests`
- Link ADR in PR description; include a brief decision note

## Test Expectations
- Validate JSON schemas (`packages/monad-contracts/validate_contracts.py`)
- Unit tests for services and libs (pytest or unittest)
- Sim/hardware shims should include a dry-run mode

## Examples (Generate on Request)
- **Validator:** Python CLI using `jsonschema` to validate all `*.json` contracts
- **Orchestrator:** FastAPI endpoints `/ticket` and `/execute` with Pydantic models
- **Actuator Bus:** `/actuate` endpoint logs accepted commands and state
- **Unity HUD:** C# script `RobotHUD.cs` shows yaw/pitch/roll/speed

## Prompts You Can Use (as Copilot Chat user)
- “Generate unit tests for `imu.v1.json` example frames.”
- “Create FastAPI service skeleton for `orchestrator-ren` with /ticket and /execute.”
- “Draft C# `RobotHUD.cs` to display IMU data pulled via UDP.”
- “Write golden-test scaffolding that fails if a schema is edited without a new version file.”

## Golden Tests — Rules
- If a contract file (`*.v1.json`) changes, tests must fail.
- New versions must ship with migration notes and validation samples.

## Safety Checklist (embed in PR template)
- [ ] Thresholds and e-stop paths implemented (where relevant)
- [ ] Input validation on external interfaces
- [ ] Telemetry for critical events
- [ ] Run ledger updated for experiments

_If a request conflicts with these rules, prefer to open a new ADR or propose an `exp/*` branch, do not modify protected docs._
