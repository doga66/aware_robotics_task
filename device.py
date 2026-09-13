import socket
import struct
import subprocess
import re
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print("Akilli Supurge Cihazi Baslatildi.")
print("Guc tasarrufu (Deep Sleep) ve 30 Dakikalik Periyodik Gonderim aktif...\n")

while True:
    print(f"[{time.strftime('%H:%M:%S')}] UYANIŞ: 30 dakikalik zamanlayici (Timer) tetiklendi!")
    print("1. Cihazdaki sensor verileri analiz ediliyor (Edge Computing)...")

    # Gercek C kodunu calistir ve stderr ciktisini yakala
    result = subprocess.run(['./detector', 'test/Accelerometer.csv', 'test/Gyroscope.csv'], capture_output=True, text=True)
    output = result.stderr

    try:
        clean_dist = int(float(re.search(r"2\. Gercek Temizlik Mesafesi : ([\d\.]+) metre", output).group(1)))
        work_time = int(re.search(r"3\. Calisma \(Aktif\) Suresi   : (\d+) saniye", output).group(1))
        wait_time = int(re.search(r"4\. Bekleme \(Bosta\) Suresi   : (\d+) saniye", output).group(1))
        swings = int(re.search(r"5\. Toplam Supurme Hareketi  : (\d+) salinim", output).group(1))
    except Exception as e:
        print(f"Hata: Veri analiz edilemedi. {e}")
        time.sleep(5)
        continue

    dev_id = 2603
    battery = 87 # Ornek pil yuzdesi
    status_code = 0

    print(f"2. Analiz Tamamlandi! Sonuclar:")
    print(f" - Calisma: {work_time}s, Bekleme: {wait_time}s, Salinim: {swings}, Mesafe: {clean_dist}m")

    # Veriyi 12 Byte (Big Endian) olarak paketle
    base_payload = struct.pack('>H B H H H H B', dev_id, battery, work_time, wait_time, swings, clean_dist, status_code)

    # Veri Butunlugu Icin Basit CRC (Checksum) Hesaplama - XOR mantigiyla 1 Byte
    checksum = 0
    for b in base_payload:
        checksum ^= b

    final_payload = base_payload + struct.pack('>B', checksum)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"3. Veri LoRaWAN uzerinden gonderiliyor (Hedef: {UDP_IP}:{UDP_PORT})...")
    sock.sendto(final_payload, (UDP_IP, UDP_PORT))
    
    print("4. Gonderim Basarili! LoraMAC kuyrugundan cikarildi.")
    print("--- CIHAZ 30 DAKIKA BOYUNCA DERIN UYKUYA (DEEP SLEEP) GECIYOR ---\n")
    
    # Gercek sistemde burada uykuya gecilir. Simulasyon hizli aksin diye 5 saniye bekletiyoruz.
    time.sleep(5)
