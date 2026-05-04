import sqlite3
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuel_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station TEXT,
        date TEXT,
        time TEXT,
        fuel_type TEXT,
        amount REAL,
        location TEXT
    )
    """)

    conn.commit()
    conn.close()