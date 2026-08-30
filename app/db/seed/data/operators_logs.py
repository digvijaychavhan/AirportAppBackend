"""
Seed Data Fixtures: Operators, Scan Logs & User Action Audit Logs
"""

import json
from datetime import datetime, timedelta

def get_seed_operators():
    return [
        {
            "id": "op_101",
            "username": "maya.l",
            "employee_code": "EMP-7840",
            "name": "Maya L.",
            "password": "operator123",
            "role": "Customer Support Executive",
            "status": "available",
            "supported_languages": "English, Hindi, Punjabi",
            "calls_handled": 38,
            "avg_handle_time": "2m 14s",
            "resolution_rate": "99%",
            "shift": "Morning (06:00 - 14:00)"
        },
        {
            "id": "op_102",
            "username": "priya.sharma",
            "employee_code": "EMP-9021",
            "name": "Priya Sharma",
            "password": "operator123",
            "role": "Passenger Assistance Specialist",
            "status": "available",
            "supported_languages": "English, Hindi, Tamil",
            "calls_handled": 29,
            "avg_handle_time": "2m 45s",
            "resolution_rate": "97%",
            "shift": "Morning (06:00 - 14:00)"
        },
        {
            "id": "op_103",
            "username": "rahul.verma",
            "employee_code": "EMP-9022",
            "name": "Rahul Verma",
            "password": "operator123",
            "role": "Accessibility & ADA Officer",
            "status": "offline",
            "supported_languages": "English, Hindi, Marathi",
            "calls_handled": 17,
            "avg_handle_time": "3m 10s",
            "resolution_rate": "100%",
            "shift": "Evening (14:00 - 22:00)"
        },
        {
            "id": "op_104",
            "username": "ananya.patel",
            "employee_code": "EMP-9023",
            "name": "Ananya Patel",
            "password": "operator123",
            "role": "Customer Support Executive",
            "status": "available",
            "supported_languages": "English, Gujarati, Hindi",
            "calls_handled": 42,
            "avg_handle_time": "1m 58s",
            "resolution_rate": "98%",
            "shift": "Night (22:00 - 06:00)"
        }
    ]

def get_seed_scan_logs():
    now = datetime.utcnow()
    return [
        {
            "kiosk_id": "T3-L1-K04",
            "passenger_name": "Luc Desmarais",
            "flight_number": "6E 203",
            "pnr": "ABC123",
            "seat": "14B",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "SUCCESS",
            "failure_reason": None,
            "raw_data": "M1DESMARAIS/LUC       EABC123 DELMAA6E 0203 224Y014B0012 100",
            "created_at": now - timedelta(minutes=4)
        },
        {
            "kiosk_id": "T3-L1-K04",
            "passenger_name": "Aditi Sharma",
            "flight_number": "AI 101",
            "pnr": "AI8829",
            "seat": "02A",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "SUCCESS",
            "failure_reason": None,
            "raw_data": "M1SHARMA/ADITI       EAI8829 DELLHR6E 0101 224J002A0001 100",
            "created_at": now - timedelta(minutes=18)
        },
        {
            "kiosk_id": "T3-L1-K02",
            "passenger_name": "Unknown Passenger",
            "flight_number": None,
            "pnr": None,
            "seat": None,
            "barcode_format": "QR_CODE",
            "scan_result": "FAILED",
            "failure_reason": "Unrecognized barcode format / Non-BCBP data",
            "raw_data": "https://payment-link.example.com/qr",
            "created_at": now - timedelta(minutes=32)
        },
        {
            "kiosk_id": "T2-A87",
            "passenger_name": "Rohan Mehra",
            "flight_number": "SG 812",
            "pnr": "SG4401",
            "seat": "21C",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "FAILED",
            "failure_reason": "Corrupted PDF417 checksum - glare on screen",
            "raw_data": "M1MEHRA/ROHAN???????ES??...",
            "created_at": now - timedelta(hours=1, minutes=12)
        },
        {
            "kiosk_id": "T3-L1-K01",
            "passenger_name": "Emily Watson",
            "flight_number": "UK 955",
            "pnr": "UK3391",
            "seat": "08D",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "SUCCESS",
            "failure_reason": None,
            "raw_data": "M1WATSON/EMILY       EUK3391 DELBOMUK 0955 224Y008D0045 100",
            "created_at": now - timedelta(hours=2, minutes=5)
        }
    ]

def get_seed_user_action_logs():
    now = datetime.utcnow()
    return [
        {
            "kiosk_id": "T3-L1-K04",
            "username": "Luc Desmarais",
            "session_id": "sess_1001",
            "action_type": "SCAN_BOARDING_PASS",
            "target_element": "Camera Scanner Viewfinder",
            "route": "/flights",
            "details": "Scanned boarding pass for flight 6E 203 (Luc Desmarais)",
            "metadata_json": json.dumps({"flight": "6E 203", "pnr": "ABC123", "result": "SUCCESS"}),
            "ip_address": "192.168.1.104",
            "created_at": now - timedelta(minutes=4)
        },
        {
            "kiosk_id": "T3-L1-K04",
            "username": "Luc Desmarais",
            "session_id": "sess_1001",
            "action_type": "WAYFINDING_SEARCH",
            "target_element": "Option: Elevator",
            "route": "/directions",
            "details": "Selected route from Kiosk to Bikanervala via Elevator",
            "metadata_json": json.dumps({"origin": "kiosk", "destination": "bikanervala", "mode": "elevator"}),
            "ip_address": "192.168.1.104",
            "created_at": now - timedelta(minutes=3)
        },
        {
            "kiosk_id": "T3-L1-K04",
            "username": "Luc Desmarais",
            "session_id": "sess_1001",
            "action_type": "CLICK",
            "target_element": "Button: L2 Departures",
            "route": "/map",
            "details": "Switched map floor view to Level 2 (Departures)",
            "metadata_json": json.dumps({"floor": 2}),
            "ip_address": "192.168.1.104",
            "created_at": now - timedelta(minutes=2)
        },
        {
            "kiosk_id": "T3-L1-K04",
            "username": None,  # Guest user
            "session_id": "sess_1002",
            "action_type": "CLICK",
            "target_element": "Card: Shopping & Duty Free",
            "route": "/wayfinding",
            "details": "Guest browsed Shopping directory",
            "metadata_json": json.dumps({"category": "shopping"}),
            "ip_address": "192.168.1.104",
            "created_at": now - timedelta(minutes=1)
        },
        {
            "kiosk_id": "T3-L1-K04",
            "username": "Luc Desmarais",
            "session_id": "sess_1001",
            "action_type": "START_VIDEO_CALL",
            "target_element": "Button: Connect Live Operator",
            "route": "/support",
            "details": "Initiated video call with customer support (Call ID: call_demo_101)",
            "metadata_json": json.dumps({"agent": "live", "adaPriority": True}),
            "ip_address": "192.168.1.104",
            "created_at": now - timedelta(seconds=30)
        }
    ]
