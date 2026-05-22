# Specification — Control Plane v1.11

## Change-note (v1.10 → v1.11)

**Scope of revision.** Path γ enum identifier rename absorption per `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` (operator-ratified 2026-05-21). The NEW C-CP-26 §26.2 Python enum identifier `PauseReason` (5-class workflow-layer pause taxonomy: EXPLICIT_OPERATOR / HITL_PENDING / VALIDATOR_ESCALATION / TIMEOUT_BOUNDARY / EXTERNAL_DEPENDENCY) renames to `WorkflowPauseReason` to disambiguate from the OLD C-CP-22 §22.1 Python enum identifier `PauseReason` (4-class engine-layer replay-pause taxonomy: HITL_INVOCATION_PENDING / CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE / OPERATOR_INITIATED_PAUSE / ENGINE_NATIVE_PAUSE; landed at U-CP-49 commit history; preserved verbatim at v1.10 §44 v1.9-substantive-content-preserved guarantee). Member values + cardinality + semantics of the NEW 5-class enum preserved verbatim — only the class identifier renames. v1.11 also adds a §22 ↔ §26 coexistence NOTE making the engine-layer vs workflow-layer distinction explicit (advisor-flagged drift risk per `[[spec-prose-plan-body-drift-pattern]]`).

**v1.10 substantive content preserved verbatim.** All v1.10 content outside the §26.2 enum-identifier rename + §26 coexistence-NOTE addition preserved unchanged. The v1.10 NEW §17.4 (`hitl_gate` signature) + §25 (C-CP-25 ValidatorFramework) + §27 (C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter) preserved verbatim. The v1.10 + v1.9 + v1.8 + ... + v1 chain all preserved. C-CP-01 through C-CP-24 preserved verbatim (the OLD §22 C-CP-22 `PauseReason` 4-class enum stays as-is).

