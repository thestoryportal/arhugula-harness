# Class 1 tension — `emit_override_audit_entry` audit-half consumer-chain absence

*Filed 2026-05-29 post-checkpoint item 6 audit-stub remediation arc opening. **Status: PROPOSING.** Closes PR #66 Q2=iii "audit-half stub IN-SCOPE-BUT-MARK-DEFERRED" framing as empirically wrong shape: bounded-scope stub remediation forecloses on substrate-consumer-asymmetry that requires Reading D bounded-defer per sub-species 7d catalogue at `.harness/retirement-event-pattern-catalogue-batch-45-addendum.md` §2.1.*

---

## §1 Defect

`emit_override_audit_entry` at `harness-cp/src/harness_cp/per_step_override_evaluator.py:208-231` is the override-application audit-ledger composer per CP spec v1.27 C-CP-06 §6.2 + C-CP-16 §16.2. Current body discards `override` + `actor` inputs (`_ = (override, actor)` at line 224) and hardcodes 4 fields:

```python
return CPAuditLedgerEntry(
    action_id=ActionID(f"{workflow_id}||{step_id}"),
    gate_level=GateLevel.AUTO,           # hardcoded
    response="approve",                   # hardcoded
    timestamp="",                         # hardcoded sentinel
    prior_event_hash="0" * 64,            # hardcoded sentinel
)
```

PR #66 (squash `6786a59`) Q2=iii deferred functional remediation per the "bounded-scope" framing at CP spec v1.27 §16.5.6 annotation: "audit-stub IN-SCOPE-BUT-MARK-DEFERRED — annotate `emit_override_audit_entry` stub functional gap at §16.5.6 + per-axis CLAUDE.md + plan body".

## §2 Empirical orientation — 3-grep discriminator

Per sub-species 7d catalogue 3-grep discriminator (`.harness/retirement-event-pattern-catalogue-batch-45-addendum.md` §2.1):

### §2.1 grep 1 — CPAuditLedgerEntry consumers

```
harness-cxa/src/harness_cxa/cp_audit_conversion.py:177  def cp_audit_to_od_audit(...)
```

**Result:** The `cp_audit_to_od_audit` converter exists at production. Substrate IS LANDED at the conversion layer.

### §2.2 grep 2 — production `cp_audit_to_od_audit` invocation sites

```
harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:783          od_entry = cp_audit_to_od_audit(...)
harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:489          od_entry = cp_audit_to_od_audit(...)
harness-runtime/src/harness_runtime/lifecycle/cost_attribution_llm_dispatch.py:237   audit_entry = cp_audit_to_od_audit(...)
harness-runtime/src/harness_runtime/lifecycle/cost_attribution_tool_dispatch.py:297  audit_entry = cp_audit_to_od_audit(...)
harness-runtime/src/harness_runtime/lifecycle/cost_attribution_validator_dispatch.py:224  audit_entry = cp_audit_to_od_audit(...)
harness-runtime/src/harness_runtime/lifecycle/cost_attribution_webhook_dispatch.py:191    audit_entry = cp_audit_to_od_audit(...)
```

**Result:** 4 distinct production paths invoke `cp_audit_to_od_audit` — HITL gate composer, sub-agent dispatch, 4× cost-attribution dispatches. **NONE of them trace back to `emit_override_audit_entry`**. The override audit entry is not converted to an OD-side audit-ledger entry at any production site.

### §2.3 grep 3 — `override_audit_ref` semantic consumers

```
harness-cp/src/harness_cp/per_step_override_evaluator.py:142    override_audit_ref: LedgerEntryRef | None = None  (field declaration)
harness-cp/src/harness_cp/per_step_override_evaluator.py:184    override_audit_ref=None                          (no-override branch)
harness-cp/src/harness_cp/per_step_override_evaluator.py:199    override_audit_ref=LedgerEntryRef(...)           (populated branch)
harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:94    override_audit_ref: LedgerEntryRef | None       (descent-binding field)
harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:134   override_audit_ref=None                          (descent-time set None)
```

