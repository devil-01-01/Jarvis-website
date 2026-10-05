import datetime
import io
import random
import re
import smtplib
import time
import urllib.parse
from email.mime.text import MIMEText

import extra_streamlit_components as stx
import google.generativeai as genai
import requests
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from PIL import Image

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & GEMINI STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="JARVIS AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Gemini Dark Theme Styling */
    .stApp {
        background-color: #131314;
        color: #E3E2E6;
    }
    
    /* Hide Unnecessary Streamlit UI Elements */
    .stDeployButton, [data-testid="stToolbar"], footer, #MainMenu {
        display: none !important;
    }
    
    div.block-container {
        padding-top: 2rem !important;
        max-width: 900px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20 !important;
        border-right: 1px solid #2F3033;
    }

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {
        gap: 8px;
        background: #1E1F20;
        padding: 6px;
        border-radius: 30px;
        width: fit-content;
        margin: auto;
        border: 1px solid #2F3033;
    }
    div[data-baseweb="tab"] {
        border-radius: 20px !important;
        padding: 8px 24px !important;
        background: transparent !important;
        color: #C4C6C5 !important;
        border: none !important;
        font-weight: 500;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
        background: #2F3033 !important;
        color: #E3E2E6 !important;
    }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div {
        background-color: #1E1F20 !important;
        color: #E3E2E6 !important;
        border-radius: 12px !important;
        border: 1px solid #444746 !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 20px !important;
        border: none !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. COOKIE MANAGER INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager(key="jarvis_cookie_manager")

cookie_manager = get_cookie_manager()

# -----------------------------------------------------------------------------
# 3. CONFIGURATION & CONSTANTS
# -----------------------------------------------------------------------------
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
GEMINI_MODEL_NAME = "gemini-2.0-flash"
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

MODEL_LIST = ["JARVIS-GPT (Groq)", "JARVIS-GEMINI", "JARVIS-FLUX"]
MODES = {
    "💬 Normal Chat (All in One)": "You are JARVIS AI, created by Boss DEVIL. Helpful and smart.",
    "🎨 Image Creating": "IMAGE_MODE",
    "💻 Code Helper": "You are Code Expert. Provide clean code with preview.",
    "🧮 Math Solver": "You are Math Genius. Solve with steps.",
    "📚 Study Helper": "You are Study Helper. Explain simply.",
    "🔥 Roast Mode": "You are Roast King - funny roasting.",
    "📖 Story Writer": "You are Story Writer.",
}

# -----------------------------------------------------------------------------
# 4. SECRETS INITIALIZATION
# -----------------------------------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
CX_ID = st.secrets.get("CX_ID", "e604ce9810cbf4ea4")
HF_API_KEY = st.secrets.get("HF_API_KEY", "")
EMAIL_ADDRESS = st.secrets.get("EMAIL_ADDRESS", "jarvisapp.support@gmail.com")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "").replace(" ", "")
FAST2SMS_API_KEY = st.secrets.get("FAST2SMS_API_KEY", "")
MY_PHONE_NUMBER = str(st.secrets.get("MY_PHONE_NUMBER", "")).strip()

GEMINI_KEYS = []
try:
    for k, v in st.secrets.items():
        if "GEMINI" in k.upper() and "KEY" in k.upper():
            if v and len(str(v)) > 20:
                GEMINI_KEYS.append(str(v).strip())
except Exception:
    pass

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None

# -----------------------------------------------------------------------------
# 5. OTP FUNCTIONS
# -----------------------------------------------------------------------------
def send_real_otp(to_email: str, otp: str):
    try:
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return False, "EMAIL secrets missing!"
        msg = MIMEText(f"Hello Boss,\n\nYour JARVIS OTP is: {otp}\nValid for 5 Minutes.\n\n- Team JARVIS")
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

