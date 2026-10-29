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
- Evaluate extracted fields against an expected-results CSV.

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

## Project Structure

```text
Receipt_Intake_Classification/
├── app.py
├── evaluate.py
├── expected_results.csv
├── requirements.txt
├── README.md
├── sample_docs/
├── test_pdfs/
└── src/
    ├── __init__.py
    ├── document_classifier.py
    ├── field_extractor.py
    ├── ocr_processor.py
    ├── pdf_reader.py
    └── validator.py
```

`test_pdfs/` contains the local test PDFs used by `evaluate.py`. `sample_docs/` can be used for additional sample documents.

## Design and Processing Workflow

The application separates PDF reading, document classification, field extraction, and validation into individual modules.

1. **PDF upload:** Streamlit accepts one or more PDF files.
2. **PDF reading:** `src/pdf_reader.py` extracts embedded text from digital PDFs and uses the OCR path when needed for scanned documents.
3. **OCR:** `src/ocr_processor.py` supports text recognition from scanned PDF pages/images through Tesseract OCR.
4. **Document classification:** `src/document_classifier.py` identifies the document type using rule-based keyword matching.
5. **Category classification:** The same module assigns an expense category based on document clues and keywords.
6. **Field extraction:** `src/field_extractor.py` extracts the vendor, date, amount, currency, and receipt/invoice number.
7. **Validation:** `src/validator.py` checks extracted fields and determines whether the document is complete, needs review, is unsupported, or has failed.
8. **Results and export:** `app.py` displays processing results, filters, document details, extracted text, and CSV export.

Each PDF is processed independently so that an error in one uploaded file does not prevent other uploaded files from being processed.

## Evaluation

The `evaluate.py` script compares five fields from each test PDF with the matching row in `expected_results.csv`:

- Document Type
- Category
- Vendor
- Date
- Amount

The script reads PDFs from the `test_pdfs/` folder and expected values from `expected_results.csv` in the project root.

Run the evaluation from the project root:

```powershell
python evaluate.py
```

### Current Local Evaluation Results

The latest reported local test run evaluated 12 PDFs and returned:

| Field | Correct | Field accuracy |
|---|---:|---:|
| Document Type | 12/12 | 100% |
| Category | 12/12 | 100% |
| Vendor | 12/12 | 100% |
| Date | 12/12 | 100% |
| Amount | 12/12 | 100% |

The evaluation reported no mismatches for these 12 test PDFs. These results apply only to the included local test dataset and do not guarantee the same accuracy on unseen or real-world documents.

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
7. **Test coverage:** The reported evaluation measures performance on the included 12-document test set only. More diverse real-world documents are needed to assess generalization.

## Future Improvements

- Add more diverse real-world test documents and expand evaluation coverage.
- Improve handling of overlapping keywords and unfamiliar document layouts.
- Add more robust checks for ambiguous dates, currencies, and extracted totals.
- Track additional evaluation metrics for classification and field extraction.
