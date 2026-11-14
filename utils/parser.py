"""
Robust parser for AI Resume Analysis responses.
Extracts sections, scores, lists, and roadmap steps regardless of markdown variations.
"""
import re


def clean_text_block(block):
    """Clean markdown bullet points and excess whitespace from a text block."""
    if not block or not isinstance(block, str):
        return ""
    cleaned = block.strip()
    # Strip leading markdown artifacts if needed
    cleaned = re.sub(r"^\s*[:\-\*]+\s*", "", cleaned)
    return cleaned.strip()


def extract_section(text, start, end=None):
    """
    Extract a section of text between start and end keywords.
    Handles varied markdown wrappers like ** or ## or colons.
    """
    if not text or not isinstance(text, str):
        return "Not Available"

    start_clean = re.escape(start.replace(":", "").strip())
    pattern = rf"(?:###?\s*|\*\*|\b){start_clean}(?:\*\*|:|\s)*[:\n]?"

    if end:
        end_clean = re.escape(end.replace(":", "").strip())
        full_pattern = rf"{pattern}\s*([\s\S]*?)(?=(?:###?\s*|\*\*|\b){end_clean}(?:\*\*|:|\s)*[:\n]?|\Z)"
    else:
        full_pattern = rf"{pattern}\s*([\s\S]*?\Z)"

    match = re.search(full_pattern, text, re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        # Clean trailing section separators if any
        content = re.sub(r"(?:###|\*\*)(?:.*)$", "", content).strip()
        return content if content else "Not Available"

    # Fallback to simple split if regex misses
    try:
        lower_text = text.lower()
        lower_start = start.lower().replace(":", "").strip()
        start_idx = lower_text.find(lower_start)
        if start_idx != -1:
            after_start = text[start_idx + len(lower_start):]
            if after_start.startswith(":") or after_start.startswith("**"):
                after_start = after_start.lstrip(":* \t\n")
            if end:
                lower_end = end.lower().replace(":", "").strip()
                end_idx = after_start.lower().find(lower_end)
                if end_idx != -1:
                    return after_start[:end_idx].strip()
            return after_start.strip()
    except Exception:
        pass

    return "Not Available"


def get_scores(analysis):
    """
    Extract ATS Score and Job Match Score as integers between 0 and 100.
    """
    if not analysis or not isinstance(analysis, str):
        return 0, 0

    ats_match = re.search(r"(?:ATS Score|ATS Compatibility(?: Score)?)[*:\s\-]+(\d{1,3})", analysis, re.IGNORECASE)
    ats_score = int(ats_match.group(1)) if ats_match else 0

    job_match = re.search(r"(?:Job Match Score|Match Score|Job Match)[*:\s\-]+(\d{1,3})", analysis, re.IGNORECASE)
    job_score = int(job_match.group(1)) if job_match else 0

    return max(0, min(100, ats_score)), max(0, min(100, job_score))


def parse_analysis_output(analysis_text):
    """
    Parse full AI analysis response into a clean, structured dictionary.
    """
    ats_score, job_score = get_scores(analysis_text)

    matching_skills = extract_section(analysis_text, "Matching Skills", "Missing Skills")
    missing_skills = extract_section(analysis_text, "Missing Skills", "Overall Summary")
    summary = extract_section(analysis_text, "Overall Summary", "Strengths")
    strengths = extract_section(analysis_text, "Strengths", "Weaknesses")
    weaknesses = extract_section(analysis_text, "Weaknesses", "Suggestions")
    suggestions = extract_section(analysis_text, "Suggestions", "Resume Improvement Roadmap")
    roadmap = extract_section(analysis_text, "Resume Improvement Roadmap", "Technical Interview Questions")
    questions = extract_section(analysis_text, "Technical Interview Questions")

    return {
        "ats_score": ats_score,
        "job_score": job_score,
        "matching_skills": clean_text_block(matching_skills),
        "missing_skills": clean_text_block(missing_skills),
        "summary": clean_text_block(summary),
        "strengths": clean_text_block(strengths),
        "weaknesses": clean_text_block(weaknesses),
        "suggestions": clean_text_block(suggestions),
        "roadmap": clean_text_block(roadmap),
        "questions": clean_text_block(questions),
        "raw_text": analysis_text
    }
