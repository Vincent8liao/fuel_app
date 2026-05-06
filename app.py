from flask import Flask, request, jsonify
from database.db import init_db
from database.models import insert_record, update_record, delete_record, find_duplicate_records
from services.ocr import extract_text_from_image
from services.extraction_service import extract_info
from services.query_service import *
from flask import render_template
from werkzeug.utils import secure_filename
import os
import re
from datetime import date

app = Flask(__name__)

# 初始化数据库
init_db()

REQUIRED_FIELDS = ["date", "amount"]
IMPORTANT_FIELDS = ["station", "date", "time", "fuel_type", "amount", "city"]


def analyze_quality(data, text):
    text_length = len((text or "").strip())
    field_scores = {}
    for field in IMPORTANT_FIELDS:
        value = data.get(field)
        if value in (None, ""):
            field_scores[field] = 0
        elif field in REQUIRED_FIELDS:
            field_scores[field] = 0.95
        else:
            field_scores[field] = 0.75 if text_length >= 20 else 0.45

    present = [field for field, score in field_scores.items() if score > 0]
    missing = [field for field in IMPORTANT_FIELDS if field not in present]
    confidence = round(sum(field_scores.values()) / len(IMPORTANT_FIELDS), 2)

    if text_length < 20:
        confidence = min(confidence, 0.25)

    needs_review = confidence < 0.7 or any(not data.get(field) for field in REQUIRED_FIELDS)
    return {
        "confidence": confidence,
        "needs_review": needs_review,
        "missing_fields": missing,
        "field_scores": field_scores,
        "preprocessing": "standard"
    }


def normalize_record(payload):
    return {
        "station": (payload.get("station") or "").strip() or None,
        "postcode": (payload.get("postcode") or "").strip() or None,
        "street": (payload.get("street") or "").strip() or None,
        "city": (payload.get("city") or "").strip() or None,
        "date": (payload.get("date") or "").strip() or None,
        "time": (payload.get("time") or "").strip() or None,
        "fuel_type": (payload.get("fuel_type") or "").strip() or None,
        "amount": payload.get("amount")
    }


def validate_record(data):
    errors = {}
    if not data.get("date"):
        errors["date"] = "Date is required."
    if data.get("amount") in (None, ""):
        errors["amount"] = "Amount is required."
    else:
        try:
            data["amount"] = float(str(data.get("amount")).replace(",", "."))
        except ValueError:
            errors["amount"] = "Amount must be a number."

    return errors


def request_filters():
    return {
        "month": (request.args.get("month") or "").strip() or None,
        "station": (request.args.get("station") or "").strip() or None
    }


def parse_question(question):
    text = (question or "").lower()
    filters = {"month": None, "station": None}

    month_match = re.search(r"(20\d{2})[-/.年 ](0?[1-9]|1[0-2])", text)
    if month_match:
        filters["month"] = f"{month_match.group(1)}-{int(month_match.group(2)):02d}"
    elif "this month" in text or "current month" in text or "这个月" in text or "本月" in text:
        filters["month"] = date.today().strftime("%Y-%m")

    for station in ["shell", "aral", "esso"]:
        if station in text:
            filters["station"] = station
            break

    if "record" in text or "明细" in text or "记录" in text:
        intent = "records"
    elif "monthly" in text or "每月" in text or "月度" in text:
        intent = "monthly"
    else:
        intent = "total"

    return intent, filters


# ---------------------------
# 上传并识别
# ---------------------------
@app.route("/upload", methods=["POST"])
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
        "quality": quality
    })


@app.route("/save", methods=["POST"])
def save():
    payload = request.get_json(silent=True) or {}
    data = normalize_record(payload)
    errors = validate_record(data)
    if errors:
        return jsonify({"errors": errors, "data": data}), 400

    duplicates = find_duplicate_records(data)
    if duplicates and not payload.get("allow_duplicate"):
        return jsonify({
            "duplicate": True,
            "duplicates": duplicates,
            "message": "A similar record already exists."
        }), 409

    record_id = insert_record(data)

    return jsonify({"saved": True, "id": record_id, "data": data})


@app.route("/records/<int:record_id>", methods=["PUT"])
def update(record_id):
    payload = request.get_json(silent=True) or {}
    data = normalize_record(payload)
    errors = validate_record(data)
    if errors:
        return jsonify({"errors": errors, "data": data}), 400

    duplicates = find_duplicate_records(data, exclude_id=record_id)
    if duplicates and not payload.get("allow_duplicate"):
        return jsonify({
            "duplicate": True,
            "duplicates": duplicates,
            "message": "A similar record already exists."
        }), 409

    if not update_record(record_id, data):
        return jsonify({"error": "Record not found"}), 404

    return jsonify({"saved": True, "id": record_id, "data": data})


@app.route("/records/<int:record_id>", methods=["DELETE"])
def delete(record_id):
    if not delete_record(record_id):
        return jsonify({"error": "Record not found"}), 404

    return jsonify({"deleted": True, "id": record_id})


# ---------------------------
# 查询接口
# ---------------------------
@app.route("/total")
def total():
    return jsonify(query_total(request_filters()))

@app.route("/records")
def records():
    return jsonify(query_all(request_filters()))

@app.route("/monthly")
def monthly():
    return jsonify(query_monthly({"station": request_filters().get("station")}))

@app.route("/station")
def station():
    return jsonify(query_by_station())

@app.route("/ask", methods=["POST"])
def ask():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")
    intent, filters = parse_question(question)

    if intent == "monthly":
        data = query_monthly(filters)
        return jsonify({
            "answer": "Monthly fuel cost is shown below.",
            "intent": intent,
            "filters": filters,
            "data": data
        })

    if intent == "records":
        data = query_all(filters)
        return jsonify({
            "answer": f"Found {len(data)} matching records.",
            "intent": intent,
            "filters": filters,
            "data": data
        })

    total_data = query_total(filters)
    return jsonify({
        "answer": f"Total fuel cost is {total_data['total']:.2f} EUR.",
        "intent": intent,
        "filters": filters,
        "data": total_data
    })

@app.route("/")
def index():
    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True)
