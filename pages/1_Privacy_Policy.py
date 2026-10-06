import streamlit as st

st.set_page_config(page_title="Privacy Policy - JARVIS AI", page_icon="🔒", layout="centered")

st.title("🔒 Privacy Policy")
st.caption("Last updated: October 2026")
st.divider()

st.markdown("""
### 1. Information Collection
JARVIS AI collects minimal data:
- **Google Account:** Email ID and basic profile info for authentication.
- **Gmail Access (Read-Only):** Used strictly for user context if authorized.

### 2. How Data is Used
- To authenticate user login sessions.
- To process prompt requests via Gemini API.
- **No Data Selling:** Personal data or emails are never saved to a database or shared with third parties.

### 3. Security
- API keys and tokens are stored temporarily in session memory (`st.session_state`) and reset on logout.

### 4. Developer Contact
For any concerns, contact us at: **`jarvis.developer.001@gmail.com`**
""")
