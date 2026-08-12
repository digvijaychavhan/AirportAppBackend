"""
AI Intent Orchestrator REST Router
Extracts passenger intent and route directives from transcript using Groq LLM (llama-3.3-70b-versatile) & regex fallback.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from services.ai_orchestrator import process_ai_intent

router = APIRouter(prefix="/api/v1/ai", tags=["AI Intent Orchestrator"])


class IntentRequestPayload(BaseModel):
    transcript: str = Field(..., description="Passenger voice or typed query transcript", example="Take me to Third Wave Coffee")
    kioskContext: Optional[Dict[str, Any]] = Field(default=None, description="Contextual kiosk state metadata e.g. kioskId, floor")


@router.post("/intent")
async def extract_ai_intent(payload: IntentRequestPayload):
    """
    Processes passenger voice transcript via Groq LLM to determine target action, route, stops, and TTS speech response.
    """
    if not payload.transcript or not payload.transcript.strip():
        raise HTTPException(status_code=400, detail={"error": "EMPTY_TRANSCRIPT", "message": "Transcript text cannot be empty."})

    try:
        intent_result = await process_ai_intent(
            transcript=payload.transcript,
            kiosk_context=payload.kioskContext
        )
        return {
            "success": True,
            "data": intent_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "AI_INTENT_ERROR", "message": str(e)})
