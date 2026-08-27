# Open questions — resolve before/on day 1

These block or shape the build. Don't start Stage 3 work until the starred ones are answered.

- [ ] **Policy area**: health/NHS or housing? Pull document counts for both before deciding.
- [ ] **Session/date range**: which parliamentary session, confirm start/end dates.
- [ ] ***Hansard API**: confirm base URL, auth (should be none), rate limits, and response schema against the live docs, not memory. Endpoint structure in `src/ingest.py` is a placeholder until this is checked.
- [ ] ***Written Questions and Answers API**: same check as above.
- [ ] Committees API: in or out of scope for v1? Currently dropped.
- [ ] **Document volume**: how many debates/answers fall in the chosen policy area + session? Determines whether Stage 3 is feasible as scoped.
- [ ] **LLM provider**: Claude or OpenAI, whichever the team has credits/keys for. Affects `src/extract.py` and `src/match.py` client setup.
- [ ] **RAG experience**: has anyone on the team built embedding + retrieval before? Changes the time budget for Stage 3.
- [ ] **Judging criteria**: ask EasyA directly if not already published.

Update this file as answers come in, don't let them live only in Slack/WhatsApp.

**Kabir's Answers**
**Q1:**
Team is thinking that NHS might be the best policy area of choice since there are more docs and rich in data as well as greater access to Hansard and Written and Answer Questions APIs.

**Q2:**
Date range could be last 10 years to see before & after for NHS. This needs to be explored further. change date range from 10 years to Current parliamentary session only

**Q3 & Q4:**
Each person uses their own API keys for Hansard and Written Questions and Answers. Shouldn't affect the codes. 

**Q5:**
This can only be answered once we have access to APIs

**Q8:**
Email sent for clarification; response will be added soon!

**Oscar's Answers**
- [ ] Policy area: leaning NHS (team's stated reason: more documents, richer data). Not yet verified, no document count pulled. Do the count check (hansard.parliament.uk/search + questions-statements.parliament.uk) before locking this in, see BUILD_PLAN.md day 1-2.
- [ ] [x] Session/date range: current parliamentary session only. Decided against 10 years due to volume, cost, and pitch framing risk (see BUILD_PLAN.md). Pull exact session start/end dates from parliament.uk and fill into src/config.py.
- [ ] *Hansard API: confirm base URL, auth (should be none, it's open public data), rate limits, and response schema against the live docs, not memory. Endpoint structure in src/ingest.py is a placeholder until this is checked. Not yet done.
- [ ] *Written Questions and Answers API: same check as above, also open and public, no key needed. Not yet done.
- [ ] [x] Committees API: out of scope for v1, confirmed. No RAG experience on the team (see below) makes the simpler two-source pipeline the right call, don't add a third source until Hansard + Written Answers matching actually works end to end.
- [ ] Document volume: how many debates/answers fall in the chosen policy area + session? Blocks the policy area decision above, do this first.
- [ ] [x] LLM provider keys: each team member uses their own individual API keys for Claude and OpenAI (Claude for extraction/judging, OpenAI for embeddings, per the existing src/config.py setup). Decided.
- [ ] [x] RAG experience: no one on the team has built embedding + retrieval before. This is new ground for everyone. Implication: budget more time for Stage 3 than the original plan assumed, and consider a simpler v1 (embedding similarity threshold only, no second-pass LLM judge) with the LLM judge added only if time allows, see updated note in BUILD_PLAN.md.
- [ ] Judging criteria: ask EasyA directly if not already published. Not yet done.
Update this file as answers come in, don't let them live only in Slack/WhatsApp.
