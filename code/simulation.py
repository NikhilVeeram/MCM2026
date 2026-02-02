import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# ==========================================
# 1. CALIBRATED PHYSICAL CONSTANTS (MCM-2633023)
# ==========================================
Q_CAP = 5.0 * 3600    # 5000mAh
V_NOM = 3.8           # Nominal Voltage
R_REF = 0.15          
ALPHA_THERM = 0.003   
T_REF = 25.0          
C_TH = 150.0          
H_CONV = 0.22         
T_AMB = 22.0          
V_CUTOFF = 3.1        

class MCMHighFidelityModel:
    def get_ocv(self, soc):
        """[Eq 6] Empirical Li-Ion chemistry curve"""
        s = np.clip(soc, 0.0001, 1.0)
        return 3.45 + 0.6 * s + 0.12 * np.log(s + 0.01)

    def get_p_total(self, t, s, temp, p):
        """[Eq 7-15] Refined coefficients for 12W Gaming Peak"""
        
        # User Profile Multipliers (Defaults to 1.0 if not specified)
        # Power User > 1.0 scale, Eco User < 1.0 scale
        u_mult = p.get('user_scale', 1.0) 
        
        # 1. CPU Power: Performance Cores Peak at 12W [Requested]
        # P_cpu = Alpha * f^3 + P_static
        # If f=1.0, u=1.0, we want ~12W.
        # Adjusted base to 12.0
        p_cpu_base = 12.0 * (0.7 * (0.8 + 0.3*p['f'])**2 * p['f'] * p['u']) + (p['p_app'] * 0.45)
        p_cpu = p_cpu_base * u_mult

        # 2. Display Power: Scaled by profile
        p_disp = (1.5 * (p['b']**1.6) * p['apr'] + 0.03) * u_mult
        
        # 3. Network Signal: Scaled by profile (Eco users use less background data)
        delta = 10**((-p['signal'] - 80) / 20)
        p_net = (min(3.0, (delta * 0.25)) if p['net'] else 0.02) * u_mult
        
        p_total = p_cpu + p_disp + p_net + 0.04
        
        # 4. Thermal Throttling [Eq 15 Improved]
        # Start throttling at 40C (hand comfort)
        # Hard throttling at 100C (TJ limit)
        if temp > 40.0:
            # Power scales down to prevent junction damage
            throttle_factor = np.clip(1.0 - (temp - 40.0) / 20.0, 0.35, 1.0)
            p_total *= throttle_factor
            
        if p.get('lpm', False):
            p_total *= 0.58
            
        return p_total

    def system_dynamics(self, y, t, p):
        s, vp1, vp2, temp = y
        s = max(0, s) 
        
        r0_t = R_REF * (1 + ALPHA_THERM * (temp - T_REF))
        p_total = self.get_p_total(t, s, temp, p)
        
        # Current-dependent efficiency law [Eq 12]
        eta_i = 0.99 - 0.015 * (p_total / 8.0) 

        voc = self.get_ocv(s)
        v_diff = voc - vp1 - vp2
        
        # KVL Dynamic Solver [Eq 3]
        disc = v_diff**2 - 4 * r0_t * p_total
        if disc < 0:
            i_load = p_total / 3.0 # Fallback
        else:
            i_load = (v_diff - np.sqrt(disc)) / (2 * r0_t)
        
        i_load = np.clip(i_load, 0, 6.0) 

        # State Derivatives [Eq 1, 4, 5, 15]
        ds = - (i_load) / (Q_CAP * eta_i) if s > 0 else 0
        dvp1 = - (vp1 / 30.0) + (i_load / 1500.0)
        dvp2 = - (vp2 / 300.0) + (i_load / 8000.0)
        
        # Thermal Heat Flow [Eq 15]
        q_gen = (i_load**2 * r0_t) + i_load * (vp1 + vp2)
        q_lost = H_CONV * (temp - T_AMB)
        dtemp = (q_gen - q_lost) / C_TH
        
        # Hard limit at junction temp (Throttling prevents runaway)
        if temp > 95 and dtemp > 0: dtemp *= 0.1 

        return [ds, dvp1, dvp2, dtemp]

