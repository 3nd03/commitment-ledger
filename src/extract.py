"""Stage 2: extract structured commitments from raw document text via LLM."""
import json
import sqlite3
import time
import uuid

from pydantic import BaseModel
from tqdm import tqdm

from config import DB_PATH

import anthropic

# bare client: resolves credentials via `ant auth login` OAuth profile
# (draws on claude.ai subscription credit, not a Console API-key balance)
client = anthropic.Anthropic()

COMMIT_EVERY = 20  # persist progress periodically so a crash mid-run doesn't lose everything
MAX_RETRIES = 3

EXTRACTION_PROMPT = """You are extracting parliamentary commitments from a Hansard/written answer excerpt.

Extract ONLY genuine, substantive policy commitments: a minister pledging a specific future
action, review, publication, funding decision, or reform -- something concrete enough that a
later document could show whether it actually happened. Good examples: "we will publish a
review of NHS dental access by March 2027", "the Department will fund 200 new training places
from April 2027", "we are committed to meeting all cancer waiting time standards by the end
of this Parliament".

Do NOT extract vague procedural boilerplate, even if it uses future-tense phrasing:
- "I will consider that" / "we will take this into consideration" / "we will look into it"
- "I will draw this to the attention of [a colleague]"
- "I would be happy to meet/discuss/write to" the member
- General statements of position, aspiration with no concrete action, or past-tense descriptions

If in doubt whether a statement is substantive enough to later verify, leave it out.

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
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}],
            )
            break
        except anthropic.APIConnectionError:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(3 * (attempt + 1))
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [Commitment(**item) for item in items]


def run(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # resume-safe: skip documents already processed in a prior (possibly crashed) run
    done_ids = {r[0] for r in cur.execute("SELECT DISTINCT document_id FROM commitments")}
    rows = [
        r for r in cur.execute("SELECT id, raw_text, date FROM documents").fetchall()
        if r[0] not in done_ids
    ]

    for i, (doc_id, raw_text, date) in enumerate(tqdm(rows, desc="extracting")):
        for c in extract_commitments(raw_text):
            cur.execute(
                "INSERT INTO commitments (id, document_id, commitment_text, minister, "
                "department, topic_tags, deadline_stated, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), doc_id, c.commitment_text, c.minister, c.department,
                 ",".join(c.topic_tags), c.deadline_stated, date),
            )
        if (i + 1) % COMMIT_EVERY == 0:
            conn.commit()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
