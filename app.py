import streamlit as st
import random
import io
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
from PyPDF2 import PdfReader
from streamlit_mic_recorder import mic_recorder

# --- 1. System & Page Configuration ---
st.set_page_config(
    page_title="NEXUS AI | Super-Core",
    page_icon="🌐",
    layout="wide"
)

# --- 2. Custom Professional Styling (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    .stSidebar { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .centered-header { text-align: center; margin-top: -50px; }
    /* File Uploader styling */
    .stFileUploader { background-color: #161b22; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Safe Service Initialization (Zero-Error Logic) ---
# Saare variables ko pehle 'None' set kar rahe hain taaki NameError na aaye
tavily_client = None
openai_client = None
supabase_client = None
groq_client = None

def get_secret(key):
    return st.secrets.get(key, None)

# Initialize Groq (Multiple Keys Support)
keys = get_secret("KEYS")
main_groq_key = get_secret("GROQ_API_KEY")

if keys:
    groq_client = Groq(api_key=random.choice(keys))
elif main_groq_key:
    groq_client = Groq(api_key=main_groq_key)

# Initialize Tavily (Web Search)
tavily_key = get_secret("TAVILY_API_KEY")
if tavily_key:
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=tavily_key)
    except Exception: pass

# Initialize OpenAI (Images)
openai_key = get_secret("OPENAI_API_KEY")
if openai_key:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=openai_key)
    except Exception: pass

# Initialize Supabase (Memory)
s_url = get_secret("SUPABASE_URL")
s_key = get_secret("SUPABASE_KEY")
if s_url and s_key:
    try:
        from supabase import create_client
        supabase_client = create_client(s_url, s_key)
    except Exception: pass

# --- 4. Core Logic Functions ---
def execute_query(messages):
    if not groq_client:
        return "Bhai, Groq API Key missing hai Secrets mein. Pehle use add karo!"
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception:
        return "PDF read nahi ho paayi."

# --- 5. Sidebar: Control Panel ---
st.sidebar.markdown("<h1 style='color:#00d2ff; text-align:center;'>NEXUS PRO</h1>", unsafe_allow_html=True)

# Memory Login (Only if Supabase is connected)
user_id = None
if supabase_client:
    st.sidebar.markdown("###  Secure Memory")
    user_id = st.sidebar.text_input("Enter User ID", placeholder="e.g. abhishek_01")
else:
    st.sidebar.info(" Tip: Connect Supabase for Chat Memory")

# Document Analysis
st.sidebar.markdown("###  Document Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload PDF/Text", type=['pdf', 'txt'])

# Voice Input
st.sidebar.markdown("###  Voice Command")
audio = mic_recorder(start_prompt="Record Voice", stop_prompt="Stop", key='recorder')

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Developer:** Abhishek\n\n**Status:** {'Online' if groq_client else 'Offline'}")

# --- 6. Main Dashboard UI ---
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

# --- 7. Input & Execution ---
user_input = st.chat_input("Enter command...")

# Voice Handling
if audio and audio.get('bytes'):
    st.sidebar.success("Voice Recorded! (Transcribing...)")
    # Yahan Whisper API lag sakti hai, filhaal placeholder text:
    user_input = "Voice command received"

