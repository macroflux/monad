#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for Orchestrator-REN
Starts service, runs basic tests, then stops.
"""

import time
import requests
import subprocess
import sys
from pathlib import Path

SERVICE_URL = "http://localhost:8000"
PYTHON_EXE = sys.executable
SCRIPT_DIR = Path(__file__).parent


def test_service():
    """Run basic tests against the service."""

    print("=" * 60)
    print("ORCHESTRATOR-REN TEST SUITE")
    print("=" * 60)

    # Test 1: Health check
    print("\n[TEST 1] Health Check")
    try:
        resp = requests.get(f"{SERVICE_URL}/")
        print(f"✓ Status: {resp.status_code}")
        print(f"✓ Response: {resp.json()}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 2: Create a ticket
    print("\n[TEST 2] Create Drive Ticket")
    try:
        ticket_data = {
            "command": "drive",
            "params": {"speed": 1.5, "direction": 90, "duration_seconds": 5},
            "priority": "high",
            "timeout_seconds": 30,
        }
        resp = requests.post(f"{SERVICE_URL}/ticket", json=ticket_data)
        print(f"✓ Status: {resp.status_code}")
        ticket = resp.json()
        ticket_id = ticket["id"]
        print(f"✓ Created ticket: {ticket_id}")
        print(f"✓ Status: {ticket['status']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 3: Retrieve the ticket
    print("\n[TEST 3] Retrieve Ticket")
    try:
        resp = requests.get(f"{SERVICE_URL}/ticket/{ticket_id}")
        print(f"✓ Status: {resp.status_code}")
        retrieved = resp.json()
        print(f"✓ Ticket ID matches: {retrieved['id'] == ticket_id}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 4: Execute the ticket
    print("\n[TEST 4] Execute Ticket")
    try:
        exec_data = {"ticket_id": ticket_id}
        resp = requests.post(f"{SERVICE_URL}/execute", json=exec_data)
        print(f"✓ Status: {resp.status_code}")
        result = resp.json()
        print(f"✓ Execution status: {result['status']}")
        print(f"✓ Execution time: {result['execution_time_ms']:.2f}ms")
        if result.get("result"):
            print(f"✓ Result: {result['result']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 5: List tickets
    print("\n[TEST 5] List Tickets")
    try:
        resp = requests.get(f"{SERVICE_URL}/tickets")
        print(f"✓ Status: {resp.status_code}")
        data = resp.json()
        print(f"✓ Total tickets: {data['total']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 6: Check telemetry
    print("\n[TEST 6] Check Telemetry")
    try:
        resp = requests.get(f"{SERVICE_URL}/telemetry/metrics")
        metrics = resp.json()
        print(f"✓ Metrics collected: {metrics['count']}")

        resp = requests.get(f"{SERVICE_URL}/telemetry/events")
        events = resp.json()
        print(f"✓ Events collected: {events['count']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 7: Safety check - excessive speed
    print("\n[TEST 7] Safety Check (Speed Limit)")
    try:
        unsafe_ticket = {
            "command": "drive",
            "params": {"speed": 3.5, "direction": 0, "duration_seconds": 1},
            "priority": "normal",
        }
        resp = requests.post(f"{SERVICE_URL}/ticket", json=unsafe_ticket)
        ticket = resp.json()

        exec_data = {"ticket_id": ticket["id"]}
        resp = requests.post(f"{SERVICE_URL}/execute", json=exec_data)
        result = resp.json()

        if (
            result["status"] == "failed"
            and "threshold" in result.get("error", "").lower()
        ):
            print("✓ Safety check passed: Speed limit enforced")
            print(f"✓ Error: {result['error']}")
        else:
            print("✗ Safety check failed: Speed limit not enforced")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Start the service
    print("Starting Orchestrator-REN service...")
    proc = subprocess.Popen(
        [PYTHON_EXE, "main.py"],
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for service to start with retry loop
    print("Waiting for service to start...")
    max_retries = 30
    retry_delay = 0.5
    for i in range(max_retries):
        if proc.poll() is not None:
            print("ERROR: Service failed to start")
            stdout, stderr = proc.communicate()
            print("STDOUT:", stdout.decode())
            print("STDERR:", stderr.decode())
            sys.exit(1)

        try:
            resp = requests.get(f"{SERVICE_URL}/", timeout=1)
            if resp.status_code == 200:
                print(f"Service started successfully (after {i * retry_delay:.1f}s)")
                break
        except requests.exceptions.RequestException:
            time.sleep(retry_delay)
    else:
        print(f"ERROR: Service failed to respond after {max_retries * retry_delay}s")
        proc.terminate()
        sys.exit(1)

    # Final check if process is still running
    if proc.poll() is not None:
        print("ERROR: Service failed to start")
        stdout, stderr = proc.communicate()
        print("STDOUT:", stdout.decode())
        print("STDERR:", stderr.decode())
        sys.exit(1)

    try:
        # Run tests
        success = test_service()

        # Stop the service
        print("\nStopping service...")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
                proc.wait(timeout=5)
            except Exception:
                # Ignore errors during cleanup; process is being killed and we're exiting anyway
                pass

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
                proc.wait(timeout=5)
            except Exception:
                # Ignore errors during process kill/wait; program is exiting
                pass
        sys.exit(1)

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
                proc.wait(timeout=5)
            except Exception:
                # If both terminate and kill fail, there's nothing more we can do
                pass
        sys.exit(1)
