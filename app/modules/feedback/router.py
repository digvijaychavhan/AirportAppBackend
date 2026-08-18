"""
Passenger Feedback Survey REST Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import logger
import app.db.models as models
from app.modules.feedback.schemas import FeedbackCreate

router = APIRouter(tags=["Feedback"])

@router.post("/api/v1/feedback/submit", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submit passenger feedback survey response.
    """
    try:
        ratings = payload.ratings or {}
        cleanliness = ratings.get("cleanliness", payload.cleanliness_rating or 5)
        staff = ratings.get("staff", payload.staff_rating or 5)
        wayfinding = ratings.get("navigation", ratings.get("wayfinding", payload.wayfinding_rating or 5))
        wifi = ratings.get("facilities", ratings.get("wifi", payload.wifi_rating or 5))
        food = ratings.get("facilities", ratings.get("food", payload.food_rating or 5))
        overall = ratings.get("overall", payload.overall_rating or 5)

        feedback_obj = models.FeedbackSubmission(
            kiosk_id=payload.kiosk_id or "T3-L1-K04",
            flight_number=payload.flight_number,
            pnr=payload.pnr,
            overall_rating=overall,
            cleanliness_rating=cleanliness,
            staff_rating=staff,
            wayfinding_rating=wayfinding,
            wifi_rating=wifi,
            food_rating=food,
            comments=payload.comments,
            contact_phone=payload.contact_phone
        )

        db.add(feedback_obj)
        db.commit()
        db.refresh(feedback_obj)

        return {"success": True, "message": "Feedback submitted successfully", "id": feedback_obj.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"Failed to submit feedback: {str(e)}"}
        )
