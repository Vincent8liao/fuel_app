from database.db import get_connection


RECORD_COLUMNS = [
    "id", "station", "date", "time", "fuel_type",
    "amount", "postcode", "street", "city"
]


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
        _to_float(data.get("amount")),
        data.get("postcode"),
        data.get("street"),
        data.get("city")
    ))

    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


def update_record(record_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE fuel_records
    SET station = ?, date = ?, time = ?, fuel_type = ?, amount = ?,
        postcode = ?, street = ?, city = ?
    WHERE id = ?
    """, (
        data.get("station"),
        data.get("date"),
        data.get("time"),
        data.get("fuel_type"),
        _to_float(data.get("amount")),
        data.get("postcode"),
        data.get("street"),
        data.get("city"),
        record_id
    ))

    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated > 0


def delete_record(record_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM fuel_records WHERE id = ?", (record_id,))

    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0


def _to_float(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(",", "."))


# ---------------------------
# TOTAL
# ---------------------------
def _build_filters(filters):
    filters = filters or {}
    clauses = []
    values = []

    month = filters.get("month")
    station = filters.get("station")

    if month:
        clauses.append("substr(date, 1, 7) = ?")
        values.append(month)
    if station:
        clauses.append("LOWER(COALESCE(station, '')) LIKE ?")
        values.append(f"%{station.lower()}%")

    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, values


def get_total_cost(filters=None):
    conn = get_connection()
    cursor = conn.cursor()

    where, values = _build_filters(filters)
    cursor.execute(f"SELECT SUM(amount) FROM fuel_records{where}", values)
    row = cursor.fetchone()

    conn.close()
    return row[0] if row and row[0] else 0


# ---------------------------
# ALL RECORDS
# ---------------------------
def get_all_records(filters=None):
    conn = get_connection()
    cursor = conn.cursor()

    where, values = _build_filters(filters)
    cursor.execute(f"""
    SELECT id, station, date, time, fuel_type, amount,
           postcode, street, city
    FROM fuel_records
    {where}
    ORDER BY date DESC, time DESC
    """, values)

    rows = cursor.fetchall()
    conn.close()

    return [dict(zip(RECORD_COLUMNS, row)) for row in rows]


# ---------------------------
# MONTHLY
# ---------------------------
def get_monthly_cost(filters=None):
    conn = get_connection()
    cursor = conn.cursor()

    where, values = _build_filters(filters)
    prefix = "WHERE date IS NOT NULL AND date != '' AND amount IS NOT NULL"
    if where:
        prefix += " AND " + where.replace(" WHERE ", "")

    cursor.execute(f"""
    SELECT substr(date, 1, 7) AS month, SUM(amount)
    FROM fuel_records
    {prefix}
    GROUP BY month
    ORDER BY month ASC
    """, values)

    rows = cursor.fetchall()
    conn.close()

    return [{"month": r[0], "total": round(r[1] or 0, 2)} for r in rows]


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


def find_duplicate_records(data, exclude_id=None):
    if not data.get("date") or data.get("amount") in (None, ""):
        return []

    conn = get_connection()
    cursor = conn.cursor()

    values = [data.get("date"), _to_float(data.get("amount"))]
    exclude_clause = ""
    if exclude_id:
        exclude_clause = "AND id != ?"
        values.append(exclude_id)

    cursor.execute(f"""
    SELECT id, station, date, time, fuel_type, amount,
           postcode, street, city
    FROM fuel_records
    WHERE date = ?
      AND ABS(amount - ?) < 0.01
      {exclude_clause}
    ORDER BY id DESC
    """, values)

    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(RECORD_COLUMNS, row)) for row in rows]
