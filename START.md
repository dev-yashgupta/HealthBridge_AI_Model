
# HealthBridge AI — Start Guide

Yeh guide fresh machine pe project start karne ke liye hai — step by step.

---

## Prerequisites (Pehle yeh install karo)

| Software | Version | Download |
|----------|---------|----------|
| Node.js | v18+ | https://nodejs.org |
| Anaconda / Python | 3.9+ | https://www.anaconda.com |
| PostgreSQL | 14+ | https://www.postgresql.org (optional — SQLite bhi kaam karta hai) |
| Git | latest | https://git-scm.com |

---

## Step 1 — Project Clone / Copy

Agar Git se clone kar rahe ho:
```bash
git clone <repo-url>
cd training
```

Ya directly folder copy karo `E:\training` mein.

---

## Step 2 — Python Dependencies Install

Anaconda Prompt ya terminal mein:

```bash
cd E:\training

pip install torch transformers openai thefuzz langdetect python-dotenv psycopg2-binary pandas datasets
```

> **Note:** Agar GPU nahi hai toh CPU version of PyTorch install hoga — yeh theek hai.

Verify karo:
```bash
python -c "import torch; import transformers; print('OK')"
```

---

## Step 3 — Node.js Dependencies Install

**Backend:**
```bash
cd E:\training\backend
npm install
```

**Frontend:**
```bash
cd E:\training\frontend
npm install
```

---

## Step 4 — Environment Variables Setup

`E:\training\.env` file already hai. Isme yeh values check/update karo:

```env
PORT=5000
NODE_ENV=development

# PostgreSQL (optional — sirf history summary ke liye)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthbridge_ai
DB_USER=postgres
DB_PASSWORD=yourpassword

# Groq API Key (AI translation ke liye — REQUIRED)
GROK_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx

# JWT (future use)
JWT_SECRET=healthbridge_your_jwt_secret_key_super_safe

# Frontend URL
APP_URL=http://localhost:5173

# Python executable path — APNA PATH DAALO
PYTHON_PATH=E:\CU\Data Analyst\anaconda3\python.exe
```

### PYTHON_PATH kaise find karein?

**Windows CMD mein:**
```cmd
where python
```

Jo path aaye woh `.env` mein `PYTHON_PATH=` ke baad daalo.

**Example:**
```
C:\Users\YourName\anaconda3\python.exe
```

### Groq API Key kahan se milega?

1. https://console.groq.com pe jaao
2. Account banao (free)
3. API Keys → Create New Key
4. `gsk_` se shuru hone wali key copy karo
5. `.env` mein `GROK_API_KEY=` ke baad paste karo

> **Bina Groq key ke bhi kaam karta hai** — sirf keyword matching mode mein chalega (Hindi translation nahi hogi).

---

## Step 5 — PostgreSQL Setup (Optional)

Agar PostgreSQL install hai:

```sql
-- pgAdmin ya psql mein run karo:
CREATE DATABASE healthbridge_ai;
```

Agar PostgreSQL nahi hai — **koi baat nahi**. AI pipeline SQLite use karta hai (`data/healthbridge.db`) jo automatically ban jaata hai.

---

## Step 6 — Data Files Check

Yeh files honi chahiye:

```
E:\training\
├── data\
│   └── disease_profiles.json    ← REQUIRED (matcher ke liye)
├── models\
│   └── bert_sehatsetu\final\
│       ├── config.json          ← REQUIRED (BERT model)
│       ├── model.safetensors    ← REQUIRED (BERT weights)
│       ├── tokenizer.json       ← REQUIRED
│       └── tokenizer_config.json
```

Agar `disease_profiles.json` nahi hai:
```bash
cd E:\training
python scripts/preprocess.py
```

---

## Step 7 — Application Start

**Do alag terminals mein run karo:**

### Terminal 1 — Backend Server
```bash
cd E:\training
node backend/server.js
```

Expected output:
```
Server running on http://localhost:5000
Connected to PostgreSQL database
```

> PostgreSQL connected na ho toh bhi theek hai — SQLite se kaam chalega.

### Terminal 2 — Frontend Dev Server
```bash
cd E:\training\frontend
npm run dev
```

Expected output:
```
VITE v8.x.x  ready in 500ms
➜  Local:   http://localhost:5173/
```

---

## Step 8 — Browser Mein Open Karo

```
http://localhost:5173
```

---

## Quick Test — AI Kaam Kar Raha Hai?

1. Browser mein `http://localhost:5173/checker` kholo
2. Textarea mein likho: **"fever and headache for 2 days"**
3. Duration: **"2-3 days ago"** select karo
4. **"Start AI Analysis"** button dabao
5. 5–15 seconds wait karo (pehli baar BERT load hota hai)
6. Results page pe diagnosis dikhna chahiye

---

## Common Errors & Fixes

### ❌ `Python was not found`
```
Fix: .env mein PYTHON_PATH sahi set karo
     where python  ← is command se path pata karo
```

### ❌ `No JSON found in python output`
```
Fix: Python dependencies install karo
     pip install torch transformers openai thefuzz
```

### ❌ `data/disease_profiles.json not found`
```
Fix: python scripts/preprocess.py  ← run karo
```

### ❌ `BERT load failed: Repo id must be in the form...`
```
Fix: models/bert_sehatsetu/final/ folder check karo
     config.json aur model.safetensors hone chahiye
     Agar nahi hain toh BERT disabled ho jaata hai
     (keyword mode mein kaam karta rahega)
```

### ❌ Frontend blank / no styles
```
Fix: Ctrl+Shift+R (hard refresh) karo browser mein
     Ya: cd frontend && npm run dev restart karo
```

### ❌ History page loading skeleton stuck
```
Fix: Backend server chal raha hai? Check karo:
     http://localhost:5000/api/history/GUEST/recent
     Yeh URL browser mein kholo — JSON aana chahiye
```

### ❌ PostgreSQL connection error
```
Fix: Koi baat nahi — SQLite se kaam chalega
     Error sirf log mein aata hai, app kaam karta hai
```

---

## Ports Summary

| Service | Port | URL |
|---------|------|-----|
| Frontend (React) | 5173 | http://localhost:5173 |
| Backend (Express) | 5000 | http://localhost:5000 |

---

## Files Jo Kabhi Git Mein Push Nahi Karne

```
.env                          ← API keys hain
data/healthbridge.db          ← User data hai
models/bert_sehatsetu/        ← Large model files
reports/                      ← Generated reports
__pycache__/                  ← Python cache
node_modules/                 ← npm packages
```

---

## Restart Karna Ho Toh

```bash
# Terminal 1 — Backend
cd E:\training
node backend/server.js

# Terminal 2 — Frontend
cd E:\training\frontend
npm run dev
```

Bas itna hi. Browser mein `http://localhost:5173` kholo.

---

*HealthBridge AI v2.0 | Start Guide*
