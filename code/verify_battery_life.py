
import numpy as np
import simulation

model = simulation.MCMHighFidelityModel()

# 4.5 W Constant Load Test
# We can't easily force 4.5W in the model without checking which parameters give that.
# instead, let's calculate Q_CAP / 4.5W
q_cap_wh = (simulation.Q_CAP / 3600) * simulation.V_NOM
print(f"Battery Capacity: {q_cap_wh:.2f} Wh")
print(f"Time to Empty at 4.5 W Load: {q_cap_wh / 4.5:.2f} hours")
print(f"Time to Empty at 5.0 W Load: {q_cap_wh / 5.0:.2f} hours")

# Also check Ultra Gaming power again
config = {'f': 1.0, 'u': 0.98, 'p_app': 5.0, 'b': 1.0, 'apr': 0.95, 'signal': -110, 'net': True}
p_total = model.get_p_total(0, 1.0, 22.0, config)
print(f"Ultra Gaming Power (New): {p_total:.4f} W")
print(f"Ultra Gaming Run Time: {q_cap_wh / p_total:.2f} hours")
