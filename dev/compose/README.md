# MONAD Development Stack

Docker Compose setup for local development and testing of MONAD services.

## Services

- **orchestrator-ren**: Robot Execution Orchestrator (port 8000)
- **actuator-bus**: Robot Actuator Command Interface (port 8010)

## Quick Start

### Start the Stack

```bash
# From repository root
make up

# Or from this directory
docker compose up -d --build
```

### Check Service Health

```bash
# Health check endpoints
curl http://localhost:8000/healthz  # orchestrator-ren
curl http://localhost:8010/healthz  # actuator-bus

# Full service info
curl http://localhost:8000/  # orchestrator-ren
curl http://localhost:8010/  # actuator-bus
```

### View Logs

```bash
# From repository root
make logs

# Or from this directory
docker compose logs -f

# View specific service
docker compose logs -f orchestrator-ren
docker compose logs -f actuator-bus
```

### Stop the Stack

```bash
# From repository root
make down

# Or from this directory
docker compose down
```

## Makefile Targets

From the repository root:

- `make up` - Start all services (builds images if needed)
- `make down` - Stop and remove all containers
- `make logs` - Follow logs from all services
- `make compose-test` - Run smoke tests against running services
- `make compose-validate` - Validate docker-compose configuration

## Shared Resources

### Logs Volume

Both services mount `./logs:/app/logs` for shared logging output.

### Network

Services communicate via the `monad-network` bridge network.

## Health Checks

Both services include health checks via the `/healthz` endpoint:

- **Endpoint**: `/healthz` (returns `{"status": "healthy"}`)
- **Interval**: 30 seconds
- **Timeout**: 3 seconds
- **Retries**: 3
- **Start Period**: 5 seconds

Check container health:
```bash
docker compose ps
```

The actuator-bus service depends on orchestrator-ren being healthy before starting.

## Ports

- **8000**: orchestrator-ren (internal and external)
- **8010**: actuator-bus (maps to internal 8001)

## Testing Workflow

1. Start the stack:
   ```bash
   make up
   ```

2. Wait for services to be healthy (check with `docker compose ps`)

3. Test orchestrator-ren:
   ```bash
   # Create a ticket
   curl -X POST http://localhost:8000/ticket \
     -H "Content-Type: application/json" \
     -d '{
       "command": "drive",
       "params": {"speed": 1.5, "direction": 90, "duration_seconds": 5},
       "priority": "normal"
     }'
   
   # Execute the ticket (use the returned ticket_id)
   curl -X POST http://localhost:8000/execute \
     -H "Content-Type: application/json" \
     -d '{"ticket_id": "tick-20251111-abcd1234"}'
   ```

4. Test actuator-bus:
   ```bash
   curl -X POST http://localhost:8010/actuate \
     -H "Content-Type: application/json" \
     -d '{
       "timestamp": "2025-11-11T10:30:00Z",
       "command": "drive",
       "params": {"speed": 1.5, "direction": 90}
     }'
   ```

5. View interactive API documentation:
   - Orchestrator-REN: http://localhost:8000/docs
   - Actuator-Bus: http://localhost:8010/docs

## Troubleshooting

### Container won't start

Check logs:
```bash
docker compose logs <service-name>
```

### Port already in use

Stop conflicting services or change ports in `docker-compose.yml`.

### Build issues

Clean and rebuild:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Health check failing

Check service is responding:
```bash
docker compose exec orchestrator-ren curl http://localhost:8000/
docker compose exec actuator-bus curl http://localhost:8001/
```

## Development Tips

- Use `docker compose up` (without `-d`) to see real-time logs
- Edit code in `services/` directories - rebuild required after changes
- Use `docker compose restart <service>` to restart a specific service
- Check container resource usage: `docker stats`

## CI/CD Integration

The stack can be used in CI pipelines:

```bash
# Start services
docker compose up -d

# Wait for health
docker compose ps

# Run tests
make compose-test

# Cleanup
docker compose down
```