def send_phone_otp(phone: str, otp: str):
    try:
        if not FAST2SMS_API_KEY:
            return False, "FAST2SMS_API_KEY secrets mein missing hai!"
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        querystring = {
            "authorization": FAST2SMS_API_KEY,
            "variables_values": otp,
            "route": "otp",
            "numbers": phone
        }
        
        r = requests.get(url, params=querystring, timeout=15)
        res_data = r.json()
        
        if res_data.get("return") == True:
            return True, "OTP Safaltapoorvak bhej diya gaya!"
        else:
            return False, res_data.get("message", "SMS Send failed")
    except Exception as e:
        return False, str(e)

# -----------------------------------------------------------------------------
# 6. LOGIN / AUTHENTICATION SYSTEM
# -----------------------------------------------------------------------------
time.sleep(0.2)
saved_auth = cookie_manager.get(cookie="jarvis_auth")
saved_email = cookie_manager.get(cookie="jarvis_email")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True if saved_auth == "true" else False
    if saved_email:
        st.session_state.email_try = saved_email

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center;'>🔐 Welcome to JARVIS AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Login to continue</p>", unsafe_allow_html=True)
    st.write("")

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        tab1, tab2 = st.tabs(["✉️ Email", "📱 Phone"])

        with tab1:
            st.write("")
            st.caption(f"OTP will be sent from {EMAIL_ADDRESS}")
            email = st.text_input("Email", placeholder="Enter your Gmail", label_visibility="collapsed", key="gmail_id")
            if st.button("Send OTP", use_container_width=True, key="send_gmail"):
                if "@" not in email or "." not in email:
                    st.error("Sahi Gmail daalo Boss!")
                else:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp = otp
                    st.session_state.email_try = email
                    st.session_state.otp_time = time.time()
                    with st.spinner("Sending..."):
                        ok, err = send_real_otp(email, otp)
                        st.success(f"✅ OTP sent to {email}") if ok else st.error(f"❌ {err}")

            otp_g = st.text_input("Enter OTP", type="password", placeholder="6 Digit OTP", key="otp_gmail", label_visibility="collapsed")
            st.write("")
            if st.button("Verify & Continue", use_container_width=True, type="primary", key="verify_gmail"):
                if "otp" not in st.session_state:
                    st.error("Pehle Send OTP dabao!")
                elif time.time() - st.session_state.get("otp_time", 0) > 300:
                    st.error("OTP Expire!")
                elif otp_g == st.session_state.otp:
                    expires = datetime.datetime.now() + datetime.timedelta(days=365)
                    cookie_manager.set("jarvis_auth", "true", expires_at=expires)
                    cookie_manager.set("jarvis_email", st.session_state.email_try, expires_at=expires)
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Galat OTP!")

        with tab2:
            st.write("")
            st.caption("OTP via Fast2SMS Service")
            default_phone = MY_PHONE_NUMBER if MY_PHONE_NUMBER else ""
            phone = st.text_input("Phone", value=default_phone, placeholder="10 Digit Number", label_visibility="collapsed", key="phone_id")
            
            if st.button("Send OTP", use_container_width=True, key="send_phone"):
                clean_phone = phone.replace("+91", "").replace(" ", "").strip()
                if len(clean_phone) != 10 or not clean_phone.isdigit():
                    st.error("10 digit ka valid phone number daalo Boss!")
                else:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp = otp
                    st.session_state.email_try = clean_phone
                    st.session_state.otp_time = time.time()
                    with st.spinner("Sending SMS..."):
                        ok, err = send_phone_otp(clean_phone, otp)
                        st.success(f"✅ OTP sent to {clean_phone}") if ok else st.error(f"❌ {err}")

            otp_p = st.text_input("Enter OTP", type="password", placeholder="6 Digit OTP", key="otp_phone", label_visibility="collapsed")
            st.write("")
            if st.button("Verify & Continue", use_container_width=True, type="primary", key="verify_phone"):
                if "otp" not in st.session_state:
                    st.error("Pehle Send OTP dabao!")
                elif time.time() - st.session_state.get("otp_time", 0) > 300:
                    st.error("OTP Expire!")
                elif otp_p == st.session_state.otp:
                    expires = datetime.datetime.now() + datetime.timedelta(days=365)
                    cookie_manager.set("jarvis_auth", "true", expires_at=expires)
                    cookie_manager.set("jarvis_email", st.session_state.email_try, expires_at=expires)
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Galat OTP!")
    st.stop()

