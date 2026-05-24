# Specification — Control Plane v1.16

## Change-note (v1.15 → v1.16)

**Scope of revision.** Narrow-scope §26 amendment — authors NEW `ResumeContext` typed Pydantic v2 BaseModel carrier (single field `hitl_response: HITLResult | None = None`) + widens the existing v1.10 §26.1 `PauseResumeProtocol.attempt_resume(...)` async signature with one new keyword-only parameter `resume_context: ResumeContext | None = None` (backward-compatible default). Authored to enable the HITL-gate-as-pause-trigger composition arc per ratified scoping doc `.harness/hitl_gate_as_pause_trigger_composition_scoping.md` Q3 (c-ii) FORCED — empirical-grep verification at HEAD `e394074` confirmed `ResumeContext` does NOT exist at any source tree (ZERO hits across harness-runtime/harness-cp/harness-core), so the carrier itself must be authored. Operator-ratified 2026-05-24 (post-scoping-doc AskUserQuestion). ZERO change to existing field-sets at `PauseSnapshot` / `MaterialDiffPolicy` / `ResumeResult` / `PauseReason` / `WorkflowPauseReason`. ZERO change to `capture_pause_snapshot` signature. ZERO new fail class. ZERO new span attribute. ZERO new enum. ZERO behavior change at existing callers (the L9-undecies cluster `workflow_driver.py:477` async-bridge invocation passes no `resume_context` → receives None default → identical control flow to pre-v1.16 baseline). ZERO cross-axis cascade — OD spec §C-OD-30.4 `PauseResumeAuditPayload` unaffected (the new `ResumeContext.hitl_response` field is pre-commit data, not audit-emission territory; the audit payload composes from `PauseEvent` + `ResumeOutcome` per §C-OD-30.4.1, not from `ResumeContext`); CXA v2.10 unchanged; ADR/ADD/PRD unchanged.

**v1.15 substantive content preserved verbatim.** All v1.15 §19.1.1 (NEW) canonical 4-axis statement (§19.1.1.1 per-axis enumeration table + §19.1.1.2 non-axis statement + §19.1.1.3 consumer implication + §19.1.1.4 verbatim-layer integrity) preserved unchanged. All v1.14 4-cite-cell canonical-reading amendments preserved. All v1.13 §28 ValidatorFramework rename preserved. All v1.12 §25.2.1 9th-field amendment preserved. All v1.11 §26.2 `PauseReason` → `WorkflowPauseReason` rename + §26 NEW NOTE preserved. All v1.10 §26 / C-CP-26 NEW substantive content preserved verbatim (§26.1 capture_pause_snapshot signature + §26.2 PauseReason/PauseSnapshot/MaterialDiffPolicy/ResumeResult field-sets + §26.3 lifecycle stage placement + §26.4 span emission + §26.5 failure-mode taxonomy + §26.6 invariants + §26.7 deferred-to-discretion). All v1.6/v1.2 substantive content preserved.

**Source of fix.** Ratified scoping doc at `.harness/hitl_gate_as_pause_trigger_composition_scoping.md` §0(B) empirical-verification finding + Q3 recommendation revised from initial (c-i) narrow scope to (c-ii) FORCED cross-axis scope after grep confirmed `ResumeContext` carrier does not exist + operator AskUserQuestion 2026-05-24 ratification ("Ratified") at session opening the HITL-gate-as-pause-trigger composition arc per checkpoint `20260524-130230` item #1.

**Authority basis for fix direction.** The HITL-gate-as-pause-trigger composition (resolving runtime spec v1.21 §14.14.7 deferred-discretion residual (i)) requires a delivery surface for operator HITL response across the pause-resume boundary. C-CP-17 §17.1 `await_human_approval(action, context, channel)` declares the durable-async HITL primitive shape as "Durable signal-and-wait" — the operator's response IS the durable signal that must arrive at the resumed step. The async `attempt_resume(snapshot, *, material_diff_policy)` signature at v1.10 §26.1 has NO operator-context envelope, so the durable signal has no delivery surface. The minimal fix is: (a) author a typed `ResumeContext` envelope carrier; (b) widen `attempt_resume` to accept it as keyword-only with backward-compatible default. The narrow scope preserves all existing carrier shapes (`PauseSnapshot`, `MaterialDiffPolicy`, `ResumeResult`) and all existing caller invocations.

