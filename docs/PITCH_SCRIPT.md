# Pitch script, draft

Two different formats, per the actual schedule:
- **12:15-13:15, table round.** Judges circulate and you don't know how long any one of them will stay, could be one sentence, could be a full conversation. Structured as layers below: always land the first layer, then keep going only as far as they let you.
- **13:15-14:00, stage, finalists only, strict 2:00 per team.** Now mapped directly onto the 5 slides in the actual deck (Title, Problem, Solution, Impact, Future), so what you say lines up with what's on screen instead of running as a separate monologue.

Edit both to your voice and rehearse against a timer, 2:00 on stage is unforgiving.

---

## Table round (12:15-13:15): layered opener

Say layer 1 no matter what. Only continue to the next layer if they're still listening.

**Layer 1, the whole pitch in one breath if that's all the time you get:**

> Commitment Ledger. We check whether Parliament's promises were actually kept.

**Layer 2, if they pause:**

> Real Hansard and Written Answers, an LLM extracts genuine commitments, then verifies each one against later records: fulfilled, in progress, or no evidence found, honestly, no padded numbers, every verdict linked to its source.

**Layer 3, if they're engaged, invite the demo:**

> Want me to show you one?

Then follow their lead. Have these ready to pull up on demand:

- **The hero example**: *"Recruiting an additional 8,500 mental health workers this Parliament, three years ahead of schedule"* → fulfilled, near-verbatim government confirmation, source link right there.
- **A `no_evidence_found` search trail**: click a row, show the candidate documents considered and rejected. Proves it's not a black box.
- **The bug-catching story**, if they ask "what was hard" or "how do you know it's accurate": the government's own Written Answers API was silently truncating 97% of official answers to 258 characters. Caught it, fixed it, manually re-verified every fulfilled result by hand afterward.
- **Scope honesty**, if asked why numbers look small: single policy area (NHS), current session only, most commitments are simply too recent to have resolved yet.

## Stage pitch (13:15-14:00): strict 2:00, mapped to the deck

Target ~165-175 words spoken (~65-80s at a normal-to-slow pace), leaving real buffer for 5 slide transitions plus the switch to the live dashboard.

**[Title slide — just said as it appears, no need to linger]**

> Commitment Ledger. Parliament said it, did it happen?

**[Problem slide]**

> MPs tabled over 80,000 written questions last year, 92% answered on time. But answered isn't fulfilled. Nobody actually measures whether those commitments were kept.

**[Solution slide]**

> We built a pipeline that ingests real Hansard and Written Answers, has an LLM extract genuine commitments, retrieves candidate evidence, and judges each one: fulfilled, in progress, or no evidence found. No fabricated confidence. Every verdict linked to its source.

**[switch to live dashboard — hero example]**

> Take this one: recruiting 8,500 mental health workers, three years ahead of schedule. Fulfilled. Verbatim government confirmation, right here.

**[credibility beat]**

> We even caught our own mistakes. The government's own API was silently truncating 97% of official answers. We fixed it and re-verified every result by hand.

**[Impact slide]**

> For committees, that's a standing record instead of re-reading Hansard. For MPs, a question with the receipt attached. For departments, acting before someone asks. For the public, a source to check.

**[Future slide, close]**

> Same data. Same words. Just tracked. Next, we bring in the spoken record too.

**If it's running long in rehearsal, cut in this order**: the credibility beat first (it's the strongest differentiator but the most cuttable if desperate), then compress the Impact slide to one line ("Same access, for everyone who has to check it") rather than naming all four groups.

---

## Anticipated judge questions (prep, not to read verbatim)

- **"Where's that 80,810 / 92% figure from?"** → House of Commons Library research briefing CBP-10632, "Written parliamentary questions from MPs: Recent trends" (2025), and the Commons Procedure Committee's "Written parliamentary questions: Departmental performance in Session 2023-24". Full links are in the speaker notes on the Problem slide.
- **"92% answered on time, so doesn't that mean it already works fine?"** → No. "Answered on time" only means a written answer was *given* by deadline. It says nothing about whether the promised action inside that answer was ever actually done. That gap is the entire premise of the tool.
- **"Why is 'mental health' so far ahead on the topics chart?"** → It reflects how often a commitment was *restated* across multiple written answers and Hansard sittings by different ministers, not the number of distinct promises. Real parliamentary repetition, not a duplicate-counting bug — worth saying so before a judge assumes it's an error.
- **"How does 'SEARCH' actually work?"** → It's two steps, not one: embedding-based retrieval finds candidate documents, then a separate LLM pass judges whether the retrieved passage is actually evidence. Don't let "search" sound like a black box if pressed.
- **"How do you know this is right?"** → Point at the search trail and source links. Mention the manual validation pass and the two bugs caught and fixed.
- **"Why only 7 fulfilled out of 483?"** → Session started mid-May, most commitments genuinely haven't had time to resolve. Low fulfilled count is honest, not a failure. We'd rather show 7 real ones than pad the number.
- **"Could this scale to other policy areas?"** → Yes, the pipeline is policy-area-agnostic (`config.py` swap). NHS was chosen for hackathon-scope reasons (data volume, team familiarity), not a technical limit.
- **"What's the biggest weakness?"** → Embedding retrieval sometimes misses evidence that exists elsewhere in the corpus (be ready to describe the workforce-plan case briefly if asked). We chose to under-claim rather than guess.
- **"Is this real government data?"** → Yes. Live Hansard and Written Answers APIs, not synthetic or mocked data.
- **"Who built what?"** → *(fill in before tomorrow — have a comfortable, honest answer ready for how the 5-person team split the 9-day build, not just tonight's work)*
