import os
import io
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO
import streamlit as st
from groq import Groq

load_dotenv()
api_key = None

try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GROQ_API_KEY")

CHATS_FILE = "user_chats.json"

def load_data(filename, default_type="list"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if default_type == "dict" and isinstance(data, dict):
                    return data
                elif default_type == "list" and isinstance(data, list):
                    return data
            except:
                pass
    return {} if default_type == "dict" else []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

st.set_page_config(page_title="EymenX", page_icon="🌰", layout="wide")

# BEYAZ KISIMLARI VE SEÇİM MENÜLERİNİ KOYU YEŞİL YAPAN GÜÇLÜ CSS
st.markdown("""
    <style>
    /* Üst bar ve ana arayüz */
    header[data-testid="stHeader"] {
        background-color: #142219 !important;
    }
    .stApp {
        background-color: #142219;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #142219;
        border-right: 1px solid #1f3527;
    }
    
    /* Model seçme ve açılır menü (selectbox) arka planı ve yazısı */
    div[data-baseweb="select"] > div {
        background-color: #1b2e23 !important;
        color: #ffffff !important;
        border: 1px solid #2d4a38 !important;
    }
    span {
        color: #ffffff !important;
    }
    
    /* Butonlar */
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 16px !important;
        font-weight: 600;
        border-radius: 10px;
        background-color: #1b2e23;
        color: #ffffff;
        border: 1px solid #2d4a38;
    }
    .stButton>button:hover {
        background-color: #2d4a38;
        border-color: #d4af37;
        color: #d4af37;
    }
    
    /* Sekmeler */
    .stTabs [data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold;
        padding: 10px 20px;
        color: #a3b8ad;
    }
    
    /* Başlıklar */
    h1, h2, h3 {
        color: #d4af37 !important;
    }
    
    /* Sohbet mesajları ve yazı alanları */
    .stTextInput input, .stTextArea textarea, .stChatInput input {
        background-color: #1b2e23 !important;
        color: #ffffff !important;
        border: 1px solid #2d4a38 !important;
        border-radius: 10px;
    }
    
    /* Sohbet baloncukları metin rengi */
    div[data-testid="stChatMessage"] {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

if not api_key:
    st.error("GROQ_API_KEY bulunamadı!")
    st.stop()

client = Groq(api_key=api_key)

@st.cache_data(ttl=3600)
def get_groq_models():
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data if "whisper" not in m.id and "safetensors" not in m.id]
        return sorted(model_ids)
    except Exception:
        return ["llama-3.3-70b-versatile", "llama3-8b-8192"]

# SOL MENÜ
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("### 🌰 EymenX")
    
    st.divider()
    ai_persona = st.selectbox("AI Modu:", ["Genel Asistan", "Matematik Hocası", "Kodlama Rehberi", "Siber Güvenlik Uzmanı"])
    persona_prompts = {
        "Genel Asistan": "Sen EymenX adlı kişisel yapay zeka asistanısın. Türkçe, net ve samimi yanıtlar ver.",
        "Matematik Hocası": "Sen sabırlı bir matematik öğretmenisin. Adım adım anlat.",
        "Kodlama Rehberi": "Sen bir Python ve yazılım öğretmenisin. Kod örnekleri ver.",
        "Siber Güvenlik Uzmanı": "Sen siber güvenlik uzmanısın. Güvenlik kurallarını öğret."
    }

    st.divider()
    available_models = get_groq_models()
    default_index = 0
    for idx, model_name in enumerate(available_models):
        if "70b" in model_name or "versatile" in model_name:
            default_index = idx
            break
            
    selected_model = st.selectbox("Model Seçin:", available_models, index=default_index)

    st.divider()
    if st.button("🗑️ Sohbetimi Temizle"):
        chats_data = load_data(CHATS_FILE, "dict")
        chats_data["default_user"] = []
        save_data(CHATS_FILE, chats_data)
        st.rerun()

st.title("EymenX AI Asistan & Bilişim Lab")
st.caption("Kişisel Yapay Zeka ve Geliştirme Platformu")
st.markdown("---")

tab_chat, tab_code, tab_quiz = st.tabs(["💬 Yapay Zeka Sohbet", "💻 Python Kodu Çalıştır", "🏆 Günün Bilişim Soruları"])

current_user = "default_user"

# TAB 1: SOHBET
with tab_chat:
    chats_data = load_data(CHATS_FILE, "dict")
    if current_user not in chats_data:
        chats_data[current_user] = []

    for msg in chats_data[current_user]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    st.write("⚡ **Hızlı Sorular:**")
    col1, col2, col3 = st.columns(3)
    user_prompt = None

    if col1.button("🐍 Python Nedir?"):
        user_prompt = "Python programlama dili nedir, nerelerde kullanılır?"
    if col2.button("🤖 Algoritma Örneği"):
        user_prompt = "Bana günlük hayattan basit ve eğlenceli bir algoritma örneği ver."
    if col3.button("🔐 Siber Güvenlik İpucu"):
        user_prompt = "Güçlü şifre oluşturmak için 3 önemli ipucu ver."

    chat_input = st.chat_input("EymenX'e bir şeyler yazın...")
    if chat_input:
        user_prompt = chat_input

    if user_prompt:
        chats_data[current_user].append({"role": "user", "content": user_prompt})
        save_data(CHATS_FILE, chats_data)
        
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("EymenX düşünüyor..."):
                try:
                    start_time = time.time()
                    sys_prompt = {"role": "system", "content": persona_prompts[ai_persona]}
                    formatted_msgs = [sys_prompt] + [{"role": m["role"], "content": m["content"]} for m in chats_data[current_user]]

                    completion = client.chat.completions.create(
                        model=selected_model,
                        messages=formatted_msgs,
                        stream=False
                    )

                    elapsed = round(time.time() - start_time, 2)
                    reply = completion.choices[0].message.content
                    full_reply = f"{reply}\n\n---\n⏱️ *Yanıt Süresi: {elapsed} saniye | Model: {selected_model}*"
                    
                    st.write(full_reply)
                    
                    chats_data[current_user].append({"role": "assistant", "content": full_reply})
                    save_data(CHATS_FILE, chats_data)
                    st.rerun()

                except Exception as e:
                    st.error(f"API Hatası: {e}")

# TAB 2: PYTHON PLAYGROUND
with tab_code:
    st.subheader("💻 Canlı Python Kod Derleyicisi")
    default_code = 'print("Merhaba EymenX!")\nfor i in range(1, 4):\n    print(f"Bilişim Adım: {i}")'
    user_code = st.text_area("Python Kodunuz:", value=default_code, height=180)
    if st.button("▶️ Kodu Çalıştır"):
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        try:
            exec(user_code)
            sys.stdout = old_stdout
            st.success("✅ Kod Başarıyla Çalıştı!")
            st.code(redirected_output.getvalue(), language="python")
        except Exception as err:
            sys.stdout = old_stdout
            st.error(f"❌ Hata: {err}")

# TAB 3: QUIZ
with tab_quiz:
    st.subheader("🏆 Günün 3 Bilişim Yarışması")
    st.write("Soruları cevaplayın, doğru bildiğinizde konfeti patlasın!")
    
    def trigger_success():
        st.balloons()

    st.markdown("### 1️⃣ Soru: Python'da ekrana yazı yazdırma komutu hangisidir?")
    q1 = st.radio("Seçiminizi yapın (Soru 1):", ["input()", "print()", "write()", "echo()"], key="q1_k")
    if st.button("1. Soruyu Kontrol Et"):
        if q1 == "print()":
            st.success("🎉 Harika! 1. Soru Doğru!")
            trigger_success()
        else:
            st.error("❌ Yanlış! Tekrar deneyin.")

    st.divider()

    st.markdown("### 2️⃣ Soru: Bilgisayarda mantıksal işlem yapan ve 'beyin' olarak bilinen donanım nedir?")
    q2 = st.radio("Seçiminizi yapın (Soru 2):", ["RAM Bellek", "Sabit Disk (HDD)", "İşlemci (CPU)", "Ekran Kartı"], key="q2_k")
    if st.button("2. Soruyu Kontrol Et"):
        if q2 == "İşlemci (CPU)":
            st.success("🎉 Tebrikler! 2. Soru Doğru!")
            trigger_success()
        else:
            st.error("❌ Yanlış! İpucu: Merkezi işlem birimidir.")

    st.divider()

    st.markdown("### 3️⃣ Soru: Aşağıdakilerden hangisi güçlü ve güvenli bir şifrede mutlaka bulunmalıdır?")
    q3 = st.radio("Seçiminizi yapın (Soru 3):", ["Sadece doğum tarihiniz", "Büyük harf, küçük harf, rakam ve özel karakter", "Adınız ve soyadınız", "123456 sayısı"], key="q3_k")
    if st.button("3. Soruyu Kontrol Et"):
        if q3 == "Büyük harf, küçük harf, rakam ve özel karakter":
            st.success("🏆 Muhteşem! 3 Soru da Tamam! Tam Puan Kazandın!")
            trigger_success()
        else:
            st.error("❌ Yanlış! Güvenlik kurallarını gözden geçir.")