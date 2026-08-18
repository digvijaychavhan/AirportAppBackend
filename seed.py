"""
Database Seeder CLI Entrypoint
"""

import sys
from app.db.seed.seeder import seed_database

if __name__ == "__main__":
    force_flag = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force=force_flag)
