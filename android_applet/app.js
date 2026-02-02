/**
 * EcoDrain Dashboard Logic
 * Implements the Continuous-Time mathematical model from the MCM 2026 Report
 */

// Model Constants
const Q_CAP_MAX = 3274 * 3600; // Coulombs
const R_INTERNAL = 0.0233;
const TAU_TAIL = 1.5;

class EcoDrainModel {
    constructor() {
        this.soc = 0.84; // Initial SOC
        this.v_p1 = 0.0;
        this.v_p2 = 0.0;

        // 2RC Params
        this.r1 = 0.015; this.c1 = 2000;
        this.r2 = 0.030; this.c2 = 10000;

        this.lastUpdateTime = Date.now();
        this.isLPM = false;

        // Simulation State
        this.cpu_load = 42;
        this.screen_ratio = 0.32;
        this.signal_strength = -92;
        this.temp = 34;
    }

    get_ocv(soc) {
        const s = Math.max(soc, 0.01);
        return 3.0 + 1.0 * s + 0.2 * Math.log(s + 0.01);
    }

    calculate_power() {
        // P_disp = 1.8 * Brightness(1.0) * ScreenRatio
        const p_disp = 1.8 * 1.0 * this.screen_ratio;
        // P_cpu = 3.5 * Util
        const p_cpu = 3.5 * (this.cpu_load / 100);
        // P_net scaling (exponential with signal)
        const signal_factor = Math.pow(10, (-this.signal_strength - 80) / 20);
        const p_net = 0.5 * Math.min(signal_factor, 2.0);

        let total = p_disp + p_cpu + p_net + 0.1;

        if (this.isLPM) total *= 0.65;
        return total;
    }

    step() {
        const now = Date.now();
        const dt = (now - this.lastUpdateTime) / 1000; // seconds
        this.lastUpdateTime = now;

        const p_total = this.calculate_power();
        const voc = this.get_ocv(this.soc);

        // Terminal Voltage Calculation (approximate)
        const v_term = voc - 0.05; // Simplified for UI update loop
        const i_load = p_total / v_term;

        // Update State
        this.soc -= (i_load * dt) / Q_CAP_MAX;

        // Polarization (simplified Euler)
        this.v_p1 += (-(this.v_p1 / (this.r1 * this.c1)) + (i_load / this.c1)) * dt;
        this.v_p2 += (-(this.v_p2 / (this.r2 * this.c2)) + (i_load / this.c2)) * dt;

        return {
            soc: this.soc,
            tte: (this.soc * Q_CAP_MAX) / i_load,
            power: p_total
        };
    }
}

const model = new EcoDrainModel();

// UI Elements
const socText = document.getElementById('soc-value');
const socRing = document.getElementById('soc-ring');
const tteText = document.getElementById('tte-value');
const cpuText = document.getElementById('cpu-load');
const screenText = document.getElementById('screen-ratio');
const signalText = document.getElementById('signal-strength');
const tempText = document.getElementById('temp-value');
const lpmCheckbox = document.getElementById('lpm-checkbox');
const recText = document.getElementById('recommendation');

// Update UI Loop
function updateUI() {
    // 1. Simulate Fluctuation in Markers
    model.cpu_load = 30 + Math.random() * 20;
    model.signal_strength = -90 - Math.random() * 10;

    // 2. Step Model
    const state = model.step();

    // 3. Update DOM
    socText.innerText = Math.round(state.soc * 100);

    // Ring Offset (Circumference = 282.7)
    const offset = 282.7 * (1 - state.soc);
    socRing.style.strokeDashoffset = offset;

    // TTE Formatting
    const tteHours = Math.floor(state.tte / 3600);
    const tteMins = Math.floor((state.tte % 3600) / 60);
    tteText.innerText = `${tteHours}h ${tteMins}m`;

    cpuText.innerText = Math.round(model.cpu_load);
    screenText.innerText = model.screen_ratio.toFixed(2);
    signalText.innerText = Math.round(model.signal_strength);
    tempText.innerText = (model.temp + Math.random() * 0.5).toFixed(1);

    // Update Tip based on state
    if (model.isLPM) {
        recText.innerHTML = "LPM Active. Saving approximately <span class='highlight'>35%</span> energy per hour.";
    } else {
        recText.innerHTML = "Switching to Dark Mode could extend your battery by <span class='highlight'>84 minutes</span>.";
    }
}

lpmCheckbox.addEventListener('change', (e) => {
    model.isLPM = e.target.checked;
});

// Run UI updates at 1Hz
setInterval(updateUI, 1000);
updateUI();

// Set system time
function updateClock() {
    const now = new Date();
    document.getElementById('time').innerText = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
}
setInterval(updateClock, 10000);
updateClock();
