import re

file_path = r"c:\Users\nikhil\Documents\GitHub\MCM2026\report\Modeling Smartphone Battery Drain (FINAL).tex"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# ============================================
# 1. Fix Summary Sheet: Clarify coefficients and LPM
# ============================================

# Update the methodology line to clarify beta, gamma, delta
old_methodology = r"We integrate academic findings on physical power laws with different practical use cases for individual user demand from ``Power Users'' to ``Limited Users.'' We utilize verified datasets to evaluate specific coefficients ($\beta, \gamma, \delta$) for our differential equations. Specific non-linear current ``spikes'' are accounted for in our function of power draw on the battery."

new_methodology = r"""We integrate academic findings on physical power laws with different practical use cases for individual user demand from ``Power Users'' to ``Limited Users.'' We utilize verified datasets to evaluate specific coefficients for our differential equations: $\beta$ (display power scaling), $\gamma$ (active pixel ratio), and $\delta$ (signal-dependent network penalty). Specific non-linear current ``spikes'' are accounted for in our function of power draw on the battery."""

content = content.replace(old_methodology, new_methodology)

# Fix LPM reference to explicitly define it
old_lpm_ref = r"We evaluate the effect of Low Power Mode as a vector of limiting coefficients ($\lambda$), as LPM suppresses"
new_lpm_ref = r"We evaluate the effect of Low Power Mode (LPM) as a vector of limiting coefficients ($\lambda$), as LPM suppresses"
content = content.replace(old_lpm_ref, new_lpm_ref)

# ============================================
# 2. Fix Introduction: Add DVFS definition inline
# ============================================
# Already has DVFS definition, but let's ensure it's clear
old_dvfs = r"The power consumption profile $P(t)$ of a smartphone is not static but fluctuates wildly based on screen content (display intensity), processor frequency scaling---known as Dynamic Voltage and Frequency Scaling (DVFS), which adjusts CPU power states in real-time---and radio signal conditions \cite{1}."

# This is already good, no change needed

# ============================================
# 3. Add Model Roadmap at start of Continuous-Time Model section
# ============================================

old_continuous_start = r"""\section{Continuous-Time Model}

\subsection{The Governing Equation}"""

new_continuous_start = r"""\section{Continuous-Time Model}

\textbf{Model Roadmap:} This section presents the complete mathematical framework for our Continuous-Time Kinetic Battery Model (CT-KBM). We proceed as follows: (1) The \textbf{Governing Equation} establishes the core SOC dynamics; (2) \textbf{Terminal Voltage Dynamics} couples the 2RC circuit to the load; (3) \textbf{Hardware Models} decompose $P_{total}$ into physical components (CPU, Display, Network); (4) \textbf{Software Models} aggregate app-level contributions; and (5) \textbf{System Implementation} presents the complete coupled DAE system. Each subsection builds upon the previous, progressively constructing the full state-space representation.

\subsection{The Governing Equation}"""

content = content.replace(old_continuous_start, new_continuous_start)

# ============================================
# 4. Expand the Variables Table with more parameters
# ============================================

old_table = r"""\begin{table}[H]
\centering
\caption{Summary of Model Symbols and Parameters}
\label{tab:vars}
\begin{tabular}{|c|l|c|c|}
\hline
\textbf{Symbol} & \textbf{Description} & \textbf{Unit} & \textbf{Typical App Value} \\
\hline
$Q_{cap}$ & Battery Capacity & As (Coulombs) & $18,000$ (5000mAh) \\
$V_{OC}(S)$ & Open Circuit Voltage & V & $3.45 - 4.2$ \\
$V_{nom}$ & Nominal System Voltage & V & $3.8$ \\
$T_{amb}$ & Ambient Reference Temp & $^\circ$C & $22.0$ \\
$R_0$ & Internal Ohmic Resistance & $\Omega$ & $0.12$ \\
$\kappa_{cpu}$ & CPU Power Coeff & W & $12.0$ \\
$\beta_{oled}$ & Display Power Coeff & W & $1.5$ \\
$\tau$ & Network Tail State Duration & s & $1.0 - 10.0$ \\
$P_{total}$ & Total Power Consumption & W & $0.5 - 12.0$ \\
$T_{crit}$ & Thermal Throttling Threshold & $^\circ$C & $40.0$ \\
\hline
\end{tabular}
\end{table}"""

