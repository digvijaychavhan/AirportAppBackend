from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Base Config
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Airline Schemas
class AirlineBase(BaseSchema):
    code: str
    name: str
    logo_url: Optional[str] = None
    flight_type: str = "domestic"

class AirlineResponse(AirlineBase):
    pass


# Flight Schemas
class FlightBase(BaseSchema):
    flight_number: str
    airline_code: str
    origin_iata: str = "DEL"
    destination_iata: str
    destination_name: str
    scheduled_departure: datetime
    estimated_departure: Optional[datetime] = None
    terminal: str
    gate: str
    checkin_counters: str
    baggage_belt: str
    status: str = "On Time"

class FlightResponse(FlightBase):
    id: str
    airline: Optional[AirlineResponse] = None

class FlightSearchQuery(BaseModel):
    query: Optional[str] = None
    date: Optional[str] = None
    airline: Optional[str] = None
    terminal: Optional[str] = None


# BCBP Barcode Schemas
class BCBPDecodeRequest(BaseModel):
    raw_bcbp: str = Field(..., description="Raw 2D barcode string scanned from boarding pass")

class BCBPDecodeResponse(BaseModel):
    passenger_name: str
    pnr: str
    flight_number: str
    airline_code: str
    origin_iata: str
    destination_iata: str
    seat_number: Optional[str] = None
    departure_date_julian: Optional[str] = None
    matched_flight: Optional[FlightResponse] = None
    raw_decoded: dict = {}


# Kiosk Schemas
class KioskBase(BaseSchema):
    code: str
    terminal: str
    floor_id: str
    current_node_id: str
    is_accessible_ada: bool = True
    status: str = "active"

class KioskResponse(KioskBase):
    id: str
    last_heartbeat_at: Optional[datetime] = None


# Map & Spatial Schemas
class MapFloorResponse(BaseSchema):
    id: str
    building: str
    floor_level: int
    svg_asset_url: str

class MapNodeResponse(BaseSchema):
    id: str
    floor_id: str
    x_coord: float
    y_coord: float
    zone_name: str
    is_vertical_connector: bool
    connector_type: Optional[str] = None

class MapEdgeResponse(BaseSchema):
    id: str
    source_node_id: str
    target_node_id: str
    distance_meters: float
    is_accessible_elevator: bool
    is_escalator: bool


# POI Schemas
class PoiResponse(BaseSchema):
    id: str
    name: str
    category: str
    node_id: str
    floor_id: str
    operating_hours: str
    dietary_tags: Optional[str] = None
    rating: float
    image_url: Optional[str] = None


# Operator & Support Call Schemas
class OperatorResponse(BaseSchema):
    id: str
    employee_code: str
    name: str
    role: str
    status: str
    supported_languages: str

class SupportCallCreate(BaseModel):
    kiosk_id: str
    requested_language: str = "English"
    ada_priority: bool = False

class SupportCallResponse(BaseSchema):
    id: str
    kiosk_id: str
    operator_id: Optional[str] = None
    status: str
    ada_priority: bool
    requested_language: str
    wait_duration_seconds: int
    call_duration_seconds: int
    issue_category: Optional[str] = None
    operator_notes: Optional[str] = None
    created_at: datetime

class ScreenAnnotationCreate(BaseModel):
    call_id: str
    stroke_data: str

class ScreenAnnotationResponse(BaseSchema):
    id: str
    call_id: str
    stroke_data: str
    created_at: datetime


# Feedback Schemas
class FeedbackCreate(BaseModel):
    kiosk_id: Optional[str] = None
    flight_number: Optional[str] = None
    pnr: Optional[str] = None
    overall_rating: int = Field(..., ge=1, le=5)
    cleanliness_rating: int = Field(..., ge=1, le=5)
    staff_rating: int = Field(..., ge=1, le=5)
    wayfinding_rating: int = Field(..., ge=1, le=5)
    wifi_rating: int = Field(..., ge=1, le=5)
    food_rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    contact_phone: Optional[str] = None

class FeedbackResponse(BaseSchema):
    id: str
    kiosk_id: Optional[str] = None
    flight_number: Optional[str] = None
    pnr: Optional[str] = None
    overall_rating: int
    cleanliness_rating: int
    staff_rating: int
    wayfinding_rating: int
    wifi_rating: int
    food_rating: int
    comments: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime


# Wi-Fi Guest Portal Schemas
class WifiOTPRequest(BaseModel):
    phone_number: str = Field(..., min_length=8, max_length=15, description="Mobile number with country code")

class WifiOTPResponse(BaseModel):
    message: str
    session_id: str
    otp_code: Optional[str] = None  # Returned for developer convenience in dev mode

class WifiVerifyOTPRequest(BaseModel):
    session_id: str
    otp_code: str

class WifiVerifyOTPResponse(BaseModel):
    is_verified: bool
    voucher_code: str
    expires_at: datetime
    message: str


# Wi-Fi Passport Scanning Schemas
class WifiPassportScanRequest(BaseModel):
    image_base64: Optional[str] = Field(None, description="Base64 encoded JPEG/PNG of the passport photo page")
    raw_mrz: Optional[str] = Field(None, description="Optional raw 2-line MRZ string if scanned directly")
    is_demo: bool = Field(False, description="Whether this is a demo simulation scan")
    demo_type: str = Field("valid", description="'valid' | 'invalid' | 'driver_license' | 'selfie'")
    kiosk_id: Optional[str] = Field("T3-L1-K04", description="Kiosk terminal identifier")


class PassportDetails(BaseModel):
    document_type: str
    passenger_name: str
    passport_number: str
    issuing_country: str
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    sex: Optional[str] = None
    verification_method: Optional[str] = None


class WifiAccessDetails(BaseModel):
    ssid: str
    voucher_code: str
    wifi_password: str
    wifi_qr_string: str
    portal_connect_url: str
    duration_minutes: int
    expires_at: str
    security_type: str


class WifiPassportScanResponse(BaseModel):
    success: bool
    verified: bool
    message: str
    passport_details: Optional[PassportDetails] = None
    wifi_details: Optional[WifiAccessDetails] = None
    error_code: Optional[str] = None
    details: Optional[str] = None
    extracted_raw_text: Optional[str] = None
    parsed_line1: Optional[str] = None
    parsed_line2: Optional[str] = None
    checksum_status: Optional[Dict[str, Any]] = None
    diagnostics: Optional[List[str]] = None


