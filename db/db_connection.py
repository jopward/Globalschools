# db/db_connection.py
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "schoolsdb",
    "user": "u0_a223",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    """يرجع الاتصال بقاعدة البيانات"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
