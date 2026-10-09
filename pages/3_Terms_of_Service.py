import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Terms of Service - JARVIS",
    page_icon="📋",
    layout="centered",
)

# Custom Styling to match Gemini/Google minimalist clean look
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    h1 {
        font-family: 'Google Sans', sans-serif;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    h3 {
        font-family: 'Google Sans', sans-serif;
        color: #3c4043;
        margin-top: 1.5rem;
    }
    p, li {
        font-family: 'Roboto', sans-serif;
        color: #444746;
        line-height: 1.6;
    }
    .updated-date {
        color: #5f6368;
        font-size: 0.85rem;
        margin-bottom: 2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.title("📋 Terms of Service")
st.markdown(
    '<p class="updated-date">Last updated: October 2026</p>',
    unsafe_allow_html=True,
)

st.markdown(
    "Welcome to **JARVIS**. By accessing or using our web application, you agree to comply with and be bound by the following terms. Please read them carefully."
)

st.divider()

# Section 1
st.subheader("1. Acceptance of Terms")
st.markdown(
    "By visiting or interacting with JARVIS (`https://jarvis-website.streamlit.app`), you accept these Terms of Service in full. If you disagree with any part of these terms, you must discontinue use of the application immediately."
)

# Section 2
st.subheader("2. Use of the Application")
st.markdown("""
* **Public Accessibility:** JARVIS is an open, login-free AI assistant platform designed to provide text generation, multi-model chatting, and visual processing.
* **Prohibited Conduct:** Users must not use the platform for illegal activities, generating harmful or abusive content, attempting unauthorized access, or disrupting system operations.
""")

# Section 3
st.subheader("3. Intellectual Property")
st.markdown(
    "All user interface designs, custom branding elements, application logic, and specific configurations associated with JARVIS are protected. You may not copy, duplicate, or redistribute the core source code without explicit permission from the developer."
)

# Section 4
st.subheader("4. Disclaimer of Warranties")
st.markdown(
    "The application is provided on an 'as-is' and 'as-available' basis. While we leverage advanced AI engines (Gemini and Groq) to deliver accurate responses, we do not guarantee 100% reliability, continuous uptime, or error-free outputs."
)

# Section 5
st.subheader("5. Contact Information")
st.markdown(
    "If you have any questions or concerns regarding these Terms of Service, you can reach out directly at:"
)
st.markdown("📧 **Email:** `jarvisapp.support@gmail.com`")
