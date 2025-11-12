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

## Docker Compose Development Stack

Run orchestrator-ren and actuator-bus locally:

```bash
# Start services
docker compose up

# In another terminal - run smoke tests
make compose-test

# Stop services
docker compose down
```

See `dev/compose/README.md` for detailed documentation.

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

See `docs/charter.md` for the Initialization Charter (v0.1).
