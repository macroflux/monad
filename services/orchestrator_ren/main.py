#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONAD Orchestrator-REN
FastAPI service for orchestrating robot execution tasks.

Endpoints:
- POST /ticket: Create execution ticket with validation
- POST /execute: Execute a ticket and return results
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


# ============================================================================
# TELEMETRY (placeholder - will be enhanced)
# ============================================================================


class TelemetryCollector:
    """Simple telemetry collector for metrics and events."""

    def __init__(self):
        self.metrics = []
        self.events = []

    def emit_metric(
        self, name: str, value: float, tags: Optional[Dict[str, Any]] = None
    ):
        """Emit a metric."""
        self.metrics.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "name": name,
                "value": value,
                "tags": tags or {},
            }
        )
        print(f"[METRIC] {name}={value} {tags or {}}")

    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event."""
        self.events.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": event_type,
                "data": data,
            }
        )
        print(f"[EVENT] {event_type}: {data}")


telemetry = TelemetryCollector()


# ============================================================================
# SAFETY CONSTANTS
# ============================================================================

MAX_SAFE_SPEED_MS = 3.0  # Maximum safe speed in m/s
MAX_DIRECTION_DEGREES = 360  # Maximum direction in degrees
MAX_DURATION_SECONDS = 300  # Maximum duration (5 minutes)


# ============================================================================
# MODELS (aligned with MONAD contracts)
# ============================================================================


class TicketPriority(str, Enum):
    """Execution priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    """Ticket lifecycle states."""

    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TicketCreateRequest(BaseModel):
    """Request to create a new execution ticket."""

    command: str = Field(
        ..., description="Command to execute (e.g., 'drive', 'scan', 'navigate')"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Command parameters"
    )
    priority: TicketPriority = Field(
        default=TicketPriority.NORMAL, description="Execution priority"
    )
    timeout_seconds: Optional[int] = Field(
        default=300, description="Max execution time in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "command": "drive",
                "params": {"speed": 1.5, "direction": 90, "duration_seconds": 10},
                "priority": "normal",
                "timeout_seconds": 30,
                "metadata": {"operator": "user-001", "session_id": "ses-123"},
            }
        }


class Ticket(BaseModel):
    """Execution ticket with full lifecycle tracking."""

    id: str = Field(..., description="Unique ticket identifier")
    command: str
    params: Dict[str, Any]
    priority: TicketPriority
    status: TicketStatus
    timeout_seconds: int
    metadata: Dict[str, Any]
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")
    started_at: Optional[str] = Field(
        default=None, description="Execution start timestamp"
    )
    completed_at: Optional[str] = Field(
        default=None, description="Execution completion timestamp"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Execution result data"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ExecuteRequest(BaseModel):
    """Request to execute a ticket."""

    ticket_id: str = Field(..., description="ID of ticket to execute")
    force: bool = Field(
        default=False, description="Force execution even if already executed"
    )

    class Config:
        json_schema_extra = {
            "example": {"ticket_id": "tick-20251108-a3f7e9c0", "force": False}
        }


class ExecuteResponse(BaseModel):
    """Response from ticket execution."""

    ticket_id: str
    status: TicketStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float
    message: str


# ============================================================================
# IN-MEMORY STORAGE (for demo - replace with persistent storage)
# ============================================================================

tickets_db: Dict[str, Ticket] = {}


# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    # Startup
    telemetry.emit_event(
        "service_started", {"service": "orchestrator-ren", "version": "0.1.0"}
    )
    print("[STARTUP] Orchestrator-REN service started")

    yield

    # Shutdown
    telemetry.emit_event(
        "service_stopped",
        {"service": "orchestrator-ren", "total_tickets": len(tickets_db)},
    )
    print("[SHUTDOWN] Orchestrator-REN service stopped")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    lifespan=lifespan,
    title="MONAD Orchestrator-REN",
    description="Robot Execution Orchestrator - manages task tickets and execution",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "orchestrator-ren",
        "version": "0.1.0",
        "status": "operational",
        "tickets": {
            "total": len(tickets_db),
            "pending": sum(
                1 for t in tickets_db.values() if t.status == TicketStatus.PENDING
            ),
            "executing": sum(
                1 for t in tickets_db.values() if t.status == TicketStatus.EXECUTING
            ),
            "completed": sum(
                1 for t in tickets_db.values() if t.status == TicketStatus.COMPLETED
            ),
            "failed": sum(
                1 for t in tickets_db.values() if t.status == TicketStatus.FAILED
            ),
        },
    }


