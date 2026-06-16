import streamlit as st
import google.generativeai as genai
import requests

# 1. KONFIGURASI HALAMAN UTAMA STREAMLIT
st.set_page_config(
    page_title="AgroKalkulator Sugarcane",
    page_icon="🌾",
    layout="wide"
)

# Judul Utama sesuai Permintaan
st.title("🌾 AgroKalkulator Sugarcane Yield & Revenue Estimator")
st.subheader("Otomatisasi Proyeksi Produktivitas dan Valuasi Ekonomi Tebu")
st.markdown("---")

# 2. INISIALISASI & KONFIGURASI GEMINI API
# Catatan Gagal Akses API: Jika Gemini tidak bisa diakses, pastikan Anda sudah memasukkan
# GEMINI_API_KEY ke dalam menu "Secrets" di Streamlit Cloud / file secrets.toml lokal.
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        # Menggunakan model stabil gemini-1.5-flash untuk pemrosesan cepat
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("❌ ERROR: `GEMINI_API_KEY` tidak ditemukan di Secrets Streamlit. Periksa pengaturan Advanced Settings Anda.")
except Exception as e:
    st.error(f"❌ ERROR KONFIGURASI AI: {e}")

# 3. FUNGSI UNTUK MENGIRIM BALASAN/LAPORAN KE TELEGRAM
def send_to_telegram(text_content):
    try:
        bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
        
        if not bot_token or not chat_id:
            st.warning("⚠️ Catatan: Laporan belum terkirim ke Telegram karena `TELEGRAM_BOT_TOKEN` atau `TELEGRAM_CHAT_ID` belum diatur di Secrets Streamlit.")
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
        st.error(f"❌ Gagal mengirim notifikasi ke Telegram: {e}")
        return False

# 4. ALUR KERJA: INPUT NODES (6 Parameter Data Riil Lapangan)
st.header("📥 Input Nodes (Data Riil Pengamatan Lapangan)")
st.markdown("Masukkan parameter hasil pengamatan lapangan untuk memulai otomatisasi proyeksi:")

col1, col2 = st.columns(2)

with col1:
    luas_lahan_ru = st.number_input(
        "1) Luas Lahan (Ru)", 
        min_value=1.0, 
        value=100.0, 
        step=1.0, 
        help="Mengakomodasi luasan lahan pengamatan dalam satuan lokal Ru (1 Ru = 14 m²)"
    )
    jumlah_anakan = st.number_input(
        "2) Jumlah Anakan Awal (per m²)", 
        min_value=0.1, 
        value=12.0, 
        step=0.1, 
        help="Rata-rata populasi anakan tebu dari kompilasi 100 titik sampel acak"
    )
    survival_rate = st.slider(
        "3) Survival Rate (%)", 
        min_value=0.0, 
        max_value=100.0, 
        value=85.0, 
        step=0.5, 
        help="Estimasi persentase kelangsungan hidup anakan tebu hingga menjadi batang dewasa siap panen"
    )

with col2:
    bobot_batang = st.number_input(
        "4) Bobot Per Batang (kg)", 
        min_value=0.1, 
        max_value=5.0, 
        value=1.5, 
        step=0.1, 
        help="Estimasi berat rata-rata satu batang tebu dewasa (kisaran normal 1–2 kg)"
    )
    rendemen = st.slider(
        "5) Rendemen (%)", 
        min_value=0.0, 
        max_value=20.0, 
        value=7.5, 
        step=0.1, 
        help="Persentase estimasi kandungan kadar gula murni yang dapat diekstrak"
    )
    harga_pasar = st.number_input(
        "6) Harga Pasar (Rp/kg)", 
        min_value=1000, 
        value=18500, 
        step=100, 
        help="Harga jual aktual gula murni di pasar komoditas untuk memonitor fluktuasi"
    )

st.markdown("---")

