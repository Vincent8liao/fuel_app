from datetime import date
import re


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

    return {
        "confidence": confidence,
        "needs_review": confidence < 0.7 or any(not data.get(field) for field in REQUIRED_FIELDS),
        "missing_fields": missing,
        "field_scores": field_scores,
        "preprocessing": "standard",
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
        "amount": payload.get("amount"),
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


def parse_question(question):
    text = (question or "").lower()
    filters = {"month": None, "station": None}

    month_match = re.search(r"(20\d{2})[-/. ](0?[1-9]|1[0-2])", text)
    if month_match:
        filters["month"] = f"{month_match.group(1)}-{int(month_match.group(2)):02d}"
    elif "this month" in text or "current month" in text:
        filters["month"] = date.today().strftime("%Y-%m")

    for station in ["shell", "aral", "esso"]:
        if station in text:
            filters["station"] = station
            break

    if "record" in text or "detail" in text:
        intent = "records"
    elif "monthly" in text or "by month" in text:
        intent = "monthly"
    else:
        intent = "total"

    return intent, filters
