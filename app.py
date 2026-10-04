# 1. IMPORT
import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, re, requests, io, json, os
from PIL import Image
from datetime import datetime
import streamlit.components.v1 as components

# 2. PAGE CONFIG
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")
st.markdown("""
<style>
   .stDeployButton{display:none!important;}
    [data-testid="stToolbar"]{display:none!important;}
    footer{visibility:hidden!important;}
    #MainMenu{visibility:hidden!important;}
    div.block-container{padding-top: 1rem!important;}
    [data-testid="stChatInput"]{border-radius:28px!important; box-shadow:0 4px 15px rgba(0,0,0,0.1)!important;}
    [data-testid="stChatInput"] textarea{height:56px!important; font-size:17px!important; padding-top:16px!important;}
</style>
""", unsafe_allow_html=True)

# 3. LOGIN SYSTEM - BINA LOGIN APP LOCK
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "history" not in st.session_state:
    st.session_state.history = []

# AGAR LOGIN NAHI HAI TO YAHI RUK JAO
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🔐 JARVIS AI - Login Required</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Bina Login ke app kaam nahi karega Boss!</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📧 Google Login", "📱 Phone Login"])

    with tab1:
        st.write("### Google se Login")
        email = st.text_input("Email daalo (Google wala)", placeholder="boss@gmail.com")
        if st.button("✅ Continue with Google", use_container_width=True, type="primary"):
            if "@gmail.com" in email or "@" in email:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success(f"Welcome {email}!")
                st.rerun()
            else:
                st.error("Sahi Email daalo Boss!")

    with tab2:
        st.write("### Phone Number se Login")
        phone = st.text_input("Phone Number", placeholder="+91 9876543210")
        otp = st.text_input("OTP (Demo ke liye 1234 daalo)", type="password")
        if st.button("📱 Login with Phone", use_container_width=True):
            if len(phone) >= 10 and otp == "1234":
                st.session_state.logged_in = True
                st.session_state.user_email = phone
                st.success(f"Welcome {phone}!")
                st.rerun()
            else:
                st.error("Phone 10 digit aur OTP 1234 daalo (Demo)")

    st.stop() # YAHAN APP RUK JAYEGA - AAGE NAHI JAYEGA

# 4. MODELS
GROQ_MODEL_NAME = "openai/gpt-oss-20b"
GEMINI_MODEL_NAME = "gemini-1.5-flash"
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
MODEL_LIST = ["JARVIS-GPT", "JARVIS-GEMINI", "JARVIS-FLUX"]
MODES = {
    "💬 Normal Chat": "You are JARVIS AI, created by Boss DEVIL.",
    "Image Creating": "IMAGE_MODE",
    "Code Helper": "You are Code Expert.",
    "Math Solver": "You are Math Genius.",
    "Study Helper": "You are Study Helper.",
}

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
        if "GEMINI" in k.upper() and "KEY" in k.upper() and len(str(v))>20:
            GEMINI_KEYS.append(str(v).strip())
except: pass

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def google_custom_search(query):
    if not GOOGLE_API_KEY or not CX_ID: return ""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        r = requests.get(url, params={'q': query, 'key': GOOGLE_API_KEY, 'cx': CX_ID, 'num': 3}, timeout=8)
        return " ".join([f"{i.get('title','')} - {i.get('snippet','')}" for i in r.json().get('items', [])])[:1500]
    except: return ""

def get_text_answer(prompt, system_prompt):
    enhanced = google_custom_search(prompt)
    final_prompt = f"{system_prompt}\nWeb Info: {enhanced}\nQuestion: {prompt}"
    if client:
        try:
            res = client.chat.completions.create(model=GROQ_MODEL_NAME, messages=[{"role":"system","content":system_prompt},{"role":"user","content":final_prompt}], max_tokens=2000)
            if res.choices[0].message.content: return res.choices[0].message.content
        except: pass
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            resp = genai.GenerativeModel(GEMINI_MODEL_NAME).generate_content(final_prompt)
            if resp.text: return resp.text
        except: continue
    return enhanced or "API busy, try again!"

