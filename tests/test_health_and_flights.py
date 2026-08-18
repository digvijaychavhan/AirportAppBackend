"""
Tests for Health, Flights Search, BCBP Decoding, and Baggage Belts
"""

import pytest
from fastapi.testclient import TestClient
from app.main import fastapi_app

client = TestClient(fastapi_app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_flights_search_all():
    response = client.get("/api/v1/flights/search")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

def test_flights_search_query():
    response = client.get("/api/v1/flights/search?query=6E")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert any("6E" in f["flightNumber"] or f.get("airlineCode") == "6E" for f in data["data"])

def test_bcbp_decode_default():
    response = client.post("/api/v1/flights/bcbp-decode", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["passengerName"] == "Nirant Patil"
    assert data["data"]["flightNumber"] == "6E 2262"

def test_baggage_belts():
    response = client.get("/api/v1/baggage/belts")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 3

def test_transfer_shuttles():
    response = client.get("/api/v1/transfer/shuttles")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 3
