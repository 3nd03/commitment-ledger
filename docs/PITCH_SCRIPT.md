# Pitch script — draft

First pass. Edit to your own voice and time it — this reads at roughly 4-5 minutes for the talk + demo, adjust to whatever slot EasyA actually gives you.

---

## 1. Hook (~30s)

Parliament makes thousands of commitments every session — ministers promising to publish a review, fund a programme, hit a target. Right now, checking whether any specific one was kept means manually cross-referencing Hansard and written answers by hand. Nobody does this systematically. Not journalists, not opposition researchers, not the public. The volume makes it practically impossible.

## 2. What we built (~30s)

Commitment Ledger. It ingests real Hansard debates and Written Answers, uses an LLM to extract genuine policy commitments — not vague boilerplate — then embeds and retrieves candidate follow-up evidence, and uses a second LLM pass to judge whether that evidence shows the commitment was fulfilled, in progress, or not yet evidenced.

## 3. The differentiator: honesty by design (~45s)

Most AI tools optimize to look impressive. We optimized to be checkable. Three states only — no fabricated confidence scores. And "no evidence found" is deliberately framed as a statement about *our search*, not an accusation against the minister — we might just not have found it yet.

Every single verdict ships with a source link, the actual evidence quote, and a full search trail: which documents we checked, how similar each one was, and why we did or didn't count it as evidence. You can audit every claim this tool makes.

## 4. Live demo (~90s)

*(runs against a pre-computed dataset — no live API calls on stage)*

- Load the dashboard. Point at the top callout: 386 documents in, 483 commitments extracted, honest split of outcomes.
- **Hero example** — click into: *"Recruiting an additional 8,500 mental health workers this Parliament, three years ahead of schedule."* Marked fulfilled. Show the evidence quote — near-verbatim government confirmation — and the source link.
- Click a `no_evidence_found` row. Open the search trail. Show the candidates that *were* checked and why none counted as evidence — this is the receipts, not a black box.
- Scroll the charts: commitments over time, most-tagged topics, department breakdown (log scale, since one department dominates a single-policy-area pilot).

## 5. Credibility beat: we caught our own bugs (~30-45s)

While building this, we found that the government's own Written Answers API was silently truncating 97% of official answers to 258 characters — we were judging evidence on a preview, not the real record. We also found a JSON-parsing bug that was discarding every genuine "fulfilled" verdict as "unrelated." We fixed both, then personally re-verified every single fulfilled result by hand — and downgraded ones that didn't hold up, even after the fixes. That's not a caveat. That's the point: a tool that checks itself is worth more than one that doesn't.

## 6. Honest limitations (~20-30s)

Scoped to one policy area — NHS — and the current parliamentary session. This demo runs against a frozen, pre-computed dataset; no live calls during the pitch. Our retrieval isn't perfect — we manually found cases where real evidence existed but our system's search missed it, and in every one of those cases we chose to report "no evidence found" rather than guess.

## 7. Responsible AI (~15-20s)

Public data only. No personal profiling. Evidence-first, not confidence-fabricating. Human-in-the-loop validation throughout the build, not just at the end.

## 8. Close (~15s)

This is what government-accountability tooling looks like when it refuses to lie to you.

---

## Anticipated judge questions (prep, not to read verbatim)

- **"How do you know this is right?"** → Point at the search trail + source links. Mention the manual validation pass and the two bugs caught and fixed.
- **"Why only 7 fulfilled out of 483?"** → Session started mid-May, most commitments genuinely haven't had time to resolve. Low fulfilled count is honest, not a failure — we'd rather show 7 real ones than pad the number.
- **"Could this scale to other policy areas?"** → Yes, the pipeline is policy-area-agnostic (`config.py` swap); NHS was chosen for hackathon-scope reasons (data volume, team familiarity), not a technical limit.
- **"What's the biggest weakness?"** → Embedding retrieval sometimes misses evidence that exists elsewhere in the corpus (be ready to describe the workforce-plan case briefly if asked) — we chose to under-claim rather than guess.
- **"Is this real government data?"** → Yes — live Hansard and Written Answers APIs, not synthetic/mocked data.
