"""
HealthBridge_Al -- Grok Translator Test Suite
Tests 8 cases across Hindi, Punjabi, Hinglish, English, and Mixed.
"""

import sys
import os
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from grok_translator import (
    detect_language,
    translate_to_medical_english,
    predict_with_translation,
    GROK_AVAILABLE,
)
from config import print_config

# ---------------------------------------------------------------------------
# 8 TEST CASES
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "id": 1,
        "lang": "Hindi",
        "text": "3 din se bukhar hai, sar dard bhi ho raha hai",
        "expect": "Typhoid",
    },
    {
        "id": 2,
        "lang": "Hindi",
        "text": "pet mein dard hai, dast lag gaye hain, ulti ho rahi hai",
        "expect": "Gastroenteritis",
    },
    {
        "id": 3,
        "lang": "Punjabi",
        "text": "2 din ton bukhaar aa gaya, sir noon vich dard hai",
        "expect": "Typhoid",
    },
    {
        "id": 4,
        "lang": "Punjabi",
        "text": "sans lene noon vich taklif hai aur chest noon vich dard",
        "expect": "Pneumonia",
    },
    {
        "id": 5,
        "lang": "Hinglish",
        "text": "fever 4 din se chal raha hai aur headache bhi",
        "expect": "Influenza",
    },
    {
        "id": 6,
        "lang": "Hinglish",
        "text": "aankhon ka rang peela ho gaya aur bhook nahi hai",
        "expect": "Jaundice",
    },
    {
        "id": 7,
        "lang": "English",
        "text": "fever for 2 days with stomach pain and diarrhea",
        "expect": "Gastroenteritis",
    },
    {
        "id": 8,
        "lang": "Mixed",
        "text": "khujli aur rash poore body pe, itching bahut ho rahi",
        "expect": "Allergic Reaction",
    },
]


def run_test_suite():
    """Run all 8 tests and print comparison table."""

    print()
    print("=" * 70)
    print("  HealthBridge_Al -- GROK TRANSLATOR TEST SUITE")
    print("=" * 70)
    print_config()
    print(f"  Grok API   : {'CONNECTED' if GROK_AVAILABLE else 'NOT AVAILABLE'}")
    print("=" * 70)

    results = []

    for tc in TEST_CASES:
        tid = tc["id"]
        expected_lang = tc["lang"].lower()
        text = tc["text"]

        print(f"\n{'='*70}")
        print(f"  TEST {tid} | Expected: {tc['lang']} -> {tc['expect']}")
        print(f"{'='*70}")

        # --- Language Detection ---
        detected = detect_language(text)
        lang_ok = (detected == expected_lang) or (
            expected_lang in ("mixed", "hinglish") and detected in ("mixed", "hinglish", "hindi")
        )
        print(f"  Input      : \"{text}\"")
        print(f"  Language   : {detected} {'[OK]' if lang_ok else '[MISMATCH]'}")

        # --- Without Grok (keyword only) ---
        try:
            from nlp_predictor import predict_disease
            from nlp_extractor import extract_symptoms
            raw_bert = predict_disease(text)
            raw_syms = extract_symptoms(text)
        except:
            raw_bert = {"top_disease": None, "confidence": 0.0}
            raw_syms = {}

        # --- With Grok ---
        start = time.time()
        grok_result = predict_with_translation(text)
        elapsed = int((time.time() - start) * 1000)

        # Print translation result
        print(f"  Translated : \"{grok_result['translated_text']}\"")
        print(f"  Grok Used  : {grok_result['grok_used']}  ({elapsed}ms)")

        # Print BERT comparison
        old_disease = raw_bert.get("top_disease", "N/A")
        old_conf = raw_bert.get("confidence", 0.0)
        new_disease = grok_result.get("bert_disease", "N/A")
        new_conf = grok_result.get("bert_confidence", 0.0)

        print(f"\n  WITHOUT GROK:")
        print(f"    BERT     : {old_disease} ({old_conf*100:.1f}%)")
        syms_old = ", ".join(f"{k}({v})" for k, v in raw_syms.items()) or "none"
        print(f"    Keywords : {syms_old}")

        print(f"  WITH GROK:")
        print(f"    BERT     : {new_disease} ({new_conf*100:.1f}%)")
        syms_new = ", ".join(f"{k}({v})" for k, v in grok_result["detected_symptoms"].items()) or "none"
        print(f"    Keywords : {syms_new}")
        print(f"    Method   : {grok_result['method']}")

        # Improvement
        if old_conf > 0:
            improvement = ((new_conf - old_conf) / old_conf) * 100
        else:
            improvement = 0.0

        results.append({
            "id": tid,
            "lang": tc["lang"],
            "old_disease": old_disease or "N/A",
            "old_conf": old_conf,
            "new_disease": new_disease or "N/A",
            "new_conf": new_conf,
            "improvement": improvement,
            "method": grok_result["method"],
            "grok_used": grok_result["grok_used"],
        })

    # === COMPARISON TABLE ===
    print("\n\n")
    print("=" * 80)
    print("  COMPARISON TABLE: Without Grok vs With Grok Translation")
    print("=" * 80)

    header = (
        f"{'#':<4} {'Lang':<10} {'Old Disease':<18} {'Old %':<8} "
        f"{'New Disease':<18} {'New %':<8} {'Change':<8} {'Method':<16}"
    )
    print(header)
    print("-" * 80)

    for r in results:
        imp_str = f"+{r['improvement']:.0f}%" if r['improvement'] >= 0 else f"{r['improvement']:.0f}%"
        row = (
            f"{r['id']:<4} {r['lang']:<10} {r['old_disease'][:16]:<18} "
            f"{r['old_conf']*100:>5.1f}%  "
            f"{r['new_disease'][:16]:<18} {r['new_conf']*100:>5.1f}%  "
            f"{imp_str:<8} {r['method']:<16}"
        )
        print(row)

    print("=" * 80)

    # Summary
    avg_old = sum(r["old_conf"] for r in results) / len(results) * 100
    avg_new = sum(r["new_conf"] for r in results) / len(results) * 100
    grok_count = sum(1 for r in results if r["grok_used"])

    print(f"\n  Avg BERT confidence WITHOUT Grok : {avg_old:.1f}%")
    print(f"  Avg BERT confidence WITH Grok    : {avg_new:.1f}%")
    print(f"  Tests with Grok translation      : {grok_count}/{len(results)}")
    print(f"  Overall improvement              : +{avg_new - avg_old:.1f}%")
    print()


if __name__ == "__main__":
    run_test_suite()
