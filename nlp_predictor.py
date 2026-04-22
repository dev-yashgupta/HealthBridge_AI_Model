import os
import json
import torch

from config import (
    BERT_MODEL_PATH,
    DISEASE_PROFILES_PATH,
    BERT_HIGH_CONFIDENCE,
    BERT_MID_CONFIDENCE,
    HYBRID_BERT_WEIGHT,
    HYBRID_KEYWORD_WEIGHT,
    HYBRID_TOP_K_BERT,
    HYBRID_TOP_K_KEYWORD,
)

BERT_AVAILABLE = False
tokenizer = None
model = None
id2label = {}
device = "cpu"

# Debug logs helpful for tuning thresholds / weights.
# Set `HEALTHBRIDGE_DEBUG_HYBRID_LOGS=0` to silence.
DEBUG_HYBRID_LOGS = os.environ.get("HEALTHBRIDGE_DEBUG_HYBRID_LOGS", "1") == "1"


def _project_dir() -> str:
    # training/nlp_predictor.py -> project root is training/
    return os.path.dirname(os.path.abspath(__file__))


def _load_label_encodings() -> dict:
    """Best-effort loader for label_encodings.json across repo locations."""
    base_dir = _project_dir()
    candidates = [
        os.path.join(base_dir, "label_encodings.json"),
        os.path.join(base_dir, "unused_legacy", "label_encodings.json"),
        os.path.join(base_dir, "archive", "label_encodings.json"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(BERT_MODEL_PATH)
    model.eval()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    # Prefer model config id2label if present; else fall back to label_encodings.json.
    label_data = _load_label_encodings()
    if hasattr(model, "config") and getattr(model.config, "id2label", None):
        id2label = {int(k): v for k, v in model.config.id2label.items()}
    elif "id2label" in label_data:
        id2label = {int(k): v for k, v in label_data["id2label"].items()}
    elif "diseases" in label_data:
        id2label = {i: v for i, v in enumerate(label_data["diseases"])}
    else:
        id2label = {}

    if not id2label:
        # If this happens, we can still run inference but labels will be numeric.
        print("[WARN] BERT labels mapping not found; returning numeric ids.")

    print(f"[OK] BERT Model loaded | Device: {device} | Classes: {len(id2label) if id2label else 'unknown'}")
    BERT_AVAILABLE = True
except Exception as e:
    print(f"[ERROR] BERT load failed: {e}")
    print("Keyword-only mode active")


def get_disease_symptoms(disease_name: str) -> dict:
    """Return {symptom: weight} for a given disease from `data/disease_profiles.json`."""
    try:
        with open(DISEASE_PROFILES_PATH, encoding="utf-8") as f:
            profiles = json.load(f)

        for profile in profiles:
            if str(profile["disease"]).lower() == str(disease_name).lower():
                return dict(zip(profile["symptoms"], profile["weights"]))
    except Exception:
        pass
    return {}


def _normalize_keyword_score_percent(score_percent: float) -> float:
    # Matcher score is already 0-100.
    try:
        return max(0.0, min(float(score_percent) / 100.0, 1.0))
    except Exception:
        return 0.0


def decide_method_from_bert(bert_top_conf: float) -> str:
    """
    Hybrid decision system:
      - confidence > 0.75  -> "bert"
      - 0.40 .. 0.75      -> "hybrid"
      - confidence < 0.40  -> "keyword_fallback"
    """
    if bert_top_conf > BERT_HIGH_CONFIDENCE:
        return "bert"
    if bert_top_conf >= BERT_MID_CONFIDENCE:
        return "hybrid"
    return "keyword_fallback"


def predict_disease(text: str, top_k: int = 5) -> dict:
    """
    Predict diseases using BERT.
    Returns:
      {"top_disease": str, "confidence": float, "top_5": [{"disease": str, "confidence": float}, ...]}
    """
    if not BERT_AVAILABLE:
        return {"top_disease": None, "confidence": 0.0, "top_5": []}

    top_k = int(top_k) if top_k and top_k > 0 else 5

    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=128,
        truncation=True,
        padding=True,
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    top_k = min(top_k, probs.shape[-1])

    top_probs, top_indices = torch.topk(probs, top_k)
    top_preds = []
    for i in range(top_k):
        idx = int(top_indices[i].item())
        disease = id2label.get(idx, str(idx))
        top_preds.append({
            "disease": disease,
            "confidence": round(float(top_probs[i].item()), 4),
        })

    return {
        "top_disease": top_preds[0]["disease"] if top_preds else None,
        "confidence": top_preds[0]["confidence"] if top_preds else 0.0,
        # Backward-compatible name used across the codebase.
        "top_5": top_preds,
    }


def _keyword_rankings(keyword_symptoms: dict, top_k: int) -> list:
    """Return matcher rankings for keyword_symptoms."""
    try:
        if not keyword_symptoms:
            return []
        from matcher import match_diseases

        matches = match_diseases(keyword_symptoms, top_k=top_k)
        return [
            {
                "disease": m["disease"],
                "keyword_score_percent": float(m["score"]),
                "keyword_score_norm": _normalize_keyword_score_percent(m["score"]),
            }
            for m in matches
        ]
    except Exception:
        return []


def _combine_bert_and_keyword_hybrid(bert_top3: list, keyword_rankings: list, debug: bool) -> list:
    """
    Combine top-3 BERT predictions with keyword matching scores.
    final = (hybrid_bert_weight * bert_score) + (hybrid_keyword_weight * keyword_score_norm)

    Returns list of:
      [{"disease": str, "confidence": float}, ...] where confidence is final_score in [0,1].
    """
    if not bert_top3:
        return []

    # Fallback safety: if no keyword match, return BERT top-3.
    if not keyword_rankings:
        if debug:
            print("[HYBRID DEBUG] Keyword ranking empty -> fallback to BERT top-3.")
        return [{"disease": x["disease"], "confidence": float(x["confidence"])} for x in bert_top3]

    bert_map = {x["disease"]: float(x["confidence"]) for x in bert_top3}
    keyword_map = {x["disease"]: float(x["keyword_score_norm"]) for x in keyword_rankings}
    candidates = list(dict.fromkeys(list(bert_map.keys()) + list(keyword_map.keys())))  # stable union

    combined = []
    for disease in candidates:
        bert_score = bert_map.get(disease, 0.0)
        keyword_score_norm = keyword_map.get(disease, 0.0)
        final_score = (HYBRID_BERT_WEIGHT * bert_score) + (HYBRID_KEYWORD_WEIGHT * keyword_score_norm)
        
        # Sanity filter: penalize ungrounded diseases
        if keyword_score_norm == 0.0:
            final_score *= 0.5
            
        combined.append({
            "disease": disease,
            "confidence": float(final_score),
            "_bert_score": bert_score,
            "_keyword_score_norm": keyword_score_norm,
        })

    combined.sort(key=lambda x: x["confidence"], reverse=True)

    if debug:
        print("[HYBRID DEBUG] BERT top-3:")
        for x in bert_top3:
            print(f"  - {x['disease']:<30} bert_conf={x['confidence']:.4f}")

        print("[HYBRID DEBUG] Keyword top-3:")
        for x in keyword_rankings[:HYBRID_TOP_K_KEYWORD]:
            print(
                f"  - {x['disease']:<30} keyword_score={x['keyword_score_percent']:.1f}% "
                f"(norm={x['keyword_score_norm']:.3f})"
            )

        print("[HYBRID DEBUG] Hybrid combined candidates (top shown):")
        for x in combined[: max(5, len(bert_top3) + len(keyword_rankings))]:
            print(
                f"  - {x['disease']:<30} final={x['confidence']:.4f} "
                f"(0.7*{x['_bert_score']:.3f} + 0.3*{x['_keyword_score_norm']:.3f})"
            )

    # Strip debug fields before returning.
    out = [{"disease": x["disease"], "confidence": x["confidence"]} for x in combined]
    return out[:3]


def decide_and_build_hybrid_output(bert_top5: list, keyword_symptoms: dict) -> dict:
    """
    Build structured hybrid output and return:
      - method: "bert" | "hybrid" | "keyword_fallback"
      - predictions: top-ranked list with confidence in [0,1]
      - detected_symptoms: dict for downstream matcher pipeline
    """
    bert_top5 = bert_top5 or []
    top_bert = bert_top5[0] if bert_top5 else {"disease": None, "confidence": 0.0}
    method = decide_method_from_bert(float(top_bert.get("confidence", 0.0)))

    keyword_symptoms = keyword_symptoms or {}
    top_disease = top_bert.get("disease")
    detected_symptoms = {}
    predictions = []

    if method == "bert":
        detected_symptoms = get_disease_symptoms(top_disease) if top_disease else {}
        if not detected_symptoms:
            detected_symptoms = keyword_symptoms

        predictions = [{"disease": x["disease"], "confidence": float(x["confidence"])} for x in bert_top5[:3]]
        source = "bert_profile"

    elif method == "hybrid":
        bert_top3 = bert_top5[:HYBRID_TOP_K_BERT]
        keyword_rankings = _keyword_rankings(keyword_symptoms, top_k=HYBRID_TOP_K_KEYWORD)
        predictions = _combine_bert_and_keyword_hybrid(
            bert_top3=bert_top3,
            keyword_rankings=keyword_rankings,
            debug=DEBUG_HYBRID_LOGS,
        )

        # Keep keyword evidence for downstream matcher; if keyword_symptoms empty,
        # use top prediction disease profile to avoid empty outputs.
        detected_symptoms = keyword_symptoms
        if not detected_symptoms:
            detected_symptoms = get_disease_symptoms(predictions[0]["disease"]) if predictions else {}

        source = "hybrid_combined"

    else:  # keyword_fallback
        keyword_rankings = _keyword_rankings(keyword_symptoms, top_k=HYBRID_TOP_K_KEYWORD)
        predictions = [{"disease": x["disease"], "confidence": float(x["keyword_score_norm"])} for x in keyword_rankings]

        # Fallback safety: if no keyword match, return BERT top-3 predictions.
        if not predictions and bert_top5:
            predictions = [{"disease": x["disease"], "confidence": float(x["confidence"])} for x in bert_top5[:3]]

        detected_symptoms = keyword_symptoms
        if not detected_symptoms and top_disease:
            detected_symptoms = get_disease_symptoms(top_disease)

        source = "keyword_fallback"

    return {
        "method": method,
        "predictions": predictions,
        "detected_symptoms": detected_symptoms,
        "source": source,
    }


def predict_and_extract(text: str) -> dict:
    """
    Full inference:
      - Extract keyword symptoms (rules)
      - Run BERT classifier (AI)
      - Decide method using confidence thresholds
      - In hybrid: combine BERT top-3 + keyword disease scores
    """
    from nlp_extractor import extract_symptoms

    keyword_symptoms = extract_symptoms(text)

    # If BERT failed to load, rely purely on keyword matching.
    if not BERT_AVAILABLE:
        keyword_rankings = _keyword_rankings(keyword_symptoms, top_k=HYBRID_TOP_K_KEYWORD)
        predictions = [{"disease": x["disease"], "confidence": float(x["keyword_score_norm"])} for x in keyword_rankings]
        return {
            "method": "keyword_fallback",
            "predictions": predictions,
            "bert_disease": None,
            "bert_confidence": 0.0,
            "detected_symptoms": keyword_symptoms,
            "top_5": [],
            "source": "keyword_fallback",
        }

    bert_result = predict_disease(text, top_k=5)
    bert_top5 = bert_result.get("top_5", [])

    decided = decide_and_build_hybrid_output(
        bert_top5=bert_top5,
        keyword_symptoms=keyword_symptoms,
    )

    predictions = decided["predictions"]
    top_confidence = predictions[0]["confidence"] if predictions else 0.0
    
    if top_confidence > 0.75:
        confidence_level = "high"
    elif top_confidence >= 0.4:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    return {
        "method": decided["method"],
        "confidence_level": confidence_level,
        "predictions": predictions,
        "note": "Results are AI-assisted. Consult a doctor for confirmation.",
        "bert_disease": bert_result.get("top_disease"),
        "bert_confidence": bert_result.get("confidence", 0.0),
        "detected_symptoms": decided["detected_symptoms"],
        "top_5": bert_top5,
        "source": decided.get("source", "hybrid_combined"),
    }


if __name__ == "__main__":
    tests = [
        "2 din se bahut tez bukhar hai aur sar dard",
        "pet mein dard, loose motion, ulti",
        "skin pe khujli aur laal daane nikle hain",
        "sans lene mein takleef, chest mein dard",
        "aankhon ka rang peela ho gaya, bhook nahi lagti"
    ]
    
    print("\n")
    for t in tests:
        res = predict_and_extract(t)
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Input   : \"{t}\"")
        print(f"Method  : {res['method']}")

        preds = res.get("predictions", [])[:3]
        if preds:
            print("Predictions:")
            for p in preds:
                print(f"  - {p['disease']:<30} conf={p['confidence']:.4f}")
        
        if res.get('bert_disease'):
            print(f"Disease : {res['bert_disease']} ({res['bert_confidence']*100:.1f}%)")
            top_3 = " | ".join([f"{x['disease']} {x['confidence']*100:.0f}%" for x in res.get('top_5', [])[:3]])
            print(f"Top 3   : {top_3}")
            
        syms_str = ", ".join([f"{k}({v})" for k, v in res['detected_symptoms'].items()])
        print(f"Symptoms: {syms_str}")
        print("\n")
