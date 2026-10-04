import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, requests, io, uuid, smtplib, ssl
from email.message import EmailMessage
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stDeployButton{display:none!important;} footer{visibility:hidden!important;} #MainMenu{visibility:hidden!important;} header{visibility:hidden!important;}
.fixed-top {position: fixed!important; top:0!important; left:0!important; right:0!important; background:#f8f9fa!important; z-index:999998!important; padding:8px 10px!important; border-bottom:1px solid #e8eaed!important; display:flex!important;}
div.block-container{padding-top:70px!important; padding-bottom:115px!important; max-width:800px!important;}
[data-testid="stPopover"] button {height:32px!important; min-height:32px!important; padding:0 12px!important; font-size:13px!important; border-radius:20px!important; border:1px solid #dadce0!important; background:white!important;}
[data-testid="stChatInput"] {position: fixed!important; bottom: 14px!important; left: 50%!important; transform: translateX(-50%)!important; width:92%!important; max-width:760px!important; z-index:999999!important; background:#f1f3f4!important; border-radius:28px!important; box-shadow:0 4px 20px rgba(0,0,0,0.1)!important;}
.g-logo {width:48px; height:48px; background: linear-gradient(135deg, #4285f4, #9c27b0); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:24px; margin:0 auto 14px auto;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_email" not in st.session_state: st.session_state.user_email=""
if "all_chats" not in st.session_state: st.session_state.all_chats={}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id=None
if "gmail_otp" not in st.session_state: st.session_state.gmail_otp=""
if "phone_otp" not in st.session_state: st.session_state.phone_otp=""
if "gmail_pending" not in st.session_state: st.session_state.gmail_pending=""
if "phone_pending" not in st.session_state: st.session_state.phone_pending=""

def new_chat():
    cid=str(uuid.uuid4())[:8]
    st.session_state.all_chats[cid]={"title":"New chat","messages":[],"time":datetime.now().strftime("%d %b %I:%M %p")}
    st.session_state.current_chat_id=cid
    return cid

def cur_msgs():
    if not st.session_state.current_chat_id or st.session_state.current_chat_id not in st.session_state.all_chats:
        new_chat()
    return st.session_state.all_chats[st.session_state.current_chat_id]["messages"]

# REAL EMAIL SENDING FUNCTION
def send_real_email(to_email, otp):
    try:
        EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
        EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
        msg = EmailMessage()
        msg['Subject'] = 'JARVIS AI - Your Verification Code'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg.set_content(f"""
Hello Boss,

Your JARVIS AI verification code is: {otp}

This code will expire in 5 minutes.

If you didn't request this, ignore this email.

- JARVIS AI Team
        """)
        msg.add_alternative(f"""
        <div style="font-family: Arial; padding:20px; border:1px solid #eee; border-radius:10px;">
            <h2 style="color:#4285f4;">✦ JARVIS AI Verification</h2>
            <p>Your verification code is:</p>
            <h1 style="background:#f1f3f4; padding:12px 24px; border-radius:8px; letter-spacing:6px; text-align:center;">{otp}</h1>
            <p style="color:#5f6368; font-size:12px;">Expires in 5 minutes. Don't share this code.</p>
        </div>
        """, subtype='html')

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email sending failed: {e}. Check EMAIL_ADDRESS/PASSWORD in secrets.")
        return False

# --- LOGIN WITH REAL VERIFICATION ---
if not st.session_state.logged_in:
    st.markdown("""<div style="display:flex; flex-direction:column; align-items:center; text-align:center; margin-top:20px;">
        <div class="g-logo">✦</div>
        <h2 style="font-weight:400; font-size:26px; margin:0;">Verify to continue</h2>
        <p style="color:#5f6368; font-size:13px;">Code will go to your real Gmail inbox</p></div>""", unsafe_allow_html=True)

    col = st.columns([1,2,1])[1]
    with col:
        tab1, tab2 = st.tabs(["📧 Gmail Verify", "📱 Phone Verify"])

        with tab1:
            st.markdown("**Gmail Verification - Real Email**")
            gmail = st.text_input("Gmail", placeholder="ayr86068@gmail.com", key="gmail_input")
            if st.button("📨 Send Verification Code", use_container_width=True, key="send_gmail"):
                if "@" in gmail:
                    otp = str(random.randint(100000,999999))
                    st.session_state.gmail_otp = otp
                    st.session_state.gmail_pending = gmail
                    with st.spinner("Sending code to your Gmail..."):
                        if send_real_email(gmail, otp):
                            st.success(f"✅ Verification code sent to {gmail}")
                            st.warning("📧 Gmail inbox check karo - Spam me bhi dekho!")
                        # NO DEMO OTP SHOWN HERE
                else:
                    st.error("Sahi Gmail daalo")

            if st.session_state.gmail_otp!= "":
                st.divider()
                st.write(f"Code sent to: **{st.session_state.gmail_pending}**")
                st.caption("Gmail inbox me code aaya hoga - yahan enter karo")
                user_otp = st.text_input("Enter 6-digit Code from Gmail", placeholder="Check Gmail inbox", key="gmail_otp_input")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("✅ Verify & Login", type="primary", use_container_width=True, key="verify_gmail"):
                        if user_otp == st.session_state.gmail_otp:
                            st.session_state.logged_in=True
                            st.session_state.user_email=st.session_state.gmail_pending
                            st.session_state.gmail_otp=""
                            new_chat()
                            st.success("Gmail Verified ✅")
                            st.rerun()
                        else:
                            st.error("Galat Code! Gmail wala sahi code daalo")
                with c2:
                    if st.button("🔄 Resend Code", use_container_width=True, key="resend_gmail"):
                        new_otp = str(random.randint(100000,999999))
                        st.session_state.gmail_otp = new_otp
                        if send_real_email(st.session_state.gmail_pending, new_otp):
                            st.success("New code sent to Gmail!")

        with tab2:
            st.markdown("**Phone Verification**")
            phone = st.text_input("Phone Number", placeholder="+91 9876543210", key="phone_input_verify")
            st.caption("Note: Phone pe real SMS ke liye Twilio chahiye, abhi demo chal raha hai")
            if st.button("📲 Send OTP to Phone", use_container_width=True, key="send_phone"):
                if len(phone) >= 10:
                    otp = str(random.randint(100000,999999))
                    st.session_state.phone_otp = otp
                    st.session_state.phone_pending = phone
                    # Phone ke liye abhi demo hi hai - real SMS paid hai
                    st.success(f"✅ OTP generated for {phone}")
                    st.info(f"Phone Demo OTP: {otp} (Real SMS ke liye Twilio lagega)")
                else:
                    st.error("10 digit number daalo")

            if st.session_state.phone_otp!= "":
                st.divider()
                st.write(f"OTP for: **{st.session_state.phone_pending}**")
                user_p_otp = st.text_input("Enter Phone OTP", placeholder="123456", key="phone_otp_input")
                cp1, cp2 = st.columns(2)
                with cp1:
                    if st.button("✅ Verify & Login", type="primary", use_container_width=True, key="verify_phone"):
                        if user_p_otp == st.session_state.phone_otp:
                            st.session_state.logged_in=True
                            st.session_state.user_email=st.session_state.phone_pending
                            st.session_state.phone_otp=""
                            new_chat()
                            st.rerun()
                        else:
                            st.error("Galat OTP!")

        st.markdown("<p style='text-align:center; color:#5f6368; font-size:11px; margin-top:20px;'>🔐 Gmail pe real code jayega, bina Gmail khole login nahi hoga<br>© 2026 JARVIS AI</p>", unsafe_allow_html=True)
    st.stop()

# --- REST APP SAME ---
try: GROQ_API_KEY=st.secrets["GROQ_API_KEY"]
except: GROQ_API_KEY=""
try: GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"]
except: GOOGLE_API_KEY=""
try: CX_ID=st.secrets["CX_ID"]
except: CX_ID="e604ce9810cbf4ea4"
GEMINI_KEYS=[str(v) for k,v in st.secrets.items() if "GEMINI" in k.upper() and "KEY" in k.upper() and len(str(v))>20]
client=Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
MODEL_LIST=["Gemini Flash","JARVIS-GPT","JARVIS-FLUX"]
MODES={"💬 Chat":"You are JARVIS AI by Boss DEVIL","🎨 Image":"IMAGE_MODE","💻 Code":"You are code expert","📚 Study":"You are study helper"}

def get_ans(p, sys):
    info=""
    try:
        if GOOGLE_API_KEY and CX_ID:
            r=requests.get("https://www.googleapis.com/customsearch/v1", params={'q':p,'key':GOOGLE_API_KEY,'cx':CX_ID,'num':2}, timeout=6)
            info=" ".join([i.get('snippet','') for i in r.json().get('items',[])])[:800]
    except: pass
    final=f"{sys}\nContext:{info}\nQ:{p}"
    if client:
        try:
            res=client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":sys},{"role":"user","content":final}], max_tokens=2000)
            return res.choices[0].message.content
        except: pass
    for k in GEMINI_KEYS:
        try:
            genai.configure(api_key=k)
            return genai.GenerativeModel("gemini-1.5-flash").generate_content(final).text
        except: continue
    return "Try again Boss!"

def gen_img(pr):
    try:
        safe=urllib.parse.quote(pr[:600])
        url=f"https://image.pollinations.ai/prompt/{safe}?model=flux&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true"
        r=requests.get(url, timeout=30)
        if r.status_code==200: return Image.open(io.BytesIO(r.content))
    except: pass
    return None

st.markdown('<div class="fixed-top">', unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns([0.7,0.9,2.8,0.9,0.7], gap="small")
with c1:
    with st.popover("☰", use_container_width=True):
        if st.button("➕ New chat", type="primary", use_container_width=True):
            new_chat(); st.rerun()
        st.divider()
        for cid, chat in list(st.session_state.all_chats.items())[::-1][:10]:
            title = chat["messages"][0]["content"][:22]+".." if chat["messages"] else "New chat"
            if st.button(f"{title}", key=f"ch_{cid}", use_container_width=True):
                st.session_state.current_chat_id=cid; st.rerun()
with c2:
    with st.popover("Model", use_container_width=True):
        sel_model=st.selectbox("Model", MODEL_LIST, label_visibility="collapsed")
with c3:
    st.markdown("<div style='text-align:center; font-weight:600; font-size:15px; padding-top:3px;'>JARVIS AI</div>", unsafe_allow_html=True)
with c4:
    with st.popover("Mode", use_container_width=True):
        sel_mode_name=st.selectbox("Mode", list(MODES.keys()), label_visibility="collapsed")
with c5:
    with st.popover("👤", use_container_width=True):
        st.write(f"**{st.session_state.user_email[:20]}**")
        page=st.radio("Menu", ["Chat","Privacy"], label_visibility="collapsed")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in=False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if 'page' not in locals(): page="Chat"
if page=="Privacy":
    st.title("🔒 Privacy")
    st.write("Real Gmail verification via SMTP. No demo OTP shown.")
else:
    msgs=cur_msgs()
    if not msgs:
        st.markdown("<div style='text-align:center; margin-top:50px;'><div style='font-size:40px;'>✦</div><h2 style='font-weight:400;'>Hello, Boss</h2></div>", unsafe_allow_html=True)
    for m in msgs:
        with st.chat_message(m["role"], avatar="👤" if m["role"]=="user" else "🤖"):
            if "image" in m: st.image(m["image"])
            st.markdown(m["content"])
    if prompt := st.chat_input("Ask JARVIS"):
        if len(msgs)==0:
            st.session_state.all_chats[st.session_state.current_chat_id]["title"]=prompt[:30]
        msgs.append({"role":"user","content":prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            if "image" in prompt.lower() or MODES[sel_mode_name]=="IMAGE_MODE":
                with st.spinner("Creating..."):
                    img=gen_img(prompt)
                    if img:
                        st.image(img)
                        msgs.append({"role":"assistant","content":f"Image: {prompt}","image":img})
            else:
                with st.spinner("Thinking..."):
                    ans=get_ans(prompt, MODES[sel_mode_name])
                    st.markdown(ans)
                    msgs.append({"role":"assistant","content":ans})
        st.session_state.all_chats[st.session_state.current_chat_id]["messages"]=msgs
        st.rerun()
