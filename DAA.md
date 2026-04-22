# DAA — Design & Analysis of Algorithms
## HealthBridge AI Project

**Project:** HealthBridge AI — Multilingual Medical Symptom Checker  
**Stack:** Python · Node.js · React 19 · SQLite  
**Date:** April 2026

---

## Table of Contents

1. [Searching Algorithms](#1-searching-algorithms)
2. [Sorting Algorithms](#2-sorting-algorithms)
3. [Hashing / Dictionary Algorithms](#3-hashing--dictionary-algorithms)
4. [Graph / Tree Algorithms](#4-graph--tree-algorithms)
5. [Greedy Algorithms](#5-greedy-algorithms)
6. [Dynamic Programming / Memoization](#6-dynamic-programming--memoization)
7. [String Algorithms](#7-string-algorithms)
8. [Summary Table](#8-summary-table)

---

## 1. Searching Algorithms

---

### 1.1 Linear Search — Symptom Synonym Lookup
**File:** `nlp_extractor.py` — function `extract_symptoms()`

```python
sorted_keys = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)
for phrase in sorted_keys:
    if phrase in text_lower:   # ← Linear search through synonym list
        found[canonical] = wt
```

**Kya karta hai:** User ke input text mein 200+ Hindi/English symptom synonyms dhundta hai. Har phrase ko text ke against check karta hai.

**Kyon use kiya:**
- Synonym list fixed size hai (200 entries) — O(n) acceptable hai
- Dictionary lookup `phrase in text_lower` Python mein O(m) hai (m = text length)
- Multi-word phrases pehle check hoti hain (longest-first sort) taaki partial match na ho
- Example: "sar dard" pehle match ho, phir "dard" alag se na match kare

**Complexity:** O(n × m) — n = synonyms count, m = input text length

---

### 1.2 Hash Set Lookup (O(1) Search) — Disease Profile Lookup
**File:** `matcher.py` — function `match_diseases()`

```python
DISEASE_PROFILES = _load_profiles()  # dict loaded at startup

for disease, profile in DISEASE_PROFILES.items():
    sym_weight = dict(zip(dis_syms, dis_weights))
    for sym, d_wt in sym_weight.items():
        if sym in patient_syms:   # ← Python set lookup = O(1) hash search
```

**Kya karta hai:** Patient ke detected symptoms ko 41 disease profiles ke against match karta hai.

**Kyon use kiya:**
- `patient_syms` ko Python `set` mein store kiya — set membership check O(1) average
- Agar list use karte toh O(n) per lookup hota — 41 diseases × ~17 symptoms = 697 comparisons
- Set use karne se effectively O(1) per symptom check

**Complexity:** O(D × S) — D = diseases (41), S = avg symptoms per disease (~17)

---

### 1.3 Fuzzy Search — Misspelled Symptom Matching
**File:** `nlp_extractor.py` — function `extract_symptoms()`

```python
from thefuzz import fuzz, process as fuzz_process

match, score = fuzz_process.extractOne(
    token, ALL_SYMPTOMS, scorer=fuzz.ratio
)
if score >= fuzzy_threshold:   # threshold = 80%
    found[match] = WEIGHT_MAP.get(match, 1)
```

**Kya karta hai:** Agar user ne symptom galat spell kiya (e.g., "faver" instead of "fever"), fuzzy matching usse correct canonical name se match karta hai.

**Kyon use kiya:**
- Indian users often misspell English medical terms
- Levenshtein distance based ratio score use hota hai
- 80% threshold — too low = false positives, too high = misses
- `thefuzz` library Levenshtein distance algorithm implement karta hai

**Algorithm:** Levenshtein Edit Distance  
**Complexity:** O(m × n) per comparison — m, n = string lengths

---

## 2. Sorting Algorithms

---

### 2.1 Sort by Score (Descending) — Disease Ranking
**File:** `matcher.py` — function `match_diseases()`

```python
results.sort(key=lambda x: x["score"], reverse=True)
return results[:top_k]
```

**Kya karta hai:** Saare 41 disease match scores ko descending order mein sort karta hai. Top-K results return karta hai.

**Kyon use kiya:**
- User ko sabse probable disease pehle dikhani hai
- Python's built-in `list.sort()` **Timsort** algorithm use karta hai
- Timsort real-world data pe best performance deta hai (partially sorted lists)
- `reverse=True` — highest confidence disease pehle

**Algorithm:** Timsort (Python built-in)  
**Complexity:** O(n log n) — n = 41 diseases

---

### 2.2 Sort by Length (Descending) — Longest Phrase First
**File:** `nlp_extractor.py` — function `extract_symptoms()`

```python
sorted_keys = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)
```

**Kya karta hai:** Symptom synonyms ko length ke hisaab se descending sort karta hai — longest phrases pehle check hoti hain.

**Kyon use kiya:**
- **Greedy approach** — longer match = more specific
- Agar "sar dard" (2 words) pehle match ho jaaye, toh "dard" (1 word) alag se match nahi hoga
- Bina is sort ke: "dard" match hoga aur "sar dard" miss ho sakta tha
- Example: "pet mein dard" → `stomach_pain` (correct) vs "dard" → `joint_pain` (wrong)

**Algorithm:** Timsort on string lengths  
**Complexity:** O(n log n) — n = 200 synonyms (one-time at startup)

---

### 2.3 Sort by Date (Descending) — History Timeline
**File:** `frontend/src/pages/History.jsx` — function `groupEntriesByDate()`

```javascript
const sortedGroups = new Map(
    [...groups.entries()].sort((a, b) => new Date(b[0]) - new Date(a[0]))
)
```

**Kya karta hai:** Symptom history entries ko date ke hisaab se descending sort karta hai — most recent entries pehle dikhti hain.

**Kyon use kiya:**
- Medical history mein latest entries sabse relevant hoti hain
- `Date` objects ka subtraction numeric comparison deta hai
- JavaScript's `Array.sort()` V8 engine mein **Timsort** use karta hai

**Algorithm:** Timsort (JavaScript V8 engine)  
**Complexity:** O(n log n) — n = number of date groups

---

### 2.4 Sort by Confidence (Descending) — Hybrid Predictions
**File:** `nlp_predictor.py` — function `_combine_bert_and_keyword_hybrid()`

```python
combined.sort(key=lambda x: x["confidence"], reverse=True)
```

**Kya karta hai:** BERT + keyword hybrid scores ko combine karne ke baad final confidence score se sort karta hai.

**Kyon use kiya:**
- Hybrid scoring ke baad candidates unordered hote hain
- Top-3 predictions return karne ke liye sort zaroori hai
- Highest combined confidence = most likely disease

**Algorithm:** Timsort  
**Complexity:** O(n log n) — n = candidate diseases (typically 3–6)

---

### 2.5 Sort by Created Date (Descending) — Reports List
**File:** `db_bridge.py` — SQL query

```sql
SELECT * FROM reports
WHERE patient_id = ?
ORDER BY created_at DESC
LIMIT 50
```

**Kya karta hai:** Reports ko creation date ke hisaab se descending order mein fetch karta hai.

**Kyon use kiya:**
- Latest report sabse pehle dikhni chahiye
- SQLite `ORDER BY` B-Tree index use karta hai agar indexed column ho
- `LIMIT 50` — pagination ke bina bhi performance theek rehti hai

**Algorithm:** B-Tree sort (SQLite internal)  
**Complexity:** O(n log n) without index, O(log n + k) with index — k = result count

---

## 3. Hashing / Dictionary Algorithms

---

### 3.1 Hash Map — Symptom Weight Lookup
**File:** `nlp_extractor.py` — `WEIGHT_MAP` dictionary

```python
WEIGHT_MAP = {}
for profile in profiles:
    for sym, wt in zip(profile["symptoms"], profile["weights"]):
        if sym not in weight_map or wt > weight_map[sym]:
            weight_map[sym] = wt   # ← Hash map: symptom → max weight
```

**Kya karta hai:** Har symptom ka maximum severity weight (1–7) store karta hai across all 41 diseases.

**Kyon use kiya:**
- O(1) average lookup — symptom ka weight instantly milta hai
- Alternative (linear search through profiles) = O(41 × 17) = O(697) per lookup
- Hash map ek baar build hota hai at startup, phir O(1) reads

**Algorithm:** Hash Map (Python dict)  
**Complexity:** Build O(n), Lookup O(1) average

---

### 3.2 Hash Map — Disease Profile Storage
**File:** `matcher.py` — `DISEASE_PROFILES` dictionary

```python
profiles = {}
for entry in raw:
    profiles[entry["disease"]] = {
        "symptoms": entry["symptoms"],
        "weights" : entry["weights"],
    }
```

**Kya karta hai:** 41 disease profiles ko memory mein hash map mein store karta hai — disease name → {symptoms, weights}.

**Kyon use kiya:**
- O(1) disease lookup by name
- Hybrid scoring mein disease name se directly profile access hoti hai
- JSON file ek baar read hoti hai at startup — repeated disk I/O avoid

**Algorithm:** Hash Map  
**Complexity:** Build O(n), Lookup O(1)

---

### 3.3 Hash Set — Patient Symptom Membership Check
**File:** `matcher.py` — function `match_diseases()`

```python
patient_syms = set(detected_symptoms.keys())  # ← Hash Set

for sym, d_wt in sym_weight.items():
    if sym in patient_syms:   # ← O(1) set membership check
```

**Kya karta hai:** Patient ke detected symptoms ko set mein convert karta hai taaki O(1) membership check ho sake.

**Kyon use kiya:**
- Agar list use karte: `if sym in list` = O(n) per check
- Set use karne se: `if sym in set` = O(1) average
- 41 diseases × 17 symptoms = 697 checks — set se significant speedup

**Algorithm:** Hash Set  
**Complexity:** O(1) per membership check

---

## 4. Graph / Tree Algorithms

---

### 4.1 Decision Tree (Logic) — NLP Method Selection
**File:** `nlp_predictor.py` — function `decide_method_from_bert()`

```python
def decide_method_from_bert(bert_top_conf: float) -> str:
    if bert_top_conf > BERT_HIGH_CONFIDENCE:   # > 0.75
        return "bert"
    if bert_top_conf >= BERT_MID_CONFIDENCE:   # >= 0.40
        return "hybrid"
    return "keyword_fallback"
```

**Kya karta hai:** BERT confidence score ke basis pe decide karta hai ki kaunsa NLP method use karna hai.

**Kyon use kiya:**
- Simple threshold-based decision tree
- 3 branches: bert / hybrid / keyword_fallback
- O(1) decision — no iteration needed
- Medical domain mein interpretable decisions zaroori hain

```
                  [BERT Confidence]
                 /                 \
          > 0.75                 < 0.75
           /                         \
        BERT                      >= 0.40
       Mode                      /       \
                              Hybrid   Keyword
                              Mode     Fallback
```

**Algorithm:** Decision Tree (threshold-based)  
**Complexity:** O(1)

---

### 4.2 Trie (Implicit) — Regex Pattern Matching
**File:** `nlp_extractor.py` — function `get_duration()`

```python
week_match = re.search(
    r"(\d+|ek|do|teen|...)\s*hafte", text_lower
)
day_match = re.search(
    r"(\d+|ek|do|teen|...)\s*(?:din|day|days)", text_lower
)
```

**Kya karta hai:** Text mein duration patterns dhundta hai — "3 din", "ek hafte", "2 days" etc.

**Kyon use kiya:**
- Python `re` module internally NFA/DFA (finite automata) use karta hai — similar to Trie
- Multiple patterns ek saath match ho sakti hain
- Hindi numbers (ek, do, teen) + English numbers + units (din/day/hafte/week) — complex pattern
- Regex alternation `|` effectively trie-like branching karta hai

**Algorithm:** NFA/DFA (Regex engine — similar to Trie traversal)  
**Complexity:** O(m) — m = input text length

---

### 4.3 Weighted Bipartite Graph — Disease-Symptom Matching
**File:** `matcher.py` — function `match_diseases()`

```
Patient Symptoms          Disease Symptoms
(Left Nodes)              (Right Nodes)
                          
high_fever ──── w=7 ──→  [Typhoid]
headache   ──── w=3 ──→  [Typhoid]
nausea     ──── w=5 ──→  [Typhoid]
                          
                          Coverage = matched_weight / total_weight × 100
```

**Kya karta hai:** Patient symptoms aur 41 disease profiles ke beech weighted bipartite graph matching karta hai. Coverage score = normalized path weight.

**Complexity:** O(D × S) — D = 41 diseases, S = ~17 symptoms per disease

---

## 5. Greedy Algorithms

---

### 5.1 Greedy Merge — History-Aware Symptom Merging
**File:** `matcher.py` — function `match_with_history()`

```python
# Greedy: current symptoms override history (highest weight wins)
history_syms = {}
for entry in history:
    sym = entry["symptom"]
    wt  = entry["weight"]
    if sym not in history_syms or wt > history_syms[sym]:
        history_syms[sym] = wt   # ← Keep maximum weight (greedy)

merged = {**history_syms, **current_symptoms}  # current overrides history
```

**Kya karta hai:** Last 30 days ki history aur current symptoms ko merge karta hai. Duplicate symptoms ke liye maximum weight rakhta hai.

**Kyon use kiya:**
- **Greedy choice:** Highest severity weight = most clinically relevant
- Current symptoms always override history (fresh data more reliable)
- O(n) single pass — no backtracking needed
- Medical context: agar fever 3 din pehle 5/7 tha aur aaj 7/7 hai, toh 7/7 use karo

**Algorithm:** Greedy (maximum weight selection)  
**Complexity:** O(n) — n = history entries

---

### 5.2 Greedy Top-K Selection — Top Disease Results
**File:** `matcher.py` — function `match_diseases()`

```python
results.sort(key=lambda x: x["score"], reverse=True)
return results[:top_k]   # ← Greedy: take top-k highest scores
```

**Kya karta hai:** Sort ke baad sirf top-K diseases return karta hai.

**Kyon use kiya:**
- Full sort + slice = greedy top-K selection
- Alternative: heap-based top-K = O(n log k) — but n=41 itna chhota hai ki simple sort better
- User ko 3–5 results chahiye, 41 nahi

**Algorithm:** Greedy Top-K (sort + slice)  
**Complexity:** O(n log n) sort + O(k) slice

---

### 5.3 Greedy Best-First Search — Hybrid Disease Ranking
**File:** `nlp_predictor.py` — function `_combine_bert_and_keyword_hybrid()`

```python
# Greedy Best-First: always expand the highest-score candidate
combined.sort(key=lambda x: x["confidence"], reverse=True)

# Return top candidates — greedy selection
out = [{"disease": x["disease"], "confidence": x["confidence"]} for x in combined]
return out[:3]
```

**Kya karta hai:** BERT + keyword combined scores mein se greedy best-first approach se top-3 diseases select karta hai.

**Kyon use kiya:**
- Greedy best-first = heuristic-guided search
- Heuristic = combined confidence score (BERT × 0.6 + keyword × 0.4)
- No backtracking needed — medical diagnosis mein top candidates sufficient hain

**Algorithm:** Greedy Best-First Search  
**Complexity:** O(n log n) sort + O(1) selection

---

## 6. Dynamic Programming / Memoization

---

### 6.1 Memoization — BERT Model Lazy Loading
**File:** `grok_translator.py` — function `_ensure_bert()`

```python
_bert_loaded = False   # ← Memoization flag
_predict_disease = None

def _ensure_bert():
    global _bert_loaded, _predict_disease
    if _bert_loaded:          # ← Already loaded? Skip (O(1) check)
        return
    # ... load BERT model (expensive: 3-5 seconds) ...
    _bert_loaded = True       # ← Mark as loaded (memoize)
```

**Kya karta hai:** BERT model sirf pehli baar load hota hai. Subsequent calls mein already loaded model use hota hai.

**State Table (DP-style):**

| Call # | `_bert_loaded` Before | Action | Time Cost |
|--------|----------------------|--------|-----------|
| 1st | False | Load BERT model | ~4 seconds |
| 2nd | True | Skip loading | ~0ms |
| 3rd | True | Skip loading | ~0ms |

**Kyon use kiya:**
- BERT model load karna 3–5 seconds leta hai (500MB+ weights)
- Bina memoization ke: har diagnosis pe 3–5 second overhead
- With memoization: sirf pehli baar load, phir instant
- Python process lifetime mein model memory mein rehta hai

**Algorithm:** Memoization (lazy initialization)  
**Complexity:** First call O(model_size), subsequent calls O(1)

---

### 6.2 Weighted Scoring (DP-style Accumulation)
**File:** `matcher.py` — function `match_diseases()`

```python
for each disease in 41 profiles:
    matched_score = 0
    for each symptom in disease profile:
        if symptom in patient_symptoms:
            matched_score += disease_weight[symptom]
            # Bonus: patient severity ≥ disease weight → +15%
            if patient_weight[symptom] >= disease_weight[symptom]:
                matched_score += disease_weight[symptom] * 0.15
    
    coverage = (matched_score / total_disease_weight) * 100
    
    # Penalty for sparse input (1 symptom vs 10+ disease symptoms)
    if len(patient_symptoms) == 1 and len(disease_symptoms) >= 10:
        coverage -= 10
    
    final_score = clamp(coverage, 0, 100)
    urgency = HIGH if score >= 70 else MEDIUM if score >= 40 else LOW
```

**Kya karta hai:** Cumulative score accumulate karta hai — subproblem solutions (individual symptom matches) combine karke final disease score banata hai.

**Algorithm:** Cumulative Weighted Scoring (DP-style)  
**Complexity:** O(D × S) — D = diseases (41), S = symptoms (~17)

---

## 7. String Algorithms

---

### 7.1 String Matching — Phrase Detection
**File:** `nlp_extractor.py` — function `extract_symptoms()`

```python
if phrase in text_lower:   # ← Python's optimized string search
    text_lower = text_lower.replace(phrase, " ", 1)  # Remove matched
```

**Kya karta hai:** Input text mein symptom phrases dhundta hai aur match hone ke baad remove karta hai (taaki double-match na ho).

**Kyon use kiya:**
- Python's `in` operator for strings uses **Boyer-Moore-Horspool** or similar optimized algorithm internally
- `replace(..., 1)` — sirf pehla occurrence replace karo (count=1)
- Removal prevents: "sar dard" match ke baad "dard" alag se match na ho

**Algorithm:** Boyer-Moore-Horspool (Python string search)  
**Complexity:** O(n × m) worst case, O(n/m) average — n = text length, m = pattern length

---

### 7.2 Levenshtein Edit Distance — Fuzzy Matching Core
**File:** `nlp_extractor.py` (via `thefuzz` library)

```
Edit Distance Example:
"faver" → "fever"
Steps:
  f a v e r
  f e v e r
  ↑
  1 substitution: a → e
  Edit Distance = 1
  Similarity = (5-1)/5 = 80% ✓ (threshold met)
```

**Algorithm:** Levenshtein Distance (Dynamic Programming)  
**Complexity:** O(m × n) — m, n = string lengths

---

### 7.3 Regex Tokenization — Fuzzy Match Preprocessing
**File:** `nlp_extractor.py`

```python
tokens = re.findall(r"[a-z_]+", text_lower)
for token in tokens:
    if len(token) < 3:
        continue   # Skip very short tokens
```

**Kya karta hai:** Input text ko individual word tokens mein split karta hai fuzzy matching ke liye.

**Kyon use kiya:**
- Fuzzy matching word-level pe kaam karta hai, character-level nahi
- `len(token) < 3` filter — "is", "ho", "se" jaise common words skip karo
- Regex `[a-z_]+` — only alphabetic tokens, numbers/punctuation ignore

**Algorithm:** Regex tokenization  
**Complexity:** O(n) — n = text length

---

## 8. Summary Table

| Algorithm | File | Function | Time Complexity | Purpose |
|-----------|------|----------|-----------------|---------| 
| Linear Search | `nlp_extractor.py` | `extract_symptoms()` | O(n×m) | Synonym phrase matching |
| Hash Set Lookup | `matcher.py` | `match_diseases()` | O(1) avg | Symptom membership check |
| Fuzzy Search (Levenshtein) | `nlp_extractor.py` | `extract_symptoms()` | O(m×n) | Misspelling correction |
| Timsort (score desc) | `matcher.py` | `match_diseases()` | O(n log n) | Disease ranking |
| Timsort (length desc) | `nlp_extractor.py` | `extract_symptoms()` | O(n log n) | Longest phrase first |
| Timsort (date desc) | `History.jsx` | `groupEntriesByDate()` | O(n log n) | Timeline ordering |
| Timsort (confidence desc) | `nlp_predictor.py` | `_combine_bert_and_keyword_hybrid()` | O(n log n) | Hybrid result ranking |
| B-Tree Sort (SQL) | `db_bridge.py` | SQL `ORDER BY` | O(n log n) | Reports date ordering |
| Hash Map | `nlp_extractor.py` | `load_weight_map()` | O(1) lookup | Symptom weight lookup |
| Hash Map | `matcher.py` | `_load_profiles()` | O(1) lookup | Disease profile lookup |
| Decision Tree | `nlp_predictor.py` | `decide_method_from_bert()` | O(1) | NLP method selection |
| NFA/DFA (Regex) | `nlp_extractor.py` | `get_duration()` | O(m) | Duration pattern matching |
| Greedy Merge | `matcher.py` | `match_with_history()` | O(n) | Max-weight symptom merge |
| Greedy Top-K | `matcher.py` | `match_diseases()` | O(n log n) | Top disease selection |
| Greedy Best-First | `nlp_predictor.py` | `_combine_bert_and_keyword_hybrid()` | O(n log n) | Hybrid candidate ranking |
| Memoization | `grok_translator.py` | `_ensure_bert()` | O(1) after init | BERT lazy loading |
| Weighted Scoring (DP) | `matcher.py` | `match_diseases()` | O(D×S) | Disease confidence score |
| Boyer-Moore (String) | `nlp_extractor.py` | `extract_symptoms()` | O(n/m) avg | Phrase detection |
| Levenshtein (String DP) | `nlp_extractor.py` | `extract_symptoms()` | O(m×n) | Edit distance fuzzy match |

---

*D = diseases (41), S = symptoms per disease (~17), n = input size, m = pattern size*

---

*DAA.md — HealthBridge AI v2.0 | April 2026*
