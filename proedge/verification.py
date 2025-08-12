from datetime import timedelta
from django.utils import timezone

def automated_verify_agent_document(document_instance):
    """
    Automated verification of agent document:
    - Extracts issue date (mocked here, replace with real extraction)
    - Checks expiry based on document type:
      - FFC expires 3 years after issue date
      - ID expires 6 months after issue date
    - Updates document status and rejection_reason accordingly
    """

    # TODO: Replace this mock extraction with actual OCR or metadata extraction
    issue_date = extract_issue_date_from_document(document_instance.document.path)

    if not issue_date:
        document_instance.status = 'rejected'
        document_instance.rejection_reason = 'Unable to read issue date from document.'
        document_instance.automated_checked = True
        document_instance.save()
        return

    today = timezone.now().date()

    if document_instance.document_type == 'FFC':
        expiry_date = issue_date + timedelta(days=3*365)
    elif document_instance.document_type == 'ID':
        expiry_date = issue_date + timedelta(days=6*30)  # Approx 6 months
    else:
        # Unknown document type, keep pending for manual review
        document_instance.status = 'pending'
        document_instance.rejection_reason = 'Document type not supported for automatic verification.'
        document_instance.automated_checked = True
        document_instance.save()
        return

    document_instance.expiry_date = expiry_date

    if expiry_date < today:
        document_instance.status = 'rejected'
        document_instance.rejection_reason = f'{document_instance.document_type} document has expired on {expiry_date}.'
    else:
        document_instance.status = 'approved'
        document_instance.rejection_reason = None

    document_instance.automated_checked = True
    document_instance.save()

def extract_issue_date_from_document(file_path):
    """
    Placeholder function for extracting issue date from the document.
    This could use OCR, metadata, or user input.
    For now, returns None to simulate failure.
    """
    # TODO: Implement actual extraction logic
    return None
