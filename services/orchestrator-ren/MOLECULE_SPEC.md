# Molecule Spec: Orchestrator-REN

## Intent (metric & constraint)
**Goal:** Provide a reliable task orchestration layer for robot command execution with <100ms ticket creation latency and >99% execution success rate under normal operating conditions.

**Metrics:**
- Ticket creation latency < 100ms (p95)
- Execution latency tracked per command type
- Success rate > 99% for valid commands
- Zero unauthorized executions (safety constraint)

**Constraints:**
- All commands must validate against MONAD contracts
- Speed limits enforced (max 3.0 m/s)
- Timeout protection on all executions
- No ticket loss (eventual persistence required)

## Inputs/Outputs (contracts)
**Inputs:**
- `TicketCreateRequest` - Command specification with params, priority, timeout, metadata
- `ExecuteRequest` - Ticket ID and optional force flag

**Outputs:**
- `Ticket` - Full ticket object with lifecycle tracking
- `ExecuteResponse` - Execution results with status, timing, and error reporting
- Telemetry events: `ticket_created`, `execution_started`, `execution_completed`, `execution_failed`
- Telemetry metrics: `tickets.created`, `tickets.total`, `execution.latency_ms`, `execution.success`, `execution.failure`

**Contract Alignment:**
- Commands dispatch to subsystems using `actuator.v1.json` contract
- Execution results can include sensor data (`imu.v1.json`, `ultrasonic.v1.json`)
- All runs should emit `metrics.v1.json` compatible telemetry
- Integration with `run.v1.json` for experiment tracking (future)

## Dependencies
**Runtime:**
- FastAPI >= 0.104.0
- Uvicorn >= 0.24.0 (ASGI server)
- Pydantic >= 2.0.0 (data validation)
- Python 3.7+

**Future/Planned:**
- Database (PostgreSQL/MongoDB) for persistent ticket storage
- Redis for distributed locking and queue management
- MONAD telemetry package (`monad-telemetry` - to be created)
- MONAD contracts package for validation

**External Services:**
- Actuator bus service (for command dispatch)
- Sensor services (IMU, ultrasonic) for feedback
- Metrics aggregator (Prometheus/Grafana compatible)

## Tests & Benchmarks
**Unit Tests (Required):**
- ✅ Ticket creation with valid/invalid inputs
- ✅ Priority handling (low/normal/high/critical)
- ✅ Status transitions (pending → executing → completed/failed)
- ✅ Timeout validation
- ✅ Safety threshold checks (speed limits)
- ✅ Duplicate execution prevention (unless forced)
- ✅ Error handling and error message generation

**Integration Tests (Required):**
- ✅ Full lifecycle: create → execute → retrieve
- ✅ Concurrent ticket execution
- ✅ Telemetry emission verification
- ✅ Database persistence (when implemented)
- ✅ Command dispatch to mock subsystems

**Benchmarks (Target):**
- Ticket creation: <100ms (p95)
- Ticket execution overhead: <50ms
- Throughput: >100 tickets/sec creation, >20 concurrent executions
- Memory: <100MB for 10k tickets in memory

**Golden Tests:**
- API contract stability (OpenAPI schema hash)
- No breaking changes to ticket schema
- Telemetry schema matches `metrics.v1.json`

## Telemetry
**Metrics Emitted:**
- `tickets.created` (counter, tags: command)
- `tickets.total` (gauge)
- `execution.latency_ms` (histogram, tags: command, status)
- `execution.success` (counter, tags: command)
- `execution.failure` (counter, tags: command)

**Events Emitted:**
- `ticket_created` - On ticket creation (payload: ticket_id, command, priority)
- `execution_started` - When execution begins (payload: ticket_id, command)
- `execution_completed` - On successful completion (payload: ticket_id, command, execution_time_ms)
- `execution_failed` - On failure (payload: ticket_id, command, error, execution_time_ms)
- `service_started` - Service startup
- `service_stopped` - Service shutdown (payload: total_tickets)

**Endpoints:**
- `GET /telemetry/metrics` - Retrieve collected metrics
- `GET /telemetry/events` - Retrieve collected events

**Future:** Integrate with centralized MONAD telemetry aggregator and time-series database.

## Demo Script
**File:** `demo.sh` or inline below

```bash
#!/bin/bash
# Orchestrator-REN Demo Script

echo "==> Starting Orchestrator-REN..."
python main.py &
PID=$!
sleep 2

echo -e "\n==> Check service health"
curl http://localhost:8000/

echo -e "\n\n==> Create a drive ticket"
TICKET=$(curl -s -X POST http://localhost:8000/ticket \
  -H "Content-Type: application/json" \
  -d '{
    "command": "drive",
    "params": {"speed": 1.5, "direction": 90, "duration_seconds": 5},
    "priority": "high"
  }')
echo $TICKET | jq .

TICKET_ID=$(echo $TICKET | jq -r .id)
echo "Created ticket: $TICKET_ID"

echo -e "\n==> Execute the ticket"
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\": \"$TICKET_ID\"}" | jq .

echo -e "\n==> Check ticket status"
curl http://localhost:8000/ticket/$TICKET_ID | jq .

echo -e "\n==> List all tickets"
curl http://localhost:8000/tickets | jq .

echo -e "\n==> View metrics"
curl http://localhost:8000/telemetry/metrics | jq .

echo -e "\n==> View events"
curl http://localhost:8000/telemetry/events | jq .

echo -e "\n==> Stopping service"
kill $PID
```

## Docs
- `README.md` - Setup, usage, API documentation
- `MOLECULE_SPEC.md` - This file
- Auto-generated API docs at `/docs` (Swagger UI) and `/redoc` when service is running

**Related ADRs:**
- ADR-0001: Molecularization (this service follows the pattern)
- ADR-0002: Contract Versioning (integrates with contract schemas)
- ADR-0003: Sim-Reality Bridge (orchestrator coordinates sim/hardware)

**Architecture Position:**
- **Layer:** Orchestration/Control
- **Peers:** Actuator bus, sensor aggregators, telemetry collector
- **Upstream:** User interfaces, planning systems, autonomous agents
- **Downstream:** Hardware drivers, simulation APIs

**Safety Notes:**
- All commands pass through safety validation
- Speed thresholds enforced (max 3.0 m/s in current implementation)
- Timeout protection prevents runaway executions
- Error states are terminal (no auto-retry without operator intervention)
- Future: E-stop integration required before production use

**Open Issues:**
1. Persistent storage not yet implemented (in-memory only)
2. No authentication/authorization
3. Command dispatch is simulated (needs integration with actual subsystems)
4. No distributed coordination (single-instance only)
5. Priority queue processing not implemented (FIFO currently)
