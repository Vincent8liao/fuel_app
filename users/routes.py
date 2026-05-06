import sqlite3

from flask import Blueprint, jsonify, request, session

from database.models import authenticate_user, create_user, list_users, update_user
from users.auth import admin_required, current_user, public_user


users_bp = Blueprint("users", __name__)


@users_bp.route("/auth/status")
def auth_status():
    return jsonify({"user": public_user(current_user())})


@users_bp.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    user = authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    return jsonify({"user": public_user(user)})


@users_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"logged_out": True})


@users_bp.route("/admin/users")
@admin_required
def admin_users():
    return jsonify(list_users())


@users_bp.route("/admin/users", methods=["POST"])
@admin_required
def admin_create_user():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username:
        return jsonify({"error": "Username is required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    try:
        user_id = create_user(username, password, bool(payload.get("is_admin")))
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409

    return jsonify({"created": True, "id": user_id})


@users_bp.route("/admin/users/<int:user_id>", methods=["PUT"])
@admin_required
def admin_update_user(user_id):
    user = current_user()
    payload = request.get_json(silent=True) or {}

    if user_id == user["id"] and payload.get("is_active") is False:
        return jsonify({"error": "You cannot deactivate your own admin account"}), 400
    if user_id == user["id"] and payload.get("is_admin") is False:
        return jsonify({"error": "You cannot remove your own admin role"}), 400

    if not update_user(user_id, payload):
        return jsonify({"error": "No user update was applied"}), 400

    return jsonify({"updated": True, "id": user_id})