if user_input:
    # 1. Capture and Display User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)

    # 2. Assistant Logic
    with st.chat_message("assistant", avatar=None):
        # Professional Identity
        system_msg = (
            "Your name is NEXUS AI. You are a sophisticated AI workstation created by Abhishek. "
            "Abhishek is a skilled Software Developer and Data Science student expert in Python. "
            "If anyone asks who made you, tell them Abhishek is your developer and he built you with hard work."
        )

        # Context: File Upload
        file_context = ""
        if uploaded_file:
            with st.spinner("Analyzing document..."):
                file_context = f"\n\n[DOCUMENT DATA]: {extract_pdf_text(uploaded_file)[:1500]}"

        # Tool: Web Search
        if ("search" in user_input.lower() or "online" in user_input.lower()) and tavily_client:
            with st.spinner("Searching the web..."):
                try:
                    search_results = tavily_client.search(query=user_input, search_depth="basic")
                    search_data = "\n".join([f"- {r['content']}" for r in search_results['results']])
                    user_input += f"\n\n[WEB SEARCH RESULTS]:\n{search_data}"
                except Exception: pass

        # Tool: Image Generation
        if "generate image" in user_input.lower() and openai_client:
            with st.spinner("NEXUS Vision is rendering..."):
                try:
                    # Placeholder for OpenAI Image API call
                    st.info("Generating Image... (Ensure OpenAI Billing is active)")
                except Exception: pass

        # Final AI Response
        full_context = [{"role": "system", "content": system_instruction if 'system_instruction' in locals() else system_msg + file_context}] + \
                       [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        with st.spinner("Thinking..."):
            response = execute_query(full_context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Optional: Supabase Sync
            if supabase_client and user_id:
                try:
                    supabase_client.table('nexus_memory').upsert({"id": user_id, "history": st.session_state.messages}).execute()
                except Exception: passimport streamlit as st
import random
import io
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
from PyPDF2 import PdfReader
from streamlit_mic_recorder import mic_recorder

# --- 1. System & Page Configuration ---
st.set_page_config(
    page_title="NEXUS AI | Super-Core",
    page_icon="🌐",
    layout="wide"
)

# --- 2. Custom Professional Styling (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    .stSidebar { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .centered-header { text-align: center; margin-top: -50px; }
    /* File Uploader styling */
    .stFileUploader { background-color: #161b22; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Safe Service Initialization (Zero-Error Logic) ---
# Saare variables ko pehle 'None' set kar rahe hain taaki NameError na aaye
tavily_client = None
openai_client = None
supabase_client = None
groq_client = None

def get_secret(key):
    return st.secrets.get(key, None)

# Initialize Groq (Multiple Keys Support)
keys = get_secret("KEYS")
main_groq_key = get_secret("GROQ_API_KEY")

if keys:
    groq_client = Groq(api_key=random.choice(keys))
elif main_groq_key:
    groq_client = Groq(api_key=main_groq_key)

# Initialize Tavily (Web Search)
tavily_key = get_secret("TAVILY_API_KEY")
if tavily_key:
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=tavily_key)
    except Exception: pass

# Initialize OpenAI (Images)
openai_key = get_secret("OPENAI_API_KEY")
if openai_key:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=openai_key)
    except Exception: pass

# Initialize Supabase (Memory)
s_url = get_secret("SUPABASE_URL")
s_key = get_secret("SUPABASE_KEY")
if s_url and s_key:
    try:
        from supabase import create_client
        supabase_client = create_client(s_url, s_key)
    except Exception: pass

# --- 4. Core Logic Functions ---
def execute_query(messages):
    if not groq_client:
        return "Bhai, Groq API Key missing hai Secrets mein. Pehle use add karo!"
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception:
        return "PDF read nahi ho paayi."

# --- 5. Sidebar: Control Panel ---
st.sidebar.markdown("<h1 style='color:#00d2ff; text-align:center;'>NEXUS PRO</h1>", unsafe_allow_html=True)

# Memory Login (Only if Supabase is connected)
user_id = None
if supabase_client:
    st.sidebar.markdown("### 🛡️ Secure Memory")
    user_id = st.sidebar.text_input("Enter User ID", placeholder="e.g. abhishek_01")
else:
    st.sidebar.info(" Tip: Connect Supabase for Chat Memory")

# Document Analysis
st.sidebar.markdown("###  Document Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload PDF/Text", type=['pdf', 'txt'])

# Voice Input
st.sidebar.markdown("###  Voice Command")
audio = mic_recorder(start_prompt="Record Voice", stop_prompt="Stop", key='recorder')

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Developer:** Abhishek\n\n**Status:** {'Online' if groq_client else 'Offline'}")

# --- 6. Main Dashboard UI ---
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

# --- 7. Input & Execution ---
user_input = st.chat_input("Enter command...")

# Voice Handling
if audio and audio.get('bytes'):
    st.sidebar.success("Voice Recorded! (Transcribing...)")
    # Yahan Whisper API lag sakti hai, filhaal placeholder text:
    user_input = "Voice command received"

if user_input:
    # 1. Capture and Display User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)

    # 2. Assistant Logic
    with st.chat_message("assistant", avatar=None):
        # Professional Identity
        system_msg = (
            "Your name is NEXUS AI. You are a sophisticated AI workstation created by Abhishek. "
            "Abhishek is a skilled Software Developer and Data Science student expert in Python. "
            "If anyone asks who made you, tell them Abhishek is your developer and he built you with hard work."
        )

        # Context: File Upload
        file_context = ""
        if uploaded_file:
            with st.spinner("Analyzing document..."):
                file_context = f"\n\n[DOCUMENT DATA]: {extract_pdf_text(uploaded_file)[:1500]}"

        # Tool: Web Search
        if ("search" in user_input.lower() or "online" in user_input.lower()) and tavily_client:
            with st.spinner("Searching the web..."):
                try:
                    search_results = tavily_client.search(query=user_input, search_depth="basic")
                    search_data = "\n".join([f"- {r['content']}" for r in search_results['results']])
                    user_input += f"\n\n[WEB SEARCH RESULTS]:\n{search_data}"
                except Exception: pass

        # Tool: Image Generation
        if "generate image" in user_input.lower() and openai_client:
            with st.spinner("NEXUS Vision is rendering..."):
                try:
                    # Placeholder for OpenAI Image API call
                    st.info("Generating Image... (Ensure OpenAI Billing is active)")
                except Exception: pass

        # Final AI Response
        full_context = [{"role": "system", "content": system_instruction if 'system_instruction' in locals() else system_msg + file_context}] + \
                       [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        with st.spinner("Thinking..."):
            response = execute_query(full_context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Optional: Supabase Sync
            if supabase_client and user_id:
                try:
                    supabase_client.table('nexus_memory').upsert({"id": user_id, "history": st.session_state.messages}).execute()
                except Exception: pass
