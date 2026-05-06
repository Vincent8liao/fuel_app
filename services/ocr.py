"in this service we will use the tesseract ocr engine to extract text from images "
import cv2
import pytesseract
from PIL import Image
import os
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------------
# 图像预处理（关键）
# ---------------------------
def image_processing(image_path):
    img = cv2.imread(image_path)

    # 放大（提升识别率）
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 去噪
    gray = cv2.medianBlur(gray, 3)

    # 二值化（核心）
    _, thresh = cv2.threshold(gray,150, 255, cv2.THRESH_BINARY)

    return thresh


# ---------------------------
# OCR
# ---------------------------
def extract_text_from_image(image_path):
    try:
        processed_img = image_processing(image_path)

        # 👉 OCR 参数（很重要）
        config = r'--oem 3 --psm 6'

        text = pytesseract.image_to_string(
            processed_img,
            lang="eng+deu",   # 德国票据必须加 deu
            config=config
        )

        return text

    except Exception as e:
        print("OCR Error:", e)
        return ""

"if the "
# ---------------------------
# 测试
# ---------------------------
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    image_path = os.path.join(base_dir, "data/bad", "4.jpg")

    text = extract_text_from_image(image_path)
    print("📄 Extracted Text:\n", text)