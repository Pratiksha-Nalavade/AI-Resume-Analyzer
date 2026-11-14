"""
File details component displaying document metadata and extracted text statistics.
"""
import streamlit as st


def show_file_details(uploaded_file, extracted_text=None):
    """
    Render professional metadata card for the uploaded resume file.
    """
    file_size_kb = round(uploaded_file.size / 1024, 2)
    file_ext = uploaded_file.name.split(".")[-1].upper()

    word_count = len(extracted_text.split()) if extracted_text else 0
    char_count = len(extracted_text) if extracted_text else 0
    reading_time_mins = max(1, round(word_count / 200, 1)) if word_count > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="file-detail-card">
                <div class="file-detail-label">DOCUMENT NAME</div>
                <div class="file-detail-val" title="{uploaded_file.name}">
                    {uploaded_file.name}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="file-detail-card">
                <div class="file-detail-label">FORMAT & SIZE</div>
                <div class="file-detail-val val-blue">
                    {file_ext} • {file_size_kb} KB
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="file-detail-card">
                <div class="file-detail-label">WORD COUNT</div>
                <div class="file-detail-val val-green">
                    {word_count} words ({char_count} chars)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="file-detail-card">
                <div class="file-detail-label">READING TIME</div>
                <div class="file-detail-val val-amber">
                    ~{reading_time_mins} min read
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
