"""
Feedback Domain Pydantic V2 Schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class FeedbackCreate(BaseModel):
    ratings: Optional[Dict[str, int]] = {}
    kiosk_id: Optional[str] = Field("T3-L1-K04", alias="kioskId")
    flight_number: Optional[str] = Field(None, alias="flightNumber")
    pnr: Optional[str] = None
    overall_rating: Optional[int] = Field(5, alias="overallRating")
    cleanliness_rating: Optional[int] = Field(5, alias="cleanlinessRating")
    staff_rating: Optional[int] = Field(5, alias="staffRating")
    wayfinding_rating: Optional[int] = Field(5, alias="wayfindingRating")
    wifi_rating: Optional[int] = Field(5, alias="wifiRating")
    food_rating: Optional[int] = Field(5, alias="foodRating")
    comments: Optional[str] = ""
    contact_phone: Optional[str] = Field(None, alias="contactPhone")

    class Config:
        populate_by_name = True
