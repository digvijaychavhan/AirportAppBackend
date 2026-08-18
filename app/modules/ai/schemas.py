"""
AI Intent Domain Pydantic V2 Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class IntentRequestPayload(BaseModel):
    transcript: str = Field(..., description="Passenger voice query transcript", example="Take me to Third Wave Coffee")
    kiosk_context: Optional[Dict[str, Any]] = Field(default=None, alias="kioskContext", description="Kiosk contextual state")

    class Config:
        populate_by_name = True

class IntentResponseData(BaseModel):
    action: str = Field(..., description="category_page | map | conversation")
    target_route: Optional[str] = Field(None, alias="targetRoute")
    stops: Optional[List[str]] = []
    mode: Optional[str] = "escalator"
    speech_response: str = Field(..., alias="speechResponse")

    class Config:
        populate_by_name = True
