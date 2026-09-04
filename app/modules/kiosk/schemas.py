"""
Kiosk Presence Domain Pydantic V2 Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BaseKioskSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class KioskHeartbeatPayload(BaseKioskSchema):
    kiosk_id: Optional[str] = Field("T3-L1-K04", alias="kioskId")
    page: Optional[str] = "/"


class KioskClaimPayload(BaseKioskSchema):
    preferred_kiosk_id: Optional[str] = Field(None, alias="preferredKioskId")
    client_session_id: Optional[str] = Field(None, alias="clientSessionId")
    runtime_env: Optional[str] = Field(None, alias="runtimeEnv")
