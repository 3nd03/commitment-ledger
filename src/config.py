import os
from dotenv import load_dotenv

load_dotenv()

# Locked 2026-09-02: NHS/health (team consensus, doc volume checked live), current
# session only (started 13 May 2026, no prorogation yet as of this date). Bump
# SESSION_END closer to the hackathon date to pick up newer written answers.
POLICY_AREA = "NHS"
SESSION_START = "2026-05-13"
SESSION_END = "2026-09-02"

DB_PATH = os.getenv("DB_PATH", "data/ledger.db")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

STATUSES = ("fulfilled", "in_progress", "no_evidence_found")
