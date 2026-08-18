"""
Support & Operator Call Queue REST Endpoints
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import logger
from app.core.config import settings
import app.db.models as models
from app.modules.support.schemas import (
    CallRequestPayload,
    AcceptCallPayload,
    OperatorLogSubmitPayload
)
from app.modules.support.service import (
    active_calls,
    call_queue,
    online_operators,
    get_operator_info,
    get_recordings_dir
)

router = APIRouter(tags=["Support & Operators"])

@router.post("/api/v1/support/call-request")
async def place_call_request(payload: CallRequestPayload):
    """
    Enqueues a new video support call request from a kiosk.
    """
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    call_data = {
        "callId": call_id,
        "kioskId": payload.kiosk_id,
        "adaPriority": payload.ada_priority,
        "language": payload.language,
        "status": "QUEUED",
        "enqueueTimestamp": datetime.utcnow().isoformat()
    }

    active_calls[call_id] = call_data
    if payload.ada_priority:
        call_queue.insert(0, call_data)
    else:
        call_queue.append(call_data)

    return {
        "success": True,
        "data": call_data,
        "queuePosition": len(call_queue)
    }


@router.get("/api/v1/operator/queue")
async def get_active_call_queue():
    """
    Fetches active waiting video call queue for Operator Dashboard.
    """
    return {
        "success": True,
        "totalQueued": len(call_queue),
        "queue": call_queue
    }


@router.post("/api/v1/operator/queue/clear")
async def clear_call_queue():
    """
    Clears all stale waiting calls from operator queue.
    """
    global call_queue
    call_queue.clear()
    return {"success": True, "message": "Call queue cleared"}


@router.post("/api/v1/operator/calls/accept")
async def accept_call(payload: AcceptCallPayload):
    """
    Operator accepts a call request from queue.
    """
    call_id = payload.call_id
    if call_id not in active_calls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Call request not found or expired"}
        )

    session = active_calls[call_id]
    if session["status"] != "QUEUED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Call has already been accepted by another operator"}
        )

    session["status"] = "IN_PROGRESS"
    session["operatorId"] = payload.operator_id
    session["startTime"] = datetime.utcnow().isoformat()

    global call_queue
    call_queue[:] = [c for c in call_queue if c.get("callId") != call_id]

    return {
        "success": True,
        "message": "Call accepted successfully",
        "data": session
    }


@router.get("/api/v1/operator/call/{call_id}")
async def get_call_details(
    call_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve call session details, notes, categories, and recording URL.
    """
    rec_dir = get_recordings_dir()
    rec_file_url = None
    if os.path.exists(os.path.join(rec_dir, f"{call_id}.webm")):
        rec_file_url = f"/recordings/{call_id}.webm"
    elif os.path.exists(os.path.join(rec_dir, f"{call_id}.mp4")):
        rec_file_url = f"/recordings/{call_id}.mp4"

    if call_id in active_calls:
        session = active_calls[call_id]
        op_id = session.get("operatorId")
        op_name = session.get("operatorName")
        op_role = session.get("operatorRole")
        if op_id and not op_name:
            op_info = get_operator_info(op_id)
            op_name = op_info.get("name")
            op_role = op_info.get("role")

        return {
            "success": True,
            "data": {
                **session,
                "operatorName": op_name or "Priya Sharma",
                "operatorRole": op_role or "Customer Support Executive",
                "recordingUrl": session.get("recordingUrl") or rec_file_url
            }
        }

    try:
        call = db.query(models.SupportCall).filter(models.SupportCall.id == call_id).first()
        if call:
            minutes = call.call_duration_seconds // 60
            seconds = call.call_duration_seconds % 60
            dur_str = f"{minutes:02d}:{seconds:02d}"
            kiosk_code = call.kiosk.code if call.kiosk else (call.kiosk_id or "T3-L1-K04")

            categories_list = [c.strip() for c in call.issue_category.split(",")] if call.issue_category else []
            op_name = "Operator"
            op_role = "Customer Support Executive"
            if call.operator:
                op_name = call.operator.name
                op_role = call.operator.role.replace("_", " ").title() if call.operator.role else "Customer Support Executive"
            elif call.operator_id:
                op_lookup = db.query(models.Operator).filter(
                    (models.Operator.id == call.operator_id) |
                    (models.Operator.employee_code == call.operator_id) |
                    (models.Operator.username == call.operator_id)
                ).first()
                if op_lookup:
                    op_name = op_lookup.name
                    op_role = op_lookup.role.replace("_", " ").title() if op_lookup.role else "Customer Support Executive"
                else:
                    op_name = call.operator_id

            rec_url = call.recording_url or rec_file_url

            data = {
                "sessionId": call.id,
                "passengerName": call.passenger_name or "",
                "flightNumber": call.flight_number or "",
                "pnr": call.pnr or "",
                "kioskId": kiosk_code,
                "duration": dur_str,
                "operatorId": call.operator_id,
                "operatorName": op_name,
                "operatorRole": op_role,
                "notes": call.operator_notes or "",
                "categories": categories_list,
                "recordingUrl": rec_url,
                "date": call.created_at.strftime("%d-%b-%y"),
                "time": call.created_at.strftime("%I:%M %p"),
                "status": "RESOLVED"
            }
            return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching call details for {call_id}: {e}")

    if rec_file_url:
        return {
            "success": True,
            "data": {
                "sessionId": call_id,
                "passengerName": "",
                "recordingUrl": rec_file_url,
                "status": "RESOLVED"
            }
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"success": False, "message": "Call not found"}
    )


