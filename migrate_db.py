import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "app.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Operators table columns
cols_op = [c[1] for c in cursor.execute("PRAGMA table_info(operators)").fetchall()]
for col, ctype in [
    ("password", "TEXT DEFAULT 'operator123'"),
    ("calls_handled", "INTEGER DEFAULT 0"),
    ("avg_handle_time", "TEXT DEFAULT '2m 30s'"),
    ("resolution_rate", "TEXT DEFAULT '98%'"),
    ("shift", "TEXT DEFAULT 'Morning (06:00 - 14:00)'"),
    ("created_at", "DATETIME")
]:
    if col not in cols_op:
        cursor.execute(f"ALTER TABLE operators ADD COLUMN {col} {ctype}")
        print(f"Added {col} to operators")

# 2. POIs table columns
cols_poi = [c[1] for c in cursor.execute("PRAGMA table_info(pois)").fetchall()]
for col, ctype in [
    ("x_coord", "REAL"),
    ("y_coord", "REAL"),
    ("is_active", "BOOLEAN DEFAULT 1")
]:
    if col not in cols_poi:
        cursor.execute(f"ALTER TABLE pois ADD COLUMN {col} {ctype}")
        print(f"Added {col} to pois")

conn.commit()
conn.close()
print("Database schema migration successful!")
