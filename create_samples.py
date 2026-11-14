"""
Helper script to generate clean sample resume files in DOCX and PDF formats for testing.
"""
import os
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("sample_resumes", exist_ok=True)

# ----------------------------------------------------------------------
# 1. Generate DOCX Sample Resume
# ----------------------------------------------------------------------
doc = Document()
doc.add_heading("Alex Morgan", level=0)
doc.add_paragraph("Email: alex.morgan@example.com | Phone: (555) 234-5678 | San Francisco, CA\nLinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan")

doc.add_heading("Professional Summary", level=1)
doc.add_paragraph(
    "Full Stack Software Engineer with 3+ years of experience designing and deploying scalable web applications, "
    "RESTful microservices, and high-performance cloud architectures. Proven expertise in Python, React, PostgreSQL, "
    "and Docker, delivering 30% reduction in API response latency across distributed systems."
)

doc.add_heading("Core Technical Skills", level=1)
doc.add_paragraph("• Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3")
doc.add_paragraph("• Frameworks & Libraries: React, FastAPI, Django, Flask, Node.js, Express, Tailwind CSS")
doc.add_paragraph("• Databases & Caching: PostgreSQL, MongoDB, Redis, MySQL")
doc.add_paragraph("• Cloud & DevOps: AWS (EC2, S3), Docker, CI/CD, GitHub Actions, Linux, Git")
doc.add_paragraph("• Methodologies: Agile/Scrum, RESTful APIs, Microservices, Unit Testing (PyTest)")

doc.add_heading("Work Experience", level=1)
doc.add_heading("Software Engineer | CloudScale Tech | 2023 - Present", level=2)
doc.add_paragraph("• Engineered microservices using FastAPI and PostgreSQL, serving 100,000+ daily active users.")
doc.add_paragraph("• Implemented Redis caching layers, reducing database query load by 40% and cutting latency to under 80ms.")
doc.add_paragraph("• Built dynamic, responsive dashboard interfaces in React and TypeScript with 99.8% crash-free sessions.")
doc.add_paragraph("• Automated CI/CD build and testing pipelines using GitHub Actions and Docker, reducing deployment cycle times by 50%.")

doc.add_heading("Junior Full Stack Developer | InnovateX Labs | 2021 - 2023", level=2)
doc.add_paragraph("• Developed full stack features with Django, React, and MySQL for an enterprise SaaS platform.")
doc.add_paragraph("• Integrated third-party payment gateways and webhook notification engines with robust error recovery.")
doc.add_paragraph("• Authored unit and integration test suites using PyTest, boosting test coverage from 62% to 88%.")

doc.add_heading("Projects", level=1)
doc.add_heading("AI Document Analyzer & Search Engine", level=2)
doc.add_paragraph("• Architected a semantic document search platform using Python, FastAPI, and vector embeddings.")
doc.add_paragraph("• Deployed containerized services to AWS EC2 using Docker Compose and automated SSL via Nginx reverse proxy.")

doc.add_heading("Education", level=1)
doc.add_paragraph("Bachelor of Science in Computer Science | University of California, Berkeley (2017 - 2021)")

docx_path = os.path.join("sample_resumes", "sample_software_engineer_resume.docx")
doc.save(docx_path)
print(f"Created sample DOCX: {docx_path}")

# ----------------------------------------------------------------------
# 2. Generate PDF Sample Resume
# ----------------------------------------------------------------------
pdf_path = os.path.join("sample_resumes", "sample_software_engineer_resume.pdf")
pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
styles = getSampleStyleSheet()

h1_style = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#1e3a8a"), spaceBefore=10, spaceAfter=4)
h2_style = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=colors.HexColor("#0f172a"), spaceBefore=6, spaceAfter=2)
body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=colors.HexColor("#334155"))
bullet_style = ParagraphStyle("Bullet", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"), spaceAfter=2)

story = []
story.append(Paragraph("<b>ALEX MORGAN</b>", ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor("#0f172a"))))
story.append(Paragraph("Email: alex.morgan@example.com | Phone: (555) 234-5678 | San Francisco, CA | LinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan", body_style))
story.append(Spacer(1, 8))

story.append(Paragraph("PROFESSIONAL SUMMARY", h1_style))
story.append(Paragraph(
    "Full Stack Software Engineer with 3+ years of experience designing and deploying scalable web applications, "
    "RESTful microservices, and high-performance cloud architectures. Proven expertise in Python, React, PostgreSQL, "
    "and Docker, delivering 30% reduction in API response latency across distributed systems.",
    body_style
))
story.append(Spacer(1, 6))

story.append(Paragraph("CORE TECHNICAL SKILLS", h1_style))
story.append(Paragraph("• <b>Languages:</b> Python, JavaScript, TypeScript, SQL, HTML5, CSS3", bullet_style))
story.append(Paragraph("• <b>Frameworks & Tools:</b> React, FastAPI, Django, Flask, Node.js, Express, Tailwind CSS", bullet_style))
story.append(Paragraph("• <b>Databases:</b> PostgreSQL, MongoDB, Redis, MySQL", bullet_style))
story.append(Paragraph("• <b>DevOps & Cloud:</b> AWS (EC2, S3), Docker, CI/CD, GitHub Actions, Linux, Git", bullet_style))
story.append(Spacer(1, 6))

story.append(Paragraph("WORK EXPERIENCE", h1_style))
story.append(Paragraph("<b>Software Engineer</b> — CloudScale Tech (2023 - Present)", h2_style))
story.append(Paragraph("• Engineered microservices using FastAPI and PostgreSQL, serving 100,000+ daily active users.", bullet_style))
story.append(Paragraph("• Implemented Redis caching layers, reducing database query load by 40% and cutting latency to under 80ms.", bullet_style))
story.append(Paragraph("• Built dynamic, responsive dashboard interfaces in React and TypeScript with 99.8% crash-free sessions.", bullet_style))
story.append(Paragraph("• Automated CI/CD build and testing pipelines using GitHub Actions and Docker, reducing deployment cycle times by 50%.", bullet_style))

story.append(Paragraph("<b>Junior Full Stack Developer</b> — InnovateX Labs (2021 - 2023)", h2_style))
story.append(Paragraph("• Developed full stack features with Django, React, and MySQL for an enterprise SaaS platform.", bullet_style))
story.append(Paragraph("• Integrated third-party payment gateways and webhook notification engines with robust error recovery.", bullet_style))
story.append(Paragraph("• Authored unit and integration test suites using PyTest, boosting test coverage from 62% to 88%.", bullet_style))
story.append(Spacer(1, 6))

story.append(Paragraph("PROJECTS", h1_style))
story.append(Paragraph("<b>AI Document Analyzer & Search Platform</b>", h2_style))
story.append(Paragraph("• Architected a semantic document search platform using Python, FastAPI, and vector embeddings.", bullet_style))
story.append(Paragraph("• Deployed containerized services to AWS EC2 using Docker Compose and automated SSL via Nginx reverse proxy.", bullet_style))
story.append(Spacer(1, 6))

story.append(Paragraph("EDUCATION", h1_style))
story.append(Paragraph("<b>Bachelor of Science in Computer Science</b> — University of California, Berkeley (2017 - 2021)", body_style))

pdf_doc.build(story)
print(f"Created sample PDF: {pdf_path}")
