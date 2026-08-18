"""
Legacy Re-Export Wrapper for IATA BCBP Parser
"""

from app.modules.flights.service import (
    AIRLINES,
    AIRPORTS,
    clean_passenger_name,
    clean_seat_number,
    decode_bcbp
)

__all__ = [
    "AIRLINES",
    "AIRPORTS",
    "clean_passenger_name",
    "clean_seat_number",
    "decode_bcbp"
]
