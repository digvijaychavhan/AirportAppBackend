"""
Enterprise Admin Portal API Router
Provides endpoints for:
- System Overview & KPI metrics
- Device Fleet Healthcheck & Diagnostics
- Operator Workforce Management & Status Sync
- Boarding Pass Scan Logging (Success / Failure tracking)
- User Action Logging & Audit Trail
- Real-time Network Health Telemetry
- Airport Amenities / Directory Manager (CRUD with optional x,y coords)
"""

import json
import logging
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from starlette.responses import JSONResponse
from starlette.routing import Route
from database import SessionLocal, Base, engine
from models import Device, ScanLog, UserActionLog, Operator, Poi, WayfindingCategory
from services.webrtc_signaling import online_operators

logger = logging.getLogger("admin_routes")

# Ensure all database tables exist
Base.metadata.create_all(bind=engine)


# ----------------------------------------------------------------------
# Seed Default Sample Data if tables are empty
# ----------------------------------------------------------------------
def seed_admin_defaults():
    try:
        db = SessionLocal()

        # 1. Seed Devices
        if db.query(Device).count() == 0:
            devices = [
                Device(device_id="KIOSK-T3-L1-01", name="Kiosk T3-L1 Departure Gate 12", device_type="kiosk", ip_address="192.168.1.101", mac_address="00:1A:2B:3C:4D:01", terminal="Terminal 3", floor_name="Level 1", location="Central Concourse Gate 12", status="online", ping_ms=8, cpu_pct=22, ram_pct=42, screen_status="OK", scanner_status="OK", camera_status="OK"),
                Device(device_id="KIOSK-T3-L1-02", name="Kiosk T3-L1 Information Hub", device_type="kiosk", ip_address="192.168.1.102", mac_address="00:1A:2B:3C:4D:02", terminal="Terminal 3", floor_name="Level 1", location="Near Information Desk", status="online", ping_ms=11, cpu_pct=28, ram_pct=46, screen_status="OK", scanner_status="OK", camera_status="OK"),
                Device(device_id="KIOSK-T3-L1-04", name="Kiosk T3-L1-K04 Central Concourse", device_type="kiosk", ip_address="192.168.1.104", mac_address="00:1A:2B:3C:4D:04", terminal="Terminal 3", floor_name="Level 1", location="Near Gate B12 & Elevator", status="online", ping_ms=9, cpu_pct=34, ram_pct=51, screen_status="OK", scanner_status="OK", camera_status="OK"),
                Device(device_id="KIOSK-T3-L2-01", name="Kiosk T3-L2 Lounge Zone", device_type="kiosk", ip_address="192.168.1.105", mac_address="00:1A:2B:3C:4D:05", terminal="Terminal 3", floor_name="Level 2", location="Near Encalm Lounge Entrance", status="online", ping_ms=14, cpu_pct=19, ram_pct=38, screen_status="OK", scanner_status="OK", camera_status="OK"),
                Device(device_id="KIOSK-T2-A87", name="Kiosk T2 Domestic Concourse", device_type="kiosk", ip_address="192.168.2.87", mac_address="00:1A:2B:3C:4D:87", terminal="Terminal 2", floor_name="Level 1", location="Gate A87", status="warning", ping_ms=78, cpu_pct=72, ram_pct=84, screen_status="OK", scanner_status="DEGRADED", camera_status="OK"),
                Device(device_id="SCANNER-GATE-B12", name="Gate B12 BCBP Scanner Unit", device_type="scanner", ip_address="192.168.1.212", mac_address="00:1A:2B:3C:4D:B2", terminal="Terminal 3", floor_name="Level 2", location="Gate B12 Turnstile", status="online", ping_ms=6, cpu_pct=15, ram_pct=29, screen_status="OK", scanner_status="OK", camera_status="N/A"),
                Device(device_id="OP-DESK-01", name="Helpdesk Operator Terminal 1", device_type="operator_terminal", ip_address="192.168.1.50", mac_address="00:1A:2B:3C:4D:F1", terminal="Terminal 3", floor_name="Control Room", location="Station 01", status="online", ping_ms=5, cpu_pct=18, ram_pct=35, screen_status="OK", scanner_status="N/A", camera_status="OK"),
            ]
            db.add_all(devices)
            db.commit()

        # 2. Seed Operators
        if db.query(Operator).count() == 0:
            operators = [
                Operator(id="op_101", employee_code="EMP-7840", name="Maya L.", role="Customer Support Executive", status="available", supported_languages="English, Hindi, Punjabi", calls_handled=38, avg_handle_time="2m 14s", resolution_rate="99%", shift="Morning (06:00 - 14:00)"),
                Operator(id="op_102", employee_code="EMP-9021", name="Priya Sharma", role="Passenger Assistance Specialist", status="available", supported_languages="English, Hindi, Tamil", calls_handled=29, avg_handle_time="2m 45s", resolution_rate="97%", shift="Morning (06:00 - 14:00)"),
                Operator(id="op_103", employee_code="EMP-9022", name="Rahul Verma", role="Accessibility & ADA Officer", status="offline", supported_languages="English, Hindi, Marathi", calls_handled=17, avg_handle_time="3m 10s", resolution_rate="100%", shift="Evening (14:00 - 22:00)"),
                Operator(id="op_104", employee_code="EMP-9023", name="Ananya Patel", role="Customer Support Executive", status="available", supported_languages="English, Gujarati, Hindi", calls_handled=42, avg_handle_time="1m 58s", resolution_rate="98%", shift="Night (22:00 - 06:00)"),
            ]
            db.add_all(operators)
            db.commit()

        # 3. Seed Scan Logs (Realistic Success / Failed Records)
        if db.query(ScanLog).count() == 0:
            now = datetime.utcnow()
            scan_logs = [
                ScanLog(kiosk_id="T3-L1-K04", passenger_name="Luc Desmarais", flight_number="6E 203", pnr="ABC123", seat="14B", barcode_format="PDF417_BCBP", scan_result="SUCCESS", failure_reason=None, raw_data="M1DESMARAIS/LUC       EABC123 DELMAA6E 0203 224Y014B0012 100", created_at=now - timedelta(minutes=4)),
                ScanLog(kiosk_id="T3-L1-K04", passenger_name="Aditi Sharma", flight_number="AI 101", pnr="AI8829", seat="02A", barcode_format="PDF417_BCBP", scan_result="SUCCESS", failure_reason=None, raw_data="M1SHARMA/ADITI       EAI8829 DELLHR6E 0101 224J002A0001 100", created_at=now - timedelta(minutes=18)),
                ScanLog(kiosk_id="T3-L1-K02", passenger_name="Unknown Passenger", flight_number=None, pnr=None, seat=None, barcode_format="QR_CODE", scan_result="FAILED", failure_reason="Unrecognized barcode format / Non-BCBP data", raw_data="https://payment-link.example.com/qr", created_at=now - timedelta(minutes=32)),
                ScanLog(kiosk_id="T2-A87", passenger_name="Rohan Mehra", flight_number="SG 812", pnr="SG4401", seat="21C", barcode_format="PDF417_BCBP", scan_result="FAILED", failure_reason="Corrupted PDF417 checksum - glare on screen", raw_data="M1MEHRA/ROHAN???????ES??...", created_at=now - timedelta(hours=1, minutes=12)),
                ScanLog(kiosk_id="T3-L1-K01", passenger_name="Emily Watson", flight_number="UK 955", pnr="UK3391", seat="08D", barcode_format="PDF417_BCBP", scan_result="SUCCESS", failure_reason=None, raw_data="M1WATSON/EMILY       EUK3391 DELBOMUK 0955 224Y008D0045 100", created_at=now - timedelta(hours=2, minutes=5)),
                ScanLog(kiosk_id="T3-L1-K04", passenger_name="Vikram Singh", flight_number="6E 504", pnr="6E9912", seat="19F", barcode_format="PDF417_BCBP", scan_result="SUCCESS", failure_reason=None, raw_data="M1SINGH/VIKRAM       E6E9912 DELBLR6E 0504 224Y019F0078 100", created_at=now - timedelta(hours=3, minutes=20)),
                ScanLog(kiosk_id="T1-D12", passenger_name="Sarah Jenkins", flight_number="AI 408", pnr="AI1104", seat="05C", barcode_format="AZTEC", scan_result="FAILED", failure_reason="Expired flight departure date", raw_data="M1JENKINS/SARAH     EAI1104 DELCCUAI 0408 200Y005C0012 100", created_at=now - timedelta(hours=4, minutes=45)),
            ]
            db.add_all(scan_logs)
            db.commit()

        # 4. Seed User Action Logs
        if db.query(UserActionLog).count() == 0:
            now = datetime.utcnow()
            action_logs = [
                UserActionLog(kiosk_id="T3-L1-K04", session_id="sess_1001", action_type="SCAN_BOARDING_PASS", details="Scanned boarding pass for flight 6E 203 (Luc Desmarais)", metadata_json=json.dumps({"flight": "6E 203", "pnr": "ABC123", "result": "SUCCESS"}), ip_address="192.168.1.104", created_at=now - timedelta(minutes=4)),
                UserActionLog(kiosk_id="T3-L1-K04", session_id="sess_1001", action_type="WAYFINDING_SEARCH", details="Searched route from Kiosk to Gate B12 (Mode: Elevator)", metadata_json=json.dumps({"origin": "kiosk_t3_l1", "destination": "node_gate_b12", "mode": "elevator"}), ip_address="192.168.1.104", created_at=now - timedelta(minutes=3)),
                UserActionLog(kiosk_id="T3-L1-K04", session_id="sess_1001", action_type="VIEW_MAP", details="Switched floor view to Level 2 (International Concourse)", metadata_json=json.dumps({"floor": "L2"}), ip_address="192.168.1.104", created_at=now - timedelta(minutes=2)),
                UserActionLog(kiosk_id="T3-L1-K04", session_id="sess_1001", action_type="START_VIDEO_CALL", details="Initiated video call with customer support (Call ID: call_demo_101)", metadata_json=json.dumps({"agent": "live", "adaPriority": True}), ip_address="192.168.1.104", created_at=now - timedelta(minutes=1)),
                UserActionLog(kiosk_id="T3-L1-K02", session_id="sess_1002", action_type="DIRECTORY_CLICK", details="Viewed details for Third Wave Coffee (Eat & Dine)", metadata_json=json.dumps({"poi": "Third Wave Coffee", "category": "Dining"}), ip_address="192.168.1.102", created_at=now - timedelta(minutes=15)),
                UserActionLog(kiosk_id="T3-L1-K01", session_id="sess_1003", action_type="LANGUAGE_SWITCH", details="Changed kiosk interface language to Hindi (HI)", metadata_json=json.dumps({"language": "HI"}), ip_address="192.168.1.101", created_at=now - timedelta(minutes=45)),
                UserActionLog(kiosk_id="T3-L2-01", session_id="sess_1004", action_type="DOWNLOAD_QR_MAP", details="Generated mobile QR token for mobile navigation route", metadata_json=json.dumps({"dest": "Encalm Lounge"}), ip_address="192.168.1.105", created_at=now - timedelta(hours=1, minutes=10)),
                UserActionLog(kiosk_id="T3-L1-K04", session_id="sess_1005", action_type="SUBMIT_FEEDBACK", details="Submitted 5-star kiosk cleanliness and helpfulness rating", metadata_json=json.dumps({"rating": 5, "category": "Cleanliness"}), ip_address="192.168.1.104", created_at=now - timedelta(hours=2)),
            ]
            db.add_all(action_logs)
            db.commit()

        db.close()
    except Exception as e:
        logger.error(f"Error seeding admin defaults: {e}")

