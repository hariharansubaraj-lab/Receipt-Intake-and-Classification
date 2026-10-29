import os
import tempfile

import pandas as pd
import streamlit as st

from src.pdf_reader import read_pdf
from src.document_classifier import classify_document, classify_category
from src.field_extractor import extract_fields
from src.validator import validate_document


st.set_page_config(
    page_title="Receipt Intake & Classification",
    page_icon="📄",
    layout="wide"
)

st.title("Receipt Intake and Classification")
st.write(
    "Upload expense PDFs to extract details, classify documents "
    "and review their processing status."
)

st.caption("Only PDF files are supported.")


def get_category_reason(document_type, category, text):
    """Explain the main keyword or document clue behind the category."""

    if document_type == "Not an expense document":
        return "The document does not match the supported expense document types."

    if category == "Accommodation":
        return "Hotel or accommodation-related keywords were detected."

    if category == "Travel":
        return "Travel, transport or ticket-related keywords were detected."

    if category == "Food & Beverage":
        return "Food, restaurant or beverage-related keywords were detected."

    if category == "Office Supplies":
        return "Office supplies or stationery-related keywords were detected."

    return "No specific category keyword was found; classified as Other."


def process_pdf(file_bytes):
    """Process one PDF and return its extracted results."""

    temporary_path = None

    try:
        # Reject files that do not contain a PDF signature.
        if not file_bytes[:1024].lstrip().startswith(b"%PDF-"):
            return {
                "error": "Uploaded file is not a valid PDF."
            }

        # Save uploaded bytes temporarily because the reader uses a file path.
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False
        ) as temporary_file:
            temporary_file.write(file_bytes)
            temporary_path = temporary_file.name

        pdf_result = read_pdf(temporary_path)

        if pdf_result.get("error"):
            return {"error": pdf_result["error"]}

        text = pdf_result.get("text", "").strip()
        source = pdf_result.get("source", "")

        if not text:
            return {
                "error": "PDF contains no readable text after OCR."
            }

        document_type = classify_document(text)
        category = classify_category(document_type, text)

        fields = extract_fields(text)

        # Unsupported documents must not show expense fields.
        if document_type == "Not an expense document":
            fields = {
                "vendor": "",
                "date": "",
                "amount": "",
                "currency": "",
                "receipt_number": ""
            }
            confidence = 0.95
            reason = get_category_reason(document_type, category, text)
            status = validate_document(
                document_type, category, fields, confidence
            )
        else:
            
            # Heuristic confidence based on required-field completeness.
            required = [
                fields.get("vendor", ""),
                fields.get("date", ""),
                fields.get("amount", ""),
                fields.get("currency", "")
            ]

            filled_fields = sum(
                1 for value in required if str(value).strip()
            )
            confidence = 0.90 * (filled_fields / len(required))


            reason = get_category_reason(document_type, category, text)
            status = validate_document(
                document_type, category, fields, confidence
            )

        return {
            "document_type": document_type,
            "category": category,
            "vendor": fields.get("vendor", ""),
            "date": fields.get("date", ""),
            "amount": fields.get("amount", ""),
            "currency": fields.get("currency", ""),
            "receipt_number": fields.get("receipt_number", ""),
            "source": source,
            "confidence": confidence,
            "reason": reason,
            "status": status,
            "extracted_text": text
        }

    except Exception as error:
        return {"error": str(error)}

    finally:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError:
                pass


uploaded_files = st.file_uploader(
    "Choose one or more expense PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Process PDFs", type="primary"):
        results = []
        progress = st.progress(0)
        status_message = st.empty()

        total_files = len(uploaded_files)

        for index, uploaded_file in enumerate(uploaded_files):
            status_message.write(
                f"Processing {index + 1}/{total_files}: "
                f"{uploaded_file.name}"
            )

            result = process_pdf(uploaded_file.getvalue())

            if result.get("error"):
                results.append({
                    "filename": uploaded_file.name,
                    "document_type": "",
                    "category": "",
                    "vendor": "",
                    "date": "",
                    "amount": "",
                    "currency": "",
                    "receipt_number": "",
                    "source": "",
                    "confidence": 0.0,
                    "reason": result["error"],
                    "status": "Failed",
                    "extracted_text": ""
                })
            else:
                result["filename"] = uploaded_file.name
                results.append(result)

            progress.progress((index + 1) / total_files)

        st.session_state["receipt_results"] = results
        status_message.success("Processing finished.")


