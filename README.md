LAPORAN FINAL PROJECT
LLM-Based Tools and Gemini API Integration for Data Scientists

Disusun oleh: Dian Nur Effendi

Nama project

AgroKalkulator Sugarcane Yield & Revenue Estimator: Otomatisasi Proyeksi Produktivitas dan Valuasi Ekonomi Tebu.

Siapa target pengguna chatbot Anda?

Target pengguna utama dari aplikasi berbasis AI ini meliputi:

Praktisi Perkebunan: Petani tebu skala menengah hingga besar serta mandor lapangan yang mengelola data pengamatan harian.

Sektor Kelembagaan: Pengurus dan manajer koperasi pertanian yang menaungi para petani tebu, berguna sebagai alat bantu untuk memproyeksikan potensi hasil panen guna keperluan pembiayaan atau penyaluran dana.

Analis & Pelaku Bisnis: Analis agronomi dan pelaku industri komoditas gula yang membutuhkan valuasi ekonomi cepat berdasarkan kondisi lapangan dan fluktuasi harga pasar aktual.

Bagaimana chatbot Anda dapat membantu pengguna?

Chatbot ini bertindak sebagai asisten pakar agronomi virtual yang mengubah data mentah menjadi wawasan bisnis yang dapat ditindaklanjuti (actionable insight). Aplikasi ini membantu pengguna melalui:

Otomatisasi Kalkulasi (Efisiensi Waktu): Menghilangkan proses perhitungan manual yang rawan human error. Pengguna cukup memasukkan 6 parameter lapangan (luas lahan, anakan, survival rate, bobot, rendemen, dan harga pasar) untuk mendapatkan proyeksi tonase dan estimasi hasil gula murni secara instan.

Analisis Valuasi Ekonomi Berbasis LLM: Memanfaatkan keandalan Gemini API untuk menerjemahkan angka kalkulasi dasar menjadi narasi laporan komprehensif terkait potensi profitabilitas dan identifikasi risiko ekonomi.

Saran Agronomis Instan: AI memberikan rekomendasi taktis secara real-time terkait langkah-langkah yang harus diambil untuk mempertahankan survival rate tanaman dan mengoptimalkan rendemen gula menjelang masa tebang.

Distribusi Laporan Terintegrasi: Hasil analisis tidak hanya ditampilkan di layar komputer, tetapi langsung dikirimkan ke perangkat seluler pengguna melalui integrasi Telegram Bot API. Hal ini sangat membantu pengguna saat sedang mobilitas tinggi di area perkebunan.

Link Github

https://github.com/IanEffendi/AgroKalkulator-Sugarcane-Yield

Deskripsi Antarmuka (UI):

Header & Status: Menggunakan antarmuka mode lebar (wide layout) dengan indikator status di sidebar yang menampilkan deteksi model AI secara real-time untuk memastikan sistem terhubung sebelum digunakan.

Input Nodes (Bagian Tengah): Terdiri dari dua kolom responsif. Desain ini memastikan pengguna tidak perlu melakukan scrolling panjang ke bawah. Dilengkapi dengan komponen interaktif seperti slider dan number input yang memiliki fitur tooltip/help untuk memandu pengguna saat mengisi data pengamatan.

Output Nodes (Bagian Bawah): Terdapat tombol eksekusi tunggal untuk menjalankan seluruh pipeline. Hasilnya dipaparkan menggunakan teks tanpa format kode (Plain Text) yang rapi, dan sistem akan memunculkan toast/success notification hijau ketika laporan berhasil disalurkan ke Telegram.
