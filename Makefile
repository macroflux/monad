.PHONY: help venv validate test clean

help:
	@echo "Available targets:"
	@echo "  make venv      - Create Python virtual environment and install dependencies"
	@echo "  make validate  - Run contract validator with golden checks"
	@echo "  make test      - Run all pytest tests"
	@echo "  make clean     - Remove virtual environment and cache files"

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
