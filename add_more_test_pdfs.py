
from pathlib import Path
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path("test_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

documents = [
    {
        "file": "06_usd_receipt.pdf",
        "lines": [
            "DEMO COFFEE SHOP",
            "RECEIPT",
            "Date: 20/10/2026",
            "Receipt No: RC-6001",
            "Currency: USD",
            "Food and beverages",
            "TOTAL USD $18.50",
        ],
    },
    {
        "file": "07_train_ticket.pdf",
        "lines": [
            "DEMO RAILWAYS",
            "TRAVEL TICKET",
            "Date: 21/10/2026",
            "Ticket No: TK-7001",
            "Currency: INR",
            "Train fare",
            "TOTAL INR 1250.00",
        ],
    },
    {
        "file": "08_hotel_cad.pdf",
        "lines": [
            "DEMO CANADA HOTEL",
            "HOTEL FOLIO",
            "Date: 22/10/2026",
            "Folio No: HF-8001",
            "Currency: CAD",
            "Room charges",
            "TOTAL CAD $320.00",
        ],
    },
    {
        "file": "09_tax_invoice.pdf",
        "lines": [
            "DEMO TECHNOLOGY STORE",
            "TAX INVOICE",
            "Invoice Date: 23/10/2026",
            "Invoice No: INV-9001",
            "Currency: SGD",
            "Office supplies",
            "TOTAL SGD 13715.52",
        ],
    },
    {
        "file": "10_non_expense.pdf",
        "lines": [
            "DEMO NEWSLETTER",
            "MONTHLY NEWS UPDATE",
            "Date: 24/10/2026",
            "Latest news and announcements",
            "No purchase or payment details",
        ],
    },
    {
        "file": "11_missing_date.pdf",
        "lines": [
            "DEMO OFFICE MART",
            "RECEIPT",
            "Receipt No: RC-11001",
            "Currency: INR",
            "Office supplies",
            "TOTAL INR 450.00",
        ],
    },
    {
        "file": "12_ambiguous_dollar.pdf",
        "lines": [
            "DEMO HOTEL",
            "HOTEL FOLIO",
            "Date: 25/10/2026",
            "Folio No: HF-12001",
            "Room charges",
            "TOTAL $780.75",
        ],
    },
]

for document in documents:
    path = OUTPUT_DIR / document["file"]
    pdf = canvas.Canvas(str(path))
    y = 800

    for line in document["lines"]:
        pdf.drawString(60, y, line)
        y -= 35

    pdf.save()
    print(f"Created: {path}")

print("Finished creating 7 additional synthetic PDFs.")