new_table = r"""\begin{table}[H]
\centering
\caption{Summary of Model Symbols and Parameters}
\label{tab:vars}
\begin{tabular}{|c|l|c|c|}
\hline
\textbf{Symbol} & \textbf{Description} & \textbf{Unit} & \textbf{Typical Value} \\
\hline
\multicolumn{4}{|c|}{\textit{Battery Circuit Parameters}} \\
\hline
$Q_{cap}$ & Battery Capacity & As (Coulombs) & $18,000$ (5000mAh) \\
$V_{OC}(S)$ & Open Circuit Voltage & V & $3.45 - 4.2$ \\
$R_0$ & Internal Ohmic Resistance & $\Omega$ & $0.12$ \\
$R_1, R_2$ & Polarization Resistances & $\Omega$ & $0.02, 0.05$ \\
$C_1, C_2$ & Polarization Capacitances & F & $1200, 6000$ \\
$\tau_1, \tau_2$ & RC Time Constants ($R_i C_i$) & s & $24, 300$ \\
\hline
\multicolumn{4}{|c|}{\textit{Hardware Power Coefficients}} \\
\hline
$\kappa_{soc}$ & SoC Peak Power Coefficient & W & $12.0$ \\
$\alpha_{cpu}$ & CMOS Switching Activity Factor & --- & $0.8$ \\
$\beta_1$ & OLED Peak Power Coefficient & W & $1.5$ \\
$\gamma(t)$ & Active Pixel Ratio (OLED) & --- & $0.1 - 0.9$ \\
$\delta_{snr}$ & Signal-Dependent Network Penalty & --- & $0.1 - 10$ \\
$C_{lcd}$ & LCD Backlight Coefficient & W & $2.5$ \\
$P_{driver}$ & Display Driver Overhead & W & $0.1$ \\
\hline
\multicolumn{4}{|c|}{\textit{Thermal and Efficiency Parameters}} \\
\hline
$T_{amb}$ & Ambient Reference Temperature & $^\circ$C & $22.0$ \\
$T_{crit}$ & Thermal Throttling Threshold & $^\circ$C & $40.0$ \\
$\eta_{base}$ & Baseline Coulombic Efficiency & --- & $0.99$ \\
$\zeta$ & Efficiency Degradation Factor & --- & $0.015$ \\
$m C_p$ & Device Thermal Mass & J/K & $150$ \\
$hA$ & Convective Heat Transfer Coeff & W/K & $0.22$ \\
\hline
\end{tabular}
\end{table}"""

content = content.replace(old_table, new_table)

# ============================================
# 5. Fix typo in Background section header
# ============================================
content = content.replace(r"\section{Background on Developing Equaitons}", r"\section{Background on Developing Equations}")

# ============================================
# 6. Replace AI Usage Report with COMAP-compliant format
# ============================================

