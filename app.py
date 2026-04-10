import streamlit as st
from groq import Groq
import random
from PyPDF2 import PdfReader
from streamlit_mic_recorder import mic_recorder

# --- System Configuration ---
st.set_page_config(page_title="NEXUS AI PRO", page_icon="🌐", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    .stSidebar { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .centered-header { text-align: center; margin-top: -50px; }
    </style>
    """, unsafe_allow_html=True)

# --- Core Logic Functions ---
def execute_query(messages):
    api_pool = st.secrets.get("KEYS", [])
    active_pool = list(api_pool)
    random.shuffle(active_pool)
    for key in active_pool:
        try:
            client = Groq(api_key=key)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            return completion.choices[0].message.content
        except Exception: continue
    return "Error: Cores busy."

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- Sidebar: Control Panel (Voice & File) ---
st.sidebar.markdown("<h1 style='color:#00d2ff; text-align:center;'>NEXUS PRO</h1>", unsafe_allow_html=True)

# FEATURE: Voice Input
st.sidebar.markdown("### 🎙️ Voice Command")
audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key='recorder')

# FEATURE: File Upload
st.sidebar.markdown("###  Document Analysis")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=['pdf'])

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Developer:** Abhishek\n\n**Status:** Online\n\n**Cores:** {len(st.secrets.get('KEYS', []))}")

# --- Main Dashboard ---
st.markdown("<div class='centered-header'><h1>🌐</h1><h1>NEXUS AI</h1></div>", unsafe_allow_html=True)
st.caption("<p style='text-align:center;'>Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("---")

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I assist you?"}]

# Render History
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

# --- Input Handling ---
user_input = st.chat_input("Enter command...")

# If Voice is used
if audio:
    # Note: For actual speech-to-text, you'd need an API like Whisper. 
    # Currently, this records and we can notify the user.
    st.sidebar.success("Audio Recorded!")
    user_input = "Audio signal received (Transcribe feature coming soon)"

# Process Input
if user_input:
    file_content = ""
    if uploaded_file:
        file_content = f"\n\n[CONTEXT FROM PDF]: {extract_pdf_text(uploaded_file)[:2000]}"

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=None):
        system_instruction = (
            "Your name is NEXUS AI. Developed by Abhishek (Software Developer & Data Science student). "
            "If asked who made you, say: 'Mujhe Abhishek ne banaya hai. Wahi mere creator hain.' "
            "Use the provided PDF context if available."
        )
        
        full_context = [{"role": "system", "content": system_instruction + file_content}] + \
                       [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        with st.spinner("NEXUS is thinking..."):
            response = execute_query(full_context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
