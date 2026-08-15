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
        # Remove any pending queued calls for this client and notify operators immediately
        removed_calls = [c for c in call_queue if c.get("kioskSid") == sid or (client_id and c.get("kioskId") == client_id)]
        call_queue = [c for c in call_queue if c not in removed_calls]
        for c in removed_calls:
            cid = c.get("callId")
            if cid in active_calls:
                active_calls.pop(cid, None)
            logger.info(f"Queued call cancelled due to socket disconnect: {cid}")
            await sio.emit("SUPPORT_CALL_CANCELLED", {"callId": cid, "kioskId": c.get("kioskId")}, room="operators")
        
        # Clean up active calls if client was in an active call
        call_id = client_info.get("active_call_id")
        if call_id and call_id in active_calls:
            call_session = active_calls[call_id]
            logger.info(f"Terminating call session {call_id} due to disconnect of {sid}")
            await sio.emit(
                "CALL_ENDED",
                {"callId": call_id, "reason": "PEER_DISCONNECTED"},
                room=f"call_{call_id}"
            )
            active_calls.pop(call_id, None)


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

    await sio.emit("CALL_CANCELLED_ACK", {"status": "CANCELLED"}, room=sid)


@sio.event
async def REGISTER_CLIENT(sid: str, data: Dict[str, Any]):
    """
    Registers client as either 'kiosk' or 'operator'.
    data = { "role": "kiosk" | "operator", "clientId": "T3-L1-K04" | "op_101" }
    """
    role = data.get("role", "kiosk")
    client_id = data.get("clientId", sid)
    # Preserve active_call_id if client is re-registering (e.g. after page navigation)
    existing_call_id = connected_clients.get(sid, {}).get("active_call_id")
    connected_clients[sid] = {
        "sid": sid,
        "role": role,
        "clientId": client_id,
        "active_call_id": existing_call_id
    }

    if role == "operator":
        await sio.enter_room(sid, "operators")
        logger.info(f"Operator {client_id} joined operators room")

    await sio.emit("REGISTERED_ACK", {"status": "REGISTERED", "role": role, "clientId": client_id}, room=sid)


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

    # Remove any existing pending queued call for this kioskId to prevent duplicates
    call_queue = [c for c in call_queue if c.get("kioskId") != kiosk_id]

    call_data = {
        "callId": call_id,
        "kioskId": kiosk_id,
        "kioskSid": sid,
        "operatorId": None,
        "operatorSid": None,
        "adaPriority": ada_priority,
        "language": language,
        "status": "QUEUED",
        "passengerName": passenger_name,
        "flightNumber": flight_number,
        "pnr": pnr,
        "enqueueTime": datetime.utcnow().isoformat()
    }

    active_calls[call_id] = call_data
    if sid in connected_clients:
        connected_clients[sid]["active_call_id"] = call_id

    # Place in queue (prioritize ADA requests)
    if ada_priority:
        call_queue.insert(0, call_data)
    else:
        call_queue.append(call_data)

    logger.info(f"New call request enqueued: {call_id} from {kiosk_id}")

    # Notify kiosk that call is enqueued
    await sio.emit("CALL_ENQUEUED_ACK", {"callId": call_id, "queuePosition": len(call_queue)}, room=sid)

    # Broadcast new queued call to all operators
    await sio.emit("SUPPORT_CALL_ENQUEUED", call_data, room="operators")


@sio.event
async def OPERATOR_ACCEPT_CALL(sid: str, data: Dict[str, Any]):
    """
    Operator accepts an incoming queued call.
    data = { "callId": "call_12345678", "operatorId": "op_101" }
    """
    global call_queue
    call_id = data.get("callId")
    operator_id = data.get("operatorId", "op_default")

    if not call_id or call_id not in active_calls:
        await sio.emit("ERROR", {"message": "Call session not found or already accepted"}, room=sid)
        return

    call_session = active_calls[call_id]
    if call_session["status"] != "QUEUED":
        await sio.emit("ERROR", {"message": "Call is no longer in queue"}, room=sid)
        return

    # Update call session state
    call_session["status"] = "IN_PROGRESS"
    call_session["operatorId"] = operator_id
    call_session["operatorSid"] = sid
    call_session["startTime"] = datetime.utcnow().isoformat()

    if sid in connected_clients:
        connected_clients[sid]["active_call_id"] = call_id

    # Remove call from queue
    call_queue = [c for c in call_queue if c["callId"] != call_id]

    kiosk_sid = call_session["kioskSid"]

    # Put both kiosk and operator into a dedicated call room
    room_name = f"call_{call_id}"
    await sio.enter_room(sid, room_name)
    if kiosk_sid:
        await sio.enter_room(kiosk_sid, room_name)

    logger.info(f"Operator {operator_id} accepted call {call_id}. Room {room_name} created.")

    # Send acceptance signal to kiosk and operator
    accept_payload = {
        "callId": call_id,
        "operatorId": operator_id,
        "kioskId": call_session["kioskId"],
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
        if sid in connected_clients:
            connected_clients[sid]["active_call_id"] = call_id
        logger.info(f"{role} {sid} joined call room {room_name}")


@sio.event
async def OPERATOR_READY(sid: str, data: Dict[str, Any]):
    call_id = data.get("callId")
    room_name = f"call_{call_id}"
    await sio.emit("OPERATOR_READY", {"callId": call_id}, room=room_name)


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

    if call_id and call_id in active_calls:
        active_calls.pop(call_id, None)

    logger.info(f"Call {call_id} ended: {reason}")
    await sio.emit("CALL_ENDED", {"callId": call_id, "reason": reason}, room=room_name)


@sio.event
async def SCREEN_ANNOTATION_STROKE(sid: str, data: Dict[str, Any]):
    """
    Relays live screen drawing stroke events between Operator and Kiosk screen.
    data = { "callId": "call_123", "action": "START"|"DRAW"|"CLEAR", "stroke": {...} }
    """
    call_id = data.get("callId")
    room_name = f"call_{call_id}"
    await sio.emit("SCREEN_ANNOTATION_STROKE", data, room=room_name, skip_sid=sid)
