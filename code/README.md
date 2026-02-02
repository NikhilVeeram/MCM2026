# EcoDrain Simulation Backend

This directory contains the mathematical engine and simulation scripts for the **MCM 2026 Project: Modeling Smartphone Battery Drain**.

## Overview
The simulation implements a continuous-time system of differential equations based on the **2RC-Thevenin Equivalent Circuit Model**. It predicts the State of Charge (SOC) and terminal voltage behavior under various hardware and software load profiles.

## Files
- `simulation.py`: High-fidelity Python script for running multi-scenario simulations.
- `simulation.ipynb`: Annotated Jupyter Notebook for interactive analysis of the 15+ equations.
- `requirements.txt`: List of Python dependencies.

## Setup & Execution

### 1. Install Dependencies
It is recommended to use a virtual environment:
```bash
pip install -r requirements.txt
```

### 2. Run Python Simulation
To execute the baseline comparison script:
```bash
python simulation.py
```
This will generate a plot saved to `../images/high_fidelity_ode_model.png`.

### 3. Run Jupyter Notebook
For interactive exploration:
```bash
jupyter notebook simulation.ipynb
```

## Mathematical Framework
The simulation covers:
- **Eq 192/352**: Governing SOC Differential Equation.
- **Eq 208-216**: 2RC-Thevenin Terminal Voltage Dynamics.
- **Eq 245**: CPU Convex Power Scaling.
- **Eq 260**: OLED Active Pixel Ratio (APR) Power Law.
- **Eq 273**: 5G Network Tail Energy & Signal Scaling.
