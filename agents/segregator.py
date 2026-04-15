import base64
import time
from typing import Dict, List
from google.genai import types
from config.llm_setup import client

DOC_TYPES = [
    "claim_forms",
    "cheque_or_bank_details",
    "identity_document",
    "itemized_bill",
    "discharge_summary",
    "prescription",
    "investigation_report",
    "cash_receipt",
    "other",
]

RETRYABLE_ERRORS = ("429", "500", "503", "quota", "rate")


def safe_segregate(content, max_retries: int = 3):
    """
    Calls LLM safely with retry logic.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=content
            )
            return response.text

        except Exception as e:
            error_msg = str(e).lower()

            # Only retry transient errors
            if not any(code in error_msg for code in RETRYABLE_ERRORS):
                raise

            wait = 2 ** attempt  # exponential backoff (2s, 4s, 8s...)
            print(f"[Retry {attempt}] Error: {e}. Retrying in {wait}s...")

            if attempt == max_retries:
                raise RuntimeError(f"All {max_retries} attempts failed.") from e

            time.sleep(wait)


def classify_page(page: Dict) -> str:
    """
    Classify a single page into one of DOC_TYPES.
    """
    prompt = f"""
Classify this insurance document page into exactly one of the following types:
{', '.join(DOC_TYPES)}

Return ONLY the document type. No explanation.
"""

    # Prefer text; fallback to image only if text is empty
    if page.get("text", "").strip():
        content = prompt + "\n\nPage Content:\n" + page["text"]
    else:
        try:
            image_bytes = base64.b64decode(page["image"])
            content = [
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ]
        except Exception:
            return "other"

    try:
        result = safe_segregate(content).strip().lower()
        return result if result in DOC_TYPES else "other"
    except Exception as e:
        print(f"[Classification Error] Page {page.get('page_num')}: {e}")
        return "other"


def segregation(pages: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classify all pages into document types.
    """
    classified_pages = {doc_type: [] for doc_type in DOC_TYPES}

    for page in pages:
        doc_type = classify_page(page)
        classified_pages[doc_type].append(page)
        time.sleep(15)
    return classified_pages


# ---------------- MOCK VERSION (for testing without LLM) ---------------- #

def mock_classify(page: Dict) -> str:
    text = page.get("text", "").lower()

    if "invoice" in text or "total amount" in text:
        return "itemized_bill"
    elif "discharge" in text:
        return "discharge_summary"
    elif "patient name" in text or "dob" in text:
        return "identity_document"
    else:
        return "other"


def mock_segregation(pages: List[Dict]) -> Dict[str, List[Dict]]:
    classified_pages = {doc_type: [] for doc_type in DOC_TYPES}

    for page in pages:
        doc_type = mock_classify(page)
        classified_pages[doc_type].append(page)

    return classified_pages