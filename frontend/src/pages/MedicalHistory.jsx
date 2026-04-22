import { Link } from 'react-router-dom'

// ── Hardcoded medical profile data (Phase 1 — no backend endpoint yet) ────────
// Requirements 4.1–4.4
const MEDICAL_PROFILE = {
  conditions: ['Type 2 Diabetes', 'Hypertension', 'Asthma'],
  medications: [
    { name: 'Metformin',     dosage: '500mg',   frequency: 'Twice daily',  status: 'Active'   },
    { name: 'Lisinopril',    dosage: '10mg',    frequency: 'Once daily',   status: 'Active'   },
    { name: 'Salbutamol',    dosage: '100mcg',  frequency: 'As needed',    status: 'Active'   },
    { name: 'Atorvastatin',  dosage: '20mg',    frequency: 'Once daily',   status: 'Inactive' },
  ],
  allergies: [
    { name: 'Penicillin', severity: 'Severe'   },
    { name: 'Shellfish',  severity: 'Moderate' },
    { name: 'Pollen',     severity: 'Mild'     },
  ],
  surgeries: [
    { date: 'Mar 2019', procedure: 'Appendectomy',      facility: 'City General Hospital', doctor: 'Dr. Sarah Chen'  },
    { date: 'Nov 2015', procedure: 'Knee Arthroscopy',  facility: 'Orthopedic Clinic',     doctor: 'Dr. James Patel' },
  ],
}

// ── Severity styling map ──────────────────────────────────────────────────────
// Requirement 4.3: Severe → red (#ba1a1a), Moderate → amber (#ffb694), Mild → teal (#97f3e2)
const SEVERITY_STYLES = {
  Severe:   {
    bg:     'bg-[#ba1a1a]/10',
    border: 'border-[#ba1a1a]/30',
    text:   'text-[#ba1a1a]',
    label:  'text-[#ba1a1a]',
  },
  Moderate: {
    bg:     'bg-[#ffb694]/10',
    border: 'border-[#ffb694]/30',
    text:   'text-[#ffb694]',
    label:  'text-[#ffb694]',
  },
  Mild: {
    bg:     'bg-[#97f3e2]/10',
    border: 'border-[#97f3e2]/30',
    text:   'text-[#97f3e2]',
    label:  'text-[#97f3e2]',
  },
}