The (c-ii) cross-axis scoping at the spec-writer level (CP-axis authoring the carrier) rather than runtime-spec-only field-extension (the initially-considered (c-i) narrow scope) is forced by the empirical absence of any existing carrier at HEAD — the L9-undecies cluster (runtime spec v1.21 §14.14 + impl at U-RT-87/88/89) landed only `PauseSnapshot` / `ResumeResult` / `MaterialDiffPolicy` / `ResumeOutcomeKind` / `ResumeOutcome` / `ResumeAttempt`, none of which carry operator-supplied resume-context envelope shape. CP-side authoring places `ResumeContext` adjacent to the existing carriers at C-CP-22 (v1.10 §26.2 / `pause_resume_protocol_types.py`), preserving co-location discipline.

**Two amendment sites (1 NEW sub-section + 1 signature widening).**

| Site | Amendment shape |
|---|---|
| **§26.8 (NEW) — `ResumeContext` carrier** | NEW sub-section appended at §26 (v1.10 §26.1-§26.7 + v1.11 NEW NOTE preserved verbatim outside this addition). Authors `ResumeContext` typed Pydantic v2 BaseModel — frozen, single field `hitl_response: HITLResult | None = None`. Single carrier; no methods. Forward-cite to runtime spec v1.24 §14.8.2 step 4-bis (the consumer of the carrier) deferred until runtime spec v1.24 lands. |
| **§26.1 — `attempt_resume` signature widening** | Amends the v1.10 §26.1 canonical `attempt_resume` async signature: ADDS one new keyword-only parameter `resume_context: ResumeContext | None = None` at the end of the keyword-only parameter list (after `material_diff_policy`). Backward-compatible default `None`. ZERO removal; ZERO existing-parameter type change; ZERO return-type change. |

**Adjacent harmonization sites.** None — the §26.2 field-sets (PauseReason / PauseSnapshot / MaterialDiffPolicy / ResumeResult), §26.3 lifecycle stage placement, §26.4 span emission, §26.5 failure-mode taxonomy, §26.6 invariants (5 invariants preserved verbatim — the operator-response delivery surface authored at v1.16 is orthogonal to all 5 existing invariants), §26.7 deferred-to-discretion enumeration, the v1.11 NEW NOTE on §22 ↔ §26 engine-layer vs workflow-layer coexistence — all preserved verbatim. The amendment is **purely additive** at the signature layer (one new optional parameter with backward-compatible default) and **purely additive** at the type-set layer (one new typed envelope adjacent to existing carriers).

**Sections preserved verbatim from v1.15.** All v1.15 §19.1.1 (NEW) canonical 4-axis statement preserved verbatim. All v1.14 4-cite-cell amendments preserved. All v1.13 §28 rename preserved. All v1.12 9th-field amendment preserved. All v1.11/v1.10/v1.6/v1.2 substantive content preserved.

**Status posture.** Proposed (v1.15) → **Proposed (v1.16)**. v1.16 is a fidelity-pure additive amendment — one NEW field-set carrier + one signature widening with backward-compatible default. NO v1.15 contract removed; NO v1.15 contract re-decomposition; NO v1.15 field-set modified. Contract count unchanged at 28 (the carrier is a sub-type of C-CP-26, not a new contract surface). Fail-class count unchanged. Signature change at any Protocol: ONE — `PauseResumeProtocol.attempt_resume(...)` gains one keyword-only parameter with backward-compatible default. Acceptance criterion change at any contract: NONE at spec-side (CP plan U-CP-NN absorption AC re-decomposition is downstream absorption per (b) below). Behavior change: NONE (existing callers receive None default; new callers may pass `ResumeContext(hitl_response=...)` to inject operator response; the runtime-spec-side consumer at v1.24 §14.8.2 step 4-bis is the only authorized propagation path).

**Downstream absorption owed (post-v1.16).**

(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.15 → v1.16); co-published this arc.

