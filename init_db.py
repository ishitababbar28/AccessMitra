"""
Database initialization and seeding CLI script for AccessMitra.
Run:
    python init_db.py
Or with MySQL setup flags.
"""
import sys
import logging
from database import init_db, get_engine, active_db_type, Scheme, Helpline, GrievanceAuthority, AccessibilityResource, get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main():
    print("=" * 60)
    print("   AccessMitra - Indian Accessibility Portal DB Setup")
    print("=" * 60)

    try:
        init_db(seed=True)
        db = get_db()
        schemes = db.query(Scheme).count()
        helplines = db.query(Helpline).count()
        authorities = db.query(GrievanceAuthority).count()
        resources = db.query(AccessibilityResource).count()
        db.close()

        print("\n[SUCCESS] Database initialized successfully!")
        print(f"Backend Engine: {active_db_type}")
        print(f"Schemes: {schemes}")
        print(f"Helplines: {helplines}")
        print(f"Grievance Authorities: {authorities}")
        print(f"Accessibility Resources: {resources}")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
