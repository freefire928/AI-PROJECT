import streamlit as st
from groq import Groq

# --- Page Config ---
st.set_page_config(page_title="NEXUS | Abhishek OS", page_icon="🌐", layout="wide")

# Custom CSS for "Rola"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 NEXUS : The Intelligent Core")
st.caption("🚀 High-Performance AI System | Developed by Abhishek")

# --- API Key Fetch ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

if api_key:
    try:
        client = Groq(api_key=api_key)
        
        # NEXUS Persona
        system_prompt = (
            "Tumhara naam 'NEXUS' hai. Tum Abhishek OS ke Intelligent Core ho. "
            "Tumhe Abhishek ne develop kiya hai. Tumhara tone futuristic, smart aur helpful hai. "
            "Har jawab ke end mein 'NEXUS | Abhishek OS' likho."
        )

        # Sidebar with Developer Info
        st.sidebar.title("System Info")
        st.sidebar.success("Status: Online 🟢")
        st.sidebar.markdown("---")
        st.sidebar.write("**Developer:** Abhishek")
        st.sidebar.write("**OS Version:** 1.0 (Toofani)")
        st.sidebar.info("Ye AI Groq LPU engine par chalta hai, jo duniya ka sabse fast AI processor hai.")

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "System Online. Main NEXUS hoon. Main aapki kya madad kar sakta hoon?"}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Command bhejo..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "system", "content": system_prompt}] + 
                                 [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        model="llama-3.3-70b-versatile",
                    )
                    res_text = chat_completion.choices[0].message.content
                    st.markdown(res_text)
                    st.session_state.messages.append({"role": "assistant", "content": res_text})
                except Exception as e:
                    st.error(f"Sync Error: {e}")
    except Exception as e:
        st.error(f"Boot Error: {e}")
else:
    st.warning("Nexus is restricted. API Key required.")
