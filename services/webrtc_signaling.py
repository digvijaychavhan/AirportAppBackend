"""
WebRTC Signaling & Support Call Queue Service
Manages Socket.IO real-time events, WebRTC SDP exchanges, ICE candidates,
Support Queue matching, and Remote Screen Annotation stroke streaming.
"""

import socketio
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("webrtc_signaling")

# Initialize Socket.IO Async Server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=False
)

# In-memory call queues and active session states
# call_id -> Call Session metadata
active_calls: Dict[str, Dict[str, Any]] = {}
# socket_id -> user metadata (role: 'kiosk' | 'operator', id: str)
connected_clients: Dict[str, Dict[str, Any]] = {}
# Waiting queue list of call_ids
call_queue: List[Dict[str, Any]] = []
# Operator availability pool: operator_id -> { operatorId, sid, name, roleName, status: 'AVAILABLE'|'BUSY'|'OFFLINE', availableSince: float, currentCallId: str }
online_operators: Dict[str, Dict[str, Any]] = {}


def get_operator_info(operator_id: str) -> Dict[str, str]:
    """
    Resolves operator id, name and role from memory pool or sqlite database.
    """
    if not operator_id:
        return {"id": "op_101", "name": "Priya Sharma", "role": "Customer Support Executive"}
        
    if operator_id in online_operators and online_operators[operator_id].get("name"):
        return {
            "id": operator_id,
            "name": online_operators[operator_id]["name"],
            "role": online_operators[operator_id].get("roleName", "Customer Support Executive")
        }
    try:
        from database import SessionLocal
        from models import Operator
        db = SessionLocal()
        op = db.query(Operator).filter(
            (Operator.id == operator_id) |
            (Operator.username == operator_id) |
            (Operator.employee_code == operator_id) |
            (Operator.name == operator_id)
        ).first()
        if op:
            role_title = op.role.replace("_", " ").title() if op.role else "Customer Support Executive"
            info = {"id": op.id, "name": op.name, "role": role_title}
            db.close()
            return info
        db.close()
    except Exception as e:
        logger.error(f"Error getting operator info: {e}")
    return {"id": operator_id, "name": operator_id, "role": "Customer Support Executive"}


def get_longest_idle_available_operator(exclude_op_id: str = None) -> Any:
    """
    Returns the operator who is currently AVAILABLE and has been idle/free
    for the longest duration (earliest availableSince timestamp).
    """
    available_ops = [
        op for op in online_operators.values()
        if op.get("status") == "AVAILABLE" and op.get("sid") and op.get("operatorId") != exclude_op_id
    ]
    if not available_ops:
        return None
    # Sort ascending by availableSince (oldest idle timestamp first)
    available_ops.sort(key=lambda x: x.get("availableSince", 0))
    return available_ops[0]


async def dispatch_call_to_operator(call_data: Dict[str, Any], target_op: Dict[str, Any]):
    """
    Emits incoming call ringing event ONLY to the specific allocated available operator.
    """
    if not target_op or target_op.get("status") != "AVAILABLE":
        logger.info(f"Target operator {target_op.get('operatorId')} is not AVAILABLE (Status: {target_op.get('status')})")
        return

    call_id = call_data["callId"]
    ring_start = call_data.get("ringStartTime") or datetime.utcnow().isoformat()
    call_data["ringStartTime"] = ring_start
    call_data["allocatedOperatorId"] = target_op["operatorId"]

    payload = {
        "callId": call_id,
        "kioskId": call_data.get("kioskId"),
        "passengerName": call_data.get("passengerName", "Luc Desmarais"),
        "flightNumber": call_data.get("flightNumber", "6E 203"),
        "pnr": call_data.get("pnr", "ABC123"),
        "ringStartTime": ring_start,
        "allocatedTo": target_op["operatorId"],
        "adaPriority": call_data.get("adaPriority", False)
    }

    logger.info(f"Allocating call {call_id} to available operator {target_op['operatorId']} (SID: {target_op.get('sid')})")
    if target_op.get("sid"):
        await sio.emit("INCOMING_CALL_RINGING", payload, room=target_op["sid"])


