"""
Main Python ASGI Server Application
Built on Starlette & Socket.IO for maximum execution speed and zero build bottlenecks
"""

import json
import logging
from datetime import datetime
import random
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import socketio

from services.webrtc_signaling import sio, active_calls
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

async def get_call_details(request):
    call_id = request.path_params.get("call_id")
    if call_id in active_calls:
        return JSONResponse({"success": True, "data": active_calls[call_id]})
    
    try:
        from database import SessionLocal
        from models import SupportCall
        db = SessionLocal()
        call = db.query(SupportCall).filter(SupportCall.id == call_id).first()
        if call:
            minutes = call.call_duration_seconds // 60
            seconds = call.call_duration_seconds % 60
            dur_str = f"{minutes:02d}:{seconds:02d}"
            kiosk_code = call.kiosk.code if call.kiosk else (call.kiosk_id or "T3-L1-K04")
            
            categories_list = [c.strip() for c in call.issue_category.split(",")] if call.issue_category else []

            data = {
                "sessionId": call.id,
                "passengerName": call.passenger_name or "Passenger",
                "flightNumber": call.flight_number or "",
                "pnr": call.pnr or "",
                "kioskId": kiosk_code,
                "duration": dur_str,
                "notes": call.operator_notes or "",
                "categories": categories_list,
                "date": call.created_at.strftime("%d-%b-%y"),
                "time": call.created_at.strftime("%I:%M %p"),
                "status": "RESOLVED"
            }
            db.close()
            return JSONResponse({"success": True, "data": data})
        db.close()
    except Exception as e:
        logger.error(f"Error finding call details: {e}")

    return JSONResponse({"success": False, "message": "Call not found"}, status_code=404)

