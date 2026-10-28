
import re
from datetime import datetime


def extract_fields(text):
    """Extract vendor, date, amount, currency and receipt number."""

    fields = {
        "vendor": "",
        "date": "",
        "amount": "",
        "currency": "",
        "receipt_number": "",
    }

    if not text or not text.strip():
        return fields

    # Normalize whitespace without changing the document's content.
    text = text.replace("\r", "\n")
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # --------------------------------------------------
    # 1. Vendor extraction
    # --------------------------------------------------
    ignored_words = (
        "receipt", "tax invoice", "invoice", "date:",
        "receipt date", "invoice date", "guest:",
        "check-in", "check-out", "total", "subtotal",
        "payment", "amount due", "bill to", "ship to",
        "phone:", "tel:", "email:", "address:"
    )

    for line in lines[:8]:
        lower_line = line.lower()

        if any(word in lower_line for word in ignored_words):
            # Keep a vendor name before a receipt label on the same line.
            candidate = re.split(
                r"\b(?:receipt|tax invoice|invoice|date:)\b",
                line,
                flags=re.IGNORECASE,
            )[0].strip(" :-#")

            if len(candidate) >= 2 and not re.search(
                r"\d{4,}", candidate
            ):
                fields["vendor"] = candidate
                break
            continue

        if len(line) < 2:
            continue

        if re.fullmatch(r"[\d\s.,:/#-]+", line):
            continue

        if re.search(r"\d{4,}", line):
            continue

        fields["vendor"] = line.strip(" :-#")
        break

    # --------------------------------------------------
    # 2. Date extraction
    # Prefer explicitly labelled receipt/invoice dates.
    # --------------------------------------------------
    date_patterns = [
        (
            r"(?i)\b(?:receipt\s+date|invoice\s+date|"
            r"transaction\s+date|date)\s*[:#-]?\s*"
            r"(\d{4}-\d{2}-\d{2})",
            ["%Y-%m-%d"],
        ),
        (
            r"(?i)\b(?:receipt\s+date|invoice\s+date|"
            r"transaction\s+date|date)\s*[:#-]?\s*"
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            ["%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"],
        ),
        (
            r"(?i)\b(?:receipt\s+date|invoice\s+date|"
            r"transaction\s+date|date)\s*[:#-]?\s*"
            r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
            ["%d %b %Y", "%d %B %Y"],
        ),
    ]

    for pattern, formats in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_value = match.group(1)
            for date_format in formats:
                try:
                    fields["date"] = datetime.strptime(
                        date_value, date_format
                    ).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
        if fields["date"]:
            break

    # If no labelled date was found, try other date formats.
    if not fields["date"]:
        fallback_patterns = [
            (
                r"\b(\d{4}-\d{2}-\d{2})\b",
                ["%Y-%m-%d"],
            ),
            (
                r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",
                ["%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"],
            ),
            (
                r"\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b",
                ["%d %b %Y", "%d %B %Y"],
            ),
        ]

        for pattern, formats in fallback_patterns:
            for match in re.finditer(pattern, text):
                for date_format in formats:
                    try:
                        fields["date"] = datetime.strptime(
                            match.group(1), date_format
                        ).strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                if fields["date"]:
                    break
            if fields["date"]:
                break

    # --------------------------------------------------
    # 3. Currency extraction
    # Only assign a currency when the code is explicit.
    # A $ symbol alone is ambiguous.
    # --------------------------------------------------
    
    currency_match = re.search(
        r"(?i)\b(SGD|USD|INR|EUR|GBP|AUD|CAD|MYR)\b",
        text,
    )

    if currency_match:
        fields["currency"] = currency_match.group(1).upper()
    elif re.search(r"€", text):
        fields["currency"] = "EUR"
    elif re.search(r"₹", text):
        fields["currency"] = "INR"


    # --------------------------------------------------
    # 4. Total amount extraction
    # Supports 780.75, 1060,00 and 1,060.00.
    # --------------------------------------------------
    number_pattern = r"(\d[\d,]*[.,]\d{2})"

    total_patterns = [
        rf"(?i)\bgrand\s+total\b\s*[:\-]?\s*"
        rf"(?:SGD|USD|INR|EUR|GBP|AUD|CAD|MYR)?\s*[$€₹]?\s*"
        rf"{number_pattern}",

        rf"(?i)\btotal\s+amount\b\s*[:\-]?\s*"
        rf"(?:SGD|USD|INR|EUR|GBP|AUD|CAD|MYR)?\s*[$€₹]?\s*"
        rf"{number_pattern}",

        rf"(?i)\bamount\s+due\b\s*[:\-]?\s*"
        rf"(?:SGD|USD|INR|EUR|GBP|AUD|CAD|MYR)?\s*[$€₹]?\s*"
        rf"{number_pattern}",

        rf"(?i)\btotal\b\s*[:\-]?\s*"
        rf"(?:SGD|USD|INR|EUR|GBP|AUD|CAD|MYR)?\s*[$€₹]?\s*"
        rf"{number_pattern}",
    ]

    for pattern in total_patterns:
        match = re.search(pattern, text)
        if match:
            amount_value = match.group(1).strip()

            # Normalize decimal and thousands separators.
            if "," in amount_value and "." in amount_value:
                if amount_value.rfind(",") > amount_value.rfind("."):
                    amount_value = (
                        amount_value.replace(".", "").replace(",", ".")
                    )
                else:
                    amount_value = amount_value.replace(",", "")
            elif "," in amount_value:
                parts = amount_value.split(",")
                if len(parts[-1]) == 2:
                    amount_value = "".join(parts[:-1]) + "." + parts[-1]
                else:
                    amount_value = "".join(parts)
            elif amount_value.count(".") > 1:
                parts = amount_value.split(".")
                amount_value = "".join(parts[:-1]) + "." + parts[-1]

            try:
                fields["amount"] = f"{float(amount_value):.2f}"
                break
            except ValueError:
                continue

    # --------------------------------------------------
    # 5. Receipt / invoice / ticket number
    # --------------------------------------------------
    
    number_patterns = [
        r"(?i)\b(?:receipt|invoice|ticket|folio)\s*"
        r"(?:number|no\.?|#)\s*[:#-]?\s*([A-Z0-9][A-Z0-9/-]*)",

        r"(?i)\b(?:receipt|invoice|ticket|folio)\s*"
        r"\s*[:#]\s*([A-Z0-9][A-Z0-9/-]*)",
    ]


    for pattern in number_patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip(" :-#")
            if value:
                fields["receipt_number"] = value
                break

    return fields
