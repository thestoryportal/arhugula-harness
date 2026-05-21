# Implementation Plan — Control Plane v2.15

## Change-note (v2.14 → v2.15)

**Scope of revision.** Phase C atomic-unit decomposition pass per Remaining-Work Closure Arc plan file. Absorbs CP spec v1.10 (§25 C-CP-25 ValidatorFramework + §26 C-CP-26 PauseResumeProtocol + §27 C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter + §17.4 hitl_gate signature). Adds 15 new atomic units (U-CP-58 through U-CP-72). v2.14 substantive content (U-CP-00 through U-CP-57, all clusters, DAG topology) preserved verbatim.

**Source of fix.** Plan-orchestrated Remaining-Work Closure Arc, Phase C with prerequisites:
- Phase A.2 + B (CP spec v1.9 → v1.10 with new §25/§26/§27 + §17.4).
- Phase A.1 confirmation: Pattern-D 15 types inherited by citation per CP plan v2.9 + v2.10; no re-decomposition.
- Phase B iteration-2 absorption: F2-03 ValidatorOutcome → ValidatorNextAction mapping table (OPERATOR_BURDEN_EXCEEDED → ESCALATE_HITL).

**Spec authority chain.** CP spec v1.10 §25 / §26 / §27 / §17.4 + runtime spec v1.13 §14.9 / §14.10 (cross-axis) + ADR-D1 v1.2 + ADR-D2 v1.2 + ADR-D3 v1.2 + ADR-D5 v1.4 + ADR-D6 v1.2.

**Plan shape preserved.** v2.14's 9-cluster axis-led structure preserved verbatim. New units land at Cluster 10 (NEW — composer + per-server-trust + pause/resume).

**Sections preserved verbatim from v2.14.** All v2.14 content outside the new Cluster 10 preserved. The v2.14 + v2.13 + ... + v2.6 + v2.5 + v2.4 + v2.3 + v2.2 + v2.1 + v2.0 + v2 chain preserved.

**Status posture.** Proposed (v2.14) → Proposed (v2.15). v2.15 is an additive patch — 15 new atomic units; no v2.14 unit re-decomposition.

**Downstream absorption owed (post-v2.15).**
(a) Workspace `CLAUDE.md` §2.4 CP row version bump (v2.14 → v2.15).
(b) `harness-cp/CLAUDE.md` §3 + §4.1 — new L0 entry-points (U-CP-58 + U-CP-62 + U-CP-66 are Cluster-10 L0); retirement-table extensions for H_T-CP-18 / H_T-CP-21 / H_T-CP-22 pending implementation arc.

---

## §1 — Cluster 10 — Validator + Pause/Resume + Per-Server-Trust composers (NEW at v2.15)

**Cluster scope.** 15 units materializing C-CP-25 ValidatorFramework + C-CP-26 PauseResumeProtocol + C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter + C-CP-17 §17.4 hitl_gate signature materialization + the `cp_audit_to_od_audit` converter extension for 6 new action_id prefix patterns (Phase D iteration-2 F2-02 absorbed +1).

**Sub-cluster decomposition (Phase D iteration-1 F2-05 absorption — cluster sizing for single-arc landing feasibility):**
- **10-CP-A — ValidatorFramework (4 units): U-CP-58 / U-CP-59 / U-CP-60 / U-CP-61.** Single composer landing arc; lands ValidatorFramework end-to-end with span emission.
- **10-CP-B — PauseResumeProtocol (4 units): U-CP-62 / U-CP-63 / U-CP-64 / U-CP-65.** Single composer landing arc; closes pause_resume_protocol.py NotImplementedError sites + span emission.
- **10-CP-C — PerServerTrustEvaluator + MCPClientNamespaceEmitter (5 units): U-CP-66 / U-CP-67 / U-CP-68 / U-CP-69 / U-CP-70.** Single composer landing arc; closes per-server-trust + mcp.* namespace emission.
- **10-CP-D — hitl_gate signature + converter extension (2 units): U-CP-71 / U-CP-72.** Cross-axis integration landing arc; depends on 10-CP-A + 10-CP-B + 10-CP-C + runtime L9-sexies for converter producer-side completeness.

