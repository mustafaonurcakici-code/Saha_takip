import streamlit as st
import gspread
from google.oauth2 import service_account
from datetime import datetime
import streamlit.components.v1 as components

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

# Form Alanları
islem_tarihi = st.date_input("İşlem Tarihi", value=datetime.now())
personel = st.selectbox("İşlemi Yapan Personel", ["Emir ALP", "Diğer Personel"], key="personel_secim")

# Konteyner Cinsi Seçimi
konteyner_cinsi = st.selectbox(
    "Konteyner Cinsi / Türü", 
    ["Yeni 800", "Standart 400", "Diğer"], 
    key="konteyner_cinsi_secim"
)

# Yapılacak İşlem Türü Seçimi
islem_turu = st.selectbox(
    "Yapılacak İşlem Türü", 
    ["Yeni Konteyner Kurulumu", "Konteyner Değişimi", "Bakım / Onarım"], 
    key="islem_turu_secim"
)

# 📍 Konum Bilgileri ve GPS / Konum Alma Çözümü
st.subheader("📍 Konum Bilgileri")
st.info("💡 Mobilde adres yazmak yerine tarayıcınızın konum özelliğini kullanabilirsiniz.")

# Tarayıcı konumunu otomatik çeken akıllı buton bileşeni
location_js = """
<div>
    <button onclick="getLocation()" style="background-color:#FF4B4B; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">
        📍 Telefonun Anlık Konumunu Al (GPS)
    </button>
    <p id="demo" style="margin-top:5px; font-size:14px; color:gray;"></p>
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else { 
            document.getElementById("demo").innerHTML = "Tarayıcınız konumu desteklemiyor.";
        }
    }
    function showPosition(position) {
        let coords = "Enlem: " + position.coords.latitude.toFixed(6) + ", Boylam: " + position.coords.longitude.toFixed(6);
        document.getElementById("demo").innerHTML = "Konum Alındı! Lütfen bunu aşağıdaki kutuya kopyalayın: <b>" + coords + "</b>";
    }
    function showError(error) {
        switch(error.code) {
            case error.PERMISSION_DENIED:
                alert("Konum izni reddedildi. Lütfen tarayıcı ayarlarından izin verin.");
                break;
            case error.POSITION_UNAVAILABLE:
                alert("Konum bilgisi alınamıyor.");
                break;
            case error.TIMEOUT:
                alert("İstek zaman aşımına uğradı.");
                break;
        }
    }
    </script>
</div>
"""
components.html(location_js, height=110)

alinan_nokta = st.text_input("Alınan Konteyner Noktası (Adres / Yukarıdan Konumu Kopyala)", key="alinan_nokta_input")
birakilan_nokta = st.text_input("Bırakılan Konteyner Noktası (Adres / Konum Tarifi)", key="birakilan_nokta_input")

notlar = st.text_area("Notlar", key="notlar_input")

st.subheader("📸 Fotoğraf İşlemleri")
foto = st.file_uploader("Konteynerin fotoğrafını yükleyin / çekin:", type=["jpg", "jpeg", "png"], key="foto_yukleme")

if st.button("Kaydet ve Gönder", key="kaydet_butonu"):
    try:
        # Google E-Tablo adını kendi tablo adınızla değiştirebilirsiniz
        sheet = client.open("Saha_Takip_Veritabani").sheet1
        
        tarih_str = islem_tarihi.strftime("%Y-%m-%d")
        foto_adi = foto.name if foto is not None else "Fotoğraf Yok"
        
        # 📌 SÜTUN SIRALAMASI:
        # A: Tarih | B: Personel | C: Konteyner Cinsi | D: İşlem Türü 
        # E: Alınan Nokta | F: Bırakılan Nokta | G: Fotoğraf | H: Notlar
        yeni_satir = [
            tarih_str,         # A - Tarih
            personel,          # B - Personel
            konteyner_cinsi,   # C - Konteyner Cinsi
            islem_turu,        # D - İşlem Türü
            alinan_nokta,      # E - Alınan Konteyner Noktası
            birakilan_nokta,   # F - Bırakılan Konteyner Noktası
            foto_adi,          # G - Fotoğraf
            notlar             # H - Notlar
        ]
        
        sheet.append_row(yeni_satir)
        st.success("İşlem başarıyla kaydedildi ve Google Sheets'e gönderildi!")
    except Exception as e:
        st.error(f"Kayıt sırasında hata oluştu: {e}")
