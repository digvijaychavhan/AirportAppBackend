"""
Database Seeder Engine
Populates SQLite / PostgreSQL database with domain records idempotently.
"""

import sys
from app.core.database import engine, Base, SessionLocal
from app.core.logging import logger
import app.db.models as models
from app.db.seed.data import (
    get_seed_airlines,
    get_seed_flights,
    get_seed_floors,
    get_seed_map_nodes,
    get_seed_map_edges,
    get_seed_kiosks,
    get_seed_categories,
    get_seed_pois,
    get_seed_devices,
    get_seed_operators,
    get_seed_scan_logs,
    get_seed_user_action_logs
)

def seed_database(force: bool = False, session=None, custom_engine=None):
    """
    Seeds initial database tables with domain entities.
    If force=True, drops and recreates all tables.
    Otherwise, performs idempotent upserts across all domain entities.
    """
    active_engine = custom_engine or engine
    logger.info("Initializing database schema...")
    if force and not session:
        logger.warning("Force flag enabled: dropping all tables...")
        Base.metadata.drop_all(bind=active_engine)

    if not session:
        Base.metadata.create_all(bind=active_engine)
        db = SessionLocal()
        owns_session = True
    else:
        db = session
        owns_session = False

    try:
        # 1. Airlines (Upsert)
        for a in get_seed_airlines():
            existing = db.query(models.Airline).filter(models.Airline.code == a["code"]).first()
            if not existing:
                db.add(models.Airline(**a))
            else:
                for k, v in a.items():
                    setattr(existing, k, v)
        db.commit()

        # 2. Map Floors (Upsert)
        for f in get_seed_floors():
            existing = db.query(models.MapFloor).filter(models.MapFloor.id == f["id"]).first()
            if not existing:
                db.add(models.MapFloor(**f))
            else:
                for k, v in f.items():
                    setattr(existing, k, v)
        db.commit()

        # 3. Map Nodes (Upsert)
        for n in get_seed_map_nodes():
            existing = db.query(models.MapNode).filter(models.MapNode.id == n["id"]).first()
            if not existing:
                db.add(models.MapNode(**n))
            else:
                for k, v in n.items():
                    setattr(existing, k, v)
        db.commit()

        # 4. Map Edges (Upsert)
        for e in get_seed_map_edges():
            existing = db.query(models.MapEdge).filter(models.MapEdge.id == e["id"]).first()
            if not existing:
                db.add(models.MapEdge(**e))
            else:
                for k, v in e.items():
                    setattr(existing, k, v)
        db.commit()

        # 5. Kiosks (Upsert)
        for k_data in get_seed_kiosks():
            existing = db.query(models.Kiosk).filter(models.Kiosk.id == k_data["id"]).first()
            if not existing:
                db.add(models.Kiosk(**k_data))
            else:
                for k, v in k_data.items():
                    setattr(existing, k, v)
        db.commit()

        # 6. Wayfinding Categories (Upsert)
        for c in get_seed_categories():
            existing = db.query(models.WayfindingCategory).filter(models.WayfindingCategory.id == c["id"]).first()
            if not existing:
                db.add(models.WayfindingCategory(**c))
            else:
                for k, v in c.items():
                    setattr(existing, k, v)
        db.commit()

        # 7. Points of Interest (POIs) (Upsert & Clean)
        for p in get_seed_pois():
            existing = db.query(models.Poi).filter(models.Poi.id == p["id"]).first()
            if not existing:
                db.add(models.Poi(**p))
            else:
                for k, v in p.items():
                    setattr(existing, k, v)
                existing.is_active = True
        db.commit()

        # 8. Flights (Upsert)
        for fl in get_seed_flights():
            existing = db.query(models.Flight).filter(models.Flight.id == fl["id"]).first()
            if not existing:
                db.add(models.Flight(**fl))
            else:
                for k, v in fl.items():
                    setattr(existing, k, v)
        db.commit()

        # 9. Devices (Upsert)
        for d in get_seed_devices():
            existing = db.query(models.Device).filter(models.Device.device_id == d["device_id"]).first()
            if not existing:
                db.add(models.Device(**d))
            else:
                for k, v in d.items():
                    setattr(existing, k, v)
        db.commit()

        # 10. Operators (Upsert)
        for op in get_seed_operators():
            existing = db.query(models.Operator).filter(models.Operator.id == op["id"]).first()
            if not existing:
                db.add(models.Operator(**op))
            else:
                for k, v in op.items():
                    setattr(existing, k, v)
        db.commit()

        # 11. Feedback Categories (Upsert)
        seed_feedback_cats = [
            {"id": "cleanliness", "title": "Airport Cleanliness", "label": "Airport Cleanliness", "icon": "cleaning_services", "sort_order": 1, "is_active": 1},
            {"id": "staff", "title": "Staff Helpfulness", "label": "Staff Helpfulness", "icon": "support_agent", "sort_order": 2, "is_active": 1},
            {"id": "navigation", "title": "Signage & Navigation", "label": "Signage & Navigation", "icon": "directions", "sort_order": 3, "is_active": 1},
            {"id": "facilities", "title": "Washrooms & Rest Areas", "label": "Washrooms & Rest Areas", "icon": "water_drop", "sort_order": 4, "is_active": 1},
            {"id": "security", "title": "Security Screening", "label": "Security Screening", "icon": "security", "sort_order": 5, "is_active": 1},
            {"id": "overall", "title": "Overall Experience", "label": "Overall Experience", "icon": "stars", "sort_order": 6, "is_active": 1},
        ]
        for fc in seed_feedback_cats:
            existing = db.query(models.FeedbackCategory).filter(models.FeedbackCategory.id == fc["id"]).first()
            if not existing:
                db.add(models.FeedbackCategory(**fc))
            else:
                for k, v in fc.items():
                    setattr(existing, k, v)
        db.commit()

        # 12. Operator Query Tag Categories (Upsert)
        import json
        seed_query_tags = [
            {"id": "cat1", "name": "Accessibility Services", "sub_items_json": json.dumps(["Wheelchair", "Elderly", "Infant Care"]), "sort_order": 1, "is_active": True},
            {"id": "cat2", "name": "Baggage Services", "sub_items_json": json.dumps(["Lost", "Delayed", "Damaged", "Wrapping"]), "sort_order": 2, "is_active": True},
            {"id": "cat3", "name": "Check-In Assistance", "sub_items_json": json.dumps(["Counter Info", "Baggage Drop", "Self Kiosk"]), "sort_order": 3, "is_active": True},
            {"id": "cat4", "name": "Customer Complaints", "sub_items_json": json.dumps(["Staff", "Cleanliness", "Facilities"]), "sort_order": 4, "is_active": True},
            {"id": "cat5", "name": "Flight Information", "sub_items_json": json.dumps(["Delays", "Cancellations", "Gate Change", "Boarding"]), "sort_order": 5, "is_active": True},
            {"id": "cat6", "name": "Location & Wayfinding", "sub_items_json": json.dumps(["Dining", "Lounges", "Shops", "Gates", "Restrooms"]), "sort_order": 6, "is_active": True},
            {"id": "cat7", "name": "Lost & Found", "sub_items_json": json.dumps(["Report Found", "Looking for Item", "Collection Desk"]), "sort_order": 7, "is_active": True},
            {"id": "cat8", "name": "Security Screening", "sub_items_json": json.dumps(["Express Queue", "Rules", "Liquids"]), "sort_order": 8, "is_active": True},
            {"id": "cat9", "name": "Transportation Services", "sub_items_json": json.dumps(["Airport Metro", "Taxi", "Bus Shuttle", "Rental"]), "sort_order": 9, "is_active": True},
            {"id": "cat10", "name": "Travel Documentation", "sub_items_json": json.dumps(["Visa Check", "Passport Desk", "Customs"]), "sort_order": 10, "is_active": True},
        ]
        for qt in seed_query_tags:
            existing = db.query(models.QueryTagCategory).filter(models.QueryTagCategory.id == qt["id"]).first()
            if not existing:
                db.add(models.QueryTagCategory(**qt))
            else:
                for k, v in qt.items():
                    setattr(existing, k, v)
        db.commit()

        # 13. Airports (Upsert)
        seed_airports = [
            {"iata_code": "DEL", "city": "Delhi", "name": "Indira Gandhi International Airport", "country": "India", "is_active": True},
            {"iata_code": "BOM", "city": "Mumbai", "name": "Chhatrapati Shivaji Maharaj International Airport", "country": "India", "is_active": True},
            {"iata_code": "BLR", "city": "Bengaluru", "name": "Kempegowda International Airport", "country": "India", "is_active": True},
            {"iata_code": "HYD", "city": "Hyderabad", "name": "Rajiv Gandhi International Airport", "country": "India", "is_active": True},
            {"iata_code": "MAA", "city": "Chennai", "name": "Chennai International Airport", "country": "India", "is_active": True},
            {"iata_code": "CCU", "city": "Kolkata", "name": "Netaji Subhash Chandra Bose International Airport", "country": "India", "is_active": True},
            {"iata_code": "PNQ", "city": "Pune", "name": "Pune Airport", "country": "India", "is_active": True},
            {"iata_code": "GOI", "city": "Goa", "name": "Dabolim / Mopa International Airport", "country": "India", "is_active": True},
            {"iata_code": "COK", "city": "Kochi", "name": "Cochin International Airport", "country": "India", "is_active": True},
            {"iata_code": "AMD", "city": "Ahmedabad", "name": "Sardar Vallabhbhai Patel International Airport", "country": "India", "is_active": True},
            {"iata_code": "JAI", "city": "Jaipur", "name": "Jaipur International Airport", "country": "India", "is_active": True},
            {"iata_code": "DXB", "city": "Dubai", "name": "Dubai International Airport", "country": "UAE", "is_active": True},
            {"iata_code": "LHR", "city": "London", "name": "Heathrow Airport", "country": "United Kingdom", "is_active": True},
            {"iata_code": "SIN", "city": "Singapore", "name": "Singapore Changi Airport", "country": "Singapore", "is_active": True},
            {"iata_code": "BKK", "city": "Bangkok", "name": "Suvarnabhumi Airport", "country": "Thailand", "is_active": True},
            {"iata_code": "DOH", "city": "Doha", "name": "Hamad International Airport", "country": "Qatar", "is_active": True},
        ]
        for ap in seed_airports:
            existing = db.query(models.Airport).filter(models.Airport.iata_code == ap["iata_code"]).first()
            if not existing:
                db.add(models.Airport(**ap))
            else:
                for k, v in ap.items():
                    setattr(existing, k, v)
        db.commit()

        # 14. Scan Logs (Initial seed if empty)
        if db.query(models.ScanLog).count() == 0:
            scans = [models.ScanLog(**s) for s in get_seed_scan_logs()]
            db.add_all(scans)
            db.commit()

        # 15. User Action Logs (Initial seed if empty)
        if db.query(models.UserActionLog).count() == 0:
            actions = [models.UserActionLog(**act) for act in get_seed_user_action_logs()]
            db.add_all(actions)
            db.commit()

        logger.info("Database seeding / upsert synchronization completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        if owns_session:
            db.close()

if __name__ == "__main__":
    force_seed = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force=force_seed)