(b) **CP plan v2.20 → v2.21** — single-unit-body amendment at the U-CP unit hosting `attempt_resume` (`U-CP-64` or naming-equivalent per v2.20 enumeration; the unit that landed §26.6 invariants 1-5 at cluster 10-CP-B `49617e7`). Add `resume_context: ResumeContext | None = None` to the AC enumerating the async signature; add `ResumeContext` carrier to the unit's Files-column. NO new unit; NO new cluster; NO DAG topology change. Co-published this arc.

(c) **harness-cp impl** updates: `harness-cp/src/harness_cp/pause_resume_protocol_types.py` — APPEND new `ResumeContext` BaseModel (frozen Pydantic v2; single optional field). `harness-cp/src/harness_cp/pause_resume_protocol.py:295` — AMEND async `attempt_resume(...)` signature: add `resume_context: ResumeContext | None = None` keyword-only parameter at end of kw-only list. Method body: NO change at v1.16 — the parameter is ingested but not consumed at the CP-side implementation (the resumed-step HITL-gate response-propagation logic lives at runtime-side per scoping doc Q3 + Q1; CP-side just carries the parameter for the runtime-side to inspect via the `attempt_resume` return-path or via reading from `resume_context` at the workflow-driver resume entry-point). 16/16 existing pause/resume tests should pass unchanged (no behavior change with default None). Co-published this arc OR next sequential commit.

(d) **harness-runtime impl** updates: ZERO at this arc — the runtime-side consumption of `ResumeContext.hitl_response` is authored at the SEPARATE runtime spec v1.23 → v1.24 amendment + L9-terdecies cluster impl (U-RT-93/94/95) per scoping doc §3.1.

(e) **OD spec / OD plan / OD impl**: ZERO — `PauseResumeAuditPayload` at OD spec §C-OD-30.4 composes from `PauseEvent` + `ResumeOutcome` per §C-OD-30.4.1; `ResumeContext` is pre-commit data and never enters the audit-emission path. ZERO OD cascade.

(f) **CXA v2.10**: ZERO — no new cross-axis edge; `ResumeContext` is intra-CP-axis (carrier authored at CP, consumed at runtime via existing CP→runtime composition pattern); the pause/resume CP→OD audit-write seam at CXA §2.3.7 row 6 is unaffected.

(g) **ADR-D1 / ADR-D5 / ADD / PRD**: ZERO retag owed — `ResumeContext` is a derivative carrier within C-CP-26 (ADR-D1 v1.2 commitment territory: engine + replay; pause/resume sits at the same primitive level as replay-resumption). The narrow widening preserves the §26 contract surface as already-committed-at-ADR-level.

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **`ResumeContext` future-extensibility.** v1.16 authors the carrier with a single field `hitl_response: HITLResult | None = None`. Future arcs may need additional operator-supplied resume-time context (e.g., `operator_burden_override` per OPERATOR_BURDEN_EXCEEDED validator outcome; `revalidation_skip_reason` for sub-tier-recovery paths; `resume_idempotency_key` for explicit-idempotency-on-resume). Surfaced; NOT patched at v1.16 per FM-2 — the scoping doc Q3 authorized ONLY `hitl_response` field. Subsequent fields routed to follow-on operator-discretion arcs.

(ii) **`ResumeContext.hitl_response` semantic at non-HITL pause reasons.** When `snapshot.pause_reason ∈ {EXPLICIT_OPERATOR, TIMEOUT_BOUNDARY, EXTERNAL_DEPENDENCY}` (i.e., pause reasons NOT correlated with a HITL gate), `resume_context.hitl_response` should be None (the resume has no HITL gate to inject a response into). The §26 invariants do NOT currently enumerate a per-pause-reason validity check on `ResumeContext`. Surfaced; NOT patched at v1.16 per FM-2 — runtime-side consumer (v1.24 §14.8.2 step 4-bis) is the appropriate check site, not the CP-side carrier definition. If runtime-spec v1.24 authors such a check, the cross-pause-reason validity matrix can be co-published or deferred to a separate spec-extension arc.

