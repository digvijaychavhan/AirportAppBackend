from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/v1/feedback", tags=["Feedback"])

@router.post("/submit", response_model=schemas.FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_in: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submit passenger feedback rating & survey data from kiosk or web portal.
    """
    try:
        feedback_obj = models.FeedbackSubmission(
            kiosk_id=feedback_in.kiosk_id,
            flight_number=feedback_in.flight_number,
            pnr=feedback_in.pnr,
            overall_rating=feedback_in.overall_rating,
            cleanliness_rating=feedback_in.cleanliness_rating,
            staff_rating=feedback_in.staff_rating,
            wayfinding_rating=feedback_in.wayfinding_rating,
            wifi_rating=feedback_in.wifi_rating,
            food_rating=feedback_in.food_rating,
            comments=feedback_in.comments,
            contact_phone=feedback_in.contact_phone
        )

        db.add(feedback_obj)
        db.commit()
        db.refresh(feedback_obj)

        return feedback_obj
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )
