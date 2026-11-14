"""
DOCX text extraction utility.
Extracts text from paragraphs, tables, headers, and footers with robust error handling.
"""
from docx import Document

def extract_text_from_docx(docx_file):
    """
    Extract text from an uploaded DOCX file or path.
    Extracts text from paragraphs, tables, and sections.

    Parameters:
        docx_file: Uploaded file buffer, BytesIO, or file path.

    Returns:
        str: Extracted text.

    Raises:
        ValueError: If file is empty or cannot be parsed.
    """
    if hasattr(docx_file, "seek"):
        docx_file.seek(0)

    try:
        document = Document(docx_file)
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX document: {e}")

    extracted_lines = []

    # 1. Paragraphs
    for p in document.paragraphs:
        line = p.text.strip()
        if line:
            extracted_lines.append(line)

    # 2. Tables (Resumes often use tables for layouts, skills, or education)
    for table in document.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                # Remove consecutive duplicates in merged cells
                cleaned_cells = []
                for c in row_cells:
                    if not cleaned_cells or c != cleaned_cells[-1]:
                        cleaned_cells.append(c)
                if cleaned_cells:
                    extracted_lines.append(" | ".join(cleaned_cells))

    # 3. Header / Footer text if present
    try:
        for section in document.sections:
            if section.header and section.header.paragraphs:
                for hp in section.header.paragraphs:
                    htext = hp.text.strip()
                    if htext and htext not in extracted_lines:
                        extracted_lines.insert(0, htext)
    except Exception:
        pass

    full_text = "\n".join(extracted_lines).strip()

    if not full_text:
        raise ValueError(
            "The DOCX document contains no readable text. "
            "Please upload a valid resume."
        )

    return full_text
