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


def extract_discharge_details(classified):
    pages = classified.get("discharge_summary", [])

    if not pages:
        return {"discharge_summary": None, "details": "No discharge summary found"}

    page_text = "\n\n".join(
        [f"Page {p['page_num']}:\n{p.get('text', '')}" for p in pages]
    )

    prompt = f"""
Extract discharge summary information from these document pages.

Return ONLY valid JSON with no extra text, markdown, or backticks:

{{
    "patient_name": "",
    "admission_date": "",
    "discharge_date": "",
    "length_of_stay_days": null,
    "admitting_diagnosis": "",
    "final_diagnosis": [],
    "treating_physician": "",
    "department": "",
    "procedures_performed": [],
    "medications_on_discharge": [],
    "follow_up_instructions": "",
    "other_details": {{}}
}}

DOCUMENT:
{page_text}
"""

    result = safe_generate(prompt)

    try:
        clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    except Exception:
        return {"discharge_summary": None, "raw_output": result}