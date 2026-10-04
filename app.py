# 1. IMPORT - CHECKED ✅
import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, re, base64, io
from PIL import Image
import streamlit.components.v1 as components

# 2. PAGE CONFIG
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stDeployButton{display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
footer{visibility:hidden!important;}
#MainMenu{visibility:hidden!important;}
</style>
""", unsafe_allow_html=True)

# 3. MODEL - FINAL COMBO ✅
GROQ_MODEL_NAME = "openai/gpt-oss-20b"
GEMINI_MODEL_NAME = "gemini-3.8-flash"
NANO_BANANA_MODEL = "gemini-3.1-flash-image" # BEST
NANO_BANANA_FALLBACK = "gemini-2.5-flash-image" # FAST FREE
MODEL_LIST = ["Gemini 3.8 Flash - LATEST", "Groq - openai/gpt-oss-20b", "Gemini 3.1 + Nano Banana - BEST IMAGE"]

MODES = {
    "💬 Normal Chat (All in One)": "You are JARVIS AI, created by Boss DEVIL. You can do everything.",
    "Image Creating": "IMAGE_MODE",
    "Code Helper": "You are Code Expert.",
    "Math Solver": "You are Math Genius. Solve with LaTeX $...$",
    "Image Prompt": "You are Image Prompt Expert.",
    "Story Writer": "You are Story Writer.",
    "Roast Mode": "You are Roast King.",
    "Study Helper": "You are Study Helper.",
    "🌐 Translator": "You are Translator.",
    "✉️ Email Writer": "You are Email Expert.",
    "Video Creating": "VIDEO_MODE",
}

# 4. SECRET - 0 TO INFINITY ✅
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "gsk_dummy"

GEMINI_KEYS = []
try:
    for k,v in st.secrets.items():
        if "GEMINI" in k and "KEY" in k:
            GEMINI_KEYS.append(v)
except:
    pass

client = Groq(api_key=GROQ_API_KEY)

# 5. NANO BANANA - 0 TO INFINITY LOGIC ✅
def generate_nano_banana(prompt):
    # Agar ek bhi key nahi to None
    if not GEMINI_KEYS:
        return None
    # Har key try karo 0 se Infinity tak
    for key in GEMINI_KEYS:
        for mid in [NANO_BANANA_MODEL, NANO_BANANA_FALLBACK]:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(mid)
                resp = model.generate_content([prompt], generation_config={"response_modalities": ["TEXT","IMAGE"]})
                for part in resp.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        img_data = base64.b64decode(part.inline_data.data)
                        return Image.open(io.BytesIO(img_data))
            except:
                continue
    return None

# 6. CORE LOGIC - 0 TO INFINITY ✅
def get_text_answer(prompt, model_name, system_prompt):
    final = f"{system_prompt}\nQuestion: {prompt}"
    if "Groq" in model_name:
        res = client.chat.completions.create(model=GROQ_MODEL_NAME, messages=[{"role":"system","content":final},{"role":"user","content":prompt}], temperature=0.7)
        return res.choices[0].message.content
    for key in GEMINI_KEYS: # 0 to Infinity
        try:
            genai.configure(api_key=key)
            m = genai.GenerativeModel(GEMINI_MODEL_NAME)
            return m.generate_content(final).text
        except: continue
    res = client.chat.completions.create(model=GROQ_MODEL_NAME, messages=[{"role":"system","content":final},{"role":"user","content":prompt}], temperature=0.7)
    return res.choices[0].message.content

def render_with_preview(text):
    st.markdown(text)
    matches = re.findall(r"```(html|javascript|js|css)\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    for lang, code in matches:
        st.write(f"🔥 Live Preview ({lang}):")
        html_code = f"<script>{code}</script>" if lang.lower() in ["js","javascript"] else code
        components.html(html_code, height=350, scrolling=True)

# 7. UI
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🤖 JARVIS Control")
    page = st.radio("Page", ["Chat", "Privacy Policy"], key="main_page")
    if page == "Chat":
        selected_model = st.selectbox("🧠 Model", MODEL_LIST, key="side_model")
        selected_mode_name = st.selectbox("🎮 Modes", list(MODES.keys()), key="side_mode")
        selected_prompt = MODES[selected_mode_name]
        st.caption(f"Keys Loaded: {len(GEMINI_KEYS)} 🔑 | 0 to Infinity ON")
        if st.button("Clear Chat 🗑️"):
            st.session_state.messages = []
            st.rerun()

if page == "Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.markdown("No data saved. Created by Boss DEVIL | Gemini 3.8 + Nano Banana 3.1")
else:
    st.title("JARVIS AI - Gemini 3.8 + Nano Banana")
    c1, c2 = st.columns(2)
    with c1:
        selected_model = st.selectbox("🧠 Model Change", MODEL_LIST, key="main_model2")
    with c2:
        selected_mode_name = st.selectbox("🎮 Mode Change", list(MODES.keys()), key="main_mode2")
    selected_prompt = MODES[selected_mode_name]
    st.caption(f"Mode: {selected_mode_name} | Model: {selected_model}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "image" in msg: st.image(msg["image"])
            if "image_url" in msg: st.image(msg["image_url"])
            st.markdown(msg["content"])

    if prompt := st.chat_input("Bolo Boss... image banao to sidha Nano Banana se banega..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            q = prompt.lower()
            # DIRECT IMAGE LOGIC - CHITTHI BAND ✅
            image_keywords = ["image", "photo", "picture", "draw", "banao", "generate", "poster", "logo", "wallpaper"]
            is_image = any(w in q for w in image_keywords) or selected_prompt == "IMAGE_MODE"

            if is_image:
                with st.spinner("🍌 Nano Banana 3.1 BEST (0 to Infinity)..."):
                    img = generate_nano_banana(prompt)
                    if img:
                        st.image(img)
                        st.session_state.messages.append({"role":"assistant","content":f"✅ Nano Banana 3.1 se ban gaya: {prompt}", "image": img})
                    else:
                        safe = urllib.parse.quote(prompt[:500])
                        url = f"https://image.pollinations.ai/prompt/{safe}?model=flux&seed={random.randint(1,99999)}&width=1024&height=1024&nologo=true"
                        st.image(url)
                        st.session_state.messages.append({"role":"assistant","content":f"Image: {prompt}", "image_url": url})
            else:
                with st.spinner("Gemini 3.8..."):
                    ans = get_text_answer(prompt, selected_model, selected_prompt)
                    render_with_preview(ans)
                    st.session_state.messages.append({"role":"assistant","content":ans})

st.markdown("""<div style="text-align:center; padding:15px; color:#888; font-size:12px; border-top:1px solid #333; margin-top:30px;">© 2026 JARVIS AI | Created by Boss DEVIL | Gemini 3.8 + Nano Banana 3.1 | 0 to Infinity</div>""", unsafe_allow_html=True)
