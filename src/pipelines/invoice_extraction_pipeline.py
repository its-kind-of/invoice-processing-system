from parsers.invoice_parser import parse_invoice_text
from extractors.invoice_llm_extractor import extract_invoice_with_groq

def choose_invoice_id(regex_id: str | None, llm_id: str | None):
    if regex_id and llm_id:
        return regex_id if len(regex_id) >= len(llm_id) else llm_id
    return regex_id or llm_id

def extract_invoice(text: str) -> dict:
    """
    Unified invoice extraction pipeline.
    Regex first, LLM fallback only if required.
    """

    regex_result = parse_invoice_text(text)

    # If regex is good enough, return it
    if not regex_result['needs_fallback']:
        return {
            "invoice_number": regex_result["invoice_number"],
            "invoice_date": regex_result["invoice_date"],
            "total_amount": regex_result["total_amount"],
            "source": "regex"
        }
    # Fallback to LLM
    llm_result = extract_invoice_with_groq(text)

    primary_invoice_id = choose_invoice_id(
        regex_result.get("invoice_number"),
        llm_result.get("invoice_number")
    )

    secondary_invoice_id = (
        llm_result.get("invoice_number")
        if primary_invoice_id == regex_result.get("invoice_number")
        else regex_result.get("invoice_number")
    )

    # Merge results: regex preferred if available
    final =  {
        "invoice_number": primary_invoice_id,
        "invoice_number_alternate": secondary_invoice_id,
        "invoice_date": regex_result["invoice_date"] or llm_result.get("invoice_date"),
        "total_amount": regex_result['total_amount'] or llm_result.get("total_amount"),
        "source": "llm_fallback"
    }

    confidence_level = (
        "high" if final['source'] == "regex" else "medium"
    )

    final['confidence'] = confidence_level

    return final