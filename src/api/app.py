from fastapi import FastAPI, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
import shutil

from ocr.ocr_engine import extract_text_from_pdf, extract_text_via_ocr
from pipelines.invoice_extraction_pipeline import extract_invoice
from db.database import init_db, insert_invoice

from pydantic import BaseModel
from typing import Optional

class InvoiceResponse(BaseModel):
    invoice_number: Optional[str]
    invoice_number_alternate: Optional[str]
    invoice_date: Optional[str]
    total_amount: Optional[float]
    source: str
    confidence: str

app = FastAPI(
    title = "Invoice extraction API",
    description="OCR + AI-powered invoice extraction",
    version="1.0.0"
)

# initialize db on startup
def startup():
    init_db()

@app.post("/extract-invoice", response_model=InvoiceResponse)
async def extract_invoice_api(file: UploadFile = File(...)):
    # validate file typ
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail='Only PDF file are supported')
    
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # extract text 
    text = extract_text_from_pdf(tmp_path)
    if len(text.strip()) < 100:
        text = extract_text_via_ocr(tmp_path)

    # run unified pipeline
    final = extract_invoice(text)

    # persist to db
    insert_invoice(final, text)

    return final
    

