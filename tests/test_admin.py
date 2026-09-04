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


def test_admin_device_crud():
    # 1. Create with machine name only
    create_res = client.post("/api/v1/admin/devices", json={"name": "Test Kiosk Gate 42"})
    assert create_res.status_code == 200
    res_data = create_res.json()
    assert res_data["success"] is True
    device_id = res_data["deviceId"]

    # 2. Verify in devices list
    list_res = client.get("/api/v1/admin/devices")
    assert list_res.status_code == 200
    items = list_res.json()["data"]
    found = [d for d in items if d["deviceId"] == device_id]
    assert len(found) == 1
    assert found[0]["name"] == "Test Kiosk Gate 42"
    assert found[0]["deviceType"] == "kiosk"

    # 3. Delete the device
    del_res = client.delete(f"/api/v1/admin/devices/{device_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 4. Verify deleted
    list_res2 = client.get("/api/v1/admin/devices")
    items2 = list_res2.json()["data"]
    assert not any(d["deviceId"] == device_id for d in items2)


def test_kiosk_claim():
    res = client.post("/api/v1/kiosks/claim", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "kiosk" in data or "data" in data
    kiosk = data.get("data") or data.get("kiosk")
    assert "deviceId" in kiosk
    assert "name" in kiosk


