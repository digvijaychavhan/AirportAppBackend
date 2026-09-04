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
        try:
            airline = db.query(models.Airline).filter(models.Airline.code == clean_code).first()
            if airline:
                return {
                    "code": airline.code,
                    "name": airline.name,
                    "logoUrl": airline.logo_url or "/logos/indigo.png",
                    "defaultTerminal": "T3" if airline.flight_type == "international" else "T2"
                }
        finally:
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
        try:
            airport = db.query(models.Airport).filter(models.Airport.iata_code == clean_iata).first()
            if airport:
                return {
                    "city": airport.city,
                    "name": airport.name,
                    "country": airport.country
                }
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Error querying Airport table: {e}")

    return AIRPORTS.get(clean_iata, {"city": clean_iata, "name": f"{clean_iata} Airport", "country": "India"})


def clean_passenger_name(raw_name: str) -> str:
    if not raw_name:
        return ""
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
        return ""
    cleaned = seat_raw.strip()
    return re.sub(r"^0+", "", cleaned) or cleaned

from app.core.timezone import get_current_year

def parse_julian_date(julian_str: str, year: Optional[int] = None) -> Dict[str, Any]:
    if not julian_str or not julian_str.isdigit():
        return {"day": None, "formatted": None, "iso": None}
    try:
        current_year = year or get_current_year()
        day_num = int(julian_str)
        date_obj = datetime(current_year, 1, 1) + timedelta(days=day_num - 1)
        return {
            "day": day_num,
            "formatted": date_obj.strftime("%d %B (%a)"),
            "iso": date_obj.strftime("%Y-%m-%d")
        }
    except Exception:
        return {"day": None, "formatted": None, "iso": None}

def get_compartment_name(code: str) -> str:
    code_upper = (code or "").strip().upper()
    mapping = {
        "F": "First Class (F)",
        "A": "First Class Discounted (A)",
        "J": "Business Class (J)",
        "C": "Business Class (C)",
        "D": "Business Class Discounted (D)",
        "W": "Premium Economy (W)",
        "S": "Premium Economy (S)",
        "Y": "Economy Class (Y)",
        "B": "Economy Class (B)",
        "M": "Economy Class (M)",
        "H": "Economy Class (H)",
        "Q": "Economy Class (Q)",
        "V": "Economy Class (V)"
    }
    return mapping.get(code_upper, f"Unknown ({code_upper})" if code_upper else "")

def get_passenger_status_name(status_code: str) -> str:
    mapping = {
        "0": "Ticket Issued (Not Checked In)",
        "1": "Gate Check-in",
        "2": "Checked-in with Baggage Dropped",
        "3": "Boarding / Passenger Boarded",
        "4": "Passenger Suspended / Standby",
        "5": "Revalidated / Modified",
        "6": "Ticket Cancelled"
    }
    return mapping.get((status_code or "").strip(), "")

