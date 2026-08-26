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
    """
    logger.info("Initializing database schema...")
    if force:
        logger.warning("Force flag enabled: dropping all tables...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if not force:
            existing_airline = db.query(models.Airline).first()
            existing_cat = db.query(models.WayfindingCategory).first()
            if existing_airline and existing_cat:
                logger.info("Database already seeded. Skipping seeder.")
                return

        # 1. Airlines
        if db.query(models.Airline).count() == 0:
            logger.info("Seeding Airlines...")
            airlines = [models.Airline(**a) for a in get_seed_airlines()]
            db.add_all(airlines)
            db.commit()

        # 2. Map Floors
        if db.query(models.MapFloor).count() == 0:
            logger.info("Seeding Map Floors...")
            floors = [models.MapFloor(**f) for f in get_seed_floors()]
            db.add_all(floors)
            db.commit()

        # 3. Map Nodes
        if db.query(models.MapNode).count() == 0:
            logger.info("Seeding Map Nodes...")
            nodes = [models.MapNode(**n) for n in get_seed_map_nodes()]
            db.add_all(nodes)
            db.commit()

        # 4. Map Edges
        if db.query(models.MapEdge).count() == 0:
            logger.info("Seeding Map Edges...")
            edges = [models.MapEdge(**e) for e in get_seed_map_edges()]
            db.add_all(edges)
            db.commit()

        # 5. Kiosks
        if db.query(models.Kiosk).count() == 0:
            logger.info("Seeding Kiosks...")
            kiosks = [models.Kiosk(**k) for k in get_seed_kiosks()]
            db.add_all(kiosks)
            db.commit()

        # 6. Categories & POIs
        if db.query(models.WayfindingCategory).count() == 0:
            logger.info("Seeding Wayfinding Categories...")
            categories = [models.WayfindingCategory(**c) for c in get_seed_categories()]
            db.add_all(categories)
            db.commit()
        else:
            # Backfill any missing subcategories_json
            for seed_cat in get_seed_categories():
                existing = db.query(models.WayfindingCategory).filter(models.WayfindingCategory.id == seed_cat["id"]).first()
                if existing and not existing.subcategories_json:
                    existing.subcategories_json = seed_cat.get("subcategories_json")
                    db.commit()

        if db.query(models.Poi).count() == 0:
            logger.info("Seeding POIs...")
            pois = [models.Poi(**p) for p in get_seed_pois()]
            db.add_all(pois)
            db.commit()

        # 7. Flights
        if db.query(models.Flight).count() == 0:
            logger.info("Seeding Flights...")
            flights = [models.Flight(**fl) for fl in get_seed_flights()]
            db.add_all(flights)
            db.commit()

        # 8. Devices
        if db.query(models.Device).count() == 0:
            logger.info("Seeding Device Fleet...")
            devices = [models.Device(**d) for d in get_seed_devices()]
            db.add_all(devices)
            db.commit()

        # 9. Operators
        if db.query(models.Operator).count() == 0:
            logger.info("Seeding Operators...")
            operators = [models.Operator(**op) for op in get_seed_operators()]
            db.add_all(operators)
            db.commit()

        # 10. Scan Logs
        if db.query(models.ScanLog).count() == 0:
            logger.info("Seeding Scan Logs...")
            scans = [models.ScanLog(**s) for s in get_seed_scan_logs()]
            db.add_all(scans)
            db.commit()

        # 11. User Action Logs
        if db.query(models.UserActionLog).count() == 0:
            logger.info("Seeding User Action Logs...")
            actions = [models.UserActionLog(**act) for act in get_seed_user_action_logs()]
            db.add_all(actions)
            db.commit()

        logger.info("Database seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_seed = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force=force_seed)
