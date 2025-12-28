# ocr extraction engine

import pytesseract
from PIL import Image
import pdfplumber

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text 

def extract_text_via_ocr(path):
    images = []
    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            img = page.to_image(resolution=300)
            pil_img = Image.fromarray(img.original)
            text += pytesseract.image_o_string(pil_img)
    return text
