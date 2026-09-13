# Akıllı Süpürge - Operasyon ve Performans Takip Sistemi (IoT)

Bu proje, manuel temizlik süreçlerini dijitalleştirmek amacıyla standart süpürgeleri Nesnelerin İnterneti (IoT) tabanlı akıllı cihazlara dönüştüren bir gömülü sistem çalışmasıdır. İvmeölçer ve Jiroskop verileri (IMU) kullanılarak personelin temizlik sırasındaki durumları (Yürüme, Durma, Süpürme) "Varyans" ve "Tepe Noktası (Peak)" algoritmalarıyla analiz edilir. 

Sistem, hesaplamaları Uç Birimde (Edge Computing) gerçekleştirip performansı (Aktif süre, boşta bekleme, adım mesafesi, fırça darbesi) hesaplar ve 30 dakikada bir **13 Byte'lık sıkıştırılmış bir LoRaWAN paketi** olarak uzak sunucuya iletir.

### 🎥 Sistem Animasyonu
Aşağıdaki videoda, C algoritmamızın gelen sensör verilerini "Varyans" hesabıyla nasıl milisaniyeler içinde yorumladığını (Süpürme, Yürüme vb.) ve sağ üst köşede performansı nasıl saydığını canlı olarak görebilirsiniz:

<video src="https://github.com/doga66/aware_robotics_task/raw/main/test_realtime_kalman.mp4" width="800" controls></video>

*(Not: Eğer video açılmazsa, klasördeki `test_realtime_kalman.mp4` dosyasını doğrudan indirebilirsiniz.)*

---

## 📂 Klasör Yapısı ve Veriler

*   `detector.c`: Projenin kalbi olan ana C algoritması. Sensör verilerini saniyelik okur, varyans hesabını yapar, hareket sayımlarını (Peak Detection) gerçekleştirir ve 1D Kalman Filtresini barındırır.
*   `device.py`: Sahadaki IoT süpürge cihazını simüle eden Python kodudur. `detector.c`'yi çalıştırıp sonuçları alır, 13 Byte'lık Hexadecimal bir Byte Array'e (Payload) dönüştürür ve UDP (LoRa radyo dalgası simülasyonu) üzerinden fırlatıp uyku moduna geçer.
*   `server.py`: 20 km uzaklıktaki Merkezi Sunucuyu (Gateway) simüle eder. Havadan gelen UDP paketini dinler, `XOR Checksum` kontrolü yaparak verinin bozulup bozulmadığını doğrular ve Big-Endian yapısındaki paketi insan diline (Decode) çevirir.
*   `realtime_visualize.py`: Sensör verilerinin zaman içerisindeki akışını ve algoritmanın verdiği anlık kararları canlı izlemek için kullanılır.
*   `/test/`: C algoritmasının test edilebilmesi için gerekli olan `Accelerometer.csv` ve `Gyroscope.csv` örnek verilerini barındırır.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Algoritmayı Derleme ve Test Etme
Gereksinimler: `gcc`
```bash
# C kodunu derleyin
gcc -o detector detector.c -lm

# Test verisiyle (Filtresiz) çalıştırın
./detector test/Accelerometer.csv test/Gyroscope.csv

# Çok gürültülü sensörler için Kalman Filtresiyle çalıştırın
./detector test/Accelerometer.csv test/Gyroscope.csv --use-kalman
```

### 2. Haberleşme Simülasyonu (LoRaWAN)
İki ayrı terminal açarak bir uçtan diğer uca veri gönderimini simüle edin:
```bash
# Terminal 1 (Merkezi Sunucuyu Başlatın)
python3 server.py

# Terminal 2 (Süpürgeyi/Cihazı Başlatın)
python3 device.py
```

### 3. Görselleştirme ve Animasyon
```bash
# Algoritmanın anlık kararlarını MP4 olarak kaydetmek ve izlemek için:
python3 realtime_visualize.py
```

---

## 📡 Haberleşme Yapısı (Payload) Hakkında
Pil ömrünü korumak adına JSON gibi ağır metin tipleri KULLANILMAMIŞTIR. Veriler C dilindeki `Struct Packing` (Big Endian) mantığıyla bit seviyesinde şifrelenir. Toplam boyut, veri bütünlüğü koruması (Checksum) ile birlikte sadece 13 Byte'tır:

*   `0-1 Byte`: Cihaz ID (2 Byte - Unsigned Short)
*   `2 Byte`: Batarya Yüzdesi (1 Byte - Unsigned Char)
*   `3-4 Byte`: Çalışma Süresi (2 Byte - Unsigned Short)
*   `5-6 Byte`: Bekleme Süresi (2 Byte - Unsigned Short)
*   `7-8 Byte`: Salınım (Süpürme) Sayısı (2 Byte - Unsigned Short)
*   `9-10 Byte`: Temizlik Mesafesi (2 Byte - Unsigned Short)
*   `11 Byte`: Hata Durum Kodu (1 Byte - Unsigned Char)
*   `12 Byte`: XOR Checksum (1 Byte)
