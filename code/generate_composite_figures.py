
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def create_composite_figure(user_type, main_data, workloads, filename, color_palette):
    """
    Creates a composite figure with one main plot and 5 surrounding workload plots.
    """
    fig = plt.figure(figsize=(15, 10))
    gs = gridspec.GridSpec(3, 3, figure=fig)

    # Main Figure in the Center (Occupies center)
    # Actually, "surrounding" suggests center is main, and others are around.
    # Grid:
    # [Sub1] [Sub2] [Sub3]
    # [Sub4] [MAIN] [Sub5] -> Main can't be bigger easily here.
    
    # Better Layout:
    # [Main Main] [Sub1]
    # [Main Main] [Sub2]
    # [Sub3] [Sub4] [Sub5]
    
    # Or:
    # [Sub1] [Sub2] [Sub3] - Top Row
    # [Sub4] [Main] [Sub5] - Main in middle, but 2x scale? No.
    
    # Let's do:
    # Main Figure: Top Left 2x2
    # Sub1: Top Right
    # Sub2: Middle Right
    # Sub3: Bottom Left
    # Sub4: Bottom Middle 
    # Sub5: Bottom Right
    
    # Correct GridSpec for this:
    # 3x3 Grid
    # Main: [0:2, 0:2]
    # Sub1: [0, 2]
    # Sub2: [1, 2]
    # Sub3: [2, 0]
    # Sub4: [2, 1]
    # Sub5: [2, 2]
    
    ax_main = fig.add_subplot(gs[0:2, 0:2])
    ax_sub1 = fig.add_subplot(gs[0, 2])
    ax_sub2 = fig.add_subplot(gs[1, 2])
    ax_sub3 = fig.add_subplot(gs[2, 0])
    ax_sub4 = fig.add_subplot(gs[2, 1])
    ax_sub5 = fig.add_subplot(gs[2, 2])
    
    subs = [ax_sub1, ax_sub2, ax_sub3, ax_sub4, ax_sub5]
    
    # --- Main Figure Styling ---
    # Breakdown of Total Energy for the Profile
    # main_data = {'CPU': x, 'Display': y, 'Network': z, 'Other': w}
    labels = list(main_data.keys())
    sizes = list(main_data.values())
    explode = (0.05, 0, 0, 0)  # offset the first slice
    
    # Use distinct colors from palette
    colors = color_palette[:len(labels)]
    
    ax_main.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, 
                textprops={'fontsize': 14, 'fontweight': 'bold'}, pctdistance=0.85, explode=explode)
    
    # Draw circle
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    ax_main.add_artist(centre_circle)
    
    ax_main.set_title(f"{user_type} Profile: Average Power Breakdown", fontsize=18, fontweight='bold')
    ax_main.text(0, 0, f"Total\n~{sum(sizes):.1f} W", ha='center', va='center', fontsize=20, fontweight='bold')

    # --- Subplots Styling ---
    # Each workload has a mini bar chart of components
    
    for ax, (name, data) in zip(subs, workloads.items()):
        # data = [cpu, display, net]
        components = ['CPU', 'Disp', 'Net']
        vals = data
        
        # Determine max power for text
        total_p = sum(vals)
        
        ax.bar(components, vals, color=colors[:3])
        ax.set_title(name, fontsize=12, fontweight='bold')
        ax.set_ylim(0, max(14, total_p * 1.5)) # Fixed scale for consistency roughly
        ax.grid(axis='y', alpha=0.3)
        
        # Add Max Power Draw Text
        ax.text(0.5, 0.9, f"Max: {total_p:.1f}W", transform=ax.transAxes, 
                ha='center', color='red', fontweight='bold', fontsize=11)
        
        # Remove some clutter
        ax.tick_params(axis='y', labelsize=8)
        ax.tick_params(axis='x', labelsize=9)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"Generated {filename}")

# --- Data Definition ---

# 1. Power User Data
# Palette: Red/Orange/Yellow theme for High Power? Or standard Blue/Green/Orange.
# User asked for "different color scheme" for Limited user.
# Power User: "Hot" colors or Standard. Let's use "Standard" (Blue/Green/Red).
power_palette = ["#ef4444", "#10b981", "#3b82f6", "#f59e0b"] # Red, Green, Blue, Orange

power_main = {
    'CPU/SoC': 6.0,
    'Display (OLED)': 2.5,
    '5G Network': 3.5,
    'Background': 1.0
}

power_workloads = {
    'Ultra Gaming\n(120Hz, High)': [9.5, 1.8, 1.7],
    '4K Streaming\n(5G, HDR)': [1.5, 1.4, 2.1],
    'Web Browsing\n(Light Mode)': [2.5, 1.8, 1.0],
    'Video Call\n(5G, 60fps)': [3.0, 1.5, 2.5],
    'Multitasking\n(Split Screen)': [5.0, 2.0, 1.2]
}

create_composite_figure("Power User", power_main, power_workloads, "../images/power_user_composite.png", power_palette)

# 2. Limited User Data
# Palette: Cool/Eco colors (Teal, Blue, Grey)
# User said "different color scheme than anything else".
# Let's try Purple/Pink/Cyan or just very "Cool" tones.
limited_palette = ["#8b5cf6", "#06b6d4", "#64748b", "#94a3b8"] # Violet, Cyan, Slate, LightSlate

limited_main = {
    'CPU/SoC': 0.5,
    'Display (OLED)': 0.8,
    'Network (WiFi)': 0.3,
    'Background': 0.1
}

limited_workloads = {
    'Eco Reading\n(Dark Mode)': [0.2, 0.3, 0.0],
    'Audio Streaming\n(Screen Off)': [0.3, 0.0, 0.2],
    'Texting\n(WiFi, Dark)': [0.5, 0.6, 0.1],
    'Standby\n(Deep Sleep)': [0.05, 0.0, 0.1],
    'Web Browsing\n(Eco Mode)': [0.8, 0.5, 0.2]
}

create_composite_figure("Limited User", limited_main, limited_workloads, "../images/limited_user_composite.png", limited_palette)