**Source of fix.** Phase 7b implementation-arc fork detection per `phase-7-back-flow-routing` skill discipline:
- Pre-implementation carrier-surface inspection at U-CP-62 entry surfaced the `PauseReason` namespace collision (NEW C-CP-26 §26.2 vs OLD C-CP-22 §22.1).
- Operator ratification of path γ (rename NEW C-CP-26 enum) over alternatives α / β / δ per fork file.
- Path γ has ZERO landed-code blast radius — the U-CP-62 carrier file does not exist yet; absorption is entirely design-substrate.
- Advisor pass flagged: (i) `ExplicitPauseReason` semantically wrong for TIMEOUT_BOUNDARY + EXTERNAL_DEPENDENCY members (system-triggered, not "explicit"); operator-ratified `WorkflowPauseReason` (workflow-layer-vs-engine-layer split); (ii) §22 ↔ §26 coexistence relationship unspecified — operator-ratified inclusion of coexistence NOTE at v1.11.
- Co-published artifacts: OD spec v1.8 → v1.9 (§C-OD-30.1 attribute type citation); CP plan v2.16 → v2.17 (U-CP-62 carrier + U-CP-63/64 AC #4 strike); OD plan v2.14 → v2.15 (U-OD-51 enum citation); CXA v2.7 → v2.8 (spec-version citation bumps).

**One amendment site + one new NOTE.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§26.2 enum identifier rename** | The 5-class NEW C-CP-26 enum `PauseReason` declaration renames to `WorkflowPauseReason`. Member values (EXPLICIT_OPERATOR / HITL_PENDING / VALIDATOR_ESCALATION / TIMEOUT_BOUNDARY / EXTERNAL_DEPENDENCY) + member string values + cardinality (5) + semantics preserved verbatim. §26.1 `PauseSnapshot.pause_reason` field type annotation cites renamed identifier. §26.4 span attribute name `pause.reason` (lowercase dot-notation OTel attribute) unchanged (attribute-name-string-literal layer is independent of Python class-identifier layer). | Path γ operator ratification 2026-05-21 |
| **§26 NEW NOTE — §22 ↔ §26 coexistence** | Explicit statement that C-CP-22 (§22, engine-layer replay-pause protocol from U-CP-49) and C-CP-26 (§26, workflow-layer explicit-pause protocol introduced at v1.10) are **distinct coexisting protocols** at distinct architectural layers. The two protocols share neither the `PauseReason` identifier (v1.11 rename) nor the `PauseEvent` vs `PauseSnapshot` envelope (already-distinct identifiers). Free-function `capture_pause_snapshot` / `attempt_resume` at the OLD module level (U-CP-49 surface) and class-method `PauseResumeProtocol.capture_pause_snapshot` / `.attempt_resume` (NEW U-CP-63/64 surface) coexist at distinct lexical scopes within the same module `harness-cp/src/harness_cp/pause_resume_protocol.py`. **The OLD line-121 + line-143 NotImplementedError sites belong to the OLD §22 surface and are NOT closed by U-CP-63/64**; closure of those sites is a separate U-CP-49 implementation arc (not currently scoped). | Advisor-flagged drift risk; operator-ratified inclusion at v1.11 |

**Status posture.** Proposed (v1.10) → **Proposed (v1.11)**. v1.11 is a fidelity-bookkeeping patch — single-identifier rename at §26.2 + one cross-section coexistence NOTE addition. No v1.10 contract re-decomposition; no signature change; no acceptance criterion change; no new contract; no fail-class change.

**Downstream absorption owed (post-v1.11).**
(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.10 → v1.11).
(b) `Spec_Operational_Discipline_v1_9.md` (co-published this arc) — §C-OD-30.1 absorbs the renamed enum citation.
(c) `Implementation_Plan_Control_Plane_v2_17.md` (co-published this arc) — U-CP-62 carrier name renamed; U-CP-63/64 AC #4 line-121/143 closure STRUCK per §26 NEW NOTE (those lines are OLD §22 surface).
(d) `Implementation_Plan_Operational_Discipline_v2_15.md` (co-published this arc) — U-OD-51 enum citation renamed.
(e) `Cross_Axis_Composition_Document_v2_8.md` (co-published this arc) — §2.3.7 row 6 (C-CP-26 §26 producer) spec-version citation bump; the §2.3.7 row 8 cost-attribution audit-write seam **REMAINS OWED** (paired with U-CP-72 implementation per workspace CLAUDE.md §2.4 + handoff §6; v2.8 publishes for path γ rename absorption, NOT for cost-attribution).
(f) `harness-cp/CLAUDE.md` + `harness-od/CLAUDE.md` pointer rows (cluster file paths preserved verbatim; spec/plan version pointer bumps).

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** None — apply pass is fidelity-pure transcription of operator-ratified path γ + operator-ratified coexistence NOTE.

---

## §1 — §26.2 amendment (v1.11)

The v1.10 §26.2 declaration of the `PauseReason` 5-class enum is amended to rename the class identifier to `WorkflowPauseReason`. Members + cardinality + string values + semantics preserved verbatim.

### §26.2 renamed enum declaration (v1.11 amendment)

```python
# v1.11 amendment — class identifier renamed from PauseReason to WorkflowPauseReason
# to disambiguate from OLD §22.1 PauseReason 4-class engine-layer enum (U-CP-49 surface)
class WorkflowPauseReason(Enum):
    EXPLICIT_OPERATOR = "explicit_operator"
    HITL_PENDING = "hitl_pending"
    VALIDATOR_ESCALATION = "validator_escalation"
    TIMEOUT_BOUNDARY = "timeout_boundary"
    EXTERNAL_DEPENDENCY = "external_dependency"
```

### §26.1 cross-reference update (v1.11 amendment)

The v1.10 §26.1 `PauseSnapshot.pause_reason` field type annotation:

```python
@dataclass(frozen=True)
class PauseSnapshot:
    workflow_id: str
    run_id: str
    step_index: int
    pause_reason: WorkflowPauseReason                    # v1.11 amendment — was PauseReason at v1.10
    state_summary: StateSummary
    snapshot_hash: str
    created_at: int
    state_ledger_anchor: str
```

All other §26.2 field-set declarations (`PauseSnapshot`, `MaterialDiffPolicy`, `ResumeResult`) preserved verbatim from v1.10.

### §26.4 span attribute name preservation

The §26.4 span emission table is preserved verbatim. The OTel attribute name `pause.reason` (lowercase dot-notation string literal) is independent of the Python class identifier; only the type annotation that references the enum class updates per §26.1 above.

---

## §2 — §26 NEW NOTE — §22 ↔ §26 coexistence (v1.11)

The v1.10 §26.6 invariant 5 explicitly addresses coexistence with U-CP-56 prefix-replay-resumption. v1.11 adds an analogous NOTE making the §22 ↔ §26 coexistence relationship explicit:

> **NOTE (v1.11) — §22 ↔ §26 coexistence.** C-CP-22 (§22, "Pause and resume") declares the engine-layer replay-pause-anchored protocol introduced at v1 and landed at U-CP-49 — it carries the OLD `PauseReason` 4-class enum (`HITL_INVOCATION_PENDING` / `CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE` / `OPERATOR_INITIATED_PAUSE` / `ENGINE_NATIVE_PAUSE`), the `PauseEvent` Pydantic envelope, the `ResumeAttempt` / `ResumeOutcome` / `ResumeOutcomeKind` carriers, and the free-function `capture_pause_snapshot(workflow_id, pause_reason) -> PauseEvent` / `attempt_resume(attempt) -> ResumeOutcome` signatures. C-CP-26 (§26, "PauseResumeProtocol", NEW at v1.10) declares the workflow-layer explicit-pause + resume protocol — it carries the NEW `WorkflowPauseReason` 5-class enum (v1.11 renamed; was `PauseReason` at v1.10), the `PauseSnapshot` frozen-dataclass envelope, the `MaterialDiffPolicy` 3-class enum, the `ResumeResult` frozen-dataclass envelope, and class-method signatures on a `PauseResumeProtocol` class (`async capture_pause_snapshot(workflow_id, run_id, step_index, pause_reason) -> PauseSnapshot` / `async attempt_resume(snapshot, *, material_diff_policy) -> ResumeResult`). The two protocols are **distinct architectural primitives at distinct layers**: C-CP-22 anchors at engine-native pause + replay-resumption mechanics; C-CP-26 anchors at workflow-driver explicit-pause + material-diff resumption mechanics. They share neither Python class identifiers (post-v1.11) nor envelope types (already-distinct at v1.10). The OLD U-CP-49 free-function surface and the NEW C-CP-26 class-method surface coexist at distinct lexical scopes within the same Python module (`harness-cp/src/harness_cp/pause_resume_protocol.py`) — module-level free-function names and class-method names do not collide. The OLD `pause_resume_protocol.py:121` + `:143` `NotImplementedError` sites belong to the OLD §22 / U-CP-49 surface and are **NOT closed** by C-CP-26 / U-CP-63 / U-CP-64; closure of those sites is a separate implementation arc anchored at C-CP-22 / U-CP-49 (not currently scoped).

---

## §3 — Preservation guarantees

| Element | Disposition |
|---|---|
| All v1.10 contracts (C-CP-01 through C-CP-27) | Preserved verbatim outside §26.2 enum-identifier rename + §26 NEW NOTE addition |
| v1.10 §22 / C-CP-22 surface (OLD `PauseReason` 4-class, `PauseEvent`, `ResumeAttempt`, `ResumeOutcome`, `ResumeOutcomeKind`, free-function signatures) | Preserved verbatim (already preserved at v1.10 §44 v1.9-substantive-content-preserved guarantee; v1.11 makes the preservation operative-rather-than-incidental via the §26 NEW NOTE) |
| v1.10 §26.1 method signatures (class scope) | Preserved verbatim; only the `pause_reason` field type annotation cite at `PauseSnapshot` is updated |
| v1.10 §26.2 field-set declarations (`PauseSnapshot` 8 fields, `MaterialDiffPolicy` 3-class, `ResumeResult` 5 fields) | Preserved verbatim; only the `PauseReason` enum class identifier renames to `WorkflowPauseReason` |
| v1.10 §26.3 lifecycle stage placement | Preserved verbatim |
| v1.10 §26.4 span emission table (2 spans, 4 attributes each, attribute names lowercase dot-notation) | Preserved verbatim |
| v1.10 §26.5 failure-mode taxonomy (3 CP fail classes) | Preserved verbatim |
| v1.10 §26.6 invariants (5 invariants) | Preserved verbatim |
| v1.10 §26.7 deferred-to-implementation-discretion items | Preserved verbatim |
| All ADR commitments (F1–F5 + D1–D6) | Unchanged |
| Pattern-D inheritance table (v1.10 change-note) | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_11.md` |
| Version | v1.11 |
| Filing event | Path γ enum identifier rename absorption + §22 ↔ §26 coexistence NOTE addition, 2026-05-21 |
| Predecessor | `Spec_Control_Plane_v1_10.md` (v1.10 substantive content preserved verbatim outside §26.2 identifier rename + §26 NEW NOTE) |
| Co-published artifacts | OD spec v1.9; CP plan v2.17; OD plan v2.15; CXA v2.8; workspace CLAUDE.md + per-axis CLAUDE.md pointer bumps |
| Operator authority | `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` path γ ratification 2026-05-21 + `WorkflowPauseReason` naming ratification + coexistence-NOTE inclusion ratification |
| Contract-count change | None (27 → 27) |
| Fail-class-count change | None |
| Skill discipline | `phase-7-back-flow-routing` Class 1 fork detection + `phase-7-implementation` carrier-surface inspection (`[[carrier-surface-inspection-catches-namespace-collision]]` pattern applied at U-CP-62 entry) + advisor pre-execution pass |
| Date | 2026-05-21 |
