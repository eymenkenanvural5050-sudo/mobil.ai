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

# KOYU YEŞİL TEMA VE EL YAZISI STİLİ CSS
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&display=swap" rel="stylesheet">
    <style>
    .cursive-text { 
        font-family: 'Caveat', cursive; 
        font-size: 28px; 
        color: #d4af37 !important; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5); 
    }
    /* Ana arayüz ve koyu yeşil tema */
    .stApp, [data-testid="stSidebar"], header[data-testid="stHeader"], .main {
        background-color: #142219 !important;
        color: #ffffff !important;
    }
    /* Sağ üst bayrak ve el yazısı alanı */
    .header-banner {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        padding: 5px 10px;
        margin-bottom: -15px;
    }
    /* Yan menü (Sidebar) içindeki logo */ 
    [data-testid="stSidebar"] img { 
        display: block; 
        margin-left: auto; 
        margin-right: auto; 
        max-width: 140px !important; 
        border-radius: 12px; 
    }
    /* Giriş kutuları */ 
    .stTextInput input, .stTextArea textarea, .stChatInput input, div[data-baseweb="select"] > div { 
        background-color: #1b2e23 !important; 
        color: #ffffff !important; 
        border: 1px solid #2d4a38 !important; 
        border-radius: 12px !important; 
    }
    /* Sohbet baloncukları */ 
    div[data-testid="stChatMessage"] { 
        background-color: #1b2e23 !important; 
        color: #ffffff !important; 
        border: 1px solid #2d4a38 !important; 
        border-radius: 14px !important; 
        padding: 12px; 
        margin-bottom: 10px; 
    } 
    div[data-testid="stChatMessage"] * { 
        color: #ffffff !important; 
    }
    /* Metin renkleri */ 
    p, span, label, div, li { 
        color: #ffffff !important; 
    }
    h1, h2, h3 { 
        color: #d4af37 !important; 
    }
    /* Buton tasarımı */ 
    .stButton>button { 
        width: 100%; 
        min-height: 3em; 
        font-size: 15px !important; 
        font-weight: 600; 
        border-radius: 12px; 
        background-color: #1b2e23; 
        color: #ffffff !important; 
        border: 1px solid #2d4a38; 
    } 
    .stButton>button:hover { 
        background-color: #2d4a38; 
        border-color: #d4af37; 
        color: #d4af37 !important; 
    }
    /* Mobilde küçük ekranlar için yazı boyutu ayarı */ 
    @media (max-width: 768px) { 
        .cursive-text { font-size: 20px !important; } 
    }
    </style>
