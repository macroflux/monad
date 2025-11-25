.PHONY: help venv validate test clean up down logs

help:
	@echo "Available targets:"
	@echo "  make venv      - Create Python virtual environment and install dependencies"
	@echo "  make validate  - Run contract validator with golden checks"
	@echo "  make test      - Run all pytest tests"
	@echo "  make clean     - Remove virtual environment and cache files"
	@echo "  make up        - Start services with docker compose"
	@echo "  make down      - Stop services with docker compose"
	@echo "  make logs      - Follow docker compose logs"

venv:
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install jsonschema fastapi "pydantic>=2" uvicorn pytest httpx requests

validate:
	python packages/monad-contracts/validate_contracts.py --check-golden

test:
	pytest -q

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

up:
	docker compose up

down:
	docker compose down

logs:
	docker compose logs -f
