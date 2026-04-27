# 🌊 Smart Water Monitoring & Automated Control System

## 📝 Deskripsi Proyek
Sistem ini merupakan solusi **Enterprise-Grade IoT** yang dirancang untuk manajemen sumber daya air secara cerdas dan otomatis. Menggunakan arsitektur sistem tertanam (embedded system) yang tangguh, alat ini mampu melakukan pemantauan tingkat elevasi air secara presisi serta mengontrol aktuator pengisian (pompa) secara otonom.

Sistem ini mengintegrasikan sensor ultrasonik berbasis gelombang suara dan sensor konduktivitas air analog untuk memastikan akurasi data yang tinggi. Dengan dukungan sinkronisasi waktu global dan pengiriman data melalui protokol HTTP, proyek ini menjadi landasan kuat untuk pengembangan sistem manajemen air pintar di lingkungan residensial maupun industri kecil.

---

## ✨ Fitur Utama
* **Autonomous Pump Control**: Logika otomasi cerdas yang menjaga ketersediaan air tanpa intervensi manual.
* **Advanced Hysteresis Algorithm**: Implementasi zona penyangga (buffer zone) untuk memitigasi efek osilasi (nyala-mati cepat) pada relay akibat turbulensi air, sehingga memperpanjang usia pakai komponen mekanis.
* **Dual-Sensor Validation**: Mengintegrasikan sensor ultrasonik non-kontak dan sensor konduktivitas analog untuk memastikan validitas data level air.
* **Real-time Data Streaming**: Metrik sensor ditransmisikan setiap detik ke backend server menggunakan protokol HTTP untuk analisis lebih lanjut.
* **Temporal Precision**: Sinkronisasi waktu otomatis melalui protokol NTP guna menjamin akurasi timestamp pada setiap log data.

---

## 📐 Logika Operasional & Threshold
Sistem dikalibrasi pada wadah dengan ketinggian efektif **19.0 cm** dengan parameter kendali sebagai berikut:

| Jarak (Distance) | Status Sistem | Kondisi Pompa (Relay) | Indikator Suara |
| :--- | :--- | :--- | :--- |
| **> 12.0 cm** | **Normal** | **Aktif (Pengisian)** | Silent |
| **8.1 - 12.0 cm** | **Warning** | **Hysteresis Locked** (Mati jika naik, Nyala jika surut < 9cm) | Intermiten (Bip) |
| **≤ 8.0 cm** | **Bahaya** | **Non-Aktif (Safety Stop)** | Continuous Alarm |

---

## 🛠️ Konfigurasi Arsitektur Perangkat Keras
Berikut adalah pemetaan pin (*pin-to-pin mapping*) yang diimplementasikan pada unit **ESP32 S3**:

| Komponen | Koneksi VCC/GND | Interface (GPIO) |
| :--- | :--- | :--- |
| **Ultrasonic HC-SR04** | 3V3 & GND | **Trig: 6, Echo: 7** |
| **Water Level Sensor** | 3V3 & GND | **Signal: 4 (Analog)** |
| **Relay Module** | 3V3 & GND | **IN1: 2** |
| **Active Buzzer** | GND | **Positive (+): 14** |

---

## 🌐 Integrasi Ekosistem & Kolaborasi
Proyek ini merupakan hasil kolaborasi lintas disiplin untuk menciptakan sistem pemantauan yang komprehensif:

* **IoT & Embedded Systems**: Bertanggung jawab atas desain sirkuit, manajemen sensor, dan logika kendali pada perangkat keras.
* **Web Development**: Mengembangkan infrastruktur Backend API untuk pengolahan data serta Dashboard Frontend sebagai antarmuka visualisasi pengguna.
* **Machine Learning**: Melakukan pemrosesan data historis untuk kebutuhan analisis prediktif dan klasifikasi status kualitas air.

---

## 📂 Dokumentasi Integrasi Data (JSON)
Payload data ditransmisikan ke server menggunakan metode **POST** dengan skema sebagai berikut:
```json
{
  "timestamp": "2026-04-27 13:00:00", 
  "water_level": 5.5,                 
  "distance": 13.5,                   
  "water_raw": 0,                     
  "status": "normal"                  
}