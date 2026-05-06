import sqlite3
import os
from config import DB_PATH
from werkzeug.security import generate_password_hash

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuel_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
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

    cursor.execute("PRAGMA table_info(fuel_records)")
    columns = [row[1] for row in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE fuel_records ADD COLUMN user_id INTEGER")

    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    row = cursor.fetchone()
    if row:
        admin_id = row[0]
    else:
        cursor.execute("""
        INSERT INTO users (username, password_hash, is_admin, is_active)
        VALUES (?, ?, 1, 1)
        """, ("admin", generate_password_hash("admin123")))
        admin_id = cursor.lastrowid

    cursor.execute("""
    UPDATE fuel_records
    SET user_id = ?
    WHERE user_id IS NULL
    """, (admin_id,))

    conn.commit()
    conn.close()
