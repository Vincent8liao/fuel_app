from functools import wraps

from flask import jsonify, request, session

from database.models import get_user_by_id


def public_user(user):
    if not user:
        return None
    return {
        "id": user["id"],
        "username": user["username"],
        "is_admin": bool(user["is_admin"]),
        "is_active": bool(user.get("is_active", True)),
    }


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user["is_active"]:
            session.clear()
            return jsonify({"error": "Login required"}), 401
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user["is_active"]:
            session.clear()
            return jsonify({"error": "Login required"}), 401
        if not user["is_admin"]:
            return jsonify({"error": "Admin access required"}), 403
        return func(*args, **kwargs)

    return wrapper


def target_user_id(payload=None):
    user = current_user()
    requested = None
    if payload:
        requested = payload.get("user_id")
    requested = requested or request.args.get("user_id")

    if user["is_admin"] and requested:
        return int(requested)
    return user["id"]
