import streamlit as st
import random
import io
from groq import Groq
from PyPDF2 import PdfReader
from supabase import create_client

# --- 1. SYSTEM CONFIG & ELITE UI ---
st.set_page_config(page_title="NEXUS AI", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    /* Dark Slate Theme */
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    
    /* Sexy Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
        border-right: 1px solid #30363d;
    }
    
    /* Centered Dashboard Branding */
    .nexus-title { 
        text-align: center; color: #58a6ff; 
        font-weight: 800; font-size: 4rem; 
        margin-bottom: 0px; letter-spacing: 6px;
        text-transform: uppercase;
    }
    .nexus-subtitle { 
        text-align: center; color: #8b949e; 
        font-size: 1.2rem; font-weight: 400;
        margin-top: -10px; margin-bottom: 20px;
        letter-spacing: 1px;
    }
    .help-prompt {
        text-align: center; color: #c9d1d9;
        font-size: 1.8rem; font-weight: 300;
        margin-bottom: 50px;
    }

    /* Minimalist Elements */
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 4px; }
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    .sidebar-brand { text-align: center; color: #58a6ff; font-weight: 700; font-size: 1.8rem; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE ENGINES INITIALIZATION ---
def init_nexus_system():
    try:
        S_URL = st.secrets["SUPABASE_URL"]
        S_KEY = st.secrets["SUPABASE_KEY"]
        G_KEYS = st.secrets["KEYS"]
        
        db = create_client(S_URL, S_KEY)
        # Load balancing across 6 Groq cores
        ai_engine = Groq(api_key=random.choice(G_KEYS))
        
        tavily = None
        if "TAVILY_API_KEY" in st.secrets:
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
            
        openai = None
        if "OPENAI_API_KEY" in st.secrets:
            from openai import OpenAI
            openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            
        return db, ai_engine, tavily, openai
    except Exception as e:
        st.error(f"System Offline: Check Secrets Configuration.")
        return None, None, None, None

supabase, groq_client, tavily, openai = init_nexus_system()

# --- 3. CLOUD SYNC & UTILITIES ---
def sync_load(email):
    try:
        response = supabase.table('nexus_memory').select("history").eq("id", email).execute()
        return response.data[0]['history'] if response.data else None
    except: return None

def sync_save(email, history):
    try:
        supabase.table('nexus_memory').upsert({"id": email, "history": history}).execute()
    except: pass

def process_document(file):
    try:
        pdf = PdfReader(file)
        return " ".join([page.extract_text() for page in pdf.pages])
    except: return "Document Error."

# --- 4. CONTROL PANEL (Sidebar) ---
st.sidebar.markdown("<p class='sidebar-brand'>🌐 NEXUS</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Hybrid Access Logic
user_auth = st.sidebar.text_input("Access Key (Gmail)", placeholder="Optional for Cloud Sync")

if user_auth:
    if "session_user" not in st.session_state or st.session_state.session_user != user_auth:
        with st.spinner("Syncing..."):
            history = sync_load(user_auth)
            st.session_state.messages = history if history else [{"role": "assistant", "content": "Encrypted session active."}]
            st.session_state.session_user = user_auth
    st.sidebar.success("Cloud Synchronized")
else:
    if "session_user" in st.session_state:
        del st.session_state.session_user
        st.session_state.messages = [{"role": "assistant", "content": "Guest mode active."}]
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Guest mode active."}]
    st.sidebar.info("Guest Mode (No Save)")

st.sidebar.markdown("---")
st.sidebar.subheader("Intelligence Tools")
doc_upload = st.sidebar.file_uploader("Document Intel (PDF)", type=['pdf'])

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align:center; color:#8b949e; font-size:0.8rem;'>Developer: Abhishek</p>", unsafe_allow_html=True)

# --- 5. DASHBOARD LAYOUT ---
st.markdown("<h1 class='nexus-title'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='nexus-subtitle'>Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("<p class='help-prompt'>How can I help you?</p>", unsafe_allow_html=True)
st.markdown("---")

# Conversation Render
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. COMMAND EXECUTION CORE ---
if user_query := st.chat_input("Enter Command"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        # Context Injection
        doc_context = ""
        if doc_upload:
            doc_context = f"\n[Document Context]: {process_document(doc_upload)[:1500]}"
            
        # Web Search Module
        if ("search" in user_query.lower() or "online" in user_query.lower()) and tavily:
            with st.spinner(""):
                results = tavily.search(query=user_query)
                web_data = "\n".join([f"- {r['content']}" for r in results['results']])
                user_query += f"\n\n[Web Data]: {web_data}"

        # Vision Module
        if "generate image" in user_query.lower() and openai:
            with st.spinner(""):
                url = openai.images.generate(model="dall-e-3", prompt=user_query).data[0].url
                st.image(url)
                st.session_state.messages.append({"role": "assistant", "content": f"Vision Output: {url}"})

        # Final AI Logic & Personality
        system_protocol = (
            "Identity: NEXUS AI. Developed by Abhishek. "
            "Developer Profile: Abhishek is a Software Developer and Data Science student. "
            "Abhishek's Skills: Python expert, AI application architect, Linux/Ubuntu specialist. "
            "Constraint: STRICTLY NO EMOJIS (except 🌐). Professional workstation tone. "
            f"{doc_context}"
        )
        
        full_chain = [{"role": "system", "content": system_protocol}] + st.session_state.messages
        
        with st.spinner(""):
            if groq_client:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=full_chain,
                    temperature=0.3
                ).choices[0].message.content
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                if "session_user" in st.session_state:
                    sync_save(st.session_state.session_user, st.session_state.messages)
            else:
                st.error("Engine Connection Failure.")
