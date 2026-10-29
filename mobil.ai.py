import os
import streamlit as st
from groq import Groq

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="EymenX",
    page_icon="🌰",
    layout="centered"
)

# 2. Özel Koyu Yeşil ve Şık Tasarım (CSS)
st.markdown("""
    <style>
    .stApp {
        background-color: #1b2e23;
        color: #e8ede9;
    }
    [data-testid="stSidebar"] {
        background-color: #142219;
    }
    h1, h2, h3 {
        color: #d4af37 !important;
    }
    .stTextInput input {
        background-color: #243b2f;
        color: #ffffff;
        border: 1px solid #324e3f;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Logo ve Başlık Alanı
col1, col2 = st.columns([1, 4])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    else:
        st.write("🌰")

with col2:
    st.title("EymenX")
    st.caption("Kişisel Yapay Zeka Asistanın")

st.markdown("---")

# 4. Groq API Bağlantısı (Streamlit Secrets'tan çeker)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Lütfen Streamlit Cloud Secrets bölümüne GROQ_API_KEY ekleyin!")
    st.stop()

# 5. Sohbet Geçmişi Yönetimi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekranda tutma
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Kullanıcı Girişi ve Yanıt Üretme
if prompt := st.chat_input("EymenX'e bir şeyler sor..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan yanıtı
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Groq API çağrısı (llama modelini kullanır)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Bir hata oluştu: {e}"
            message_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})