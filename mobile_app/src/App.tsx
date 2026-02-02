import React, { useState, useEffect, useMemo } from 'react';
import {
    Wifi,
    Battery,
    Cpu,
    Monitor,
    Thermometer,
    Zap,
    ShieldCheck,
    ChevronRight,
    Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Constants & Model ---
const Q_CAP_MAX = 3274 * 3600;

class EcoDrainModel {
    soc: number = 0.84;
    v_p1: number = 0;
    v_p2: number = 0;
    r1 = 0.015; c1 = 2000;
    r2 = 0.030; c2 = 10000;
    lastUpdateTime = Date.now();

    step(isLPM: boolean, cpu: number, screen: number, signal: number) {
        const now = Date.now();
        const dt = (now - this.lastUpdateTime) / 1000;
        this.lastUpdateTime = now;

        // Power Calculation
        const p_disp = 1.8 * screen;
        const p_cpu = 3.5 * (cpu / 100);
        const signal_factor = Math.pow(10, (-signal - 80) / 20);
        const p_net = 0.5 * Math.min(signal_factor, 2.0);

        let total = p_disp + p_cpu + p_net + 0.1;
        if (isLPM) total *= 0.65;

        const voc = 3.0 + 1.0 * this.soc + 0.2 * Math.log(this.soc + 0.01);
        const v_term = voc - 0.05;
        const i_load = total / v_term;

        this.soc -= (i_load * dt) / Q_CAP_MAX;
        return {
            soc: this.soc,
            tte: (this.soc * Q_CAP_MAX) / i_load,
            power: total
        };
    }
}

// --- Components ---

const MarkerCard = ({ icon: Icon, label, value, unit, color = "var(--accent-color)" }: any) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-3xl p-4 flex flex-col gap-2 relative overflow-hidden"
        style={{ minWidth: '160px', flex: 1 }}
    >
        <div className="flex items-center gap-2">
            <Icon size={16} className="text-slate-400" strokeWidth={2.5} />
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">{label}</span>
        </div>
        <div className="flex items-baseline gap-1">
            <span className="text-2xl font-semibold tracking-tight">{value}</span>
            <span className="text-xs text-slate-500 font-medium">{unit}</span>
        </div>
        <div className="h-1 w-full bg-slate-800 rounded-full mt-2 overflow-hidden">
            <motion.div
                className="h-full"
                style={{ backgroundColor: color }}
                animate={{ width: `${Math.min(100, Math.max(0, parseFloat(value) * (unit === '%' ? 1 : 100)))}%` }}
            />
        </div>
    </motion.div>
);

