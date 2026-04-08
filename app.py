import streamlit as st
from groq import Groq

# --- Page Config ---
st.set_page_config(page_title="NEXUS | Abhishek OS", page_icon="🌐", layout="wide")

st.title("🌐 NEXUS : Hyper-Speed Core")
st.caption("Developed by Abhishek | Powered by Groq LPU™")
st.markdown("---")

# --- API Key Fetch (Secrets se) ---
# Pehle check karega ki Streamlit Secrets mein key hai ya nahi
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    # Backup: Agar secrets mein nahi hai toh sidebar se lega
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

if api_key:
    try:
        client = Groq(api_key=api_key)
        
        # NEXUS Persona
        system_prompt = (
            "Tumhara naam 'NEXUS' hai. Tum Abhishek OS ke Intelligent Core ho. "
            "Tumhe Abhishek ne develop kiya hai. Tumhara tone futuristic, sharp aur alpha hai. "
            "Har jawab ke end mein 'NEXUS | Abhishek OS' likho."
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User Input
        if prompt := st.chat_input("Command bhejo, Abhishek..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    with st.spinner('NEXUS is processing at light speed...'):
                        # Using llama-3.3-70b for best intelligence and speed
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": system_prompt},
                                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                            ],
                            model="llama-3.3-70b-versatile",
                        )
                        res_text = chat_completion.choices[0].message.content
                        st.markdown(res_text)
                        st.session_state.messages.append({"role": "assistant", "content": res_text})
                except Exception as e:
                    st.error(f"Nexus Sync Error: {e}")
    except Exception as e:
        st.error(f"Initialization Failed: {e}")
else:
    st.warning("Nexus is waiting for the Secret Key. Update it in Streamlit Secrets.")
