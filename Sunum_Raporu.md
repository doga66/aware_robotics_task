# AKILLI SÜPÜRGE - OPERASYON VE PERFORMANS TAKİP SİSTEMİ
## TEKNİK PROJE VE MİMARİ RAPORU

### 1. PROJE ÖZETİ VE HEDEFLER
Bu proje, manuel temizlik süreçlerini dijitalleştirmek amacıyla standart süpürgeleri Nesnelerin İnterneti (IoT) tabanlı akıllı cihazlara dönüştürmeyi hedeflemektedir. Temel amacımız; sürekli sensör verisi göndererek pili hızla tüketen donanımlar yerine, veriyi mikrodenetleyici üzerinde işleyip (Edge Computing) sadece periyodik sonuçları ileten, yüksek enerji verimliliğine sahip, düşük maliyetli ve otonom bir uç birim (edge node) tasarlamaktır.

### 2. SİSTEM MİMARİSİ VE DONANIM BİLEŞENLERİ
Sistem donanımı, endüstriyel dayanıklılık ve düşük güç tüketimi prensiplerine göre tasarlanmıştır:
* **Sensör:** Titreşim ve hareket algılaması için düşük maliyetli ve yüksek hassasiyetli 6 eksenli **LSM6DS3 (IMU)** kullanılmıştır. Cihaz, açısal hızı kaybetmemek ve darbelere maruz kalmamak adına süpürge sapının orta-alt kısımlarına yerleştirilmelidir.
* **Mikrodenetleyici (MCU):** LoRa modülü entegre edilmiş **STM32WLE5** çipi tercih edilmiştir. Bu sayede harici bir haberleşme modülüne gerek kalmamış, devre kartı (PCB) alanı ve güç tüketimi minimize edilmiştir.
* **Güç:** 18650 tipi 3.7V Li-Ion batarya ile desteklenen sistem, günün %99'unda uyku modunda kalacak şekilde programlandığından aylarca şarj edilmeden sahada görev yapabilmektedir.

### 3. ALGORİTMA TASARIMI VE KOD MANTIĞI (DETAYLI İNCELEME)
Projenin yazılım altyapısı, ağır makine öğrenmesi modelleri yerine mikrodenetleyicinin kısıtlı kaynaklarında çok hızlı ve hatasız çalışabilecek istatistiksel matematik temellerine (C dili) dayandırılmıştır.

**A. Sensör Seçimi ve Veri Toplama Süreci:**
Tasarımın en başında, donanım testi ve algoritma geliştirme süreci için standart bir MPU6050 IMU sensörü kullanılması düşünülmüştür. Ancak saha verilerini hızlıca elde etmek ve donanımsal kalibrasyon sorunlarıyla vakit kaybetmemek adına, yüksek çözünürlüklü sensörlere sahip olan akıllı telefonun dahili IMU donanımı kullanılmıştır. Telefon, süpürgeye sabitlenerek farklı senaryolardaki (Yürüme, Süpürme, Durma) hareketler 100 Hz hızında CSV dosyaları olarak kaydedilmiş, C algoritması bu gerçek saha verileri kullanılarak satır satır geliştirilmiştir.

**B. Veri Pencereleme (Windowing) Mantığı:**
Kod içerisinde `#define WINDOW_SIZE 200` sabiti ile 2 saniyelik bir veri penceresi oluşturulmuştur.
* *Kod Mantığı:* Sensörlerden okunan veriler, anında işlenmek yerine C dilindeki `while` döngüsü içerisinde `acc_y` ve `gyr_x` isimli 200 elemanlı dizilere (arrays) doldurulur. İşlemci her seferinde anlık veriye bakıp yanılmak yerine, bu 2 saniyelik bloğun bütününe bakar. Bu sayede sensördeki saliselik hatalı bir titremenin "Adım atıldı" olarak algılanmasının önüne geçilir ve sistem kararlılığı sağlanır.

**C. Varyans (Dalgalanma) Kullanımı ile Durum Tespiti:**
Personelin o anki eylemini anlamak için `calculate_variance()` isimli özel bir fonksiyon yazılmıştır. Varyans, verilerin ortalamadan ne kadar uzaklaştığını gösteren temel bir istatistiksel formüldür.
* *Kod Mantığı:* Algoritma her veri penceresi dolduğunda Jiroskopun X ekseninin ve İvmeölçerin Y ekseninin ayrı ayrı varyansını hesaplar. Personel süpürgeyi sağa sola salladığında Jiroskopun varyansı dramatik şekilde artar (>1.5 eşik değeri). Yürüdüğünde ise ayakların yere vurma şiddetinden dolayı İvmeölçer Y ekseni dalgalanır (>0.3 eşik değeri). Kodumuzdaki `if-else` karar ağacı, bu iki eşik değerini kıyaslayarak personelin o an "Durarak mı süpürdüğünü" yoksa "Yürürken mi süpürdüğünü" 4 farklı durum (State 0, 1, 2, 3) olarak milisaniyeler içinde kesin bir şekilde tespit eder.

**D. Tepe Noktası Tespiti (Peak Detection) ile Adım ve Salınım Sayımı:**
Varyans ile eylemin türü bulunduktan sonra, mesafe hesaplamak için atılan adımların sayılması gerekir.
* *Kod Mantığı:* Veri bloğu `for` döngüsü ile taranır. Eğer bir ivme verisi `acc_y[i]`, hem bir önceki `acc_y[i-1]` hem de bir sonraki `acc_y[i+1]` verisinden büyükse ve o anki genel gürültü ortalamasını (mean + 0.5) aşıyorsa, algoritma bunu bir "Tepe Noktası" (Peak) yani kesin bir "Adım" olarak kabul eder. Aynı mantık Jiroskop X ekseninde uygulanarak fırçanın sağa ve sola tam tur "Salınım" sayısı hesaplanır. Tespit edilen her adım, standart yürüme mesafesi olan 0.7 metre ile çarpılarak (Örn: `total_steps * 0.7`) bloktaki temizlik mesafesine dönüştürülür.

