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
    Moon,
    Info,
    Gamepad2,
    Globe,
    Youtube,
    BookOpen,
    X,
    ShieldCheck,
    Instagram,
    MessageSquare,
    Music,
    Trash2,
    Apple
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/** 
 * ECODRAIN IOS EDITION 
 * Calibrated for iPhone / A-Series Dynamics
 */

const Q_CAP_MAH = 3274;
const Q_CAP_COULOMBS = Q_CAP_MAH * 3.6;
const V_NOM = 3.82; // iOS specific voltage calibration
const R_REF = 0.10;
const T_AMB = 22.0;

class IOSHardwareEngine {
    soc: number = 0.83;
    vp1: number = 0;
    vp2: number = 0;
    temp: number = 24.5;
    lastTime: number = Date.now();

    step(params: any) {
        const now = Date.now();
        const dt = (now - this.lastTime) / 1000;
        this.lastTime = now;

        const { brightness, cpuUtil, isLPM, signal, appDrain, apr } = params;

        // 1. IOS SYSTEM CALIBRATION [A-Series Efficiency]
        // Calibrated for 7h active idle (Screen on, low CPU, Min Brightness)
        const pCpu = (7.0 * (Math.pow(cpuUtil / 100, 3.0))) + (appDrain / 1000 * 0.45) + 0.35;

        // Display: EXTREME scaling (Max ~4.8W for ProMotion brightness)
        const pDisp = 4.8 * Math.pow(brightness, 2.0) * apr + 0.1;

        // C1 Modem Calibration (iOS radio stack)
        const delta = Math.pow(10, (-signal - 80) / 28);
        const pNet = Math.min(3.0, 0.2 + delta * 2.5);

        let pTotal = pCpu + pDisp + pNet + 0.05;
        if (isLPM) pTotal *= 0.58; // iOS Low Power Mode is quite aggressive

        // 2. STATE DYNAMICS
        const voc = 3.48 + 0.72 * this.soc;
        const r0 = R_REF * (1 + 0.003 * (this.temp - 25));
        const vDiff = voc - this.vp1 - this.vp2;

        const disc = vDiff * vDiff - 4 * r0 * pTotal;
        const iLoad = (disc < 0 || vDiff < 0.5) ? pTotal / 3.2 : (vDiff - Math.sqrt(disc)) / (2 * r0);
        const iCap = Math.min(iLoad, 8.5);

        // 3. IOS THERMAL COUPLING
        const qGen = (iCap * iCap * r0 * 4.5) + (pDisp * 2.8) + iCap * (this.vp1 + this.vp2) * 3.5;
        const qLost = 0.20 * (this.temp - T_AMB);
        this.temp += (qGen - qLost) / 12 * dt;

        this.soc -= iCap * dt / Q_CAP_COULOMBS;
        this.vp1 += (-(this.vp1 / 30) + (iCap / 1200)) * dt;
        this.vp2 += (-(this.vp2 / 300) + (iCap / 6000)) * dt;

        return {
            soc: Math.max(0, this.soc),
            temp: this.temp,
            pTotal, pDisp, pCpu, pNet, iLoad: iCap,
            tte: iCap > 0.01 ? (this.soc * Q_CAP_COULOMBS) / iCap : 86400
        };
    }
}

const CoreChip = ({ name, freq, power, color }: any) => (
    <div className="core-chip" style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.1)' }}>
        <span className="name" style={{ fontSize: '10px', fontWeight: 600 }}>{name}</span>
        <span className="freq" style={{ color, fontSize: '14px', fontWeight: 700 }}>{freq}GHz</span>
        <span className="power" style={{ fontSize: '10px', opacity: 0.6 }}>{power}W</span>
    </div>
);

