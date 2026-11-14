"""
Resume Improvement Roadmap component with interactive step tracking and progress.
"""
import streamlit as st


def show_roadmap(roadmap_text):
    """
    Render step-by-step resume improvement roadmap with interactive checklist.
    """
    st.markdown("### 🗺️ Prioritized Resume Improvement Roadmap")
    st.caption("Complete these actionable steps in sequence to maximize ATS score and interview callbacks.")

    if not roadmap_text or roadmap_text == "Not Available":
        st.info("Analyze a resume to generate your customized improvement roadmap.")
        return

    # Extract distinct roadmap steps
    raw_steps = [ln.strip() for ln in str(roadmap_text).split("\n") if ln.strip()]
    cleaned_steps = []
    for step in raw_steps:
        s = step.lstrip("0123456789.-•*# ")
        if s:
            cleaned_steps.append(s)

    if not cleaned_steps:
        st.info("No roadmap steps found in analysis.")
        return

    # Initialize roadmap completion state if needed
    if "roadmap_progress" not in st.session_state:
        st.session_state["roadmap_progress"] = {}

    completed_count = 0
    total_steps = len(cleaned_steps)

    for i, step in enumerate(cleaned_steps, 1):
        key = f"roadmap_step_{i}"
        is_checked = st.session_state["roadmap_progress"].get(key, False)
        if is_checked:
            completed_count += 1

    # Overall progress bar
    progress_ratio = completed_count / total_steps if total_steps > 0 else 0
    st.progress(progress_ratio)
    st.markdown(
        f"<div class='roadmap-progress-summary'>"
        f"<b>{completed_count} of {total_steps}</b> action items completed ({int(progress_ratio * 100)}%)"
        f"</div>",
        unsafe_allow_html=True
    )

    # Render each step card
    for i, step in enumerate(cleaned_steps, 1):
        key = f"roadmap_step_{i}"
        is_done = st.session_state["roadmap_progress"].get(key, False)

        step_col1, step_col2 = st.columns([0.08, 0.92])

        with step_col1:
            checked = st.checkbox(
                label=f"Step {i}",
                value=is_done,
                key=key,
                label_visibility="collapsed"
            )
            st.session_state["roadmap_progress"][key] = checked

        with step_col2:
            title_class = "roadmap-title completed" if checked else "roadmap-title"
            badge_bg = "#10b981" if checked else "#3b82f6"
            badge_text = "COMPLETED" if checked else f"PHASE {i}"

            st.markdown(
                f"""
                <div class="roadmap-card" style="border-left: 4px solid {badge_bg};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="background: {badge_bg}; color: #ffffff; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">
                            {badge_text}
                        </span>
                        <span class="roadmap-step-counter">Step {i} of {total_steps}</span>
                    </div>
                    <div class="{title_class}">
                        {step}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
