# Orchestrator-REN

**Robot Execution Orchestrator** - FastAPI service for managing robot task tickets and execution.

## Overview

Orchestrator-REN is a molecularized service that provides a ticket-based task execution system for robot commands. It follows MONAD principles with telemetry, contract validation, and safety-first design.

## Features

- ✅ **Ticket Creation** (`POST /ticket`) - Queue execution tasks with priority and timeout
- ✅ **Ticket Execution** (`POST /execute`) - Execute queued tickets with result tracking
- ✅ **Telemetry Built-in** - Emits metrics and events for all operations
- ✅ **Safety Checks** - Threshold validation and error handling
- ✅ **Status Tracking** - Full lifecycle management (pending → executing → completed/failed)
- ✅ **Query Interface** - List and filter tickets by status

## API Endpoints

### `GET /`
Health check and service status.

```json
{
  "service": "orchestrator-ren",
  "version": "0.1.0",
  "status": "operational",
  "tickets": {
    "total": 42,
    "pending": 5,
    "executing": 2,
    "completed": 30,
    "failed": 5
  }
}
```

### `POST /ticket`
Create a new execution ticket.

**Request:**
```json
{
  "command": "drive",
  "params": {
    "speed": 1.5,
    "direction": 90,
    "duration_seconds": 10
  },
  "priority": "normal",
  "timeout_seconds": 30,
  "metadata": {
    "operator": "user-001",
    "session_id": "ses-123"
  }
}
```

**Response (201):**
```json
{
  "id": "tick-20251108-a3f7e9c0",
  "command": "drive",
  "params": {...},
  "priority": "normal",
  "status": "pending",
  "timeout_seconds": 30,
  "metadata": {...},
  "created_at": "2025-11-08T10:30:00Z",
  "updated_at": "2025-11-08T10:30:00Z",
  "started_at": null,
  "completed_at": null,
  "result": null,
  "error": null
}
```

### `GET /ticket/{ticket_id}`
Retrieve a specific ticket by ID.

### `POST /execute`
Execute a ticket.

**Request:**
```json
{
  "ticket_id": "tick-20251108-a3f7e9c0",
  "force": false
}
```

**Response:**
```json
{
  "ticket_id": "tick-20251108-a3f7e9c0",
  "status": "completed",
  "result": {
    "command": "drive",
    "executed": true,
    "speed": 1.5,
    "direction": 90,
    "duration_seconds": 10,
    "distance_traveled": 15.0
  },
  "error": null,
  "execution_time_ms": 234.5,
  "message": "Execution completed successfully"
}
```

### `GET /tickets`
List tickets with optional filtering.

**Query Parameters:**
- `status` - Filter by status (pending, executing, completed, failed)
- `limit` - Max results (default: 100)
- `offset` - Pagination offset (default: 0)

### `GET /telemetry/metrics`
Retrieve collected metrics.

### `GET /telemetry/events`
Retrieve collected events.

## Installation

```bash
cd services/orchestrator-ren
pip install -r requirements.txt
```

## Usage

### Start the Service

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

### Interactive API Docs

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Usage

```bash
# Create a ticket
curl -X POST http://localhost:8000/ticket \
  -H "Content-Type: application/json" \
  -d '{
    "command": "drive",
    "params": {"speed": 1.5, "direction": 90, "duration_seconds": 10},
    "priority": "normal"
  }'

# Execute the ticket
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "tick-20251108-a3f7e9c0"
  }'

# List all tickets
curl http://localhost:8000/tickets

# Get metrics
curl http://localhost:8000/telemetry/metrics
```

## Ticket Lifecycle

```
PENDING → QUEUED → EXECUTING → COMPLETED
                              ↘ FAILED
                              ↘ CANCELLED
```

## Safety Features

- **Speed Threshold Validation** - Prevents excessive speeds (max 3.0 m/s)
- **Timeout Protection** - Tickets have configurable timeouts
- **Error Handling** - All failures are captured and logged
- **Telemetry** - All operations emit metrics and events
- **Force Re-execution** - Optional `force` flag to retry failed tickets

## Telemetry

### Metrics
- `tickets.created` - Counter for ticket creation
- `tickets.total` - Gauge for total tickets
- `execution.latency_ms` - Histogram of execution times
- `execution.success` - Counter for successful executions
- `execution.failure` - Counter for failed executions

### Events
- `ticket_created` - Ticket was created
- `execution_started` - Ticket execution began
- `execution_completed` - Ticket execution succeeded
- `execution_failed` - Ticket execution failed
- `service_started` - Service startup
- `service_stopped` - Service shutdown

## Commands

Current supported commands (extensible):
- `drive` - Move the robot (params: speed, direction, duration_seconds)
- `stop` - Stop all motion
- `scan` - Perform environment scan

## Development Notes

### In-Memory Storage
Current implementation uses in-memory storage (`tickets_db`). For production:
- Replace with persistent database (PostgreSQL, MongoDB, Redis)
- Add ticket persistence across restarts
- Implement distributed locking for multi-instance deployments

### Command Execution
The `_execute_command()` function is a placeholder. Production implementation should:
- Dispatch to actual subsystems (actuator bus, sensor modules)
- Validate against MONAD contracts (actuator.v1.json, etc.)
- Implement comprehensive safety checks
- Include e-stop pathways
- Add dry-run/simulation modes

### Testing
See `MOLECULE_SPEC.md` for testing requirements.

## MONAD Compliance

✅ **Molecularization** - Single-responsibility service with clear contracts  
✅ **Telemetry** - All operations emit metrics and events  
✅ **Safety** - Input validation and threshold checks  
✅ **Contracts** - Uses MONAD contract schemas  
✅ **Molecule Spec** - See MOLECULE_SPEC.md

## Next Steps

1. Add persistent storage backend
2. Implement actual command dispatch to robot subsystems
3. Add authentication/authorization
4. Create comprehensive unit tests
5. Add integration tests with other MONAD services
6. Implement ticket priority queue processing
7. Add WebSocket support for real-time status updates
