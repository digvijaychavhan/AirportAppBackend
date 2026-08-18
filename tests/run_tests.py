"""
Direct Test Runner for Backend Validation
"""

import os
import sys

# Ensure Backend root is in sys.path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from fastapi.testclient import TestClient
from app.main import fastapi_app

def run_all_tests():
    client = TestClient(fastapi_app)
    passed = 0
    failed = 0

    tests = [
        # Health
        ("GET /health", lambda: client.get("/health").status_code == 200),
        ("GET /", lambda: client.get("/").status_code == 200),

        # Flights
        ("GET /api/v1/flights/search", lambda: client.get("/api/v1/flights/search").json().get("success") is True),
        ("GET /api/v1/flights/search?query=6E", lambda: client.get("/api/v1/flights/search?query=6E").json().get("success") is True),
        ("POST /api/v1/flights/bcbp-decode", lambda: client.post("/api/v1/flights/bcbp-decode", json={}).json().get("success") is True),
        ("GET /api/v1/baggage/belts", lambda: len(client.get("/api/v1/baggage/belts").json().get("data", [])) >= 3),
        ("GET /api/v1/transfer/shuttles", lambda: len(client.get("/api/v1/transfer/shuttles").json().get("data", [])) >= 3),

        # Wayfinding
        ("POST /api/v1/wayfinding/route", lambda: client.post("/api/v1/wayfinding/route", json={"originNodeId": "node_kiosk_t3_l1_04", "destinationPoiId": "poi_gate_b12"}).json().get("success") is True),
        ("GET /api/v1/wayfinding/pois", lambda: client.get("/api/v1/wayfinding/pois").json().get("success") is True),
        ("GET /api/v1/directory", lambda: client.get("/api/v1/directory").json().get("success") is True),
        ("GET /api/v1/map/nodes", lambda: client.get("/api/v1/map/nodes").json().get("success") is True),

        # Support
        ("GET /api/v1/operator/queue", lambda: client.get("/api/v1/operator/queue").json().get("success") is True),
        ("GET /api/v1/operator/stats", lambda: client.get("/api/v1/operator/stats").json().get("success") is True),
        ("POST /api/v1/support/call-request", lambda: client.post("/api/v1/support/call-request", json={"kioskId": "T3-L1-K04", "adaPriority": True}).json().get("success") is True),
        ("POST /api/v1/operator/queue/clear", lambda: client.post("/api/v1/operator/queue/clear").json().get("success") is True),
        ("POST /api/v1/operator/logs/submit", lambda: client.post("/api/v1/operator/logs/submit", json={"sessionId": "test_s1", "notes": "Test"}).json().get("success") is True),

        # Admin
        ("GET /api/v1/admin/overview", lambda: client.get("/api/v1/admin/overview").json().get("success") is True),
        ("GET /api/v1/admin/network", lambda: client.get("/api/v1/admin/network").json().get("success") is True),
        ("GET /api/v1/admin/devices", lambda: client.get("/api/v1/admin/devices").json().get("success") is True),
        ("GET /api/v1/admin/operators", lambda: client.get("/api/v1/admin/operators").json().get("success") is True),
        ("GET /api/v1/admin/scans", lambda: client.get("/api/v1/admin/scans").json().get("success") is True),
        ("GET /api/v1/admin/actions", lambda: client.get("/api/v1/admin/actions").json().get("success") is True),
        ("GET /api/v1/admin/amenities", lambda: client.get("/api/v1/admin/amenities").json().get("success") is True),
        ("GET /api/v1/admin/wayfinding/categories", lambda: client.get("/api/v1/admin/wayfinding/categories").json().get("success") is True),

        # Wi-Fi & Passport
        ("POST /api/v1/wifi/request-otp", lambda: client.post("/api/v1/wifi/request-otp", json={"phoneNumber": "+91 98765 43210"}).json().get("success") is True),
        ("POST /api/v1/wifi/verify-otp", lambda: client.post("/api/v1/wifi/verify-otp", json={"otp": "123456"}).json().get("isVerified") is True),
        ("POST /api/v1/wifi/scan-passport", lambda: client.post("/api/v1/wifi/scan-passport", json={"isDemo": True, "demoType": "valid"}).json().get("verified") is True),

        # AI Intent & Feedback & Heartbeat
        ("POST /api/v1/ai/intent", lambda: client.post("/api/v1/ai/intent", json={"transcript": "Find coffee"}).json().get("success") is True),
        ("POST /api/v1/feedback/submit", lambda: client.post("/api/v1/feedback/submit", json={"overallRating": 5}).json().get("success") is True),
        ("POST /api/v1/kiosk/heartbeat", lambda: client.post("/api/v1/kiosk/heartbeat", json={"kioskId": "T3-L1-K04"}).json().get("success") is True),
    ]

    print("==================================================")
    print(" Running Backend Endpoint Automated Test Suite   ")
    print("==================================================")

    for name, test_fn in tests:
        try:
            result = test_fn()
            if result:
                print(f"[PASS] {name}")
                passed += 1
            else:
                print(f"[FAIL] {name}: assertion returned False")
                failed += 1
        except Exception as e:
            print(f"[FAIL] {name}: Exception {e}")
            failed += 1

    print("==================================================")
    print(f" Summary: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("==================================================")

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
