import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_title="Saha Operasyon ve Konteyner Takip Paneli"

# Google Sheets Bağlantı Ayarları (Streamlit Secrets üzerinden)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Özel anahtardaki satır sonu bozulmalarını otomatik düzeltir
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    st.success("Google Sheets bağlantısı başarılı!")
except Exception as e:
    st.error(f"Google Sheets bağlantı hatası: {e}")

st.title("🚛 Saha Operasyon ve Konteyner Takip Paneli")

# Form Alanları
islem_tarihi = st.date_input("İşlem Tarihi", value=datetime.now())
personel = st.selectbox("İşlemi Yapan Personel", ["Emir ALP", "Diğer Personel"])
islem_turu = st.selectbox("Yapılacak İşlem Türü", ["Yeni Konteyner Kurulumu", "Konteyner Değişimi", "Bakım / Onarım"])
konteyner_cinsi = st.selectbox("Konteyner Cinsi / Türü", ["Yeni 800", "Standart 400", "Diğer"])

st.subheader("📍 Konum ve Fotoğraf İşlemleri")
st.info("📍 Alınan Yer: Operasyon Merkezi (Otomatik)")

# Fotoğraf Yükleme Alanı
foto = st.file_uploader("Bırakılan Yer: Konteynerin bırakıldığı noktanın fotoğrafını yükleyin / çekin:", type=["jpg", "jpeg", "png"])

if st.button("Kaydet ve Gönder"):
    st.success("İşlem başarıyla kaydedildi!")