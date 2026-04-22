"""
Lightweight DB bridge — only reads from SQLite.
Does NOT import main.py or any AI modules.
Used by Express for history/reports endpoints.
"""
import sys
import json
import sqlite3
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "data/healthbridge.db"

def get_recent_history(patient_id: str) -> list:
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT symptom, severity_weight AS weight, duration_days, logged_at
            FROM symptom_log
            WHERE patient_id = ?
            ORDER BY logged_at DESC
            LIMIT 50
        """, (patient_id,))
        rows = [dict(r) for r in cursor.fetchall()]
    except Exception:
        rows = []
    conn.close()
    return rows

def get_history_summary(patient_id: str) -> dict:
    if not os.path.exists(DB_PATH):
        return {"summary": {}, "total_days_sick": 0}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT substr(logged_at, 1, 10) AS log_date, symptom
            FROM symptom_log
            WHERE patient_id = ?
            ORDER BY log_date ASC
        """, (patient_id,))
        rows = cursor.fetchall()
    except Exception:
        rows = []
    conn.close()
    summary = {}
    for log_date, symptom in rows:
        if log_date not in summary:
            summary[log_date] = []
        if symptom not in summary[log_date]:
            summary[log_date].append(symptom)
    return {"summary": summary, "total_days_sick": len(summary)}

def get_reports(patient_id: str) -> list:
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                top_disease TEXT,
                top_score REAL,
                urgency TEXT,
                report_text TEXT,
                file_path TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            SELECT id, patient_id, top_disease, top_score, urgency, report_text, file_path, created_at
            FROM reports
            WHERE patient_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (patient_id,))
        rows = [dict(r) for r in cursor.fetchall()]
    except Exception:
        rows = []
    conn.close()
    return rows

def run():
    try:
        data = json.loads(sys.stdin.read())
        action = data.get("action", "")
        patient_id = data.get("patient_id", "GUEST")

        if action == "history_recent":
            print(json.dumps(get_recent_history(patient_id)))
        elif action == "history_summary":
            print(json.dumps(get_history_summary(patient_id)))
        elif action == "get_reports":
            print(json.dumps(get_reports(patient_id)))
        else:
            print(json.dumps({"error": f"Unknown action: {action}"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    run()
