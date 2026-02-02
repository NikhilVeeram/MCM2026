import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, width, height, text, color='#e0e7ff', title=None):
    # Use FancyBboxPatch for rounded rectangles
    rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02", linewidth=2, edgecolor='#1e3a8a', facecolor=color)
    ax.add_patch(rect)
    if title:
        ax.text(x + width/2, y + height - 0.02, title, ha='center', va='top', fontsize=9, fontweight='bold', color='#1e3a8a')
        ax.text(x + width/2, y + height/2 - 0.02, text, ha='center', va='center', fontsize=8, wrap=True)
    else:
        ax.text(x + width/2, y + height/2, text, ha='center', va='center', fontsize=8, wrap=True)
    return (x + width/2, y, x + width/2, y + height)

def draw_arrow(ax, start, end, text=None):
    ax.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color='#4b5563', lw=1.5))
    if text:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x + 0.02, mid_y, text, fontsize=7, color='#374151', backgroundcolor='white')

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.0)
ax.axis('off')

# 1. Inputs (Left)
draw_box(ax, 0.05, 0.8, 0.15, 0.1, "Inputs:\nFreq, Brightness, Signal", "#f3f4f6", "User Profile")

# 2. Power Models (Top Middle)
draw_box(ax, 0.3, 0.8, 0.4, 0.12, "Eq 7: CPU (Convex)\nEq 8: OLED (Non-linear)\nEq 9: 5G (Path Loss)", "#dbeafe", "Component Power Models")

# 3. Aggregation & Thermal (Middle)
draw_box(ax, 0.3, 0.55, 0.18, 0.1, "Eq 6: P_total\nSum(Components)", "#bfdbfe", "Aggregation")
draw_box(ax, 0.52, 0.55, 0.18, 0.1, "Eq 15: Thermal Throttle\nMax(0.35, 1-dT)", "#fca5a5", "Thermal Feedback (T)")

# 4. Efficiency (Middle Lower)
draw_box(ax, 0.3, 0.35, 0.4, 0.08, "Eq 12: Efficiency (eta)\nLinear Decay w/ Power", "#fee2e2", "Coulombic Efficiency")

# 5. Circuit Interaction (Bottom)
draw_box(ax, 0.3, 0.15, 0.4, 0.1, "Eq 2: Load Current (I = P / V)\nEq 3-5: 2RC Voltage Drop", "#ddd6fe", "Circuit Dynamics")

# 6. State (Right)
draw_box(ax, 0.8, 0.15, 0.15, 0.1, "Eq 1: SOC\nIntegral(I/Q)", "#bbf7d0", "State of Charge")
draw_box(ax, 0.8, 0.55, 0.15, 0.1, "Eq 11: OCV\nNon-linear V(S)", "#bbf7d0", "Open Circuit Voltage")

# Arrows
draw_arrow(ax, (0.2, 0.85), (0.3, 0.85)) # Input -> Models
draw_arrow(ax, (0.5, 0.8), (0.4, 0.65))  # Models -> Aggregation (offset manual)
draw_arrow(ax, (0.48, 0.6), (0.52, 0.6)) # Agg -> Thermal
draw_arrow(ax, (0.61, 0.55), (0.61, 0.47)) # Thermal -> Actual P (implicit path down)
draw_arrow(ax, (0.5, 0.55), (0.5, 0.43)) # Agg -> Eff (Visual flow)

# Structural connectors
ax.annotate('', xy=(0.5, 0.43), xytext=(0.5, 0.55), arrowprops=dict(arrowstyle="->", color='#4b5563', lw=1.5)) # P -> Eff
ax.annotate('', xy=(0.5, 0.25), xytext=(0.5, 0.35), arrowprops=dict(arrowstyle="->", color='#4b5563', lw=1.5)) # Eff -> Circuit

draw_arrow(ax, (0.7, 0.2), (0.8, 0.2), "I_load") # Circuit -> SOC
draw_arrow(ax, (0.875, 0.25), (0.875, 0.55), "S(t)") # SOC -> OCV
draw_arrow(ax, (0.8, 0.6), (0.7, 0.25)) # OCV -> Circuit (Feedback)

# Thermal Loop
ax.text(0.72, 0.4, "Temp depends on I^2R", fontsize=7, style='italic', color='red')
ax.annotate('', xy=(0.65, 0.55), xytext=(0.65, 0.25), arrowprops=dict(arrowstyle="->", color='red', lw=1, linestyle="--"))

plt.title("Modular Interaction of Mathematical battery Models", fontsize=14, fontweight='bold', y=0.95)
plt.tight_layout()
plt.savefig('../images/equation_flowchart.png', dpi=300)
