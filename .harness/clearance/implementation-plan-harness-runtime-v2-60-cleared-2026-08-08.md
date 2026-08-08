---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_60.md
version: v2.60
cleared_at: 2026-08-08T00:00:00-06:00
clearance_type: ratified-fork-apply-pass
back_reference:
  - .harness/class_2_fork_b116_breaker_failure_semantics_harness_internal_faults.md (FILED PR #1265)
  - .harness/council/b116-breaker-semantics/DELIVERABLE.md (merged PR #1267 — the council-unanimous package whose "Build legs implied by ratification" item 2 this plan decomposes)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.112 §14.6.3 (the spec leg this plan's U-RT-152 implements; same PR)
  - operator ratification 2026-08-07 — Reading (II)
  - .harness/post-phase-8-forward-register.md `B-111` closure bullet (PR #1260 — the recorded Class 3 probe-text trio this delta's §2 rider discharges)
  - PR '#pending' (this arc)
merge_commit: pending
reviewer_chain:
  - ratified-fork apply pass — decomposes the ratified impl leg into ONE new unit (U-RT-152) with the DELIVERABLE's own witness prescriptions (Probes B/C as assertions; positive controls incl. the store-subtype BY-NAME control; the 3/25 raise-site partition witness; PD-8 mutation probes) carried as acceptance criteria, and discharges the standing v2.60 probe-text rider (Class 3; U-RT-151 stays CLOSED, zero behaviour change).
  - empirical grounding pass at this leg — Probes B/C re-resolved to their council definitions by direct read of the contribution files (Probe B: one candidate-independent fault charging N breakers in one dispatch; Probe C: repeated misconfiguration silently converting the declared chain into a null topology, OPEN being absorbing with the dead half-open latch); the guard site, classifier and raise-site counts re-verified programmatically at HEAD `969846a0`; the rider trio carried VERBATIM from the `B-111` closure bullet at `.harness/post-phase-8-forward-register.md` (PR #1260); the ENOENT narrowing note carried from the #1263 adjudication (antecedent-never-binds). ONE rider item (the "lens-3 phase-4 vacuity nit") is CARRIED FORWARD BY NAME, not discharged — its detail was never durably recorded because the #1256 and #1263 merge-gate rows were not committed to `.harness/merge-gate-log.md` (gate-log gap surfaced at this PR rather than silently dropped).
  - out-of-family Codex E3 — quota-floored at this leg (resets Sat 2026-08-09 ~08:43; recorded deviation). Review duty: harness-adversarial-reviewer + fresh-context Opus rounds (records appended below as they run).
supersedes: implementation-plan-harness-runtime-v2-59-cleared-2026-08-07.md
---

# Clearance — `Implementation_Plan_Harness_Runtime v2.60`

v2.60 is the `B-116` plan leg: ONE new unit **U-RT-152** (the breaker-waiver guard ≈30–35 src lines across `retry_breaker_fallback.py` + `llm_dispatch.py`, the `LLMDispatchPayloadShapeInternalError` re-type of the three pre-flight payload-shape sites, the t1+t2 waived-charge emission, and the full witness set with PD-8 mutation probes), ONE new DAG edge (U-RT-58 → U-RT-152), ZERO amended units, ZERO cross-axis edges, ZERO CXA rows. The delta also discharges the standing probe-text rider owed since the U-RT-151 impl leg: the recorded Class 3 trio (two mis-homed probes, one assertion-count correction), the #1263 ENOENT-narrowing note, and — carried forward by name rather than silently dropped — the one rider item whose detail was never durably recorded.

Caveat for Phase 7 consumers: U-RT-152's partition witness pins the payload-shape raise-site split at **3/25 at this revision** — a deliberate drift tripwire, not an invariant; a future arc adding payload-shape raise sites must re-classify and re-pin as part of its own acceptance surface.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
