import base64
import json
import time
import uuid
import extra_streamlit_components as stx
from google import genai
from google.genai import types
from google.genai.errors import APIError
from groq import Groq
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="JARVIS",
    page_icon="🤖",
    layout="wide",
)

# 2. Global Secrets Fetching
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)

if not GEMINI_API_KEY:
  st.error(
      "⚠️ GEMINI_API_KEY Missing! Streamlit Cloud Secrets mein 'GEMINI_API_KEY'"
      " add karein."
  )
  st.stop()

# 3. Cookie Manager
cookie_manager = stx.CookieManager(key="jarvis_multi_chat_mgr")

# 4. Strict System Prompt
STRICT_SYSTEM_PROMPT = """
You are JARVIS. 
If anyone asks who created you, who you are, or about your developer/creator/boss (in any language, e.g., English, Hindi, Hinglish), your response MUST BE STRICTLY EXACTLY:
"I am Jarvis. Develop by boss DEVIL"
Do not break character. Do not mention Google, OpenAI, Groq, or any other entity as your creator.
"""

# Load Saved Threads
saved_threads_raw = cookie_manager.get("jarvis_chat_threads")
if "chat_threads" not in st.session_state:
  try:
    st.session_state.chat_threads = (
        json.loads(saved_threads_raw) if saved_threads_raw else {}
    )
  except Exception:
    st.session_state.chat_threads = {}

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


def sync_threads_to_cookie():
  cookie_manager.set(
      "jarvis_chat_threads",
      json.dumps(st.session_state.chat_threads),
      key="set_threads_cookie",
  )


# ---------------------------------------------------------
# SIDEBAR: MODEL SELECTOR & CHATS
# ---------------------------------------------------------
with st.sidebar:
  st.title("🤖 JARVIS")
  st.caption("Powered by Global Engine")

  st.divider()

  # Model Selection Menu
  selected_model = st.selectbox(
      "🎯 Select Model:",
      options=[
          "openai/gpt-oss-20b (Text)",
          "gemini-nano-banana-2.1 (Image & Vision)",
      ],
      index=0,
  )

  st.divider()

  if st.button("➕ New Chat", use_container_width=True, type="primary"):
    new_id = str(uuid.uuid4())[:8]
    st.session_state.chat_threads[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_thread_id = new_id
    sync_threads_to_cookie()
    st.rerun()

  st.subheader("📚 Saved Threads")
  for t_id in list(st.session_state.chat_threads.keys()):
    t_data = st.session_state.chat_threads[t_id]
    title = t_data.get("title", "Untitled")
    is_active = t_id == st.session_state.current_thread_id
    btn_label = f"👉 {title}" if is_active else f"💬 {title}"

    col_btn, col_del = st.columns([0.8, 0.2])
    with col_btn:
      if st.button(btn_label, key=f"select_{t_id}", use_container_width=True):
        st.session_state.current_thread_id = t_id
        st.rerun()
    with col_del:
      if st.button("🗑️", key=f"del_{t_id}"):
        del st.session_state.chat_threads[t_id]
        remaining = list(st.session_state.chat_threads.keys())
        st.session_state.current_thread_id = (
            remaining[0] if remaining else str(uuid.uuid4())[:8]
        )
        if not remaining:
          st.session_state.chat_threads[st.session_state.current_thread_id] = {
              "title": "New Chat",
              "messages": [],
          }
        sync_threads_to_cookie()
        st.rerun()

# ---------------------------------------------------------
# MAIN INTERFACE
# ---------------------------------------------------------
active_id = st.session_state.current_thread_id
current_thread = st.session_state.chat_threads[active_id]
messages = current_thread["messages"]

st.title("JARVIS")

# Render History
for msg in messages:
  with st.chat_message(msg["role"]):
    if msg.get("type") == "image":
      st.image(msg["content"], caption=msg.get("caption", "Generated Visual"))
    else:
      st.markdown(msg["content"])

if user_query := st.chat_input("Ask JARVIS or request an image..."):
  if len(messages) == 0:
    current_thread["title"] = user_query[:25] + "..."

  messages.append({"role": "user", "content": user_query})
  with st.chat_message("user"):
    st.markdown(user_query)

  query_lower = user_query.lower()

  creator_keywords = [
      "who are you",
      "kaun ho",
      "kon ho",
      "who created you",
      "who developed you",
      "tumhe kisne banaya",
      "aapko kisne banaya",
      "who is your boss",
      "who is your creator",
      "who is devil",
  ]

  is_creator_query = any(kw in query_lower for kw in creator_keywords)

  with st.chat_message("assistant"):
    # 1. Direct Hardcoded Creator Guard
    if is_creator_query:
      bot_reply = "I am Jarvis. Develop by boss DEVIL"
      st.markdown(bot_reply)
      messages.append({"role": "assistant", "content": bot_reply})
      sync_threads_to_cookie()

    # 2. Image Generation Mode (gemini-nano-banana-2.1)
    elif selected_model == "gemini-nano-banana-2.1 (Image & Vision)" or any(
        kw in query_lower
        for kw in ["image", "generate", "draw", "photo", "picture", "banana"]
    ):
      st.info("🎨 Generating visual with gemini-nano-banana-2.1...")
      client = genai.Client(api_key=GEMINI_API_KEY)

      image_prompt = (
          f"System Context: {STRICT_SYSTEM_PROMPT}\nUser Prompt: {user_query}"
      )
      config = types.GenerateContentConfig(response_modalities=["IMAGE"])

      success = False
      for attempt in range(3):
        try:
          response = client.models.generate_content(
              model="gemini-nano-banana-2.1",
              contents=image_prompt,
              config=config,
          )

          image_rendered = False
          if hasattr(response, "candidates") and response.candidates:
            for part in response.candidates[0].content.parts:
              if hasattr(part, "inline_data") and part.inline_data:
                img_data = base64.b64encode(part.inline_data.data).decode(
                    "utf-8"
                )
                img_url = f"data:{part.inline_data.mime_type};base64,{img_data}"
                st.image(img_url, caption=user_query)

                messages.append({
                    "role": "assistant",
                    "type": "image",
                    "content": img_url,
                    "caption": user_query,
                })
                image_rendered = True

          if not image_rendered and getattr(response, "text", None):
            st.markdown(response.text)
            messages.append({"role": "assistant", "content": response.text})

          success = True
          break
        except APIError as e:
          if e.code == 503 and attempt < 2:
            time.sleep(3)
            continue
          else:
            st.error(
                f"⚠️ Server High Load / API Error ({e.code}): {e.message}"
            )
            break
        except Exception as e:
          st.error(f"Execution Error: {str(e)}")
          break

      if success:
        sync_threads_to_cookie()

    # 3. Text Generation Mode (openai/gpt-oss-20b via Groq)
    else:
      if not GROQ_API_KEY:
        st.error(
            "⚠️ GROQ_API_KEY Missing! Streamlit Cloud Secrets mein GROQ_API_KEY"
            " add karein."
        )
      else:
        try:
          groq_client = Groq(api_key=GROQ_API_KEY)

          completion = groq_client.chat.completions.create(
              model="openai/gpt-oss-20b",
              messages=[
                  {"role": "system", "content": STRICT_SYSTEM_PROMPT},
                  {"role": "user", "content": user_query},
              ],
              temperature=0.3,
          )

          resp_text = completion.choices[0].message.content
          st.markdown(resp_text)
          messages.append({"role": "assistant", "content": resp_text})
          sync_threads_to_cookie()
        except Exception as e:
          st.error(f"Execution Error (openai/gpt-oss-20b): {str(e)}")
      
