"""
Support & Operator Call Domain Pydantic V2 Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CallRequestPayload(BaseModel):
    kiosk_id: str = Field(..., alias="kioskId", example="T3-L1-K04")
    ada_priority: bool = Field(default=False, alias="adaPriority")
    language: str = Field(default="EN")

    class Config:
        populate_by_name = True

class AcceptCallPayload(BaseModel):
    call_id: str = Field(..., alias="callId", example="call_12345678")
    operator_id: str = Field(..., alias="operatorId", example="op_101")

    class Config:
        populate_by_name = True

class OperatorLogSubmitPayload(BaseModel):
    session_id: Optional[str] = Field(None, alias="sessionId")
    kiosk_id: Optional[str] = Field(default="T3-L1-K04", alias="kioskId")
    duration: Optional[str] = "00:00"
    categories: Optional[List[str]] = []
    first_name: Optional[str] = Field(default="", alias="firstName")
    last_name: Optional[str] = Field(default="", alias="lastName")
    passenger_name: Optional[str] = Field(default="", alias="passengerName")
    operator_id: Optional[str] = Field(None, alias="operatorId")
    notes: Optional[str] = ""
    flight_no: Optional[str] = Field(default="", alias="flightNo")
    flight_number: Optional[str] = Field(default="", alias="flightNumber")
    pnr: Optional[str] = ""
    recording_url: Optional[str] = Field(None, alias="recordingUrl")

    class Config:
        populate_by_name = True
