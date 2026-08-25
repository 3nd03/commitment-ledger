import os
from dotenv import load_dotenv

load_dotenv()

# TODO: fill in once policy area and session are confirmed, see docs/OPEN_QUESTIONS.md
POLICY_AREA = None  # e.g. "health"
SESSION_START = None  # e.g. "2024-07-17"
SESSION_END = None

DB_PATH = os.getenv("DB_PATH", "data/ledger.db")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

STATUSES = ("fulfilled", "in_progress", "no_evidence_found")
