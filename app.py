import json
import extra_streamlit_components as stx
import google.generativeai as genai
import streamlit as st
from streamlit_oauth import OAuth2Component

# 1. Page Configuration
st.set_page_config(
    page_title="JARVIS AI - Gemini Style Persistent",
    page_icon="🤖",
    layout="wide",
)


# 2. Cookie Manager Initialization
@st.cache_resource(experimental_allow_widgets=True)
def get_cookie_manager():
  return stx.CookieManager()


cookie_manager = get_cookie_manager()

# 3. Fetch Secrets
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", None)
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", None)
REDIRECT_URI = st.secrets.get("REDIRECT_URI", None)

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
  st.error("⚠️ Streamlit Secrets mein OAuth Keys missing hain!")
  st.stop()

# 4. OAuth Setup
oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/revoke",
)


# 5. Fast Gemini Model Caching
@st.cache_resource
def load_gemini_model(api_key):
  genai.configure(api_key=api_key)
  return genai.GenerativeModel("gemini-2.0-flash")


# 6. Cookie-Based Session Restoration
saved_auth = cookie_manager.get("jarvis_auth_token")
saved_tc = cookie_manager.get("jarvis_tc_accepted")
saved_chat = cookie_manager.get("jarvis_chat_history")

if "auth" not in st.session_state:
  st.session_state.auth = saved_auth if saved_auth else None

if "tc_accepted" not in st.session_state:
  st.session_state.tc_accepted = True if saved_tc == "true" else False

if "messages" not in st.session_state:
  if saved_chat:
    try:
      st.session_state.messages = json.loads(saved_chat)
    except Exception:
      st.session_state.messages = []
  else:
    st.session_state.messages = []


# Helper Function to Save Chat History in Browser Cookies
def save_chat_to_cookie():
  if st.session_state.messages:
    # Save last 15 messages in Browser Cookie
    cookie_manager.set(
        "jarvis_chat_history",
        json.dumps(st.session_state.messages[-15:]),
        key="set_chat",
    )


# STEP 1: Login Interface (Incognito mein bina login yehi screen dikhegi)
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
        scope=(
            "openid email profile"
            " https://www.googleapis.com/auth/gmail.readonly"
        ),
        key="google_auth",
    )

    if result and "token" in result:
      token_val = result["token"].get("access_token", "logged_in")
      st.session_state.auth = token_val
      # Save Auth token in real browser cookie (expires in 7 days)
      cookie_manager.set("jarvis_auth_token", token_val, key="set_auth")
      st.rerun()

# STEP 2: Terms & Conditions (One time setup)
elif st.session_state.auth and not st.session_state.tc_accepted:
  st.title("📜 Terms & Conditions")
  st.warning("⚠️ Access karne ke liye terms accept karein:")
  st.markdown(
      "1. Read-only access for personalization.\n2. Non-sensitive data"
      " handling."
  )
  st.divider()

  if st.button("✅ Accept & Continue", type="primary"):
    st.session_state.tc_accepted = True
    cookie_manager.set("jarvis_tc_accepted", "true", key="set_tc")
    st.rerun()

# STEP 3: Main Persistent Gemini Chat Engine
else:
  with st.sidebar:
    st.title("🤖 JARVIS Config")
    st.success("✅ Logged In")

    default_gemini = st.secrets.get("GEMINI_API_KEY", "")
    gemini_key = st.text_input(
        "Gemini API Key:", value=default_gemini, type="password"
    )

    st.divider()
    st.subheader("📚 App History")
    st.caption(f"Saved Messages: {len(st.session_state.messages)}")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
      st.session_state.messages = []
      cookie_manager.delete("jarvis_chat_history", key="del_chat")
      st.rerun()

    if st.button("🔴 Logout", use_container_width=True):
      st.session_state.auth = None
      st.session_state.tc_accepted = False
      st.session_state.messages = []

      # Delete All Browser Cookies On Logout
      cookie_manager.delete("jarvis_auth_token", key="del_auth")
      cookie_manager.delete("jarvis_tc_accepted", key="del_tc")
      cookie_manager.delete("jarvis_chat_history", key="del_chat_logout")
      st.rerun()

  st.title("⚡ JARVIS AI Engine")

  # Render Existing Saved Chat History
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Floating Gemini Style Input Bar
  if user_query := st.chat_input("Ask JARVIS anything..."):
    if not gemini_key.strip():
      st.error("⚠️ Gemini API Key missing hai! Sidebar mein key add karein.")
    else:
      # Append User Question
      st.session_state.messages.append({"role": "user", "content": user_query})
      with st.chat_message("user"):
        st.markdown(user_query)

      # Generate Streamed Response
      with st.chat_message("assistant"):
        try:
          model = load_gemini_model(gemini_key.strip())

          response_placeholder = st.empty()
          full_response = ""

          response = model.generate_content(
              user_query,
              generation_config=genai.types.GenerationConfig(
                  max_output_tokens=800, temperature=0.5
              ),
              stream=True,
          )

          for chunk in response:
            if chunk.text:
              full_response += chunk.text
              response_placeholder.markdown(full_response + "▌")

          response_placeholder.markdown(full_response)
          st.session_state.messages.append(
              {"role": "assistant", "content": full_response}
          )

          # Save Updated Memory to Browser Cookies
          save_chat_to_cookie()

        except Exception as e:
          st.error(f"Error: {str(e)}")
