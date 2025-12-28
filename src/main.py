from ocr.ocr_engine import extract_text_from_pdf, extract_text_via_ocr
from pipelines.invoice_extraction_pipeline import extract_invoice
from db.database import init_db, insert_invoice

pdf_path = r"D:\finance-automation\data\invoices\Invoice_AMB-1_NikhilShengde.pdf"

init_db()

text = extract_text_from_pdf(pdf_path)

if len(text.strip()) < 100:
    print("low-quality PDF, switching to OCR")
    text = extract_text_via_ocr(pdf_path)

# print("RAW EXTRATED TEXT:\n", text)

final = extract_invoice(text)

print("\nFINAL INVOICE OUTPUT:\n", final)

insert_invoice(final, text)
print("\n INVOICE SAVED TO DB")