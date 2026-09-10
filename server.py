import socket
import struct
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"LoRaWAN Merkezi Sunucusu Baslatildi. {UDP_PORT} portu dinleniyor...")
print("Cihazlardan veri bekleniyor...\n")

while True:
    data, addr = sock.recvfrom(1024)
    if len(data) == 12:
        print(f"[{time.strftime('%H:%M:%S')}] Yeni Paket Alindi! (Gonderen IP: {addr[0]})")
        print(f"Ham Hex Payload: {data.hex().upper()}")
        
        # Unpack the 12-byte payload (Big Endian)
        # > : Big Endian
        # H : unsigned short (2 bytes)
        # B : unsigned char (1 byte)
        # H H H H : 4x unsigned short
        # B : unsigned char
        unpacked = struct.unpack('>H B H H H H B', data)
        
        dev_id = unpacked[0]
        battery = unpacked[1]
        work_time = unpacked[2]
        wait_time = unpacked[3]
        swings = unpacked[4]
        clean_dist = unpacked[5]
        status = unpacked[6]
        
        print("--- PAKET COZULDU (DECODED) ---")
        print(f"Cihaz ID      : {dev_id}")
        print(f"Batarya       : %{battery}")
        print(f"Calisma Suresi: {work_time} saniye")
        print(f"Bekleme Suresi: {wait_time} saniye")
        print(f"Firca Salinimi: {swings} kez")
        print(f"Temizlenen Yer: {clean_dist} metre")
        print(f"Durum Kodu    : {'OK' if status == 0 else 'HATA'}")
        print("-" * 30 + "\n")
