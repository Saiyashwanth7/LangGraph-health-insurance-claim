# mock_agents.py

def mock_segregation(pages):
    classified = {
        "identity_document": [],
        "discharge_summary": [],
        "itemized_bill": [],
        "cash_receipt": [],
        "claim_forms": [],
        "cheque_or_bank_details": [],
        "prescription": [],
        "investigation_report": [],
        "other": []
    }

    for page in pages:
        text = page["text"].lower()

        if "aadhaar" in text or "pan" in text or "insured details" in text:
            classified["identity_document"].append(page)

        elif "discharge summary" in text or "final diagnosis" in text:
            classified["discharge_summary"].append(page)

        elif "hospital bill" in text or "itemized bill" in text:
            classified["itemized_bill"].append(page)

        elif "cash receipt" in text:
            classified["cash_receipt"].append(page)

        elif "claim form" in text:
            classified["claim_forms"].append(page)

        elif "bank details" in text:
            classified["cheque_or_bank_details"].append(page)

        elif "prescription" in text:
            classified["prescription"].append(page)

        elif "lab report" in text:
            classified["investigation_report"].append(page)

        else:
            classified["other"].append(page)

    return classified


# ---------------- ID AGENT ---------------- #

def mock_id_agent(classified):
    return {
        "patient_name": "Ravi Kumar",
        "date_of_birth": "1985-05-12",
        "id_numbers": [
            "XXXX-XXXX-4321",
            "ABCPK1234Q"
        ],
        "policy_number": "HDFC123456789",
        "policy_holder": "Ravi Kumar",
        "insurance_company": "HDFC Ergo"
    }


# ---------------- DISCHARGE AGENT ---------------- #

def mock_discharge_agent(classified):
    return {
        "hospital_name": "Apollo Hospitals",
        "admission_date": "2026-03-10",
        "discharge_date": "2026-03-14",
        "length_of_stay_days": 4,
        "admitting_diagnosis": "Viral Fever",
        "final_diagnosis": ["Dengue Fever"],
        "treating_physician": "Dr. Suresh Reddy",
        "procedures_performed": [],
        "medications_on_discharge": [],
        "follow_up_instructions": None
    }


# ---------------- BILL AGENT ---------------- #

def mock_bill_agent(classified):
    return {
        "hospital_name": "Apollo Hospitals",
        "bill_date": "2026-03-14",
        "line_items": [
            {"description": "Room Charges", "quantity": None, "unit_price": None, "amount": 3000},
            {"description": "Medicine Charges", "quantity": None, "unit_price": None, "amount": 1500},
            {"description": "Lab Charges", "quantity": None, "unit_price": None, "amount": 2000},
            {"description": "Injection", "quantity": None, "unit_price": None, "amount": 500},
            {"description": "Consultation", "quantity": None, "unit_price": None, "amount": 800},
            {"description": "ICU Charges", "quantity": None, "unit_price": None, "amount": 4000}
        ],
        "subtotal": 11800,
        "taxes_and_fees": None,
        "total_amount": 11800,
        "amount_paid": 6500,
        "amount_due": 5300,
        "currency": "INR",
        "payment_mode": "Cash"
    }


# ---------------- AGGREGATOR ---------------- #

def mock_aggregate(identity, discharge, bill):
    return {
        "metadata": {
            "status": "success",
            "errors": None
        },
        "patient": {
            "name": identity.get("patient_name"),
            "date_of_birth": identity.get("date_of_birth"),
            "id_numbers": identity.get("id_numbers"),
            "policy_number": identity.get("policy_number"),
            "policy_holder": identity.get("policy_holder"),
            "insurance_company": identity.get("insurance_company"),
        },
        "hospitalization": {
            "hospital_name": discharge.get("hospital_name"),
            "admission_date": discharge.get("admission_date"),
            "discharge_date": discharge.get("discharge_date"),
            "length_of_stay_days": discharge.get("length_of_stay_days"),
            "admitting_diagnosis": discharge.get("admitting_diagnosis"),
            "final_diagnosis": discharge.get("final_diagnosis"),
            "treating_physician": discharge.get("treating_physician"),
        },
        "billing": {
            "hospital_name": bill.get("hospital_name"),
            "bill_date": bill.get("bill_date"),
            "line_items": bill.get("line_items"),
            "total_amount": bill.get("total_amount"),
            "amount_paid": bill.get("amount_paid"),
            "amount_due": bill.get("amount_due"),
            "currency": bill.get("currency"),
            "payment_mode": bill.get("payment_mode"),
        }
    }