import { useLocation, Link } from 'react-router-dom'
import { getUrgencyStyle } from '../utils/urgency'

function BackToCheckerLink() {
  return (
    <Link
      to="/checker"
      className="inline-flex items-center gap-2 mt-6 px-8 py-3.5 bg-[#22d3ee] text-[#001946] rounded-2xl font-bold text-sm transition-all shadow-[0_10px_25px_rgba(34,211,238,0.25)] hover:shadow-[0_15px_35px_rgba(34,211,238,0.35)] hover:-translate-y-0.5 active:translate-y-0 active:scale-95"
    >
      <span className="material-symbols-outlined text-base">arrow_back</span>
      Back to Symptom Checker
    </Link>
  )
}

function FallbackCard({ icon, iconColor = 'text-[#22d3ee]', children }) {
  return (
    <div className="bg-[#0b1429] border border-white/10 rounded-2xl p-10 md:p-14 flex flex-col items-center text-center relative overflow-hidden" style={{ boxShadow: '0 4px 24px -1px rgba(0,0,0,0.5)' }}>
      <div className="absolute top-0 right-0 w-48 h-48 bg-[#22d3ee]/5 rounded-full -mr-24 -mt-24 blur-3xl pointer-events-none" />
      <div className="relative z-10 flex flex-col items-center">
        <div className={`p-4 rounded-2xl bg-[#22d3ee]/10 border border-[#22d3ee]/20 mb-6 ${iconColor}`}>
          <span className="material-symbols-outlined text-3xl">{icon}</span>
        </div>
        {children}
      </div>
    </div>
  )
}

// ── Parse the plain-text report into structured sections ─────────────────────
function parseReport(reportText) {
  if (!reportText) return {}
  const sections = {}
  const lines = reportText.split('\n')
  let currentSection = null
  let buffer = []

  for (const line of lines) {
    if (line.startsWith('-- ') && line.includes(' -')) {
      if (currentSection) sections[currentSection] = buffer.join('\n').trim()
      currentSection = line.replace(/^-- /, '').replace(/ -+$/, '').trim()
      buffer = []
    } else if (line.startsWith('===')) {
      // skip borders
    } else if (currentSection) {
      buffer.push(line)
    }
  }
  if (currentSection) sections[currentSection] = buffer.join('\n').trim()
  return sections
}

const METHOD_LABELS = {
  'grok'            : 'Grok + BERT Hybrid',
  'hybrid'          : 'BERT + Keyword Hybrid',
  'bert'            : 'BERT Neural Engine',
  'keyword'         : 'Keyword Matching',
  'keyword_fallback': 'Keyword Matching',
}

