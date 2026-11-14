"""
Interview Preparation component with structured technical questions, suggested answer approaches, and interview strategies.
"""
import re
import streamlit as st


def show_questions(questions_text):
    """
    Render structured technical interview questions with answer guidelines.
    """
    st.markdown("### 💬 Technical & Project Interview Preparation")
    st.caption("AI-curated technical and architectural questions based directly on your resume projects and target job requirements.")

    if not questions_text or questions_text == "Not Available":
        st.info("Analyze a resume against a job description to generate targeted interview questions.")
        return

    # Interview Strategy Tip Box
    st.markdown(
        """
        <div class="interview-tip-box">
            <div class="interview-tip-title">
                💡 Interviewer's Pro Tip: The STAR Framework
            </div>
            <div class="interview-tip-text">
                When answering project questions, structure your reply using <b>Situation</b> (the context), <b>Task</b> (the challenge), <b>Action</b> (your specific engineering decisions and technologies used), and <b>Result</b> (quantifiable outcome, metrics, or performance improvements).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Parse questions block
    raw_blocks = re.split(r"\n(?=\d+[\.\)])", questions_text.strip())

    for idx, block in enumerate(raw_blocks, 1):
        clean_block = block.strip()
        if not clean_block:
            continue

        # Extract Question and Focus if available
        q_match = re.search(r"(?:Q:|\d+[\.\)])\s*(.*?)(?=\n\s*(?:Focus:|Approach:|$))", clean_block, re.DOTALL | re.IGNORECASE)
        focus_match = re.search(r"(?:Focus|Approach|Tip|Answer Key):\s*(.*)", clean_block, re.DOTALL | re.IGNORECASE)

        if q_match:
            question_content = q_match.group(1).strip()
            # Clean leading numbers
            question_content = re.sub(r"^\d+[\.\)]\s*", "", question_content)
        else:
            first_line = clean_block.split("\n")[0]
            question_content = re.sub(r"^\d+[\.\)]\s*", "", first_line)

        focus_content = focus_match.group(1).strip() if focus_match else None

        with st.expander(f"📌 Question {idx}: {question_content[:95]}...", expanded=(idx <= 2)):
            st.markdown(f"**Full Question:**")
            st.markdown(f"> *{question_content}*")

            if focus_content:
                st.markdown(
                    f"""
                    <div class="interview-focus-box">
                        <span class="interview-focus-title">Expected Answer Focus & Strategy:</span>
                        <div class="interview-focus-text">
                            {focus_content}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                remaining_lines = clean_block.split("\n")[1:]
                if remaining_lines:
                    st.markdown("\n".join(remaining_lines))
                else:
                    st.markdown("*Practice explaining your design decisions, trade-offs, and technologies applied in this project area.*")
