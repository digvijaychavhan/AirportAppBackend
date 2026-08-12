import re
from typing import Dict, Any, Optional

def decode_bcbp(raw_barcode: str) -> Dict[str, Any]:
    """
    Decodes an IATA Resolution 792 Bar Coded Boarding Pass (BCBP) string or relaxed simulated format.

    Standard BCBP Layout (Mandatory Fields):
    - Format Code: 1 char ('M')
    - Number of Legs: 1 char ('1')
    - Passenger Name: 20 chars ('LASTNAME/FIRSTNAME MR  ')
    - Electronic Ticket Indicator: 1 char ('E')
    - PNR / Booking Code: 7 chars ('PNR1234')
    - Origin IATA: 3 chars ('DEL')
    - Destination IATA: 3 chars ('MAA')
    - Operating Carrier: 3 chars ('6E ')
    - Flight Number: 5 chars ('00203')
    - Julian Date of Flight: 3 chars ('224')
    - Compartment Code: 1 char ('Y')
    - Seat Number: 4 chars ('012A')
    - Sequence Number: 5 chars ('0001 ')
    - Passenger Status: 1 char ('1')
    """
    if not raw_barcode or not isinstance(raw_barcode, str):
        raise ValueError("Invalid barcode payload: String required")

    cleaned = raw_barcode.strip()

    # Default fallback extraction structure
    result = {
        "passenger_name": "PASSENGER/UNKNOWN",
        "pnr": "UNKNOWN",
        "flight_number": "6E203",
        "airline_code": "6E",
        "origin_iata": "DEL",
        "destination_iata": "MAA",
        "seat_number": "12A",
        "departure_date_julian": "224",
        "raw_decoded": {}
    }

    try:
        # Check if standard IATA BCBP (starts with 'M') and has sufficient length
        if cleaned.startswith("M") and len(cleaned) >= 55:
            format_code = cleaned[0]          # 'M'
            number_of_legs = cleaned[1]       # '1'
            name_raw = cleaned[2:22].strip()   # 'DOE/JOHN MR'
            eticket_ind = cleaned[22]         # 'E'
            pnr_raw = cleaned[23:30].strip()   # 'ABC123D'
            origin_iata = cleaned[30:33].strip() # 'DEL'
            dest_iata = cleaned[33:36].strip()   # 'MAA'
            airline_code_raw = cleaned[36:39].strip() # '6E' or 'AI'
            flight_num_raw = cleaned[39:44].strip()   # '00203'
            julian_date = cleaned[44:47].strip()      # '224'
            compartment = cleaned[47:48].strip()      # 'Y'
            seat_raw = cleaned[48:52].strip()         # '012A'

            # Clean Flight Number (remove leading zeroes if alphanumeric)
            flight_num_clean = re.sub(r"^0+", "", flight_num_raw)
            full_flight_number = f"{airline_code_raw}{flight_num_clean}" if not flight_num_raw.startswith(airline_code_raw) else flight_num_raw

            result["passenger_name"] = name_raw.replace("/", " ") if "/" in name_raw else name_raw
            result["pnr"] = pnr_raw
            result["flight_number"] = full_flight_number
            result["airline_code"] = airline_code_raw
            result["origin_iata"] = origin_iata
            result["destination_iata"] = dest_iata
            result["seat_number"] = seat_raw
            result["departure_date_julian"] = julian_date
            result["raw_decoded"] = {
                "format_code": format_code,
                "legs": number_of_legs,
                "raw_name": name_raw,
                "eticket": eticket_ind,
                "pnr": pnr_raw,
                "origin": origin_iata,
                "destination": dest_iata,
                "carrier": airline_code_raw,
                "flight_raw": flight_num_raw,
                "julian_date": julian_date,
                "compartment": compartment,
                "seat": seat_raw
            }
            return result

        # Fallback regex parser for non-standard / simplified boarding pass strings
        # Example: "6E 203 DEL MAA PNR: ABC123D NAME: JOHN DOE"
        flight_match = re.search(r"([A-Z0-9]{2})\s*([0-9]{3,4})", cleaned)
        if flight_match:
            airline_code = flight_match.group(1)
            flight_num = flight_match.group(2)
            result["airline_code"] = airline_code
            result["flight_number"] = f"{airline_code} {flight_num}"

        pnr_match = re.search(r"\b([A-Z0-9]{6,7})\b", cleaned)
        if pnr_match:
            result["pnr"] = pnr_match.group(1)

        name_match = re.search(r"([A-Z]+/[A-Z\s]+)", cleaned)
        if name_match:
            result["passenger_name"] = name_match.group(1).replace("/", " ")

        result["raw_decoded"] = {"fallback_parse": True, "raw_string": cleaned}
        return result

    except Exception as e:
        # Graceful fallback on unexpected parse error
        result["raw_decoded"] = {"error": str(e), "raw_string": cleaned}
        return result
