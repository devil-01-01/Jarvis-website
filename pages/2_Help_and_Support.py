import streamlit as st

st.set_page_config(page_title="Help & Support - JARVIS AI", page_icon="❓", layout="centered")

st.title("❓ Help & Support")
st.caption("Need assistance with JARVIS AI?")
st.divider()

st.markdown("""
### 🚀 Frequently Asked Questions (FAQ)

**1. How do I setup my Gemini API Key?**
- Go to [Google AI Studio](https://aistudio.google.com/) and generate a free API key.
- Enter the key in the sidebar of the main page or save it in Streamlit Secrets as `GEMINI_API_KEY`.

**2. Is my login data secure?**
- Yes, we use standard Google OAuth2 authentication. Your credentials are processed directly by Google.

**3. What should I do if the app gets stuck?**
- Click on the **Logout** button in the sidebar or refresh your browser tab.

---

### 📩 Contact Developer
If you encounter any issues or need custom features:
- **Email Support:** `jarvisapp.support@gmail.com`
""")
