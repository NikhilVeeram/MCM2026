import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# ==========================================
# CONSTANTS & COEFFICIENTS
# Derived from LaTeX report modeling
# ==========================================
Q_CAP_MAX = 3274 * 3600  # mAh to Coulomb (As)
R_INTERNAL = 0.0233      # Ohms (Internal Resistance)
V_NOMINAL = 3.7          # Volts
ALPHA_LIGHT = 0.8        # Active Pixel Ratio (Light Mode)
ALPHA_DARK = 0.1         # Active Pixel Ratio (Dark Mode)
P_TAIL_5G = 0.5          # Watts (Tail Energy)
TAU_TAIL = 1.5           # Seconds (Tail Duration)

class SmartphoneBattery:
    def __init__(self, soc_init=1.0, health=1.0):
        self.soc = soc_init
        self.capacity = Q_CAP_MAX * health
        self.v_term = V_NOMINAL
        # 2RC Parameters based on report
        self.r0 = R_INTERNAL
        self.r1 = 0.015
        self.c1 = 2000
        self.r2 = 0.030
        self.c2 = 10000
        # State Vector: [SOC, V_p1, V_p2]
        self.state = [soc_init, 0.0, 0.0]

    def get_ocv(self, soc):
        """
        Open Circuit Voltage curve (Non-linear).
        Approximated from Li-Ion discharge curve in report.
        """
        # Ensure SOC doesn't go below 0 for log
        soc_clamped = max(soc, 0.001)
        return 3.0 + 1.0 * soc_clamped + 0.2 * np.log(soc_clamped + 0.01)

    def power_drain_model(self, t, profile):
        """
        Calculates P_total based on active profile markers.
        Includes CPU, Display, and Network components.
        """
        # Hardware: Display (OLED Model)
        # Beta_max * Brightness * Alpha (Pixel Ratio)
        p_disp = 1.8 * profile['brightness'] * profile['alpha']
        
        # Hardware: CPU (Convex Model: P = k * V^2 * f * U)
        # Simplified to k' * f^2 * U assuming V proportional to f
        p_cpu = 3.5 * (profile['cpu_freq'] ** 2) * profile['cpu_util']
        
        # Hardware: Network (Tail Energy & Signal Strength)
        signal_scaling = profile.get('signal_factor', 1.0)
        if profile['network_active']:
            p_net = 2.1 * signal_scaling
        elif t < profile.get('last_tx_time', -100) + TAU_TAIL:
            p_net = P_TAIL_5G  # Tail State
        else:
            p_net = 0.05  # Idle / Standby
            
        # Miscellaneous / Parasitic
        p_misc = 0.1
        
        total_p = p_disp + p_cpu + p_net + p_misc
        
        # Apply Low Power Mode (LPM) coefficient if enabled
        if profile.get('lpm_enabled', False):
            # LPM limits background, reduces brightness, throttles CPU
            total_p *= 0.65 
            
        return total_p

def differential_eqs(y, t, battery, profile):
    """
    System of Differential Equations for 2RC Model.
    y = [SOC, V_p1, V_p2]
    """
    soc, v_p1, v_p2 = y
    
    # 1. Calculate Total Power Demand
    p_total = battery.power_drain_model(t, profile)
    
    # 2. Estimate Load Current (I = P / V_term)
    v_oc = battery.get_ocv(soc)
    # V_term = V_oc - I*R0 - Vp1 - Vp2
    # To avoid algebraic loop, we use an approximation for I or solve for it:
    # V_term = V_oc - (P/V_term)*R0 - Vp1 - Vp2
    # V_term^2 - (V_oc - Vp1 - Vp2)*V_term + P*R0 = 0
    v_diff = v_oc - v_p1 - v_p2
    discriminant = v_diff**2 - 4 * p_total * battery.r0
    
    if discriminant < 0:
        # Battery collapsed under load
        v_term = 2.5 
    else:
        v_term = (v_diff + np.sqrt(discriminant)) / 2
        
    i_load = p_total / v_term
    
    # 3. SOC Derivative (Coulomb Counting)
    d_soc = - (1 / battery.capacity) * i_load
    
    # 4. Polarization Voltage Derivatives (2RC Dynamics)
    d_vp1 = -(v_p1 / (battery.r1 * battery.c1)) + (i_load / battery.c1)
    d_vp2 = -(v_p2 / (battery.r2 * battery.c2)) + (i_load / battery.c2)
    
    return [d_soc, d_vp1, d_vp2]

def run_simulation(duration_hrs, profile):
    """
    Runs the simulation for a given profile over a duration.
    """
    t_points = np.linspace(0, duration_hrs * 3600, 2000)
    battery = SmartphoneBattery()
    
    solution = odeint(differential_eqs, battery.state, t_points, 
                      args=(battery, profile))
    
    return t_points, solution

if __name__ == "__main__":
    # Define Scenarios
    power_user = {
        'brightness': 1.0, 'alpha': 0.8, 
        'cpu_freq': 1.0, 'cpu_util': 0.8,
        'network_active': True, 'signal_factor': 1.8, # Poor signal
        'lpm_enabled': False
    }
    
    limited_user = {
        'brightness': 0.3, 'alpha': 0.1, # Dark Mode
        'cpu_freq': 0.5, 'cpu_util': 0.2,
        'network_active': False, 'signal_factor': 1.0,
        'lpm_enabled': True
    }
    
    hrs = 8
    t_p, sol_p = run_simulation(hrs, power_user)
    t_l, sol_l = run_simulation(hrs, limited_user)
    
    plt.figure(figsize=(10, 6))
    plt.plot(t_p / 3600, sol_p[:, 0] * 100, label='Power User (Poor Signal, Bright, Gaming)')
    plt.plot(t_l / 3600, sol_l[:, 0] * 100, label='Limited User (Dark Mode, LPM, Low Util)')
    plt.xlabel('Time (Hours)')
    plt.ylabel('State of Charge (%)')
    plt.title('Smartphone Battery Drain Simulation')
    plt.legend()
    plt.grid(True)
    plt.savefig('../images/battery_drain_simulation.png')
    print("Simulation complete. Results saved to ../images/battery_drain_simulation.png")
    
    print(f"Final SOC (Power User): {sol_p[-1, 0]*100:.2f}%")
    print(f"Final SOC (Limited User): {sol_l[-1, 0]*100:.2f}%")
