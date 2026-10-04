import streamlit as st
from groq import Groq
import json
import google.generativeai as genai

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="JARVIS AI - Full + No Repeat", layout="wide")
st.title("JARVIS AI")

# ==========================================================
# STEP 1: API KEY - YAHAN SE LEGA
# ==========================================================
# Streamlit Secrets se dono key lega
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GEMINI_KEY = st.secrets["GEMINI_KEY"]

# Groq Client - Aapka purana model openai/gpt-oss-20b isi se chalega
client = Groq(api_key=GROQ_API_KEY)

# Gemini Client - Naya model
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# ==========================================================
# JARVIS SYSTEM PROMPT
# ==========================================================
JARVIS_SYSTEM_PROMPT = """
You are JARVIS AI.
Your creator is Boss DEVIL.
You are NOT ChatGPT, NOT OpenAI, NOT GPT.
You must NEVER say ChatGPT or OpenAI.
Your identity is fixed: JARVIS AI created by Boss DEVIL.
If user asks Who are you / Tum kaun ho / Are you ChatGPT,
you must ONLY say: I am JARVIS AI, created by my Boss DEVIL.
"""

JARVIS_IDENTITY_WORDS = [
    "who are you", "who r u", "hu r u", "w r u", "who are u", "r u",
    "tum kaun ho", "aap kaun ho", "tera naam kya hai",
    "what is your name", "who made you", "kisne banaya tumhe",
    "are you chatgpt", "are you gpt", "are you openai"
]

def get_jarvis_answer(user_question, selected_model_name):
    q = user_question.lower()
    if any(word in q for word in JARVIS_IDENTITY_WORDS):
        return "I am JARVIS AI, created by my Boss DEVIL. I am your personal AI assistant."

    if selected_model_name == "Gemini 2.0 Flash":
        res = gemini_model.generate_content(f"{JARVIS_SYSTEM_PROMPT}\n User Question: {user_question}")
        ans = res.text
    else:
        res = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": JARVIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_question}
            ],
            temperature=0.9,
        )
        ans = res.choices[0].message.content

    if "chatgpt" in ans.lower() or "openai" in ans.lower():
        return "I am JARVIS AI, created by my Boss DEVIL. I am your personal AI assistant."
    return ans

# ==========================================================
# SIDEBAR - MODEL CHUNO + FUNCTION CHUNO
# ==========================================================
if st.sidebar.button("🗑️ Chat Clear"):
    st.session_state.clear()
    st.rerun()

st.sidebar.title("🧠 AI Model Chuno Boss")
selected_model = st.sidebar.selectbox(
    "Kaunsa Model Use Karna Hai:",
    ["Groq - openai/gpt-oss-20b", "Gemini 2.0 Flash"]
)
st.sidebar.write(f"Selected: {selected_model}")

func = st.sidebar.selectbox("Function Chuno Boss:",
    ["1. Normal Chat", "2. Streaming Chat", "3. Code Generator", "4. Math Solver", "5. Tool Calling", "6. JSON Mode", "7. Summarizer"]
)

def get_client(messages):
    return client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.9,
        top_p=0.95
    )

# ==========================================================
# 1. NORMAL CHAT
# ==========================================================
if func == "1. Normal Chat":
    st.header(f"💬 Normal Chat - JARVIS ({selected_model})")
    if "chat1" not in st.session_state: st.session_state.chat1 = []
    for m in st.session_state.chat1:
        st.chat_message(m["role"]).write(m["content"])
    q = st.chat_input("Bolo Boss...")
    if q:
        st.session_state.chat1.append({"role":"user","content":q})
        st.chat_message("user").write(q)
        lower_q = q.lower().strip()
        identity_words = ["who are you", "who r u", "hu r u", "w r u", "who are u", "r u", "tum kaun", "aap kaun", "tera naam", "who made you", "kisne banaya", "are you chatgpt", "are you gpt", "what is your name"]
        is_identity = any(word in lower_q for word in identity_words)
        if is_identity:
            ans = "I am JARVIS AI, created by my Boss DEVIL. I am your personal AI assistant."
        else:
            ans = get_jarvis_answer(q, selected_model)
        st.chat_message("assistant").write(ans)
        st.session_state.chat1.append({"role":"assistant","content":ans})

