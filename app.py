import streamlit as st
import random
import io
from groq import Groq
from PyPDF2 import PdfReader
from supabase import create_client

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="NEXUS AI", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stSidebar { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE SERVICES ---
def get_service_clients():
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEYS = st.secrets["KEYS"]
    
    # Core Clients
    supabase = create_client(S_URL, S_KEY)
    groq_client = Groq(api_key=random.choice(G_KEYS))
    
    # Optional Clients (Tavily & OpenAI)
    tavily_client = None
    if "TAVILY_API_KEY" in st.secrets:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
        
    openai_client = None
    if "OPENAI_API_KEY" in st.secrets:
        from openai import OpenAI
        openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
    return supabase, groq_client, tavily_client, openai_client

supabase, groq_client, tavily, openai = get_service_clients()

# --- 3. HELPER FUNCTIONS ---
def load_memories(email):
    try:
        res = supabase.table('nexus_memory').select("history").eq("id", email).execute()
        return res.data[0]['history'] if res.data else None
    except: return None

def save_memories(email, history):
    try:
        supabase.table('nexus_memory').upsert({"id": email, "history": history}).execute()
    except: pass

def extract_pdf(file):
    reader = PdfReader(file)
    return "".join([p.extract_text() for p in reader.pages])

# --- 4. SIDEBAR (Tools & Login) ---
st.sidebar.title("🌐 NEXUS PRO")
user_email = st.sidebar.text_input("Gmail Login", placeholder="email@gmail.com")

if user_email:
    if "active_user" not in st.session_state or st.session_state.active_user != user_email:
        history = load_memories(user_email)
        st.session_state.messages = history if history else [{"role": "assistant", "content": f"System Ready for {user_email}"}]
        st.session_state.active_user = user_email
    st.sidebar.success("Cloud Memory Linked")
else:
    st.sidebar.warning("Login to save progress")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Welcome. Login to continue."}]

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Tools")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=['pdf'])
st.sidebar.caption("Developer: Abhishek")

# --- 5. MAIN INTERFACE ---
st.markdown("<h2 style='text-align: center;'>NEXUS AI WORKSTATION</h2>", unsafe_allow_html=True)
st.markdown("---")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. INTELLIGENCE LOGIC ---
if prompt := st.chat_input("Ask anything, search web, or generate images..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Context building
        file_data = ""
        if uploaded_file:
            file_data = f"\n[DOCUMENT DATA]: {extract_pdf(uploaded_file)[:1500]}"
        
        # Web Search Tool
        if ("search" in prompt.lower() or "online" in prompt.lower()) and tavily:
            with st.spinner("Searching the web..."):
                search_res = tavily.search(query=prompt)
                search_text = "\n".join([f"- {r['content']}" for r in search_res['results']])
                prompt += f"\n\n[WEB SEARCH RESULTS]:\n{search_text}"

        # Image Gen Tool
        if "generate image" in prompt.lower() and openai:
            with st.spinner("Generating Vision..."):
                img_url = openai.images.generate(model="dall-e-3", prompt=prompt).data[0].url
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": f"Image generated: {img_url}"})

        # Final AI Processing
        sys_prompt = [{"role": "system", "content": f"You are NEXUS AI, created by Abhishek (Software Developer). {file_data}"}]
        full_history = sys_prompt + st.session_state.messages
        
        with st.spinner("Processing..."):
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_history,
                temperature=0.7
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            if user_email:
                save_memories(user_email, st.session_state.messages)
