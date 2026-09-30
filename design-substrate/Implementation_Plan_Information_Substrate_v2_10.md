# Implementation Plan — Information Substrate (IS axis) — v2.10

*Delta over v2.9. This revision classifies the new model-tool HITL response F2 direct append introduced by PR #1616 under the existing C-IS-07 §7.6.1 per-call-site election rule. All v2.9 rows, U-IS-11 criteria #1–#20 (including #14-bis), other unit bodies, dependency edges, and coverage rows remain unchanged.*

**Status:** Cleared for the local source-contract candidate on 2026-09-29; PR CI, merge and installed acceptance remain pending.

---

## §0 Authority and scope

The cleared predecessor is `Implementation_Plan_Information_Substrate_v2_9.md` and its 2026-08-07 clearance marker. The current IS spec head v1.16 retains C-IS-07 §7.6.1: a direct append may elect writer-owned sampling only where its ledger timestamp means **when appended**; the default for every non-electing producer remains caller-supplied. The contract deliberately places the site roster in this plan. This successor adds one newly reachable site to that roster; it does not change the IS spec, the writer's sentinel behavior, the clock-skew tolerance, or the event-time RETAIN disposition of v2.9 row 14.

The new `RuntimeHITLToolResponseAuditor._record_sync` records a model-tool operator response before tool dispatch. Its F2 state-ledger entry anchors the CP-to-OD response audit and has the same append-time meaning as the workflow-step HITL F2 entry classified ELECT at v2.9 row 11. The CP audit entry's separate `timestamp` is sampled when the audit record is composed in the offload worker, after the operator reply; no precise operator-click instant is captured. Treating that sample as the F2 ledger's event time would misdescribe the value and reintroduce the sample-before-lock refusal that B-57 removed for eligible sites.

## §1 U-IS-11 per-site roster addition

The v2.9 §2.1 table's rows 1–14 are preserved as historical classifications. Add this row, grounded in the new production path at this successor's source candidate:

| # | Direct append site | Ledger timestamp meaning | Disposition |
|---|---|---|---|
| 15 | `harness-runtime/src/harness_runtime/lifecycle/hitl_tool_response_audit.py`, `RuntimeHITLToolResponseAuditor._record_sync` → `LedgerWriter.append(EntryPayload(...))` | When this F2 audit anchor is appended; the distinct CP audit timestamp is the audit-composition sample | **ELECT** by passing `WRITER_OWNED_TIMESTAMP` at this call site |

Current roster: **15 rows = 11 ordinary ELECT** (v2.9 rows 1–9 and 11, plus row 15) + **2 ELECT with their already resolved injection caveats** (rows 12–13) + **1 RETAIN** (row 14) + **1 DEFER** (row 10). The v2.9 counts remain true of that predecessor's 14-row snapshot. No writer-side mode or ambient default is introduced. The `as_is_wiring.py` event-time control stays caller-supplied, and the v2.9 §0.6 council trigger is not activated by this ELECT classification.

## §2 Acceptance and witnesses

**U-IS-11 AC #21 (new):** The model-tool HITL response F2 direct append at row 15 elects writer-owned timestamp sampling inside the existing write critical section. Its CP audit timestamp remains the independently sampled audit-composition value. A stale pre-append CP audit sample must neither become the F2 ledger timestamp nor cause a spurious non-monotonic refusal after an already newer ledger entry. The response audit still completes before any tool dispatch; an actual write failure propagates before dispatch. All v2.9 U-IS-11 criteria, including the negative default-preservation witness and exact per-site conformance check, continue to apply.

The load-bearing real-ledger witness is `test_tool_response_f2_uses_append_time_when_audit_clock_is_stale`: force only the CP audit composition clock one day behind, leave the ledger writer clock real, run an approved model tool call through the wired factory, and require dispatch plus an F2 timestamp later than that stale CP sample. With caller-supplied F2 sampling this test fails with `NonMonotonicTimestampError`; with the site election it passes. The roster test `test_sentinel_electing_sites_match_the_plan_v2_10_roster` must include exactly one sentinel stamp in this new module; it failed before the election and prevents a missed or drive-by conversion. The existing non-electing default, event-time RETAIN, and two-process contention witnesses remain required and unchanged.

## §3 Structural and delivery boundary

No new unit, DAG node or edge, auxiliary type, coverage-matrix row, writer API, IS outbound dependency, or CXA seam is introduced. The Runtime call site already consumes the IS ledger-write contract; classification changes the value passed at that existing seam. This is a plan-roster and implementation correction for PR #1616, not an installed-runtime proof. Independent plan/source review, complete local checks, PR CI, merge review and post-main CI remain separate gates.

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.10 (delta over v2.9) |
| Authority | IS spec v1.16 C-IS-07 §7.6.1; v2.9 U-IS-11 AC #17's newly appearing site rule; independent PR #1616 F1 HOLD disposition |
| Net delta | One classified ELECT row and U-IS-11 AC #21; all earlier rows/criteria and structural counts preserved |
| Source grounding | Direct read of the new `RuntimeHITLToolResponseAuditor._record_sync` production append and the sibling `hitl_gate_composer.py` HITL F2 append at this candidate |
| Clearance | Independent Opus plan/source GO and narrow delta GO recorded; v2.10 clearance marker filed in this PR, with no main or installed-readiness claim |
