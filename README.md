# Document Processing Pipeline

A FastAPI service that processes insurance claim PDFs using **LangGraph** to orchestrate document segregation and multi-agent data extraction powered by the **Gemini API**.

---

## Project Structure

```
├── main.py                  # FastAPI app and endpoint
├── graph.py                 # LangGraph workflow definition
├── agents/
│   ├── segregator.py        # Classifies pages into document types
│   ├── id_agent.py          # Extracts patient & policy identity info
│   ├── discharge_agent.py   # Extracts discharge summary details
│   ├── bill_agent.py        # Extracts itemized billing information
│   └── aggregator.py        # Combines all agent outputs
├── utils/
│   └── pdf_parsing.py       # PDF → pages (text + base64 image)
├── config/
│   └── llm_setup.py         # Gemini client initialisation
├── .env                     # API keys (not committed)
└── requirements.txt
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the root:

```env
GEMINI_API_KEY2=your_gemini_api_key_here
```

### 3. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## API

### `POST /api/process`

Processes a PDF claim file and returns structured extracted data.

**Request** — `multipart/form-data`

| Field      | Type   | Description                  |
|------------|--------|------------------------------|
| `claim_id` | string | Unique identifier for the claim |
| `file`     | file   | PDF file to process          |

**Example using curl**

```bash
curl -X POST http://localhost:8000/api/process \
  -F "claim_id=CLM001" \
  -F "file=@/path/to/claim.pdf"
```

**Response** — `application/json`

```json
{
  "metadata": {
    "processed_at": "2026-04-15T10:00:00Z",
    "status": "success",
    "errors": null
  },
  "patient": {
    "name": "Ravi Kumar",
    "date_of_birth": "12/05/1985",
    "id_numbers": ["XXXX-XXXX-4321", "ABCPK1234Q"],
    "policy_number": "HDFC123456789",
    "policy_holder": "Ravi Kumar",
    "insurance_company": "HDFC Ergo"
  },
  "hospitalization": {
    "hospital_name": "Apollo Hospitals",
    "admission_date": "10/03/2026",
    "discharge_date": "14/03/2026",
    "length_of_stay_days": 4,
    "final_diagnosis": ["Dengue Fever"],
    "treating_physician": "Dr. Suresh Reddy",
    "procedures_performed": [],
    "medications_on_discharge": ["Paracetamol 500mg", "Dolo 650"]
  },
  "billing": {
    "line_items": [
      { "description": "Room Charges", "amount": 3000 },
      { "description": "Medicine Charges", "amount": 1500 },
      { "description": "Lab Charges", "amount": 2000 }
    ],
    "total_amount": 11800,
    "currency": "INR",
    "payment_mode": "Cash"
  }
}
```

---

## LangGraph Workflow

```
START
  │
  ▼
segregation_node        ← Classifies every PDF page into one of 9 document types
  │
  ▼
id_agent_node           ← Extracts patient name, DOB, policy & ID numbers
  │
  ▼
discharge_agent_node    ← Extracts diagnosis, admission/discharge dates, physician
  │
  ▼
bill_agent_node         ← Extracts all line items, totals, payment details
  │
  ▼
aggregator_node         ← Merges all agent outputs into final JSON
  │
  ▼
END
```

All three extraction agents read from `classified_pages` produced by the segregator. Each agent only receives the pages relevant to it — the ID agent never sees billing pages, etc.

### Document Types (9)

| Type | Description |
|------|-------------|
| `identity_document` | Patient ID, Aadhaar, PAN, policy card |
| `claim_forms` | Insurance claim forms |
| `discharge_summary` | Hospital discharge records |
| `itemized_bill` | Hospital bills with line items |
| `prescription` | Doctor prescriptions |
| `investigation_report` | Lab / diagnostic reports |
| `cash_receipt` | Payment receipts |
| `cheque_or_bank_details` | Bank account / cheque info |
| `other` | Anything that doesn't fit above |

---

## Requirements

```
fastapi
uvicorn
python-multipart
langgraph
google-genai
pymupdf
Pillow
python-dotenv
typing_extensions
```

---

## Development Tips

- Use `mock_segregation()` in `segregator.py` during development to avoid spending API quota — it classifies pages with simple keyword matching, no API calls.
- The Gemini free tier has per-minute rate limits. The `safe_generate` / `safe_segregate` functions use exponential backoff (15s → 30s → 60s) and only retry on known transient errors (429, 500, 503).
- Image-only PDF pages (scanned documents) are handled by converting the page to PNG bytes and passing them to Gemini via `types.Part.from_bytes()`.