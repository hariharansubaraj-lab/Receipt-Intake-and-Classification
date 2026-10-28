from datetime import datetime


def validate_document(document_type, category, fields, confidence):
    """Decide whether an expense document is complete enough."""

    if document_type == "Not an expense document":
        return "Unsupported"

    required_fields = [
        fields.get("vendor", ""),
        fields.get("date", ""),
        fields.get("amount", ""),
        fields.get("currency", "")
    ]

    # Missing required fields must not be guessed.
    if not all(str(value).strip() for value in required_fields):
        return "Needs review"

    # Validate date format.
    try:
        datetime.strptime(fields["date"], "%Y-%m-%d")
    except (ValueError, TypeError):
        return "Needs review"

    # Validate amount and currency.
    try:
        amount = float(fields["amount"])
        if amount < 0:
            return "Needs review"
    except (ValueError, TypeError):
        return "Needs review"

    if len(fields["currency"]) != 3 or not fields["currency"].isalpha():
        return "Needs review"

    # Low confidence needs human review.
    if confidence < 0.75:
        return "Needs review"

    if not category:
        return "Needs review"

    return "Done"
