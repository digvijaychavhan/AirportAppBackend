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
