"input text from ocr.py "
"output the extracted details in a structured format includeing the date, time, amount, and the type of fuel and the location of the tankstelle.the location include the postcode,street,city and the station name if possible"
"algorithm: use regular expression to extract the date, time, amount, fuel type and location from the text"
from services.ocr import extract_text_from_image
import re

def extract_info(text):
    result = {
        "station": None,
        "postcode": None,
        "street": None,
        "city": None,
        "date": None,
        "time": None,
        "fuel_type": None,
        "amount": None
    }

    text_upper = text.upper()

    # -------------------
    # 1️⃣ 加油站品牌（容错）
    # -------------------
    if "SHELL" in text_upper or "SHEL" in text_upper:
        result["station"] = "Shell"
    elif "ARAL" in text_upper:
        result["station"] = "Aral"
    elif "ESSO" in text_upper:
        result["station"] = "Esso"
    elif "TOTAL" in text_upper:
        result["station"] = "Total"

    # -------------------
    # 2️⃣ 日期 + 时间
    # -------------------
    dt_match = re.search(r"(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2})", text)
    if dt_match:
        d, m, y = dt_match.group(1).split(".")
        result["date"] = f"{y}-{m}-{d}"
        result["time"] = dt_match.group(2)

    # -------------------
    # 3️⃣ 金额（优先匹配 Gesamtbetrag）
    # -------------------
    amount_match = re.search(r"(GESAMT.*?)(\d+,\d{2})\s*EUR", text_upper)
    if not amount_match:
        amount_match = re.search(r"(\d+,\d{2})\s*EUR", text_upper)

    if amount_match:
        amount = amount_match.group(2 if len(amount_match.groups()) > 1 else 1)
        result["amount"] = float(amount.replace(",", "."))

    # -------------------
    # 4️⃣ 油类型
    # -------------------
    fuel_match = re.search(r"(SUPER\s\w+|SUPER|DIESEL|E10|E5)", text_upper)
    if fuel_match:
        result["fuel_type"] = fuel_match.group()

    # -------------------
    # 5️⃣ 地址（德国格式）
    # -------------------
    # 邮编 + 城市
    loc_match = re.search(r"(\d{5})\s+([A-ZÄÖÜa-zäöüß]+)", text)
    if loc_match:
        result["postcode"] = loc_match.group(1)
        result["city"] = loc_match.group(2)

    # 街道
    lines = text.split("\n")

    for line in lines:
        street_match = re.search(
            r"([A-ZÄÖÜ][a-zäöüß]+(?:\s[A-ZÄÖÜa-zäöüß]+)*\s(?:Str\.?|Straße|Strasse|Str|Allee|Weg|Platz)\s\d+)",
            line
        )
        if street_match:
            result["street"] = street_match.group(1)
            break

    return result



if __name__ == "__main__":
    # 示例：从图片提取文本并解析
    image_path = r"fuel_app\data\3.JPG"
    text = extract_text_from_image(image_path)
    details = extract_info(text)
    print(details)