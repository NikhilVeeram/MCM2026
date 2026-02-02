
import numpy as np
import simulation

model = simulation.MCMHighFidelityModel()
config = {'f': 1.0, 'u': 0.98, 'p_app': 5.0, 'b': 1.0, 'apr': 0.95, 'signal': -110, 'net': True}
# p_total(t, s, temp, p)
# t=0, s=1.0, temp=22.0
p_total = model.get_p_total(0, 1.0, 22.0, config)
print(f"Ultra Gaming Power: {p_total:.4f} W")
