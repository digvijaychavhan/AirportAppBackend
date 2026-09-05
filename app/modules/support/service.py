"""
WebRTC Signaling & Support Call Real-Time State Service
Manages Socket.IO real-time events, WebRTC SDP exchanges, ICE candidates,
Support Queue matching, and Remote Screen Annotation stroke streaming.
"""

import os
import socketio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.logging import logger
from app.core.config import settings
from app.core.timezone import get_current_time, get_current_iso

# Initialize Socket.IO Async Server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=10,
    ping_interval=5,
    max_http_buffer_size=10_000_000,
    logger=False,
    engineio_logger=False
)

# In-memory state
active_calls: Dict[str, Dict[str, Any]] = {}
connected_clients: Dict[str, Dict[str, Any]] = {}
call_queue: List[Dict[str, Any]] = []
online_operators: Dict[str, Dict[str, Any]] = {}
online_kiosks: Dict[str, Dict[str, Any]] = {}
active_kiosk_claims: Dict[str, Dict[str, Any]] = {}


async def cleanup_ghost_connections(timeout_seconds: int = 120) -> Dict[str, int]:
    """
    Audits active sockets, operators, kiosks, and queues to eliminate stale/ghost connections.
    """
    global call_queue
    now_ts = get_current_time().timestamp()
    cleaned_ops = 0
    cleaned_kiosks = 0
    cleaned_calls = 0

    # 1. Audit operators with dead sockets or stale state
    for op_id, op_data in list(online_operators.items()):
        sid = op_data.get("sid")
        if sid and sid not in connected_clients:
            op_data["sid"] = None
            op_data["status"] = "OFFLINE"
            cleaned_ops += 1

    # 2. Audit kiosks with timed out heartbeats
    for kiosk_id, kiosk_data in list(online_kiosks.items()):
        last_seen = kiosk_data.get("lastSeen", 0)
        sid = kiosk_data.get("sid")
        if (sid and sid not in connected_clients) or (now_ts - last_seen > timeout_seconds):
            online_kiosks.pop(kiosk_id, None)
            cleaned_kiosks += 1

    # 3. Clean stale calls waiting in queue whose kiosk disconnected
    active_kiosk_sids = set(connected_clients.keys())
    valid_calls = []
    for call in call_queue:
        ksid = call.get("kioskSid")
        if ksid and ksid not in active_kiosk_sids and call.get("status") == "QUEUED":
            cid = call.get("callId")
            if cid in active_calls and active_calls[cid].get("status") == "QUEUED":
                active_calls.pop(cid, None)
            cleaned_calls += 1
        else:
            valid_calls.append(call)
    call_queue = valid_calls

    if cleaned_ops > 0 or cleaned_kiosks > 0 or cleaned_calls > 0:
        await broadcast_admin_telemetry()

    return {
        "cleaned_operators": cleaned_ops,
        "cleaned_kiosks": cleaned_kiosks,
        "cleaned_calls": cleaned_calls
    }


def get_recordings_dir() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    rec_dir = os.path.join(base_dir, "recordings")
    os.makedirs(rec_dir, exist_ok=True)
    return rec_dir

def get_operator_info(operator_id: str) -> Dict[str, str]:
    if not operator_id:
        return {"id": "op_101", "name": "Priya Sharma", "role": "Customer Support Executive"}

    if operator_id in online_operators and online_operators[operator_id].get("name"):
        return {
            "id": operator_id,
            "name": online_operators[operator_id]["name"],
            "role": online_operators[operator_id].get("roleName", "Customer Support Executive")
        }

    try:
        from app.core.database import SessionLocal
        import app.db.models as models
        db = SessionLocal()
        try:
            op = db.query(models.Operator).filter(
                (models.Operator.id == operator_id) |
                (models.Operator.username == operator_id) |
                (models.Operator.employee_code == operator_id) |
                (models.Operator.name == operator_id)
            ).first()
            if op:
                role_title = op.role.replace("_", " ").title() if op.role else "Customer Support Executive"
                return {"id": op.id, "name": op.name, "role": role_title}
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error getting operator info: {e}")
    return {"id": operator_id, "name": operator_id, "role": "Customer Support Executive"}



