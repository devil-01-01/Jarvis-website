import json
import uuid
import extra_streamlit_components as stx
import google.generativeai as genai
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="JARVIS AI - Multi-Chat Engine", page_icon="🤖", layout="wide"
)

# 2. Cookie Manager Initialization
cookie_manager = stx.CookieManager(key="jarvis_multi_chat_mgr")


# 3. Gemini Model Loader
@st.cache_resource
def load_gemini_model(api_key):
  genai.configure(api_key=api_key)
  return genai.GenerativeModel("gemini-4.0-flash")


# 4. Load Chat History Threads from Browser Cookies
# Structure: { "thread_id_1": {"title": "Chat 1", "messages": [...]}, ... }
saved_threads_raw = cookie_manager.get("jarvis_chat_threads")

if "chat_threads" not in st.session_state:
  if saved_threads_raw:
    try:
      st.session_state.chat_threads = json.loads(saved_threads_raw)
    except Exception:
      st.session_state.chat_threads = {}
  else:
    st.session_state.chat_threads = {}

# Ensure at least one active thread exists
if not st.session_state.chat_threads:
  initial_id = str(uuid.uuid4())[:8]
  st.session_state.chat_threads = {
      initial_id: {"title": "New Chat", "messages": []}
  }
  st.session_state.current_thread_id = initial_id
elif "current_thread_id" not in st.session_state:
  st.session_state.current_thread_id = list(
      st.session_state.chat_threads.keys()
  )[0]


# Helper: Sync all chat threads to Cookie
def sync_threads_to_cookie():
  try:
    cookie_manager.set(
        "jarvis_chat_threads",
        json.dumps(st.session_state.chat_threads),
        key="set_threads_cookie",
    )
  except Exception as e:
    st.error(f"Failed to sync history: {str(e)}")


# ---------------------------------------------------------
# SIDEBAR: THREAD MANAGEMENT & SETTINGS
# ---------------------------------------------------------
with st.sidebar:
  st.title("🤖 JARVIS AI")

  # Gemini API Key Setup
  default_gemini = st.secrets.get("GEMINI_API_KEY", "")
  gemini_key = st.text_input(
      "Gemini API Key:", value=default_gemini, type="password"
  )

  st.divider()

  # Create New Chat Button
  if st.button("➕ New Chat Thread", use_container_width=True, type="primary"):
    new_id = str(uuid.uuid4())[:8]
    st.session_state.chat_threads[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_thread_id = new_id
    sync_threads_to_cookie()
    st.rerun()

  st.subheader("📚 Saved Conversations")

  # List All Saved Chat Threads
  thread_ids = list(st.session_state.chat_threads.keys())
  for t_id in thread_ids:
    thread_data = st.session_state.chat_threads[t_id]
    title = thread_data.get("title", "Untitled Chat")

    # Highlight active thread
    is_active = t_id == st.session_state.current_thread_id
    btn_label = f"💬 {title}" if not is_active else f"👉 {title} (Active)"

    col_btn, col_del = st.columns([0.8, 0.2])
    with col_btn:
      if st.button(btn_label, key=f"select_{t_id}", use_container_width=True):
        st.session_state.current_thread_id = t_id
        st.rerun()
    with col_del:
      if st.button("🗑️", key=f"del_{t_id}"):
        del st.session_state.chat_threads[t_id]
        # If deleted active thread, switch to remaining or create new
        remaining = list(st.session_state.chat_threads.keys())
        if remaining:
          st.session_state.current_thread_id = remaining[0]
        else:
          fresh_id = str(uuid.uuid4())[:8]
          st.session_state.chat_threads[fresh_id] = {
              "title": "New Chat",
              "messages": [],
          }
          st.session_state.current_thread_id = fresh_id

        sync_threads_to_cookie()
        st.rerun()

  st.divider()
  if st.button("🚨 Delete All History", use_container_width=True):
    st.session_state.chat_threads = {}
    fresh_id = str(uuid.uuid4())[:8]
    st.session_state.chat_threads[fresh_id] = {
        "title": "New Chat",
        "messages": [],
    }
    st.session_state.current_thread_id = fresh_id
    cookie_manager.delete("jarvis_chat_threads", key="del_all_threads")
    st.rerun()


# ---------------------------------------------------------
# MAIN CHAT INTERFACE
# ---------------------------------------------------------
active_id = st.session_state.current_thread_id
current_thread = st.session_state.chat_threads[active_id]
messages = current_thread["messages"]

st.title(f"⚡ {current_thread['title']}")

# Render Current Thread Chat Messages
for msg in messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

# User Query Processing
if user_query := st.chat_input("Ask JARVIS anything..."):
  if not gemini_key.strip():
    st.error("⚠️ Gemini API Key missing hai! Sidebar mein enter karein.")
  else:
    # Auto-title thread from first prompt
    if len(messages) == 0:
      new_title = user_query[:25] + ("..." if len(user_query) > 25 else "")
      current_thread["title"] = new_title

    # Append User Message
    messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
      st.markdown(user_query)

    # Generate Model Response
    with st.chat_message("assistant"):
      try:
        model = load_gemini_model(gemini_key.strip())
        response_placeholder = st.empty()
        full_response = ""

        response = model.generate_content(
            user_query,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1000, temperature=0.5
            ),
            stream=True,
        )

        for chunk in response:
          if chunk.text:
            full_response += chunk.text
            response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)
        messages.append({"role": "assistant", "content": full_response})

        # Save Complete Updated Thread Structure to Cookie
        sync_threads_to_cookie()

      except Exception as e:
        st.error(f"Error: {str(e)}")
