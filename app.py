import streamlit as st
from streamlit_oauth import OAuth2Component
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="JARVIS AI - Home", page_icon="🤖", layout="wide")

# 2. Safe Fetch Secrets
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", None)
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", None)
REDIRECT_URI = st.secrets.get("REDIRECT_URI", None)

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    st.error("⚠️ Streamlit Secrets load nahi ho pa rahe hain! Kripya check karein ki Secrets section mein exact keys add hain ya nahi.")
    st.stop()

# 3. OAuth Setup (Directly Passing Parameters)
oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/revoke"
)

if "auth" not in st.session_state:
    st.session_state.auth = None

if "tc_accepted" not in st.session_state:
    st.session_state.tc_accepted = False

# Step 1: Login Interface
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🤖 Welcome to JARVIS AI")
        st.write("Google Account se login karein:")
        st.divider()

        result = oauth2.authorize_button(
            name="Continue with Google 🚀",
            icon="https://www.google.com/favicon.ico",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile https://www.googleapis.com/auth/gmail.readonly",
            key="google_auth"
        )

        if result and "token" in result:
            st.session_state.auth = result["token"]
            st.rerun()

# Step 2: Terms & Conditions
elif st.session_state.auth and not st.session_state.tc_accepted:
    st.title("📜 Terms & Conditions")
    st.warning("⚠️ Access karne ke liye terms accept karein:")
    st.markdown("1. Read-only access for personalization.\n2. Non-sensitive data handling.")
    st.divider()
    
    if st.button("✅ Accept & Continue", type="primary"):
        st.session_state.tc_accepted = True
        st.rerun()

# Step 3: Main Gemini AI Engine
else:
    with st.sidebar:
        st.title("🤖 JARVIS Config")
        st.success("✅ Connected")
        
        default_gemini = st.secrets.get("GEMINI_API_KEY", "")
        gemini_key = st.text_input("Gemini API Key:", value=default_gemini, type="password")

        if st.button("🔴 Logout", use_container_width=True):
            st.session_state.auth = None
            st.session_state.tc_accepted = False
            st.rerun()

    st.title("⚡ JARVIS AI Engine")
    user_query = st.text_area("Question:", placeholder="Type your query here...")

    if st.button("⚡ Generate Response", type="primary"):
        if not user_query.strip():
            st.warning("Please type a question.")
        elif not gemini_key.strip():
            st.error("Gemini API Key missing hai!")
        else:
            try:
                genai.configure(api_key=gemini_key.strip())
                model = genai.GenerativeModel("gemini-2.0-flash")
                
                with st.spinner("⚡ Processing..."):
                    response = model.generate_content(
                        user_query,
                        generation_config=genai.types.GenerationConfig(max_output_tokens=500)
                    )
                
                st.success("⚡ Done!")
                st.markdown("### 🎯 Answer")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
  
