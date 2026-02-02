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
    Grid
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Calibration Constants ---
const Q_CAP_MAH = 5000; // Standard 5000mAh Battery
const Q_CAP_COULOMBS = Q_CAP_MAH * 3.6;
const V_NOM = 3.8;
const R_REF = 0.12;
const T_AMB = 22.0;

// Profile Interface
type UserProfile = 'Eco 2x' | 'Eco 1.5x' | 'Eco 1x' | 'Baseline' | 'Power 1x' | 'Power 1.5x' | 'Power 2x';

const PROFILE_CONFIGS: Record<UserProfile, { scale: number, label: string, color: string }> = {
    'Eco 2x': { scale: 0.5, label: 'Extreme Eco', color: '#10b981' },
    'Eco 1.5x': { scale: 0.65, label: 'High Eco', color: '#34d399' },
    'Eco 1x': { scale: 0.8, label: 'Eco', color: '#6ee7b7' },
    'Baseline': { scale: 1.0, label: 'Balanced', color: '#94a3b8' },
    'Power 1x': { scale: 1.25, label: 'Performance', color: '#f472b6' },
    'Power 1.5x': { scale: 1.5, label: 'High Perf', color: '#ec4899' },
    'Power 2x': { scale: 2.0, label: 'Ultra Max', color: '#db2777' }
};

class HardwarePhysicsEngine {
    soc: number = 0.95;
    vp1: number = 0;
    vp2: number = 0;
    temp: number = 25.0;
    lastTime: number = Date.now();

