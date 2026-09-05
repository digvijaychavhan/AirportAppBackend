"""
Seed Data Fixtures: Operators, Scan Logs & User Action Audit Logs
"""

import json
from datetime import timedelta
from app.core.security import hash_password
from app.core.timezone import get_current_time

def get_seed_operators():
    default_hashed_pw = hash_password("operator123")
    return [
        {
            "id": "op_101",
            "username": "maya.l",
            "employee_code": "EMP-7840",
            "name": "Maya L.",
            "password": default_hashed_pw,
            "role": "Customer Support Executive",
            "status": "offline",
            "supported_languages": "English, Hindi, Punjabi",
            "calls_handled": 0,
            "avg_handle_time": "0s",
            "resolution_rate": "100%",
            "shift": "Morning (06:00 - 14:00)"
        },
        {
            "id": "op_102",
            "username": "priya.sharma",
            "employee_code": "EMP-9021",
            "name": "Priya Sharma",
            "password": default_hashed_pw,
            "role": "Passenger Assistance Specialist",
            "status": "offline",
            "supported_languages": "English, Hindi, Tamil",
            "calls_handled": 0,
            "avg_handle_time": "0s",
            "resolution_rate": "100%",
            "shift": "Morning (06:00 - 14:00)"
        },
        {
            "id": "op_103",
            "username": "rahul.verma",
            "employee_code": "EMP-9022",
            "name": "Rahul Verma",
            "password": default_hashed_pw,
            "role": "Accessibility & ADA Officer",
            "status": "offline",
            "supported_languages": "English, Hindi, Marathi",
            "calls_handled": 0,
            "avg_handle_time": "0s",
            "resolution_rate": "100%",
            "shift": "Evening (14:00 - 22:00)"
        },
        {
            "id": "op_104",
            "username": "ananya.patel",
            "employee_code": "EMP-9023",
            "name": "Ananya Patel",
            "password": default_hashed_pw,
            "role": "Customer Support Executive",
            "status": "offline",
            "supported_languages": "English, Gujarati, Hindi",
            "calls_handled": 0,
            "avg_handle_time": "0s",
            "resolution_rate": "100%",
            "shift": "Night (22:00 - 06:00)"
        }
    ]

def get_seed_scan_logs():
    now = get_current_time()
    return [
        {
            "kiosk_id": "KIOSK-T3-L1-04",
            "passenger_name": "Luc Desmarais",
            "flight_number": "6E 2262",
            "pnr": "ABC123",
            "seat": "14B",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "SUCCESS",
            "failure_reason": None,
            "raw_data": "M1DESMARAIS/LUC       EABC123 DELPNQ6E 2262 224Y014B0012 100",
            "created_at": now - timedelta(minutes=4)
        },
        {
            "kiosk_id": "KIOSK-T3-L1-04",
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
            "kiosk_id": "KIOSK-T3-L1-01",
            "passenger_name": "Emily Watson",
            "flight_number": "UK 812",
            "pnr": "UK3391",
            "seat": "08D",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "SUCCESS",
            "failure_reason": None,
            "raw_data": "M1WATSON/EMILY       EUK3391 DELBLRUK 0812 224Y008D0045 100",
            "created_at": now - timedelta(hours=1, minutes=5)
        },
        {
            "kiosk_id": "KIOSK-T3-L2-01",
            "passenger_name": "Vikram Malhotra",
            "flight_number": "SG 812",
            "pnr": "SG7741",
            "seat": "18C",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "SUCCESS",
            "failure_reason": None,
            "raw_data": "M1MALHOTRA/VIKRAM    ESG7741 DELBOMSG 0812 224Y018C0023 100",
            "created_at": now - timedelta(hours=1, minutes=30)
        },
        {
            "kiosk_id": "KIOSK-T2-A87",
            "passenger_name": "Rajesh Patel",
            "flight_number": "QP 1102",
            "pnr": "QP9912",
            "seat": "05F",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "SUCCESS",
            "failure_reason": None,
            "raw_data": "M1PATEL/RAJESH       EQP9912 DELAMDQP 1102 224Y005F0018 100",
            "created_at": now - timedelta(hours=2, minutes=10)
        },
        {
            "kiosk_id": "KIOSK-T3-L1-02",
            "passenger_name": "Unknown Passenger",
            "flight_number": None,
            "pnr": None,
            "seat": None,
            "barcode_format": "QR_CODE",
            "scan_result": "FAILED",
            "failure_reason": "Unrecognized barcode format / Non-BCBP data",
            "raw_data": "https://payment-link.example.com/qr",
            "created_at": now - timedelta(minutes=45)
        },
        {
            "kiosk_id": "KIOSK-T2-A87",
            "passenger_name": "Rohan Mehra",
            "flight_number": "SG 812",
            "pnr": "SG4401",
            "seat": "21C",
            "barcode_format": "PDF417_BCBP",
            "scan_result": "FAILED",
            "failure_reason": "Corrupted PDF417 checksum - glare on screen",
            "raw_data": "M1MEHRA/ROHAN???????ES??...",
            "created_at": now - timedelta(hours=2, minutes=45)
        }
    ]

def get_seed_user_action_logs():
    now = get_current_time()
    return [
        {
            "kiosk_id": "KIOSK-T3-L1-04",
            "username": "Luc Desmarais",
            "session_id": "sess_seed_001",
            "action_type": "SCAN_BOARDING_PASS",
            "target_element": "Camera Scanner Viewfinder",
            "route": "/flights",
            "details": "Scanned boarding pass for flight 6E 2262 (Luc Desmarais)",
            "metadata_json": json.dumps({"flight": "6E 2262", "pnr": "ABC123", "result": "SUCCESS"}),
            "ip_address": "192.168.1.104",
            "created_at": now - timedelta(minutes=4)
        }
    ]

def get_seed_support_calls():
    return [
        {
            "id": "call_seed_01",
            "kiosk_id": "T1-L1-K01",
            "operator_id": "op_101",
            "status": "ended",
            "ada_priority": False,
            "requested_language": "English",
            "wait_duration_seconds": 12,
            "call_duration_seconds": 134,
            "issue_category": "Location & Wayfinding",
            "operator_notes": "Passenger assisted with gate directions to Gate B12.",
            "passenger_name": "Luc Desmarais",
            "flight_number": "6E 2262",
            "pnr": "ABC123",
            "recording_url": None,
            "recording_duration_seconds": 0
        }
    ]

def get_seed_feedback_submissions():
    return [
        {
            "kiosk_id": "KIOSK-T3-L1-04",
            "flight_number": "6E 2262",
            "pnr": "ABC123",
            "overall_rating": 5,
            "cleanliness_rating": 5,
            "staff_rating": 5,
            "wayfinding_rating": 5,
            "wifi_rating": 5,
            "food_rating": 4,
            "comments": "Seamless boarding pass scan and intuitive wayfinding map at the Terminal 3 kiosk.",
            "contact_phone": "+91 98765 43210"
        }
    ]
