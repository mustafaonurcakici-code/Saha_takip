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
    try:
        # Google E-Tablo adını buraya yaz (Kendi tablo adınla değiştirmeyi unutma)
        sheet = client.open("Saha_Takip_Deposu").sheet1
        
        tarih_str = islem_tarihi.strftime("%Y-%m-%d")
        foto_adi = foto.name if foto is not None else "Fotoğraf Yok"
        
        # Tabloya eklenecek satır verileri
        yeni_satir = [tarih_str, personel, islem_turu, konteyner_cinsi, "Operasyon Merkezi", foto_adi]
        
        # Veriyi Google Sheets'e gönder
        sheet.append_row(yeni_satir)
        
        st.success("İşlem başarıyla kaydedildi ve Google Sheets'e gönderildi!")
    except Exception as e:
        st.error(f"Kayıt sırasında hata oluştu: {e}")