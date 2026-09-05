"""
Unit & Integration Tests for Socket.IO WebRTC Signaling & Telemetry
Tests event handlers: connect, register, call queue, accept, media, strokes, and ghost cleanup.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.modules.support import service
from app.core.timezone import get_current_time


@pytest.fixture(autouse=True)
def reset_service_state():
    """Reset in-memory signaling state before and after each test."""
    service.active_calls.clear()
    service.connected_clients.clear()
    service.call_queue.clear()
    service.online_operators.clear()
    service.online_kiosks.clear()
    service.active_kiosk_claims.clear()
    yield
    service.active_calls.clear()
    service.connected_clients.clear()
    service.call_queue.clear()
    service.online_operators.clear()
    service.online_kiosks.clear()
    service.active_kiosk_claims.clear()


@pytest.mark.asyncio
async def test_socketio_connection_and_disconnect():
    sid = "test_kiosk_sid_123"
    environ = {"HTTP_UPGRADE": "websocket"}

    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.connect(sid, environ)
        mock_emit.assert_called_once()
        args, kwargs = mock_emit.call_args
        assert args[0] == "CONNECTED_ACK"
        assert kwargs.get("room") == sid

    # Register client
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.REGISTER_CLIENT(sid, {"role": "kiosk", "clientId": "KIOSK-T3-01"})
        assert sid in service.connected_clients
        assert service.connected_clients[sid]["role"] == "kiosk"
        assert "KIOSK-T3-01" in service.online_kiosks

    # Disconnect client
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.disconnect(sid)
        assert sid not in service.connected_clients
        assert "KIOSK-T3-01" not in service.online_kiosks


@pytest.mark.asyncio
async def test_operator_registration_and_status_sync():
    sid = "test_operator_sid_456"
    op_id = "op_101"

    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit, \
         patch.object(service.sio, "enter_room", new_callable=AsyncMock) as mock_enter_room:
        await service.REGISTER_CLIENT(sid, {
            "role": "operator",
            "clientId": op_id,
            "name": "Priya Sharma",
            "roleName": "Customer Support Executive"
        })

        assert sid in service.connected_clients
        assert op_id in service.online_operators
        assert service.online_operators[op_id]["status"] == "AVAILABLE"
        mock_enter_room.assert_called_with(sid, "operators")

    # Update status to BUSY
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.OPERATOR_STATUS_UPDATE(sid, {"operatorId": op_id, "status": "BUSY"})
        assert service.online_operators[op_id]["status"] == "BUSY"


@pytest.mark.asyncio
async def test_call_request_and_queue_prioritization():
    kiosk1_sid = "kiosk_sid_1"
    kiosk2_sid = "kiosk_sid_2"

    # Enqueue standard call
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.CALL_REQUEST(kiosk1_sid, {
            "kioskId": "KIOSK-01",
            "adaPriority": False,
            "passengerName": "Passenger One"
        })
        assert len(service.call_queue) == 1
        assert service.call_queue[0]["kioskId"] == "KIOSK-01"

    # Enqueue ADA priority call (should be inserted at front)
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.CALL_REQUEST(kiosk2_sid, {
            "kioskId": "KIOSK-ADA-02",
            "adaPriority": True,
            "passengerName": "Passenger Two"
        })
        assert len(service.call_queue) == 2
        assert service.call_queue[0]["kioskId"] == "KIOSK-ADA-02"
        assert service.call_queue[0]["adaPriority"] is True


@pytest.mark.asyncio
async def test_operator_accept_call_workflow():
    op_sid = "op_sid_789"
    op_id = "op_101"
    kiosk_sid = "kiosk_sid_001"

    # Register available operator
    with patch.object(service.sio, "emit", new_callable=AsyncMock), \
         patch.object(service.sio, "enter_room", new_callable=AsyncMock):
        await service.REGISTER_CLIENT(op_sid, {
            "role": "operator",
            "clientId": op_id,
            "name": "Priya Sharma"
        })

    # Enqueue call
    with patch.object(service.sio, "emit", new_callable=AsyncMock):
        await service.CALL_REQUEST(kiosk_sid, {
            "kioskId": "KIOSK-01",
            "adaPriority": False,
            "passengerName": "John Doe"
        })

    call_id = list(service.active_calls.keys())[0]

    # Operator accepts call
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit, \
         patch.object(service.sio, "enter_room", new_callable=AsyncMock) as mock_enter_room:
        await service.OPERATOR_ACCEPT_CALL(op_sid, {
            "callId": call_id,
            "operatorId": op_id
        })

        assert service.active_calls[call_id]["status"] == "IN_PROGRESS"
        assert service.active_calls[call_id]["operatorId"] == op_id
        assert service.online_operators[op_id]["status"] == "BUSY"
        assert len(service.call_queue) == 0


@pytest.mark.asyncio
async def test_webrtc_signaling_and_annotations():
    call_id = "call_test_123"
    sid = "socket_sid_abc"
    service.active_calls[call_id] = {"callId": call_id, "status": "IN_PROGRESS"}

    # Test WebRTC Offer relay
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.WEBRTC_OFFER(sid, {"callId": call_id, "sdp": "v=0\r\ntest-offer"})
        mock_emit.assert_called_once_with(
            "WEBRTC_OFFER",
            {"callId": call_id, "sdp": "v=0\r\ntest-offer"},
            room=f"call_{call_id}",
            skip_sid=sid
        )

    # Test WebRTC Answer relay
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.WEBRTC_ANSWER(sid, {"callId": call_id, "sdp": "v=0\r\ntest-answer"})
        mock_emit.assert_called_once_with(
            "WEBRTC_ANSWER",
            {"callId": call_id, "sdp": "v=0\r\ntest-answer"},
            room=f"call_{call_id}",
            skip_sid=sid
        )

    # Test Screen Annotation Stroke relay
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        stroke_data = {"callId": call_id, "points": [{"x": 10, "y": 20}, {"x": 15, "y": 25}], "color": "#FF0000"}
        await service.SCREEN_ANNOTATION_STROKE(sid, stroke_data)
        mock_emit.assert_called_once_with(
            "SCREEN_ANNOTATION_STROKE",
            stroke_data,
            room=f"call_{call_id}",
            skip_sid=sid
        )


@pytest.mark.asyncio
async def test_remote_control_starts_only_for_assigned_operator_and_electron_client():
    call_id = "call_remote_electron"
    operator_sid = "operator_remote_sid"
    kiosk_sid = "kiosk_remote_sid"
    service.connected_clients[kiosk_sid] = {
        "sid": kiosk_sid,
        "role": "kiosk",
        "clientId": "KIOSK-01",
        "runtimeEnv": "electron"
    }
    service.active_calls[call_id] = {
        "callId": call_id,
        "status": "IN_PROGRESS",
        "operatorSid": operator_sid,
        "kioskSid": kiosk_sid,
        "kioskId": "KIOSK-01"
    }

    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.REMOTE_CONTROL_REQUEST(operator_sid, {
            "callId": call_id,
            "operatorId": "op_101",
            "operatorName": "Priya Sharma"
        })

        assert service.active_calls[call_id]["remoteControlActive"] is True
        start_calls = [call for call in mock_emit.call_args_list if call.args[0] == "REMOTE_CONTROL_START"]
        assert len(start_calls) == 1
        assert start_calls[0].kwargs["room"] == kiosk_sid

    event = {"callId": call_id, "type": "click", "normX": 0.4, "normY": 0.6}
    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.REMOTE_CONTROL_EVENT(operator_sid, event)
        mock_emit.assert_called_once_with("REMOTE_CONTROL_EVENT", event, room=kiosk_sid)


@pytest.mark.asyncio
async def test_remote_control_reports_browser_client_as_unavailable():
    call_id = "call_remote_browser"
    operator_sid = "operator_browser_sid"
    kiosk_sid = "kiosk_browser_sid"
    service.connected_clients[kiosk_sid] = {
        "sid": kiosk_sid,
        "role": "kiosk",
        "clientId": "KIOSK-WEB",
        "runtimeEnv": "browser"
    }
    service.active_calls[call_id] = {
        "callId": call_id,
        "status": "IN_PROGRESS",
        "operatorSid": operator_sid,
        "kioskSid": kiosk_sid,
        "kioskId": "KIOSK-WEB"
    }

    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.REMOTE_CONTROL_REQUEST(operator_sid, {
            "callId": call_id,
            "operatorId": "op_101",
            "operatorName": "Priya Sharma"
        })

        assert service.active_calls[call_id]["remoteControlActive"] is False
        mock_emit.assert_called_once()
        assert mock_emit.call_args.args[0] == "REMOTE_CONTROL_UNAVAILABLE"
        assert mock_emit.call_args.kwargs["room"] == operator_sid


@pytest.mark.asyncio
async def test_remote_input_rejects_unassigned_socket():
    call_id = "call_remote_forbidden"
    service.active_calls[call_id] = {
        "callId": call_id,
        "status": "IN_PROGRESS",
        "remoteControlActive": True,
        "operatorSid": "assigned_operator_sid",
        "kioskSid": "assigned_kiosk_sid"
    }

    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.REMOTE_CONTROL_EVENT("attacker_sid", {
            "callId": call_id,
            "type": "click",
            "normX": 0.5,
            "normY": 0.5
        })

        mock_emit.assert_called_once()
        assert mock_emit.call_args.args[0] == "REMOTE_CONTROL_ERROR"
        assert mock_emit.call_args.args[1]["code"] == "NOT_ASSIGNED_OPERATOR"
        assert mock_emit.call_args.kwargs["room"] == "attacker_sid"


@pytest.mark.asyncio
async def test_end_call_lifecycle():
    op_sid = "op_sid_end"
    op_id = "op_101"
    kiosk_sid = "kiosk_sid_end"
    call_id = "call_end_test"

    service.online_operators[op_id] = {
        "operatorId": op_id,
        "sid": op_sid,
        "status": "BUSY",
        "currentCallId": call_id
    }
    service.active_calls[call_id] = {
        "callId": call_id,
        "operatorId": op_id,
        "operatorName": "Priya Sharma",
        "kioskId": "KIOSK-T3-01",
        "status": "IN_PROGRESS",
        "startTime": get_current_time().isoformat()
    }

    with patch.object(service.sio, "emit", new_callable=AsyncMock) as mock_emit:
        await service.END_CALL(kiosk_sid, {"callId": call_id, "reason": "PASSENGER_ENDED"})
        assert call_id not in service.active_calls
        assert service.online_operators[op_id]["status"] == "AVAILABLE"
        assert service.online_operators[op_id]["currentCallId"] is None


@pytest.mark.asyncio
async def test_ghost_connection_cleanup():
    # Setup ghost operator (sid not in connected_clients)
    service.online_operators["op_ghost"] = {
        "operatorId": "op_ghost",
        "sid": "dead_socket_sid",
        "status": "AVAILABLE"
    }

    # Setup ghost kiosk (lastSeen expired)
    service.online_kiosks["KIOSK-EXPIRED"] = {
        "kioskId": "KIOSK-EXPIRED",
        "sid": "dead_kiosk_sid",
        "lastSeen": get_current_time().timestamp() - 300,
        "status": "online"
    }

    # Setup stale queued call from dead kiosk
    service.call_queue.append({
        "callId": "call_stale_1",
        "kioskSid": "dead_kiosk_sid",
        "status": "QUEUED"
    })
    service.active_calls["call_stale_1"] = {
        "callId": "call_stale_1",
        "status": "QUEUED"
    }

    with patch.object(service.sio, "emit", new_callable=AsyncMock):
        stats = await service.cleanup_ghost_connections(timeout_seconds=60)
        assert stats["cleaned_operators"] == 1
        assert stats["cleaned_kiosks"] == 1
        assert stats["cleaned_calls"] == 1
        assert service.online_operators["op_ghost"]["status"] == "OFFLINE"
        assert "KIOSK-EXPIRED" not in service.online_kiosks
        assert len(service.call_queue) == 0
