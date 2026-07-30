import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_title="Saha Operasyon ve Konteyner Takip Paneli"

# Google Sheets Bağlantı Ayarları (Streamlit Secrets üzerinden)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

try:
    # Streamlit secrets kullanarak güvenli kimlik doğrulama
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # E-Tablo bağlantısı (Örn: Google Drive'daki dosya adın neyse buraya yazabilirsin veya ana tablo)
    # sheet = client.open("Saha_Takip_Veritabani").sheet1
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
    st.success("İşlem başarıyla kaydedildi! (Test modu)")