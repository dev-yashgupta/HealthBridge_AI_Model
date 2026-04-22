# AI_Tool.md — AI Search Algorithms
## HealthBridge AI Project

**Project:** HealthBridge AI — Multilingual Medical Symptom Checker  
**Stack:** Python · PyTorch · HuggingFace · Groq LLaMA · SQLite  
**Date:** April 2026

---

## Table of Contents

1. [Beam Search — BERT Top-K Predictions](#1-beam-search--bert-top-k-predictions)
2. [Greedy Best-First Search — Hybrid Disease Ranking](#2-greedy-best-first-search--hybrid-disease-ranking)
3. [Weighted Graph Search — Disease-Symptom Matching](#3-weighted-graph-search--disease-symptom-matching)
4. [Semantic Search — BERT Transformer Classification](#4-semantic-search--bert-transformer-classification)
5. [Fuzzy Search — Approximate String Matching](#5-fuzzy-search--approximate-string-matching)
6. [Heuristic Search — Language Detection](#6-heuristic-search--language-detection)
7. [RAG Pattern — Retrieval-Augmented Generation](#7-rag-pattern--retrieval-augmented-generation)
8. [Ensemble Method — Multi-Model Soft Voting](#8-ensemble-method--multi-model-soft-voting)
9. [Summary Table](#9-summary-table)

---

## 1. Beam Search — BERT Top-K Predictions

**File:** `nlp_predictor.py` — function `predict_disease()`

```python
top_probs, top_indices = torch.topk(probs, top_k)   # ← Top-K beam search

top_preds = []
for i in range(top_k):
    idx = int(top_indices[i].item())
    disease = id2label.get(idx, str(idx))
    top_preds.append({
        "disease": disease,
        "confidence": round(float(top_probs[i].item()), 4),
    })
```

**Kya karta hai:** BERT model ke softmax output se top-5 highest probability diseases select karta hai.

**How it Works — Beam Visualization:**

```
BERT Softmax Output (41 classes):
Typhoid     → 0.52  ←── Beam 1 (Selected)
Malaria     → 0.41  ←── Beam 2 (Selected)
Dengue      → 0.18  ←── Beam 3 (Selected)
Hepatitis A → 0.14  ←── Beam 4 (Selected)
Jaundice    → 0.11  ←── Beam 5 (Selected)
Common Cold → 0.06      (Pruned — outside top-5)
Diabetes    → 0.04      (Pruned)
... (36 more)           (Pruned)

torch.topk(probs, k=5) → Returns top 5 beams
```

**Kyon use kiya:**
- Pure greedy search (sirf top-1) = agar BERT galat ho toh koi backup nahi
- Beam search (top-5) = multiple candidates available hain hybrid scoring ke liye
- `torch.topk()` efficiently top-K values find karta hai O(n log k) mein
- Medical diagnosis mein multiple hypotheses maintain karna zaroori hai

**Algorithm:** Top-K Selection (Beam Search variant)  
**Complexity:** O(n log k) — n = 41 classes, k = 5

---

## 2. Greedy Best-First Search — Hybrid Disease Ranking

**File:** `nlp_predictor.py` — function `_combine_bert_and_keyword_hybrid()`

```python
# Greedy Best-First: always expand the highest-score candidate
combined.sort(key=lambda x: x["confidence"], reverse=True)

# Return top candidates — greedy selection
out = [{"disease": x["disease"], "confidence": x["confidence"]} for x in combined]
return out[:3]
```

**Heuristic Function:**

```
h(disease) = (0.6 × bert_score) + (0.4 × keyword_score)

# Penalty if no keyword evidence:
if keyword_score == 0:
    h(disease) *= 0.5
```

**Search Visualization:**

```
Candidate List (after hybrid scoring):
Typhoid     → h = 0.68  ←── Best-first: select this
Malaria     → h = 0.55  ←── Select 2nd
Dengue      → h = 0.31  ←── Select 3rd
Hepatitis   → h = 0.22      (Pruned — not in top-3)
```

**Kyon use kiya:**
- Greedy best-first = heuristic-guided search
- Heuristic = combined confidence score (BERT × 0.6 + keyword × 0.4)
- No backtracking needed — medical diagnosis mein top candidates sufficient hain
- A* search se simpler — no path cost, sirf heuristic value

**vs. A* Search:**

| Feature | Greedy Best-First | A* Search |
|---------|------------------|-----------|
| Uses heuristic | ✅ Yes | ✅ Yes |
| Uses path cost (g) | ❌ No | ✅ Yes |
| Optimal? | ❌ Not guaranteed | ✅ Yes |
| Speed | Faster | Slower |
| Used here because | Small candidate set (41) | Not needed |

**Algorithm:** Greedy Best-First Search  
**Complexity:** O(n log n) sort + O(1) selection

---

## 3. Weighted Graph Search — Disease-Symptom Matching

**File:** `matcher.py` — function `match_diseases()`

```python
# Disease-symptom relationship = weighted bipartite graph
# Node: disease ←→ symptom
# Edge weight: severity_weight (1-7)

for disease, profile in DISEASE_PROFILES.items():
    sym_weight = dict(zip(dis_syms, dis_weights))  # ← weighted edges
    
    matched_score = 0.0
    for sym, d_wt in sym_weight.items():
        if sym in patient_syms:
            matched_score += d_wt              # ← edge weight accumulation
            if patient_weight[sym] >= d_wt:
                matched_score += d_wt * 0.15   # ← bonus weight
    
    coverage = (matched_score / total_score) * 100  # ← path score
```

**Graph Model:**

```
Patient Symptoms          Disease Nodes
(Left Nodes)              (Right Nodes)
                          
high_fever ──── w=7 ──→  Typhoid    (score: 7+3+5=15)
headache   ──── w=3 ──→  Typhoid    
nausea     ──── w=5 ──→  Typhoid    

high_fever ──── w=7 ──→  Malaria    (score: 7+5=12)
nausea     ──── w=5 ──→  Malaria    

high_fever ──── w=7 ──→  Dengue     (score: 7=7)

Coverage = matched_weight / total_disease_weight × 100
Typhoid: 15/30 = 50% → MEDIUM urgency
```

**Kyon use kiya:**
- Simple symptom count (unweighted) = "fever" aur "chest_pain" equal weight milta
- Weighted matching = "chest_pain" (weight 7) > "mild_fever" (weight 3) — clinically correct
- Bipartite graph model: left nodes = patient symptoms, right nodes = disease symptoms, edges = weights
- Coverage score = normalized path weight

**Urgency Thresholds:**

| Coverage Score | Urgency Level |
|---------------|---------------|
| ≥ 70% | 🔴 HIGH |
| 40–69% | 🟡 MEDIUM |
| < 40% | 🟢 LOW |

**Algorithm:** Weighted Bipartite Graph Matching  
**Complexity:** O(D × S) — D = 41 diseases, S = ~17 symptoms per disease

---

## 4. Semantic Search — BERT Transformer Classification

**File:** `nlp_predictor.py` — function `predict_disease()`

```python
inputs = tokenizer(
    text,
    return_tensors="pt",
    max_length=128,
    truncation=True,
    padding=True,
).to(device)

with torch.no_grad():
    outputs = model(**inputs)   # ← BERT forward pass

probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
```

**How BERT Semantic Search Works:**

```
Input Text: "fever for 3 days with headache"
     ↓
Tokenization: [CLS] fever for 3 days with headache [SEP]
     ↓
BERT Embedding: 768-dimensional vector per token
     ↓
Self-Attention (12 heads × 12 layers):
  "fever" ←→ "days" ←→ "headache" (context captured)
     ↓
[CLS] token → Classification Head (768 → 41)
     ↓
Softmax → Probability over 41 diseases
     ↓
"high temperature for days" → Typhoid: 0.52 (semantic match)
```

**vs Keyword Search:**

| Type | "fever" matches | "high temperature" matches | "bukhar" matches |
|------|----------------|---------------------------|-----------------|
| Keyword Search | ✅ Yes (exact) | ❌ No (different words) | ❌ No (Hindi) |
| Semantic (BERT) | ✅ Yes | ✅ Yes (same meaning) | ✅ Yes (after translation) |

**Kyon use kiya:**
- Keyword search = exact match only ("fever" matches "fever", not "high temperature")
- Semantic search = meaning-based match ("high temperature" → fever class)
- BERT contextual embeddings capture semantic similarity
- "3 din se bukhar" (Hindi) → translated → BERT understands medical context

**Algorithm:** Semantic Search via BERT Transformer (Multi-Head Self-Attention)  
**Complexity:** O(n²) attention — n = sequence length (max 128 tokens)

---

## 5. Fuzzy Search — Approximate String Matching

**File:** `nlp_extractor.py` — function `extract_symptoms()`

```python
from thefuzz import fuzz, process as fuzz_process

# Fuzzy search: find closest match in symptom vocabulary
match, score = fuzz_process.extractOne(
    token,           # query: "faver"
    ALL_SYMPTOMS,    # search space: ["high_fever", "headache", ...]
    scorer=fuzz.ratio
)
if score >= 80:      # 80% similarity threshold
    found[match] = WEIGHT_MAP.get(match, 1)
```

**Levenshtein Distance — Edit Distance Example:**

```
Query: "faver"
Target: "fever"

    ""  f  e  v  e  r
""   0  1  2  3  4  5
f    1  0  1  2  3  4
a    2  1  1  2  3  4
v    3  2  2  1  2  3
e    4  3  2  2  1  2
r    5  4  3  3  2  1

Edit Distance = 1 (1 substitution: a → e)
Similarity = (5 - 1) / 5 = 80% ✓ (threshold met → match!)
```

**Common Indian Misspellings Handled:**

| User Types | Corrected To | Edit Distance |
|-----------|-------------|---------------|
| "faver" | "high_fever" | 1 |
| "headach" | "headache" | 1 |
| "vommiting" | "vomiting" | 1 |
| "diarea" | "diarrhoea" | 3 |
| "stomac pain" | "stomach_pain" | 1 |

**Kyon use kiya:**
- Exact search: "faver" → no match (wrong)
- Fuzzy search: "faver" → "high_fever" (80% similarity) → correct match
- Indian users frequently misspell: "headach", "vommiting", "diarea"
- Levenshtein distance = edit distance between strings (DP algorithm internally)

**Algorithm:** Fuzzy String Search (Levenshtein Distance — Dynamic Programming)  
**Complexity:** O(m × n) per comparison — m, n = string lengths

---

## 6. Heuristic Search — Language Detection

**File:** `grok_translator.py` — function `detect_language()`

```python
def detect_language(text: str) -> str:
    # Heuristic 1: Count Hindi keyword hits
    hindi_score = sum(1 for kw in HINDI_KEYWORDS if kw in text_lower)
    
    # Heuristic 2: Count Punjabi keyword hits
    punjabi_score = sum(1 for kw in PUNJABI_KEYWORDS if kw in text_lower)
    
    # Heuristic 3: Count English medical terms
    english_score = sum(1 for t in english_terms if t in text_lower)
    
    # Heuristic 4: Hinglish markers
    hinglish_particles = sum(1 for m in hinglish_markers if m in words)
    
    # Decision based on heuristic scores
    if punjabi_score >= 2: return "punjabi"
    if english_score >= 2 and hindi_score == 0: return "english"
    if english_score >= 1 and hinglish_particles >= 1: return "hinglish"
    if hindi_score >= 1: return "hindi"
    return "mixed"
```

**Heuristic Decision Tree Visualization:**

```
Input: "3 din se bukhar hai, headache bhi hai"
          ↓
[Heuristic Scoring]
  Hindi keywords:    ["din", "se", "bukhar", "hai"] → score = 4
  Punjabi keywords:  []                              → score = 0
  English terms:     ["headache"]                   → score = 1
  Hinglish particles: ["hai", "se"]                 → score = 2
          ↓
[Decision Rules]
  punjabi_score >= 2?        NO
  english_score >= 2?        NO  
  english >= 1 AND hinglish >= 1? YES → "hinglish"
          ↓
Result: "hinglish" → Send to Groq for translation
```

**Language Priority Order (Why):**

| Priority | Language | Reason |
|----------|----------|--------|
| 1st | Punjabi | Rarest, most specific keywords |
| 2nd | English | Pure English = no translation needed |
| 3rd | Hinglish | Mixed signal (English + Hindi particles) |
| 4th | Hindi | Mono-Hindi input |
| Last | Mixed | Fallback for edge cases |

**Kyon use kiya:**
- Rule-based exact matching = "agar sirf Hindi words hain toh Hindi" — too rigid
- Heuristic scoring = multiple weak signals combine karke strong decision
- Multi-criteria approach handles real-world messy Hinglish inputs

**Algorithm:** Heuristic Search (Multi-criteria scoring)  
**Complexity:** O(k × n) — k = keyword lists size, n = text length

---

## 7. RAG Pattern — Retrieval-Augmented Generation

**File:** `grok_translator.py` + `matcher.py`

```python
# Step 1: RETRIEVE — keyword extraction from input
keyword_symptoms = _extract_symptoms(text)           # ← Retrieval

# Step 2: AUGMENT — add retrieved context to BERT query  
bert_result = _predict_disease(translated_text)      # ← Generation with context

# Step 3: COMBINE — RAG-style fusion
decided = decide_and_build_hybrid_output(
    bert_top5=bert_result.get("top_5", []),
    keyword_symptoms=keyword_symptoms,               # ← Augmented context
)
```

**RAG Architecture in HealthBridge:**

```
User Input: "3 din se bukhar hai, sar dard bhi"
                    │
        ┌───────────┴───────────┐
        │ RETRIEVE              │ GENERATE
        ↓                       ↓
nlp_extractor.py          Groq Translation
keyword_symptoms =        "fever for 3 days,
{high_fever: 7,            headache also"
 headache: 3}                   │
        │                       ↓
        │                  nlp_predictor.py
        │                  BERT Inference
        │                  Typhoid: 0.52
        │                  Malaria: 0.41
        │                       │
        └───────────┬───────────┘
                    │ AUGMENT + COMBINE
                    ↓
            decide_and_build_hybrid_output()
            final = 0.6×bert + 0.4×keyword
                    │
                    ↓
            Typhoid: 0.65 (final hybrid score)
```

**vs Traditional RAG:**

| Feature | Traditional RAG | HealthBridge RAG |
|---------|----------------|-----------------|
| Retrieval | Vector DB similarity search | Keyword/synonym matching |
| Generation | LLM (GPT/Claude) | BERT Classifier |
| Augmentation | Retrieved docs in prompt | Retrieved keywords in scoring |
| Fusion | Prompt injection | Weighted score combination |

**Kyon use kiya:**
- Pure BERT (generation only) = hallucination risk, low confidence in medical domain
- Pure keyword (retrieval only) = misses semantic meaning ("high temperature" not caught)
- RAG hybrid = retrieval grounds the generation, generation adds semantic understanding
- Medical domain mein grounding zaroori hai — BERT ko keyword evidence chahiye validation ke liye

**Algorithm:** Retrieval-Augmented Generation (RAG) — simplified variant  
**Complexity:** O(retrieval) + O(generation) = O(n) + O(n²)

---

## 8. Ensemble Method — Multi-Model Soft Voting

**File:** `nlp_predictor.py` — function `decide_and_build_hybrid_output()`

```python
# Ensemble: combine multiple models' predictions
bert_map     = {x["disease"]: float(x["confidence"]) for x in bert_top3}
keyword_map  = {x["disease"]: float(x["keyword_score_norm"]) for x in keyword_rankings}

# Weighted ensemble (Soft Voting)
for disease in candidates:
    bert_score    = bert_map.get(disease, 0.0)
    keyword_score = keyword_map.get(disease, 0.0)
    
    # Weighted average — ensemble combination
    final_score = (HYBRID_BERT_WEIGHT * bert_score) + (HYBRID_KEYWORD_WEIGHT * keyword_score)
    
    # Disagreement penalty — ensemble penalizes lone predictions
    if keyword_score == 0.0:
        final_score *= 0.5
```

**Ensemble Formula:**

```
final_score = (0.6 × BERT_score) + (0.4 × keyword_score)

Penalty:  if keyword_score == 0 → final_score × 0.5

Example:
  Typhoid:
    BERT = 0.52, keyword = 0.70
    final = (0.6 × 0.52) + (0.4 × 0.70) = 0.312 + 0.280 = 0.592

  Tuberculosis:
    BERT = 0.45, keyword = 0.0 (no keyword evidence!)
    final = (0.6 × 0.45) + 0 = 0.27 × 0.5 = 0.135 (penalized)

Winner: Typhoid (0.592) ✓
```

**vs Other Ensemble Types:**

| Type | How | HealthBridge Uses |
|------|-----|-------------------|
| Hard Voting | Majority vote | ❌ No |
| Soft Voting | Weighted probability avg | ✅ Yes |
| Stacking | Meta-learner on top | ❌ No |
| Bagging | Same model, different data | ❌ No |
| Boosting | Sequential error correction | ❌ No |

**Confidence Thresholds — When to Use Ensemble:**

```
BERT Confidence > 0.75?
    YES → Use BERT alone (high confidence, no ensemble needed)
    
BERT Confidence 0.40–0.75?
    → Use Weighted Ensemble (hybrid mode)
    
BERT Confidence < 0.40?
    → Use keyword scores only (BERT too uncertain)
```

**Kyon use kiya:**
- Single model (BERT alone) = higher variance, lower reliability in medical domain
- Ensemble = multiple models agree → higher confidence, lower false positive rate
- BERT weight 0.6 > keyword weight 0.4 — BERT more trusted but not exclusive
- Disagreement penalty (keyword_score=0) — agar sirf BERT agree kare aur keyword evidence nahi, score reduce karo
- Medical diagnosis mein false positives dangerous hain — ensemble reduces risk

**Algorithm:** Weighted Ensemble (Soft Voting with Disagreement Penalty)  
**Complexity:** O(n) — n = candidate diseases

---

## 9. Summary Table

| AI Algorithm | File | Function | Complexity | Purpose |
|-------------|------|----------|-----------|---------|
| Beam Search (Top-K) | `nlp_predictor.py` | `predict_disease()` | O(n log k) | BERT top-5 disease candidates |
| Greedy Best-First Search | `nlp_predictor.py` | `_combine_bert_and_keyword_hybrid()` | O(n log n) | Hybrid top-3 selection |
| Weighted Graph Search | `matcher.py` | `match_diseases()` | O(D × S) | Symptom-disease weighted matching |
| Semantic Search (BERT) | `nlp_predictor.py` | `predict_disease()` | O(n²) attention | Meaning-based disease classification |
| Fuzzy Search (Levenshtein) | `nlp_extractor.py` | `extract_symptoms()` | O(m × n) | Misspelling-tolerant symptom search |
| Heuristic Search | `grok_translator.py` | `detect_language()` | O(k × n) | Multi-signal language detection |
| RAG Pattern | `grok_translator.py` | `predict_with_translation()` | O(n) + O(n²) | Retrieval + generation fusion |
| Ensemble (Soft Voting) | `nlp_predictor.py` | `decide_and_build_hybrid_output()` | O(n) | BERT + keyword weighted combination |

---

### Pipeline Overview — All AI Algorithms Together

```
User Input (Hindi/Hinglish/English)
        │
        ▼
[Heuristic Search]          ← Language Detection
detect_language()
        │
        ├──── "english"? → Skip translation
        └──── Other? → Groq LLaMA-3.3-70B translation
                │
                ▼
        [Semantic Search]   ← BERT Transformer
        predict_disease()
        BERT top-5 via [Beam Search]
                │
                ▼
        [Fuzzy Search]      ← Approximate Matching
        extract_symptoms()
        Levenshtein Distance
                │
                ▼
        [RAG Fusion]        ← Retrieval + Generation combined
        decide_and_build_hybrid_output()
        [Ensemble / Weighted Voting]
                │
                ▼
        [Weighted Graph Search]  ← Disease-Symptom Bipartite Matching
        match_with_history()
                │
                ▼
        [Greedy Best-First] ← Final disease rankings
        Top-3 Results + Urgency
                │
                ▼
        JSON Response → React Frontend
```

---

*D = diseases (41), S = symptoms/disease (~17), n = input size, k = beam width (5), m = string length*

---

*AI_Tool.md — AI Search Algorithms | HealthBridge AI v2.0 | April 2026*
