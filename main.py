"""
Main Python ASGI Server Application
Built on Starlette & Socket.IO for maximum execution speed and zero build bottlenecks
"""

import json
import logging
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import socketio

from services.webrtc_signaling import sio
from services.pathfinding import compute_indoor_route
from services.ai_orchestrator import parse_ai_intent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")


# --- REST API Handlers ---

async def health_check(request):
    return JSONResponse({
        "status": "online",
        "service": "Airport Digital Helpdesk Python Backend",
        "version": "1.0.0"
    })

async def search_flights(request):
    query = request.query_params.get("query", "6E203")
    sample_flights = [
        {
            "id": "fl_6e203",
            "flightNumber": "6E 203",
            "airline": {"code": "6E", "name": "IndiGo", "logoUrl": "/logos/indigo.png"},
            "origin": "DEL",
            "destination": "MAA",
            "destinationName": "Chennai",
            "scheduledDeparture": "2026-08-12T10:45:00Z",
            "estimatedDeparture": "2026-08-12T11:45:00Z",
            "terminal": "T2",
            "gate": "B12",
            "checkinCounters": "45 – 52",
            "baggageBelt": "Carousel 4",
            "status": "DELAYED",
            "delayReason": "Late arrival of incoming aircraft from Chennai"
        },
        {
            "id": "fl_ai101",
            "flightNumber": "AI 101",
            "airline": {"code": "AI", "name": "Air India", "logoUrl": "/logos/airindia.png"},
            "origin": "DEL",
            "destination": "LHR",
            "destinationName": "London Heathrow",
            "scheduledDeparture": "2026-08-12T12:15:00Z",
            "terminal": "T3",
            "gate": "A08",
            "checkinCounters": "12 – 24",
            "baggageBelt": "Carousel 9",
            "status": "BOARDING"
        },
        {
            "id": "fl_sg812",
            "flightNumber": "SG 812",
            "airline": {"code": "SG", "name": "SpiceJet", "logoUrl": "/logos/spicejet.png"},
            "origin": "DEL",
            "destination": "BOM",
            "destinationName": "Mumbai",
            "scheduledDeparture": "2026-08-12T10:45:00Z",
            "estimatedDeparture": "2026-08-12T11:45:00Z",
            "terminal": "T1",
            "gate": "C04",
            "checkinCounters": "08 – 14",
            "baggageBelt": "Carousel 2",
            "status": "DELAYED",
            "delayReason": "Late arrival of incoming aircraft from Mumbai"
        }
    ]
    return JSONResponse({"success": True, "data": sample_flights})

async def decode_bcbp(request):
    try:
        body = await request.json() if request.method == "POST" else {}
    except Exception:
        body = {}
    raw_bc = body.get("rawBarcode") or body.get("barcode") or ""
    if raw_bc:
        try:
            from services.bcbp_decoder import decode_bcbp as parse_bcbp
            decoded = parse_bcbp(raw_bc)
            pname = decoded.get("passenger_name", "LUC DESMARAIS")
            # Format "DESMARAIS LUC" into "Luc Desmarais"
            if " " in pname:
                parts = pname.split()
                formatted_name = " ".join([p.capitalize() for p in reversed(parts)])
            else:
                formatted_name = pname.title()

            return JSONResponse({
                "success": True,
                "data": {
                    "passengerName": formatted_name,
                    "pnr": decoded.get("pnr", "ABC123"),
                    "flightNumber": decoded.get("flight_number", "6E 203"),
                    "airline": {"code": decoded.get("airline_code", "6E"), "name": "IndiGo", "logoUrl": "/logos/indigo.png"},
                    "origin": decoded.get("origin_iata", "DEL"),
                    "destination": decoded.get("destination_iata", "MAA"),
                    "destinationName": "Chennai" if decoded.get("destination_iata") == "MAA" else "London Heathrow",
                    "scheduledDeparture": "2026-08-12T10:45:00Z",
                    "estimatedDeparture": "2026-08-12T11:45:00Z",
                    "terminal": "T2",
                    "gate": "B12",
                    "checkinCounters": "45 – 52",
                    "baggageBelt": "Carousel 4",
                    "status": "DELAYED",
                    "delayReason": "Late arrival of incoming aircraft"
                }
            })
        except Exception as e:
            logger.warning(f"Error parsing BCBP barcode: {e}")

    return JSONResponse({
        "success": True,
        "data": {
            "passengerName": "Luc Desmarais",
            "pnr": "ABC123",
            "flightNumber": "6E 203",
            "airline": {"code": "6E", "name": "IndiGo", "logoUrl": "/logos/indigo.png"},
            "origin": "DEL",
            "destination": "MAA",
            "destinationName": "Chennai",
            "scheduledDeparture": "2026-08-12T10:45:00Z",
            "estimatedDeparture": "2026-08-12T11:45:00Z",
            "terminal": "T2",
            "gate": "B12",
            "checkinCounters": "45 – 52",
            "baggageBelt": "Carousel 4",
            "status": "DELAYED",
            "delayReason": "Late arrival of incoming aircraft"
        }
    })

