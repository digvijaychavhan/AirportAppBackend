from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from services.bcbp_decoder import decode_bcbp

router = APIRouter(prefix="/api/v1/flights", tags=["Flights"])

@router.get("/search", response_model=List[schemas.FlightResponse])
def search_flights(
    query: Optional[str] = Query(None, description="Search term for flight number, destination, or airline"),
    date: Optional[str] = Query(None, description="Filter date in YYYY-MM-DD format"),
    airline: Optional[str] = Query(None, description="Filter by airline code (e.g. 6E, AI)"),
    terminal: Optional[str] = Query(None, description="Filter by terminal (e.g. Terminal 3, T3)"),
    db: Session = Depends(get_db)
):
    """
    Search flights by flight number, destination, airline code, or terminal.
    """
    db_query = db.query(models.Flight)

    if query:
        search_pattern = f"%{query.strip()}%"
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
    return flights


@router.post("/bcbp-decode", response_model=schemas.BCBPDecodeResponse)
def decode_boarding_pass(
    payload: schemas.BCBPDecodeRequest,
    db: Session = Depends(get_db)
):
    """
    Decode raw 2D barcode string (IATA BCBP PDF417/Aztec format) from passenger boarding pass
    and attempt matching against real-time flight database.
    """
    if not payload.raw_bcbp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Raw barcode payload cannot be empty"
        )

    decoded_info = decode_bcbp(payload.raw_bcbp)

    # Attempt database flight lookup
    flight_num = decoded_info.get("flight_number", "").replace(" ", "").upper()
    matched_flight = None

    if flight_num:
        # Search by exact or partial flight number match
        matched_flight = (
            db.query(models.Flight)
            .filter(
                (models.Flight.flight_number.ilike(flight_num)) |
                (models.Flight.flight_number.ilike(f"%{flight_num}%"))
            )
            .first()
        )

    return schemas.BCBPDecodeResponse(
        passenger_name=decoded_info["passenger_name"],
        pnr=decoded_info["pnr"],
        flight_number=decoded_info["flight_number"],
        airline_code=decoded_info["airline_code"],
        origin_iata=decoded_info["origin_iata"],
        destination_iata=decoded_info["destination_iata"],
        seat_number=decoded_info.get("seat_number"),
        departure_date_julian=decoded_info.get("departure_date_julian"),
        matched_flight=matched_flight,
        raw_decoded=decoded_info.get("raw_decoded", {})
    )


@router.get("/{flight_id}", response_model=schemas.FlightResponse)
def get_flight_by_id(
    flight_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve flight status details by Flight ID or Flight Number.
    """
    flight = (
        db.query(models.Flight)
        .filter(
            (models.Flight.id == flight_id) |
            (models.Flight.flight_number.ilike(flight_id))
        )
        .first()
    )

    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID or flight number '{flight_id}' was not found"
        )

    return flight