**Result:** `override_audit_ref` is populated at `StepEffectiveBinding` per line 199 — and **never read at any production site for any semantic action** (persistence / signing / conversion / cross-reference resolution). The field is structurally instantiated and dropped.

### §2.4 Discriminator verdict

Case (B) per advisor 50th application: **substrate LANDED at the composer layer + converter layer; ZERO production consumer-loop connecting `emit_override_audit_entry` output → `cp_audit_to_od_audit` → audit-writer chain.** Sub-species 7d shape — **substrate-consumer asymmetry at retirement gates**, NOT binding-chain ordering defect, NOT bounded composer-conformance fix.

## §3 Why Reading D applies

Per sub-species 7d catalogue at `.harness/retirement-event-pattern-catalogue-batch-45-addendum.md` §2.1:

> Closure shape = **bounded-defer Reading D** per X-AL-2 bounded-residual carry-forward, with explicit §"why-Reading-D-applies" naming the missing upstream consumer-loop.

The missing consumer-loop for `emit_override_audit_entry`:

1. **No persistence path** — `audit_entry` returned at `resolve_step_binding:187` is consumed structurally (`action_id` + `prior_event_hash` extracted to populate `override_audit_ref` at line 199-203) but NEVER passed to any writer (no `audit_writer.append(...)` or equivalent invocation).
2. **No signing path** — `f5_signing_key_resolution.py:sign_audit_entry` exists; ZERO calls from override flow. The `CPSignedAuditLedgerEntry` shape per CP spec v1.27 §20.4 is never produced for override entries at production.
3. **No conversion path** — `cp_audit_to_od_audit` converter exists; 4 production invocation sites do NOT trigger from override flow. The OD-side audit-ledger never receives an override-application entry.
4. **No `override_audit_ref` reader** — the populated field at `StepEffectiveBinding` is never dereferenced for downstream audit-trail correlation, signed-bytes reconstruction, or hash-chain verification.

Remediating field hardcoding (`gate_level=AUTO` / `timestamp=""` / `prior_event_hash="0"*64`) produces a richer `CPAuditLedgerEntry` that still has no destination. The richness is invisible at production. This is silent X-AL-3 absorption per Meta-Architecture §7.7 — composer substrate emitting into a void with documentation claiming a populated audit record.

## §4 Readings

