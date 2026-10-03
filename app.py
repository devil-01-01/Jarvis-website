import streamlit as st
import time

# Page config
st.set_page_config(
    page_title="JARVIS",
    page_icon="🤖",
    layout="wide"
)

# Styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1 {
        color: #00f5ff !important;
        text-align: center;
        font-size: 65px !important;
        text-shadow: 0 0 25px #00f5ff;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("JARVIS")

# Init chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello Boss. I am JARVIS. Online and Ready."
    })

# Show old chats
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input box
if prompt := st.chat_input("Message JARVIS..."):
    # 1. User message save
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. JARVIS reply with typing effect
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Yahi par aapka AI ka jawab aayega
        bot_reply = f"Boss, you said: {prompt}\n\nI am JARVIS, your personal AI. I'm working perfectly!"

        for word in bot_reply.split():
            full_response += word + " "
            placeholder.markdown(full_response + "▌")
            time.sleep(0.06)
        
        placeholder.markdown(full_response)

    # 3. Save bot message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