async def submit_operator_log(request):
    try:
        body = await request.json()
        session_id = body.get("sessionId")
        kiosk_id = body.get("kioskId", "T3-L1-K04")

        from database import SessionLocal
        from models import SupportCall, Kiosk
        
        db = SessionLocal()
        
        kiosk_obj = db.query(Kiosk).filter(Kiosk.id == kiosk_id).first()
        if not kiosk_obj:
            kiosk_obj = db.query(Kiosk).filter(Kiosk.code == kiosk_id).first()
            
        kiosk_db_id = kiosk_obj.id if kiosk_obj else "T3-L1-K04"
        
        duration_str = body.get("duration", "00:00")
        call_duration_seconds = 0
        if ":" in duration_str:
            parts = duration_str.split(":")
            if len(parts) == 2:
                call_duration_seconds = int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                call_duration_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                
        categories = body.get("categories", [])
        categories_str = ", ".join(categories) if categories else None
        
        support_call = SupportCall(
            id=session_id if session_id and not ("demo" in session_id or "test" in session_id) else None,
            kiosk_id=kiosk_db_id,
            operator_id="op_101",  # Priya Sharma
            status="ended",
            call_duration_seconds=call_duration_seconds,
            issue_category=categories_str,
            operator_notes=body.get("notes", ""),
            passenger_name=f"{body.get('firstName', '')} {body.get('lastName', '')}".strip() or "Passenger",
            flight_number=body.get("flightNo", ""),
            pnr="ABC123"
        )
        
        db.add(support_call)
        db.commit()
        
        res_data = {
            "session": support_call.id,
            "date": support_call.created_at.strftime("%d-%b-%y"),
            "time": support_call.created_at.strftime("%I:%M %p"),
            "kiosk": kiosk_id,
            "passenger": support_call.passenger_name,
            "duration": duration_str,
            "notes": support_call.operator_notes,
            "categories": categories,
            "flightNo": support_call.flight_number
        }
        logger.info(f"Saved support call to DB: {support_call.id}")
        db.close()
        return JSONResponse({"success": True, "message": "Log submitted successfully", "data": res_data})
    except Exception as e:
        logger.error(f"Error submitting operator log: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

async def get_operator_stats(request):
    try:
        from database import SessionLocal
        from models import SupportCall
        
        db = SessionLocal()
        calls = db.query(SupportCall).all()
        total = len(calls)
        
        if total == 0:
            db.close()
            return JSONResponse({
                "success": True,
                "data": {
                    "totalInboundCalls": 0,
                    "avgCallTimeMinutes": "0.00",
                    "resolutionRate": "100%",
                    "activeOperators": 3
                }
            })
            
        total_seconds = sum(c.call_duration_seconds for c in calls)
        avg_minutes = (total_seconds / 60) / total
        
        db.close()
        return JSONResponse({
            "success": True,
            "data": {
                "totalInboundCalls": total,
                "avgCallTimeMinutes": f"{avg_minutes:.2f}",
                "resolutionRate": "100%",
                "activeOperators": 3
            }
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

async def get_operator_logs(request):
    try:
        from database import SessionLocal
        from models import SupportCall
        
        db = SessionLocal()
        calls = db.query(SupportCall).order_by(SupportCall.created_at.desc()).all()
        
        logs = []
        for c in calls:
            kiosk_code = c.kiosk_id
            if c.kiosk:
                kiosk_code = c.kiosk.code
                
            minutes = c.call_duration_seconds // 60
            seconds = c.call_duration_seconds % 60
            duration_str = f"{minutes:02d}:{seconds:02d}"
            
            logs.append({
                "session": c.id,
                "date": c.created_at.strftime("%d-%b-%y"),
                "time": c.created_at.strftime("%I:%M %p"),
                "kiosk": kiosk_code,
                "passenger": c.passenger_name or "Passenger",
                "duration": duration_str,
                "notes": c.operator_notes or "",
                "status": "RESOLVED",
                "categories": c.issue_category.split(", ") if c.issue_category else [],
                "flightNo": c.flight_number or ""
            })
            
        db.close()
        return JSONResponse({"success": True, "data": logs})
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

async def submit_feedback(request):
    try:
        body = await request.json()
        ratings = body.get("ratings", {})
        comments = body.get("comments", "")
        
        from database import SessionLocal
        from models import FeedbackSubmission
        
        db = SessionLocal()
        
        cleanliness = ratings.get("cleanliness", 5)
        staff = ratings.get("staff", 5)
        wayfinding = ratings.get("navigation", 5)
        wifi = ratings.get("facilities", 5)
        food = ratings.get("facilities", 5)
        overall = ratings.get("overall", 5)
        
        feedback = FeedbackSubmission(
            cleanliness_rating=cleanliness,
            staff_rating=staff,
            wayfinding_rating=wayfinding,
            wifi_rating=wifi,
            food_rating=food,
            overall_rating=overall,
            comments=comments,
            kiosk_id="T3-L1-K04"
        )
        
        db.add(feedback)
        db.commit()
        logger.info(f"Feedback saved successfully: {feedback.id}")
        db.close()
        return JSONResponse({"success": True, "message": "Feedback submitted successfully"})
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

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
    try:
        category = request.query_params.get("category", "").strip()
        from database import SessionLocal
        from models import Poi
        db = SessionLocal()
        
        query = db.query(Poi)
        if category:
            query = query.filter(Poi.category.ilike(category))
            
        pois = query.all()
        
        data = [{
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "categoryLabel": p.sub_category or p.category,
            "subCategory": p.sub_category or "",
            "description": p.description or "",
            "isOpen": True,
            "hours": p.operating_hours or "24 Hours",
            "terminal": p.terminal or "",
            "floor": p.floor_name or "",
            "gate": p.gate or "",
            "distanceM": p.distance_m or 100,
            "image": p.image_url or "",
            "badge": p.badge_label or "",
            "badgeVariant": p.badge_variant or "purple",
            "filter": p.sub_category.split(",") if p.sub_category else []
        } for p in pois]
        
        db.close()
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Error fetching directory pois: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

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


from starlette.routing import Route, Mount
from routes.map_editor import routes as map_editor_routes
from routes.admin import routes as admin_routes

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
    Route("/api/v1/operator/call/{call_id}", get_call_details),
    Route("/api/v1/operator/logs/submit", submit_operator_log, methods=["POST"]),
    Route("/api/v1/feedback/submit", submit_feedback, methods=["POST"]),
    Route("/api/v1/wifi/request-otp", request_wifi_otp, methods=["POST"]),
    Route("/api/v1/wifi/verify-otp", verify_wifi_otp, methods=["POST"]),
    Route("/api/v1/baggage/belts", get_baggage_belts),
    Route("/api/v1/directory", get_directory_pois),
    Route("/api/v1/transfer/shuttles", get_shuttle_schedules),
    Route("/api/v1/kiosk/heartbeat", kiosk_heartbeat, methods=["POST"]),
] + map_editor_routes + admin_routes

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

starlette_app = Starlette(debug=True, routes=routes, middleware=middleware)

# Combine Starlette app with Socket.IO ASGI app
combined_app = socketio.ASGIApp(sio, starlette_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:combined_app", host="0.0.0.0", port=5000, reload=True)
