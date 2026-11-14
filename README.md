# 📄 AI Resume Analyzer Pro

An enterprise-grade, AI-powered Resume Evaluation, ATS (Applicant Tracking System) Compatibility Audit, and Career Coaching platform built with **Python**, **Streamlit**, and the **Groq AI (Llama 3.3 70B)** high-speed inference engine.

---

## 🌟 Key Features

### 1. 📤 Multi-Format Resume Upload & Parsing
- Supports text extraction from both **PDF (`.pdf`)** and **Microsoft Word (`.docx`)** documents.
- Multi-column and table extraction support for modern resume templates.
- Metadata and text metrics display: word count, character count, file size, and estimated reading time.
- Handles encrypted PDFs, corrupted streams, and empty uploads with user-friendly error alerts.

### 2. 🏛️ Five-Pillar ATS Compatibility Scoring Engine
An in-depth, deterministic scoring algorithm evaluating resumes against 5 core ATS dimensions (0–100 scale):
1. **Contact Information & Online Presence (15 pts):** Validates email, phone number, LinkedIn, and GitHub profiles.
2. **Standard Section Headings (25 pts):** Scans for ATS-standard sections (*Summary*, *Experience*, *Education*, *Skills*, *Projects*, *Certifications*).
3. **Skills & Keyword Density (25 pts):** Cross-references technical competencies against a 70+ skill taxonomy and job description requirements.
4. **Action Verbs & Measurable Impact (15 pts):** Analyzes high-impact verbs (*engineered*, *optimized*, *spearheaded*) and quantifiable metrics (*%, $, numbers*).
5. **Formatting & Readability (20 pts):** Assesses optimal word counts (400–900 words), bulleted layout, and sentence brevity.

### 3. 🤖 Deep Groq AI Evaluation
- Leverages **Groq's LLaMA-3.3-70B-Versatile** model (with selectable fallbacks to `llama-3.1-8b-instant`).
- Provides comprehensive candidate fit appraisals, strengths analysis, identified gaps, and actionable recommendations.
- Non-blocking design: deterministic local ATS scoring works independently even if API keys are not yet configured.

### 4. 🎯 Job Description Alignment & Keyword Match
- Compares candidate qualifications directly against job requirements.
- Highlights exact **Matching Skills** (green badges) and critical **Missing Skills** (red badges).
- Generates high-priority keyword recommendations to bypass initial ATS recruiter filters.

### 5. 🗺️ Prioritized Step-by-Step Resume Roadmap
- Actionable 5-phase optimization roadmap.
- Interactive checklist UI allowing candidates to track progress as they polish their resume.

### 6. 💬 Technical & Project Interview Preparation
- Generates custom interview questions based directly on the candidate's stated projects and the target job description.
- Includes expected answer guidelines, evaluation focus criteria, and the STAR framework (Situation, Task, Action, Result).

### 7. 📊 Executive Dashboard & History Telemetry
- Real-time KPIs: Latest ATS Score, Job Match Score, Total Evaluations, and Highest ATS Score.
- Interactive historical trajectory chart tracking score improvements across revisions.
- Searchable and inspectable evaluation log stored locally in `data/history.csv`.

### 8. 📑 Executive PDF Report Generation
- One-click generation of a styled, publication-ready PDF evaluation report built with **ReportLab**.
- Formatted tables for KPI scores, matching/missing skills, strengths, weaknesses, roadmap, and interview prep questions.

---

## 🏗️ Project Architecture

```
AI-Resume-Analyzer/
├── assets/
│   ├── logo.png               # Application branding logo
│   └── styles.css             # Modern Dark & Light theme styling
├── components/
│   ├── dashboard.py           # Dashboard KPIs, charts, and activity log
│   ├── file_details.py        # Document metadata & reading stats
│   ├── interview.py           # Technical interview questions component
│   ├── roadmap.py             # Interactive step-by-step roadmap
│   └── sidebar.py             # Sidebar navigation & status indicators
├── data/
│   ├── history.csv            # Evaluation history database
│   └── history_details.json   # Detailed evaluation archives
├── sample_resumes/
│   ├── sample_software_engineer_resume.pdf   # Test PDF resume
│   └── sample_software_engineer_resume.docx  # Test DOCX resume
├── utils/
│   ├── __init__.py
│   ├── analyzer.py            # Groq AI integration & prompt orchestration
│   ├── ats_score.py           # 5-Pillar ATS scoring engine
│   ├── docx_reader.py         # DOCX paragraphs & table extraction
│   ├── history.py             # History storage, retrieval, and telemetry
│   ├── parser.py              # Robust markdown output parser
│   ├── pdf_generator.py       # ReportLab PDF report generation
│   ├── pdf_reader.py          # PyPDF / PyPDF2 text extraction
│   └── skills.py              # 70+ skills taxonomy & matcher
├── .env.example               # Environment variables template
├── app.py                     # Main Streamlit web application
├── config.py                  # Dynamic configuration & API discovery
├── requirements.txt           # Python dependencies
├── test_api.py                # Groq API connectivity test
├── test_models.py             # Groq model listing utility
└── test_suite.py              # Comprehensive automated test suite
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.13, 3.14)
- Pip package manager

### 2. Clone or Navigate to the Project Directory
```bash
cd c:\AI-Resume-Analyzer
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Groq API Key (Free)
1. Sign up for a free Groq account and create an API key at [https://console.groq.com/keys](https://console.groq.com/keys).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and paste your key:
   ```env
   GROQ_API_KEY=gsk_your_actual_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
   *(Note: You can also enter or update your API key directly within the app's **Settings & API** interface at any time!)*

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Verification

The project includes automated verification tools:

### Run Full Test Suite
Runs unit tests for text extraction (PDF & DOCX), ATS calculation, skills taxonomy matching, parser robustness, PDF report generation, and history persistence:
```bash
python test_suite.py
```

### Test Groq API Connectivity
Verify your Groq API key and test model completions:
```bash
python test_api.py
```

### List Available Groq Models
List all active LLM models on your Groq account:
```bash
python test_models.py
```

---

## 🎓 Placement Interview Talking Points

If presenting this project during a technical or placement interview, highlight these engineering highlights:

1. **Dual Evaluation Engine (Deterministic + Generative AI):**
   - The platform doesn't rely solely on an LLM. It implements a deterministic, multi-pillar ATS heuristic engine (`utils/ats_score.py`) alongside Groq's LLaMA 3.3 70B model. If an API outage occurs or keys are missing, the system gracefully degrades to deterministic analysis without throwing errors or generating fake results.

2. **Defensive Parsing Architecture:**
   - LLMs can format output unpredictably (markdown headers, bolding, colons). The parser (`utils/parser.py`) uses boundary-safe regular expressions and split-fallbacks to extract sections cleanly regardless of model formatting variations.

3. **Multi-Column & Table Resume Extraction:**
   - Many candidates design resumes with side-by-side columns or tables for skills. `utils/docx_reader.py` extracts text from both paragraphs and table structures to avoid dropping critical skills.

4. **Streamlit Session State & Persistence:**
   - Separated navigation from execution to prevent data loss on widget reruns. Full evaluation state is retained across views (*ATS Score*, *Job Match*, *Roadmap*, *Interview Prep*).

5. **Enterprise-Grade PDF Reporting:**
   - Generates high-resolution PDF documents with ReportLab (`utils/pdf_generator.py`), complete with safe XML escaping, custom KPI tables, and clean typography.
