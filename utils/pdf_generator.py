"""
Executive-grade PDF Report Generator using ReportLab.
Renders structured, styled PDF reports with KPI score tables, skills breakdown,
strengths, roadmap, and interview preparation questions.
"""
import os
import xml.sax.saxutils as saxutils
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from utils.parser import parse_analysis_output


def escape_xml(text):
    """Safely escape text for ReportLab XML/HTML-like formatting tags."""
    if not text:
        return ""
    return saxutils.escape(str(text))


def format_bullet_points(text_block, bullet_style):
    """Convert raw text block with newlines/dashes/numbers into styled Paragraphs."""
    paragraphs = []
    lines = str(text_block).split("\n")
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        # Remove markdown symbols
        cleaned = cleaned.lstrip("•-*#0123456789. ")
        escaped = escape_xml(cleaned)
        paragraphs.append(Paragraph(f"• &nbsp; {escaped}", bullet_style))
    return paragraphs


def create_pdf(analysis_data, resume_filename="Resume", output_filename="Resume_Analysis_Report.pdf"):
    """
    Generate an executive PDF analysis report.

    Parameters:
        analysis_data (dict | str): Parsed dictionary or raw analysis text string.
        resume_filename (str): Name of uploaded resume file.
        output_filename (str): Destination PDF file path.

    Returns:
        str: Absolute or relative path to the generated PDF.
    """
    # If a raw string is passed, parse it
    if isinstance(analysis_data, str):
        parsed = parse_analysis_output(analysis_data)
    else:
        parsed = analysis_data

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename) or ".", exist_ok=True)

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e3a8a"),
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155")
    )

    bullet_style = ParagraphStyle(
        "BulletItem",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=3
    )

    kpi_title_style = ParagraphStyle(
        "KPITitle",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        alignment=1
    )

    kpi_value_style = ParagraphStyle(
        "KPIValue",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        alignment=1
    )

    kpi_sub_style = ParagraphStyle(
        "KPISub",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10,
        textColor=colors.HexColor("#2563eb"),
        alignment=1
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("AI RESUME EVALUATION & ATS AUDIT REPORT", title_style))
    analysis_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    meta_text = f"<b>Candidate Document:</b> {escape_xml(resume_filename)} &nbsp;|&nbsp; <b>Report Date:</b> {analysis_date}"
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=14))

    # 2. Executive KPI Cards Table
    ats_score = parsed.get("ats_score", 0)
    job_score = parsed.get("job_score", 0)

    ats_status = "Excellent" if ats_score >= 80 else ("Good" if ats_score >= 65 else "Needs Work")
    job_status = "High Fit" if job_score >= 80 else ("Moderate Fit" if job_score >= 60 else "Low Alignment")

    kpi_data = [
        [
            Paragraph("ATS COMPATIBILITY", kpi_title_style),
            Paragraph("JOB MATCH ALIGNMENT", kpi_title_style),
            Paragraph("APPLICATION READINESS", kpi_title_style),
        ],
        [
            Paragraph(f"{ats_score}%", kpi_value_style),
            Paragraph(f"{job_score}%", kpi_value_style),
            Paragraph("READY" if ats_score >= 75 and job_score >= 70 else "OPTIMIZE", kpi_value_style),
        ],
        [
            Paragraph(ats_status, kpi_sub_style),
            Paragraph(job_status, kpi_sub_style),
            Paragraph("Verified by Groq AI Engine", kpi_sub_style),
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[180, 180, 180])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # 3. Overall Summary
    summary_text = parsed.get("summary", "Analysis completed successfully.")
    story.append(Paragraph("Executive Summary", section_heading))
    story.append(Paragraph(escape_xml(summary_text), body_style))
    story.append(Spacer(1, 10))

    # 4. Matching & Missing Skills
    matching_skills = parsed.get("matching_skills", "Not Available")
    missing_skills = parsed.get("missing_skills", "Not Available")

    skills_data = [
        [
            Paragraph("<b>Matching Skills Identified</b>", ParagraphStyle("HMatch", parent=body_style, textColor=colors.HexColor("#15803d"))),
            Paragraph("<b>Missing / Gap Skills to Address</b>", ParagraphStyle("HMiss", parent=body_style, textColor=colors.HexColor("#b91c1c"))),
        ],
        [
            Paragraph(escape_xml(matching_skills).replace("\n", "<br />"), bullet_style),
            Paragraph(escape_xml(missing_skills).replace("\n", "<br />"), bullet_style),
        ]
    ]
    skills_table = Table(skills_data, colWidths=[270, 270])
    skills_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0fdf4")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#fef2f2")),
        ("BOX", (0, 0), (0, -1), 0.5, colors.HexColor("#bbf7d0")),
        ("BOX", (1, 0), (1, -1), 0.5, colors.HexColor("#fecaca")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 12))

    # 5. Strengths & Weaknesses
    strengths = parsed.get("strengths", "")
    weaknesses = parsed.get("weaknesses", "")

    sw_data = [
        [
            Paragraph("<b>Key Candidate Strengths</b>", ParagraphStyle("HStr", parent=body_style, textColor=colors.HexColor("#1d4ed8"))),
            Paragraph("<b>Identified Weaknesses / Gaps</b>", ParagraphStyle("HWeak", parent=body_style, textColor=colors.HexColor("#b45309"))),
        ],
        [
            Paragraph(escape_xml(strengths).replace("\n", "<br />"), bullet_style),
            Paragraph(escape_xml(weaknesses).replace("\n", "<br />"), bullet_style),
        ]
    ]
    sw_table = Table(sw_data, colWidths=[270, 270])
    sw_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#fffbeb")),
        ("BOX", (0, 0), (0, -1), 0.5, colors.HexColor("#bfdbfe")),
        ("BOX", (1, 0), (1, -1), 0.5, colors.HexColor("#fde68a")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(sw_table)
    story.append(Spacer(1, 12))

    # 6. Actionable Suggestions
    suggestions = parsed.get("suggestions", "")
    if suggestions and suggestions != "Not Available":
        story.append(Paragraph("Actionable Improvement Suggestions", section_heading))
        for p in format_bullet_points(suggestions, bullet_style):
            story.append(p)
        story.append(Spacer(1, 10))

    # 7. Resume Improvement Roadmap
    roadmap = parsed.get("roadmap", "")
    if roadmap and roadmap != "Not Available":
        story.append(Paragraph("Step-by-Step Improvement Roadmap", section_heading))
        lines = [ln.strip() for ln in roadmap.split("\n") if ln.strip()]
        for idx, line in enumerate(lines, 1):
            clean_ln = line.lstrip("0123456789.- ")
            item_p = Paragraph(f"<b>Step {idx}:</b> {escape_xml(clean_ln)}", bullet_style)
            story.append(item_p)
        story.append(Spacer(1, 10))

    # 8. Technical Interview Preparation
    questions = parsed.get("questions", "")
    if questions and questions != "Not Available":
        story.append(KeepTogether([
            Paragraph("Technical & Behavioral Interview Preparation", section_heading),
            Paragraph(
                escape_xml(questions).replace("\n", "<br />"),
                ParagraphStyle("QStyle", parent=body_style, fontSize=9, leading=13)
            )
        ]))

    # Footer note
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
    footer_text = "Generated by AI Resume Analyzer • Powered by Groq AI"
    story.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=subtitle_style, alignment=1, fontSize=8)))

    # Build the PDF document
    doc.build(story)

    return output_filename