async def check_and_dispatch_queued_calls():
    """
    Checks for waiting calls in queue and dispatches to available idle operators.
    """
    for call in call_queue:
        if call.get("status") == "QUEUED" and not call.get("allocatedOperatorId"):
            idle_op = get_longest_idle_available_operator()
            if idle_op:
                await dispatch_call_to_operator(call, idle_op)
                break


@sio.event
async def connect(sid: str, environ: Dict[str, Any]):
    logger.info(f"Socket connected: {sid}")
    await sio.emit("CONNECTED_ACK", {"sid": sid, "timestamp": datetime.utcnow().isoformat()}, room=sid)


@sio.event
async def disconnect(sid: str):
    global call_queue
    logger.info(f"Socket disconnected: {sid}")
    client_info = connected_clients.pop(sid, None)
    if client_info:
        client_id = client_info.get("clientId")
        role = client_info.get("role")

        # If operator disconnected, update operator pool
        if role == "operator" and client_id in online_operators:
            # Check if this socket was the active one
            if online_operators[client_id].get("sid") == sid:
                online_operators[client_id]["status"] = "OFFLINE"
                logger.info(f"Operator {client_id} marked OFFLINE due to socket disconnect")

        # Remove any pending queued calls for this client and notify operators immediately
        removed_calls = [c for c in call_queue if c.get("kioskSid") == sid or (client_id and c.get("kioskId") == client_id)]
        call_queue = [c for c in call_queue if c not in removed_calls]
        for c in removed_calls:
            cid = c.get("callId")
            if cid in active_calls:
                active_calls.pop(cid, None)
            logger.info(f"Queued call cancelled due to socket disconnect: {cid}")
            await sio.emit("SUPPORT_CALL_CANCELLED", {"callId": cid, "kioskId": c.get("kioskId")}, room="operators")
            await sio.emit("INCOMING_CALL_DISMISSED", {"callId": cid}, room="operators")
        
        # Clean up active calls if client was in an active call
        call_id = client_info.get("active_call_id")
        if call_id and call_id in active_calls:
            call_session = active_calls.pop(call_id, None)
            dur_secs = 0
            if call_session:
                start_time_str = call_session.get("startTime")
                if start_time_str:
                    try:
                        start_dt = datetime.fromisoformat(start_time_str)
                        dur_secs = max(1, int((datetime.utcnow() - start_dt).total_seconds()))
                    except Exception:
                        pass
                auto_save_support_call(call_id, call_session, dur_secs)

            logger.info(f"Terminating call session {call_id} due to disconnect of {sid}")
            await sio.emit(
                "CALL_ENDED",
                {"callId": call_id, "reason": "PEER_DISCONNECTED", "durationSeconds": dur_secs},
                room=f"call_{call_id}"
            )
            # If an operator was in this call, make them available again
            op_id = call_session.get("operatorId") if call_session else None
            if op_id and op_id in online_operators:
                online_operators[op_id]["status"] = "AVAILABLE"
                online_operators[op_id]["availableSince"] = datetime.utcnow().timestamp()
                online_operators[op_id]["currentCallId"] = None


@sio.event
async def CANCEL_CALL_REQUEST(sid: str, data: Dict[str, Any]):
    """
    Kiosk cancels its pending call request before an operator answers.
    data = { "callId": "call_12345678", "kioskId": "T3-L1-K04" }
    """
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
        logger.info(f"Queued call cancelled by kiosk: {cid}")
        await sio.emit("SUPPORT_CALL_CANCELLED", {"callId": cid, "kioskId": c.get("kioskId")}, room="operators")
        await sio.emit("INCOMING_CALL_DISMISSED", {"callId": cid}, room="operators")

    await sio.emit("CALL_CANCELLED_ACK", {"status": "CANCELLED"}, room=sid)


