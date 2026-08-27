# Build plan

Team of 5, all technical. Hackathon day Friday 4 September. See Timeline below for the current schedule.

## Roles

| Role | Owns | People |
|---|---|---|
| Ingestion | `src/ingest.py`, API integration, SQLite schema | Abdur & Nuralom |
| Extraction | `src/extract.py`, prompt design, Pydantic schema | Harsh |
| Matching | `src/match.py`, embeddings, retrieval, LLM judge | Abdur & Oscar |
| Dashboard | `src/dashboard/app.py`, Plotly Dash | Kabir, can start early on mock data (can be done at the start of project) --> Dashboard Design|

Fill in names in this table once assigned.

## Work outside the four coding roles

These don't disappear just because they're not code. Someone has to own each one.

**Research**
- Read 15-20 real Hansard commitment examples once policy area's confirmed, calibrates the extraction prompt against real phrasing
- Check for prior art (mySociety/TheyWorkForYou), know before a judge asks
- Parliamentary session structure, dates, how written questions differ from oral questions
- Get judging criteria from EasyA directly

**Validation**
- Manually verify 10-15 known cases through the finished pipeline, ideally by someone who didn't build the matching stage, a fresh check is stronger than checking your own work

**Pitch and presentation**
- Deck and spoken narrative built around the "productivity, not gotcha" framing
- Responsible-AI slide: public data only, no personal profiling, human-in-the-loop, evidence-first
- Demo script, what gets clicked through, in what order
- Rehearsal against a timer

**Logistics**
- Demo machine/connectivity sorted before the day
- Backup: static export/screenshot of the working dashboard in case something breaks during setup
- Someone sanity-checks nobody's burning API credits on a runaway loop

**Coordination**
- Someone owns keeping `OPEN_QUESTIONS.md` and this file up to date so decisions don't live only in chat
- Daily or every-other-day check-in, given matching is the known risk, catch delays early

## Suggested division across 5 people

Coding work doesn't split evenly into 5, matching needs the most heads. Layer the non-coding work on top of the coding roles rather than treating it as a sixth workstream nobody owns.

| Person | Primary | Also owns |
|---|---|---|
| 1 | Ingestion | API/session research, judging criteria follow-up with EasyA |
| 2 | Extraction | Reading real Hansard examples to calibrate the prompt, doubles as domain research |
| 3 | Matching | (this role alone is close to a full-time job given no RAG experience) |
| 4 | Matching (paired with 3) | Validation of known cases once matching produces output, ideally reviews 3's work rather than only their own |
| 5 | Dashboard | Pitch deck, demo script, logistics, coordination and doc upkeep |

Adjust based on who's actually strongest where, this is a starting split, not a fixed assignment. The one thing worth keeping regardless of who goes where: validation shouldn't be done solely by whoever wrote the matching code, and the pitch/logistics work needs one clear owner so it isn't picked up last-minute on day 10.

## Timeline

Replanned from Thursday 27 August. Original plan assumed a Monday 24 start with nothing done yet on data or API access, that's 3 days lost against the original schedule. This version is compressed accordingly, and something will likely need to be cut later, most likely the LLM-judge second pass in matching or part of the validation step. Flag that trade-off explicitly if it comes to it, don't let it happen silently on day 8.

**Day 1, Thu 27 Aug (today)**
- Resolve every open item in `docs/OPEN_QUESTIONS.md` that's blocked on API/data access: confirm Hansard and Written Answers base URL, auth, rate limits, response schema
- Run the document count check for NHS at current-session scope, confirm policy area is actually workable
- Confirm exact session start/end dates, fill into `src/config.py`
- This day blocks everything else, don't start ingestion code until the API responses are confirmed against real calls, not the placeholder assumptions in `src/ingest.py`

**Day 2, Fri 28 Aug**
- Finalise DB schema against the real API response shape (update `src/db_schema.sql` if needed)
- Start ingestion coding for real
- Dashboard: start building the shell against mock/sample rows, doesn't need real data yet
- Start reading 15-20 real Hansard commitment examples to calibrate the extraction prompt

**Days 3-5, Sat 29 - Mon 31 Aug**
- Lower-sync window, expect uneven availability across the team over the weekend, plan for it rather than assuming full-speed progress
- Best suited to work that doesn't need pairing or fast turnaround: extraction prompt drafting, dashboard shell progress, research reading, prior-art check, chasing EasyA on judging criteria
- Don't schedule the start of matching/retrieval in this window, that needs full team availability given nobody's built it before

**Day 6, Tue 1 Sept**
- Full team back, ingestion pipeline should be pulling real data end to end
- Extraction tested against real text, not just the calibration sample
- Dashboard wired to sample/mock data if real data isn't through the pipeline yet

**Day 7, Wed 2 Sept**
- Matching/retrieval starts in earnest. Simplest version first: embed, cosine similarity, threshold. Target this working end to end by end of day
- This is now the tightest point in the schedule, if it slips here, the LLM-judge second pass is the first thing to cut, not the validation step

**Day 8, Thu 3 Sept**
- Add the LLM-judge second pass only if the simple matching version is solid
- Wire dashboard to real matched output
- Start manual validation against known cases, this is now compressed to about a day, don't skip it even if rushed, a handful of checked cases beats zero
- Pre-compute the final demo dataset

**Day 9, hackathon day, Fri 4 Sept**
- No live pipeline runs on stage, demo against the pre-computed dataset only
- Final dashboard polish if time allows
- Rehearse the pitch, including the honest scope/limitations line

## Definition of done for the demo

- Dashboard loads against a pre-computed dataset, no live API calls during the pitch
- Every commitment shown has a source link and search trail
- At least 10 manually-validated cases the team can defend if a judge asks "how do you know this is right"
- One slide/line on responsible-AI framing: public data only, no personal profiling, human-in-the-loop, evidence-first
