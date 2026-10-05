import streamlit as st
from streamlit_oauth import OAuth2Component
import google.generativeai as genai
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="JARVIS Multi-Agent Engine", page_icon="🤖", layout="wide")

# 2. Fetch OAuth Secrets
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "")

# Validation check for OAuth secrets
if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    st.error("⚠️️ Streamlit Secrets me GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ya REDIRECT_URI missing hai!")
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

# Initialize Session State
if "auth" not in st.session_state:
    st.session_state.auth = None

if "tc_accepted" not in st.session_state:
    st.session_state.tc_accepted = False

# --- STEP 1: GOOGLE OAUTH LOGIN ---

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🤖 Welcome to JARVIS AI")
        st.write("Access karne ke liye apne Google Account se login karein:")
        st.divider()

        # Scopes include Gmail Readonly Access
        result = oauth2.authorize_button(
            name="Continue with Google 🚀",
            icon="https://www.google.com/favicon.ico",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile https://www.googleapis.com/auth/gmail.readonly",
            key="google_auth",
            extras_params={"client_id": CLIENT_ID}
        )

        if result and "token" in result:
            st.session_state.auth = result["token"]
            st.rerun()

# --- STEP 2: TERMS AND CONDITIONS ACCEPTANCE PAGE ---

elif st.session_state.auth and not st.session_state.tc_accepted:
    st.title("📜 Terms & Conditions and Privacy Policy")
    st.warning("⚠️ JARVIS AI app access karne ke liye aapko nimnlikhit sharaton ko accept karna hoga:")
    
    st.markdown("""
    ### JARVIS AI Data Usage Terms:
    1. **Gmail Data Usage:** JARVIS AI aapke Gmail metadata aur read-only permission ka upyog karke aapke prompts aur assistance ko personalize karega.
    2. **Multi-Agent Processing:** Aapke inputs Gemini series (2.5 Flash, 2.5 Pro, 3.5 Flash) aur Groq (Llama 3.3 70B) models ke dwaara securely synthesize kiye jayenge.
    3. **Privacy Assurance:** Aapka private data kisi bhi third-party ad network ke saath share nahi kiya jayega.
    """)

    st.divider()
    
    col_agree, col_deny = st.columns([1, 1])
    
    with col_agree:
        if st.button("✅ I Agree & Accept Terms", type="primary", use_container_width=True):
            st.session_state.tc_accepted = True
            st.rerun()
            
    with col_deny:
        if st.button("❌ Decline & Logout", use_container_width=True):
            st.session_state.auth = None
            st.session_state.tc_accepted = False
            st.rerun()

# --- STEP 3: MAIN JARVIS MULTI-AGENT DASHBOARD ---

