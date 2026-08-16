import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "app.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Operators table columns
cols_op = [c[1] for c in cursor.execute("PRAGMA table_info(operators)").fetchall()]
for col, ctype in [
    ("username", "VARCHAR"),
    ("employee_code", "VARCHAR"),
    ("password", "TEXT DEFAULT 'operator123'"),
    ("role", "TEXT DEFAULT 'Assistant'"),
    ("status", "TEXT DEFAULT 'available'"),
    ("supported_languages", "TEXT DEFAULT 'English, Hindi'"),
    ("calls_handled", "INTEGER DEFAULT 0"),
    ("avg_handle_time", "TEXT DEFAULT '2m 30s'"),
    ("resolution_rate", "TEXT DEFAULT '98%'"),
    ("shift", "TEXT DEFAULT 'Morning (06:00 - 14:00)'"),
    ("created_at", "DATETIME")
]:
    if col not in cols_op:
        cursor.execute(f"ALTER TABLE operators ADD COLUMN {col} {ctype}")
        print(f"Added {col} to operators")

cursor.execute("UPDATE operators SET username = LOWER(REPLACE(name, ' ', '.')) WHERE username IS NULL OR username = '';")

# 2. Support calls table columns
cols_sc = [c[1] for c in cursor.execute("PRAGMA table_info(support_calls)").fetchall()]
for col, ctype in [
    ("recording_url", "VARCHAR"),
    ("recording_duration_seconds", "INTEGER DEFAULT 0"),
    ("wait_duration_seconds", "INTEGER DEFAULT 0"),
    ("call_duration_seconds", "INTEGER DEFAULT 0"),
    ("issue_category", "TEXT"),
    ("operator_notes", "TEXT"),
    ("passenger_name", "TEXT"),
    ("flight_number", "TEXT"),
    ("pnr", "TEXT")
]:
    if col not in cols_sc:
        cursor.execute(f"ALTER TABLE support_calls ADD COLUMN {col} {ctype}")
        print(f"Added {col} to support_calls")

# 3. POIs table columns
cols_poi = [c[1] for c in cursor.execute("PRAGMA table_info(pois)").fetchall()]
for col, ctype in [
    ("x_coord", "REAL"),
    ("y_coord", "REAL"),
    ("is_active", "BOOLEAN DEFAULT 1"),
    ("operating_hours", "TEXT DEFAULT '24/7'"),
    ("dietary_tags", "TEXT"),
    ("rating", "REAL DEFAULT 4.5"),
    ("image_url", "TEXT"),
    ("badge_label", "TEXT"),
    ("badge_variant", "TEXT")
]:
    if col not in cols_poi:
        cursor.execute(f"ALTER TABLE pois ADD COLUMN {col} {ctype}")
        print(f"Added {col} to pois")

conn.commit()
conn.close()
print("Database schema migration successful!")
