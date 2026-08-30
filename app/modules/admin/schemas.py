"""
Admin Portal Domain Pydantic V2 Schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class OperatorLoginPayload(BaseModel):
    username: Optional[str] = None
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    password: str

    class Config:
        populate_by_name = True

class OperatorCreatePayload(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    name: str
    password: Optional[str] = "operator123"
    role: Optional[str] = "Customer Support Executive"
    status: Optional[str] = "available"
    supported_languages: Optional[str] = Field("English, Hindi", alias="supportedLanguages")
    shift: Optional[str] = "Morning (06:00 - 14:00)"

    class Config:
        populate_by_name = True

class OperatorStatusPayload(BaseModel):
    status: str

class OperatorPasswordPayload(BaseModel):
    password: str

class DevicePayload(BaseModel):
    id: Optional[str] = None
    device_id: Optional[str] = Field(None, alias="deviceId")
    name: str
    device_type: Optional[str] = Field("kiosk", alias="deviceType")
    ip_address: Optional[str] = Field("192.168.1.100", alias="ipAddress")
    mac_address: Optional[str] = Field("00:1A:2B:3C:4D:00", alias="macAddress")
    terminal: Optional[str] = "Terminal 3"
    floor_name: Optional[str] = Field("Level 1", alias="floorName")
    location: Optional[str] = "Central Concourse"
    status: Optional[str] = "online"

    class Config:
        populate_by_name = True

class ScanLogCreatePayload(BaseModel):
    kiosk_id: Optional[str] = Field("T3-L1-K04", alias="kioskId")
    passenger_name: Optional[str] = Field(None, alias="passengerName")
    flight_number: Optional[str] = Field(None, alias="flightNumber")
    pnr: Optional[str] = None
    seat: Optional[str] = None
    barcode_format: Optional[str] = Field("PDF417_BCBP", alias="barcodeFormat")
    scan_result: Optional[str] = Field("SUCCESS", alias="scanResult")
    failure_reason: Optional[str] = Field(None, alias="failureReason")
    raw_data: Optional[str] = Field(None, alias="rawData")

    class Config:
        populate_by_name = True

class UserActionLogCreatePayload(BaseModel):
    kiosk_id: Optional[str] = Field("T3-L1-K04", alias="kioskId")
    username: Optional[str] = None  # Logged-in passenger name / username; None for Guest
    session_id: Optional[str] = Field(None, alias="sessionId")
    action_type: str = Field("CLICK", alias="actionType")  # CLICK, PAGE_VIEW, SCAN, SEARCH, NAVIGATION
    target_element: Optional[str] = Field(None, alias="targetElement")
    route: Optional[str] = None
    details: Optional[str] = None
    metadata_json: Optional[Any] = Field(None, alias="metadata")
    ip_address: Optional[str] = Field(None, alias="ipAddress")
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    class Config:
        populate_by_name = True

class BatchUserActionsPayload(BaseModel):
    kiosk_id: Optional[str] = Field("T3-L1-K04", alias="kioskId")
    actions: List[UserActionLogCreatePayload] = []

    class Config:
        populate_by_name = True

class KioskTelemetryHeartbeatPayload(BaseModel):
    kiosk_id: str = Field("T3-L1-K04", alias="kioskId")
    scanner_connected: bool = Field(True, alias="scannerConnected")
    scanner_working: str = Field("OK", alias="scannerWorking")  # OK, ERROR, DISCONNECTED
    camera_connected: bool = Field(True, alias="cameraConnected")
    camera_working: str = Field("OK", alias="cameraWorking")  # OK, ERROR, DISCONNECTED
    network_bandwidth_mbps: float = Field(100.0, alias="networkBandwidthMbps")
    cpu_pct: float = Field(18.0, alias="cpuPct")
    ram_used_mb: float = Field(2048.0, alias="ramUsedMb")
    ram_total_mb: float = Field(8192.0, alias="ramTotalMb")
    ram_pct: float = Field(25.0, alias="ramPct")
    ping_ms: Optional[int] = Field(12, alias="pingMs")
    ip_address: Optional[str] = Field(None, alias="ipAddress")
    status: Optional[str] = "online"

    class Config:
        populate_by_name = True

class AmenityPayload(BaseModel):
    id: Optional[str] = None
    name: str
    category: str
    sub_category: Optional[str] = Field(None, alias="subCategory")
    description: Optional[str] = None
    terminal: Optional[str] = "Terminal 3"
    floor_name: Optional[str] = Field("Level 1", alias="floorName")
    gate: Optional[str] = None
    operating_hours: Optional[str] = Field("24/7", alias="operatingHours")
    image_url: Optional[str] = Field(None, alias="imageUrl")
    badge_label: Optional[str] = Field(None, alias="badgeLabel")
    badge_variant: Optional[str] = Field("purple", alias="badgeVariant")
    x: Optional[float] = None
    y: Optional[float] = None
    x_coord: Optional[float] = Field(None, alias="xCoord")
    y_coord: Optional[float] = Field(None, alias="yCoord")
    is_active: Optional[bool] = Field(True, alias="isActive")

    class Config:
        populate_by_name = True

class CategoryPayload(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    photo_url: Optional[str] = Field(None, alias="photoUrl")
    icon: Optional[str] = "place"
    icon_color: Optional[str] = Field("#2563EB", alias="iconColor")
    icon_bg: Optional[str] = Field("#DBEAFE", alias="iconBg")
    route: str
    subcategories: Optional[List[Dict[str, Any]]] = None
    subcategories_json: Optional[str] = Field(None, alias="subcategoriesJson")
    is_active: Optional[bool] = Field(True, alias="isActive")

    class Config:
        populate_by_name = True
