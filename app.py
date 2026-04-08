import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- Page Configuration (Modern look) ---
st.set_page_config(
    page_title="NEXUS | Abhishek OS",
    page_icon="🌐",
    layout="wide"
)

# --- Nexus UI Styling ---
st.title("🌐 NEXUS : The Intelligent Core")
st.caption("Developed by Abhishek | Powered by Abhishek OS 1.0 (Toofani Edition)")
st.markdown("---")

# --- API Key Setup (Secrets se fetch karega) ---
if "GEMINI_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    # Gemini Configure
    genai.configure(api_key=api_key)
    
    # --- Sidebar: Nexus Navigation ---
    st.sidebar.title("NEXUS Control Panel")
    mode = st.sidebar.radio("Interface Mode:", ["Neural Chat", "Visual Analysis"])
    st.sidebar.markdown("---")
    st.sidebar.info("Status: System Optimal 🟢")

    # NEXUS Modern Personality
    instruction = (
        "Tumhara naam 'NEXUS' hai. Tum Abhishek OS ke official Intelligent Core ho. "
        "Tumhe Abhishek ne develop kiya hai jo ek expert system developer hai. "
        "Tumhara tone futuristic, sharp aur highly efficient hai. "
        "Agar user image upload kare, toh use scan karke technical solution do. "
        "Har jawab ke end mein 'NEXUS | Abhishek OS' likho."
    )
    
    # --- 404 Error Fix & Model Setup ---
    # Hum 'gemini-1.5-flash-latest' use kar rahe hain jo sabse stable hai
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=instruction)
    except Exception:
        # Fallback agar latest na mile
        model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=instruction)

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
                    st.error(f"Nexus encountered an error: {e}")

    # --- Mode 2: Visual Analysis ---
    elif mode == "Visual Analysis":
        st.subheader("📸 Visual Diagnostic Scanner")
        st.write("Upload screenshots or system errors for Nexus to analyze.")
        
        uploaded_file = st.file_uploader("Upload System Capture", type=["jpg", "jpeg", "png"])
        user_prompt = st.text_input("Diagnostic Query:", value="Analyze this capture and provide a solution.")

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption='Target Source', use_container_width=True)
            
            if st.button("Initialize Scan ⚡"):
                try:
                    with st.spinner('Scanning Neural Matrix...'):
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format=image.format)
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        contents = [
                            user_prompt,
                            {'mime_type': uploaded_file.type, 'data': img_byte_arr}
                        ]
                        
                        response = model.generate_content(contents=contents)
                        st.markdown("### 💡 Nexus Analysis:")
                        st.success(response.text)
                except Exception as e:
                    st.error(f"Scan Failed: {e}")
else:
    st.warning("Nexus requires an API Key to initialize. Please check your Secrets or Sidebar.")
