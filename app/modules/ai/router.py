"""
AI Intent Orchestrator REST Router
"""

from fastapi import APIRouter, HTTPException, status
from app.modules.ai.schemas import IntentRequestPayload
from app.modules.ai.service import process_ai_intent

router = APIRouter(tags=["AI Intent Orchestrator"])

@router.post("/api/v1/ai/intent")
async def extract_ai_intent(payload: IntentRequestPayload):
    """
    Processes passenger voice transcript via Groq LLM to determine target action, route, stops, and TTS speech response.
    """
    if not payload.transcript or not payload.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "EMPTY_TRANSCRIPT", "message": "Transcript text cannot be empty."}
        )

    try:
        intent_result = await process_ai_intent(
            transcript=payload.transcript,
            kiosk_context=payload.kiosk_context
        )
        return {
            "success": True,
            "data": intent_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "AI_INTENT_ERROR", "message": str(e)}
        )
