from database.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash


RECORD_COLUMNS = [
    "id", "user_id", "username", "station", "date", "time", "fuel_type",
    "amount", "postcode", "street", "city"
]

USER_COLUMNS = ["id", "username", "is_admin", "is_active", "created_at"]


# ---------------------------
# INSERT
# ---------------------------
def insert_record(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO fuel_records (
        user_id, station, date, time, fuel_type, amount,
        postcode, street, city
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("user_id"),
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
    SET user_id = ?, station = ?, date = ?, time = ?, fuel_type = ?, amount = ?,
        postcode = ?, street = ?, city = ?
    WHERE id = ?
    """, (
        data.get("user_id"),
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


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, username, password_hash, is_admin, is_active, created_at
    FROM users
    WHERE LOWER(username) = LOWER(?)
    """, (username,))

    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    return {
        "id": row[0],
        "username": row[1],
        "password_hash": row[2],
        "is_admin": bool(row[3]),
        "is_active": bool(row[4]),
        "created_at": row[5]
    }


def authenticate_user(username, password):
    user = get_user_by_username(username)
    if not user or not user["is_active"]:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "is_admin": user["is_admin"],
        "is_active": user["is_active"]
    }


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, username, is_admin, is_active, created_at
    FROM users
    WHERE id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()
    return dict(zip(USER_COLUMNS, row)) if row else None


def list_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, username, is_admin, is_active, created_at
    FROM users
    ORDER BY username ASC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(USER_COLUMNS, row)) for row in rows]


def create_user(username, password, is_admin=False):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (username, password_hash, is_admin, is_active)
    VALUES (?, ?, ?, 1)
    """, (username, generate_password_hash(password), 1 if is_admin else 0))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def update_user(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []
    if "password" in data and data.get("password"):
        fields.append("password_hash = ?")
        values.append(generate_password_hash(data["password"]))
    if "is_admin" in data:
        fields.append("is_admin = ?")
        values.append(1 if data.get("is_admin") else 0)
    if "is_active" in data:
        fields.append("is_active = ?")
        values.append(1 if data.get("is_active") else 0)

    if not fields:
        conn.close()
        return False

    values.append(user_id)
    cursor.execute(f"""
    UPDATE users
    SET {", ".join(fields)}
    WHERE id = ?
    """, values)

    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated > 0


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
    user_id = filters.get("user_id")

    if user_id:
        clauses.append("fuel_records.user_id = ?")
        values.append(user_id)
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
    SELECT fuel_records.id, fuel_records.user_id, users.username,
           station, date, time, fuel_type, amount,
           postcode, street, city
    FROM fuel_records
    LEFT JOIN users ON users.id = fuel_records.user_id
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
def get_cost_by_station(filters=None):
    conn = get_connection()
    cursor = conn.cursor()

    where, values = _build_filters(filters)
    cursor.execute(f"""
    SELECT station, SUM(amount)
    FROM fuel_records
    {where}
    GROUP BY station
    ORDER BY SUM(amount) DESC
    """, values)

    rows = cursor.fetchall()
    conn.close()

    return [{"station": r[0], "total": r[1]} for r in rows]


def find_duplicate_records(data, exclude_id=None):
    if not data.get("date") or data.get("amount") in (None, ""):
        return []

    conn = get_connection()
    cursor = conn.cursor()

    values = [data.get("date"), _to_float(data.get("amount"))]
    user_id = data.get("user_id")
    exclude_clause = ""
    user_clause = ""
    if user_id:
        user_clause = "AND fuel_records.user_id = ?"
        values.append(user_id)
    if exclude_id:
        exclude_clause = "AND fuel_records.id != ?"
        values.append(exclude_id)

    cursor.execute(f"""
    SELECT fuel_records.id, fuel_records.user_id, users.username,
           station, date, time, fuel_type, amount,
           postcode, street, city
    FROM fuel_records
    LEFT JOIN users ON users.id = fuel_records.user_id
    WHERE date = ?
      AND ABS(amount - ?) < 0.01
      {user_clause}
      {exclude_clause}
    ORDER BY fuel_records.id DESC
    """, values)

    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(RECORD_COLUMNS, row)) for row in rows]
