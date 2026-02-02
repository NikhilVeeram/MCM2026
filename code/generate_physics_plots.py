import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# 1. OCV Curve [Eq 11]
# V_oc = 3.45 + 0.6*S + 0.12*ln(S + 0.01)
soc = np.linspace(0, 1, 100)
v_oc = 3.45 + 0.6 * soc + 0.12 * np.log(soc + 0.01)
axes[0, 0].plot(soc, v_oc, color='#2563eb', linewidth=2.5)
axes[0, 0].set_title('Open Circuit Voltage (OCV)', fontweight='bold')
axes[0, 0].set_xlabel('State of Charge (SOC)')
axes[0, 0].set_ylabel('Voltage (V)')
axes[0, 0].grid(True, linestyle='--', alpha=0.7)

# 2. Coulombic Efficiency [Eq 12]
# eta = 0.99 - 0.015 * (P / 8.0)
p_load = np.linspace(0, 15, 100) # 0 to 15 Watts
eta = 0.99 - 0.015 * (p_load / 8.0)
axes[0, 1].plot(p_load, eta, color='#ef4444', linewidth=2.5)
axes[0, 1].axvline(12, color='gray', linestyle='--', label='Max Gaming Load')
axes[0, 1].set_title('Discharge Efficiency $\eta(P)$', fontweight='bold')
axes[0, 1].set_xlabel('Total Power Load (W)')
axes[0, 1].set_ylabel('Coulombic Efficiency')
axes[0, 1].legend()

# 3. 5G Signal Penalty [Eq 9]
# delta = 10^((-L - 80)/25) per App.tsx
# p_net = min(3.0, 0.2 + delta * 2.5)
# Range: -130 dBm (Very Weak) to -70 dBm (Excellent)
signal_dbm = np.linspace(-130, -70, 100) 
delta = 10**((-signal_dbm - 80) / 25)
p_net = np.clip(0.2 + delta * 2.5, 0, 3.0)
axes[1, 0].plot(signal_dbm, p_net, color='#10b981', linewidth=2.5)
axes[1, 0].fill_between(signal_dbm, p_net, color='#10b981', alpha=0.2)
axes[1, 0].set_title('5G Power vs. Signal Strength', fontweight='bold')
axes[1, 0].set_xlabel('Signal Strength (dBm)')
axes[1, 0].set_ylabel('Modem Power (W)')
axes[1, 0].invert_xaxis() # Weak signals on left, strong on right

# 4. Thermal Throttling [Eq 15]
# scale = max(0.35, 1 - (T-40)/20)
temp = np.linspace(30, 65, 100)
throttle = np.clip(1 - (temp - 40) / 20, 0.35, 1.0)
axes[1, 1].plot(temp, throttle, color='#f59e0b', linewidth=2.5)
axes[1, 1].axvline(40, color='black', linestyle=':', label='$T_{crit}=40^\circ$C')
axes[1, 1].set_title('Thermal Throttling Factor', fontweight='bold')
axes[1, 1].set_xlabel('Device Temperature ($^\circ$C)')
axes[1, 1].set_ylabel('Performance Scale Factor')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('../images/model_physics_curves.png', dpi=300, bbox_inches='tight')
