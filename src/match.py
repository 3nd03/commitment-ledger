"""Stage 3: match commitments to follow-up evidence via embedding retrieval + LLM judge."""
import json
import sqlite3
import uuid
from datetime import datetime, timezone

import numpy as np
from openai import OpenAI
from tqdm import tqdm

from config import DB_PATH, OPENAI_API_KEY, ANTHROPIC_API_KEY, EMBEDDING_MODEL

import anthropic

openai_client = OpenAI(api_key=OPENAI_API_KEY)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TOP_K = 5

JUDGE_PROMPT = """Commitment made: "{commitment}"

Candidate follow-up passage: "{passage}"

Does this passage provide evidence the commitment was fulfilled, is in progress, or is unrelated?
Respond with JSON only: {{"status": "fulfilled" | "in_progress" | "unrelated", "evidence_quote": str or null}}
"""


def embed(texts: list[str]) -> np.ndarray:
    resp = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data])


def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / np.linalg.norm(a, axis=-1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=-1, keepdims=True)
    return a_norm @ b_norm.T


def judge(commitment_text: str, passage: str) -> dict:
    resp = claude_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(commitment=commitment_text, passage=passage)}],
    )
    try:
        return json.loads(resp.content[0].text.strip())
    except json.JSONDecodeError:
        return {"status": "unrelated", "evidence_quote": None}


def run(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    commitments = cur.execute(
        "SELECT id, commitment_text, date FROM commitments"
    ).fetchall()
    documents = cur.execute(
        "SELECT id, raw_text, date FROM documents"
    ).fetchall()

    if not commitments or not documents:
        print("Nothing to match, run ingest.py and extract.py first")
        return

    doc_ids = [d[0] for d in documents]
    doc_embeddings = embed([d[1][:2000] for d in documents])  # truncate for embedding cost

    for c_id, c_text, c_date in tqdm(commitments, desc="matching"):
        c_embedding = embed([c_text])
        # only consider documents dated after the commitment
        candidates = [(i, doc) for i, doc in enumerate(documents) if doc[2] > c_date]
        if not candidates:
            status, quote, score = "no_evidence_found", None, 0.0
        else:
            idxs = [i for i, _ in candidates]
            sims = cosine_sim(c_embedding, doc_embeddings[idxs])[0]
            top_idx_local = np.argsort(sims)[-TOP_K:][::-1]

            status, quote, score = "no_evidence_found", None, 0.0
            for local_i in top_idx_local:
                global_i = idxs[local_i]
                passage = documents[global_i][1][:2000]
                result = judge(c_text, passage)
                if result["status"] in ("fulfilled", "in_progress"):
                    status = result["status"]
                    quote = result.get("evidence_quote")
                    score = float(sims[local_i])
                    break

        cur.execute(
            "INSERT INTO follow_ups (id, commitment_id, document_id, status, evidence_quote, "
            "similarity_score, checked_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), c_id, None, status, quote, score,
             datetime.now(timezone.utc).isoformat()),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