    step(params: any) {
        const now = Date.now();
        const dt = (now - this.lastTime) / 1000;
        this.lastTime = now;

        const { brightness, cpuUtil, isLPM, signal, appDrain, apr, profileScale, isNetworkStress } = params;

        // 1. RECALIBRATED SUBSYSTEM EQUATIONS [Eq 7-12]

        // Processor: RE-TUNED FOR 12W PEAK (Gaming)
        // Base is ~12W when cpuUtil=100 and appDrain is high
        // Adjusted coef to 0.8 to compensate for typical radio capping
        const pCpuBase = (12.0 * (0.8 * Math.pow(cpuUtil / 100, 3.0))) + (appDrain / 1000 * 0.6) + 0.4;
        const pCpu = pCpuBase * profileScale;

        // Display: Scaled by profile (Screen brightness preference)
        const pDisp = (1.5 * Math.pow(brightness, 1.8) * apr + 0.1) * profileScale;

        // Modem: Floor 0.2W.
        // Capped at 1.0W UNLESS in specific "Network Stress" scenario
        const delta = Math.pow(10, (-signal - 80) / 25);
        const rawNet = 0.2 + delta * 2.5;
        const netCap = isNetworkStress ? 3.0 : 1.0;
        const pNet = Math.min(netCap, rawNet) * profileScale;

        let pTotal = pCpu + pDisp + pNet + 0.1 + (Math.random() * 0.05);
        if (isLPM) pTotal *= 0.6;

        // 2. STATE DYNAMICS
        const voc = 3.45 + 0.75 * this.soc;
        const r0 = R_REF * (1 + 0.003 * (this.temp - 25));
        const vDiff = voc - this.vp1 - this.vp2;

        const disc = vDiff * vDiff - 4 * r0 * pTotal;
        const iLoad = (disc < 0 || vDiff < 0.5) ? pTotal / 3.0 : (vDiff - Math.sqrt(disc)) / (2 * r0);
        const iCap = Math.min(iLoad, 8.0);

        // 3. THERMAL ACCELERATION 
        const qGen = (iCap * iCap * r0 * 4.0) + (pDisp * 2.5) + iCap * (this.vp1 + this.vp2) * 3.0;
        const qLost = 0.18 * (this.temp - T_AMB);
        this.temp += (qGen - qLost) / 10 * dt;

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
    <div className="core-chip">
        <span className="name">{name}</span>
        <span className="freq" style={{ color }}>{freq}GHz</span>
        <span className="power">{power}W</span>
    </div>
);

const FYIModal = ({ isOpen, onClose }: any) => (
    <AnimatePresence>
        {isOpen && (
            <div className="fyi-overlay">
                <motion.div initial={{ y: 50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="fyi-content">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                        <h2>Architecture Guide</h2>
                        <X onClick={onClose} style={{ cursor: 'pointer' }} />
                    </div>
                    <div className="eq-box">
                        <code>P_cpu = 12W * (U/100)³ * ProfileScale</code>
                        <p>12W peak power scaling for Power Users.</p>
                    </div>
                    <div className="eq-box">
                        <code>P_net = (Wifi ? 0.8 : 3.0) * Load</code>
                        <p>Dynamic radio capping. 5G uses 4x more power than Wi-Fi.</p>
                    </div>
                </motion.div>
            </div>
        )}
    </AnimatePresence>
);

export default function App() {
    const model = useMemo(() => new HardwarePhysicsEngine(), []);
    const [state, setState] = useState({ soc: 0.95, temp: 25.0, tte: 28800, mah: 4800, p: 1.2, pCpu: 0.4, pDisp: 0.3, pNet: 0.5 });
    const [isDarkMode, setIsDarkMode] = useState(true);
    const [isLPM, setIsLPM] = useState(false);
    const [isWifi, setIsWifi] = useState(false); // Default to 5G
    const [brightness, setBrightness] = useState(0.6);
    const [isFYIOpen, setIsFYIOpen] = useState(false);
    const [userProfile, setUserProfile] = useState<UserProfile>('Baseline');
    const [isWidgetView, setIsWidgetView] = useState(false);

    const [activeScenario, setActiveScenario] = useState<string | null>(null);
    const [timer, setTimer] = useState(0);

    const [apps, setApps] = useState<any[]>([]);

    // Update Apps based on Profile
    useEffect(() => {
        const baseApps = [
            { id: 'whatsapp', name: 'WhatsApp', icon: MessageSquare, wattage: 0.05, impact: 'low', color: '#25d366' },
            { id: 'spotify', name: 'Spotify', icon: Music, wattage: 0.15, impact: 'medium', color: '#1db954' },
        ];

        let newApps = [...baseApps];

        if (userProfile.includes('Power')) {
            newApps.push({ id: 'youtube', name: 'YouTube 4K', icon: Youtube, wattage: 0.82, impact: 'high', color: '#ff0000' });
            newApps.push({ id: 'genshin', name: 'Genshin Impact', icon: Gamepad2, wattage: 3.5, impact: 'max', color: '#ff4757' });
            if (userProfile === 'Power 2x') {
                newApps.push({ id: 'twitch', name: 'Twitch Stream', icon: Monitor, wattage: 1.2, impact: 'high', color: '#9146ff' });
            }
        } else if (userProfile.includes('Eco')) {
            // Eco has fewer apps
        } else {
            // Baseline
            newApps.push({ id: 'instagram', name: 'Instagram', icon: Instagram, wattage: 0.35, impact: 'high', color: '#e4405f' });
        }

        setApps(newApps);
    }, [userProfile]);

    const configs: any = {
        'Gaming': { u: 98, b: 1.0, icon: Gamepad2, color: '#ff4757', label: "Thermal Stress" },
        'Network': { u: 45, b: 0.6, icon: Globe, color: '#00f2ff', label: "5G Stress" },
        'Social': { u: 75, b: 0.8, icon: Youtube, color: '#7d5fff', label: "Video Render" }
    };

    const removeApp = (id: string) => {
        setApps(prev => prev.filter(app => app.id !== id));
    };

    useEffect(() => {
        const root = document.documentElement;
        if (isDarkMode) root.classList.remove('theme-light');
        else root.classList.add('theme-light');
    }, [isDarkMode]);

    useEffect(() => {
        const interval = setInterval(() => {
            const pConfig = PROFILE_CONFIGS[userProfile];
            // Calculate Network Load (0.0 - 1.0)
            let netLoad = 0.05; // Base ping
            if (activeScenario === 'Network') netLoad = 1.0; // Max download
            else if (activeScenario === 'Gaming') netLoad = 0.6; // Consistent multiplayer data
            else if (activeScenario === 'Social') netLoad = 0.3; // Feed scrolling
            else if (apps.some((a: any) => a.id === 'youtube' || a.id === 'twitch')) netLoad = 0.5; // Streaming
            else if (apps.some((a: any) => a.id === 'instagram')) netLoad = 0.2;

            let params = {
                brightness,
                cpuUtil: 15 + Math.random() * 10,
                isLPM,
                isWifi,
                signal: -85,
                appDrain: apps.reduce((acc, curr) => acc + curr.wattage * 1000, 0) / 2,
                apr: isDarkMode ? 0.3 : 0.9,
                profileScale: pConfig.scale,
                networkLoad: netLoad
            };

            if (activeScenario && timer > 0) {
                const c = configs[activeScenario];
                params = { ...params, brightness: c.b, cpuUtil: c.u, signal: -115, appDrain: 3000, networkLoad: 1.0 };
                setTimer(t => t - 1);
            } else if (timer === 0) {
                setActiveScenario(null);
            }

            const res = model.step(params);
            setState({
                ...res,
                mah: Math.round(res.soc * Q_CAP_MAH),
                p: res.pTotal
            });
        }, 1000);
        return () => clearInterval(interval);
    }, [brightness, isLPM, isDarkMode, isWifi, activeScenario, timer, model, apps, userProfile]);

    return (
        <div className="app-container">
            <header>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Zap size={20} color="var(--accent-color)" />
                    <span style={{ fontWeight: 800, fontSize: '14px', letterSpacing: '1px' }}>ECODRAIN v1.3</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <button onClick={() => setIsWidgetView(!isWidgetView)} style={{ background: 'none', border: 'none', color: 'var(--accent-color)', cursor: 'pointer', marginRight: '15px' }} title="Toggle Home Widget View">
                        <Grid size={20} />
                    </button>
                    <button onClick={() => setIsFYIOpen(true)} style={{ background: 'none', border: 'none', color: 'var(--accent-color)', cursor: 'pointer' }}>
                        <BookOpen size={20} />
                    </button>
                </div>
            </header>

            {isWidgetView ? (
                <div style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '20px',
                    backgroundColor: '#333',
                    backgroundImage: 'url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop")',
                    backgroundPosition: 'center',
                    backgroundSize: 'cover',
                    position: 'relative',
                    overflow: 'hidden',
                    minHeight: '600px',
                    border: '4px solid #1a1b1e',
                    boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
                }}>
                    {/* Status Bar Shim */}
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '30px', background: 'rgba(0,0,0,0.3)', backdropFilter: 'blur(2px)' }}></div>

                    <div style={{
                        width: '90%',
                        padding: '16px',
                        background: 'rgba(20, 20, 20, 0.75)',
                        backdropFilter: 'blur(16px)',
                        borderRadius: '24px',
                        border: '1px solid rgba(255,255,255,0.1)',
                        color: '#fff',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '12px',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Zap size={16} color="var(--accent-color)" fill="var(--accent-color)" />
                                <span style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '0.5px' }}>EcoDrain</span>
                            </div>
                            <span style={{ fontSize: '11px', opacity: 0.7, background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px' }}>{userProfile}</span>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: '5px' }}>
                            <div>
                                <div style={{ fontSize: '36px', fontWeight: 600, lineHeight: 1 }}>{Math.round(state.soc * 100)}%</div>
                                <div style={{ fontSize: '12px', opacity: 0.7, marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <Battery size={12} />
                                    {Math.floor(state.tte / 3600)}h {Math.floor((state.tte % 3600) / 60)}m Left
                                </div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '20px', fontWeight: 600, color: 'var(--accent-color)' }}>{state.p.toFixed(1)}W</div>
                                <div style={{ fontSize: '10px', opacity: 0.7 }}>Current Load</div>
                            </div>
                        </div>

                        <div style={{ marginTop: '5px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', marginBottom: '4px', opacity: 0.6 }}>
                                <span>Discharge Rate</span>
                                <span>{state.soc < 0.2 ? 'Critical' : 'Normal'}</span>
                            </div>
                            <div style={{ height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                                <div style={{ height: '100%', width: `${state.soc * 100}%`, background: state.soc < 0.2 ? 'var(--danger)' : 'linear-gradient(90deg, var(--accent-color), #2ed573)' }} />
                            </div>
                        </div>
                    </div>

                    <div style={{ position: 'absolute', bottom: '80px', display: 'flex', gap: '15px' }}>
                        {[1, 2, 3, 4].map(i => (
                            <div key={i} style={{ width: '50px', height: '50px', borderRadius: '14px', background: 'rgba(255,255,255,0.15)', backdropFilter: 'blur(10px)' }}></div>
                        ))}
                    </div>

                    <div style={{ position: 'absolute', bottom: '40px', fontSize: '12px', fontWeight: 600, color: 'rgba(255,255,255,0.8)', textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>
                        Simulated Home Screen
                    </div>
                </div>
            ) : (
                <>
                    <section className="hero-visual">
                        <div className="ring-container">
                            <svg className="ring-svg" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(128,128,128,0.05)" strokeWidth="6" />
                                <motion.circle
                                    cx="50" cy="50" r="46"
                                    fill="none" stroke="var(--accent-color)" strokeWidth="6"
                                    strokeDasharray="289" animate={{ strokeDashoffset: 289 * (1 - state.soc) }}
                                    strokeLinecap="round"
                                />
                            </svg>
                            <div className="percentage-display">
                                <h1>{Math.round(state.soc * 100)}<span className="unit">%</span></h1>
                                <div className="charging-status" style={{ color: activeScenario ? 'var(--danger)' : PROFILE_CONFIGS[userProfile].color }}>
                                    {userProfile} Profile
                                </div>
                            </div>
                        </div>
                        <div className="tte-display">
                            <span className="label">ACTIVE TIME TO EMPTY</span>
                            <div className="value">{Math.floor(state.tte / 3600)}h {Math.floor((state.tte % 3600) / 60)}m</div>
                        </div>
                    </section>

                    <section className="control-sheet">
                        {/* User Profile Selector */}
                        <div style={{ marginBottom: '10px', overflowX: 'auto', whiteSpace: 'nowrap', paddingBottom: '5px' }}>
                            {Object.keys(PROFILE_CONFIGS).map((key) => (
                                <button
                                    key={key}
                                    onClick={() => setUserProfile(key as UserProfile)}
                                    style={{
                                        display: 'inline-block',
                                        padding: '6px 12px',
                                        margin: '0 4px',
                                        borderRadius: '12px',
                                        background: userProfile === key ? PROFILE_CONFIGS[key as UserProfile].color : 'rgba(255,255,255,0.1)',
                                        color: userProfile === key ? '#000' : '#fff',
                                        border: 'none',
                                        fontSize: '11px',
                                        fontWeight: 700,
                                        cursor: 'pointer'
                                    }}
                                >
                                    {key}
                                </button>
                            ))}
                        </div>

                        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                            <button className={`scenario-btn ${isDarkMode ? 'active' : ''}`} style={{ flex: 1, flexDirection: 'row', padding: '12px' }} onClick={() => setIsDarkMode(!isDarkMode)}>
                                {isDarkMode ? <Moon size={16} /> : <Sun size={16} />} <span>{isDarkMode ? 'OLED Dark' : 'Bright Mode'}</span>
                            </button>
                            <button className={`scenario-btn ${isLPM ? 'active' : ''}`} style={{ flex: 1, flexDirection: 'row', padding: '12px' }} onClick={() => setIsLPM(!isLPM)}>
                                <Zap size={16} /> <span>Eco Mode</span>
                            </button>
                            <button className="scenario-btn" style={{ flex: 1, flexDirection: 'row', padding: '12px' }} onClick={() => setIsWifi(!isWifi)}>
                                {isWifi ? <Wifi size={16} /> : <Activity size={16} />} <span>{isWifi ? 'Wi-Fi On' : '5G Data'}</span>
                            </button>
                        </div>

                        <div style={{ padding: '0 5px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                <span style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-secondary)' }}>BACKLIGHT LEVEL</span>
                                <span style={{ fontSize: '10px', fontWeight: 800 }}>{Math.round(brightness * 100)}%</span>
                            </div>
                            <input type="range" min="0.05" max="1" step="0.01" value={brightness} onChange={e => setBrightness(parseFloat(e.target.value))} className="slider" style={{ width: '100%' }} />
                        </div>

                        <div className="scenario-grid">
                            {Object.entries(configs).map(([key, c]: [string, any]) => (
                                <button key={key} className={`scenario-btn ${activeScenario === key ? 'active' : ''}`} onClick={() => { setActiveScenario(key); setTimer(10); }}>
                                    <c.icon size={20} color={activeScenario === key ? '#000' : c.color} />
                                    <span>{key} Load</span>
                                </button>
                            ))}
                        </div>
                    </section>

                    <div className="markers-grid">
                        <div className="marker-card">
                            <div className="marker-header"><Thermometer size={14} /> <span>Thermal Engine</span></div>
                            <div className="marker-value"><h3 style={{ color: state.temp > 38 ? 'var(--danger)' : 'var(--success)' }}>{state.temp.toFixed(1)}</h3><span className="unit">°C</span></div>
                            <div className="marker-progress"><div className="progress-fill" style={{ width: `${Math.min(100, (state.temp - 22) * 4)}%`, background: state.temp > 38 ? 'var(--danger)' : 'var(--success)' }} /></div>
                        </div>
                        <div className="marker-card">
                            <div className="marker-header"><Activity size={14} /> <span>Global Sink</span></div>
                            <div className="marker-value"><h3>{state.p.toFixed(2)}</h3><span className="unit">Watts</span></div>
                            <div className="marker-progress"><div className="progress-fill" style={{ width: `${Math.min(100, state.p * 15)}%`, background: 'var(--accent-color)' }} /></div>
                        </div>

                        <div className="marker-card full-width">
                            <div className="marker-header"><Cpu size={14} /> <span>Octa-Core Cluster Activity</span></div>
                            <div className="core-grid">
                                <CoreChip name="P-Core 1" freq={(activeScenario ? 3.2 : 0.6 + Math.random() * 0.4).toFixed(2)} power={(state.pCpu * 0.35).toFixed(2)} color="var(--danger)" />
                                <CoreChip name="P-Core 2" freq={(activeScenario ? 3.2 : 0.6 + Math.random() * 0.4).toFixed(2)} power={(state.pCpu * 0.35).toFixed(2)} color="var(--danger)" />
                                <CoreChip name="E-Core 1" freq={(0.4 + Math.random() * 1.5).toFixed(2)} power={(state.pCpu * 0.07).toFixed(2)} color="var(--success)" />
                                <CoreChip name="E-Core 2" freq={(0.4 + Math.random() * 1.5).toFixed(2)} power={(state.pCpu * 0.07).toFixed(2)} color="var(--success)" />
                                <CoreChip name="E-Core 3" freq={(0.4 + Math.random() * 1.5).toFixed(2)} power={(state.pCpu * 0.07).toFixed(2)} color="var(--success)" />
                                <CoreChip name="E-Core 4" freq={(0.4 + Math.random() * 1.5).toFixed(2)} power={(state.pCpu * 0.07).toFixed(2)} color="var(--success)" />
                            </div>
                        </div>

                        {/* Per-App Impact with Removal Logic */}
                        <div className="marker-card full-width">
                            <div className="marker-header"><Activity size={14} /> <span>Active Software Impact</span></div>
                            <div className="app-impact-list">
                                <AnimatePresence>
                                    {apps.map((app) => (
                                        <motion.div
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, scale: 0.8 }}
                                            className="impact-item"
                                            key={app.id}
                                        >
                                            <div className="impact-app-info">
                                                <app.icon size={16} color={app.color} />
                                                <span className="impact-name">{app.name}</span>
                                                <span className={`impact-badge impact-${app.impact}`}>{app.impact}</span>
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                                <span className="impact-wattage">{(app.wattage * (activeScenario === 'Gaming' && app.impact === 'high' ? 2.5 : 1)).toFixed(2)}W</span>
                                                {app.id !== 'ecodrain' && (
                                                    <Trash2 size={14} color="var(--danger)" style={{ cursor: 'pointer', opacity: 0.6 }} onClick={() => removeApp(app.id)} />
                                                )}
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                                {apps.length === 1 && (
                                    <div style={{ textAlign: 'center', fontSize: '11px', color: 'var(--text-secondary)', padding: '10px' }}>
                                        All background apps terminated. System Optimized.
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="marker-card full-width">
                            <div className="marker-header"><Layers size={14} /> <span>Topology Breakdown</span></div>
                            <div className="physics-stack">
                                <div className="physics-item"><span>Processor Cluster</span><span>{state.pCpu.toFixed(2)}W</span></div>
                                <div className="physics-item"><span>OLED Logic (APR: {isDarkMode ? '0.30' : '0.90'})</span><span>{state.pDisp.toFixed(2)}W</span></div>
                                <div className="physics-item"><span>Carrier Radio (Capped peak)</span><span>{state.pNet.toFixed(2)}W</span></div>
                            </div>
                        </div>
                    </div>

                    <div className="android-notification">
                        <Zap size={18} color="var(--accent-color)" />
                        <div style={{ flex: 1 }}>
                            <h6 style={{ fontSize: '11px', color: '#fff', fontWeight: 800 }}>ECODRAIN ACTIVE</h6>
                            <div style={{ display: 'flex', gap: '15px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                                <span>{state.p.toFixed(2)}W Drain</span>
                                <span>{Math.floor(state.tte / 3600)}h {Math.floor((state.tte % 3600) / 60)}m Left</span>
                            </div>
                        </div>
                        <ShieldCheck size={18} color="var(--success)" style={{ opacity: 0.5 }} />
                    </div>
                </>
            )
            }

            <FYIModal isOpen={isFYIOpen} onClose={() => setIsFYIOpen(false)} />
        </div >
    );
}
