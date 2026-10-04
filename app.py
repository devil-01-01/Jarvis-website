import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, requests, io
from PIL import Image

st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# --- 1. CSS - KEYBOARD FIX + GEMINI UI ---
st.markdown("""
<style>
.stDeployButton{display:none!important;}
footer{visibility:hidden!important;}
#MainMenu{visibility:hidden!important;}
header{visibility:hidden!important;}
div.block-container{padding-top:0.5rem!important; padding-bottom:110px!important;}

/* SEARCH BAR KEYBOARD KE UPAR CHIPKEGA - MAIN FIX */
[data-testid="stChatInput"] {
    position: fixed!important;
    bottom: 15px!important;
    left: 50%!important;
    transform: translateX(-50%)!important;
    width: 95%!important;
    max-width: 720px!important;
    z-index: 999999!important;
    background: white!important;
    border-radius: 28px!important;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.15)!important;
}
[data-testid="stChatInput"] textarea{
    height:54px!important;
    font-size:16px!important;
}

/* Mobile pe aur perfect */
@media (max-width: 768px) {
    [data-testid="stChatInput"] {
        bottom: 8px!important;
        width: 92%!important;
    }
    div.block-container{padding-bottom:120px!important;}
}

/* LOGIN CSS */
.gemini-login-container {display:flex; flex-direction:column; align-items:center; text-align:center; margin-top:25px;}
.gemini-logo {width:62px; height:62px; background:linear-gradient(135deg, #4285f4, #9c27b0, #fbbc04); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:32px; color:white; margin:0 auto 12px auto;}
.divider {display:flex; align-items:center; max-width:320px; width:100%; margin:14px auto; color:#70757a; font-size:13px;}
.divider::before,.divider::after {content:""; flex:1; height:1px; background:#dadce0;}
.divider span {padding:0 10px;}
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION ---
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_email" not in st.session_state: st.session_state.user_email=""
if "messages" not in st.session_state: st.session_state.messages=[]
if "show_google_input" not in st.session_state: st.session_state.show_google_input=False
if "show_phone_input" not in st.session_state: st.session_state.show_phone_input=False

# --- 3. GEMINI JAISA LOGIN PAGE ---
if not st.session_state.logged_in:
    st.markdown("""
    <div class="gemini-login-container">
        <div class="gemini-logo">✦</div>
        <h2 style="font-weight:400; margin:0;">Welcome to JARVIS AI</h2>
        <p style="color:#5f6368; font-size:14px; margin-top:6px;">Your personal AI assistant by Boss DEVIL</p>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1,2,1])[1]
    with col:
        st.markdown("<p style='text-align:center; font-size:14px; font-weight:500; margin-top:15px;'>Sign in to continue</p>", unsafe_allow_html=True)

        if st.button(" Continue with Google", use_container_width=True):
            st.session_state.show_google_input=True
            st.session_state.show_phone_input=False

        if st.session_state.show_google_input:
            email = st.text_input("Email", placeholder="ayr86068@gmail.com", label_visibility="collapsed", key="g_email")
            if st.button("Continue →", type="primary", use_container_width=True, key="g_cont"):
                if "@" in email:
                    st.session_state.logged_in=True
                    st.session_state.user_email=email
                    st.rerun()
                else:
                    st.error("Sahi Gmail daalo Boss!")

        st.markdown('<div class="divider"><span>or</span></div>', unsafe_allow_html=True)

        if st.button(" Continue with Phone 📱", use_container_width=True):
            st.session_state.show_phone_input=True
            st.session_state.show_google_input=False

        if st.session_state.show_phone_input:
            phone = st.text_input("Phone", placeholder="+91 9876543210", label_visibility="collapsed", key="p_phone")
            otp = st.text_input("OTP", placeholder="OTP 1234 daalo", type="password", label_visibility="collapsed", key="p_otp")
            if st.button("Verify OTP", use_container_width=True, key="p_verify"):
                if len(phone)>=10 and otp=="1234":
                    st.session_state.logged_in=True
                    st.session_state.user_email=phone
                    st.rerun()
                else:
                    st.error("Phone 10 digit + OTP 1234")

        st.markdown("<p style='text-align:center; font-size:11px; color:#5f6368; margin-top:28px;'>By continuing, you agree to JARVIS AI's Terms and Privacy Policy<br>© 2026 JARVIS AI | Boss DEVIL</p>", unsafe_allow_html=True)
    st.stop()

# --- 4. SECRETS ---
try: GROQ_API_KEY=st.secrets["GROQ_API_KEY"]
except: GROQ_API_KEY=""
try: GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"]
except: GOOGLE_API_KEY=""
try: CX_ID=st.secrets["CX_ID"]
except: CX_ID="e604ce9810cbf4ea4"

