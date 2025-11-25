# MONAD Omnibus

Seed monorepo for a unified architecture spanning AI, robotics, simulation, and data systems.

- **Vision:** One system of thinking and building—compose small “molecules” into systems.
- **This commit:** Initialization Charter v0.1, repo scaffold, ADR templates, and CI stubs.

## Quickstart
```bash
# 1) Initialize and make first commit
git init
git add .
git commit -m "feat(init): MONAD Omnibus v0.1 — charter, ADR templates, CI stubs"

# 2) Tag the charter version and create branches
git tag charter-v0.1
git branch -M main
git branch dev
git checkout dev

# 3) Create WIP tracks
git checkout -b exp/sim-bridge
git checkout -b feat/contracts-v1
git checkout -b feat/orchestrator-skeleton
```

## Branching
- `main`: protected, release-quality
- `dev`: integration
- `feat/*`: feature tracks
- `exp/*`: research experiments
- `hotfix/*`: urgent fixes

## Versioning
- **Charter tags:** `charter-vX.Y`
- **Schema/contracts:** `contracts/vX` folders + tests
- **Models:** tracked via registry with dataset + code SHA
- **Releases:** semver; changelog automated

## Development

The Makefile provides shortcuts for common development tasks:

```bash
make up        # Start services with docker compose
make down      # Stop services with docker compose
make logs      # Follow docker compose logs
make test      # Run all pytest tests
make validate  # Run contract validator with golden checks
make venv      # Create Python virtual environment and install dependencies
make clean     # Remove virtual environment and cache files
```

See `docs/charter.md` for the Initialization Charter (v0.1).
