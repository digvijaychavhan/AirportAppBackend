"""
Flights Domain Business Logic & Services
Includes IATA Bar Coded Boarding Pass (BCBP) parser, Flight querying, Baggage belts, and Shuttle data.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
import app.db.models as models

AIRLINES = {
    "6E": {"code": "6E", "name": "IndiGo", "logoUrl": "/logos/indigo.png", "defaultTerminal": "T2"},
    "AI": {"code": "AI", "name": "Air India", "logoUrl": "/logos/airindia.png", "defaultTerminal": "T3"},
    "UK": {"code": "UK", "name": "Vistara", "logoUrl": "/logos/vistara.png", "defaultTerminal": "T3"},
    "QP": {"code": "QP", "name": "Akasa Air", "logoUrl": "/logos/akasa.png", "defaultTerminal": "T2"},
    "SG": {"code": "SG", "name": "SpiceJet", "logoUrl": "/logos/spicejet.png", "defaultTerminal": "T1"},
    "IX": {"code": "IX", "name": "Air India Express", "logoUrl": "/logos/airindia.png", "defaultTerminal": "T3"},
    "G8": {"code": "G8", "name": "Go First", "logoUrl": "/logos/gofirst.png", "defaultTerminal": "T2"},
    "I5": {"code": "I5", "name": "AirAsia India", "logoUrl": "/logos/airasia.png", "defaultTerminal": "T3"},
    "BA": {"code": "BA", "name": "British Airways", "logoUrl": "/logos/ba.png", "defaultTerminal": "T3"},
    "EK": {"code": "EK", "name": "Emirates", "logoUrl": "/logos/emirates.png", "defaultTerminal": "T3"},
    "SQ": {"code": "SQ", "name": "Singapore Airlines", "logoUrl": "/logos/singapore.png", "defaultTerminal": "T3"},
    "LH": {"code": "LH", "name": "Lufthansa", "logoUrl": "/logos/lufthansa.png", "defaultTerminal": "T3"}
}

AIRPORTS = {
    "DEL": {"city": "Delhi", "name": "Indira Gandhi International Airport", "country": "India"},
    "BOM": {"city": "Mumbai", "name": "Chhatrapati Shivaji Maharaj International Airport", "country": "India"},
    "PNQ": {"city": "Pune", "name": "Pune International Airport", "country": "India"},
    "MAA": {"city": "Chennai", "name": "Chennai International Airport", "country": "India"},
    "BLR": {"city": "Bengaluru", "name": "Kempegowda International Airport", "country": "India"},
    "CCU": {"city": "Kolkata", "name": "Netaji Subhash Chandra Bose International Airport", "country": "India"},
    "HYD": {"city": "Hyderabad", "name": "Rajiv Gandhi International Airport", "country": "India"},
    "AMD": {"city": "Ahmedabad", "name": "Sardar Vallabhbhai Patel International Airport", "country": "India"},
    "GOI": {"city": "Goa (Dabolim)", "name": "Dabolim Airport", "country": "India"},
    "GOX": {"city": "Goa (Mopa)", "name": "Manohar International Airport", "country": "India"},
    "COK": {"city": "Kochi", "name": "Cochin International Airport", "country": "India"},
    "JAI": {"city": "Jaipur", "name": "Jaipur International Airport", "country": "India"},
    "LKO": {"city": "Lucknow", "name": "Chaudhary Charan Singh International Airport", "country": "India"},
    "PAT": {"city": "Patna", "name": "Jay Prakash Narayan Airport", "country": "India"},
    "GAU": {"city": "Guwahati", "name": "Lokpriya Gopinath Bordoloi International Airport", "country": "India"},
    "IXC": {"city": "Chandigarh", "name": "Shaheed Bhagat Singh International Airport", "country": "India"},
    "SXR": {"city": "Srinagar", "name": "Sheikh ul-Alam International Airport", "country": "India"},
    "VNS": {"city": "Varanasi", "name": "Lal Bahadur Shastri International Airport", "country": "India"},
    "IXB": {"city": "Bagdogra", "name": "Bagdogra International Airport", "country": "India"},
    "TRV": {"city": "Thiruvananthapuram", "name": "Trivandrum International Airport", "country": "India"},
    "IXE": {"city": "Mangalore", "name": "Mangalore International Airport", "country": "India"},
    "NAG": {"city": "Nagpur", "name": "Dr. Babasaheb Ambedkar International Airport", "country": "India"},
    "IDR": {"city": "Indore", "name": "Devi Ahilya Bai Holkar Airport", "country": "India"},
    "BBI": {"city": "Bhubaneswar", "name": "Biju Patnaik International Airport", "country": "India"},
    "LHR": {"city": "London", "name": "London Heathrow Airport", "country": "United Kingdom"},
    "DXB": {"city": "Dubai", "name": "Dubai International Airport", "country": "UAE"},
    "SIN": {"city": "Singapore", "name": "Singapore Changi Airport", "country": "Singapore"},
    "BKK": {"city": "Bangkok", "name": "Suvarnabhumi Airport", "country": "Thailand"}
}

def get_airline_info(code: str) -> Dict[str, Any]:
    """
    Look up airline metadata from SQLite database, with dictionary fallback.
    """
    clean_code = (code or "").strip().upper()
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        airline = db.query(models.Airline).filter(models.Airline.code == clean_code).first()
        if airline:
            res = {
                "code": airline.code,
                "name": airline.name,
                "logoUrl": airline.logo_url or "/logos/indigo.png",
                "defaultTerminal": "T3" if airline.flight_type == "international" else "T2"
            }
            db.close()
            return res
        db.close()
    except Exception as e:
        logger.warning(f"Error querying Airline table: {e}")

    return AIRLINES.get(clean_code, {"code": clean_code, "name": "Domestic Airline", "logoUrl": "/logos/indigo.png", "defaultTerminal": "T2"})


def get_airport_info(iata: str) -> Dict[str, Any]:
    """
    Look up airport city and name from SQLite database, with dictionary fallback.
    """
    clean_iata = (iata or "").strip().upper()
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        airport = db.query(models.Airport).filter(models.Airport.iata_code == clean_iata).first()
        if airport:
            res = {
                "city": airport.city,
                "name": airport.name,
                "country": airport.country
            }
            db.close()
            return res
        db.close()
    except Exception as e:
        logger.warning(f"Error querying Airport table: {e}")

    return AIRPORTS.get(clean_iata, {"city": clean_iata, "name": f"{clean_iata} Airport", "country": "India"})


def clean_passenger_name(raw_name: str) -> str:
    if not raw_name:
        return "Passenger"
    cleaned = re.sub(r"\b(MR|MRS|MS|MISS|MSTR|DR|PROF)\b", "", raw_name, flags=re.IGNORECASE).strip()
    if "/" in cleaned:
        parts = [p.strip() for p in cleaned.split("/") if p.strip()]
        if len(parts) >= 2:
            return f"{parts[1].title()} {parts[0].title()}"
        elif len(parts) == 1:
            return parts[0].title()
    return cleaned.title()

def clean_seat_number(seat_raw: str) -> str:
    if not seat_raw:
        return "12A"
    cleaned = seat_raw.strip()
    return re.sub(r"^0+", "", cleaned) or cleaned

def decode_bcbp(raw_barcode: str) -> Dict[str, Any]:
    if not raw_barcode or not isinstance(raw_barcode, str):
        raise ValueError("Invalid barcode payload: String required")

    cleaned = raw_barcode.strip()
    result = {
        "passenger_name": "Nirant Patil",
        "pnr": "K9BZMM",
        "flight_number": "6E 2262",
        "airline_code": "6E",
        "airline_name": "IndiGo",
        "airline_logo": "/logos/indigo.png",
        "origin_iata": "DEL",
        "origin_city": "Delhi",
        "destination_iata": "PNQ",
        "destination_city": "Pune",
        "seat_number": "20B",
        "cabin_class": "Economy (Y)",
        "terminal": "T2",
        "gate": "B12",
        "baggage_belt": "Carousel 4",
        "status": "ON TIME",
        "raw_decoded": {}
    }

    try:
        # Standard IATA BCBP M-Format (e.g. M1PATIL/NIRANT...)
        if cleaned.startswith("M") and len(cleaned) >= 50:
            passenger_raw = cleaned[2:22].strip()
            result["passenger_name"] = clean_passenger_name(passenger_raw)

            pnr_raw = cleaned[23:30].strip()
            if pnr_raw:
                result["pnr"] = pnr_raw

            origin = cleaned[30:33].strip().upper()
            dest = cleaned[33:36].strip().upper()
            if origin:
                result["origin_iata"] = origin
                result["origin_city"] = AIRPORTS.get(origin, {}).get("city", origin)
            if dest:
                result["destination_iata"] = dest
                result["destination_city"] = AIRPORTS.get(dest, {}).get("city", dest)

            airline_code = cleaned[36:38].strip().upper()
            flight_num_digits = cleaned[38:43].strip()
            if airline_code:
                result["airline_code"] = airline_code
                airline_info = AIRLINES.get(airline_code, {"name": "Aero Airways", "logoUrl": "/logos/indigo.png", "defaultTerminal": "T2"})
                result["airline_name"] = airline_info["name"]
                result["airline_logo"] = airline_info["logoUrl"]
                result["terminal"] = airline_info.get("defaultTerminal", "T2")

            if airline_code and flight_num_digits:
                clean_digits = re.sub(r"^0+", "", flight_num_digits)
                result["flight_number"] = f"{airline_code} {clean_digits}"

            seat_raw = cleaned[47:51].strip()
            if seat_raw:
                result["seat_number"] = clean_seat_number(seat_raw)
    except Exception as e:
        logger.warning(f"Error parsing IATA BCBP string: {e}")

    return result

def get_baggage_belts_data() -> List[Dict[str, Any]]:
    return [
        {"id": "belt_4", "carousel": "Carousel 4", "flightNumber": "6E 203", "airline": "IndiGo", "origin": "Chennai (MAA)", "status": "DELIVERING", "location": "Terminal 2 · Arrival Hall Level 1"},
        {"id": "belt_9", "carousel": "Carousel 9", "flightNumber": "AI 101", "airline": "Air India", "origin": "London (LHR)", "status": "FIRST_BAG", "location": "Terminal 3 · International Arrival"},
        {"id": "belt_2", "carousel": "Carousel 2", "flightNumber": "SG 812", "airline": "SpiceJet", "origin": "Mumbai (BOM)", "status": "DELAYED", "location": "Terminal 1 · Domestic Arrival"}
    ]

def get_shuttles_data() -> List[Dict[str, Any]]:
    return [
        {"id": "shuttle_1", "route": "Terminal 3 ↔ Terminal 1", "frequencyMinutes": 10, "nextDeparture": "4 mins", "location": "Gate 4, Arrival Level"},
        {"id": "shuttle_2", "route": "Terminal 3 ↔ Terminal 2", "frequencyMinutes": 5, "nextDeparture": "2 mins", "location": "Gate 2, Arrival Level"},
        {"id": "shuttle_3", "route": "Express Metro Transit", "frequencyMinutes": 12, "nextDeparture": "6 mins", "location": "Airport Metro Station"}
    ]