| Reading | Shape | Disposition |
|---|---|---|
| **A** Stub remediation (PR #66 Q2=iii original) | Compose richer fields (clock-derived timestamp; gate_level from override.hitl_placement; prior_event_hash threaded from caller) | **FORECLOSED** — wires substrate to no consumer; silent X-AL-3 absorption per §3 |
| **B** Author full consumer-loop (persistence + signing + conversion + ref reader) | Open arc spanning workflow_driver + audit_writer wiring + override-prefix branch at cp_audit_to_od_audit + override_audit_ref dereferencer | NOT-IN-SCOPE — would be a full Phase 7 cluster arc beyond a single Q2=iii deferral closure; requires new spec contract for override-audit lifecycle distinct from HITL/sub-agent/cost-attribution chains |
| **D** Bounded-defer per X-AL-2 (Recommended) | Acknowledge audit-half as sub-species 7d substrate-pending-upstream-loop; close PR #66 Q2=iii framing; remediation deferred until consumer arc opens | **RECOMMENDED** |

## §5 Cross-axis cascade

ZERO cascade. Intra-CP-axis audit-half deferral. No IS / AS / OD / runtime spec / CXA amendment owed. CP spec v1.27 §16.5.6 v1.27 annotation PRESERVED VERBATIM (annotation correctly described the structural gap; this fork doc names the gap as sub-species 7d not "bounded-scope").

## §6 Q-set for ratification

| Q | Question | Recommended |
|---|---|---|
| Q1 | Reading | **D** bounded-defer |
| Q2 | PR #66 Q2=iii framing | Close as **empirically wrong (case-B sub-species 7d)**; ratification at PR #66 stands but Q2=iii closure path reroutes |
| Q3 | Spec amendment owed | **None** — §16.5.6 v1.27 annotation accurately documents the structural gap |
| Q4 | Plan amendment owed | **None** — U-CP-14 unit body has no AC about audit-half functional closure |
| Q5 | Filing posture | **(ii) file-only this session** (mirror PRs #65/#68/#69); ratification + closure deferred to fresh session per token-budget guidance |
| Q6 | Cross-axis cascade | **NONE** verified at §5 |

## §7 Catalogue updates owed

**5th instance of sub-species 7d** (`LANDED-substrate-pending-upstream-loop-substrate`). Per `.harness/retirement-event-pattern-catalogue-batch-45-addendum.md` §2.1 "Routing for future instances: at 5th instance, consider consolidating retirement-event-pattern catalogue at a dedicated `.harness/retirement-event-pattern-catalogue.md` and locking sub-species numbering."

This filing crosses the 5th-instance threshold. Consolidation arc owed at a future session — not at this filing (FM-2 narrow scope). 5-instance cardinality refresh table:

| # | Fork doc | Substrate LANDED at | Missing upstream consumer-loop | PR |
|---|---|---|---|---|
| 1 | HITL `rewrite_tool_call` | `hitl_placement.py:187` | LLM inner tool-call interception loop | #67 |
| 2 | Sibling-ledger U-CP-34 | LANDED composer | Recursive-harness recursion boundary | #67 |
| 3 | U-CP-49 engine-layer | `pause_resume_protocol.py:106,128` stubs | Engine-layer recovery loop | #69+#70 |
| 4 | Bootstrap-emission | U-CP-75 + U-RT-110 LANDED | Per-step `engine_selector.select(...)` query site | #68+#71 |
| 5 | **`emit_override_audit_entry`** | Composer + `cp_audit_to_od_audit` converter LANDED | Override-audit persistence / signing / conversion / ref-reader chain | **this fork** |

50th [[advisor-before-substantive-work-for-cross-axis-blockers]] application this arc — caught case (B) discriminator BEFORE the impl arc opened. Cardinality 5-of-5 instances surfaced by pre-substantive empirical orientation; the catalogue + 3-grep discriminator from PR #72 §2.1 directly enabled this finding.

## §8 Test plan

- [x] X-AL-3 CI guard: PASS expected (`.harness/` only; no `design-substrate/` edits at filing)
- [x] Empirical orientation grounded: 3-grep discriminator output enumerated at §2.1-§2.3
- [x] 50th advisor application catalogued; case (A) vs case (B) reading discriminated pre-substantive
- [x] Sub-species 7d catalogue at PR #72 §2.1 cardinality threshold (5 instances) documented at §7
- [x] PR #66 Q2=iii framing closure path documented at §4 (Reading A FORECLOSED) + Q2 (§6)

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_tension_emit_override_audit_entry_consumer_chain_absence.md` |
| Filing | Class 1 tension; **Status: PROPOSING** |
| Trigger | Checkpoint item 6 audit-stub remediation arc opening 2026-05-29; 3-grep discriminator at empirical orientation surfaced case (B) sub-species 7d |
| Authority anchor | Sub-species 7d catalogue at `.harness/retirement-event-pattern-catalogue-batch-45-addendum.md` §2.1; CP spec v1.27 §16.5.6 v1.27 annotation; PR #66 Q2=iii deferral framing |
| Operator decision needed | Q1 Reading D ratification; Q2 PR #66 Q2=iii closure path; Q5 filing posture |
| Effects | ZERO production code change; ZERO design-substrate edit; ZERO clearance marker; ZERO retirement-event tier transit. Pure `.harness/` fork-doc filing under CLAUDE.md §11 design-phase posture |
| H_T-RT-35 transit posture | UNCHANGED at RETIRE-READY |
| H_T-CP-14 transit posture | UNCHANGED (Q2=iii closure path reroutes but no tier transit owed) |
| Sub-species 7d instance count | 4 (pre-filing) → **5** (post-filing); consolidation arc threshold met |