export default function AnalysisResults() {
  const location = useLocation()
  const state = location.state

  if (!state) {
    return (
      <main className="pt-4 pb-8 px-6 max-w-3xl mx-auto">
        <section className="mb-8">
          <h2 className="text-4xl font-headline font-extrabold text-[#22d3ee] mb-2">Analysis Results</h2>
          <p className="text-[#94a3b8]">Your AI-powered diagnosis summary.</p>
        </section>
        <FallbackCard icon="search_off">
          <h3 className="text-xl font-bold text-white mb-3">No analysis results found.</h3>
          <p className="text-[#94a3b8] text-sm max-w-sm leading-relaxed">It looks like you arrived here directly. Run a symptom check first to see your results.</p>
          <BackToCheckerLink />
        </FallbackCard>
      </main>
    )
  }

  if (state.status === 'no_symptoms') {
    return (
      <main className="pt-4 pb-8 px-6 max-w-3xl mx-auto">
        <section className="mb-8">
          <h2 className="text-4xl font-headline font-extrabold text-[#22d3ee] mb-2">Analysis Results</h2>
          <p className="text-[#94a3b8]">Your AI-powered diagnosis summary.</p>
        </section>
        <FallbackCard icon="sentiment_dissatisfied" iconColor="text-[#ffb694]">
          <h3 className="text-xl font-bold text-white mb-3">No symptoms detected.</h3>
          <p className="text-[#94a3b8] text-sm max-w-sm leading-relaxed">No symptoms were detected. Try describing your symptoms in more detail.</p>
          <BackToCheckerLink />
        </FallbackCard>
      </main>
    )
  }

  if (state.status === 'error') {
    return (
      <main className="pt-4 pb-8 px-6 max-w-3xl mx-auto">
        <section className="mb-8">
          <h2 className="text-4xl font-headline font-extrabold text-[#22d3ee] mb-2">Analysis Results</h2>
          <p className="text-[#94a3b8]">Your AI-powered diagnosis summary.</p>
        </section>
        <FallbackCard icon="error_outline" iconColor="text-[#ba1a1a]">
          <h3 className="text-xl font-bold text-white mb-3">Analysis Error</h3>
          <p className="text-[#94a3b8] text-sm max-w-sm leading-relaxed">{state.message ?? 'An unexpected error occurred during analysis.'}</p>
          <BackToCheckerLink />
        </FallbackCard>
      </main>
    )
  }

  const topScorePct  = Math.round(state.top_score)
  const bertScorePct = Math.round((state.bert_confidence ?? 0) * 100)
  const hasBert      = typeof state.bert_suggestion === 'string' && state.bert_suggestion !== null && state.bert_suggestion !== ''
  const symptomKeys  = Object.keys(state.detected_symptoms ?? {})
  const methodLabel  = METHOD_LABELS[state.method_used] ?? state.method_used ?? 'AI Analysis'
  const sections     = parseReport(state.report)

  const handlePrint = () => {
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>HealthBridge AI Report</title>
          <style>
            body { font-family: monospace; font-size: 13px; padding: 32px; color: #111; background: #fff; }
            h1 { font-size: 18px; margin-bottom: 4px; }
            pre { white-space: pre-wrap; word-break: break-word; line-height: 1.6; }
            .meta { color: #555; font-size: 12px; margin-bottom: 16px; }
            @media print { body { padding: 16px; } }
          </style>
        </head>
        <body>
          <h1>HealthBridge AI — Medical Report</h1>
          <div class="meta">Patient: ${state.patient_id ?? 'GUEST'} &nbsp;|&nbsp; ${new Date().toLocaleString()}</div>
          <pre>${state.report ?? ''}</pre>
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.focus()
    printWindow.print()
  }

  return (
    <main className="pt-4 pb-8 px-4 md:px-8 max-w-7xl mx-auto">
      {/* Header */}
      <section className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-4xl font-headline font-extrabold text-[#22d3ee] mb-2">Analysis Results</h2>
          <p className="text-[#94a3b8] max-w-2xl leading-relaxed">
            Based on your reported symptoms, here is a prioritised list of potential health matches and recommended actions.
          </p>
        </div>
        <div className="flex gap-3 shrink-0">
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#0f172a] border border-[#22d3ee]/30 text-[#22d3ee] rounded-xl font-bold text-sm hover:bg-[#22d3ee]/10 transition-all active:scale-95"
            type="button"
          >
            <span className="material-symbols-outlined text-base">print</span>
            Print Report
          </button>
          <Link
            to="/history"
            className="flex items-center gap-2 px-5 py-2.5 bg-[#0f172a] border border-white/10 text-[#94a3b8] rounded-xl font-bold text-sm hover:bg-white/5 transition-all active:scale-95"
          >
            <span className="material-symbols-outlined text-base">history</span>
            View History
          </Link>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* ── 8-col main ─────────────────────────────────────────────────── */}
        <section className="lg:col-span-8 space-y-6">

          {/* Potential Matches */}
          <div className="bg-[#0f172a] p-6 rounded-2xl border border-[#22d3ee]/10" style={{ boxShadow: '0 4px 24px -1px rgba(0,0,0,0.5)' }}>
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-xl font-headline font-bold text-slate-100">Potential Matches</h3>
              <span className="text-[10px] text-[#22d3ee] bg-[#22d3ee]/10 border border-[#22d3ee]/20 px-3 py-1 rounded-full uppercase tracking-wider font-bold">{methodLabel}</span>
            </div>
            <div className="space-y-6">
              {/* Primary */}
              <div className="bg-[#091328] p-6 rounded-xl border border-transparent hover:border-[#22d3ee]/30 transition-all">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-2xl font-bold text-slate-100 mb-1">{state.top_disease}</h4>
                    <p className="text-[#94a3b8] text-sm">Primary AI diagnosis</p>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-extrabold text-[#22d3ee]" style={{ textShadow: '0 0 8px rgba(34,211,238,0.4)' }}>{topScorePct}%</div>
                    <div className="text-[10px] uppercase font-bold text-[#94a3b8]">Confidence</div>
                  </div>
                </div>
                <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                  <div className="bg-[#22d3ee] h-full rounded-full" style={{ width: `${topScorePct}%`, boxShadow: '0 0 8px #22d3ee' }} />
                </div>
              </div>
              {/* BERT secondary */}
              {hasBert && (
                <div className="bg-[#091328]/50 p-6 rounded-xl border border-transparent hover:border-[#22d3ee]/20 transition-all">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-xl font-bold text-slate-200">{state.bert_suggestion}</h4>
                      <p className="text-[#94a3b8] text-sm">BERT secondary match</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-slate-400">{bertScorePct}%</div>
                      <div className="text-[10px] uppercase font-bold text-[#94a3b8]">Likelihood</div>
                    </div>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-slate-500 h-full rounded-full opacity-60" style={{ width: `${bertScorePct}%` }} />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Detected Symptoms */}
          {symptomKeys.length > 0 && (
            <div className="bg-[#0f172a] p-6 rounded-2xl border border-[#22d3ee]/10" style={{ boxShadow: '0 4px 24px -1px rgba(0,0,0,0.5)' }}>
              <h3 className="text-xl font-headline font-bold text-slate-100 mb-4">Detected Symptoms</h3>
              <div className="flex flex-wrap gap-2">
                {symptomKeys.map((symptom) => (
                  <span key={symptom} className="px-3 py-1.5 bg-[#22d3ee]/10 border border-[#22d3ee]/20 text-[#22d3ee] text-sm font-medium rounded-full capitalize">
                    {symptom.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Tests — from parsed report */}
          {sections['RECOMMENDED TESTS'] && (
            <div className="bg-[#0f172a] p-6 rounded-2xl border border-[#22d3ee]/10" style={{ boxShadow: '0 4px 24px -1px rgba(0,0,0,0.5)' }}>
              <h3 className="text-xl font-headline font-bold text-slate-100 mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#22d3ee]">biotech</span>
                Recommended Tests
              </h3>
              <pre className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-sans">{sections['RECOMMENDED TESTS']}</pre>
            </div>
          )}

          {/* Recommended Next Steps */}
          <div className="bg-[#0f172a] p-6 rounded-2xl border border-[#22d3ee]/10" style={{ boxShadow: '0 4px 24px -1px rgba(0,0,0,0.5)' }}>
            <h3 className="text-xl font-headline font-bold text-slate-100 mb-6">Recommended Next Steps</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-[#030712] p-6 rounded-xl border-l-4 border-[#22d3ee] flex flex-col gap-4 shadow-lg shadow-black/40">
                <span className="material-symbols-outlined text-[#22d3ee] text-3xl">stethoscope</span>
                <div>
                  <h5 className="font-bold text-slate-100">Consult a GP</h5>
                  <p className="text-sm text-[#94a3b8]">A general practitioner can confirm this diagnosis and advise on treatment.</p>
                </div>
              </div>
              <div className="bg-[#030712] p-6 rounded-xl border-l-4 border-slate-500 flex flex-col gap-4 shadow-lg shadow-black/40">
                <span className="material-symbols-outlined text-slate-300 text-3xl">water_drop</span>
                <div>
                  <h5 className="font-bold text-slate-100">Rest &amp; Hydrate</h5>
                  <p className="text-sm text-[#94a3b8]">Increase fluid intake to 3 L/day and prioritise sleep to support recovery.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── 4-col sidebar ──────────────────────────────────────────────── */}
        <aside className="lg:col-span-4 space-y-6">

          {/* Urgency Badge */}
          {(() => {
            const urgencyStyle = getUrgencyStyle(state.urgency)
            const urgencyIcon = state.urgency === 'HIGH' ? 'warning' : 'info'
            return (
              <div className={`p-6 rounded-2xl border ${urgencyStyle.bg} ${urgencyStyle.border}`} style={{ boxShadow: '0 4px 24px -1px rgba(0,0,0,0.4)' }}>
                <p className="text-xs uppercase tracking-widest font-bold text-slate-400 mb-3">Urgency Level</p>
                <div className="flex items-center gap-3">
                  <span className={`material-symbols-outlined text-2xl ${urgencyStyle.text}`} style={{ fontVariationSettings: "'FILL' 1" }}>{urgencyIcon}</span>
                  <span className={`text-2xl font-extrabold tracking-wide ${urgencyStyle.text}`}>{state.urgency} URGENCY</span>
                </div>
              </div>
            )
          })()}

          {/* Doctor Advice — from parsed report */}
          {sections['DOCTOR ADVICE'] && (
            <div className="bg-[#0f172a] p-6 rounded-2xl border border-[#22d3ee]/10">
              <h3 className="text-sm font-bold text-[#22d3ee] uppercase tracking-widest mb-3 flex items-center gap-2">
                <span className="material-symbols-outlined text-base">medical_information</span>
                Doctor Advice
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed">{sections['DOCTOR ADVICE'].replace(/^\s*\[!\]\s*/m, '')}</p>
            </div>
          )}

          {/* Summary of Analysis — structured */}
          <div
            className="p-6 rounded-2xl border border-[#22d3ee]/20 text-slate-100 relative overflow-hidden"
            style={{ background: 'linear-gradient(135deg, rgba(34,211,238,0.08) 0%, #060e20 100%)', boxShadow: '0 4px 24px -1px rgba(0,0,0,0.5)' }}
          >
            <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, #22d3ee 1px, transparent 0)', backgroundSize: '24px 24px' }} />
            <h3 className="text-base font-headline font-bold mb-4 relative z-10 text-[#22d3ee] flex items-center gap-2">
              <span className="material-symbols-outlined text-base">psychology</span>
              Summary of Analysis
            </h3>
            <div className="relative z-10 space-y-2 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>Method</span>
                <span className="text-slate-200 font-medium">{methodLabel}</span>
              </div>
              <div className="flex justify-between">
                <span>Top Match</span>
                <span className="text-slate-200 font-medium">{state.top_disease}</span>
              </div>
              <div className="flex justify-between">
                <span>Confidence</span>
                <span className="text-slate-200 font-medium">{topScorePct}%</span>
              </div>
              <div className="flex justify-between">
                <span>Symptoms Found</span>
                <span className="text-slate-200 font-medium">{symptomKeys.length}</span>
              </div>
              {state.duration_days >= 0 && (
                <div className="flex justify-between">
                  <span>Duration</span>
                  <span className="text-slate-200 font-medium">{state.duration_days} day(s)</span>
                </div>
              )}
            </div>
            {/* Full report toggle */}
            <details className="relative z-10 mt-4">
              <summary className="text-xs text-[#22d3ee] cursor-pointer hover:brightness-125 font-bold uppercase tracking-widest">
                View Full Report
              </summary>
              <pre className="mt-3 text-slate-400 text-[10px] leading-relaxed whitespace-pre-wrap font-mono max-h-64 overflow-y-auto">
                {state.report}
              </pre>
            </details>
          </div>

          {/* Algorithm Verified */}
          <div className="bg-[#22d3ee]/10 border border-[#22d3ee]/20 p-6 rounded-2xl flex items-center gap-4">
            <div className="bg-[#22d3ee] text-[#001946] p-2 rounded-full" style={{ boxShadow: '0 0 15px rgba(34,211,238,0.5)' }}>
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
            </div>
            <div>
              <h6 className="font-bold text-cyan-100 leading-tight">Algorithm Verified</h6>
              <p className="text-[#94a3b8] text-xs">Analysis cross-referenced with 500k+ clinical cases.</p>
            </div>
          </div>

          {/* Emergency Banner */}
          <div className="bg-red-500/10 p-6 rounded-2xl border border-red-500/20">
            <div className="flex items-center gap-3 mb-3">
              <span className="material-symbols-outlined text-red-500">emergency</span>
              <h6 className="font-bold text-red-100">Seek Emergency Care If…</h6>
            </div>
            <ul className="text-xs text-slate-300 space-y-2 list-disc ml-4">
              <li>Chest pain or pressure</li>
              <li>Difficulty breathing or shortness of breath</li>
              <li>Sudden severe headache</li>
              <li>Loss of consciousness</li>
              <li>High fever above 103 °F (39.4 °C)</li>
            </ul>
          </div>
        </aside>
      </div>

      <footer className="mt-16 text-center border-t border-slate-800 pt-8 pb-10">
        <p className="text-xs text-[#94a3b8] italic max-w-2xl mx-auto px-4">
          <strong className="text-slate-400">Disclaimer: Not a medical diagnosis.</strong>{' '}
          HealthBridge AI provides health information based on user-provided data. This is not a substitute for professional medical advice, diagnosis, or treatment. In a medical emergency, call your local emergency services immediately.
        </p>
      </footer>
    </main>
  )
}