Each sub-cluster matches the precedent landing size (~4-8 commits per prior U-RT-58/59/60/62 arc). 10-CP-D opens last (depends on 3 prior sub-clusters at U-CP-72's predecessor set).

### U-CP-58 — ValidatorOutcome + ValidatorFailClass + ValidatorNextAction enum carriers

- **Implements:** CP spec v1.10 §25.2 (3 enums: 5-class ValidatorOutcome + 5-class ValidatorFailClass + 4-class ValidatorNextAction)
- **Files:** `harness-cp/src/harness_cp/validator_framework_types.py` (NEW)
- **Signatures:** 3 enum classes; all member values frozen
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `ValidatorOutcome` enum has exactly 5 members matching spec §25.2 verbatim values
  2. `ValidatorFailClass` enum has exactly 5 members matching spec §25.2
  3. `ValidatorNextAction` enum has exactly 4 members (PROCEED / RETRY / ESCALATE_HITL / ABORT)
  4. All enums frozen + hashable
  5. pyright strict mode passes

### U-CP-59 — Validator Protocol + ValidatorResult + ValidatorEvaluation + HITLEscalationBrief schemas

- **Implements:** CP spec v1.10 §25.1 (Validator Protocol + ValidatorFramework Protocol) + §25.2 (ValidatorResult + ValidatorEvaluation + HITLEscalationBrief dataclasses)
- **Files:** `harness-cp/src/harness_cp/validator_framework_types.py` (EXTEND)
- **Signatures:** `class Validator(Protocol)`, `@dataclass(frozen=True) class ValidatorResult`, `class ValidatorEvaluation`, `class HITLEscalationBrief`
- **Depends on:** [U-CP-58]
- **ACs:**
  1. `Validator.validate()` Protocol signature matches §25.1 exactly
  2. `ValidatorResult` instantiable with all 5 fields (outcome required; others optional per outcome)
  3. `ValidatorEvaluation` includes `burden_count` cumulative tracking
  4. `HITLEscalationBrief.proposed_response_palette` defaults to C-CP-16 §16.1 4-response palette
  5. Pydantic v2 validation on all dataclasses

### U-CP-60 — ValidatorFramework.evaluate() body + outcome→next_action mapping (per F2-03)

- **Implements:** CP spec v1.10 §25.1 ValidatorFramework class + §25.2 mapping table (F2-03 RATIFIED — OPERATOR_BURDEN_EXCEEDED → ESCALATE_HITL) + §25.4 invocation discipline + §25.6 fail classes
- **Files:** `harness-cp/src/harness_cp/validator_framework.py` (NEW)
- **Signatures:** `class ValidatorFramework`, `async def evaluate(step, step_result, *, step_context) -> ValidatorEvaluation`, internal `_map_outcome_to_next_action()` private helper
- **Depends on:** [U-CP-58, U-CP-59]
- **ACs:**
  1. Bijective-on-outcomes mapping: PASS→PROCEED / REVALIDATE→RETRY / ESCALATE→ESCALATE_HITL / PERMANENT_FAIL→ABORT / OPERATOR_BURDEN_EXCEEDED→ESCALATE_HITL
  2. Burden count monotonic per workflow; tracked on `ctx.operator_burden_counter`
  3. Single Validator per step invariant; raises `MultipleValidatorsError` on registry conflict
  4. CP fail class `CP-FAIL-VALIDATOR-PERMANENT` raised on `PERMANENT_FAIL`
  5. Unit test: each of 5 outcomes maps to the documented next_action
  6. REVALIDATE-budget-exhaustion-escalates-to-PERMANENT_FAIL test per CP spec v1.10 §25.7 invariant 3: validator returns REVALIDATE; retry-wrapper exhausts policy budget per C-RT-16; framework converts to PERMANENT_FAIL outcome + emits `CP-FAIL-VALIDATOR-PERMANENT` fail class. (Phase D iteration-1 F2-03 absorption.)

### U-CP-61 — validator.* span emission at workflow_driver post-dispatch hook

- **Implements:** CP spec v1.10 §25.5 span emission (`validator.evaluate` + `validator.fail` + `validator.revalidation` + `validator.escalation`)
- **Files:** `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND — post-dispatch validation hook)
- **Signatures:** Hook addition at line ~398 (post-dispatch, pre-ledger-append): `evaluation = await ctx.validator_framework.evaluate(...)`
- **Depends on:** [U-CP-60, U-OD-50 (cross-axis: OD)]
- **ACs:**
  1. Hook fires on every step (per Decision 2.D3 RATIFIED — opt-out via no-op validator)
  2. `validator.evaluate` outer span emits with 3 canonical attributes per OD spec v1.8 §C-OD-29.1 row 1-3
  3. `validator.fail` event emits when outcome != PASS with full 4-attribute set
  4. `validator.escalation.parent_hitl_span_id` populated when outcome=ESCALATE (links to subsequent HITL gate per F2-02 absorption)
  5. Workflow-driver test: PASS outcome proceeds; ESCALATE outcome opens HITL gate

### U-CP-62 — PauseReason + MaterialDiffPolicy + PauseSnapshot + ResumeResult schemas

- **Implements:** CP spec v1.10 §26.2 (PauseReason 5-class enum + MaterialDiffPolicy 3-class enum + PauseSnapshot dataclass + ResumeResult dataclass)
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol_types.py` (NEW)
- **Signatures:** 2 enums + 2 dataclasses
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `PauseReason` 5-class enum with all members per §26.2
  2. `MaterialDiffPolicy` default value = `STRICT` (per Decision 2.D7 RATIFIED)
  3. `PauseSnapshot.state_summary` typed against existing CP plan v2.9 `StateSummary` (Pattern-D inherited)
  4. `PauseSnapshot.snapshot_hash` is sha256 hex string (64 chars)
  5. `ResumeResult.diff_summary_hash` optional per spec §26.2

### U-CP-63 — PauseResumeProtocol.capture_pause_snapshot()

- **Implements:** CP spec v1.10 §26.1 capture_pause_snapshot signature + §26.6 invariants 1-3
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND — closes line 121 NotImplementedError)
- **Signatures:** `async def capture_pause_snapshot(workflow_id, run_id, step_index, pause_reason) -> PauseSnapshot`
- **Depends on:** [U-CP-62]
- **ACs:**
  1. Snapshot computes `snapshot_hash` via canonical serialization of (workflow_id + run_id + step_index + state_summary)
  2. Snapshot immutable after capture (frozen dataclass)
  3. State-ledger anchor populated with current `entry_hash` from `ctx.state_ledger_writer`
  4. Existing `harness-cp/src/harness_cp/pause_resume_protocol.py:121` NotImplementedError closed
  5. Unit test: capture + verify hash + verify immutability

