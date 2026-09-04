"""
AI Intent Domain Pydantic V2 Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BaseAiSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class IntentRequestPayload(BaseAiSchema):
    transcript: str = Field(..., description="Passenger voice query transcript", json_schema_extra={"example": "Take me to Third Wave Coffee"})
    kiosk_context: Optional[Dict[str, Any]] = Field(default=None, alias="kioskContext", description="Kiosk contextual state")


class IntentResponseData(BaseAiSchema):
    action: str = Field(..., description="category_page | map | conversation")
    target_route: Optional[str] = Field(None, alias="targetRoute")
    stops: Optional[List[str]] = []
    mode: Optional[str] = "escalator"
    speech_response: str = Field(..., alias="speechResponse")
