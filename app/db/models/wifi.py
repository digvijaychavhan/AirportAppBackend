"""
Wi-Fi Guest Portal Sessions ORM Models
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from app.core.database import Base
from app.db.base import generate_uuid

class WifiSession(Base):
    __tablename__ = "wifi_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    phone_number = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    voucher_code = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
