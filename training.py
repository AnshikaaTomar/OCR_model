import os
import cv2
import re
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# path definitions
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "inputs")
output_dir = os.path.join(base_dir, "outputs")  

poppler_path = "C:\\poppler-25.12.0\\Library\\bin"

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


# supported formats
supported_formats = {'.pdf', '.jpg', '.jpeg', '.png'}

# clean text
UNWANTED_PHRASES = [
    "Gautam Buddha University",
    "Greater Noida, U.P.",
    "Greater Noida",
    "Notice",
    "confidential",
    "draft",
]

def find_end_index(lines):
    total = len(lines)
    min_line = int(total * 0.30)

    for i, line in enumerate(lines):
        if i < min_line:
            continue

        stripped = line.strip()

        # Dr. / डा० signature marker
        if re.search(r"(\(Dr\.|\(डा०|\(डा0)", stripped, re.IGNORECASE):
            end_index = i
            for j in range(i - 1, max(i - 4, -1), -1):
                prev = lines[j].strip()
                if not prev:
                    continue
                if len(prev) < 10 and not prev[0].isdigit():
                    end_index = j
                break
            return end_index

        # Designation line without Dr. prefix
        if re.search(r"(Chairperson|नोडल\s+अधिकारी|In-Charge|Finance\s+Officer|Hostel\s+Warden|कुलसचिव|निदेशक)", stripped):
            for j in range(i - 1, max(i - 5, -1), -1):
                prev = lines[j].strip()
                if not prev:
                    continue
                if len(prev) < 50 and not re.search(r"(must|shall|are|were|will|है|हैं|करना|होगा|अनिवार्य)", prev):
                    return j
                else:
                    return i
                break

        # English distribution list
        if re.match(r"(?i)c[o0]py\s*t[o0]\s*[:\-]?", stripped):
            return i

        # Hindi distribution list — प्रतिलिपि
        if re.match(r"(प्रतिलिपि|प्रति\s*[:\-])", stripped):
            return i

        # Hindi bullet distribution list — ०.
        if re.match(r"^[०o0]\s*[\.\-]", stripped):
            return i

    return total


def clean_text(text):

    lines = text.splitlines()

    # FIND END — प्रतिलिपि for Hindi, Copy to for English
    end_index = find_end_index(lines)
    lines = lines[:end_index]
    text = "\n".join(lines)
    
    for phrase in UNWANTED_PHRASES:
        text = re.sub(re.escape(phrase), "", text, flags=re.IGNORECASE)

    text = re.sub(r"[^\x20-\x7E\u0900-\u097F\n]", "", text) # Remove non-ASCII and non-Devanagari characters

    cleaned_lines = []
    for line in text.splitlines():
        if len(line.strip()) == 0:
            cleaned_lines.append(line)
            continue
        letter_ratio = sum(c.isalpha() for c in line) / len(line)
        if letter_ratio >= 0.4:
            cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# preprocessing
def preprocess(pil_image):
    # Convert PIL image to OpenCV format
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Convert to grayscale
    scale = 2.0
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # crisp edges for better readability
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel)
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(gray, h=20)

    # deskew the image
    coords = np.column_stack(np.where(denoised > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = denoised.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        denoised = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, blockSize= 31, C=15)

    return thresh


# OCR 
def extract_text(processed_image):
    config = r"--psm 6 --oem 3"
    text = pytesseract.image_to_string(processed_image, lang="eng+hin", config=config)
    return text.strip()

# load files
def load_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        images = convert_from_path(filepath, dpi=300, poppler_path=poppler_path)
        return images
    else:
        image = Image.open(filepath)
        return [image]
    

# crop the header of the first page
def crop_header(pil_image):
    width, height = pil_image.size
    top_crop = int(height * 0.20)
    return pil_image.crop((0, top_crop, width, height))


# process each file
def process_file(filepath):
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]
    print(f"\nProcessing: {filename}")

    pages = load_file(filepath)
    if not pages:
        return

    all_text = []

    for i, pil_image in enumerate(pages):
        print(f"  → Page {i + 1}/{len(pages)}")

        if i == 0:
            pil_image = crop_header(pil_image)

        processed = preprocess(pil_image)
        text = extract_text(processed)

        # DEBUG BLOCK 
        # debug_path = os.path.join(output_dir, f"{name_without_ext}_raw_page{i+1}.txt")
        # with open(debug_path, "w", encoding="utf-8") as f:
        #     f.write(text)
        # print(f"  Raw output saved: {debug_path}")

        text = clean_text(text)
        all_text.append(f"--- Page {i + 1} ---\n{text}")

    # Join all pages into one string
    final_text = "\n\n".join(all_text)

    # save output
    output_path = os.path.join(output_dir, f"{name_without_ext}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"  ✓ Saved: {output_path}")

# main function
if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)

    # Collect all supported files from input folder
    all_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if os.path.splitext(f)[1].lower() in supported_formats
    ]

    if not all_files:
        print("No supported files found in inputs folder.")
    else:
        print(f"Found {len(all_files)} file(s) to process.")
        for filepath in all_files:
            process_file(filepath)