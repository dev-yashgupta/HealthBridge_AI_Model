"""
TASK 5 - Comparison Test: Old vs New Integrated Pipeline
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

OLD_SCORES = {
    "P101": 61.6,
    "P102": 70.3,
    "P103": None,
    "P104": None,
}

PATIENTS = [
    ("P101", "teen din se bukhar hai, khansi bhi aa rahi hai"),
    ("P102", "pet mein dard hai, dast lag rahe hain, ulti bhi"),
    ("P103", "sar mein bahut dard hai, aankhon ke peeche dard"),
    ("P104", "khujli ho rahi hai poore badan mein, daane nikle"),
]

from main import diagnose

print()
print("=" * 65)
print("  COMPARISON TEST  --  Old vs New Integrated Pipeline")
print("=" * 65)
print(f"{'Patient':<9} {'Old Score':<11} {'New Score':<11} {'Method':<10} {'Better?':<8}")
print("-" * 65)

for pid, text in PATIENTS:
    res = diagnose(pid, text)
    if res.get("status") == "success":
        new_score = res["top_score"]
        method    = res.get("method_used", "keyword").upper()
        old_score = OLD_SCORES.get(pid)
        if old_score is not None:
            delta   = new_score - old_score
            better  = (f"+{delta:.1f}%" if delta >= 0 else f"{delta:.1f}%")
            old_str = f"{old_score:.1f}%"
        else:
            better  = "N/A"
            old_str = "partial"
        print(f"  {pid:<7} {old_str:<11} {new_score:.1f}%{'':<6} {method:<10} {better:<8}")
        sym_str = ", ".join(f"{k}({v})" for k, v in res["detected_symptoms"].items())
        print(f"           Symptoms  : {sym_str}")
        if res.get("bert_suggestion"):
            print(f"           BERT hint : {res['bert_suggestion']} ({res['bert_confidence']*100:.1f}%)")
    else:
        print(f"  {pid:<7} ERROR: {res.get('message', '')}")
    print()

print("=" * 65)
print("  All 5 tasks complete.")
print("=" * 65)
