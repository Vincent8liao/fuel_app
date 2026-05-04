from database.db import init_db
from database.models import insert_record, get_total_cost
from services.extraction_service import extract_info
from flask import Flask, render_template, request
from database.db import init_db
from database.models import insert_record, get_total_cost
from services.extraction_service import extract_info
from database.models import (
    insert_record,
    get_total_cost,
    get_all_records,
    get_monthly_cost
)
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    extracted = None

    if request.method == "POST":
        text = request.form.get("fuel_text")

        if text:
            data = extract_info(text)
            insert_record(data)
            extracted = data

    total = get_total_cost()
    records = get_all_records()
    monthly = get_monthly_cost()

    return render_template(
        "index.html",
        total=total,
        extracted=extracted,
        records=records,
        monthly=monthly
    )
