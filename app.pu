# 1. IMPORT - EVERY DATA SEARCH ON ✅
import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, re, base64, io
from PIL import Image
import streamlit.components.v1 as components

# 2. PAGE CONFIG
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")
st.markdown("""<style>.stDeployButton{display:none!important;}[data-testid="stToolbar"]{display:none!important;}footer{visibility:hidden!important;}#MainMenu{visibility:hidden!important;}</style>""", unsafe_allow_html=True)

# 3. MODEL - FINAL
GROQ_MODEL_NAME = "openai/gpt-oss-20b"
GEMINI_MODEL_NAME = "gemini-3.8-flash"
NANO_BANANA_MODEL = "gemini-3.1-flash-image"
NANO_BANANA_FALLBACK = "gemini-2.5-flash-image"
MODEL_LIST = ["Gemini 3.8 Flash - SEARCH ON", "Groq - openai/gpt-oss-20b", "Gemini 3.1 Nano Banana - SEARCH ON"]

MODES = {
    "💬 Normal Chat (All in One)": "You are JARVIS AI, created by Boss DEVIL. Use Google Search and Wikipedia for every data for accurate answer.",
    "🖼️ Image Creating": "IMAGE_MODE",
    "💻 Code Helper": "You are Code Expert. Search latest docs from web if needed.",
    "🧮 Math Solver": "You are Math Genius. Solve with LaTeX.",
    "🎨 Image Prompt": "You are Image Prompt Expert. Search character details from Wikipedia.",
    "📖 Story Writer": "You are Story Writer. Search story details from web if it's novel based.",
    "🔥 Roast Mode": "You are Roast King.",
    "📚 Study Helper": "You are Study Helper. Use Google Search and Wikipedia for every study data.",
    "🌐 Translator": "You are Translator.",
    "✉️ Email Writer": "You are Email Expert.",
    "🎬 Video Creating": "VIDEO_MODE",
}

# 4. SECRET - 0 TO INFINITY
try: GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except: GROQ_API_KEY = "gsk_dummy"
GEMINI_KEYS = []
try:
    for k,v in st.secrets.items():
        if "GEMINI" in k and "KEY" in k: GEMINI_KEYS.append(v)
except: pass
client = Groq(api_key=GROQ_API_KEY)

# 5. CORE - FOR EVERYTHING EVERY DATA SEARCH ON ✅
def search_enhance_prompt(query):
    """Har prompt ko Wikipedia + Google se enhance karo"""
    try:
        for key in GEMINI_KEYS:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(GEMINI_MODEL_NAME, tools=[{"google_search_retrieval": {}}])
                q = f"Search Wikipedia/Google for accurate info about: {query}. Give short accurate summary for AI to use. If character/novel, give visual details."
                resp = model.generate_content(q)
                return resp.text
            except: continue
    except: pass
    return query

def get_text_answer(prompt, model_name, system_prompt):
    """FOR EVERY DATA - SEARCH ON"""
    enhanced_info = search_enhance_prompt(prompt)
    final = f"""{system_prompt}
    User Question: {prompt}
    Web Search Data (Wikipedia/Google): {enhanced_info}
    Use above search data for 100% accurate answer. If it's character, use accurate details.
    Question: {prompt}"""

    if "Groq" in model_name:
        res = client.chat.completions.create(model=GROQ_MODEL_NAME, messages=[{"role":"system","content":final},{"role":"user","content":prompt}], temperature=0.7)
        return res.choices[0].message.content

    # Gemini with SEARCH ON - FOR EVERY DATA
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME, tools=[{"google_search_retrieval": {}}])
            return model.generate_content(final).text
        except: continue

    # Fallback without search
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            m = genai.GenerativeModel(GEMINI_MODEL_NAME)
            return m.generate_content(final).text
        except: continue

    res = client.chat.completions.create(model=GROQ_MODEL_NAME, messages=[{"role":"system","content":final},{"role":"user","content":prompt}], temperature=0.7)
    return res.choices[0].message.content

