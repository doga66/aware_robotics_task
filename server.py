import socket
import struct
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"LoRaWAN Merkezi Sunucusu Baslatildi. {UDP_PORT} portu dinleniyor...")
print("Cihazlardan veri bekleniyor...\n")

def calculate_checksum(payload_bytes):
    checksum = 0
    for b in payload_bytes:
        checksum ^= b
    return checksum

while True:
    data, addr = sock.recvfrom(1024)
    # Yeni payload boyutumuz CRC (Checksum) ile birlikte 13 Byte oldu
    if len(data) == 13:
        print(f"[{time.strftime('%H:%M:%S')}] Yeni Paket Alindi! (Gonderen IP: {addr[0]})")
        print(f"Ham Hex Payload: {data.hex().upper()}")
        
        # Gelen paketi parcala (Son byte CRC)
        unpacked = struct.unpack('>H B H H H H B B', data)
        
        dev_id = unpacked[0]
        battery = unpacked[1]
        work_time = unpacked[2]
        wait_time = unpacked[3]
        swings = unpacked[4]
        clean_dist = unpacked[5]
        status = unpacked[6]
        received_checksum = unpacked[7]
        
        # Data butunlugu dogrulamasi (CRC XOR)
        expected_checksum = calculate_checksum(data[:-1])
        
        if expected_checksum != received_checksum:
            print("!!! UYARI: Paket butunlugu bozulmus (Checksum Hatasi). Veri cope atiliyor. !!!\n")
            continue
            
        print("--- PAKET COZULDU VE DOGRULANDI (DECODED) ---")
        print(f"Cihaz ID      : {dev_id}")
        print(f"Batarya       : %{battery}")
        print(f"Calisma Suresi: {work_time} saniye")
        print(f"Bekleme Suresi: {wait_time} saniye")
        print(f"Firca Salinimi: {swings} kez")
        print(f"Temizlenen Yer: {clean_dist} metre")
        print(f"Durum Kodu    : {'OK' if status == 0 else 'HATA'}")
        print("-" * 40 + "\n")
