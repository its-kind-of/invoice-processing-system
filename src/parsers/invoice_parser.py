import re 
from datetime import datetime


# Utility helper
def _clean_number(s: str) -> float:
    if not s:
        return None
    
    # remove currency symbols, spaces, non-numeric except dot and comma
    s = s.replace("₹", "").replace(",", "").strip()
    
    # convert comma-decimal if needed
    try :
        return float(s)
    except:
        # fallback: extract numbers and decimals
        m = re.search(r"([0-9]+(?:\.[0-9]{1,2})?)", s.replace(",", ""))
        return float(m.group(1)) if m else None 
    
def _try_parse_date(s: str) -> datetime:
    if not s :
        return None
    
    s = s.strip()

    # common date formats
    formats = ["%d-%m-%y", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y",
               "%Y-%m-%d", "%d.%m.%Y", "%d %b %Y", "%d %B %Y"]
    
    for fmt in formats:
        try :
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d") # normlise to ISO
        except :
            pass

    # fallback: extract numbers and try heuristics
    m = re.search(r"([0-9]{1,2}[-\/\.][0-9]{1,2}[-\/\.][0-9]{2,4})", s)
    if m:
        token = m.group(1)
        for fmt in ["%d-%m-%y", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y", "%d.%m.%Y"]:
            try:
                dt = datetime.strptime(token, fmt)
                return dt.strftime("%Y-%m-%d")
            except: 
                pass
    return None


# Patterns to try 
INVOICE_NUMBER_PATTERNS = [
    r"(Invoice\s*(No\.?|Number)[:\s\-]*)\s*([A-Za-z0-9\/\-\_]+)",
    r"(Inv(?:oice)?\s*#[:\s]*)\s*([A-Za-z0-9\/\-\_]+)",
    r"\b([A-Z]{2,4}\/\d{4}\/\d{1,3}\/\d{1,3})\b",  # patterns like AMB/2025/09/01
    r"\b([A-Z]{2,6}[-_]\d{3,10})\b",
    r"Invoice\s*[:\-]?\s*([A-Za-z0-9\-\/]{4,30})"
]

INVOICE_DATE_PATTERNS = [
    r"Invoice\s*Date[:\s\-]*([0-9]{1,2}[-\/\.][0-9]{1,2}[-\/\.][0-9]{2,4})",
    r"Date[:\s\-]*([0-9]{1,2}[-\/\.][0-9]{1,2}[-\/\.][0-9]{2,4})",
    r"Invoice Date[:\s\-]*([0-9]{2,4}[-\/\.][0-9]{1,2}[-\/\.][0-9]{1,2})",
]

TOTAL_AMOUNT_PATTERNS = [
    # Strong patterns ONLY
    r"(?:Grand\s*Total|Total\s*Amount|Amount\s*Due|Notes\s*Total|Total)[:\s\-]*₹?\s*([0-9,]+\.\d{2})",
    r"Sub\s*Total[:\s\-]*₹?\s*([0-9,]+\.\d{2})",
]

def parse_invoice_text(text: str, debug=False):
    """
    Returns : 
    {
        "invoice_number": value or None,
        "invoice_date": YYYY-MM-DD or None,
        "total_amount": float or None,
        "confidence: {
            "invoice_number": bool,
            "invoice_date": bool,
            "total_amount": bool
        },
        "needs_fallback": True/False

    }
    """

    if not text:
        return _result(None, None, None, debug, reason="empty_text")
    
    # normalise whitespace
    txt = " ".join(text.split())
    lower = txt.lower()


    results = {"invoice_number": None, "invoice_date": None, "total_amount": None}
    confidence = {"invoice_number": 0.0, "invoice_date": 0.0, "total_amount": 0.0}

    reasons = []

    # 1. invoice number - try multiple patterns prefer longer matches
    for pat in INVOICE_NUMBER_PATTERNS:
        m = re.search(pat, txt, re.IGNORECASE)
        if m:
            # find last capturing group that looks like the id
            groups = [g for g in m.groups() if g]
            # pick the last group (usually the actual token)
            candidate = groups[-1].strip()
            # filter out false positives like "No." alone
            if len(candidate) >= 3 and not re.fullmatch(r"no\.", candidate, re.IGNORECASE):
                results["invoice_number"] = candidate
                confidence["invoice_number"] = 1.0
                break
            else:
                # small matches are low confidence
                results['invoice_number'] = candidate
                confidence['invoice_number'] = 0.3

    # 2. Date - try pattern then fallback parser
    for pat in INVOICE_DATE_PATTERNS:
        m = re.search(pat, txt, re.IGNORECASE)
        if m:
            raw = m.groups()[-1]
            parsed = _try_parse_date(raw)
            if parsed:
                results['invoice_date'] = parsed
                confidence['invoice_date'] = 0.95
                break

    # if still None, try any date-like token
    if results['invoice_date'] is None:
        m = re.search(r"([0-9]{1,2}[-\/\.][0-9]{1,2}[-\/\.][0-9]{2,4})", txt)
        if m:
            parsed = _try_parse_date(m.group(1))
            if parsed:
                results['invoice_date'] = parsed
                confidence['invoice_date'] = 0.6

    # 3. Total amount - try patterns and heuristics
    for pat in TOTAL_AMOUNT_PATTERNS:
        m = re.search(pat, txt, re.IGNORECASE)
        if m:
            cand = m.group()[1]
            num = _clean_number(cand)
            if num is not None:
                results['total_amount'] = num
                confidence['total_amount'] = 0.95
                break

 
    # 4. Additional sanity fixes if invoice_number included 'Invoice prefix, strip it.
    if results['invoice_number'] and results["invoice_number"].lower().startswith('invoice'):
        token = re.sub(r"(?i)invoice(?:\sno\.?[:\s\-]*)", "", results["invoice_number"]).strip()
        if token:
            results['invoice_number'] = token

    # 5. Final normalization convert ints to float
    if isinstance(results['total_amount'], (int, float)):
        pass
    elif results['total_amount'] is not None:
        results['total_amount'] = _clean_number(str(results['total_amount']))

    # sanity check ; total amount must be realistic
    if results['total_amount'] is not None and results['total_amount'] < 100:
            # Impossible invoice total -> force fallback
            results['total_amount'] = None
            confidence['total_amount'] = 0.0

    # 6. Compute needs_fallback of any field is missing or low confidence
    needs_fallback = False
    for k in ['invoice_number', "invoice_date", "total_amount"]:
        if results[k] is None or confidence[k] < 0.6:
            needs_fallback =  True
            reasons.append(f"{k}_low")
    overall_confidence = sum(confidence.values()) / 3.0



    return {
        "invoice_number": results["invoice_number"],
        "invoice_date": results["invoice_date"],
        "total_amount": results["total_amount"],
        "confidence": confidence,
        "overall_confidence": round(overall_confidence, 2),
        "needs_fallback": needs_fallback,
        "reasons": reasons
    }
def _result(inv, date, total, debug=False, reason=None):
    return {
        "invoice_number": inv,
        "invoice_date": date,
        "total_amount": total,
        "confidence": {
            "invoice_number": 0 if not inv else 1,
            "invoice_date": 0 if not date else 1,
            "total_amount": 0 if not total else 1
        },
        "overall_confidence": 1.0 if inv and date and total else 0.0,
        "needs_fallback": not (inv and date and total),
        "reasons": [reason] if reason else []
    }