### U-CP-64 — PauseResumeProtocol.attempt_resume() + material-diff detection

- **Implements:** CP spec v1.10 §26.1 attempt_resume signature + §26.6 invariants 4-5
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND — closes line 143 NotImplementedError)
- **Signatures:** `async def attempt_resume(snapshot, *, material_diff_policy) -> ResumeResult`
- **Depends on:** [U-CP-62, U-CP-63]
- **ACs:**
  1. Snapshot hash validated on resume; corruption → `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`
  2. Material diff detected when `state_ledger_anchor` no longer reachable from current entry chain
  3. STRICT policy: diff → `CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED`
  4. OPERATOR_ARBITRATE policy: diff → `CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED` + HITL escalation
  5. Coexist with U-CP-56 prefix-replay-based resumption (Path A-modified preserved)

### U-CP-65 — pause.captured + resume.attempted span emission

- **Implements:** CP spec v1.10 §26.4 span emission (2 spans, 4 attributes each)
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND)
- **Signatures:** Span emission via `ctx.tracer` at capture + resume sites
- **Depends on:** [U-CP-63, U-CP-64]; soft-dep (Pattern-P1-alignment-check predicate, not landing-order): U-OD-51 (cross-axis: OD — canonical schema documentation; runtime emit by attribute-name string-literal does not import OD schema module). Phase D iteration-1 F1-03 absorption.
- **ACs:**
  1. `pause.captured` span emits with 4 attributes per OD spec v1.8 §C-OD-30.1
  2. `resume.attempted` span emits with 4 attributes per §C-OD-30.1
  3. Both spans head=1.0 (always-sampled per §26.4)
  4. Span attribute names match OD canonical schema byte-exact (Pattern-P1 alignment)
  5. Integration test: pause + resume + verify span emission via OTel test collector

