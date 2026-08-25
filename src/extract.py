"""Stage 2: extract structured commitments from raw document text via LLM."""
import json
import sqlite3
import uuid

from pydantic import BaseModel
from tqdm import tqdm

from config import DB_PATH, ANTHROPIC_API_KEY

import anthropic

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

EXTRACTION_PROMPT = """You are extracting parliamentary commitments from a Hansard/written answer excerpt.

Only extract sentences where a minister commits to a future action: "I will...", "we will...",
"the government will...", "I have asked officials to...", "we are committed to...".
Do not extract general statements of position or past-tense descriptions.

Return a JSON array. Each item: {{"commitment_text": str, "minister": str or null,
"department": str or null, "topic_tags": [str], "deadline_stated": str or null}}.
Return an empty array if no genuine commitment is present. No prose, JSON only.

Text:
{text}
"""


class Commitment(BaseModel):
    commitment_text: str
    minister: str | None = None
    department: str | None = None
    topic_tags: list[str] = []
    deadline_stated: str | None = None


def extract_commitments(text: str) -> list[Commitment]:
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}],
    )
    raw = resp.content[0].text.strip()
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [Commitment(**item) for item in items]


def run(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, raw_text, date FROM documents").fetchall()

    for doc_id, raw_text, date in tqdm(rows, desc="extracting"):
        for c in extract_commitments(raw_text):
            cur.execute(
                "INSERT INTO commitments (id, document_id, commitment_text, minister, "
                "department, topic_tags, deadline_stated, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), doc_id, c.commitment_text, c.minister, c.department,
                 ",".join(c.topic_tags), c.deadline_stated, date),
            )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
