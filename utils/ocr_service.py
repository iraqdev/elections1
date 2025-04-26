try:
    import cv2
    import pytesseract
    from PIL import Image
    import numpy as np

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCRService:
    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE
        if self.tesseract_available:
            try:
                # تحديد مسار Tesseract (قد تحتاج إلى تغييره بناءً على التثبيت)
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            except:
                pass

    def extract_id_info(self, image_path):
        """
        استخراج المعلومات من صورة بطاقة الهوية
        """
        if not self.tesseract_available:
            return {
                "name": "",
                "id_number": "",
                "address": ""
            }

        try:
            # قراءة الصورة
            img = cv2.imread(image_path)

            # تحسين الصورة
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            # استخراج النص من الصورة
            custom_config = r'--oem 3 --psm 6 -l ara'
            text = pytesseract.image_to_string(gray, config=custom_config)

            # معالجة النص واستخراج المعلومات المطلوبة
            # هذا تطبيق مبسط، في التطبيق الحقيقي ستحتاج إلى خوارزمية أكثر تعقيدًا
            # لاستخراج البيانات بشكل دقيق من البطاقة
            lines = text.split('\n')

            name = ""
            id_number = ""
            address = ""

            # بحث عن الاسم ورقم البطاقة والعنوان
            for line in lines:
                line = line.strip()
                if "الاسم" in line or "اسم" in line:
                    name = line.split(":")[-1].strip() if ":" in line else line
                elif "رقم" in line and ("البطاقة" in line or "الهوية" in line):
                    id_number = ''.join(filter(str.isdigit, line))
                elif "العنوان" in line or "عنوان" in line:
                    address = line.split(":")[-1].strip() if ":" in line else line

            return {
                "name": name,
                "id_number": id_number,
                "address": address
            }
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return {
                "name": "",
                "id_number": "",
                "address": ""
            }