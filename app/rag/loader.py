import os

from pypdf import PdfReader
from docx import Document


def load_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def load_docx(file_path: str) -> str:
    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def load_document(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()

    if extension in [".txt", ".md"]:
        return load_txt(file_path)

    elif extension == ".pdf":
        return load_pdf(file_path)

    elif extension == ".docx":
        return load_docx(file_path)

    else:
        raise ValueError("Unsupported file type")