import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'accessmitra_secret_production_key_2026')
    PORT = int(os.getenv('PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'accessmitra')

    DB_BACKEND = os.getenv('DB_BACKEND', 'mysql').lower()
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'accessmitra.db')

    @classmethod
    def get_mysql_uri(cls):
        pwd = f":{cls.MYSQL_PASSWORD}" if cls.MYSQL_PASSWORD else ""
        return f"mysql+pymysql://{cls.MYSQL_USER}{pwd}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DB}?charset=utf8mb4"

    @classmethod
    def get_sqlite_uri(cls):
        # Resolve path relative to project root
        base_dir = os.path.abspath(os.path.dirname(__file__))
        db_file = os.path.join(base_dir, cls.SQLITE_DB_PATH)
        return f"sqlite:///{db_file}"
