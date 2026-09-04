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

def test_bcbp_decode_empty():
    response = client.post("/api/v1/flights/bcbp-decode", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "required" in data["error"].lower()

def test_bcbp_decode_valid():
    sample = "M1DOE/JOHN            EABC123 LHRJFKBA 0115 142Y012A0045100"
    response = client.post("/api/v1/flights/bcbp-decode", json={"rawBarcode": sample})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["passengerName"] == "John Doe"
    assert data["data"]["pnr"] == "ABC123"
    assert data["data"]["flightNumber"] == "BA 115"
    assert data["data"]["origin"] == "LHR"
    assert data["data"]["destination"] == "JFK"
    assert data["data"]["seatNumber"] == "12A"

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

def test_flights_pagination():
    response = client.get("/api/v1/flights/search?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "pagination" in data
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["offset"] == 0
    assert len(data["data"]) <= 2

