
# HealthBridge AI — Full Project Report

**Project Name:** HealthBridge AI  
**Version:** 2.0  
**Type:** Full-Stack AI-Powered Medical Symptom Checker  
**Stack:** Python · Node.js/Express · React 19 · SQLite · PostgreSQL  
**Date:** April 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Application Architecture](#2-application-architecture)
3. [AI Model — How It Works](#3-ai-model--how-it-works)
4. [NLP Pipeline — Step by Step](#4-nlp-pipeline--step-by-step)
5. [Data Layers](#5-data-layers)
6. [Database Design](#6-database-design)
7. [Backend API](#7-backend-api)
8. [Frontend Application](#8-frontend-application)
9. [Technologies Used](#9-technologies-used)
10. [File Structure](#10-file-structure)
11. [Data Flow Diagrams](#11-data-flow-diagrams)
12. [Key Algorithms](#12-key-algorithms)
13. [Limitations & Future Work](#13-limitations--future-work)

---

## 1. Project Overview

HealthBridge AI is a multilingual medical symptom checker designed for Indian users. It accepts symptom descriptions in **Hindi, Punjabi, Hinglish, or English**, processes them through a multi-stage AI pipeline, and returns a structured diagnosis with disease matches, urgency level, recommended tests, and a full medical report.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| Multilingual Input | Hindi, Punjabi, Hinglish, English, mixed |
| AI Translation | Groq LLaMA-3.3-70B translates non-English input to medical English |
| BERT Classification | Custom-trained BERT model (`bert_sehatsetu`) classifies diseases |
| Keyword Matching | Rule-based fallback with 200+ Hindi/English symptom synonyms |
| Hybrid Scoring | Combines BERT confidence + keyword match score |
| History Awareness | Past 30 days of symptoms boost current diagnosis accuracy |
| Report Generation | Full plain-text medical report saved to file + SQLite DB |
| Web Application | React 19 SPA with dark glassmorphism UI |

---

## 2. Application Architecture

The system follows a **three-tier architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (React SPA)                       │
│  SymptomChecker → AnalysisResults → History → MedicalHistory│
│  Vite + React 19 + React Router v7 + Tailwind CSS v4        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP (fetch API)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              EXPRESS SERVER (Node.js :5000)                  │
│  POST /api/diagnose                                          │
│  GET  /api/history/:id/recent                               │
│  GET  /api/history/:id                                      │
│  GET  /api/reports/:id                                      │
└──────────┬──────────────────────────┬───────────────────────┘
           │ spawn (stdin/stdout)      │ spawn (stdin/stdout)
           ▼                           ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│   api_bridge.py      │   │        db_bridge.py              │
│   (AI Pipeline)      │   │   (Lightweight DB reads only)    │
│                      │   │   No AI imports — fast response  │
│  main.py → diagnose()│   └──────────────┬───────────────────┘
│  ├─ grok_translator  │                  │
│  ├─ nlp_predictor    │                  ▼
│  ├─ nlp_extractor    │   ┌──────────────────────────────────┐
│  ├─ matcher          │   │     SQLite: data/healthbridge.db │
│  ├─ history_db       │   │  Tables: symptom_log, reports    │
│  └─ report_generator │   └──────────────────────────────────┘
└──────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI MODELS & DATA                           │
│  models/bert_sehatsetu/final/  — Custom BERT (41 diseases)  │
│  data/disease_profiles.json    — 41 disease symptom profiles│
│  data/label_mapping.json       — Disease label encodings    │
│  Groq API (LLaMA-3.3-70B)     — Translation + NLP          │
└─────────────────────────────────────────────────────────────┘
```

### Why Two Python Bridges?

| Bridge | Purpose | Speed |
|--------|---------|-------|
| `api_bridge.py` | Full AI pipeline (diagnosis) | 5–15 seconds (loads BERT + calls Groq) |
| `db_bridge.py` | SQLite reads only (history/reports) | < 200ms (no AI imports) |

Using `api_bridge.py` for history reads caused 10–15 second timeouts. `db_bridge.py` solves this by importing only `sqlite3` — zero AI overhead.

---

## 3. AI Model — How It Works

### Model: `bert_sehatsetu`

A custom fine-tuned **BERT** (Bidirectional Encoder Representations from Transformers) model trained on Indian medical symptom-disease datasets.

| Property | Value |
|----------|-------|
| Base Architecture | BERT (bert-base-uncased variant) |
| Task | Multi-class text classification |
| Classes | 41 diseases |
| Input | Symptom description text (max 128 tokens) |
| Output | Probability distribution over 41 disease classes |
| Training Data | Kaggle disease-symptom dataset + HuggingFace symptom-disease dataset + Mendeley SymbiPredict 2022 |
| Model Path | `models/bert_sehatsetu/final/` |
| Files | `config.json`, `model.safetensors`, `tokenizer.json`, `tokenizer_config.json` |

### 41 Supported Diseases

Fungal infection, Allergy, GERD, Chronic cholestasis, Drug Reaction, Peptic ulcer disease, AIDS, Diabetes, Gastroenteritis, Bronchial Asthma, Hypertension, Migraine, Cervical spondylosis, Paralysis (brain hemorrhage), Jaundice, Malaria, Chicken pox, Dengue, Typhoid, Hepatitis A/B/C/D/E, Alcoholic hepatitis, Tuberculosis, Common Cold, Pneumonia, Piles, Heart attack, Varicose veins, Hypothyroidism, Hyperthyroidism, Hypoglycemia, Osteoarthritis, Arthritis, Vertigo, Acne, UTI, Psoriasis, Impetigo.

### Confidence Thresholds

```python
BERT_HIGH_CONFIDENCE = 0.75   # > 75% → use BERT result fully
BERT_MID_CONFIDENCE  = 0.40   # 40–75% → hybrid mode (BERT + keyword)
                               # < 40% → keyword fallback only
```

### Hybrid Scoring Formula

When BERT confidence is between 40–75%, the system combines both scores:

```
final_score = (0.6 × bert_score) + (0.4 × keyword_score_normalized)
```

If a disease has no keyword evidence (`keyword_score = 0`), its final score is penalized by 50% to prevent BERT hallucinations.

---

## 4. NLP Pipeline — Step by Step

When a user submits symptoms, the following 8-step pipeline runs:

```
User Input (Hindi/English/Hinglish)
         │
         ▼
Step 1: Language Detection (grok_translator.py)
         │  Detects: hindi / punjabi / hinglish / english / mixed
         │  Uses keyword scoring + langdetect library
         ▼
Step 2: Translation (Groq API — LLaMA-3.3-70B)
         │  Non-English → Medical English
         │  e.g. "3 din se bukhar hai" → "fever for 3 days"
         │  English input: passed through unchanged
         ▼
Step 3: BERT Prediction (nlp_predictor.py)
         │  Tokenizes translated text (max 128 tokens)
         │  Runs through bert_sehatsetu model
         │  Returns top-5 disease predictions with confidence scores
         ▼
Step 4: Keyword Extraction (nlp_extractor.py)
         │  Matches 200+ Hindi/English synonyms against input
         │  Also runs on translated text and merges results
         │  Returns {symptom_name: severity_weight} dict
         │  Optional: fuzzy matching via thefuzz library
         ▼
Step 5: Duration Extraction (nlp_extractor.py → get_duration())
         │  Regex patterns for: "X din se", "X days", "kal se", "aaj"
         │  Returns integer days (-1 = not specified)
         ▼
Step 6: Method Decision (nlp_predictor.py → decide_method_from_bert())
         │  HIGH confidence (>75%) → "bert" mode
         │  MID confidence (40–75%) → "hybrid" mode
         │  LOW confidence (<40%) → "keyword_fallback" mode
         ▼
Step 7: Disease Matching (matcher.py → match_with_history())
         │  Merges current symptoms with last 30 days history
         │  Weighted scoring against 41 disease profiles
         │  History boost: past symptoms increase match score
         │  Urgency: HIGH (≥70%), MEDIUM (40–69%), LOW (<40%)
         ▼
Step 8: Report Generation (report_generator.py)
         │  Structured English report with:
         │  - Patient info, duration, NLP method
         │  - Detected symptoms with severity weights
         │  - Top 3 disease matches with scores
         │  - Recommended diagnostic tests
         │  - Doctor advice based on urgency
         ▼
Output: JSON response → Express → React frontend
        + Report saved to: reports/ folder + SQLite DB
```

---

## 5. Data Layers

The project uses **three data layers** for training and inference:

### Layer 1 — Raw Source Datasets (`data/layer1/`)

| Dataset | Source | Records | Purpose |
|---------|--------|---------|---------|
| `hf_symptom_disease/` | HuggingFace | ~1,200 | Symptom-disease pairs (train/test split) |
| `kaggle_disease_symptom/` | Kaggle (itachi9604) | 4,920 | Disease profiles with symptom severity weights |

The Kaggle dataset includes:
- `dataset.csv` — disease → symptom mappings
- `Symptom-severity.csv` — symptom severity weights (1–7 scale)
- `symptom_Description.csv` — disease descriptions
- `symptom_precaution.csv` — precautions per disease

### Layer 2 — Processed/Combined Data (`data/layer2/`)

| File | Description |
|------|-------------|
| `combined_training_data.csv` | Merged training data from all sources |
| `symptom-disease-train-dataset.csv` | Final training split |
| `symptom-disease-test-dataset.csv` | Final test split |
| `mapping.json` | Disease name normalization map |
| `mendeley/symbipredict_2022.csv` | Mendeley SymbiPredict dataset (additional validation) |

### Layer 3 — Model Artifacts (`data/layer3/`, `models/`)

| Artifact | Location | Description |
|----------|----------|-------------|
| BERT model weights | `models/bert_sehatsetu/final/model.safetensors` | Fine-tuned BERT weights |
| Tokenizer | `models/bert_sehatsetu/final/tokenizer.json` | BERT tokenizer config |
| Model config | `models/bert_sehatsetu/final/config.json` | Architecture config (41 labels) |
| Disease profiles | `data/disease_profiles.json` | 41 diseases × symptoms × weights |
| Label mapping | `data/label_mapping.json` | Integer ID → disease name |

### Runtime Data (`data/`)

| File | Description |
|------|-------------|
| `data/healthbridge.db` | SQLite database (symptom_log + reports tables) |
| `data/disease_profiles.json` | Loaded at startup by matcher.py |

---

## 6. Database Design

### Database: SQLite (`data/healthbridge.db`)

Chosen over PostgreSQL for the AI pipeline because:
- No server required — file-based, zero configuration
- Fast reads for history lookups during diagnosis
- No connection pool overhead
- Portable — single file, easy to backup

PostgreSQL is still connected (for future multi-user expansion) but the AI pipeline uses SQLite exclusively.

### Table: `symptom_log`

Stores every symptom detected during a diagnosis session.

```sql
CREATE TABLE symptom_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT    NOT NULL,        -- e.g. "GUEST", "P001"
    symptom         TEXT    NOT NULL,        -- canonical name e.g. "high_fever"
    severity_weight INTEGER,                 -- 1–7 scale from disease profiles
    duration_days   INTEGER DEFAULT 0,       -- -1 = not specified, 0 = today
    logged_at       TEXT                     -- ISO timestamp "2026-04-18 15:39:35"
);
```

**Usage:** Each diagnosis logs N rows (one per detected symptom). The matcher reads the last 30 days to build a history-aware symptom profile.

### Table: `reports`

Stores the full generated medical report for each diagnosis.

```sql
CREATE TABLE reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id  TEXT NOT NULL,
    top_disease TEXT,           -- Primary diagnosis e.g. "Malaria"
    top_score   REAL,           -- Confidence 0–100
    urgency     TEXT,           -- "HIGH" | "MEDIUM" | "LOW"
    report_text TEXT,           -- Full plain-text report
    file_path   TEXT,           -- Path to .txt file in reports/
    created_at  TEXT            -- ISO timestamp
);
```

**Usage:** Every diagnosis saves a report here. The History page's "Reports" tab reads from this table via `db_bridge.py`.

### History Boost Mechanism

When a new diagnosis runs, `match_with_history()` in `matcher.py`:

1. Fetches all symptoms logged in the last **30 days** for the patient
2. Builds a `history_syms` dict with the highest weight per symptom
3. Merges with current symptoms (current takes precedence)
4. Runs disease matching on the merged set
5. Tags results with `history_boost: True` if any matched symptom came from history

This means a patient who had `high_fever` yesterday and reports only `headache` today will still get Malaria/Typhoid in their top matches — because the history fills in the missing fever symptom.

---

## 7. Backend API

### Server: Express.js (`backend/server.js`)

| Endpoint | Method | Handler | Description |
|----------|--------|---------|-------------|
| `/api/diagnose` | POST | `api_bridge.py` | Full AI diagnosis pipeline |
| `/api/history/:id/recent` | GET | `db_bridge.py` | Last 50 symptom log entries |
| `/api/history/:id` | GET | `db_bridge.py` | Symptom history summary grouped by date |
| `/api/reports/:id` | GET | `db_bridge.py` | All saved diagnosis reports |

### Request/Response: POST `/api/diagnose`

**Request:**
```json
{
  "patient_id": "GUEST",
  "symptoms": "Fever for 2 days, headache, nausea"
}
```

**Response (success):**
```json
{
  "status": "success",
  "patient_id": "GUEST",
  "detected_symptoms": { "high_fever": 7, "headache": 3, "nausea": 5 },
  "duration_days": 2,
  "top_disease": "Typhoid",
  "top_score": 68.4,
  "urgency": "MEDIUM",
  "matched_symptoms": ["high_fever", "headache", "nausea"],
  "predictions": [
    { "disease": "Typhoid", "confidence": 0.684 },
    { "disease": "Malaria", "confidence": 0.521 }
  ],
  "report": "=== HEALTHBRIDGE AI -- MEDICAL REPORT ===\n...",
  "saved_path": "reports/GUEST_20260418_153935.txt",
  "method_used": "keyword_fallback",
  "bert_suggestion": "Tuberculosis",
  "bert_confidence": 0.18
}
```

### Python Bridge Communication

Express spawns Python as a child process and communicates via **stdin/stdout JSON**:

```
Express → JSON payload → Python stdin
Python stdout → JSON result → Express → HTTP response
```

This avoids the overhead of a persistent Python server while keeping the AI pipeline stateless and restartable.

---

## 8. Frontend Application

### Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.4 | UI framework |
| React Router | v7 | Client-side routing |
| Tailwind CSS | v4 | Utility-first styling |
| Vite | v8 | Build tool + dev server |
| @tailwindcss/vite | v4 | Tailwind v4 Vite plugin |

### Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Home.jsx` | Dashboard with health stats bento grid |
| `/checker` | `SymptomChecker.jsx` | Symptom input form with quick-chips, duration, severity |
| `/results` | `AnalysisResults.jsx` | Diagnosis results with urgency badge, charts, report |
| `/history` | `History.jsx` | Symptom timeline + Reports tab |
| `/history/medical` | `MedicalHistory.jsx` | Static medical profile (conditions, medications, allergies, surgeries) |
| `/profile` | `Profile.jsx` | User profile stub |

### Design System

The UI uses a **dark glassmorphism** aesthetic defined in `frontend/src/index.css`:

- Background: `#1a1b21` (deep navy-black)
- Primary accent: `#22d3ee` (neon cyan)
- Secondary: `#94f0df` (teal)
- Error/High urgency: `#ba1a1a` (red)
- Medium urgency: `#ffb694` (amber)
- Low urgency: `#97f3e2` (teal)
- Glass panels: `backdrop-filter: blur(20px)` + `rgba(26,27,33,0.8)` background
- Typography: Public Sans (headlines) + Inter (body)
- Icons: Google Material Symbols Outlined

### API Service (`frontend/src/services/api.js`)

```javascript
submitDiagnosis(patientId, symptoms)  // POST /api/diagnose
fetchHistory(patientId)               // GET /api/history/:id/recent
fetchHistorySummary(patientId)        // GET /api/history/:id
fetchReports(patientId)               // GET /api/reports/:id
```

---

## 9. Technologies Used

### AI / Machine Learning

| Technology | Version | Role |
|------------|---------|------|
| PyTorch | latest | BERT model inference |
| Transformers (HuggingFace) | latest | BERT tokenizer + model loading |
| Groq API (LLaMA-3.3-70B) | cloud | Hindi/Punjabi → Medical English translation |
| thefuzz | latest | Fuzzy symptom name matching |
| langdetect | latest | Language detection fallback |

### Backend

| Technology | Version | Role |
|------------|---------|------|
| Python | 3.x (Anaconda) | AI pipeline runtime |
| Node.js | latest | Express server runtime |
| Express.js | v5 | REST API server |
| SQLite3 (Python) | built-in | Symptom log + reports storage |
| PostgreSQL + pg | v8 | Connected (future multi-user) |
| dotenv / dotenvx | latest | Environment variable management |
| cors | v2 | Cross-origin request handling |

### Frontend

| Technology | Version | Role |
|------------|---------|------|
| React | 19.2.4 | UI framework |
| React Router DOM | v7 | SPA routing |
| Tailwind CSS | v4 | Utility CSS |
| Vite | v8 | Build tool |
| Vitest | v4 | Test runner |
| fast-check | v4 | Property-based testing |
| @testing-library/react | v16 | Component testing |

---

## 10. File Structure

```
E:\training\
├── api_bridge.py          # Express → AI pipeline bridge (stdin/stdout JSON)
├── db_bridge.py           # Express → SQLite bridge (lightweight, no AI)
├── main.py                # Core diagnose() function — orchestrates pipeline
├── config.py              # All config: API keys, model paths, thresholds
├── grok_translator.py     # Language detection + Groq translation + BERT hybrid
├── nlp_predictor.py       # BERT inference + hybrid scoring logic
├── nlp_extractor.py       # Keyword/synonym symptom extraction + duration parsing
├── matcher.py             # Weighted disease matching + history-aware scoring
├── history_db.py          # SQLite CRUD for symptom_log table
├── report_generator.py    # Plain-text medical report generation + DB save
├── .env                   # API keys, DB credentials (not in git)
│
├── backend/
│   ├── server.js          # Express REST API server
│   └── package.json       # Node.js dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Route definitions
│   │   ├── main.jsx                   # React entry point
│   │   ├── index.css                  # Tailwind v4 design tokens
│   │   ├── components/
│   │   │   └── Layout.jsx             # TopAppBar + BottomNavBar
│   │   ├── pages/
│   │   │   ├── Home.jsx               # Dashboard
│   │   │   ├── SymptomChecker.jsx     # Symptom input form
│   │   │   ├── AnalysisResults.jsx    # Diagnosis results display
│   │   │   ├── History.jsx            # Symptom timeline + Reports tab
│   │   │   ├── MedicalHistory.jsx     # Static medical profile
│   │   │   └── Profile.jsx            # Profile stub
│   │   ├── services/
│   │   │   └── api.js                 # HTTP client functions
│   │   └── utils/
│   │       └── urgency.js             # Urgency color mapping
│   ├── index.html                     # HTML entry (Google Fonts loaded here)
│   └── vite.config.js                 # Vite + Tailwind + Vitest config
│
├── data/
│   ├── healthbridge.db                # SQLite database
│   ├── disease_profiles.json          # 41 disease symptom profiles
│   ├── label_mapping.json             # Disease label encodings
│   ├── layer1/                        # Raw source datasets
│   ├── layer2/                        # Processed/combined datasets
│   └── layer3/                        # Model artifacts (README)
│
├── models/
│   └── bert_sehatsetu/final/          # Custom trained BERT model
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       └── tokenizer_config.json
│
├── reports/                           # Generated .txt report files
├── training_scripts/                  # BERT training notebooks + scripts
└── .kiro/specs/                       # Kiro spec files
```

---

## 11. Data Flow Diagrams

### Diagnosis Request Flow

```
User types: "3 din se bukhar hai, sar dard"
Duration: "2-3 days ago" selected
Severity: "Moderate" selected
                │
                ▼ (SymptomChecker.jsx)
Full text: "3 din se bukhar hai, sar dard, for 2 days, moderate symptoms"
                │
                ▼ POST /api/diagnose
                │
                ▼ (api_bridge.py → main.py → diagnose())
                │
    ┌───────────┴────────────┐
    │                        │
    ▼                        ▼
grok_translator.py      nlp_extractor.py
detect_language()       extract_symptoms()
→ "hinglish"            → {high_fever:7, headache:3}
    │                        │
    ▼                        │
Groq API call                │
→ "fever for 3 days,         │
   headache"                 │
    │                        │
    ▼                        │
nlp_predictor.py             │
BERT inference               │
→ Typhoid: 0.52              │
→ Malaria: 0.41              │
    │                        │
    └───────────┬────────────┘
                │
                ▼ decide_and_build_hybrid_output()
                │ method = "hybrid" (0.40 ≤ conf ≤ 0.75)
                │ final = 0.6×bert + 0.4×keyword
                │
                ▼ history_db.py → log_symptoms()
                │ Saves to SQLite symptom_log
                │
                ▼ matcher.py → match_with_history()
                │ Merges with last 30 days history
                │ Scores all 41 diseases
                │ Returns top 5 matches
                │
                ▼ report_generator.py → generate_report()
                │ Builds English plain-text report
                │ Saves to reports/ + SQLite reports table
                │
                ▼ JSON response to Express → React
                │
                ▼ navigate("/results", { state: result })
                │
                ▼ AnalysisResults.jsx renders:
                  - Top disease + confidence bar
                  - BERT secondary match
                  - Detected symptom chips
                  - Urgency badge (color-coded)
                  - Recommended tests
                  - Doctor advice
                  - Print button
```

### History Read Flow (Fast Path)

```
User opens /history
        │
        ▼ fetchHistory("GUEST") + fetchReports("GUEST")
        │ (parallel Promise.all)
        │
        ▼ GET /api/history/GUEST/recent
        │ GET /api/reports/GUEST
        │
        ▼ db_bridge.py (no AI imports)
        │ Opens data/healthbridge.db
        │ SELECT from symptom_log / reports
        │ Returns JSON in < 200ms
        │
        ▼ History.jsx renders:
          Symptoms tab: alternating timeline grouped by date
          Reports tab: expandable cards with structured data
```

---

## 12. Key Algorithms

### Weighted Disease Matching (`matcher.py`)

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

### Hybrid Scoring (`nlp_predictor.py`)

```python
# Combine BERT top-3 with keyword matcher top-3
for each candidate disease:
    bert_score    = bert_predictions.get(disease, 0.0)   # [0,1]
    keyword_score = keyword_rankings.get(disease, 0.0)   # normalized [0,1]
    
    final = (0.6 × bert_score) + (0.4 × keyword_score)
    
    # Penalize diseases with no keyword evidence
    if keyword_score == 0:
        final *= 0.5

sort by final score descending → top prediction
```

### Duration Extraction (`nlp_extractor.py`)

```python
# Regex patterns (priority order):
"kal se" / "yesterday"     → 1 day
"ghante" / "hour"          → 0 days (same day)
"X hafte"                  → X × 7 days
"X din" / "X days"         → X days
"aaj" / "today"            → 0 days
no match                   → -1 (not specified)
```

---

## 13. Limitations & Future Work

### Current Limitations

| Limitation | Description |
|------------|-------------|
| Single user | All data stored under "GUEST" patient ID — no authentication |
| BERT accuracy | Custom BERT trained on limited data; confidence often < 40% (keyword fallback) |
| No real-time | Python spawned per request — 5–15 second diagnosis latency |
| Static medical profile | MedicalHistory page uses hardcoded data, not from DB |
| No image input | Cannot process medical images or lab reports |
| English-only report | Report is in English; Hindi output not yet supported |

### Planned Improvements

| Feature | Priority |
|---------|----------|
| User authentication (JWT) | High |
| Persistent user profiles | High |
| BERT model retraining with larger dataset | High |
| Persistent Python process (FastAPI) to eliminate spawn overhead | Medium |
| Hindi/Urdu report output | Medium |
| Lab report PDF parsing | Low |
| Doctor appointment booking integration | Low |
| Mobile app (React Native) | Low |

---

## Summary

HealthBridge AI is a production-ready prototype of a multilingual AI medical assistant. It combines:

- **Groq LLaMA-3.3-70B** for real-time Hindi/Punjabi → Medical English translation
- **Custom BERT** (`bert_sehatsetu`) for neural disease classification
- **Weighted keyword matching** as a reliable fallback
- **History-aware diagnosis** that improves accuracy using past symptom data
- **Full-stack web application** with React 19 + Express + SQLite

The system is designed to be accessible to Indian users who may describe symptoms in their native language, making AI-assisted healthcare more inclusive.

---

*Report generated: April 2026 | HealthBridge AI v2.0*


---

## 14. Algorithms Used — With File Names & Reasons

Yeh section DSA project submission ke liye hai. Har algorithm ke saath:
- **File name** jahan implement hai
- **Kya karta hai** (purpose)
- **Kyon use kiya** (justification)
- **Time complexity**

---

### 14.1 Searching Algorithms

---

#### Linear Search — Symptom Synonym Lookup
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

#### Binary Search (Implicit) — Disease Profile Lookup
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
- Set use karne se effectively O(1) per symptom check — total O(41 × 17) = O(697) constant

**Complexity:** O(D × S) — D = diseases (41), S = avg symptoms per disease (~17)

---

#### Fuzzy Search — Misspelled Symptom Matching
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

### 14.2 Sorting Algorithms

---

#### Sort by Score (Descending) — Disease Ranking
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

#### Sort by Length (Descending) — Longest Phrase First
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

#### Sort by Date (Descending) — History Timeline
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
- Map order preserve karta hai insertion order — sorted entries correct order mein render hoti hain

**Algorithm:** Timsort (JavaScript V8 engine)  
**Complexity:** O(n log n) — n = number of date groups

---

#### Sort by Confidence (Descending) — Hybrid Predictions
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

#### Sort by Created Date (Descending) — Reports List
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

### 14.3 Hashing / Dictionary Algorithms

---

#### Hash Map — Symptom Weight Lookup
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

#### Hash Map — Disease Profile Storage
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

#### Hash Set — Patient Symptom Membership Check
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

### 14.4 Graph / Tree Algorithms

---

#### Decision Tree (Logic) — NLP Method Selection
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

**Algorithm:** Decision Tree (threshold-based)  
**Complexity:** O(1)

---

#### Trie (Implicit) — Regex Pattern Matching
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

### 14.5 Greedy Algorithms

---

#### Greedy Merge — History-Aware Symptom Merging
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

#### Greedy Top-K Selection — Top Disease Results
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

### 14.6 Dynamic Programming (Memoization)

---

#### Memoization — BERT Model Lazy Loading
**File:** `grok_translator.py` — function `_ensure_bert()`

```python
_bert_loaded = False   # ← Memoization flag
_predict_disease = None

def _ensure_bert():
    global _bert_loaded, _predict_disease
    if _bert_loaded:          # ← Already loaded? Skip
        return
    # ... load BERT model ...
    _bert_loaded = True       # ← Mark as loaded
```

**Kya karta hai:** BERT model sirf pehli baar load hota hai. Subsequent calls mein already loaded model use hota hai.

**Kyon use kiya:**
- BERT model load karna 3–5 seconds leta hai (500MB+ weights)
- Bina memoization ke: har diagnosis pe 3–5 second overhead
- With memoization: sirf pehli baar load, phir instant
- Python process lifetime mein model memory mein rehta hai

**Algorithm:** Memoization (lazy initialization)  
**Complexity:** First call O(model_size), subsequent calls O(1)

---

### 14.7 String Algorithms

---

#### String Matching — Phrase Detection
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

#### String Tokenization — Fuzzy Match Preprocessing
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

### Summary Table — All Algorithms

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
| Memoization | `grok_translator.py` | `_ensure_bert()` | O(1) after init | BERT lazy loading |
| Boyer-Moore (String) | `nlp_extractor.py` | `extract_symptoms()` | O(n/m) avg | Phrase detection |
| Weighted Scoring | `matcher.py` | `match_diseases()` | O(D×S) | Disease confidence score |
| Hybrid Scoring | `nlp_predictor.py` | `_combine_bert_and_keyword_hybrid()` | O(n) | BERT + keyword fusion |

---

*D = diseases (41), S = symptoms per disease (~17), n = input size, m = pattern size*


---

## 15. OOPs Concepts — Kahan Kahan Use Kiye

Yeh project Python + JavaScript mein hai. Dono languages mein OOPs concepts apply hue hain.

---

### 15.1 Encapsulation

**Definition:** Data aur usse operate karne wale functions ko ek unit mein band karna. Internal implementation hide karna, sirf interface expose karna.

---

#### Encapsulation — Config Module
**File:** `config.py`

```python
# Saari configuration ek jagah encapsulate hai
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
BERT_MODEL_PATH = "models/bert_sehatsetu/final"
BERT_HIGH_CONFIDENCE = 0.75
HYBRID_BERT_WEIGHT = 0.6
HYBRID_KEYWORD_WEIGHT = 0.4

def print_config():
    """Internal state ko controlled way mein expose karta hai"""
    key_status = "SET" if GROK_API_KEY else "NOT SET"
    print(f"[CONFIG] Grok API Key : {key_status}")  # Key value hide, sirf status
```

**Kyon:** API key directly expose nahi hoti — sirf "SET/NOT SET" status dikhta hai. Saari config ek module mein band hai, baaki code `from config import X` se access karta hai.

---

#### Encapsulation — DB Bridge Module
**File:** `history_db.py`

```python
# Internal DB path hide hai
DB_PATH = "data/healthbridge.db"   # private to module

# Public interface — caller ko DB path jaanna zaroori nahi
def log_symptoms(patient_id: str, symptoms_dict: dict, duration_days: int = 0) -> int:
    conn = sqlite3.connect(DB_PATH)   # internal detail
    # ...

def get_history(patient_id: str, days: int = 7) -> list:
    conn = sqlite3.connect(DB_PATH)   # internal detail
    # ...
```

**Kyon:** `DB_PATH`, connection management, SQL queries — sab `history_db.py` ke andar encapsulate hain. `main.py` ko sirf `log_symptoms()` aur `get_history()` call karna hai — internal kaise kaam karta hai yeh jaanna zaroori nahi.

---

#### Encapsulation — React Component State
**File:** `frontend/src/pages/SymptomChecker.jsx`

```javascript
export default function SymptomChecker() {
  // State encapsulated inside component — bahar se access nahi
  const [symptomsText, setSymptomsText] = useState('')
  const [isLoading, setIsLoading]       = useState(false)
  const [error, setError]               = useState(null)
  const [duration, setDuration]         = useState('Started today')
  const [severity, setSeverity]         = useState('Moderate')

  // Internal function — component ke andar hi use hoti hai
  const handleChipClick = (label) => { ... }
  const handleSubmit    = async () => { ... }

  // Sirf JSX return hota hai — internal state bahar nahi jaati
  return ( <main>...</main> )
}
```

**Kyon:** Component ka internal state (`symptomsText`, `isLoading`, etc.) bahar se directly access nahi hota. Sirf rendered JSX expose hota hai. Yeh React ka core encapsulation pattern hai.

---

#### Encapsulation — API Service Module
**File:** `frontend/src/services/api.js`

```javascript
const API_BASE_URL = 'http://localhost:5000/api'  // private constant

// Public functions — caller ko base URL jaanna zaroori nahi
export const submitDiagnosis = async (patientId, symptoms) => {
    const response = await fetch(`${API_BASE_URL}/diagnose`, { ... })
    // Error handling encapsulated here
    if (!response.ok) throw new Error('Diagnosis failed')
    return response.json()
}
```

**Kyon:** `API_BASE_URL` module-private hai. HTTP fetch logic, headers, error handling — sab `api.js` mein encapsulate hai. Components sirf `submitDiagnosis("GUEST", text)` call karte hain.

---

### 15.2 Abstraction

**Definition:** Complex implementation hide karna, sirf essential interface dikhana.

---

#### Abstraction — diagnose() Function
**File:** `main.py`

```python
def diagnose(patient_id: str, user_text: str) -> dict:
    """
    8-step pipeline ko ek simple function call mein abstract kiya.
    Caller ko andar ki complexity jaanni zaroori nahi.
    """
    # Step 1: Language detect + translate (grok_translator)
    # Step 2: BERT predict (nlp_predictor)
    # Step 3: Keyword extract (nlp_extractor)
    # Step 4: Duration extract
    # Step 5: DB log (history_db)
    # Step 6: Disease match (matcher)
    # Step 7: Report generate (report_generator)
    # Step 8: Save report
    return { "status": "success", "top_disease": ..., ... }
```

**Kyon:** `api_bridge.py` sirf `diagnose(patient_id, symptoms_text)` call karta hai — 8 steps ki complexity completely abstract hai. Caller ko BERT, Groq, SQLite kuch bhi jaanna zaroori nahi.

---

#### Abstraction — getUrgencyStyle() Utility
**File:** `frontend/src/utils/urgency.js`

```javascript
const URGENCY_COLORS = {
    LOW:    { bg: 'bg-[#97f3e2]/20', text: 'text-[#97f3e2]', border: 'border-[#97f3e2]/30' },
    MEDIUM: { bg: 'bg-[#ffb694]/20', text: 'text-[#ffb694]', border: 'border-[#ffb694]/30' },
    HIGH:   { bg: 'bg-[#ba1a1a]/20', text: 'text-[#ba1a1a]', border: 'border-[#ba1a1a]/30' },
}

// Abstract interface — caller ko color codes jaanne ki zaroorat nahi
export const getUrgencyStyle = (urgency) => URGENCY_COLORS[urgency] ?? URGENCY_COLORS.LOW
```

**Kyon:** `AnalysisResults.jsx` sirf `getUrgencyStyle(state.urgency)` call karta hai — actual hex color codes, CSS class names sab abstract hain. Agar colors change karne ho toh sirf `urgency.js` update karo.

---

#### Abstraction — spawnDbBridge() Helper
**File:** `backend/server.js`

```javascript
// Complex spawn logic abstract kiya ek reusable function mein
function spawnDbBridge(payload, res, parseMode = 'array') {
    const proc = spawn(pythonExe, [scriptPath], { ... })
    // stdout collect, parse, respond — sab andar
    proc.stdin.write(JSON.stringify(payload))
    proc.stdin.end()
}

// Usage — 1 line mein complex operation
app.get('/api/history/:patient_id/recent', (req, res) => {
    spawnDbBridge({ action: 'history_recent', patient_id: req.params.patient_id }, res, 'array')
})
```

**Kyon:** Har route handler mein spawn logic repeat karne ki zaroorat nahi. `spawnDbBridge()` ek abstract interface provide karta hai — payload do, response milega.

---

### 15.3 Modularity (Module Pattern — OOPs ka practical form)

**Definition:** Code ko independent, reusable modules mein divide karna. Har module ek specific responsibility handle kare.

---

#### Single Responsibility Principle
**Files:** Har Python file ek kaam karta hai

| File | Single Responsibility |
|------|----------------------|
| `config.py` | Sirf configuration store karna |
| `nlp_extractor.py` | Sirf symptom extraction + duration parsing |
| `grok_translator.py` | Sirf language detection + translation |
| `nlp_predictor.py` | Sirf BERT inference + hybrid scoring |
| `matcher.py` | Sirf disease matching + scoring |
| `history_db.py` | Sirf SQLite CRUD operations |
| `report_generator.py` | Sirf report generation + saving |
| `api_bridge.py` | Sirf Express ↔ AI pipeline bridge |
| `db_bridge.py` | Sirf Express ↔ SQLite bridge |
| `main.py` | Sirf pipeline orchestration |

**Kyon:** Agar BERT model change karna ho, sirf `nlp_predictor.py` update karo — baaki code untouched. Agar DB change karna ho, sirf `history_db.py` update karo.

---

### 15.4 Composition (OOPs — "has-a" relationship)

**Definition:** Complex objects ko simple objects combine karke banana — inheritance ki jagah composition prefer karna.

---

#### Composition — Pipeline Modules
**File:** `main.py`

```python
# diagnose() function composed of multiple modules
from grok_translator  import predict_with_translation   # has-a translator
from nlp_predictor    import predict_and_extract         # has-a predictor
from nlp_extractor    import extract_symptoms, get_duration  # has-a extractor
from matcher          import match_with_history          # has-a matcher
from history_db       import log_symptoms, get_history_summary  # has-a DB
from report_generator import generate_report, save_report  # has-a reporter
```

**Kyon:** `main.py` kisi bhi module se inherit nahi karta — instead unhe compose karta hai. Agar kal BERT ki jagah GPT use karna ho, sirf `nlp_predictor.py` replace karo, `main.py` same rahega.

---

#### Composition — React Component Tree
**File:** `frontend/src/App.jsx`, `frontend/src/components/Layout.jsx`

```javascript
// App composed of Layout + Pages
function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>   {/* Layout has-a Outlet */}
                <Route index element={<Home />} />
                <Route path="checker" element={<SymptomChecker />} />
                <Route path="results" element={<AnalysisResults />} />
                <Route path="history" element={<History />} />
            </Route>
        </Routes>
    )
}

// Layout composed of TopAppBar + BottomNavBar + Outlet
export default function Layout() {
    return (
        <div>
            <header>...</header>      {/* TopAppBar */}
            <Outlet />                {/* Page content */}
            <nav>...</nav>            {/* BottomNavBar */}
        </div>
    )
}
```

**Kyon:** Layout component reusable hai — saare pages iske andar render hote hain. Agar header change karna ho, sirf `Layout.jsx` update karo — saare pages automatically update ho jaate hain.

---

### 15.5 Polymorphism

**Definition:** Same interface, different behavior — ek function/method alag alag inputs pe alag kaam kare.

---

#### Polymorphism — NLP Method Selection
**File:** `main.py` + `grok_translator.py` + `nlp_predictor.py`

```python
# Same interface — diagnose() — different behavior based on available method
if GROK_AVAILABLE:
    result = predict_with_translation(user_text)   # Grok + BERT behavior
elif NLP_AVAILABLE:
    result = predict_and_extract(user_text)         # BERT-only behavior
else:
    detected_symptoms = extract_symptoms(user_text) # Keyword-only behavior
```

**Kyon:** `diagnose()` function same input (`user_text`) leta hai lekin available AI method ke hisaab se alag pipeline use karta hai. Caller ko pata nahi kaunsa method use ho raha hai — same output format milta hai.

---

#### Polymorphism — urgency Style Mapping
**File:** `frontend/src/utils/urgency.js`

```javascript
// Same function — different output based on input value
const getUrgencyStyle = (urgency) => URGENCY_COLORS[urgency] ?? URGENCY_COLORS.LOW

// "HIGH"   → red styles
// "MEDIUM" → amber styles
// "LOW"    → teal styles
// "UNKNOWN" → teal styles (default fallback)
```

**Kyon:** Same function call, different CSS classes return hoti hain based on urgency value. Yeh runtime polymorphism ka example hai.

---

#### Polymorphism — spawnDbBridge parseMode
**File:** `backend/server.js`

```javascript
function spawnDbBridge(payload, res, parseMode = 'array') {
    proc.on('close', () => {
        if (parseMode === 'array') {
            // Parse as JSON array
            res.json(JSON.parse(out.substring(s, e + 1)))
        } else {
            // Parse as JSON object
            res.json(JSON.parse(out.substring(s, e + 1)))
        }
    })
}

// Same function — different parsing behavior
spawnDbBridge({ action: 'history_recent' }, res, 'array')   // returns []
spawnDbBridge({ action: 'history_summary' }, res, 'object') // returns {}
```

**Kyon:** Same `spawnDbBridge()` function `parseMode` parameter ke basis pe alag behavior karta hai — array ya object parse karta hai.

---

### 15.6 Closure (Functional OOPs)

**Definition:** Function apne outer scope ke variables ko "remember" karta hai even after outer function return ho jaaye.

---

#### Closure — React useState Hook
**File:** `frontend/src/pages/SymptomChecker.jsx`

```javascript
export default function SymptomChecker() {
    const [symptomsText, setSymptomsText] = useState('')

    // handleChipClick closes over setSymptomsText
    const handleChipClick = (label) => {
        setSymptomsText(prev =>
            prev.trim() === '' ? label : prev + ' ' + label
        )
    }

    // handleSubmit closes over symptomsText, setIsLoading, setError, navigate
    const handleSubmit = async () => {
        setIsLoading(true)
        const result = await submitDiagnosis("GUEST", symptomsText)  // ← closure
        navigate("/results", { state: result })
    }
}
```

**Kyon:** `handleSubmit` function `symptomsText` ko close over karta hai — jab button click hota hai tab current value use hoti hai. Yeh React hooks ka fundamental pattern hai.

---

#### Closure — Module-Level State (Python)
**File:** `grok_translator.py`

```python
_bert_loaded = False      # module-level state
_predict_disease = None   # module-level state

def _ensure_bert():
    global _bert_loaded, _predict_disease   # closes over module state
    if _bert_loaded:
        return
    from nlp_predictor import predict_disease
    _predict_disease = predict_disease
    _bert_loaded = True

def predict_with_translation(text: str) -> dict:
    _ensure_bert()                    # uses closed-over state
    if _predict_disease is not None:
        bert_result = _predict_disease(translated_text)  # ← closure
```

**Kyon:** `predict_with_translation()` function `_predict_disease` variable ko close over karta hai jo module level pe store hai. Yeh Python mein module-level closure pattern hai.

---

### OOPs Summary Table

| OOPs Concept | File(s) | Where Applied | Benefit |
|-------------|---------|---------------|---------|
| Encapsulation | `config.py` | API key hide, config bundled | Security + maintainability |
| Encapsulation | `history_db.py` | DB path + SQL hidden | Caller doesn't need DB details |
| Encapsulation | `SymptomChecker.jsx` | Component state private | React component isolation |
| Encapsulation | `api.js` | API_BASE_URL private | Single place to change URL |
| Abstraction | `main.py` | `diagnose()` hides 8 steps | Simple interface for complex pipeline |
| Abstraction | `urgency.js` | `getUrgencyStyle()` hides colors | UI logic separated from data |
| Abstraction | `server.js` | `spawnDbBridge()` hides spawn | DRY code, reusable helper |
| Modularity (SRP) | All `.py` files | One file = one responsibility | Easy to maintain/replace |
| Composition | `main.py` | Pipeline composed of modules | Flexible, replaceable parts |
| Composition | `App.jsx` | Layout + Pages composed | Reusable layout component |
| Polymorphism | `main.py` | Same `diagnose()`, 3 AI modes | Transparent method switching |
| Polymorphism | `urgency.js` | Same function, 4 outputs | Extensible color mapping |
| Polymorphism | `server.js` | `spawnDbBridge()` parseMode | Reusable with different outputs |
| Closure | `SymptomChecker.jsx` | `handleSubmit` closes over state | React hooks pattern |
| Closure | `grok_translator.py` | Module-level BERT state | Lazy loading with memory |

---

## 16. AI Search Algorithms — Kahan Kahan Use Kiye

Yeh section specifically AI/ML search techniques cover karta hai jo is project mein use hue hain.

---

### 16.1 Beam Search (Implicit) — BERT Top-K Predictions

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

**Kyon use kiya:**
- Pure greedy search (sirf top-1) = agar BERT galat ho toh koi backup nahi
- Beam search (top-5) = multiple candidates available hain hybrid scoring ke liye
- `torch.topk()` efficiently top-K values find karta hai O(n log k) mein
- Medical diagnosis mein multiple hypotheses maintain karna zaroori hai

**Algorithm:** Top-K Selection (Beam Search variant)  
**Complexity:** O(n log k) — n = 41 classes, k = 5

---

### 16.2 Greedy Best-First Search — Hybrid Disease Ranking

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
- A* search se simpler — no path cost, sirf heuristic value

**Algorithm:** Greedy Best-First Search  
**Complexity:** O(n log n) sort + O(1) selection

---

### 16.3 Weighted Graph Search — Disease-Symptom Matching

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

**Kya karta hai:** Patient symptoms aur disease profiles ke beech weighted matching karta hai — jaise weighted graph mein path score calculate karna.

**Kyon use kiya:**
- Simple symptom count (unweighted) = "fever" aur "chest_pain" equal weight milta
- Weighted matching = "chest_pain" (weight 7) > "mild_fever" (weight 3) — clinically correct
- Bipartite graph model: left nodes = patient symptoms, right nodes = disease symptoms, edges = weights
- Coverage score = normalized path weight

**Algorithm:** Weighted Bipartite Graph Matching  
**Complexity:** O(D × S) — D = 41 diseases, S = ~17 symptoms per disease

---

### 16.4 Semantic Search — BERT Embedding-Based Classification

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

**Kya karta hai:** Input text ko 768-dimensional embedding space mein map karta hai, phir 41 disease classes mein classify karta hai.

**Kyon use kiya:**
- Keyword search = exact match only ("fever" matches "fever", not "high temperature")
- Semantic search = meaning-based match ("high temperature" → fever class)
- BERT contextual embeddings capture semantic similarity
- "3 din se bukhar" (Hindi) → translated → BERT understands medical context

**Algorithm:** Semantic Search via BERT Transformer (Attention Mechanism)  
**Complexity:** O(n²) attention — n = sequence length (max 128 tokens)

---

### 16.5 Fuzzy Search — Approximate String Matching

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

**Kya karta hai:** Misspelled ya approximate symptom names ko correct canonical names se match karta hai.

**Kyon use kiya:**
- Exact search: "faver" → no match (wrong)
- Fuzzy search: "faver" → "high_fever" (80% similarity) → correct match
- Indian users frequently misspell: "headach", "vommiting", "diarea"
- Levenshtein distance = edit distance between strings

**Algorithm:** Fuzzy String Search (Levenshtein Distance)  
**Complexity:** O(m × n) per comparison — m, n = string lengths

---

### 16.6 Heuristic Search — Language Detection

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

**Kya karta hai:** Multiple heuristics combine karke language detect karta hai — exact rules nahi, approximate scoring.

**Kyon use kiya:**
- Rule-based exact matching = "agar sirf Hindi words hain toh Hindi" — too rigid
- Heuristic scoring = multiple weak signals combine karke strong decision
- Punjabi highest priority (rarer, more specific keywords)
- Hinglish = English terms + Hindi particles (both present)

**Algorithm:** Heuristic Search (Multi-criteria scoring)  
**Complexity:** O(k × n) — k = keyword lists size, n = text length

---

### 16.7 Retrieval-Augmented Generation (RAG) Pattern

**File:** `grok_translator.py` + `matcher.py`

```python
# Step 1: Retrieve — keyword extraction from input
keyword_symptoms = _extract_symptoms(text)           # ← Retrieval

# Step 2: Augment — add retrieved context to BERT query
bert_result = _predict_disease(translated_text)      # ← Generation with context

# Step 3: Combine — RAG-style fusion
decided = decide_and_build_hybrid_output(
    bert_top5=bert_result.get("top_5", []),
    keyword_symptoms=keyword_symptoms,               # ← Augmented context
)
```

**Kya karta hai:** Keyword retrieval se extracted symptoms ko BERT neural prediction ke saath combine karta hai — RAG pattern ka simplified version.

**Kyon use kiya:**
- Pure BERT (generation only) = hallucination risk, low confidence
- Pure keyword (retrieval only) = misses semantic meaning
- RAG hybrid = retrieval grounds the generation, generation adds semantic understanding
- Medical domain mein grounding zaroori hai — BERT ko keyword evidence chahiye

**Algorithm:** Retrieval-Augmented Generation (RAG) — simplified  
**Complexity:** O(retrieval) + O(generation) = O(n) + O(n²)

---

### 16.8 Ensemble Method — Multi-Model Voting

**File:** `nlp_predictor.py` — function `decide_and_build_hybrid_output()`

```python
# Ensemble: combine multiple models' predictions
bert_map     = {x["disease"]: float(x["confidence"]) for x in bert_top3}
keyword_map  = {x["disease"]: float(x["keyword_score_norm"]) for x in keyword_rankings}

# Weighted ensemble voting
for disease in candidates:
    bert_score    = bert_map.get(disease, 0.0)
    keyword_score = keyword_map.get(disease, 0.0)
    
    # Weighted average — ensemble combination
    final_score = (HYBRID_BERT_WEIGHT * bert_score) + (HYBRID_KEYWORD_WEIGHT * keyword_score)
    
    # Penalize if no keyword evidence (ensemble disagreement penalty)
    if keyword_score == 0.0:
        final_score *= 0.5
```

**Kya karta hai:** BERT neural model aur keyword rule-based model ke predictions ko weighted ensemble se combine karta hai.

**Kyon use kiya:**
- Single model = higher variance, lower reliability
- Ensemble = multiple models agree → higher confidence
- BERT weight 0.6 > keyword weight 0.4 — BERT more trusted but not exclusive
- Disagreement penalty (keyword_score=0) — agar sirf BERT agree kare, score reduce karo

**Algorithm:** Weighted Ensemble (Soft Voting)  
**Complexity:** O(n) — n = candidate diseases

---

### AI Search Algorithms Summary Table

| AI Algorithm | File | Function | Purpose |
|-------------|------|----------|---------|
| Beam Search (Top-K) | `nlp_predictor.py` | `predict_disease()` | BERT top-5 disease candidates |
| Greedy Best-First | `nlp_predictor.py` | `_combine_bert_and_keyword_hybrid()` | Hybrid top-3 selection |
| Weighted Graph Search | `matcher.py` | `match_diseases()` | Symptom-disease weighted matching |
| Semantic Search (BERT) | `nlp_predictor.py` | `predict_disease()` | Meaning-based disease classification |
| Fuzzy Search (Levenshtein) | `nlp_extractor.py` | `extract_symptoms()` | Misspelling-tolerant symptom search |
| Heuristic Search | `grok_translator.py` | `detect_language()` | Multi-signal language detection |
| RAG Pattern | `grok_translator.py` | `predict_with_translation()` | Retrieval + generation fusion |
| Ensemble (Soft Voting) | `nlp_predictor.py` | `decide_and_build_hybrid_output()` | BERT + keyword weighted combination |

---

*Sections 15 (OOPs) aur 16 (AI Search) added — April 2026 | HealthBridge AI v2.0*
