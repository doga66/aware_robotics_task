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
Projenin yazılım altyapısı, ağır makine öğrenmesi modelleri yerine mikrodenetleyicinin kısıtlı kaynaklarında çok hızlı ve hatasız çalışabilecek istatistiksel matematik temellerine (C dili) dayandırılmıştır. Algoritmanın temel çalışma prensipleri aşağıda sırasıyla açıklanmıştır:

**A. Veri Pencereleme (Windowing):**
Sensörlerden 100 Hz (saniyede 100 veri) hızında okunan İvmeölçer ve Jiroskop verileri, 2 saniyelik (200 verilik) bloklar (pencereler) halinde analiz edilir. Bu yaklaşım, anlık hatalı sensör okumalarının genel kararı etkilemesini önler.

**B. Varyans (İstatistiksel Dalgalanma) Kullanımı ile Durum Tespiti:**
Personelin eylemlerini (Yürüme, Durma, Süpürme) tespit etmek için istatistiksel bir ölçüt olan "Varyans" hesaplaması kullanılmıştır. Varyans, verilerin ortalamadan ne kadar uzaklaştığını (dalgalanma miktarını) gösterir.
* **Süpürme Tespiti:** Personel süpürme hareketi yaptığında, süpürge sağa ve sola sallandığı için Jiroskopun X ekseninde periyodik dalgalanmalar oluşur. Algoritma, Jiroskop X ekseninin varyansı belirli bir eşiği aştığında cihazın "Süpürme" eyleminde olduğuna karar verir.
* **Yürüme Tespiti:** Yürüme esnasında, adımların yere çarpma kuvveti İvmeölçerin Y ekseninde dikey titreşimler yaratır. Algoritma, İvme Y ekseninin varyansı beklenen eşiği geçtiğinde personelin "Yürüme" eyleminde olduğunu saptar.
* Bu iki koşulun matematiksel kombinasyonu ile toplamda 4 farklı durum (Durma & Süpürmeme, Yürüme & Süpürmeme, Durma & Süpürme, Yürüme & Süpürme) yüksek doğrulukla ayırt edilir.

**C. Tepe Noktası Tespiti (Peak Detection) ile Adım ve Salınım Sayımı:**
Varyans ile genel durum tespit edildikten sonra, kesin mesafeyi ve fırça darbesini hesaplamak için sinyaldeki tepe noktaları sayılır. Algoritma, bir veri noktasının (örneğin ivme değerinin) hem sağındaki hem solundaki değerlerden daha büyük olup olmadığına ve sistem gürültü ortalamasını aşıp aşmadığına bakar. Şartlar sağlanıyorsa bu bir "Adım" veya "Fırça Salınımı" olarak kaydedilir. Atılan adım sayısı, ortalama adım uzunluğu (0.7m) ile çarpılarak kat edilen toplam ve gerçek temizlik mesafeleri metre cinsinden elde edilir.

**D. Kalman Filtresi (Sinyal İyileştirme):**
Ortamdaki veya kalitesiz sensörlerden kaynaklanabilecek rastgele gürültüleri filtrelemek amacıyla algoritmaya parametrik olarak (istenildiğinde aktif edilebilecek) 1D Kalman Filtresi eklenmiştir. Bu yapı, ham verideki hatalı sıçramaları yumuşatarak varyans hesaplamasının tamamen temiz veriler üzerinden yapılmasını güvence altına alır.

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
