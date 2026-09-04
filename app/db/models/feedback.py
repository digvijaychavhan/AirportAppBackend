"""
Passenger Feedback Survey ORM Models
"""

from sqlalchemy import Column, String, Integer, DateTime, Text
from app.core.database import Base
from app.db.base import generate_uuid, TimestampMixin
from app.core.timezone import get_current_time

class FeedbackSubmission(Base, TimestampMixin):
    __tablename__ = "feedback_submissions"

    id = Column(String, primary_key=True, default=generate_uuid)
    kiosk_id = Column(String, nullable=True)
    flight_number = Column(String, nullable=True)
    pnr = Column(String, nullable=True)
    overall_rating = Column(Integer, nullable=False)
    cleanliness_rating = Column(Integer, nullable=False)
    staff_rating = Column(Integer, nullable=False)
    wayfinding_rating = Column(Integer, nullable=False)
    wifi_rating = Column(Integer, nullable=False)
    food_rating = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    contact_phone = Column(String, nullable=True)



class FeedbackCategory(Base):
    __tablename__ = "feedback_categories"

    id = Column(String, primary_key=True)  # e.g. "cleanliness", "staff", "navigation"
    title = Column(String, nullable=True)
    label = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    description = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Integer, default=1)