GEMINI_KEYS=[str(v) for k,v in st.secrets.items() if "GEMINI" in k.upper() and "KEY" in k.upper() and len(str(v))>20]
client=Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_LIST=["JARVIS-GPT", "JARVIS-GEMINI", "JARVIS-FLUX"]
MODES={"💬 Normal Chat":"You are JARVIS AI, helpful assistant created by Boss DEVIL","🎨 Image Creating":"IMAGE_MODE","💻 Code Helper":"You are Code Expert","📚 Study Helper":"You are Study Helper"}

def get_answer(prompt, sys_prompt):
    info=""
    try:
        if GOOGLE_API_KEY and CX_ID:
            r=requests.get("https://www.googleapis.com/customsearch/v1", params={'q':prompt,'key':GOOGLE_API_KEY,'cx':CX_ID,'num':2}, timeout=6)
            info=" ".join([i.get('snippet','') for i in r.json().get('items',[])])[:800]
    except: pass
    final=f"{sys_prompt}\nWeb Info: {info}\nQuestion: {prompt}\nAnswer in same language as user:"
    if client:
        try:
            res=client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":sys_prompt},{"role":"user","content":final}], max_tokens=2000)
            return res.choices[0].message.content
        except: pass
    for k in GEMINI_KEYS:
        try:
            genai.configure(api_key=k)
            return genai.GenerativeModel("gemini-1.5-flash").generate_content(final).text
        except: continue
    return info or "API busy hai Boss, 1 min baad try karo!"

def gen_image(prompt):
    try:
        safe=urllib.parse.quote(prompt[:600])
        url=f"https://image.pollinations.ai/prompt/{safe}?model=flux&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true"
        r=requests.get(url, timeout=30)
        if r.status_code==200:
            return Image.open(io.BytesIO(r.content))
    except: pass
    return None

# --- 5. GEMINI TOP BAR - LEFT HISTORY, RIGHT PROFILE, BEECH ME MODEL/MODE ---
top_left, top_mid, top_right = st.columns([1, 2.5, 1])

with top_left:
    with st.popover("☰", use_container_width=True):
        st.markdown("### 📜 History")
        st.caption(f"{st.session_state.user_email}")
        if not st.session_state.messages:
            st.write("No chats yet")
        else:
            for m in st.session_state.messages[-10:][::-1]:
                st.caption(f"{'🧑' if m['role']=='user' else '🤖'} {m['content'][:45]}...")
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages=[]
            st.rerun()

with top_mid:
    st.markdown("<div style='text-align:center; font-weight:600; font-size:19px; padding-top:4px;'>JARVIS AI 🤖</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.popover("🤖 Model", use_container_width=True):
            selected_model = st.selectbox("Model", MODEL_LIST, label_visibility="collapsed", key="model_pop")
    with c2:
        with st.popover("🎭 Mode", use_container_width=True):
            selected_mode_name = st.selectbox("Mode", list(MODES.keys()), label_visibility="collapsed", key="mode_pop")

with top_right:
    with st.popover("👤", use_container_width=True):
        st.markdown("### 👤 Profile")
        st.write(f"**{st.session_state.user_email}**")
        st.success("Logged in ✅")
        page = st.radio("Go to", ["Chat", "Privacy Policy"], key="page_radio")
        if st.button("🚪 Logout", type="primary", use_container_width=True):
            st.session_state.logged_in=False
            st.session_state.user_email=""
            st.session_state.messages=[]
            st.rerun()

# --- 6. PAGES ---
if 'page' not in locals():
    page="Chat"

if page == "Privacy Policy":
    st.title("🔒 Privacy Policy - JARVIS AI")
    st.markdown("""
    **Last Updated: Oct 2026**
    1. **Google Login:** Sirf Email ID lete hain, password kabhi nahi.
    2. **Phone Login:** Phone number sirf OTP (1234 demo) ke liye.
    3. **Chat History:** Aapki history sirf session me save hoti hai, logout pe delete.
    4. **Third Party:** Groq, Gemini, Google CSE, FLUX APIs use karte hain.
    5. **Personal Data:** Aapki personal baatein private rehti hain.
    Contact: devil.boss.jarvis@gmail.com
    © 2026 JARVIS AI | Created by Boss DEVIL
    """)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "image" in msg: st.image(msg["image"])
            st.markdown(msg["content"])

    # YE SEARCH BAR AB KEYBOARD KE UPAR AYEGA
    if prompt := st.chat_input("Bolo Boss, kya chahiye? ✨"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            if "image" in prompt.lower() or MODES[selected_mode_name]=="IMAGE_MODE":
                with st.spinner("FLUX se bana raha hu..."):
                    img=gen_image(prompt)
                    if img:
                        st.image(img)
                        st.session_state.messages.append({"role":"assistant","content":f"✅ Image: {prompt}","image":img})
                    else: st.error("Image fail!")
            else:
                with st.spinner("Soch raha hu..."):
                    ans=get_answer(prompt, MODES[selected_mode_name])
                    st.markdown(ans)
                    st.session_state.messages.append({"role":"assistant","content":ans})
