---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.66
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — change-note-level amendment extending the §14.23 C-RT-32 `EngineOutputStore` producer gate + resume-side rehydrate from `EVENT_SOURCED_REPLAY` to `{EVENT_SOURCED_REPLAY, WAL_SEGMENT}`, marking the §14.23.7 registered follow-on `B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT` BUILT; additive + opt-out-byte-identical)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT spine BUILT note)
  - design-substrate/Spec_Control_Plane_v1_47.md (the CP-side C-CP-08 §8.1 `segment_replay` cached-output capability clause; co-published in the same bundled-absorption PR)
  - design-substrate/Spec_Harness_Runtime_v1.md (v1.63 — the §14.23 C-RT-32 `EngineOutputStore` contract this arc extends; v1.63 §14.23.7 explicitly registered this follow-on; PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — confirmed the pick + the two-surface bundled-absorption framing (runtime §14.23.5 + CP §8.1); anchored the record↔rehydrate coupling correctness property (never record-only) + the full-chain witness requirement (record→resume→recovered-predecessor, not gate-membership); confirmed the resume_at composes (WAL_SEGMENT's is the same F2-prefix step-index; both key on run_idempotency_key)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; <pending>)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.66`

v1.66 is a change-note-level additive amendment absorbing the runtime half of the **R-FS-1 standalone arc `B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT`**. It extends the §14.23 C-RT-32 `EngineOutputStore` cached-output replay from `EVENT_SOURCED_REPLAY` to `WAL_SEGMENT`:

- **§14.23.5 invariants (amended):** the producer gate "GATED on `EVENT_SOURCED_REPLAY`" → "GATED on the cached-output-replay engine classes `{EVENT_SOURCED_REPLAY, WAL_SEGMENT}`" — both share the store + the C-CP-08 §8.1 refinement. RESERVE-before-COMMIT + opt-out-byte-identical PRESERVED.
- **§14.23.7 (registered follow-on LANDED):** `B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT` is BUILT; WAL_SEGMENT now rehydrates the durably-stored prefix into the inter-step channel on resume, fail-closing on a store↔ledger skew / body-change identity mismatch via the SAME `_rehydrate_inter_step_channel_on_replay` helper. The "non-linear resume-blind strategies" residual remains registered.

**§14.23 has no expanded body section** (the v1.63 change-note table rows ARE the contract), so v1.66 is a change-note amendment of the §14.23.5 producer-gate scope + the §14.23.7 follow-on status — no in-place body edit. The §14.23 C-RT-32 contract carrier (store schema, RESERVE-before-COMMIT, fail-close gates) is PRESERVED VERBATIM.

**NO operator gate.** Additive correctness; sacrifices no committed invariant; the opt-out default (`engine_output_replay=False`) is byte-identical, and the producer gate stays closed for non-replay engine classes (`SAVE_POINT_CHECKPOINT` / `PURE_PATTERN_NO_ENGINE` never write a never-rehydrated journal). No new field, no new contract, no §5.2-hash change. CP spec v1.47 co-amends C-CP-08 §8.1 (the capability declaration).

**The record↔rehydrate coupling is the correctness property (advisor).** The producer gate's purpose is "don't write a never-rehydrated journal." Extending the producer to WAL_SEGMENT is safe ONLY because the resume-side rehydrate ships for the SAME class in the same arc — never record-only. The full-chain witness (`test_wal_segment_records_then_rehydrates_full_chain`) drives a real WAL_SEGMENT run that records each output → a resume that rehydrates → the first re-dispatched segment-step reads its RECOVERED predecessor's output (not None), with a negative control (no store → None) + a store↔ledger fail-close.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp impl + tests land together (`merge_commit` pinned at the post-merge refresh).
