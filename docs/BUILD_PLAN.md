# Build plan

Team of 5, all technical. Start Monday 24 August, hackathon day Friday 4 September.

## Roles

| Role | Owns | People |
|---|---|---|
| Ingestion | `src/ingest.py`, API integration, SQLite schema | 1-2 |
| Extraction | `src/extract.py`, prompt design, Pydantic schema | 1 |
| Matching | `src/match.py`, embeddings, retrieval, LLM judge | 1-2 (biggest risk, most time) |
| Dashboard | `src/dashboard/app.py`, Plotly Dash | 1, can start early on mock data |

Fill in names in this table once assigned.

## Timeline

**Days 1-2 (Mon-Tue)**
- Resolve every starred item in `docs/OPEN_QUESTIONS.md`
- Confirm API access and pull real sample data
- Agree final DB schema (`src/db_schema.sql`)
- Pull document counts for candidate policy areas, pick one

**Days 3-5 (Wed-Fri)**
- Ingestion pipeline running end to end against real data
- Extraction: build and test against 15-20 manually-read real commitment examples
- Dashboard: build shell against mock/sample rows, don't wait for real data

**Days 6-8 (weekend + Mon)**
- Matching/retrieval, start this early, it will take longer than expected
- Wire dashboard to real matched output

**Days 9-10**
- Manually validate 10-15 known cases through the full pipeline, check the "no evidence found" cases are actually correct
- Fix false negatives found in validation, this is the most important bug class in the whole project

**Day 11 and hackathon day (4 Sept)**
- Pre-compute the final demo dataset, do not plan to run the pipeline live on stage
- Polish dashboard styling
- Rehearse pitch, including the honest limitations line ("scoped to X policy area, this session, as proof of concept")

## Definition of done for the demo

- Dashboard loads against a pre-computed dataset, no live API calls during the pitch
- Every commitment shown has a source link and search trail
- At least 10 manually-validated cases the team can defend if a judge asks "how do you know this is right"
- One slide/line on responsible-AI framing: public data only, no personal profiling, human-in-the-loop, evidence-first
