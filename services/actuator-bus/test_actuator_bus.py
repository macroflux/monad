#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Actuator Bus service
Tests both successful (200) and validation error (422) cases.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestActuatorBus:
    """Test suite for actuator-bus service"""
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "actuator-bus"
        assert data["status"] == "operational"
    
    def test_actuate_drive_command_success(self):
        """Test successful drive command (200 OK)"""
        payload = {
            "timestamp": "2025-11-08T10:30:00Z",
            "command": "drive",
            "params": {"speed": 1.5, "direction": 90}
        }
        
        response = client.post("/actuate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ack"] is True
        assert "received_at" in data
        # Verify received_at is ISO 8601 format
        assert "T" in data["received_at"]
    
    def test_actuate_stop_command_success(self):
        """Test successful stop command without params (200 OK)"""
        payload = {
            "timestamp": "2025-11-08T10:31:00Z",
            "command": "stop"
        }
        
        response = client.post("/actuate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ack"] is True
        assert "received_at" in data
    
    def test_actuate_brake_command_success(self):
        """Test successful brake command (200 OK)"""
        payload = {
            "timestamp": "2025-11-08T10:32:00Z",
            "command": "brake",
            "params": {"force": 0.8}
        }
        
        response = client.post("/actuate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ack"] is True
    
    def test_actuate_missing_timestamp(self):
        """Test validation error when timestamp is missing (422)"""
        payload = {
            "command": "drive",
            "params": {"speed": 1.5}
        }
        
        response = client.post("/actuate", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_actuate_missing_command(self):
        """Test validation error when command is missing (422)"""
        payload = {
            "timestamp": "2025-11-08T10:30:00Z",
            "params": {"speed": 1.5}
        }
        
        response = client.post("/actuate", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_actuate_invalid_command(self):
        """Test validation error with invalid command (422)"""
        payload = {
            "timestamp": "2025-11-08T10:30:00Z",
            "command": "fly"  # Not in enum [drive, stop, brake]
        }
        
        response = client.post("/actuate", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_actuate_invalid_timestamp_format(self):
        """Test validation error with malformed timestamp (422)"""
        payload = {
            "timestamp": "not-a-timestamp",
            "command": "drive"
        }
        
        response = client.post("/actuate", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_actuate_empty_body(self):
        """Test validation error with empty body (422)"""
        response = client.post("/actuate", json={})
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_actuate_invalid_json(self):
        """Test validation error with malformed JSON (422)"""
        response = client.post(
            "/actuate",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
