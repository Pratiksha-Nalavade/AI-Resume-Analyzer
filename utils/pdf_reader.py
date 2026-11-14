"""
PDF text extraction utility supporting both pypdf and PyPDF2.
Handles stream seeking, encrypted files, and corrupted page streams gracefully.
"""
import io
import warnings

def extract_text_from_pdf(pdf_file):
    """
    Extract text from an uploaded PDF file or file path.

    Parameters:
        pdf_file: Uploaded file buffer, BytesIO, or file path.

    Returns:
        str: Extracted clean text content.

    Raises:
        ValueError: If file is empty or cannot be read.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                raise ImportError("Neither 'pypdf' nor 'PyPDF2' is installed. Please install pypdf.")

    # Reset buffer position if available
    if hasattr(pdf_file, "seek"):
        pdf_file.seek(0)

    try:
        reader = PdfReader(pdf_file)
    except Exception as e:
        raise ValueError(f"Failed to open PDF document: {e}")

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise ValueError("The PDF is password protected. Please provide an unencrypted resume.")

    text_parts = []
    total_pages = len(reader.pages)

    if total_pages == 0:
        raise ValueError("The uploaded PDF has no pages.")

    for idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())
        except Exception as e:
            print(f"Warning: Could not extract text from page {idx + 1}: {e}")

    full_text = "\n\n".join(text_parts).strip()

    if not full_text:
        raise ValueError(
            "No readable text could be extracted from this PDF. "
            "It may be a scanned image or photo. Please provide a text-based PDF or DOCX file."
        )

    return full_text
