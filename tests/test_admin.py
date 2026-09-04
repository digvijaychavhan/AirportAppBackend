"""
Tests for Admin Overview, Fleet Devices, Operators, and Scans
"""

import pytest
from fastapi.testclient import TestClient
from app.main import fastapi_app

client = TestClient(fastapi_app)

def test_admin_overview():
    response = client.get("/api/v1/admin/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "kiosks" in data["data"]
    assert "operators" in data["data"]

def test_admin_devices():
    response = client.get("/api/v1/admin/devices")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0

def test_admin_operators():
    response = client.get("/api/v1/admin/operators")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0

def test_admin_scans():
    response = client.get("/api/v1/admin/scans")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_admin_amenities():
    response = client.get("/api/v1/admin/amenities")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_admin_scans_and_actions_pagination():
    response = client.get("/api/v1/admin/scans?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "pagination" in data
    assert data["pagination"]["limit"] == 5

    response_actions = client.get("/api/v1/admin/actions?limit=5&offset=0")
    assert response_actions.status_code == 200
    data_actions = response_actions.json()
    assert data_actions["success"] is True
    assert "pagination" in data_actions
    assert data_actions["pagination"]["limit"] == 5

