---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.62
cleared_at: 2026-06-19T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — the deferred NOTE 6-ii decode-semantics fill; mutation discipline (A) JSON-decode-then-replace PRESERVES the committed replace-not-merge mandate; probe-resolved fork, FULL-SPEC pre-authorized)
back_reference:
  - .harness/class_1_fork_hitl_edit_carrier_drift_str_vs_mapping.md (RESOLVED by this arc)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-EDIT-CARRIER spine BUILT note)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — pre-substantive: foreclosed the mutation-discipline "fork" to (A) via the discriminator "preserves vs overrides replace-not-merge" → mine-to-build, no operator gate; designed the full-chain witness obligation (real str → Mapping → dispatched step_payload, no Mapping-returning mock); flagged the flip-don't-delete interim-raise test + the ledger (d)/(e) items (taxonomy + post-mutation hash)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed — nothing committed is sacrificed, the deferred decode semantics are filled)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.62`

v1.62 is a targeted amendment delta over v1.61 absorbing the **R-FS-1 standalone arc `B-EDIT-CARRIER`**. It lands **functional operator EDIT** at the wrap-time HITL gate (§14.8.2 step 4i), RESOLVING the U-RT-120 / B3-impl-3 carrier-drift fork (`.harness/class_1_fork_hitl_edit_carrier_drift_str_vs_mapping.md`, D-edit.B interim raise). `EDIT` is a spec-mandated 4-response-palette member that shipped **non-functional** (raised `HITLGateEditCarrierDriftError`) until this arc; the just-landed #657 `B-HITL-PLACEMENT-PER-STEP-PRODUCER` producer made the EDIT gate reachable in production.

**The reconciliation.** §14.8.2 step 4i + NOTE 6-ii mandate replace-not-merge; the CP carrier is `Mapping[str, Any]` but the wired runtime ask-surface returns a flat `str` (MCP elicitation is flat-schema). v1.62 reconciles via **mutation discipline (A)**: JSON-decode the operator `str` → a `Mapping`, then replace `step.step_payload` verbatim. A non-object proposal raises the newly-registered `RT-FAIL-HITL-GATE-EDIT-DECODE` (retiring the interim `HITLGateEditCarrierDriftError`); the `edited_proposal_hash` becomes the **post-mutation** payload hash (closing reviewer F3-03).

**NO operator gate.** The fork enumerated three disciplines; the cleared constraints (flat-`str` carrier + committed replace-not-merge + arbitrary-nested target) foreclose to (A) — (B) cannot carry arbitrary nesting; (C) would override replace-not-merge. Because (A) **preserves** (does not sacrifice) the committed replace-not-merge decision, this is the deferred-decode-semantics fill, FULL-SPEC pre-authorized (probe-resolved; the fork's "operator ratification" framing predates the 2026-06-12 FULL-SPEC directive). Additive + opt-in: EDIT fires only when the operator selects it at a declared placement.

Reviewed during clearance: the discipline foreclosure (A over B/C); the full-chain witness proving the `str`→`Mapping`→dispatched-`step_payload` transit through the real composer with NO Mapping-returning mock (`[[full-chain-witness-not-half-proofs]]` / `[[test-bypass-as-runtime-truth-pattern]]`); the interim-raise test FLIPPED (not deleted) into the invalid-JSON negative control; the post-mutation `edited_proposal_hash` (asserted `== post_mutation_hash` AND `!= sha256(raw_str)`); the real-consumer witness (composer's inner = the REAL `RuntimeLLMDispatcher` over a recording provider → the decoded payload is what the provider actually received, not the original); the wrap-time-sync-only scope. The durable-async resume path currently dispatches the resumed step UNCHANGED for ALL response types (the v2.24 AC #7 MVP shape; resumed-response integration deferred per FM-2), so a durable-async EDIT is silently not-applied — a PRE-EXISTING documented limitation, registered as the follow-on `B-EDIT-CARRIER-DURABLE-ASYNC-RESUME`.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- See `.harness/clearance/README.md` for marker discipline.