// ── MedicalHistory page ───────────────────────────────────────────────────────
export default function MedicalHistory() {
  return (
    <main className="pt-24 pb-32 px-6 max-w-5xl mx-auto">

      {/* ── Back link (Requirement 3.9 / navigation) ─────────────────────── */}
      <div className="mb-6">
        <Link
          to="/history"
          className="inline-flex items-center gap-1.5 text-[#94f0df] text-sm font-semibold hover:brightness-125 transition-all"
        >
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          Back to History
        </Link>
      </div>

      {/* ── Page header ──────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
        <div>
          <nav className="flex mb-2 gap-2 text-xs font-semibold uppercase tracking-wider text-[#94f0df]/70">
            <span>History</span>
            <span className="text-[#434651]">/</span>
            <span className="text-[#94f0df]">Medical History</span>
          </nav>
          <h1 className="font-headline text-4xl md:text-5xl font-extrabold text-[#dae2ff] tracking-tight mb-2">
            Medical Background
          </h1>
          <p className="text-[#434651] max-w-2xl text-base leading-relaxed">
            Your chronic conditions, active medications, known allergies, and past surgical procedures.
          </p>
        </div>

        {/* Requirement 4.5: Export Records button — disabled */}
        <button
          disabled
          className="flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm
                     bg-[#2b2d35] text-[#434651] border border-[#434651]/30
                     cursor-not-allowed opacity-50 select-none"
          aria-disabled="true"
          type="button"
        >
          <span className="material-symbols-outlined text-[20px]">download</span>
          Export Records
        </button>
      </div>

      {/* ── Bento grid ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">

        {/* ── Chronic Conditions (Requirement 4.1) ─────────────────────── */}
        <section
          className="md:col-span-8 glass-panel p-8 rounded-2xl relative overflow-hidden border border-[#c4c6d3]/10"
          aria-labelledby="conditions-heading"
        >
          {/* Left accent bar */}
          <div className="absolute top-0 left-0 w-1 h-full bg-[#94f0df] rounded-l-2xl" />

          <div className="flex justify-between items-start mb-8">
            <div>
              <h2
                id="conditions-heading"
                className="text-xl font-bold font-headline text-[#dae2ff] flex items-center gap-3"
              >
                <span className="material-symbols-outlined text-[#94f0df]">vital_signs</span>
                Chronic Conditions
              </h2>
              <p className="text-sm text-[#434651] mt-1.5">
                Actively monitored long-term health conditions.
              </p>
            </div>

            {/* Requirement 4.6: Edit button — non-functional */}
            <button
              className="p-2.5 bg-[#2b2d35] hover:bg-[#32353f] rounded-xl transition-all border border-[#c4c6d3]/10"
              type="button"
              onClick={() => {}}
              aria-label="Edit chronic conditions"
            >
              <span className="material-symbols-outlined text-[#94f0df] text-[20px]">edit</span>
            </button>
          </div>

          {/* Condition chips */}
          <div className="flex flex-wrap gap-3">
            {MEDICAL_PROFILE.conditions.map((condition) => (
              <div
                key={condition}
                className="bg-[#94f0df]/10 px-5 py-2.5 rounded-xl flex items-center gap-3 border border-[#94f0df]/20"
              >
                <span
                  className="w-2 h-2 rounded-full bg-[#94f0df]"
                  style={{ boxShadow: '0 0 8px rgba(148,240,223,0.8)' }}
                />
                <span className="text-[#dae2ff] font-semibold text-sm">{condition}</span>
              </div>
            ))}

            {/* Requirement 4.6: Add button — non-functional */}
            <button
              className="bg-[#2b2d35] px-5 py-2.5 rounded-xl flex items-center gap-2
                         hover:bg-[#32353f] transition-all text-[#434651] text-sm font-semibold
                         border border-[#c4c6d3]/10"
              type="button"
              onClick={() => {}}
              aria-label="Add chronic condition"
            >
              <span className="material-symbols-outlined text-sm">add</span>
              Add Condition
            </button>
          </div>
        </section>

        {/* ── Encrypted Records badge ───────────────────────────────────── */}
        <div className="md:col-span-4 bg-gradient-to-br from-[#103e8f]/40 to-[#1a1b21]/60 p-8 rounded-2xl border border-[#94f0df]/20 flex flex-col justify-between">
          <div className="bg-[#94f0df]/20 w-12 h-12 flex items-center justify-center rounded-xl mb-6">
            <span className="material-symbols-outlined text-[#94f0df]">verified_user</span>
          </div>
          <div>
            <h3 className="text-[#dae2ff] font-bold text-lg mb-2">Encrypted Records</h3>
            <p className="text-[#434651] text-sm leading-relaxed">
              Protected by AES-256 encryption and HIPAA-compliant protocols.
            </p>
          </div>
        </div>

        {/* ── Medications (Requirement 4.2) ─────────────────────────────── */}
        <section
          className="md:col-span-6 glass-panel p-8 rounded-2xl border border-[#c4c6d3]/10"
          aria-labelledby="medications-heading"
        >
          <div className="flex justify-between items-start mb-8">
            <div>
              <h2
                id="medications-heading"
                className="text-xl font-bold font-headline text-[#dae2ff] flex items-center gap-3"
              >
                <span className="material-symbols-outlined text-[#b1c5ff]">pill</span>
                Medications
              </h2>
              <p className="text-sm text-[#434651] mt-1.5">
                Active dosage schedules and intervals.
              </p>
            </div>

            {/* Requirement 4.6: Edit button — non-functional */}
            <button
              className="p-2.5 bg-[#2b2d35] hover:bg-[#32353f] rounded-xl transition-all border border-[#c4c6d3]/10"
              type="button"
              onClick={() => {}}
              aria-label="Edit medications"
            >
              <span className="material-symbols-outlined text-[#b1c5ff] text-[20px]">edit</span>
            </button>
          </div>

          <div className="space-y-4">
            {MEDICAL_PROFILE.medications.map((med) => (
              <div
                key={med.name}
                className="bg-[#1a1b21]/60 p-5 rounded-xl flex justify-between items-center
                           border border-[#c4c6d3]/10 hover:border-[#94f0df]/20 transition-all"
              >
                <div>
                  <p className="font-bold text-[#dae2ff]">{med.name}</p>
                  <p className="text-xs text-[#434651] mt-1">
                    {med.dosage} · {med.frequency}
                  </p>
                </div>

                {/* Active / Inactive badge */}
                {med.status === 'Active' ? (
                  <span className="text-[10px] uppercase tracking-widest font-bold text-[#94f0df] bg-[#94f0df]/10 px-2.5 py-1 rounded-md border border-[#94f0df]/20">
                    Active
                  </span>
                ) : (
                  <span className="text-[10px] uppercase tracking-widest font-bold text-[#434651] bg-[#2b2d35] px-2.5 py-1 rounded-md border border-[#c4c6d3]/10">
                    Inactive
                  </span>
                )}
              </div>
            ))}

            {/* Requirement 4.6: Add button — non-functional */}
            <button
              className="w-full py-4 border border-dashed border-[#434651] rounded-xl
                         text-[#434651] font-bold text-sm
                         hover:border-[#94f0df]/50 hover:text-[#94f0df] transition-all"
              type="button"
              onClick={() => {}}
              aria-label="Add new prescription"
            >
              + Add New Prescription
            </button>
          </div>
        </section>

        {/* ── Allergies (Requirement 4.3) ───────────────────────────────── */}
        <section
          className="md:col-span-6 glass-panel p-8 rounded-2xl border border-[#c4c6d3]/10"
          aria-labelledby="allergies-heading"
        >
          <div className="flex justify-between items-start mb-8">
            <div>
              <h2
                id="allergies-heading"
                className="text-xl font-bold font-headline text-[#dae2ff] flex items-center gap-3"
              >
                <span className="material-symbols-outlined text-[#ba1a1a]">warning</span>
                Allergies
              </h2>
              <p className="text-sm text-[#434651] mt-1.5">
                Critical adverse reactions on record.
              </p>
            </div>

            {/* Requirement 4.6: Edit button — non-functional */}
            <button
              className="p-2.5 bg-[#2b2d35] hover:bg-[#32353f] rounded-xl transition-all border border-[#c4c6d3]/10"
              type="button"
              onClick={() => {}}
              aria-label="Edit allergies"
            >
              <span className="material-symbols-outlined text-[#ba1a1a] text-[20px]">edit</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {MEDICAL_PROFILE.allergies.map((allergy) => {
              const style = SEVERITY_STYLES[allergy.severity] ?? SEVERITY_STYLES.Mild
              return (
                <div
                  key={allergy.name}
                  className={`p-5 rounded-xl border transition-all ${style.bg} ${style.border}`}
                >
                  <p className={`font-bold text-sm ${style.text}`}>{allergy.name}</p>
                  <p className={`text-xs mt-1 uppercase tracking-tighter font-bold ${style.label}`}>
                    {allergy.severity}
                  </p>
                </div>
              )
            })}

            {/* Requirement 4.6: Add button — non-functional */}
            <button
              className="bg-[#2b2d35] border border-[#434651]/50 rounded-xl flex items-center
                         justify-center min-h-[80px] hover:bg-[#32353f] transition-all"
              type="button"
              onClick={() => {}}
              aria-label="Add allergy"
            >
              <span className="material-symbols-outlined text-[#434651]">add_circle</span>
            </button>
          </div>
        </section>

        {/* ── Past Surgeries (Requirement 4.4) ─────────────────────────── */}
        <section
          className="md:col-span-12 glass-panel p-8 rounded-2xl border border-[#c4c6d3]/10"
          aria-labelledby="surgeries-heading"
        >
          <div className="flex justify-between items-start mb-8">
            <div>
              <h2
                id="surgeries-heading"
                className="text-xl font-bold font-headline text-[#dae2ff] flex items-center gap-3"
              >
                <span className="material-symbols-outlined text-[#94f0df]">history_edu</span>
                Past Surgeries
              </h2>
              <p className="text-sm text-[#434651] mt-1.5">
                Verified clinical procedures and interventions.
              </p>
            </div>

            {/* Requirement 4.6: Add button — non-functional */}
            <button
              className="p-2.5 bg-[#94f0df]/10 hover:bg-[#94f0df]/20 rounded-xl transition-all border border-[#94f0df]/20"
              type="button"
              onClick={() => {}}
              aria-label="Add surgery record"
            >
              <span className="material-symbols-outlined text-[#94f0df] text-[20px]">add</span>
            </button>
          </div>

          <div className="space-y-2">
            {MEDICAL_PROFILE.surgeries.map((surgery) => (
              <div
                key={`${surgery.date}-${surgery.procedure}`}
                className="flex items-center gap-6 p-5 hover:bg-[#2b2d35]/60 rounded-2xl
                           transition-all border border-transparent hover:border-[#c4c6d3]/10"
              >
                {/* Date */}
                <div className="text-[#94f0df] font-bold w-24 text-sm font-headline uppercase tracking-wider shrink-0">
                  {surgery.date}
                </div>

                {/* Procedure + facility + doctor */}
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-[#dae2ff]">{surgery.procedure}</p>
                  <p className="text-xs text-[#434651] mt-1">
                    {surgery.facility} · {surgery.doctor}
                  </p>
                </div>

                {/* Chevron (decorative) */}
                <span className="material-symbols-outlined text-[#434651] shrink-0">
                  chevron_right
                </span>
              </div>
            ))}
          </div>
        </section>

      </div>
    </main>
  )
}
