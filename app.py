import streamlit as st
from groq import Groq
import random

# --- System Configuration ---
st.set_page_config(
    page_title="NEXUS AI",
    page_icon="None",
    layout="wide"
)

# Custom CSS to hide the default robot/user icons (Avatars)
st.markdown("""
    <style>
    [data-testid="chatAvatarIcon-assistant"], 
    [data-testid="chatAvatarIcon-user"] {
        display: none !important;
    }
    .stChatMessage {
        padding-left: 0px !important;
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

# --- Sidebar: Clean Branding ---
st.sidebar.markdown("### NEXUS CONTROL PANEL")
st.sidebar.markdown("---")
st.sidebar.markdown("**Developed by:** Abhishek")
st.sidebar.markdown("**System:** NEXUS AI Core")
st.sidebar.markdown("---")
st.sidebar.text(f"Status: Operational")
st.sidebar.text(f"Active Cores: {len(st.secrets.get('KEYS', []))}")

# --- Main Interface ---
st.title("NEXUS AI")
st.caption("Proprietary Intelligence System")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "NEXUS AI system is online. How can I assist you?"}
    ]

for message in st.session_state.messages:
    # avatar=None se default logo hat jayega
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
                "Do not mention any address or specific location. "
                "Maintain a professional and sharp tone. "
                "Do not add any repetitive footers or signatures at the end of your responses."
            )
        }
        
        conversation_context = [system_instruction] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        
        with st.spinner("Processing..."):
            response_content = execute_query(conversation_context)
            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})
