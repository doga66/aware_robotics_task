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

# --- METRIKLERI ONCEDEN HESAPLA (Animasyon sirasinda kasmamasi icin) ---
cum_working = np.zeros(len(times))
cum_waiting = np.zeros(len(times))
cum_total_dist = np.zeros(len(times))
cum_clean_dist = np.zeros(len(times))
cum_swings = np.zeros(len(times))

waiting_sec = 0.0
working_sec = 0.0
total_steps = 0
clean_steps = 0
swings = 0

window_size_samples = 200
last_w = 0

for w in range(0, len(times) - window_size_samples, window_size_samples):
    current_state = states[w]
    w_acc_y = acc_y[w:w+window_size_samples]
    w_gyr_x = gyr_x[w:w+window_size_samples]
    
    mean_y = np.mean(w_acc_y)
    mean_gx = np.mean(w_gyr_x)
    
    steps_in_window = 0
    swings_in_window = 0
    
    # Steps
    if current_state == 1 or current_state == 3:
        i = 1
        while i < window_size_samples - 1:
            if w_acc_y[i] > w_acc_y[i-1] and w_acc_y[i] > w_acc_y[i+1]:
                if w_acc_y[i] > mean_y + 0.5:
                    steps_in_window += 1
                    i += 20
                    continue
            i += 1
            
    # Swings
    if current_state == 2 or current_state == 3:
        i = 1
        while i < window_size_samples - 1:
            if w_gyr_x[i] > w_gyr_x[i-1] and w_gyr_x[i] > w_gyr_x[i+1]:
                if w_gyr_x[i] > mean_gx + 1.5:
                    swings_in_window += 1
                    i += 30
                    continue
            i += 1

    # Zaman icinde dagit
    for j in range(window_size_samples):
        idx = w + j
        cum_total_dist[idx] = total_steps * 0.7
        cum_clean_dist[idx] = clean_steps * 0.7
        cum_swings[idx] = swings
        cum_working[idx] = working_sec
        cum_waiting[idx] = waiting_sec
        
        if states[idx] == 0:
            waiting_sec += 0.01 # 100Hz
        else:
            working_sec += 0.01
            
    total_steps += steps_in_window
    if current_state == 3:
        clean_steps += steps_in_window
    swings += swings_in_window
    last_w = w

# Kalan son kismi doldur
for idx in range(last_w + window_size_samples, len(times)):
    cum_total_dist[idx] = total_steps * 0.7
    cum_clean_dist[idx] = clean_steps * 0.7
    cum_swings[idx] = swings
    cum_working[idx] = working_sec
    cum_waiting[idx] = waiting_sec
# -----------------------------------------------------------------------

# 3. Animation Setup
fig, ax = plt.subplots(figsize=(12, 7))

line_gyr, = ax.plot([], [], label='Gyr X (Sweep)', color='blue', alpha=0.7)
line_acc, = ax.plot([], [], label='Acc Y (Walk)', color='orange', alpha=0.7)

# Text for state and time (Top Left)
state_text = ax.text(0.02, 0.92, "", transform=ax.transAxes, 
                     fontsize=14, fontweight='bold', 
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

time_text = ax.text(0.02, 0.85, "", transform=ax.transAxes, 
                     fontsize=14, fontweight='bold', 
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

# Text for Performance Report (Top Right)
report_text = ax.text(0.98, 0.95, "", transform=ax.transAxes, 
                     fontsize=12, fontweight='bold', va='top', ha='right',
                     bbox=dict(facecolor='lightyellow', alpha=0.9, edgecolor='black'))

ax.set_ylim(-10, 10)
ax.set_title("Test Kaydi Icin Gercek Zamanli Algoritma Ciktisi")
ax.set_xlabel("Zaman (s)")
ax.set_ylabel("Sensor Verisi")
ax.legend(loc='lower right')
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
    report_text.set_text("")
    return line_gyr, line_acc, state_text, time_text, report_text

def update(frame):
    current_time = times[frame]
    
    start_time = max(times[0], current_time - window_size)
    ax.set_xlim(start_time, start_time + window_size)
    
    start_index = max(0, frame - int(window_size * 100))
    t_data = times[start_index:frame+1]
    
    line_gyr.set_data(t_data, gyr_x[start_index:frame+1])
    line_acc.set_data(t_data, acc_y[start_index:frame+1])
    
    current_state = states[frame]
    current_label = state_labels.get(current_state, "Bilinmeyen")
    
    state_text.set_text(f"Durum: {current_label}")
    time_text.set_text(f"Süre: {current_time:.1f} s")
    
    # Rapor Guncelleme
    report_text.set_text(
        f"--- ANLIK PERFORMANS ---\n"
        f"Mesafe (Top.): {cum_total_dist[frame]:.1f} m\n"
        f"Mesafe (Temiz): {cum_clean_dist[frame]:.1f} m\n"
        f"Aktif Sure: {cum_working[frame]:.1f} s\n"
        f"Bosta Sure: {cum_waiting[frame]:.1f} s\n"
        f"Firca Salinimi: {int(cum_swings[frame])} kez"
    )
    
    if current_state == 0: state_text.set_color('black')
    elif current_state == 1: state_text.set_color('green')
    elif current_state == 2: state_text.set_color('red')
    elif current_state == 3: state_text.set_color('blue')
        
    return line_gyr, line_acc, state_text, time_text, report_text

frames = range(0, len(times), step)
ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=1000/fps, repeat=False)

print("Video kaydediliyor... Bu islem birkac dakika surebilir (test_realtime.mp4)")
writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='Antigravity'), bitrate=1800)
try:
    ani.save('test_realtime.mp4', writer=writer)
    print("Video basariyla kaydedildi: test_realtime.mp4")
except Exception as e:
    print(f"Video kaydedilirken hata olustu: {e}")

print("Animasyon ekranda gosteriliyor...")
plt.show()
