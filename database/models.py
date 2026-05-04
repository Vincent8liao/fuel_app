from database.db import get_connection

def insert_record(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO fuel_records (station, date, time, fuel_type, amount, location)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("station"),
        data.get("date"),
        data.get("time"),
        data.get("fuel_type"),
        data.get("amount"),
        data.get("location")
    ))

    conn.commit()
    conn.close()

def get_total_cost():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM fuel_records")
    result = cursor.fetchone()[0]

    conn.close()
    return result or 0

def get_all_records():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT station, date, time, fuel_type, amount, location
    FROM fuel_records
    ORDER BY date DESC, time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_monthly_cost():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT substr(date, 1, 7) AS month, SUM(amount)
    FROM fuel_records
    GROUP BY month
    ORDER BY month DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows