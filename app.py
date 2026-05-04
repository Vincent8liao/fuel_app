from flask import Flask, request, jsonify
from database.db import init_db
from database.models import insert_record
from services.ocr import extract_text_from_image
from services.extraction_service import extract_info
from services.query_service import *
from flask import render_template
import os

app = Flask(__name__)

# 初始化数据库
init_db()


# ---------------------------
# 上传并识别
# ---------------------------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    path = os.path.join("uploads", file.filename)
    file.save(path)

    text = extract_text_from_image(path)
    data = extract_info(text)

    insert_record(data)

    return jsonify(data)


# ---------------------------
# 查询接口
# ---------------------------
@app.route("/total")
def total():
    return jsonify(query_total())

@app.route("/records")
def records():
    return jsonify(query_all())

@app.route("/monthly")
def monthly():
    return jsonify(query_monthly())

@app.route("/station")
def station():
    return jsonify(query_by_station())

@app.route("/")
def index():
    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True)