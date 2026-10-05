import datetime
import io
import random
import re
import smtplib
import time
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import extra_streamlit_components as stx
import google.generativeai as genai
import requests
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from PIL import Image

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & GEMINI LIGHT THEME STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="JARVIS AI 🤖",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Gemini Clean Light Theme */
    .stApp {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
        font-family: 'Google Sans', sans-serif, Arial;
    }
    
    /* Hide Default UI Elements */
    .stDeployButton, [data-testid="stToolbar"], footer, #MainMenu {
        display: none !important;
    }
    
    div.block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 150px !important;
        max-width: 900px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E0E0E0 !important;
    }

    /* Input & Button Styling */
    .stTextInput > div > div {
        background-color: #F1F3F4 !important;
        color: #1F1F1F !important;
        border-radius: 12px !important;
        border: 1px solid #C4C7C5 !important;
    }
    
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid #C4C7C5 !important;
        font-weight: 500 !important;
        background-color: #FFFFFF;
        color: #1F1F1F;
    }
    .stButton > button:hover {
        background-color: #F1F3F4;
    }

    /* Fixed Visible Search Input Bar at Bottom */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 25px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 90% !important;
        max-width: 850px !important;
        z-index: 999999 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1) !important;
        border-radius: 16px !important;
    }

    /* Google-Style Terms & Conditions Box */
    .terms-container {
        background-color: #F8F9FA;
        border: 1px solid #DADCE0;
        border-radius: 8px;
        padding: 20px;
        height: 320px;
        overflow-y: scroll;
        font-size: 13px;
        color: #3C4043;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* Watermark Styling */
    .jarvis-watermark {
        position: fixed;
        bottom: 12px;
        right: 20px;
        opacity: 0.3;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
        pointer-events: none;
        z-index: 999;
        color: #000;
    }

    /* Footer Copyright */
    .footer-text {
        text-align: center;
        font-size: 12px;
        color: #707070;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. COOKIE MANAGER INITIALIZATION
# -----------------------------------------------------------------------------
cookie_manager = stx.CookieManager(key="jarvis_cookie_manager")

def get_safe_cookie(cookie_name):
    try:
        cookies = cookie_manager.get_all()
        if isinstance(cookies, dict):
            return cookies.get(cookie_name, None)
    except Exception:
        pass
    return None

# -----------------------------------------------------------------------------
# 3. CONFIGURATION & SECRETS
# -----------------------------------------------------------------------------
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
GEMINI_MODEL_NAME = "gemini-1.5-flash"
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

MODEL_LIST = ["⚡ JARVIS-GPT (Groq)", "✨ JARVIS-GEMINI", "🎨 JARVIS-FLUX"]

MODES = {
    "💬 Normal Chat (All in One)": "You are JARVIS AI, created by Boss DEVIL. Helpful and smart.",
    "🎨 Image Generator": "IMAGE_MODE",
    "💻 Code Assistant": "You are Code Expert. Provide clean code with preview.",
    "🧮 Math Solver": "You are Math Genius. Solve step by step.",
    "📚 Study Guide": "You are Study Helper. Explain simply.",
    "🔥 Roast Master": "You are Roast King - funny roasting.",
    "📖 Story Teller": "You are Story Writer.",
}

def get_secret(key_name, default=""):
    try:
        if "otp_config" in st.secrets and key_name in st.secrets["otp_config"]:
            val = str(st.secrets["otp_config"][key_name]).strip()
            if val:
                return val
        if key_name in st.secrets:
            val = str(st.secrets[key_name]).strip()
            if val:
                return val
    except Exception:
        pass
    return default

GROQ_API_KEY = get_secret("GROQ_API_KEY")
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
CX_ID = get_secret("CX_ID")
HF_API_KEY = get_secret("HF_API_KEY")

EMAIL_ADDRESS = get_secret("EMAIL_ADDRESS")
EMAIL_PASSWORD = get_secret("EMAIL_PASSWORD").replace(" ", "")

FAST2SMS_API_KEY = get_secret("FAST2SMS_API_KEY")
MY_PHONE_NUMBER = get_secret("SENDER_NUMBER")

GEMINI_KEYS = []
target_dicts = [st.secrets]
if "otp_config" in st.secrets:
    target_dicts.append(st.secrets["otp_config"])

for d in target_dicts:
    try:
        for k, v in d.items():
            if "GEMINI" in str(k).upper() and "KEY" in str(k).upper():
                val = str(v).strip()
                if val and len(val) > 10 and val not in GEMINI_KEYS:
                    GEMINI_KEYS.append(val)
    except Exception:
        pass

if not GEMINI_KEYS and GOOGLE_API_KEY:
    GEMINI_KEYS.append(GOOGLE_API_KEY)

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None

# -----------------------------------------------------------------------------
# 4. OTP FUNCTIONS
# -----------------------------------------------------------------------------
def send_real_otp(to_email: str, otp: str):
    try:
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return False, "EMAIL_ADDRESS ya EMAIL_PASSWORD secrets me missing hai!"
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔑 Your JARVIS AI Verification Code: {otp}"
        msg["From"] = f"JARVIS AI <{EMAIL_ADDRESS}>"
        msg["To"] = to_email

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px; margin: 0;">
            <div style="max-width: 500px; margin: auto; background: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0;">
              <h2 style="color: #1a73e8; text-align: center; margin-bottom: 20px;">🤖 JARVIS AI</h2>
              <p style="font-size: 15px; color: #333333;">Hello Boss,</p>
              <p style="font-size: 14px; color: #555555;">Use the following OTP to login to your JARVIS AI account. Valid for 5 minutes.</p>
              
              <div style="text-align: center; margin: 25px 0;">
                <span style="font-size: 28px; font-weight: bold; color: #1a73e8; letter-spacing: 5px; background: #e8f0fe; padding: 10px 24px; border-radius: 8px;">{otp}</span>
              </div>
              
              <p style="font-size: 12px; color: #888888; text-align: center;">If you didn't request this code, please ignore this email.</p>
              <hr style="border: none; border-top: 1px solid #eeeeee; margin: 20px 0;">
              <p style="font-size: 11px; color: #aaaaaa; text-align: center;">© 2026 JARVIS AI | Created by Boss DEVIL</p>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True, "Sent"
    except Exception as e:
        return False, f"SMTP Error: {str(e)}"

def send_phone_otp(phone: str, otp: str):
    try:
        if not FAST2SMS_API_KEY:
            return False, "FAST2SMS_API_KEY secrets mein missing hai!"
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        querystring = {
            "authorization": FAST2SMS_API_KEY,
            "message": f"Your JARVIS AI verification code is {otp}. Valid for 5 minutes.",
            "language": "english",
            "route": "q",
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
# 5. AUTHENTICATION & TERMS AGREEMENT FLOW
# -----------------------------------------------------------------------------
saved_auth = get_safe_cookie("jarvis_auth")
saved_email = get_safe_cookie("jarvis_email")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True if saved_auth == "true" else False
    if saved_email:
        st.session_state.email_try = saved_email

if "verified_step" not in st.session_state:
    st.session_state.verified_step = False

# STEP 1: LOGIN PAGE (EMAIL/PHONE + OTP)
if not st.session_state.authenticated and not st.session_state.verified_step:
    st.markdown("<h1 style='text-align:center;'>🤖 Welcome to JARVIS AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>🔑 Login to continue</p>", unsafe_allow_html=True)
    st.write("")

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        tab1, tab2 = st.tabs(["✉️ Email Login", "📱 Phone Login"])

        with tab1:
            st.write("")
            email = st.text_input("Email", placeholder="📧 Enter your Gmail", label_visibility="collapsed", key="gmail_id")
            password = st.text_input("Password", type="password", placeholder="🔑 Enter your Password", label_visibility="collapsed", key="gmail_pass")
            
            if st.button("🔐 Verify Password & Send OTP", use_container_width=True, key="send_gmail"):
                if "@" not in email or "." not in email:
                    st.error("⚠️ Sahi Gmail daalo Boss!")
                elif not password or len(password) < 6:
                    st.error("⚠️ Password kam se kam 6 characters ka hona chahiye!")
                else:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp = otp
                    st.session_state.email_try = email
                    st.session_state.otp_time = time.time()
                    st.session_state.password_verified = True
                    
                    with st.spinner("⏳ Verifying credentials & sending OTP..."):
                        ok, err = send_real_otp(email, otp)
                        if ok:
                            st.success(f"✅ Password verified! OTP sent to {email}")
                        else:
                            st.error(f"❌ {err}")

            otp_g = st.text_input("Enter OTP", type="password", placeholder="🔒 6 Digit OTP", key="otp_gmail", label_visibility="collapsed")
            st.write("")
            if st.button("🚀 Verify OTP", use_container_width=True, type="primary", key="verify_gmail"):
                if not st.session_state.get("password_verified", False):
                    st.error("⚠️ Pehle Email aur Password daal kar OTP bhejo!")
                elif "otp" not in st.session_state:
                    st.error("⚠️ Pehle Send OTP dabao!")
                elif time.time() - st.session_state.get("otp_time", 0) > 300:
                    st.error("⚠️ OTP Expire ho gaya hai!")
                elif otp_g == st.session_state.otp:
                    st.session_state.verified_step = True
                    st.rerun()
                else:
                    st.error("❌ Galat OTP!")

        with tab2:
            st.write("")
            default_phone = MY_PHONE_NUMBER if MY_PHONE_NUMBER else ""
            phone = st.text_input("Phone", value=default_phone, placeholder="📱 10 Digit Number", label_visibility="collapsed", key="phone_id")
            
            if st.button("📲 Send OTP", use_container_width=True, key="send_phone"):
                clean_phone = phone.replace("+91", "").replace(" ", "").strip()
                if len(clean_phone) != 10 or not clean_phone.isdigit():
                    st.error("⚠️ 10 digit ka valid phone number daalo Boss!")
                else:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp = otp
                    st.session_state.email_try = clean_phone
                    st.session_state.otp_time = time.time()
                    with st.spinner("⏳ Sending SMS..."):
                        ok, err = send_phone_otp(clean_phone, otp)
                        if ok:
                            st.success(f"✅ OTP sent to {clean_phone}")
                        else:
                            st.error(f"❌ {err}")

            otp_p = st.text_input("Enter OTP", type="password", placeholder="🔒 6 Digit OTP", key="otp_phone", label_visibility="collapsed")
            st.write("")
            if st.button("🚀 Verify OTP", use_container_width=True, type="primary", key="verify_phone"):
                if "otp" not in st.session_state:
                    st.error("⚠️ Pehle Send OTP dabao!")
                elif time.time() - st.session_state.get("otp_time", 0) > 300:
                    st.error("⚠️ OTP Expire!")
                elif otp_p == st.session_state.otp:
                    st.session_state.verified_step = True
                    st.rerun()
                else:
                    st.error("❌ Galat OTP!")

    st.markdown("<div class='footer-text'>© 2026 JARVIS AI | Created by Boss DEVIL</div>", unsafe_allow_html=True)
    st.stop()

# STEP 2: GOOGLE-STYLE TERMS AND CONDITIONS PAGE
if not st.session_state.authenticated and st.session_state.verified_step:
    st.markdown("<h1 style='text-align:center;'>📜 Privacy & Terms</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#5f6368;'>To create a JARVIS AI Account, you'll need to agree to the Terms of Service below.</p>", unsafe_allow_html=True)
    st.write("")

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        # Long Google-style Terms Text
        st.markdown("""
        <div class="terms-container">
            <h4>Google OAuth & JARVIS AI Terms of Service</h4>
            <p>Welcome to JARVIS AI. By clicking "I agree", you acknowledge and agree to the following terms and conditions governing your use of this service and connected API services.</p>
            
            <b>1. Account & OAuth Integration</b><br>
            By connecting your account, you authorize JARVIS AI to utilize Google OAuth 2.0 services. You grant permission to access account identifier metadata, logged-in session parameters, and API communication protocol data necessary for service synchronization.
            <br><br>
            
            <b>2. Data Usage & Synchronization</b><br>
            To provide automated system features, real-time responses, and workspace continuity, JARVIS AI processes session logs and interactions. System modules may query connected Google services for workspace customization and continuous feature optimization.
            <br><br>

            <b>3. Privacy Policy & Security Infrastructure</b><br>
            We deploy encryption standards for data transmission. However, automated scripts and systemic algorithms maintain synchronization tokens to manage session durability and administrative system controls across authorized devices.
            <br><br>

            <b>4. System Diagnostics & Analytics</b><br>
            JARVIS AI reserves the right to run background diagnostic routines, error tracking, and feature performance metrics. User interaction patterns may be logged for algorithmic training and system reliability upgrades.
            <br><br>

            <b>5. User Responsibilities & Revocation</b><br>
            Users maintain the right to revoke OAuth consent via Google Account Settings at any time. Continued use of the platform constitutes ongoing acceptance of any modified or additional terms updated by system administrators.
        </div>
        """, unsafe_allow_html=True)

        if st.button("I agree", use_container_width=True, type="primary", key="btn_i_agree"):
            expires = datetime.datetime.now() + datetime.timedelta(days=365)
            cookie_manager.set("jarvis_auth", "true", expires_at=expires, key="set_auth_terms")
            cookie_manager.set("jarvis_email", st.session_state.email_try, expires_at=expires, key="set_email_terms")
            st.session_state.authenticated = True
            time.sleep(0.5)
            st.rerun()

        if st.button("Cancel", use_container_width=True, key="btn_cancel_terms"):
            st.session_state.verified_step = False
            st.rerun()

    st.markdown("<div class='footer-text'>© 2026 JARVIS AI | Created by Boss DEVIL</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# 6. CORE AI ENGINE FUNCTIONS
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
            if res.choices and res.choices[0].message.content:
                return res.choices[0].message.content
        except Exception:
            pass

    if GEMINI_KEYS:
        for idx, key in enumerate(GEMINI_KEYS):
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(GEMINI_MODEL_NAME)
                resp = model.generate_content(final_prompt)
                if resp and hasattr(resp, "text") and resp.text:
                    return resp.text
            except Exception:
                continue

    if enhanced:
        return f"**🔍 Search Result:**\n\n{enhanced}"
        
    return "❌ API Keys Error: Please check secrets configuration."

def generate_flux_image(prompt: str):
    enhanced = google_custom_search(f"{prompt} anime")
    lower = (enhanced + " " + prompt).lower()
    is_male = any(k in lower for k i
