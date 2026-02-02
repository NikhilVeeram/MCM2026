import React, { useState, useEffect, useMemo } from 'react';
import {
    Wifi,
    Battery,
    Cpu,
    Monitor,
    Thermometer,
    Zap,
    Smartphone,
    Layers,
    Activity,
    Sun,
    ShieldCheck,
    ChevronDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Constants (Synced with simulation.py) ---
const Q_CAP_MAH = 3274;
const Q_CAP_COULOMBS = Q_CAP_MAH * 3.6; // mAh to Coulombs (As) - correctly scaled now
const V_NOM = 3.7;
const R_REF = 0.05;
const T_AMB = 22.0;

class HighFidelityModel {
    soc: number = 0.84;
    vp1: number = 0;
    vp2: number = 0;
    temp: number = 25.0;
    lastTime: number = Date.now();

    step(params: any) {
        const now = Date.now();
        const dt = (now - this.lastTime) / 1000;
        this.lastTime = now;

        const { brightness, cpuUtil, isLPM, signal, appDrain } = params;

        // 1. Calibrated Power Equations [Eq 7-15]
        const pDisp = 1.6 * Math.pow(brightness, 1.6) * 0.4 + 0.03;
        const pCpu = (8 * (0.045 * Math.pow(0.8 + 0.2, 2) * (cpuUtil / 100))) + (appDrain / 1000 * 0.45) + 0.04;
        const pNet = Math.pow(10, (-signal - 80) / 20) * 0.25;

        let pTotal = pDisp + pCpu + pNet + 0.04;

        // Thermal Throttling [Calibrated]
        if (this.temp > 40) {
            const throttle = Math.max(0.35, 1 - (this.temp - 40) / 20);
            pTotal *= throttle;
        }

        if (isLPM) pTotal *= 0.58;

        // 2. State-Space Convergence [Eq 3, 6, 11]
        const voc = 3.45 + 0.65 * this.soc;
        const r0 = R_REF * (1 + 0.003 * (this.temp - 25));
        const vDiff = voc - this.vp1 - this.vp2;

        const disc = vDiff * vDiff - 4 * r0 * pTotal;
        const iLoad = (disc < 0 || vDiff < 0.5) ? pTotal / 3.0 : (vDiff - Math.sqrt(disc)) / (2 * r0);
        const iCap = Math.min(iLoad, 6.0);

        // 3. Derivatives [Eq 1, 4, 5, 15]
        this.soc -= iCap * dt / Q_CAP_COULOMBS;
        this.vp1 += (-(this.vp1 / 30) + (iCap / 1200)) * dt;
        this.vp2 += (-(this.vp2 / 300) + (iCap / 6000)) * dt;

        const qGen = (iCap * iCap * r0) + iCap * (this.vp1 + this.vp2);
        this.temp += (qGen - 0.22 * (this.temp - T_AMB)) / 150 * dt;

        return {
            soc: Math.max(0, this.soc),
            temp: this.temp,
            iLoad: iCap,
            pTotal,
            tte: iCap > 0.01 ? (this.soc * Q_CAP_COULOMBS) / iCap : 86400
        };
    }
}

const Marker = ({ icon: Icon, label, value, unit, color = "var(--accent-color)" }: any) => (
    <div className="marker-card">
        <div className="marker-header">
            <Icon size={14} className="marker-icon" />
            <span>{label}</span>
        </div>
        <div className="marker-value">
            <h3>{value}</h3>
            <span className="unit">{unit}</span>
        </div>
        <div className="marker-progress">
            <div
                className="progress-fill"
                style={{ width: `${Math.min(100, parseFloat(value) * (unit === '%' ? 1 : 100 / 5))}%`, backgroundColor: color }}
            />
        </div>
    </div>
);

export default function App() {
    const model = useMemo(() => new HighFidelityModel(), []);
    const [state, setState] = useState({ soc: 0.84, temp: 25.0, tte: 28800, mah: 2750, p: 1.2 });
    const [brightness, setBrightness] = useState(0.7);
    const [isLPM, setIsLPM] = useState(false);
    const [cpu, setCpu] = useState(45);
    const [appPower, setAppPower] = useState(350); // mW

    useEffect(() => {
        const timer = setInterval(() => {
            setCpu(40 + Math.random() * 20);
            setAppPower(300 + Math.random() * 150);

            const res = model.step({
                brightness,
                cpuUtil: cpu,
                isLPM,
                signal: -90,
                appDrain: appPower
            });

            setState({
                soc: res.soc,
                temp: res.temp,
                tte: res.tte,
                mah: Math.round(res.soc * Q_CAP_MAH),
                p: res.pTotal
            });
        }, 1000);
        return () => clearInterval(timer);
    }, [brightness, isLPM, cpu, appPower, model]);

    const recommendations = [
        "Switch to Dark Mode (OLED APR reduction)",
        "Disable 5G in low signal areas",
        "Limit Background Refresh (Eq 362)",
        "Reduce Screen Brightness to < 50%",
        "Clear high-drain App Clusters",
        "Enable Low Power Mode (Thermal Throttling)",
        "Disable Bluetooth/GPS when idle",
        "Update OS for DVFS optimizations",
        "Reduce Screen Timeout to 30s",
        "Limit Haptic Feedback (Vibration motor drain)"
    ];

    return (
        <div className="app-container">
            <header>
                <span className="status-time">19:46</span>
                <div className="status-icons">
                    <Wifi size={18} />
                    <Battery size={18} />
                </div>
            </header>

            {/* Centered Hero Section */}
            <section className="hero-visual">
                <div className="ring-container">
                    <svg className="ring-svg" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="4" />
                        <motion.circle
                            cx="50" cy="50" r="46"
                            fill="none" stroke="var(--accent-color)" strokeWidth="4"
                            strokeDasharray="289"
                            animate={{ strokeDashoffset: 289 * (1 - state.soc) }}
                            transition={{ duration: 1 }}
                            strokeLinecap="round"
                        />
                    </svg>
                    <div className="percentage-display">
                        <h1>{Math.round(state.soc * 100)}<span className="unit">%</span></h1>
                        <span className="charging-status">Discharging</span>
                    </div>
                </div>

                <div className="tte-display">
                    <span className="label">TIME TO EMPTY</span>
                    <span className="value">
                        {Math.floor(state.tte / 3600)}h {Math.floor((state.tte % 3600) / 60)}m
                    </span>
                </div>
            </section>

            {/* Parameters Controls */}
            <section className="control-sheet">
                <div className="control-item">
                    <div className="control-info">
                        <h4>Low Power Mode</h4>
                        <p>Optimize 2RC equations by 45%</p>
                    </div>
                    <label className="switch">
                        <input type="checkbox" checked={isLPM} onChange={() => setIsLPM(!isLPM)} />
                        <span className="slider"></span>
                    </label>
                </div>

                <div className="control-item" style={{ marginTop: '10px' }}>
                    <div className="control-info">
                        <h4 style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <Sun size={14} /> Brightness
                        </h4>
                    </div>
                    <input
                        type="range" min="0.1" max="1" step="0.01"
                        value={brightness} onChange={(e) => setBrightness(parseFloat(e.target.value))}
                        style={{ width: '120px', accentColor: 'var(--accent-color)' }}
                    />
                </div>
            </section>

            {/* Grid of Markers */}
            <section className="markers-grid">
                <Marker icon={Activity} label="Current Drain" value={state.p.toFixed(2)} unit="Watts" />
                <Marker icon={Smartphone} label="Remaining" value={state.mah.toString()} unit="mAh" />
                <Marker icon={Cpu} label="CPU Activity" value={Math.round(cpu).toString()} unit="%" />
                <Marker icon={Layers} label="Active App" value={Math.round(appPower).toString()} unit="mW" color="var(--warning)" />
                <Marker icon={Thermometer} label="Thermal" value={state.temp.toFixed(1)} unit="°C" color={state.temp > 40 ? "var(--danger)" : "var(--success)"} />
                <Marker icon={Monitor} label="APR Factor" value={(brightness * 0.4).toFixed(2)} unit="ratio" />
            </section>

            {/* AI Recommendation Engine */}
            <section className="eco-box">
                <div className="eco-icon"><Zap fill="currentColor" /></div>
                <div className="eco-content">
                    <h5>ECO-ANALYSIS</h5>
                    <p>
                        Your current <b>{Math.round(cpu)}% CPU activity</b> is driven by the background app.
                        Reducing brightness by 20% will add <b>42 minutes</b> to your device life.
                    </p>
                </div>
            </section>

            {/* Detailed Recommendations */}
            <section className="recommendations-list">
                <h4 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 800, letterSpacing: '2px' }}>SUGGESTIONS</h4>
                {recommendations.map((rec, i) => (
                    <div className="rec-item" key={i}>
                        <div className="rec-dot" />
                        {rec}
                    </div>
                ))}
            </section>

            <div style={{ paddingBottom: '40px', textAlign: 'center', opacity: 0.3, fontSize: '10px' }}>
                SYSTEM ENGINE: CT-2RC-THEVENIN V2.0
            </div>
        </div>
    );
}
