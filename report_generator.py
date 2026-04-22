"""
HealthBridge_Al - Medical Report Generator
Produces formatted diagnostic reports from NLP + matcher pipeline
All report text is in English.
"""

import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────────────────
# 1. TEST MAP — 41 diseases → recommended tests
# ─────────────────────────────────────────────────────────────────────────────
TEST_MAP = {
    "Fungal infection"                       : "KOH test, Skin biopsy",
    "Allergy"                                : "Skin prick test, IgE blood test",
    "GERD"                                   : "Endoscopy, pH monitoring",
    "Chronic cholestasis"                    : "LFT, Ultrasound abdomen",
    "Drug Reaction"                          : "Allergy panel, Liver function test",
    "Peptic ulcer disease"                   : "Endoscopy, H.pylori test",
    "AIDS"                                   : "HIV ELISA, CD4 count, Viral load",
    "Diabetes"                               : "FBS, HbA1c, OGTT",
    "Gastroenteritis"                        : "Stool culture, CBC",
    "Bronchial Asthma"                       : "Spirometry, Peak flow, Chest X-ray",
    "Hypertension"                           : "BP monitoring, ECG, Kidney function",
    "Migraine"                               : "MRI brain, CT scan",
    "Cervical spondylosis"                   : "X-ray cervical spine, MRI",
    "Paralysis (brain hemorrhage)"           : "MRI brain, CT scan, Neurologist consult",
    "Jaundice"                               : "LFT, Bilirubin, Ultrasound abdomen",
    "Malaria"                                : "RDT, Peripheral smear, CBC",
    "Chicken pox"                            : "Clinical diagnosis, Tzanck smear",
    "Dengue"                                 : "CBC, NS1 antigen, Dengue IgM/IgG",
    "Typhoid"                                : "CBC, Widal test, Blood culture",
    "hepatitis A"                            : "LFT, Anti-HAV IgM",
    "hepatitis B"                            : "HBsAg, LFT, Viral load",
    "hepatitis C"                            : "Anti-HCV, HCV RNA, LFT",
    "hepatitis D"                            : "Anti-HDV, LFT",
    "hepatitis E"                            : "Anti-HEV IgM, LFT",
    "Alcoholic hepatitis"                    : "LFT, GGT, Ultrasound",
    "Tuberculosis"                           : "Chest X-ray, Sputum AFB, Mantoux test",
    "Common Cold"                            : "Clinical diagnosis, rest recommended",
    "Pneumonia"                              : "Chest X-ray, CBC, Sputum culture",
    "Dimorphic hemmorhoids(piles)"           : "Proctoscopy, Colonoscopy",
    "Heart attack"                           : "ECG, Troponin, Echo",
    "Varicose veins"                         : "Doppler ultrasound",
    "Hypothyroidism"                         : "TSH, T3, T4",
    "Hyperthyroidism"                        : "TSH, T3, T4, Thyroid scan",
    "Hypoglycemia"                           : "FBS, HbA1c, Insulin level",
    "Osteoarthritis"                         : "X-ray joints, ESR, CRP",
    "Arthritis"                              : "RA factor, Anti-CCP, X-ray",
    "(vertigo) Paroymsal  Positional Vertigo": "ENT consult, Dix-Hallpike test",
    "Acne"                                   : "Clinical diagnosis, Hormonal panel",
    "Urinary tract infection"                : "Urine culture, Urine R/M",
    "Psoriasis"                              : "Skin biopsy, Clinical diagnosis",
    "Impetigo"                               : "Swab culture, Clinical diagnosis",
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. URGENCY ADVICE — all in English
# ─────────────────────────────────────────────────────────────────────────────
URGENCY_ADVICE = {
    "HIGH"  : "Consult a doctor today. These symptoms may be serious.",
    "MEDIUM": "See a doctor within 2-3 days. Monitor your symptoms closely.",
    "LOW"   : "Rest at home. If symptoms persist beyond 3 days, consult a doctor.",
}

URGENCY_TAG = {
    "HIGH"  : "[!!] HIGH",
    "MEDIUM": "[ !] MEDIUM",
    "LOW"   : "[  ] LOW",
}

METHOD_LABELS = {
    "bert"            : "BERT Neural Engine",
    "hybrid"          : "BERT + Keyword Hybrid",
    "grok"            : "Grok + BERT Hybrid",
    "keyword"         : "Keyword Matching",
    "keyword_fallback": "Keyword Matching",
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper — lookup tests for a disease
# ─────────────────────────────────────────────────────────────────────────────
def _get_tests(disease_name: str) -> str:
    if disease_name in TEST_MAP:
        return TEST_MAP[disease_name]
    dl = disease_name.lower()
    for key, val in TEST_MAP.items():
        if key.lower() in dl or dl in key.lower():
            return val
    return "Consult a doctor for appropriate diagnostic tests"


# ─────────────────────────────────────────────────────────────────────────────
# 3. GENERATE REPORT — fully in English
# ─────────────────────────────────────────────────────────────────────────────
def generate_report(
    patient_id      : str,
    user_text       : str,
    detected_syms   : dict,
    duration_days   : int,
    matches         : list,
    history_summary : dict,
    method_used     : str   = "keyword",
    bert_suggestion : str   = None,
    bert_conf       : float = 0.0,
) -> str:
    now       = datetime.now()
    time_str  = now.strftime("%d %b %Y, %I:%M %p")
    dur_str   = f"{duration_days} day(s)" if duration_days > 0 else ("Started today" if duration_days == 0 else "Not specified")
    top_match = matches[0] if matches else None

    W            = 60
    border_top   = "=" * W
    section_line = lambda title: f"-- {title} " + "-" * (W - len(title) - 4)

    method_label = METHOD_LABELS.get(method_used, "AI Analysis")

    lines = []
    lines.append(border_top)
    lines.append("       HEALTHBRIDGE AI  --  MEDICAL REPORT")
    lines.append(border_top)
    lines.append("")
    lines.append(f"  Patient ID   : {patient_id}")
    lines.append(f"  Report Time  : {time_str}")
    lines.append(f"  Input Text   : \"{user_text}\"")
    lines.append(f"  Duration     : {dur_str}")
    lines.append(f"  NLP Method   : {method_label}")
    if bert_suggestion and bert_conf >= 0.40:
        lines.append(f"  BERT Suggest : {bert_suggestion} ({bert_conf:.0%} confidence)")
    lines.append("")

    # ── Symptoms Detected ────────────────────────────────────────────────────
    lines.append(section_line("SYMPTOMS DETECTED"))
    if detected_syms:
        for sym, wt in detected_syms.items():
            readable = sym.replace("_", " ").title()
            lines.append(f"  * {readable:<35} [severity: {wt}/7]")
    else:
        lines.append("  No symptoms detected.")
    lines.append("")

    # ── Symptom History ──────────────────────────────────────────────────────
    lines.append(section_line("SYMPTOM HISTORY (last 7 days)"))
    summary = history_summary.get("summary", {})
    if summary:
        for date, syms in list(summary.items())[-7:]:
            readable_syms = [s.replace("_", " ").title() for s in syms]
            lines.append(f"  {date} : {', '.join(readable_syms)}")
    else:
        lines.append("  No prior history found.")
    lines.append("")

    # ── Top Diagnoses ────────────────────────────────────────────────────────
    lines.append(section_line("TOP DIAGNOSIS"))
    for i, m in enumerate(matches[:3], 1):
        urgency = m.get("urgency", "LOW")
        tag     = URGENCY_TAG[urgency]
        boost   = "  [history boost]" if m.get("history_boost") else ""
        lines.append(f"  #{i}  {m['disease']:<30} {m['score']:>5.1f}%  {tag}{boost}")
        if m.get("matched_symptoms"):
            readable = [s.replace("_", " ").title() for s in m["matched_symptoms"]]
            lines.append(f"       Matched  : {', '.join(readable)}")
        if m.get("missing_critical"):
            crit = [s.replace("_", " ").title() for s in m["missing_critical"][:4]]
            lines.append(f"       Missing  : {', '.join(crit)}")
        lines.append("")

    # ── Recommended Tests ────────────────────────────────────────────────────
    lines.append(section_line("RECOMMENDED TESTS"))
    if top_match:
        tests = _get_tests(top_match["disease"])
        lines.append(f"  Based on top diagnosis ({top_match['disease']}):")
        lines.append(f"  -> {tests}")
    else:
        lines.append("  Insufficient data for test recommendation.")
    lines.append("")

    # ── Doctor Advice ────────────────────────────────────────────────────────
    lines.append(section_line("DOCTOR ADVICE"))
    if top_match:
        advice = URGENCY_ADVICE.get(top_match["urgency"], URGENCY_ADVICE["LOW"])
        lines.append(f"  [!] {advice}")
    lines.append("")

    # ── Disclaimer ───────────────────────────────────────────────────────────
    lines.append(section_line("DISCLAIMER"))
    lines.append("  This report is an AI-based suggestion only.")
    lines.append("  Please consult a registered medical professional for diagnosis.")
    lines.append(border_top)

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 4. SAVE REPORT to file + SQLite DB
# ─────────────────────────────────────────────────────────────────────────────
def save_report(report_str: str, patient_id: str, top_disease: str = "", top_score: float = 0.0, urgency: str = "LOW") -> str:
    """
    Saves report to:
      - reports/<patient_id>_<timestamp>.txt  (file)
      - data/healthbridge.db reports table    (SQLite)
    Returns saved file path.
    """
    os.makedirs("reports", exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{patient_id}_{ts}.txt"
    filepath = os.path.join("reports", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_str)

    # Save to SQLite DB
    try:
        import sqlite3
        db_path = "data/healthbridge.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id  TEXT NOT NULL,
                top_disease TEXT,
                top_score   REAL,
                urgency     TEXT,
                report_text TEXT,
                file_path   TEXT,
                created_at  TEXT
            )
        """)
        cursor.execute(
            """INSERT INTO reports (patient_id, top_disease, top_score, urgency, report_text, file_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, top_disease, top_score, urgency, report_str, filepath,
             datetime.now().isoformat(sep=" ", timespec="seconds"))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WARN] Could not save report to DB: {e}", file=sys.stderr)

    return filepath
