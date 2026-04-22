"""
HealthBridge_Al - NLP Symptom Extractor
Extracts symptoms from Hinglish/Hindi/English text and maps them to
canonical symptom names from disease_profiles.json
"""

import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from thefuzz import fuzz, process as fuzz_process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("[WARN] thefuzz not installed. Fuzzy matching disabled.")

# ─────────────────────────────────────────────────────────────────────────────
# 1. SYNONYM MAP  (Hinglish / Hindi / casual English → canonical symptom name)
#    Multi-word phrases are listed first — they are checked before single words
# ─────────────────────────────────────────────────────────────────────────────
SYNONYM_MAP = {
    # ── Multi-word Hindi / Hinglish ──────────────────────────────────────────
    "sar mein dard"             : "headache",
    "sir mein dard"             : "headache",
    "daane nikalna"             : "skin_rash",
    "poore badan mein khujli"   : "itching",
    "body pe daane"             : "nodal_skin_eruptions",
    "aankhon mein sujan"        : "puffy_face_and_eyes",
    "haath pair thande"         : "cold_hands_and_feets",
    "bhook nahi lagti"          : "loss_of_appetite",
    "neend nahi aati"           : "restlessness",
    "weight kam ho raha"        : "weight_loss",
    "sar dard"                  : "headache",
    "sir dard"                  : "headache",
    "sar me dard"               : "headache",
    "sir me dard"               : "headache",
    "aankhon ke peeche dard"    : "pain_behind_the_eyes",
    "aankhon mein dard"         : "pain_behind_the_eyes",
    "aankhon mein jalan"        : "redness_of_eyes",
    "aankhon mein lali"         : "redness_of_eyes",
    "aankhon se paani"          : "watering_from_eyes",
    "pet dard"                  : "stomach_pain",
    "pet mein dard"             : "stomach_pain",
    "pet ke niche dard"         : "abdominal_pain",
    "pet mein akdan"            : "abdominal_pain",
    "seene mein dard"           : "chest_pain",
    "seene mein jalan"          : "chest_pain",
    "saans lene mein takleef"   : "breathlessness",
    "saans phoolna"             : "breathlessness",
    "saans fhoolna"             : "breathlessness",
    "bahut thakaan"             : "fatigue",
    "bohat thakaan"             : "fatigue",
    "kamar dard"                : "back_pain",
    "kamar mein dard"           : "back_pain",
    "gardan mein dard"          : "neck_stiffness",
    "gardan akad jana"          : "neck_stiffness",
    "gaanth banana"             : "swelled_lymph_nodes",
    "gathiya"                   : "joint_pain",
    "jodon mein dard"           : "joint_pain",
    "ghutne mein dard"          : "knee_pain",
    "kadmon mein dard"          : "painful_walking",
    "loose motion"              : "diarrhoea",
    "loose motions"             : "diarrhoea",
    "pait mein gas"             : "passage_of_gases",
    "high fever"                : "high_fever",
    "high temp"                 : "high_fever",
    "tez bukhar"                : "high_fever",
    "body ache"                 : "muscle_pain",
    "body pain"                 : "muscle_pain",
    "badan dard"                : "muscle_pain",
    "badan mein dard"           : "muscle_pain",
    "wajan kam hona"            : "weight_loss",
    "wajan badhna"              : "weight_gain",
    "bahut pasina"              : "sweating",
    "raat ko pasina"            : "sweating",
    "thanda pasina"             : "sweating",
    "naak bahna"                : "runny_nose",
    "naak se paani"             : "runny_nose",
    "naak band"                 : "congestion",
    "gale mein dard"            : "throat_irritation",
    "gale mein kharash"         : "throat_irritation",
    "sore throat"               : "throat_irritation",
    "tummy ache"                : "stomach_pain",
    "throwing up"               : "vomiting",
    "throwing up food"          : "vomiting",
    "skin rash"                 : "skin_rash",
    "running nose"              : "runny_nose",
    "runny nose"                : "runny_nose",
    "chest pain"                : "chest_pain",
    "chest dard"                : "chest_pain",
    "chest mein dard"           : "chest_pain",
    "seene mein dard"           : "chest_pain",
    "sans lene mein takleef"    : "breathlessness",
    "sans phoolna"              : "breathlessness",
    "blurry vision"             : "blurred_and_distorted_vision",
    "pain in eyes"              : "pain_behind_the_eyes",
    "eye pain"                  : "pain_behind_the_eyes",
    "yellow eyes"               : "yellowing_of_eyes",
    "yellow skin"               : "yellowish_skin",
    "dark urine"                : "dark_urine",
    "blood in stool"            : "bloody_stool",
    "pus filled pimples"        : "pus_filled_pimples",

    # ── New Hindi Synonym Boost (BERT weakness compensation) ─────────────────
    "kala peela"                : "yellowing_of_eyes",
    "pet phulna"                : "swelling_of_stomach",
    "haath kaanpna"             : "muscle_wasting",
    "aankhein peeli"            : "yellowish_skin",
    "gardan akad"               : "stiff_neck",
    "peshab mein jalan"         : "burning_micturition",
    "bar bar peshab"            : "polyuria",
    "munh mein chale"           : "ulcers_on_tongue",
    "bhook zyada lagti"         : "excessive_hunger",
    "dil ghabrana"              : "fast_heart_rate",
    "sans chhoti hona"          : "breathlessness",
    "aankhon mein lali"         : "redness_of_eyes",
    "naak se pani"              : "runny_nose",
    "gardan mein sujan"         : "swelled_lymph_nodes",
    "zinc jaisa swad"           : "altered_sensorium",

    # ── Single-word Hindi ────────────────────────────────────────────────────
    "bukhar"        : "high_fever",
    "bukhaar"       : "high_fever",
    "bukhara"       : "high_fever",
    "khansi"        : "cough",
    "khaansi"       : "cough",
    "khasi"         : "cough",
    "ulti"          : "vomiting",
    "ultio"         : "vomiting",
    "qai"           : "vomiting",
    "chakkar"       : "loss_of_balance",
    "chakkra"       : "loss_of_balance",
    "dast"          : "diarrhoea",
    "daast"         : "diarrhoea",
    "thakaan"       : "fatigue",
    "thakaawat"     : "fatigue",
    "thaka"         : "fatigue",
    "khujli"        : "itching",
    "kharish"       : "itching",
    "paseena"       : "sweating",
    "pasina"        : "sweating",
    "kaampna"       : "shivering",
    "kaapna"        : "shivering",
    "thithurana"    : "chills",
    "thand"         : "chills",
    "bhook"         : "loss_of_appetite",
    "bhookh"        : "loss_of_appetite",
    "pyaas"         : "dehydration",
    "nausea"        : "nausea",
    "ji machlaana"  : "nausea",
    "ghabrahat"     : "anxiety",
    "bechain"       : "restlessness",
    "soojan"        : "swelling_joints",
    "sujan"         : "swelling_joints",
    "peela"         : "yellowish_skin",
    "peeli"         : "yellowish_skin",
    "zakhm"         : "ulcers_on_tongue",
    "phoda"         : "pus_filled_pimples",
    "kala"          : "blackheads",
    "daag"          : "dischromic_patches",
    "daane"         : "skin_rash",
    "chatpatahat"   : "acidity",
    "jalan"         : "burning_micturition",
    "dhadkan"       : "palpitations",
    "likhna"        : "slurred_speech",

    # ── Single-word English casual / misspellings ────────────────────────────
    "fever"         : "high_fever",
    "faver"         : "high_fever",
    "feber"         : "high_fever",
    "feaver"        : "high_fever",
    "headache"      : "headache",
    "hedache"       : "headache",
    "headach"       : "headache",
    "headech"       : "headache",
    "cough"         : "cough",
    "cogh"          : "cough",
    "vomiting"      : "vomiting",
    "vommiting"     : "vomiting",
    "vomit"         : "vomiting",
    "diarrhea"      : "diarrhoea",
    "diarea"        : "diarrhoea",
    "diarrhoea"     : "diarrhoea",
    "diarrea"       : "diarrhoea",
    "tired"         : "fatigue",
    "tiredness"     : "fatigue",
    "dizzy"         : "loss_of_balance",
    "dizziness"     : "loss_of_balance",
    "nausea"        : "nausea",
    "nauseous"      : "nausea",
    "sweating"      : "sweating",
    "sweat"         : "sweating",
    "itching"       : "itching",
    "itch"          : "itching",
    "rash"          : "skin_rash",
    "chills"        : "chills",
    "chill"         : "chills",
    "shivering"     : "shivering",
    "constipation"  : "constipation",
    "indigestion"   : "indigestion",
    "acidity"       : "acidity",
    "bloating"      : "swelling_of_stomach",
    "fatigue"       : "fatigue",
    "weakness"      : "lethargy",
    "anxiety"       : "anxiety",
    "depression"    : "depression",
    "irritability"  : "irritability",
    "palpitations"  : "palpitations",
    "breathless"    : "breathlessness",
    "breathlessness": "breathlessness",
    "dehydration"   : "dehydration",
    "sneezing"      : "continuous_sneezing",
    "sneeze"        : "continuous_sneezing",
    "congestion"    : "congestion",
    "mucus"         : "phlegm",
    "phlegm"        : "phlegm",
    "sputum"        : "mucoid_sputum",
    "jaundice"      : "yellowish_skin",
    "obesity"       : "obesity",
    "insomnia"      : "restlessness",
    "backpain"      : "back_pain",
    "backache"      : "back_pain",
}

