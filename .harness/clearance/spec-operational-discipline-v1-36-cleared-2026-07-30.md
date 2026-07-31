---
artifact: design-substrate/Spec_Operational_Discipline_v1_36.md
version: v1.36
cleared_at: 2026-07-30T00:00:00-04:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/council-b69-pause-state-accessor-2026-07-30.md
  - .harness/council-b69-pause-state-accessor-2026-07-30.md §6.5 (trace emission ruled REQUIRED) + §9 row 5b (namespace determination delegated to OD)
  - .harness/forward-register.yaml row B-69
merge_commit: <pending — this PR>
reviewer_chain:
  - council voices C10 + C11 + C9 (the emission obligation was declared by all three; the schema was named as owed, not authored, at the convening)
  - harness-adversarial-reviewer in-family pass — which itself ADDED this delta row after finding the first draft ruled the emission REQUIRED but gave it no §9 delta row
  - out-of-family `just codex-review-uncommitted` (GPT-5.6)
  - operator AskUserQuestion ratification 2026-07-30 — OPTION A′
  - spec-writer apply pass (this arc), which made the namespace determination the council delegated
---

# Clearance — `Spec_Operational_Discipline_v1_36.md`

v1.36 is the OD-owned leg of the RATIFIED **B-69 durable-pause-state read accessor arc**. It carries exactly ONE new section — **§C-OD-30.5** — declaring the observability home for the two events the council's §6.5 ruled REQUIRED: the §14.14.9 accessor read, and a `resume()` refused on the §30 staleness precondition.

**The determination this delta was filed to make.** Grounding produced a **split** answer, which is why a bare "it rides existing" sentence in a sibling spec's change-note would not have discharged the obligation. Both events belong in C-OD-30's existing family — but **neither is representable by the existing payload composition unchanged**. The **accessor read** is neither a `PauseEvent` nor a `(ResumeAttempt, ResumeOutcome)` pair but a **third event class**. The **staleness refusal** is raised **PRE-BOOTSTRAP**, before any `(ResumeAttempt, ResumeOutcome)` exists, so it composes through neither existing helper nor the CP→OD converter's `resume:` branch — and `PauseResumeAuditPayload` is `frozen` + `extra="forbid"` with no staleness-token field, so the token cannot ride it. **Ruling: both events emit within the EXISTING C-OD-30 `pause.*` / `resume.*` family; NO new top-level namespace is minted; the C-OD-05 §5.1 roster is UNCHANGED; the read is declared as a new event kind; and §30.5.2 AUTHORIZES an additive carrier for the refusal (an additive field or a sibling payload type — impl discretion), with the existing payload field set and both existing helpers otherwise PRESERVED VERBATIM.**

**One correction on the record.** A first draft of this delta asserted the refusing resume needed *"no new payload type and no new converter branch."* Out-of-family review round 2 found **both halves false** — on timing (pre-bootstrap) and on schema (frozen, `extra="forbid"`, no token field). The claim is corrected in place in the delta rather than quietly repaired, and the plan consequence is **UNCONDITIONAL**: **an OD plan delta is owed AT THE IMPL LEG under EITHER §30.5.2 carrier option** — option (a) mutates the OD-owned frozen payload and option (b) adds a sibling type beside it, and a Runtime unit can own neither. *(An earlier draft of this paragraph made the obligation conditional on option (b) or a helper, which left option (a) unowned; corrected at review rounds 3 and 14 [P2].)*

**The load-bearing requirement is the PAIRING.** The same staleness token must be emitted at **both** the read and the refusing resume, so a stale-read refusal is reconstructable as **one causal pair from telemetry alone** — without which the refusal's own operator-facing text is unverifiable after the fact.

**Plan disposition, recorded as a decision rather than an oversight — and an OD plan delta IS OWED at the impl leg under EITHER carrier option.** The **emission** is Runtime-side and pre-bootstrap, so its witnesses ride Runtime plan v2.55's U-RT-148 (AC #13) where the producing code lands. The **carrier**, however, is an OD-owned schema surface **under both** §30.5.2 options — option (a) mutates the `frozen` / `extra="forbid"` `PauseResumeAuditPayload` this axis declares, and option (b) adds a sibling type alongside it — and **a Runtime plan unit cannot own an OD schema change or supply its acceptance criteria.** `[HIGH]` **Therefore: whichever option is selected, an OD plan delta assigning the carrier to an OD unit is OWED AT THE IMPL LEG**, with its own ACs (schema shape; `frozen` / `extra="forbid"` posture preserved; and, for option (a), a byte-compat witness that every existing `PauseResumeAuditPayload` construction site is unaffected). Runtime plan v2.55 records the resulting ordering constraint as a **pending, not-yet-numbered OD dependency** of U-RT-148, so the Runtime unit is not scheduled ahead of it. *(Corrected at out-of-family review rounds 3 [P1] and 5 [P1]: an earlier draft of this marker made the OD delta conditional on option (b) or a helper, which left option (a) — an OD schema mutation — unowned and without acceptance criteria.)* **No OD plan delta is filed at THIS leg** because the carrier's shape is impl discretion between two live options, and pre-authoring a unit for an unchosen shape would fix by plan what §30.5.2 deliberately leaves open — the obligation is registered as owed, not deferred silently.

**Caveats for Phase 7 consumers.** §C-OD-30.1–§C-OD-30.4 are PRESERVED VERBATIM; `PauseResumeAuditPayload` is unchanged. Concrete OTel attribute keys, payload field names, emission call sites, and the helper question are **deferred to implementation discretion** — the delta states the obligation and its required content, not a schema for a producer that does not yet exist. The redaction posture is **NOT ENGAGED because nothing redactable is emitted**, with a registered reopening condition: if a future arc admits `summary_text` into the projection, this posture MUST be re-adjudicated in the same arc, with a redaction contract as a precondition of any inclusion.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
