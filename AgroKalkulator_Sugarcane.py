import streamlit as st
import google.generativeai as genai
import requests

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA STREAMLIT
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
# 2. INISIALISASI & AUTO-DETECT GEMINI API
# ==========================================
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        
        # Mengambil daftar semua model yang didukung secara riil oleh API Key Anda
        supported_models = [
            m.name.replace("models/", "") 
            for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        if supported_models:
            # Memprioritaskan gemini-3.5-flash sesuai permintaan, jika tidak ada pakai model pertama di list
            if "gemini-3.5-flash" in supported_models:
                terpilih = "gemini-3.5-flash"
            else:
                terpilih = supported_models[0] # Fallback otomatis yang pasti jalan
                
            model = genai.GenerativeModel(terpilih)
            st.sidebar.success(f"✅ AI Terhubung! Menggunakan model: `{terpilih}`")
        else:
            st.error("❌ API Key valid, tetapi tidak ada model yang tersedia untuk generateContent di versi library ini.")
            st.stop()
    else:
        st.error("❌ ERROR: `GEMINI_API_KEY` tidak ditemukan di Secrets Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"❌ ERROR KONFIGURASI AI: {e}")
    st.stop()

# ==========================================
# 3. FUNGSI INTEGRASI TELEGRAM BOT
# ==========================================
def send_to_telegram(text_content):
    try:
        bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
        
        if not bot_token or not chat_id:
            st.sidebar.warning("⚠️ Laporan tidak dikirim ke Telegram (Token/Chat ID kosong).")
            return False
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text_content,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        st.sidebar.error(f"❌ Gagal mengirim Telegram: {e}")
        return False

# ==========================================
# 4. INPUT NODES (Parameter Lapangan)
# ==========================================
st.header("📥 Input Nodes (Data Riil Pengamatan Lapangan)")
st.markdown("Masukkan 6 parameter data riil lapangan untuk memulai otomatisasi:")

col1, col2 = st.columns(2)

with col1:
    luas_lahan_ru = st.number_input(
        "1) Luas Lahan (Ru)", min_value=1.0, value=100.0, step=1.0, 
        help="1 Ru = 14 m²"
    )
    jumlah_anakan = st.number_input(
        "2) Jumlah Anakan Awal (per m²)", min_value=0.1, value=12.0, step=0.1, 
        help="Rata-rata populasi dari 100 titik sampel acak"
    )
    survival_rate = st.slider(
        "3) Survival Rate (%)", min_value=0.0, max_value=100.0, value=85.0, step=0.5, 
        help="Persentase hidup anakan tebu hingga panen"
    )

with col2:
    bobot_batang = st.number_input(
        "4) Bobot Per Batang (kg)", min_value=0.1, max_value=5.0, value=1.5, step=0.1, 
        help="Estimasi berat rata-rata satu batang dewasa"
    )
    rendemen = st.slider(
        "5) Rendemen (%)", min_value=0.0, max_value=20.0, value=7.5, step=0.1, 
        help="Persentase kandungan kadar gula murni"
    )
    harga_pasar = st.number_input(
        "6) Harga Pasar (Rp/kg)", min_value=1000, value=18500, step=100, 
        help="Harga jual aktual gula murni"
    )

st.markdown("---")

# ==========================================
# 5. PROCESS & OUTPUT NODES
# ==========================================
if st.button("🚀 Jalankan Otomatisasi Proyeksi & Kirim Laporan"):
    
    # [PROCESS 1] Perhitungan Matematis (Data Grounding untuk AI)
    luas_m2 = luas_lahan_ru * 14
    total_anakan_awal = luas_m2 * jumlah_anakan
    estimasi_batang_panen = total_anakan_awal * (survival_rate / 100)
    estimasi_tonase_tebu = (estimasi_batang_panen * bobot_batang) / 1000  # Ton
    estimasi_gula_kg = (estimasi_tonase_tebu * 1000) * (rendemen / 100)  # Kg
    total_pendapatan = estimasi_gula_kg * harga_pasar  # Rupiah

    with st.spinner("Gemini AI sedang memproses pemodelan proyeksi..."):
        try:
            # [PROCESS 2] Prompt Engineering untuk Gemini
            prompt_analisis = f"""
            Anda adalah sistem pakar Agronomi dan Valuasi Ekonomi Industri Gula.
            Lakukan otomatisasi proyeksi berdasarkan data lapangan berikut:
            
            [DATA INPUT]
            - Luas Lahan: {luas_lahan_ru} Ru ({luas_m2:,.0f} m²)
            - Jumlah Anakan Awal: {jumlah_anakan} per m²
            - Survival Rate: {survival_rate}%
            - Bobot Per Batang: {bobot_batang} kg
            - Rendemen Gula: {rendemen}%
            - Harga Pasar Gula: Rp {harga_pasar:,}/kg
            
            [KALKULASI SISTEM]
            - Estimasi Batang Panen: {estimasi_batang_panen:,.0f} batang
            - Estimasi Tonase Tebu: {estimasi_tonase_tebu:,.2f} Ton
            - Estimasi Gula Murni: {estimasi_gula_kg:,.2f} kg
            - Proyeksi Pendapatan Kotor: Rp {total_pendapatan:,.2f}
            
            Buatlah laporan komprehensif berformat Markdown yang berisi:
            1. 📊 Analisis produktivitas tanaman berdasarkan kepadatan populasi.
            2. 💰 Analisis Valuasi Ekonomi dan potensi profitabilitas.
            3. 🌾 Rekomendasi agronomis singkat untuk mengoptimalkan Survival Rate dan Rendemen.
            """
            
            response = model.generate_content(prompt_analisis)
            hasil_analisis = response.text
            
            # [OUTPUT 1] Tampilkan di UI Streamlit
            st.header("📊 Output Node (Hasil Analisis AI)")
            st.markdown(hasil_analisis)
            
            st.markdown("---")
            
            # [OUTPUT 2] Kirim ke Telegram
            with st.spinner("Mengirimkan laporan ke Telegram..."):
                pesan_telegram = f"🌾 *LAPORAN AGROKALKULATOR TEBU*\n\n{hasil_analisis}"
                terkirim = send_to_telegram(pesan_telegram)
                
                if terkirim:
                    st.success("✅ Laporan analisis berhasil dikirimkan ke Telegram!")
                else:
                    st.info("ℹ️ Laporan berhasil dibuat di layar. Pengiriman Telegram dilewati karena pengaturan Token di Secrets belum lengkap.")
                    
        except Exception as ai_err:
            st.error(f"❌ Terjadi kesalahan saat memproses API: {ai_err}")
