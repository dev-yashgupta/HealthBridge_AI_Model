# HealthBridge_Al -- Grok Translation Layer

## Overview
Translates Hindi, Punjabi, Hinglish, and mixed-language symptom descriptions
into medical English using Grok API, then feeds the clean English text to
our BERT model for accurate disease prediction.

## Pipeline Priority
```
User Input (any language)
    |
    v
[1] Grok Translation  --> Medical English
    |
    v
[2] BERT Prediction   --> Disease + Confidence
    |
    v
[3] Keyword Extraction --> Symptoms (fallback / merge)
    |
    v
[4] Method Selection   --> bert_translated / hybrid / keyword_fallback
```

## Setup

### 1. Install Dependencies
```bash
pip install openai langdetect
```

### 2. Set Grok API Key
Get your key from https://console.x.ai

**Windows PowerShell:**
```powershell
$env:GROK_API_KEY="xai-your-key-here"
```

**Linux/Mac:**
```bash
export GROK_API_KEY="xai-your-key-here"
```

### 3. Run Tests
```bash
python test_grok_translator.py
```

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `config.py` | ~100 | Central config: API keys, thresholds, prompts |
| `grok_translator.py` | ~330 | Translation + prediction pipeline |
| `test_grok_translator.py` | ~190 | 8 test cases across all languages |
| `main.py` | (updated) | Integration: Grok > BERT > Keyword |

## Supported Languages
- **Hindi**: bukhar, sar dard, pet dard, dast, ulti...
- **Punjabi**: bukhaar, sir noon vich, pet noon vich dard...
- **Hinglish**: fever + hai, headache + ho raha...
- **English**: fever, headache, stomach pain...
- **Mixed**: Any combination of above

## Confidence Thresholds
| BERT Confidence | Method Used | Description |
|----------------|-------------|-------------|
| >= 70% | `bert_translated` | BERT fully trusted |
| 40-70% | `hybrid_translated` | BERT + keywords merged |
| < 40% | `keyword_fallback` | Keywords only |

## Fallback Chain
```
Grok API fails?    --> Use original text with BERT
BERT model fails?  --> Use keyword extraction
No API key?        --> Skip Grok, use BERT/keyword
No internet?       --> Skip Grok, use BERT/keyword
```

## Return Structure
```python
{
    "method": "bert_translated",
    "original_text": "3 din se bukhar hai",
    "detected_language": "hindi",
    "translated_text": "fever for 3 days",
    "translation_confidence": 0.95,
    "bert_disease": "Typhoid",
    "bert_confidence": 0.87,
    "detected_symptoms": {"high_fever": 7, "headache": 3},
    "top_5": [...],
    "grok_used": True,
    "duration_days": 3,
}
```
