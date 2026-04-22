"""
HealthBridge_Al / HealthBridge_Al — Main Pipeline
End-to-end diagnosis: NLP → DB → Matcher → Report
"""

import sys
import os
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Guard: disease_profiles.json must exist before anything else ──────────────
if not os.path.exists("data/disease_profiles.json"):
    print("[ERROR] data/disease_profiles.json not found.")
    print("        Please run preprocess.py first.")
    sys.exit(1)

# ── Import pipeline modules ───────────────────────────────────────────────────
# Priority: Grok Translator > BERT Hybrid > Keyword Only
GROK_AVAILABLE = False
NLP_AVAILABLE = False

try:
    from grok_translator import predict_with_translation, GROK_AVAILABLE as _grok_ok
    GROK_AVAILABLE = _grok_ok
    if GROK_AVAILABLE:
        print("NLP Mode: Grok + BERT Hybrid")
    else:
        print("NLP Mode: Grok module loaded (API key not set)")
except Exception as _grok_e:
    print(f"NLP Mode: Grok unavailable ({_grok_e})")

try:
    from nlp_predictor import predict_and_extract
    NLP_AVAILABLE = True
    if not GROK_AVAILABLE:
        print("NLP Mode: BERT Hybrid (no Grok)")
except Exception as _nlp_e:
    NLP_AVAILABLE = False
    if not GROK_AVAILABLE:
        print(f"NLP Mode: Keyword only ({_nlp_e})")

from nlp_extractor   import extract_symptoms, get_duration
from history_db      import log_symptoms, get_history_summary
from matcher         import match_with_history
from report_generator import generate_report, save_report


