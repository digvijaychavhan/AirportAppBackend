"""
Tests for Support Queue, Operator Stats, and Call Logs
"""

import importlib
import tempfile
from pathlib import Path

def test_operator_queue(client):
    response = client.get("/api/v1/operator/queue")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "totalQueued" in data

def test_operator_stats(client):
    response = client.get("/api/v1/operator/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "totalInboundCalls" in data["data"]

def test_call_request_and_clear(client):
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

def test_submit_operator_log(client):
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
    assert data["data"]["recordingId"] == "test_call_9999"
    assert data["data"]["recordingStatus"] == "UPLOADING"


def test_kiosk_call_recording_upload_and_download(client, monkeypatch):
    support_router = importlib.import_module("app.modules.support.router")
    support_service = importlib.import_module("app.modules.support.service")
    tests_dir = Path(__file__).resolve().parent

    with tempfile.TemporaryDirectory(dir=tests_dir) as recordings_dir:
        monkeypatch.setattr(support_router, "get_recordings_dir", lambda: recordings_dir)
        monkeypatch.setattr(support_service, "get_recordings_dir", lambda: recordings_dir)

        upload = client.post(
            "/api/v1/operator/call/test_screen_capture/recording",
            files={"file": ("capture.webm", b"webm-screen-bytes", "video/webm")},
        )
        assert upload.status_code == 200
        payload = upload.json()
        assert payload["success"] is True
        assert payload["recordingId"] == "test_screen_capture"
        assert payload["recordingName"] == "recording_test_screen_capture.webm"
        assert payload["recordingStatus"] == "AVAILABLE"

        details = client.get("/api/v1/operator/call/test_screen_capture")
        assert details.status_code == 200
        assert details.json()["data"]["recordingStatus"] == "AVAILABLE"
        assert details.json()["data"]["recordingId"] == "test_screen_capture"

        download = client.get("/api/v1/operator/call/test_screen_capture/download-recording")
        assert download.status_code == 200
        assert download.content == b"webm-screen-bytes"