@router.post("/api/v1/operator/logs/submit")
async def submit_operator_log(
    payload: OperatorLogSubmitPayload,
    db: Session = Depends(get_db)
):
    """
    Submits finalized call notes, category tagging, and operator resolution log.
    """
    try:
        session_id = payload.session_id
        kiosk_id = payload.kiosk_id or "T3-L1-K04"

        kiosk_obj = db.query(models.Kiosk).filter(
            (models.Kiosk.id == kiosk_id) | (models.Kiosk.code == kiosk_id)
        ).first()
        kiosk_db_id = kiosk_obj.id if kiosk_obj else "T3-L1-K04"

        duration_str = payload.duration or "00:00"
        call_duration_seconds = 0
        if ":" in duration_str:
            parts = duration_str.split(":")
            if len(parts) == 2:
                call_duration_seconds = int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                call_duration_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

        categories = payload.categories or []
        categories_str = ", ".join(categories) if categories else None

        passenger_name = f"{payload.first_name} {payload.last_name}".strip() or payload.passenger_name or ""
        raw_op_id = payload.operator_id
        op_obj = db.query(models.Operator).filter(
            (models.Operator.id == raw_op_id) |
            (models.Operator.username == raw_op_id) |
            (models.Operator.employee_code == raw_op_id)
        ).first() if raw_op_id else None
        op_id = op_obj.id if op_obj else (raw_op_id or "op_101")

        rec_dir = get_recordings_dir()
        rec_url = payload.recording_url
        if not rec_url and session_id:
            if os.path.exists(os.path.join(rec_dir, f"{session_id}.webm")):
                rec_url = f"/recordings/{session_id}.webm"
            elif os.path.exists(os.path.join(rec_dir, f"{session_id}.mp4")):
                rec_url = f"/recordings/{session_id}.mp4"

        existing_call = db.query(models.SupportCall).filter(models.SupportCall.id == session_id).first() if session_id else None
        if existing_call:
            existing_call.kiosk_id = kiosk_db_id
            existing_call.operator_id = op_id
            if call_duration_seconds > 0:
                existing_call.call_duration_seconds = call_duration_seconds
            if categories_str:
                existing_call.issue_category = categories_str
            if payload.notes:
                existing_call.operator_notes = payload.notes
            existing_call.passenger_name = passenger_name
            existing_call.flight_number = payload.flight_no or payload.flight_number or ""
            existing_call.pnr = payload.pnr or ""
            if rec_url and not existing_call.recording_url:
                existing_call.recording_url = rec_url
            existing_call.status = "ended"
            db.commit()
            support_call = existing_call
        else:
            support_call = models.SupportCall(
                id=session_id or None,
                kiosk_id=kiosk_db_id,
                operator_id=op_id,
                status="ended",
                call_duration_seconds=call_duration_seconds,
                issue_category=categories_str or "General Inquiry",
                operator_notes=payload.notes or "Assisted passenger at kiosk.",
                passenger_name=passenger_name,
                flight_number=payload.flight_no or payload.flight_number or "",
                pnr=payload.pnr or "",
                recording_url=rec_url
            )
            db.add(support_call)
            db.commit()

        res_data = {
            "session": support_call.id,
            "date": support_call.created_at.strftime("%d-%b-%y"),
            "time": support_call.created_at.strftime("%I:%M %p"),
            "kiosk": kiosk_id,
            "passenger": support_call.passenger_name,
            "duration": duration_str,
            "notes": support_call.operator_notes,
            "categories": categories,
            "flightNo": support_call.flight_number,
            "recordingUrl": support_call.recording_url
        }

        return {"success": True, "message": "Log saved successfully", "data": res_data}
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting operator log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.get("/api/v1/operator/stats")
async def get_operator_stats(
    operatorId: Optional[str] = Query(None),
    operator_id: Optional[str] = Query(None),
    scope: str = Query("me"),
    db: Session = Depends(get_db)
):
    """
    Returns analytics KPIs for Operator Dashboard.
    """
    try:
        raw_op_id = operatorId or operator_id
        query = db.query(models.SupportCall)

        if raw_op_id and scope != "all":
            op = db.query(models.Operator).filter(
                (models.Operator.id == raw_op_id) |
                (models.Operator.username == raw_op_id) |
                (models.Operator.employee_code == raw_op_id)
            ).first()
            actual_op_id = op.id if op else raw_op_id
            query = query.filter(models.SupportCall.operator_id == actual_op_id)

        calls = query.all()
        total = len(calls)
        active_ops_count = max(1, len([op for op in online_operators.values() if op.get("status") == "AVAILABLE"]))

        if total == 0:
            return {
                "success": True,
                "data": {
                    "totalInboundCalls": 0,
                    "avgCallTimeMinutes": "0.00",
                    "resolutionRate": "100%",
                    "activeOperators": active_ops_count
                }
            }

        total_seconds = sum(c.call_duration_seconds for c in calls)
        avg_minutes = (total_seconds / 60) / total if total > 0 else 0

        return {
            "success": True,
            "data": {
                "totalInboundCalls": total,
                "avgCallTimeMinutes": f"{avg_minutes:.2f}",
                "resolutionRate": "98%",
                "activeOperators": active_ops_count
            }
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.get("/api/v1/operator/logs")
async def get_operator_logs(
    operatorId: Optional[str] = Query(None),
    operator_id: Optional[str] = Query(None),
    scope: str = Query("me"),
    timeFilter: Optional[str] = Query(""),
    db: Session = Depends(get_db)
):
    """
    Returns historical call logs with filtering by operator and time horizon.
    """
    try:
        raw_op_id = operatorId or operator_id
        time_filter = (timeFilter or "").lower().strip()
        query = db.query(models.SupportCall)

        if raw_op_id and scope != "all":
            op = db.query(models.Operator).filter(
                (models.Operator.id == raw_op_id) |
                (models.Operator.username == raw_op_id) |
                (models.Operator.employee_code == raw_op_id)
            ).first()
            actual_op_id = op.id if op else raw_op_id
            query = query.filter(models.SupportCall.operator_id == actual_op_id)

        now = datetime.utcnow()
        if time_filter == "today":
            start_of_today = datetime(now.year, now.month, now.day)
            query = query.filter(models.SupportCall.created_at >= start_of_today)
        elif time_filter == "yesterday":
            start_of_today = datetime(now.year, now.month, now.day)
            start_of_yesterday = start_of_today - timedelta(days=1)
            query = query.filter(
                models.SupportCall.created_at >= start_of_yesterday,
                models.SupportCall.created_at < start_of_today
            )
        elif time_filter in ("this week", "this_week", "week"):
            start_of_week = now - timedelta(days=7)
            query = query.filter(models.SupportCall.created_at >= start_of_week)

        calls = query.order_by(models.SupportCall.created_at.desc()).all()
        rec_dir = get_recordings_dir()

        logs = []
        for c in calls:
            kiosk_code = c.kiosk.code if c.kiosk else (c.kiosk_id or "T3-L1-K04")
            minutes = c.call_duration_seconds // 60
            seconds = c.call_duration_seconds % 60
            duration_str = f"{minutes:02d}:{seconds:02d}"

            rec_url = c.recording_url
            if rec_url and "/api/v1/recordings/" in rec_url:
                rec_url = rec_url.replace("/api/v1/recordings/", "/recordings/")
            if not rec_url:
                if os.path.exists(os.path.join(rec_dir, f"{c.id}.webm")):
                    rec_url = f"/recordings/{c.id}.webm"
                elif os.path.exists(os.path.join(rec_dir, f"{c.id}.mp4")):
                    rec_url = f"/recordings/{c.id}.mp4"

            op_name = c.operator.name if c.operator else "Priya Sharma"
            op_code = c.operator.employee_code if c.operator else "EMP-9021"
            op_id_val = c.operator_id or (c.operator.id if c.operator else "op_101")

            logs.append({
                "session": c.id,
                "date": c.created_at.strftime("%d-%b-%y"),
                "time": c.created_at.strftime("%I:%M %p"),
                "kiosk": kiosk_code,
                "passenger": c.passenger_name or "",
                "duration": duration_str,
                "notes": c.operator_notes or "",
                "status": "RESOLVED",
                "categories": c.issue_category.split(", ") if c.issue_category else [],
                "recordingUrl": rec_url,
                "flightNo": c.flight_number or "",
                "operatorId": op_id_val,
                "operatorName": op_name,
                "operatorCode": op_code
            })

        return {"success": True, "count": len(logs), "data": logs}
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.post("/api/v1/operator/call/{call_id}/recording")
async def upload_call_recording(
    call_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Accepts WebM/MP4 media blob from frontend and attaches recording to SupportCall DB record.
    """
    if not call_id:
        raise HTTPException(status_code=400, detail="call_id parameter required")

    try:
        content_type = request.headers.get("content-type", "")
        file_bytes = b""
        filename = f"{call_id}.webm"

        if "multipart/form-data" in content_type:
            form = await request.form()
            upload_file = form.get("file") or form.get("recording") or form.get("video")
            if upload_file:
                file_bytes = await upload_file.read()
                if hasattr(upload_file, "filename") and upload_file.filename and upload_file.filename.endswith(".mp4"):
                    filename = f"{call_id}.mp4"
        else:
            file_bytes = await request.body()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty recording payload")

        rec_dir = get_recordings_dir()
        dest_path = os.path.join(rec_dir, filename)
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        rel_url = f"/recordings/{filename}"

        call = db.query(models.SupportCall).filter(models.SupportCall.id == call_id).first()
        if call:
            call.recording_url = rel_url
            db.commit()
        else:
            new_call = models.SupportCall(
                id=call_id,
                kiosk_id="T3-L1-K04",
                operator_id="op_101",
                status="ended",
                call_duration_seconds=1,
                issue_category="General Inquiry",
                operator_notes="Assisted passenger at kiosk.",
                passenger_name="",
                recording_url=rel_url
            )
            db.add(new_call)
            db.commit()

        return {
            "success": True,
            "message": "Recording uploaded and linked successfully",
            "callId": call_id,
            "recordingUrl": rel_url,
            "sizeBytes": len(file_bytes)
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading recording: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.get("/api/v1/operator/call/{call_id}/download-recording")
async def download_recording(call_id: str):
    """
    Streams call recording file for playback or download.
    """
    rec_dir = get_recordings_dir()
    filename = f"{call_id}.webm"
    file_path = os.path.join(rec_dir, filename)
    if not os.path.exists(file_path):
        filename = f"{call_id}.mp4"
        file_path = os.path.join(rec_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Recording file not found")

    return FileResponse(
        path=file_path,
        media_type="video/webm" if filename.endswith(".webm") else "video/mp4",
        filename=f"call_recording_{call_id}.webm",
        headers={"Content-Disposition": f'attachment; filename="call_recording_{call_id}.webm"'}
    )