# ─────────────────────────────────────────────────────────────────────────────
# Load symptom → weight mapping from disease_profiles.json
# ─────────────────────────────────────────────────────────────────────────────
def load_weight_map(profiles_path="data/disease_profiles.json") -> dict:
    """Returns {symptom_name: max_weight_across_all_diseases}"""
    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] {profiles_path} not found. Run preprocess.py first.")
        return {}

    weight_map = {}
    for profile in profiles:
        for sym, wt in zip(profile["symptoms"], profile["weights"]):
            if sym not in weight_map or wt > weight_map[sym]:
                weight_map[sym] = wt
    return weight_map


WEIGHT_MAP = load_weight_map()
ALL_SYMPTOMS = list(WEIGHT_MAP.keys())


# ─────────────────────────────────────────────────────────────────────────────
# 2. extract_symptoms(text) → {symptom: weight}
# ─────────────────────────────────────────────────────────────────────────────
def extract_symptoms(text: str, fuzzy_threshold: int = 80) -> dict:
    """
    Extracts symptoms from Hinglish/English text.
    Returns dict: {"high_fever": 7, "headache": 3}
    """
    text_lower = text.lower().strip()
    found = {}

    # Sort synonym keys: longest (multi-word) first to prevent partial matches
    sorted_keys = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)

    for phrase in sorted_keys:
        canonical = SYNONYM_MAP[phrase]
        if phrase in text_lower:
            wt = WEIGHT_MAP.get(canonical, 1)
            if canonical not in found:
                found[canonical] = wt
            # Remove matched phrase so it is not matched again partially
            text_lower = text_lower.replace(phrase, " ", 1)

    # ── Fuzzy matching on remaining tokens ──────────────────────────────────
    if FUZZY_AVAILABLE and ALL_SYMPTOMS:
        tokens = re.findall(r"[a-z_]+", text_lower)
        for token in tokens:
            if len(token) < 3:
                continue
            # Check against canonical symptom names directly
            match, score = fuzz_process.extractOne(
                token, ALL_SYMPTOMS, scorer=fuzz.ratio
            )
            if score >= fuzzy_threshold and match not in found:
                found[match] = WEIGHT_MAP.get(match, 1)

    return found