@app.post("/ticket", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(request: TicketCreateRequest):
    """
    Create a new execution ticket.

    Validates the request, generates a unique ticket ID, and stores it for execution.
    Emits telemetry for ticket creation.
    """
    # Generate unique ticket ID
    ticket_id = f"tick-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat() + "Z"

    # Create ticket
    ticket = Ticket(
        id=ticket_id,
        command=request.command,
        params=request.params,
        priority=request.priority,
        status=TicketStatus.PENDING,
        timeout_seconds=request.timeout_seconds,
        metadata=request.metadata,
        created_at=now,
        updated_at=now,
    )

    # Store ticket
    tickets_db[ticket_id] = ticket

    # Emit telemetry
    telemetry.emit_event(
        "ticket_created",
        {
            "ticket_id": ticket_id,
            "command": request.command,
            "priority": request.priority.value,
        },
    )
    telemetry.emit_metric("tickets.created", 1.0, {"command": request.command})
    telemetry.emit_metric("tickets.total", float(len(tickets_db)))

    return ticket


@app.get("/ticket/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str):
    """
    Retrieve a ticket by ID.
    """
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found",
        )

    return tickets_db[ticket_id]


@app.post("/execute", response_model=ExecuteResponse)
async def execute_ticket(request: ExecuteRequest):
    """
    Execute a ticket.

    Validates the ticket exists and is in a valid state for execution.
    Simulates execution and updates ticket status.
    Emits telemetry for execution tracking.
    """
    start_time = datetime.utcnow()
    ticket_id = request.ticket_id

    # Validate ticket exists
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found",
        )

    ticket = tickets_db[ticket_id]

    # Check if already executed (unless forced)
    if not request.force and ticket.status in [
        TicketStatus.COMPLETED,
        TicketStatus.FAILED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ticket already in terminal state: {ticket.status}. Use force=true to re-execute.",
        )

    # Update ticket to executing
    now = datetime.utcnow().isoformat() + "Z"
    ticket.status = TicketStatus.EXECUTING
    ticket.started_at = now
    ticket.updated_at = now

    telemetry.emit_event(
        "execution_started", {"ticket_id": ticket_id, "command": ticket.command}
    )

    # Simulate execution (replace with actual command dispatch)
    try:
        result = _execute_command(ticket.command, ticket.params)

        # Update ticket to completed
        ticket.status = TicketStatus.COMPLETED
        ticket.result = result
        ticket.completed_at = datetime.utcnow().isoformat() + "Z"
        ticket.updated_at = ticket.completed_at

        execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Emit success telemetry
        telemetry.emit_event(
            "execution_completed",
            {
                "ticket_id": ticket_id,
                "command": ticket.command,
                "execution_time_ms": execution_time_ms,
            },
        )
        telemetry.emit_metric(
            "execution.latency_ms",
            execution_time_ms,
            {"command": ticket.command, "status": "success"},
        )
        telemetry.emit_metric("execution.success", 1.0, {"command": ticket.command})

        return ExecuteResponse(
            ticket_id=ticket_id,
            status=ticket.status,
            result=result,
            execution_time_ms=execution_time_ms,
            message="Execution completed successfully",
        )

    except Exception as e:
        # Update ticket to failed
        ticket.status = TicketStatus.FAILED
        ticket.error = str(e)
        ticket.completed_at = datetime.utcnow().isoformat() + "Z"
        ticket.updated_at = ticket.completed_at

        execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Emit failure telemetry
        telemetry.emit_event(
            "execution_failed",
            {
                "ticket_id": ticket_id,
                "command": ticket.command,
                "error": str(e),
                "execution_time_ms": execution_time_ms,
            },
        )
        telemetry.emit_metric(
            "execution.latency_ms",
            execution_time_ms,
            {"command": ticket.command, "status": "failed"},
        )
        telemetry.emit_metric("execution.failure", 1.0, {"command": ticket.command})

        return ExecuteResponse(
            ticket_id=ticket_id,
            status=ticket.status,
            error=str(e),
            execution_time_ms=execution_time_ms,
            message=f"Execution failed: {str(e)}",
        )


