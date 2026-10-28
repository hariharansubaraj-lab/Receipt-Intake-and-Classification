from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image
import pytesseract


# Location of Tesseract OCR on Windows
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def read_pdf(file_path):
    """Read digital PDFs directly and use OCR for scanned PDFs."""

    try:
        reader = PdfReader(file_path)

        # Password-protected PDFs need separate handling.
        if reader.is_encrypted:
            return {
                "text": "",
                "source": "Digital",
                "error": "Password-protected PDF"
            }

        # First, try extracting the existing text layer.
        extracted_text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

        # If useful text exists, return it directly.
        if extracted_text.strip():
            return {
                "text": extracted_text.strip(),
                "source": "Digital",
                "error": ""
            }

        # No usable text: render each page and apply OCR.
        pdf_document = pdfium.PdfDocument(file_path)
        ocr_text = []

        try:
            for page in pdf_document:
                image = page.render(scale=2).to_pil()
                page_text = pytesseract.image_to_string(image)

                if page_text.strip():
                    ocr_text.append(page_text.strip())
        finally:
            pdf_document.close()

        return {
            "text": "\n".join(ocr_text),
            "source": "OCR",
            "error": ""
        }

    except Exception as error:
        return {
            "text": "",
            "source": "",
            "error": str(error)
        }
