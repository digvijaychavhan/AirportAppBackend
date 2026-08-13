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

async def get_operator_stats(request):
    return JSONResponse({
        "success": True,
        "data": {
            "totalInboundCalls": 24,
            "avgCallTimeMinutes": "3.45",
            "resolutionRate": "95%",
            "activeOperators": 3
        }
    })

async def get_operator_logs(request):
    logs = [
        {"session": "89542", "date": "13-Aug-26", "time": "11:30", "kiosk": "T3-L1-K04", "passenger": "Luc Desmarais", "duration": "4m 12s", "status": "RESOLVED"},
        {"session": "78405", "date": "13-Aug-26", "time": "10:45", "kiosk": "T2-A87", "passenger": "Ananya Sharma", "duration": "3m 05s", "status": "RESOLVED"},
        {"session": "89545", "date": "13-Aug-26", "time": "09:20", "kiosk": "T2-A92", "passenger": "Rajesh Kumar", "duration": "2m 50s", "status": "RESOLVED"},
        {"session": "597712", "date": "13-Aug-26", "time": "08:15", "kiosk": "T1-C04", "passenger": "Priya Patel", "duration": "5m 10s", "status": "RESOLVED"}
    ]
    return JSONResponse({"success": True, "data": logs})

async def submit_feedback(request):
    return JSONResponse({"success": True, "message": "Feedback submitted successfully"})

async def request_wifi_otp(request):
    return JSONResponse({"success": True, "message": "OTP sent to phone", "otp": "123456"})

async def verify_wifi_otp(request):
    return JSONResponse({"success": True, "voucher": "WIFI-AIRPORT-8891", "expiresInMinutes": 45})


async def get_baggage_belts(request):
    belts = [
        {"id": "belt_4", "carousel": "Carousel 4", "flightNumber": "6E 203", "airline": "IndiGo", "origin": "Chennai (MAA)", "status": "DELIVERING", "location": "Terminal 2 · Arrival Hall Level 1"},
        {"id": "belt_9", "carousel": "Carousel 9", "flightNumber": "AI 101", "airline": "Air India", "origin": "London (LHR)", "status": "FIRST_BAG", "location": "Terminal 3 · International Arrival"},
        {"id": "belt_2", "carousel": "Carousel 2", "flightNumber": "SG 812", "airline": "SpiceJet", "origin": "Mumbai (BOM)", "status": "DELAYED", "location": "Terminal 1 · Domestic Arrival"}
    ]
    return JSONResponse({"success": True, "data": belts})

async def get_directory_pois(request):
    category = request.query_params.get("category", "")
    pois = [
        {"id": "poi_third_wave", "name": "Third Wave Coffee", "category": "eat-dine", "sub": "Café & Artisanal Coffee", "floor": "L1", "terminal": "T3", "gate": "Near Gate B10"},
        {"id": "poi_starbucks", "name": "Starbucks Coffee", "category": "eat-dine", "sub": "Beverages & Pastries", "floor": "L2", "terminal": "T3", "gate": "Food Court"},
        {"id": "poi_duty_free", "name": "Delhi Duty Free", "category": "shopping", "sub": "Perfumes, Cosmetics & Liquor", "floor": "L1", "terminal": "T3", "gate": "Central Atrium"},
        {"id": "poi_relay", "name": "Relay Travel Store", "category": "shopping", "sub": "Books, Snacks & Electronics", "floor": "L1", "terminal": "T2", "gate": "Gate B12"},
        {"id": "poi_plaza_premium", "name": "Encalm Premium Lounge", "category": "lounge", "sub": "24/7 Buffet, Shower & Wifi", "floor": "L2", "terminal": "T3", "gate": "Mezzanine Level"},
        {"id": "poi_medical", "name": "Apollo Medical Centre", "category": "medical", "sub": "24/7 Doctor & Pharmacy", "floor": "L1", "terminal": "T3", "gate": "Near Elevator B"}
    ]
    if category:
        pois = [p for p in pois if p["category"] == category or category in p["sub"].lower()]
    return JSONResponse({"success": True, "data": pois})

async def get_shuttle_schedules(request):
    shuttles = [
        {"id": "shuttle_1", "route": "Terminal 3 ↔ Terminal 1", "frequencyMinutes": 10, "nextDeparture": "4 mins", "location": "Gate 4, Arrival Level"},
        {"id": "shuttle_2", "route": "Terminal 3 ↔ Terminal 2", "frequencyMinutes": 5, "nextDeparture": "2 mins", "location": "Gate 2, Arrival Level"},
        {"id": "shuttle_3", "route": "Express Metro Transit", "frequencyMinutes": 12, "nextDeparture": "6 mins", "location": "Airport Metro Station"}
    ]
    return JSONResponse({"success": True, "data": shuttles})

async def kiosk_heartbeat(request):
    body = await request.json() if request.method == "POST" else {}
    kiosk_id = body.get("kioskId", "T3-L1-K04")
    return JSONResponse({"success": True, "status": "acknowledged", "kioskId": kiosk_id})


routes = [
    Route("/", health_check),
    Route("/health", health_check),
    Route("/api/v1/flights/search", search_flights),
    Route("/api/v1/flights/bcbp-decode", decode_bcbp, methods=["POST"]),
    Route("/api/v1/wayfinding/route", calculate_wayfinding_route, methods=["POST"]),
    Route("/api/v1/wayfinding/pois", list_pois),
    Route("/api/v1/ai/intent", process_ai_intent, methods=["POST"]),
    Route("/api/v1/operator/queue", get_operator_queue),
    Route("/api/v1/operator/stats", get_operator_stats),
    Route("/api/v1/operator/logs", get_operator_logs),
    Route("/api/v1/feedback/submit", submit_feedback, methods=["POST"]),
    Route("/api/v1/wifi/request-otp", request_wifi_otp, methods=["POST"]),
    Route("/api/v1/wifi/verify-otp", verify_wifi_otp, methods=["POST"]),
    Route("/api/v1/baggage/belts", get_baggage_belts),
    Route("/api/v1/directory", get_directory_pois),
    Route("/api/v1/transfer/shuttles", get_shuttle_schedules),
    Route("/api/v1/kiosk/heartbeat", kiosk_heartbeat, methods=["POST"]),
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
