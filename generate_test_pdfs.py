
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path

OUTPUT_DIR = Path("test_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

documents = {
    "01_restaurant_receipt.pdf": [
        "DEMO CAFE",
        "Receipt",
        "Date: 15/10/2026",
        "Receipt No: RC-1001",
        "Currency: SGD",
        "Food and beverages",
        "Total: SGD 25.50",
    ],
    "02_flight_ticket.pdf": [
        "DEMO AIRWAYS",
        "TRAVEL TICKET",
        "Passenger: Sample Passenger",
        "Ticket No: TK-2001",
        "Date: 16/10/2026",
        "Currency: USD",
        "Total: USD 250.00",
    ],
    "03_hotel_folio.pdf": [
        "DEMO HOTEL",
        "HOTEL FOLIO",
        "Guest: Sample Guest",
        "Folio No: HF-3001",
        "Date: 17/10/2026",
        "Currency: SGD",
        "Room charges",
        "Total: SGD 180.00",
    ],
    "04_office_invoice.pdf": [
        "DEMO OFFICE SUPPLIES",
        "TAX INVOICE",
        "Invoice No: INV-4001",
        "Invoice Date: 18/10/2026",
        "Stationery and printer paper",
        "Currency: SGD",
        "Total: SGD 75.00",
    ],
    "05_missing_amount.pdf": [
        "DEMO CAFE",
        "RECEIPT",
        "Date: 19/10/2026",
        "Receipt No: RC-5001",
        "Currency: SGD",
        "Food and beverages",
        "Total: ",
    ],
}

for filename, lines in documents.items():
    path = OUTPUT_DIR / filename
    pdf = canvas.Canvas(str(path), pagesize=A4)
    _, page_height = A4

    pdf.setFont("Helvetica", 12)
    y = page_height - 80

    for line in lines:
        pdf.drawString(60, y, line)
        y -= 28

    pdf.save()
    print(f"Created: {path}")

print("\nAll 5 synthetic test PDFs created.")
