import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_state(state):
    acc = pd.read_csv(f'{state}/Accelerometer.csv')
    gyr = pd.read_csv(f'{state}/Gyroscope.csv')
    
    acc['mag'] = np.sqrt(acc['x']**2 + acc['y']**2 + acc['z']**2)
    gyr['mag'] = np.sqrt(gyr['x']**2 + gyr['y']**2 + gyr['z']**2)
    
    fig, axs = plt.subplots(4, 1, figsize=(12, 12))
    
    axs[0].plot(acc['seconds_elapsed'].values, acc['mag'].values)
    axs[0].set_title(f'{state} - Acc Mag')
    
    axs[1].plot(gyr['seconds_elapsed'].values, gyr['x'].values, label='Gyr X (Sweep axis)')
    axs[1].set_title(f'{state} - Gyr X')
    
    axs[2].plot(acc['seconds_elapsed'].values, acc['y'].values, label='Acc Y (Walking direction?)')
    axs[2].plot(acc['seconds_elapsed'].values, acc['z'].values, label='Acc Z (Vertical?)')
    axs[2].legend()
    axs[2].set_title(f'{state} - Acc Y, Z')
    
    axs[3].plot(gyr['seconds_elapsed'].values, gyr['y'].values, label='Gyr Y')
    axs[3].plot(gyr['seconds_elapsed'].values, gyr['z'].values, label='Gyr Z')
    axs[3].legend()
    axs[3].set_title(f'{state} - Gyr Y, Z')
    
    plt.tight_layout()
    plt.savefig(f'{state}_plot.png')
    plt.close()

states = ['durma_supurme', 'yurume_supurme']
for s in states:
    plot_state(s)
