# Receipt Intake and Classification

## Overview

A Python-based application that accepts multiple PDF expense documents, extracts text using digital PDF text extraction or OCR, classifies document types and expense categories, extracts key fields, and flags documents that need manual review.

## Features

- Upload multiple PDF files.
- Reject invalid or unsupported files with a clear error message.
- Extract embedded text from digital PDFs.
- Use Tesseract OCR for scanned PDFs.
- Classify documents as `Receipt`, `Tax invoice`, `Travel ticket`, `Hotel folio`, or `Not an expense document`.
- Categorize expenses as `Food & Beverage`, `Travel`, `Accommodation`, `Office Supplies`, or `Other`.
- Extract vendor, date, amount, currency, and receipt/invoice number.
- Validate required fields and assign processing statuses: `Done`, `Needs review`, `Unsupported`, or `Failed`.
- Display confidence scores, category reasons, and extracted text.
- Filter and review results in a Streamlit interface.
- Download processed results as a CSV file.
- Evaluate extracted fields against an expected-results CSV when the official test dataset is available.

## Technology Stack

- Python
- Streamlit
- Pandas
- pypdf
- pypdfium2
- Tesseract OCR
- pytesseract
- Pillow
- ReportLab (for generating synthetic test PDFs)

## Setup

### Prerequisites

- Python installed on your system.
- Tesseract OCR installed and configured.
- Windows PowerShell or a compatible terminal.

Ensure the Tesseract executable path configured in `src/pdf_reader.py` matches your installation. Update the path if necessary.

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Start the application

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal. Upload one or more PDF documents, click **Process PDFs**, review the extracted results, and download the CSV report.

## Evaluation

The evaluation script compares extracted fields against an expected-results CSV.

1. Place the assessment's official sample PDFs in `sample_docs`.
2. Place the official `expected_results.csv` in the project root.
3. Run:

```powershell
python evaluate.py
```

The script cannot calculate official evaluation accuracy until the expected-results CSV and corresponding PDF samples are available.

## Design

The application separates PDF reading, document classification, field extraction, and validation into individual modules.

1. **PDF reading:** Extract embedded text from digital PDFs. If embedded text is unavailable, use Tesseract OCR to process scanned documents.
2. **Document classification:** Identify the document type using document text and rule-based matching.
3. **Category classification:** Assign an expense category based on document clues and keywords.
4. **Field extraction:** Extract the vendor, date, total amount, currency, and receipt or invoice number.
5. **Validation:** Check required fields and determine whether the document is complete, needs review, is unsupported, or has failed.
6. **User interface:** Use Streamlit to display processing results, filters, document details, and CSV export.

Each PDF is processed independently so that an error in one document does not prevent other uploaded files from being processed.

## Confidence Score

The displayed confidence score is a heuristic based on the completeness of four required fields: vendor, date, amount, and currency.

It is not a calibrated machine-learning probability and does not guarantee that extracted values are correct. A document with missing required fields receives a lower score and may be marked `Needs review`.

## AI Tools Used

- **ChatGPT:** Used for implementation guidance, code explanations, debugging assistance, and documentation support.
- **Local testing:** The application was tested using synthetic PDF samples, including missing-field cases, an unsupported document, multiple currencies, and an ambiguous dollar symbol.

## Known Limitations

1. **OCR quality:** Blurry, rotated, handwritten, or low-resolution documents may produce inaccurate text.
2. **Ambiguous currencies:** A dollar symbol (`$`) alone does not identify a unique currency. Such documents may require manual review.
3. **Date ambiguity:** Different date formats can be interpreted differently. Missing or uncertain dates should be reviewed rather than guessed.
4. **Rule-based extraction:** Unfamiliar document layouts or unusual field labels may not be handled correctly.
5. **Category classification:** Documents containing overlapping keywords may be assigned an incorrect category.
6. **Confidence score:** The score measures required-field completeness, not actual extraction accuracy.
7. **Evaluation dataset:** Official accuracy cannot be reported until the official expected-results CSV and matching PDF samples are available.