async def calculate_wayfinding_route(request):
    body = await request.json() if request.method == "POST" else {}
    origin = body.get("originNodeId", "node_kiosk_t3_l1_04")
    dest = body.get("destinationPoiId", "poi_gate_b12")
    mode = body.get("accessibilityMode", "elevator")
    result = compute_indoor_route(origin_node_id=origin, destination_poi_id=dest, accessibility_mode=mode)
    return JSONResponse(result)

async def list_pois(request):
    pois = [
        {"id": "poi_gate_b12", "name": "Gate B12", "category": "GATE", "floor": "L2"},
        {"id": "poi_medical_centre", "name": "Medical Centre & Pharmacy", "category": "AMENITY", "floor": "L2"},
        {"id": "poi_third_wave", "name": "Third Wave Coffee", "category": "DINING", "floor": "L1"},
        {"id": "poi_relay_books", "name": "Relay Books", "category": "SHOPPING", "floor": "L1"}
    ]
    return JSONResponse({"success": True, "data": pois})

async def process_ai_intent(request):
    body = await request.json() if request.method == "POST" else {}
    transcript = body.get("transcript", "Help me find pharmacy")
    intent = await parse_ai_intent(transcript)
    return JSONResponse({"success": True, "data": intent})

async def get_operator_queue(request):
    from services.webrtc_signaling import call_queue
    return JSONResponse({"success": True, "totalQueued": len(call_queue), "queue": call_queue})

async def submit_feedback(request):
    return JSONResponse({"success": True, "message": "Feedback submitted successfully"})

async def request_wifi_otp(request):
    return JSONResponse({"success": True, "message": "OTP sent to phone", "otp": "123456"})

async def verify_wifi_otp(request):
    return JSONResponse({"success": True, "voucher": "WIFI-AIRPORT-8891", "expiresInMinutes": 45})


routes = [
    Route("/", health_check),
    Route("/health", health_check),
    Route("/api/v1/flights/search", search_flights),
    Route("/api/v1/flights/bcbp-decode", decode_bcbp, methods=["POST"]),
    Route("/api/v1/wayfinding/route", calculate_wayfinding_route, methods=["POST"]),
    Route("/api/v1/wayfinding/pois", list_pois),
    Route("/api/v1/ai/intent", process_ai_intent, methods=["POST"]),
    Route("/api/v1/operator/queue", get_operator_queue),
    Route("/api/v1/feedback/submit", submit_feedback, methods=["POST"]),
    Route("/api/v1/wifi/request-otp", request_wifi_otp, methods=["POST"]),
    Route("/api/v1/wifi/verify-otp", verify_wifi_otp, methods=["POST"]),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

starlette_app = Starlette(debug=True, routes=routes, middleware=middleware)

# Combine Starlette app with Socket.IO ASGI app
combined_app = socketio.ASGIApp(sio, starlette_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:combined_app", host="0.0.0.0", port=5000, reload=True)
