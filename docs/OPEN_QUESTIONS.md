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

**Q1:**
Team is thinking that NHS might be the best policy area of choice since there are more docs and rich in data as well as greater access to Hansard and Written and Answer Questions APIs.

**Q2:**
Date range could be last 10 years to see before & after for NHS. This needs to be explored further. 

**Q3:**
Each person uses their own API keys for Hansard and Written Questions and Answers. Shouldn't affect the codes. 
