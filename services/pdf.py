import pymupdf

from config.gemini import client, MODEL_NAME


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extracts text from a PDF file provided as bytes."""

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        pages_text = [
            page.get_text("text")
            for page in pdf
        ]

    full_text = "\n".join(pages_text).strip()

    if not full_text:
        raise ValueError(
            "No readable text was found in this PDF."
        )

    return full_text


def analyze_pdf(prompt: str, pdf_text: str) -> str:
    """Sends extracted PDF text and a prompt to Gemini."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, pdf_text],
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
