# db/db_connection.py
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_oO1Y4jVvFkmL",
    "host": "ep-gentle-bonus-ag6liiq4-pooler.c-2.eu-central-1.aws.neon.tech",
    "port": "5432",
    "sslmode": "require"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