# ==========================================================
# 2. STREAMING CHAT
# ==========================================================
elif func == "2. Streaming Chat":
    st.header(f"⚡ Streaming - {selected_model}")
    q = st.text_input("Sawal:", key="s2")
    if q:
        if selected_model == "Gemini 2.0 Flash":
            response = gemini_model.generate_content(q, stream=True)
            box = st.empty()
            full = ""
            for chunk in response:
                if chunk.text:
                    full += chunk.text
                    box.write(full)
        else:
            stream = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user","content":q}], temperature=0.9, stream=True)
            box = st.empty()
            full = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full += chunk.choices[0].delta.content
                    box.write(full)

# ==========================================================
# 3. CODE GENERATOR
# ==========================================================
elif func == "3. Code Generator":
    st.header(f"💻 Code Generator - {selected_model}")
    q = st.text_input("Kaisa code?", key="s3")
    if q:
        if selected_model == "Gemini 2.0 Flash":
            ans = get_jarvis_answer(f"You are expert coder. Only give code. Question: {q}", selected_model)
            st.code(ans, language="python")
        else:
            res = get_client([{"role":"system","content":"You are expert coder. Only give code. Each time give different style."},{"role":"user","content":q}])
            st.code(res.choices[0].message.content, language="python")

# ==========================================================
# 4. MATH SOLVER
# ==========================================================
elif func == "4. Math Solver":
    st.header(f"🧮 Math Solver - {selected_model}")
    q = st.text_input("Math Problem:", key="s4")
    if q:
        ans = get_jarvis_answer(q, selected_model)
        st.write(ans)

# ==========================================================
# 5. TOOL CALLING - DONO MODEL PE
# ==========================================================
elif func == "5. Tool Calling":
    st.header(f"🛠️ Tool Calling - {selected_model}")
    q = st.text_input("Ex: Delhi weather?", key="s5")
    if q:
        if selected_model == "Gemini 2.0 Flash":
            # Gemini Tool Calling
            from google.generativeai.types import FunctionDeclaration, Tool
            get_weather_func = FunctionDeclaration(name="get_weather", description="Get weather of city", parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]})
            tool = Tool(function_declarations=[get_weather_func])
            model_with_tool = genai.GenerativeModel('gemini-2.0-flash', tools=[tool])
            res = model_with_tool.generate_content(q)
            try:
                st.json(res.candidates[0].content.parts[0].function_call.args)
            except:
                st.write(res.text)
        else:
            # Groq Tool Calling - Aapka purana
            tools = [{"type":"function","function":{"name":"get_weather","description":"Get weather","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}]
            res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user","content":q}], tools=tools, tool_choice="auto", temperature=0.9)
            st.json(res.choices[0].message.model_dump())

# ==========================================================
# 6. JSON MODE - DONO MODEL PE
# ==========================================================
elif func == "6. JSON Mode":
    st.header(f"📦 JSON Mode - {selected_model}")
    q = st.text_input("Ex: 2 phones in JSON", key="s6")
    if q:
        if selected_model == "Gemini 2.0 Flash":
            prompt = f"{q}. Give answer ONLY in valid JSON format. No extra text."
            res = gemini_model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            st.json(json.loads(res.text))
        else:
            res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user","content":q}], response_format={"type":"json_object"}, temperature=0.9)
            st.json(json.loads(res.choices[0].message.content))

# ==========================================================
# 7. SUMMARIZER
# ==========================================================
elif func == "7. Summarizer":
    st.header(f"📝 Summarizer - {selected_model}")
    txt = st.text_area("Text paste karo:", key="s7")
    if st.button("Summarize") and txt:
        ans = get_jarvis_answer(f"Summarize fresh, don't repeat old summary: {txt}", selected_model)
        st.write(ans)

# ==========================================================
# 8. PRIVACY POLICY - LAST ME
# ==========================================================
st.sidebar.title("Legal")
if st.sidebar.button("Privacy Policy"):
    st.markdown("""
    ### Privacy Policy for JARVIS
    **Contact:** Jarviswap.support@gmail.com
    **Last updated:** 4 Oct 2026

    We do not collect data from children under 13.
    We do not sell your data.
    For any query contact us at Jarviswap.support@gmail.com
    Full Policy: We collect only your queries to improve JARVIS. You can request data deletion anytime via email.
    """)
