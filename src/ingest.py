"""
Stage 1: ingest Hansard and Written Answers into SQLite.

Endpoints and response shapes verified against live APIs on 2026-09-02
(see docs/OPEN_QUESTIONS.md):

- Hansard /search/debates.json returns metadata only (title, date, ext id),
  NOT full text. Full text requires a second call per result to
  /debates/debate/{extId}.json.
- Written Answers now lives at questions-statements-api.parliament.uk
  (writtenquestions-api.parliament.uk still 301-redirects there, but we
  call the real domain directly). Response items are wrapped as
  {"value": {...}, "links": [...]}, and it's self-contained (question +
  answer text in one call, no second fetch needed).
"""
import re
import sqlite3
from datetime import datetime

import requests
from tqdm import tqdm

from config import DB_PATH, POLICY_AREA, SESSION_START, SESSION_END

HANSARD_BASE = "https://hansard-api.parliament.uk"
WRITTEN_ANSWERS_BASE = "https://questions-statements-api.parliament.uk"

PAGE_SIZE = 50
MAX_WRITTEN_ANSWERS = 400  # bounds LLM extraction cost/time; raise if budget allows

# /search/debates.json only matches titles (confirmed live), and its
# `department` query param is a no-op (confirmed live: a bogus department
# value returns the same count as the real one -- it's silently ignored by
# the API despite being documented). So coverage is built from multiple
# title-search terms instead, merged and deduped by debate ext id.
HANSARD_SEARCH_TERMS = [
    "NHS", "health", "hospital", "GP", "mental health", "cancer", "dental",
    "care", "medicine", "vaccination", "maternity", "social care", "disability",
    "pharmacy", "autism",
]
# A term whose reported TotalResultCount is this large is almost certainly hitting
# an API parsing quirk (confirmed live for "A and E": returns the full unfiltered
# session count, ~1861, instead of an actual match count) -- skip it rather than
# silently ingesting unrelated debates.
SUSPICIOUS_TOTAL_THRESHOLD = 500


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    with open("src/db_schema.sql") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def _strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html or "").strip()


def _slug(title: str) -> str:
    # matches Hansard's own URL slug scheme, e.g. "NHS Hospitals: Parking" -> "NHSHospitalsParking"
    return re.sub(r"[^A-Za-z0-9]", "", title or "")


def _fetch_hansard_search_term(term: str, start: str, end: str) -> list[dict]:
    params = {
        "queryParameters.searchTerm": term,
        "queryParameters.startDate": start,
        "queryParameters.endDate": end,
        "queryParameters.take": PAGE_SIZE,
    }
    resp = requests.get(f"{HANSARD_BASE}/search/debates.json", params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    total = payload.get("TotalResultCount", 0)
    if total > SUSPICIOUS_TOTAL_THRESHOLD:
        return []  # API parsing quirk for this term, not a real match count -- skip
    return payload.get("Results", [])


def _fetch_debate_text(ext_id: str, fallback_title: str, fallback_house: str, fallback_date: str) -> dict:
    detail_resp = requests.get(f"{HANSARD_BASE}/debates/debate/{ext_id}.json", timeout=30)
    detail_resp.raise_for_status()
    detail = detail_resp.json()

    overview = detail.get("Overview", {})
    items = detail.get("Items", [])
    text = "\n\n".join(
        f"{i.get('AttributedTo', '')}: {_strip_tags(i.get('Value', ''))}"
        for i in items if i.get("ItemType") == "Contribution"
    )
    speakers = sorted({i["AttributedTo"] for i in items if i.get("AttributedTo")})
    department = next(
        (n["Title"] for n in detail.get("Navigator", []) if n.get("HRSTag") == "hs_6bDepartment"),
        None,
    )
    title = overview.get("Title") or fallback_title
    house = overview.get("House") or fallback_house
    date = (overview.get("Date") or fallback_date)[:10]

    return {
        "id": f"hansard-{ext_id}",
        "date": date,
        "speaker": "; ".join(speakers) if speakers else None,
        "department": department,
        "title": title,
        "url": f"https://hansard.parliament.uk/{house.lower()}/{date}/debates/{ext_id}/{_slug(title)}",
        "text": text,
    }


def fetch_hansard_debates(policy_area: str, start: str, end: str) -> list[dict]:
    """
    /search/debates.json only matches titles, so a single term like "NHS"
    severely undercounts (12 debates over the full session). Merge results
    from multiple related terms, deduped by debate ext id. Per-term result
    counts are all well under the API's page size here, so no pagination is
    needed (unlike fetch_written_answers, which does need it).
    """
    seen_ids = set()
    results = []
    for term in HANSARD_SEARCH_TERMS:
        for r in _fetch_hansard_search_term(term, start, end):
            ext_id = r["DebateSectionExtId"]
            if ext_id not in seen_ids:
                seen_ids.add(ext_id)
                results.append(r)

    docs = []
    for r in tqdm(results, desc="fetching hansard debate text"):
        docs.append(_fetch_debate_text(
            r["DebateSectionExtId"], r.get("Title", ""), r.get("House", "Commons"), r.get("SittingDate", ""),
        ))
    return docs


def _fetch_written_answers_window(policy_area: str, start: str, end: str, cap: int) -> list[dict]:
    docs = []
    skip = 0
    total = None

    while len(docs) < cap and (total is None or skip < total):
        params = {
            "searchTerm": policy_area,
            "tabledWhenFrom": start,
            "tabledWhenTo": end,
            "expandMember": "true",
            "take": PAGE_SIZE,
            "skip": skip,
        }
        # this endpoint is slow (~20s/page with expandMember=true), give it real headroom
        resp = requests.get(f"{WRITTEN_ANSWERS_BASE}/api/writtenquestions/questions", params=params, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        total = payload.get("totalResults", 0)
        results = payload.get("results", [])
        if not results:
            break

        for item in results:
            v = item["value"]
            if not v.get("answerText"):
                continue  # not yet answered, nothing to extract/match against
            date_tabled = (v.get("dateTabled") or "")[:10]
            answering = v.get("answeringMember") or {}
            docs.append({
                "id": f"wq-{v['id']}",
                "date": (v.get("dateAnswered") or v.get("dateTabled") or "")[:10],
                "speaker": answering.get("name") or v.get("answeringBodyName"),
                "department": v.get("answeringBodyName"),
                "title": v.get("heading"),
                "url": f"https://questions-statements.parliament.uk/written-questions/detail/{date_tabled}/{v['uin']}",
                "text": f"Q: {v.get('questionText', '')}\n\nA: {v.get('answerText', '')}",
            })
            if len(docs) >= cap:
                break

        skip += PAGE_SIZE

    return docs


def fetch_written_answers(policy_area: str, start: str, end: str, windows: int = 4) -> list[dict]:
    """
    Split the session into equal date windows and fetch a capped, roughly even
    share from each. The API's default ordering favours recent results, and a
    single capped pull from [start, end] silently skips older parts of the
    session -- exactly the commitments old enough to have real follow-up
    evidence. Sampling per-window fixes that bias.
    """
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    span = (end_dt - start_dt) / windows
    per_window_cap = MAX_WRITTEN_ANSWERS // windows

    docs = []
    for i in range(windows):
        w_start = (start_dt + span * i).date().isoformat()
        w_end = (start_dt + span * (i + 1)).date().isoformat() if i < windows - 1 else end
        docs.extend(_fetch_written_answers_window(policy_area, w_start, w_end, per_window_cap))
    return docs


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
