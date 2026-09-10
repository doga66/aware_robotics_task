import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import subprocess
import sys

state = 'test'

state_labels = {
    0: "Durma & Supurmeme",
    1: "Yurume & Supurmeme",
    2: "Durma & Supurme",
    3: "Yurume & Supurme"
}

# 1. Run detector to ensure we have the latest predictions
print("Algoritma calistiriliyor...")
acc_path = f'{state}/Accelerometer.csv'
gyr_path = f'{state}/Gyroscope.csv'
out_path = f'{state}/predicted.csv'
with open(out_path, 'w') as f:
    subprocess.run(['./detector', acc_path, gyr_path], stdout=f)

# 2. Read data
print("Veriler okunuyor...")
acc = pd.read_csv(acc_path)
gyr = pd.read_csv(gyr_path)
pred = pd.read_csv(out_path)

min_len = min(len(acc), len(gyr), len(pred))
acc = acc.iloc[:min_len]
gyr = gyr.iloc[:min_len]
pred = pred.iloc[:min_len]

times = pred['time'].values
gyr_x = gyr['x'].values
acc_y = acc['y'].values
states = pred['state'].values

# 3. Animation Setup
fig, ax = plt.subplots(figsize=(10, 6))

line_gyr, = ax.plot([], [], label='Gyr X (Sweep)', color='blue', alpha=0.7)
line_acc, = ax.plot([], [], label='Acc Y (Walk)', color='orange', alpha=0.7)

# Text for state and time
state_text = ax.text(0.05, 0.9, "", transform=ax.transAxes, 
                     fontsize=14, fontweight='bold', 
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

time_text = ax.text(0.05, 0.82, "", transform=ax.transAxes, 
                     fontsize=14, fontweight='bold', 
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

ax.set_ylim(-10, 10)
ax.set_title("Test Kaydi Icin Gercek Zamanli Algoritma Ciktisi")
ax.set_xlabel("Zaman (s)")
ax.set_ylabel("Sensor Verisi")
ax.legend(loc='upper right')
ax.grid(True)

window_size = 5.0 # Saniyede ekranda gosterilecek pencere genisligi

# Parametreler
fps = 30 # Saniyedeki kare sayisi
step = int(100 / fps) # Her karede kac sample atlanacak (100Hz data)
if step < 1: step = 1

def init():
    line_gyr.set_data([], [])
    line_acc.set_data([], [])
    state_text.set_text("")
    time_text.set_text("")
    return line_gyr, line_acc, state_text, time_text

def update(frame):
    # frame is the current index in the data array
    current_time = times[frame]
    
    # Ekranda gorunecek verinin araligini belirle
    start_time = max(times[0], current_time - window_size)
    ax.set_xlim(start_time, start_time + window_size)
    
    # Hangi indexlerin cizilecegini bul
    start_index = max(0, frame - int(window_size * 100))
    
    t_data = times[start_index:frame+1]
    
    line_gyr.set_data(t_data, gyr_x[start_index:frame+1])
    line_acc.set_data(t_data, acc_y[start_index:frame+1])
    
    current_state = states[frame]
    current_label = state_labels.get(current_state, "Bilinmeyen")
    
    state_text.set_text(f"Durum: {current_label}")
    time_text.set_text(f"Süre: {current_time:.1f} s")
    
    # Rengi duruma gore degistir
    if current_state == 0:
        state_text.set_color('black')
    elif current_state == 1:
        state_text.set_color('green')
    elif current_state == 2:
        state_text.set_color('red')
    elif current_state == 3:
        state_text.set_color('blue')
        
    return line_gyr, line_acc, state_text, time_text

frames = range(0, len(times), step)
ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=1000/fps, repeat=False)

print("Video kaydediliyor... Bu islem birkac dakika surebilir (test_realtime.mp4)")
# Kaydetme islemi
writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='Antigravity'), bitrate=1800)
try:
    ani.save('test_realtime.mp4', writer=writer)
    print("Video basariyla kaydedildi: test_realtime.mp4")
except Exception as e:
    print(f"Video kaydedilirken hata olustu (Sisteminizde FFmpeg kurulu olmayabilir): {e}")

print("Animasyon ekranda gosteriliyor...")
plt.show()
