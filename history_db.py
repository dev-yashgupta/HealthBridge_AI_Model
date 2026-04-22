"""
HealthBridge_Al - Patient Symptom History DB
SQLite-based history tracking for patient symptom logs
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "data/healthbridge.db"
os.makedirs("data", exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. init_db() — Create DB + table if not exists
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    """Creates the SQLite DB and symptom_log table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptom_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id      TEXT    NOT NULL,
            symptom         TEXT    NOT NULL,
            severity_weight INTEGER,
            duration_days   INTEGER DEFAULT 0,
            logged_at       TEXT
        )
    """)
    conn.commit()
    conn.close()


# Auto-init on import
init_db()


# ─────────────────────────────────────────────────────────────────────────────
# 2. log_symptoms() — Save symptoms for a patient
# ─────────────────────────────────────────────────────────────────────────────
def log_symptoms(patient_id: str, symptoms_dict: dict, duration_days: int = 0) -> int:
    """
    Saves each symptom as a separate row in symptom_log.

    Args:
        patient_id    : Unique patient identifier (e.g. "P001")
        symptoms_dict : {symptom_name: severity_weight}
        duration_days : Number of days patient has had these symptoms

    Returns:
        Number of rows inserted
    """
    if not symptoms_dict:
        return 0

    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    rows = [
        (patient_id, symptom, weight, duration_days, now)
        for symptom, weight in symptoms_dict.items()
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany(
        """INSERT INTO symptom_log
           (patient_id, symptom, severity_weight, duration_days, logged_at)
           VALUES (?, ?, ?, ?, ?)""",
        rows
    )
    conn.commit()
    inserted = cursor.rowcount
    conn.close()
    return inserted


# ─────────────────────────────────────────────────────────────────────────────
# 3. get_history() — Fetch last N days entries for a patient
# ─────────────────────────────────────────────────────────────────────────────
def get_history(patient_id: str, days: int = 7) -> list:
    """
    Returns symptom entries for a patient from the last `days` days.

    Returns:
        List of dicts:
        [{"symptom": "high_fever", "weight": 7, "duration_days": 2, "logged_at": "..."}]
    """
    since = (datetime.now() - timedelta(days=days)).isoformat(sep=" ", timespec="seconds")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """SELECT symptom, severity_weight AS weight, duration_days, logged_at
           FROM symptom_log
           WHERE patient_id = ?
             AND logged_at >= ?
           ORDER BY logged_at ASC""",
        (patient_id, since)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# 4. get_history_summary() — Group symptoms by date
# ─────────────────────────────────────────────────────────────────────────────
def get_history_summary(patient_id: str) -> dict:
    """
    Groups all symptom entries by date (YYYY-MM-DD) for a patient.

    Returns:
        {
          "summary": {
            "2024-01-15": ["high_fever", "headache"],
            "2024-01-16": ["high_fever", "nausea"]
          },
          "total_days_sick": 2
        }
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT substr(logged_at, 1, 10) AS log_date, symptom
           FROM symptom_log
           WHERE patient_id = ?
           ORDER BY log_date ASC""",
        (patient_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    summary = {}
    for log_date, symptom in rows:
        if log_date not in summary:
            summary[log_date] = []
        if symptom not in summary[log_date]:
            summary[log_date].append(symptom)

    return {
        "summary": summary,
        "total_days_sick": len(summary)
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. get_all_patients() — List unique patients
# ─────────────────────────────────────────────────────────────────────────────
def get_all_patients() -> list:
    """Returns sorted list of all unique patient_ids in the DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT patient_id FROM symptom_log ORDER BY patient_id")
    patients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return patients


# ─────────────────────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("HISTORY DB — TEST SEQUENCE")
    print("=" * 60)

    # a) P001 visit 1
    n = log_symptoms("P001", {"high_fever": 7, "headache": 3}, duration_days=2)
    print(f"\n[a] P001 Visit 1 logged  — {n} rows inserted")

    # b) P001 visit 2
    n = log_symptoms("P001", {"high_fever": 7, "nausea": 5, "vomiting": 5}, duration_days=3)
    print(f"[b] P001 Visit 2 logged  — {n} rows inserted")

    # c) P002 visit 1
    n = log_symptoms("P002", {"cough": 4, "chest_pain": 7}, duration_days=1)
    print(f"[c] P002 Visit 1 logged  — {n} rows inserted")

    # d) P001 history
    print("\n[d] get_history('P001') — last 7 days:")
    history = get_history("P001", days=7)
    for entry in history:
        print(f"    symptom={entry['symptom']:<30} weight={entry['weight']}  "
              f"duration={entry['duration_days']}d  logged_at={entry['logged_at']}")

    # e) P001 summary
    print("\n[e] get_history_summary('P001'):")
    result = get_history_summary("P001")
    print(f"    total_days_sick : {result['total_days_sick']}")
    for date, syms in result["summary"].items():
        print(f"    {date} : {syms}")

    # f) All patients
    print("\n[f] get_all_patients():")
    patients = get_all_patients()
    for p in patients:
        print(f"    - {p}")

    print("\n" + "=" * 60)
    print(f"[DONE] data/healthbridge.db created and history saved!\n")
