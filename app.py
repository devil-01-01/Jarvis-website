import streamlit as st
from groq import Groq
import google.generativeai as genai
import urllib.parse, random, requests, io, uuid
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="JARVIS AI", page_icon="✦", layout="wide")

# --- GEMINI FULL CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
html, body, [class*="css"] {font-family: 'Google Sans', sans-serif!important;}
.stDeployButton{display:none!important;} footer{visibility:hidden!important;} #MainMenu{visibility:hidden!important;} header{visibility:hidden!important;}

/* FIXED TOP - GEMINI JAISA CHOTA */
.fixed-top {
    position: fixed!important; top:0!important; left:0!important; right:0!important;
    background: #f8f9fa!important; z-index:999998!important;
    padding: 8px 12px!important; border-bottom: 1px solid #e8eaed!important;
    display: flex!important; align-items: center!important;
}
div.block-container{padding-top:72px!important; padding-bottom:115px!important; max-width: 800px!important;}

/* GEMINI BUTTONS - CHOTE PILL */
[data-testid="stPopover"] button {
    height: 32px!important; min-height: 32px!important;
    padding: 0 12px!important; font-size: 13px!important; font-weight:500!important;
    border-radius: 20px!important; border:1px solid #dadce0!important; background: white!important;
}
[data-testid="stPopover"] button:hover {background:#f1f3f4!important;}

/* GEMINI CHAT BUBBLES */
[data-testid="stChatMessage"] {background: transparent!important; padding: 12px 0!important;}
[data-testid="stChatMessage"]:nth-child(odd) {background: #f8f9fa!important; border-radius: 24px 24px 24px 8px!important; padding: 14px 18px!important; margin: 8px 0!important;}
[data-testid="stChatMessageAvatar"] {width:32px!important; height:32px!important;}

/* GEMINI SEARCH BAR - FLOATING ABOVE KEYBOARD */
[data-testid="stChatInput"] {
    position: fixed!important; bottom: 18px!important; left: 50%!important;
    transform: translateX(-50%)!important; width: 92%!important; max-width: 760px!important;
    z-index:999999!important; background: #f1f3f4!important;
    border-radius: 28px!important; border:1px solid #e8eaed!important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1)!important;
}
[data-testid="stChatInput"] textarea {background: #f1f3f4!important; font-size:15px!important;}
[data-testid="stChatInput"]:focus-within {background: white!important; box-shadow: 0 4px 24px rgba(0,0,0,0.15)!important;}

@media (max-width: 768px){
    div.block-container{padding-top:64px!important; padding-bottom:120px!important;}
    [data-testid="stChatInput"]{bottom: 10px!important; width: 94%!important;}
}

/* LOGIN GEMINI */
.gemini-login {display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:75vh; text-align:center;}
.g-logo {width:48px; height:48px; background: linear-gradient(135deg, #4285f4, #9c27b0); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:24px; margin-bottom:18px;}
.g-btn {width:100%; max-width:340px; height:44px; background:white; border:1px solid #dadce0; border-radius:24px; font-weight:500; margin:6px 0;}
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_email" not in st.session_state: st.session_state.user_email=""
if "all_chats" not in st.session_state: st.session_state.all_chats={}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id=None
if "show_g" not in st.session_state: st.session_state.show_g=False
if "show_p" not in st.session_state: st.session_state.show_p=False

def new_chat():
    cid=str(uuid.uuid4())[:8]
    st.session_state.all_chats[cid]={"title":"New chat","messages":[],"time":datetime.now().strftime("%d %b %I:%M %p")}
    st.session_state.current_chat_id=cid
    return cid

def cur_msgs():
    if not st.session_state.current_chat_id or st.session_state.current_chat_id not in st.session_state.all_chats:
        new_chat()
    return st.session_state.all_chats[st.session_state.current_chat_id]["messages"]

# --- LOGIN GEMINI STYLE ---
if not st.session_state.logged_in:
    st.markdown("""
    <div class="gemini-login">
        <div class="g-logo">✦</div>
        <h2 style="font-weight:400; font-size:26px; margin:0; color:#202124;">Welcome to JARVIS</h2>
        <p style="color:#5f6368; font-size:14px; margin:8px 0 24px 0;">Ask, create, and explore with AI</p>
    </div>
    """, unsafe_allow_html=True)
    c = st.columns([1,2,1])[1]
    with c:
        if st.button(" Continue with Google", use_container_width=True, key="lg_g"):
            st.session_state.show_g=True; st.session_state.show_p=False
        if st.session_state.show_g:
            em=st.text_input("Email", placeholder="Email", label_visibility="collapsed", key="em_g")
            if st.button("Continue", type="primary", use_container_width=True):
                if "@" in em:
                    st.session_state.logged_in=True; st.session_state.user_email=em; new_chat(); st.rerun()
        st.markdown("<div style='display:flex; align-items:center; gap:10px; max-width:340px; margin:12px auto;'><div style='flex:1; height:1px; background:#dadce0;'></div><span style='color:#5f6368; font-size:12px;'>OR</span><div style='flex:1; height:1px; background:#dadce0;'></div></div>", unsafe_allow_html=True)
        if st.button(" Continue with phone", use_container_width=True, key="lg_p"):
            st.session_state.show_p=True; st.session_state.show_g=False
        if st.session_state.show_p:
            ph=st.text_input("Phone", placeholder="+91 Phone", label_visibility="collapsed", key="ph_p")
            ot=st.text_input("OTP", placeholder="1234", type="password", label_visibility="collapsed", key="ot_p")
            if st.button("Verify", use_container_width=True):
                if len(ph)>=10 and ot=="1234":
                    st.session_state.logged_in=True; st.session_state.user_email=ph; new_chat(); st.rerun()
        st.markdown("<p style='text-align:center; color:#5f6368; font-size:11px; margin-top:24px;'>By continuing, you agree to JARVIS Terms and Privacy<br>© 2026 JARVIS AI • Boss DEVIL</p>", unsafe_allow_html=True)
    st.stop()

# --- SECRETS ---
try: GROQ_API_KEY=st.secrets["GROQ_API_KEY"]
except: GROQ_API_KEY=""
try: GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"]
except: GOOGLE_API_KEY=""
try: CX_ID=st.secrets["CX_ID"]
except: CX_ID="e604ce9810cbf4ea4"
GEMINI_KEYS=[str(v) for k,v in st.secrets.items() if "GEMINI" in k.upper() and "KEY" in k.upper() and len(str(v))>20]
client=Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_LIST=["Gemini Flash","JARVIS-GPT","JARVIS-FLUX"]
MODES={"💬 Chat":"You are JARVIS AI by Boss DEVIL, friendly Gemini style","🎨 Image":"IMAGE_MODE","💻 Code":"You are code expert","📚 Study":"You are study helper"}

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
    return "Thoda ruk ke try karo Boss!"

def gen_img(pr):
    try:
        safe=urllib.parse.quote(pr[:600])
        url=f"https://image.pollinations.ai/prompt/{safe}?model=flux&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true"
        r=requests.get(url, timeout=30)
        if r.status_code==200: return Image.open(io.BytesIO(r.content))
    except: pass
    return None

# --- GEMINI FIXED TOP BAR - SMALL ---
st.markdown('<div class="fixed-top">', unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns([0.7,0.9,2.8,0.9,0.7], gap="small")
with c1:
    with st.popover("☰", use_container_width=True):
        st.markdown("**JARVIS AI**")
        st.caption(f"{st.session_state.user_email[:20]}")
        if st.button("➕ New chat", use_container_width=True, type="primary"):
            new_chat(); st.rerun()
        st.divider()
        st.markdown("**Recent**")
        for cid, chat in list(st.session_state.all_chats.items())[::-1][:10]:
            title = chat["messages"][0]["content"][:22]+".." if chat["messages"] else "New chat"
            if st.button(f"{title}", key=f"ch_{cid}", use_container_width=True):
                st.session_state.current_chat_id=cid; st.rerun()
        if st.button("Clear all", use_container_width=True):
            st.session_state.all_chats={}; new_chat(); st.rerun()
with c2:
    with st.popover("✦ Model", use_container_width=True):
        sel_model=st.selectbox("Model", MODEL_LIST, label_visibility="collapsed")
with c3:
    st.markdown("<div style='text-align:center; font-weight:500; color:#202124; font-size:16px; padding-top:2px;'>JARVIS</div>", unsafe_allow_html=True)
with c4:
    with st.popover(" Mode", use_container_width=True):
        sel_mode_name=st.selectbox("Mode", list(MODES.keys()), label_visibility="collapsed")
with c5:
    with st.popover("👤", use_container_width=True):
        st.markdown(f"**{st.session_state.user_email}**")
        st.caption("Google Account")
        page=st.radio("Menu", ["Chat","Privacy"], label_visibility="collapsed")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in=False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN ---
if 'page' not in locals(): page="Chat"

if page=="Privacy":
    st.title("Privacy")
    st.write("JARVIS AI saves whole chat session-wise in memory. Email/Phone only for login. No password stored. Contact: devil.boss.jarvis@gmail.com")
else:
    msgs=cur_msgs()
    if not msgs:
        st.markdown("""
        <div style="text-align:center; margin-top:60px;">
            <div style="font-size:42px; margin-bottom:12px;">✦</div>
            <h2 style="font-weight:400; color:#202124;">Hello, Boss</h2>
            <p style="color:#5f6368;">How can I help you today?</p>
        </div>
        """, unsafe_allow_html=True)
        # Gemini suggestion chips
        s1,s2,s3=st.columns(3)
        with s1:
            if st.button("✍️ Write a story", use_container_width=True): st.session_state.suggest="Write a story about space"
        with s2:
            if st.button("💡 Explain AI", use_container_width=True): st.session_state.suggest="Explain AI in simple words"
        with s3:
            if st.button("🎨 Create image", use_container_width=True): st.session_state.suggest="Create image of sunset"

    for m in msgs:
        with st.chat_message(m["role"], avatar="🧑‍💼" if m["role"]=="user" else "✦"):
            if "image" in m: st.image(m["image"])
            st.markdown(m["content"])

    # Input - Gemini floating
    prompt = st.chat_input("Ask JARVIS")
    if prompt:
        if len(msgs)==0:
            st.session_state.all_chats[st.session_state.current_chat_id]["title"]=prompt[:30]
        msgs.append({"role":"user","content":prompt})
        with st.chat_message("user", avatar="🧑‍💼"): st.markdown(prompt)
        with st.chat_message("assistant", avatar="✦"):
            if "image" in prompt.lower() or MODES[sel_mode_name]=="IMAGE_MODE":
                with st.spinner("Creating..."):
                    img=gen_img(prompt)
                    if img:
                        st.image(img)
                        msgs.append({"role":"assistant","content":f"Image: {prompt}","image":img})
                    else: st.error("Image failed")
            else:
                with st.spinner(""):
                    ans=get_ans(prompt, MODES[sel_mode_name])
                    st.markdown(ans)
                    msgs.append({"role":"assistant","content":ans})
        st.session_state.all_chats[st.session_state.current_chat_id]["messages"]=msgs
        st.rerun()
