import os
import platform
import pytesseract

# path definitions
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "inputs")
output_dir = os.path.join(base_dir, "outputs")  

poppler_path = POPPLER_PATH = r"C:\\poppler-25.12.0\\Library\\bin" if platform.system() == "Windows" else None

TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe" if platform.system() == "Windows" else None


# supported formats
supported_formats = {'.pdf', '.jpg', '.jpeg', '.png'}
