from fastapi import FastAPI,Form,UploadFile,File,HTTPException
from starlette import status
from graph import create_graph
from utils.pdf_parsing import extract_pages

app=FastAPI(title='SuperClaims processing pipeline')

@app.post('/')
async def insurance_claim(claim_id:str=Form(...),file:UploadFile=File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='File must be a PDF')
    graph=create_graph()
    pdf_bytes = await file.read() #this breaks PDF into chunks
    pages = extract_pages(pdf_bytes)
    initial_state = {
        "claim_id": claim_id,
        "pages": pages,
        "classified_pages": {},
        "identity_data": {},
        "discharge_data": {},
        "bill_data": {},
        "final_result": {}
    }
    
    result = graph.invoke(initial_state)
    return result["final_result"]
    

