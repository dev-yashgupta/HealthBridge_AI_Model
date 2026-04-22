import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import heroMedicalAi from '../assets/hero-medical-ai.png';

export default function Home() {
  // Subtle animated numeric state for the UI effect
  const [pulse, setPulse] = useState(68);
  useEffect(() => {
    const interval = setInterval(() => {
      setPulse(p => p === 68 ? 69 : (p === 69 ? 67 : 68));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="px-4 md:px-8 xl:px-10 2xl:px-14 max-w-[1920px] mx-auto min-h-screen relative text-slate-200 py-8 overflow-hidden font-sans">
      {/* Background ambient glows (Futuristic Environment) */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden bg-[#030712]">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-cyan-900/20 rounded-full blur-[150px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-blue-900/20 rounded-full blur-[150px]"></div>
        <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] bg-indigo-900/10 rounded-full blur-[120px]"></div>
        {/* Subtle grid pattern background overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')] opacity-50 z-0"></div>
      </div>

      <div className="relative z-10 w-full space-y-12">
        
        {/* Welcome Section with Hero Background Image */}
        <section className="relative w-full rounded-[40px] overflow-hidden flex flex-col lg:flex-row items-center justify-between min-h-[550px] 2xl:min-h-[620px] mb-20 xl:mb-28 border border-white/5 shadow-[0_25px_60px_rgba(0,0,0,0.6)] bg-[#030712]">
          {/* Background Image & Overlays */}
          <div className="absolute inset-0 z-0 overflow-hidden">
            <img 
              src={heroMedicalAi} 
              alt="AI Healthcare Concept" 
              className="w-full h-full object-cover object-center lg:object-[90%_75%] opacity-100 lg:scale-[1.15] lg:-translate-x-8 lg:-translate-y-2 animate-[float-down_20s_ease-in-out_infinite]"
            />
            {/* Deep gradient overlay for text readability on left */}
            <div className="absolute inset-0 bg-gradient-to-r from-[#030712] via-[#030712]/85 to-transparent"></div>
            {/* Top/bottom vignette gradients */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#030712]/90 via-transparent to-[#030712]/90"></div>
          </div>
          
          <div className="relative z-10 flex flex-col lg:flex-row items-center justify-between w-full px-8 py-14 lg:p-20 xl:p-24 gap-12 lg:gap-10">
            {/* Left Content Area */}
            <div className="space-y-10 max-w-2xl xl:max-w-5xl w-full text-center lg:text-left z-10 lg:translate-y-8">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold tracking-[0.2em] uppercase backdrop-blur-md shadow-[0_0_20px_rgba(6,182,212,0.15)] mx-auto lg:mx-0">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                </span>
                Neural Matrix Online
              </div>
              
              <h1 className="font-headline text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tighter text-white drop-shadow-xl leading-[1.1]">
                Advanced <span className="text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]">AI-Guided</span><br />
                Healthcare
              </h1>
              
              <p className="text-slate-300 text-lg md:text-xl font-light leading-relaxed max-w-xl mx-auto lg:mx-0">
                Welcome back. Your biometrics are stabilized. Core physiological and cognitive neural links indicate an optimal state across all monitored frequencies.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-5 pt-4">
                <Link to="/checker" className="w-full sm:w-auto px-10 py-4 bg-cyan-500 hover:bg-cyan-400 text-cyan-950 font-bold uppercase tracking-widest text-sm rounded-xl transition-all duration-500 shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_40px_rgba(6,182,212,0.7)] hover:-translate-y-1.5 text-center flex items-center justify-center gap-2 group/cta">
                  Start AI Analysis
                  <span className="material-symbols-outlined text-xl group-hover/cta:translate-x-1 transition-transform">rocket_launch</span>
                </Link>
                <Link to="/history" className="w-full sm:w-auto px-10 py-4 bg-white/5 hover:bg-white/10 text-white border border-white/20 font-bold uppercase tracking-widest text-sm rounded-xl transition-all duration-500 backdrop-blur-md hover:border-cyan-500/50 hover:text-cyan-300 hover:shadow-[0_0_25px_rgba(6,182,212,0.25)] hover:-translate-y-1.5 text-center">
                  View History
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Dynamic Bento Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 lg:gap-10 mb-16">
          
          {/* Main Health Metric - Glassmorphism Layered Card */}
          <div className="lg:col-span-2 group relative rounded-[40px] p-[1px] overflow-hidden">
            {/* Premium Animated Border Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/40 via-[#0a142c] to-blue-500/40 group-hover:from-cyan-300/60 group-hover:to-blue-400/60 transition-colors duration-700"></div>
            
            <div className="relative h-full bg-[#050b14]/90 backdrop-blur-3xl rounded-[39px] p-10 lg:p-12 flex flex-col justify-between overflow-hidden">
              {/* Internal glowing highlights */}
              <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-600/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/3 group-hover:bg-cyan-500/20 group-hover:scale-110 transition-all duration-1000 ease-out"></div>
              
              <div className="relative z-10">
                <div className="flex justify-between items-start mb-10">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-cyan-400 mb-2 block opacity-90">Live Telemetry</span>
                    <h2 className="text-3xl lg:text-4xl font-headline font-bold text-white tracking-tight">Cardiovascular Scan</h2>
                  </div>
                  <div className="w-14 h-14 rounded-2xl bg-cyan-950/40 border border-cyan-500/30 flex items-center justify-center shadow-[inset_0_0_20px_rgba(6,182,212,0.2)] backdrop-blur-sm transform group-hover:rotate-12 transition-transform duration-500">
                    <span className="material-symbols-outlined text-cyan-400 text-3xl">monitor_heart</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12 mb-8">
                  <div className="space-y-3 relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-cyan-400 to-transparent rounded-full opacity-50"></div>
                    <div className="pl-4">
                      <p className="text-slate-400 text-xs font-semibold uppercase tracking-[0.2em] mb-2">Resting Vitals</p>
                      <div className="flex items-end gap-3">
                        <span className="text-6xl font-headline font-extrabold text-white drop-shadow-[0_2px_10px_rgba(255,255,255,0.2)] transition-all duration-300">
                          {pulse}
                        </span>
                        <span className="text-cyan-500 font-bold mb-2 tracking-widest uppercase text-sm">BPM</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3 relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-400 to-transparent rounded-full opacity-50"></div>
                    <div className="pl-4">
                      <p className="text-slate-400 text-xs font-semibold uppercase tracking-[0.2em] mb-2">Blood Pressure</p>
                      <div className="flex items-end gap-3">
                        <span className="text-6xl font-headline font-extrabold text-white drop-shadow-[0_2px_10px_rgba(255,255,255,0.2)]">118<span className="text-4xl text-slate-500/80">/76</span></span>
                        <span className="text-blue-400 font-bold mb-2 tracking-widest uppercase text-sm">mmHg</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="relative z-10 pt-6 border-t border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <p className="text-xs text-slate-400 flex items-center gap-3 font-medium tracking-wide">
                  <span className="relative flex h-2.5 w-2.5 shadow-[0_0_10px_#22d3ee]">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
                  </span>
                  Quantum Sync Active • Rendered {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </p>
                <button className="text-cyan-400 hover:text-cyan-300 text-sm font-bold tracking-widest uppercase transition-colors flex items-center gap-2 group/btn">
                  Analyze Metrics 
                  <span className="material-symbols-outlined text-lg group-hover/btn:translate-x-1 group-hover/btn:scale-110 transition-transform">trending_flat</span>
                </button>
              </div>
            </div>
          </div>

          {/* Quick Action: Checker Gateway */}
          <Link to="/checker" className="block relative group rounded-3xl p-[1px] overflow-hidden transform hover:-translate-y-2 transition-all duration-500 shadow-[0_15px_40px_-15px_rgba(59,130,246,0.3)] hover:shadow-[0_20px_50px_-10px_rgba(6,182,212,0.4)]">
            <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/60 to-blue-700/60 group-hover:from-cyan-400 group-hover:to-blue-600 transition-colors duration-500"></div>
            <div className="relative h-full bg-gradient-to-br from-blue-900/90 via-[#060c1d] to-indigo-900/90 backdrop-blur-2xl rounded-[23px] p-8 lg:p-10 flex flex-col justify-between text-white overflow-hidden">
              
              {/* Abstract decorative elements */}
              <div className="absolute -bottom-16 -right-16 w-64 h-64 bg-blue-500/20 rounded-full blur-[60px] group-hover:bg-cyan-400/30 transition-colors duration-700"></div>
              <div className="absolute top-0 right-0 p-6 opacity-30 group-hover:opacity-100 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-300">
                <span className="material-symbols-outlined text-4xl text-cyan-300">open_in_new</span>
              </div>
              
              <div className="w-20 h-20 rounded-[20px] bg-white/5 border border-white/20 flex items-center justify-center mb-8 backdrop-blur-xl shadow-[0_10px_25px_rgba(0,0,0,0.5)] group-hover:scale-110 group-hover:bg-white/10 transition-all duration-500">
                <span className="material-symbols-outlined text-4xl text-cyan-200">hub</span>
              </div>
              
              <div className="z-10 relative">
                <h3 className="text-3xl font-headline font-bold mb-3 text-white">AI Interface</h3>
                <p className="text-blue-200/70 text-sm leading-relaxed font-light tracking-wide">
                  Deploy neural diagnostic algorithms to assess and isolate newly detected bio-anomalies.
                </p>
              </div>
              
              {/* Animated Progress/Scanning Bar Effect */}
              <div className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent w-full opacity-0 group-hover:opacity-100 group-hover:animate-[translate-x-full_2s_linear_infinite] transition-opacity"></div>
            </div>
          </Link>

        </div>

        {/* Secondary Modules: History & Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 mb-16">
          
          {/* Encrypted History Log */}
          <div className="group relative rounded-[40px] p-[1px] overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-transparent"></div>
            <div className="relative h-full bg-[#050b14]/90 backdrop-blur-3xl rounded-[39px] flex flex-col shadow-[0_15px_40px_rgba(0,0,0,0.6)]">
              <div className="p-8 lg:p-10 border-b border-white/5 flex justify-between items-center bg-white/[0.01]">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-indigo-500/20 border border-indigo-500/30 hidden sm:block">
                    <span className="material-symbols-outlined text-indigo-400 block text-sm">history_toggle_off</span>
                  </div>
                  <h3 className="font-headline text-2xl font-bold text-white tracking-tight">System Logs</h3>
                </div>
                <Link to="/history" className="text-indigo-400 hover:text-cyan-300 text-xs font-bold uppercase tracking-[0.2em] transition-all py-2.5 px-5 rounded-full border border-indigo-500/30 hover:bg-cyan-900/30 hover:border-cyan-400/50">View Protocol</Link>
              </div>
              
              <div className="p-8 lg:p-10 space-y-5 flex-1">
                {/* Log Entry 1 */}
                <div className="group/item flex items-center gap-5 bg-[#0a1122] hover:bg-[#0c162e] border border-white/5 hover:border-cyan-500/30 p-5 rounded-2xl transition-all duration-300 cursor-pointer shadow-sm hover:shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-600/30 to-indigo-600/20 border border-blue-500/30 flex items-center justify-center shadow-[inset_0_0_15px_rgba(59,130,246,0.2)]">
                    <span className="material-symbols-outlined text-blue-400">check_circle</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-slate-200 font-bold tracking-wide text-sm group-hover/item:text-cyan-300 transition-colors">Routine Scan Authorized</p>
                    <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mt-1">Oct 12, 2023 • 14:02:44</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center group-hover/item:bg-cyan-500/20 group-hover/item:border-cyan-500/40 transition-all">
                    <span className="material-symbols-outlined text-slate-400 group-hover/item:text-cyan-400 text-sm">arrow_forward_ios</span>
                  </div>
                </div>
                
                {/* Log Entry 2 */}
                <div className="group/item flex items-center gap-5 bg-[#0a1122] hover:bg-[#0c162e] border border-white/5 hover:border-cyan-500/30 p-5 rounded-2xl transition-all duration-300 cursor-pointer shadow-sm hover:shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-600/30 to-teal-600/20 border border-cyan-500/30 flex items-center justify-center shadow-[inset_0_0_15px_rgba(6,182,212,0.2)]">
                    <span className="material-symbols-outlined text-cyan-400">biotech</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-slate-200 font-bold tracking-wide text-sm group-hover/item:text-cyan-300 transition-colors">Lab Results Verified</p>
                    <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mt-1">Oct 05, 2023 • 08:15:10</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center group-hover/item:bg-cyan-500/20 group-hover/item:border-cyan-500/40 transition-all">
                    <span className="material-symbols-outlined text-slate-400 group-hover/item:text-cyan-400 text-sm">arrow_forward_ios</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Neuro Tip Holographic Container */}
          <div className="group relative rounded-[40px] p-[1px] overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/20 via-transparent to-blue-500/20"></div>
            <div className="relative h-full bg-[#050b14]/90 backdrop-blur-3xl rounded-[39px] overflow-hidden flex flex-col shadow-[0_15px_40px_rgba(0,0,0,0.6)] border border-white/[0.02]">
              <div className="h-64 relative overflow-hidden">
                <img 
                  alt="Neuro tip visual background" 
                  className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-[2000ms] opacity-50 mix-blend-luminosity filter contrast-125" 
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAdW_-T-7m9CvbG771Ly02tVqt_14Ft_hoHVH_x61YRgWaLsjjbkoZJsuRJIVUWb2KqUYl_gYa82UD4AOs11A_7QADPSNJDoD3PQCsJey5H7nxie1XXjTZfuUBu4_TE8yvC8vdzizPSrZzY2hsqV5WeVFy4sJdnn8khB-YEJXoxqG6Y45wQ6YtgPaCi5bFVkvUK6lPVditXfiirDdb4ms3JHGad4dqiGcrQ_hwVbO2TNoQfY9ld787TqbGoic5EhID2wjG6W7h8_D8"
                />
                
                {/* Glitch/Scanline Overlays */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#050b14] via-[#050b14]/60 to-transparent z-10"></div>
                <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.1)_1px,transparent_1px)] bg-[size:100%_4px] opacity-20 pointer-events-none z-10"></div>
                <div className="absolute inset-0 bg-cyan-900/30 mix-blend-color z-10"></div>
                
                <div className="absolute bottom-6 left-6 right-6 z-20">
                  <div className="inline-flex items-center gap-2 bg-cyan-950/80 backdrop-blur-xl text-cyan-300 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-[0.2em] mb-4 border border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                    <span className="material-symbols-outlined text-[14px]">memory</span>
                    Optimization Insight
                  </div>
                  <h3 className="text-3xl font-headline font-bold text-white tracking-tight drop-shadow-[0_2px_10px_rgba(0,0,0,0.8)]">Hydration Protocol</h3>
                </div>
              </div>
              
              <div className="p-8 lg:p-10 2xl:p-12 flex-1 flex flex-col justify-between relative z-20 bg-[#050b14]">
                <p className="text-slate-400 text-sm lg:text-base xl:text-lg leading-relaxed mb-8 font-light tracking-wide">
                  Maintaining optimal liquid-baseline balance enhances neuro-plasticity and physical performance by up to 30%. Required daily intake: <span className="text-cyan-400 font-semibold">2500ml</span> to prevent system degradation.
                </p>
                <button className="flex items-center justify-between w-full bg-white/[0.02] hover:bg-cyan-950/40 hover:border-cyan-500/50 border border-white/10 rounded-2xl p-5 lg:p-6 transition-all duration-300 group/btn shadow-[inset_0_0_0_rgba(6,182,212,0)] hover:shadow-[0_0_20px_rgba(6,182,212,0.15)]">
                  <span className="text-slate-300 font-bold uppercase tracking-widest text-xs lg:text-sm group-hover/btn:text-cyan-300 transition-colors">Initialize Full Report</span>
                  <span className="material-symbols-outlined text-slate-500 group-hover/btn:text-cyan-300 group-hover/btn:translate-x-1 transition-all">double_arrow</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Security Badge */}
        <div className="flex justify-center pb-8 border-t border-white/5 pt-12">
          <div className="flex items-center gap-3 backdrop-blur-2xl bg-[#0a1122]/80 px-6 py-3 rounded-full border border-blue-500/20 shadow-[0_0_30px_rgba(0,0,0,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.2)] transition-shadow duration-500 cursor-default group/badge">
            <div className="relative flex items-center justify-center w-6 h-6">
              <div className="absolute inset-0 bg-cyan-400 rounded-full blur-[10px] opacity-40 group-hover/badge:opacity-70 transition-opacity"></div>
              <span className="material-symbols-outlined text-cyan-400 text-[18px] relative z-10 animate-pulse" style={{fontVariationSettings: "'FILL' 1"}}>shield_locked</span>
            </div>
            <span className="text-slate-400 text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.3em] group-hover/badge:text-cyan-200 transition-colors">End-to-End Quantum Encryption</span>
          </div>
        </div>
      </div>
    </main>
  );
}
