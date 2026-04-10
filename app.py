import streamlit as st
import random
import io
from groq import Groq
from PyPDF2 import PdfReader
from supabase import create_client

# --- 1. SYSTEM CONFIG & SEXY UI (Custom CSS) ---
st.set_page_config(page_title="NEXUS AI", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Roboto, sans-serif; }
    
    /* Sexy Sidebar (Control Panel) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
        border-right: 1px solid #30363d;
        padding-top: 20px;
    }
    
    /* Dashboard Header */
    .nexus-title { 
        text-align: center; color: #58a6ff; 
        font-weight: 800; font-size: 3.5rem; 
        margin-bottom: 0px; letter-spacing: 5px;
        text-transform: uppercase;
    }
    .nexus-subtitle { 
        text-align: center; color: #8b949e; 
        font-size: 1.2rem; font-weight: 400;
        margin-top: -10px; margin-bottom: 40px;
        letter-spacing: 2px;
    }

    /* Input Field Styling */
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; }
    
    /* Remove Avatars */
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    
    /* Sidebar Widgets */
    .sidebar-header { color: #58a6ff; font-weight: 700; font-size: 1.5rem; text-align: center; margin-bottom: 20px; }
    .status-online { color: #238636; font-size: 0.9rem; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE CORES ---
def init_system():
    try:
        S_URL = st.secrets["SUPABASE_URL"]
        S_KEY = st.secrets["SUPABASE_KEY"]
        G_KEYS = st.secrets["KEYS"]
        
        db = create_client(S_URL, S_KEY)
        # 6-Key Load Balancing
        ai_engine = Groq(api_key=random.choice(G_KEYS))
        
        # Tools
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

# --- 3. CORE LOGIC ---
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
    except: return "Document Error."

# --- 4. CONTROL PANEL (Sidebar) ---
st.sidebar.markdown("<p class='sidebar-header'>🌐 NEXUS CONTROL</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p class='status-online'>SYSTEM ONLINE</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Secure Login
user_identity = st.sidebar.text_input(" ACCESS KEY (GMAIL)", placeholder="user@gmail.com")

if user_identity:
    if "session_id" not in st.session_state or st.session_state.session_id != user_identity:
        with st.spinner("Syncing Cloud Memory..."):
            data = sync_load(user_identity)
            st.session_state.messages = data if data else [{"role": "assistant", "content": f"Nexus Authorized: {user_identity}"}]
            st.session_state.session_id = user_identity
        st.sidebar.success("Memory Linked")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Authentication required."}]

st.sidebar.markdown("---")
st.sidebar.subheader("Tools")
doc_file = st.sidebar.file_uploader("Document Analysis (PDF)", type=['pdf'])

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align:center; color:#8b949e; font-size:0.8rem;'>Lead Developer: Abhishek</p>", unsafe_allow_html=True)

# --- 5. DASHBOARD ---
st.markdown("<h1 class='nexus-title'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='nexus-subtitle'>Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("---")

# Render Logs
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. INTELLIGENCE ENGINE ---
if query := st.chat_input("Enter Command..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        # Context Injection
        context = ""
        if doc_file:
            context = f"\n[Doc Context]: {read_document(doc_file)[:1500]}"
            
        # Tool: Web Search
        if ("search" in query.lower() or "online" in query.lower()) and tavily:
            with st.spinner("Accessing Global Intel"):
                web_raw = tavily.search(query=query)
                web_info = "\n".join([f"- {r['content']}" for r in web_raw['results']])
                query += f"\n\n[Web Data]: {web_info}"

        # Tool: Vision Gen
        if "generate image" in query.lower() and openai:
            with st.spinner("Processing Vision Engine"):
                url = openai.images.generate(model="dall-e-3", prompt=query).data[0].url
                st.image(url)
                st.session_state.messages.append({"role": "assistant", "content": f"Vision Resource: {url}"})

        # Identity & Precision Logic
        system_logic = (
            "Identity: NEXUS AI. "
            "Developer: Abhishek. "
            "Abhishek Profile: Software Developer, Data Science Student, Python Expert, AI Architect. "
            "Skills: Expert in LLM orchestration, Linux systems, and automation. "
            "Response Protocol: High-precision, zero emojis (except 🌐), strictly professional. "
            f"{context}"
        )
        
        history_chain = [{"role": "system", "content": system_logic}] + st.session_state.messages
        
        with st.spinner(""):
            if groq_client:
                result = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history_chain,
                    temperature=0.3
                ).choices[0].message.content
                
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
                
                if user_identity:
                    sync_save(user_identity, st.session_state.messages)
