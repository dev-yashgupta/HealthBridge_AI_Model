"""
HealthBridge_Al - Data Preprocessing
Builds disease_profiles.json from layer1 datasets (Kaggle + severity weights)
"""

import pandas as pd
import json
import os
import sys

# Force UTF-8 output so Windows terminal does not choke on special chars
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ──────────────────────────────────────────────────────────────────
DATASET_CSV  = "data/layer1/kaggle_disease_symptom/dataset.csv"
SEVERITY_CSV = "data/layer1/kaggle_disease_symptom/Symptom-severity.csv"
OUTPUT_DIR   = "data"
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, "disease_profiles.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Step 1: Load main dataset ───────────────────────────────────────────────
print("[1] Loading dataset.csv ...")
df = pd.read_csv(DATASET_CSV)

df["Disease"] = df["Disease"].str.strip()

symptom_cols = [c for c in df.columns if c.startswith("Symptom_")]

def clean_symptoms(row):
    syms = []
    for col in symptom_cols:
        val = row[col]
        if pd.notna(val) and str(val).strip():
            syms.append(str(val).strip().lower())
    return syms

print(f"   Rows loaded : {len(df)}")
print(f"   Symptom cols: {len(symptom_cols)}")

# ── Step 2: Load severity weights ───────────────────────────────────────────
print("\n[2] Loading Symptom-severity.csv ...")
sev_df = pd.read_csv(SEVERITY_CSV)

sev_df.columns = sev_df.columns.str.strip()
sym_col    = sev_df.columns[0]   # e.g. "Symptom"
weight_col = sev_df.columns[1]   # e.g. "weight"

severity_map = {}
for _, row in sev_df.iterrows():
    sym = str(row[sym_col]).strip().lower()
    try:
        wt = int(row[weight_col])
    except (ValueError, TypeError):
        wt = 0
    severity_map[sym] = wt

print(f"   Severity entries loaded: {len(severity_map)}")

# ── Step 3: Build disease profiles ─────────────────────────────────────────
print("\n[3] Building disease profiles ...")

disease_symptom_map = {}
for _, row in df.iterrows():
    disease = row["Disease"]
    syms    = clean_symptoms(row)
    if disease not in disease_symptom_map:
        disease_symptom_map[disease] = set()
    disease_symptom_map[disease].update(syms)

profiles        = []
all_unique_syms = set()

for disease, syms in sorted(disease_symptom_map.items()):
    syms_list = sorted(syms)
    weights   = [severity_map.get(s, 0) for s in syms_list]
    all_unique_syms.update(syms_list)
    profiles.append({
        "disease" : disease,
        "symptoms": syms_list,
        "weights" : weights
    })

# ── Step 4: Save JSON ───────────────────────────────────────────────────────
print(f"\n[4] Saving to {OUTPUT_FILE} ...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(profiles, f, indent=2, ensure_ascii=False)

print(f"   [OK] Saved {len(profiles)} disease profiles.")

# ── Step 5: Stats ───────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("PREPROCESSING STATS")
print("=" * 55)
print(f"  Total diseases found   : {len(profiles)}")
print(f"  Total unique symptoms  : {len(all_unique_syms)}")

top5 = sorted(severity_map.items(), key=lambda x: x[1], reverse=True)[:5]
print("\n  Top 5 heaviest symptoms by weight:")
for sym, wt in top5:
    print(f"    * {sym:<35} weight = {wt}")

print("\n  Sample disease profiles (first 2):")
for p in profiles[:2]:
    print(f"\n  Disease : {p['disease']}")
    print(f"  Symptoms: {p['symptoms']}")
    print(f"  Weights : {p['weights']}")

print("\n" + "=" * 55)
print("[DONE] data/disease_profiles.json is ready!\n")
