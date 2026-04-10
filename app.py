import streamlit as st
import random
import io
from groq import Groq
from PyPDF2 import PdfReader
from supabase import create_client

# --- 1. CONFIGURATION & MINIMALIST THEME ---
st.set_page_config(page_title="NEXUS AI", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    /* Dark Theme & Minimalist UI */
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .stSidebar { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 5px; }
    
    /* Remove default avatars */
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    
    /* Clean Header */
    .header-text { text-align: center; color: #58a6ff; font-weight: 600; letter-spacing: 2px; }
    .dev-text { text-align: center; color: #8b949e; font-size: 0.8rem; }
    
    /* Buttons */
    div.stButton > button { width: 100%; border-radius: 5px; background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; }
    div.stButton > button:hover { border-color: #58a6ff; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE SERVICES ---
def init_system():
    try:
        # Load credentials from secrets
        S_URL = st.secrets["SUPABASE_URL"]
        S_KEY = st.secrets["SUPABASE_KEY"]
        G_KEYS = st.secrets["KEYS"]
        
        # Clients
        db = create_client(S_URL, S_KEY)
        # Select one of 6 keys for load balancing
        ai_engine = Groq(api_key=random.choice(G_KEYS))
        
        # Optional Tools
        search_tool = None
        if "TAVILY_API_KEY" in st.secrets:
            from tavily import TavilyClient
            search_tool = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
            
        vision_tool = None
        if "OPENAI_API_KEY" in st.secrets:
            from openai import OpenAI
            vision_tool = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            
        return db, ai_engine, search_tool, vision_tool
    except Exception as e:
        st.error(f"Initialization Failed: {str(e)}")
        return None, None, None, None

supabase, groq_client, tavily, openai = init_system()

# --- 3. SYSTEM UTILITIES ---
def sync_load(email):
    try:
        response = supabase.table('nexus_memory').select("history").eq("id", email).execute()
        return response.data[0]['history'] if response.data else None
    except: return None

def sync_save(email, history):
    try:
        supabase.table('nexus_memory').upsert({"id": email, "history": history}).execute()
    except: pass

def read_document(file):
    try:
        pdf = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf.pages])
    except: return "Error processing document."

# --- 4. SIDEBAR: CONTROL CENTER ---
st.sidebar.markdown("<h2 class='header-text'>🌐 NEXUS AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

user_identity = st.sidebar.text_input("User Access ID", placeholder="Enter Gmail")

if user_identity:
    if "session_id" not in st.session_state or st.session_state.session_id != user_identity:
        data = sync_load(user_identity)
        st.session_state.messages = data if data else [{"role": "assistant", "content": f"Nexus System Active: {user_identity}"}]
        st.session_state.session_id = user_identity
    st.sidebar.success("Cloud Memory Synced")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Authentication required for persistent session."}]

st.sidebar.markdown("---")
doc_file = st.sidebar.file_uploader("Attach PDF", type=['pdf'])

st.sidebar.markdown("---")
st.sidebar.markdown("<p class='dev-text'>Developed by Abhishek</p>", unsafe_allow_html=True)

# --- 5. MAIN WORKSTATION ---
st.markdown("<h1 class='header-text'>NEXUS AI WORKSTATION</h1>", unsafe_allow_html=True)
st.markdown("---")

# Render Logs
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. CORE INTELLIGENCE ---
if query := st.chat_input("Enter Command"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        # Document Injection
        context_data = ""
        if doc_file:
            context_data = f"\n[Document Context]: {read_document(doc_file)[:1500]}"
            
        # Web Intelligence
        if ("search" in query.lower() or "online" in query.lower()) and tavily:
            with st.spinner("Accessing Web Data"):
                web_raw = tavily.search(query=query)
                web_info = "\n".join([f"- {r['content']}" for r in web_raw['results']])
                query += f"\n\n[Web Data]: {web_info}"

        # Vision Generation
        if "generate image" in query.lower() and openai:
            with st.spinner("Generating Vision"):
                url = openai.images.generate(model="dall-e-3", prompt=query).data[0].url
                st.image(url)
                st.session_state.messages.append({"role": "assistant", "content": f"Resource Generated: {url}"})

        # Process Final Response
        system_logic = f"Identity: NEXUS AI. Developer: Abhishek. Task: High-precision workstation response. {context_data}"
        history_chain = [{"role": "system", "content": system_logic}] + st.session_state.messages
        
        with st.spinner("Processing Cores"):
            if groq_client:
                result = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history_chain,
                    temperature=0.4
                ).choices[0].message.content
                
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
                
                if user_identity:
                    sync_save(user_identity, st.session_state.messages)
            else:
                st.error("Engine Offline")
