# Fuel AI Dashboard

Fuel AI Dashboard is a Flask-based fuel receipt recognition and expense tracking app. It extracts structured fuel purchase data from receipt images with OCR, lets the user review or manually correct low-confidence results, stores clean records in SQLite, and visualizes monthly fuel costs.

The project is currently an MVP for document intelligence and personal fuel expense analytics.

## Current Features

- Upload fuel receipt images.
- Extract OCR text with Tesseract.
- Parse receipt fields with regular expressions:
  - station
  - date
  - time
  - fuel type
  - amount
  - postcode
  - street
  - city
- Review OCR results before saving.
- Show field-level OCR confidence scores.
- Manually enter receipt data when OCR quality is low.
- Detect possible duplicate receipts before saving.
- Save verified records to SQLite.
- Edit existing records from the dashboard.
- Delete bad or unwanted records from the dashboard.
- Filter records by month and station.
- Show total fuel cost.
- Show monthly fuel cost chart.
- Show recent records.
- Ask simple natural-language questions against saved data.

## Tech Stack

- Python
- Flask
- SQLite
- Tesseract OCR via `pytesseract`
- OpenCV for image preprocessing
- Pillow
- Chart.js
- HTML, CSS, JavaScript

## Project Structure

```text
fuel_app/
|-- app.py                       # Flask app and API routes
|-- config.py                    # Project paths and database path
|-- main.py                      # Local OCR / extraction test notes
|-- README.md                    # Project documentation
|-- data/
|   |-- fuel.db                  # SQLite database
|   `-- bad/                     # Low-quality receipt examples
|-- database/
|   |-- db.py                    # Database connection and table setup
|   `-- models.py                # CRUD and analytics queries
|-- processing/
|   |-- cleaner.py               # Text cleaning utilities
|   `-- parser.py                # Parser experiments
|-- routes/
|   |-- query_route.py           # Older route placeholder
|   `-- upload_route.py          # Older route placeholder
|-- services/
|   |-- extraction_service.py    # Regex-based field extraction
|   |-- ocr.py                   # OCR and image preprocessing
|   `-- query_service.py         # Query service wrapper
|-- templates/
|   `-- index.html               # Dashboard frontend
`-- uploads/                     # Uploaded receipt images
```

## Data Flow

```text
Receipt image
    -> image preprocessing
    -> OCR text extraction
    -> regex field extraction
    -> field-level quality check
    -> user review / manual correction
    -> duplicate detection
    -> SQLite storage
    -> dashboard analytics and query
```

## Setup

Install Python dependencies:

```bash
pip install flask pytesseract opencv-python pillow
```

Install Tesseract OCR separately.

On Windows, the current OCR service expects Tesseract at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If your Tesseract path is different, update `services/ocr.py`.

## Run

From the project directory:

```bash
cd fuel_app
python app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

If port `5000` is already in use, run with Flask:

```bash
flask --app app run --port 5001
```

Then open:

```text
http://127.0.0.1:5001/
```

## Dashboard Workflow

1. Upload a receipt image.
2. OCR extracts text and the backend parses structured fields.
3. The dashboard displays extracted values and field confidence scores.
4. If OCR quality is low, manually correct or fill the missing fields.
5. Save the verified record.
6. If a similar record already exists, review the duplicate warning or choose `Save Anyway`.
7. Monthly chart, total cost, and recent records refresh automatically.

## API Endpoints

### Page

```http
GET /
```

Returns the dashboard page.

### Upload Receipt

```http
POST /upload
```

Form data:

```text
file=<receipt image>
```

Returns OCR text, extracted fields, and quality metadata.

Example response:

```json
{
  "data": {
    "station": "Shell",
    "date": "2016-06-24",
    "time": "12:30",
    "fuel_type": "SUPER FUELSAVE",
    "amount": 10.02,
    "postcode": "42389",
    "street": "Dahler Str. 34",
    "city": "Wuppertal"
  },
  "quality": {
    "confidence": 0.86,
    "needs_review": false,
    "missing_fields": [],
    "field_scores": {
      "station": 0.75,
      "date": 0.95,
      "time": 0.75,
      "fuel_type": 0.75,
      "amount": 0.95,
      "city": 0.75
    },
    "preprocessing": "standard"
  }
}
```

### Save Record

```http
POST /save
```

JSON body:

```json
{
  "station": "Shell",
  "date": "2016-06-24",
  "time": "12:30",
  "fuel_type": "SUPER FUELSAVE",
  "amount": 10.02,
  "postcode": "42389",
  "street": "Dahler Str. 34",
  "city": "Wuppertal"
}
```

If a possible duplicate exists, the API returns `409`.

To save anyway:

```json
{
  "station": "Shell",
  "date": "2016-06-24",
  "amount": 10.02,
  "allow_duplicate": true
}
```

### Update Record

```http
PUT /records/<record_id>
```

Updates an existing receipt record.

### Delete Record

```http
DELETE /records/<record_id>
```

Deletes an existing receipt record.

### List Records

```http
GET /records
```

Optional filters:

```http
GET /records?month=2016-06&station=Shell
```

### Total Cost

```http
GET /total
```

Optional filters:

```http
GET /total?month=2016-06&station=Shell
```

### Monthly Cost

```http
GET /monthly
```

Optional station filter:

```http
GET /monthly?station=Shell
```

### Cost By Station

```http
GET /station
```

### Natural-Language Query

```http
POST /ask
```

JSON body:

```json
{
  "question": "total this month"
}
```

Supported examples:

- `total this month`
- `monthly Shell`
- `records 2016-06`
- `total 2016-06 Shell`

This is a lightweight rule-based query parser, not a full LLM or RAG system yet.

## Database Schema

Table: `fuel_records`

```sql
CREATE TABLE IF NOT EXISTS fuel_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station TEXT,
    date TEXT,
    time TEXT,
    fuel_type TEXT,
    amount REAL,
    postcode TEXT,
    street TEXT,
    city TEXT
);
```

## Current Limitations

- OCR accuracy depends heavily on image quality.
- Field extraction is regex-based and may fail on unfamiliar receipt formats.
- Natural-language query support is rule-based and limited.
- Duplicate detection currently uses `date + amount`, so it is useful but not perfect.
- No user authentication yet.
- No automated test suite yet.

## Recommended Next Steps

1. Add automated tests for extraction, duplicate detection, and query filters.
2. Improve OCR preprocessing by trying multiple thresholding strategies and choosing the best result.
3. Add delete support for bad records.
4. Add stronger duplicate detection using station, date, amount, and time.
5. Add better German receipt parsing rules.
6. Add CSV export for monthly expense reports.
7. Add an LLM or RAG layer for more flexible document querying.

## Example Use Case

A user uploads a fuel receipt. The system extracts the date, fuel station, fuel type, amount, and location. If the OCR confidence is low, the dashboard prompts the user to manually correct the data. After saving, the record appears in the recent records table and contributes to the monthly fuel cost chart.
