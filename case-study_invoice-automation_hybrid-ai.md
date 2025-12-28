# Case Study: Production-Grade Invoice Extraction Pipeline
## OCR + Deterministic + AI

**Role:** Applied AI Engineer  
*(End-to-end ownership: design, implementation, deployment)*

---

## 1. Business Context

Finance teams process large volumes of vendor invoices in PDF format. These documents vary widely in structure, quality, and formatting.

### Common problems observed:
- Manual data entry is slow and error-prone
- Invoices differ across vendors and months
- OCR quality varies (scanned vs digital PDFs)
- Pure AI-based extraction is unreliable and expensive
- Deterministic systems fail on edge cases

### Goal
Build a reliable invoice extraction system that:
- Maximizes accuracy
- Minimizes AI usage and cost
- Fails safely
- Is auditable and explainable
- Can be integrated via API into existing systems

---

## 2. Scale & Operating Assumptions

The solution was designed for finance teams processing **hundreds to low thousands of invoices per month**, with documents varying across vendors, formats, and PDF quality (digital and scanned).

The focus was on **batch-oriented workflows**, not real-time streaming, aligning with typical finance operations and month-end processing cycles.

---

## 3. Key Constraints & Design Principles

### Constraints
- Input documents are unstructured PDFs
- OCR quality is inconsistent
- Invoice formats vary across vendors
- Systems must not silently return incorrect data
- Output must be consumable by finance teams (Excel/CSV)

### Design Principles
1. **Deterministic first, AI Second**
2. **Fail-safe over 'smart'**
3. **Explainability over black-box automation**
4. **Batch-ready and API-first**
5. **Human-in-the-loop by design**

---

## 4. Solution Overview

The system uses a **hybrid extraction strategy**:

### 1. PDF Text Extraction
- Direct text extraction for digital PDFs
- OCR fallback for scanned or low-quality PDFs

### 2. Deterministic Parsing
- Regex-based extraction for:
  - Invoice number
  - Invoice date
  - Total amount
- Confidence scoring per field based on pattern strength, format validity, and value sanity checks (e.g., realistic invoice totals)

### 3. AI-Assisted Fallback
- LLM-based extraction only when deterministic confidence is low
- Used selectively to control cost and variance

### 4. Merge & Validation Layer
- Deterministic results preferred over LLM outputs
- Invoice ID disambiguation logic
- Type normalization and sanity checks

### 5. API + UI Layer
- FastAPI backend with strict response schemas
- Streamlit UI for batch uploads and CSV export

---

## 5. System Architecture (Logical)

![Alt text](screenshots\architecture.png)

### 5.1. Design Trade-offs

Several design trade-offs were made deliberately:

- **Deterministic reliability over agentic complexity**: Invoices are structured, repetitive, and compliance-bound. Introducing agentic workflows would increase cost and unpredictability without improving reliability.

- **AI as fallback, not default**: Large language models are powerful but variable. Using them selectively reduced cost and prevented silent failures.

- **Batch-first UX**: Finance teams process invoices in batches, not one-by-one. The system was optimized for batch upload and export rather than real-time interaction.

---

## 6. Key Technical Decisions (and Why)

### 6.1. Deterministic + AI Hybrid (Not Agentic)

**Decision:** Avoid agentic workflows and multi-agent orchestration

**Reason:** Invoices are structured, repetitive, and compliance-bound. Agentic systems add cost, complexity, and unpredictability without improving reliability.

**Outcome:**
- Lower inference cost
- Easier debugging
- Predictable behaviour

### 6.2. Confidence-Based Extraction

Each extracted invoice is labelled with:
- `confidence: high` → deterministic extraction
- `confidence: medium` → AI-assisted extraction

**Why this matters:**
- Finance teams need trust signals
- Enables human review where needed
- Prevents blind automation

### 6.3. Invoice ID Disambiguation

Invoices often contain multiple identifiers:
- Short reference IDs
- Full invoice numbers
- Internal vendor codes

### 6.4. Strict API Contracts

FastAPI response models enforce:
- Type safety
- Consistent schemas
- No silent failures

