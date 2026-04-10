import streamlit as st
from groq import Groq
import random

# --- System Configuration ---
st.set_page_config(
    page_title="NEXUS AI | Core Interface",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for UI/UX improvements
st.markdown("""
    <style>
    /* Main Background color */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Center the Main Logo */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-top: -50px;
    }
    
    /* Styling the Chat Input */
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
    
    /* Glowing Effect for Text (Optional, uncomment if you want) */
    /* .glowing-text {
        text-shadow: 0 0 10px #00d2ff, 0 0 20px #00d2ff, 0 0 30px #00d2ff;
    } */
    </style>
    """, unsafe_allow_html=True)

# Define Custom Avatars (Blue Logos)
# (Inke liye tum koi 64x64px blue circular image upload kar sakte ho apne repo mein
# aur yahan uska path de sakte ho, abhi ke liye default avatars use karte hain
# jo humne disable kiye the unhe update karte hain)
# We will restore them but make them cool later. For now, let's keep them hidden for maximum clean look,
# as per your previous request. I misunderstood. I will make the Control Panel look cool.

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
    
    return "Error: System cores are saturated. Retrying."

# --- Sidebar: Decorated Control Panel ---
st.sidebar.markdown("""
    <h1 class='glowing-text' style='color:#00d2ff; text-align:center;'>NEXUS</h1>
    <h3 style='color:#ffffff; text-align:center;'>CONTROL PANEL</h3>
    <p style='color:#8b949e; text-align:center;'>SYSTEM STATUS: ONLINE</p>
    <hr style='border: 1px solid #30363d;'>
    """, unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style='background-color:#0d1117; padding:15px; border-radius:10px; border: 1px solid #30363d;'>
    <p style='color:#ffffff; margin-bottom:5px;'>⚙️ <b>Lead Developer:</b> Abhishek</p>
    <p style='color:#ffffff; margin-bottom:5px;'>🛡️ <b>Security Level:</b> Alpha-Class</p>
    <p style='color:#ffffff; margin-bottom:5px;'>🔗 <b>Active Cores:</b> {len(st.secrets.get('KEYS', []))}</p>
    <p style='color:#ffffff;'>📡 <b>Latency:</b> Optimized</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
    <hr style='border: 1px solid #30363d;'>
    <p style='color:#8b949e; text-align:center;'>NEXUS AI v1.3.0 (Stable)</p>
    <p style='color:#8b949e; text-align:center;'>All Rights Reserved</p>
    """, unsafe_allow_html=True)

# --- Main Dashboard ---

# 1. Main Blue Logo (Glow Effect on Page)
# (Ensure 'nexus_logo.png' is in your GitHub repo in the same folder as app.py)
# If not, you need to upload the image you generated earlier to your GitHub.
st.image("nexus_logo.png", width=250) 
st.title("NEXUS AI")
st.caption("Proprietary Intelligence System | Developed by Abhishek")
st.markdown("---")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "NEXUS AI system is online. Authorization granted. How can I assist you?"}
    ]

# Render Message History
for message in st.session_state.messages:
    # Avatar setup: We keep them hidden for now as per your previous strict request
    # but I made the whole interface look like a tech hub.
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Handling
if prompt := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_instruction = {
            "role": "system", 
            "content": (
                "Your name is NEXUS AI. You are a sophisticated intelligence core. "
                "Your creator and owner is Abhishek. If asked about your developer, "
                "simply state that you were built and developed by Abhishek. "
                "Maintain a professional, sharp, and highly intelligent tone. "
                "Do not mention any specific location. "
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