else:
    with st.sidebar:
        st.title("🤖 JARVIS Engine")
        st.success("✅ Logged In & Verified")
        
        st.divider()
        st.subheader("🔑 API Keys Input")
        
        # User input boxes for API keys (Auto-loaded from secrets if present)
        default_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
        default_groq_key = st.secrets.get("GROQ_API_KEY", "")

        gemini_api_key = st.text_input(
            "Gemini API Key:",
            value=default_gemini_key,
            type="password",
            placeholder="AIzaSy...",
            help="Enter your Google Gemini API Key"
        )

        groq_api_key = st.text_input(
            "Groq API Key:",
            value=default_groq_key,
            type="password",
            placeholder="gsk_...",
            help="Enter your Groq API Key"
        )

        st.divider()
        st.info("🧠 Active Models:\n- Gemini 2.5 Flash\n- Gemini 2.5 Pro\n- Gemini 3.5 Flash\n- Gemini 1.5 Pro\n- Groq (Llama 3.3 70B)")
        st.divider()
        
        if st.button("🔴 Logout", use_container_width=True):
            st.session_state.auth = None
            st.session_state.tc_accepted = False
            st.rerun()

    st.title("🚀 JARVIS Multi-Agent Synthesis Engine")
    st.write("Apna sawaal likhein. Sabhi AI models milkar aapke inputs par best answer denge.")

    user_query = st.text_area("Apna sawaal yahan poochhein:", placeholder="Ask anything to JARVIS AI...")

    if st.button("✨ Generate Unified Response", type="primary"):
        if not user_query.strip():
            st.warning("Kripya pehle koi sawaal likhein.")
        elif not gemini_api_key.strip():
            st.error("⚠️ Please enter a valid Gemini API Key in the sidebar!")
        elif not groq_api_key.strip():
            st.error("⚠️ Please enter a valid Groq API Key in the sidebar!")
        else:
            # Configure Keys with Clean String
            genai.configure(api_key=gemini_api_key.strip())
            groq_client = Groq(api_key=groq_api_key.strip())

            with st.spinner("⚡ Sabhi Gemini Models aur Groq Llama parallel process ho rahe hain..."):
                responses = {}

                # 1. Gemini 2.5 Flash
                try:
                    m1 = genai.GenerativeModel('gemini-2.5-flash')
                    responses["Gemini 2.5 Flash"] = m1.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 2.5 Flash"] = f"Error: {str(e)}"

                # 2. Gemini 2.5 Pro
                try:
                    m2 = genai.GenerativeModel('gemini-2.5-pro')
                    responses["Gemini 2.5 Pro"] = m2.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 2.5 Pro"] = f"Error: {str(e)}"

                # 3. Gemini 3.5 Flash
                try:
                    m3 = genai.GenerativeModel('gemini-3.5-flash')
                    responses["Gemini 3.5 Flash"] = m3.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 3.5 Flash"] = f"Error: {str(e)}"

                # 4. Gemini 1.5 Pro
                try:
                    m4 = genai.GenerativeModel('gemini-1.5-pro')
                    responses["Gemini 1.5 Pro"] = m4.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 1.5 Pro"] = f"Error: {str(e)}"

                # 5. Groq Model
                try:
                    groq_resp = groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": user_query}],
                        model="llama-3.3-70b-versatile",)
                        model="openai/gpt-oss-20b"
                    responses["Groq"] = groq_resp.choices[0].message.content
                except Exception as e:
                    responses["Groq"] = f"Error: {str(e)}"

                # Master Synthesis (Judge Model)
                try:
                    synthesis_prompt = f"""
                    You are JARVIS Master AI Synthesizer. Analyze the responses from 5 different AI models (Gemini 2.5 Flash, 2.5 Pro, 3.5 Flash, 1.5 Pro, and Groq Llama 3.3) for the query: '{user_query}'.
                    Combine their insights into ONE single best, highly detailed, accurate, and easy-to-understand response in Hinglish/Hindi-English.

                    Individual Models Output:
                    1. Gemini 2.5 Flash: {responses.get('Gemini 2.5 Flash', '')}
                    2. Gemini 2.5 Pro: {responses.get('Gemini 2.5 Pro', '')}
                    3. Gemini 3.5 Flash: {responses.get('Gemini 3.5 Flash', '')}
                    4. Gemini 1.5 Pro: {responses.get('Gemini 1.5 Pro', '')}
                    5. Groq Llama 3.3: {responses.get('Groq (Llama 3.3)', '')}
                    """
                    
                    master_model = genai.GenerativeModel('gemini-2.5-pro')
                    final_synthesized_answer = master_model.generate_content(synthesis_prompt).text
                except Exception as e:
                    final_synthesized_answer = f"Synthesis Error: {str(e)}"

            # Display Output
            st.success("✅ Multi-Agent Response Ready!")
            st.markdown("### 🎯 Final Unified Response (Best of All Models)")
            st.write(final_synthesized_answer)

            st.divider()

            with st.expander("🔍 Behind the Scenes: View Individual Model Responses"):
                cols = st.columns(3)
                cols[0].subheader("Gemini 2.5 Flash")
                cols[0].write(responses.get("Gemini 2.5 Flash", ""))

                cols[1].subheader("Gemini 2.5 Pro")
                cols[1].write(responses.get("Gemini 2.5 Pro", ""))

                cols[2].subheader("Gemini 3.5 Flash")
                cols[2].write(responses.get("Gemini 3.5 Flash", ""))

                cols2 = st.columns(2)
                cols2[0].subheader("Gemini 1.5 Pro")
                cols2[0].write(responses.get("Gemini 1.5 Pro", ""))

                cols2[1].subheader("Groq (Llama 3.3)")
                cols2[1].write(responses.get("Groq (Llama 3.3)", ""))
