"""
Tests for Wayfinding, Spatial Routes, Directory, and Map Editor
"""

import pytest
from fastapi.testclient import TestClient
from app.main import fastapi_app

client = TestClient(fastapi_app)

def test_wayfinding_route():
    payload = {
        "originNodeId": "node_kiosk_t3_l1_04",
        "destinationPoiId": "poi_gate_b12",
        "accessibilityMode": "elevator"
    }
    response = client.post("/api/v1/wayfinding/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "path" in data
    assert len(data["path"]) > 0
    assert "totalDistanceMeters" in data

def test_directory_pois():
    response = client.get("/api/v1/directory")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0

def test_map_nodes():
    response = client.get("/api/v1/map/nodes")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