### 6.5. Challenges & Iterations

#### Date Parsing Variability
**Problem:** Initial parsing failed on invoices using mixed formats (DD/MM/YYYY, textual dates, and shorthand formats).

**Resolution:** Introduced multi-format parsing with fallback heuristics and reduced confidence instead of forcing a value.

#### Invoice ID Ambiguity
**Problem:** Some invoices contained multiple identifiers (short reference vs full invoice numbers).

**Resolution:** Implemented deterministic disambiguation logic favouring longer, structured identifiers while preserving alternates.

#### OCR Noise
**Problem:** Low-quality scans produced partial or noisy text.

**Resolution:** Added OCR fallback detection and downstream confidence degradation instead of silent acceptance.

---

## 7. Batch Processing & Operational UX

### Capabilities
- Upload multiple PDFs at once
- Process invoices sequentially
- Display results in tabular form
- Export results as CSV

### Why This Matters
- Finance teams never process invoices one-by-one
- CSV output integrates with Excel and accounting systems
- Batch UX significantly increases real-world usability

---

## 8. Example Output (Structured)

### Invoice Before vs After Extraction

```json
{
  "invoice_id": "INV-2024-001234",
  "invoice_date": "2024-03-15",
  "total_amount": 15750.50,
  "currency": "USD",
  "vendor_name": "ABC Supplies Ltd",
  "confidence": "high",
  "extraction_method": "deterministic"
}
```

---

## 9. Results & Measured Impact

The system was validated on a pilot dataset consisting of multiple invoice formats across several vendors, including both digital and scanned PDFs.

### Observed Outcomes:
- **Deterministic extraction succeeded on ~65–70% of invoices** without AI usage
- AI-assisted fallback handled remaining edge cases
- **End-to-end processing time: ~10–20 seconds per invoice**
- **Estimated AI cost: <$0.05 per invoice**, significantly lower than pure LLM-based approaches

Compared to manual processing (estimated ~4-5 minutes per invoice), the system **reduced processing time to under a minute**, while preserving auditability and review controls.

### Indicative ROI:
For a team processing **~500 invoices/month**, this approach can save **~30–40 hours of manual effort monthly** while keeping AI costs predictable and low.

---

## 10. What This System Is and Is Not

### This System IS:
- A production-ready invoice automation component
- A consulting-grade deliverable
- A foundation for broader finance automation

### This System IS NOT:
- A fully autonomous accounting system
- A generic 'AI Agent' demo
- A black-box extraction model

*This was a deliberate design choice.*

---

## 11. Key Learnings

1. **Reliability beats intelligence** in finance automation
2. **Deterministic systems are still essential**
3. **AI is most valuable as a fallback, not a default**
4. **Confidence and explainability matter more than raw accuracy**
5. **Production systems fail at integration boundaries, not algorithms**
6. Early attempts to rely solely on AI increased variability and cost without improving reliability; **a hybrid approach proved more robust**

---

## 12. Future Extensions (Optional)

- Vendor-specific validation rules (GST, tax splits)
- Batch OCR optimization
- ERP integration (SAP, Tally, QuickBooks)
- Review & approval workflows
- Cost and accuracy analytics

---

## Appendix A: Batch Processing & UI

![Alt text](screenshots\batch-ui.png)
![Alt text](screenshots\csv-export.png)


---

## Final Consultant Takeaway

> This project demonstrates how to build a **practical, production-grade AI system** by combining deterministic methods with AI in a controlled, explainable way—prioritizing **reliability, auditability, and real-world usability** over hype.

---

### Tech Stack
- **Backend:** FastAPI, Python
- **OCR:** Tesseract / Cloud OCR APIs
- **LLM:** GPT-4 / Claude / Groq (selective fallback)
- **Frontend:** Streamlit
- **Export:** CSV, JSON

---

### Contact
**LinkedIn:** [Nikhil Shendge](https://www.linkedin.com/in/nikhil-shendge-7a064b175/)  
**Email:** nikhil.s.shendge@gmail.com  
