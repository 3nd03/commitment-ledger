"""
Records, for every commitment, the top-K candidate documents actually
considered during matching -- independent of the final follow_ups verdict.

This is embedding-only (reuses match.py's embed/cosine_sim), no LLM judge
calls, so it's cheap to (re)build even after matching is already done. Lets
the dashboard show the search trail (what was checked and rejected) for
`no_evidence_found` commitments, not just the final status.
"""
import sqlite3
import uuid

import numpy as np
from tqdm import tqdm

from config import DB_PATH
from match import embed, cosine_sim, TOP_K


def run(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    commitments = cur.execute("SELECT id, commitment_text, date FROM commitments").fetchall()
    documents = cur.execute("SELECT id, raw_text, date FROM documents").fetchall()

    if not commitments or not documents:
        print("Nothing to search, run ingest.py and extract.py first")
        return

    cur.execute("DELETE FROM search_candidates")

    doc_embeddings = embed([d[1][:2000] for d in documents])

    for i, (c_id, c_text, c_date) in enumerate(tqdm(commitments, desc="recording search trail")):
        c_embedding = embed([c_text])
        candidates = [(i, doc) for i, doc in enumerate(documents) if doc[2] > c_date]
        if not candidates:
            continue

        idxs = [i for i, _ in candidates]
        sims = cosine_sim(c_embedding, doc_embeddings[idxs])[0]
        top_idx_local = np.argsort(sims)[-TOP_K:][::-1]

        for rank, local_i in enumerate(top_idx_local, start=1):
            global_i = idxs[local_i]
            cur.execute(
                "INSERT INTO search_candidates (id, commitment_id, document_id, rank, similarity_score) "
                "VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), c_id, documents[global_i][0], rank, float(sims[local_i])),
            )
        if (i + 1) % 10 == 0:
            conn.commit()

    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