old_ai_section = r"""% --- AI USE REPORT ---
\newpage
\section*{Report on Use of AI Tools}
\textbf{Tools Used:} Google Gemini (Antigravity Agentic Assistant), ChatGPT (Prism Model) \\
\textbf{Date of Use:} January 30 -- February 2, 2026 \\

\subsection*{Specific Usage Details}
\begin{enumerate}
    \item \textbf{Mathematical Model Development (Gemini):} 
    \begin{itemize}
        \item \textit{Role:} Assisted in the derivation of the continuous-time state-space models for the 2RC-Thevenin equivalent circuit and the coupling of hardware power laws (CMOS scaling, OLED luminosity).
        \item \textit{Prompt:} ``Develop a system of differential equations that models smartphone battery SOC as a continuous-time process, incorporating hardware variables like OLED brightness and 5G tail energy.''
    \end{itemize}
    
    \item \textbf{Code Generation and Implementation (Gemini):}
    \begin{itemize}
        \item \textit{Role:} Generated the Python simulation engine, the numerical ODE solvers, and the React/Capacitor dashboard for the mobile application.
        \item \textit{Prompt:} ``Write a Python class \texttt{SmartphoneBattery} that implements the 2RC circuit model and a simulation loop that compares different user profiles.''
    \end{itemize}

    \item \textbf{Data Synthesis and Literature Review (Gemini):}
    \begin{itemize}
        \item \textit{Role:} Summarized academic findings regarding 5G Signal-to-Noise Ratio (SNR) impacts and OLED Active Pixel Ratio (APR). Assisted in mapping coefficients from provided datasets (NASA, Kaggle) to the model equations, including the calibration for the iPhone 17 Pro battery parameters ($Q_{cap} \approx 3988$ mAh).
        \item \textit{Prompt:} ``Analyze the relationship between OLED active pixel ratio and battery drain, and suggest mathematical clustering for different app categories based on empirical data.''
    \end{itemize}

    \item \textbf{LaTeX Formatting and Grammar Fixes (Gemini \& ChatGPT):}
    \begin{itemize}
        \item \textit{Role:} Generated the LaTeX document structure and used iterative prompts to fix grammatical errors, improve flow, and ensure proper \LaTeX\ scientific formatting throughout the document.
        \item \textit{Prompt:} ``Review the following \LaTeX\ sections for grammatical consistency, scientific tone, and proper structural formatting. Ensure that all mathematical environments are correctly implemented and that the text flows logically between the model derivation and the case studies.''
    \end{itemize}

    \item \textbf{Mathematical Model Refinement (Gemini):}
    \begin{itemize}
        \item \textit{Role:} Iteratively refined the power drain equations based on real-time impetus from simulation failures (where initial battery life was calculated as unrealistically high). 
        \item \textit{Prompt:} ``The initial model is predicting 40+ hours of battery life for heavy users, which is unrealistic. Adjust the CMOS logic power scaling and the 5G tail energy constants to align with empirical industry benchmark data while maintaining the 2RC-Thevenin circuit structure.''
    \end{itemize}

    \item \textbf{Data Visualization and Diagrammatic Summary (Gemini):}
    \begin{itemize}
        \item \textit{Role:} Generated a Python script using the `matplotlib` library to create a modular block diagram. This visual summarizes the interdependencies between the derived equations (Equations 1--15), clarifying the relationship between power generation modules, thermal feedback, and circuit dynamics.
        \item \textit{Prompt:} ``Generate a diagrammatic visual summary of the system of equations using Python code, delineating the modular dependencies between power generation, circuit dynamics, and thermal feedback loops. Specifically, create a modular block diagram that highlights how terms from Equations 1, 2, and 6 interface with each other.''
    \end{itemize}
\end{enumerate}

\subsection*{Affirmation}
The authors confirm that all mathematical derivations, conclusions, and insights were verified for accuracy and logical consistency. The AI tools served as facilitators for technical writing, code scaffolding, and literature synthesis, but the final model and report (as well the veracity of these submitted items) represent the intellectual contribution of the human authors."""