@sio.event
async def REGISTER_CLIENT(sid: str, data: Dict[str, Any]):
    """
    Registers client as either 'kiosk' or 'operator'.
    data = { "role": "kiosk" | "operator", "clientId": "T3-L1-K04" | "op_101", "status": "AVAILABLE" | "OFFLINE", "name": str, "roleName": str }
    """
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

        if client_id in online_operators:
            online_operators[client_id]["sid"] = sid
            online_operators[client_id]["name"] = name
            online_operators[client_id]["roleName"] = role_name
            if status and status != "PRESERVE":
                online_operators[client_id]["status"] = status
        else:
            initial_status = status if (status and status != "PRESERVE") else "AVAILABLE"
            online_operators[client_id] = {
                "operatorId": client_id,
                "sid": sid,
                "name": name,
                "roleName": role_name,
                "status": initial_status,
                "availableSince": datetime.utcnow().timestamp(),
                "currentCallId": None
            }

        logger.info(f"Operator {client_id} ({name}) registered (Status: {online_operators[client_id]['status']})")
        await sio.emit("OPERATOR_STATE_SYNC", online_operators[client_id], room=sid)
        # Check if there are pending queued calls waiting for an operator
        await check_and_dispatch_queued_calls()

    await sio.emit("REGISTERED_ACK", {"status": "REGISTERED", "role": role, "clientId": client_id}, room=sid)


@sio.event
async def OPERATOR_STATUS_UPDATE(sid: str, data: Dict[str, Any]):
    """
    Operator toggles Online/Offline status.
    data = { "operatorId": "op_101", "status": "AVAILABLE" | "OFFLINE" }
    """
    op_id = data.get("operatorId", "op_101")
    status = data.get("status", "AVAILABLE")

    if op_id in online_operators:
        online_operators[op_id]["status"] = status
        online_operators[op_id]["sid"] = sid
        if status == "AVAILABLE":
            online_operators[op_id]["availableSince"] = datetime.utcnow().timestamp()
            logger.info(f"Operator {op_id} is now ONLINE & AVAILABLE. Checking for waiting calls in queue...")
            # Immediately dispatch waiting calls to this operator
            await check_and_dispatch_queued_calls()
        else:
            logger.info(f"Operator {op_id} is now OFFLINE (DND). No calls will ring this operator.")
            # Dismiss any ringing call currently displayed on this operator's screen
            for call in call_queue:
                if call.get("allocatedOperatorId") == op_id and call.get("status") == "QUEUED":
                    call["allocatedOperatorId"] = None
                    await sio.emit("INCOMING_CALL_DISMISSED", {"callId": call.get("callId")}, room=sid)
            # Re-dispatch any waiting calls to another available operator if online
            await check_and_dispatch_queued_calls()

        await sio.emit("OPERATOR_STATE_SYNC", online_operators[op_id], room=sid)


@sio.event
async def CALL_REQUEST(sid: str, data: Dict[str, Any]):
    """
    Kiosk places a call request into queue.
    Deduplicates existing pending call requests for the same kioskId.
    data = { "kioskId": "T3-L1-K04", "adaPriority": bool, "language": "EN" }
    """
    global call_queue
    import uuid
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    kiosk_id = data.get("kioskId", "Kiosk-01")
    ada_priority = data.get("adaPriority", False)
    language = data.get("language", "EN")
    passenger_name = data.get("passengerName", "Luc Desmarais")
    flight_number = data.get("flightNumber", "6E 203")
    pnr = data.get("pnr", "ABC123")
    ring_start_time = datetime.utcnow().isoformat()

    # Remove any existing pending queued call for this kioskId to prevent duplicates
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

    # Place in queue (prioritize ADA requests)
    if ada_priority:
        call_queue.insert(0, call_data)
    else:
        call_queue.append(call_data)

    logger.info(f"New call request enqueued: {call_id} from {kiosk_id} ({passenger_name})")

    # Notify kiosk that call is enqueued (kiosk starts ringing)
    await sio.emit("CALL_ENQUEUED_ACK", {"callId": call_id, "queuePosition": len(call_queue), "ringStartTime": ring_start_time}, room=sid)

    # Broadcast new queued call to all operators for dashboard counter
    await sio.emit("SUPPORT_CALL_ENQUEUED", call_data, room="operators")

    # Allocate to longest-idle available operator
    idle_op = get_longest_idle_available_operator()
    if idle_op:
        await dispatch_call_to_operator(call_data, idle_op)
    else:
        logger.info(f"No available online operator for call {call_id}. Call remains queued in waiting state until an operator becomes AVAILABLE.")


