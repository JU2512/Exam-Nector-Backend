# app/services/ocr_service.py

from fastapi import UploadFile
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"


def extract_text_from_file(file: UploadFile) -> str:
    """
    Main entry point.
    Accepts an uploaded file and returns fully cleaned, AI-ready text.
    """
    filename = file.filename.lower()
    file_bytes = file.file.read()

    if filename.endswith(".pdf"):
        raw_text = _extract_from_pdf(file_bytes)

    elif filename.endswith((".png", ".jpg", ".jpeg")):
        raw_text = _extract_from_image(file_bytes)

    else:
        return ""

    cleaned_text = _clean_text(raw_text)
    validated_text = _validate_text(cleaned_text)

    return validated_text


# -------------------------------------------------------------------
# Internal helpers
# -------------------------------------------------------------------

def _extract_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF.
    - First tries text-based extraction
    - Falls back to OCR for scanned pages
    """
    import io
    import pdfplumber
    import pytesseract

    extracted_text = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text and page_text.strip():
                extracted_text.append(page_text)
            else:
                # OCR fallback for scanned page
                page_image = page.to_image(resolution=300).original
                ocr_text = pytesseract.image_to_string(
                    page_image,
                    lang="eng"
                )
                if ocr_text.strip():
                    extracted_text.append(ocr_text)

    return "\n".join(extracted_text).strip()


def _extract_from_image(file_bytes: bytes) -> str:
    """
    OCR extraction for image files (JPG / PNG)
    """
    import io
    from PIL import Image
    import pytesseract

    image = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    return text.strip()


def _clean_text(text: str) -> str:
    """
    Normalize and clean OCR text to make it AI-ready.
    """
    import re

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove extra spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove space before punctuation
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)

    # Rebuild paragraphs
    lines = [line.strip() for line in text.split("\n")]
    paragraphs = []

    current_para = ""
    for line in lines:
        if not line:
            if current_para:
                paragraphs.append(current_para.strip())
                current_para = ""
        else:
            if current_para:
                current_para += " " + line
            else:
                current_para = line

    if current_para:
        paragraphs.append(current_para.strip())

    return "\n\n".join(paragraphs).strip()


def _validate_text(text: str) -> str:
    """
    Validate extracted text before sending to AI.
    """
    if not text:
        return ""

    # Minimum length check
    if len(text) < 50:
        return ""

    # Check if text is mostly alphabetic (English-like)
    alpha_chars = sum(c.isalpha() for c in text)
    total_chars = len(text)

    if total_chars == 0:
        return ""

    if (alpha_chars / total_chars) < 0.4:
        return ""

    return text
