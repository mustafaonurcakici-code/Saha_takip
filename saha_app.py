from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Saha Operasyon Takip", page_icon="🚛", layout="centered"
)

st.title("🚛 Saha Operasyon ve Konteyner Takip Paneli")
st.markdown("---")


# --- GOOGLE SHEETS BAĞLANTI FONKSİYONU ---
def get_sheet_connection():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]
  # Streamlit secrets üzerinden güvenli bağlantı
creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

  client = gspread.authorize(creds)
  sheet = client.open("Saha_Takip_Deposu").sheet1
  return sheet


# --- SABİT LİSTELER ---
PERSONEL_LISTesi = [
    "Seçiniz...",
    "Emir ALP",
    "Hasan KOCAMAN",
    "Ertan SERT",
    "Hakan KOKAŞ",
    "Diğer",
]

KONTEYNER_CINSLERI = [
    "Seçiniz...",
    "Yeni 800",
    "Yeni 1100",
    "Tamirli 800",
    "Tamirli 1100",
    "Ambalaj",
    "Kafes",
]

# --- GİRİŞ ALANLARI ---
tarih = st.date_input("İşlem Tarihi", value=datetime.now())
personel = st.selectbox("İşlemi Yapan Personel", PERSONEL_LISTesi)

islem_turu = st.selectbox(
    "Yapılacak İşlem Türü",
    [
        "Seçiniz...",
        "Yeni Konteyner Kurulumu",
        "Konteyner Değişimi",
        "Kurum İçi Kumbara Teslimi (ÇAKAB)",
        "Tamir İçin Merkeze Getirilen",
    ],
)

konteyner_cinsi = st.selectbox("Konteyner Cinsi / Türü", KONTEYNER_CINSLERI)

# Değişkenler
eski_konum = ""
yeni_konum = ""

st.markdown("---")
st.subheader("📍 Konum ve Fotoğraf İşlemleri")

# --- SENARYO BAZLI ALINAN VE BIRAKILAN YER YÖNETİMİ ---
if islem_turu == "Yeni Konteyner Kurulumu":
  st.info("📍 **Alınan Yer:** Operasyon Merkezi (Otomatik)")
  eski_konum = "Operasyon Merkezi"

  st.write(
      "📸 **Bırakılan Yer:** Konteynerin bırakıldığı noktanın fotoğrafını"
      " yükleyin / çekin:"
  )
  foto_birakilan = st.file_uploader(
      "Bırakılma Noktası Fotoğrafı",
      type=["jpg", "jpeg", "png"],
      key="birakilan_yeni",
  )
  if foto_birakilan:
    yeni_konum = "Sahadan Konum (Fotoğraflı Kayıt)"
    st.success("✅ Bırakılan yer fotoğrafı ve konumu alındı.")

elif islem_turu == "Konteyner Değişimi":
  st.write(
      "📸 **Alınan Yer:** Eski konteynerin alındığı noktanın fotoğrafını"
      " yükleyin / çekin:"
  )
  foto_alinan = st.file_uploader(
      "Alınan Yer Fotoğrafı (Eski Konteyner)",
      type=["jpg", "jpeg", "png"],
      key="alinan_degisim",
  )
  if foto_alinan:
    eski_konum = "Sahadan Alınan Konum (Fotoğraflı Kayıt)"
    st.success("✅ Alınan yer fotoğrafı kaydedildi.")

  st.write(
      "📸 **Bırakılan Yer:** Yeni konteynerin bırakıldığı noktanın fotoğrafını"
      " yükleyin / çekin:"
  )
  foto_birakilan = st.file_uploader(
      "Bırakılan Yer Fotoğrafı (Yeni Konteyner)",
      type=["jpg", "jpeg", "png"],
      key="birakilan_degisim",
  )
  if foto_birakilan:
    yeni_konum = "Sahadan Bırakılan Konum (Fotoğraflı Kayıt)"
    st.success("✅ Bırakılan yer fotoğrafı kaydedildi.")

elif islem_turu == "Kurum İçi Kumbara Teslimi (ÇAKAB)":
  st.info("📍 **Alınan Yer:** Operasyon Merkezi (Otomatik)")
  eski_konum = "Operasyon Merkezi"

  kurum_adi = st.text_input("Teslim Edilen Kurum / Birim Adı")
  st.write(
      "📸 **Bırakılan Yer:** Kurum içinde teslimat yapılan noktanın fotoğrafını"
      " yükleyin / çekin:"
  )
  foto_birakilan = st.file_uploader(
      "Kurum İçi Teslimat Fotoğrafı",
      type=["jpg", "jpeg", "png"],
      key="birakilan_kurum",
  )
  if foto_birakilan:
    yeni_konum = f"Kurum: {kurum_adi} (Fotoğraflı Kayıt)"
    st.success("✅ Kurum teslimat fotoğrafı alındı.")

elif islem_turu == "Tamir İçin Merkeze Getirilen":
  st.write(
      "📸 **Alınan Yer:** Konteynerin sahadan alındığı noktanın fotoğrafını"
      " yükleyin / çekin:"
  )
  foto_alinan = st.file_uploader(
      "Sahadan Alınma Noktası Fotoğrafı",
      type=["jpg", "jpeg", "png"],
      key="alinan_tamir",
  )
  if foto_alinan:
    eski_konum = "Sahadan Alınan Konum (Fotoğraflı Kayıt)"
    st.success("✅ Alınan yer fotoğrafı kaydedildi.")

  st.info("📍 **Bırakılan Yer:** Operasyon Merkezi Depo (Otomatik)")
  yeni_konum = "Operasyon Merkezi Depo"

notlar = st.text_area("Ek Notlar / Açıklama")
st.markdown("---")

# --- KAYDET BUTONU ---
if st.button("🚀 Kaydet ve Tabloya Gönder", type="primary"):
  if (
      personel == "Seçiniz..."
      or islem_turu == "Seçiniz..."
      or konteyner_cinsi == "Seçiniz..."
  ):
    st.error(
        "Lütfen **Personel**, **İşlem Türü** ve **Konteyner Cinsi** alanlarını"
        " eksiksiz seçin!"
    )
  else:
    try:
      sheet = get_sheet_connection()
      row_data = [
          str(tarih),
          personel,
          islem_turu,
          konteyner_cinsi,
          eski_konum,
          yeni_konum,
          notlar,
      ]
      sheet.append_row(row_data)
      st.success("✅ Kayıt başarıyla Google E-Tabloya aktarıldı!")
    except Exception as e:
      st.error(f"Bağlantı veya kayıt hatası oluştu: {e}")