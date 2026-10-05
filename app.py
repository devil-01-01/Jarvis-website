import streamlit as st
from streamlit_oauth import OAuth2Component
import google.generativeai as genai
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="JARVIS Multi-Agent Engine", page_icon="🤖", layout="wide")

# 2. Fetch Secrets
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Secrets Check
if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    st.error("⚠️ Streamlit Secrets mein GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ya REDIRECT_URI missing hai!")
    st.stop()

# Configure API Keys
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

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

# Session States Initialization
if "auth" not in st.session_state:
    st.session_state.auth = None

if "tc_accepted" not in st.session_state:
    st.session_state.tc_accepted = False

# --- FLOW 1: GOOGLE OAUTH LOGIN ---

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

# --- FLOW 2: TERMS AND CONDITIONS ACCEPTANCE PAGE ---

elif st.session_state.auth and not st.session_state.tc_accepted:
    st.title("📜 Terms & Conditions and Privacy Policy")
    st.warning("⚠️ JARVIS AI app access karne ke liye aapko nimnlikhit sharaton ko accept karna hoga:")
    
    st.markdown("""
    ### JARVIS AI Data Usage Terms:
    1. **Gmail Data Usage:** JARVIS AI aapke Gmail metadata aur read-only permission ka upyog karke aapke prompts aur assistance ko personalize karega.
    2. **Multi-Agent Processing:** Aapke inputs Gemini 1.0, 1.5, 2.0 aur Groq (Llama 3) models ke dwaara securely synthesize kiye jayenge.
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

# --- FLOW 3: MAIN JARVIS MULTI-AGENT DASHBOARD ---

else:
    with st.sidebar:
        st.title("🤖 JARVIS Engine")
        st.success("✅ Logged In & Verified")
        st.info("🧠 Active Models:\n- Gemini 1.0 Pro\n- Gemini 1.5 Flash\n- Gemini 1.5 Pro\n- Gemini 2.0 Flash\n- Groq (Llama 3 70B)")
        st.divider()
        if st.button("🔴 Logout", use_container_width=True):
            st.session_state.auth = None
            st.session_state.tc_accepted = False
            st.rerun()

    st.title("🚀 JARVIS Multi-Agent Synthesis Engine")
    st.write("Apna sawaal likhein. Sabhi AI models milkar aapke Gmail context aur inputs par best answer denge.")

    user_query = st.text_area("Apna sawaal yahan poochhein:", placeholder="Ask anything to JARVIS AI...")

    if st.button("✨ Generate Unified Response", type="primary"):
        if not user_query.strip():
            st.warning("Kripya pehle koi sawaal likhein.")
        elif not GEMINI_API_KEY or not GROQ_API_KEY:
            st.error("⚠️️ Secrets mein GEMINI_API_KEY ya GROQ_API_KEY missing hai!")
        else:
            with st.spinner("⚡ Sabhi Gemini Models aur Groq Llama parallel process ho rahe hain..."):
                responses = {}

                # 1. Gemini 1.0 Pro
                try:
                    m1 = genai.GenerativeModel('gemini-1.0-pro')
                    responses["Gemini 1.0 Pro"] = m1.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 1.0 Pro"] = f"Error: {str(e)}"

                # 2. Gemini 1.5 Flash
                try:
                    m2 = genai.GenerativeModel('gemini-1.5-flash')
                    responses["Gemini 1.5 Flash"] = m2.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 1.5 Flash"] = f"Error: {str(e)}"

                # 3. Gemini 1.5 Pro
                try:
                    m3 = genai.GenerativeModel('gemini-1.5-pro')
                    responses["Gemini 1.5 Pro"] = m3.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 1.5 Pro"] = f"Error: {str(e)}"

                # 4. Gemini 2.0 Flash
                try:
                    m4 = genai.GenerativeModel('gemini-2.0-flash-exp')
                    responses["Gemini 2.0 Flash"] = m4.generate_content(user_query).text
                except Exception as e:
                    responses["Gemini 2.0 Flash"] = f"Error: {str(e)}"

                # 5. Groq Model (Llama 3 70B)
                try:
                    groq_resp = groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": user_query}],
                        model="llama3-70b-8192",
                    )
                    responses["Groq (Llama 3)"] = groq_resp.choices[0].message.content
                except Exception as e:
                    responses["Groq (Llama 3)"] = f"Error: {str(e)}"

                # Master Synthesis (Judge Model)
                try:
                    synthesis_prompt = f"""
                    You are JARVIS Master AI Synthesizer. Analyze the responses from 5 different AI models (Gemini 1.0, 1.5 Flash, 1.5 Pro, 2.0 Flash, and Groq Llama 3) for the query: '{user_query}'.
                    Combine their insights into ONE single best, highly detailed, accurate, and easy-to-understand response in Hinglish/Hindi-English.

                    Individual Models Output:
                    1. Gemini 1.0 Pro: {responses['Gemini 1.0 Pro']}
                    2. Gemini 1.5 Flash: {responses['Gemini 1.5 Flash']}
                    3. Gemini 1.5 Pro: {responses['Gemini 1.5 Pro']}
                    4. Gemini 2.0 Flash: {responses['Gemini 2.0 Flash']}
                    5. Groq Llama 3: {responses['Groq (Llama 3)']}
                    """
                    
                    master_model = genai.GenerativeModel('gemini-1.5-pro')
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
                cols[0].subheader("Gemini 1.0 Pro")
                cols[0].write(responses.get("Gemini 1.0 Pro", ""))

                cols[1].subheader("Gemini 1.5 Flash")
                cols[1].write(responses.get("Gemini 1.5 Flash", ""))

                cols[2].subheader("Gemini 1.5 Pro")
                cols[2].write(responses.get("Gemini 1.5 Pro", ""))

                cols2 = st.columns(2)
                cols2[0].subheader("Gemini 2.0 Flash")
                cols2[0].write(responses.get("Gemini 2.0 Flash", ""))

                cols2[1].subheader("Groq (Llama 3)")
                cols2[1].write(responses.get("Groq (Llama 3)", ""))
