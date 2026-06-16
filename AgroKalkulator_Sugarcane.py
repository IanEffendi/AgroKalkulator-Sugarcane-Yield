import streamlit as st
import google.generativeai as genai
import requests

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="AgroKalkulator Sugarcane",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 AgroKalkulator Sugarcane Yield & Revenue Estimator")
st.subheader("Otomatisasi Proyeksi Produktivitas dan Valuasi Ekonomi Tebu")
st.markdown("---")

# ==========================================
# 2. INISIALISASI GEMINI API (AUTO-DETECT)
# ==========================================
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        
        # Deteksi model yang didukung API Key
        supported_models = [
            m.name.replace("models/", "") 
            for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        if supported_models:
            terpilih = "gemini-3.5-flash" if "gemini-3.5-flash" in supported_models else supported_models[0]
            model = genai.GenerativeModel(terpilih)
            st.sidebar.success(f"✅ AI Terhubung")
        else:
            st.error("❌ Tidak ada model yang tersedia di API Key ini.")
            st.stop()
    else:
        st.error("❌ `GEMINI_API_KEY` tidak ditemukan di Secrets.")
        st.stop()
except Exception as e:
    st.error(f"❌ ERROR KONFIGURASI AI: {e}")
    st.stop()

# ==========================================
# 3. FUNGSI TELEGRAM BOT (RINGKAS & AMAN)
# ==========================================
def send_to_telegram(text_content):
    bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        st.sidebar.warning("⚠️ Pengiriman Telegram dilewati (Token kosong).")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        # Potong per 4000 karakter agar tidak ditolak Telegram
        for i in range(0, len(text_content), 4000):
            payload = {
                "chat_id": str(chat_id).strip(),
                "text": text_content[i:i+4000]
            }
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                st.sidebar.error(f"❌ Telegram menolak: {response.text}")
                return False
                
        return True
        
    except Exception as e:
        st.sidebar.error(f"❌ Error Telegram: {e}")
        return False

# ==========================================
# 4. INPUT NODES (DATA LAPANGAN)
# ==========================================
st.header("📥 Input Parameter Lapangan")

col1, col2 = st.columns(2)
with col1:
    luas_lahan_ru = st.number_input("1. Luas Lahan (Ru)", min_value=1.0, value=100.0)
    jumlah_anakan = st.number_input("2. Anakan Awal (per m²)", min_value=0.1, value=12.0)
    survival_rate = st.slider("3. Survival Rate (%)", min_value=0.0, max_value=100.0, value=85.0)

with col2:
    bobot_batang = st.number_input("4. Bobot Per Batang (kg)", min_value=0.1, max_value=5.0, value=1.5)
    rendemen = st.slider("5. Rendemen (%)", min_value=0.0, max_value=20.0, value=7.5)
    harga_pasar = st.number_input("6. Harga Pasar (Rp/kg)", min_value=1000, value=18500, step=100)

st.markdown("---")

# ==========================================
# 5. PROCESS & OUTPUT NODES
# ==========================================
if st.button("🚀 Jalankan Proyeksi & Kirim Telegram"):
    
    # Dasar Perhitungan
    luas_m2 = luas_lahan_ru * 14
    total_anakan = luas_m2 * jumlah_anakan
    estimasi_panen = total_anakan * (survival_rate / 100)
    estimasi_tonase = (estimasi_panen * bobot_batang) / 1000
    estimasi_gula = (estimasi_tonase * 1000) * (rendemen / 100)
    pendapatan = estimasi_gula * harga_pasar

    with st.spinner("AI sedang menyusun laporan..."):
        try:
            # PROMPT ENGINEERING KHUSUS AGAR TEKS RAPI DI TELEGRAM
            prompt_analisis = f"""
            Anda adalah pakar Agronomi Tebu. Susun laporan analisis berdasarkan data berikut:
            - Lahan: {luas_lahan_ru} Ru ({luas_m2:,.0f} m²)
            - Anakan: {jumlah_anakan}/m² (Survival: {survival_rate}%)
            - Bobot: {bobot_batang} kg | Rendemen: {rendemen}% | Harga: Rp {harga_pasar:,}/kg
            
            Hasil Kalkulasi Dasar:
            - Est. Batang: {estimasi_panen:,.0f} batang
            - Est. Tonase: {estimasi_tonase:,.2f} Ton
            - Est. Gula: {estimasi_gula:,.2f} kg
            - Est. Pendapatan: Rp {pendapatan:,.2f}

            ATURAN FORMAT PENULISAN (SANGAT PENTING):
            1. DILARANG KERAS menggunakan simbol Markdown seperti bintang (**) atau tagar (#).
            2. Gunakan HURUF KAPITAL penuh untuk setiap Judul dan Sub-judul.
            3. Beri jarak satu baris kosong (enter) antar paragraf agar mudah dibaca di layar HP.
            4. Gunakan tanda strip (-) untuk membuat daftar/list.
            5. Gunakan emoji secukupnya di awal judul untuk mempercantik tampilan.
            
            Isi laporan harus mencakup:
            - KESIMPULAN PRODUKTIVITAS LAHAN
            - ANALISIS VALUASI EKONOMI & RISIKO
            - REKOMENDASI PERAWATAN AGRONOMIS
            """
            
            response = model.generate_content(prompt_analisis)
            hasil_analisis = response.text
            
            # Tampilkan di Layar
            st.header("📊 Hasil Proyeksi")
            st.text(hasil_analisis) # Menggunakan st.text agar format di layar sama persis dengan di Telegram
            
            st.markdown("---")
            
            # Kirim ke Telegram
            with st.spinner("Mengirim ke Telegram..."):
                header_pesan = "LAPORAN OTOMATISASI AGROKALKULATOR\n==================================\n\n"
                pesan_final = header_pesan + hasil_analisis
                
                terkirim = send_to_telegram(pesan_final)
                
                if terkirim:
                    st.success("✅ Laporan berhasil dikirim ke Telegram dengan susunan yang rapi!")
                    
        except Exception as ai_err:
            st.error(f"❌ Terjadi kesalahan API: {ai_err}")
