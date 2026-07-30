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

# 📍 Konum Bilgileri (Butona basınca direkt kutuya yazan akıllı sistem)
st.subheader("📍 Konum Bilgileri")
st.info("💡 'Konumu Al' butonuna bastığınızda enlem ve boylam bilgisi ilgili kutuya otomatik yazılacaktır.")

# Alınan Konum Alanı ve Butonu
st.write("**Alınan Konteyner Noktası**")
alinan_nokta = st.text_input("Alınan Nokta", key="alinan_nokta_input", label_visibility="collapsed")

alinan_js = f"""
<div>
    <button onclick="getAlinanLocation()" style="background-color:#FF4B4B; color:white; padding:8px 15px; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%; margin-bottom:10px;">
        📍 Alınan Konumun GPS Verisini Al ve Kutuya Yaz
    </button>
    <script>
    function getAlinanLocation() {{
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(function(position) {{
                let coords = position.coords.latitude.toFixed(6) + ", " + position.coords.longitude.toFixed(6);
                // Streamlit input elemanını bul ve değerini otomatik değiştir
                const doc = window.parent.document;
                const inputs = doc.querySelectorAll('input[type="text"]');
                inputs.forEach(input => {{
                    if (input.value === "{alinan_nokta}" || input.placeholder === "" || input.getAttribute("aria-label")?.includes("Alınan")) {{
                        input.value = coords;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }});
                alert("Alınan konum başarıyla kutuya eklendi: " + coords);
            }}, function(error) {{
                alert("Konum alınamadı. Lütfen izinleri kontrol edin.");
            }});
        }} else {{
            alert("Tarayıcınız konumu desteklemiyor.");
        }}
    }}
    </script>
</div>
"""
components.html(alinan_js, height=60)


# Bırakılan Konum Alanı ve Butonu
st.write("**Bırakılan Konteyner Noktası**")
birakilan_nokta = st.text_input("Bırakılan Nokta", key="birakilan_nokta_input", label_visibility="collapsed")

birakilan_js = f"""
<div>
    <button onclick="getBirakilanLocation()" style="background-color:#0083B8; color:white; padding:8px 15px; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%; margin-bottom:10px;">
        📍 Bırakılan Konumun GPS Verisini Al ve Kutuya Yaz
    </button>
    <script>
    function getBirakilanLocation() {{
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(function(position) {{
                let coords = position.coords.latitude.toFixed(6) + ", " + position.coords.longitude.toFixed(6);
                const doc = window.parent.document;
                const inputs = doc.querySelectorAll('input[type="text"]');
                inputs.forEach(input => {{
                    if (input.value === "{birakilan_nokta}") {{
                        input.value = coords;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }});
                alert("Bırakılan konum başarıyla kutuya eklendi: " + coords);
            }}, function(error) {{
                alert("Konum alınamadı.");
            }});
        }} else {{
            alert("Tarayıcınız konumu desteklemiyor.");
        }}
    }}
    </script>
</div>
"""
components.html(birakilan_js, height=60)

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
