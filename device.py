import socket
import struct
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print("Akilli Supurge Cihazi Baslatildi.")
print("Veriler hazirlaniyor...\n")

# Gercek test verimizden elde ettigimiz sonuclar
dev_id = 2603
battery = 90
work_time = 142
wait_time = 16
swings = 90
clean_dist = 88
status_code = 0

# Veriyi 12 Byte (Big Endian) olarak paketle (C tarafindaki payload mantigi)
# >H B H H H H B
payload = struct.pack('>H B H H H H B', dev_id, battery, work_time, wait_time, swings, clean_dist, status_code)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Olusturulan 12 Byte Payload: {payload.hex().upper()}")
print(f"Veri gonderiliyor (Hedef: {UDP_IP}:{UDP_PORT})...")

# Gonder
sock.sendto(payload, (UDP_IP, UDP_PORT))

print("Gonderim Basarili! LoraMAC kuyrugundan cikarildi.")
