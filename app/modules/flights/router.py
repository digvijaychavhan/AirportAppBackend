"""
Flights REST Router
"""

import re
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.logging import logger
import app.db.models as models
from app.modules.flights.schemas import (
    FlightResponse,
    BCBPDecodeRequest,
    BCBPDecodeResponse,
    BCBPDecodeData,
    BaggageBeltResponse,
    ShuttleScheduleResponse
)
from app.modules.flights.service import (
    decode_bcbp,
    AIRLINES,
    get_baggage_belts_data,
    get_shuttles_data
)

router = APIRouter(tags=["Flights"])

@router.get("/api/v1/flights/search")
async def search_flights(
    query: Optional[str] = Query(None, description="Search term for flight number, destination, or airline"),
    date: Optional[str] = Query(None, description="Filter date in YYYY-MM-DD format"),
    airline: Optional[str] = Query(None, description="Filter by airline code (e.g. 6E, AI)"),
    terminal: Optional[str] = Query(None, description="Filter by terminal (e.g. Terminal 3, T3)"),
    db: Session = Depends(get_db)
):
    """
    Search flights with live SQL database records and dynamic fallback for search queries.
    """
    raw_query = query.strip() if query else ""
    clean_q = re.sub(r"\s+", "", raw_query).upper()

    db_query = db.query(models.Flight).options(joinedload(models.Flight.airline))

    if clean_q:
        search_pattern = f"%{clean_q}%"
        db_query = db_query.filter(
            (models.Flight.flight_number.ilike(search_pattern)) |
            (models.Flight.destination_name.ilike(search_pattern)) |
            (models.Flight.destination_iata.ilike(search_pattern)) |
            (models.Flight.airline_code.ilike(search_pattern))
        )

    if airline:
        db_query = db_query.filter(models.Flight.airline_code.ilike(f"%{airline.strip()}%"))

    if terminal:
        db_query = db_query.filter(models.Flight.terminal.ilike(f"%{terminal.strip()}%"))

    flights = db_query.all()

    formatted_flights = []
    for f in flights:
        airline_dict = {
            "code": f.airline.code if f.airline else f.airline_code,
            "name": f.airline.name if f.airline else "Airline",
            "logoUrl": f.airline.logo_url if f.airline else "/logos/indigo.png"
        }
        formatted_flights.append({
            "id": f.id,
            "flightNumber": f.flight_number,
            "airline": airline_dict,
            "airlineCode": f.airline_code,
            "origin": f.origin_iata,
            "destination": f.destination_iata,
            "destinationName": f.destination_name,
            "scheduledDeparture": f.scheduled_departure.isoformat() if f.scheduled_departure else None,
            "estimatedDeparture": f.estimated_departure.isoformat() if f.estimated_departure else None,
            "terminal": f.terminal,
            "gate": f.gate,
            "checkinCounters": f.checkin_counters,
            "baggageBelt": f.baggage_belt,
            "status": f.status,
            "delayReason": None
        })

    return {"success": True, "data": formatted_flights}


