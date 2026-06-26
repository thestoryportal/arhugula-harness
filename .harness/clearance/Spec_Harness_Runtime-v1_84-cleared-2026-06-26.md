---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.84
cleared_at: 2026-06-26T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Control_Plane_v1_74.md §1 (the PRIMARY consumer delta — the crash-durable scoped-abort persistence + reconstruct; this runtime delta is the paired store disposition vocabulary extension)
  - design-substrate/Spec_Harness_Runtime_v1.md §14.23 C-RT-32 (the EngineOutputStore per-branch disposition vocabulary {completed, timed_out} → {completed, timed_out, scoped_aborted}, additive)
  - harness-runtime/src/harness_runtime/lifecycle/engine_output_store.py (the _read_last_branch_disposition closed-set guard accepts "scoped_aborted"; record_branch / read_branch_records docstrings)
  - .harness/clearance/Spec_Control_Plane-v1_74-cleared-2026-06-26.md (the paired CP marker — full reviewer chain)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor (full-transcript) — directed the replay-store-vs-IS-ledger determination (the store terminal_status is a free str disjoint from the IS Literal → record the distinguishing value in the store, keep the IS ledger at "completed") + caught that the read-back guard is ENFORCED (an unknown disposition is treated as corruption → fail-closed), so "scoped_aborted" MUST be added to the accept-set or a mixed abort+survivor recovery wrongly fails closed. Full chain in the paired CP v1.74 marker.
  - out-of-family Codex — diff review owed pre-merge.
  - by-execution witnesses: the real-store scoped_aborted round-trip + not-in-corrupt-set (test_engine_output_store.py — RED-without-fix verified: without the accept-set extension the record is dropped → surfaced as corrupt); 37 store tests pass; the CP consumer full-chain witnesses (paired CP v1.74). pyright 0/0/0; ruff clean.
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.84`

v1.84 is a **change-note-level bundled-absorption** delta (co-published with `harness-runtime` + `harness-cp` impl + tests + the paired CP delta v1.74) — the runtime half of the registered R-FS-1 arc `B-FANOUT-EFFECT-FENCE-SCOPED-ABORT-CRASH-DURABLE`.

- **The §14.23 C-RT-32 `EngineOutputStore` per-branch disposition vocabulary grows additively** `{completed, timed_out}` → `{completed, timed_out, scoped_aborted}`. A `scoped_aborted` branch is one the operator scoped-aborted via `EffectFenceResolution.ABORT_BRANCH` (CP v1.74 §1): output `None`, never re-dispatched, recorded DISTINCT from a ran-and-errored `completed`-no-output. The read-back closed-set guard (`_read_last_branch_disposition`) accepts it (an unknown value still fails closed as corruption).
- **No new field, no new contract, no §5.2 IS-hash change.** `record_branch` already accepts a free-form `terminal_status` str; only the read-back accept-set + the docstring vocabulary change. The IS-hash-bearing F2 ledger terminal entry for the SAME branch stays `completed` — the distinguishing value lives ONLY in the runtime crash-resume store (a free-form string disjoint from the IS `terminal_status` Literal).

## Caveats for Phase 7 consumers

- Change-note-level: ADDITIVE. No new contract, no new field, no new fail-class, no §5.2-hash change, no StepDispatcher Protocol widening, no new CXA edge. The §14.23.1–.7 + the v1.59–v1.83 narrative PRESERVED VERBATIM. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.
- **CP spec C-CP-25 §25.15 / C-CP-26 §26.8 v1.73 → v1.74** is the paired PRIMARY contract.
