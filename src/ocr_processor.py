import pytesseract
from PIL import Image

# Tell Python where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_image(image_path):
    """Extract text from an image using OCR."""

    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)

    return extracted_text.strip()
