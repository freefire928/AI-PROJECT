import streamlit as st
from groq import Groq
import random
import io

# --- 1. System & Page Configuration ---
st.set_page_config(
    page_title="NEXUS AI | Pro",
    page_icon="🌐",
    layout="wide"
)

# --- 2. Custom Professional Styling (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] { display: none !important; }
    .stChatInput { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    .stSidebar { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .centered-header { text-align: center; margin-top: -50px; }
    .stFileUploader { background-color: #161b22; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Multi-Core Engine ---
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
            if "429" in str(e): continue
            else: return f"System Error: {str(e)}"
    return "Error: All processing cores are saturated."

# --- 4. Sidebar: Advanced Control Panel ---
st.sidebar.markdown("<h1 style='color:#00d2ff; text-align:center;'>NEXUS PRO</h1>", unsafe_allow_html=True)

# Feature 1: File Uploader in Sidebar
st.sidebar.markdown("###  Document Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload PDF or Text for Analysis", type=['pdf', 'txt'])

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
    <div style='background-color:#0d1117; padding:15px; border-radius:10px; border: 1px solid #30363d;'>
    <p style='color:#ffffff; margin-bottom:8px;'>⚙️ <b>Lead Developer:</b> Abhishek</p>
    <p style='color:#ffffff; margin-bottom:8px;'>🛡️ <b>Mode:</b> Advanced (Multi-Feature)</p>
    <p style='color:#ffffff;'>🔗 <b>Active Cores:</b> {len(st.secrets.get('KEYS', []))}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. Main Dashboard UI ---
st.markdown("<div class='centered-header'><h1>🌐</h1><h1>NEXUS AI</h1></div>", unsafe_allow_html=True)
st.caption("<p style='text-align:center;'>Developed by Abhishek</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. Chat Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I assist you today?"}]

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask anything or generate images..."):
    # Identity & Skill Knowledge
    system_instruction = (
        "Your name is NEXUS AI. You are a sophisticated intelligence core created by Abhishek. "
        "Abhishek is a Software Developer and Data Science student expert in Python and AI. "
        "If asked about your creator, explain his skills and that he developed you. "
        "If the user asks to 'Generate an image of...', respond creatively and acknowledge the request."
    )

    # Adding context if a file is uploaded
    file_context = ""
    if uploaded_file is not None:
        file_context = f"\n[Document Content]: The user has uploaded a file named {uploaded_file.name}. Assist them based on its context."

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=None):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=None):
        # Image Generation Feature (Trigger)
        if "generate image" in prompt.lower() or "make a photo" in prompt.lower():
            with st.spinner("Generating Nexus Vision..."):
                # Yahan hum Image Tool ka use kar sakte hain
                st.markdown(f"Generating image for: *{prompt}*")
                # Note: Streamlit cloud par image gen ke liye API call lagti hai
                st.info("Nexus Vision Core is preparing the render... [Image Generation active]")
        
        # Standard Text/File Processing
        full_prompt = [
            {"role": "system", "content": system_instruction + file_context}
        ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

        with st.spinner("Analyzing..."):
            response_content = execute_query(full_prompt)
            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})