(iii) **Forward-cite to runtime spec v1.24 §14.8.2 step 4-bis.** The `ResumeContext` authored at v1.16 §26.8 has a forward-cite consumer at runtime spec v1.24 §14.8.2 step 4-bis (the HITL gate composer body durable-async branch). Runtime spec v1.24 is co-published in this arc per scoping doc §3.1 commit-3. v1.16 §26.8 contains a placeholder forward-cite that resolves when v1.24 lands; this is the established v2.6 / v2.9 forward-cite hygiene pattern preserved.

(iv) **D8 cite-correction (v1.21 §18.3 → §18.1)** absorbed at runtime spec v1.24, NOT at CP spec v1.16. The CP spec §18 sections (§18.1 synchrony-class matrix, §18.3 both-by-tier overlay) are correctly anchored at the CP-side; the cite drift lives at the runtime spec deferral text per scoping doc §0(D). v1.16 does NOT touch any §18.* section.

---

## §26.8 (NEW) — `ResumeContext` carrier

### §26.8.1 Carrier definition

```python
class ResumeContext(BaseModel):
    """Operator-supplied resume-time context envelope.

    Authored at CP spec v1.16 to enable HITL-gate-as-pause-trigger composition
    per runtime spec v1.21 §14.14.7 deferred-discretion residual (i) resolution.

    The envelope carries operator-supplied data that the resumed step must
    consume during the resume cycle. v1.16 authors a single field for the
    durable-async HITL response delivery surface; future arcs may extend
    with additional operator-supplied resume-time context (see v1.16
    change-note adjacent defect (i)).
    """
    model_config = ConfigDict(frozen=True)

    hitl_response: HITLResult | None = None
    """Operator HITL response delivered during durable-async pause.

    Set to None when the pause was not correlated with a HITL gate
    (e.g., EXPLICIT_OPERATOR, TIMEOUT_BOUNDARY, EXTERNAL_DEPENDENCY
    pause reasons). Set to a populated HITLResult when the pause was
    triggered by a HITL gate composer body firing
    ``ctx.pause_requested_flag.set()`` on durable-async cell synchrony
    per C-CP-18 §18.1 (NOT §18.3 — see runtime spec v1.24 §14.8.2
    cite-correction) and the operator has delivered a response via
    the inbound webhook endpoint that consumes operator response.

    Consumed by runtime spec v1.24 §14.8.2 step 4-bis (the HITL gate
    composer body durable-async branch on resumed-step re-entry).
    The HITLResult shape is canonical at C-CP-17 §17.1 (CP spec v1.2
    line 1495-1502, preserved verbatim through v1.16).
    """
```

### §26.8.2 Field semantics

| Field | Type | Semantics | Source-of-truth carrier for type |
|---|---|---|---|
| `hitl_response` | `HITLResult \| None` | Operator HITL response delivered during durable-async pause. None when pause was not HITL-gate-correlated; populated `HITLResult` when pause was HITL-gate-correlated AND operator has delivered response. | C-CP-17 §17.1 (CP spec v1.2 line 1495-1502) |

### §26.8.3 Composition with §26.6 invariants

The 5 invariants at §26.6 (preserved verbatim from v1.10) are **all orthogonal** to `ResumeContext`:

| Invariant | Composition with `ResumeContext` |
|---|---|
| 1. Snapshot is immutable once captured | Orthogonal — `ResumeContext` is supplied at resume-time, not at capture-time |
| 2. Resume must validate snapshot hash | Orthogonal — `ResumeContext` does not affect snapshot hash validation (`AC #1` per §26.6 line 295-298 unchanged) |
| 3. Material diff defined as state-ledger-anchor divergence | Orthogonal — `ResumeContext.hitl_response` is pre-commit operator data; material diff check is independent state-ledger validity check |
| 4. Per-pause-reason routing | Orthogonal — each `WorkflowPauseReason` retains its own `MaterialDiffPolicy` default; `ResumeContext.hitl_response` is an additional operator-supplied datum, not a routing input |
| 5. Coexist with U-CP-56 prefix-replay-based resumption | Orthogonal — `ResumeContext` is consumed only at `PauseResumeProtocol.attempt_resume(...)` path, not at U-CP-56 prefix-replay path; the two paths remain non-overlapping per Decision 2.D6 |

