# 1. IMPORT
import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, re, requests, io
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
    
    /* YE 2 LINE SPACE KHATAM KAREGI BOSS */
    div.block-container{padding-top: 0rem !important; margin-top: -70px !important;}
    h1{padding-top: 0px !important; margin-top: 0px !important;}
</style>
""", unsafe_allow_html=True)

# 3. MODELS - FLUX ONLY, NO NANO BANANA
GROQ_MODEL_NAME = "openai/gpt-oss-20b"
GEMINI_MODEL_NAME = "gemini-3.5-flash"
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
MODEL_LIST = ["JARVIS-GPT", "JARVIS-GEMINI", "JARVIS-FLUX"]

MODES = {
    "💬 Normal Chat (All in One)": "You are JARVIS AI, created by Boss DEVIL. You are helpful, smart, and always answer. Use web knowledge.",
    "Image Creating": "IMAGE_MODE",
    "Code Helper": "You are Code Expert. Provide clean code with preview.",
    "Math Solver": "You are Math Genius. Solve with steps and LaTeX.",
    "Study Helper": "You are Study Helper. Explain simply with examples.",
    "Roast Mode": "You are Roast King - funny roasting.",
    "Story Writer": "You are Story Writer.",
}

# 4. SECRETS - SAFE LOADING
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
        if "GEMINI" in k.upper() and "KEY" in k.upper():
            if v and len(str(v)) > 20:
                GEMINI_KEYS.append(str(v).strip())
except: pass

client = None
if GROQ_API_KEY:
    try: client = Groq(api_key=GROQ_API_KEY)
    except: pass

# 5. CORE FUNCTIONS - ERROR PROOF
def google_custom_search(query):
    if not GOOGLE_API_KEY or not CX_ID: return ""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {'q': query, 'key': GOOGLE_API_KEY, 'cx': CX_ID, 'num': 3}
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        text = ""
        for item in data.get('items', []):
            text += f"{item.get('title','')} - {item.get('snippet','')} "
        return text[:1500]
    except: return ""

def get_text_answer(prompt, model_name, system_prompt):
    enhanced = google_custom_search(prompt)
    final_prompt = f"{system_prompt}\n\nWeb Search Info: {enhanced}\n\nUser Question: {prompt}\n\nGive detailed, accurate answer in same language as user:"

    # TRY 1: GROQ - SABSE STABLE
    if client:
        try:
            res = client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[{"role":"system","content":system_prompt},{"role":"user","content":final_prompt}],
                temperature=0.7, max_tokens=2000
            )
            if res.choices[0].message.content:
                return res.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}")

    # TRY 2: GEMINI KEYS
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            resp = model.generate_content(final_prompt)
            if resp and hasattr(resp, 'text') and resp.text:
                return resp.text
        except Exception as e:
            print(f"Gemini {key[:10]} fail: {e}")
            continue

    # TRY 3: LAST FALLBACK - SEARCH DATA SE ANSWER
    if enhanced:
        return f"**Google Search se mila (API busy tha):**\n\n{enhanced}\n\n**Iske basis par:** {prompt} ke liye ye information sabse relevant hai."

    return "Boss, saare API busy hai! 1 minute baad try karo. Ya GROQ_API_KEY check karo Secrets me - wo sabse stable hai."

def generate_flux_image(prompt):
    enhanced = google_custom_search(f"{prompt} anime character")
    lower = (enhanced + " " + prompt).lower()
    is_male = any(k in lower for k in ["xiao yan", "tang san", "nie li", "lin dong", "male", "boy", "he is", "protagonist"])

    if is_male:
        final_prompt = f"{prompt}, 1boy, handsome male protagonist, short black hair, masculine face, male only, solo, ultra detailed anime, 8k"
        negative = "1girl, female, woman, breasts"
    else:
        final_prompt = f"{prompt}, beautiful detailed, ultra detailed anime, 8k, {enhanced[:200]}"
        negative = "ugly, deformed, blurry"

    # HF FLUX
    if HF_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            r = requests.post(HF_API_URL, headers=headers, json={"inputs": final_prompt}, timeout=60)
            if r.status_code == 200:
                return Image.open(io.BytesIO(r.content))
        except Exception as e:
            print(f"HF Error: {e}")

    # Pollination Backup
    try:
        safe = urllib.parse.quote(final_prompt[:700])
        neg = urllib.parse.quote(negative)
        url = f"https://image.pollinations.ai/prompt/{safe}?model=flux-pro&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true&negative_prompt={neg}"
        r = requests.get(url, timeout=25)
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
    st.title("JARVIS AI")
    page = st.radio("Page", ["Chat", "Privacy Policy"])
    if page == "Chat":
        selected_model = st.selectbox("Model", MODEL_LIST, index=0)
        selected_mode_name = st.selectbox("Modes", list(MODES.keys()))
        st.caption(f"Groq: {'ON ✅' if client else 'OFF ❌'} | Gemini Keys: {len(GEMINI_KEYS)} | HF: {'ON ✅' if HF_API_KEY else 'OFF ❌'}")
        if st.button("Clear Chat 🗑️"):
            st.session_state.messages = []
            st.rerun()

if page == "Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.markdown("© 2026 JARVIS AI | Created by Boss DEVIL | All data searched via Google CSE")
else:
    st.title("JARVIS AI - No More API Error 🤖")
    c1, c2 = st.columns(2)
    with c1: selected_model = st.selectbox("Model Change", MODEL_LIST, index=0, key="main_model")
    with c2: selected_mode_name = st.selectbox("Mode Change", list(MODES.keys()), key="main_mode")
    selected_prompt = MODES[selected_mode_name]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "image" in msg: st.image(msg["image"])
            st.markdown(msg["content"])

    if prompt := st.chat_input("Bolo Boss, kya chahiye?"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            q = prompt.lower()
            image_keywords = ["image", "photo", "picture", "draw", "banao", "generate", "poster", "logo", "wallpaper", "character", "xiao yan", "nie li"]
            is_image = any(w in q for w in image_keywords) or MODES[selected_mode_name] == "IMAGE_MODE"
            if is_image:
                with st.spinner("FLUX se bana raha hu Boss..."):
                    img = generate_flux_image(prompt)
                    if img:
                        st.image(img)
                        st.session_state.messages.append({"role":"assistant","content":f"✅ Image Generated: {prompt}", "image": img})
                    else:
                        st.error("Image nahi bani! HF_API_KEY Secrets me dalo!")
            else:
                with st.spinner("Jawab dhoond raha hu..."):
                    ans = get_text_answer(prompt, selected_model, selected_prompt)
                    render_with_preview(ans)
                    st.session_state.messages.append({"role":"assistant","content":ans})

st.markdown("""<div style="text-align:center; padding:10px; color:#888; font-size:12px;">© 2026 JARVIS AI | Groq First - No Error | Created by Boss DEVIL</div>""", unsafe_allow_html=True)
