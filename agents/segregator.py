from PIL import Image
import io
import base64
import time
from utils.pdf_parsing import extract_pages
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


def safe_segregate(content, classified_pages, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=content
            )
            return response
        except Exception as e:
            wait = 15 * (2 ** (attempt - 1))  # 15s, 30s, 60s
            print(f"Attempt {attempt}/{max_retries} failed: {e}. Retrying in {wait}s...")
            print(classified_pages)
            if attempt == max_retries:
                raise RuntimeError(f"All {max_retries} attempts failed.") from e
            time.sleep(wait)
                
"""def safe_segregate(client,content,classified_pages):
    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4.1-mini"
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict document classifier. Respond with ONLY one label."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0
            )
            return response.choices[0].message.content

        except Exception as e:
            print("Exception occurred:", e)
            print(classified_pages)
            time.sleep(5)"""

def core_segregation(page, classified_pages):
    prompt = f"""Classify this Insurance document page into exactly one document type of below 9 document type: 
    {','.join(DOC_TYPES)}
    Respond with ONLY the document type, nothing else."""
        
    if page["text"].strip():
        contents = prompt + "\n\n Page content:\n" + page["text"]
    else:
        image_bytes = base64.b64decode(page["image"])
        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            prompt
        ]
 
    response = safe_segregate(client,contents,classified_pages)
    
    result = response.text.strip().lower()
    if result not in DOC_TYPES:
        return "others"
    return result

def segregation(pages):
    classified_pages = {doc_type: [] for doc_type in DOC_TYPES}
    for page in pages:
        doc_type = core_segregation(page,classified_pages)
        classified_pages[doc_type].append(page)
        time.sleep(15)
    return classified_pages

def mock_classify(page):
    text = page["text"].lower()

    if "invoice" in text or "total amount" in text:
        return "itemized_bill"
    elif "discharge" in text:
        return "discharge_summary"
    elif "patient name" in text or "dob" in text:
        return "identity_document"
    else:
        return "other"

def mock_segregation(pages):
    classified_pages = {doc_type: [] for doc_type in DOC_TYPES}
    for page in pages:
        doc_type = mock_classify(page)
        classified_pages[doc_type].append(page)
    return classified_pages