@sio.event
async def OPERATOR_DECLINE_CALL(sid: str, data: Dict[str, Any]):
    """
    Operator declines incoming call popup. Re-allocates call to the next longest-idle operator.
    data = { "callId": "call_12345678", "operatorId": "op_101" }
    """
    call_id = data.get("callId")
    operator_id = data.get("operatorId")
    logger.info(f"Operator {operator_id} declined call {call_id}. Re-routing to next available operator.")

    # Dismiss ringing on declining operator's screen
    await sio.emit("INCOMING_CALL_DISMISSED", {"callId": call_id}, room=sid)

    if call_id and call_id in active_calls:
        call = active_calls[call_id]
        if call.get("status") == "QUEUED":
            next_op = get_longest_idle_available_operator(exclude_op_id=operator_id)
            if next_op:
                await dispatch_call_to_operator(call, next_op)
            else:
                call["allocatedOperatorId"] = None
                logger.info(f"No other operator free to take call {call_id}. Waiting in queue.")


@sio.event
async def OPERATOR_ACCEPT_CALL(sid: str, data: Dict[str, Any]):
    """
    Operator accepts an incoming call.
    data = { "callId": "call_12345678", "operatorId": "op_101" }
    """
    global call_queue
    call_id = data.get("callId")
    operator_id = data.get("operatorId", "op_101")

    if not call_id or call_id not in active_calls:
        await sio.emit("ERROR", {"message": "Call session not found or already accepted"}, room=sid)
        return

    call_session = active_calls[call_id]
    if call_session["status"] != "QUEUED":
        await sio.emit("ERROR", {"message": "Call is no longer in queue"}, room=sid)
        return

    op_info = get_operator_info(operator_id)
    op_name = op_info.get("name", "Priya Sharma")
    op_role = op_info.get("role", "Customer Support Executive")

    # Update call session state
    call_session["status"] = "IN_PROGRESS"
    call_session["operatorId"] = operator_id
    call_session["operatorName"] = op_name
    call_session["operatorRole"] = op_role
    call_session["operatorSid"] = sid
    call_session["startTime"] = datetime.utcnow().isoformat()

    # Mark operator as BUSY
    if operator_id in online_operators:
        online_operators[operator_id]["status"] = "BUSY"
        online_operators[operator_id]["currentCallId"] = call_id
        await sio.emit("OPERATOR_STATE_SYNC", online_operators[operator_id], room=sid)

    if sid in connected_clients:
        connected_clients[sid]["active_call_id"] = call_id

    # Remove call from queue
    call_queue = [c for c in call_queue if c["callId"] != call_id]

    kiosk_sid = call_session.get("kioskSid")

    # Put both kiosk and operator into a dedicated call room
    room_name = f"call_{call_id}"
    await sio.enter_room(sid, room_name)
    if kiosk_sid:
        await sio.enter_room(kiosk_sid, room_name)

    logger.info(f"Operator {operator_id} ({op_name}) accepted call {call_id}. Room {room_name} created.")

    # Dismiss incoming ringing popups across all operators
    await sio.emit("INCOMING_CALL_DISMISSED", {"callId": call_id}, room="operators")

    # Send acceptance signal to kiosk and operator (stops ringtone and launches call)
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
    """
    Allows a client to join an existing call room (e.g. after page navigation).
    data = { "callId": "call_12345678", "role": "kiosk" | "operator" }
    """
    call_id = data.get("callId")
    role = data.get("role", "kiosk")
    if call_id:
        room_name = f"call_{call_id}"
        await sio.enter_room(sid, room_name)
        # Update the call session's kiosk sid if it's a kiosk reconnecting
        if role == "kiosk" and call_id in active_calls:
            active_calls[call_id]["kioskSid"] = sid
            session = active_calls[call_id]
            op_id = session.get("operatorId")
            op_info = get_operator_info(op_id) if op_id else {}
            op_name = session.get("operatorName") or op_info.get("name", "Priya Sharma")
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
        logger.info(f"{role} {sid} joined call room {room_name}")