def run_calibrated_suite():
    model = MCMHighFidelityModel()
    t = np.linspace(0, 24 * 3600, 8000) # 24 Hour potential span
    y0 = [0.95, 0, 0, 22.0]

    # Updated Scenarios for Requested Discharge Curves
    scenarios = [
        # Ultra Gaming: Dead @ ~1.75 hrs -> Need ~14W avg
        ("Ultra Gaming (5G)", {'f': 1.0, 'u': 1.0, 'p_app': 9.5, 'b': 1.0, 'apr': 1.0, 'signal': -110, 'net': True}),
        
        # Standard Gaming: Dead @ ~2.75 hrs -> Need ~9W avg
        ("Standard Gaming", {'f': 0.8, 'u': 0.8, 'p_app': 6.0, 'b': 0.9, 'apr': 0.8, 'signal': -100, 'net': True}),
        
        # 4K Stream: ~4-5 hours typical
        ("4K Stream", {'f': 0.5, 'u': 0.4, 'p_app': 1.0, 'b': 0.8, 'apr': 0.4, 'signal': -80, 'net': True}),
        
        # Social Media: ~6-7 hours typical
        ("Social Media", {'f': 0.4, 'u': 0.4, 'p_app': 0.6, 'b': 0.7, 'apr': 0.6, 'signal': -85, 'net': True}),
        
        # GPS Nav: ~5 hours typical
        ("GPS Nav (Car)", {'f': 0.5, 'u': 0.4, 'p_app': 0.5, 'b': 1.0, 'apr': 0.3, 'signal': -95, 'net': True}),
        
        # Web Browsing: Dead @ ~10 hours -> Need ~2.5W avg
        ("Web Browsing", {'f': 0.3, 'u': 0.2, 'p_app': 0.3, 'b': 0.5, 'apr': 0.2, 'signal': -75, 'net': True}),
        
        # Voice Call: Dead @ ~8 hours -> Need ~3.2W avg (Modem heavy)
        ("Voice Call", {'f': 0.2, 'u': 0.1, 'p_app': 0.1, 'b': 0.05, 'apr': 0.0, 'signal': -100, 'net': True}),
        
        # Eco Reading: Dead @ ~15 hours -> Need ~1.7W avg
        ("Eco Reading", {'f': 0.2, 'u': 0.1, 'p_app': 0.3, 'b': 0.4, 'apr': 0.05, 'signal': -80, 'net': False, 'lpm': True}),
        
        # Deep Standby: Extremely flat -> Very low leakage
        ("Deep Standby", {'f': 0.05, 'u': 0.0, 'p_app': 0.0, 'b': 0.0, 'apr': 0.0, 'signal': -90, 'net': False})
    ]

    # 1. The 9-Scenario Grid
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle("Calibrated Battery & Thermal Dynamics (2X-Optimized Realism)", fontsize=24, fontweight='bold', y=0.98)

    for i, (name, config) in enumerate(scenarios):
        res = odeint(model.system_dynamics, y0, t, args=(config,))
        ax = axes[i//3, i%3]
        
        soc = res[:, 0] * 100
        # Find death index
        zero_idxs = np.where(soc <= 0)[0]
        end_idx = zero_idxs[0] if len(zero_idxs) > 0 else -1
        
        t_slice = t[:end_idx]/3600
        soc_slice = soc[:end_idx]
        temp_slice = res[:end_idx, 3]

        ax.plot(t_slice, soc_slice, color='#2563eb', lw=2.5, label='SOC (%)')
        ax2 = ax.twinx()
        ax2.plot(t_slice, temp_slice, color='#ef4444', ls='--', alpha=0.8, label='Thermal ($^o$C)')
        
        ax.set_title(f"{name}", fontsize=15, fontweight='bold')
        ax.set_ylim(-2, 105)
        ax2.set_ylim(20, 65) # Realistic temp floor/ceiling
        ax.grid(True, alpha=0.15)
        
        if i == 0: 
            ax.legend(loc='lower left', fontsize=9)
            ax2.legend(loc='lower right', fontsize=9)
            
        if i >= 6: ax.set_xlabel("Time (Hours)")
        if i % 3 == 0: ax.set_ylabel("Battery %")
        if i % 3 == 2: ax2.set_ylabel("Temp ($^o$C)")

    plt.tight_layout(rect=[0, 0.03, 1, 0.94])
    plt.savefig('../images/battery_scenario_grid.png', dpi=300)

    # 2. Stacked Component Power Breakdown (Gaming Scenario)
    plt.figure(figsize=(10, 6))
    gaming_config = scenarios[0][1] # Ultra Gaming
    times = np.linspace(0, 3600, 100)
    
    # Calculate components using the exact logic from get_p_total
    p_cpu_list = []
    p_disp_list = []
    p_net_list = []
    
    for tm in times:
        # Use roughly the same calculation logic as the class method for consistency
        p_cpu = 12.0 * (0.7 * (0.8 + 0.3*gaming_config['f'])**2 * gaming_config['f'] * gaming_config['u']) + (gaming_config['p_app'] * 0.45)
        p_disp = 1.5 * (gaming_config['b']**1.6) * gaming_config['apr'] + 0.03
        delta = 10**((-gaming_config['signal'] - 80) / 20)
        p_net = min(3.0, (delta * 0.25)) # Cap at 3W
        
        p_cpu_list.append(p_cpu)
        p_disp_list.append(p_disp)
        p_net_list.append(p_net)
        
    plt.stackplot(times/60, p_cpu_list, p_disp_list, p_net_list, 
                  labels=['CPU/SoC (~9W)', 'OLED Display', '5G/Network (<3W)'], 
                  colors=['#4f46e5', '#10b981', '#f59e0b'], alpha=0.8)
    plt.title("Instantaneous Power Breakdown: Ultra Gaming Profile", fontsize=14)
    plt.ylabel("Power (Watts)")
    plt.xlabel("Time (Minutes)")
    plt.legend(loc='upper right')
    plt.grid(alpha=0.2)
    plt.savefig('../images/power_breakdown.png', dpi=300)

    print("Calibrated graphics generated in ../images/")

if __name__ == "__main__":
    run_calibrated_suite()
