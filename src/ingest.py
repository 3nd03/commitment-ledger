"""
Stage 1: ingest Hansard and Written Answers into SQLite.

TODO: endpoint paths and params below are placeholders. Confirm against
live API docs (hansard-api.parliament.uk, writtenquestions-api.parliament.uk)
before relying on this, see docs/OPEN_QUESTIONS.md.
"""
import sqlite3
import requests
from tqdm import tqdm

from config import DB_PATH, POLICY_AREA, SESSION_START, SESSION_END

HANSARD_BASE = "https://hansard-api.parliament.uk"
WRITTEN_ANSWERS_BASE = "https://writtenquestions-api.parliament.uk"


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    with open("src/db_schema.sql") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def fetch_hansard_debates(policy_area: str, start: str, end: str) -> list[dict]:
    # TODO: confirm real query params, this is a placeholder shape
    params = {"queryParameters.searchTerm": policy_area,
              "queryParameters.startDate": start,
              "queryParameters.endDate": end}
    resp = requests.get(f"{HANSARD_BASE}/search/debates.json", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("Results", [])


def fetch_written_answers(policy_area: str, start: str, end: str) -> list[dict]:
    # TODO: confirm real query params against live docs
    params = {"searchTerm": policy_area, "answeredWhenFrom": start, "answeredWhenTo": end}
    resp = requests.get(f"{WRITTEN_ANSWERS_BASE}/api/writtenquestions/questions", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("results", [])


def store_documents(conn: sqlite3.Connection, docs: list[dict], source: str) -> None:
    cur = conn.cursor()
    for doc in tqdm(docs, desc=f"storing {source}"):
        cur.execute(
            "INSERT OR IGNORE INTO documents (id, source, date, speaker, department, title, url, raw_text) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                doc.get("id"), source, doc.get("date"), doc.get("speaker"),
                doc.get("department"), doc.get("title"), doc.get("url"), doc.get("text", ""),
            ),
        )
    conn.commit()


def main() -> None:
    if not POLICY_AREA or not SESSION_START or not SESSION_END:
        raise ValueError("Set POLICY_AREA, SESSION_START, SESSION_END in src/config.py first")

    init_db()
    conn = sqlite3.connect(DB_PATH)

    debates = fetch_hansard_debates(POLICY_AREA, SESSION_START, SESSION_END)
    store_documents(conn, debates, "hansard")

    answers = fetch_written_answers(POLICY_AREA, SESSION_START, SESSION_END)
    store_documents(conn, answers, "written_answer")

    conn.close()
    print(f"Ingested {len(debates)} debates, {len(answers)} written answers")


if __name__ == "__main__":
    main()
