# monad-contracts

Versioned data contracts and validators.

## Contracts

- `imu.v1.json`
- `ultrasonic.v1.json`
- `actuator.v1.json`
- `run.v1.json`
- `metrics.v1.json`

## Validator

`validate_contracts.py` validates contract schemas, examples, and enforces immutability via golden hashes.

### Usage

```bash
python validate_contracts.py [--check-golden] [--update-golden] [--require-examples] [--force]
```

**Options:**
- `--check-golden`: Verify contracts match golden hashes (prevents accidental edits to v1 contracts)
- `--update-golden`: Add new contract versions to golden map
- `--require-examples`: Fail if any contract lacks example files
- `--force`: Allow overwriting existing golden entries (use with caution)

**Exit Codes:**
- `0`: Success - all validations passed
- `1`: CLI usage error (invalid arguments)
- `2`: Validation errors (malformed JSON, invalid examples, missing required examples)
- `3`: Golden check failed (hash mismatch or missing golden entry)
