from datetime import datetime


def calculate_claim_total(bill_data):
    """Safely pull total amount from bill agent output."""
    if not bill_data or bill_data.get("itemized_bill") is None and "total_amount" not in bill_data:
        return None
    return bill_data.get("total_amount")


def aggregate_results(identity_data, discharge_data, bill_data):
    """
    Combines outputs from all 3 extraction agents into a single
    structured claim JSON.

    Args:
        identity_data   : output of extract_id_details()
        discharge_data  : output of extract_discharge_details()
        bill_data       : output of extract_bill_details()

    Returns:
        dict: final aggregated claim payload
    """

    # Track which agents failed so the caller knows what to re-run
    errors = {}
    if identity_data.get("identity") is None and "patient_name" not in identity_data:
        errors["identity_agent"] = identity_data.get("details") or identity_data.get("raw_output")
    if discharge_data.get("discharge_summary") is None and "final_diagnosis" not in discharge_data:
        errors["discharge_agent"] = discharge_data.get("details") or discharge_data.get("raw_output")
    if bill_data.get("itemized_bill") is None and "total_amount" not in bill_data:
        errors["bill_agent"] = bill_data.get("details") or bill_data.get("raw_output")

    aggregated = {
        "metadata": {
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "status": "partial" if errors else "success",
            "errors": errors if errors else None,
        },
        "patient": {
            "name":             identity_data.get("patient_name"),
            "date_of_birth":    identity_data.get("date_of_birth"),
            "id_numbers":       identity_data.get("id_numbers", []),
            "policy_number":    identity_data.get("policy_number"),
            "policy_holder":    identity_data.get("policy_holder"),
            "insurance_company":identity_data.get("insurance_company"),
        },
        "hospitalization": {
            "hospital_name":        discharge_data.get("hospital_name"),
            "admission_date":       discharge_data.get("admission_date"),
            "discharge_date":       discharge_data.get("discharge_date"),
            "length_of_stay_days":  discharge_data.get("length_of_stay_days"),
            "admitting_diagnosis":  discharge_data.get("admitting_diagnosis"),
            "final_diagnosis":      discharge_data.get("final_diagnosis", []),
            "treating_physician":   discharge_data.get("treating_physician"),
            "procedures_performed": discharge_data.get("procedures_performed", []),
            "medications_on_discharge": discharge_data.get("medications_on_discharge", []),
            "follow_up_instructions":   discharge_data.get("follow_up_instructions"),
        },
        "billing": {
            "hospital_name":    bill_data.get("hospital_name"),
            "bill_date":        bill_data.get("bill_date"),
            "line_items":       bill_data.get("line_items", []),
            "subtotal":         bill_data.get("subtotal"),
            "taxes_and_fees":   bill_data.get("taxes_and_fees"),
            "total_amount":     calculate_claim_total(bill_data),
            "amount_paid":      bill_data.get("amount_paid"),
            "amount_due":       bill_data.get("amount_due"),
            "currency":         bill_data.get("currency", "INR"),
            "payment_mode":     bill_data.get("payment_mode"),
        },
    }

    return aggregated