import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- Page Configuration ---
st.set_page_config(page_title="NEXUS | Abhishek OS", page_icon="🌐", layout="wide")

st.title("🌐 NEXUS : The Intelligent Core")
st.caption("Developed by Abhishek | High-Limit Mode Enabled 🚀")
st.markdown("---")

# --- API Key Setup ---
if "GEMINI_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    # Nexus Navigation
    st.sidebar.title("NEXUS Control Panel")
    mode = st.sidebar.radio("Interface Mode:", ["Neural Chat", "Visual Analysis"])
    
    # Modern Personality
    instruction = (
        "Tumhara naam 'NEXUS' hai. Tum Abhishek OS ke official Intelligent Core ho. "
        "Tumhe Abhishek ne develop kiya hai. Tumhara tone sharp aur efficient hai. "
        "Har jawab ke end mein 'NEXUS | Abhishek OS' likho."
    )

    # --- High Limit Model Selection ---
    # Hum 'gemini-1.5-flash' use kar rahe hain kyunki iski limit 1500 RPM tak ho sakti hai
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=instruction
    )

    # --- Mode 1: Neural Chat ---
    if mode == "Neural Chat":
        st.subheader("🧠 Neural Interface")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Accessing Nexus... Enter command:"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    with st.spinner('Processing...'):
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 Limit hit! Thoda wait karo, system refresh ho raha hai.")
                    else:
                        st.error(f"Error: {e}")

    # --- Mode 2: Visual Analysis ---
    elif mode == "Visual Analysis":
        st.subheader("📸 Visual Diagnostic Scanner")
        uploaded_file = st.file_uploader("Upload System Capture", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption='Target Source', use_container_width=True)
            if st.button("Initialize Scan ⚡"):
                try:
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=image.format)
                    contents = ["Analyze this and provide a solution.", {'mime_type': uploaded_file.type, 'data': img_byte_arr.getvalue()}]
                    response = model.generate_content(contents=contents)
                    st.success(response.text)
                except Exception as e:
                    st.error(f"Scan Failed: {e}")
else:
    st.warning("Nexus requires an API Key to initialize.")
