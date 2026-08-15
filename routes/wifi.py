import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/v1/wifi", tags=["Wi-Fi Guest Portal"])

def generate_random_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))

def generate_voucher_code(prefix: str = "FLYER-WIFI") -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"

@router.post("/request-otp", response_model=schemas.WifiOTPResponse)
def request_wifi_otp(
    payload: schemas.WifiOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Request a high-speed airport Wi-Fi access OTP for a passenger's mobile phone number.
    """
    phone_clean = payload.phone_number.strip()
    if not phone_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number cannot be empty"
        )

    # Generate 6-digit OTP code (default to '123456' or random for developer convenience)
    otp_code = generate_random_otp(6)
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    try:
        session_obj = models.WifiSession(
            phone_number=phone_clean,
            otp_code=otp_code,
            is_verified=False,
            expires_at=expires_at
        )

        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)

        return schemas.WifiOTPResponse(
            message="OTP code generated and sent to mobile device",
            session_id=session_obj.id,
            otp_code=otp_code
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to issue OTP: {str(e)}"
        )


@router.post("/verify-otp", response_model=schemas.WifiVerifyOTPResponse)
def verify_wifi_otp(
    payload: schemas.WifiVerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify passenger OTP code and issue high-speed Wi-Fi session voucher token.
    """
    session_obj = (
        db.query(models.WifiSession)
        .filter(models.WifiSession.id == payload.session_id)
        .first()
    )

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired Wi-Fi session"
        )

    if session_obj.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code has expired. Please request a new code."
        )

    if session_obj.otp_code.strip() != payload.otp_code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP verification code"
        )

    try:
        voucher_code = generate_voucher_code()
        session_obj.is_verified = True
        session_obj.voucher_code = voucher_code

        db.commit()
        db.refresh(session_obj)

        return schemas.WifiVerifyOTPResponse(
            is_verified=True,
            voucher_code=voucher_code,
            expires_at=session_obj.expires_at,
            message="Wi-Fi verification successful! Connected to FLYER_HIGH_SPEED_GUEST."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete Wi-Fi verification: {str(e)}"
        )


@router.post("/scan-passport", response_model=schemas.WifiPassportScanResponse)
async def scan_passport_for_wifi(
    payload: schemas.WifiPassportScanRequest,
    db: Session = Depends(get_db)
):
    """
    Scans, verifies passport authenticity (MRZ & Vision AI), and returns Wi-Fi QR Code credentials.
    Rejects non-passport documents.
    """
    from services.passport_verifier import verify_passport_image, generate_wifi_qr_payload

    # Run verification pipeline
    is_valid, passport_data, error_reason = await verify_passport_image(
        image_base64=payload.image_base64,
        raw_mrz=payload.raw_mrz,
        is_demo=payload.is_demo,
        demo_type=payload.demo_type
    )

    if not is_valid or not passport_data:
        return schemas.WifiPassportScanResponse(
            success=False,
            verified=False,
            message="Passport verification failed.",
            error_code="INVALID_PASSPORT",
            details=error_reason or "Scanned document is not a valid passport photo page.",
            extracted_raw_text=passport_data.get("extracted_raw_text") if passport_data else payload.raw_mrz,
            parsed_line1=passport_data.get("parsed_line1") if passport_data else None,
            parsed_line2=passport_data.get("parsed_line2") if passport_data else None,
            checksum_status=passport_data.get("checksum_status") if passport_data else None,
            diagnostics=passport_data.get("diagnostics") if passport_data else None
        )

    # Generate Wi-Fi voucher & QR code credentials
    passenger_name = passport_data.get("passenger_name", "INTERNATIONAL TRAVELER")
    passport_num = passport_data.get("passport_number", "P1234567")
    wifi_data = generate_wifi_qr_payload(
        passenger_name=passenger_name,
        passport_number=passport_num,
        ssid="GMR Free Wi-Fi",
        duration_minutes=45
    )

    # Persist session to database
    try:
        session_obj = models.WifiSession(
            phone_number=f"PASS:{passport_num}",
            otp_code="PASSPORT_VERIFIED",
            is_verified=True,
            voucher_code=wifi_data["voucher_code"],
            expires_at=datetime.utcnow() + timedelta(minutes=45)
        )
        db.add(session_obj)
        db.commit()
    except Exception as e:
        db.rollback()
        # Session logging is best effort

    return schemas.WifiPassportScanResponse(
        success=True,
        verified=True,
        message="Passport successfully verified! Scan the QR code below on your mobile device to connect.",
        passport_details=schemas.PassportDetails(
            document_type=passport_data.get("document_type", "P (Passport)"),
            passenger_name=passenger_name,
            passport_number=passport_num,
            issuing_country=passport_data.get("issuing_country", "IND"),
            nationality=passport_data.get("nationality", "IND"),
            date_of_birth=passport_data.get("date_of_birth"),
            sex=passport_data.get("sex"),
            verification_method=passport_data.get("verification_method")
        ),
        wifi_details=schemas.WifiAccessDetails(
            ssid=wifi_data["ssid"],
            voucher_code=wifi_data["voucher_code"],
            wifi_password=wifi_data["wifi_password"],
            wifi_qr_string=wifi_data["wifi_qr_string"],
            portal_connect_url=wifi_data["portal_connect_url"],
            duration_minutes=wifi_data["duration_minutes"],
            expires_at=wifi_data["expires_at"],
            security_type=wifi_data["security_type"]
        ),
        extracted_raw_text=passport_data.get("extracted_raw_text") or payload.raw_mrz,
        parsed_line1=passport_data.get("parsed_line1"),
        parsed_line2=passport_data.get("parsed_line2"),
        checksum_status=passport_data.get("checksum_status"),
        diagnostics=passport_data.get("diagnostics")
    )

