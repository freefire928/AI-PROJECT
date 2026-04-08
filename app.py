import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Abhishek OS: Multimodal Toofani AI",
    page_icon="⚡",
    layout="wide"
)

# --- App Title & Header ---
st.title("⚡ Abhishek OS: Multimodal Toofani AI Assistant")
st.markdown("---")

# --- API Key Setup (Safe Tarika) ---
# Streamlit Cloud ke Secrets mein 'GEMINI_KEY' naam se key dalo
if "GEMINI_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    # Gemini Configure
    genai.configure(api_key=api_key)
    
    # --- Side Bar: Mode Selection & File Upload ---
    st.sidebar.title("Configuration")
    mode = st.sidebar.radio("Mode Select Karo:", ["Chat Bot", "Image Analysis"])
    
    # System Instruction for Persona
    instruction = (
        "Tum Abhishek OS ke Multimodal Toofani AI ho. Tumhe Abhishek ne banaya hai. "
        "Agar user chat kare, toh confidence aur energy se jawab do. "
        "Agar user image upload kare (jaise screenshot ya error), toh use dhyaan se analyze karo, "
        "problem identify karo, aur technical solution (code snippets, commands) ke saath answer do. "
        "Har jawab ke end mein 'Abhishek OS Zindabad' likho."
    )
    
    # Model define karna (Using gemini-1.5-flash which is multimodal and good for free tier)
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=instruction)

    # --- Feature 1: Chat Bot Mode ---
    if mode == "Chat Bot":
        st.subheader(" Chat with Toofani AI")
        # Chat History Setup
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User Input
        if prompt := st.chat_input("Command do, Abhishek!"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    with st.spinner('Thinking like a hurricane...'):
                        # Chat mode uses only text contents
                        response = model.generate_content(prompt)
                        full_res = response.text
                        st.markdown(full_res)
                        st.session_state.messages.append({"role": "assistant", "content": full_res})
                except Exception as e:
                    if "429" in str(e):
                        st.error(" Limit hit! Bhai, thoda sabar karo (1 min wait). Free tier hai na!")
                    else:
                        st.error(f" Kuch gadbad ho gayi: {e}")

    # --- Feature 2: Image Analysis Mode ---
    elif mode == "Image Analysis":
        st.subheader(" Computer Bug Visualizer")
        st.markdown(
            "Apne computer ka error screenshot, terminal output, ya hardware ki photo upload karo. "
            "Abhishek's AI use dekhega aur solution batayega."
        )
        
        # File Uploader
        uploaded_file = st.file_uploader("Image Select Karo...", type=["jpg", "jpeg", "png"])
        
        # User input prompt for the image
        user_prompt = st.text_input("Kya problem hai? (Jaise: 'Isko fix karne ka command batao')", value="Isko dhyaan se dekho aur solution batao.")

        if uploaded_file is not None:
            # 1. Image ko display karna
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Screenshot/Image.', use_container_width=True)
            
            # 2. Image Analysis Button
            if st.button("Analyze Image "):
                # 3. Gemini ke liye Multimodal Content taiyar karna
                try:
                    with st.spinner('Analyzing the visual matrix...'):
                        # Gemini requires image data as bytes or a specific format
                        # Convert PIL image to bytes for API call
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format=image.format)
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        # Multimodal contents (List of items: prompt, image_data)
                        contents = [
                            user_prompt,
                            {'mime_type': uploaded_file.type, 'data': img_byte_arr}
                        ]
                        
                        # Generate content call with visual data
                        # Note: Instruction automatically applied because of how model was initialized
                        response = model.generate_content(contents=contents)
                        
                        # Display Solution
                        st.markdown("---")
                        st.markdown("###  Toofani AI ka Solution:")
                        st.success(response.text)
                        
                except Exception as e:
                    if "429" in str(e):
                        st.error(" Limit hit! Thoda wait karo (1 min).")
                    elif "404" in str(e):
                        st.error(" Model issue. 'gemini-1.5-flash' should work.")
                    else:
                        st.error(f" Kuch gadbad ho gayi: {e}")
        else:
            st.info("Pehle ek image upload karo.")

else:
    st.warning("Pehle Sidebar mein API Key dalo ya use secrets par configure karo!")
    st.markdown(
        "Deploy karne ke baad, Streamlit Cloud ke Settings > Secrets mein `GEMINI_KEY = 'YOUR_API_KEY'` add kar lena."
    )
