import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from database.models import delete_record, find_duplicate_records, insert_record, update_record
from fuel.helpers import analyze_quality, normalize_record, parse_question, validate_record
from services.extraction_service import extract_info
from services.ocr import extract_text_from_image
from services.query_service import query_all, query_by_station, query_monthly, query_total
from users.auth import login_required, target_user_id


fuel_bp = Blueprint("fuel", __name__)


def request_filters():
    return {
        "user_id": target_user_id(),
        "month": (request.args.get("month") or "").strip() or None,
        "station": (request.args.get("station") or "").strip() or None,
    }


def record_visible(record_id, user_id):
    return any(record["id"] == record_id for record in query_all({"user_id": user_id}))


@fuel_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400

    os.makedirs("uploads", exist_ok=True)
    filename = secure_filename(file.filename)
    path = os.path.join("uploads", filename)
    file.save(path)

    text = extract_text_from_image(path)
    data = extract_info(text)
    quality = analyze_quality(data, text)

    return jsonify({
        "data": data,
        "ocr_text": text,
        "quality": quality,
    })


@fuel_bp.route("/save", methods=["POST"])
@login_required
def save():
    payload = request.get_json(silent=True) or {}
    data = normalize_record(payload)
    data["user_id"] = target_user_id(payload)
    errors = validate_record(data)
    if errors:
        return jsonify({"errors": errors, "data": data}), 400

    duplicates = find_duplicate_records(data)
    if duplicates and not payload.get("allow_duplicate"):
        return jsonify({
            "duplicate": True,
            "duplicates": duplicates,
            "message": "A similar record already exists.",
        }), 409

    record_id = insert_record(data)
    return jsonify({"saved": True, "id": record_id, "data": data})


@fuel_bp.route("/records/<int:record_id>", methods=["PUT"])
@login_required
def update(record_id):
    payload = request.get_json(silent=True) or {}
    data = normalize_record(payload)
    data["user_id"] = target_user_id(payload)
    errors = validate_record(data)
    if errors:
        return jsonify({"errors": errors, "data": data}), 400

    if not record_visible(record_id, data["user_id"]):
        return jsonify({"error": "Record not found"}), 404

    duplicates = find_duplicate_records(data, exclude_id=record_id)
    if duplicates and not payload.get("allow_duplicate"):
        return jsonify({
            "duplicate": True,
            "duplicates": duplicates,
            "message": "A similar record already exists.",
        }), 409

    if not update_record(record_id, data):
        return jsonify({"error": "Record not found"}), 404

    return jsonify({"saved": True, "id": record_id, "data": data})


@fuel_bp.route("/records/<int:record_id>", methods=["DELETE"])
@login_required
def delete(record_id):
    user_id = target_user_id()
    if not record_visible(record_id, user_id):
        return jsonify({"error": "Record not found"}), 404

    if not delete_record(record_id):
        return jsonify({"error": "Record not found"}), 404

    return jsonify({"deleted": True, "id": record_id})


@fuel_bp.route("/total")
@login_required
def total():
    return jsonify(query_total(request_filters()))


@fuel_bp.route("/records")
@login_required
def records():
    return jsonify(query_all(request_filters()))


@fuel_bp.route("/monthly")
@login_required
def monthly():
    filters = request_filters()
    return jsonify(query_monthly({
        "user_id": filters.get("user_id"),
        "station": filters.get("station"),
    }))


@fuel_bp.route("/station")
@login_required
def station():
    return jsonify(query_by_station(request_filters()))


@fuel_bp.route("/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")
    intent, filters = parse_question(question)
    filters["user_id"] = target_user_id(payload)

    if intent == "monthly":
        data = query_monthly(filters)
        return jsonify({
            "answer": "Monthly fuel cost is shown below.",
            "intent": intent,
            "filters": filters,
            "data": data,
        })

    if intent == "records":
        data = query_all(filters)
        return jsonify({
            "answer": f"Found {len(data)} matching records.",
            "intent": intent,
            "filters": filters,
            "data": data,
        })

    total_data = query_total(filters)
    return jsonify({
        "answer": f"Total fuel cost is {total_data['total']:.2f} EUR.",
        "intent": intent,
        "filters": filters,
        "data": total_data,
    })