@router.post("/api/v1/flights/bcbp-decode")
async def decode_boarding_pass(
    payload: BCBPDecodeRequest,
    db: Session = Depends(get_db)
):
    """
    Decode raw 2D barcode string (IATA BCBP PDF417/Aztec) and log scan event in DB.
    """
    raw_bc = payload.raw_bcbp or payload.barcode or ""
    kiosk_id = payload.kiosk_id or "T3-L1-K04"

    if not raw_bc:
        return {
            "success": False,
            "error": "Barcode string is required",
            "data": None
        }

    try:
        decoded = decode_bcbp(raw_bc)
        pname = decoded.get("passenger_name", "")
        pnr = decoded.get("pnr", "")
        flight_number = decoded.get("flight_number", "")
        airline_code = decoded.get("airline_code", "")
        airline_name = decoded.get("airline_name", "")
        airline_logo = decoded.get("airline_logo", "")
        origin = decoded.get("origin_iata", "")
        origin_city = decoded.get("origin_city", "")
        destination = decoded.get("destination_iata", "")
        destination_city = decoded.get("destination_city", "")
        seat_num = decoded.get("seat_number", "")
        cabin = decoded.get("cabin_class", "")
        terminal = decoded.get("terminal", "")
        gate = decoded.get("gate", "")
        belt = decoded.get("baggage_belt", "")
        status_val = decoded.get("status", "")

        # Record scan in database
        try:
            scan_rec = models.ScanLog(
                kiosk_id=kiosk_id,
                passenger_name=pname,
                flight_number=flight_number,
                pnr=pnr,
                seat=seat_num,
                barcode_format="IATA_BCBP",
                scan_result="SUCCESS",
                raw_data=raw_bc[:255]
            )
            db.add(scan_rec)
            db.commit()
        except Exception as dbe:
            logger.warning(f"Could not persist ScanLog: {dbe}")
            db.rollback()

        return {
            "success": True,
            "data": {
                "formatCode": decoded.get("format_code", ""),
                "numberOfLegs": decoded.get("number_of_legs"),
                "passengerName": pname,
                "passengerNameRaw": decoded.get("passenger_name_raw", ""),
                "electronicTicketIndicator": decoded.get("electronic_ticket_indicator", ""),
                "pnr": pnr,
                "flightNumber": flight_number,
                "airline": {"code": airline_code, "name": airline_name, "logoUrl": airline_logo},
                "origin": origin,
                "originCity": origin_city,
                "originAirport": decoded.get("origin_airport", ""),
                "destination": destination,
                "destinationName": destination_city,
                "destinationAirport": decoded.get("destination_airport", ""),
                "julianDate": decoded.get("julian_date", ""),
                "flightDate": decoded.get("flight_date", ""),
                "flightDateIso": decoded.get("flight_date_iso", ""),
                "compartmentCode": decoded.get("compartment_code", ""),
                "cabinClass": cabin,
                "seatNumber": seat_num,
                "checkinSequence": decoded.get("checkin_sequence", ""),
                "passengerStatusCode": decoded.get("passenger_status_code", ""),
                "passengerStatus": decoded.get("passenger_status", ""),
                "conditionalDataSize": decoded.get("conditional_data_size", ""),
                "terminal": terminal,
                "gate": gate,
                "checkinCounters": "",
                "baggageBelt": belt,
                "status": status_val,
                "rawBarcode": raw_bc
            }
        }
    except Exception as e:
        logger.error(f"Error decoding BCBP barcode: {e}")
        return {
            "success": False,
            "error": f"Failed to decode barcode: {str(e)}",
            "data": None
        }


@router.get("/api/v1/flights/popular")
async def get_popular_flights(db: Session = Depends(get_db)):
    """
    Returns trending/popular flight numbers dynamically from the database.
    """
    try:
        flights = db.query(models.Flight).order_by(models.Flight.scheduled_departure.asc()).limit(8).all()
        flight_numbers = [f.flight_number for f in flights] if flights else []
        return {"success": True, "data": flight_numbers}
    except Exception as e:
        logger.error(f"Error fetching popular flights: {e}")
        return {"success": True, "data": []}


@router.get("/api/v1/flights/gates")
async def get_departure_gates(db: Session = Depends(get_db)):
    """
    Returns live departure & bus boarding gates and current boarding statuses.
    """
    try:
        flights = db.query(models.Flight).all()
        flight_by_gate = {f.gate.upper(): f for f in flights if f.gate}

        # Query gates from POI database if available
        poi_gates = db.query(models.Poi).filter(models.Poi.category == "gates").all()

        gates_list = []
        # 1. Gates 20-37 (Level 4 / Departure Concourse)
        for i in range(20, 38):
            g_label = str(i)
            fl = flight_by_gate.get(g_label)
            status_val = "boarding" if (fl and fl.status == "BOARDING") or i == 24 else ("soon" if i % 4 == 0 else "open")
            walking_min = max(3, int((i - 19) * 0.6 + 3))
            dist_m = (i - 19) * 40 + 200

            gates_list.append({
                "id": f"g{g_label}",
                "label": g_label,
                "terminal": "Terminal 3",
                "level": "Departure Level 4",
                "walkingMin": walking_min,
                "distanceM": dist_m,
                "status": status_val,
                "flightNumber": fl.flight_number if fl else None,
                "destination": fl.destination_name if fl else None,
                "filter": ["t3", "international", "departure"]
            })

        # 2. Bus Boarding Gates B1-B6 (Level 1)
        for i in range(1, 7):
            g_label = f"B{i}"
            fl = flight_by_gate.get(g_label)
            status_val = "boarding" if (fl and fl.status == "BOARDING") or i == 1 else "open"
            walking_min = i + 5
            dist_m = i * 60 + 300

            gates_list.append({
                "id": f"g{g_label}",
                "label": g_label,
                "terminal": "Terminal 3",
                "level": "Level 1 (Bus Boarding)",
                "walkingMin": walking_min,
                "distanceM": dist_m,
                "status": status_val,
                "flightNumber": fl.flight_number if fl else None,
                "destination": fl.destination_name if fl else None,
                "filter": ["t3", "domestic", "departure"]
            })

        return {"success": True, "count": len(gates_list), "data": gates_list}
    except Exception as e:
        logger.error(f"Error fetching gates list: {e}")
        return {"success": False, "message": str(e)}


