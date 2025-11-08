# Actuator Bus

**MONAD Actuator Bus** - FastAPI service for robot actuator command interface.

## Overview

The Actuator Bus service provides a validated endpoint for receiving robot actuator commands. It implements the `actuator.v1.json` contract and logs all commands for auditing and debugging.

## Features

- ✅ **Contract Validation** - Enforces `actuator.v1.json` schema
- ✅ **Command Enum** - Only accepts: `drive`, `stop`, `brake`
- ✅ **Timestamp Validation** - ISO 8601 format required
- ✅ **Comprehensive Logging** - INFO for valid commands, WARN for invalid input
- ✅ **Type Safety** - Pydantic models with strict validation
- ✅ **Test Coverage** - Pytest suite covering 200/422 cases

## API Endpoint

### `POST /actuate`

Accept and validate actuator commands.

**Request Body:**
```json
{
  "timestamp": "2025-11-08T10:30:00Z",
  "command": "drive",
  "params": {
    "speed": 1.5,
    "direction": 90
  }
}
```

**Valid Commands:**
- `drive` - Move the robot (typically includes speed/direction params)
- `stop` - Stop all motion
- `brake` - Apply brakes (may include force param)

**Response (200 OK):**
```json
{
  "ack": true,
  "received_at": "2025-11-08T10:30:01.234Z"
}
```

**Validation Errors (422):**
- Missing `timestamp` or `command`
- Invalid `command` (not in enum)
- Malformed `timestamp` (not ISO 8601)
- Invalid JSON structure

## Installation

```bash
cd services/actuator-bus
pip install -r requirements.txt
```

## Running the Service

### Standard Run

```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`

### With Custom Port

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Direct Python

```bash
python main.py
```

## Usage Examples

### Valid Commands

```bash
# Drive command
curl -X POST http://localhost:8000/actuate \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-11-08T10:30:00Z",
    "command": "drive",
    "params": {"speed": 1.5, "direction": 90}
  }'

# Stop command
curl -X POST http://localhost:8000/actuate \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-11-08T10:31:00Z",
    "command": "stop"
  }'

# Brake command
curl -X POST http://localhost:8000/actuate \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-11-08T10:32:00Z",
    "command": "brake",
    "params": {"force": 0.8}
  }'
```

### Invalid Commands (Will return 422)

```bash
# Invalid command
curl -X POST http://localhost:8000/actuate \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-11-08T10:30:00Z",
    "command": "fly"
  }'

# Missing timestamp
curl -X POST http://localhost:8000/actuate \
  -H "Content-Type: application/json" \
  -d '{
    "command": "drive"
  }'
```

## Testing

Run the test suite with pytest:

```bash
# Run all tests
pytest test_actuator_bus.py -v

# Run specific test
pytest test_actuator_bus.py::TestActuatorBus::test_actuate_drive_command_success -v

# Run with coverage
pytest test_actuator_bus.py --cov=main --cov-report=term-missing
```

### Test Coverage

The test suite includes:
- ✅ Health check endpoint
- ✅ Successful commands (200 OK) - drive, stop, brake
- ✅ Missing required fields (422)
- ✅ Invalid command enum (422)
- ✅ Malformed timestamp (422)
- ✅ Empty body (422)
- ✅ Invalid JSON (422)

## Logging

The service logs:

**INFO Level (Valid Commands):**
```
2025-11-08 10:30:01,234 - actuator-bus - INFO - Actuator command received: command=drive, timestamp=2025-11-08T10:30:00Z, params={'speed': 1.5, 'direction': 90}
```

**WARN Level (Invalid Input):**
```
2025-11-08 10:30:02,567 - actuator-bus - WARNING - Validation error - Invalid input: [{'type': 'missing', 'loc': ['body', 'timestamp'], 'msg': 'Field required'}]
```

## Interactive API Docs

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contract Alignment

This service implements **`actuator.v1.json`**:

```json
{
  "timestamp": "string (ISO 8601)",
  "command": "drive | stop | brake",
  "params": "object (optional)"
}
```

## MONAD Compliance

✅ **Contract Adherence** - Strict validation against actuator.v1.json  
✅ **Logging** - INFO for success, WARN for validation failures  
✅ **Type Safety** - Pydantic models prevent runtime errors  
✅ **Testing** - Comprehensive pytest coverage  
✅ **Documentation** - Clear API docs and examples

## Next Steps

1. Add persistent command logging (database or file)
2. Integrate with actual hardware/simulation actuators
3. Add authentication/authorization
4. Implement command queuing for async execution
5. Add telemetry metrics (integrate with orchestrator-ren)
6. Create integration tests with robot hardware
