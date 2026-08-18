"""
Tests for Wi-Fi OTP, Passport Verification, AI Intent, Feedback, and Kiosk Heartbeat
"""

import pytest
from fastapi.testclient import TestClient
from app.main import fastapi_app

client = TestClient(fastapi_app)

def test_wifi_request_otp():
    payload = {"phoneNumber": "+91 98765 43210"}
    response = client.post("/api/v1/wifi/request-otp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "otp" in data

def test_wifi_verify_otp():
    payload = {"otp": "123456"}
    response = client.post("/api/v1/wifi/verify-otp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["isVerified"] is True

def test_wifi_scan_passport_demo():
    payload = {"isDemo": True, "demoType": "valid"}
    response = client.post("/api/v1/wifi/scan-passport", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["verified"] is True
    assert "passportDetails" in data
    assert "wifiDetails" in data

def test_ai_intent():
    payload = {"transcript": "Take me to Third Wave Coffee"}
    response = client.post("/api/v1/ai/intent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["action"] in ["map", "category_page", "conversation"]

def test_feedback_submit():
    payload = {
        "overallRating": 5,
        "cleanlinessRating": 5,
        "staffRating": 5,
        "comments": "Great kiosk experience!"
    }
    response = client.post("/api/v1/feedback/submit", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["success"] is True

def test_kiosk_heartbeat():
    payload = {"kioskId": "T3-L1-K04", "page": "/wayfinding"}
    response = client.post("/api/v1/kiosk/heartbeat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "acknowledged"
