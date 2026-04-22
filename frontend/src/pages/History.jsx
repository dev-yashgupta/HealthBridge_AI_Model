import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { fetchHistory, fetchReports } from '../services/api'

// ── groupEntriesByDate ────────────────────────────────────────────────────────
// Groups an array of SymptomLogEntry objects by their locale date string.
// Returns a Map<string, SymptomLogEntry[]> sorted by date descending (most recent first).
// Requirement 3.3, 3.10: every entry appears in exactly one group; no entries lost or duplicated.
export function groupEntriesByDate(entries) {
  const groups = new Map()

  for (const entry of entries) {
    const dateKey = new Date(entry.logged_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
    if (groups.has(dateKey)) {
      groups.get(dateKey).push(entry)
    } else {
      groups.set(dateKey, [entry])
    }
  }

  // Sort groups by date descending
  const sortedGroups = new Map(
    [...groups.entries()].sort((a, b) => new Date(b[0]) - new Date(a[0]))
  )

  return sortedGroups
}

// ── TimelineGroups ────────────────────────────────────────────────────────────
// Renders all date groups as an alternating left/right timeline.
// Requirement 3.3, 3.8, 8.1–8.4
function TimelineGroups({ entries }) {
  const grouped = groupEntriesByDate(entries)
  let globalIndex = 0 // tracks alternating left/right position across all groups

  return (
    <div className="space-y-10">
      {[...grouped.entries()].map(([dateLabel, groupEntries]) => (
        <div key={dateLabel}>
          {/* Date section heading */}
          <div className="flex items-center gap-4 mb-6">
            <span className="text-[#94f0df] font-headline font-bold text-xs tracking-widest uppercase">
              {dateLabel}
            </span>
            <div className="flex-1 h-px bg-[#2b2d35]" />
          </div>

          {/* Entries for this date */}
          <div className="space-y-6">
            {groupEntries.map((entry) => {
              const isRight = globalIndex % 2 === 1
              globalIndex++

              // Requirement 8.1: weight → percentage
              const severityPct = Math.round((entry.weight / 7) * 100)
              // Requirement 8.2 / 8.3: duration display
              const durationLabel =
                entry.duration_days === -1 || entry.duration_days === null
                  ? 'Not specified'
                  : entry.duration_days === 0
                  ? 'Started today'
                  : `${entry.duration_days} day${entry.duration_days !== 1 ? 's' : ''}`
              // Requirement 8.4: human-readable logged_at date
              const loggedDate = new Date(entry.logged_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              })
              // Capitalize symptom name
              const symptomLabel =
                entry.symptom.charAt(0).toUpperCase() + entry.symptom.slice(1)

              return (
                <div key={`${entry.symptom}-${entry.logged_at}`} className="relative pl-8 md:pl-0">
                  {/* Center vertical line */}
                  <div className="hidden md:block absolute left-[50%] top-0 bottom-0 w-[1px] bg-[#2b2d35]" />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                    {/* ── Info side (date + symptom name) ── */}
                    <div
                      className={
                        isRight
                          ? 'md:order-2 md:text-left pl-12'
                          : 'md:text-right pr-12'
                      }
                    >
                      <span className="text-[#94f0df] font-headline font-bold text-sm tracking-widest uppercase">
                        {loggedDate}
                      </span>
                      <h3 className="text-[#dae2ff] text-2xl font-bold mt-1">
                        {symptomLabel}
                      </h3>
                      <p className="text-[#434651] text-sm mt-2">
                        Duration:{' '}
                        <span className="text-[#c4c6d3]">{durationLabel}</span>
                      </p>
                    </div>

                    {/* ── Card side (severity score + progress bar) ── */}
                    <div className={`relative ${isRight ? 'md:order-1' : ''}`}>
                      {/* Neon node dot on center line */}
                      <div
                        className={`hidden md:block absolute ${
                          isRight ? '-right-[43px]' : '-left-[45px]'
                        } top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-[#94f0df] shadow-[0_0_15px_rgba(148,240,223,0.6)] z-10`}
                      />

                      <div className="bg-[#2b2d35] p-6 rounded-2xl border border-[#c4c6d3]/10 hover:border-[#94f0df]/30 transition-all group">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <span className="text-xs font-bold text-[#434651] block mb-1 uppercase tracking-widest">
                              Severity Score
                            </span>
                            <span
                              className="text-3xl font-headline font-extrabold"
                              style={{
                                color: '#94f0df',
                                textShadow: '0 0 8px rgba(148, 240, 223, 0.4)',
                              }}
                            >
                              {severityPct}%
                            </span>
                          </div>
                          <span className="bg-[#103e8f]/30 text-[#8eadff] text-[10px] px-3 py-1 rounded-full font-bold uppercase tracking-widest">
                            Logged
                          </span>
                        </div>

                        {/* Progress bar */}
                        <div className="w-full bg-[#1a1b21] h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-[#94f0df] h-full rounded-full"
                            style={{
                              width: `${severityPct}%`,
                              boxShadow: '0 0 10px rgba(148,240,223,0.4)',
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Loading skeleton: 3 pulsing placeholder cards matching dark glassmorphism style
function HistorySkeleton() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading history">
      {[0, 1, 2].map((i) => (
        <div key={i} className="relative pl-8 md:pl-0 animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            {/* Date + title placeholder */}
            <div className={`${i % 2 === 1 ? 'md:order-2 md:text-left pl-12' : 'md:text-right pr-12'} space-y-3`}>
              <div className="h-3 w-24 bg-[#2b2d35] rounded-full inline-block" />
              <div className="h-6 w-40 bg-[#2b2d35] rounded-lg" />
              <div className="h-3 w-56 bg-[#2b2d35] rounded-full" />
            </div>
            {/* Card placeholder */}
            <div className={`relative ${i % 2 === 1 ? 'md:order-1' : ''}`}>
              {/* Neon node placeholder */}
              <div
                className={`hidden md:block absolute ${i % 2 === 1 ? '-right-[43px]' : '-left-[45px]'} top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-[#2b2d35] z-10`}
              />
              <div className="bg-[#2b2d35] p-6 rounded-2xl border border-[#c4c6d3]/10">
                <div className="flex justify-between items-start mb-4">
                  <div className="space-y-2">
                    <div className="h-2.5 w-24 bg-[#1a1b21] rounded-full" />
                    <div className="h-8 w-16 bg-[#1a1b21] rounded-lg" />
                  </div>
                  <div className="h-5 w-20 bg-[#1a1b21] rounded-full" />
                </div>
                <div className="w-full bg-[#1a1b21] h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-[#3a3d47] h-full rounded-full"
                    style={{ width: `${40 + i * 20}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function History() {
  const [entries, setEntries] = useState([])
  const [reports, setReports] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('symptoms') // 'symptoms' | 'reports'

  const loadHistory = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [data, reps] = await Promise.all([
        fetchHistory('GUEST'),
        fetchReports('GUEST').catch(() => []),
      ])
      setEntries(data)
      setReports(reps)
    } catch {
      setError('Could not load your history. Please check your connection.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  return (
    <main className="pt-24 pb-32 px-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-10">
        <h1 className="font-headline text-5xl font-extrabold text-[#dae2ff] mb-2 tracking-tighter">History</h1>
        <p className="text-[#434651] max-w-md">Your clinical longitudinal record. Monitor past assessments and health transitions with precision.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8">
        <button
          onClick={() => setActiveTab('symptoms')}
          className={`px-6 py-2.5 rounded-xl font-bold text-sm transition-all ${activeTab === 'symptoms' ? 'bg-[#94f0df] text-[#001946]' : 'bg-[#2b2d35] text-[#94a3b8] hover:bg-[#32353f]'}`}
          type="button"
        >
          <span className="material-symbols-outlined text-sm align-middle mr-1">monitor_heart</span>
          Symptoms
        </button>
        <button
          onClick={() => setActiveTab('reports')}
          className={`px-6 py-2.5 rounded-xl font-bold text-sm transition-all ${activeTab === 'reports' ? 'bg-[#94f0df] text-[#001946]' : 'bg-[#2b2d35] text-[#94a3b8] hover:bg-[#32353f]'}`}
          type="button"
        >
          <span className="material-symbols-outlined text-sm align-middle mr-1">description</span>
          Reports {reports.length > 0 && <span className="ml-1 bg-[#103e8f] text-[#8eadff] text-[10px] px-2 py-0.5 rounded-full">{reports.length}</span>}
        </button>
      </div>

      {/* Search row — symptoms tab only */}
      {activeTab === 'symptoms' && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="md:col-span-3 relative group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-[#434651] group-focus-within:text-[#94f0df]">
              <span className="material-symbols-outlined">search</span>
            </div>
            <input
              className="w-full bg-[#2b2d35] border-none rounded-xl py-4 pl-12 pr-4 text-[#dae2ff] placeholder-[#434651] focus:ring-2 focus:ring-[#94f0df]/50 transition-all outline-none"
              placeholder="Search symptoms..."
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              aria-label="Search history"
            />
          </div>
          <div className="md:col-span-1">
            <button className="w-full h-full bg-[#2b2d35] hover:bg-[#32353f] text-[#dae2ff] rounded-xl flex items-center justify-center gap-2 transition-all active:scale-95 py-4" type="button">
              <span className="material-symbols-outlined">tune</span>
              <span className="font-medium">Filter</span>
            </button>
          </div>
        </div>
      )}
      {/* Loading */}
      {isLoading && <HistorySkeleton />}

      {/* Error */}
      {!isLoading && error && (
        <div className="bg-[#2b2d35] border border-[#ba1a1a]/30 rounded-2xl p-8 text-center">
          <span className="material-symbols-outlined text-[#ba1a1a] text-4xl mb-4 block">error_outline</span>
          <p className="text-[#dae2ff] font-semibold mb-2">{error}</p>
          <button onClick={loadHistory} className="mt-4 px-6 py-2.5 bg-[#94f0df] text-[#001946] rounded-xl font-bold text-sm hover:brightness-110 active:scale-95 transition-all" type="button">Retry</button>
        </div>
      )}

      {/* ── Symptoms Tab ─────────────────────────────────────────────── */}
      {!isLoading && !error && activeTab === 'symptoms' && (() => {
        const filteredEntries = entries.filter(e =>
          e.symptom.toLowerCase().includes(searchTerm.toLowerCase())
        )
        return (
          <>
            {filteredEntries.length > 0 && <TimelineGroups entries={filteredEntries} />}
            {filteredEntries.length === 0 && (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <span className="material-symbols-outlined text-6xl mb-4" style={{ color: '#434651' }}>history</span>
                <p className="text-[#434651] text-lg font-semibold">No history yet.</p>
                {searchTerm && <p className="text-[#434651] text-sm mt-2">No entries match &ldquo;{searchTerm}&rdquo;.</p>}
              </div>
            )}
          </>
        )
      })()}

      {/* ── Reports Tab ──────────────────────────────────────────────── */}
      {!isLoading && !error && activeTab === 'reports' && (
        <div className="space-y-4">
          {reports.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <span className="material-symbols-outlined text-6xl mb-4" style={{ color: '#434651' }}>description</span>
              <p className="text-[#434651] text-lg font-semibold">No reports yet.</p>
              <p className="text-[#434651] text-sm mt-2">Run a symptom check to generate your first report.</p>
            </div>
          ) : (
            reports.map((rep) => {
              const urgencyColor = rep.urgency === 'HIGH' ? '#ba1a1a' : rep.urgency === 'MEDIUM' ? '#ffb694' : '#94f0df'
              const urgencyBg = rep.urgency === 'HIGH' ? 'bg-[#ba1a1a]/10 border-[#ba1a1a]/30 text-[#ba1a1a]' : rep.urgency === 'MEDIUM' ? 'bg-[#ffb694]/10 border-[#ffb694]/30 text-[#ffb694]' : 'bg-[#94f0df]/10 border-[#94f0df]/30 text-[#94f0df]'
              const score = Math.round(rep.top_score ?? 0)
              const dateStr = rep.created_at ? new Date(rep.created_at).toLocaleString('en-US', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''

              // Parse sections from report text
              const sections = {}
              if (rep.report_text) {
                let cur = null, buf = []
                for (const line of rep.report_text.split('\n')) {
                  if (line.startsWith('-- ') && line.includes(' -')) {
                    if (cur) sections[cur] = buf.join('\n').trim()
                    cur = line.replace(/^-- /, '').replace(/ -+$/, '').trim()
                    buf = []
                  } else if (!line.startsWith('===') && cur) {
                    buf.push(line)
                  }
                }
                if (cur) sections[cur] = buf.join('\n').trim()
              }

              const symptoms = (sections['SYMPTOMS DETECTED'] || '')
                .split('\n').filter(l => l.trim().startsWith('*'))
                .map(l => l.replace(/^\s*\*\s*/, '').replace(/\[.*?\]/, '').trim())
                .filter(Boolean)

              const tests = (sections['RECOMMENDED TESTS'] || '').replace(/^.*?->\s*/m, '').trim()
              const advice = (sections['DOCTOR ADVICE'] || '').replace(/^\s*\[!\]\s*/m, '').trim()

              return (
                <details key={rep.id} className="bg-[#1a1b21] rounded-2xl border border-[#c4c6d3]/10 overflow-hidden group">
                  {/* Summary row */}
                  <summary className="flex items-center justify-between p-5 cursor-pointer hover:bg-[#2b2d35] transition-all list-none">
                    <div className="flex items-center gap-4 min-w-0">
                      <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: urgencyColor, boxShadow: `0 0 8px ${urgencyColor}` }} />
                      <div className="min-w-0">
                        <p className="text-[#dae2ff] font-bold text-sm truncate">{rep.top_disease ?? 'Unknown'}</p>
                        <p className="text-[#434651] text-xs mt-0.5">{dateStr}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0 ml-4">
                      <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border uppercase tracking-wider ${urgencyBg}`}>{rep.urgency}</span>
                      <span className="text-[#94f0df] font-bold text-sm">{score}%</span>
                      <span className="material-symbols-outlined text-[#434651] group-open:rotate-180 transition-transform duration-200">expand_more</span>
                    </div>
                  </summary>

                  {/* Expanded content */}
                  <div className="border-t border-[#c4c6d3]/10 p-5 space-y-4">
                    {/* Confidence bar */}
                    <div>
                      <div className="flex justify-between text-xs text-[#434651] mb-1.5">
                        <span>Confidence</span><span className="text-[#94f0df] font-bold">{score}%</span>
                      </div>
                      <div className="w-full bg-[#2b2d35] h-1.5 rounded-full overflow-hidden">
                        <div className="h-full rounded-full bg-[#94f0df]" style={{ width: `${score}%`, boxShadow: '0 0 8px rgba(148,240,223,0.4)' }} />
                      </div>
                    </div>

                    {/* Symptoms chips */}
                    {symptoms.length > 0 && (
                      <div>
                        <p className="text-[10px] font-bold text-[#434651] uppercase tracking-widest mb-2">Detected Symptoms</p>
                        <div className="flex flex-wrap gap-2">
                          {symptoms.map(s => (
                            <span key={s} className="px-3 py-1 bg-[#94f0df]/10 border border-[#94f0df]/20 text-[#94f0df] text-xs font-medium rounded-full">{s}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tests */}
                    {tests && (
                      <div className="bg-[#2b2d35] rounded-xl p-4">
                        <p className="text-[10px] font-bold text-[#434651] uppercase tracking-widest mb-1.5 flex items-center gap-1">
                          <span className="material-symbols-outlined text-xs">biotech</span> Recommended Tests
                        </p>
                        <p className="text-[#c4c6d3] text-xs leading-relaxed">{tests}</p>
                      </div>
                    )}

                    {/* Doctor advice */}
                    {advice && (
                      <div className="bg-[#2b2d35] rounded-xl p-4">
                        <p className="text-[10px] font-bold text-[#434651] uppercase tracking-widest mb-1.5 flex items-center gap-1">
                          <span className="material-symbols-outlined text-xs">medical_information</span> Doctor Advice
                        </p>
                        <p className="text-[#c4c6d3] text-xs leading-relaxed">{advice}</p>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-3 pt-1">
                      <button
                        onClick={() => {
                          const w = window.open('', '_blank')
                          w.document.write(`<html><head><title>HealthBridge Report</title><style>body{font-family:monospace;font-size:13px;padding:32px;color:#111;background:#fff}pre{white-space:pre-wrap;line-height:1.6}</style></head><body><pre>${rep.report_text ?? ''}</pre></body></html>`)
                          w.document.close(); w.focus(); w.print()
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-[#2b2d35] border border-[#94f0df]/20 text-[#94f0df] rounded-xl text-xs font-bold hover:bg-[#94f0df]/10 transition-all"
                        type="button"
                      >
                        <span className="material-symbols-outlined text-sm">print</span>
                        Print
                      </button>
                      <details className="flex-1">
                        <summary className="flex items-center gap-1 px-4 py-2 bg-[#2b2d35] border border-[#c4c6d3]/10 text-[#434651] rounded-xl text-xs font-bold cursor-pointer hover:bg-[#32353f] transition-all list-none">
                          <span className="material-symbols-outlined text-sm">article</span>
                          Full Report
                        </summary>
                        <pre className="mt-3 text-slate-400 text-[10px] leading-relaxed whitespace-pre-wrap font-mono max-h-64 overflow-y-auto bg-[#0b1429] rounded-xl p-4">{rep.report_text}</pre>
                      </details>
                    </div>
                  </div>
                </details>
              )
            })
          )}
        </div>
      )}

      {/* Stats Bento */}
      {!isLoading && !error && entries.length > 0 && activeTab === 'symptoms' && (
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-[#103e8f] to-[#002869] p-8 rounded-3xl col-span-1 md:col-span-2 relative overflow-hidden group">
            <div className="relative z-10">
              <h4 className="text-[#dae2ff] font-bold text-xl mb-4">Symptom Overview</h4>
              <p className="text-[#8eadff] mb-6 max-w-xs">
                You have logged <span className="text-[#dae2ff] font-bold">{entries.length}</span> symptom{entries.length !== 1 ? 's' : ''} across <span className="text-[#dae2ff] font-bold">{groupEntriesByDate(entries).size}</span> session{groupEntriesByDate(entries).size !== 1 ? 's' : ''}.
              </p>
              <Link to="/history/medical" className="inline-block bg-[#94f0df] text-[#001946] px-6 py-3 rounded-xl font-bold text-sm hover:brightness-110 active:scale-95 transition-all">
                View Medical History
              </Link>
            </div>
            <div className="absolute -right-8 -bottom-8 opacity-10 scale-150 rotate-12 transition-transform group-hover:rotate-6 duration-700">
              <span className="material-symbols-outlined text-[200px]">monitoring</span>
            </div>
          </div>
          <div className="bg-[#2b2d35] p-8 rounded-3xl flex flex-col justify-between">
            <span className="material-symbols-outlined text-4xl" style={{ color: '#94f0df', fontVariationSettings: "'FILL' 1" }}>verified</span>
            <div>
              <div className="text-4xl font-headline font-extrabold text-[#dae2ff]">{entries.length}</div>
              <div className="text-[#434651] text-sm font-bold uppercase tracking-widest">Total Entries</div>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
