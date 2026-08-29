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

def seed_database(force: bool = False):
    """
    Seeds initial database tables with domain entities.
    If force=True, drops and recreates all tables.
    Otherwise, performs idempotent upserts across all domain entities.
    """
    logger.info("Initializing database schema...")
    if force:
        logger.warning("Force flag enabled: dropping all tables...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

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

        # 11. Scan Logs (Initial seed if empty)
        if db.query(models.ScanLog).count() == 0:
            scans = [models.ScanLog(**s) for s in get_seed_scan_logs()]
            db.add_all(scans)
            db.commit()

        # 12. User Action Logs (Initial seed if empty)
        if db.query(models.UserActionLog).count() == 0:
            actions = [models.UserActionLog(**act) for act in get_seed_user_action_logs()]
            db.add_all(actions)
            db.commit()

        logger.info("Database seeding / upsert synchronization completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_seed = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force=force_seed)
