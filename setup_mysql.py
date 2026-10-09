"""
Interactive / Automatic MySQL database creation and setup script for AccessMitra.
Allows the user to specify or test their MySQL root password, creates the database
'accessmitra' with utf8mb4 encoding, and applies the schema.
"""
import os
import sys
import getpass
import pymysql
from dotenv import load_dotenv, set_key

load_dotenv()

def setup_mysql():
    print("=" * 60)
    print("   AccessMitra - MySQL Database Setup Utility")
    print("=" * 60)

    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    user = os.getenv('MYSQL_USER', 'root')
    existing_pwd = os.getenv('MYSQL_PASSWORD', '')

    print(f"Connecting to MySQL server at {host}:{port} as user '{user}'...")
    pwd = existing_pwd

    # If existing password fails or is empty, we can test it
    conn = None
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=pwd)
        print("[✓] Connected to MySQL successfully using configured password.")
    except Exception as e:
        print(f"[!] Direct connection failed: {e}")
        if sys.stdin.isatty():
            pwd = getpass.getpass("Enter your MySQL root password (or press Enter if blank): ")
            try:
                conn = pymysql.connect(host=host, port=port, user=user, password=pwd)
                print("[✓] Connection successful!")
                # Update .env
                set_key(".env", "MYSQL_PASSWORD", pwd)
                print("[✓] Updated MYSQL_PASSWORD in .env")
            except Exception as ex2:
                print(f"[ERROR] Could not connect: {ex2}")
                print("Tip: You can still run AccessMitra immediately using the built-in SQLite engine.")
                return False
        else:
            print("Non-interactive terminal detected. Skipping password prompt.")
            print("Tip: You can edit .env manually with MYSQL_PASSWORD=your_password")
            return False

    try:
        with conn.cursor() as cursor:
            print("Creating database 'accessmitra' if not exists...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS accessmitra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute("USE accessmitra;")
            print("[✓] Database 'accessmitra' is ready.")
        conn.close()

        # Now run init_db
        from database import init_db
        init_db(seed=True)
        print("[✓] MySQL tables created and seeded with verified Indian Government schemes!")
        print("=" * 60)
        return True
    except Exception as err:
        print(f"[ERROR] Failed during database setup: {err}")
        return False

if __name__ == '__main__':
    setup_mysql()
