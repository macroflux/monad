.PHONY: help venv validate test clean up down logs compose-test compose-validate

help:
	@echo "Available targets:"
	@echo "  make venv             - Create Python virtual environment and install dependencies"
	@echo "  make validate         - Run contract validator with golden checks"
	@echo "  make test             - Run all pytest tests"
	@echo "  make clean            - Remove virtual environment and cache files"
	@echo ""
	@echo "Docker Compose targets:"
	@echo "  make up               - Start dev stack (orchestrator + actuator)"
	@echo "  make down             - Stop and remove dev stack containers"
	@echo "  make logs             - Follow logs from all containers"
	@echo "  make compose-test     - Run smoke test against running containers"
	@echo "  make compose-validate - Validate docker-compose configuration"

venv:
	python -m venv .venv
	.venv\Scripts\python.exe -m pip install --upgrade pip
	.venv\Scripts\python.exe -m pip install jsonschema fastapi "pydantic>=2" uvicorn pytest httpx requests

validate:
	.venv\Scripts\python.exe packages\monad-contracts\validate_contracts.py --check-golden

test:
	.venv\Scripts\python.exe -m pytest -q

clean:
	if exist .venv rmdir /s /q .venv
	for /d /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i"
	for /d /r %%i in (.pytest_cache) do @if exist "%%i" rmdir /s /q "%%i"

# ============================================================================
# Docker Compose Targets
# ============================================================================

up:
	cd dev/compose && docker compose up -d --build

down:
	cd dev/compose && docker compose down

logs:
	cd dev/compose && docker compose logs -f

compose-test:
	@echo "Testing orchestrator-ren on port 8000..."
	@curl -s http://localhost:8000/healthz || echo "Failed to connect to orchestrator-ren"
	@echo ""
	@echo "Testing actuator-bus on port 8010..."
	@curl -s http://localhost:8010/healthz || echo "Failed to connect to actuator-bus"

compose-validate:
	cd dev/compose && docker compose config
