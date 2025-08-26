# SSO_Project/backend/ocr.py
"""
Reserved for later OCR integration (pytesseract).
Currently not used by the keyword-clustering endpoint.
"""

from PIL import Image, ImageOps, ImageFilter
import pytesseract
import io

def preprocess_pil_image(pil_img: Image.Image) -> Image.Image:
    pil = pil_img.convert("RGB")
    gray = ImageOps.grayscale(pil)
    try:
        gray = ImageOps.autocontrast(gray, cutoff=2)
    except Exception:
        pass
    try:
        gray = gray.filter(ImageFilter.SHARPEN)
    except Exception:
        pass
    return gray

def extract_text_from_pil(pil_image: Image.Image) -> str:
    try:
        pre = preprocess_pil_image(pil_image)
        text = pytesseract.image_to_string(pre)
        return text.strip()
    except Exception:
        try:
            return pytesseract.image_to_string(pil_image).strip()
        except Exception as e2:
            return f"OCR_Error: {str(e2)}"

def extract_text_from_bytes(image_bytes: bytes) -> str:
    try:
        pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return extract_text_from_pil(pil)
    except Exception as e:
        return f"OCR_Error: {str(e)}"
