---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.107
cleared_at: 2026-07-30T00:00:00-04:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/council-b69-pause-state-accessor-2026-07-30.md
  - .harness/council-b69-pause-state-accessor-2026-07-30.md §14 (ratification addendum — operator AskUserQuestion 2026-07-30, OPTION A′)
  - .harness/forward-register.yaml row B-69
merge_commit: <pending — this PR>
reviewer_chain:
  - council voices C10 (action safety / blast radius, promoted primary) + C11 (operator loop / local deployment, primary) + C9 (reliability / recovery, consultant) — genuine dedicated agent invocations, reconciled to zero twice
  - harness-adversarial-reviewer in-family pass (0 Class 3 · 7 Class 2 · 4 Class 1 — "cleared with current-phase revision")
  - out-of-family `just codex-review-uncommitted` (GPT-5.6) on the council record — 4 × [P1] + 1 × [P2], near-zero overlap with the in-family pass
  - operator AskUserQuestion ratification 2026-07-30 — OPTION A′ (CO-REQUISITE, SEQUENCED)
  - spec-writer apply pass (this arc) + out-of-family `just codex-review-uncommitted` on the applied delta
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.107`

v1.107 is the Runtime-owned leg of the RATIFIED **B-69 durable-pause-state read accessor arc**. It carries three surfaces plus one co-requisite invariant declaration. **(A) NEW §31 C-RT-36** — a public async read on the `harness_runtime` package root taking the identical `(workflow, resume_handle, config)` triple `resume()` requires, returning a CLOSED discriminated union of the council record's **FOUR** location variants (`HitlAddressable` / `EffectFenceAddressable` / `UniformFallbackOnly` / `TransitivelyPaused`) spanning **SEVEN-PLUS source shapes**, with fields declared PER SOURCE SHAPE and a sub-discriminator required on multi-shape variants. **One reversal is on the record:** a draft declared a FIFTH variant for the empty-`idempotency_key` crash-reconstruction carrier; out-of-family review round 11 [P1] showed that would **break the one-authority invariant** (the empty-key distinction is not derivable from CP properties 1-8 — the authoritative walk includes it, the uniform-fallback computation counts it, only the abort walk filters it), so it is modelled as an `EffectFenceAddressable` SOURCE SHAPE **with the key field ABSENT** — same foreclosure, no second authority, variant set unchanged from the record, keyed `workflow_id`-only, fail-closed on inability to mint its staleness token, with a five-member cause-attribution vocabulary and the declared no-gate / no-HITL-trigger / no-internal-retry postures. **(B)** the discharge of §30 `:3274`'s registered scope-limit sentence, replaced by a cross-reference rather than left as stale-carry. **(C) NEW §30 refusal-only staleness precondition** plus a cause-attribution refinement on the EXISTING `RT-FAIL-RESUME-HANDLE-UNKNOWN` — **one** new fail class (`RT-FAIL-RESUME-PAUSE-STATE-STALE`), **no** new peer class for the attribution. **(C-co-requisite) NEW §14.14.8 substrate invariant** — the per-workflow pause journal is append-only and **never truncated**, stated because §30's absolute token property was otherwise resting on an unstated implementation fact.

**Contract-number choice, recorded because the council left it to the spec-writer.** A NEW `C-RT-36` at a NEW top-level §31 was chosen over the alternative §14.14.9-sibling home: §14.14.x is C-RT-24 territory (the `PauseResumeProtocol` ctx-binding and its internal durable substrate), whereas this surface is a caller-facing package-root Python API — structurally the second member of the class C-RT-35 §30 (`resume()`) already occupies. This file's own `:680` framing ("no new operation") is the discriminator: v1.46's changes were not new operations; this one is.

**Ratified scope + closure criterion (X-AL-2 conjunctive form).** **B-69 closes iff *(accessor landed)* ∧ *(staleness precondition landed ∧ exercised by the W3 mutation-probe)*. Partial is non-closure.** Spec surfaces and impl units MAY land in separate merges within the arc, subject to one ordering constraint: **the staleness precondition lands FIRST OR SIMULTANEOUSLY — never after.** The criterion is recorded **verbatim** at the `B-69` register row's `close_out`. **Enforcement is a pre-merge review obligation on the closing PR, not a validator rule** — `tools/forward_register.py --check` validates `close_out` presence and a closed row's PR cite without parsing the conjunction, so a reviewer MUST confirm both conjuncts (W3 green) before flipping `closed`. Structured per-conjunct fields plus validator support are a `tools/` change outside a doc-only spec leg's scope and are registered at the row.

**Caveats for Phase 7 consumers.** Spec + impl do NOT land together — the impl arc follows (Runtime plan v2.55 U-RT-148). The staleness token is stated as a **PROPERTY, never a composition**; a session that names `snapshot_hash` or `(snapshot_hash, created_at)` as the carrier is re-making the error the council's P4 probe caught. Four findings are surfaced but **NOT patched**, and they do NOT all get register rows — the distinction matters for anyone auditing the tracking surface. **THREE are REGISTERED as new rows:** the pause journal's absent tenant binding (**B-97**); gate-description absence from every durable pause carrier (**B-98**); the `summary_text` reopening condition (**B-99**). **The FOURTH — the journal-vs-HITL-queue posture divergence — is RECORDED IN-SPEC, NOT ACTIONED and NOT registered**, because unifying tier semantics is a persistence-layer question and scope creep here; what it leaves behind is a binding *constraint* (the projection must not be shaped to imply the journal IS the queue), not a work item. *(Stated explicitly at out-of-family review round 10 [P2], which caught this paragraph implying all four had register entries.)*

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
