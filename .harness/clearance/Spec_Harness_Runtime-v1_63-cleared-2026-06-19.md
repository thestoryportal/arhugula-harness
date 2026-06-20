---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.63
cleared_at: 2026-06-19T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — a NEW additive contract §14.23 C-RT-32 + an opt-in RuntimeConfig flag + an additive HarnessContext field; materializes the R-CC-1 design §1.1 self-documented MVP re-open trigger for the linear case, the B-FANOUT-PAUSE precedent, not a committed-invariant sacrifice)
back_reference:
  - .harness/class_2_fork_b_engine_output_replay_output_carrying_substrate.md
  - .harness/r-fs-1-e-impl-1-finding.md (§2/§4 — the registered build arc this absorbs)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-ENGINE-OUTPUT-REPLAY spine BUILT note + forward arcs)
  - .harness/clearance/Spec_Control_Plane-v1_42-cleared-2026-06-19.md (B-FANOUT-PAUSE — the §1.1-reuse precedent)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — probe-resolved the substrate-shape fork to a dedicated store (IS-purity + I-6 + ADR-F2 + JournalWorkflowPauseStore precedent foreclose the IS-extension), surfaced the store↔ledger SKEW correctness rule (RESERVE-before-COMMIT + rehydrate-by-resume_at + fail-closed), confirmed the §1.1-reuse no-gate disposition
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.63`

v1.63 is an additive delta over v1.62 absorbing the **R-FS-1 standalone arc `B-ENGINE-OUTPUT-REPLAY`** — a NEW contract **§14.23 C-RT-32 `EngineOutputStore`**, the output-carrying event-history substrate that materializes the C-CP-08 §8.1 `engine_replay` "activity outputs cached and replayed" clause for LINEAR `EVENT_SOURCED_REPLAY` (degenerate at HEAD per E-impl-1 Finding 2 — the F2 ledger stores a `response_hash` digest, not outputs, and a skip-prefix resume leaves the inter-step channel fresh-empty).

**NO operator gate.** The completed-step output recovery breaks the R-CC-1 design §1.1 position-only resume model, but §1.1 is a self-documented MVP scoping note with an explicit §6 re-open trigger — this arc IS that designed re-open firing (the linear analogue of B-FANOUT-PAUSE's fan-out re-open). Adopt-and-note + clearance under the FULL-SPEC directive; the B-FANOUT-PAUSE gate-discriminator reused verbatim. Additive contract + opt-in flag (`engine_output_replay`, default off → byte-identical); no committed-invariant sacrifice.

Reviewed during clearance: the substrate-shape probe-resolution (dedicated runtime store over the IS `EntryPayload` extension — the IS ledger stores a digest by design; extending it ripples the §5.2 hash + JSONL shape + IS contract; I-6 + ADR-F2 + the `JournalWorkflowPauseStore` precedent foreclose); the **store↔ledger SKEW** correctness rule (the producer writes BEFORE the ledger-append `resume_at` counts — RESERVE-before-COMMIT — and rehydration is driven by `resume_at` with fail-closed-on-missing-output/identity-mismatch, the B-FANOUT-PAUSE symmetry); the keying by `run_idempotency_key` (the stable id the resume join uses); the narrow observable surface (`most_recent_output()` → "first re-dispatched step reads its recovered predecessor"); the capability-built-not-fires-in-production framing; LINEAR EVENT_SOURCED_REPLAY only (WAL_SEGMENT + non-linear registered forward arcs).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-runtime + harness-cp impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- IS spec UNCHANGED (dedicated store; the F2 `EntryPayload` byte-unchanged); CP spec UNCHANGED (the CP driver consumes the store via the `cp_is_wiring` getattr idiom — no `harness_cp` → `harness_runtime` import).
- See `.harness/clearance/README.md` for marker discipline.
