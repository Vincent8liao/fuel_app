import sqlite3
import os

DB_PATH = os.path.join("data", "fuel.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

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
        postcode TEXT,
        street TEXT,
        city TEXT
    )
    """)

    conn.commit()
    conn.close()