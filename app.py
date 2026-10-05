# 1. IMPORT - Sab checked
import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse
import random
import re
import requests
import io
import time
import smtplib
from email.mime.text import MIMEText
from PIL import Image
import streamlit.components.v1 as components
import extra_streamlit_components as stx

# 2. PAGE CONFIG
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")
st.markdown("""
<style>
  .stDeployButton{display:none!important;}
    [data-testid="stToolbar"]{display:none!important;}
    footer{visibility:hidden!important;}
    #MainMenu{visibility:hidden!important;}
    div.block-container { padding-top: 2rem!important; }
    h1 { display: block!important; visibility: visible!important; margin-top: 0px!important; }
</style>
""", unsafe_allow_html=True)

# COOKIE MANAGER FOR LIFETIME LOGIN
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()

# 3. MODELS
GROQ_MODEL_NAME = "openai/gpt-oss-20b"
GEMINI_MODEL_NAME = "gemini-2.0-flash"
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
MODEL_LIST = ["JARVIS-GPT", "JARVIS-GEMINI", "JARVIS-FLUX"]

MODES = {
    "💬 Normal Chat (All in One)": "You are JARVIS AI, created by Boss DEVIL. Helpful and smart.",
    "Image Creating": "IMAGE_MODE",
    "Code Helper": "You are Code Expert. Provide clean code with preview.",
    "Math Solver": "You are Math Genius. Solve with steps.",
    "Study Helper": "You are Study Helper. Explain simply.",
    "Roast Mode": "You are Roast King - funny roasting.",
    "Story Writer": "You are Story Writer.",
}

# 4. SECRETS - SAFE LOADING
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = ""
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = ""
try:
    CX_ID = st.secrets["CX_ID"]
except:
    CX_ID = "e604ce9810cbf4ea4"
try:
    HF_API_KEY = st.secrets["HF_API_KEY"]
except:
    HF_API_KEY = ""
try:
    EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
except:
    EMAIL_ADDRESS = "jarvisapp.support@gmail.com"
try:
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    EMAIL_PASSWORD = EMAIL_PASSWORD.replace(" ", "")
except:
    EMAIL_PASSWORD = ""

GEMINI_KEYS = []
try:
    for k, v in st.secrets.items():
        if "GEMINI" in k.upper() and "KEY" in k.upper():
            if v and len(str(v)) > 20:
                GEMINI_KEYS.append(str(v).strip())
except:
    pass

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except:
        client = None

# 5. EMAIL OTP FUNCTION
def send_real_otp(to_email, otp):
    try:
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return False, "EMAIL_ADDRESS / EMAIL_PASSWORD Secrets me nahi hai"
        msg = MIMEText(f"Hello Boss,\n\nYour JARVIS OTP is: {otp}\n\nValid for 5 Minutes.\n\n- Team JARVIS")
        msg["Subject"] = f"JARVIS OTP - {otp}"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True, "Sent"
    except Exception as e:
        return False, str(e)

# 6. LOGIN SYSTEM - LIFETIME FIXED
time.sleep(0.5) # Cookie load fix
saved_auth = cookie_manager.get(cookie="jarvis_auth")
saved_email = cookie_manager.get(cookie="jarvis_email")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True if saved_auth == "true" else False
    if saved_email:
        st.session_state.email_try = saved_email

if not st.session_state.authenticated:
    st.title("🔐 JARVIS AI - Login")
    st.write(f"OTP yahan se jayega: {EMAIL_ADDRESS}")
    email = st.text_input("Gmail ID daalo:")

    if st.button("Send OTP"):
        if "@" not in email or "." not in email:
            st.error("Sahi Gmail daalo Boss!")
        else:
            otp = str(random.randint(100000, 999999))
            st.session_state.otp = otp
            st.session_state.email_try = email
            st.session_state.otp_time = time.time()
            with st.spinner(f"{email} pe OTP bhej raha hu..."):
                ok, err = send_real_otp(email, otp)
                if ok:
                    st.success(f"✅ OTP bhej diya! {email} ka Inbox / Spam check karo")
                else:
                    st.error(f"❌ Error: {err}")

    otp_input = st.text_input("6 Digit OTP:", type="password")
    if st.button("Verify & Login"):
        if "otp" not in st.session_state or st.session_state.otp is None:
            st.error("Pehle Send OTP dabao!")
        elif time.time() - st.session_state.get("otp_time", 0) > 300:
            st.error("OTP Expire ho gaya! Dubara bhejo!")
        elif otp_input == st.session_state.otp:
            # LIFETIME SAVE
            cookie_manager.set("jarvis_auth", "true", expires_at=time.time() + 365*24*60*60)
            cookie_manager.set("jarvis_email", st.session_state.email_try, expires_at=time.time() + 365*24*60*60)
            st.session_state.authenticated = True
            st.success("Login Success! Lifetime save ho gaya!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Galat OTP!")
    st.stop()

