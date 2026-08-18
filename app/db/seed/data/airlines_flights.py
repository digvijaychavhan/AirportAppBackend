"""
Seed Data Fixtures: Airlines & Flights
"""

from datetime import datetime, timedelta

def get_seed_airlines():
    return [
        {"code": "6E", "name": "IndiGo", "logo_url": "/logos/indigo.png", "flight_type": "DOMESTIC"},
        {"code": "AI", "name": "Air India", "logo_url": "/logos/airindia.png", "flight_type": "INTERNATIONAL"},
        {"code": "UK", "name": "Vistara", "logo_url": "/logos/vistara.png", "flight_type": "DOMESTIC"},
        {"code": "SG", "name": "SpiceJet", "logo_url": "/logos/spicejet.png", "flight_type": "DOMESTIC"},
        {"code": "EK", "name": "Emirates", "logo_url": "/logos/emirates.png", "flight_type": "INTERNATIONAL"},
        {"code": "QP", "name": "Akasa Air", "logo_url": "/logos/akasa.png", "flight_type": "DOMESTIC"},
    ]

def get_seed_flights():
    now = datetime.utcnow()
    return [
        {
            "id": "fl_6e2262",
            "flight_number": "6E 2262",
            "airline_code": "6E",
            "origin_iata": "DEL",
            "destination_iata": "PNQ",
            "destination_name": "Pune",
            "scheduled_departure": now + timedelta(hours=1, minutes=30),
            "estimated_departure": now + timedelta(hours=1, minutes=30),
            "terminal": "T2",
            "gate": "B12",
            "checkin_counters": "45 – 52",
            "baggage_belt": "Carousel 4",
            "status": "ON TIME"
        },
        {
            "id": "fl_6e203",
            "flight_number": "6E 203",
            "airline_code": "6E",
            "origin_iata": "DEL",
            "destination_iata": "MAA",
            "destination_name": "Chennai (MAA)",
            "scheduled_departure": now + timedelta(hours=2),
            "estimated_departure": now + timedelta(hours=2, minutes=45),
            "terminal": "T2",
            "gate": "B14",
            "checkin_counters": "45 – 52",
            "baggage_belt": "Carousel 4",
            "status": "DELAYED"
        },
        {
            "id": "fl_ai101",
            "flight_number": "AI 101",
            "airline_code": "AI",
            "origin_iata": "DEL",
            "destination_iata": "LHR",
            "destination_name": "London Heathrow (LHR)",
            "scheduled_departure": now + timedelta(hours=1, minutes=15),
            "estimated_departure": now + timedelta(hours=1, minutes=15),
            "terminal": "T3",
            "gate": "A08",
            "checkin_counters": "12 – 24",
            "baggage_belt": "Carousel 9",
            "status": "BOARDING"
        },
        {
            "id": "fl_uk812",
            "flight_number": "UK 812",
            "airline_code": "UK",
            "origin_iata": "DEL",
            "destination_iata": "BLR",
            "destination_name": "Bengaluru (BLR)",
            "scheduled_departure": now + timedelta(hours=3, minutes=30),
            "estimated_departure": now + timedelta(hours=3, minutes=30),
            "terminal": "T3",
            "gate": "A14",
            "checkin_counters": "25 – 32",
            "baggage_belt": "Carousel 7",
            "status": "ON TIME"
        },
        {
            "id": "fl_sg812",
            "flight_number": "SG 812",
            "airline_code": "SG",
            "origin_iata": "DEL",
            "destination_iata": "BOM",
            "destination_name": "Mumbai (BOM)",
            "scheduled_departure": now + timedelta(hours=4),
            "estimated_departure": now + timedelta(hours=4, minutes=30),
            "terminal": "T1",
            "gate": "C04",
            "checkin_counters": "08 – 14",
            "baggage_belt": "Carousel 2",
            "status": "DELAYED"
        },
        {
            "id": "fl_qp1102",
            "flight_number": "QP 1102",
            "airline_code": "QP",
            "origin_iata": "DEL",
            "destination_iata": "AMD",
            "destination_name": "Ahmedabad",
            "scheduled_departure": now + timedelta(hours=5),
            "estimated_departure": now + timedelta(hours=5),
            "terminal": "T2",
            "gate": "B06",
            "checkin_counters": "35 – 42",
            "baggage_belt": "Carousel 5",
            "status": "ON TIME"
        }
    ]