@app.get("/tickets")
async def list_tickets(
    status: Optional[TicketStatus] = None, limit: int = 100, offset: int = 0
):
    """
    List tickets with optional filtering.
    """
    tickets = list(tickets_db.values())

    # Filter by status if provided
    if status:
        tickets = [t for t in tickets if t.status == status]

    # Sort by created_at descending (newest first)
    tickets.sort(key=lambda t: t.created_at, reverse=True)

    # Paginate
    total = len(tickets)
    tickets = tickets[offset : offset + limit]

    return {"total": total, "limit": limit, "offset": offset, "tickets": tickets}


@app.get("/telemetry/metrics")
async def get_metrics():
    """
    Retrieve collected metrics.
    """
    return {
        "count": len(telemetry.metrics),
        "metrics": telemetry.metrics[-100:],  # Last 100 metrics
    }


@app.get("/telemetry/events")
async def get_events():
    """
    Retrieve collected events.
    """
    return {
        "count": len(telemetry.events),
        "events": telemetry.events[-100:],  # Last 100 events
    }


# ============================================================================
# COMMAND EXECUTION LOGIC (placeholder)
# ============================================================================


def _execute_command(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a command with given parameters.

    This is a placeholder implementation. In production, this would:
    - Dispatch to appropriate subsystems (actuator, sensor, etc.)
    - Validate against MONAD contracts
    - Include safety checks and thresholds
    - Implement e-stop pathways
    """
    # Simulate command execution
    if command == "drive":
        # Validate required parameters
        if "speed" not in params:
            raise ValueError("Missing required parameter: speed")
        if "duration_seconds" not in params:
            raise ValueError("Missing required parameter: duration_seconds")

        speed = params["speed"]
        direction = params.get("direction", 0)
        duration = params["duration_seconds"]

        # Validate parameter types and ranges
        if not isinstance(speed, (int, float)):
            raise ValueError(f"Speed must be numeric, got {type(speed).__name__}")
        if not isinstance(duration, (int, float)):
            raise ValueError(f"Duration must be numeric, got {type(duration).__name__}")
        if not isinstance(direction, (int, float)):
            raise ValueError(
                f"Direction must be numeric, got {type(direction).__name__}"
            )

        # Safety checks
        if speed > MAX_SAFE_SPEED_MS:
            raise ValueError(
                f"Speed {speed} exceeds safety threshold of {MAX_SAFE_SPEED_MS} m/s"
            )
        if speed < 0:
            raise ValueError(f"Speed must be non-negative, got {speed}")
        if duration > MAX_DURATION_SECONDS:
            raise ValueError(
                f"Duration {duration}s exceeds maximum of {MAX_DURATION_SECONDS}s"
            )
        if duration < 0:
            raise ValueError(f"Duration must be non-negative, got {duration}")
        if not (0 <= direction < MAX_DIRECTION_DEGREES):
            raise ValueError(
                f"Direction {direction} must be in range [0, {MAX_DIRECTION_DEGREES})"
            )

        distance_traveled = speed * duration

        return {
            "command": "drive",
            "executed": True,
            "speed": speed,
            "direction": direction,
            "duration_seconds": duration,
            "distance_traveled": distance_traveled,
        }

    elif command == "stop":
        return {"command": "stop", "executed": True, "status": "stopped"}

    elif command == "scan":
        return {
            "command": "scan",
            "executed": True,
            "scan_points": 360,
            "obstacles_detected": 3,
        }

    else:
        raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