def generate_nano_banana(prompt):
    """FOR EVERY IMAGE - WIKIPEDIA SEARCH ON"""
    if not GEMINI_KEYS: return None

    # Pehle har image ke liye Wikipedia search
    enhanced = search_enhance_prompt(prompt)

    for key in GEMINI_KEYS:
        for mid in [NANO_BANANA_MODEL, NANO_BANANA_FALLBACK]:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(mid)
                final_prompt = f"{enhanced}, accurate character, highly detailed, 8k, sharp focus, {prompt}"
                resp = model.generate_content([final_prompt], generation_config={"response_modalities": ["TEXT","IMAGE"]})
                for part in resp.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                        img_data = base64.b64decode(part.inline_data.data)
                        return Image.open(io.BytesIO(img_data))
            except: continue
    return None

def render_with_preview(text):
    st.markdown(text)
    matches = re.findall(r"```(html|javascript|js|css)\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    for lang, code in matches:
        st.write(f"🔥 Live Preview ({lang}):")
        html_code = f"<script>{code}</script>" if lang.lower() in ["js","javascript"] else code
        components.html(html_code, height=350, scrolling=True)

# 6. UI
if "messages" not in st.session_state: st.session_state.messages = []
with st.sidebar:
    st.title("🤖 JARVIS - SEARCH ON")
    page = st.radio("Page", ["Chat", "Privacy Policy"])
    if page == "Chat":
        selected_model = st.selectbox("🧠 Model", MODEL_LIST, key="side_model")
        selected_mode_name = st.selectbox("🎮 Modes", list(MODES.keys()), key="side_mode")
        st.caption(f"Keys: {len(GEMINI_KEYS)} | Search: ON | For Everything Every Data")
        if st.button("Clear Chat 🗑️"):
            st.session_state.messages = []
            st.rerun()

if page == "Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.markdown("Search ON via Google + Wikipedia. Created by Boss DEVIL")
else:
    st.title("JARVIS AI - EVERY DATA SEARCH ON 🔍")
    c1, c2 = st.columns(2)
    with c1: selected_model = st.selectbox("🧠 Model Change", MODEL_LIST, key="main_model2")
    with c2: selected_mode_name = st.selectbox("🎮 Mode Change", list(MODES.keys()), key="main_mode2")
    selected_prompt = MODES[selected_mode_name]
    st.caption(f"Mode: {selected_mode_name} | Model: {selected_model} | 🌐 Wikipedia + Google Search ON")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "image" in msg: st.image(msg["image"])
            if "image_url" in msg: st.image(msg["image_url"])
            st.markdown(msg["content"])

    if prompt := st.chat_input("Bolo Boss... Har sawal ka jawab Wikipedia + Google Search se..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            q = prompt.lower()
            image_keywords = ["image", "photo", "picture", "draw", "banao", "generate", "poster", "logo", "wallpaper", "character", "xiao yan", "nie li", "tang san"]
            is_image = any(w in q for w in image_keywords) or MODES[selected_mode_name] == "IMAGE_MODE"

            if is_image:
                with st.spinner("🔍 Wikipedia + Google se search kar raha hu... Fir Nano Banana se image..."):
                    img = generate_nano_banana(prompt)
                    if img:
                        st.image(img)
                        st.session_state.messages.append({"role":"assistant","content":f"✅ Search + Nano Banana: {prompt}", "image": img})
                    else:
                        # Fallback with enhanced search
                        enh = search_enhance_prompt(prompt)
                        safe = urllib.parse.quote(enh[:500])
                        url = f"https://image.pollinations.ai/prompt/{safe}?model=flux&seed={random.randint(1,99999)}&width=1024&height=1024&nologo=true"
                        st.image(url)
                        st.session_state.messages.append({"role":"assistant","content":f"Image (Search ON): {prompt}", "image_url": url})
            else:
                with st.spinner("🔍 Google + Wikipedia Search ON - Jawab la raha hu..."):
                    ans = get_text_answer(prompt, selected_model, selected_prompt)
                    render_with_preview(ans)
                    st.session_state.messages.append({"role":"assistant","content":ans})

st.markdown("""<div style="text-align:center; padding:10px; color:#888; font-size:12px;">© 2026 JARVIS AI | Every Data - Google + Wikipedia Search ON | Created by Boss DEVIL</div>""", unsafe_allow_html=True)