### §26.8.4 Verbatim-layer integrity

The v1.10 file (`Spec_Control_Plane_v1_10.md`) §26.1-§26.7 substantive content is NOT edited at v1.16 — delta-only spec-chain preservation discipline preserved per v1.13 §1.3 + v1.14 §1.3 + v1.15 §19.1.1.4 verbatim-layer-integrity precedent. The §26.1 `attempt_resume` async signature widening at v1.16 is recorded at §26.8.5 below as a canonical-reading amendment over the v1.10 signature; consumers reading the delta chain interpret the v1.10 §26.1 signature AS canonically supplemented at v1.16 §26.8.5 per this change-note.

### §26.8.5 `attempt_resume` async signature widening (canonical reading)

The v1.10 §26.1 `PauseResumeProtocol.attempt_resume(...)` async signature is canonically read at v1.16 as:

```python
class PauseResumeProtocol:
    async def attempt_resume(
        self,
        snapshot: PauseSnapshot,
        *,
        material_diff_policy: MaterialDiffPolicy,
        resume_context: ResumeContext | None = None,  # NEW at v1.16; backward-compatible default
    ) -> ResumeResult: ...
```

**Backward compatibility.** Existing callers at L9-undecies impl arc (`workflow_driver.py:477` async-bridge invocation per U-RT-89 landing at `de4ae66` / `671f195`) pass no `resume_context` → receives None default → identical control flow to pre-v1.16 baseline. The 16/16 existing pause/resume unit tests + 4/4 e2e tests at `harness-runtime/tests/integration/test_u_rt_89_pause_resume_full_execution_path.py` pass unchanged.