export default function App() {
    const model = useMemo(() => new IOSHardwareEngine(), []);
    const [state, setState] = useState({ soc: 0.83, temp: 24.5, tte: 28800, mah: 2750, p: 0.8, pCpu: 0.3, pDisp: 0.2, pNet: 0.2 });
    const [isDarkMode, setIsDarkMode] = useState(true);
    const [isLPM, setIsLPM] = useState(false);
    const [brightness, setBrightness] = useState(0.5);
    const [isFYIOpen, setIsFYIOpen] = useState(false);
    const [activeScenario, setActiveScenario] = useState<string | null>(null);
    const [timer, setTimer] = useState(0);

    const [apps, setApps] = useState([
        { id: 'ecodrain', name: 'EcoDrain', icon: Smartphone, wattage: 0.07, impact: 'active', color: '#007AFF' },
        { id: 'youtube', name: 'YouTube', icon: Youtube, wattage: 0.38, impact: 'high', color: '#FF0000' },
        { id: 'instagram', name: 'Instagram', icon: Instagram, wattage: 0.32, impact: 'high', color: '#E4405F' },
        { id: 'music', name: 'Music', icon: Music, wattage: 0.12, impact: 'medium', color: '#FA2D48' },
    ]);

    useEffect(() => {
        const interval = setInterval(() => {
            let params = {
                brightness,
                cpuUtil: 12 + Math.random() * 8,
                isLPM,
                signal: -82,
                appDrain: apps.reduce((acc, curr) => acc + curr.wattage * 1000, 0) / 2.2,
                apr: isDarkMode ? 0.28 : 0.92
            };

            if (activeScenario && timer > 0) {
                params = { ...params, brightness: 1.0, cpuUtil: 95, signal: -110, appDrain: 2200 };
                setTimer(t => t - 1);
            } else if (timer === 0) {
                setActiveScenario(null);
            }

            const res = model.step(params);
            setState({ ...res, mah: Math.round(res.soc * Q_CAP_MAH), p: res.pTotal });
        }, 1000);
        return () => clearInterval(interval);
    }, [brightness, isLPM, isDarkMode, activeScenario, timer, model, apps]);

    return (
        <div className="app-container" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif' }}>
            <header style={{ padding: '10px 0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Apple size={22} color={isDarkMode ? '#fff' : '#000'} />
                    <span style={{ fontWeight: 700, fontSize: '17px' }}>Battery Health</span>
                </div>
                <button onClick={() => setIsFYIOpen(true)} style={{ background: 'none', border: 'none', color: '#007AFF', cursor: 'pointer' }}>
                    <Info size={22} />
                </button>
            </header>

            <section className="hero-visual" style={{ padding: '0' }}>
                <div className="ring-container" style={{ width: '220px', height: '220px' }}>
                    <svg className="ring-svg" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(128,128,128,0.1)" strokeWidth="5" />
                        <motion.circle
                            cx="50" cy="50" r="46"
                            fill="none" stroke={state.soc < 0.2 ? '#FF3B30' : '#34C759'} strokeWidth="5"
                            strokeDasharray="289" animate={{ strokeDashoffset: 289 * (1 - state.soc) }}
                            strokeLinecap="round"
                        />
                    </svg>
                    <div className="percentage-display">
                        <h1 style={{ fontSize: '56px', fontWeight: 600 }}>{Math.round(state.soc * 100)}%</h1>
                        <div style={{ fontSize: '11px', color: '#8E8E93', letterSpacing: '0.5px' }}>
                            {activeScenario ? `CALIBRATING LOAD: ${timer}s` : 'DISCHARGING'}
                        </div>
                    </div>
                </div>
                <div className="tte-display" style={{ marginTop: '10px' }}>
                    <div style={{ fontSize: '28px', fontWeight: 500 }}>{Math.floor(state.tte / 3600)}h {Math.floor((state.tte % 3600) / 60)}m Remaining</div>
                </div>
            </section>

            <section className="control-sheet" style={{ borderRadius: '20px', padding: '16px' }}>
                <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                    <button className={`scenario-btn ${isLPM ? 'active' : ''}`} style={{ flex: 1, flexDirection: 'row', borderRadius: '12px', background: isLPM ? '#FFD60A' : 'rgba(128,128,128,0.1)', color: isLPM ? '#000' : 'inherit' }} onClick={() => setIsLPM(!isLPM)}>
                        <Zap size={16} fill={isLPM ? '#000' : 'none'} /> <span>Low Power Mode</span>
                    </button>
                    <button className="scenario-btn" style={{ flex: 1, flexDirection: 'row', borderRadius: '12px', background: 'rgba(128,128,128,0.1)' }} onClick={() => setIsDarkMode(!isDarkMode)}>
                        {isDarkMode ? <Moon size={16} /> : <Sun size={16} />} <span>{isDarkMode ? 'Night' : 'Day'} Mode</span>
                    </button>
                </div>

                <div className="scenario-grid">
                    {['Gaming', 'Network', 'Social'].map(s => (
                        <button key={s} className={`scenario-btn ${activeScenario === s ? 'active' : ''}`} style={{ borderRadius: '14px', background: activeScenario === s ? '#007AFF' : 'rgba(128,128,128,0.05)' }} onClick={() => { setActiveScenario(s); setTimer(10); }}>
                            {s === 'Gaming' ? <Gamepad2 size={20} /> : s === 'Network' ? <Globe size={20} /> : <Youtube size={20} />}
                            <span>{s}</span>
                        </button>
                    ))}
                </div>
            </section>

            <div className="markers-grid">
                <div className="marker-card" style={{ borderRadius: '18px' }}>
                    <div className="marker-header"><Thermometer size={14} /> <span>Thermal Engine</span></div>
                    <div className="marker-value"><h3>{state.temp.toFixed(1)}°</h3></div>
                    <div className="marker-progress"><div className="progress-fill" style={{ width: `${Math.min(100, (state.temp - 22) * 4)}%`, background: state.temp > 38 ? '#FF3B30' : '#34C759' }} /></div>
                </div>
                <div className="marker-card" style={{ borderRadius: '18px' }}>
                    <div className="marker-header"><Activity size={14} /> <span>Live Output</span></div>
                    <div className="marker-value"><h3>{state.p.toFixed(2)}W</h3></div>
                    <div className="marker-progress"><div className="progress-fill" style={{ width: `${Math.min(100, state.p * 15)}%`, background: '#007AFF' }} /></div>
                </div>

                <div className="marker-card full-width" style={{ borderRadius: '18px' }}>
                    <div className="marker-header"><Cpu size={14} /> <span>A-Series Architecture</span></div>
                    <div className="core-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                        <CoreChip name="Firestorm (P)" freq={activeScenario ? '3.45' : '0.82'} power={(state.pCpu * 0.4).toFixed(2)} color="#FF3B30" />
                        <CoreChip name="Icestorm (E)" freq={(0.4 + Math.random() * 2.1).toFixed(2)} power={(state.pCpu * 0.1).toFixed(2)} color="#34C759" />
                    </div>
                </div>

                <div className="marker-card full-width" style={{ borderRadius: '18px' }}>
                    <div className="marker-header"><Activity size={14} /> <span>App Energy Usage</span></div>
                    <div className="app-impact-list">
                        {apps.map((app) => (
                            <div className="impact-item" key={app.id} style={{ borderRadius: '12px', padding: '12px' }}>
                                <div className="impact-app-info">
                                    <app.icon size={16} color={app.color} />
                                    <span className="impact-name">{app.name}</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <span className="impact-wattage" style={{ color: '#8E8E93' }}>{app.wattage.toFixed(2)}W</span>
                                    {app.id !== 'ecodrain' && <Trash2 size={14} color="#FF3B30" style={{ cursor: 'pointer' }} onClick={() => setApps(prev => prev.filter(a => a.id !== app.id))} />}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="android-notification" style={{ borderRadius: '14px', background: 'rgba(0,0,0,0.8)', border: 'none' }}>
                <ShieldCheck size={20} color="#34C759" />
                <div style={{ flex: 1 }}>
                    <h6 style={{ fontSize: '11px', color: '#fff', fontWeight: 600 }}>IOS SYSTEM GUARD</h6>
                    <div style={{ fontSize: '12px', color: '#8E8E93' }}>{state.p.toFixed(2)}W Sink | {Math.round(state.soc * 100)}% SOC</div>
                </div>
            </div>
        </div>
    );
}
