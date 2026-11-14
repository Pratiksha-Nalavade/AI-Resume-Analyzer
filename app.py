"""
AI Resume Analyzer Pro
Main Streamlit Application
"""
import os
import time
import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration & environment
from config import (
    get_groq_api_key, get_selected_model, DEFAULT_MODEL
)

# Utilities
from utils.pdf_reader import extract_text_from_pdf
from utils.docx_reader import extract_text_from_docx
from utils.analyzer import analyze_resume
from utils.parser import parse_analysis_output, extract_section
from utils.ats_score import calculate_ats_score
from utils.skills import extract_skills, compare_skills
from utils.history import (
    save_history, get_history, get_history_stats, get_detailed_history, clear_history
)
from utils.pdf_generator import create_pdf

# Components
from components.sidebar import show_sidebar
from components.dashboard import show_dashboard
from components.file_details import show_file_details
from components.roadmap import show_roadmap
from components.interview import show_questions

# -------------------------------------------------------------
# Streamlit Page Setup
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# Session State Initialization
# -------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Resume Upload"

if "groq_api_key" not in st.session_state:
    env_key = get_groq_api_key()
    st.session_state["groq_api_key"] = env_key

if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = DEFAULT_MODEL

# Analysis storage
if "analysis_complete" not in st.session_state:
    st.session_state["analysis_complete"] = False

if "analysis_data" not in st.session_state:
    st.session_state["analysis_data"] = {}

# -------------------------------------------------------------
# CSS Styling & Theme Injection
# -------------------------------------------------------------
def load_css():
    base_css_file = os.path.join("assets", "styles.css")
    base_css = ""
    if os.path.exists(base_css_file):
        with open(base_css_file, "r", encoding="utf-8") as f:
            base_css = f.read()

    theme = st.session_state.get("theme", "dark")
    theme_file = os.path.join("assets", "light_theme.css" if theme == "light" else "dark_theme.css")
    theme_css = ""
    if os.path.exists(theme_file):
        with open(theme_file, "r", encoding="utf-8") as f:
            theme_css = f.read()

    st.markdown(f"<style>{base_css}\n{theme_css}</style>", unsafe_allow_html=True)


load_css()

# Render Sidebar Navigation
show_sidebar()

active_page = st.session_state["active_page"]


# =============================================================
# Helper: Sample Job Description for Testing & Demos
# =============================================================
SAMPLE_JD = """Full Stack Software Engineer
Responsibilities:
- Build, optimize, and maintain responsive web applications and scalable RESTful APIs.
- Collaborate across engineering and product teams in an agile environment.
- Design database schemas, write efficient SQL queries, and implement caching strategies.
- Deploy microservices to AWS cloud using Docker and CI/CD automation pipelines.

Required Qualifications & Skills:
- 2+ years experience in Python, JavaScript/TypeScript, and SQL.
- Strong proficiency with React or Next.js for frontend interfaces.
- Hands-on experience with backend frameworks like FastAPI, Django, Flask, or Node.js.
- Solid understanding of PostgreSQL or MongoDB, Redis, Docker, and Git.
- Exposure to AWS or Google Cloud, CI/CD pipelines, and unit testing.
- Strong problem-solving, communication, and team collaboration skills."""


# =============================================================
# PAGE: DASHBOARD
# =============================================================
if active_page == "Dashboard":
    latest_ats = st.session_state["analysis_data"].get("ats_score", None)
    latest_job = st.session_state["analysis_data"].get("job_score", None)
    latest_name = st.session_state.get("resume_name", None)

    show_dashboard(latest_ats, latest_job, latest_name)

    if not st.session_state["analysis_complete"]:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📤 Upload & Evaluate a New Resume", type="primary", use_container_width=True):
                st.session_state["active_page"] = "Resume Upload"
                st.rerun()


