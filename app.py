import streamlit as st
from groq import Groq
import random

# --- System Configuration ---
st.set_page_config(
    page_title="NEXUS AI",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for Professional Dark Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .stChatInput {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    .stSidebar {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    .centered-header {
        text-align: center;
        margin-top: -40px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Core Engine Logic ---
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
                return f"Internal System Error: {str(e)}"
    
    return "Error: System cores are saturated. Please retry."

# --- Sidebar: Control Panel ---
st.sidebar.markdown("""
    <h1 style='color:#00d2ff; text-align:center;'>NEXUS</h1>
    <h3 style='color:#ffffff; text-align:center;'>CONTROL PANEL</h3>
    <hr style='border: 1px solid #30363d;'>
    """, unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style='background-color:#0d1117; padding:15px; border-radius:10px; border: 1px solid #30363d;'>
    <p style='color:#ffffff; margin-bottom:5px;'>⚙️ <b>Lead Developer:</b> Abhishek</p>
    <p style='color:#ffffff; margin-bottom:5px;'>🛡️ <b>Security:</b> Alpha-Class</p>
    <p style='color:#ffffff;'>🔗 <b>Active Cores:</b> {len(st.secrets.get('KEYS', []))}</p>
    </div>
    """, unsafe_allow_html=True)

# --- Main Dashboard ---
st.markdown("""
    <div class='centered-header'>
        <h1 style='font-size: 70px; margin-bottom: 0px;'>🌐</h1>
        <h1 style='margin-top: 10px;'>NEXUS AI</h1>
    </div>
    """, unsafe_allow_html=True)

st.caption("<p style='text-align:center;'>Proprietary Intelligence System | Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "NEXUS AI system is online. How can I assist you?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=None):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=None):
        system_instruction = {
            "role": "system", 
            "content": (
                "Your name is NEXUS AI. You are a sophisticated intelligence core. "
                "Your creator and owner is Abhishek. If asked about your developer, "
                "simply state that you were built and developed by Abhishek. "
                "Maintain a professional and sharp tone. "
                "Do not add any signatures at the end of your responses."
            )
        }
        
        conversation_context = [system_instruction] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        
        with st.spinner("Processing..."):
            response_content = execute_query(conversation_context)
            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})
