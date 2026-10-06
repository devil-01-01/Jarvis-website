import streamlit as st
from streamlit_oauth import OAuth2Component
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="JARVIS AI - Home", page_icon="🤖", layout="wide")

# Fetch Secrets
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", None)
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", None)
REDIRECT_URI = st.secrets.get("REDIRECT_URI", None)

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    st.error("⚠️ Streamlit Secrets mein OAuth Keys missing hain!")
    st.stop()

# Initialize OAuth Component
oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/revoke"
)

# Persistent Session Management
if "auth" not in st.session_state:
    st.session_state.auth = None

if "tc_accepted" not in st.session_state:
    st.session_state.tc_accepted = False

# Step 1: Login Check
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

# Step 3: High-Speed Fast Generation Engine
else:
    with st.sidebar:
        st.title("🤖 JARVIS Config")
        st.success("✅ Logged In")
        
        default_gemini = st.secrets.get("GEMINI_API_KEY", "")
        gemini_key = st.text_input("Gemini API Key:", value=default_gemini, type="password")

        if st.button("🔴 Logout", use_container_width=True):
            st.session_state.auth = None
            st.session_state.tc_accepted = False
            st.rerun()

    st.title("⚡ JARVIS AI Engine (Fast Mode)")
    user_query = st.text_area("Question:", placeholder="Type your query here...")

    if st.button("⚡ Fast Generate", type="primary"):
        if not user_query.strip():
            st.warning("Please type a question.")
        elif not gemini_key.strip():
            st.error("Gemini API Key missing hai!")
        else:
            try:
                genai.configure(api_key=gemini_key.strip())
                model = genai.GenerativeModel("gemini-3.8-flash")
                
                # Streaming response for immediate visible output
                st.markdown("### 🎯 Answer")
                response_placeholder = st.empty()
                full_response = ""

                response = model.generate_content(
                    user_query,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=500,
                        temperature=0.7
                    ),
                    stream=True
                )
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
  