**Forward-compatibility.** New callers (the runtime spec v1.24 §14.8.2 step 4-bis durable-async branch's resume-entry-point invocation, after operator HITL response arrives via inbound webhook endpoint) pass `ResumeContext(hitl_response=HITLResult(...))` → resumed-step HITL gate consumes the response without re-firing the webhook.

**Method body posture at v1.16.** The CP-side `PauseResumeProtocol.attempt_resume(...)` method body at `harness-cp/src/harness_cp/pause_resume_protocol.py:295` ingests but does NOT consume `resume_context` at v1.16 — the runtime-side consumer (v1.24 §14.8.2 step 4-bis) is the propagation site. The CP-side method just carries the parameter through; the runtime-side caller is responsible for inspecting `resume_context.hitl_response` at the resumed-step HITL gate evaluation site. This preserves the CP→runtime composition pattern established at C-CP-26 v1.10 §26.3 (CP authors the protocol; runtime composes the consumption pattern).

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v1.15 §19.1.1 (NEW) canonical 4-axis statement (§19.1.1.1-§19.1.1.4) | Preserved verbatim |
| v1.14 4-cite-cell canonical-reading amendment | Preserved verbatim |
| v1.13 §28 ValidatorFramework rename | Preserved verbatim |
| v1.12 §25.2.1 9th-field `workflow_id` amendment | Preserved verbatim |
| v1.11 §26.2 `PauseReason` → `WorkflowPauseReason` rename + §26 NEW NOTE | Preserved verbatim |
| v1.10 §26 / C-CP-26 PauseResumeProtocol substantive content (§26.1-§26.7) | Preserved verbatim — v1.16 §26.8 (NEW) appended; §26.1 async signature widening recorded as canonical-reading amendment at §26.8.5; v1.10 file NOT edited |
| v1.10 §27 / C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter | Preserved verbatim |
| v1.10 §25 / C-CP-25 → §28 / C-CP-28 ValidatorFramework (rename per v1.13) | Preserved verbatim |
| v1.6/v1.2 substantive contract bodies | Preserved verbatim |
| C-CP-17 §17.1 HITLResult type (CP spec v1.2 line 1495-1502) | Preserved verbatim — `ResumeContext.hitl_response: HITLResult \| None` consumes this canonical type without modification |
| C-CP-18 §18.1 synchrony-class × HITL-primitive-shape 2D matrix | Preserved verbatim |
| C-CP-18 §18.3 both-by-tier per-tool overlay | Preserved verbatim |
| C-CP-22 §22.1 (any §22.1 pre-existing content at lineage point) | Preserved verbatim |
| §26.1 `capture_pause_snapshot` async signature | Preserved verbatim (unchanged at v1.16) |
| §26.2 field-sets (PauseReason / WorkflowPauseReason / PauseSnapshot / MaterialDiffPolicy / ResumeResult) | Preserved verbatim |
| §26.3 lifecycle stage placement | Preserved verbatim |
| §26.4 span emission | Preserved verbatim |
| §26.5 failure-mode taxonomy | Preserved verbatim |
| §26.6 invariants 1-5 | Preserved verbatim — §26.8.3 documents orthogonality of all 5 to `ResumeContext` |
| §26.7 deferred-to-discretion enumeration | Preserved verbatim |
| All other v1.x contracts | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_16.md` |
| Version | v1.16 |
| Filing event | HITL-gate-as-pause-trigger composition arc per ratified scoping doc `.harness/hitl_gate_as_pause_trigger_composition_scoping.md` Q3 (c-ii) FORCED + operator AskUserQuestion 2026-05-24 ratification |
| Predecessor | `Spec_Control_Plane_v1_15.md` (v1.15 substantive content preserved verbatim outside the NEW §26.8 sub-section) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.3 CP row bump v1.15 → v1.16; CP plan v2.20 → v2.21 (single-unit-body amendment at U-CP-NN hosting `attempt_resume`); harness-cp impl (`pause_resume_protocol_types.py` NEW ResumeContext + `pause_resume_protocol.py:295` signature widening); runtime spec v1.23 → v1.24 (NEW §14.8.2 step 4-bis durable-async branch authoring; consumes ResumeContext.hitl_response); runtime plan v2.22 → v2.23 (NEW L9-terdecies cluster U-RT-93/94/95); harness-runtime impl; tests |
| Downstream absorption owed (next arcs) | `ResumeContext` future-extensibility per (i) of "Adjacent defects surfaced" (separate operator-discretion arcs as fields are needed); per-pause-reason validity matrix per (ii) (runtime spec v1.24 or follow-on); D8 §18.3 → §18.1 cite-correction at runtime spec v1.24 (per scoping doc §0(D); CP spec §18.* untouched at v1.16) |
| Operator authority | AskUserQuestion 2026-05-24 ("Ratified") at session opening checkpoint `20260524-130230` item #1; ratified scoping doc Q3 (c-ii) FORCED recommendation |
| Contract-count change | None — `ResumeContext` is a sub-type within C-CP-26, not a new contract surface |
| Fail-class-count change | None |
| Signature change at any Protocol | ONE — `PauseResumeProtocol.attempt_resume(...)` gains `resume_context: ResumeContext \| None = None` keyword-only parameter with backward-compatible default; existing callers receive None unchanged |
| Field-set change at any field set | NEW field-set: `ResumeContext` typed Pydantic v2 BaseModel (frozen, single optional field `hitl_response: HITLResult \| None = None`) |
| Acceptance criterion change at any contract | None at spec-side (CP plan U-CP-NN absorption AC re-decomposition is downstream absorption per (b); runtime plan v2.23 L9-terdecies cluster authors new ACs at U-RT-93/94/95 per scoping doc §3.1) |
| Behavior change | None at spec-side method body (the parameter is ingested but not consumed at CP-side; runtime-side consumption authored at v1.24); ZERO behavior change at existing callers |
| Cross-axis cascade | ZERO at semantics layer — OD spec §C-OD-30.4 `PauseResumeAuditPayload` unaffected (composes from PauseEvent + ResumeOutcome, not from ResumeContext); CXA v2.10 unaffected; ADR/ADD/PRD unaffected |
| Skill discipline | `spec-writer` Phase-7 narrow-scope spec-amendment application of operator-ratified Q3 (c-ii) FORCED disposition; fidelity-pure additive amendment (one NEW carrier + one signature widening with backward-compatible default); NO contract change; NO extension beyond authorized scope (4 adjacent defects surfaced at change-note for follow-on arcs per FM-2); preservation audit PASSED |
| Date | 2026-05-24 |
