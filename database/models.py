from database.db import get_connection


# ---------------------------
# INSERT
# ---------------------------
def insert_record(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO fuel_records (
        station, date, time, fuel_type, amount,
        postcode, street, city
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("station"),
        data.get("date"),
        data.get("time"),
        data.get("fuel_type"),
        data.get("amount"),
        data.get("postcode"),
        data.get("street"),
        data.get("city")
    ))

    conn.commit()
    conn.close()


# ---------------------------
# TOTAL
# ---------------------------
def get_total_cost():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM fuel_records")
    row = cursor.fetchone()

    conn.close()
    return row[0] if row and row[0] else 0


# ---------------------------
# ALL RECORDS
# ---------------------------
def get_all_records():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT station, date, time, fuel_type, amount,
           postcode, street, city
    FROM fuel_records
    ORDER BY date DESC, time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    columns = ["station", "date", "time", "fuel_type",
               "amount", "postcode", "street", "city"]

    return [dict(zip(columns, row)) for row in rows]


# ---------------------------
# MONTHLY
# ---------------------------
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

    return [{"month": r[0], "total": r[1]} for r in rows]


# ---------------------------
# BY STATION
# ---------------------------
def get_cost_by_station():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT station, SUM(amount)
    FROM fuel_records
    GROUP BY station
    ORDER BY SUM(amount) DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [{"station": r[0], "total": r[1]} for r in rows]