# 7. CORE FUNCTIONS
def google_custom_search(query):
    if not GOOGLE_API_KEY or not CX_ID:
        return ""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"q": query, "key": GOOGLE_API_KEY, "cx": CX_ID, "num": 3}
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        text = ""
        for item in data.get("items", []):
            text += f"{item.get('title','')} - {item.get('snippet','')} "
        return text[:1500]
    except:
        return ""

def get_text_answer(prompt, model_name, system_prompt):
    enhanced = google_custom_search(prompt)
    final_prompt = f"{system_prompt}\n\nWeb Info: {enhanced}\n\nUser: {prompt}\n\nAnswer in same language:"
    if client:
        try:
            res = client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": final_prompt}],
                temperature=0.7, max_tokens=2000
            )
            if res.choices[0].message.content:
                return res.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}")
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            resp = model.generate_content(final_prompt)
            if resp and hasattr(resp, "text") and resp.text:
                return resp.text
        except:
            continue
    if enhanced:
        return f"**Search Result:**\n\n{enhanced}"
    return "Boss API busy hai! 1 min baad try karo."

def generate_flux_image(prompt):
    enhanced = google_custom_search(f"{prompt} anime")
    lower = (enhanced + " " + prompt).lower()
    is_male = any(k in lower for k in ["xiao yan", "tang san", "male", "boy"])
    if is_male:
        final_prompt = f"{prompt}, 1boy, handsome male protagonist, short black hair, solo, ultra detailed anime, 8k"
        negative = "1girl, female, woman, breasts"
    else:
        final_prompt = f"{prompt}, beautiful detailed, ultra detailed anime, 8k, {enhanced[:200]}"
        negative = "ugly, deformed, blurry"
    if HF_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            r = requests.post(HF_API_URL, headers=headers, json={"inputs": final_prompt}, timeout=60)
            if r.status_code == 200:
                return Image.open(io.BytesIO(r.content))
        except:
            pass
    try:
        safe = urllib.parse.quote(final_prompt[:700])
        neg = urllib.parse.quote(negative)
        url = f"https://image.pollinations.ai/prompt/{safe}?model=flux-pro&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true&negative_prompt={neg}"
        r = requests.get(url, timeout=25)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content))
    except:
        pass
    return None

def render_with_preview(text):
    st.markdown(text)
    matches = re.findall(r"```(html|javascript|js|css)\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    for lang, code in matches:
        st.write(f"Preview ({lang}):")
        html_code = f"<script>{code}</script>" if lang.lower() in ["js", "javascript"] else code
        components.html(html_code, height=350, scrolling=True)

# 8. UI
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("JARVIS AI")
    st.success(f"Logged: {st.session_state.get('email_try','')}")
    if st.button("Logout"):
        cookie_manager.delete("jarvis_auth")
        cookie_manager.delete("jarvis_email")
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()
    st.divider()
    page = st.radio("Page", ["Chat", "Privacy Policy"])
    if page == "Chat":
        selected_model = st.selectbox("Model", MODEL_LIST, index=0)
        selected_mode_name = st.selectbox("Modes", list(MODES.keys()))
        st.caption(f"Groq: {'ON' if client else 'OFF'} | Gemini Keys: {len(GEMINI_KEYS)} | HF: {'ON' if HF_API_KEY else 'OFF'}")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if page == "Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.markdown(f"""
    Contact: {EMAIL_ADDRESS}
    CX_ID: {CX_ID}
    © 2026 JARVIS AI | Created by Boss DEVIL
    We do not sell data.
    Gmail is used only for OTP login.
    """)
else:
    st.title("JARVIS AI - 🤖")
    c1, c2 = st.columns(2)
    with c1:
        selected_model = st.selectbox("Model Change", MODEL_LIST, index=0, key="main_model")
    with c2:
        selected_mode_name = st.selectbox("Mode Change", list(MODES.keys()), key="main_mode")
    selected_prompt = MODES[selected_mode_name]
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "image" in msg:
                st.image(msg["image"])
            st.markdown(msg["content"])
    if prompt := st.chat_input("Bolo Boss, kya chahiye?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            q = prompt.lower()
            image_keywords = ["image", "photo", "picture", "draw", "banao", "generate", "poster", "logo", "wallpaper"]
            is_image = any(w in q for w in image_keywords) or MODES[selected_mode_name] == "IMAGE_MODE"
            if is_image:
                with st.spinner("FLUX se bana raha hu..."):
                    img = generate_flux_image(prompt)
                    if img:
                        st.image(img)
                        st.session_state.messages.append({"role": "assistant", "content": f"Image Generated: {prompt}", "image": img})
                    else:
                        st.error("Image nahi bani! HF_API_KEY check karo!")
            else:
                with st.spinner("Jawab dhoond raha hu..."):
                    ans = get_text_answer(prompt, selected_model, selected_prompt)
                    render_with_preview(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
    st.markdown('<div style="text-align:center; padding:10px; color:#888; font-size:12px;">© 2026 JARVIS AI | Created by Boss DEVIL</div>', unsafe_allow_html=True)
