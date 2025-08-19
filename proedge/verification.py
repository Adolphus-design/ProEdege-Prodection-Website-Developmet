"""import re
from datetime import timedelta, datetime
from django.utils import timezone
import fitz  # PyMuPDF
import pytesseract
from .utils import notify
from pdf2image import convert_from_path

def automated_verify_agent_document(document_instance):
    """
    Auto-verify a single AgentDocument (PDF only):
      - Extract issue date from PDF text (with OCR fallback)
      - FFC expires 3 years after issue date
      - ID is valid 6 months after issue date (stamp recency)
      - Update status, expiry_date, rejection_reason
    """
    issue_date = extract_issue_date_from_document(document_instance.document.path)

    if not issue_date:
        document_instance.status = 'rejected'
        document_instance.rejection_reason = 'Unable to read issue date from document.'
        document_instance.automated_checked = True
        document_instance.save()
        print(f"[auto-verify] Failed to extract issue date from document ID {document_instance.id}")
        return

    today = timezone.now().date()

    if document_instance.document_type == 'FFC':
        expiry_date = issue_date + timedelta(days=3 * 365)
    elif document_instance.document_type == 'ID':
        expiry_date = issue_date + timedelta(days=6 * 30)
    else:
        document_instance.status = 'pending'
        document_instance.rejection_reason = 'Unsupported document type for auto-check.'
        document_instance.automated_checked = True
        document_instance.save()
        return

    document_instance.expiry_date = expiry_date

    if expiry_date < today:
        document_instance.status = 'rejected'
        document_instance.rejection_reason = (
            f'{document_instance.document_type} has expired on {expiry_date}.'
        )
    else:
        document_instance.status = 'approved'
        document_instance.rejection_reason = None

    document_instance.automated_checked = True
    document_instance.save()
    print(f"[auto-verify] Document ID {document_instance.id} verified with status: {document_instance.status}")

    notify(
        document_instance.join_request.agent,
        title=f"Document auto-check: {document_instance.document_type} → {document_instance.status.upper()}",
        message=document_instance.rejection_reason or "Passed automated checks."
    )   
def extract_issue_date_from_document(file_path):
    """
    Extract issue date from a PDF by text parsing.
    If no text found, use OCR to extract text from images of pages.
    Returns: datetime.date or None
    """
    try:
        doc = fitz.open(file_path)
        full_text = []
        for page in doc:
            page_text = page.get_text()
            full_text.append(page_text)
        doc.close()

        text = "\n".join(full_text).strip()

        if text:
            print("[PDF parse] Text extracted from PDF, length:", len(text))
            date = _extract_date_from_text(text)
            if date:
                print("[PDF parse] Found date from text extraction.")
                return date

        print("[PDF parse] No text found or no date found in text extraction. Trying OCR fallback...")

        images = convert_from_path(file_path)
        ocr_text = ""
        for i, image in enumerate(images):
            ocr_page_text = pytesseract.image_to_string(image)
            print(f"[OCR] Page {i+1} OCR text length: {len(ocr_page_text)}")
            ocr_text += ocr_page_text + "\n"

        date = _extract_date_from_text(ocr_text)
        if date:
            print("[OCR] Found date from OCR text.")
            return date

        print("[OCR] No valid date found in OCR text.")
        return None

    except Exception as e:
        print(f"[PDF parse error] {e}")
        return None


def _extract_date_from_text(text):
    """
    Helper to extract a date from text using regex and date parsing.
    """
    labeled_date_patterns = [
        r'(Issue\s*Date|Date\s*of\s*Issue|Issued\s*On)[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})',
        r'(Issue\s*Date|Date\s*of\s*Issue|Issued\s*On)[:\s]+(\d{4}[/-]\d{2}[/-]\d{2})',
        r'(Issue\s*Date|Date\s*of\s*Issue|Issued\s*On)[:\s]+(\d{1,2}\s+\w{3,9}\s+\d{4})',
        r'(Issue\s*Date|Date\s*of\s*Issue|Issued\s*On)[:\s]+(\w{3,9}\s+\d{1,2},?\s+\d{4})',
    ]

    general_date_patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
        r'\b\d{4}[/-]\d{2}[/-]\d{2}\b',
        r'\b\d{1,2}\s+\w{3,9}\s+\d{4}\b',
        r'\b\w{3,9}\s+\d{1,2},?\s+\d{4}\b',
    ]

    for pattern in labeled_date_patterns + general_date_patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            date_str = m.group(2) if len(m.groups()) > 1 else m.group(0)
            parsed = _parse_any_date(date_str.strip())
            if parsed:
                return parsed
    return None


def _parse_any_date(date_str):
    fmts = (
        "%d/%m/%Y", "%d-%m-%Y",
        "%Y-%m-%d", "%Y/%m/%d",
        "%d %B %Y", "%B %d, %Y",
        "%d %b %Y", "%b %d, %Y",
    )
    for fmt in fmts:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None"""
