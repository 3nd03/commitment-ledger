# Commitment Ledger

AI tool that tracks parliamentary commitments made in Hansard and written answers, and checks whether they've been followed up. Built for the UK Parliament Hackathon with EasyA, 4 September 2026.

## Problem

Parliament generates huge volumes of debates, written answers and committee reports. There's no automated way to connect a minister's original commitment to whatever evidence exists later that it was acted on.

## Scope (v1)

- One policy area (health or housing, TBC after volume check)
- One parliamentary session
- Sources: Hansard API, Written Questions and Answers API

## Status model

Three states only, no fabricated confidence scores:
- `fulfilled`
- `in_progress`
- `no_evidence_found`

Every status is backed by the original commitment quote, source link, what was searched, and last checked date.

## Pipeline

1. **Ingest** (`src/ingest.py`): pulls debates and written answers, stores raw text in SQLite
2. **Extract** (`src/extract.py`): LLM pulls structured commitments out of the raw text
3. **Match** (`src/match.py`): embeds commitments and candidate passages, retrieves, LLM judges whether it's follow-up evidence
4. **Dashboard** (`src/dashboard/app.py`): Plotly Dash, shows department/topic view by default

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # fill in API keys
```

## Environment variables

See `.env.example`. You need an LLM API key (Claude or OpenAI) and an embeddings API key. The parliamentary APIs (Hansard, Written Questions) don't need a key, but check the rate limits before the build week starts, see `docs/OPEN_QUESTIONS.md`.

## Running

```bash
python src/ingest.py       # populates data/ledger.db
python src/extract.py      # extracts commitments into DB
python src/match.py        # matches commitments to follow-up evidence
python src/dashboard/app.py  # runs Dash app on localhost:8050
```

## Team roles

See `docs/BUILD_PLAN.md`.

## AI use disclosure

AI was used for scaffolding, error checking, and review during the build. Logic, scoping, and framing decisions are the team's own. No AI attribution in commits or this README.