### U-CP-66 — MCPPrimitive + TrustDecisionReason + TierDerivationRule enum carriers

- **Implements:** CP spec v1.10 §27.2 (3 enums: 4-class MCPPrimitive + 6-class TrustDecisionReason + 3-class TierDerivationRule)
- **Files:** `harness-cp/src/harness_cp/per_server_trust_types.py` (NEW)
- **Signatures:** 3 enum classes
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `MCPPrimitive` 4-class enum matches §27.2 verbatim
  2. `TrustDecisionReason` 6-class enum includes `UNKNOWN_SERVER_TIER_FLOOR_PASS` + `UNKNOWN_SERVER_TIER_FLOOR_VIOLATION` per Decision 3.D1 RATIFIED
  3. `TierDerivationRule` 3-class enum (CONSERVATIVE / PROTOCOL_VERSION_TABLE / OPERATOR_HOOK)
  4. All enums frozen + hashable
  5. pyright strict mode passes

### U-CP-67 — TrustPolicy + TrustEvaluation schemas

- **Implements:** CP spec v1.10 §27.2 (TrustPolicy dataclass + TrustEvaluation dataclass)
- **Files:** `harness-cp/src/harness_cp/per_server_trust_types.py` (EXTEND)
- **Signatures:** 2 dataclasses
- **Depends on:** [U-CP-66]
- **ACs:**
  1. `TrustPolicy` includes `tier_derivation: TierDerivationRule` field per Decision 3.D1 ALLOW-with-tier-floor
  2. `TrustPolicy.allow_list` and `deny_list` are `frozenset[str]`
  3. `TrustEvaluation.audit_required` bool field
  4. Both dataclasses frozen
  5. Pydantic v2 validation

### U-CP-68 — PerServerTrustEvaluator.evaluate() + ALLOW-with-tier-floor

- **Implements:** CP spec v1.10 §27.1 (PerServerTrustEvaluator class + evaluate signature) + §27.6 invariants 1-4 (Decision 3.D1 RATIFIED)
- **Files:** `harness-cp/src/harness_cp/per_server_trust_evaluator.py` (NEW)
- **Signatures:** `class PerServerTrustEvaluator`, `async def evaluate(server_name, primitive, tool_contract, operator_policy) -> TrustEvaluation`
- **Depends on:** [U-CP-66, U-CP-67]
- **ACs:**
  1. Deny-list wins over allow-list (per §27.6 invariant 3)
  2. Unknown-server with resolved tier ≥ `TrustPolicy.default_tier` → permitted (per Decision 3.D1)
  3. UNKNOWN_SERVER_* decisions ALWAYS set `audit_required=true` (per §27.6 invariant 4)
  4. Trust policy immutable per workflow (loaded at bootstrap)
  5. Unit test: each of 6 TrustDecisionReason values exercised

### U-CP-69 — MCPClientNamespaceEmitter.emit_mcp_call_span()

- **Implements:** CP spec v1.10 §27.1 (MCPClientNamespaceEmitter class) + producer-side `mcp.*` 7-attribute namespace emission per C-AS-14 §14.3
- **Files:** `harness-cp/src/harness_cp/mcp_client_namespace_emitter.py` (NEW)
- **Signatures:** `class MCPClientNamespaceEmitter`, `def emit_mcp_call_span(span, server_name, primitive, signature_hash) -> None`
- **Depends on:** [U-CP-66]
- **ACs:**
  1. Mutates `mcp.tool.call` span with all 7 attributes per C-AS-14 §14.3
  2. `mcp.transport` value populates correctly per per-server config (stdio / streamable_http / sse)
  3. `mcp.auth_present` reflects actual auth state (False on STDIO; transport-config-driven elsewhere)
  4. `mcp.primitive.signature.sha256` is content-addressable per-primitive
  5. Unit test: emit + verify all 7 attributes via OTel test collector