# -----------------------------------------------------------------------------
# 7. CORE AI FUNCTIONS
# -----------------------------------------------------------------------------
def google_custom_search(query: str) -> str:
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
    except Exception:
        return ""

def get_text_answer(prompt: str, selected_model: str, system_prompt: str) -> str:
    enhanced = google_custom_search(prompt)
    final_prompt = f"{system_prompt}\n\nWeb Info: {enhanced}\n\nUser: {prompt}\nAnswer in same language:"
    
    if "Groq" in selected_model and client:
        try:
            res = client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": final_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            if res.choices[0].message.content:
                return res.choices[0].message.content
        except Exception:
            pass

    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            resp = model.generate_content(final_prompt)
            if resp and hasattr(resp, "text") and resp.text:
                return resp.text
        except Exception:
            continue

    if enhanced:
        return f"**Search Result:**\n\n{enhanced}"
    return "Boss API busy hai! 1 min baad try karo."

def generate_flux_image(prompt: str):
    enhanced = google_custom_search(f"{prompt} anime")
    lower = (enhanced + " " + prompt).lower()
    is_male = any(k in lower for k in ["xiao yan", "tang san", "male", "boy"])
    final_prompt = f"{prompt}, 1boy, handsome male" if is_male else f"{prompt}, ultra detailed anime, 8k, {enhanced[:200]}"
    negative = "1girl" if is_male else "ugly, blurry"
    
    if HF_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            r = requests.post(HF_API_URL, headers=headers, json={"inputs": final_prompt}, timeout=60)
            if r.status_code == 200:
                return Image.open(io.BytesIO(r.content))
        except Exception:
            pass

    try:
        safe = urllib.parse.quote(final_prompt[:700])
        neg = urllib.parse.quote(negative)
        url = f"https://image.pollinations.ai/prompt/{safe}?model=flux-pro&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true&negative_prompt={neg}"
        r = requests.get(url, timeout=25)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content))
    except Exception:
        pass
    return None

def render_with_preview(text: str):
    st.markdown(text)
    matches = re.findall(r"```(html|javascript|js|css)\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    for lang, code in matches:
        with st.expander(f"✨ Live Preview ({lang.upper()})", expanded=True):
            html_code = f"<script>{code}</script>" if lang.lower() in ["js", "javascript"] else code
            components.html(html_code, height=350, scrolling=True)

# -----------------------------------------------------------------------------
# 8. MAIN UI & CHAT SYSTEM
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🤖 JARVIS AI")
    st.success(f"Logged in: {st.session_state.get('email_try','')}")
    if st.button("Logout", use_container_width=True):
        cookie_manager.delete("jarvis_auth")
        cookie_manager.delete("jarvis_email")
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()
    st.divider()
    page = st.radio("Page", ["Chat", "Privacy Policy"], label_visibility="collapsed")
    if page == "Chat":
        selected_model = st.selectbox("Model Engine", MODEL_LIST, index=0, key="sb_model")
        selected_mode_name = st.selectbox("Assistant Persona", list(MODES.keys()), key="sb_mode")
        st.caption(f"Groq API: {'🟢 ON' if client else '🔴 OFF'} | Gemini Keys: {len(GEMINI_KEYS)}")
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

if page == "Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.markdown(f"Contact: {EMAIL_ADDRESS}\n\n© 2026 JARVIS AI | Created by Boss DEVIL")
else:
    st.title("JARVIS AI - 🤖")
    
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
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Image Generated: {prompt}",
                            "image": img
                        })
                    else:
                        st.error("Image nahi bani!")
            else:
                with st.spinner("Jawab dhoond raha hu..."):
                    ans = get_text_answer(prompt, selected_model, selected_prompt)
                    render_with_preview(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
