"""
Flights Domain Pydantic V2 Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class AirlineSchema(BaseModel):
    code: str
    name: str
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    flight_type: Optional[str] = Field(default="domestic", alias="flightType")

    class Config:
        populate_by_name = True
        from_attributes = True

class FlightResponse(BaseModel):
    id: str
    flight_number: str = Field(..., alias="flightNumber")
    airline_code: str = Field(..., alias="airlineCode")
    airline: Optional[AirlineSchema] = None
    origin_iata: str = Field(..., alias="origin")
    destination_iata: str = Field(..., alias="destination")
    destination_name: str = Field(..., alias="destinationName")
    scheduled_departure: datetime = Field(..., alias="scheduledDeparture")
    estimated_departure: Optional[datetime] = Field(None, alias="estimatedDeparture")
    terminal: str
    gate: str
    checkin_counters: str = Field(..., alias="checkinCounters")
    baggage_belt: str = Field(..., alias="baggageBelt")
    status: str
    delay_reason: Optional[str] = Field(None, alias="delayReason")

    class Config:
        populate_by_name = True
        from_attributes = True

class BCBPDecodeRequest(BaseModel):
    raw_bcbp: Optional[str] = Field(None, alias="rawBarcode", description="IATA BCBP raw barcode string (PDF417 / Aztec)")
    barcode: Optional[str] = None
    kiosk_id: Optional[str] = Field(default="T3-L1-K04", alias="kioskId")

    class Config:
        populate_by_name = True

class BCBPDecodeData(BaseModel):
    passenger_name: str = Field(..., alias="passengerName")
    pnr: str
    flight_number: str = Field(..., alias="flightNumber")
    airline: Optional[Dict[str, Any]] = None
    origin: str
    origin_city: Optional[str] = Field(default="Delhi", alias="originCity")
    destination: str
    destination_name: str = Field(..., alias="destinationName")
    seat_number: Optional[str] = Field(None, alias="seatNumber")
    cabin_class: Optional[str] = Field(default="Economy (Y)", alias="cabinClass")
    scheduled_departure: Optional[str] = Field(default="2026-08-17T11:45:00Z", alias="scheduledDeparture")
    estimated_departure: Optional[str] = Field(default="2026-08-17T11:45:00Z", alias="estimatedDeparture")
    terminal: str
    gate: str
    checkin_counters: Optional[str] = Field(default="45 – 52", alias="checkinCounters")
    baggage_belt: Optional[str] = Field(default="Carousel 4", alias="baggageBelt")
    status: str = "ON TIME"
    raw_barcode: Optional[str] = Field(None, alias="rawBarcode")

    class Config:
        populate_by_name = True

class BCBPDecodeResponse(BaseModel):
    success: bool = True
    data: BCBPDecodeData

class BaggageBeltResponse(BaseModel):
    id: str
    carousel: str
    flightNumber: str
    airline: str
    origin: str
    status: str
    location: str

class ShuttleScheduleResponse(BaseModel):
    id: str
    route: str
    frequencyMinutes: int
    nextDeparture: str
    location: str
