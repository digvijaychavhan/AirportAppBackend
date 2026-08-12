"""
Support & Operator Call Queue REST Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from services.webrtc_signaling import active_calls, call_queue

router = APIRouter(prefix="/api/v1", tags=["Support Queue"])


class CallRequestPayload(BaseModel):
    kioskId: str = Field(..., example="T3-L1-K04")
    adaPriority: bool = Field(default=False)
    language: str = Field(default="EN")


class AcceptCallPayload(BaseModel):
    callId: str = Field(..., example="call_12345678")
    operatorId: str = Field(..., example="op_priya_101")


@router.post("/support/call-request")
async def place_call_request(payload: CallRequestPayload):
    """
    Enqueues a new video support call request from a kiosk.
    """
    import uuid
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    call_data = {
        "callId": call_id,
        "kioskId": payload.kioskId,
        "adaPriority": payload.adaPriority,
        "language": payload.language,
        "status": "QUEUED",
        "enqueueTimestamp": datetime.utcnow().isoformat()
    }
    
    active_calls[call_id] = call_data
    if payload.adaPriority:
        call_queue.insert(0, call_data)
    else:
        call_queue.append(call_data)
        
    return {
        "success": True,
        "data": call_data,
        "queuePosition": len(call_queue)
    }


@router.get("/operator/queue")
async def get_active_call_queue():
    """
    Fetches active waiting video call queue for Operator Dashboard.
    """
    return {
        "success": True,
        "count": len(call_queue),
        "queue": call_queue
    }


@router.post("/operator/queue/clear")
async def clear_call_queue():
    """
    Clears all stale waiting calls from operator queue.
    """
    global call_queue
    call_queue.clear()
    return {
        "success": True,
        "message": "Call queue cleared"
    }


@router.post("/operator/calls/accept")
async def accept_call(payload: AcceptCallPayload):
    """
    Operator accepts a call request from queue.
    """
    call_id = payload.callId
    if call_id not in active_calls:
        raise HTTPException(status_code=404, detail="Call request not found or expired")

    session = active_calls[call_id]
    if session["status"] != "QUEUED":
        raise HTTPException(status_code=400, detail="Call has already been accepted by another operator")

    session["status"] = "IN_PROGRESS"
    session["operatorId"] = payload.operatorId
    session["startTime"] = datetime.utcnow().isoformat()

    # Remove from queue list
    global call_queue
    call_queue[:] = [c for c in call_queue if c["callId"] != call_id]

    return {
        "success": True,
        "message": "Call accepted successfully",
        "data": session
    }
