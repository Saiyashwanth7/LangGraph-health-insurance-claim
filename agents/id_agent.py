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


def extract_id_details(classified):
    pages = classified.get("identity_document", [])

    if not pages:
        return {"identity": None, "details": "No identity details found"}

    # Convert pages into text format for LLM
    page_text = "\n\n".join(
        [f"Page {p['page_num']}:\n{p.get('text','')}" for p in pages]
    )

    prompt = f"""
                Extract identity information from these document pages.

                Return ONLY valid JSON:

                {{
                "patient_name": "",
                "date_of_birth": "",
                "id_numbers": [],
                "policy_number": "",
                "policy_holder": "",
                "insurance_company": "",
                "other_details": {{}}
                }}

                DOCUMENT:
                {page_text}
                """

    result = safe_generate(prompt)

    try:
        clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    except:
        return {"identity": None, "raw_output": result}
