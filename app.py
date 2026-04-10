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
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .stSidebar { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 5px; }
    
    /* Remove default avatars */
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    
    /* Dashboard Header */
    .nexus-title { text-align: center; color: #58a6ff; font-weight: 700; font-size: 3rem; margin-bottom: 0px; letter-spacing: 3px; }
    .nexus-subtitle { text-align: center; color: #8b949e; font-size: 1.1rem; margin-top: -10px; margin-bottom: 30px; }
    
    /* Sidebar styling */
    .sidebar-brand { text-align: center; color: #58a6ff; font-weight: 600; font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE SERVICES ---
def init_system():
    try:
        S_URL = st.secrets["SUPABASE_URL"]
        S_KEY = st.secrets["SUPABASE_KEY"]
        G_KEYS = st.secrets["KEYS"]
        
        db = create_client(S_URL, S_KEY)
        ai_engine = Groq(api_key=random.choice(G_KEYS))
        
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

# --- 3. CLOUD MEMORY LOGIC ---
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

# --- 4. SIDEBAR: AUTHENTICATION & TOOLS ---
st.sidebar.markdown("<p class='sidebar-brand'>🌐 NEXUS AI</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

user_identity = st.sidebar.text_input("Gmail Login", placeholder="email@gmail.com")

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
st.sidebar.subheader("Tools")
doc_file = st.sidebar.file_uploader("Attach PDF", type=['pdf'])

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 class='nexus-title'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='nexus-subtitle'>Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("---")

# Render Conversation
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
            context_data = f"\n[User Document Context]: {read_document(doc_file)[:1500]}"
            
        # Web Search
        if ("search" in query.lower() or "online" in query.lower()) and tavily:
            with st.spinner("Searching Web"):
                web_raw = tavily.search(query=query)
                web_info = "\n".join([f"- {r['content']}" for r in web_raw['results']])
                query += f"\n\n[Web Data Found]: {web_info}"

        # Vision Generation
        if "generate image" in query.lower() and openai:
            with st.spinner("Rendering Vision"):
                url = openai.images.generate(model="dall-e-3", prompt=query).data[0].url
                st.image(url)
                st.session_state.messages.append({"role": "assistant", "content": f"Vision Resource: {url}"})

        # Final AI Response with Developer Identity
        system_logic = (
            "You are NEXUS AI. You were developed by Abhishek. "
            "Abhishek is a Software Developer and Data Science student. "
            "Skills of Abhishek: Python expert, AI application developer, Linux (Ubuntu/Abhishek OS) specialist, and Data Science expert. "
            "Task: Provide high-precision workstation responses without extra emojis. "
            f"{context_data}"
        )
        
        history_chain = [{"role": "system", "content": system_logic}] + st.session_state.messages
        
        with st.spinner("Processing"):
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
            else:
                st.error("System Offline")