""", unsafe_allow_html=True)

if not api_key:
    st.error("GROQ_API_KEY bulunamadı!")
    st.stop()

client = Groq(api_key=api_key)

FIXED_MODEL = "openai/gpt-oss-120b"

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
    st.info(f"🧠 **Model:**\n`{FIXED_MODEL}`")

    st.divider()
    if st.button("🗑️ Sohbeti Temizle"):
        chats_data = load_data(CHATS_FILE, "dict")
        chats_data["default_user"] = []
        save_data(CHATS_FILE, chats_data)
        st.rerun()

# SAĞ ÜST KÖŞE: GERÇEKÇİ DALGALANAN BAYRAK GÖRSELİ VE EL YAZISI
col_space, col_text, col_flag = st.columns([6, 3, 1.2])
with col_text:
    st.markdown('<div style="text-align: right; padding-top: 5px;"><span class="cursive-text">Cumhuriyet hürriyet demektir</span></div>', unsafe_allow_html=True)
with col_flag:
    if os.path.exists("bayrak.gif"):
        st.image("bayrak.gif", width=85)
    elif os.path.exists("bayrak.png"):
        st.image("bayrak.png", width=85)
    else:
        st.markdown("🇹🇷")

st.title("EymenX AI Asistan & Bilişim Lab")
st.caption("Kişisel Yapay Zeka ve Geliştirme Platformu")
st.markdown("---")

tab_chat, tab_code, tab_quiz = st.tabs(["💬 Sohbet", "💻 Python", "🏆 Quiz"])

current_user = "default_user"

with tab_chat:
    chats_data = load_data(CHATS_FILE, "dict")
    if current_user not in chats_data:
        chats_data[current_user] = []

    for msg in chats_data[current_user]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.write("⚡ **Hızlı Sorular:**")
    
    col1, col2, col3 = st.columns(3)
    user_prompt = None

    with col1:
        if st.button("🐍 Python Nedir?"):
            user_prompt = "Python programlama dili nedir, nerelerde kullanılır?"
    with col2:
        if st.button("🤖 Algoritma Örneği"):
            user_prompt = "Bana günlük hayattan basit ve eğlenceli bir algoritma örneği ver."
    with col3:
        if st.button("🔐 Güvenlik İpucu"):
            user_prompt = "Güçlü şifre oluşturmak için 3 önemli ipucu ver."

    chat_input = st.chat_input("EymenX'e bir şeyler yazın...")
    if chat_input:
        user_prompt = chat_input

    if user_prompt:
        chats_data[current_user].append({"role": "user", "content": user_prompt})
        save_data(CHATS_FILE, chats_data)
        
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("EymenX düşünüyor..."):
                try:
                    start_time = time.time()
                    sys_prompt = {"role": "system", "content": persona_prompts[ai_persona]}
                    formatted_msgs = [sys_prompt] + [{"role": m["role"], "content": m["content"]} for m in chats_data[current_user]]

                    completion = client.chat.completions.create(
                        model=FIXED_MODEL,
                        messages=formatted_msgs,
                        stream=False
                    )

                    elapsed = round(time.time() - start_time, 2)
                    reply = completion.choices[0].message.content
                    full_reply = f"{reply}\n\n---\n⏱️ *{elapsed}s | {FIXED_MODEL}*"
                    
                    st.markdown(full_reply)
                    
                    chats_data[current_user].append({"role": "assistant", "content": full_reply})
                    save_data(CHATS_FILE, chats_data)

                except Exception as e:
                    st.error(f"API Hatası: {e}")

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
            st.success("✅ Başarılı!")
            st.code(redirected_output.getvalue(), language="python")
        except Exception as err:
            sys.stdout = old_stdout
            st.error(f"❌ Hata: {err}")

with tab_quiz:
    st.subheader("🏆 Günün 3 Bilişim Yarışması")
    
    def trigger_success():
        st.balloons()

    st.markdown("### 1️⃣ Python ekrana yazdırma komutu?")
    q1 = st.radio("Seçenekler:", ["input()", "print()", "write()", "echo()"], key="q1_k")
    if st.button("1. Soruyu Kontrol Et"):
        if q1 == "print()":
            st.success("🎉 Doğru!")
            trigger_success()
        else:
            st.error("❌ Yanlış!")

    st.divider()

    st.markdown("### 2️⃣ 'Beyin' olarak bilinen donanım?")
    q2 = st.radio("Seçenekler:", ["RAM", "HDD", "İşlemci (CPU)", "Ekran Kartı"], key="q2_k")
    if st.button("2. Soruyu Kontrol Et"):
        if q2 == "İşlemci (CPU)":
            st.success("🎉 Doğru!")
            trigger_success()
        else:
            st.error("❌ Yanlış!")

    st.divider()

    st.markdown("### 3️⃣ Güvenli şifrede ne olmalıdır?")
    q3 = st.radio("Seçenekler:", ["Sadece doğum tarihi", "Büyük/küçük harf, rakam, özel karakter", "Ad ve soyad", "123456"], key="q3_k")
    if st.button("3. Soruyu Kontrol Et"):
        if q3 == "Büyük/küçük harf, rakam, özel karakter":
            st.success("🏆 Tebrikler, Tam Puan!")
            trigger_success()
        else:
            st.error("❌ Yanlış!")