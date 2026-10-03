import streamlit as st
from groq import Groq
import json

st.set_page_config(page_title="JARVIS AI - Full + No Repeat", layout="wide")
st.title("JARVIS AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

JARVIS_SYSTEM = "You are JARVIS AI, created by BOSS DEVIL. You are NOT ChatGPT, NOT OpenAI, NOT Meta AI. If anyone asks 'Who are you?' you MUST say: 'I am JARVIS, created by my Boss DEVIL . I am your personal AI assistant.' Never say you are ChatGPT. Always reply as JARVIS."

# Clear Button
if st.sidebar.button("🗑️ Chat Clear"):
    st.session_state.clear()
    st.rerun()

func = st.sidebar.selectbox("Function Chuno Boss:",
    ["1. Normal Chat", "2. Streaming Chat", "3. Code Generator", "4. Math Solver", "5. Tool Calling", "6. JSON Mode", "7. Summarizer"]
)

# Common settings - Isse repeat khatam hoga
def get_client(messages):
    return client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.9, # No repeat ke liye
        top_p=0.95
    )

# 1. NORMAL CHAT - No Repeat
if func == "1. Normal Chat":
    st.header("💬 Normal Chat")
    if "chat1" not in st.session_state: st.session_state.chat1 = []
    for m in st.session_state.chat1: st.chat_message(m["role"]).write(m["content"])
    q = st.chat_input("Bolo Boss...")
    if q:
        st.session_state.chat1.append({"role":"user","content":q})
        st.chat_message("user").write(q)
        # Sirf naya sawal bhejo, pura history nahi
        res = get_client([{"role":"user","content":q}])
        ans = res.choices[0].message.content
        st.chat_message("assistant").write(ans)
        st.session_state.chat1.append({"role":"assistant","content":ans})

# 2. STREAMING CHAT - No Repeat
elif func == "2. Streaming Chat":
    st.header("⚡ Streaming")
    q = st.text_input("Sawal:", key="s2")
    if q:
        stream = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user","content":q}], temperature=0.9, stream=True)
        box = st.empty()
        full = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                box.write(full)

# 3. CODE GENERATOR - No Repeat
elif func == "3. Code Generator":
    st.header("💻 Code Generator")
    q = st.text_input("Kaisa code?", key="s3")
    if q:
        res = get_client([{"role":"system","content":"You are expert coder. Only give code. Each time give different style."},{"role":"user","content":q}])
        st.code(res.choices[0].message.content, language="python")

# 4. MATH SOLVER - No Repeat
elif func == "4. Math Solver":
    st.header("🧮 Math Solver")
    q = st.text_input("Math Problem:", key="s4")
    if q:
        res = get_client([{"role":"system","content":"Solve step by step, fresh answer every time."},{"role":"user","content":q}])
        st.write(res.choices[0].message.content)

# 5. TOOL CALLING
elif func == "5. Tool Calling":
    st.header("🛠️ Tool Calling")
    q = st.text_input("Ex: Delhi weather?", key="s5")
    if q:
        tools = [{"type":"function","function":{"name":"get_weather","description":"Get weather","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}]
        res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user","content":q}], tools=tools, tool_choice="auto", temperature=0.9)
        st.json(res.choices[0].message.model_dump())

# 6. JSON MODE
elif func == "6. JSON Mode":
    st.header("📦 JSON Mode")
    q = st.text_input("Ex: 2 phones in JSON", key="s6")
    if q:
        res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user","content":q}], response_format={"type":"json_object"}, temperature=0.9)
        st.json(json.loads(res.choices[0].message.content))

# 7. SUMMARIZER
elif func == "7. Summarizer":
    st.header("📝 Summarizer")
    txt = st.text_area("Text paste karo:", key="s7")
    if st.button("Summarize") and txt:
        res = get_client([{"role":"user","content":f"Summarize fresh, don't repeat old summary: {txt}"}])
        st.write(res.choices[0].message.content)