# ─────────────────────────────────────────────────────────────────────────────
# 3. get_duration(text) → int (days)
# ─────────────────────────────────────────────────────────────────────────────
HINDI_NUMBERS = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5,
    "chhe": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

def get_duration(text: str) -> int:
    """
    Extract symptom duration in days from Hinglish/English text.
    Examples:
      "2 din se"       -> 2
      "kal se"         -> 1
      "teen ghante se" -> 0   (same day, <1 day)
      "ek hafte se"    -> 7
      "do hafte se"    -> 14
    """
    text_lower = text.lower().strip()

    # ── yesterday ───────────────────────────────────────────────────────────
    if re.search(r"\bkal\s+se\b|\byesterday\b", text_lower):
        return 1

    # ── minutes / ghante (hours → same day = 0) ─────────────────────────────
    if re.search(r"ghante|hour|minute|mins?\b", text_lower):
        return 0

    # ── weeks ────────────────────────────────────────────────────────────────
    week_match = re.search(
        r"(\d+|ek|do|teen|char|paanch|chhe|saat|aath|nau|das|one|two|three|four|five|six|seven)\s*hafte",
        text_lower
    )
    if week_match:
        raw = week_match.group(1)
        n = HINDI_NUMBERS.get(raw, None) or (int(raw) if raw.isdigit() else 1)
        return n * 7

    # ── days ─────────────────────────────────────────────────────────────────
    day_match = re.search(
        r"(\d+|ek|do|teen|char|paanch|chhe|saat|aath|nau|das|one|two|three|four|five|six|seven)\s*(?:din|day|days)",
        text_lower
    )
    if day_match:
        raw = day_match.group(1)
        n = HINDI_NUMBERS.get(raw, None) or (int(raw) if raw.isdigit() else 1)
        return n

    # ── aaj / today ──────────────────────────────────────────────────────────
    if re.search(r"\baaj\b|\btoday\b", text_lower):
        return 0

    # Default: unknown duration
    return -1


# ─────────────────────────────────────────────────────────────────────────────
# 4. TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_inputs = [
        "2 din se bukhar hai aur sar dard ho raha hai",
        "loose motion aur pet mein dard hai",
        "khansi aa rahi hai aur chest mein dard hai",
        "body ache, high fever, sweating bahut ho raha hai",
        "chakkar aa rahe hain, aankhon ke peeche dard hai",
    ]

    print("=" * 60)
    print("NLP EXTRACTOR — TEST RESULTS")
    print("=" * 60)

    for i, inp in enumerate(test_inputs, 1):
        symptoms = extract_symptoms(inp)
        duration = get_duration(inp)

        print(f"\n[Test {i}] Input : {inp}")
        print(f"         Duration: {duration} day(s)  (-1 = unknown)")
        if symptoms:
            print("         Symptoms detected:")
            for sym, wt in symptoms.items():
                print(f"           * {sym:<40} weight = {wt}")
        else:
            print("         Symptoms detected: None")

    print("\n" + "=" * 60)
    print("[DONE] nlp_extractor.py working correctly!\n")
