"""
Idempotent Database Migration Manager
Safely checks existing table columns and adds missing columns without data loss or exceptions.
"""

from sqlalchemy import text
from app.core.database import engine, Base
from app.core.logging import logger
import app.db.models  # Ensures all models are registered on Base

def run_migrations():
    """
    Executes table creation and non-destructive column additions.
    """
    try:
        # 1. Ensure all tables are created
        Base.metadata.create_all(bind=engine)

        # 2. Check for SQLite column updates
        with engine.connect() as conn:
            # Operators column migrations
            try:
                op_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(operators);")).fetchall()]
                if op_cols:
                    columns_to_add = [
                        ("username", "VARCHAR"),
                        ("employee_code", "VARCHAR"),
                        ("password", "VARCHAR DEFAULT 'operator123'"),
                        ("role", "VARCHAR DEFAULT 'Assistant'"),
                        ("status", "VARCHAR DEFAULT 'available'"),
                        ("supported_languages", "VARCHAR DEFAULT 'English, Hindi'"),
                        ("calls_handled", "INTEGER DEFAULT 0"),
                        ("avg_handle_time", "VARCHAR DEFAULT '2m 30s'"),
                        ("resolution_rate", "VARCHAR DEFAULT '98%'"),
                        ("shift", "VARCHAR DEFAULT 'Morning (06:00 - 14:00)'"),
                        ("created_at", "DATETIME")
                    ]
                    for col_name, col_type in columns_to_add:
                        if col_name not in op_cols:
                            conn.execute(text(f"ALTER TABLE operators ADD COLUMN {col_name} {col_type};"))
                            logger.info(f"Database migration: added {col_name} to operators")
                    conn.execute(text("UPDATE operators SET username = LOWER(REPLACE(name, ' ', '.')) WHERE username IS NULL OR username = '';"))
                    conn.commit()
            except Exception as e:
                logger.warning(f"Notice on operators migration: {e}")

            # Support calls column migrations
            try:
                sc_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(support_calls);")).fetchall()]
                if sc_cols:
                    sc_columns = [
                        ("recording_url", "VARCHAR"),
                        ("recording_duration_seconds", "INTEGER DEFAULT 0"),
                        ("wait_duration_seconds", "INTEGER DEFAULT 0"),
                        ("call_duration_seconds", "INTEGER DEFAULT 0"),
                        ("issue_category", "TEXT"),
                        ("operator_notes", "TEXT"),
                        ("passenger_name", "TEXT"),
                        ("flight_number", "TEXT"),
                        ("pnr", "TEXT")
                    ]
                    for col_name, col_type in sc_columns:
                        if col_name not in sc_cols:
                            conn.execute(text(f"ALTER TABLE support_calls ADD COLUMN {col_name} {col_type};"))
                            logger.info(f"Database migration: added {col_name} to support_calls")
                    conn.commit()
            except Exception as e:
                logger.warning(f"Notice on support_calls migration: {e}")

            # POIs column migrations
            try:
                poi_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(pois);")).fetchall()]
                if poi_cols:
                    poi_columns = [
                        ("x_coord", "REAL"),
                        ("y_coord", "REAL"),
                        ("is_active", "BOOLEAN DEFAULT 1"),
                        ("operating_hours", "TEXT DEFAULT '24/7'"),
                        ("dietary_tags", "TEXT"),
                        ("rating", "REAL DEFAULT 4.5"),
                        ("image_url", "TEXT"),
                        ("badge_label", "TEXT"),
                        ("badge_variant", "TEXT")
                    ]
                    for col_name, col_type in poi_columns:
                        if col_name not in poi_cols:
                            conn.execute(text(f"ALTER TABLE pois ADD COLUMN {col_name} {col_type};"))
                            logger.info(f"Database migration: added {col_name} to pois")
                    conn.commit()
            except Exception as e:
                logger.warning(f"Notice on pois migration: {e}")

            # Wayfinding Categories column migrations
            try:
                cat_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(wayfinding_categories);")).fetchall()]
                if cat_cols:
                    if "subcategories_json" not in cat_cols:
                        conn.execute(text("ALTER TABLE wayfinding_categories ADD COLUMN subcategories_json JSON;"))
                        logger.info("Database migration: added subcategories_json to wayfinding_categories")
                    conn.commit()
            except Exception as e:
                logger.warning(f"Notice on wayfinding_categories migration: {e}")

            # User Action Logs column migrations
            try:
                ual_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(user_action_logs);")).fetchall()]
                if ual_cols:
                    if "metadata_json" not in ual_cols:
                        conn.execute(text("ALTER TABLE user_action_logs ADD COLUMN metadata_json JSON;"))
                        logger.info("Database migration: added metadata_json to user_action_logs")
                    if "created_at" not in ual_cols:
                        conn.execute(text("ALTER TABLE user_action_logs ADD COLUMN created_at DATETIME;"))
                        logger.info("Database migration: added created_at to user_action_logs")
                    conn.commit()
            except Exception as e:
                logger.warning(f"Notice on user_action_logs migration: {e}")

            # Screen Annotations column migrations
            try:
                sa_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(screen_annotations);")).fetchall()]
                if sa_cols:
                    if "stroke_data" not in sa_cols:
                        conn.execute(text("ALTER TABLE screen_annotations ADD COLUMN stroke_data JSON;"))
                        logger.info("Database migration: added stroke_data to screen_annotations")
                    if "created_at" not in sa_cols:
                        conn.execute(text("ALTER TABLE screen_annotations ADD COLUMN created_at DATETIME;"))
                        logger.info("Database migration: added created_at to screen_annotations")
                    conn.commit()
            except Exception as e:
                logger.warning(f"Notice on screen_annotations migration: {e}")

            # Devices column migrations
            try:
                dev_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(devices);")).fetchall()]
                if dev_cols:
                    if "runtime_env" not in dev_cols:
                        conn.execute(text("ALTER TABLE devices ADD COLUMN runtime_env VARCHAR DEFAULT 'browser';"))
                        logger.info("Database migration: added runtime_env to devices")
                    conn.commit()
            except Exception as e:
                logger.warning(f"Notice on devices migration: {e}")

        logger.info("Database schema migration verification completed.")

    except Exception as e:
        logger.error(f"Error during migration execution: {e}")

if __name__ == "__main__":
    run_migrations()
