"""
Sidebar navigation and status indicator component.
"""
import streamlit as st
from config import get_groq_api_key


def show_sidebar():
    with st.sidebar:
        # --------------------------------------------------
        # Logo / Brand
        # --------------------------------------------------
        st.markdown(
            """
            <div class="my-sidebar-brand">
                <div class="my-logo">
                    📄
                </div>
                <div class="my-brand-text">
                    <div class="brand-title">AI Resume</div>
                    <div class="brand-subtitle">Analyzer Pro</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="my-divider"></div>', unsafe_allow_html=True)

        # --------------------------------------------------
        # Current Page State Check
        # --------------------------------------------------
        if "active_page" not in st.session_state:
            st.session_state["active_page"] = "Resume Upload"

        current_page = st.session_state["active_page"]

        # --------------------------------------------------
        # Main Menu
        # --------------------------------------------------
        st.markdown('<div class="my-section-title">MAIN NAVIGATION</div>', unsafe_allow_html=True)

        menu_items = [
            ("▦", "Dashboard"),
            ("📤", "Resume Upload"),
            ("📊", "ATS Score"),
            ("🎯", "Job Match"),
            ("💡", "AI Suggestions"),
            ("🗺️", "Resume Roadmap"),
            ("💬", "Interview Questions"),
            ("🕘", "Analysis History"),
            ("📑", "PDF Report"),
        ]

        for icon, name in menu_items:
            # Highlight active page button
            is_active = (current_page == name)
            label = f"▸ {icon}  {name}" if is_active else f"{icon}   {name}"
            btn_type = "primary" if is_active else "secondary"

            if st.button(
                label,
                key=f"sidebar_btn_{name}",
                use_container_width=True,
                type=btn_type
            ):
                st.session_state["active_page"] = name
                st.rerun()

        # --------------------------------------------------
        # API Status & Bottom Section
        # --------------------------------------------------
        st.markdown('<div class="my-divider bottom-divider"></div>', unsafe_allow_html=True)

        # Check API status
        api_key = get_groq_api_key()
        if api_key and api_key != "gsk_your_groq_api_key_here":
            st.markdown(
                """
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; font-size: 12px; color: #10b981; display: flex; align-items: center; gap: 8px;">
                    <span>●</span> <span>Groq AI Ready</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; font-size: 12px; color: #f59e0b; display: flex; align-items: center; gap: 8px;">
                    <span>⚠️</span> <span>API Key Needed</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button(
            "⚙️   Settings",
            key="sidebar_btn_Settings",
            use_container_width=True,
            type="primary" if current_page == "Settings" else "secondary"
        ):
            st.session_state["active_page"] = "Settings"
            st.rerun()

        if st.button(
            "🔄   Reset Session",
            key="sidebar_btn_Reset",
            use_container_width=True
        ):
            # Keep theme and api key, reset analysis
            theme = st.session_state.get("theme", "dark")
            api_key = st.session_state.get("groq_api_key", "")
            st.session_state.clear()
            st.session_state["theme"] = theme
            if api_key:
                st.session_state["groq_api_key"] = api_key
            st.session_state["active_page"] = "Resume Upload"
            st.rerun()
