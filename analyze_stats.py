import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

states = [
    'durma_supurmeme',
    'durma_supurme',
    'yurume_supurmeme',
    'yurume_supurme',
    'test'
]

def load_data(state):
    acc = pd.read_csv(f'{state}/Accelerometer.csv')
    gyr = pd.read_csv(f'{state}/Gyroscope.csv')
    # Merge on seconds_elapsed or time. Since frequencies might slightly differ, let's use merge_asof or just assume they are roughly aligned if we compute windowed stats.
    # Actually, we can just calculate windowed variance for both.
    return acc, gyr

for state in states:
    acc, gyr = load_data(state)
    
    # Calculate rolling variance over 1 second (approx 100 samples if 100Hz)
    # Let's check the frequency
    dt = acc['seconds_elapsed'].diff().mean()
    freq = 1.0 / dt if dt > 0 else 0
    print(f"[{state}] Acc frequency: {freq:.2f} Hz")
    
    window_size = int(freq) # 1 second window
    
    # Magnitude of acceleration
    acc['mag'] = np.sqrt(acc['x']**2 + acc['y']**2 + acc['z']**2)
    gyr['mag'] = np.sqrt(gyr['x']**2 + gyr['y']**2 + gyr['z']**2)
    
    acc_var = acc['mag'].rolling(window_size).var().mean()
    gyr_var = gyr['mag'].rolling(window_size).var().mean()
    gyr_z_var = gyr['z'].rolling(window_size).var().mean()
    gyr_y_var = gyr['y'].rolling(window_size).var().mean()
    gyr_x_var = gyr['x'].rolling(window_size).var().mean()
    
    acc_x_var = acc['x'].rolling(window_size).var().mean()
    acc_y_var = acc['y'].rolling(window_size).var().mean()
    acc_z_var = acc['z'].rolling(window_size).var().mean()
    
    print(f"{state:20s} - Acc X Var: {acc_x_var:.4f}, Acc Y Var: {acc_y_var:.4f}, Acc Z Var: {acc_z_var:.4f}, Gyr X Var: {gyr_x_var:.4f}, Gyr Z Var: {gyr_z_var:.4f}")
