import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

# New 9 Apps
apps = [
    'Ultra Gaming', 'Standard Gaming', '4K Stream', 
    'GPS Nav', 'Social Media', 'Voice Call', 
    'Web Browsing', 'Eco Reading', 'Deep Standby'
]

# Estimated Power Allocations based on simulation.py tuning
# Total must match simulation approx (Ultra ~13W, Std ~9W, etc.)
# Components: [CPU/SoC, OLED, 5G/Network]

data = {
    'Ultra Gaming': [9.5, 1.8, 1.7],    # Total ~13W
    'Standard Gaming': [6.0, 1.5, 1.5], # Total ~9W
    '4K Stream': [1.5, 1.4, 2.0],       # High Display/Net, Low CPU
    'GPS Nav': [3.0, 1.8, 0.5],         # High CPU/Disp, Low Net (GPS is separate chip usually but lumped)
    'Social Media': [2.5, 1.2, 1.0],    # Balanced
    'Voice Call': [1.0, 0.1, 2.8],      # High Net, Low Disp
    'Web Browsing': [1.5, 0.8, 0.5],    # Lowish
    'Eco Reading': [0.8, 0.5, 0.0],     # Very Low
    'Deep Standby': [0.1, 0.0, 0.1]     # Near Zero
}

cpu_vals = [data[app][0] for app in apps]
oled_vals = [data[app][1] for app in apps]
net_vals = [data[app][2] for app in apps]

x = np.arange(len(apps))
width = 0.6

fig, ax = plt.subplots(figsize=(12, 7))

# Stacked Bar Chart
p1 = ax.bar(x, cpu_vals, width, label='CPU/SoC', color='#4f46e5', alpha=0.9)
p2 = ax.bar(x, oled_vals, width, bottom=cpu_vals, label='OLED Display', color='#10b981', alpha=0.9)
bottom_net = np.array(cpu_vals) + np.array(oled_vals)
p3 = ax.bar(x, net_vals, width, bottom=bottom_net, label='5G/Network', color='#f59e0b', alpha=0.9)

ax.set_ylabel('Avg Power Consumption (Watts)', fontweight='bold')
ax.set_title('Component Power Contribution by App Activity', fontweight='bold', fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(apps, rotation=45, ha='right')
ax.legend(loc='upper right')
ax.grid(axis='y', linestyle='--', alpha=0.9)

# Add total labels
for i in range(len(apps)):
    total = cpu_vals[i] + oled_vals[i] + net_vals[i]
    ax.text(i, total + 0.2, f"{total:.1f}W", ha='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('../images/app_power_comparison.png', dpi=300)
print("Generated ../images/app_power_comparison.png")
