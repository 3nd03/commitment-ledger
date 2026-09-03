CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,  -- 'hansard' or 'written_answer'
    date TEXT NOT NULL,
    speaker TEXT,
    department TEXT,
    title TEXT,
    url TEXT,
    raw_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS commitments (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    commitment_text TEXT NOT NULL,
    minister TEXT,
    department TEXT,
    topic_tags TEXT,  -- comma-separated
    deadline_stated TEXT,
    date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS follow_ups (
    id TEXT PRIMARY KEY,
    commitment_id TEXT NOT NULL REFERENCES commitments(id),
    document_id TEXT REFERENCES documents(id),
    status TEXT NOT NULL,  -- fulfilled | in_progress | no_evidence_found
    evidence_quote TEXT,
    similarity_score REAL,
    checked_at TEXT NOT NULL
);

-- search trail: the candidate documents actually considered for each commitment,
-- independent of the final follow_ups verdict. Lets the dashboard show *what was
-- searched and rejected*, not just the outcome. Embedding-only (no LLM judge), so
-- it's cheap to (re)build without re-spending on matching.
CREATE TABLE IF NOT EXISTS search_candidates (
    id TEXT PRIMARY KEY,
    commitment_id TEXT NOT NULL REFERENCES commitments(id),
    document_id TEXT NOT NULL REFERENCES documents(id),
    rank INTEGER NOT NULL,
    similarity_score REAL NOT NULL
);
