
from pathlib import Path
import pandas as pd

from src.pdf_reader import read_pdf
from src.document_classifier import classify_document, classify_category
from src.field_extractor import extract_fields

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_docs"
EXPECTED_FILE = BASE_DIR / "expected_results.csv"

FIELDS = {
    "document_type": "Document Type",
    "category": "Category",
    "vendor": "Vendor",
    "date": "Date",
    "amount": "Amount",
}


def normalize(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in {"nan", "none"}:
        return ""
    return value


def normalize_amount(value):
    value = normalize(value).replace(",", "")
    if not value:
        return ""
    try:
        return f"{float(value):.2f}"
    except ValueError:
        return value


def evaluate():
    if not EXPECTED_FILE.exists():
        print("ERROR: expected_results.csv not found.")
        print(f"Expected location: {EXPECTED_FILE}")
        print("Place the official assessment CSV in the project root.")
        return

    if not SAMPLE_DIR.exists():
        print(f"ERROR: Sample PDF folder not found: {SAMPLE_DIR}")
        return

    expected_df = pd.read_csv(EXPECTED_FILE).fillna("")
    available_files = {
        path.name: path for path in SAMPLE_DIR.glob("*.pdf")
    }

    filename_column = next(
        (col for col in expected_df.columns
         if col.strip().lower() in {"filename", "file name", "pdf"}),
        None,
    )

    if filename_column is None:
        print("ERROR: CSV must contain a Filename column.")
        print("Available columns:", list(expected_df.columns))
        return

    column_map = {}
    for key, expected_name in FIELDS.items():
        matching = next(
            (col for col in expected_df.columns
             if col.strip().lower() == expected_name.lower()),
            None,
        )
        if matching is None:
            print(f"ERROR: Missing expected column: {expected_name}")
            return
        column_map[key] = matching

    comparisons = {key: [] for key in FIELDS}
    mismatches = []
    missing_pdfs = []

    for _, row in expected_df.iterrows():
        filename = normalize(row[filename_column])
        pdf_path = available_files.get(filename)

        if pdf_path is None:
            missing_pdfs.append(filename)
            continue

        try:
            result = read_pdf(str(pdf_path))
            text = result.get("text", "")
            document_type = classify_document(text)
            category = classify_category(document_type, text)
            extracted = extract_fields(text)

            actual = {
                "document_type": document_type,
                "category": category,
                "vendor": extracted.get("vendor", ""),
                "date": extracted.get("date", ""),
                "amount": extracted.get("amount", ""),
            }

            for key, expected_column in column_map.items():
                expected_value = normalize(row[expected_column])
                actual_value = normalize(actual[key])

                if key == "amount":
                    expected_value = normalize_amount(expected_value)
                    actual_value = normalize_amount(actual_value)

                correct = expected_value.casefold() == actual_value.casefold()
                comparisons[key].append(correct)

                if not correct:
                    mismatches.append({
                        "filename": filename,
                        "field": expected_column,
                        "expected": expected_value,
                        "actual": actual_value,
                    })

        except Exception as exc:
            print(f"ERROR processing {filename}: {exc}")
            for key in FIELDS:
                comparisons[key].append(False)
                mismatches.append({
                    "filename": filename,
                    "field": FIELDS[key],
                    "expected": normalize(row[column_map[key]]),
                    "actual": f"PROCESSING ERROR: {exc}",
                })

    print("\n=== RECEIPT CLASSIFICATION EVALUATION ===")
    print(f"Expected documents: {len(expected_df)}")
    print(f"Successfully matched to PDFs: "
          f"{len(expected_df) - len(missing_pdfs) - 0}")

    if missing_pdfs:
        print("\nMissing PDF files:")
        for filename in missing_pdfs:
            print(f"  - {filename}")

    print("\nField accuracy:")
    for key, label in FIELDS.items():
        values = comparisons[key]
        if values:
            accuracy = sum(values) / len(values) * 100
            print(f"{label}: {accuracy:.2f}% ({sum(values)}/{len(values)})")
        else:
            print(f"{label}: N/A (no PDFs evaluated)")

    print("\nMismatches:")
    if mismatches:
        for item in mismatches:
            print(
                f"- {item['filename']} | {item['field']} | "
                f"Expected: {item['expected']!r} | "
                f"Actual: {item['actual']!r}"
            )
    else:
        print("No mismatches among evaluated PDFs.")

    if missing_pdfs:
        print("\nWARNING: Evaluation is incomplete because PDFs are missing.")


if __name__ == "__main__":
    evaluate()
