import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# ==========================================
# 1. CONSTANTS & PARAMETERS (Table 1/Appendix D)
# ==========================================
Q_CAP = 3274 * 3600  # Capacity in Coulombs (As) [Eq 192/352]
R0 = 0.0233          # Internal Ohmic Resistance (Ohms) [Eq 208]
R1, C1 = 0.015, 2000 # Short-term RC branch parameters [Eq 214]
R2, C2 = 0.030, 10000# Long-term RC branch parameters [Eq 215]
ETA = 0.98           # Coulombic Efficiency [Eq 198]
P_IDLE = 0.05        # Baseline idle power (W)
P_TAIL_5G = 0.5      # Tail state power (W) [Eq 273]
TAU_TAIL = 1.5       # Tail state duration (s)

class MCMBatterySimulator:
    def __init__(self):
        # State Vector: [SOC (S), V_p1, V_p2]
        self.y0 = [1.0, 0.0, 0.0]

    def get_ocv(self, soc):
        """[Eq 565/Appendix A] Non-linear Open Circuit Voltage curve"""
        s = np.clip(soc, 0.001, 1.0)
        return 3.0 + 1.0 * s + 0.2 * np.log(s + 0.01)

    def get_p_cpu(self, freq, util, cores=8):
        """[Eq 245] CPU Power: P = cores * (alpha * V^2 * f * U + P_static)"""
        # Dynamic Voltage Scaling approximation: V(f) = 0.8 + 0.4*f
        v = 0.8 + 0.4 * freq
        p_dyn = cores * (0.125 * (v**2) * freq * util)
        return p_dyn + 0.05

    def get_p_disp(self, brightness, apr):
        """[Eq 260] OLED Power: P = Beta * B * Gamma + P_base"""
        return 1.95 * brightness * apr + 0.02

    def get_p_net(self, t, last_tx, signal_strength, active=True):
        """[Eq 273] Networking: P = Delta(L) * (D_rate * E_bit + P_tail)"""
        # Delta factor based on signal dBm
        delta = 10**((-signal_strength - 80) / 16) 
        if active:
            return delta * 2.2 + P_IDLE
        elif t < last_tx + TAU_TAIL:
            return P_TAIL_5G
        return P_IDLE

    def derivatives(self, y, t, p):
        soc, vp1, vp2 = y
        
        # 1. Aggregate Power [Eq 352]
        pcpu = self.get_p_cpu(p['f'], p['u'])
        pdisp = self.get_p_disp(p['b'], p['apr'])
        pnet = self.get_p_net(t, p['last_tx'], p['signal'], p['net'])
        p_total = pcpu + pdisp + pnet + 0.1 # misc
        
        # 2. LPM Scaling [Eq 362]
        if p.get('lpm', False):
            p_total *= 0.55 # Significant reduction for visualization
            
        # 3. Voltage/Current Solver [Eq 198/208]
        voc = self.get_ocv(soc)
        v_diff = voc - vp1 - vp2
        discriminant = v_diff**2 - 4 * R0 * p_total
        
        if discriminant < 0:
            i = p_total / 2.5 # Minimum sustain voltage
        else:
            i = (v_diff - np.sqrt(discriminant)) / (2 * R0)
            
        # 4. State Updates [Eq 192, 214, 215]
        dsoc = - (1 / Q_CAP) * (i / ETA)
        dvp1 = - (vp1 / (R1 * C1)) + (i / C1)
        dvp2 = - (vp2 / (R2 * C2)) + (i / C2)
        
        return [dsoc, dvp1, dvp2]

def run():
    sim = MCMBatterySimulator()
    t = np.linspace(0, 10 * 3600, 4000) # 10h Simulation
    
    # Define Profiles
    power = {'f': 1.0, 'u': 0.95, 'b': 1.0, 'apr': 0.9, 'signal': -115, 'net': True, 'last_tx': 0}
    standard = {'f': 0.7, 'u': 0.5, 'b': 0.6, 'apr': 0.4, 'signal': -90, 'net': False, 'last_tx': 10}
    eco = {'f': 0.4, 'u': 0.2, 'b': 0.3, 'apr': 0.05, 'signal': -80, 'net': False, 'last_tx': -1, 'lpm': True}

    res_p = odeint(sim.derivatives, sim.y0, t, args=(power,))
    res_s = odeint(sim.derivatives, sim.y0, t, args=(standard,))
    res_e = odeint(sim.derivatives, sim.y0, t, args=(eco,))

    plt.figure(figsize=(12, 7))
    plt.plot(t/3600, res_p[:, 0]*100, color='#ff4757', label='Extreme Build (Gaming + 5G)', lw=2.5)
    plt.plot(t/3600, res_s[:, 0]*100, color='#ffa502', label='Standard Profile', lw=2)
    plt.plot(t/3600, res_e[:, 0]*100, color='#2ed573', label='Eco Mode (Dark + LPM)', lw=2.5)
    
    plt.title("Physical Battery Drain Simulation [MCM Continuous-Time Model]", fontsize=14, fontweight='bold')
    plt.xlabel("Time (Hours)", fontsize=12)
    plt.ylabel("Battery Percentage (%)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.15)
    plt.axhline(0, color='black', lw=1, alpha=0.5)
    plt.ylim(-5, 105)
    plt.savefig('../images/high_fidelity_ode_model.png')
    print("Simulation complete. Image saved to images/high_fidelity_ode_model.png")
    plt.show()

if __name__ == "__main__":
    run()
