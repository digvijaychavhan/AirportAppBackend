"""
Groq AI Intent Orchestrator Service
Parses spoken transcripts into structured UI actions using Groq LLM (llama-3.3-70b-versatile) with heuristic regex fallback.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
from app.core.logging import logger
from app.core.config import settings

def fallback_intent_parser(transcript: str, kiosk_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    t_lower = transcript.strip().lower()
    mode = "elevator" if any(w in t_lower for w in ["wheelchair", "elevator", "lift", "accessible", "handicap"]) else "escalator"

    pname = (kiosk_context or {}).get("passenger_name") or (kiosk_context or {}).get("passengerName")
    fnum = (kiosk_context or {}).get("flight_number") or (kiosk_context or {}).get("flightNumber") or "6E 2262"
    gate = (kiosk_context or {}).get("gate") or "Gate B12"
    seat = (kiosk_context or {}).get("seat") or (kiosk_context or {}).get("seatNumber") or "20B"
    dest = (kiosk_context or {}).get("destinationName") or (kiosk_context or {}).get("destination") or "Pune"

    if any(w in t_lower for w in ["my flight", "flight status", "gate", "where is my gate", "my seat", "boarding", "departure"]):
        greeting = f"Hello {pname}! " if pname else ""
        resp = f"{greeting}Your flight {fnum} to {dest} is on time. Gate is {gate} and your assigned seat is {seat}."
        return {
            "action": "map" if any(w in t_lower for w in ["gate", "where", "direction", "way"]) else "category_page",
            "targetRoute": None if any(w in t_lower for w in ["gate", "where", "direction", "way"]) else "/flights",
            "stops": [gate] if any(w in t_lower for w in ["gate", "where", "direction", "way"]) else [],
            "mode": mode,
            "speechResponse": resp
        }

    greetings = ["hi", "hello", "hey", "who are you", "what is your name", "i am ", "my name is", "how are you"]
    if any(t_lower.startswith(g) or g in t_lower for g in greetings) and not any(k in t_lower for k in ["where", "take me", "show", "way to", "direction", "buy", "eat"]):
        name_match = re.search(r"(?:i am|my name is)\s+([a-zA-Z]+)", t_lower)
        user_name = name_match.group(1).capitalize() if name_match else pname
        greeting_text = f"Hello {user_name}! I am Aero AI, your airport digital assistant at Terminal 3. How can I help your journey today?" if user_name else "Hello! I am Aero AI, your airport digital helpdesk assistant. How can I assist you today?"
        return {
            "action": "conversation",
            "targetRoute": None,
            "stops": [],
            "mode": mode,
            "speechResponse": greeting_text
        }

    if any(w in t_lower for w in ["all restaurant", "restaurants", "food court", "eat and dine", "places to eat", "where to eat", "dine"]):
        return {
            "action": "category_page",
            "targetRoute": "/eat-dine",
            "stops": [],
            "mode": mode,
            "speechResponse": "Navigating to our Eat & Dine directory for restaurants and cafes."
        }

    if any(w in t_lower for w in ["shopping stores", "shopping directory", "all shops", "stores page", "retail stores"]):
        return {
            "action": "category_page",
            "targetRoute": "/wayfinding/shopping",
            "stops": [],
            "mode": mode,
            "speechResponse": "Opening our airport shopping directory."
        }

    if any(w in t_lower for w in ["lounge page", "all lounges", "show lounges", "vip lounges"]):
        return {
            "action": "category_page",
            "targetRoute": "/wayfinding/lounges",
            "stops": [],
            "mode": mode,
            "speechResponse": "Showing available airport lounges."
        }

    if any(w in t_lower for w in ["flight schedule", "all flights", "departures", "arrivals", "boarding gate"]):
        return {
            "action": "category_page",
            "targetRoute": "/flights",
            "stops": ["Gate B12"],
            "mode": mode,
            "speechResponse": "Opening flight departure details and gate status."
        }

    if any(w in t_lower for w in ["wifi", "internet"]):
        return {
            "action": "category_page",
            "targetRoute": "/wifi",
            "stops": [],
            "mode": mode,
            "speechResponse": "Navigating to Airport Free Wi-Fi OTP portal."
        }

    poi_keywords = [
        (r"medicine|pharmacy|medical|doctor", "Medical Centre"),
        (r"coffee|third wave", "Third Wave Coffee"),
        (r"apple|airpods|imagine|iphone", "Imagine Store"),
        (r"book|relay|crossword|magazine", "Relay Books"),
        (r"mcdonald|burger", "McDonald's"),
        (r"duty free|perfume|liquor", "Duty Free"),
        (r"encalm|lounge", "Encalm Lounge"),
        (r"subway|sandwich", "Subway"),
        (r"baggage|lost property", "Baggage Services"),
        (r"gate\s*b?12", "Gate B12"),
    ]

    detected_stops: List[str] = []
    for pattern, poi_name in poi_keywords:
        if re.search(pattern, t_lower):
            if poi_name not in detected_stops:
                detected_stops.append(poi_name)

    if detected_stops:
        stops_str = " and then ".join(detected_stops)
        return {
            "action": "map",
            "targetRoute": None,
            "stops": detected_stops,
            "mode": mode,
            "speechResponse": f"I have mapped your route to {stops_str}. Follow the map guidance on screen."
        }

    return {
        "action": "conversation",
        "targetRoute": None,
        "stops": [],
        "mode": mode,
        "speechResponse": f"Hello! I understood '{transcript}'. How can I assist your journey at Terminal 3 today?"
    }


async def parse_ai_intent(transcript: str, kiosk_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    groq_api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")

    # Retrieve live POIs from database to inject into system prompt
    poi_names_str = "Medical Centre, Third Wave Coffee, McDonald's, Relay Books, Duty Free, Encalm Lounge, Gate B12, Gate 24, Restrooms, Baggage Claim"
    try:
        from app.core.database import SessionLocal
        import app.db.models as models
        db = SessionLocal()
        pois = db.query(models.Poi).filter(models.Poi.is_active == True).all()
        if pois:
            poi_names_str = ", ".join([p.name for p in pois[:30]])
        db.close()
    except Exception as dbe:
        logger.warning(f"Could not load POIs for AI prompt context: {dbe}")

    system_prompt = (
        "You are Aero AI, the AI Intent Parser for an Airport Digital Kiosk at Terminal 3. "
        f"Known active airport locations and services: [{poi_names_str}]. "
        "Convert the user's request into a strict JSON object with fields:\n"
        "- 'action': 'category_page' | 'map' | 'conversation'\n"
        "- 'targetRoute': string or null (e.g. '/eat-dine', '/wayfinding/shopping', '/wayfinding/lounges', '/flights', '/wifi', '/feedback')\n"
        "- 'stops': list of location names from known locations (e.g. ['Medical Centre', 'Third Wave Coffee', 'Gate B12'])\n"
        "- 'mode': 'elevator' | 'escalator'\n"
        "- 'speechResponse': polite concise response text for passenger\n"
        "Return ONLY the JSON object, no commentary."
    )

    if not groq_api_key:
        return fallback_intent_parser(transcript, kiosk_context)

    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Transcript: '{transcript}'. Context: {json.dumps(kiosk_context or {})}"}
            ],
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"}
        )

        result_text = completion.choices[0].message.content
        return json.loads(result_text)
    except Exception as e:
        logger.warning(f"Groq API call fallback: {e}")
        return fallback_intent_parser(transcript, kiosk_context)

process_ai_intent = parse_ai_intent
