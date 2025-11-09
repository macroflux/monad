#!/bin/bash
# Orchestrator-REN Demo Script
# Demonstrates ticket creation and execution

echo "==> Starting Orchestrator-REN..."
python main.py &
PID=$!
sleep 3

echo -e "\n==> 1. Check service health"
curl -s http://localhost:8000/ | python -m json.tool

echo -e "\n\n==> 2. Create a drive ticket"
RESPONSE=$(curl -s -X POST http://localhost:8000/ticket \
  -H "Content-Type: application/json" \
  -d '{
    "command": "drive",
    "params": {"speed": 1.5, "direction": 90, "duration_seconds": 5},
    "priority": "high"
  }')
echo "$RESPONSE" | python -m json.tool

TICKET_ID=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created ticket: $TICKET_ID"

echo -e "\n==> 3. Execute the ticket"
curl -s -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\": \"$TICKET_ID\"}" | python -m json.tool

echo -e "\n==> 4. Check ticket status"
curl -s http://localhost:8000/ticket/$TICKET_ID | python -m json.tool

echo -e "\n==> 5. Create a scan ticket"
curl -s -X POST http://localhost:8000/ticket \
  -H "Content-Type: application/json" \
  -d '{
    "command": "scan",
    "params": {},
    "priority": "normal"
  }' | python -m json.tool

echo -e "\n==> 6. List all tickets"
curl -s http://localhost:8000/tickets?limit=10 | python -m json.tool

echo -e "\n==> 7. View metrics"
curl -s http://localhost:8000/telemetry/metrics | python -m json.tool

echo -e "\n==> 8. View events"
curl -s http://localhost:8000/telemetry/events | python -m json.tool

echo -e "\n\n==> Stopping service..."
kill $PID
echo "Demo complete!"