# =============================================================
# PAGE: RESUME UPLOAD & ANALYZER
# =============================================================
elif active_page == "Resume Upload":
    st.markdown("## 📤 Resume Upload & AI Analysis Engine")
    st.caption("Upload your resume in PDF or DOCX format and evaluate it against your target job description.")

    # Top API Status Banner
    current_key = get_groq_api_key()
    if not current_key or current_key == "gsk_your_groq_api_key_here":
        st.warning(
            "⚠️ **Groq API Key Not Configured:** Deterministic ATS and skills extraction will run locally. "
            "To unlock deep Groq LLM feedback, roadmap, and interview prep, configure your GROQ_API_KEY in your .env file."
        )

    # Main input grid
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📋 Target Job Description")
        load_sample = st.button("🧪 Insert Sample Job Description", key="btn_sample_jd")
        default_jd = SAMPLE_JD if load_sample else st.session_state.get("job_description_text", "")

        job_description = st.text_area(
            "Paste the job description or requirements:",
            value=default_jd,
            height=220,
            placeholder="Paste target job responsibilities, qualifications, and required skills here...",
            key="input_job_desc"
        )
        st.session_state["job_description_text"] = job_description

    with col2:
        st.markdown("### 📄 Candidate Resume Document")
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF or DOCX)",
            type=["pdf", "docx"],
            help="Supported formats: PDF (.pdf) and Microsoft Word (.docx)"
        )

        resume_text = ""
        if uploaded_file is not None:
            st.session_state["uploaded_file_name"] = uploaded_file.name
            try:
                if uploaded_file.name.lower().endswith(".pdf"):
                    resume_text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.name.lower().endswith(".docx"):
                    resume_text = extract_text_from_docx(uploaded_file)
                else:
                    st.error("Unsupported file extension. Please provide a PDF or DOCX file.")

                if resume_text:
                    st.success("✅ Document parsed successfully!")
                    show_file_details(uploaded_file, resume_text)
                    st.session_state["current_resume_text"] = resume_text

            except Exception as e:
                st.error(f"❌ Error extracting resume content: {e}")
                resume_text = ""

    # Preview extracted resume text
    if st.session_state.get("current_resume_text"):
        with st.expander("👁️ Inspect Extracted Resume Text Content", expanded=False):
            st.text_area(
                "Extracted Text",
                st.session_state["current_resume_text"],
                height=200,
                disabled=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Analyze Button Row
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        analyze_btn = st.button(
            "🤖 Analyze Resume & Run ATS Audit",
            use_container_width=True,
            type="primary"
        )

    # Process Analysis
    if analyze_btn:
        active_resume_text = st.session_state.get("current_resume_text", "")
        active_jd_text = st.session_state.get("job_description_text", "")
        active_filename = st.session_state.get("uploaded_file_name", "Candidate_Resume")

        if not active_resume_text:
            st.warning("⚠️ Please upload a valid resume in PDF or DOCX format.")
            st.stop()

        if not active_jd_text or not active_jd_text.strip():
            st.warning("⚠️ Please provide the target job description to run job matching.")
            st.stop()

        with st.spinner("🔍 Evaluating ATS compatibility and querying Groq AI Engine..."):
            start_time = time.time()

            # 1. Deterministic ATS and Skills Evaluation
            ats_audit = calculate_ats_score(active_resume_text, active_jd_text)
            skills_comparison = compare_skills(active_resume_text, active_jd_text)

            # 2. AI Analysis via Groq
            ai_analysis_text = ""
            groq_error = None
            try:
                ai_analysis_text = analyze_resume(
                    resume_text=active_resume_text,
                    job_description=active_jd_text,
                    api_key=st.session_state.get("groq_api_key"),
                    model=st.session_state.get("selected_model")
                )
            except Exception as e:
                groq_error = str(e)

            elapsed = round(time.time() - start_time, 2)

            # 3. Parse and Assemble Results
            if ai_analysis_text:
                parsed_res = parse_analysis_output(ai_analysis_text)
                # If Groq scores were parsed, use them, otherwise blend with deterministic
                ats_score = parsed_res["ats_score"] if parsed_res["ats_score"] > 0 else ats_audit["total_score"]
                job_score = parsed_res["job_score"] if parsed_res["job_score"] > 0 else skills_comparison["match_percentage"]

                analysis_payload = {
                    "ats_score": ats_score,
                    "job_score": job_score,
                    "ats_audit": ats_audit,
                    "skills_comparison": skills_comparison,
                    "matching_skills": parsed_res["matching_skills"] or ", ".join(skills_comparison["matching_skills"]),
                    "missing_skills": parsed_res["missing_skills"] or ", ".join(skills_comparison["missing_skills"]),
                    "summary": parsed_res["summary"],
                    "strengths": parsed_res["strengths"],
                    "weaknesses": parsed_res["weaknesses"],
                    "suggestions": parsed_res["suggestions"],
                    "roadmap": parsed_res["roadmap"],
                    "questions": parsed_res["questions"],
                    "raw_text": ai_analysis_text,
                    "ai_powered": True
                }
            else:
                # Deterministic fallback when AI is unavailable
                analysis_payload = {
                    "ats_score": ats_audit["total_score"],
                    "job_score": skills_comparison["match_percentage"],
                    "ats_audit": ats_audit,
                    "skills_comparison": skills_comparison,
                    "matching_skills": "\n".join([f"- {s}" for s in skills_comparison["matching_skills"]]) if skills_comparison["matching_skills"] else "None identified",
                    "missing_skills": "\n".join([f"- {s}" for s in skills_comparison["missing_skills"]]) if skills_comparison["missing_skills"] else "None missing",
                    "summary": f"Resume analysis completed with ATS score {ats_audit['total_score']}% and Job Match {skills_comparison['match_percentage']}%. Configure GROQ_API_KEY in your .env file to unlock deep LLM commentary.",
                    "strengths": "\n".join([f"- Found {len(skills_comparison['matching_skills'])} matching skills", f"- ATS format score: {ats_audit['breakdown']['readability_format']['score']}/{ats_audit['breakdown']['readability_format']['max']}"]),
                    "weaknesses": "\n".join([f"- Missing {len(skills_comparison['missing_skills'])} job skills: {', '.join(skills_comparison['missing_skills'][:5])}"]),
                    "suggestions": "\n".join([f"- {s}" for s in ats_audit["suggestions"]]),
                    "roadmap": "1. Integrate missing target skills into work experience.\n2. Quantify achievements with metrics and impact.\n3. Verify section headings match standard ATS conventions.\n4. Tailor summary to target job title.\n5. Re-check ATS score.",
                    "questions": "1. Q: Describe your experience with the primary technologies listed in your projects.\n   Focus: Architecture, design patterns, and problem resolution.\n2. Q: How have you optimized performance in past systems?\n   Focus: Metrics, bottleneck identification, profiling.",
                    "raw_text": "",
                    "ai_powered": False,
                    "groq_error": groq_error
                }

            # Save in session
            st.session_state["analysis_complete"] = True
            st.session_state["analysis_data"] = analysis_payload
            st.session_state["resume_name"] = active_filename

            # Save to permanent history
            save_history(
                filename=active_filename,
                ats_score=analysis_payload["ats_score"],
                job_score=analysis_payload["job_score"],
                matching_skills=analysis_payload["matching_skills"],
                missing_skills=analysis_payload["missing_skills"],
                analysis_raw=ai_analysis_text or analysis_payload["summary"]
            )

        if groq_error:
            st.warning(
                f"⚠️ **Note on AI Features:** Deterministic ATS evaluation succeeded in {elapsed}s, "
                f"but Groq AI was unavailable: `{groq_error}`. Please check your GROQ_API_KEY in the .env file."
            )
        else:
            st.success(f"✅ Full AI Evaluation completed in {elapsed} seconds!")

    # -------------------------------------------------------------
    # Live Results Section
    # -------------------------------------------------------------
    if st.session_state["analysis_complete"]:
        res = st.session_state["analysis_data"]
        st.divider()

        st.markdown("## 📊 Evaluation Summary")

        score_c1, score_c2, score_c3 = st.columns(3)
        with score_c1:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="score-card-title">📄 ATS Compatibility</div>
                    <div class="score-card-value">{res['ats_score']}%</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {res['ats_score']}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with score_c2:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="score-card-title">🎯 Job Description Match</div>
                    <div class="score-card-value">{res['job_score']}%</div>
                    <div class="progress-container">
                        <div class="progress-bar progress-bar-match" style="width: {res['job_score']}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with score_c3:
            status_text = "READY TO APPLY" if res['ats_score'] >= 80 and res['job_score'] >= 70 else "NEEDS REFINEMENT"
            status_color = "#10b981" if "READY" in status_text else "#f59e0b"
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="score-card-title">🚀 Application Readiness</div>
                    <div class="score-card-value" style="font-size: 26px; color: {status_color};">{status_text}</div>
                    <div class="score-card-subtext">
                        Navigation tabs on sidebar provide deep breakdowns.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Quick breakdown tabs
        tab_summary, tab_skills, tab_suggestions, tab_roadmap, tab_interview = st.tabs([
            "📝 Summary & Fit", "🧩 Skills Match", "💡 Suggestions", "🗺️ Roadmap", "💬 Interview Prep"
        ])

        with tab_summary:
            st.markdown("### Executive Fit Summary")
            st.info(res.get("summary", "Analysis completed."))
            col_s, col_w = st.columns(2)
            with col_s:
                st.markdown("#### 💪 Key Strengths")
                st.markdown(res.get("strengths", "No specific strengths highlighted."))
            with col_w:
                st.markdown("#### ⚠️ Identified Gaps")
                st.markdown(res.get("weaknesses", "No specific weaknesses highlighted."))

        with tab_skills:
            col_match, col_miss = st.columns(2)
            with col_match:
                st.markdown("#### 🟢 Matching Skills")
                st.markdown(res.get("matching_skills", "None identified."))
            with col_miss:
                st.markdown("#### 🔴 Missing / Desired Skills")
                st.markdown(res.get("missing_skills", "None missing."))

        with tab_suggestions:
            st.markdown("### Actionable Improvement Suggestions")
            st.markdown(res.get("suggestions", "No suggestions generated."))

        with tab_roadmap:
            show_roadmap(res.get("roadmap", ""))

        with tab_interview:
            show_questions(res.get("questions", ""))

        # Download Report Button
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_path = create_pdf(res, resume_filename=st.session_state.get("resume_name", "Resume"))
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Full PDF Analysis Report",
                    data=f.read(),
                    file_name="Resume_Analysis_Report.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )


# =============================================================
# PAGE: ATS SCORE DETAILED AUDIT
# =============================================================
elif active_page == "ATS Score":
    st.markdown("## 📊 ATS Compatibility Score & Audit")
    st.caption("Deep technical inspection of formatting, contact completeness, standard headings, and keyword density.")

    if not st.session_state["analysis_complete"]:
        # Fallback to history if available
        history_df = get_history()
        if not history_df.empty:
            latest = history_df.iloc[-1]
            score = int(latest["ATS Score"])
            st.metric("Latest Recorded ATS Score", f"{score}%")
            st.progress(score / 100)
            st.info("💡 To view the complete 5-pillar technical breakdown, upload and analyze a resume in the **Resume Upload** section.")
        else:
            st.info("Please upload and analyze a resume first to generate your ATS Compatibility Audit.")
    else:
        res = st.session_state["analysis_data"]
        ats_score = res["ats_score"]
        audit = res.get("ats_audit", {})
        breakdown = audit.get("breakdown", {})

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("ATS Compatibility Score", f"{ats_score}%")
            st.progress(ats_score / 100)
            if ats_score >= 80:
                st.success("🟢 **ATS Optimized:** High pass likelihood across Enterprise ATS systems.")
            elif ats_score >= 65:
                st.warning("🟡 **Moderate Compatibility:** Passes basic filters, but risks rejection on competitive roles.")
            else:
                st.error("🔴 **Low Compatibility:** Critical sections or keyword densities require revision.")

        with col2:
            st.markdown("### 🏛️ Five Pillars of ATS Compatibility")
            if breakdown:
                for k, item in breakdown.items():
                    sub_score = item["score"]
                    sub_max = item["max"]
                    sub_pct = round((sub_score / sub_max) * 100)
                    status_badge = "🟢 Pass" if item["status"] == "Pass" else "🟡 Improve"

                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                            <span class="pillar-label">{item['label']}</span>
                            <span class="pillar-subtext"><b>{sub_score}</b> / {sub_max} pts ({status_badge})</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.progress(sub_pct / 100)

        st.divider()
        st.subheader("💡 ATS Improvement Checklist")
        suggestions = audit.get("suggestions", [])
        if suggestions:
            for s in suggestions:
                st.markdown(f"- ⚠️ {s}")
        else:
            st.success("✅ Excellent formatting! No critical ATS structural defects detected.")


# =============================================================
# PAGE: JOB MATCH ANALYSIS
# =============================================================
elif active_page == "Job Match":
    st.markdown("## 🎯 Job Description Alignment Analysis")
    st.caption("Measure how closely your qualifications, tools, and technical competencies match the target role.")

    if not st.session_state["analysis_complete"]:
        history_df = get_history()
        if not history_df.empty:
            latest = history_df.iloc[-1]
            st.metric("Latest Recorded Job Match", f"{latest['Job Match Score']}%")
            st.progress(int(latest['Job Match Score']) / 100)
            st.info("Upload and analyze a resume against a target job to see exact matching and missing skills.")
        else:
            st.info("Analyze a resume against a job description to inspect your skill alignment.")
    else:
        res = st.session_state["analysis_data"]
        job_score = res["job_score"]

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Job Match Score", f"{job_score}%")
            st.progress(job_score / 100)
            if job_score >= 80:
                st.success("🟢 Strong candidate alignment with core requirements.")
            elif job_score >= 60:
                st.warning("🟡 Moderate match. Bridging key gaps will boost callback rate.")
            else:
                st.error("🔴 Low alignment with required qualifications.")

        with col2:
            skills_cmp = res.get("skills_comparison", {})
            matching = skills_cmp.get("matching_skills", [])
            missing = skills_cmp.get("missing_skills", [])

            st.markdown("### 🧩 Skills Distribution")
            st.write(f"• **Matching Skills Count:** {len(matching)}")
            st.write(f"• **Missing Target Skills Count:** {len(missing)}")

        st.divider()
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown("### 🟢 Matching Skills Detected")
            st.markdown(res.get("matching_skills", "None identified."))

        with col_m2:
            st.markdown("### 🔴 Missing Skills & Keywords")
            st.markdown(res.get("missing_skills", "None missing."))

        if skills_cmp.get("keyword_suggestions"):
            st.markdown("### 🔑 Recommended Keywords to Integrate")
            kw_html = " ".join([f"<span class='skill-badge'>{k}</span>" for k in skills_cmp["keyword_suggestions"]])
            st.markdown(kw_html, unsafe_allow_html=True)


# =============================================================
# PAGE: AI SUGGESTIONS
# =============================================================
elif active_page == "AI Suggestions":
    st.markdown("## 💡 AI Career Coach Suggestions & Appraisal")
    st.caption("Objective analysis of your profile strengths, gaps, and high-impact optimization strategies.")

    if not st.session_state["analysis_complete"]:
        st.info("Analyze a resume first to view tailored AI suggestions.")
    else:
        res = st.session_state["analysis_data"]

        st.markdown("### 📝 Executive Summary")
        st.info(res.get("summary", "Analysis completed."))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Profile Strengths")
            st.success(res.get("strengths", "No specific strengths listed."))

        with col2:
            st.markdown("### ⚠️ Areas for Improvement")
            st.warning(res.get("weaknesses", "No specific weaknesses listed."))

        st.divider()
        st.markdown("### 🎯 Strategic Recommendations")
        st.markdown(res.get("suggestions", "No suggestions available."))


# =============================================================
# PAGE: RESUME ROADMAP
# =============================================================
elif active_page == "Resume Roadmap":
    st.markdown("## 🗺️ Step-by-Step Resume Improvement Roadmap")
    if not st.session_state["analysis_complete"]:
        st.info("Analyze a resume first to generate your personalized action plan.")
    else:
        res = st.session_state["analysis_data"]
        show_roadmap(res.get("roadmap", ""))


# =============================================================
# PAGE: INTERVIEW QUESTIONS
# =============================================================
elif active_page == "Interview Questions":
    st.markdown("## 💬 Technical Interview Preparation")
    if not st.session_state["analysis_complete"]:
        st.info("Analyze a resume against a target job to generate customized interview questions.")
    else:
        res = st.session_state["analysis_data"]
        show_questions(res.get("questions", ""))


# =============================================================
# PAGE: ANALYSIS HISTORY
# =============================================================
elif active_page == "Analysis History":
    st.markdown("## 🕘 Resume Analysis History")
    st.caption("Complete record of past evaluations, ATS scores, and target job match performance.")

    history_df = get_history()
    detailed_history = get_detailed_history()

    if not history_df.empty:
        stats = get_history_stats()
        h1, h2, h3 = st.columns(3)
        with h1:
            st.metric("Total Resumes Evaluated", stats["total_count"])
        with h2:
            st.metric("Average ATS Score", f"{stats['avg_ats']}%")
        with h3:
            st.metric("Average Job Match Score", f"{stats['avg_job_match']}%")

        st.divider()
        st.subheader("All Evaluation Records")
        st.dataframe(history_df, use_container_width=True, hide_index=True)

        if detailed_history:
            st.markdown("### 🔍 Inspect Previous Evaluation Details")
            options = [f"#{r['id']} - {r['resume']} ({r['date']}) - ATS: {r['ats_score']}%" for r in reversed(detailed_history)]
            selected_option = st.selectbox("Select a past record to review:", options)

            if selected_option:
                rec_id = int(selected_option.split("#")[1].split(" ")[0])
                record = next((r for r in detailed_history if r["id"] == rec_id), None)
                if record:
                    st.markdown(f"**Document:** {record['resume']} &nbsp;|&nbsp; **Date:** {record['date']}")
                    st.markdown(f"**ATS Score:** {record['ats_score']}% &nbsp;|&nbsp; **Job Match:** {record['job_score']}%")

                    with st.expander("📄 View Stored Raw Analysis / Summary", expanded=False):
                        st.markdown(record.get("raw_analysis", "No stored content."))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All Analysis History", type="secondary"):
            clear_history()
            st.success("History cleared successfully.")
            time.sleep(1)
            st.rerun()

    else:
        st.info("ℹ️ No historical evaluations recorded yet. Upload a resume to create your first record.")


# =============================================================
# PAGE: PDF REPORT
# =============================================================
elif active_page == "PDF Report":
    st.markdown("## 📑 Download Executive PDF Report")
    st.caption("Generate a formatted, publication-ready PDF analysis report to save or share.")

    if not st.session_state["analysis_complete"]:
        st.info("Analyze a resume first to generate and download the executive PDF report.")
    else:
        res = st.session_state["analysis_data"]
        resume_name = st.session_state.get("resume_name", "Resume")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(f"**Document Name:** {resume_name}")
            st.write(f"**ATS Compatibility:** {res['ats_score']}%")
            st.write(f"**Job Match Score:** {res['job_score']}%")

        pdf_path = create_pdf(res, resume_filename=resume_name)

        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="📥 Download Resume Analysis Report (PDF)",
                data=pdf_bytes,
                file_name=f"Analysis_Report_{resume_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )


# =============================================================
# PAGE: SETTINGS
# =============================================================
elif active_page == "Settings":
    st.markdown("## ⚙️ Application Settings")
    st.caption("Manage interface themes and local storage.")

    # 1. Appearance / Theme
    st.subheader("🎨 Interface Theme")
    theme_choice = st.radio(
        "Choose Dashboard Theme:",
        options=["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state["theme"] == "dark" else 1,
        horizontal=True
    )
    target_theme = "dark" if "Dark" in theme_choice else "light"
    if target_theme != st.session_state["theme"]:
        st.session_state["theme"] = target_theme
        st.rerun()

    st.divider()

    # 2. Storage & History
    st.subheader("🗂️ Data & Storage Management")
    stats = get_history_stats()
    st.write(f"Currently stored: **{stats['total_count']} resume evaluation records**.")

    if stats["total_count"] > 0:
        if st.button("🗑️ Clear All Evaluation History", key="btn_clear_data"):
            clear_history()
            st.success("All evaluation records cleared.")
            time.sleep(0.5)
            st.rerun()

    st.divider()
    st.caption("AI Resume Analyzer Pro • Built with Streamlit and Groq • Version 2.0")
