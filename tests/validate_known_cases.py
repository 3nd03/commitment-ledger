"""
Manual validation harness, run before demo day.

Fill KNOWN_CASES with real commitment/outcome pairs you've verified by hand,
then check the pipeline's stored status matches. This is your main defence
against false "no_evidence_found" results, see docs/OPEN_QUESTIONS.md.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from config import DB_PATH  # noqa: E402

# TODO: fill in after manually reading real Hansard cases
KNOWN_CASES = [
    # {"commitment_snippet": "...", "expected_status": "fulfilled"},
]


def run() -> None:
    if not KNOWN_CASES:
        print("KNOWN_CASES is empty, fill it in with verified examples first")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    correct = 0

    for case in KNOWN_CASES:
        row = cur.execute(
            "SELECT c.id, f.status FROM commitments c LEFT JOIN follow_ups f "
            "ON f.commitment_id = c.id WHERE c.commitment_text LIKE ?",
            (f"%{case['commitment_snippet']}%",),
        ).fetchone()
        if row is None:
            print(f"NOT FOUND: {case['commitment_snippet']}")
            continue
        _, status = row
        match = status == case["expected_status"]
        correct += match
        print(f"{'OK' if match else 'MISMATCH'}: expected {case['expected_status']}, got {status}")

    print(f"\n{correct}/{len(KNOWN_CASES)} correct")
    conn.close()


if __name__ == "__main__":
    run()
