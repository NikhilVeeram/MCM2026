import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, width, height, text, color='#e0e7ff', title=None):
    # Use FancyBboxPatch for rounded rectangles
    rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02", linewidth=2, edgecolor='#1e3a8a', facecolor=color)
    ax.add_patch(rect)
    
    center_x = x + width / 2
    
    if title:
        # Title near top
        ax.text(center_x, y + height - 0.03, title, ha='center', va='top', fontsize=10, fontweight='bold', color='#1e3a8a')
        # Content in middle-bottom
        ax.text(center_x, y + (height / 2) - 0.02, text, ha='center', va='center', fontsize=9, wrap=True)
    else:
        ax.text(center_x, y + height/2, text, ha='center', va='center', fontsize=9, wrap=True)
    return (x + width/2, y, x + width/2, y + height)

def draw_arrow(ax, start, end, text=None, curved=False):
    arrow_style = "Simple,tail_width=0.5,head_width=4,head_length=8"
    connection_style = "arc3,rad=-0.2" if curved else "arc3,rad=0"
    
    ax.annotate('', xy=end, xytext=start, 
                arrowprops=dict(arrowstyle="->", color='#4b5563', lw=2, connectionstyle=connection_style))
    
    if text:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2 + (0.05 if curved else 0)
        ax.text(mid_x, mid_y, text, fontsize=8, color='#374151', backgroundcolor='white', ha='center')

fig, ax = plt.subplots(figsize=(14, 10)) # Increased size for better spacing
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.0)
ax.axis('off')

# --- Layout Definitions ---
# Top Row (y approx 0.85)
box_input = (0.02, 0.82, 0.18, 0.12)
box_power = (0.28, 0.82, 0.46, 0.12)

# Middle Top (y approx 0.6)
box_agg = (0.28, 0.62, 0.22, 0.12)
box_therm = (0.54, 0.62, 0.20, 0.12) # Thermal Next to Agg
box_ocv = (0.80, 0.62, 0.18, 0.12)   # OCV on right

# Middle Low (y approx 0.45)
box_eff = (0.28, 0.44, 0.46, 0.10)

# Bottom (y approx 0.2)
box_circuit = (0.28, 0.18, 0.46, 0.15)
box_soc = (0.80, 0.18, 0.18, 0.15)

# --- Draw Boxes ---

# 1. Inputs
draw_box(ax, *box_input, "Inputs:\nFreq, Brightness, Signal", "#f3f4f6", "User Profile")

# 2. Power Models
draw_box(ax, *box_power, "Eq 7: CPU (Convex)\nEq 8: OLED (Non-linear)\nEq 9: 5G (Path Loss)", "#dbeafe", "Component Power Models")

# 3. Aggregation & Thermal
draw_box(ax, *box_agg, "Eq 6: P_total\nSum(Components)", "#bfdbfe", "Aggregation")
draw_box(ax, *box_therm, "Eq 15: Thermal Throttle\nMax(0.35, 1-dT)", "#fca5a5", "Thermal Feedback (T)")

# 6. OCV (Right)
draw_box(ax, *box_ocv, "Eq 11: OCV\nNon-linear V(S)", "#bbf7d0", "Open Circuit Voltage")

# 4. Efficiency
draw_box(ax, *box_eff, "Eq 12: Efficiency (eta)\nLinear Decay w/ Power", "#fee2e2", "Coulombic Efficiency")

# 5. Circuit Interaction
draw_box(ax, *box_circuit, "Eq 2: Load Current (I = P / V)\nEq 3-5: 2RC Voltage Drop", "#ddd6fe", "Circuit Dynamics")

# 7. SOC (Right Bottom)
draw_box(ax, *box_soc, "Eq 1: SOC\nIntegral(I/Q)", "#bbf7d0", "State of Charge")


# --- Draw Arrows ---

# Input -> Power
draw_arrow(ax, (0.20, 0.88), (0.28, 0.88))

# Power -> Aggregation
draw_arrow(ax, (0.51, 0.82), (0.39, 0.74))

# Aggregation -> Thermal (Right)
draw_arrow(ax, (0.50, 0.68), (0.54, 0.68))

# Aggregation -> Efficiency (Down)
draw_arrow(ax, (0.39, 0.62), (0.39, 0.54))

# Efficiency -> Circuit (Down)
draw_arrow(ax, (0.51, 0.44), (0.51, 0.33))

# Circuit -> SOC (Right)
draw_arrow(ax, (0.74, 0.255), (0.80, 0.255), "I_load")

# SOC -> OCV (Up)
draw_arrow(ax, (0.89, 0.33), (0.89, 0.62), "S(t)")

# OCV -> Circuit (Curve/Diagonal)
# Connect bottom of OCV to right side of Circuit or top of Circuit
# Drawing straight line from OCV bottom to Circuit top-right
draw_arrow(ax, (0.80, 0.68), (0.74, 0.33), "V_oc")

# Thermal Feedback (Red Dashed)
# Thermal to Circuit or Power? Actually Thermal affects 'Aggregation'/'Efficiency' or 'Circuit' resistance?
# In this diagram, User had arrow going down from Thermal.
# Let's verify original code: 
# "Thermal -> Actual P (implicit path down)" and "Temp depends on I^2R" back up.
# Let's draw arrow from Circuit UP to Thermal (Heat Generation)
# And Thermal DOWN to modify Power (Simulation loop)

# Circuit (Heat) -> Thermal
ax.annotate('', xy=(0.64, 0.62), xytext=(0.64, 0.33), 
            arrowprops=dict(arrowstyle="->", color='#ef4444', lw=2, linestyle="dashed"))
ax.text(0.65, 0.48, "Heat (I^2R)", fontsize=8, color='#dc2626', rotation=90)

# Thermal -> Aggregation/Eff (Throttle)
# Draw arrow from Thermal down/left to Efficiency or Aggregation
ax.annotate('', xy=(0.58, 0.54), xytext=(0.60, 0.62), 
            arrowprops=dict(arrowstyle="->", color='#ef4444', lw=2))
ax.text(0.61, 0.58, "Throttle", fontsize=8, color='#dc2626')

plt.title("Modular Interaction of Mathematical Battery Models", fontsize=16, fontweight='bold', y=0.96)
plt.tight_layout()
plt.savefig('../images/equation_flowchart.png', dpi=300)
print("Updated flowchart saved to ../images/equation_flowchart.png")
