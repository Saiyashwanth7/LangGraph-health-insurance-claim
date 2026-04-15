import json
import time
from config.llm_setup import client


RETRYABLE_ERRORS = ("429", "500", "503", "quota", "rate")


def safe_generate(content, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=content
            )
            return response.text
        except Exception as e:
            error_msg = str(e).lower()
            is_retryable = any(code in error_msg for code in RETRYABLE_ERRORS)
            if not is_retryable:
                raise
            print(f"Attempt {attempt}/{max_retries} failed: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"All {max_retries} attempts failed.") from e
            time.sleep(15 * (2 ** (attempt - 1)))


def extract_bill_details(classified):
    # Pull both itemized bills and cash receipts for a full financial picture
    bill_pages = classified.get("itemized_bill", [])
    receipt_pages = classified.get("cash_receipt", [])
    pages = bill_pages + receipt_pages

    if not pages:
        return {"itemized_bill": None, "details": "No billing information found"}

    page_text = "\n\n".join(
        [f"Page {p['page_num']}:\n{p.get('text', '')}" for p in pages]
    )

    prompt = f"""
Extract complete billing information from these document pages.

Return ONLY valid JSON with no extra text, markdown, or backticks:

{{
    "hospital_name": "",
    "bill_date": "",
    "patient_name": "",
    "line_items": [
        {{
            "description": "",
            "quantity": null,
            "unit_price": null,
            "amount": null
        }}
    ],
    "subtotal": null,
    "taxes_and_fees": null,
    "total_amount": null,
    "amount_paid": null,
    "amount_due": null,
    "currency": "INR",
    "payment_mode": "",
    "other_details": {{}}
}}

Rules:
- Extract EVERY line item listed across ALL pages.
- For total_amount, use the final grand total. Do not sum yourself if the document states it.
- All monetary values should be numbers (not strings).

DOCUMENT:
{page_text}
"""

    result = safe_generate(prompt)

    try:
        clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    except Exception:
        return {"itemized_bill": None, "raw_output": result}