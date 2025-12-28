# System Architecture

This document describes the logical architecture and key design decisions behind the invoice automation pipeline.

---

## High-Level Flow

## System Architecture

<pre style="background: #1a1a1a; color: #ff6b35; padding: 20px; border-radius: 8px; font-family: 'Courier New', monospace;">
<span style="color: #ff6b35;">PDF Upload</span>
       ↓
<span style="color: #ff6b35;">Text Extraction</span>
       ├─ <span style="color: #e91e63;">Direct PDF text</span>
       └─ <span style="color: #e91e63;">OCR fallback</span>
       ↓
<span style="color: #e91e63;">Deterministic Parser (Regex)</span>
       ↓
<span style="color: #e91e63;">Confidence Evaluation</span>
       ├─ <span style="color: #4caf50;">High → Accept</span>
       └─ <span style="color: #2196f3;">Low → AI Fallback</span>
       ↓
<span style="color: #ff9800;">Merge & Validation</span>
       ↓
<span style="color: #9c27b0;">Structured Output</span>
       ↓
<span style="color: #e91e63;">API / UI / CSV Export</span>
</pre>


---

## Core Components

### 1. Text Extraction
- Direct extraction for digital PDFs
- OCR fallback for scanned or low-quality documents
- Quality thresholding to decide OCR usage

### 2. Deterministic Parser
- Regex-based extraction for:
  - Invoice number
  - Invoice date
  - Total amount
- Field-level confidence scoring based on:
  - Pattern strength
  - Format validity
  - Value sanity checks

### 3. AI-Assisted Fallback
- Invoked only when deterministic confidence is low
- Used selectively to reduce cost and variance
- Output normalized and validated before acceptance

### 4. Merge & Disambiguation Layer
- Deterministic results preferred over AI outputs
- Invoice ID disambiguation logic
- Alternate identifiers preserved for traceability

### 5. API Layer
- FastAPI backend
- Strict response schemas
- Clear failure signaling (no silent errors)

### 6. UI & Batch Processing
- Streamlit UI for:
  - Batch uploads
  - Tabular review
  - CSV export
- Designed to match real finance workflows

---

## Design Philosophy

- Deterministic reliability over agentic complexity
- AI as fallback, not default
- Explainability over black-box automation
- Batch-first, API-first mindset

This architecture prioritizes **predictability, auditability, and cost control** over novelty.