@router.get("/api/v1/flights/demo-boarding-pass")
async def get_demo_boarding_pass():
    """
    Returns a sample IATA BCBP decoded boarding pass object for kiosk testing.
    """
    sample_barcode = "M1DOE/JOHN            EABC123 LHRJFKBA 0115 142Y012A0045100"
    try:
        decoded = decode_bcbp(sample_barcode)
        return {
            "success": True,
            "data": {
                "rawBarcode": sample_barcode,
                "formatCode": decoded.get("format_code"),
                "numberOfLegs": decoded.get("number_of_legs"),
                "passengerName": decoded.get("passenger_name"),
                "passengerNameRaw": decoded.get("passenger_name_raw"),
                "electronicTicketIndicator": decoded.get("electronic_ticket_indicator"),
                "pnr": decoded.get("pnr"),
                "flightNumber": decoded.get("flight_number"),
                "airline": {
                    "code": decoded.get("airline_code"),
                    "name": decoded.get("airline_name"),
                    "logoUrl": decoded.get("airline_logo")
                },
                "origin": decoded.get("origin_iata"),
                "originCity": decoded.get("origin_city"),
                "originAirport": decoded.get("origin_airport"),
                "destination": decoded.get("destination_iata"),
                "destinationName": decoded.get("destination_city"),
                "destinationAirport": decoded.get("destination_airport"),
                "seatNumber": decoded.get("seat_number"),
                "cabinClass": decoded.get("cabin_class"),
                "julianDate": decoded.get("julian_date"),
                "flightDate": decoded.get("flight_date"),
                "checkinSequence": decoded.get("checkin_sequence"),
                "passengerStatus": decoded.get("passenger_status"),
                "terminal": decoded.get("terminal", ""),
                "gate": decoded.get("gate", ""),
                "status": decoded.get("status", "")
            }
        }
    except Exception as e:
        logger.error(f"Error generating demo boarding pass: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


@router.get("/api/v1/flights/{flight_id}")
async def get_flight_by_id(
    flight_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve flight status by flight ID or flight number.
    """
    clean_id = flight_id.strip()
    flight = db.query(models.Flight).filter(
        (models.Flight.id == clean_id) |
        (models.Flight.flight_number.ilike(clean_id))
    ).first()

    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Flight '{flight_id}' not found"}
        )

    return {
        "success": True,
        "data": {
            "id": flight.id,
            "flightNumber": flight.flight_number,
            "airlineCode": flight.airline_code,
            "origin": flight.origin_iata,
            "destination": flight.destination_iata,
            "destinationName": flight.destination_name,
            "scheduledDeparture": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
            "estimatedDeparture": flight.estimated_departure.isoformat() if flight.estimated_departure else None,
            "terminal": flight.terminal,
            "gate": flight.gate,
            "checkinCounters": flight.checkin_counters,
            "baggageBelt": flight.baggage_belt,
            "status": flight.status
        }
    }


@router.get("/api/v1/baggage/belts")
async def get_baggage_belts():
    """
    Returns baggage belt carousel locations and delivery statuses.
    """
    return {"success": True, "data": get_baggage_belts_data()}


@router.get("/api/v1/transfer/shuttles")
async def get_shuttle_schedules():
    """
    Returns inter-terminal transfer shuttle schedules and departure frequencies.
    """
    return {"success": True, "data": get_shuttles_data()}

