# Pitch script, draft

Two different formats, per the actual schedule:
- **12:15-13:15, table round.** Judges circulate, you demo live and talk one-on-one. No hard clock, but each judge only stops briefly, so lead with a tight hook and let *them* drive with questions.
- **13:15-14:00, stage, finalists only, strict 2:00 per team.** This is a monologue with a hard cap. Assume the 2:00 includes any screen-switch lag. The script below runs about 80-90 seconds spoken, leaving real buffer.

---

## Table round (12:15-13:15): opener + talking points

**Opener (~30-40s, then stop and let them respond):**

> Hey, this is Commitment Ledger. Parliament makes thousands of policy commitments a session and nobody systematically checks if they were kept. We built a pipeline that pulls real Hansard and Written Answers, has an LLM extract genuine commitments, then verifies each one against later government records: fulfilled, in progress, or no evidence found. Honestly, no padded numbers. Every verdict has a source link and a full search trail so you can audit it yourself. Want me to show you one?

Then follow their lead. Have these ready to pull up on demand:

- **The hero example**: *"Recruiting an additional 8,500 mental health workers this Parliament, three years ahead of schedule"* → fulfilled, near-verbatim government confirmation, source link right there.
- **A `no_evidence_found` search trail**: click a row, show the candidate documents considered and rejected. Proves it's not a black box.
- **The bug-catching story**, if they ask "what was hard" or "how do you know it's accurate": the government's own Written Answers API was silently truncating 97% of official answers to 258 characters. Caught it, fixed it, manually re-verified every fulfilled result by hand afterward.
- **Scope honesty**, if asked why numbers look small: single policy area (NHS), current session only, most commitments are simply too recent to have resolved yet.

## Stage pitch (13:15-14:00): strict 2:00

Read-through target: ~85-95 seconds of speech, leaving buffer for the screen switch to the live dashboard.

> Parliament makes thousands of policy commitments a session. No one checks if they were kept. The volume makes it impossible by hand.
>
> We built Commitment Ledger. It ingests real Hansard and Written Answers, has an LLM extract genuine commitments, then verifies whether later government records show each one was fulfilled, in progress, or not yet evidenced.
>
> What makes this different: we didn't build it to look impressive. We built it to be checkable. No fabricated confidence scores. Three honest states, and every verdict ships with a source link and the actual evidence quote.
>
> *[switch to dashboard]* Take this one: "Recruiting 8,500 mental health workers, three years ahead of schedule." Fulfilled. Verbatim government confirmation, right here.
>
> And we don't just trust our own pipeline. While building this, we found the government's own API was silently truncating 97% of official answers. We were judging evidence on a preview, not the real record. We caught it, fixed it, and manually re-verified every fulfilled result by hand.
>
> This is what government accountability tooling looks like when it refuses to lie to you.

**If there's time left after rehearsing** (there probably won't be, but in order of priority to add back in): one line on scope (NHS, current session only), then responsible-AI framing (public data only, no profiling, evidence-first).

---

## Anticipated judge questions (prep, not to read verbatim)

- **"How do you know this is right?"** → Point at the search trail and source links. Mention the manual validation pass and the two bugs caught and fixed.
- **"Why only 7 fulfilled out of 483?"** → Session started mid-May, most commitments genuinely haven't had time to resolve. Low fulfilled count is honest, not a failure. We'd rather show 7 real ones than pad the number.
- **"Could this scale to other policy areas?"** → Yes, the pipeline is policy-area-agnostic (`config.py` swap). NHS was chosen for hackathon-scope reasons (data volume, team familiarity), not a technical limit.
- **"What's the biggest weakness?"** → Embedding retrieval sometimes misses evidence that exists elsewhere in the corpus (be ready to describe the workforce-plan case briefly if asked). We chose to under-claim rather than guess.
- **"Is this real government data?"** → Yes. Live Hansard and Written Answers APIs, not synthetic or mocked data.