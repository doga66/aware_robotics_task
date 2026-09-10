import pandas as pd
import numpy as np

def classify_window(acc_window, gyr_window):
    gyr_x_var = np.var(gyr_window['x'])
    acc_y_var = np.var(acc_window['y'])
    
    if gyr_x_var > 1.5: # Sweeping
        if acc_y_var > 0.3:
            return "Yurume & Supurme"
        else:
            return "Durma & Supurme"
    else: # Not Sweeping
        if acc_y_var > 0.1:
            return "Yurume & Supurmeme"
        else:
            return "Durma & Supurmeme"

def process_file(state):
    acc = pd.read_csv(f'{state}/Accelerometer.csv')
    gyr = pd.read_csv(f'{state}/Gyroscope.csv')
    
    # Simple alignment by index since they have same freq
    min_len = min(len(acc), len(gyr))
    acc = acc.iloc[:min_len]
    gyr = gyr.iloc[:min_len]
    
    window_size = 200 # 2 seconds
    results = []
    
    for i in range(0, min_len - window_size, window_size):
        w_acc = acc.iloc[i:i+window_size]
        w_gyr = gyr.iloc[i:i+window_size]
        res = classify_window(w_acc, w_gyr)
        results.append(res)
        
    from collections import Counter
    print(f"[{state}] {Counter(results)}")

states = ['durma_supurmeme', 'durma_supurme', 'yurume_supurmeme', 'yurume_supurme', 'test']
for s in states:
    process_file(s)