# 5. ALUR KERJA: PROCESS & OUTPUT NODES
if st.button("🚀 Jalankan Otomatisasi Proyeksi & Kirim Laporan"):
    
    # [PROCESS NODES] Perhitungan Matematis Dasar sebagai Aturan Grounding Data
    luas_m2 = luas_lahan_ru * 14
    total_anakan_awal = luas_m2 * jumlah_anakan
    estimasi_batang_panen = total_anakan_awal * (survival_rate / 100)
    estimasi_tonase_tebu = (estimasi_batang_panen * bobot_batang) / 1000  # Konversi ke satuan Ton
    estimasi_gula_kg = (estimasi_tonase_tebu * 1000) * (rendemen / 100)  # Total kg gula murni yang dihasilkan
    total_pendapatan = estimasi_gula_kg * harga_pasar            # Valuasi Ekonomi total

    with st.spinner("Gemini AI sedang memproses pemodelan proyeksi dan analisis bisnis..."):
        try:
            # Konstruksi Prompt Struktur Komprehensif untuk model AI
            prompt_analisis = f"""
            Anda adalah sistem kecerdasan buatan pakar Agronomi dan Analis Valuasi Ekonomi Industri Gula.
            Tugas Anda adalah melakukan otomatisasi proyeksi produktivitas dan ekonomi tebu berbasis data terstruktur berikut:
            
            [DATA INPUT NODES]
            - Luas Lahan: {luas_lahan_ru} Ru (Setara dengan {luas_m2:,} m²)
            - Jumlah Anakan Awal: {jumlah_anakan} per m²
            - Survival Rate: {survival_rate}%
            - Bobot Per Batang: {bobot_batang} kg
            - Rendemen Gula: {rendemen}%
            - Harga Pasar Gula Aktual: Rp {harga_pasar:,}/kg
            
            [HASIL KALKULASI DASAR]
            - Total Estimasi Batang Siap Panen: {estimasi_batang_panen:,.0f} batang
            - Estimasi Total Tonase Tebu: {estimasi_tonase_tebu:,.2f} Ton
            - Estimasi Hasil Gula Murni: {estimasi_gula_kg:,.2f} kg
            - Proyeksi Pendapatan Kotor (Valuasi): Rp {total_pendapatan:,.2f}
            
            Buatlah laporan komprehensif, formal, dan berstruktur rapi dalam format Markdown. Laporan harus mencakup:
            1. 📊 Analisis potensi produktivitas tanaman berdasarkan kepadatan populasi efektif.
            2. 💰 Analisis Valuasi Ekonomi tebu serta dampak fluktuasi harga pasar terhadap profitabilitas kebun.
            3. 🌾 Rekomendasi agronomis taktis jangka pendek untuk menjaga Survival Rate tetap tinggi serta cara optimalisasi Rendemen gula saat tebu memasuki masa tebang.
            """
            
            # Memproses prompt menggunakan Gemini API
            response = model.generate_content(prompt_analisis)
            hasil_analisis = response.text
            
            # [OUTPUT NODES] - 1. Tampilkan Hasil Analisis di Antarmuka Web Streamlit
            st.header("📊 Output Node (Hasil Proyeksi & Analisis Valuasi)")
            st.markdown(hasil_analisis)
            
            st.markdown("---")
            
            # [OUTPUT NODES] - 2. Kirim Salinan Laporan secara Otomatis ke Telegram
            with st.spinner("Mengirimkan laporan otomatisasi ke Telegram grup/chat..."):
                pesan_telegram = f"🌾 *LAPORAN OTOMATISASI AGROKALKULATOR TEBU*\n\n{hasil_analisis}"
                
                terkirim = send_to_telegram(pesan_telegram)
                if terkirim:
                    st.success("✅ Sukses! Laporan analisis komprehensif telah dikirimkan ke Telegram.")
                else:
                    st.info("ℹ️ Aplikasi berjalan normal, laporan ditampilkan di atas. Pengiriman Telegram dilewati karena konfigurasi Token/Chat ID belum diisi di Secrets.")
                    
        except Exception as ai_err:
            st.error(f"❌ Terjadi kesalahan saat memproses data dengan Gemini API: {ai_err}")