export default function App() {
    const model = useMemo(() => new EcoDrainModel(), []);
    const [stats, setStats] = useState({ soc: 0.84, tte: 20520, power: 1.2 });
    const [isLPM, setIsLPM] = useState(false);
    const [markers, setMarkers] = useState({ cpu: 42, screen: 0.32, signal: -92, temp: 34.2 });
    const [time, setTime] = useState(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

    useEffect(() => {
        const interval = setInterval(() => {
            // Fluctuate markers
            setMarkers(m => ({
                ...m,
                cpu: 25 + Math.random() * 30,
                signal: -85 - Math.random() * 15,
                temp: 33 + Math.random() * 2
            }));

            const newState = model.step(isLPM, markers.cpu, markers.screen, markers.signal);
            setStats(newState);
            setTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        }, 1000);
        return () => clearInterval(interval);
    }, [isLPM, markers, model]);

    const socPercentage = Math.round(stats.soc * 100);
    const tteHours = Math.floor(stats.tte / 3600);
    const tteMins = Math.floor((stats.tte % 3600) / 60);

    return (
        <div className="scroll-container px-6 pt-4 pb-12">
            {/* OS Status Bar */}
            <header className="flex justify-between items-center mb-8">
                <span className="font-semibold text-sm opacity-60">{time}</span>
                <div className="flex gap-2">
                    <Wifi size={14} className="opacity-60" />
                    <Battery size={14} className="opacity-60" />
                </div>
            </header>

            {/* Hero Header */}
            <div className="mb-10">
                <h1 className="text-3xl font-bold tracking-tight mb-1">EcoDrain</h1>
                <p className="text-slate-400 text-sm font-medium">Model 2RC-Thevenin Intelligence</p>
            </div>

            {/* Main Visualizer */}
            <section className="flex flex-col items-center mb-12">
                <div className="relative w-64 h-64 flex-center">
                    <svg className="absolute w-full h-full -rotate-90">
                        <circle
                            cx="128" cy="128" r="110"
                            fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="12"
                        />
                        <motion.circle
                            cx="128" cy="128" r="110"
                            fill="none" stroke="var(--accent-color)" strokeWidth="12"
                            strokeLinecap="round"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: stats.soc }}
                            transition={{ type: "spring", stiffness: 50 }}
                            style={{ filter: "drop-shadow(0 0 12px var(--accent-glow))" }}
                        />
                    </svg>
                    <div className="text-center z-10">
                        <div className="flex items-baseline justify-center">
                            <span className="text-7xl font-bold tracking-tighter">{socPercentage}</span>
                            <span className="text-xl font-medium text-slate-500 ml-1">%</span>
                        </div>
                        <p className="text-[10px] tracking-[0.2em] font-bold text-cyan-400 mt-[-4px]">DISCHARGING</p>
                    </div>
                </div>

                <div className="mt-8 text-center">
                    <span className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">TIME TO EMPTY</span>
                    <span className="text-2xl font-medium">{tteHours}h {tteMins}m</span>
                </div>
            </section>

            {/* Markers Grid */}
            <section className="grid grid-cols-2 gap-4 mb-10">
                <MarkerCard icon={Cpu} label="CPU Activity" value={markers.cpu.toFixed(0)} unit="%" />
                <MarkerCard icon={Monitor} label="OLED APR" value={markers.screen.toFixed(2)} unit="ratio" />
                <MarkerCard icon={Wifi} label="Network" value={markers.signal.toFixed(0)} unit="dBm" />
                <MarkerCard icon={Thermometer} label="Thermal" value={markers.temp.toFixed(1)} unit="°C" color="var(--danger)" />
            </section>

            {/* Optimization Toggles */}
            <section className="space-y-4">
                <h2 className="text-sm font-bold uppercase tracking-widest text-slate-500 px-1">Control Center</h2>

                <div className="glass rounded-[32px] p-6 flex justify-between items-center">
                    <div>
                        <h3 className="font-bold flex items-center gap-2">
                            <Zap size={16} className="text-yellow-400" />
                            Low Power Mode
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">Throttle markers by 35%</p>
                    </div>
                    <button
                        onClick={() => setIsLPM(!isLPM)}
                        className={`w-14 h-8 rounded-full relative transition-colors duration-300 ${isLPM ? 'bg-cyan-500' : 'bg-slate-800'}`}
                    >
                        <motion.div
                            animate={{ x: isLPM ? 26 : 4 }}
                            className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg"
                        />
                    </button>
                </div>

                <motion.div
                    layout
                    className="bg-gradient-to-r from-cyan-500/10 to-transparent border-l-4 border-cyan-500 rounded-3xl p-6 flex gap-4"
                >
                    <div className="w-10 h-10 rounded-2xl bg-cyan-500/20 flex-center text-xl">✨</div>
                    <div className="flex-1">
                        <h4 className="text-[10px] font-black tracking-tighter text-cyan-400 mb-1 uppercase">Recommended</h4>
                        <p className="text-sm leading-relaxed">
                            {isLPM
                                ? "LPM is extending your session using limited background refresh."
                                : "Switching to Dark Mode reduces Pixel Ratio (APR) significantly."
                            }
                        </p>
                    </div>
                </motion.div>
            </section>

            {/* Style overrides for standard Tailwind-like classes used above */}
            <style>{`
        .flex-center { display: flex; align-items: center; justify-content: center; }
        .rounded-3xl { border-radius: 1.5rem; }
        .rounded-[32px] { border-radius: 2rem; }
        .tracking-widest { letter-spacing: 0.1em; }
        .tracking-tighter { letter-spacing: -0.05em; }
        .grid { display: grid; }
        .grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .gap-4 { gap: 1rem; }
        .px-6 { padding-left: 1.5rem; padding-right: 1.5rem; }
        .pt-4 { padding-top: 1rem; }
        .pb-12 { padding-bottom: 3rem; }
        .mb-8 { margin-bottom: 2rem; }
        .mb-10 { margin-bottom: 2.5rem; }
        .mb-12 { margin-bottom: 3rem; }
        .space-y-4 > * + * { margin-top: 1rem; }
        .flex { display: flex; }
        .flex-col { flex-direction: column; }
        .items-center { align-items: center; }
        .items-baseline { align-items: baseline; }
        .justify-between { justify-content: space-between; }
        .justify-center { justify-content: center; }
        .gap-1 { gap: 0.25rem; }
        .gap-2 { gap: 0.5rem; }
        .gap-4 { gap: 1rem; }
        .text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
        .text-2xl { font-size: 1.5rem; line-height: 2rem; }
        .text-xl { font-size: 1.25rem; line-height: 1.75rem; }
        .text-sm { font-size: 0.875rem; line-height: 1.25rem; }
        .text-xs { font-size: 0.75rem; line-height: 1rem; }
        .text-7xl { font-size: 4.5rem; line-height: 1; }
        .font-bold { font-weight: 700; }
        .font-semibold { font-weight: 600; }
        .font-medium { font-weight: 500; }
        .text-slate-400 { color: #94a3b8; }
        .text-slate-500 { color: #64748b; }
        .text-cyan-400 { color: #22d3ee; }
        .text-cyan-500 { color: #06b6d4; }
        .bg-cyan-500 { background-color: #06b6d4; }
        .bg-cyan-500\/10 { background-color: rgb(6 182 212 / 0.1); }
        .bg-cyan-500\/20 { background-color: rgb(6 182 212 / 0.2); }
        .border-l-4 { border-left-width: 4px; }
        .border-cyan-500 { border-color: #06b6d4; }
        .opacity-60 { opacity: 0.6; }
      `}</style>
        </div>
    );
}
