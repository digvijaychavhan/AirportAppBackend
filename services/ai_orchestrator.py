"""
Legacy Re-Export Wrapper for AI Intent Orchestrator
"""

from app.modules.ai.service import (
    fallback_intent_parser,
    parse_ai_intent,
    process_ai_intent
)

__all__ = [
    "fallback_intent_parser",
    "parse_ai_intent",
    "process_ai_intent"
]