def get_longest_idle_available_operator(exclude_op_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    available_ops = [
        op for op in online_operators.values()
        if op.get("status") == "AVAILABLE" and op.get("sid") and op.get("operatorId") != exclude_op_id
    ]
    if not available_ops:
        return None
    available_ops.sort(key=lambda x: x.get("availableSince", 0))
    return available_ops[0]


async def dispatch_call_to_operator(call_data: Dict[str, Any], target_op: Dict[str, Any]):
    if not target_op or target_op.get("status") != "AVAILABLE":
        logger.info(f"Target operator {target_op.get('operatorId')} is not AVAILABLE")
        return

    call_id = call_data["callId"]
    ring_start = call_data.get("ringStartTime") or get_current_iso()
    call_data["ringStartTime"] = ring_start
    call_data["allocatedOperatorId"] = target_op["operatorId"]

    payload = {
        "callId": call_id,
        "kioskId": call_data.get("kioskId"),
        "passengerName": call_data.get("passengerName") or "",
        "flightNumber": call_data.get("flightNumber") or "",
        "pnr": call_data.get("pnr") or "",
        "ringStartTime": ring_start,
        "allocatedTo": target_op["operatorId"],
        "adaPriority": call_data.get("adaPriority", False)
    }

    logger.info(f"Allocating call {call_id} to available operator {target_op['operatorId']} (SID: {target_op.get('sid')})")
    if target_op.get("sid"):
        await sio.emit("INCOMING_CALL_RINGING", payload, room=target_op["sid"])


async def check_and_dispatch_queued_calls():
    for call in call_queue:
        if call.get("status") == "QUEUED" and not call.get("allocatedOperatorId"):
            idle_op = get_longest_idle_available_operator()
            if idle_op:
                await dispatch_call_to_operator(call, idle_op)
                break


async def broadcast_admin_telemetry():
    try:
        available_count = len([op for op in online_operators.values() if (op.get("status") or "").upper() == "AVAILABLE"])
        busy_count = len([op for op in online_operators.values() if (op.get("status") or "").upper() in ["BUSY", "IN_CALL", "IN CALL"]])
        active_kiosks_count = len([k for k in online_kiosks.values() if k.get("sid") in connected_clients or k.get("sid")])
        payload = {
            "operators": {
                "online": available_count + busy_count,
                "available": available_count,
                "inCall": busy_count,
                "total": len(online_operators)
            },
            "kiosks": {
                "active": active_kiosks_count,
                "online": active_kiosks_count,
                "total": max(5, active_kiosks_count)
            },
            "online": available_count + busy_count,
            "available": available_count,
            "inCall": busy_count,
            "activeKiosks": active_kiosks_count
        }
        await sio.emit("ADMIN_TELEMETRY_UPDATE", payload)
        await sio.emit("ADMIN_TELEMETRY_UPDATED", payload)
        await sio.emit("OPERATORS_UPDATED", payload)
        await sio.emit("KIOSKS_UPDATED", payload)
    except Exception as e:
        logger.error(f"Error broadcasting admin telemetry: {e}")


def auto_save_support_call(call_id: str, session: Optional[Dict[str, Any]], duration_seconds: int):
    if not call_id:
        return
    try:
        from app.core.database import SessionLocal
        import app.db.models as models
        db = SessionLocal()
        try:
            recordings_dir = get_recordings_dir()
            rec_url = (session or {}).get("recordingUrl")
            if not rec_url:
                if os.path.exists(os.path.join(recordings_dir, f"{call_id}.webm")):
                    rec_url = f"/recordings/{call_id}.webm"
                elif os.path.exists(os.path.join(recordings_dir, f"{call_id}.mp4")):
                    rec_url = f"/recordings/{call_id}.mp4"

            existing = db.query(models.SupportCall).filter(models.SupportCall.id == call_id).first()
            kiosk_id = (session or {}).get("kioskId", "T3-L1-K04")
            kiosk_obj = db.query(models.Kiosk).filter((models.Kiosk.id == kiosk_id) | (models.Kiosk.code == kiosk_id)).first()
            kiosk_db_id = kiosk_obj.id if kiosk_obj else "T3-L1-K04"

            raw_op_id = (session or {}).get("operatorId")
            op_id = None
            if raw_op_id:
                op_match = db.query(models.Operator).filter(
                    (models.Operator.id == raw_op_id) | (models.Operator.username == raw_op_id) | (models.Operator.employee_code == raw_op_id)
                ).first()
                op_id = op_match.id if op_match else raw_op_id

            passenger_name = (session or {}).get("passengerName") or ""
            flight_number = (session or {}).get("flightNumber") or ""
            pnr = (session or {}).get("pnr") or ""

            if existing:
                existing.call_duration_seconds = max(1, duration_seconds) if duration_seconds > 0 else existing.call_duration_seconds
                existing.status = "ended"
                if op_id:
                    existing.operator_id = op_id
                if passenger_name:
                    existing.passenger_name = passenger_name
                if flight_number:
                    existing.flight_number = flight_number
                if rec_url and not existing.recording_url:
                    existing.recording_url = rec_url

                db.commit()
                logger.info(f"Auto-save updated support call {call_id}")
            else:
                new_call = models.SupportCall(
                    id=call_id,
                    kiosk_id=kiosk_db_id,
                    operator_id=op_id,
                    status="ended",
                    call_duration_seconds=max(1, duration_seconds),
                    issue_category="General Inquiry",
                    operator_notes="Assisted passenger at kiosk.",
                    passenger_name=passenger_name,
                    flight_number=flight_number,
                    pnr=pnr,
                    recording_url=rec_url
                )
                db.add(new_call)
                db.commit()
                logger.info(f"Auto-saved new support call record {call_id}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error auto-saving support call {call_id}: {e}")


# --- Socket.IO Event Handlers ---

@sio.event
async def connect(sid: str, environ: Dict[str, Any]):
    logger.info(f"Socket.IO client connected: {sid} (Transport: {environ.get('HTTP_UPGRADE', 'polling')})")
    await sio.emit("CONNECTED_ACK", {"sid": sid, "timestamp": get_current_iso()}, room=sid)


@sio.event
async def disconnect(sid: str):
    global call_queue
    logger.info(f"Socket disconnected: {sid}")
    client_info = connected_clients.pop(sid, None)
    if client_info:
        client_id = client_info.get("clientId")
        role = client_info.get("role")

        if role == "operator":
            if client_id and client_id in online_operators:
                online_operators[client_id]["sid"] = None
            for k, op_data in online_operators.items():
                if op_data.get("sid") == sid:
                    op_data["sid"] = None
            await broadcast_admin_telemetry()

        if role == "kiosk":
            for kid, kdata in list(online_kiosks.items()):
                if kdata.get("sid") == sid:
                    online_kiosks.pop(kid, None)
                    active_kiosk_claims.pop(kid, None)
            await broadcast_admin_telemetry()

        # Only cancel from queue if call is still waiting in QUEUED state (passenger disconnected before answer)
        removed_calls = [c for c in call_queue if (c.get("kioskSid") == sid or (client_id and c.get("kioskId") == client_id)) and c.get("status") == "QUEUED"]
        call_queue = [c for c in call_queue if c not in removed_calls]
        for c in removed_calls:
            cid = c.get("callId")
            if cid in active_calls and active_calls[cid].get("status") == "QUEUED":
                active_calls.pop(cid, None)
            await sio.emit("SUPPORT_CALL_CANCELLED", {"callId": cid, "kioskId": c.get("kioskId")}, room="operators")
            await sio.emit("INCOMING_CALL_DISMISSED", {"callId": cid}, room="operators")

        # For in-progress calls, clear the disconnected sid without destroying the call session
        call_id = client_info.get("active_call_id")
        if call_id and call_id in active_calls:
            session = active_calls[call_id]
            if session.get("operatorSid") == sid:
                session["operatorSid"] = None
            if session.get("kioskSid") == sid:
                session["kioskSid"] = None


@sio.event
async def CANCEL_CALL_REQUEST(sid: str, data: Dict[str, Any]):
    global call_queue
    call_id = data.get("callId")
    kiosk_id = data.get("kioskId")

    removed_calls = []
    new_queue = []
    for c in call_queue:
        if (call_id and c.get("callId") == call_id) or (kiosk_id and c.get("kioskId") == kiosk_id) or c.get("kioskSid") == sid:
            removed_calls.append(c)
        else:
            new_queue.append(c)
    call_queue = new_queue

    for c in removed_calls:
        cid = c.get("callId")
        if cid in active_calls:
            active_calls.pop(cid, None)
        await sio.emit("SUPPORT_CALL_CANCELLED", {"callId": cid, "kioskId": c.get("kioskId")}, room="operators")
        await sio.emit("INCOMING_CALL_DISMISSED", {"callId": cid}, room="operators")

    await sio.emit("CALL_CANCELLED_ACK", {"status": "CANCELLED"}, room=sid)


@sio.event
async def REGISTER_CLIENT(sid: str, data: Dict[str, Any]):
    role = data.get("role", "kiosk")
    client_id = data.get("clientId", sid)
    existing_call_id = connected_clients.get(sid, {}).get("active_call_id")

    connected_clients[sid] = {
        "sid": sid,
        "role": role,
        "clientId": client_id,
        "active_call_id": existing_call_id
    }

    if role == "operator":
        await sio.enter_room(sid, "operators")
        status = data.get("status")
        name = data.get("name")
        role_name = data.get("roleName")

        if not name or not role_name:
            op_db_info = get_operator_info(client_id)
            name = name or op_db_info.get("name", client_id)
            role_name = role_name or op_db_info.get("role", "Customer Support Executive")

        req_status = status.upper() if (status and status not in ["PRESERVE", "preserve"]) else None

        if client_id in online_operators:
            online_operators[client_id]["sid"] = sid
            online_operators[client_id]["name"] = name
            online_operators[client_id]["roleName"] = role_name
            if req_status:
                online_operators[client_id]["status"] = req_status
            elif online_operators[client_id].get("status") == "OFFLINE":
                online_operators[client_id]["status"] = "AVAILABLE"
                online_operators[client_id]["availableSince"] = get_current_time().timestamp()
        else:
            online_operators[client_id] = {
                "operatorId": client_id,
                "sid": sid,
                "name": name,
                "roleName": role_name,
                "status": req_status or "AVAILABLE",
                "availableSince": get_current_time().timestamp(),
                "currentCallId": None
            }

        await sio.emit("OPERATOR_STATE_SYNC", online_operators[client_id], room=sid)
        await check_and_dispatch_queued_calls()
        await broadcast_admin_telemetry()

    if role == "kiosk":
        kiosk_id = client_id or f"KIOSK-{sid[:6]}"
        page_name = data.get("page", "/")
        runtime_env = data.get("runtimeEnv") or "browser"
        session_id = data.get("clientSessionId")
        online_kiosks[kiosk_id] = {
            "kioskId": kiosk_id,
            "sid": sid,
            "sessionId": session_id,
            "page": page_name,
            "runtimeEnv": runtime_env,
            "lastSeen": get_current_time().timestamp(),
            "status": "online"
        }
        active_kiosk_claims[kiosk_id] = {
            "sessionId": session_id,
            "runtimeEnv": runtime_env,
            "lastSeen": get_current_time().timestamp(),
            "kioskId": kiosk_id,
            "sid": sid
        }
        connected_clients[sid]["kioskId"] = kiosk_id

        # Persist runtime_env to database
        try:
            from app.core.database import SessionLocal
            import app.db.models as models
            db = SessionLocal()
            try:
                dev = db.query(models.Device).filter(
                    (models.Device.device_id == kiosk_id) | (models.Device.id == kiosk_id)
                ).first()
                if dev:
                    dev.status = "online"
                    dev.runtime_env = runtime_env
                    dev.last_heartbeat = get_current_time()
                    db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error updating device status on REGISTER_CLIENT: {e}")

        await broadcast_admin_telemetry()

    await sio.emit("REGISTERED_ACK", {"status": "REGISTERED", "role": role, "clientId": client_id}, room=sid)


@sio.event
async def KIOSK_HEARTBEAT(sid: str, data: Dict[str, Any]):
    kiosk_id = data.get("clientId") or data.get("kioskId")
    page_name = data.get("page", "/")
    session_id = data.get("clientSessionId")
    if kiosk_id:
        online_kiosks[kiosk_id] = {
            "kioskId": kiosk_id,
            "sid": sid,
            "sessionId": session_id,
            "page": page_name,
            "lastSeen": get_current_time().timestamp(),
            "status": "online"
        }
        if kiosk_id in active_kiosk_claims:
            active_kiosk_claims[kiosk_id]["lastSeen"] = get_current_time().timestamp()
            if session_id:
                active_kiosk_claims[kiosk_id]["sessionId"] = session_id
        # Update DB device telemetry if present
        try:
            from app.core.database import SessionLocal
            import app.db.models as models
            db = SessionLocal()
            try:
                dev = db.query(models.Device).filter(
                    (models.Device.device_id == kiosk_id) | (models.Device.id == kiosk_id)
                ).first()
                if dev:
                    dev.runtime_env = data.get("runtimeEnv") or ("electron" if data.get("cpuPct") is not None else "browser")
                    if "cpuPct" in data:
                        dev.cpu_pct = data.get("cpuPct")
                    if "ramUsedMb" in data:
                        dev.ram_used_mb = data.get("ramUsedMb")
                    if "ramTotalMb" in data:
                        dev.ram_total_mb = data.get("ramTotalMb")
                    if "ramPct" in data:
                        dev.ram_pct = data.get("ramPct")
                    if "networkBandwidthMbps" in data:
                        dev.network_bandwidth_mbps = data.get("networkBandwidthMbps")
                    if "scannerConnected" in data:
                        dev.scanner_connected = data.get("scannerConnected")
                    if "scannerWorking" in data:
                        dev.scanner_working = data.get("scannerWorking")
                        dev.scanner_status = data.get("scannerWorking")
                    if "cameraConnected" in data:
                        dev.camera_connected = data.get("cameraConnected")
                    if "cameraWorking" in data:
                        dev.camera_working = data.get("cameraWorking")
                        dev.camera_status = data.get("cameraWorking")
                    if "pingMs" in data and data.get("pingMs") is not None:
                        dev.ping_ms = data.get("pingMs")
                    dev.status = "online"
                    dev.last_heartbeat = get_current_time()
                    db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error saving KIOSK_HEARTBEAT to db: {e}")

        await broadcast_admin_telemetry()


@sio.event
async def UNREGISTER_KIOSK(sid: str, data: Dict[str, Any]):
    kiosk_id = data.get("clientId") or data.get("kioskId")
    session_id = data.get("clientSessionId")
    for kid, kdata in list(online_kiosks.items()):
        if kid == kiosk_id or kdata.get("sid") == sid:
            online_kiosks.pop(kid, None)
    if kiosk_id:
        curr = active_kiosk_claims.get(kiosk_id)
        if not session_id or (curr and curr.get("sessionId") == session_id):
            active_kiosk_claims.pop(kiosk_id, None)
    await broadcast_admin_telemetry()


@sio.event
async def OPERATOR_STATUS_UPDATE(sid: str, data: Dict[str, Any]):
    client_info = connected_clients.get(sid, {})
    raw_op_id = data.get("operatorId") or client_info.get("clientId") or "op_101"
    status = (data.get("status") or "AVAILABLE").upper()

    target_keys = []
    for k, v in list(online_operators.items()):
        if k == raw_op_id or v.get("operatorId") == raw_op_id or v.get("sid") == sid:
            target_keys.append(k)

    if not target_keys:
        op_db_info = get_operator_info(raw_op_id)
        resolved_id = op_db_info.get("id", raw_op_id)
        online_operators[resolved_id] = {
            "operatorId": resolved_id,
            "sid": sid,
            "name": op_db_info.get("name", raw_op_id),
            "roleName": op_db_info.get("role", "Customer Support Executive"),
            "status": status,
            "availableSince": get_current_time().timestamp(),
            "currentCallId": None
        }
        target_keys = [resolved_id]

    for k in target_keys:
        online_operators[k]["status"] = status
        online_operators[k]["sid"] = sid
        if status == "AVAILABLE":
            online_operators[k]["availableSince"] = get_current_time().timestamp()

    # Sync to DB
    try:
        from app.core.database import SessionLocal
        import app.db.models as models
        db = SessionLocal()
        try:
            for k in target_keys:
                op_row = db.query(models.Operator).filter(
                    (models.Operator.id == k) | (models.Operator.username == k) | (models.Operator.employee_code == k)
                ).first()
                if op_row:
                    op_row.status = status.lower()
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error syncing operator status: {e}")


    if status == "AVAILABLE":
        await check_and_dispatch_queued_calls()
    else:
        for call in call_queue:
            if call.get("allocatedOperatorId") in target_keys and call.get("status") == "QUEUED":
                call["allocatedOperatorId"] = None
                await sio.emit("INCOMING_CALL_DISMISSED", {"callId": call.get("callId")}, room=sid)
        await check_and_dispatch_queued_calls()

    if target_keys:
        await sio.emit("OPERATOR_STATE_SYNC", online_operators[target_keys[0]], room=sid)

    await broadcast_admin_telemetry()


@sio.event
async def CALL_REQUEST(sid: str, data: Dict[str, Any]):
    global call_queue
    import uuid
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    kiosk_id = data.get("kioskId", "Kiosk-01")
    ada_priority = data.get("adaPriority", False)
    language = data.get("language", "EN")
    passenger_name = data.get("passengerName") or ""
    flight_number = data.get("flightNumber") or ""
    pnr = data.get("pnr") or ""
    ring_start_time = get_current_iso()

    call_queue = [c for c in call_queue if c.get("kioskId") != kiosk_id]

    call_data = {
        "callId": call_id,
        "kioskId": kiosk_id,
        "kioskSid": sid,
        "operatorId": None,
        "operatorSid": None,
        "allocatedOperatorId": None,
        "adaPriority": ada_priority,
        "language": language,
        "status": "QUEUED",
        "passengerName": passenger_name,
        "flightNumber": flight_number,
        "pnr": pnr,
        "enqueueTime": ring_start_time,
        "ringStartTime": ring_start_time
    }

    active_calls[call_id] = call_data
    if sid in connected_clients:
        connected_clients[sid]["active_call_id"] = call_id

    if ada_priority:
        call_queue.insert(0, call_data)
    else:
        call_queue.append(call_data)

    logger.info(f"New call enqueued: {call_id} from {kiosk_id}")
    await sio.emit("CALL_ENQUEUED_ACK", {"callId": call_id, "queuePosition": len(call_queue), "ringStartTime": ring_start_time}, room=sid)
    await sio.emit("SUPPORT_CALL_ENQUEUED", call_data, room="operators")

    idle_op = get_longest_idle_available_operator()
    if idle_op:
        await dispatch_call_to_operator(call_data, idle_op)


@sio.on("REQUEST_CALL")
async def REQUEST_CALL(sid: str, data: Dict[str, Any]):
    await CALL_REQUEST(sid, data)


@sio.on("REGISTER_OPERATOR")
async def REGISTER_OPERATOR(sid: str, data: Dict[str, Any]):
    payload = {**data, "role": "operator", "clientId": data.get("operatorId", sid)}
    await REGISTER_CLIENT(sid, payload)


@sio.event
async def OPERATOR_DECLINE_CALL(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    operator_id = data.get("operatorId")
    await sio.emit("INCOMING_CALL_DISMISSED", {"callId": call_id}, room=sid)

    if call_id and call_id in active_calls:
        call = active_calls[call_id]
        if call.get("status") == "QUEUED":
            next_op = get_longest_idle_available_operator(exclude_op_id=operator_id)
            if next_op:
                await dispatch_call_to_operator(call, next_op)
            else:
                call["allocatedOperatorId"] = None


@sio.event
async def OPERATOR_ACCEPT_CALL(sid: str, data: Dict[str, Any]):
    global call_queue
    call_id = data.get("callId")
    operator_id = data.get("operatorId", "op_101")

    if not call_id or call_id not in active_calls:
        await sio.emit("ERROR", {"message": "Call session not found"}, room=sid)
        return

    call_session = active_calls[call_id]
    if call_session["status"] != "QUEUED":
        await sio.emit("ERROR", {"message": "Call is no longer in queue"}, room=sid)
        return

    op_info = get_operator_info(operator_id)
    op_name = op_info.get("name", "Priya Sharma")
    op_role = op_info.get("role", "Customer Support Executive")

    call_session["status"] = "IN_PROGRESS"
    call_session["operatorId"] = operator_id
    call_session["operatorName"] = op_name
    call_session["operatorRole"] = op_role
    call_session["operatorSid"] = sid
    call_session["startTime"] = get_current_iso()

    if operator_id in online_operators:
        online_operators[operator_id]["status"] = "BUSY"
        online_operators[operator_id]["currentCallId"] = call_id
        await sio.emit("OPERATOR_STATE_SYNC", online_operators[operator_id], room=sid)

    if sid in connected_clients:
        connected_clients[sid]["active_call_id"] = call_id

    call_queue = [c for c in call_queue if c["callId"] != call_id]
    kiosk_sid = call_session.get("kioskSid")

    room_name = f"call_{call_id}"
    await sio.enter_room(sid, room_name)
    if kiosk_sid:
        await sio.enter_room(kiosk_sid, room_name)

    claimed_payload = {
        "callId": call_id,
        "operatorId": operator_id,
        "operatorName": op_name,
        "kioskId": call_session.get("kioskId", "T3-L1-K04")
    }
    await sio.emit("SUPPORT_CALL_CLAIMED", claimed_payload, room="operators")
    await sio.emit("CALL_CLAIMED", claimed_payload, room="operators")
    await sio.emit("INCOMING_CALL_DISMISSED", {"callId": call_id}, room="operators")
    await broadcast_admin_telemetry()

    accept_payload = {
        "callId": call_id,
        "operatorId": operator_id,
        "operatorName": op_name,
        "operatorRole": op_role,
        "kioskId": call_session.get("kioskId", "T3-L1-K04"),
        "status": "ACCEPTED"
    }
    await sio.emit("CALL_ACCEPTED", accept_payload, room=room_name)



@sio.event
async def JOIN_CALL_ROOM(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    role = data.get("role", "kiosk")
    if call_id:
        room_name = f"call_{call_id}"
        await sio.enter_room(sid, room_name)

        if role == "operator":
            if call_id in active_calls:
                active_calls[call_id]["operatorSid"] = sid
                active_calls[call_id]["status"] = "IN_PROGRESS"
                if data.get("kioskId"):
                    active_calls[call_id]["kioskId"] = data.get("kioskId")
            else:
                active_calls[call_id] = {
                    "callId": call_id,
                    "kioskId": data.get("kioskId") or data.get("clientId") or "Kiosk",
                    "operatorSid": sid,
                    "operatorId": data.get("operatorId") or "Operator",
                    "status": "IN_PROGRESS",
                    "startTime": get_current_iso()
                }

        if role == "kiosk" and call_id in active_calls:
            active_calls[call_id]["kioskSid"] = sid
            session = active_calls[call_id]
            op_id = session.get("operatorId")
            op_info = get_operator_info(op_id) if op_id else {}
            op_name = session.get("operatorName") or op_info.get("name", "Operator")
            op_role = session.get("operatorRole") or op_info.get("role", "Customer Support Executive")
            await sio.emit("CALL_INFO", {
                "callId": call_id,
                "operatorId": op_id,
                "operatorName": op_name,
                "operatorRole": op_role,
                "status": session.get("status", "IN_PROGRESS"),
                "startTime": session.get("startTime")
            }, room=sid)

        if sid in connected_clients:
            connected_clients[sid]["active_call_id"] = call_id


@sio.event
async def OPERATOR_READY(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    operator_id = data.get("operatorId")
    if not operator_id and call_id in active_calls:
        operator_id = active_calls[call_id].get("operatorId")

    if call_id:
        if call_id in active_calls:
            active_calls[call_id]["operatorSid"] = sid
            active_calls[call_id]["status"] = "IN_PROGRESS"
            if data.get("kioskId"):
                active_calls[call_id]["kioskId"] = data.get("kioskId")
        else:
            active_calls[call_id] = {
                "callId": call_id,
                "kioskId": data.get("kioskId") or data.get("clientId") or "Kiosk",
                "operatorSid": sid,
                "operatorId": operator_id or "Operator",
                "status": "IN_PROGRESS",
                "startTime": get_current_iso()
            }

    op_info = get_operator_info(operator_id) if operator_id else {}
    op_name = op_info.get("name") or (active_calls.get(call_id, {}).get("operatorName", "Priya Sharma"))
    op_role = op_info.get("role") or (active_calls.get(call_id, {}).get("operatorRole", "Customer Support Executive"))

    room_name = f"call_{call_id}"
    await sio.emit("OPERATOR_READY", {
        "callId": call_id,
        "operatorId": operator_id,
        "operatorName": op_name,
        "operatorRole": op_role
    }, room=room_name)


@sio.event
async def WEBRTC_OFFER(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    sdp = data.get("sdp")
    room_name = f"call_{call_id}"
    await sio.emit("WEBRTC_OFFER", {"callId": call_id, "sdp": sdp}, room=room_name, skip_sid=sid)


@sio.event
async def WEBRTC_ANSWER(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    sdp = data.get("sdp")
    room_name = f"call_{call_id}"
    await sio.emit("WEBRTC_ANSWER", {"callId": call_id, "sdp": sdp}, room=room_name, skip_sid=sid)


@sio.event
async def ICE_CANDIDATE(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    candidate = data.get("candidate")
    room_name = f"call_{call_id}"
    await sio.emit("ICE_CANDIDATE", {"callId": call_id, "candidate": candidate}, room=room_name, skip_sid=sid)


@sio.event
async def END_CALL(sid: str, data: Dict[str, Any]):
    global call_queue
    call_id = data.get("callId")
    reason = data.get("reason", "USER_ENDED")
    room_name = f"call_{call_id}"

    call_queue = [c for c in call_queue if c["callId"] != call_id]

    op_id = None
    op_name = None
    duration_seconds = 0
    session = None
    if call_id and call_id in active_calls:
        session = active_calls.pop(call_id, None)
        if session:
            op_id = session.get("operatorId")
            op_name = session.get("operatorName")
            start_time_str = session.get("startTime")
            if start_time_str:
                try:
                    start_dt = datetime.fromisoformat(start_time_str)
                    duration_seconds = max(1, int((get_current_time() - start_dt).total_seconds()))
                except Exception:
                    pass

    if call_id:
        auto_save_support_call(call_id, session, duration_seconds)

    if op_id and op_id in online_operators:
        if online_operators[op_id].get("status") != "OFFLINE":
            online_operators[op_id]["status"] = "AVAILABLE"
            online_operators[op_id]["availableSince"] = get_current_time().timestamp()
            online_operators[op_id]["currentCallId"] = None
            await sio.emit("OPERATOR_STATE_SYNC", online_operators[op_id], room=online_operators[op_id].get("sid", ""))
            await check_and_dispatch_queued_calls()

    await sio.emit("CALL_ENDED", {
        "callId": call_id,
        "reason": reason,
        "operatorName": op_name,
        "durationSeconds": duration_seconds
    }, room=room_name)


@sio.event
async def MEDIA_STATE_CHANGED(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    if call_id:
        room_name = f"call_{call_id}"
        await sio.emit("MEDIA_STATE_CHANGED", data, room=room_name, skip_sid=sid)


@sio.event
async def SCREEN_ANNOTATION_STROKE(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    room_name = f"call_{call_id}"
    await sio.emit("SCREEN_ANNOTATION_STROKE", data, room=room_name, skip_sid=sid)


# --- Live Remote Screen Control & Input Streaming Events ---

@sio.event
async def REMOTE_CONTROL_REQUEST(sid: str, data: Dict[str, Any]):
    """Operator requests or triggers remote screen control on caller's kiosk.
    NOTE: Part of Remote Control Module — do not modify without testing remote access flow."""
    call_id = data.get("callId")
    operator_id = data.get("operatorId")
    operator_name = data.get("operatorName", "Operator")
    if call_id:
        room_name = f"call_{call_id}"
        if call_id in active_calls:
            active_calls[call_id]["remoteControlActive"] = True
            active_calls[call_id]["remoteControlOperator"] = operator_name
        logger.info(f"[RemoteControl] Request initiated for call {call_id} by {operator_name}")
        await sio.emit("REMOTE_CONTROL_START", {
            "callId": call_id,
            "operatorId": operator_id,
            "operatorName": operator_name,
            "timestamp": get_current_iso()
        }, room=room_name, skip_sid=sid)


@sio.event
async def REMOTE_CONTROL_STOP(sid: str, data: Dict[str, Any]):
    """Operator or Kiosk stops / pauses remote screen control.
    NOTE: Part of Remote Control Module — do not modify without testing remote access flow."""
    call_id = data.get("callId")
    stopped_by = data.get("stoppedBy", "operator")
    if call_id:
        room_name = f"call_{call_id}"
        if call_id in active_calls:
            active_calls[call_id]["remoteControlActive"] = False
        logger.info(f"[RemoteControl] Stopped for call {call_id} by {stopped_by}")
        await sio.emit("REMOTE_CONTROL_STOPPED", {
            "callId": call_id,
            "stoppedBy": stopped_by,
            "timestamp": get_current_iso()
        }, room=room_name, skip_sid=sid)


@sio.event
async def REMOTE_CONTROL_EVENT(sid: str, data: Dict[str, Any]):
    """Relays real-time mouse movements, clicks, keys, typing, and scroll events.
    NOTE: Part of Remote Control Module — do not modify without testing remote access flow."""
    call_id = data.get("callId")
    if call_id:
        room_name = f"call_{call_id}"
        await sio.emit("REMOTE_CONTROL_EVENT", data, room=room_name, skip_sid=sid)


@sio.event
async def REMOTE_SCREEN_OFFER(sid: str, data: Dict[str, Any]):
    """WebRTC offer for dedicated HD screen stream.
    NOTE: Part of Remote Control Module — do not modify without testing remote access flow."""
    call_id = data.get("callId")
    sdp = data.get("sdp")
    if call_id:
        room_name = f"call_{call_id}"
        await sio.emit("REMOTE_SCREEN_OFFER", {"callId": call_id, "sdp": sdp}, room=room_name, skip_sid=sid)


@sio.event
async def REMOTE_SCREEN_ANSWER(sid: str, data: Dict[str, Any]):
    """WebRTC answer for dedicated HD screen stream.
    NOTE: Part of Remote Control Module — do not modify without testing remote access flow."""
    call_id = data.get("callId")
    sdp = data.get("sdp")
    if call_id:
        room_name = f"call_{call_id}"
        await sio.emit("REMOTE_SCREEN_ANSWER", {"callId": call_id, "sdp": sdp}, room=room_name, skip_sid=sid)


@sio.event
async def REMOTE_SCREEN_ICE(sid: str, data: Dict[str, Any]):
    """ICE candidate for dedicated HD screen stream.
    NOTE: Part of Remote Control Module — do not modify without testing remote access flow."""
    call_id = data.get("callId")
    candidate = data.get("candidate")
    if call_id:
        room_name = f"call_{call_id}"
        await sio.emit("REMOTE_SCREEN_ICE", {"callId": call_id, "candidate": candidate}, room=room_name, skip_sid=sid)

