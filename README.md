# Invoice Automation – Hybrid AI Pipeline

Production-grade invoice automation system using a **deterministic-first, AI-fallback** architecture.

This repository demonstrates how to build a **reliable, explainable, and cost-aware** invoice extraction pipeline designed for real-world finance workflows.

---

## What This Is

- OCR + direct PDF text extraction
- Deterministic parsing (regex-based)
- AI-assisted fallback only when confidence is low
- Confidence-based review signals
- Batch processing with CSV export
- API-first design (FastAPI)
- Operational UI for demos and validation (Streamlit)

This is **not** a generic “AI agent” demo.  
It is a **practical automation system** optimized for predictability, auditability, and cost control.

---

## Case Study

A detailed consulting-style case study is available here:

➡️ **[case-study_invoice-automation_hybrid-ai.md](case-study_invoice-automation_hybrid-ai.md)**

The case study covers:
- Business context and constraints
- Architecture and design trade-offs
- Why deterministic + AI beats pure AI for finance
- Measured outcomes and ROI
- Real-world failure handling

---

## Architecture Overview

High-level system architecture and design rationale:

➡️ **[architecture.md](architecture.md)**

---

## 🖼 Screenshots

Example UI and batch processing outputs are available in the `screenshots/` directory.

---

## What This Project Is Not

- Not a fully autonomous accounting system
- Not an agentic or self-reflective AI workflow
- Not optimized for hype-driven demos

This project prioritizes **correctness over cleverness**.

---

## Author

**Applied AI Engineer**  
End-to-end ownership: problem framing, system design, implementation, and deployment.

---

## License

This repository is intended for educational, portfolio, and demonstration purposes.
