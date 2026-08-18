"""
Kiosk Presence & Telemetry REST Router
"""

from fastapi import APIRouter
from app.modules.kiosk.schemas import KioskHeartbeatPayload

router = APIRouter(tags=["Kiosk"])

@router.post("/api/v1/kiosk/heartbeat")
async def kiosk_heartbeat(payload: KioskHeartbeatPayload):
    """
    Acknowledges kiosk client heartbeat ping.
    """
    kiosk_id = payload.kiosk_id or "T3-L1-K04"
    return {"success": True, "status": "acknowledged", "kioskId": kiosk_id}
