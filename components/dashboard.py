"""
Dashboard component displaying metrics, historical trends, and recent analysis activity.
"""
import streamlit as st
import pandas as pd
from utils.history import get_history, get_history_stats


def show_dashboard(ats_score=None, job_score=None, resume_name=None):
    """
    Render executive dashboard with real historical metrics, charts, and activity log.
    """
    st.markdown("## 📊 Executive Resume Performance Dashboard")
    st.caption("Real-time telemetry and analytical breakdown of your resume evaluations")

    stats = get_history_stats()
    history_df = get_history()

    # Determine latest scores: use arguments or read from latest history
    if ats_score is None or job_score is None:
        if not history_df.empty:
            latest = history_df.iloc[-1]
            ats_score = int(latest["ATS Score"])
            job_score = int(latest["Job Match Score"])
            resume_name = str(latest["Resume"])
        else:
            ats_score = 0
            job_score = 0
            resume_name = "No resume analyzed yet"

    # -------------------------------------------------------------
    # 1. Top KPI Metrics Row
    # -------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        ats_delta = None
        if stats["total_count"] > 1:
            diff = ats_score - stats["avg_ats"]
            ats_delta = f"{'+' if diff >= 0 else ''}{diff}% vs avg"
        st.metric(
            label="📄 Latest ATS Score",
            value=f"{ats_score}%" if stats["total_count"] > 0 else "N/A",
            delta=ats_delta
        )

    with kpi2:
        job_delta = None
        if stats["total_count"] > 1:
            diff = job_score - stats["avg_job_match"]
            job_delta = f"{'+' if diff >= 0 else ''}{diff}% vs avg"
        st.metric(
            label="🎯 Latest Job Match",
            value=f"{job_score}%" if stats["total_count"] > 0 else "N/A",
            delta=job_delta
        )

    with kpi3:
        st.metric(
            label="📈 Total Evaluations",
            value=stats["total_count"]
        )

    with kpi4:
        st.metric(
            label="🏆 Highest ATS Score",
            value=f"{stats['highest_ats']}%" if stats["total_count"] > 0 else "N/A"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. Visual Performance Indicators
    # -------------------------------------------------------------
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-card-title">📄 ATS Compatibility Rating</div>
                <div class="score-card-value">{ats_score}%</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {max(0, min(100, ats_score))}%;"></div>
                </div>
                <div class="score-card-subtext">
                    Target: 80%+ for Tier-1 applicant tracking systems.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-card-title">🎯 Target Job Alignment</div>
                <div class="score-card-value">{job_score}%</div>
                <div class="progress-container">
                    <div class="progress-bar progress-bar-match" style="width: {max(0, min(100, job_score))}%;"></div>
                </div>
                <div class="score-card-subtext">
                    Relevance ratio matching skills and responsibilities.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Readiness assessment banner
    if stats["total_count"] > 0:
        if ats_score >= 80 and job_score >= 75:
            st.success("✅ **High Application Readiness:** Your resume is well-optimized for ATS and closely aligned with the target job requirements.")
        elif ats_score >= 65 and job_score >= 60:
            st.warning("⚠️ **Moderate Alignment:** Good foundation, but optimizing missing skills and section headers will significantly improve interview callback rates.")
        else:
            st.error("❗ **Optimization Required:** Low keyword match or ATS compatibility detected. Review the suggestions and roadmap before submitting.")

    st.divider()

    # -------------------------------------------------------------
    # 3. Score History Trend Chart
    # -------------------------------------------------------------
    if not history_df.empty:
        st.subheader("📈 Performance Trajectory")
        chart_data = history_df[["Resume", "ATS Score", "Job Match Score"]].copy()
        # Add index label
        chart_data["Evaluation #"] = [f"#{i+1} - {r[:15]}" for i, r in enumerate(chart_data["Resume"])]
        chart_df = chart_data.set_index("Evaluation #")[["ATS Score", "Job Match Score"]]
        st.line_chart(chart_df, color=["#3b82f6", "#10b981"], height=280)

        # -------------------------------------------------------------
        # 4. Recent Analysis Log Table
        # -------------------------------------------------------------
        st.subheader("🕘 Recent Evaluation History")
        recent_records = history_df.tail(10).iloc[::-1]

        # Display clean dataframe
        display_df = recent_records.copy()
        display_df["ATS Status"] = display_df["ATS Score"].apply(
            lambda s: "🟢 Excellent" if s >= 80 else ("🟡 Good" if s >= 65 else "🔴 Needs Work")
        )
        display_df["Match Status"] = display_df["Job Match Score"].apply(
            lambda s: "🟢 High" if s >= 80 else ("🟡 Medium" if s >= 60 else "🔴 Low")
        )

        st.dataframe(
            display_df[["Date", "Resume", "ATS Score", "ATS Status", "Job Match Score", "Match Status"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("ℹ️ No historical resume evaluations recorded yet. Upload and analyze your first resume to populate this dashboard.")
