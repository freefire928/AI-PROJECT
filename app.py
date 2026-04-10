import streamlit as st
from groq import Groq
import random

# --- System Configuration ---
st.set_page_config(
    page_title="NEXUS AI | Core Interface",
    page_icon="None",
    layout="wide"
)

# --- Core Engine Logic ---
def execute_query(messages):
    """
    Handles API rotation and request execution.
    """
    api_pool = st.secrets.get("KEYS", [])
    
    # Shuffle pool to balance load across all 6 keys
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
            # Handle rate limiting by switching to the next available key
            if "429" in str(e):
                continue
            else:
                return f"Internal System Error: {str(e)}"
    
    return "Error: All processing cores are currently saturated. Retrying in 60 seconds."

# --- Interface Layout ---
st.title("NEXUS AI")
st.subheader("High-Performance Intelligence Core")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("System Parameters")
st.sidebar.text(f"Status: Operational")
st.sidebar.text(f"Active Cores: {len(st.secrets.get('KEYS', []))}")
st.sidebar.markdown("---")
st.sidebar.write("Developed by: Abhishek")
st.sidebar.write("Version: 1.1.0 (Stable)")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "NEXUS AI system is online and stabilized. How may I assist you today?"}
    ]

# Render Message History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Handling
if prompt := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # System instructions for persona consistency
        system_instruction = {
            "role": "system", 
            "content": (
                "You are NEXUS AI, a sophisticated intelligence core developed by Abhishek. "
                "Provide direct, factual, and high-quality responses. Maintain a professional tone. "
                "Conclude every response with the identifier: NEXUS AI"
            )
        }
        
        # Construct full context
        conversation_context = [system_instruction] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        
        with st.spinner("Processing request..."):
            response_content = execute_query(conversation_context)
            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})