def generate_flux_image(prompt):
    try:
        safe = urllib.parse.quote(prompt[:700])
        url = f"https://image.pollinations.ai/prompt/{safe}?model=flux-pro&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true"
        r = requests.get(url, timeout=25)
        if r.status_code == 200: return Image.open(io.BytesIO(r.content))
    except: pass
    return None

# 5. TOP BAR + HISTORY + LOGOUT
top1, top2, top3 = st.columns([3,1,1])
with top1: st.markdown(f"<h3 style='margin:0;'>JARVIS AI 🤖</h3><small style='color:gray;'>Logged in: {st.session_state.user_email}</small>", unsafe_allow_html=True)
with top2:
    if st.button("📜 History"):
        st.session_state.show_history = not st.session_state.get("show_history", False)
with top3:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.messages = []
        st.rerun()

# History Drawer
if st.session_state.get("show_history", False):
    st.info(f"📜 Total Chats: {len(st.session_state.get('messages', []))}")
    for i, msg in enumerate(st.session_state.get('messages', [])[-10:]): # Last 10
        st.caption(f"{msg['role']}: {msg['content'][:80]}...")
    if st.button("Clear History 🗑️"):
        st.session_state.messages = []
        st.rerun()
    st.divider()

if "messages" not in st.session_state: st.session_state.messages = []

# 6. MAIN CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image" in msg: st.image(msg["image"])
        st.markdown(msg["content"])

col1, col2 = st.columns(2)
with col1: selected_model = st.selectbox("Model", MODEL_LIST, label_visibility="collapsed")
with col2: selected_mode_name = st.selectbox("Mode", list(MODES.keys()), label_visibility="collapsed")
selected_prompt = MODES[selected_mode_name]

if prompt := st.chat_input("Bolo Boss, kya chahiye? ✨"):
    st.session_state.messages.append({"role":"user","content":prompt, "time": str(datetime.now())})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        if "image" in prompt.lower() or selected_prompt == "IMAGE_MODE":
            img = generate_flux_image(prompt)
            if img:
                st.image(img)
                st.session_state.messages.append({"role":"assistant","content":f"Image: {prompt}", "image": img})
        else:
            ans = get_text_answer(prompt, selected_prompt)
            st.markdown(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})

      if page == "Privacy Policy":
    st.title("🔒 Privacy Policy - JARVIS AI")
    st.caption("Last Updated: 4 Oct 2026 | Created by Boss DEVIL")

    st.markdown("""
    ### 1. Introduction
    Welcome to JARVIS AI. Your privacy is very important to us. This policy explains what data we collect when you use Google Login or Phone Login.

    ### 2. Data We Collect
    **a) Google Login:** Jab aap Google se login karte ho, hum sirf aapka Email ID collect karte hain login ke liye. Password hum kabhi nahi lete.
    
    **b) Phone Number Login:** Phone login me aapka phone number sirf OTP verification ke liye use hota hai. Hum isko kisi ko share nahi karte.

    **c) Chat History:** Aapki chat history aapke browser me save hoti hai (session storage). Hum aapki chat ko server par permanently store nahi karte. Clear History dabate hi sab delete ho jata hai.

    **d) Images:** Aap jo image generate karte ho, wo Pollination / HuggingFace API se banti hai. Hum usko store nahi karte.

    ### 3. Third-Party APIs
    Hum ye services use karte hain:
    - **Groq AI** for fast chat answers
    - **Google Gemini** for search + answer
    - **Google Custom Search (CSE)** for web search
    - **HuggingFace FLUX** for image generation
    
    Inka data unki apni privacy policy ke hisab se handle hota hai.

    ### 4. Shaadi / Personal Data
    Agar aap shaadi ya personal life ke baare me kuch puchte ho, to wo data bhi private hi rehta hai. Hum aapki personal baatein kisi AI ko train karne ke liye use nahi karte.

    ### 5. Security
    Bina login ke app kaam nahi karega. Iska matlab aapka data dusra koi nahi dekh sakta.

    ### 6. Contact
    Koi bhi sawal ho to: **devil.boss.jarvis@gmail.com**

    ---
    **© 2026 JARVIS AI | All Rights Reserved | Created by Boss DEVIL**
    """)