# ─────────────────────────────────────────────────────────────────────────────
# 1. CORE DIAGNOSE FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def diagnose(patient_id: str, user_text: str) -> dict:
    """
    Full end-to-end diagnosis pipeline.

    Args:
        patient_id : Unique patient ID (e.g. "P001")
        user_text  : Symptom description in Hindi/English/Hinglish/Punjabi

    Returns:
        dict with keys: patient_id, detected_symptoms, duration_days,
                        top_disease, top_score, urgency,
                        report, saved_path, status
        OR on no-symptoms: {"status": "no_symptoms", "message": ...}
        OR on error      : {"status": "error", "message": ...}
    """
    try:
        # Step 1 — Extract symptoms (Grok > BERT hybrid > keyword fallback)
        if GROK_AVAILABLE:
            grok_result       = predict_with_translation(user_text)
            detected_symptoms = grok_result["detected_symptoms"]
            method_used       = grok_result["method"]
            bert_disease      = grok_result.get("bert_disease", None)
            bert_conf         = grok_result.get("bert_confidence", 0.0)
            predictions       = grok_result.get("predictions", [])
        elif NLP_AVAILABLE:
            nlp_result        = predict_and_extract(user_text)
            detected_symptoms = nlp_result["detected_symptoms"]
            method_used       = nlp_result["method"]
            bert_disease      = nlp_result.get("bert_disease", None)
            bert_conf         = nlp_result.get("bert_confidence", 0.0)
            predictions       = nlp_result.get("predictions", [])
        else:
            detected_symptoms = extract_symptoms(user_text)
            method_used  = "keyword"
            bert_disease = None
            bert_conf    = 0.0
            predictions  = []

        # Step 2 — Extract duration
        duration_days = get_duration(user_text)

        # Step 3 — Handle no symptoms
        if not detected_symptoms:
            return {
                "status" : "no_symptoms",
                "message": "Koi symptom identify nahi hua. Thoda detail mein batayein.",
            }

        # Step 4 — Log to DB (with retry on locked DB)
        for attempt in range(2):
            try:
                log_symptoms(patient_id, detected_symptoms, duration_days)
                break
            except Exception as db_err:
                if attempt == 0:
                    time.sleep(1)
                else:
                    raise db_err

        # Step 5 — Get history summary
        history_summary = get_history_summary(patient_id)

        # Step 6 — Match diseases with history
        # In hybrid mode we need more candidates so that the combined (BERT+keyword) top diseases
        # are present in the matcher output and can be re-ranked.
        # Use a larger top_k in hybrid mode so BERT+keyword predicted diseases
        # (even if they are not keyword-top-N) are present and can be re-ranked.
        top_k_for_match = 50 if method_used == "hybrid" else 5
        matches = match_with_history(patient_id, detected_symptoms, top_k=top_k_for_match)

        # Step 6.1 — Hybrid scoring override (use combined BERT+keyword confidence)
        # This keeps the downstream report structure (matched_symptoms/missing_critical)
        # but ranks by the hybrid combined score.
        if method_used == "hybrid" and predictions:
            try:
                from matcher import get_urgency_level

                pred_map = {
                    str(p["disease"]).strip().lower(): float(p["confidence"])
                    for p in predictions
                    if p and "disease" in p and "confidence" in p
                }

                for m in matches:
                    key = str(m.get("disease", "")).strip().lower()
                    if key in pred_map:
                        new_score = pred_map[key] * 100.0
                        m["score"] = round(float(new_score), 2)
                        m["urgency"] = get_urgency_level(m["score"])

                matches.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            except Exception:
                # If override fails, keep original matcher ranking.
                pass

        top = matches[0] if matches else {}

        # Step 7 — Generate report
        report_str = generate_report(
            patient_id      = patient_id,
            user_text       = user_text,
            detected_syms   = detected_symptoms,
            duration_days   = duration_days,
            matches         = matches,
            history_summary = history_summary,
            method_used     = method_used,
            bert_suggestion = bert_disease,
            bert_conf       = bert_conf,
        )

        # Step 8 — Save report
        saved_path = save_report(
            report_str,
            patient_id,
            top_disease=top.get("disease", "Unknown"),
            top_score=top.get("score", 0.0),
            urgency=top.get("urgency", "LOW"),
        )

        return {
            "patient_id"        : patient_id,
            "detected_symptoms" : detected_symptoms,
            "duration_days"     : duration_days,
            "top_disease"       : top.get("disease", "Unknown"),
            "top_score"         : top.get("score", 0.0),
            "urgency"           : top.get("urgency", "LOW"),
            "matched_symptoms"  : top.get("matched_symptoms", []),
            "predictions"      : predictions,
            "report"            : report_str,
            "saved_path"        : saved_path,
            "status"            : "success",
            "method_used"       : method_used,
            "bert_suggestion"   : bert_disease,
            "bert_confidence"   : bert_conf,
        }

    except Exception as e:
        return {
            "status" : "error",
            "message": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# 2. INTERACTIVE TERMINAL MODE
# ─────────────────────────────────────────────────────────────────────────────
def diagnose_interactive():
    """Simple terminal loop for real-time diagnosis."""

    print("\n" + "=" * 50)
    print("   HealthBridge_Al  --  Symptom Checker")
    print("=" * 50)

    patient_id = input("\nPatient ID enter karein: ").strip()
    if not patient_id:
        patient_id = "GUEST"

    print("\nSymptoms describe karein (ya 'quit' likhein):")

    while True:
        try:
            user_text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKhuda hafiz! HealthBridge band ho raha hai.")
            break

        if user_text.lower() in ("quit", "exit", "q", "band", "bye"):
            print("\nKhuda hafiz! HealthBridge band ho raha hai.")
            break

        if not user_text:
            print("  (Kuch toh likhein...)")
            continue

        print("\n  [Processing...]")
        result = diagnose(patient_id, user_text)

        if result["status"] == "no_symptoms":
            print(f"  [?]  {result['message']}")

        elif result["status"] == "error":
            print(f"  [X]  Error: {result['message']}")

        else:
            sym_str = ", ".join(result["detected_symptoms"].keys())
            dur     = result["duration_days"]
            dur_str = f"{dur} day(s)" if dur >= 0 else "unknown"

            print(f"\n  [OK] Symptoms detected : {sym_str}")
            print(f"  [*]  Duration          : {dur_str}")
            print(f"  [>]  Top match         : {result['top_disease']} "
                  f"({result['top_score']}%) -- {result['urgency']}")
            print(f"  [S]  Report saved      : {result['saved_path']}")
            print("\n" + "-" * 50 + " Full Report " + "-" * 7)
            print(result["report"])

        print("\nAur symptoms describe karein (ya 'quit'):")


# ─────────────────────────────────────────────────────────────────────────────
# 3. BATCH TEST
# ─────────────────────────────────────────────────────────────────────────────
BATCH_PATIENTS = [
    ("P101", "teen din se bukhar hai, khansi bhi aa rahi hai aur thakaan bahut hai"),
    ("P102", "pet mein dard hai, dast lag rahe hain, ulti bhi"),
    ("P103", "sar mein bahut dard hai, aankhon ke peeche dard, body mein dard"),
    ("P104", "khujli ho rahi hai poore badan mein, skin pe daane nikal aaye hain"),
]


def run_batch_test():
    """Run predefined batch of patients and print summary."""
    divider = "-" * 55

    print("\n" + "=" * 55)
    print("  BATCH TEST  --  4 Patients")
    print("=" * 55)

    for patient_id, user_text in BATCH_PATIENTS:
        print(f"\n{divider}")
        result = diagnose(patient_id, user_text)

        if result["status"] == "success":
            sym_str = ", ".join(result["detected_symptoms"].keys())
            dur     = result["duration_days"]
            dur_str = f"{dur} day(s)" if dur >= 0 else "unknown"

            print(f"  Patient  : {patient_id}")
            print(f"  Input    : \"{user_text[:55]}...\"" if len(user_text) > 55
                  else f"  Input    : \"{user_text}\"")
            print(f"  Symptoms : {sym_str}")
            print(f"  Duration : {dur_str}")
            print(f"  NLP      : {result.get('method_used','keyword').upper()}", end="")
            if result.get('bert_suggestion'):
                print(f" | BERT: {result['bert_suggestion']} ({result['bert_confidence']*100:.1f}%)", end="")
            print()
            print(f"  Top Match: {result['top_disease']} "
                  f"-- {result['top_score']}% [{result['urgency']}]")
            print(f"  Saved    : {result['saved_path']}")

        elif result["status"] == "no_symptoms":
            print(f"  Patient  : {patient_id}")
            print(f"  Input    : \"{user_text[:55]}\"")
            print(f"  Result   : [NO SYMPTOMS] {result['message']}")

        else:
            print(f"  Patient  : {patient_id}")
            print(f"  Result   : [ERROR] {result['message']}")

    print(f"\n{divider}")
    print("  Batch test complete.")
    print("=" * 55)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running batch test...")
    run_batch_test()

    print("\nStarting interactive mode...")
    diagnose_interactive()
