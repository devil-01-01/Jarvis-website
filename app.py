import streamlit as st
from transformers import pipeline
import torch
import re
import sympy as sp

st.set_page_config(page_title="BOSS JARVIS")
st.title("BOSS JARVIS")

# --- SIDHA AAPKA MODEL YAHAN LOAD HOGA, KOI NONE NAHI ---
@st.cache_resource
def load_jarvis():
    jarvis_model = pipeline(
        task="text-generation",
        model="openai/gpt-oss-20b",
        torch_dtype=torch.float32,
        trust_remote_code=True
    )
    return jarvis_model

# Model ko direct naam ke saath load karo
st.write("Model: openai/gpt-oss-20b loading...")
jarvis_model = load_jarvis()
st.success("Model Loaded: openai/gpt-oss-20b")

# Maths + Reasoning
def maths_solver(q):
    try:
        if "%" in q:
            nums = re.findall(r"\d+\.?\d*", q)
            if len(nums)>=2:
                return f"Answer: {float(nums[0])*float(nums[1])/100}"
        return None
    except:
        return None

# Chat
if "chat" not in st.session_state:
    st.session_state.chat = []

for c in st.session_state.chat:
    with st.chat_message(c["role"]):
        st.markdown(c["content"])

if user_q := st.chat_input("Bolo Boss..."):
    st.session_state.chat.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)

    ans = maths_solver(user_q)

    if not ans:
        # YAHAN DIRECT MODEL USE HO RAHA HAI
        result = jarvis_model(user_q, max_new_tokens=200)
        ans = result[0]['generated_text']

    with st.chat_message("assistant"):
        st.markdown(ans)
    st.session_state.chat.append({"role": "assistant", "content": ans})
