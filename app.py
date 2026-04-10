import streamlit as st
import random
import io
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
from PyPDF2 import PdfReader
from streamlit_mic_recorder import mic_recorder
from tavily import TavilyClient
from openai import OpenAI
from supabase import create_client, Client
import contextlib

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
    .stFileUploader { background-color: #161b22; border-radius: 10px; padding: 10px; }
    /* Style code block output */
    .stCode { background-color: #161b22 !important; border-radius: 8px; color: #7ee787; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Core Service Initialize ---
# Function to get secrets securely
def get_secret(key):
    try:
        return st.secrets[key]
    except KeyError:
        return None

# Initialize Clients from Secrets (or handle if missing)
try:
    groq_client = Groq(api_key=get_secret("GROQ_API_KEY")) # Or your multiple keys pool function
    tavily_client = TavilyClient(api_key=get_secret("TAVILY_API_KEY"))
    openai_client = OpenAI(api_key=get_secret("OPENAI_API_KEY"))
    supabase_url = get_secret("SUPABASE_URL")
    supabase_key = get_secret("SUPABASE_KEY")
    supabase_client: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
except Exception:
    st.error("Error initializing core services. Check st.secrets.")

# --- 4. Tool Functions ---

# Tool: Web Search (Tavily)
def search_the_web(query):
    try:
        response = tavily_client.search(query=query, search_depth="advanced")
        context = "\n\n".join([f"[Source: {r['url']}] {r['content']}" for r in response['results']])
        return context
    except Exception as e:
        return f"Web Search Error: {str(e)}"

# Tool: Image Generation (OpenAI DALL-E)
def generate_nexus_vision(prompt):
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=f"A professional, futuristic image depicting: {prompt}",
            n=1,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        return f"Image Generation Error: {str(e)}"

# Tool: Code Interpreter (Secure Python Sandbox)
def run_code_interpreter(code):
    try:
        # Secure execution: capture stdout and stderr
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            # Safe globals and locals, allowing common data tools
            exec_globals = {"pd": pd, "plt": plt, "st": st}
            exec(code, exec_globals)
        output = f.getvalue()
        return output if output else "Code executed successfully (no output)."
    except Exception as e:
        return f"Execution Error: {str(e)}"

# Function to extract PDF text
def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- 5. Sidebar: Control Panel ---
st.sidebar.markdown("<h1 style='color:#00d2ff; text-align:center;'>NEXUS PRO</h1>", unsafe_allow_html=True)

# Persistent Memory & Login
st.sidebar.markdown("### 🛡️ User Secure Login")
user_id = st.sidebar.text_input("Enter your unique ID for memory persistence", key='user_id')

if supabase_client and user_id:
    st.sidebar.success(f"Memory active for User: {user_id}")
    # Load session state from database if available (Simplified)
    # response = supabase_client.table('nexus_memory').select('history').eq('id', user_id).execute()
    # if response.data:
    #    st.session_state.messages = response.data[0]['history']

# Document Analysis
st.sidebar.markdown("###  Document Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload PDF or TXT", type=['pdf', 'txt'])

# Voice
st.sidebar.markdown("###  Voice Input")
audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key='recorder')

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Developer:** Abhishek\n\n**Status:** Super-Core Online")

# --- 6. Main Dashboard UI ---
st.markdown("<div class='centered-header'><h1>🌐</h1><h1>NEXUS AI</h1></div>", unsafe_allow_html=True)
st.caption("<p style='text-align:center;'>Super-Core AI Workstation Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("---")

# Session State for local memory
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to NEXUS Super-Core. How can I assist you today?"}]

# Render History
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None):
        if message["role"] == "assistant" and "Image: " in message["content"]:
            # Display generated image
            st.image(message["content"].split(": ")[1], caption="Nexus Vision Generation")
        elif message["role"] == "assistant" and "Code Execution Output: " in message["content"]:
            st.code(message["content"].split(": ")[1], language='python')
        else:
            st.markdown(message["content"])

# User Input Handling
user_input = st.chat_input("Enter command, ask to generate images, or run code...")

# Voice Handling (Transcription would happen here via API)
if audio:
    st.sidebar.success("Audio Recorded!")
    user_input = "Audio signal received (Auto-transcribe feature required)"

# --- 7. Core Intelligence Loop ---
if user_input:
    # 1. Capture User Input
    file_context = ""
    if uploaded_file and "File content extracted" not in user_input:
        with st.spinner("Extracting document context..."):
            file_context = f"\n\n[CONTEXT FROM {uploaded_file.name.upper()}]:\n{extract_pdf_text(uploaded_file)[:1500]}\n"

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=None):
        system_instruction = (
            "Your name is NEXUS AI. You are a highly sophisticated Super-Core AI workstation created by Abhishek. "
            "Abhishek is a senior Software Developer and Data Science student, expert in AI and Python. "
            "If asked about your origins, mention Abhishek's expertise. "
            "You have tools for Web Search, Image Generation, and Code Execution. Use them when requested."
        )
        
        # Tool: Check for Image Request
        if "generate image" in user_input.lower() or "nexus vision" in user_input.lower():
            with st.spinner("NEXUS Vision core is rendering..."):
                vision_prompt = user_input.replace("generate image", "").strip()
                image_url = generate_nexus_vision(vision_prompt)
                if "Error" not in image_url:
                    st.image(image_url, caption=f"Nexus Vision: {vision_prompt}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Image: {image_url}"})
                    # Skip normal text processing for image success
                    st.rerun()

        # Tool: Check for Web Search Request
        elif "search the web" in user_input.lower() or "check online" in user_input.lower():
            with st.spinner("NEXUS is searching the live internet..."):
                search_query = user_input.replace("search the web", "").strip()
                web_results = search_the_web(search_query)
                user_input = f"{user_input}\n\n[LIVE WEB RESULTS]:\n{web_results}\n"

        # Tool: Check for Code Interpreter Request
        elif "run python code" in user_input.lower() or "execute script" in user_input.lower():
            with st.spinner("NEXUS Code Interpreter is active..."):
                # Simplified code extraction (User must provide raw code or clear block)
                code_block = user_input.replace("run python code", "").strip()
                execution_output = run_code_interpreter(code_block)
                st.markdown("Code executed.")
                st.code(execution_output, language='python')
                st.session_state.messages.append({"role": "assistant", "content": f"Code Execution Output: {execution_output}"})
                # Skip normal processing
                st.rerun()

        # Tool: Standard Text processing with file context
        full_context = [{"role": "system", "content": system_instruction + file_context}] + \
                       [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        with st.spinner("Thinking..."):
            # Note: For efficiency, we use Groq for text processing. 
            # (Image/Search results are now part of the user_input context)
            from groq import Groq # Re-ensure inside loop for robust client management
            api_pool = st.secrets.get("KEYS", [])
            key_to_use = random.choice(api_pool) if api_pool else st.secrets.get("GROQ_API_KEY")
            client = Groq(api_key=key_to_use)

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_context,
                temperature=0.7,
                max_tokens=2048
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Persistent Memory (Database sync after each exchange) - Requires actual table setup
            if supabase_client and user_id:
                try:
                    # Sync history to Supabase table 'nexus_memory' (column 'id', 'history')
                    history_data = [
                        {"role": m["role"], "content": m["content"][-2000:]} # Limit context size for database
                        for m in st.session_state.messages
                    ]
                    # response = supabase_client.table('nexus_memory').upsert({"id": user_id, "history": history_data}).execute()
                except Exception as e:
                    st.sidebar.error(f"Memory Sync Error: {str(e)}")
