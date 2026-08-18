"""
Tests for Support Queue, Operator Stats, and Call Logs
"""

import pytest
from fastapi.testclient import TestClient
from app.main import fastapi_app

client = TestClient(fastapi_app)

def test_operator_queue():
    response = client.get("/api/v1/operator/queue")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "totalQueued" in data

def test_operator_stats():
    response = client.get("/api/v1/operator/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "totalInboundCalls" in data["data"]

def test_call_request_and_clear():
    payload = {
        "kioskId": "T3-L1-K04",
        "adaPriority": True,
        "language": "EN"
    }
    response = client.post("/api/v1/support/call-request", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "callId" in data["data"]

    # Clear queue
    clear_resp = client.post("/api/v1/operator/queue/clear")
    assert clear_resp.status_code == 200

def test_submit_operator_log():
    payload = {
        "sessionId": "test_call_9999",
        "kioskId": "T3-L1-K04",
        "duration": "02:30",
        "firstName": "John",
        "lastName": "Doe",
        "categories": ["Wayfinding", "Baggage"],
        "notes": "Assisted passenger with gate location."
    }
    response = client.post("/api/v1/operator/logs/submit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
