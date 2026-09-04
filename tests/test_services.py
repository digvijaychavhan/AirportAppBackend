"""
Unit Tests for Pure Service Business Logic
Covers IATA BCBP barcode parsing, spatial Dijkstra pathfinding, MRZ check digits, and password security.
"""

import pytest
from app.modules.flights.service import decode_bcbp, clean_passenger_name, clean_seat_number
from app.modules.wayfinding.service import compute_indoor_route
from app.modules.wifi.service import calculate_icao_check_digit, clean_mrz_line
from app.core.security import hash_password, verify_password, generate_numeric_otp


# 1. BCBP Barcode Decoder Tests
def test_bcbp_valid_resolution_792():
    sample = "M1DOE/JOHN            EABC123 LHRJFKBA 0115 142Y012A0045100"
    decoded = decode_bcbp(sample)

    assert decoded["format_code"] == "M"
    assert decoded["number_of_legs"] == 1
    assert decoded["passenger_name"] == "John Doe"
    assert decoded["pnr"] == "ABC123"
    assert decoded["origin_iata"] == "LHR"
    assert decoded["destination_iata"] == "JFK"
    assert decoded["airline_code"] == "BA"
    assert decoded["flight_number"] == "BA 115"
    assert decoded["seat_number"] == "12A"
    assert decoded["cabin_class"] == "Economy Class (Y)"


def test_bcbp_invalid_length_raises():
    with pytest.raises(ValueError, match="at least 56 chars"):
        decode_bcbp("M1SHORT_STRING")


def test_bcbp_helper_cleaners():
    assert clean_passenger_name("SMITH/JOHN MR") == "John Smith"
    assert clean_seat_number("014B") == "14B"
    assert clean_seat_number("001A") == "1A"


# 2. Indoor Spatial Pathfinding Tests
def test_pathfinding_route_elevator_mode():
    result = compute_indoor_route(
        origin_node_id="node_kiosk_t3_l1_04",
        destination_poi_id="node_gate_b12",
        accessibility_mode="elevator"
    )
    assert result["success"] is True
    assert len(result["path"]) >= 2
    assert result["totalDistanceMeters"] > 0
    assert result["estimatedWalkTimeMinutes"] >= 1
    assert any("node_elevator" in node for node in result["path"])


def test_pathfinding_route_escalator_mode():
    result = compute_indoor_route(
        origin_node_id="kiosk_t3_l1",
        destination_poi_id="node_gate_b12",
        accessibility_mode="escalator"
    )
    assert result["success"] is True
    assert len(result["path"]) >= 2
    assert "qrCodeUrl" in result


# 3. ICAO Doc 9303 MRZ Math Tests
def test_icao_check_digit_calculation():
    # Test standard check digit calculation with 7-3-1 weights
    # "L898902C3" check digit is 6
    assert calculate_icao_check_digit("L898902C3") == 6
    # "740812" check digit is 2
    assert calculate_icao_check_digit("740812") == 2


def test_clean_mrz_line():
    raw = "P<INDDESMARAIS<<LUC<<<<<<  "
    cleaned = clean_mrz_line(raw)
    assert " " not in cleaned
    assert cleaned.startswith("P<IND")


# 4. Security & Password Hashing Tests
def test_password_hashing_and_verification():
    plain = "operatorSecret2026!"
    hashed = hash_password(plain)

    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(plain, hashed) is True
    assert verify_password("wrongPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_numeric_otp_generation():
    otp = generate_numeric_otp(6)
    assert len(otp) == 6
    assert otp.isdigit()