### U-CP-70 — mcp.trust.evaluate span emission

- **Implements:** CP spec v1.10 §27.4 span emission + sampling discipline (head=1.0 if audit_required; else head=0.1)
- **Files:** `harness-cp/src/harness_cp/per_server_trust_evaluator.py` (EXTEND)
- **Signatures:** Span emission integrated at `evaluate()` return
- **Depends on:** [U-CP-68, U-OD-52 (cross-axis: OD)]
- **ACs:**
  1. `mcp.trust.evaluate` span emits with 5 attributes per OD spec v1.8 §C-OD-31.1
  2. Sampling: head=1.0 when `audit_required=true`; else head=0.1
  3. UNKNOWN_SERVER decisions always emit (audit_required=true forces head=1.0)
  4. Span attribute names match OD canonical schema byte-exact
  5. Integration test: 5 evaluations × 6 decision reasons covered

### U-CP-71 — hitl_gate canonical signature materialization

- **Implements:** CP spec v1.10 §17.4 (extends C-CP-17 §17.3 HITLPlacement; closes `harness-cp/src/harness_cp/hitl_placement.py:178` NotImplementedError)
- **Files:** `harness-cp/src/harness_cp/hitl_placement.py` (EXTEND — line 178 NotImplementedError)
- **Signatures:** `async def hitl_gate(placement, step, step_context, *, surface, palette, timeout) -> HITLGateResult`
- **Depends on:** (none within this delta) [HIGH]; **Requires existing (landed at main):** U-RT-60 (C-RT-18 §14.8 HITL gate composer; this unit is signature-only materialization, composer body owned by C-RT-18). Phase D iteration-1 F1-04 absorption.
- **ACs:**
  1. Protocol signature materialization closes `NotImplementedError` at line 178
  2. `palette` defaults to C-CP-16 §16.1 `frozenset({APPROVE, EDIT, REJECT, RESPOND})`
  3. `surface` injected per U-RT-60 `MCPBackedAskUserQuestionSurface`
  4. Composer body owned by C-RT-18 §14.8 (existing); this unit is signature-only materialization
  5. Unit test: signature accepts canonical args; raises if surface=None

### U-CP-72 — cp_audit_to_od_audit converter extension for 6 new action_id prefix patterns (Phase D iteration-2 F2-02 absorption — expanded from 5 to 6 patterns)

