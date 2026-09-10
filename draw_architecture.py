import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 6))

# Fonksiyon: Kutu ciz
def draw_box(ax, x, y, width, height, text, color):
    rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='black', facecolor=color, alpha=0.6)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', fontsize=12, fontweight='bold')

draw_box(ax, 1, 4, 3, 1.5, "LSM6DS3 Sensoru\n(Ivme + Jiroskop)\n[Supurge Sapi]", 'lightblue')
draw_box(ax, 1, 1, 3, 1.5, "Batarya & Guc\n(18650 Li-Ion)", 'lightgreen')
draw_box(ax, 6, 2.5, 3, 2, "STM32WLE5\n(MCU + LoRa)\n- Varyans Hesabi\n- State Machine\n- Payload Encode", 'lightcoral')
draw_box(ax, 11, 2.5, 3, 2, "LoRaWAN Gateway\n(20 km Uzaklik)\n- Merkezi Sistem", 'plum')

# Oklar
ax.annotate('', xy=(6, 4.75), xytext=(4, 4.75), arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8))
ax.annotate('', xy=(6, 1.75), xytext=(4, 1.75), arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8))
ax.annotate('12 Byte Payload', xy=(11, 3.5), xytext=(9, 3.5), arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8), ha='center', va='bottom', fontsize=10)

ax.set_xlim(0, 15)
ax.set_ylim(0, 7)
ax.axis('off')
plt.title("Akilli Supurge - Sistem Mimarisi", fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('mimari.png', dpi=300)
