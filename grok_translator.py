"""
HealthBridge_Al -- Grok Translator
Translates Hindi/Punjabi/Hinglish symptoms to medical English via Grok API,
then feeds to BERT model for disease prediction.
"""

import re
import sys
import json
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import (
    GROK_API_KEY, GROK_BASE_URL, GROK_MODEL, GROK_TIMEOUT, GROK_MAX_TOKENS,
    GROK_SYSTEM_PROMPT,
    BERT_HIGH_CONFIDENCE, BERT_MID_CONFIDENCE,
    HINDI_KEYWORDS, PUNJABI_KEYWORDS, HINGLISH_KEYWORDS,
)

# ---------------------------------------------------------------------------
# GROK CLIENT SETUP
# ---------------------------------------------------------------------------
GROK_AVAILABLE = False
_grok_client = None

try:
    from openai import OpenAI
    if GROK_API_KEY:
        _grok_client = OpenAI(api_key=GROK_API_KEY, base_url=GROK_BASE_URL)
        GROK_AVAILABLE = True
        print("[OK] Grok API client ready")
    else:
        print("[WARN] GROK_API_KEY not set. Translation disabled.")
        print("       Set it: $env:GROK_API_KEY='xai-...'")
except ImportError:
    print("[WARN] openai package not installed. Run: pip install openai")
except Exception as e:
    print(f"[WARN] Grok setup failed: {e}")

# ---------------------------------------------------------------------------
# BERT PREDICTOR (lazy import)
# ---------------------------------------------------------------------------
_bert_loaded = False
_predict_disease = None
_extract_symptoms = None

def _ensure_bert():
    """Lazy-load BERT predictor and keyword extractor."""
    global _bert_loaded, _predict_disease, _extract_symptoms
    if _bert_loaded:
        return
    try:
        from nlp_predictor import predict_disease, BERT_AVAILABLE
        from nlp_extractor import extract_symptoms
        _predict_disease = predict_disease if BERT_AVAILABLE else None
        _extract_symptoms = extract_symptoms
    except Exception as e:
        print(f"[WARN] BERT/extractor import failed: {e}")
        _predict_disease = None
        try:
            from nlp_extractor import extract_symptoms
            _extract_symptoms = extract_symptoms
        except:
            _extract_symptoms = None
    _bert_loaded = True


# ============================================================================
# PART A -- LANGUAGE DETECTION
# ============================================================================

def detect_language(text: str) -> str:
    """
    Detect language of symptom text.
    Returns: 'hindi' | 'punjabi' | 'hinglish' | 'english' | 'mixed'
    """
    text_lower = text.lower().strip()
    words = text_lower.split()

    # Count keyword hits
    hindi_score = sum(1 for kw in HINDI_KEYWORDS if kw in text_lower)
    punjabi_score = sum(1 for kw in PUNJABI_KEYWORDS if kw in text_lower)

    # Check for English medical terms
    english_terms = [
        "fever", "headache", "pain", "cough", "diarrhea", "vomiting",
        "rash", "itching", "breathing", "chest", "stomach", "nausea",
        "fatigue", "weakness", "swelling", "infection", "cold",
    ]
    english_score = sum(1 for t in english_terms if t in text_lower)

    # Check for Hinglish markers (mix of Hindi particles + English terms)
    hinglish_markers = ["hai", "ho", "raha", "rahi", "se", "bhi", "aur"]
    hinglish_particles = sum(1 for m in hinglish_markers if m in words)

    # Punjabi has highest priority if detected (it's rarer)
    if punjabi_score >= 2:
        return "punjabi"

    # Pure English check
    if english_score >= 2 and hindi_score == 0 and punjabi_score == 0:
        return "english"

    # Hinglish = English terms + Hindi particles
    if english_score >= 1 and hinglish_particles >= 1:
        return "hinglish"

    # Hindi
    if hindi_score >= 1:
        return "hindi"

    # Mixed fallback
    if hindi_score >= 1 or punjabi_score >= 1 or english_score >= 1:
        return "mixed"

    # Default: try langdetect if available
    try:
        from langdetect import detect as ld_detect
        lang = ld_detect(text)
        lang_map = {"hi": "hindi", "pa": "punjabi", "en": "english"}
        return lang_map.get(lang, "mixed")
    except:
        pass

    return "mixed"


