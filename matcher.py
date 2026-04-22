"""
HealthBridge_Al - Disease Matching Engine
Core weighted scoring algorithm for disease prediction
"""

import json
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA on import
# ─────────────────────────────────────────────────────────────────────────────
PROFILES_PATH = "data/disease_profiles.json"

def _load_profiles(path: str = PROFILES_PATH) -> dict:
    """Load disease_profiles.json → {disease_name: {symptoms, weights}}"""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"[ERROR] {path} not found. Run preprocess.py first."
        )
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    profiles = {}
    for entry in raw:
        profiles[entry["disease"]] = {
            "symptoms": entry["symptoms"],
            "weights" : entry["weights"],
        }
    return profiles

DISEASE_PROFILES = _load_profiles()


# ─────────────────────────────────────────────────────────────────────────────
# 4. URGENCY LEVEL helper
# ─────────────────────────────────────────────────────────────────────────────
def get_urgency_level(score: float) -> str:
    """
    score >= 70  -> HIGH   (consult doctor today)
    score 40-69  -> MEDIUM (monitor, consult if worsens)
    score < 40   -> LOW    (rest and home care)
    """
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"


# ─────────────────────────────────────────────────────────────────────────────
# 2. CORE MATCHING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def match_diseases(detected_symptoms: dict, top_k: int = 5) -> list:
    """
    Matches patient symptoms to disease profiles using a weighted scoring algo.

    Args:
        detected_symptoms : {symptom_name: patient_severity_weight}
        top_k             : Number of top diseases to return

    Returns:
        List of top_k dicts sorted by score descending:
        [{
            "disease"          : str,
            "score"            : float   (0-100),
            "matched_symptoms" : list,
            "missing_critical" : list,   (weight >= 6 symptoms not reported)
            "urgency"          : str,    (HIGH / MEDIUM / LOW)
        }]
    """
    patient_syms = set(detected_symptoms.keys())
    results = []

    for disease, profile in DISEASE_PROFILES.items():
        dis_syms    = profile["symptoms"]   # list
        dis_weights = profile["weights"]    # list (parallel to dis_syms)

        # ── Build lookup: symptom → disease weight ──────────────────────────
        sym_weight = dict(zip(dis_syms, dis_weights))

        total_score   = sum(dis_weights)            # max possible
        if total_score == 0:
            continue

        # ── Matched score ────────────────────────────────────────────────────
        matched_syms  = []
        matched_score = 0.0

        for sym, d_wt in sym_weight.items():
            if sym in patient_syms:
                matched_syms.append(sym)
                matched_score += d_wt

                # BONUS: patient severity >= disease weight → +15%
                p_wt = detected_symptoms[sym]
                if p_wt >= d_wt:
                    matched_score += d_wt * 0.15

        # ── Coverage percentage ──────────────────────────────────────────────
        coverage = (matched_score / total_score) * 100

        # ── Collect missing critical symptoms (weight >= 6) for display ──────
        missing_critical = []
        for sym, d_wt in sym_weight.items():
            if sym not in patient_syms and d_wt >= 6:
                missing_critical.append(sym)

        # ── SOFT PENALTY: only when patient gives 1 symptom vs large profile ─
        penalty = 0.0
        if len(patient_syms) == 1 and len(dis_syms) >= 10:
            penalty = 10.0   # flat 10-point deduction for extremely sparse input

        final_score = max(0.0, coverage - penalty)
        final_score = round(min(final_score, 100.0), 2)

        results.append({
            "disease"          : disease,
            "score"            : final_score,
            "matched_symptoms" : matched_syms,
            "missing_critical" : missing_critical,
            "urgency"          : get_urgency_level(final_score),
        })

    # Sort by score descending, return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ─────────────────────────────────────────────────────────────────────────────
# 3. HISTORY-AWARE MATCHING
# ─────────────────────────────────────────────────────────────────────────────
def match_with_history(patient_id: str, current_symptoms: dict, top_k: int = 5) -> list:
    """
    Merges current symptoms with patient's history, then runs match_diseases().

    Args:
        patient_id       : e.g. "P001"
        current_symptoms : {symptom: weight} from NLP extractor
        top_k            : Number of top diseases to return

    Returns:
        Same format as match_diseases() plus:
        "history_boost": True/False per result
    """
    from history_db import get_history

    history = get_history(patient_id, days=30)   # last 30 days

    # Build history symptom dict — keep highest weight if duplicate
    history_syms: dict = {}
    for entry in history:
        sym = entry["symptom"]
        wt  = entry["weight"]
        if sym not in history_syms or wt > history_syms[sym]:
            history_syms[sym] = wt

    # Merge: current takes precedence, but history fills gaps
    merged = {**history_syms, **current_symptoms}

    # Track which symptoms came from history only (not in current)
    history_only = set(history_syms.keys()) - set(current_symptoms.keys())

    results = match_diseases(merged, top_k=top_k)

    # Tag history_boost: True if any matched symptom came from history
    for r in results:
        boosted = any(sym in history_only for sym in r["matched_symptoms"])
        r["history_boost"] = boosted

    return results


# ─────────────────────────────────────────────────────────────────────────────
# PRETTY PRINT helper
# ─────────────────────────────────────────────────────────────────────────────
def print_results(results: list, label: str = ""):
    divider = "-" * 56
    print(f"\n{divider}")
    if label:
        print(f"  TEST: {label}")
        print(divider)
    for i, r in enumerate(results, 1):
        boost_tag = "  [history boost applied]" if r.get("history_boost") else ""
        print(f"  #{i}  {r['disease']:<35} Score: {r['score']:>6.1f}%  [{r['urgency']}]")
        if r["matched_symptoms"]:
            print(f"       Matched : {', '.join(r['matched_symptoms'])}")
        if r["missing_critical"]:
            print(f"       Missing : {', '.join(r['missing_critical'])}")
        if boost_tag:
            print(f"       History :{boost_tag}")
    print(divider)


# ─────────────────────────────────────────────────────────────────────────────
# 5. TEST SEQUENCE
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from history_db import log_symptoms

    print("=" * 56)
    print("  MATCHER.PY — DISEASE MATCHING ENGINE TEST")
    print("=" * 56)

    # ── Test A: Typhoid pattern ──────────────────────────────────────────────
    r_a = match_diseases(
        {"high_fever": 7, "headache": 3, "nausea": 5, "vomiting": 5},
        top_k=5
    )
    print_results(r_a, "Classic Typhoid pattern")

    # ── Test B: Dengue pattern ───────────────────────────────────────────────
    r_b = match_diseases(
        {"high_fever": 7, "pain_behind_the_eyes": 4, "headache": 3, "muscle_pain": 2},
        top_k=5
    )
    print_results(r_b, "Dengue pattern")

    # ── Test C: Common Cold ──────────────────────────────────────────────────
    r_c = match_diseases(
        {"cough": 4, "runny_nose": 5, "congestion": 5, "mild_fever": 3},
        top_k=5
    )
    print_results(r_c, "Common Cold / Flu")

    # ── Test D: History merge ────────────────────────────────────────────────
    log_symptoms("P003", {"high_fever": 7}, duration_days=1)
    r_d = match_with_history(
        "P003",
        {"headache": 3, "nausea": 5},
        top_k=5
    )
    print_results(r_d, "History merge (P003) — high_fever from history")

    print("\n[DONE] matcher.py complete!\n")
