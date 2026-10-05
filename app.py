import streamlit as st
from streamlit_oauth import OAuth2Component

# Page Config
st.set_page_config(page_title="JARVIS AI - Google Auth", page_icon="🤖", layout="centered")

# Secrets se Credentials fetch kar rahe hain
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "http://localhost:8501/")

# Google OAuth Endpoints
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

# Initialize OAuth Component
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint=AUTHORIZE_URL,
    access_token_endpoint=TOKEN_URL,
    refresh_token_endpoint=TOKEN_URL,
    revoke_token_endpoint=REVOKE_URL
)

# Session state initialization for login
if "auth" not in st.session_state:
    st.session_state.auth = None

# --- UI LOGIC ---

if not st.session_state.auth:
    st.title("🤖 Welcome to JARVIS AI")
    st.write("Apne Real Google Account se login karein:")
    st.divider()

    # Real Google Sign-In Button
    result = oauth2.authorize_button(
        name="Continue with Google 🚀",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        key="google_auth"
    )

    if result and "token" in result:
        st.session_state.auth = result["token"]
        st.rerun()

else:
    st.title("🚀 JARVIS AI Dashboard")
    st.success("✅ Real Google Account Successfully Verified!")
    
    st.write("Aap successfully login ho chuke hain. Yahan apna baki app content aur features build kar sakte hain.")
    st.divider()

    # Logout Button
    if st.button("🔴 Logout", use_container_width=True):
        st.session_state.auth = None
        st.rerun()