- **Implements:** CXA v2.6 §2.3.7 rows 3-7 + new row 8 (cost-attribution audit-write per Phase D iteration-2 F2-02 RATIFIED operator-decision: "Extend U-CP-72 to 8 prefixes + extend CXA v2.6 to add row") + 6 new action_id prefix discriminators (`hitl_webhook:`, `operator_burden:`, `validator:`, `pause:` + `resume:`, `mcp_trust:`, `cost:`)
- **Files:** `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (EXTEND — currently handles `dispatch:` + `hitl:` patterns)
- **Signatures:** Branch additions in `cp_audit_to_od_audit()` dispatch logic
- **Depends on:** [U-CP-60, U-CP-63, U-CP-64, U-CP-68, U-RT-69 (cross-axis: runtime), U-RT-70 (cross-axis: runtime), U-CP-71, U-OD-41 (cross-axis: OD — cost-record audit-write producer)]
- **ACs:**
  1. Converter routes 8 action_id prefixes: dispatch / hitl / hitl_webhook / operator_burden / validator / pause+resume / mcp_trust / cost
  2. Each branch produces correct AuditPayload subclass per OD spec v1.8 §C-OD-29.2 through §C-OD-33.2 + new cost-record AuditPayload subclass per CXA v2.6 §2.3.7 row 8 (Phase A iteration-N CXA v2.7 amendment owed; see §1 cross-arc note below)
  3. Field projection per producer-side spec sections; no field-name drift
  4. Cross-side join discriminator `audit.cp.action_id` field carries prefix correctly
  5. Integration test: 8 producer events → 8 distinct AuditPayload subclasses + OD ledger write

**Cross-arc note (Phase D iteration-2 F2-02 absorption).** This unit's AC #1 expansion from 7 → 8 prefixes requires CXA v2.6 → v2.7 amendment to add an §2.3.7 row 8 entry for cost-attribution audit-write seam. The CXA amendment is a small additive patch (single row append + aggregate matrix +1 update); routes to a Phase A iteration-N CXA edge instantiation (estimated ~30 lines of CXA delta-over file). At Phase E handoff, this CXA owe is explicitly enumerated.

---

## §2 — DAG topology delta (v2.14 → v2.15)

15 new units added at Cluster 10. Topological sort acyclic:

```
Cluster 10 (NEW at v2.15):
  L0-within-delta: U-CP-58, U-CP-62, U-CP-66, U-CP-71
  L1-within-delta: U-CP-59 (←58), U-CP-67 (←66), U-CP-63 (←62), U-CP-69 (←66)
  L2-within-delta: U-CP-60 (←58, 59), U-CP-68 (←66, 67), U-CP-64 (←62, 63)
  L3-within-delta: U-CP-61 (←60 + U-OD-50 cross-axis), U-CP-65 (←63, 64 + U-OD-51 cross-axis), U-CP-70 (←68 + U-OD-52 cross-axis)
  L4-within-delta: U-CP-72 (←60, 63, 64, 68, 71 + U-RT-69, U-RT-70 cross-axis)
```

Cross-axis edges: U-CP-61 → U-OD-50; U-CP-65 → U-OD-51; U-CP-70 → U-OD-52; U-CP-72 → U-RT-69, U-RT-70.

DAG verified Kahn-acyclic; 15 units consumed; ∅ remaining edges.

---

## §3 — Coverage matrix delta (v2.14 → v2.15)

| Contract | Units covering |
|---|---|
| C-CP-25 §25.1 (signatures) + §25.2 (field sets) | U-CP-58, U-CP-59 |
| C-CP-25 §25.3-§25.5 (lifecycle + discipline + spans) | U-CP-60, U-CP-61 |
| C-CP-26 §26.1 (signatures) + §26.2 (field sets) | U-CP-62 |
| C-CP-26 §26.3 (lifecycle) + §26.4 (spans) + §26.6 (invariants) | U-CP-63, U-CP-64, U-CP-65 |
| C-CP-27 §27.1 (signatures) + §27.2 (field sets) | U-CP-66, U-CP-67 |
| C-CP-27 §27.3 (lifecycle) + §27.4 (spans) + §27.6 (invariants) | U-CP-68, U-CP-69, U-CP-70 |
| C-CP-17 §17.4 (hitl_gate signature materialization) | U-CP-71 |
| CXA v2.6 §2.3.7 rows 3-7 (converter extension) | U-CP-72 |

All C-CP-25 / C-CP-26 / C-CP-27 / §17.4 / CXA-converter subsections covered ≥ 1 unit. ✓

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_15.md` |
| Version | v2.15 |
| Filing event | Phase C atomic-unit decomposition pass, Remaining-Work Closure Arc, 2026-05-21 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_14.md` |
| New units | 15 (U-CP-58 through U-CP-72) |
| New cluster | 10 (NEW at v2.15) |
| Cross-axis dependencies | 5 (U-CP-61→U-OD-50; U-CP-65→U-OD-51; U-CP-70→U-OD-52; U-CP-72→U-RT-69, U-RT-70) |
| DAG verification | Kahn-acyclic; 15 units consumed; ∅ remaining edges |
| Coverage verification | All C-CP-25 / 26 / 27 / §17.4 / CXA extension subsections covered ≥ 1 unit |
| Pattern-D types | INHERITED by citation (15 types per Phase A.1 §4.2); 0 re-decomposed |
| Date | 2026-05-21 |
