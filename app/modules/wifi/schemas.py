"""
Wi-Fi Guest Portal & Passport Scan Pydantic V2 Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BaseWifiSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class WifiOTPRequest(BaseWifiSchema):
    phone_number: str = Field(..., alias="phoneNumber", json_schema_extra={"example": "+91 98765 43210"})


class WifiOTPResponse(BaseWifiSchema):
    success: bool = True
    message: str = "OTP code generated"
    session_id: Optional[str] = Field(None, alias="sessionId")
    otp: Optional[str] = "123456"


class WifiVerifyOTPRequest(BaseWifiSchema):
    session_id: Optional[str] = Field(None, alias="sessionId")
    otp_code: Optional[str] = Field(None, alias="otpCode")
    otp: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias="phoneNumber")


class WifiVerifyOTPResponse(BaseWifiSchema):
    success: bool = True
    is_verified: bool = Field(True, alias="isVerified")
    voucher: str = Field(default="WIFI-AIRPORT-8891", alias="voucher")
    voucher_code: Optional[str] = Field(default="WIFI-AIRPORT-8891", alias="voucherCode")
    expires_in_minutes: int = Field(default=45, alias="expiresInMinutes")
    message: str = "Wi-Fi verification successful!"


class WifiPassportScanRequest(BaseWifiSchema):
    image_base64: Optional[str] = Field(None, alias="imageBase64")
    raw_mrz: Optional[str] = Field(None, alias="rawMrz")
    is_demo: Optional[bool] = Field(default=False, alias="isDemo")
    demo_type: Optional[str] = Field(default="valid", alias="demoType")
