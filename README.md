# 🏥 HealthBridge_Al — ML Inference Engine

Welcome to the internal training and inference module for **HealthBridge_Al**. This engine serves as the backend intelligence unit responsible for translating symptoms, predicting diseases, and formatting clinical reports.

---

## 🏗️ Architecture

This engine operates on a cascading fallback architecture to provide maximum accuracy securely:
1. **Grok Translation Layer:** Detects Hindi, Punjabi, or Hinglish input and uses the Groq/Grok API to translate it into standard medical English.
2. **BERT Hybrid Predictor:** Feeds the cleaned English into a fine-tuned HuggingFace BERT neural network (predicting across 1082 diseases).
3. **Keyword Fallback Extraction:** If the neural network confidence is low (<40%), a heavy Regex/Fuzzy-matching keyword extractor takes over, mapping local synonyms directly to disease profiles.

## 🚀 How to Run the Application

The application requires its isolated Anaconda environment to run correctly. 

### Step 1: Activate Virtual Environment
Before running any scripts, ensure your Anaconda virtual environment is activated in your terminal:
```powershell
conda activate healthbridge
```
*(If you see an error like "conda is not recognized", try opening **Anaconda Prompt** instead of regular PowerShell and run the command there. You should see `(healthbridge)` appear on the left side of your command line.)*

### Step 2: Ensure API Keys are loaded (Optional but recommended)
The Grok Translation layer requires your `GROK_API_KEY`. The engine will auto-load this from `../backend/.env`. If you haven't set it up there, you can inject it directly:
```powershell
$env:GROK_API_KEY="gsk_your_groq_or_grok_key"
```
*(If no key is found, the system gracefully falls back to Keyword extraction).*

### Step 3: Launch the Application

You can launch the engine in two different modes:

#### Mode A: 🌐 Web Dashboard (Recommended)
This launches a beautiful Streamlit UI where you can view patient history, test the diagnostic engine, and view medical reports visually.
```bash
streamlit run app.py
```
*This will open `http://localhost:8501` in your browser.*

#### Mode B: 💻 Interactive Terminal Mode
For fast, developer-centric testing directly inside the PowerShell console:
```bash
python main.py
```

---

## 📂 File Structure

| Category | Files | Description |
| :--- | :--- | :--- |
| **Execution** | `app.py`, `main.py` | Streamlit Dashboard & Terminal CLI entry points. |
| **Intelligence** | `grok_translator.py`, `nlp_predictor.py`, `nlp_extractor.py`, `matcher.py` | Core AI prediction & extraction logic. |
| **Utilities** | `config.py`, `history_db.py`, `report_generator.py` | API configurations, database storage, and report printing. |
| **Output** | `data/`, `models/`, `reports/` | Generated profiles, downloaded models, and saved text reports. |
| **Archive** | `scripts/`, `tests/`, `training_scripts/` | Dataset preparation scripts, testing suites, and Jupyter Notebooks used for model training. |

## 🧪 Testing the Pipeline
To verify if all AI components (Language Detection, Translation, BERT, and Keyword Fallback) are functioning correctly:
```bash
python tests/test_grok_translator.py
```

*Note: Make sure your `data/disease_profiles.json` and `models/bert_healthbridge/final/` files exist before running predictions!*
