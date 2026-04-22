import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitDiagnosis } from '../services/api'

const QUICK_CHIPS = ["Fever", "Headache", "Cough", "Nausea", "Fatigue", "Dizziness"]

// Map dropdown label → duration_days value appended to symptoms text
const DURATION_MAP = {
  'Started today'      : 'since today',
  '2-3 days ago'       : 'for 2 days',
  'About a week'       : 'for 7 days',
  'More than 2 weeks'  : 'for 14 days',
}

export default function SymptomChecker() {
  const [symptomsText, setSymptomsText] = useState('')
  const [isLoading, setIsLoading]       = useState(false)
  const [error, setError]               = useState(null)
  const [duration, setDuration]         = useState('Started today')
  const [severity, setSeverity]         = useState('Moderate')

  const navigate = useNavigate()

  const handleChipClick = (label) => {
    setSymptomsText(prev => prev.trim() === '' ? label : prev + ' ' + label)
  }

  const handleSubmit = async () => {
    setError(null)
    setIsLoading(true)
    try {
      // Append duration + severity context to symptoms text so NLP can parse it
      const durationHint  = DURATION_MAP[duration] ?? ''
      const severityHint  = severity === 'Mild' ? 'mild symptoms' : severity === 'Severe' ? 'severe symptoms' : ''
      const fullText      = [symptomsText.trim(), durationHint, severityHint].filter(Boolean).join(', ')
      const result = await submitDiagnosis("GUEST", fullText)
      navigate("/results", { state: result })
    } catch {
      setError("The AI analysis failed. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const isSubmitDisabled = symptomsText.trim() === '' || isLoading

  return (
    <main className="pt-4 pb-8 px-6 max-w-5xl mx-auto">

      {/* Hero Section */}
      <section className="mb-10 relative">
        <div className="absolute -top-24 -left-24 w-64 h-64 bg-[#22d3ee]/10 rounded-full blur-[80px] pointer-events-none" />
        <div className="relative z-10">
          <span className="inline-block px-4 py-1.5 rounded-full bg-[#22d3ee]/10 border border-[#22d3ee]/20 text-[#22d3ee] text-[10px] font-bold tracking-[0.2em] uppercase mb-5">
            Diagnostic Assistant v2.0
          </span>
          <h2 className="text-4xl md:text-5xl font-headline font-extrabold text-white leading-tight mb-4">
            How are you{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#22d3ee] to-[#f472b6]">
              feeling
            </span>{' '}
            today?
          </h2>
          <p className="text-base text-[#94a3b8] max-w-xl leading-relaxed">
            Describe your symptoms. Our clinical AI analyzes data in real-time to provide immediate medical insights and next steps.
          </p>
        </div>
      </section>

      {/* 12-column grid: 8-col form + 4-col sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* Primary Form Area — 8 cols */}
        <div className="lg:col-span-8 space-y-6">

          {/* Main Input Card */}
          <div
            className="bg-[#0b1429] border border-white/10 rounded-2xl p-6 md:p-8 relative overflow-hidden group"
            style={{ boxShadow: '0 0 20px rgba(34, 211, 238, 0.15)' }}
          >
            {/* Decorative glow blob */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#22d3ee]/5 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-[#22d3ee]/10 transition-colors pointer-events-none" />

            {/* Task 3.1: Textarea with icon + label */}
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3.5 rounded-xl bg-[#22d3ee]/10 text-[#22d3ee] border border-[#22d3ee]/20 shrink-0">
                <span className="material-symbols-outlined">edit_note</span>
              </div>
              <div className="flex-1">
                <label
                  htmlFor="symptom-input"
                  className="block text-xs font-bold text-[#22d3ee] uppercase tracking-widest mb-3"
                >
                  Medical Symptoms
                </label>
                {/* Task 3.1: Textarea bound to symptomsText */}
                <textarea
                  id="symptom-input"
                  className="w-full bg-transparent border-none focus:ring-0 text-lg font-medium text-white placeholder:text-[#334155] resize-none min-h-[140px] outline-none"
                  placeholder="e.g. Sharp pain in lower back after lifting heavy furniture..."
                  value={symptomsText}
                  onChange={(e) => setSymptomsText(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Task 3.1: Quick-select chips */}
            <div className="pt-5 border-t border-white/10">
              <p className="text-[11px] font-bold text-[#475569] uppercase tracking-[0.15em] mb-4">
                Quick Select
              </p>
              <div className="flex flex-wrap gap-2.5">
                {QUICK_CHIPS.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => handleChipClick(chip)}
                    disabled={isLoading}
                    className="px-5 py-2.5 rounded-xl bg-[#111b33] text-[#94a3b8] hover:bg-[#22d3ee]/20 hover:text-[#22d3ee] border border-white/10 transition-all text-sm font-semibold active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Parameters Grid — UI-only, not wired to API */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Duration */}
            <div className="bg-[#0b1429] border border-white/10 p-6 rounded-2xl">
              <div className="flex items-center gap-3 mb-5 text-[#22d3ee]">
                <span className="material-symbols-outlined text-xl">schedule</span>
                <span className="text-xs font-bold uppercase tracking-widest">Duration</span>
              </div>
              <div className="relative">
                <select
                  className="w-full bg-[#111b33] border border-white/10 rounded-xl text-white font-medium focus:ring-2 focus:ring-[#22d3ee]/20 focus:border-[#22d3ee]/40 py-4 px-5 appearance-none cursor-pointer"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  disabled={isLoading}
                >
                  <option>Started today</option>
                  <option>2-3 days ago</option>
                  <option>About a week</option>
                  <option>More than 2 weeks</option>
                </select>
                <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-[#94a3b8]">
                  <span className="material-symbols-outlined">expand_more</span>
                </div>
              </div>
            </div>

            {/* Severity */}
            <div className="bg-[#0b1429] border border-white/10 p-6 rounded-2xl">
              <div className="flex items-center gap-3 mb-5 text-[#f472b6]">
                <span className="material-symbols-outlined text-xl">bar_chart</span>
                <span className="text-xs font-bold uppercase tracking-widest">Severity</span>
              </div>
              <div className="flex gap-2">
                {['Mild', 'Moderate', 'Severe'].map((level) => (
                  <button
                    key={level}
                    type="button"
                    disabled={isLoading}
                    onClick={() => setSeverity(level)}
                    className={`flex-1 py-3.5 rounded-xl text-sm font-bold transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed ${
                      severity === level
                        ? 'bg-[#f472b6]/10 border border-[#f472b6]/30 text-[#f472b6]'
                        : 'bg-[#111b33] border border-white/10 text-[#94a3b8] hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar — 4 cols */}
        <div className="lg:col-span-4 space-y-6">

          {/* Trust Badge Card */}
          <div className="bg-gradient-to-br from-[#0f172a] to-[#020617] border border-[#22d3ee]/20 p-6 rounded-2xl relative overflow-hidden">
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <span
                  className="material-symbols-outlined text-[#22d3ee]"
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  verified_user
                </span>
                <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#22d3ee]/80">
                  Clinical Security
                </span>
              </div>
              <p className="text-sm leading-relaxed text-[#94a3b8] mb-6">
                Your data is encrypted end-to-end and analyzed against latest{' '}
                <span className="text-white font-semibold">WHO &amp; CDC</span> protocols.
              </p>
              <div className="flex items-center gap-3">
                <div className="flex -space-x-2.5">
                  <div className="w-9 h-9 rounded-full border-2 border-slate-900 bg-[#0b1429] flex items-center justify-center">
                    <span className="material-symbols-outlined text-[#22d3ee] text-base">person</span>
                  </div>
                  <div className="w-9 h-9 rounded-full border-2 border-slate-900 bg-[#0b1429] flex items-center justify-center">
                    <span className="material-symbols-outlined text-[#22d3ee] text-base">person</span>
                  </div>
                  <div className="w-9 h-9 rounded-full border-2 border-slate-900 bg-[#0b1429] flex items-center justify-center text-[10px] font-bold text-[#22d3ee]">
                    +12
                  </div>
                </div>
                <span className="text-[11px] font-medium text-[#475569] uppercase tracking-wider">
                  Expert Verified
                </span>
              </div>
            </div>
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#22d3ee]/10 rounded-full -mr-16 -mt-16 blur-3xl pointer-events-none" />
          </div>

          {/* Tips Card */}
          <div className="bg-[#0b1429]/50 border border-white/5 p-6 rounded-2xl">
            <h3 className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#475569] mb-6">
              Optimizing Insights
            </h3>
            <ul className="space-y-5">
              {[
                'Be specific about where exactly pain is felt.',
                'Mention triggers like activities or food.',
                'Include your known pre-existing conditions.',
              ].map((tip) => (
                <li key={tip} className="flex gap-4 items-start group">
                  <div className="mt-0.5 p-1 rounded bg-[#22d3ee]/10 text-[#22d3ee] transition-colors group-hover:bg-[#22d3ee]/20 shrink-0">
                    <span className="material-symbols-outlined text-lg">check_circle</span>
                  </div>
                  <p className="text-[13px] text-[#94a3b8] leading-snug group-hover:text-[#e2e8f0] transition-colors">
                    {tip}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Action Section */}
      <div className="mt-12 flex flex-col items-center">

        {/* Task 3.2: Loading message */}
        {isLoading && (
          <p className="text-[#22d3ee] text-sm font-medium mb-4 animate-pulse">
            Analyzing symptoms with AI…
          </p>
        )}

        {/* Task 3.2: Inline error message */}
        {error && (
          <p className="text-[#ba1a1a] bg-[#ba1a1a]/10 border border-[#ba1a1a]/30 rounded-xl px-5 py-3 text-sm font-medium mb-4 text-center max-w-md">
            {error}
          </p>
        )}

        {/* Task 3.2: Submit button — disabled when empty or loading */}
        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          className="group relative flex items-center gap-4 px-12 py-5 bg-[#22d3ee] text-[#001946] rounded-2xl font-bold text-lg transition-all duration-300
            shadow-[0_15px_30px_rgba(34,211,238,0.25)]
            hover:shadow-[0_20px_40px_rgba(34,211,238,0.35)] hover:-translate-y-1
            active:translate-y-0 active:scale-95
            disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-[0_15px_30px_rgba(34,211,238,0.25)]"
        >
          <span className="tracking-wide">
            {isLoading ? 'Analyzing…' : 'Start AI Analysis'}
          </span>
          <span className="material-symbols-outlined group-hover:translate-x-1.5 transition-transform duration-300">
            arrow_forward
          </span>
          <div className="absolute inset-0 rounded-2xl bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        </button>

        {/* Disclaimer */}
        <div className="mt-10 text-center max-w-2xl">
          <p className="text-[10px] text-[#334155] leading-relaxed uppercase tracking-wider font-medium">
            Important: HealthBridge is for informational utility and not a professional diagnosis. In emergencies, contact 911 or local services immediately.
          </p>
        </div>
      </div>
    </main>
  )
}