if "receipt_results" in st.session_state:
    results = st.session_state["receipt_results"]

    st.subheader("Processing Results")

    result_df = pd.DataFrame([
        {
            "Filename": item["filename"],
            "Source": item["source"],
            "Document Type": item["document_type"],
            "Category": item["category"],
            "Vendor": item["vendor"],
            "Date": item["date"],
            "Amount": item["amount"],
            "Currency": item["currency"],
            "Receipt/Invoice Number": item["receipt_number"],
            "Confidence": item["confidence"],
            "Reason": item["reason"],
            "Status": item["status"]
        }
        for item in results
    ])

    # Keep dates and amounts in consistent display/export formats.
    # Convert dates to YYYY-MM-DD and leave missing dates blank.
    result_df["Date"] = (
        pd.to_datetime(result_df["Date"], errors="coerce")
        .dt.strftime("%Y-%m-%d")
        .fillna("")
    )

    # Display amounts with two decimal places; leave missing amounts blank.
    result_df["Amount"] = pd.to_numeric(
        result_df["Amount"], errors="coerce"
    ).map(lambda value: f"{value:.2f}" if pd.notna(value) else "")

    def color_status(row):
        if row["Status"] == "Done":
            color = "#d8f3dc"
        elif row["Status"] == "Needs review":
            color = "#fff3cd"
        else:
            color = "#f8d7da"

        return [f"background-color: {color}"] * len(row)

    # Show filters while keeping all result rows available.
    selected_statuses = st.multiselect(
        "Filter by status",
        options=["Done", "Needs review", "Unsupported", "Failed"],
        default=["Done", "Needs review", "Unsupported", "Failed"]
    )

    selected_categories = st.multiselect(
        "Filter by category",
        options=[
            category for category in [
                "Food & Beverage",
                "Travel",
                "Accommodation",
                "Office Supplies",
                "Other"
            ]
            if category in result_df["Category"].values
        ],
        default=[
            category for category in [
                "Food & Beverage",
                "Travel",
                "Accommodation",
                "Office Supplies",
                "Other"
            ]
            if category in result_df["Category"].values
        ]
    )

    filtered_df = result_df[
        result_df["Status"].isin(selected_statuses)
        & result_df["Category"].isin(selected_categories)
    ]

    st.dataframe(
        filtered_df.style.apply(color_status, axis=1),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Expense Totals by Currency")

    completed_expenses = [
        item for item in results
        if item["status"] == "Done"
        and item["amount"]
        and item["currency"]
    ]

    if completed_expenses:
        totals_df = pd.DataFrame(completed_expenses)
        totals_df["amount"] = pd.to_numeric(totals_df["amount"])
        totals = (
            totals_df.groupby("currency")["amount"]
            .sum()
            .reset_index()
        )
        totals["amount"] = totals["amount"].map(
            lambda amount: f"{amount:.2f}"
        )
        st.dataframe(
            totals.rename(columns={
                "currency": "Currency",
                "amount": "Total Amount"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No completed expenses are available to total.")

    st.subheader("Document Details")

    selected_filename = st.selectbox(
        "Select a document",
        options=[item["filename"] for item in results]
    )

    selected_result = next(
        item for item in results
        if item["filename"] == selected_filename
    )

    left, right = st.columns(2)

    with left:
        st.write("**Status:**", selected_result["status"])
        st.write("**Document Type:**", selected_result["document_type"] or "—")
        st.write("**Category:**", selected_result["category"] or "—")
        st.write("**Vendor:**", selected_result["vendor"] or "—")
        st.write("**Date:**", selected_result["date"] or "—")
        st.write("**Amount:**", selected_result["amount"] or "—")
        st.write("**Currency:**", selected_result["currency"] or "—")
        st.write(
            "**Receipt/Invoice Number:**",
            selected_result["receipt_number"] or "—"
        )

    with right:
        st.write("**Source:**", selected_result["source"] or "—")
        st.write(
            "**Confidence:**",
            f'{selected_result["confidence"]:.0%}'
        )
        st.write("**Category Reason:**", selected_result["reason"])

    with st.expander("View extracted / OCR text"):
        st.text(selected_result["extracted_text"] or "No text available.")

    # Export all processed rows, not just the filtered view.
    csv_data = result_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download Results as CSV",
        data=csv_data,
        file_name="receipt_classification_results.csv",
        mime="text/csv"
    )