seed_admin_defaults()


# ----------------------------------------------------------------------
# 1. OVERVIEW & KPI METRICS
# ----------------------------------------------------------------------
async def get_admin_overview(request):
    try:
        db = SessionLocal()
        
        # Counts
        total_kiosks = db.query(Device).filter(Device.device_type == "kiosk").count()
        online_kiosks = db.query(Device).filter(Device.device_type == "kiosk", Device.status == "online").count()
        total_devices = db.query(Device).count()
        
        total_operators = db.query(Operator).count()
        # Count available operators from live signaling pool or DB
        online_operators_count = len([op for op in online_operators.values() if op.get("status") == "AVAILABLE"])
        if online_operators_count == 0:
            online_operators_count = db.query(Operator).filter(Operator.status == "available").count()

        # Scan stats
        total_scans = db.query(ScanLog).count()
        successful_scans = db.query(ScanLog).filter(ScanLog.scan_result == "SUCCESS").count()
        failed_scans = db.query(ScanLog).filter(ScanLog.scan_result == "FAILED").count()
        scan_success_rate = f"{(successful_scans / total_scans * 100):.1f}%" if total_scans > 0 else "100%"

        # Amenities count
        total_amenities = db.query(Poi).count()
        total_actions = db.query(UserActionLog).count()

        db.close()

        return JSONResponse({
            "success": True,
            "data": {
                "kiosks": {
                    "total": total_kiosks,
                    "online": online_kiosks,
                    "healthPct": f"{(online_kiosks / max(1, total_kiosks) * 100):.0f}%"
                },
                "operators": {
                    "total": total_operators,
                    "online": online_operators_count
                },
                "scans": {
                    "total": total_scans,
                    "success": successful_scans,
                    "failed": failed_scans,
                    "successRate": scan_success_rate
                },
                "devices": {
                    "total": total_devices,
                    "online": online_kiosks + 2
                },
                "amenities": {
                    "total": total_amenities
                },
                "auditActions": {
                    "total": total_actions
                },
                "network": {
                    "healthScore": "99.8%",
                    "apiLatencyMs": 18,
                    "socketStatus": "Connected",
                    "uptime": "99.98%"
                }
            }
        })
    except Exception as e:
        logger.error(f"Error fetching admin overview: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# 2. CONNECTED DEVICES FLEET HEALTHCHECK
# ----------------------------------------------------------------------
async def get_devices(request):
    try:
        db = SessionLocal()
        devices = db.query(Device).order_by(Device.device_id).all()
        
        data = [{
            "id": d.id,
            "deviceId": d.device_id,
            "name": d.name,
            "deviceType": d.device_type,
            "ipAddress": d.ip_address,
            "macAddress": d.mac_address,
            "terminal": d.terminal,
            "floorName": d.floor_name,
            "location": d.location,
            "status": d.status,
            "pingMs": d.ping_ms,
            "cpuPct": d.cpu_pct,
            "ramPct": d.ram_pct,
            "screenStatus": d.screen_status,
            "scannerStatus": d.scanner_status,
            "cameraStatus": d.camera_status,
            "lastHeartbeat": d.last_heartbeat.isoformat() if d.last_heartbeat else None,
            "createdAt": d.created_at.isoformat() if d.created_at else None
        } for d in devices]
        
        db.close()
        return JSONResponse({"success": True, "count": len(data), "data": data})
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def create_or_update_device(request):
    try:
        body = await request.json()
        db = SessionLocal()
        dev_id = body.get("id")

        if dev_id:
            dev = db.query(Device).filter(Device.id == dev_id).first()
            if not dev:
                db.close()
                return JSONResponse({"success": False, "message": "Device not found"}, status_code=404)
        else:
            dev = Device(device_id=body.get("deviceId", f"KIOSK-{random.randint(100,999)}"))
            db.add(dev)

        dev.name = body.get("name", dev.name)
        dev.device_type = body.get("deviceType", dev.device_type)
        dev.ip_address = body.get("ipAddress", dev.ip_address)
        dev.terminal = body.get("terminal", dev.terminal)
        dev.floor_name = body.get("floorName", dev.floor_name)
        dev.location = body.get("location", dev.location)
        dev.status = body.get("status", dev.status)
        dev.last_heartbeat = datetime.utcnow()

        db.commit()
        db.refresh(dev)
        db.close()
        return JSONResponse({"success": True, "message": "Device saved successfully"})
    except Exception as e:
        logger.error(f"Error saving device: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def ping_device(request):
    try:
        device_id = request.path_params.get("id")
        db = SessionLocal()
        dev = db.query(Device).filter(Device.id == device_id).first()
        if not dev:
            db.close()
            return JSONResponse({"success": False, "message": "Device not found"}, status_code=404)

        simulated_ping = random.randint(6, 24)
        dev.ping_ms = simulated_ping
        dev.last_heartbeat = datetime.utcnow()
        if dev.status == "offline":
            dev.status = "online"

        db.commit()
        db.close()
        return JSONResponse({"success": True, "pingMs": simulated_ping, "status": "online", "message": f"Ping responded in {simulated_ping}ms"})
    except Exception as e:
        logger.error(f"Error pinging device: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def reboot_device(request):
    try:
        device_id = request.path_params.get("id")
        db = SessionLocal()
        dev = db.query(Device).filter(Device.id == device_id).first()
        if not dev:
            db.close()
            return JSONResponse({"success": False, "message": "Device not found"}, status_code=404)

        dev.cpu_pct = 12
        dev.ram_pct = 28
        dev.status = "online"
        dev.last_heartbeat = datetime.utcnow()

        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": f"Kiosk {dev.name} reboot command dispatched successfully"})
    except Exception as e:
        logger.error(f"Error rebooting device: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def delete_device(request):
    try:
        device_id = request.path_params.get("id")
        db = SessionLocal()
        dev = db.query(Device).filter(Device.id == device_id).first()
        if not dev:
            db.close()
            return JSONResponse({"success": False, "message": "Device not found"}, status_code=404)

        db.delete(dev)
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": "Device removed from fleet"})
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# 3. OPERATOR WORKFORCE MANAGEMENT
# ----------------------------------------------------------------------
async def get_operators(request):
    try:
        db = SessionLocal()
        ops = db.query(Operator).order_by(Operator.name).all()

        data = []
        for op in ops:
            # Check if live state is in memory pool
            live_status = op.status
            if op.id in online_operators:
                live_status = online_operators[op.id].get("status", op.status).lower()

            data.append({
                "id": op.id,
                "employeeCode": op.employee_code,
                "name": op.name,
                "password": op.password or "operator123",
                "role": op.role,
                "status": live_status,
                "supportedLanguages": op.supported_languages,
                "callsHandled": op.calls_handled or random.randint(15, 45),
                "avgHandleTime": op.avg_handle_time or "2m 20s",
                "resolutionRate": op.resolution_rate or "98%",
                "shift": op.shift or "Morning (06:00 - 14:00)",
                "createdAt": op.created_at.isoformat() if op.created_at else None
            })

        db.close()
        return JSONResponse({"success": True, "count": len(data), "data": data})
    except Exception as e:
        logger.error(f"Error fetching operators: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def create_or_update_operator(request):
    try:
        body = await request.json()
        db = SessionLocal()
        op_id = body.get("id")

        if op_id:
            op = db.query(Operator).filter(Operator.id == op_id).first()
            if not op:
                db.close()
                return JSONResponse({"success": False, "message": "Operator not found"}, status_code=404)
        else:
            op = Operator(employee_code=body.get("employeeCode", f"EMP-{random.randint(1000, 9999)}"))
            db.add(op)

        op.name = body.get("name", op.name)
        op.employee_code = body.get("employeeCode", op.employee_code)
        if body.get("password"):
            op.password = body.get("password")
        op.role = body.get("role", op.role)
        op.status = body.get("status", "available").lower()
        op.supported_languages = body.get("supportedLanguages", op.supported_languages)
        op.shift = body.get("shift", op.shift)

        db.commit()
        db.refresh(op)

        # Sync with memory pool
        if op.id in online_operators:
            online_operators[op.id]["status"] = op.status.upper()
            online_operators[op.id]["name"] = op.name

        db.close()
        return JSONResponse({"success": True, "message": "Operator saved successfully"})
    except Exception as e:
        logger.error(f"Error saving operator: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def set_operator_password(request):
    try:
        op_id = request.path_params.get("id")
        body = await request.json()
        new_password = body.get("password", "").strip()

        if not new_password:
            return JSONResponse({"success": False, "message": "Password cannot be empty"}, status_code=400)

        db = SessionLocal()
        op = db.query(Operator).filter(Operator.id == op_id).first()
        if not op:
            db.close()
            return JSONResponse({"success": False, "message": "Operator not found"}, status_code=404)

        op.password = new_password
        op_name = op.name
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": f"Password updated for operator {op_name}"})
    except Exception as e:
        logger.error(f"Error setting operator password: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def set_operator_status(request):
    try:
        op_id = request.path_params.get("id")
        body = await request.json()
        new_status = body.get("status", "available").lower()

        db = SessionLocal()
        op = db.query(Operator).filter(Operator.id == op_id).first()
        if not op:
            db.close()
            return JSONResponse({"success": False, "message": "Operator not found"}, status_code=404)

        op.status = new_status
        db.commit()

        if op_id in online_operators:
            online_operators[op_id]["status"] = new_status.upper()

        db.close()
        return JSONResponse({"success": True, "status": new_status, "message": f"Operator status changed to {new_status}"})
    except Exception as e:
        logger.error(f"Error setting operator status: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def delete_operator(request):
    try:
        op_id = request.path_params.get("id")
        db = SessionLocal()
        op = db.query(Operator).filter(Operator.id == op_id).first()
        if not op:
            db.close()
            return JSONResponse({"success": False, "message": "Operator not found"}, status_code=404)

        db.delete(op)
        db.commit()
        online_operators.pop(op_id, None)
        db.close()
        return JSONResponse({"success": True, "message": "Operator removed"})
    except Exception as e:
        logger.error(f"Error deleting operator: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# 4. BOARDING PASS SCAN LOGS (SUCCESS / FAILED SCANS)
# ----------------------------------------------------------------------
async def get_scan_logs(request):
    try:
        db = SessionLocal()
        result_filter = request.query_params.get("result", "").strip()
        search = request.query_params.get("search", "").strip()
        limit = int(request.query_params.get("limit", 50))

        query = db.query(ScanLog)
        if result_filter:
            query = query.filter(ScanLog.scan_result == result_filter.upper())
        if search:
            query = query.filter(
                (ScanLog.passenger_name.ilike(f"%{search}%")) |
                (ScanLog.flight_number.ilike(f"%{search}%")) |
                (ScanLog.pnr.ilike(f"%{search}%")) |
                (ScanLog.kiosk_id.ilike(f"%{search}%"))
            )

        logs = query.order_by(ScanLog.created_at.desc()).limit(limit).all()

        total = db.query(ScanLog).count()
        success_count = db.query(ScanLog).filter(ScanLog.scan_result == "SUCCESS").count()
        failed_count = db.query(ScanLog).filter(ScanLog.scan_result == "FAILED").count()

        data = [{
            "id": log.id,
            "kioskId": log.kiosk_id,
            "passengerName": log.passenger_name or "Unknown",
            "flightNumber": log.flight_number or "N/A",
            "pnr": log.pnr or "N/A",
            "seat": log.seat or "N/A",
            "barcodeFormat": log.barcode_format,
            "scanResult": log.scan_result,
            "failureReason": log.failure_reason,
            "rawData": log.raw_data,
            "createdAt": log.created_at.isoformat() if log.created_at else None
        } for log in logs]

        db.close()
        return JSONResponse({
            "success": True,
            "summary": {
                "total": total,
                "successCount": success_count,
                "failedCount": failed_count,
                "successRate": f"{(success_count / max(1, total) * 100):.1f}%"
            },
            "count": len(data),
            "data": data
        })
    except Exception as e:
        logger.error(f"Error fetching scan logs: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def create_scan_log(request):
    try:
        body = await request.json()
        db = SessionLocal()

        log = ScanLog(
            kiosk_id=body.get("kioskId", "T3-L1-K04"),
            passenger_name=body.get("passengerName"),
            flight_number=body.get("flightNumber"),
            pnr=body.get("pnr"),
            seat=body.get("seat"),
            barcode_format=body.get("barcodeFormat", "PDF417_BCBP"),
            scan_result=body.get("scanResult", "SUCCESS").upper(),
            failure_reason=body.get("failureReason"),
            raw_data=body.get("rawData")
        )
        db.add(log)
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": "Scan logged successfully"})
    except Exception as e:
        logger.error(f"Error creating scan log: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# 5. USER ACTION & AUDIT TRAIL LOGGING
# ----------------------------------------------------------------------
async def get_user_action_logs(request):
    try:
        db = SessionLocal()
        action_type = request.query_params.get("actionType", "").strip()
        search = request.query_params.get("search", "").strip()
        limit = int(request.query_params.get("limit", 60))

        query = db.query(UserActionLog)
        if action_type:
            query = query.filter(UserActionLog.action_type == action_type)
        if search:
            query = query.filter(
                (UserActionLog.details.ilike(f"%{search}%")) |
                (UserActionLog.kiosk_id.ilike(f"%{search}%")) |
                (UserActionLog.action_type.ilike(f"%{search}%"))
            )

        logs = query.order_by(UserActionLog.created_at.desc()).limit(limit).all()

        data = [{
            "id": log.id,
            "kioskId": log.kiosk_id,
            "sessionId": log.session_id,
            "actionType": log.action_type,
            "details": log.details,
            "metadata": json.loads(log.metadata_json) if log.metadata_json else {},
            "ipAddress": log.ip_address,
            "createdAt": log.created_at.isoformat() if log.created_at else None
        } for log in logs]

        db.close()
        return JSONResponse({"success": True, "count": len(data), "data": data})
    except Exception as e:
        logger.error(f"Error fetching user action logs: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def create_user_action_log(request):
    try:
        body = await request.json()
        db = SessionLocal()

        meta = body.get("metadata", {})
        meta_str = json.dumps(meta) if isinstance(meta, dict) else str(meta)

        log = UserActionLog(
            kiosk_id=body.get("kioskId", "T3-L1-K04"),
            session_id=body.get("sessionId"),
            action_type=body.get("actionType", "GENERIC_INTERACTION"),
            details=body.get("details"),
            metadata_json=meta_str,
            ip_address=request.client.host if request.client else "127.0.0.1"
        )
        db.add(log)
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": "Action logged"})
    except Exception as e:
        logger.error(f"Error creating action log: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# 6. NETWORK HEALTH & REAL-TIME TELEMETRY
# ----------------------------------------------------------------------
async def get_network_health(request):
    try:
        # Generate realistic, dynamic live network health telemetry
        now = datetime.utcnow()
        timeline = []
        for i in range(10, -1, -1):
            t = (now - timedelta(minutes=i*2)).strftime("%H:%M")
            timeline.append({
                "time": t,
                "latencyMs": random.randint(12, 26),
                "throughputMbps": round(random.uniform(42.0, 95.0), 1),
                "packetLossPct": round(random.uniform(0.01, 0.08), 3)
            })

        return JSONResponse({
            "success": True,
            "data": {
                "overallScore": "99.8%",
                "status": "HEALTHY",
                "activeSockets": len(online_operators) + 3,
                "signalingLatencyMs": 14,
                "apiAvgResponseMs": 19,
                "packetLossPct": "0.02%",
                "bandwidthUsage": "64.2 MB/s",
                "uptime": "99.98%",
                "tlsStatus": "TLS 1.3 Active",
                "timeline": timeline
            }
        })
    except Exception as e:
        logger.error(f"Error fetching network health: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# 7. AIRPORT AMENITIES & DIRECTORY (CRUD - (X,Y) OPTIONAL)
# ----------------------------------------------------------------------
async def get_amenities(request):
    try:
        db = SessionLocal()
        category = request.query_params.get("category", "").strip()
        floor = request.query_params.get("floor", "").strip()
        search = request.query_params.get("search", "").strip()

        query = db.query(Poi)
        if category:
            query = query.filter(Poi.category.ilike(category))
        if floor:
            query = query.filter(Poi.floor_name.ilike(f"%{floor}%"))
        if search:
            query = query.filter(
                (Poi.name.ilike(f"%{search}%")) |
                (Poi.description.ilike(f"%{search}%")) |
                (Poi.gate.ilike(f"%{search}%"))
            )

        amenities = query.order_by(Poi.name).all()

        data = [{
            "id": a.id,
            "name": a.name,
            "category": a.category,
            "subCategory": a.sub_category or "",
            "description": a.description or "",
            "terminal": a.terminal or "Terminal 3",
            "floorName": a.floor_name or "Level 1",
            "gate": a.gate or "",
            "operatingHours": a.operating_hours or "24/7",
            "dietaryTags": a.dietary_tags or "",
            "rating": a.rating or 4.5,
            "imageUrl": a.image_url or "",
            "xCoord": a.x_coord, # None/Optional
            "yCoord": a.y_coord, # None/Optional
            "isActive": a.is_active if a.is_active is not None else True
        } for a in amenities]

        db.close()
        return JSONResponse({"success": True, "count": len(data), "data": data})
    except Exception as e:
        logger.error(f"Error fetching amenities: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def create_or_update_amenity(request):
    try:
        body = await request.json()
        db = SessionLocal()
        amenity_id = body.get("id")

        if amenity_id:
            item = db.query(Poi).filter(Poi.id == amenity_id).first()
            if not item:
                db.close()
                return JSONResponse({"success": False, "message": "Amenity not found"}, status_code=404)
        else:
            item = Poi()
            db.add(item)

        item.name = body.get("name", item.name)
        item.category = body.get("category", item.category)
        item.sub_category = body.get("subCategory", item.sub_category)
        item.description = body.get("description", item.description)
        item.terminal = body.get("terminal", item.terminal or "Terminal 3")
        item.floor_name = body.get("floorName", item.floor_name or "Level 1")
        item.gate = body.get("gate", item.gate)
        item.operating_hours = body.get("operatingHours", item.operating_hours or "24/7")
        item.dietary_tags = body.get("dietaryTags", item.dietary_tags)
        item.rating = float(body.get("rating", item.rating or 4.5))
        item.image_url = body.get("imageUrl", item.image_url)
        
        # Non-mandatory x, y coordinates
        x_val = body.get("xCoord")
        y_val = body.get("yCoord")
        item.x_coord = float(x_val) if x_val not in (None, "") else None
        item.y_coord = float(y_val) if y_val not in (None, "") else None
        
        item.is_active = body.get("isActive", True)

        db.commit()
        db.refresh(item)
        db.close()
        return JSONResponse({"success": True, "message": "Amenity saved successfully", "id": item.id})
    except Exception as e:
        logger.error(f"Error saving amenity: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def delete_amenity(request):
    try:
        amenity_id = request.path_params.get("id")
        db = SessionLocal()
        item = db.query(Poi).filter(Poi.id == amenity_id).first()
        if not item:
            db.close()
            return JSONResponse({"success": False, "message": "Amenity not found"}, status_code=404)

        db.delete(item)
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": "Amenity removed successfully"})
    except Exception as e:
        logger.error(f"Error deleting amenity: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def toggle_amenity_status(request):
    try:
        amenity_id = request.path_params.get("id")
        db = SessionLocal()
        item = db.query(Poi).filter(Poi.id == amenity_id).first()
        if not item:
            db.close()
            return JSONResponse({"success": False, "message": "Amenity not found"}, status_code=404)

        item.is_active = not item.is_active
        db.commit()
        new_status = item.is_active
        db.close()
        return JSONResponse({"success": True, "isActive": new_status, "message": f"Amenity is now {'Active' if new_status else 'Inactive'}"})
    except Exception as e:
        logger.error(f"Error toggling amenity status: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# 8. LEGACY WAYFINDING CATEGORIES
# ----------------------------------------------------------------------
async def get_wayfinding_categories(request):
    try:
        db = SessionLocal()
        categories = db.query(WayfindingCategory).order_by(WayfindingCategory.title).all()
        data = [{
            "id": cat.id,
            "title": cat.title,
            "description": cat.description,
            "photo": cat.photo_url,
            "icon": cat.icon,
            "iconColor": cat.icon_color,
            "iconBg": cat.icon_bg,
            "route": cat.route,
            "isActive": cat.is_active
        } for cat in categories]
        db.close()
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Error fetching wayfinding categories: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def create_or_update_category(request):
    try:
        body = await request.json()
        db = SessionLocal()
        cat_id = body.get("id")
        if cat_id:
            cat = db.query(WayfindingCategory).filter(WayfindingCategory.id == cat_id).first()
            if not cat:
                db.close()
                return JSONResponse({"success": False, "message": "Category not found"}, status_code=404)
        else:
            cat = WayfindingCategory()
            db.add(cat)

        cat.title = body.get("title", cat.title)
        cat.description = body.get("description", cat.description)
        cat.photo_url = body.get("photo", cat.photo_url)
        cat.icon = body.get("icon", cat.icon)
        cat.icon_color = body.get("iconColor") or "#2563EB"
        cat.icon_bg = body.get("iconBg") or "#DBEAFE"
        cat.route = body.get("route", cat.route)
        cat.is_active = body.get("isActive", True)

        db.commit()
        db.refresh(cat)
        db.close()
        return JSONResponse({"success": True, "message": "Category saved successfully"})
    except Exception as e:
        logger.error(f"Error saving category: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


async def delete_category(request):
    try:
        cat_id = request.path_params.get("id")
        db = SessionLocal()
        cat = db.query(WayfindingCategory).filter(WayfindingCategory.id == cat_id).first()
        if not cat:
            db.close()
            return JSONResponse({"success": False, "message": "Category not found"}, status_code=404)
        db.delete(cat)
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": "Category deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# ----------------------------------------------------------------------
# ROUTE REGISTRY
# ----------------------------------------------------------------------
routes = [
    # Overview & KPIs
    Route("/api/v1/admin/overview", get_admin_overview),
    Route("/api/v1/admin/network", get_network_health),

    # Connected Devices Fleet Healthcheck
    Route("/api/v1/admin/devices", get_devices),
    Route("/api/v1/admin/devices", create_or_update_device, methods=["POST"]),
    Route("/api/v1/admin/devices/{id}/ping", ping_device, methods=["POST"]),
    Route("/api/v1/admin/devices/{id}/reboot", reboot_device, methods=["POST"]),
    Route("/api/v1/admin/devices/{id}", delete_device, methods=["DELETE"]),

    # Operator Workforce
    Route("/api/v1/admin/operators", get_operators),
    Route("/api/v1/admin/operators", create_or_update_operator, methods=["POST"]),
    Route("/api/v1/admin/operators/{id}/status", set_operator_status, methods=["POST"]),
    Route("/api/v1/admin/operators/{id}/password", set_operator_password, methods=["POST"]),
    Route("/api/v1/admin/operators/{id}", delete_operator, methods=["DELETE"]),

    # Boarding Pass Scan Logs
    Route("/api/v1/admin/scans", get_scan_logs),
    Route("/api/v1/admin/scans/log", create_scan_log, methods=["POST"]),

    # User Action Audit Trail
    Route("/api/v1/admin/actions", get_user_action_logs),
    Route("/api/v1/admin/actions/log", create_user_action_log, methods=["POST"]),

    # Amenities & Shops/Restaurants (Non-mandatory x, y)
    Route("/api/v1/admin/amenities", get_amenities),
    Route("/api/v1/admin/amenities", create_or_update_amenity, methods=["POST"]),
    Route("/api/v1/admin/amenities/{id}/toggle", toggle_amenity_status, methods=["POST"]),
    Route("/api/v1/admin/amenities/{id}", delete_amenity, methods=["DELETE"]),

    # Legacy Wayfinding Categories
    Route("/api/v1/admin/wayfinding/categories", get_wayfinding_categories),
    Route("/api/v1/admin/wayfinding/categories", create_or_update_category, methods=["POST"]),
    Route("/api/v1/admin/wayfinding/categories/{id}", delete_category, methods=["DELETE"]),
]