# ============================================================================
# PART B -- GROK API TRANSLATION
# ============================================================================

def translate_to_medical_english(text: str, source_lang: str = None) -> dict:
    """
    Translate symptom text to medical English using Grok API.

    Returns:
        {
            "original": str,
            "translated": str,
            "source_lang": str,
            "success": bool,
            "confidence": float,
            "time_ms": int,
        }
    """
    if source_lang is None:
        source_lang = detect_language(text)

    # If already English, light cleanup only
    if source_lang == "english":
        return {
            "original": text,
            "translated": text.strip(),
            "source_lang": "english",
            "success": True,
            "confidence": 1.0,
            "time_ms": 0,
        }

    # If Grok not available, return original
    if not GROK_AVAILABLE or _grok_client is None:
        return {
            "original": text,
            "translated": text,
            "source_lang": source_lang,
            "success": False,
            "confidence": 0.0,
            "time_ms": 0,
        }

    # Call Grok API
    user_prompt = f"Language: {source_lang}\nPatient says: {text}"
    start = time.time()

    try:
        response = _grok_client.chat.completions.create(
            model=GROK_MODEL,
            messages=[
                {"role": "system", "content": GROK_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=GROK_MAX_TOKENS,
            temperature=0.1,
            timeout=GROK_TIMEOUT,
        )
        elapsed_ms = int((time.time() - start) * 1000)

        translated = response.choices[0].message.content.strip()
        # Clean up any quotes or extra formatting
        translated = translated.strip('"\'')

        # Confidence heuristic: if translated is very different from original, good
        orig_words = set(text.lower().split())
        trans_words = set(translated.lower().split())
        overlap = len(orig_words & trans_words)
        total = max(len(orig_words | trans_words), 1)
        change_ratio = 1.0 - (overlap / total)
        confidence = min(0.95, 0.5 + change_ratio * 0.5)

        return {
            "original": text,
            "translated": translated,
            "source_lang": source_lang,
            "success": True,
            "confidence": round(confidence, 2),
            "time_ms": elapsed_ms,
        }

    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        print(f"[ERROR] Grok translation failed ({elapsed_ms}ms): {e}")
        return {
            "original": text,
            "translated": text,
            "source_lang": source_lang,
            "success": False,
            "confidence": 0.0,
            "time_ms": elapsed_ms,
        }


# ============================================================================
# PART B.1 -- DURATION EXTRACTION FROM TRANSLATED TEXT
# ============================================================================

def extract_duration_from_translation(translated: str) -> int:
    """
    Extract duration in days from translated English text.
    Examples: 'fever for 3 days' -> 3, 'since 2 weeks' -> 14
    Returns -1 if not found.
    """
    text = translated.lower().strip()

    # "X days" / "for X days"
    m = re.search(r"(\d+)\s*days?", text)
    if m:
        return int(m.group(1))

    # "X weeks"
    m = re.search(r"(\d+)\s*weeks?", text)
    if m:
        return int(m.group(1)) * 7

    # "X months"
    m = re.search(r"(\d+)\s*months?", text)
    if m:
        return int(m.group(1)) * 30

    # "since yesterday"
    if "yesterday" in text:
        return 1

    # "since today" / "today"
    if "today" in text or "since this morning" in text:
        return 0

    return -1


# ============================================================================
# PART C -- FULL PREDICTION PIPELINE
# ============================================================================

def predict_with_translation(text: str) -> dict:
    """
    Full pipeline: detect language -> translate -> BERT predict -> merge.

    Returns:
        {
            "method": str,
            "original_text": str,
            "detected_language": str,
            "translated_text": str,
            "translation_confidence": float,
            "bert_disease": str or None,
            "bert_confidence": float,
            "detected_symptoms": dict,
            "top_5": list,
            "grok_used": bool,
            "duration_days": int,
        }
    """
    _ensure_bert()

    # Step 1: Detect language
    source_lang = detect_language(text)

    # Step 2: Translate to medical English
    translation = translate_to_medical_english(text, source_lang)
    grok_used = translation["success"] and source_lang != "english"
    translated_text = translation["translated"]

    # Step 3: BERT prediction on translated text
    bert_result = {"top_disease": None, "confidence": 0.0, "top_5": []}
    if _predict_disease is not None:
        # Try translated text first
        bert_result = _predict_disease(translated_text)

        # If translated confidence is still low, also try original
        if bert_result["confidence"] < BERT_MID_CONFIDENCE and grok_used:
            bert_original = _predict_disease(text)
            if bert_original["confidence"] > bert_result["confidence"]:
                bert_result = bert_original

    # Step 4: Keyword symptom extraction (on original text -- keyword engine
    #          already has Hindi/Hinglish synonyms built in)
    keyword_symptoms = {}
    if _extract_symptoms is not None:
        keyword_symptoms = _extract_symptoms(text)
        # Also extract from translated text and merge
        if grok_used:
            trans_symptoms = _extract_symptoms(translated_text)
            for s, w in trans_symptoms.items():
                if s not in keyword_symptoms:
                    keyword_symptoms[s] = w

    # Step 5: Duration from translation
    duration = extract_duration_from_translation(translated_text)
    if duration < 0:
        # Fallback to original extractor
        try:
            from nlp_extractor import get_duration
            duration = get_duration(text)
        except:
            duration = -1

    # Step 6: Method selection + hybrid ranking (shared logic in nlp_predictor)
    bert_conf = bert_result.get("confidence", 0.0)
    bert_disease = bert_result.get("top_disease")

    try:
        from nlp_predictor import decide_and_build_hybrid_output

        decided = decide_and_build_hybrid_output(
            bert_top5=bert_result.get("top_5", []),
            keyword_symptoms=keyword_symptoms,
        )
        method = decided["method"]
        predictions = decided["predictions"]
        detected_symptoms = decided["detected_symptoms"]
        source = decided.get("source", "")
    except Exception:
        # Hard fallback: keep previous behavior if hybrid helper fails.
        method = "keyword_fallback"
        predictions = []
        detected_symptoms = keyword_symptoms
        source = "keyword_fallback"

    return {
        "method": method,
        "predictions": predictions,
        "original_text": text,
        "detected_language": source_lang,
        "translated_text": translated_text,
        "translation_confidence": translation.get("confidence", 0.0),
        "bert_disease": bert_disease,
        "bert_confidence": bert_conf,
        "detected_symptoms": detected_symptoms,
        "top_5": bert_result.get("top_5", []),
        "grok_used": grok_used,
        "duration_days": duration,
        "source": source,
    }


# ============================================================================
# STANDALONE TEST
# ============================================================================

if __name__ == "__main__":
    from config import print_config
    print_config()
    print()

    tests = [
        "3 din se bukhar hai, sar dard bhi ho raha hai",
        "pet mein dard hai, dast lag gaye hain, ulti ho rahi hai",
        "sans lene mein takleef, chest mein dard",
        "fever for 2 days with headache and body pain",
        "khujli aur rash poore body pe",
    ]

    for t in tests:
        print("-" * 60)
        res = predict_with_translation(t)
        print(f"  Input      : {res['original_text']}")
        print(f"  Language   : {res['detected_language']}")
        print(f"  Translated : {res['translated_text']}")
        print(f"  Grok Used  : {res['grok_used']}")
        print(f"  Method     : {res['method']}")
        if res["bert_disease"]:
            print(f"  BERT       : {res['bert_disease']} ({res['bert_confidence']*100:.1f}%)")
        syms = ", ".join(f"{k}({v})" for k, v in res["detected_symptoms"].items())
        print(f"  Symptoms   : {syms}")
        print()
