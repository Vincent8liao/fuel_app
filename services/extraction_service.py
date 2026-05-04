import re

def extract_info(text):
    lines = text.strip().split("\n")

    data = {
        "station": lines[0] if len(lines) > 0 else None,
        "location": lines[-1] if len(lines) > 1 else None,
        "date": None,
        "time": None,
        "fuel_type": None,
        "amount": None
    }

    for line in lines:
        # 日期
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", line)
        if date_match:
            data["date"] = date_match.group()

        # 时间
        time_match = re.search(r"\d{2}:\d{2}", line)
        if time_match:
            data["time"] = time_match.group()

        # 金额
        amount_match = re.search(r"(\d+[.,]\d+)", line)
        if amount_match and ("EUR" in line or "€" in line):
            data["amount"] = float(amount_match.group().replace(",", "."))

        # 油类型
        if any(x in line.lower() for x in ["diesel", "super", "e10", "e5"]):
            data["fuel_type"] = line.strip()

    return data