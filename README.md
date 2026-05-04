🟢 已完成（Level 1：基础功能）
✅ Flask 后端框架
✅ 文件上传（upload）
✅ SQLite 数据库存储


👉 结论：你已经完成 MVP（Minimum Viable Product）

🟡 半完成（Level 2：核心AI能力）
✅ 基础查询（total）
✅ OCR（已接入 or 可接入）
✅ 简单信息提取（regex）
⚠️ OCR 识别准确率（还没优化）
⚠️ 信息提取（规则还很弱）
⚠️ 查询系统（仅 keyword）
🔴 未完成（Level 3：产品级）
❌ Dashboard（图表）
❌ 用户系统（登录）
❌ GPT 查询
❌ 数据分析能力
❌ 错误处理 / fallback



📌 Overview

This project is an AI-powered fuel receipt recognition system that extracts structured data from unstructured inputs (images or text) and enables intelligent querying.

It serves as a minimum viable product (MVP) for a larger Enterprise Document Intelligence System (RAG-based).



🎯 Features
🧾 1. Receipt Input
Upload fuel receipt images (e.g., gas station receipts)
Manual text input support
🔍 2. OCR & Text Processing
Image → Text using OCR
Text cleaning and normalization
🧠 3. Information Extraction

Extract key fields:

Fuel station name
Date & time
Total amount
Fuel type (Diesel / Super / etc.)
Location
💾 4. Structured Storage
Store extracted data in SQLite database
Ready for analytics and querying
🔎 5. Query System (Retrieval)
Retrieve fuel expenses using SQL-based queries
Example queries:
Total fuel cost
Monthly fuel expenses
Fuel usage by station



🏗️ Architecture
Input (Image / Text)
        ↓
OCR (PaddleOCR)
        ↓
Text Cleaning
        ↓
Information Extraction
        ↓
Database (SQLite)
        ↓
Query Engine (SQL / NLP)
        ↓
Answer Output


🛠️ Tech Stack
Python
Flask (Backend)
PaddleOCR (OCR Engine)
SQLite (Database)
Regex / NLP (Information Extraction)


📁 Project Structure
fuel_ai_app/
│
├── app.py                # 入口（极简）
├── config.py             # 🔥 必加（路径/配置）
│
├── services/
│   ├── ocr_service.py
│   ├── extraction_service.py
│   ├── query_service.py
│
├── database/
│   ├── db.py             # 🔥 DB逻辑
│   ├── models.py         # 🔥 表结构
│
├── uploads/
├── data/
│   └── fuel.db



▶️ How to Run
1. Install dependencies
pip install paddleocr flask opencv-python pillow
2. Run the application
python app.py
3. Test OCR locally
python main.py
📊 Example Output
{
  "station": "Shell",
  "date": "2025-03-01",
  "amount": "58.20 EUR",
  "fuel_type": "Diesel"
}

🔮 Future Work
🔗 Integrate Retrieval-Augmented Generation (RAG)
📂 Add full document management system (DMS)
🧠 LLM-based extraction (better accuracy)
🌍 Multi-language support (German / English / Chinese)
📈 Expense analytics dashboard
🔐 User authentication & role-based access



💡 Use Cases
Personal fuel expense tracking
Fleet management systems
Financial automation
Enterprise document processing



Developed as part of an AI + Data Engineering project
Focused on real-world document intelligence applications