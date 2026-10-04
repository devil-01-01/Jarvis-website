# 1. IMPORT
import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, re, requests, io
from PIL import Image
import streamlit.components.v1 as components

# 2. PAGE CONFIG
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")
st.markdown("""<style>.stDeployButton{display:none!important;}[data-testid="stToolbar"]{display:none!important;}footer{visibility:hidden!important;}#MainMenu{visibility:hidden!important;}</style>""", unsafe_allow_html=True)

# 3. MODEL - NANO BANANA HATA DIYA ✅
GROQ_MODEL_NAME = "openai/gpt-oss-20b"
GEMINI_MODEL_NAME = "gemini-3.8-flash"
MODEL_LIST = ["Gemini 3.8 Flash - SEARCH ON", "Groq - openai/gpt-oss-20b", "FLUX.1 - Perfect Gender"]

MODES = {
    "💬 Normal Chat (All in One)": "You are JARVIS AI, created by Boss DEVIL. Use Google Search and Wikipedia for every data.",
    "Image Creating": "IMAGE_MODE",
    "Code Helper": "You are Code Expert.",
    "Math Solver": "You are Math Genius.",
    "Image Prompt": "You are Image Prompt Expert.",
    "Story Writer": "You are Story Writer.",
    "Roast Mode": "You are Roast King.",
    "Study Helper": "You are Study Helper.",
    "🌐 Translator": "You are Translator.",
    "✉️ Email Writer": "You are Email Expert.",
}

# 4. SECRETS
try: GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except: GROQ_API_KEY = ""
try: GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except: GOOGLE_API_KEY = ""
try: CX_ID = st.secrets["CX_ID"]
except: CX_ID = "e604ce9810cbf4ea4"
try: HF_API_KEY = st.secrets["HF_API_KEY"]
except: HF_API_KEY = ""

GEMINI_KEYS = []
try:
    for k,v in st.secrets.items():
        if "GEMINI" in k and "KEY" in k: GEMINI_KEYS.append(v)
except: pass

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# 5. CORE
def google_custom_search(query):
    if not GOOGLE_API_KEY or not CX_ID: return ""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {'q': query, 'key': GOOGLE_API_KEY, 'cx': CX_ID, 'num': 5}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        text = ""
        for item in data.get('items', []):
            text += f"{item['title']} - {item['snippet']} "
        return text
    except: return ""

def search_enhance_prompt(query):
    cse = google_custom_search(f"{query} male or female wiki")
    return f"{cse} | Original: {query}"

def get_text_answer(prompt, model_name, system_prompt):
    enhanced = search_enhance_prompt(prompt)
    final = f"{system_prompt}\nSearch Data: {enhanced}\nQuestion: {prompt}"
    if "Groq" in model_name and client:
        try:
            res = client.chat.completions.create(model=GROQ_MODEL_NAME, messages=[{"role":"system","content":final},{"role":"user","content":prompt}], temperature=0.7)
            return res.choices[0].message.content
        except: pass
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME, tools=[{"google_search_retrieval": {}}])
            return model.generate_content(final).text
        except: continue
    return "API Key Error!"

# --- IMAGE - SIRF FLUX, NO NANO BANANA ---
def generate_flux_image(prompt):
    enhanced = search_enhance_prompt(prompt)
    lower = (enhanced + " " + prompt).lower()
    is_male = any(k in lower for k in ["xiao yan", "tang san", "nie li", "lin dong", "male", "boy", "protagonist"])

    if is_male:
        gender_fix = "1boy, handsome male protagonist, masculine face, short black hair, male only, solo, not a girl, no female"
        negative = "1girl, female, woman, breasts"
    else:
        gender_fix = "accurate gender, beautiful"
        negative = "ugly, deformed"

    final_prompt = f"{prompt}, {gender_fix}, {enhanced}, ultra detailed anime, 8k, sharp focus"

    # HF FLUX.1-schnell
    if HF_API_KEY:
        try:
            API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            response = requests.post(API_URL, headers=headers, json={"inputs": final_prompt}, timeout=60)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
        except Exception as e:
            print(e)

    # Backup Pollination FLUX-PRO
    try:
        safe = urllib.parse.quote(final_prompt[:800])
        neg = urllib.parse.quote(negative)
        url = f"https://image.pollinations.ai/prompt/{safe}?model=flux-pro&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true&negative_prompt={neg}"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content))
    except: pass
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
    st.title("JARVIS - SEARCH ON")
    page = st.radio("Page", ["Chat", "Privacy Policy"])
    if page == "Chat":
        selected_model = st.selectbox("Model", MODEL_LIST, key="side_model")
        selected_mode_name = st.selectbox("Modes", list(MODES.keys()), key="side_mode")
        st.caption(f"HF: {'ON ✅' if HF_API_KEY else 'OFF ❌'}")
        if st.button("Clear Chat 🗑️"):
            st.session_state.messages = []
            st.rerun()

if page == "Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.markdown("© 2026 JARVIS AI | Created by Boss DEVIL")
else:
    st.title("JARVIS AI - FLUX ONLY 🔍")
    c1, c2 = st.columns(2)
    with c1: selected_model = st.selectbox("Model Change", MODEL_LIST, key="main_model2")
    with c2: selected_mode_name = st.selectbox("Mode Change", list(MODES.keys()), key="main_mode2")
    selected_prompt = MODES[selected_mode_name]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "image" in msg: st.image(msg["image"])
            st.markdown(msg["content"])

    if prompt := st.chat_input("Bolo Boss..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            q = prompt.lower()
            image_keywords = ["image", "photo", "picture", "draw", "banao", "generate", "poster", "logo", "wallpaper", "character", "xiao yan", "nie li", "tang san"]
            is_image = any(w in q for w in image_keywords) or MODES[selected_mode_name] == "IMAGE_MODE"
            if is_image:
                with st.spinner("FLUX se bana raha hu... 100% Ladka banega..."):
                    img = generate_flux_image(prompt)
                    if img:
                        st.image(img)
                        st.session_state.messages.append({"role":"assistant","content":f"✅ FLUX Image: {prompt}", "image": img})
                    else:
                        st.error("HF_API_KEY check karo Boss!")
            else:
                with st.spinner("Search ON..."):
                    ans = get_text_answer(prompt, selected_model, selected_prompt)
                    render_with_preview(ans)
                    st.session_state.messages.append({"role":"assistant","content":ans})
