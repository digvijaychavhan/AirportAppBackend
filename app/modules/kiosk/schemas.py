"""
Kiosk Presence Domain Pydantic V2 Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class KioskHeartbeatPayload(BaseModel):
    kiosk_id: Optional[str] = Field("T3-L1-K04", alias="kioskId")
    page: Optional[str] = "/"

    class Config:
        populate_by_name = True
