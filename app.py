import streamlit as st
from streamlit_oauth import OAuth2Component
import google.generativeai as genai
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="JARVIS AI - Multi-Agent Engine", page_icon="🤖", layout="wide")

# 2. Fetch Secrets
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "")

# API Keys from secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Secrets Check
if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    st.error("⚠️ Streamlit Secrets mein GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ya REDIRECT_URI missing hai!")
    st.stop()

# 3. OAuth Setup
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    TOKEN_URL,
    REVOKE_URL
)

if "auth" not in st.session_state:
    st.session_state.auth = None

# --- AUTHENTICATION FLOW ---

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🤖 Welcome to JARVIS AI")
        st.write("Access karne ke liye apne Google Account se login karein:")
        st.divider()

        result = oauth2.authorize_button(
            name="Continue with Google 🚀",
            icon="https://www.google.com/favicon.ico",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google_auth",
            extras_params={"client_id": CLIENT_ID}
        )

        if result and "token" in result:
            st.session_state.auth = result["token"]
            st.rerun()

else:
    # --- MAIN MULTI-AGENT INTERFACE ---
    
    with st.sidebar:
        st.title("🤖 JARVIS AI")
        st.success("✅ Logged In")
        st.info("🧠 Ensemble Engine Active: 3 AI Models working together.")
        st.divider()
        if st.button("🔴 Logout", use_container_width=True):
            st.session_state.auth = None
            st.rerun()

    st.title("🚀 JARVIS Multi-Agent Engine")
    st.write("Sawaal puchiye, teeno AI models milkar sabse accurate aur best response generate karenge.")

    user_query = st.text_area("Apna sawaal yahan likhein:", placeholder="Ask anything to JARVIS...")

    if st.button("✨ Generate Best Answer", type="primary"):
        if not user_query.strip():
            st.warning("Kripya koi sawaal likhein.")
        else:
            with st.spinner("⚡ Teeno AI Models apas mein consult kar rahe hain... Please wait!"):
                
                # Mock Responses / Replace with actual API Calls:
                # Model 1 (Gemini) Response
                ans_model1 = f"Gemini Analysis: Key facts and deep structure regarding '{user_query}'."
                
                # Model 2 (Groq/Llama) Response
                ans_model2 = f"Llama/Groq Insight: Speed, concise execution, and direct reasoning on '{user_query}'."
                
                # Model 3 (Custom Logic) Response
                ans_model3 = f"Custom Agent Perspective: Logical validation and safety checks on '{user_query}'."

                # Master Synthesis (Combine 3 Models into 1 Best Answer)
                final_combined_prompt = f"""
                You are the Master JARVIS Synthesizer. Review the answers from 3 AI models and merge them into one perfect, highly accurate, and clear Hindi-English response.

                Model 1 Output: {ans_model1}
                Model 2 Output: {ans_model2}
                Model 3 Output: {ans_model3}

                Generate the single best response:
                """
                
                # Final Best Output Simulation
                final_answer = f"🎯 **Final Unified Response (Best of 3 Models):**\n\nIs query ({user_query}) ke liye teeno models ne verify kiya hai. Teeno AI models ka combined final answer yahan show hoga."

            # Tabbed Layout: Main Answer + Behind the Scenes
            st.success("✅ Output Ready!")
            
            st.markdown(final_answer)
            
            st.divider()
            with st.expander("🔍 See Individual AI Model Responses (Behind the Scenes)"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.subheader("Model 1 (Gemini)")
                    st.write(ans_model1)
                with col_b:
                    st.subheader("Model 2 (Groq/Llama)")
                    st.write(ans_model2)
                with col_c:
                    st.subheader("Model 3 (Custom)")
                    st.write(ans_model3)
