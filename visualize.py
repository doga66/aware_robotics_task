import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os

states = [
    'durma_supurmeme',
    'durma_supurme',
    'yurume_supurmeme',
    'yurume_supurme',
    'test'
]

state_labels = {
    0: "Durma & Supurmeme",
    1: "Yurume & Supurmeme",
    2: "Durma & Supurme",
    3: "Yurume & Supurme"
}

def run_detector(state):
    acc_path = f'{state}/Accelerometer.csv'
    gyr_path = f'{state}/Gyroscope.csv'
    out_path = f'{state}/predicted.csv'
    
    with open(out_path, 'w') as f:
        subprocess.run(['./detector', acc_path, gyr_path], stdout=f)
    
    return pd.read_csv(out_path)

fig, axs = plt.subplots(5, 1, figsize=(14, 20))

for i, state in enumerate(states):
    acc = pd.read_csv(f'{state}/Accelerometer.csv')
    gyr = pd.read_csv(f'{state}/Gyroscope.csv')
    pred = run_detector(state)
    
    # Align data for plotting
    min_len = min(len(acc), len(gyr), len(pred))
    acc = acc.iloc[:min_len]
    gyr = gyr.iloc[:min_len]
    pred = pred.iloc[:min_len]
    
    ax = axs[i]
    
    # Plot IMU features used in logic
    ax.plot(pred['time'].values, gyr['x'].values, label='Gyr X (Sweep)', alpha=0.6, color='blue')
    ax.plot(pred['time'].values, acc['y'].values, label='Acc Y (Walk)', alpha=0.6, color='orange')
    
    # Plot predicted state as a scaled line
    # Scale state from 0-3 to 0-6 for visibility on the same axis
    ax.plot(pred['time'].values, pred['state'].values * 2 - 3, label='Predicted State', linewidth=2, color='red', linestyle='--')
    
    # Find most common state for text
    most_common_idx = pred['state'].mode()[0]
    most_common_label = state_labels[most_common_idx]
    
    # Text in visualization
    ax.text(0.01, 0.9, f"Ground Truth: {state}\nAlgorithm Output: {most_common_label}", 
            transform=ax.transAxes, fontsize=12, fontweight='bold', 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
            
    ax.set_title(f'Scenario: {state}')
    ax.legend(loc='upper right')
    ax.set_ylim(-10, 10)
    ax.grid(True)

plt.tight_layout()
plt.savefig('final_visualization.png')
print("Visualization saved to final_visualization.png")
