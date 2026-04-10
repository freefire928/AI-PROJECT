import streamlit as st
from groq import Groq
import random

# --- 1. System & Page Configuration ---
st.set_page_config(
    page_title="NEXUS AI | Core",
    page_icon="🌐",
    layout="wide"
)

# --- 2. Custom Professional Styling (CSS) ---
st.markdown("""
    <style>
    /* Dark Theme UI */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Hide Chat Icons for Minimalist Look */
    [data-testid="chatAvatarIcon-assistant"], 
    [data-testid="chatAvatarIcon-user"] {
        display: none !important;
    }
    
    /* Input Field Styling */
    .stChatInput {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    
    /* Professional Sidebar Styling */
    .stSidebar {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Header Alignment */
    .centered-header {
        text-align: center;
        margin-top: -50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Multi-Core Engine (API Rotation) ---
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
        except Exception as e:
            if "429" in str(e): 
                continue
            else:
                return f"System Error: {str(e)}"
    
    return "Error: All processing cores are saturated. Please wait 60 seconds."

# --- 4. Sidebar: Control Panel ---
st.sidebar.markdown("""
    <h1 style='color:#00d2ff; text-align:center; margin-bottom:0px;'>NEXUS</h1>
    <h4 style='color:#ffffff; text-align:center; margin-top:0px;'>CONTROL PANEL</h4>
    <hr style='border: 1px solid #30363d;'>
    """, unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style='background-color:#0d1117; padding:15px; border-radius:10px; border: 1px solid #30363d;'>
    <p style='color:#ffffff; margin-bottom:8px;'>⚙️ <b>Lead Developer:</b> Abhishek</p>
    <p style='color:#ffffff; margin-bottom:8px;'>🛡️ <b>Security:</b> Alpha-Class</p>
    <p style='color:#ffffff; margin-bottom:8px;'>🔗 <b>Active Cores:</b> {len(st.secrets.get('KEYS', []))}</p>
    <p style='color:#ffffff;'>📡 <b>Status:</b> Operational</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
    <br><br>
    <hr style='border: 1px solid #30363d;'>
    <p style='color:#8b949e; text-align:center; font-size:12px;'>NEXUS AI v1.3.7 Stable</p>
    """, unsafe_allow_html=True)

# --- 5. Main Dashboard UI ---
st.markdown("""
    <div class='centered-header'>
        <h1 style='font-size: 80px; margin-bottom: 0px;'>🌐</h1>
        <h1 style='margin-top: 10px; color:#ffffff;'>NEXUS AI</h1>
    </div>
    """, unsafe_allow_html=True)

# UPDATED: Clean Developer Attribution
st.caption("<p style='text-align:center;'>Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I assist you?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=None):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=None):
        # UPDATED: Identity Logic
        system_instruction = {
            "role": "system", 
            "content": (
                "Your name is NEXUS AI. You are a sophisticated intelligence core. "
                "Identity Information: You were developed and created solely by Abhishek. "
                "If anyone asks who created you, who is your developer, or who you are, "
                "you must clearly state: 'Mujhe Abhishek ne banaya hai. Wahi mere creator hain "
                "aur unhone hi NEXUS AI ko poori tarah se develop kiya hai.' "
                "Always maintain a professional, sharp, and respectful tone towards your creator, Abhishek."
            )
        }
        
        context = [system_instruction] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        
        with st.spinner("Processing..."):
            response_content = execute_query(context)
            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})
