def classify_document(text):
    """Identify the type of document."""

    if not text or not text.strip():
        return "Not an expense document"

    content = text.lower()

    if "tax invoice" in content:
        return "Tax invoice"

    if any(word in content for word in [
        "boarding pass",
        "flight ticket",
        "e-ticket",
        "airline ticket",
        "travel ticket",
        "passenger ticket",
        "baggage check",
        "flight date",
        "boarding"
    ]):
        return "Travel ticket"

    if any(word in content for word in [
        "hotel folio", "guest folio", "room charges",
        "check-in", "check-out"
    ]):
        return "Hotel folio"

    if any(word in content for word in [
        "receipt", "total paid", "payment received"
    ]):
        return "Receipt"

    return "Not an expense document"

def classify_category(document_type, text):
    """Assign one of the required expense categories."""

    if document_type == "Not an expense document":
        return ""

    content = text.lower()

    if any(word in content for word in [
        "hotel", "accommodation", "room charges",
        "lodging", "guest folio", "apartment",
        "nights in", "booking details"
    ]):
        return "Accommodation"

    if any(word in content for word in [
        "flight", "airline", "boarding pass",
        "passenger ticket", "baggage check",
        "taxi", "cab", "metro", "train ticket",
        "travel ticket", "carpark", "parking"
    ]):
        return "Travel"

    if any(word in content for word in [
        "restaurant", "cafe", "coffee", "food",
        "beverage", "dining", "meal"
    ]):
        return "Food & Beverage"

    if any(word in content for word in [
        "office supplies", "stationery", "papermart",
        "printer paper", "pen", "notebook"
    ]):
        return "Office Supplies"

    return "Other"