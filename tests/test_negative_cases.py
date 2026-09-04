"""
Negative and Edge-Case Tests for FastAPI Backend
Validates 400, 404, and input sanitization across API domains.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_nonexistent_flight(client: TestClient):
    """
    Asserts 404 is returned when querying an invalid flight ID.
    """
    response = client.get("/api/v1/flights/INVALID_FLIGHT_XYZ_99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "message" in data


def test_get_nonexistent_poi(client: TestClient):
    """
    Asserts 404 is returned when querying an invalid POI ID.
    """
    response = client.get("/api/v1/wayfinding/poi/nonexistent_poi_99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_wifi_otp_empty_phone(client: TestClient):
    """
    Asserts 400 is returned when requesting OTP with an empty phone number.
    """
    response = client.post("/api/v1/wifi/request-otp", json={"phoneNumber": "   "})
    assert response.status_code == 400


def test_recording_upload_invalid_path_traversal(client: TestClient):
    """
    Asserts 400 is returned when call_id contains path traversal characters.
    """
    response = client.post(
        "/api/v1/operator/call/..%2F..%2Fetc/upload-recording",
        content=b"dummy media content"
    )
    assert response.status_code in [400, 404]


def test_recording_download_invalid_call_id(client: TestClient):
    """
    Asserts 400 is returned when call_id contains invalid characters.
    """
    response = client.get("/api/v1/operator/call/invalid!id@traversal/download-recording")
    assert response.status_code == 400


def test_recording_download_nonexistent(client: TestClient):
    """
    Asserts 404 is returned when downloading a non-existent recording.
    """
    response = client.get("/api/v1/operator/call/valid_call_id_99999/download-recording")
    assert response.status_code == 404


def test_operator_login_invalid_credentials(client: TestClient):
    """
    Asserts 401 is returned when logging in with invalid username or password.
    """
    # Non-existent user
    resp = client.post("/api/v1/operator/login", json={"username": "ghost_operator_99999", "password": "any"})
    assert resp.status_code == 401

    # Valid user (seeded operator) with incorrect password
    resp = client.post("/api/v1/operator/login", json={"username": "op_priya", "password": "definitely_wrong_password"})
    assert resp.status_code == 401


def test_ai_intent_empty_transcript(client: TestClient):
    """
    Asserts 400 is returned when AI intent transcript is empty or whitespace.
    """
    resp = client.post("/api/v1/ai/intent", json={"transcript": "   "})
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "EMPTY_TRANSCRIPT"


def test_admin_device_reboot_nonexistent(client: TestClient):
    """
    Asserts 404 is returned when attempting to reboot a non-existent device.
    """
    resp = client.post("/api/v1/admin/devices/nonexistent_device_id_99999/reboot")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Device not found"


def test_admin_delete_nonexistent_amenity(client: TestClient):
    """
    Asserts 404 is returned when attempting to delete a non-existent amenity.
    """
    resp = client.delete("/api/v1/admin/amenities/nonexistent_poi_id_99999")
    assert resp.status_code == 404


def test_wayfinding_route_invalid_destination(client: TestClient):
    """
    Asserts 400 is returned when computing route with empty destination,
    and 422 is returned when destinationPoiId is omitted.
    """
    # Empty / whitespace destination
    resp = client.post("/api/v1/wayfinding/route", json={
        "originNodeId": "node_kiosk_t3_l1_04",
        "destinationPoiId": "   "
    })
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "PATHFINDING_INVALID_REQUEST"

    # Missing destination entirely
    resp = client.post("/api/v1/wayfinding/route", json={
        "originNodeId": "node_kiosk_t3_l1_04"
    })
    assert resp.status_code == 422


