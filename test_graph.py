from graph import create_graph

mock_pages = [
    {"page_num": 1, "text": "Patient Name: John Doe", "image": ""},
    {"page_num": 2, "text": "Discharge Summary", "image": ""},
    {"page_num": 3, "text": "Invoice Total Amount 5000", "image": ""}
]

initial_state = {
    "claim_id": "CLAIM123",
    "pages": mock_pages,
    "classified_pages": {},
    "identity_data": {},
    "discharge_data": {},
    "bill_data": {},
    "final_result": {}
}

graph = create_graph()

result = graph.invoke(initial_state)

print("FINAL RESULT:\n", result["final_result"])