**E. 1D Kalman Filtresi (Sinyal İyileştirme):**
Ortamdaki sarsıntılardan veya kalitesiz sensör okumalarından kaynaklanabilecek rastgele gürültüleri filtrelemek için kodun en başına bir `KalmanFilter1D` yapısı (struct) eklenmiştir. 
* *Kod Mantığı:* Sisteme parametrik olarak `--use-kalman` komutu gönderildiğinde, döngü içerisindeki her ham sensör verisi dizilere yazılmadan hemen önce `kalman_update()` fonksiyonundan geçirilir. Bu filtre, sinyaldeki hatalı dikenleri (ani sıçramaları) matematiksel olarak törpüleyerek pürüzsüzleştirir ve varyans hesaplamasının tamamen tertemiz veriler üzerinden yapılmasını garanti altına alır.

### 4. HABERLEŞME TEKNOLOJİSİ, SEÇİMİ VE VERİ YAPISI (DETAYLI İNCELEME)
Sistem, topladığı verileri 30 dakikada bir 20 km uzaklıktaki merkezi sisteme aktarmakla yükümlüdür.

**A. Haberleşme Teknolojisinin Seçimi:**
20 kilometre, standart kablosuz teknolojiler (Wi-Fi, Bluetooth) için ulaşılamaz bir mesafedir. Bu zorluğun aşılması için iki temel endüstriyel çözüm değerlendirilmiştir:
1. **LoRaWAN (Tercih Edilen):** Şehrin veya tesisin yüksek rakımlı bir noktasına yerleştirilecek merkezi bir Gateway (Anten) sayesinde, hücresel ağlara veya SIM karta ihtiyaç duymadan 20 km yarıçapında ücretsiz, şifreli (AES-128) ve uzun menzilli bir iletişim ağı kurulabilir.
2. **NB-IoT (Alternatif Plan):** Coğrafi engellerin (tepeler, çok yoğun yapılar) görüş hattını kestiği durumlarda, mevcut telekomünikasyon baz istasyonlarını kullanan NB-IoT teknolojisi devreye alınmalıdır. Aylık ufak veri maliyetleri doğurmasına rağmen menzil problemini tamamen ortadan kaldırır.

**B. Veri Yapısı (Payload) ve Optimizasyon:**
Sensör verilerini JSON veya XML gibi metin tabanlı (ağır) formatlarda göndermek, veri boyutunu büyüterek radyonun uzun süre açık kalmasına ve pilin çok hızlı tükenmesine yol açar. Bu sorunu çözmek için veriler, C dilindeki "Struct Packing" yöntemiyle doğrudan bit seviyesinde (Hexadecimal) paketlenerek toplamda sadece **13 Byte** boyutuna indirilmiştir.

**13 Byte'lık Haberleşme Paketi (Payload) Haritası:**
* `Byte 0-1`: Cihaz ID (Örn: Cihaz Numarası)
* `Byte 2`: Batarya Doluluk Oranı (%)
* `Byte 3-4`: Aktif Çalışma Süresi (Saniye)
* `Byte 5-6`: Bekleme (Boşta Kalma) Süresi (Saniye)
* `Byte 7-8`: Toplam Fırça Salınım Sayısı
* `Byte 9-10`: Temizlenen Gerçek Mesafe (Metre)
* `Byte 11`: Cihaz Durum veya Hata Kodu
* `Byte 12`: XOR Checksum (Sağlama Kodu)

**C. Veri Bütünlüğü ve Simülasyon Çıktısı:**
Gönderilen verinin yolda elektromanyetik dalgalardan etkilenip bozulmadığından emin olmak için paketin sonuna 1 Byte'lık Checksum eklenmiştir. Cihaz (Uç Birim), 30 dakikada bir uyanır, yukarıdaki 13 byte'ı oluşturur ve gönderimi tamamladıktan hemen sonra tekrar 30 dakikalık derin uyku (Deep Sleep) moduna geçerek döngüyü sürdürür.
* **Havadan Giden Örnek Veri (Hex):** `0A2B 57 008E 0010 005A 0058 00 24`

### 5. TAHMİNİ SİSTEM MALİYET ANALİZİ
Tasarımın, 2.000 adetlik seri üretime geçileceği varsayılarak hesaplanan, tahmini saf donanım bileşen maliyetleri aşağıdaki gibidir:

1. **Mikrodenetleyici (STM32WLE5):** ~3.50 $
2. **IMU Sensörü (LSM6DS3):** ~1.50 $
3. **Batarya (18650 Li-Ion):** ~2.50 $
4. **Güç Yönetimi ve Şarj (BMS/LDO):** ~0.80 $
5. **PCB ve Pasif Komponentler:** ~1.20 $
6. **Mekanik Kasa (IP67 Yalıtımlı):** ~2.00 $

**TOPLAM BİRİM CİHAZ DONANIM MALİYETİ:** **~ 11.50 USD**

Yüksek yazılım optimizasyonu sayesinde harici modüllerden ve yüksek kapasiteli işlemcilerden tasarruf edilmiş, böylece endüstriyel kalitede bir IoT cihazı çok rekabetçi bir üretim maliyetiyle tasarlanmıştır.