@sio.event
async def OPERATOR_READY(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    operator_id = data.get("operatorId")
    if not operator_id and call_id in active_calls:
        operator_id = active_calls[call_id].get("operatorId")
    
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
    """
    Relays WebRTC SDP Offer from sender to recipient peer.
    data = { "callId": "call_123", "sdp": { ... } }
    """
    call_id = data.get("callId")
    sdp = data.get("sdp")
    room_name = f"call_{call_id}"
    logger.info(f"Relaying WEBRTC_OFFER in room {room_name}")
    await sio.emit("WEBRTC_OFFER", {"callId": call_id, "sdp": sdp}, room=room_name, skip_sid=sid)


@sio.event
async def WEBRTC_ANSWER(sid: str, data: Dict[str, Any]):
    """
    Relays WebRTC SDP Answer from recipient to sender peer.
    data = { "callId": "call_123", "sdp": { ... } }
    """
    call_id = data.get("callId")
    sdp = data.get("sdp")
    room_name = f"call_{call_id}"
    logger.info(f"Relaying WEBRTC_ANSWER in room {room_name}")
    await sio.emit("WEBRTC_ANSWER", {"callId": call_id, "sdp": sdp}, room=room_name, skip_sid=sid)


@sio.event
async def ICE_CANDIDATE(sid: str, data: Dict[str, Any]):
    """
    Relays ICE Candidates trickled by peer connection.
    data = { "callId": "call_123", "candidate": { ... } }
    """
    call_id = data.get("callId")
    candidate = data.get("candidate")
    room_name = f"call_{call_id}"
    await sio.emit("ICE_CANDIDATE", {"callId": call_id, "candidate": candidate}, room=room_name, skip_sid=sid)


def auto_save_support_call(call_id: str, session: Dict[str, Any], duration_seconds: int):
    """
    Automatically persists default SupportCall details to database as soon as a call completes,
    guaranteeing the record exists even if the operator does not manually submit the form.
    """
    if not call_id:
        return
    try:
        from database import SessionLocal
        from models import SupportCall, Kiosk
        db = SessionLocal()
        
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        recordings_dir = os.path.join(backend_dir, "recordings")
        rec_url = (session or {}).get("recordingUrl")
        if not rec_url:
            if os.path.exists(os.path.join(recordings_dir, f"{call_id}.webm")):
                rec_url = f"/recordings/{call_id}.webm"
            elif os.path.exists(os.path.join(recordings_dir, f"{call_id}.mp4")):
                rec_url = f"/recordings/{call_id}.mp4"

        existing = db.query(SupportCall).filter(SupportCall.id == call_id).first()
        kiosk_id = (session or {}).get("kioskId", "T3-L1-K04")
        kiosk_obj = db.query(Kiosk).filter((Kiosk.id == kiosk_id) | (Kiosk.code == kiosk_id)).first()
        kiosk_db_id = kiosk_obj.id if kiosk_obj else "T3-L1-K04"
        
        raw_op_id = (session or {}).get("operatorId")
        op_id = None
        if raw_op_id:
            op_match = db.query(Operator).filter(
                (Operator.id == raw_op_id) | (Operator.username == raw_op_id) | (Operator.employee_code == raw_op_id)
            ).first()
            op_id = op_match.id if op_match else raw_op_id
            
        passenger_name = (session or {}).get("passengerName") or "Luc Desmarais"
        flight_number = (session or {}).get("flightNumber") or "6E 203"
        pnr = (session or {}).get("pnr") or "ABC123"
        
        if existing:
            existing.call_duration_seconds = max(1, duration_seconds) if duration_seconds > 0 else existing.call_duration_seconds
            existing.status = "ended"
            if op_id:
                existing.operator_id = op_id
            if not existing.passenger_name or existing.passenger_name == "Passenger":
                existing.passenger_name = passenger_name
            if not existing.flight_number:
                existing.flight_number = flight_number
            if rec_url and not existing.recording_url:
                existing.recording_url = rec_url
            db.commit()
            logger.info(f"Auto-save updated existing support call {call_id} (operator: {existing.operator_id}, recording: {existing.recording_url})")
        else:
            new_call = SupportCall(
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
            logger.info(f"Auto-saved default support call record to DB: {call_id} (operator: {new_call.operator_id}, recording: {new_call.recording_url})")
        db.close()
    except Exception as e:
        logger.error(f"Error auto-saving support call {call_id}: {e}")


@sio.event
async def END_CALL(sid: str, data: Dict[str, Any]):
    """
    Terminates active call session and notifies participants.
    data = { "callId": "call_123", "reason": "KIOSK_ENDED" | "OPERATOR_ENDED" }
    """
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
                    duration_seconds = max(1, int((datetime.utcnow() - start_dt).total_seconds()))
                except Exception:
                    pass

    # Auto-save the call log immediately upon termination
    if call_id:
        auto_save_support_call(call_id, session, duration_seconds)

    # If operator was in this call and is still online, restore AVAILABLE status
    if op_id and op_id in online_operators:
        if online_operators[op_id].get("status") != "OFFLINE":
            online_operators[op_id]["status"] = "AVAILABLE"
            online_operators[op_id]["availableSince"] = datetime.utcnow().timestamp()
            online_operators[op_id]["currentCallId"] = None
            logger.info(f"Operator {op_id} is now free and AVAILABLE (added back to queue)")
            await sio.emit("OPERATOR_STATE_SYNC", online_operators[op_id], room=online_operators[op_id].get("sid", ""))
            # Check if another call is waiting in queue
            await check_and_dispatch_queued_calls()

    logger.info(f"Call {call_id} ended: {reason} (duration: {duration_seconds}s, agent: {op_name})")
    await sio.emit("CALL_ENDED", {
        "callId": call_id,
        "reason": reason,
        "operatorName": op_name,
        "durationSeconds": duration_seconds
    }, room=room_name)


@sio.event
async def MEDIA_STATE_CHANGED(sid: str, data: Dict[str, Any]):
    """
    Relays media track states (mute / video off) between participants.
    data = { "callId": "call_123", "role": "kiosk" | "operator", "isMuted": bool, "isVideoOff": bool }
    """
    call_id = data.get("callId")
    if call_id:
        room_name = f"call_{call_id}"
        logger.info(f"Relaying MEDIA_STATE_CHANGED in room {room_name}: {data}")
        await sio.emit("MEDIA_STATE_CHANGED", data, room=room_name, skip_sid=sid)


@sio.event
async def SCREEN_ANNOTATION_STROKE(sid: str, data: Dict[str, Any]):
    """
    Relays live screen drawing stroke events between Operator and Kiosk screen.
    data = { "callId": "call_123", "action": "START"|"DRAW"|"CLEAR", "stroke": {...} }
    """
    call_id = data.get("callId")
    room_name = f"call_{call_id}"
    await sio.emit("SCREEN_ANNOTATION_STROKE", data, room=room_name, skip_sid=sid)