def decode_bcbp(raw_barcode: str) -> Dict[str, Any]:
    """
    IATA Resolution 792 — Bar Coded Boarding Pass (BCBP) M-Format Decoder.

    Mandatory single-leg layout (59 characters total):

    Index   Length  Field
    ─────   ──────  ─────────────────────────────────────
    [0:1]      1    Format Code (e.g. 'M' = multiple legs/passengers, 'S', etc.)
    [1:2]      1    Number of Legs ('1'–'4')
    [2:22]    20    Passenger Name  (SURNAME/GIVENNAME, space-padded)
    [22:23]    1    Electronic Ticket Indicator ('E' or ' ')
    [23:30]    7    Operating Carrier PNR (space-padded)
    [30:33]    3    From City Airport Code (IATA)
    [33:36]    3    To City Airport Code (IATA)
    [36:39]    3    Operating Carrier Designator (IATA, space-padded)
    [39:44]    5    Flight Number (zero/space-padded)
    [44:47]    3    Date of Flight — Julian Date (day of year)
    [47:48]    1    Compartment Code (F/C/J/Y etc.)
    [48:52]    4    Seat Number (zero-padded row + seat letter)
    [52:56]    4    Check-in Sequence Number (zero-padded)
    [56:57]    1    Passenger Status (0–6)
    [57:59]    2    Conditional Data Size (hex, '00' = none)

    Every field is extracted strictly from its fixed index.
    No hardcoded fallback values — only what the barcode string contains.
    """
    if not raw_barcode or not isinstance(raw_barcode, str):
        raise ValueError("Invalid barcode payload: String required")

    cleaned = raw_barcode.strip()

    # Mandatory block is 59 chars per IATA spec.
    # Some barcodes may omit trailing optional fields (passenger_status, conditional_data_size),
    # so we require at least 56 chars (up to check-in sequence) to attempt parsing.
    if len(cleaned) < 56:
        raise ValueError(
            f"Invalid BCBP format: must be at least 56 chars, got {len(cleaned)} chars"
        )

    # ── Extract all 15 mandatory fields at exact fixed indices ──

    # [0:1] Format Code (1 char) — e.g. 'M' (multiple legs/passengers), 'S', etc.
    format_code = cleaned[0]

    # [1:2] Number of Legs (1 char) — '1' to '4'
    num_legs_char = cleaned[1]
    number_of_legs = int(num_legs_char) if num_legs_char.isdigit() else None

    # [2:22] Passenger Name (20 chars) — SURNAME/GIVENNAME, space-padded
    passenger_name_raw = cleaned[2:22].strip()

    # [22:23] Electronic Ticket Indicator (1 char) — 'E' or space
    electronic_ticket_indicator = cleaned[22].strip()

    # [23:30] Operating Carrier PNR (7 chars) — space-padded
    pnr = cleaned[23:30].strip()

    # [30:33] From City Airport Code (3 chars)
    origin_iata = cleaned[30:33].strip().upper()

    # [33:36] To City Airport Code (3 chars)
    destination_iata = cleaned[33:36].strip().upper()

    # [36:39] Operating Carrier Designator (3 chars) — space-padded
    airline_code = cleaned[36:39].strip().upper()

    # [39:44] Flight Number (5 chars) — zero/space-padded
    flight_number_raw = cleaned[39:44].strip()
    flight_number_clean = re.sub(r"^0+", "", flight_number_raw) or flight_number_raw

    # [44:47] Date of Flight — Julian Date (3 chars)
    julian_date_raw = cleaned[44:47].strip()

    # [47:48] Compartment Code (1 char)
    compartment_code = cleaned[47].strip().upper()

    # [48:52] Seat Number (4 chars)
    seat_number_raw = cleaned[48:52].strip()

    # [52:56] Check-in Sequence Number (4 chars)
    checkin_sequence_raw = cleaned[52:56].strip()

    # [56:57] Passenger Status (1 char) — may not exist if string is only 56 chars
    passenger_status_code = cleaned[56].strip() if len(cleaned) >= 57 else ""

    # [57:59] Conditional Data Size (2 chars hex) — may not exist
    conditional_data_size = cleaned[57:59].strip() if len(cleaned) >= 59 else ""

    # ── Enrich with lookups (airport, airline, date, class) ──

    origin_info = get_airport_info(origin_iata) if origin_iata else {}
    dest_info = get_airport_info(destination_iata) if destination_iata else {}
    airline_info = get_airline_info(airline_code) if airline_code else {}
    date_info = parse_julian_date(julian_date_raw) if julian_date_raw else {}

    # ── Build result — every value comes from the barcode string ──

    result: Dict[str, Any] = {
        # Raw IATA mandatory fields
        "format_code": format_code,
        "number_of_legs": number_of_legs,
        "passenger_name_raw": passenger_name_raw,
        "passenger_name": clean_passenger_name(passenger_name_raw),
        "electronic_ticket_indicator": electronic_ticket_indicator,
        "pnr": pnr,
        "origin_iata": origin_iata,
        "origin_city": origin_info.get("city", origin_iata),
        "origin_airport": origin_info.get("name", f"{origin_iata} Airport") if origin_iata else "",
        "destination_iata": destination_iata,
        "destination_city": dest_info.get("city", destination_iata),
        "destination_airport": dest_info.get("name", f"{destination_iata} Airport") if destination_iata else "",
        "airline_code": airline_code,
        "airline_name": airline_info.get("name", airline_code),
        "airline_logo": airline_info.get("logoUrl", ""),
        "flight_number": f"{airline_code} {flight_number_clean}" if airline_code and flight_number_clean else flight_number_clean,
        "julian_date": julian_date_raw,
        "flight_date": date_info.get("formatted", ""),
        "flight_date_iso": date_info.get("iso", ""),
        "compartment_code": compartment_code,
        "cabin_class": get_compartment_name(compartment_code),
        "seat_number": clean_seat_number(seat_number_raw),
        "checkin_sequence": re.sub(r"^0+", "", checkin_sequence_raw) or checkin_sequence_raw,
        "passenger_status_code": passenger_status_code,
        "passenger_status": get_passenger_status_name(passenger_status_code),
        "conditional_data_size": conditional_data_size,
        # Enriched / operational (from airline lookup, not barcode)
        "terminal": airline_info.get("defaultTerminal", ""),
        "gate": "",
        "baggage_belt": "",
        "status": ""
    }

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