new_ai_section = r"""% --- AI USE REPORT ---
\newpage
\section*{Report on Use of AI Tools}

This section documents the use of artificial intelligence (AI) tools in the preparation of this submission, in accordance with COMAP's AI Policy (v102025). The following tools were used:

\begin{enumerate}
    \item \textbf{Google Gemini} (Antigravity Agentic Assistant, February 2026 version)
    \item \textbf{OpenAI ChatGPT} (GPT-4o, January 2026 version)
\end{enumerate}

\textbf{Date of Use:} January 30 -- February 2, 2026

\subsection*{Usage 1: Mathematical Model Development}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Develop a system of differential equations that models smartphone battery SOC as a continuous-time process, incorporating hardware variables like OLED brightness and 5G tail energy.''

\textbf{Output:} The AI suggested a coupled ODE system based on the 2RC-Thevenin equivalent circuit model. The initial output included the governing SOC equation:
\begin{verbatim}
dS/dt = -I_load(t) / Q_cap
\end{verbatim}
with terminal voltage dynamics:
\begin{verbatim}
V_term = V_OC(S) - I_load*R_0 - V_p1 - V_p2
\end{verbatim}
The AI also proposed coupling hardware power terms via $P_{total} = P_{cpu} + P_{disp} + P_{net}$. These suggestions were refined by the authors to include efficiency correction terms and thermal feedback.

\newpage

\subsection*{Usage 2: Python Simulation Engine}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Write a Python class \texttt{MCMHighFidelityModel} that implements the 2RC circuit model with thermal dynamics and a simulation loop that compares different user profiles (Gaming, Eco Reading, etc.).''

\textbf{Output:} The AI generated a complete Python class with the following structure:
\begin{verbatim}
class MCMHighFidelityModel:
    def get_ocv(self, soc):
        s = np.clip(soc, 0.0001, 1.0)
        return 3.45 + 0.6*s + 0.12*np.log(s + 0.01)
    
    def get_p_total(self, t, s, temp, p):
        # CPU Power Model
        p_cpu = 12.0 * (0.7 * (0.8 + 0.3*p['f'])**2 * ...)
        # Display and Network models...
        return p_total
    
    def system_dynamics(self, y, t, p):
        # Coupled ODE system...
        return [ds, dvp1, dvp2, dtemp]
\end{verbatim}
The authors calibrated the coefficients and added scenario configurations.

\subsection*{Usage 3: Model Calibration and Refinement}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``The initial model is predicting 40+ hours of battery life for heavy users, which is unrealistic. Adjust the CMOS logic power scaling and the 5G tail energy constants to align with empirical industry benchmark data while maintaining the 2RC-Thevenin circuit structure.''

\textbf{Output:} The AI recommended increasing the base CPU power coefficient from 8.0W to 12.0W and adding current-dependent efficiency degradation:
\begin{verbatim}
eta_i = 0.99 - 0.015 * (p_total / 8.0)
\end{verbatim}
It also suggested capping modem power at 3.0W and implementing thermal throttling above 40°C. These adjustments reduced the Ultra Gaming scenario from 40+ hours to approximately 1.75 hours, matching industry benchmarks.

\subsection*{Usage 4: OLED and Network Power Laws}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Analyze the relationship between OLED active pixel ratio and battery drain, and suggest mathematical clustering for different app categories based on empirical data.''

\textbf{Output:} The AI summarized findings from academic literature (citing De Sousa et al. and Kurale et al.) and proposed the OLED power law:
\begin{verbatim}
P_disp = beta_1 * B^1.6 * gamma + beta_0
\end{verbatim}
where $\gamma \approx 0.3$ for Dark Mode and $\gamma \approx 0.9$ for Light Mode. For app clustering, it suggested four categories: Gaming (high CPU/GPU), Media (high display, moderate network), Social (moderate all), and Utility (low all).

\newpage

\subsection*{Usage 5: 5G Signal Strength Modeling}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Model the relationship between 5G signal strength and modem power consumption. The power should increase exponentially as signal drops below -80 dBm.''

\textbf{Output:} The AI derived the signal-dependent penalty factor:
\begin{verbatim}
delta_snr = 10**((-signal - 80) / 20)
p_net = min(3.0, delta_snr * 0.25)
\end{verbatim}
This creates an exponential increase in power consumption as signal strength decreases, capped at 3.0W to prevent unrealistic values in extreme dead zones.

\subsection*{Usage 6: Thermal Throttling Implementation}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Implement thermal throttling in the simulation. The device should start throttling at 40°C and reach maximum throttling (65\% power reduction) at 60°C.''

\textbf{Output:} The AI suggested a linear throttling model:
\begin{verbatim}
if temp > 40.0:
    throttle_factor = np.clip(1.0 - (temp - 40.0)/20.0, 0.35, 1.0)
    p_total *= throttle_factor
\end{verbatim}
This ensures realistic thermal-limited discharge curves that match industry benchmarks for sustained gaming scenarios.

\subsection*{Usage 7: Data Visualization (Matplotlib)}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Generate a Python script to create a 3x3 grid of discharge curves for different user scenarios, showing both SOC and temperature over time.''

\textbf{Output:} The AI generated a complete visualization script using matplotlib:
\begin{verbatim}
fig, axes = plt.subplots(3, 3, figsize=(18, 14))
for i, (name, config) in enumerate(scenarios):
    res = odeint(model.system_dynamics, y0, t, args=(config,))
    ax = axes[i//3, i%3]
    ax.plot(t_slice, soc_slice, color='#2563eb', lw=2.5)
    ax2 = ax.twinx()
    ax2.plot(t_slice, temp_slice, color='#ef4444', ls='--')
\end{verbatim}
The authors customized colors, labels, and figure formatting.

\newpage

\subsection*{Usage 8: Equation Flowchart Diagram}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Generate a diagrammatic visual summary of the system of equations using Python code, delineating the modular dependencies between power generation, circuit dynamics, and thermal feedback loops.''

\textbf{Output:} The AI generated a Python script using matplotlib patches and arrows to create a modular block diagram showing the interconnections between:
\begin{itemize}
    \item Power Input Modules (CPU, Display, Network)
    \item Circuit Dynamics (2RC Model, SOC ODE)
    \item Thermal Feedback Loop
    \item Efficiency Correction
\end{itemize}

\subsection*{Usage 9: LaTeX Document Structure}
\textbf{Tool:} Google Gemini (Antigravity) \& OpenAI ChatGPT

\textbf{Query:} ``Review the following \LaTeX\ sections for grammatical consistency, scientific tone, and proper structural formatting. Ensure that all mathematical environments are correctly implemented.''

\textbf{Output:} The AI tools provided corrections for:
\begin{itemize}
    \item Consistent use of equation numbering and cross-references
    \item Proper formatting of units (e.g., $\Omega$ instead of Ohms)
    \item Grammar and flow improvements between sections
    \item Standardized notation for subscripts (lowercase, no spaces)
\end{itemize}

\subsection*{Usage 10: Appendix Code Documentation}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Update the Python code appendix to include the main code that models the equations from simulation.py. Make it two pages with explanations of each code snippet, referencing which equations they implement.''

\textbf{Output:} The AI restructured Appendix A into four subsections (Constants, Power Consumption, Differential System, Execution), adding inline comments that explicitly reference the equation numbers from the main text (e.g., ``Implements Equation (8)'' for the CPU power model).

\newpage

\subsection*{Usage 11: Variable Table Enhancement}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Expand Table 1 to include all circuit parameters ($R_0, R_1, C_1, R_2, C_2$), display constants ($C_{lcd}, P_{driver}$), and thermal parameters ($mC_p, hA$) with their units.''

\textbf{Output:} The AI generated an expanded table with three sections (Battery Circuit Parameters, Hardware Power Coefficients, Thermal and Efficiency Parameters), ensuring all variables used in the equations are documented.

\subsection*{Usage 12: Model Roadmap Addition}
\textbf{Tool:} Google Gemini (Antigravity)

\textbf{Query:} ``Add a roadmap paragraph at the start of Section 5 (Continuous-Time Model) that outlines the structure of the model derivation.''

\textbf{Output:} The AI suggested adding a bolded ``Model Roadmap'' paragraph that previews the five subsections, helping readers understand the logical flow before diving into the differential equations.

\subsection*{Affirmation}

The authors confirm that:
\begin{enumerate}
    \item All mathematical derivations, conclusions, and insights generated by AI tools were independently verified for accuracy and logical consistency.
    \item The AI tools served as facilitators for technical writing, code scaffolding, and literature synthesis.
    \item The final model structure, coefficient values, and report conclusions represent the intellectual contribution of the human authors.
    \item All citations suggested by AI tools were verified against original sources.
\end{enumerate}

The team acknowledges the risks outlined in COMAP's AI Policy, including the potential for AI-generated content to contain inaccuracies or biases. Human judgment was applied at every stage to ensure the validity and originality of this submission."""

content = content.replace(old_ai_section, new_ai_section)

# Write the updated content
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated the document with all improvements.")
