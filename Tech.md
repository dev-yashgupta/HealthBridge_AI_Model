# Tech.md — OOPs Concepts
## HealthBridge AI Project

**Project:** HealthBridge AI — Multilingual Medical Symptom Checker  
**Stack:** Python · Node.js · React 19 · SQLite  
**Date:** April 2026

---

## Table of Contents

1. [Encapsulation](#1-encapsulation)
2. [Abstraction](#2-abstraction)
3. [Modularity — Single Responsibility Principle](#3-modularity--single-responsibility-principle)
4. [Composition — "has-a" Relationship](#4-composition--has-a-relationship)
5. [Polymorphism](#5-polymorphism)
6. [Closure — Functional OOPs](#6-closure--functional-oops)
7. [OOPs Summary Table](#7-oops-summary-table)

---

## 1. Encapsulation

**Definition:** Data aur usse operate karne wale functions ko ek unit mein band karna. Internal implementation hide karna, sirf interface expose karna.

---

### 1.1 Encapsulation — Config Module
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

**Applied Principle:**
- API key directly expose nahi hoti — sirf "SET/NOT SET" status dikhta hai
- Saari config ek module mein band hai, baaki code `from config import X` se access karta hai
- Agar threshold change karna ho, sirf `config.py` update karo — baaki code untouched

**Benefit:** Security + maintainability — API keys, model paths, thresholds ek central location mein

---

### 1.2 Encapsulation — DB Bridge Module
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

**Applied Principle:**
- `DB_PATH`, connection management, SQL queries — sab `history_db.py` ke andar encapsulate hain
- `main.py` ko sirf `log_symptoms()` aur `get_history()` call karna hai
- Internal kaise kaam karta hai yeh jaanna zaroori nahi

**Benefit:** Caller doesn't need DB details — agar DB PostgreSQL pe migrate karo, sirf `history_db.py` change karo

---

### 1.3 Encapsulation — React Component State
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

**Applied Principle:**
- Component ka internal state (`symptomsText`, `isLoading`, etc.) bahar se directly access nahi hota
- Sirf rendered JSX expose hota hai
- Yeh React ka core encapsulation pattern hai

**Benefit:** React component isolation — component ki internal state predictable aur controllable rehti hai

---

### 1.4 Encapsulation — API Service Module
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

**Applied Principle:**
- `API_BASE_URL` module-private hai
- HTTP fetch logic, headers, error handling — sab `api.js` mein encapsulate hai
- Components sirf `submitDiagnosis("GUEST", text)` call karte hain

**Benefit:** Single place to change URL — agar backend port change karo, sirf `api.js` update karo

---

## 2. Abstraction

**Definition:** Complex implementation hide karna, sirf essential interface dikhana.

---

### 2.1 Abstraction — diagnose() Function
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

**What's Abstracted:**

```
Caller sees:          diagnose("GUEST", "fever for 3 days")
                              ↓
Inside (hidden):      Groq API call
                      BERT tokenization + inference
                      SQLite log_symptoms()
                      41-disease weighted matching
                      Plain-text report generation
                              ↓
Caller gets:          { "top_disease": "Typhoid", "top_score": 68.4 }
```

**Benefit:** `api_bridge.py` sirf `diagnose(patient_id, symptoms_text)` call karta hai — 8 steps ki complexity completely abstract hai

---

### 2.2 Abstraction — getUrgencyStyle() Utility
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

**Benefit:** `AnalysisResults.jsx` sirf `getUrgencyStyle(state.urgency)` call karta hai — actual hex color codes, CSS class names sab abstract hain

---

### 2.3 Abstraction — spawnDbBridge() Helper
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

**Benefit:** Har route handler mein spawn logic repeat karne ki zaroorat nahi. `spawnDbBridge()` ek abstract interface provide karta hai — payload do, response milega.

---

## 3. Modularity — Single Responsibility Principle

**Definition:** Code ko independent, reusable modules mein divide karna. Har module ek specific responsibility handle kare.

---

### 3.1 Single Responsibility Principle — Python Backend

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

**Benefit:** Agar BERT model change karna ho, sirf `nlp_predictor.py` update karo — baaki code untouched. Agar DB change karna ho, sirf `history_db.py` update karo.

---

### 3.2 Single Responsibility Principle — React Frontend

| Component | Single Responsibility |
|-----------|----------------------|
| `Layout.jsx` | Navigation shell (TopAppBar + BottomNav) |
| `Home.jsx` | Dashboard display only |
| `SymptomChecker.jsx` | Symptom input form only |
| `AnalysisResults.jsx` | Diagnosis results display only |
| `History.jsx` | Symptom timeline + reports display |
| `api.js` | HTTP calls to backend only |
| `urgency.js` | Urgency → CSS color mapping only |

---

## 4. Composition — "has-a" Relationship

**Definition:** Complex objects ko simple objects combine karke banana — inheritance ki jagah composition prefer karna.

---

### 4.1 Composition — Pipeline Modules
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

**Composition Diagram:**

```
main.py (Orchestrator)
    ├── has-a → grok_translator (Translation)
    ├── has-a → nlp_predictor  (BERT AI)
    ├── has-a → nlp_extractor  (Keywords)
    ├── has-a → matcher        (Scoring)
    ├── has-a → history_db     (Database)
    └── has-a → report_generator (Reports)
```

**Benefit:** `main.py` kisi bhi module se inherit nahi karta — instead unhe compose karta hai. Agar kal BERT ki jagah GPT use karna ho, sirf `nlp_predictor.py` replace karo, `main.py` same rahega.

---

### 4.2 Composition — React Component Tree
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

**Composition Diagram:**

```
App
└── Layout (has-a)
    ├── TopAppBar (has-a)
    ├── Outlet → [Home | SymptomChecker | AnalysisResults | History]
    └── BottomNavBar (has-a)
```

**Benefit:** Layout component reusable hai — saare pages iske andar render hote hain. Agar header change karna ho, sirf `Layout.jsx` update karo — saare pages automatically update ho jaate hain.

---

## 5. Polymorphism

**Definition:** Same interface, different behavior — ek function/method alag alag inputs pe alag kaam kare.

---

### 5.1 Polymorphism — NLP Method Selection
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

**Polymorphic Behavior:**

| Input | Method Used | Behavior |
|-------|-------------|----------|
| Any text (Groq available) | `predict_with_translation()` | Translate → BERT → Hybrid |
| Any text (no Groq) | `predict_and_extract()` | BERT only |
| Any text (no BERT) | `extract_symptoms()` | Keyword fallback |

**Benefit:** `diagnose()` function same input (`user_text`) leta hai lekin available AI method ke hisaab se alag pipeline use karta hai. Caller ko pata nahi kaunsa method use ho raha hai — same output format milta hai.

---

### 5.2 Polymorphism — urgency Style Mapping
**File:** `frontend/src/utils/urgency.js`

```javascript
// Same function — different output based on input value
const getUrgencyStyle = (urgency) => URGENCY_COLORS[urgency] ?? URGENCY_COLORS.LOW

// "HIGH"   → red styles   { bg: 'bg-[#ba1a1a]/20', text: 'text-[#ba1a1a]' }
// "MEDIUM" → amber styles { bg: 'bg-[#ffb694]/20', text: 'text-[#ffb694]' }
// "LOW"    → teal styles  { bg: 'bg-[#97f3e2]/20', text: 'text-[#97f3e2]' }
// "UNKNOWN"→ teal styles  (default fallback)
```

**Benefit:** Same function call, different CSS classes return hoti hain based on urgency value. Yeh runtime polymorphism ka example hai.

---

### 5.3 Polymorphism — spawnDbBridge parseMode
**File:** `backend/server.js`

```javascript
function spawnDbBridge(payload, res, parseMode = 'array') {
    proc.on('close', () => {
        if (parseMode === 'array') {
            // Parse as JSON array → []
            res.json(JSON.parse(out.substring(s, e + 1)))
        } else {
            // Parse as JSON object → {}
            res.json(JSON.parse(out.substring(s, e + 1)))
        }
    })
}

// Same function — different parsing behavior
spawnDbBridge({ action: 'history_recent' }, res, 'array')   // returns []
spawnDbBridge({ action: 'history_summary' }, res, 'object') // returns {}
```

**Benefit:** Same `spawnDbBridge()` function `parseMode` parameter ke basis pe alag behavior karta hai — array ya object parse karta hai.

---

## 6. Closure — Functional OOPs

**Definition:** Function apne outer scope ke variables ko "remember" karta hai even after outer function return ho jaaye.

---

### 6.1 Closure — React useState Hook
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

### 6.2 Closure — Module-Level State (Python)
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

## 7. OOPs Summary Table

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

*Tech.md — OOPs Concepts | HealthBridge AI v2.0 | April 2026*
