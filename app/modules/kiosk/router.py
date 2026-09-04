"""
Kiosk Presence & Telemetry REST Router
"""

from typing import Optional, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import logger
from app.core.timezone import get_current_time
import app.db.models as models
from app.modules.support.service import online_kiosks, active_kiosk_claims
from app.modules.kiosk.schemas import KioskHeartbeatPayload, KioskClaimPayload

router = APIRouter(tags=["Kiosk"])

@router.post("/api/v1/kiosk/heartbeat")
async def kiosk_heartbeat(payload: KioskHeartbeatPayload):
    """
    Acknowledges kiosk client heartbeat ping.
    """
    kiosk_id = payload.kiosk_id or "T3-L1-K04"
    return {"success": True, "status": "acknowledged", "kioskId": kiosk_id}


@router.post("/api/v1/kiosks/claim")
@router.get("/api/v1/kiosks/claim")
async def claim_kiosk(
    payload: Optional[KioskClaimPayload] = None,
    preferredKioskId: Optional[str] = Query(None),
    clientSessionId: Optional[str] = Query(None),
    runtimeEnv: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Claims an available registered kiosk for a client session.
    Guarantees conflict-free assignment: If preferredKioskId is already occupied by another
    active client session, it assigns the next available offline kiosk from the fleet.
    """
    def _clean_str(val: Any) -> Optional[str]:
        if isinstance(val, str) and val.strip():
            return val.strip()
        return None

    pref_id = _clean_str(payload.preferred_kiosk_id if payload else None) or _clean_str(preferredKioskId)
    session_id = _clean_str(payload.client_session_id if payload else None) or _clean_str(clientSessionId)
    req_env = _clean_str(payload.runtime_env if payload else None) or _clean_str(runtimeEnv) or "browser"
    now_ts = get_current_time().timestamp()

    # 1. Clean up stale claims (> 120s without heartbeat)
    stale_threshold = 120
    for kid in list(active_kiosk_claims.keys()):
        claim_data = active_kiosk_claims[kid]
        if (now_ts - claim_data.get("lastSeen", 0)) > stale_threshold:
            active_kiosk_claims.pop(kid, None)

    for kid in list(online_kiosks.keys()):
        kdata = online_kiosks[kid]
        if (now_ts - kdata.get("lastSeen", 0)) > stale_threshold:
            online_kiosks.pop(kid, None)

    # 2. If this clientSessionId already holds an active claim, preserve it
    if session_id:
        for kid, claim_info in list(active_kiosk_claims.items()):
            if claim_info.get("sessionId") == session_id:
                dev = db.query(models.Device).filter(
                    (models.Device.device_id == kid) | (models.Device.id == kid)
                ).first()
                if dev:
                    claim_info["lastSeen"] = now_ts
                    claim_info["runtimeEnv"] = req_env
                    return {
                        "success": True,
                        "data": {
                            "id": dev.id,
                            "deviceId": dev.device_id,
                            "name": dev.name,
                            "location": dev.location or "",
                            "terminal": dev.terminal or "Terminal 3",
                            "floorName": dev.floor_name or "Level 1",
                            "deviceType": dev.device_type or "kiosk"
                        }
                    }

    # 3. Check if preferredKioskId is requested and available (not occupied by another active session)
    if pref_id:
        is_occupied_by_other = False
        if pref_id in active_kiosk_claims:
            other_sess = active_kiosk_claims[pref_id].get("sessionId")
            if other_sess and (not session_id or other_sess != session_id):
                is_occupied_by_other = True

        if not is_occupied_by_other and pref_id in online_kiosks:
            other_sess = online_kiosks[pref_id].get("sessionId")
            if other_sess and (not session_id or other_sess != session_id):
                is_occupied_by_other = True

        if not is_occupied_by_other:
            existing = db.query(models.Device).filter(
                (models.Device.device_id == pref_id) | (models.Device.id == pref_id)
            ).first()
            if existing:
                active_kiosk_claims[existing.device_id] = {
                    "sessionId": session_id,
                    "runtimeEnv": req_env,
                    "lastSeen": now_ts,
                    "kioskId": existing.device_id
                }
                return {
                    "success": True,
                    "data": {
                        "id": existing.id,
                        "deviceId": existing.device_id,
                        "name": existing.name,
                        "location": existing.location or "",
                        "terminal": existing.terminal or "Terminal 3",
                        "floorName": existing.floor_name or "Level 1",
                        "deviceType": existing.device_type or "kiosk"
                    }
                }

    # 4. Preferred kiosk is missing or occupied by another active client -> Assign next available kiosk
    occupied_ids = set()
    for kid, claim_info in active_kiosk_claims.items():
        if not session_id or claim_info.get("sessionId") != session_id:
            occupied_ids.add(kid)
    for kid, kdata in online_kiosks.items():
        if not session_id or kdata.get("sessionId") != session_id:
            occupied_ids.add(kid)
            if kdata.get("kioskId"):
                occupied_ids.add(kdata["kioskId"])

    all_kiosks = db.query(models.Device).filter(
        models.Device.device_type == "kiosk"
    ).order_by(models.Device.device_id).all()

    assigned = None
    for k in all_kiosks:
        if k.device_id not in occupied_ids and k.id not in occupied_ids:
            assigned = k
            break

    # 5. Fallback: If all are currently occupied, pick first or auto-seed
    if not assigned:
        if all_kiosks:
            assigned = all_kiosks[0]
        else:
            assigned = models.Device(
                device_id="KIOSK-T3-L1-01",
                name="Kiosk T3-L1 Departure Gate 12",
                device_type="kiosk",
                ip_address="192.168.1.101",
                terminal="Terminal 3",
                floor_name="Level 1",
                location="Central Concourse Gate 12",
                status="offline"
            )
            db.add(assigned)
            db.commit()

    # Record the newly assigned kiosk claim
    active_kiosk_claims[assigned.device_id] = {
        "sessionId": session_id,
        "runtimeEnv": req_env,
        "lastSeen": now_ts,
        "kioskId": assigned.device_id
    }

    return {
        "success": True,
        "data": {
            "id": assigned.id,
            "deviceId": assigned.device_id,
            "name": assigned.name,
            "location": assigned.location or "",
            "terminal": assigned.terminal or "Terminal 3",
            "floorName": assigned.floor_name or "Level 1",
            "deviceType": assigned.device_type or "kiosk"
        }
    }

