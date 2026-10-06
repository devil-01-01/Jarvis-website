import json
import google.generativeai as genai
import streamlit as st
from streamlit_oauth import OAuth2Component

# 1. Page Configuration
st.set_page_config(
    page_title="JARVIS AI - Persistent Engine", page_icon="🤖", layout="wide"
)

# 2. Fetch Secrets
CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", None)
CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", None)
REDIRECT_URI = st.secrets.get("REDIRECT_URI", None)

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
  st.error("⚠️ Streamlit Secrets mein OAuth Keys missing hain!")
  st.stop()

# 3. OAuth Component Initialization
oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/revoke",
)

# 4. Read Query Parameters for Persistent States Across Refresh
query_params = st.query_params

# Session State Initialization
if "auth" not in st.session_state:
  st.session_state.auth = query_params.get("auth_token", None)

if "tc_accepted" not in st.session_state:
  st.session_state.tc_accepted = query_params.get("tc_accepted", "false") == "true"

if "messages" not in st.session_state:
  saved_history = query_params.get("chat_history", None)
  if saved_history:
    try:
      st.session_state.messages = json.loads(saved_history)
    except Exception:
      st.session_state.messages = []
  else:
    st.session_state.messages = []


# Helper Function to Save State in Browser Query Params
def update_browser_state():
  if st.session_state.auth:
    st.query_params["auth_token"] = str(st.session_state.auth)
  if st.session_state.tc_accepted:
    st.query_params["tc_accepted"] = "true"
  if st.session_state.messages:
    # Save last 10 messages to prevent URL length limits
    st.query_params["chat_history"] = json.dumps(st.session_state.messages[-10:])


# STEP 1: Login Interface
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
      token = result["token"]
      st.session_state.auth = token.get("access_token", "logged_in")
      update_browser_state()
      st.rerun()

# STEP 2: Terms & Conditions (First Login Only)
elif st.session_state.auth and not st.session_state.tc_accepted:
  st.title("📜 Terms & Conditions")
  st.warning("⚠️️ Access karne ke liye terms accept karein:")
  st.markdown(
      "1. Read-only access for personalization.\n2. Non-sensitive data"
      " handling."
  )
  st.divider()

  if st.button("✅ Accept & Continue", type="primary"):
    st.session_state.tc_accepted = True
    update_browser_state()
    st.rerun()

# STEP 3: Main Gemini AI Engine (Directly Opens After Login + TC)
else:
  update_browser_state()

  with st.sidebar:
    st.title("🤖 JARVIS Config")
    st.success("✅ Logged In")

    default_gemini = st.secrets.get("GEMINI_API_KEY", "")
    gemini_key = st.text_input(
        "Gemini API Key:", value=default_gemini, type="password"
    )

    st.divider()
    st.subheader("📚 App History")
    st.caption(f"Total Saved Messages: {len(st.session_state.messages)}")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
      st.session_state.messages = []
      if "chat_history" in st.query_params:
        del st.query_params["chat_history"]
      st.rerun()

    if st.button("🔴 Logout", use_container_width=True):
      st.session_state.auth = None
      st.session_state.tc_accepted = False
      st.session_state.messages = []
      st.query_params.clear()
      st.rerun()

  st.title("⚡ JARVIS AI Engine")

  # Display Saved Chat History (Persistent on Refresh)
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Bottom Fixed Chat Bar (Gemini Style)
  if user_query := st.chat_input("Ask JARVIS anything..."):
    if not gemini_key.strip():
      st.error("⚠️ Gemini API Key missing hai! Sidebar mein key add karein.")
    else:
      # Append & Display User Query
      st.session_state.messages.append({"role": "user", "content": user_query})
      with st.chat_message("user"):
        st.markdown(user_query)

      # Generate Gemini Streamed Response
      with st.chat_message("assistant"):
        try:
          genai.configure(api_key=gemini_key.strip())
          model = genai.GenerativeModel("gemini-4.0-flash")

          response_placeholder = st.empty()
          full_response = ""

          response = model.generate_content(
              user_query,
              generation_config=genai.types.GenerationConfig(
                  max_output_tokens=1000, temperature=0.7
              ),
              stream=True,
          )

          for chunk in response:
            if chunk.text:
              full_response += chunk.text
              response_placeholder.markdown(full_response + "▌")

          response_placeholder.markdown(full_response)

          # Append Assistant Response & Sync Storage State
          st.session_state.messages.append(
              {"role": "assistant", "content": full_response}
          )
          update_browser_state()

        except Exception as e:
          st.error(f"Error: {str(e)}")
