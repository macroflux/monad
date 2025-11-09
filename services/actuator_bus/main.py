#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONAD Actuator Bus
FastAPI service for robot actuator commands.

Endpoint:
- POST /actuate: Accept actuator commands (drive, stop, brake)
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("actuator-bus")


# ============================================================================
# MODELS - Aligned with actuator.v1.json contract
# ============================================================================


class ActuatorCommand(str, Enum):
    """Valid actuator commands from actuator.v1.json"""

    DRIVE = "drive"
    STOP = "stop"
    BRAKE = "brake"


class ActuateRequest(BaseModel):
    """Request body for /actuate endpoint - matches actuator.v1.json"""

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    command: ActuatorCommand = Field(..., description="Actuator command")
    params: Optional[Dict[str, Any]] = Field(
        default=None, description="Command parameters"
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp is ISO 8601 format"""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError("timestamp must be valid ISO 8601 format")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "timestamp": "2025-11-08T10:30:00Z",
                    "command": "drive",
                    "params": {"speed": 1.5, "direction": 90},
                },
                {"timestamp": "2025-11-08T10:31:00Z", "command": "stop"},
            ]
        }
    )


class ActuateResponse(BaseModel):
    """Response from /actuate endpoint"""

    ack: bool = Field(..., description="Acknowledgment of receipt")
    received_at: str = Field(..., description="ISO 8601 timestamp when received")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="MONAD Actuator Bus",
    description="Robot actuator command interface - validates and logs actuator commands",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"service": "actuator-bus", "version": "0.1.0", "status": "operational"}


@app.post("/actuate", response_model=ActuateResponse, status_code=status.HTTP_200_OK)
async def actuate(request: ActuateRequest):
    """
    Accept and validate actuator commands.

    Validates against actuator.v1.json contract:
    - command must be one of: drive, stop, brake
    - timestamp must be valid ISO 8601 format
    - params is optional

    Logs all valid requests at INFO level.
    """
    received_at = datetime.now(timezone.utc).isoformat()

    # Log successful command receipt
    logger.info(
        f"Actuator command received: command={request.command.value}, "
        f"timestamp={request.timestamp}, params={request.params}"
    )

    return ActuateResponse(ack=True, received_at=received_at)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for logging validation errors and other exceptions.
    """
    # Log validation errors at WARN level
    if isinstance(exc, HTTPException) and exc.status_code == 422:
        logger.warning(f"Invalid input received: {exc.detail}")
    else:
        logger.error(f"Unexpected error: {exc}")

    # Re-raise to let FastAPI handle the response
    raise exc


# Custom validation error handler for more detailed logging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    Logs invalid input at WARN level.
    """
    errors = exc.errors()
    logger.warning(f"Validation error - Invalid input: {errors}")

    # Convert errors to JSON-serializable format
    serializable_errors = []
    for error in errors:
        error_dict = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input"),
        }
        # Handle ctx field which may contain non-serializable objects
        if "ctx" in error and error["ctx"]:
            ctx = error["ctx"]
            if isinstance(ctx, dict):
                error_dict["ctx"] = {k: str(v) for k, v in ctx.items()}
        serializable_errors.append(error_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": serializable_errors},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
