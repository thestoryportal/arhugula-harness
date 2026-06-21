---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.68
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — change-note-level amendment marking B-HITL-WRAP-FAIL-CLASS-SURFACING BUILT + refreshing the §14.8 RT-FAIL-HITL-GATE-EDIT-DECODE row's surfacing clause: the wrap-time HITL terminal exceptions now surface their canonical RT-FAIL-HITL-* code via an rt_fail_class marker the CP driver reads, closing a prose-vs-code drift; additive, no new code/contract/hash)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-HITL-WRAP-FAIL-CLASS-SURFACING spine BUILT note)
  - design-substrate/Spec_Harness_Runtime_v1.md (v1.62 — the §14.8 RT-FAIL-HITL-GATE-EDIT-DECODE row whose "generic {type}" surfacing clause this arc refreshes to the precise marker surfacing; the §14.8 taxonomy codes PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — confirmed the bounded fork-first pick + the self-describing marker mechanism (import-free across the harness-cp ↔ harness-runtime axis boundary; the robust generalization of the pre-existing per-name canonicalization)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; <pending>)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.68`

v1.68 is a change-note-level additive amendment absorbing the **R-FS-1 standalone arc `B-HITL-WRAP-FAIL-CLASS-SURFACING`** (the Codex [P2] follow-on from B-EDIT-CARRIER #659). The wrap-time HITL gate's terminal exceptions now surface their canonical `RT-FAIL-HITL-*` code in the driver `fail_class` instead of the bare Python class name.

**The mechanism (the registered shared marker).** `harness-cp` cannot import the `harness-runtime` HITL exception TYPES (the axis dependency graph), so the CP driver surfaced caught wrap-time HITL exceptions via the generic `step-failure: {type(exc).__name__}: …` — e.g. `HITLGateRejectedError` instead of `RT-FAIL-HITL-GATE-REJECTED`. The fix: each of the 4 wrap-time HITL terminal exceptions (`HITLGateRejectedError` / `HITLGateEditDecodeError` / `HITLGateTimeoutError` / `HITLGateAuditComposeError`) carries an `rt_fail_class` class attribute naming its §14.8 code; the CP driver composes `fail_class` via a `_step_fail_class(prefix, exc)` helper reading `getattr(exc, "rt_fail_class", None) or type(exc).__name__` — import-free, applied at ALL per-topology step-dispatch failure sites (linear / EVALUATOR_OPTIMIZER / ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF). A non-marker exception falls back to the class name (byte-identical to pre-arc). `HITLCellExcludedError` is intentionally NOT marked (it has no §14.8 taxonomy code).

**NO operator gate / closes a prose-vs-code drift.** The §14.8 codes already exist and the exception docstrings already promised "Driver maps to RT-FAIL-X"; the driver merely now emits them. No new contract, no new fail-class, no new code, no §5.2-hash change. The §14.8 fail-class taxonomy + the wrap-time composer body are PRESERVED VERBATIM; only the EDIT-DECODE row's surfacing clause is refreshed (the v1.62 "generic `{type}`" description → the now-precise marker surfacing). CP spec UNCHANGED (the helper is CP-internal; reads the marker via `getattr`, no new CP contract, no cross-axis import).

Reviewed during clearance (verified by execution): the 4 HITL exceptions carry the correct `rt_fail_class` markers (harness-runtime test); `_step_fail_class` surfaces the marker code else the class name (harness-cp unit); a marker-carrying dispatch → `RunResult.fail_class` carries `RT-FAIL-HITL-GATE-REJECTED`, NOT `_MarkerError` (harness-cp integration); a non-marker exception falls back to the class name (negative control). pyright 0/0/0; harness-cp 1136 + harness-runtime non-e2e 2004 passed.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
