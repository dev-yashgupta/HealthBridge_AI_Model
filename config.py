"""
HealthBridge_Al -- Central Configuration
All API keys, model paths, and thresholds in one place.
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 1. GROK/GROQ API SETTINGS
# ---------------------------------------------------------------------------
# Auto-load from backend/.env if env var not set
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
if not GROK_API_KEY:
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend", ".env")
    if os.path.exists(_env_path):
        with open(_env_path, encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line.startswith("GROK_API_KEY=") and len(_line) > 14:
                    GROK_API_KEY = _line.split("=", 1)[1].strip()
                    break

# Detect provider: gsk_ prefix = Groq, xai- prefix = xAI
if GROK_API_KEY.startswith("gsk_"):
    GROK_BASE_URL = "https://api.groq.com/openai/v1"
    GROK_MODEL = "llama-3.3-70b-versatile"
else:
    GROK_BASE_URL = "https://api.x.ai/v1"
    GROK_MODEL = "grok-3-mini"

GROK_TIMEOUT = 10          # seconds
GROK_MAX_TOKENS = 300

# ---------------------------------------------------------------------------
# 2. BERT MODEL SETTINGS
# ---------------------------------------------------------------------------
# Use the locally trained model shipped in `training/models/bert_sehatsetu/final`.
BERT_MODEL_PATH = "models/bert_sehatsetu/final"
BERT_HIGH_CONFIDENCE = 0.75     # > 0.75 -> use BERT fully
BERT_MID_CONFIDENCE = 0.40      # >= this -> hybrid mode
# below MID_CONFIDENCE -> keyword fallback

# ---------------------------------------------------------------------------
# 2.1 Hybrid Decision / Score Tuning
# ---------------------------------------------------------------------------
# In hybrid mode we combine:
#   final = (hybrid_bert_weight * bert_score) + (hybrid_keyword_weight * keyword_score)
# where bert_score is already in [0,1] (softmax prob) and keyword_score is normalized to [0,1].
HYBRID_BERT_WEIGHT = 0.6
HYBRID_KEYWORD_WEIGHT = 0.4

# How many candidates to consider for hybrid ranking.
HYBRID_TOP_K_BERT = 3
HYBRID_TOP_K_KEYWORD = 3

# ---------------------------------------------------------------------------
# 3. SUPPORTED LANGUAGES
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = ["hindi", "punjabi", "hinglish", "english", "mixed"]

# ---------------------------------------------------------------------------
# 4. FILE PATHS
# ---------------------------------------------------------------------------
DISEASE_PROFILES_PATH = "data/disease_profiles.json"
LABEL_ENCODINGS_PATH = "label_encodings.json"
REPORTS_DIR = "reports"

# ---------------------------------------------------------------------------
# 5. TRANSLATION SYSTEM PROMPT
# ---------------------------------------------------------------------------
GROK_SYSTEM_PROMPT = """You are a medical translator for an Indian healthcare AI system.

TASK: Translate the patient's symptom description into clear medical English.

RULES:
1. Keep medical terms precise (e.g. "bukhar" -> "fever", "dast" -> "diarrhea")
2. Preserve duration info (e.g. "3 din se" -> "for 3 days")
3. Do NOT diagnose. Only translate symptoms.
4. Output ONLY the translated English text. No explanations, no quotes.
5. If input is already English, clean it up into proper medical English.
6. Handle Hindi, Punjabi, Hinglish, and mixed-language input.

HINDI MAPPINGS:
  bukhar/bukhaar = fever, sar dard = headache, pet dard = stomach pain
  dast = diarrhea, ulti = vomiting, khujli = itching, khansi = cough
  laal daane = rash, sans lene mein takleef = difficulty breathing
  seene mein dard = chest pain, kamar dard = back pain
  thakaan = fatigue, chakkar = dizziness, din = day(s)
  peela = yellow, bhook nahi = loss of appetite
  jalan = burning sensation, sujan = swelling

PUNJABI MAPPINGS:
  bukhaar = fever, sir dard = headache, pet noon vich dard = stomach pain
  sust = loose motion, kharish = itching, dard = pain
  laal daag = rash, sans lene noon vich taklif = difficulty breathing
  chhaati noon vich dard = chest pain, din = day(s), haftey = week(s)"""

# ---------------------------------------------------------------------------
# 6. HINDI / PUNJABI KEYWORD LISTS (for language detection)
# ---------------------------------------------------------------------------
HINDI_KEYWORDS = [
    "bukhar", "bukhaar", "sar dard", "sir dard", "pet dard", "dast",
    "din se", "ho raha", "ho rahi", "hai aur", "bahut", "mein dard",
    "ulti", "khujli", "khansi", "thakaan", "chakkar", "peela", "peeli",
    "bhook", "jalan", "sujan", "kamar", "seene", "pasina", "daane",
    "aankhon", "naak", "gale", "badan", "peshab",
]

PUNJABI_KEYWORDS = [
    "bukhaar", "sir noon", "noon vich", "aa gaya", "aa gayi", "haftey",
    "dard hai ji", "sust", "kharish", "laal daag", "chhaati",
    "sans lene noon", "pet noon", "kamjori", "thakan",
]

HINGLISH_KEYWORDS = [
    "fever", "headache", "pain", "loose motion", "cough", "rash",
    "itching", "vomiting", "breathing", "chest",
]

# ---------------------------------------------------------------------------
# 7. PRINT CONFIG ON IMPORT (debug)
# ---------------------------------------------------------------------------
def print_config():
    """Print current config for debugging."""
    key_status = "SET" if GROK_API_KEY else "NOT SET"
    print(f"[CONFIG] Grok API Key : {key_status}")
    print(f"[CONFIG] Grok Model   : {GROK_MODEL}")
    print(f"[CONFIG] BERT Path    : {BERT_MODEL_PATH}")
    print(f"[CONFIG] High Conf    : {BERT_HIGH_CONFIDENCE}")
    print(f"[CONFIG] Mid Conf     : {BERT_MID_CONFIDENCE}")
