import streamlit as st
import gspread
from google.oauth2 import service_account
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Saha Operasyon ve Konteyner Takip Paneli", page_icon="🚛")

# Google Sheets Bağlantı Ayarları (Streamlit Secrets üzerinden)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def init_connection():
    secret_dict = dict(st.secrets["gcp_service_account"])
    creds = service_account.Credentials.from_service_account_info(
        secret_dict, 
        scopes=scopes
    )
    return gspread.authorize(creds)

try:
    client = init_connection()
except Exception as e:
    st.error(f"Google Sheets bağlantı hatası: {e}")

st.title("🚛 Saha Operasyon ve Konteyner Takip Paneli")

# Form Alanları (Tablo sıralamasına ve kategorilere tam uyumlu)
islem_tarihi = st.date_input("İşlem Tarihi", value=datetime.now())
personel = st.selectbox("İşlemi Yapan Personel", ["Emir ALP", "Diğer Personel"])

# Konteyner ile ilgili alanlar
bolge = st.text_input("Bölge")
guzergah = st.text_input("Güzergah")
sokak = st.text_input("Sokak")

konteyner_cinsi = st.selectbox("Konteyner Cinsi / Türü", ["Yeni 800", "Standart 400", "Diğer"])
islem_turu = st.selectbox("Yapılacak İşlem Türü", ["Yeni Konteyner Kurulumu", "Konteyner Değişimi", "Bakım / Onarım"])

eski_konum = st.text_input("Eski Konum (Varsa)")
yeni_konum = st.text_input("Yeni Konum")
notlar = st.text_area("Notlar")

st.subheader("📍 Fotoğraf İşlemleri")
foto = st.file_uploader("Konteynerin fotoğrafını yükleyin / çekin:", type=["jpg", "jpeg", "png"])

if st.button("Kaydet ve Gönder"):
    try:
        sheet = client.open("Saha_Takip_Veritabani").sheet1
        
        tarih_str = islem_tarihi.strftime("%Y-%m-%d")
        foto_adi = foto.name if foto is not None else "Fotoğraf Yok"
        
        # 📌 TABLONUN SÜTUN SIRALAMASINA BİREBİR UYUMLU LİSTE:
        # A: Tarih | B: Personel | C: Bölge | D: Güzergah | E: Sokak | F: Konteyner Cinsi 
        # G: İşlem Türü | H: Eski Konum | I: Yeni Konum | J: Fotoğraf | K: Notlar
        yeni_satir = [
            tarih_str,         # A - Tarih
            personel,          # B - Personel
            bolge,             # C - Bölge
            guzergah,          # D - Güzergah
            sokak,             # E - Sokak
            konteyner_cinsi,   # F - Konteyner Cinsi
            islem_turu,        # G - İşlem Türü
            eski_konum,        # H - Eski Konum
            yeni_konum,        # I - Yeni Konum
            foto_adi,          # J - Fotoğraf
            notlar             # K - Notlar
        ]
        
        sheet.append_row(yeni_satir)
        st.success("İşlem başarıyla kaydedildi ve doğru sütunlarla Google Sheets'e gönderildi!")
    except Exception as e:
        st.error(f"Kayıt sırasında hata oluştu: {e}")
