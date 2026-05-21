# Specification — Control Plane v1.10

## Change-note (v1.9 → v1.10)

**Scope of revision.** Phase A.2 ratified-drafts apply pass per `.harness/Phase_A_2_Contract_Drafts_v1.md` (operator-ratified 2026-05-21 at this session's plan file Phase A.2 + ratification footer). Three new contracts added at §25 / §26 / §27 + one section extension at §17.4 (`hitl_gate` canonical signature materialization). 8 new CP fail-class rows added. All v1.9 content (including §13.5.1 NEW NOTE 4 + NOTE 5 + NOTE 6 from path-(i) absorption) preserved verbatim. No signature change to any v1.9 contract; no field-projection table change.

**Source of fix.** Plan-orchestrated Remaining-Work Closure Arc Phase A.2 with prerequisites:
- Phase A.0 (`.harness/Phase_A_0_LLM_Dispatch_Fork_Audit_v1.md`) — LLM-dispatch composer fork CLOSED as Option-A-taken at U-RT-52 + U-RT-58.
- Phase A.1 (`.harness/Phase_A_1_Tension_Resolution_v1.md`) — Pattern-D 13-type cluster + CP unit sequencing CONFIRMED-RESOLVED at CP plan v2.9 (T2 X-AL-3 FACTOR-OUT, 16 types) + v2.10 (R-2/W-2 RoleRoutingBinding + WorkloadRoutingOverride). **Pattern-D field sets inherited by citation; NOT re-authored.** See Phase A.1 §4.2 citation table.
- Class 2 C.1 (tool-invocation composer scope) — operator-ratified Path X.
- Class 2 C.2 (LLM-dispatch composer fork) — operator-ratified close-as-resolved.

**Pattern-D inheritance change-note.** v1.10 explicitly inherits Pattern-D structured-type field sets from CP plan v2.9 + v2.10 per Phase A.1 §4.2:

| Pattern-D type | Canonical authority (cite at every consumer) |
|---|---|
| `ProposedAction` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `ActionKind` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `ActionPayload` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `FailedAttempt` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `Alternative` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `RetryHistory` | CP plan v2.9 + CP spec v1.9 C-CP-03 §3.5 |
| `RetryPolicy` | CP plan v2.9 + CP spec v1.9 C-CP-03 §3.5 |
| `RoleRoutingBinding` | CP plan v2.10 + class_1_tension_role_routing_binding_underspec.md R-2 schema |
| `WorkloadRoutingOverride` | CP plan v2.10 + class_1_tension_role_routing_binding_underspec.md W-2 schema |
| `InferenceRequest` | Unified to `ProviderAgnosticPayload` at U-CP-00c (CP plan v2.8) |
| `AuditLedgerEntry` (OD form) | OD spec v1.7 §24 (canonical) |
| `CPAuditLedgerEntry` (CP form) | CP plan v2.9 + CP spec v1.9 C-CP-16 §16.2 |
| `CPSignedAuditLedgerEntry` (CP form) | CP plan v2.9 + CP spec v1.9 C-CP-20 §20.4 |
| `LeadAgentPlan` | CP plan v2.9 — opaque `Mapping[str, Any]` faithful factor-out |
| `HandoffContext` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1/§13.4 |

This inheritance is per the operator-ratified T2 X-AL-3 FACTOR-OUT discriminator: where the spec commits the concept, the plan may decompose into field sets without invoking X-AL-3 design extension. No re-authoring at v1.10.

**Four amendment sites.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§17.4 (NEW)** | `hitl_gate` canonical signature materialization — closes `harness-cp/src/harness_cp/hitl_placement.py:178` `NotImplementedError`. Pure signature materialization for existing C-CP-17 §17 surface. | Phase A.2 ratified drafts §2D |
| **§25 (NEW) C-CP-25 ValidatorFramework** | Defines the per-step deterministic validation gate fired between LLM dispatch (or tool dispatch via runtime spec v1.13 §14.9) and step result acceptance. 5-class `ValidatorFailClass` taxonomy (per substitution H_T-CP-21); 5-class `ValidatorOutcome` enum; `ValidatorEvaluation` envelope. Span emission: `validator.evaluate` + `validator.fail` + `validator.revalidation` + `validator.escalation`. Closes `harness-cp/src/harness_cp/operator_burden_eval.py:140` (via downstream wiring at runtime spec v1.13 §14.10 `OperatorBurdenEvaluator`). 2 new CP fail classes. | Phase A.2 ratified drafts §2A |
| **§26 (NEW) C-CP-26 PauseResumeProtocol** | Defines explicit-pause + resume mechanics distinct from prefix-replay resumption landed at U-CP-56 (Path A-modified, coexist). 5-class `PauseReason` enum; `PauseSnapshot` envelope with state-ledger-anchored snapshot-hash; `MaterialDiffPolicy` 3-class enum (STRICT default). Closes `harness-cp/src/harness_cp/pause_resume_protocol.py:121, 143` `NotImplementedError`. 3 new CP fail classes. | Phase A.2 ratified drafts §2C |
| **§27 (NEW) C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter** | Defines runtime per-server trust evaluation when H_T acts as MCP **client** (consuming external MCP servers). Distinct from the H_T-as-MCP-server role landed at U-RT-62 (Q5 disjointness pin closed). 4-class `MCPPrimitive` enum per C-AS-14; 6-class `TrustDecisionReason` enum. **Unknown-server default = ALLOW with tier-floor** per Decision 3.D1 ratification (was DENY; operator-ratified ALLOW). `TierDerivationRule` 3-class enum. UNKNOWN decisions always audit-required. Span: `mcp.trust.evaluate`. 3 new CP fail classes. | Phase A.2 ratified drafts §3 |

**Sections preserved verbatim from v1.9.** All v1.9 content outside the four amendment sites preserved unchanged. C-CP-01 through C-CP-24 (v1.9 §1 through §24) preserved verbatim. §13.5.1 NEW NOTE 4 + NOTE 5 + NOTE 6 from path-(i) absorption preserved. The v1.9 + v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 chain all preserved.

**Status posture.** Proposed (v1.9) → **Proposed (v1.10)**. v1.10 is an additive patch — three new contracts at §25 / §26 / §27 + one section extension at §17.4; no v1.9 contract re-decomposition; no acceptance criterion change.

**Downstream absorption owed (post-v1.10).**
(a) Workspace `CLAUDE.md` §2.3 CP row version bump (v1.9 → v1.10).
(b) `harness-cp/CLAUDE.md` §1.2 + §4.1 retirement-table extensions (H_T-CP-18 / H_T-CP-21 / H_T-CP-22 transition shapes pending implementation arc).
(c) `Spec_Harness_Runtime_v1.md` v1.13 co-published this arc with §14.9 (C-RT-19) + §14.10 (C-RT-20) — references §27 (`PerServerTrustEvaluator`) at §14.9.1 step 2 + step 7.
(d) `Spec_Action_Surface_v1.md` v1.4 co-published this arc with §14.3 + §15 producer-site reference notes.
(e) `Cross_Axis_Composition_Document_v2_5.md` → v2.6 co-published at Phase A.4 with new CXA edges.
(f) `Implementation_Plan_Control_Plane` revision-pass: new atomic units for §25 + §26 + §27 + §17.4 materialization. Owed to `implementation-planner` revision-pass at Phase C.
(g) `Spec_Operational_Discipline_v1_7.md` → v1.8 absorption deferred to Phase A.5 (OD compound-irrelevance unblock).

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** None — apply pass is fidelity-pure transcription of ratified draft content.

---

## §17.4 (NEW) `hitl_gate` canonical signature materialization

C-CP-17 §17 (HITLPlacement schema + 3-placement enum) is extended at §17.4 with the canonical `hitl_gate(...)` signature that closes the existing `Protocol` declaration `NotImplementedError` at `harness-cp/src/harness_cp/hitl_placement.py:178`. Pure signature materialization — no new contract surface; no new field sets; the gate body composition is owned by the runtime-side composer per C-RT-18 §14.8.

### Canonical signature

```python
async def hitl_gate(
    placement: HITLPlacement,            # from C-CP-17 §17.3
    step: WorkflowStep,
    step_context: StepExecutionContext,
    *,
    surface: AskUserQuestionSurface,     # injected per U-RT-60
    palette: frozenset[HITLResponse],    # from placement or C-CP-16 §16.1 4-response palette default
    timeout: Duration | None,
) -> HITLGateResult: ...
```

### `HITLGateResult` (typed return envelope)

Reuses the existing 4-response palette from C-CP-16 §16.1 (preserved verbatim):

```python
@dataclass(frozen=True)
class HITLGateResult:
    response: HITLResponse                              # APPROVE | EDIT | REJECT | RESPOND per C-CP-16 §16.1
    edited_proposal: Mapping[str, Any] | None           # populated when response==EDIT (per C-CP-16 §16.2 audit shape)
    rejection_reason: str | None                        # populated when response==REJECT
    response_text: str | None                           # populated when response==RESPOND
    response_latency_ms: int
    timed_out: bool
```

### Invariants

1. **Composer body owns gate execution.** This signature is the surface; the body composition lives at C-RT-18 §14.8 (runtime-side HITL gate composer).
2. **Palette default is C-CP-16 §16.1 4-response palette.** `frozenset({APPROVE, EDIT, REJECT, RESPOND})`.
3. **Surface injection per U-RT-60.** Default surface = `MCPBackedAskUserQuestionSurface`; webhook-mode delegates to `WebhookDeliveryComposer` per runtime spec v1.13 §14.10.

### Provenance

Closes the `Protocol` declaration left at `Protocol` level in v1.2 + carried forward through v1.9. v1.10 materializes the surface; runtime spec v1.13 §14.8 (preserved from v1.12) composes the gate body.

---

## §25 (NEW) C-CP-25 — ValidatorFramework

**Contract surface.** `ValidatorFramework` owns the per-step deterministic validation gate fired between LLM dispatch (or tool dispatch per runtime spec v1.13 §14.9) and step-result acceptance. Validation that fails routes per `ValidatorFailClass` taxonomy.

**PRD enablement.** PRD v1.1 §"Validator-fail taxonomy + revalidation arc". Substitution H_T-CP-21 STILL-BOUNDED per `harness-cp/CLAUDE.md` §4.1.

**ADR commitment.** ADR-D3 v1.2 (validation contract) + ADR-D5 v1.4 (escalation discipline at validator-fail) + ADR-D6 v1.2 (`validator.*` observability namespace).

**Fork-resolution provenance.** Phase A.2 ratified drafts §2A (operator-ratified 2026-05-21). Decision 2.D3: validators run EVERY step (opt-out via no-op validator) per RATIFIED-WITH-DEFAULT.

### §25.1 Canonical signature(s)

```python
# ValidatorProtocol — operator-supplied
class Validator(Protocol):
    async def validate(
        self,
        step: WorkflowStep,
        step_result: StepOutput,
        *,
        step_context: StepExecutionContext,
    ) -> ValidatorResult: ...

# ValidatorFramework — runtime-side composer (materialized at stage 5)
class ValidatorFramework:
    async def evaluate(
        self,
        step: WorkflowStep,
        step_result: StepOutput,
        *,
        step_context: StepExecutionContext,
    ) -> ValidatorEvaluation: ...
```

### §25.2 Field sets / enums introduced

**`ValidatorOutcome`** (5-class enum):

```python
class ValidatorOutcome(Enum):
    PASS = "pass"
    REVALIDATE = "revalidate"                            # mutate + retry via C-RT-16
    ESCALATE = "escalate"                                # HITL gate composition per C-RT-18 §14.8
    PERMANENT_FAIL = "permanent_fail"                    # abort workflow
    OPERATOR_BURDEN_EXCEEDED = "operator_burden_exceeded"  # degrade per persona-tier (runtime spec v1.13 §14.10 `OperatorBurdenEvaluator`)
```

**`ValidatorFailClass`** (5-class taxonomy per substitution H_T-CP-21):

```python
class ValidatorFailClass(Enum):
    SCHEMA_VIOLATION = "schema_violation"                # output doesn't match input_schema
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"    # contradicts prior step state
    SAFETY_POLICY = "safety_policy"                      # operator-defined policy hit
    RESOURCE_CONSTRAINT = "resource_constraint"          # cost/latency budget exceeded
    EXTERNAL_REJECTION = "external_rejection"            # downstream service rejected
```

**`ValidatorResult`** (operator-supplied validator return):

```python
@dataclass(frozen=True)
class ValidatorResult:
    outcome: ValidatorOutcome
    fail_class: ValidatorFailClass | None                # None if outcome=PASS
    revalidation_payload: Mapping[str, Any] | None       # populated on REVALIDATE
    escalation_brief: HITLEscalationBrief | None         # populated on ESCALATE
    fail_detail_hash: str | None                         # sha256 of fail-reason text
```

**`ValidatorEvaluation`** (framework output):

```python
@dataclass(frozen=True)
class ValidatorEvaluation:
    result: ValidatorResult
    span_attributes: Mapping[str, Any]                   # validator.* namespace per §25.5
    next_action: ValidatorNextAction                     # PROCEED | RETRY | ESCALATE_HITL | ABORT
    burden_count: int                                    # cumulative operator-burden score at this gate
```

**ValidatorOutcome → ValidatorNextAction mapping (operator-ratified 2026-05-21 per Phase B iteration-1 F2-03):**

| ValidatorOutcome | ValidatorNextAction | Rationale |
|---|---|---|
| `PASS` | `PROCEED` | Validation succeeded; step result accepted. |
| `REVALIDATE` | `RETRY` | Mutate payload (per `result.revalidation_payload`) + retry via C-RT-16 retry wrapper; if retry budget exhausted, escalates to PERMANENT_FAIL. |
| `ESCALATE` | `ESCALATE_HITL` | Validator-fail escalation arc per §25.7 invariant 4; opens HITL gate composition via C-RT-18 §14.8. |
| `PERMANENT_FAIL` | `ABORT` | Workflow aborts with `fail_class` propagation per §25.6. |
| `OPERATOR_BURDEN_EXCEEDED` | `ESCALATE_HITL` | Operator-notify pattern (operator-ratified 2026-05-21). Burden threshold breach surfaces to HITL with a degradation-notification shape; operator decides proceed/abort per-case. The runtime spec v1.13 §14.10 `OperatorBurdenEvaluator.should_degrade()` returns `DegradationDecision`; framework escalates to HITL when `degrade=true`. |

The mapping is bijective on outcomes (each outcome maps to exactly one next_action) but NOT on next_actions (ESCALATE_HITL maps from both ESCALATE and OPERATOR_BURDEN_EXCEEDED; consumers MUST disambiguate via the `validator.outcome` span attribute per §C-OD-29 namespace).

**`HITLEscalationBrief`** (typed payload passed to HITL gate when validator escalates):

```python
@dataclass(frozen=True)
class HITLEscalationBrief:
    parent_step_id: str
    parent_action_id: str
    fail_class: ValidatorFailClass
    fail_detail_hash: str
    escalation_reason: str                               # operator-readable summary
    proposed_response_palette: frozenset[HITLResponse]   # default = full palette per C-CP-16 §16.1
```

### §25.3 Lifecycle stage placement

**Stage 5 (LOOP_INIT):** `ValidatorFramework` instantiated with reference to `ctx.validator_registry` (operator-populated registry of per-step `Validator` instances). Bound to `ctx.validator_framework`.

**Workflow-driver integration:** At `workflow_driver.py` post-dispatch step (currently `_append_step_ledger_entry`), add pre-ledger-append validation hook: `evaluation = await ctx.validator_framework.evaluate(...); if evaluation.next_action != PROCEED: branch per-action`.

### §25.4 Invocation discipline

Per Decision 2.D3 RATIFIED:

1. **Run every step (opt-out via no-op validator).** Framework invokes `Validator.validate()` on every step. Operator opts out per-step by binding a no-op `Validator` returning `ValidatorResult(outcome=PASS, ...)`.
2. **Validation runs after dispatch, before ledger append.** State-ledger entry is the canonical commit point per C-IS-05 §5.
3. **REVALIDATE bounded by C-RT-16 retry policy.** A REVALIDATE outcome routes back through the retry wrapper; if retry budget exhausted, escalates to `PERMANENT_FAIL`.
4. **ESCALATE always emits HITL gate.** Escalation cannot be silently dropped.
5. **Burden count monotonic per workflow.** Tracked on `ctx.operator_burden_counter`; reset only at workflow boundary.

### §25.5 Span emission

| Span | Trigger | Attributes |
|---|---|---|
| `validator.evaluate` | Every evaluation (outer envelope) | `step.id`, `validator.outcome`, `validator.burden_count_cumulative` |
| `validator.fail` | Non-PASS outcome | `validator.fail.class`, `validator.fail.detail_hash`, `validator.fail.next_action`, `validator.fail.escalation_owed` |
| `validator.revalidation` | REVALIDATE outcome | `validator.revalidation.payload_size_bytes`, `validator.revalidation.attempt_number` |
| `validator.escalation` | ESCALATE outcome | Links to subsequent `hitl.gate.evaluated` span via parent-context propagation |

All `validator.*` spans head=1.0 (always-sampled) per operator-visibility requirement.

### §25.6 Failure-mode taxonomy

2 new CP fail classes:

| Fail class | Trigger |
|---|---|
| `CP-FAIL-VALIDATOR-PERMANENT` | `ValidatorOutcome.PERMANENT_FAIL` |
| `CP-FAIL-VALIDATOR-OPERATOR-BURDEN-EXCEEDED` | `OPERATOR_BURDEN_EXCEEDED` with no degradation policy match |

### §25.7 Invariants

1. **Every step has at most one Validator.** Multi-validator per step deferred to future arc.
2. **Validation runs after dispatch, before ledger append.**
3. **REVALIDATE bounded by C-RT-16 retry policy.**
4. **ESCALATE always emits HITL gate.**
5. **Burden count monotonic per workflow.**

### §25.8 Deferred to implementation discretion

- **`ValidatorNextAction` enum value names** — `PROCEED | RETRY | ESCALATE_HITL | ABORT` suggested; impl arc selects + documents at composer body.
- **`fail_detail_hash` content shape** — sha256 of `fail_class.value + ":" + fail_reason_text` suggested.

---

## §26 (NEW) C-CP-26 — PauseResumeProtocol

**Contract surface.** `PauseResumeProtocol` owns explicit-pause + resume mechanics distinct from the prefix-replay resumption landed at U-CP-56 (Path A-modified). Captures snapshot at pause point; resumes from snapshot + material-diff detection.

**PRD enablement.** PRD v1.1 §"Pause/resume protocol with material-diff detection". Substitution H_T-CP-22 STILL-BOUNDED per `harness-cp/CLAUDE.md` §4.1.

**ADR commitment.** ADR-D1 v1.2 (engine + replay; pause/resume sits at the same primitive level as replay-resumption) + ADR-F2 v1.2 (state-ledger anchor for snapshots).

**Fork-resolution provenance.** Phase A.2 ratified drafts §2C. Decision 2.D6: coexist with U-CP-56 (distinct semantics); Decision 2.D7: `MaterialDiffPolicy` default = STRICT.

### §26.1 Canonical signature(s)

```python
class PauseResumeProtocol:
    async def capture_pause_snapshot(
        self,
        workflow_id: str,
        run_id: str,
        step_index: int,
        pause_reason: PauseReason,
    ) -> PauseSnapshot: ...

    async def attempt_resume(
        self,
        snapshot: PauseSnapshot,
        *,
        material_diff_policy: MaterialDiffPolicy,
    ) -> ResumeResult: ...
```

### §26.2 Field sets / enums introduced

**`PauseReason`** (5-class enum):

```python
class PauseReason(Enum):
    EXPLICIT_OPERATOR = "explicit_operator"
    HITL_PENDING = "hitl_pending"
    VALIDATOR_ESCALATION = "validator_escalation"
    TIMEOUT_BOUNDARY = "timeout_boundary"
    EXTERNAL_DEPENDENCY = "external_dependency"
```

**`PauseSnapshot`:**

```python
@dataclass(frozen=True)
class PauseSnapshot:
    workflow_id: str
    run_id: str
    step_index: int
    pause_reason: PauseReason
    state_summary: StateSummary                          # from CP plan v2.9 HandoffContext family (Pattern-D inherited)
    snapshot_hash: str                                   # sha256 of canonical serialization
    created_at: int                                      # epoch ms
    state_ledger_anchor: str                             # entry_hash at pause point per C-IS-05 §5
```

**`MaterialDiffPolicy`** (3-class enum):

```python
class MaterialDiffPolicy(Enum):
    STRICT = "strict"                                    # any diff abort (DEFAULT per Decision 2.D7)
    LENIENT = "lenient"                                  # only behavior-changing diff abort
    OPERATOR_ARBITRATE = "operator_arbitrate"            # HITL on any diff
```

**`ResumeResult`:**

```python
@dataclass(frozen=True)
class ResumeResult:
    resumed: bool
    diff_detected: bool
    diff_summary_hash: str | None
    new_run_id: str | None                               # if resume requires fresh run_id
    fail_class: str | None
```

### §26.3 Lifecycle stage placement

**Stage 5 (LOOP_INIT):** `PauseResumeProtocol` instantiated with reference to `ctx.state_ledger_writer` + `ctx.state_ledger_reader`. Bound to `ctx.pause_resume_protocol`.

**Workflow-driver integration:** Pause invocation surfaces at any step boundary; resume invocation lives at workflow re-entry (alongside U-CP-56 replay-resumption check).

### §26.4 Span emission

| Span | Trigger | Attributes |
|---|---|---|
| `pause.captured` | Snapshot captured | `pause.reason`, `pause.snapshot_hash`, `pause.step_index`, `pause.state_ledger_anchor` |
| `resume.attempted` | Resume invoked | `resume.snapshot_hash`, `resume.diff_detected`, `resume.diff_policy`, `resume.outcome` |

### §26.5 Failure-mode taxonomy

3 new CP fail classes:

| Fail class | Trigger |
|---|---|
| `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION` | `snapshot_hash` doesn't validate on resume |
| `CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED` | STRICT policy + diff detected |
| `CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED` | `OPERATOR_ARBITRATE` policy + diff → HITL escalation owed |

### §26.6 Invariants

1. **Snapshot is immutable once captured.** No mutation after pause.
2. **Resume must validate snapshot hash.** Corruption → fail-closed.
3. **Material diff defined as state-ledger-anchor divergence.** If `state_ledger_anchor` no longer reachable from current entry chain, diff detected.
4. **Per-pause-reason routing.** Each `PauseReason` has its own resume policy default.
5. **Coexist with U-CP-56 replay-resumption.** Per Decision 2.D6: `PauseResumeProtocol` handles explicit pause/resume; U-CP-56 handles prefix-replay-based resumption (Path A-modified ratification preserved).

### §26.7 Deferred to implementation discretion

- **`PauseReason` → default `MaterialDiffPolicy` mapping** — operator-configurable at bootstrap.
- **`diff_summary_hash` content shape** — sha256 of diff serialization; format owed to U-CP-22 implementation arc.

---

## §27 (NEW) C-CP-27 — PerServerTrustEvaluator + MCPClientNamespaceEmitter

**Contract surface.** `PerServerTrustEvaluator` owns runtime per-server trust evaluation when H_T acts as MCP **client** (consuming external MCP servers via runtime spec v1.13 §14.9 `MCPClientHost`). Distinct from the H_T-as-MCP-server role landed at U-RT-62 (which made H_T the MCP server CC consumes). **The Q5 disjointness pin from U-RT-62 is closed at this contract.** `MCPClientNamespaceEmitter` owns `mcp.*` 7-attribute namespace emission per C-AS-14 §14.3 at the H_T-as-MCP-client tool-invocation site.

**PRD enablement.** PRD v1.1 §"Per-server trust framework + MCP integration observability". Substitution H_T-CP-18 STILL-BOUNDED per `harness-cp/CLAUDE.md` §4.1.

**ADR commitment.** ADR-D2 v1.2 (sandbox + blast-radius; per-server trust is the consumer-side complement) + ADR-D6 v1.2 (`mcp.*` observability namespace).

**Fork-resolution provenance.** Phase A.2 ratified drafts §3. Decision 3.D1 RATIFIED-WITH-EDIT: unknown-server default = ALLOW with tier-floor (was DENY); operator-elected ALLOW-with-tier-floor. UNKNOWN decisions always audit-required.

### §27.1 Canonical signature(s)

```python
class PerServerTrustEvaluator:
    async def evaluate(
        self,
        server_name: str,
        primitive: MCPPrimitive,
        tool_contract: ToolContract | None,              # populated when primitive=tool
        operator_policy: TrustPolicy,
    ) -> TrustEvaluation: ...

class MCPClientNamespaceEmitter:
    def emit_mcp_call_span(
        self,
        span: Span,                                      # the mcp.tool.call span opened by runtime spec v1.13 §14.9.4
        server_name: str,
        primitive: MCPPrimitive,
        signature_hash: str,
    ) -> None: ...                                       # mutates span with mcp.* 7-attribute namespace per C-AS-14 §14.3
```

### §27.2 Field sets / enums introduced

**`MCPPrimitive`** (4-class enum per C-AS-14):

```python
class MCPPrimitive(Enum):
    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"
    SAMPLING = "sampling"
```

**`TrustEvaluation`:**

```python
@dataclass(frozen=True)
class TrustEvaluation:
    permitted: bool
    trust_tier_evaluated: MCPTrustTier
    decision_reason: TrustDecisionReason
    audit_required: bool                                 # tail-keep when True
```

**`TrustPolicy`** (operator-configured at bootstrap):

```python
@dataclass(frozen=True)
class TrustPolicy:
    default_tier: MCPTrustTier                           # ALLOW-with-tier-floor threshold for unknown servers (Decision 3.D1)
    per_server_overrides: Mapping[str, MCPTrustTier]
    allow_list: frozenset[str]                           # exact server names always permitted (bypass tier-floor)
    deny_list: frozenset[str]                            # exact server names always denied (deny-wins)
    require_audit_below_tier: MCPTrustTier               # any call below this tier always audited
    tier_derivation: TierDerivationRule                  # how to compute tier for unknown servers (default conservative)
```

**`TierDerivationRule`** (3-class enum — operator-configurable tier-derivation strategy for unknown servers):

```python
class TierDerivationRule(Enum):
    CONSERVATIVE = "conservative"                        # unknown-server tier = MIN(MCPTrustTier members)
    PROTOCOL_VERSION_TABLE = "protocol_version_table"    # operator-supplied mapping protocol_version → tier
    OPERATOR_HOOK = "operator_hook"                      # call operator-supplied callable
```

**`TrustDecisionReason`** (6-class enum):

```python
class TrustDecisionReason(Enum):
    EXPLICIT_ALLOW = "explicit_allow"                                              # allow_list match
    EXPLICIT_DENY = "explicit_deny"                                                # deny_list match
    TIER_FLOOR_PASS = "tier_floor_pass"                                            # known server, tier >= floor
    TIER_FLOOR_VIOLATION = "tier_floor_violation"                                  # known server, tier < floor
    UNKNOWN_SERVER_TIER_FLOOR_PASS = "unknown_server_tier_floor_pass"              # unknown server, resolved tier >= default floor (ALLOW)
    UNKNOWN_SERVER_TIER_FLOOR_VIOLATION = "unknown_server_tier_floor_violation"    # unknown server, resolved tier < default floor (DENY)
```

**Reused (NOT re-authored):**
- `MCPTrustTier` from CP plan v2.8 U-CP-00c (canonical carrier; Pattern-D inherited per Phase A.1 §4.2).
- `ToolContract` from AS spec C-AS-12.

### §27.3 Lifecycle stage placement

**Stage 3a:** `PerServerTrustEvaluator` + `MCPClientNamespaceEmitter` instantiated alongside `MCPClientHost` (per runtime spec v1.13 §14.9.3). Bound to `ctx.per_server_trust_evaluator` + `ctx.mcp_client_namespace_emitter`. Trust policy loaded from bootstrap config.

**Stage 5:** `RuntimeToolDispatcher` (runtime spec v1.13 §14.9) invokes `ctx.per_server_trust_evaluator.evaluate(...)` PRE-call (step 2); `ctx.mcp_client_namespace_emitter.emit_mcp_call_span(...)` mutates the `mcp.tool.call` span DURING dispatch (step 7).

### §27.4 Span emission

| Span | Trigger | Attributes |
|---|---|---|
| `mcp.trust.evaluate` | Per evaluation | `mcp.trust.server_name`, `mcp.trust.primitive_kind`, `mcp.trust.decision_reason`, `mcp.trust.audit_required`, `mcp.trust.tier_evaluated` |
| `mcp.tool.call` (mutation) | DURING dispatch | `mcp.*` 7-attribute namespace per C-AS-14 §14.3 (populated by emitter) |

**Sampling discipline:** `mcp.trust.evaluate` head=1.0 if `audit_required=true`, else head=0.1 (tail-keep on audit-required per D6 §1.3). `UNKNOWN_SERVER_*` decisions ALWAYS set `audit_required=true` per Decision 3.D1.

### §27.5 Failure-mode taxonomy

3 new CP fail classes:

| Fail class | Trigger |
|---|---|
| `CP-FAIL-TRUST-EVALUATION-EXPLICIT-DENY` | Server in `deny_list` |
| `CP-FAIL-TRUST-EVALUATION-TIER-FLOOR-VIOLATION` | Known server, resolved tier < policy floor |
| `CP-FAIL-TRUST-EVALUATION-UNKNOWN-SERVER-TIER-FLOOR-VIOLATION` | Unknown server, resolved tier < default floor (ALLOW-with-tier-floor rejection) |

### §27.6 Invariants

1. **Trust policy immutable per workflow.** Loaded at bootstrap; no live mutation during workflow run.
2. **Every MCP-as-client call goes through evaluator.** No bypass path.
3. **Deny-list wins over allow-list.** If a server is in both, DENY.
4. **Unknown server policy = ALLOW-with-tier-floor** (Decision 3.D1 RATIFIED). Unknown server permitted iff resolved tier >= `TrustPolicy.default_tier`; resolution uses `tier_derivation` rule. `audit_required=true` auto-set on every `UNKNOWN_SERVER_TIER_FLOOR_PASS` for operator visibility.
5. **Audit-required calls always emit `mcp.trust.evaluate` span.** Tail-keep on `audit_required=true`. UNKNOWN_SERVER decisions always audit-required regardless of permitted outcome.

### §27.7 Deferred to implementation discretion

- **`TierDerivationRule.CONSERVATIVE` resolution** — `MIN(MCPTrustTier members)` per the enum-order convention; impl arc documents the explicit member at composer body.
- **`TierDerivationRule.OPERATOR_HOOK` callable shape** — operator supplies `Callable[[str, str | None], MCPTrustTier]`; signature owed to U-CP-18 implementation arc.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_10.md` |
| Version | v1.10 |
| Filing event | Phase A.2 ratified-drafts apply pass, Remaining-Work Closure Arc, 2026-05-21 |
| Predecessor | `Spec_Control_Plane_v1_9.md` (v1.9 path-(i) NOTE-form absorption; preserved verbatim) |
| Successor | Workspace `CLAUDE.md` §2.3 CP row version bump (v1.9 → v1.10); future implementation arcs per Phase C implementation-planner pass |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-21 |

*Filed at Phase 7 sub-phase 7b/7c as the CP-side ratified-drafts apply pass per `.harness/Phase_A_2_Contract_Drafts_v1.md`. v1.9 substantive content + §13.5.1 NOTE chain preserved verbatim; three NEW contracts at §25 / §26 / §27 + one §17.4 signature materialization. Pattern-D field sets inherited by citation (NOT re-authored). Pure additive patch — no signature change to any v1.9 contract. Co-published with runtime spec v1.13 + AS spec v1.4 + workspace `CLAUDE.md` updates.*
