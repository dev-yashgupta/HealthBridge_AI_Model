import sys
import json
from main import diagnose

def run():
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print(json.dumps({"status": "error", "message": "No input provided"}))
            return

        data = json.loads(input_data)
        action = data.get("action", "diagnose")

        # ── History summary ──────────────────────────────────────────────────
        if action == "history_summary":
            from history_db import get_history_summary
            patient_id = data.get("patient_id", "GUEST")
            result = get_history_summary(patient_id)
            print(json.dumps(result))
            return

        # ── Recent history ───────────────────────────────────────────────────
        if action == "history_recent":
            from history_db import get_history
            patient_id = data.get("patient_id", "GUEST")
            rows = get_history(patient_id, days=365)
            print(json.dumps(rows))
            return

        # ── Get reports ──────────────────────────────────────────────────────
        if action == "get_reports":
            import sqlite3
            patient_id = data.get("patient_id", "GUEST")
            db_path = "data/healthbridge.db"
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, patient_id, top_disease, top_score, urgency, report_text, file_path, created_at
                    FROM reports
                    WHERE patient_id = ?
                    ORDER BY created_at DESC
                    LIMIT 50
                """, (patient_id,))
                rows = [dict(row) for row in cursor.fetchall()]
                conn.close()
                print(json.dumps(rows))
            except Exception as e:
                print(json.dumps([]))
            return

        # ── Diagnose (default) ───────────────────────────────────────────────
        patient_id = data.get("patient_id", "GUEST")
        symptoms_text = data.get("symptoms", "")

        if not symptoms_text:
            print(json.dumps({"status": "error", "message": "No symptoms provided"}))
            return

        result = diagnose(patient_id, symptoms_text)
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    run()
