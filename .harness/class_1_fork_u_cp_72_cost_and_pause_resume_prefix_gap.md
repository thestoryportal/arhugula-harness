# Class 1 Fork — U-CP-72 cost + pause/resume prefix gap

**Filed:** 2026-05-22 at 10-CP-D cluster open (during `phase-7-implementation` skill §3.4 dependency-verification step for U-CP-72).

**Status:** ✅ ALL-RESIDUALS-CLOSED-OR-WONT-FIX per §11 (status-line refreshed 2026-05-27) — cost-axis Sub-arc B FULLY CLOSED 2026-05-24 (8-commit chain across CXA v2.9 §2.3.7 row 8 + OD spec v1.10 NEW §C-OD-26.6 + OD plan v2.17 U-OD-41 + impl + bucket-count refresh + step_execution_context workflow_id 5-commit arc); pause/resume Sub-arc A LANDED `5d6051d` + helper-contract authoring 3-commit arc 2026-05-24 (OD spec v1.11 NEW §C-OD-30.4 + OD plan v2.18 U-OD-51 + impl with 59 tests PASS) + production-wiring LANDED at batch-18 H_T-CP-22 RETIRED `671f195`; workflow-layer audit-write CLOSED-as-WON'T-FIX `1b7bcb0` (recovery path preserved at §11 if concrete consumer surfaces). Species 3 stale-carry per workflow v1.9 §7.4.7.2.

_Original filing footer:_ **Status:** OPEN (partial-land planned per `[[halt-route-split-AC-pattern]]` memory; 6 of 8 prefix branches materializable; 2 cross-axis-blocked).

**Trigger.** Implementation_Plan_Control_Plane_v2_15.md U-CP-72 AC #1 mandates routing for 8 action_id prefixes (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:`+`resume:` / `mcp_trust:` / `cost:`). AC #2 mandates each branch produces a correct AuditPayload subclass per OD spec.

Empirical inventory of AuditPayload subclasses at HEAD `5d67959`:

| Prefix | Required AuditPayload subclass | Status at HEAD |
|---|---|---|
| `dispatch:` | base `AuditPayload` (via `CPAuditLedgerEntry`) | landed |
| `hitl:` | base `AuditPayload` (via `CPAuditLedgerEntry`) | landed |
| `hitl_webhook:` | `WebhookDeliveryAuditPayload` | landed (U-OD-53, commit `0aed0ac`) |
| `operator_burden:` | `OperatorBurdenAuditPayload` | landed (U-OD-54, commit `128ab4f`) |
| `validator:` | `ValidatorEscalationAuditPayload` | landed (U-OD-50) |
| `mcp_trust:` | `TrustEvaluationAuditPayload` | landed (U-OD-52) |
| `pause:` / `resume:` | `PauseResumeAuditPayload` | **MISSING** — owed to U-OD-51 (cross-axis-blocked on U-CP-62 per OD plan v2.15 §1) |
| `cost:` | `CostRecordAuditPayload` | **MISSING** — owed to CXA v2.9 amendment (§2.3.7 row 8); paired with U-OD-41 producer per OD plan v2.14 §1 U-OD-41 AC #3 |

## §1 Decision class

**Class 1 — halt-route-split-AC.** Per workspace memory `[[halt-route-split-AC-pattern]]`: when a unit's AC bundles a materializable + unmaterializable surface, partial-land + strike the bad AC + file Class 1 fork.

## §2 Authority chain for the 2 missing surfaces

### §2.1 `pause:` / `resume:` — PauseResumeAuditPayload

- **Producer-side schema:** OD spec v1.9 §C-OD-30.1 + §C-OD-30.2 (8-attribute Pattern-P1 alignment with CP spec v1.11 §26.4 `WorkflowPauseReason` enum).
- **Producer unit:** U-OD-51 (OD plan v2.15) — pause/resume schema + PauseResumeAuditPayload dataclass.
- **Blocking dependency:** U-OD-51 cross-axis-blocked on U-CP-62 (CP plan v2.17 §1 — `WorkflowPauseReason` 5-class workflow-layer pause taxonomy materialization).
- **Routing target:** U-OD-51 + U-CP-62 implementation arc (separate from this 10-CP-D arc).

### §2.2 `cost:` — CostRecordAuditPayload

- **Producer-side schema:** owed to CXA v2.9 amendment per workspace `CLAUDE.md` §2.4 CXA row footer + handoff §6.
- **CXA amendment owed:** §2.3.7 row 8 (cost-attribution audit-write seam) per Implementation_Plan_Control_Plane_v2_15.md U-CP-72 cross-arc note: "AC #1 expansion from 7 → 8 prefixes requires CXA v2.6 → v2.7 amendment to add an §2.3.7 row 8 entry for cost-attribution audit-write seam."
- **Producer unit:** U-OD-41 (OD plan v2.14) — `_project_cost_record_to_audit_entry(attached: SpanCostRecord) -> CPAuditLedgerEntry`; current signature projects to `CPAuditLedgerEntry` (existing type), NOT a `CostRecordAuditPayload`. The producer-side spec contract for the new AuditPayload subclass is not yet authored.
- **Routing target:** CXA v2.9 amendment (canonicalizes the cost-attribution seam) + OD plan revision (CostRecordAuditPayload authoring) + U-OD-41 implementation arc.

## §3 Partial-land scope (this arc)

**U-CP-72 will land 6 of 8 prefix branches** in the `cp_audit_to_od_audit` converter:

1. `dispatch:` (via CPAuditLedgerEntry — preserved existing path)
2. `hitl:` (via CPAuditLedgerEntry — preserved existing path)
3. `hitl_webhook:` → `WebhookDeliveryAuditPayload`
4. `operator_burden:` → `OperatorBurdenAuditPayload`
5. `validator:` → `ValidatorEscalationAuditPayload`
6. `mcp_trust:` → `TrustEvaluationAuditPayload`

**Struck from this arc** (re-binding criterion explicit):

| Struck branch | Re-binding criterion |
|---|---|
| `pause:` / `resume:` → `PauseResumeAuditPayload` | U-OD-51 lands (waits on U-CP-62 per OD plan v2.15 §1 + checkpoint #4) |
| `cost:` → `CostRecordAuditPayload` | CXA v2.9 amendment authored + CostRecordAuditPayload subclass landed at OD package |

AC #1 modified at landing: `8 prefixes` → `6 prefixes`. AC #5 modified at landing: `8 producer events → 8 distinct AuditPayload subclasses` → `6 producer events → 6 distinct AuditPayload subclasses + base CPAuditLedgerEntry`.

## §4 Cross-axis impact

ZERO new cross-axis edges introduced by this fork resolution. The 6 landable branches consume existing producer-side AuditPayload subclasses (CP→CXA reverse-direction package imports already declared at CXA package per `harness-cxa/src/harness_cxa/cp_audit_conversion.py`). The 2 struck branches retain their original cross-axis dependency declarations at the plan body for future re-binding.

## §5 Non-amendment to U-CP-72 plan body at this arc

Per `[[halt-route-split-AC-pattern]]` discipline, the plan-body AC strikes are recorded at the landing commit message (commit body documents the strike + re-binding criterion); a CP plan v2.17 → v2.18 amendment is NOT owed at this arc (the strikes are bounded carry-forward, not contract changes). Future re-binding at the missing-subclass-landing arcs will un-strike via planner revision-pass naturally.

## §6 Adjacent finding — U-OD-41 signature precedes CostRecordAuditPayload authoring

OD plan v2.14 §1 U-OD-41 signature `_project_cost_record_to_audit_entry(attached: SpanCostRecord) -> CPAuditLedgerEntry` projects to the EXISTING `CPAuditLedgerEntry` type, not to a `CostRecordAuditPayload`. This is consistent with U-OD-41 AC #3 (`Routes via cp_audit_to_od_audit converter (action_id prefix cost: added per U-CP-72 extension — note: covered by cost: discriminator as the 8th pattern; reviewer to confirm bucket sizing or extend U-CP-72)`). The "reviewer to confirm" clause acknowledges the spec-level ambiguity; the CXA v2.9 amendment + OD plan revision authoring `CostRecordAuditPayload` is the canonical resolution path. Logged here for cross-reference at the CXA v2.9 amendment arc.

## §7 Filing footer

| Field | Value |
|---|---|
| Filed | 2026-05-22 |
| Filing arc | 10-CP-D cluster impl (U-CP-71 + U-CP-72 pair) |
| Filing skill | `phase-7-implementation` §3.4 dependency-verification |
| Resolution arc(s) | (a) U-OD-51 unblock at U-CP-62 landing; (b) CXA v2.9 amendment + CostRecordAuditPayload authoring |
| Status | OPEN at filing → PARTIAL-RESOLVED at U-CP-72 6-branch landing → **partially-advanced-Sub-arc-A (2026-05-23, OD plan v2.16)** → FULLY-RESOLVED at re-binding arcs |
| Related memory | `[[halt-route-split-AC-pattern]]`, `[[carried-fork-audit-before-cluster]]` |

---

## §8 Sub-arc A partial-advance footer (2026-05-23)

**Trigger.** U-CP-62 (`WorkflowPauseReason` + `MaterialDiffPolicy` + `PauseSnapshot` + `ResumeResult` carriers) landed at commit `49617e7` (cluster 10-CP-B impl arc commit 1/4, 2026-05-22) per CP plan v2.17 §1. Cross-axis prerequisite at §2.1 routing target (a) ("U-OD-51 cross-axis-blocked on U-CP-62 (CP plan v2.17 §1)") thereby satisfied.

**Sub-arc A scope (operator-ratified at AskUserQuestion 2026-05-23 — "Sub-arc scope" = A only).** OD plan v2.15 → v2.16 single-clause amendment lifting the cross-axis-block status-claim at §0 (c) clause. U-OD-51 transitions from cross-axis-blocked → implementation-ready at plan layer. Plan-body Depends-on relation `[U-CP-62 (cross-axis: CP)]` preserved verbatim (the DAG dependency itself remains canonical regardless of upstream landed-vs-bounded state; what lifts is the §0 status-block orchestration-time block-claim). No AC change, no signature change, no spec change.

**Artifact landed.** `design-substrate/Implementation_Plan_Operational_Discipline_v2_16.md` — 1 amendment site (§0 (c) clause single-clause delta); 4 downstream absorption pointers (workspace CLAUDE.md + harness-od CLAUDE.md preservation + Phase 7b cluster-open authorization for U-OD-51 + Sub-arc B carry-forward).

**Remaining Sub-arc A landing event.** U-OD-51 implementation arc at next `phase-7-implementation` skill activation against OD plan v2.16. Carrier: `PauseResumeAuditPayload` dataclass extending `AuditPayload` with 8 pause/resume-specific fields per OD spec v1.9 §C-OD-30.2 + Pattern-P1 byte-exact alignment with CP spec v1.11 §26.4 (U-CP-65 producer-side). Implementation arc landing additionally enables U-CP-72 `pause:` + `resume:` branch un-STRIKE at `cp_audit_to_od_audit` converter (per fork §3 partial-land table) — would advance H_T-CP-22 PARTIAL → RETIRE-READY at the workflow_driver pause-event invocation level (per batch-11 §5 H_T-CP-22 gate).

**Sub-arc B status (unchanged).** CostRecordAuditPayload authoring at OD spec + CXA v2.9 amendment + U-OD-41 signature revision remain owed per §2.2. Operator preference (i) revise-U-OD-41-signature noted at AskUserQuestion 2026-05-23 — when Sub-arc B opens, U-OD-41 signature `_project_cost_record_to_audit_entry(attached: SpanCostRecord) -> CPAuditLedgerEntry` revises to return `CostRecordAuditPayload`; no new dedicated AuditPayload-author unit. Recorded for Sub-arc B opening arc per fork §6 ambiguity resolution.

**Status post-§8.** OPEN → PARTIAL-RESOLVED → **partially-advanced-Sub-arc-A** (cross-axis-block lift at plan layer absorbed; Sub-arc A implementation landing pending; Sub-arc B carry-forward intact). The fork remains OPEN as a multi-arc cascade tracker; FULLY-RESOLVED routes at Sub-arc A implementation + Sub-arc B full authoring + landing.

---

## §9 Sub-arc A implementation landing footer (2026-05-23, retroactively documented 2026-05-24)

**Trigger.** Sub-arc A implementation arc opened + landed in a single commit `5d6051d` (`feat(U-OD-51 Sub-arc A landing): C-OD-30 pause/resume canonical namespace + PauseResumeAuditPayload + U-CP-72 converter pause:/resume: branch un-STRIKE`) on 2026-05-23 against OD plan v2.16. The earlier §8 footer (filed same session at the plan-layer cross-axis-block lift) anticipated the implementation arc as a separate event; in practice it landed same session and was not retroactively recorded in this fork doc until 2026-05-24.

**Artifacts landed at `5d6051d`.**

| Surface | Artifact | Verification at HEAD `1c1a296` |
|---|---|---|
| Schema | `harness-od/src/harness_od/pause_resume_namespace.py` — `PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA` (8 attrs across 2 span sites per §C-OD-30.1) | `harness-od/tests/test_pause_resume_namespace.py` — **27/27 PASS** |
| AuditPayload | `harness-od/src/harness_od/pause_resume_namespace.py` — `PauseResumeAuditPayload` (4 `audit_cp_*` common + 8 pause/resume-specific fields per §C-OD-30.2) | covered by namespace tests + converter tests |
| Converter branch | `harness-cxa/src/harness_cxa/cp_audit_conversion.py:289-299` — `PauseResumeAuditPayload` isinstance branch routing to `audit.pause_resume.*` sub-namespace via `PAUSE_RESUME_AUDIT_NAMESPACE_PREFIX` | `harness-cxa/tests/test_u_cp_72_converter_6_prefix_extension.py` — **16/16 PASS** (includes `test_pause_carrier_projects_to_audit_pause_resume_subnamespace` + `test_resume_carrier_projects_to_audit_pause_resume_subnamespace` + `test_pause_resume_branch_signature_attrs_present` + 5-prefix expectation set including `pause_resume`) |
| Carrier union | `CpAuditCarrier` union at `cp_audit_conversion.py:96-104` — `PauseResumeAuditPayload` member added (post-Sub-arc-A 7-prefix coverage; subsequently 8-prefix at Sub-arc B 2026-05-24 closure) | covered by converter union tests |

**U-CP-72 plan-body un-STRIKE state.** Per `[[halt-route-split-AC-pattern]]` discipline + fork §5, the converter pause/resume branch un-STRIKE is recorded at the landing commit body; no CP plan v2.17 → v2.18 amendment is owed for this scope at the time of Sub-arc A landing. (The CP plan v2.17 → v2.18 amendment that did land 2026-05-24 was scoped to U-CP-56 9th-field absorption per `[[fork-step-execution-context-workflow-id-field-absence]]`, an unrelated cost-axis arc.)

**Residual after Sub-arc A landing.** Binding-chain stages 1 (schema) + 2 (converter dispatch) are empirically green per the test counts above. **Binding-chain stage 3 (production caller)** per `[[verification-shape-sharpened-grep-vs-e2e]]` remains UNMET: as of HEAD `1c1a296`, `grep -rn "PauseResumeAuditPayload(" harness-{cp,runtime,cxa,od}` returns only test-fixture constructors (`harness-cxa/tests/test_u_cp_72_converter_6_prefix_extension.py:247` + `:264`). No production callsite at `harness-cp/src/harness_cp/material_diff_detection.py:161` (`PauseEvent` parameter site) or at any `PauseResumeProtocol` emitter constructs the typed carrier and routes it through `cp_audit_to_od_audit` + `audit_writer.append`.

**Structural parallel to cost-axis Sub-arc B.** The production-wiring gap mirrors the gap that existed at cost-axis Sub-arc A→B boundary before the 2026-05-24 closure arc. Cost-axis closure required: (a) OD spec v1.10 NEW §C-OD-26.6 production-caller contract authoring (typed `CostRecordAuditPayload` projection signature); (b) OD plan v2.17 U-OD-41 AC re-decomposition (5 → 9 ACs); (c) CXA v2.9 §2.3.7 row 8 amendment; (d) `[[fork-step-execution-context-workflow-id-field-absence]]` 5-commit Class 1 fork arc widening `StepExecutionContext` to 9 fields; (e) production callsite migration at `harness-runtime/.../cost_attribution_llm_dispatch.py`. **No equivalent spec / plan / CXA chain currently exists for pause/resume production-wiring.** U-OD-51's ACs are schema/carrier-only (5/5 met at `5d6051d`); no AC mandates production caller construction. Opening production-wiring without spec/plan back-flow ratification = X-AL-3 silent design extension per workspace `CLAUDE.md` §4.4.

**Routing target for production-wiring residual.** Operator-decision arc — deferred per AskUserQuestion 2026-05-24 (operator selected "doc-only reconciliation, then move on"). If/when opened, the back-flow shape mirrors cost-axis Sub-arc B: (1) OD spec NEW §C-OD-NN authoring a production-caller contract for pause/resume audit-write (helper signature + callsite location per CP `PauseResumeProtocol` emission lifecycle); (2) OD plan NEW unit U-OD-NN authoring the helper + production callsite migration; (3) impl arc materializing both. Estimated ~5-10 commits including spec/plan/impl. Not opened at this arc.

**Status post-§9.** OPEN → PARTIAL-RESOLVED → partially-advanced-Sub-arc-A → **Sub-arc-A-FULLY-LANDED (carrier + converter + tests; production-wiring gap deferred to operator-decision back-flow arc)** → Sub-arc-B-FULLY-CLOSED (cost-axis 2026-05-24 per existing §6 + impl arc). The fork's cost-axis residual is FULLY-CLOSED (production callsite landed at `e3fd675`). The fork's pause/resume residual now mirrors what cost-axis looked like at Sub-arc A landing pre-2026-05-24: typed carrier + converter dispatch operational; production-callsite migration deferred. Pattern reinforces `[[verification-shape-sharpened-grep-vs-e2e]]` discipline — schema + dispatch green at unit tests does not entail production-wiring operational.

**Memory updates this arc.**

- MEMORY.md `[[fork-u-cp-72]]` index entry updated to mark Sub-arc A FULLY-LANDED at `5d6051d` (was previously "Sub-arc A advanced at plan layer; U-OD-51 ready-to-implement; U-CP-72 minor revision … owed at separate arc"). Cost-axis closure language preserved verbatim from 2026-05-24 update.

---

## §10 Pause/resume Sub-arc helper-contract authoring landing footer (2026-05-24, narrow-scope ratification)

**Trigger.** Pause/resume residual production-wiring gap surfaced at §9 (Sub-arc A FULLY-LANDED at `5d6051d` 2026-05-23; production-callsite migration deferred at fork doc §9 to operator-decision back-flow arc; arc opened 2026-05-24 per operator selection on the remaining-work menu surfaced at `/checkpoint resume`). Cost-axis Sub-arc B FULLY-CLOSED 2026-05-24 (§9 prior footer) freed advisor + operator attention for the pause/resume residual.

**Operator decision (AskUserQuestion 2026-05-24).** Operator selected scope = "Narrow — OD-side helper only" from a 3-option menu (Narrow / Joint / Stay-deferred). Narrow-scope ratification: author the OD-side production-invocation contract + helper without authoring production-callsite construction. Reverses fork §9 doc-only deferral. Honest framing accepted by operator: helper lands as DEAD CODE until CP composer authoring arc lands (gates H_T-CP-22 PARTIAL → RETIRE-READY per `harness-cp/CLAUDE.md` §4.1).

**Structural asymmetry from cost-axis Sub-arc B framed explicitly.** Cost-axis Sub-arc B widened an EXISTING production callsite (`cost_attribution_llm_dispatch.py:198-202`, operational since U-OD-38). Pause/resume has NO production callsite at landing — `capture_pause_snapshot` + `attempt_resume` at `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147` are `NotImplementedError` stubs; `workflow_driver.py` does not invoke `PauseResumeProtocol`. Per advisor pre-flight + operator confirmation: cost-axis precedent did not map cleanly; narrow scope is the honest framing.

**Artifacts landed (3-commit arc).**

| # | Commit | Artifact | Verification |
|---|---|---|---|
| 1 | `ba85a1e` | `Spec_Operational_Discipline_v1_11.md` — NEW §C-OD-30.4 production-invocation contract (262 insertions) | Spec preserves v1.10 + v1.9 + v1.8 chain verbatim outside the NEW §C-OD-30.4 sub-section |
| 2 | `24ffbd9` | `Implementation_Plan_Operational_Discipline_v2_18.md` — U-OD-51 AC re-decomposition 5→10 ACs (111 insertions) | Plan preserves v2.17 + v2.16 + ... + v2.14 chain verbatim outside the single-unit-body amendment at U-OD-51; ACs #1-#5 preserved byte-exact |
| 3 | `10129c8` | `harness-od/src/harness_od/pause_resume_namespace.py` EXTEND + `harness-od/tests/test_pause_resume_audit_helpers.py` NEW (619 insertions / 2 files) | 16/16 new helper tests PASS + 27/27 Sub-arc A tests preserved + 16/16 converter tests preserved = 59/59 PASS; pyright strict 0 errors / 0 warnings |

**Helper signatures landed.**

```python
def _project_pause_event_to_audit_payload(
    event: PauseEvent,
    *,
    workflow_id: str,
    step_index: int,
    snapshot_hash: str,
    state_ledger_anchor: str,
    prior_event_hash: str,
    timestamp: str = "",
) -> PauseResumeAuditPayload: ...


def _project_resume_outcome_to_audit_payload(
    attempt: ResumeAttempt,
    outcome: ResumeOutcome,
    *,
    step_index: int,
    snapshot_hash: str,
    diff_summary_hash: str | None,
    prior_event_hash: str,
    timestamp: str = "",
) -> PauseResumeAuditPayload: ...
```

**Composition discipline encoded.**

- `audit_cp_action_id` patterns: `pause:<workflow_id>:<step_index>` / `resume:<workflow_id>:<step_index>` per §C-OD-30.2 + CXA v2.9 §0.3 8-prefix discriminator.
- `audit_cp_response` constants: pause helper hard-codes `"paused"`; resume helper switches per `ResumeOutcomeKind` (RESUME_CLEAN / RESUME_AFTER_REVALIDATION → `"resumed"`; ABORT_REVALIDATION_FAILED / ABORT_SNAPSHOT_CORRUPTED → `"diff_detected"`).
- Path-disjoint field nullification: pause helper sets resume-path fields to `None`; resume helper sets pause-path fields to `None` (enforced at helper body explicitly).
- `diff_policy` source: inlined `None` for `RESUME_CLEAN`; outcome-kind value as stand-in for non-clean outcomes per §C-OD-30.4.1 step 9 implementer-discretion deferral. Future arc MAY widen resume helper signature to accept `diff_policy` as explicit kwarg.

**Adjacent defects surfaced (not patched per FM-2).**

(i) `PauseResumeProtocol` body stubs at `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147` remain `NotImplementedError`. CP-axis scope; not addressed at this arc.

(ii) `step_index`-vs-`step_action_id` divergence with cost-axis. Cost-axis uses `cost:<workflow_id>:<step_action_id>`; pause/resume uses `pause:<workflow_id>:<step_index>` / `resume:<workflow_id>:<step_index>` per §C-OD-30.2 comment-line empirical convention. Preserved at v1.11; reconciliation candidate at future arc if CP composer arc surfaces a preferred pattern.

(iii) Cross-axis import precedent. `harness-od/src/harness_od/pause_resume_namespace.py` imports `PauseEvent` / `ResumeAttempt` / `ResumeOutcome` / `ResumeOutcomeKind` from `harness_cp.pause_resume_protocol`. Matches existing precedent at `idempotency_join_dedup.py:40` (`from harness_cp.engine_namespace import ReplayDisposition`). `harness-od/pyproject.toml` does not declare `harness-cp` as a dep; import works via uv workspace shared site-packages. Pre-existing layering inconsistency (`harness-od/CLAUDE.md` §1.1 claims "0 outbound cross-axis edges to other axes"); not addressed at this arc (would require Class 3 routing).

(iv) `PauseResumeProtocol` composer-binding invocation surface enumeration not yet committed. No spec section enumerates exactly which CP composer events trigger `_project_pause_event_to_audit_payload` vs `_project_resume_outcome_to_audit_payload`. Surfaced at §C-OD-30.4 change-note (iv); deferred to CP composer authoring arc.

**Cross-axis cascade.** ZERO at this arc. CXA v2.9 §0.3 already covers `pause:` + `resume:` discriminators per v2.6 7-row composer-arc absorption. No CXA amendment owed. No new fail class committed. No cross-axis edge added.

**Routing target for production-wiring residual (post-§10).** Remains operator-decision arc per fork §9 routing target. The CP composer authoring arc — `PauseResumeProtocol` body authoring + workflow_driver pause-event handler invoking PauseResumeProtocol + composition site invoking the §C-OD-30.4 helpers + F2 state-ledger entry anchoring + IS bounded-read for snapshot retrieval at resume boundary — is the unblock path. Estimated 15-25 commits, multi-axis (CP + runtime + possibly OD spec for `diff_policy` kwarg widening), likely multi-session. Advances H_T-CP-22 PARTIAL → RETIRE-READY.

**Status post-§10.** OPEN → PARTIAL-RESOLVED → partially-advanced-Sub-arc-A → Sub-arc-A-FULLY-LANDED → Sub-arc-B-FULLY-CLOSED (cost-axis) → **Pause/resume-helper-contract-FULLY-LANDED (narrow scope per operator 2026-05-24)**. The fork's pause/resume residual is now: typed carrier (Sub-arc A `5d6051d`) + converter dispatch (Sub-arc A `5d6051d`) + canonical production-invocation contract + helpers (this arc, 3 commits). Production callsite construction remains UNMET — gates on operator-decision CP composer authoring arc per X-AL-3 silent-extension foreclosure.

**Memory updates this arc.**

- MEMORY.md `[[fork-u-cp-72]]` index entry updated to reflect pause/resume Sub-arc helper-contract landing (status posture: helper landed as dead code; production-wiring residual remains; CP composer authoring arc is the unblock path).

## §11 Workflow-layer audit-write residual closure as WON'T-FIX (2026-05-24, narrow-scope ratification)

**Trigger.** Workflow-layer audit-write residual surfaced at runtime spec v1.21 change-note (d) (line 26 — "OD spec v1.11 unchanged at v1.21 — the §C-OD-30.4 audit-write helpers consume engine-layer §22.1 carriers; workflow-layer audit-write requires a separate OD spec extension (out of v1.21 scope)") + carried at fork §10 routing-target prose (the CP composer authoring arc shipped at narrow-scope driver-invocation-only — H_T-CP-22 PARTIAL → RETIRED at batch-18 — without authoring workflow-layer audit emission at `capture_pause_snapshot` / `attempt_resume` callsites in `workflow_driver.py`). Arc opened 2026-05-24 per operator selection on the remaining-work menu surfaced at `/checkpoint resume`.

**Operator decision (AskUserQuestion 2026-05-24).** Operator selected scope = "Stay-deferred / won't-fix at this scope" from a 3-option menu (Stay-deferred / Identify-consumer-first / Open-full-arc). The residual is closed-as-won't-fix at this arc, recoverable if a concrete downstream consumer surfaces.

**Pre-decision orientation (advisor-driven).** Per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` discipline (10th application this project), advisor surfaced three discriminating questions before any spec extension authoring:

(1) **Concrete consumer.** None named. H_T-CP-22 already RETIRED at batch-18 — no retirement gate. No failing test cites missing workflow-layer pause audit emission. No compliance shape cites workflow-layer pause audit consumption. Audit-completeness-as-architectural-principle is FM-2-suspect (speculative authoring against an unnamed consumer).

(2) **Projection collapse — does NOT hold cleanly.** Per CP spec v1.11 §26 NEW NOTE (line 21 — added at Path γ enum identifier rename absorption pass): the two protocols are **distinct architectural primitives at distinct layers**. They share neither Python class identifiers (post-v1.11 `WorkflowPauseReason` rename), nor envelope types (`PauseEvent` vs `PauseSnapshot` are already-distinct identifiers at v1.10), nor method-surface shapes (free-function vs class-method). Specifically:

| Surface | Engine-layer (§22 / C-CP-22 / U-CP-49) | Workflow-layer (§26 / C-CP-26 / U-CP-62-65) |
|---|---|---|
| Pause reason enum | `PauseReason` 4-class (`HITL_INVOCATION_PENDING` / `CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE` / `OPERATOR_INITIATED_PAUSE` / `ENGINE_NATIVE_PAUSE`) | `WorkflowPauseReason` 5-class (`EXPLICIT_OPERATOR` / `HITL_PENDING` / `VALIDATOR_ESCALATION` / `TIMEOUT_BOUNDARY` / `EXTERNAL_DEPENDENCY`) |
| Pause envelope | `PauseEvent` Pydantic envelope | `PauseSnapshot` 8-field frozen dataclass |
| Resume envelope | `ResumeAttempt` + `ResumeOutcome` + `ResumeOutcomeKind` | `ResumeResult` 5-field frozen dataclass + `MaterialDiffPolicy` 3-class enum |
| Method surface | Free-function at module-level | `PauseResumeProtocol` class-method (async) |

A projection from `PauseSnapshot` → `PauseEvent` at the audit-write boundary would be **lossy + audit-misleading**: 3 of the 5 `WorkflowPauseReason` members (`VALIDATOR_ESCALATION` / `TIMEOUT_BOUNDARY` / `EXTERNAL_DEPENDENCY`) have NO engine-layer analogue. The audit ledger would emit `pause.reason = "<engine-mappable-only>"` for all workflow-layer pauses, discarding the workflow-layer enum richness. The existing `_project_pause_event_to_audit_payload` / `_project_resume_outcome_to_audit_payload` helpers at OD spec v1.11 §C-OD-30.4 **cannot be reused without spec extension** authoring parallel workflow-layer-typed helpers.

(3) **CXA P1 allowlist pre-existing red gate.** Pre-existing failure carried at the workspace per the checkpoint remaining-work item #8. Opening an arc on a red-test gate would invert the `[[verification-shape-sharpened-grep-vs-e2e]]` discipline catalogued at batch-16/17 §4. Disjointness from this arc's test surface unverified.

**Rationale for won't-fix.** With (1) no concrete consumer + (2) lossy projection foreclosing zero-spec-extension reuse + (3) pre-existing red gate, opening a 6-9 commit multi-axis spec/plan/impl arc would be:

- Authoring against an architectural principle (audit-completeness) rather than a named consumer surface → FM-2 violation pattern (no-extension discipline applies to spec extensions authored ahead of consumer demand)
- Adding ~6-9 commits of code-and-test surface area against a feature surface (workflow-layer pause/resume) that itself emerged from the narrow-scope CP composer arc at H_T-CP-22 RETIRE-READY → RETIRED close — i.e., the entire workflow-layer surface is operational against operator-supplied `PauseResumeProtocol` instances (binding-chain MET; e2e exercises the protocol method invocations). Audit emission would add observability but not unblock any retirement gate or failing test.
- Pre-existing CXA P1 red gate makes a "tests green" claim suspect at landing-arc verification.

**Recovery path if a concrete consumer surfaces.** If a downstream consumer is named later (compliance query naming workflow-layer pause reasons; OTel collector schema requiring `pause.reason` mapped to `WorkflowPauseReason` member strings; integration test exercising workflow_driver pause emission against an audit-ledger reader fixture), this fork can be reopened. The arc shape is preserved here for future reference:

| Surface | OD spec v1.11 → v1.12 NEW §C-OD-30.5 (workflow-layer projection helpers) |
|---|---|
| Helper 1 | `_project_pause_snapshot_to_audit_payload(snapshot: PauseSnapshot, *, prior_event_hash: str, timestamp: str = "") -> WorkflowPauseResumeAuditPayload` |
| Helper 2 | `_project_resume_result_to_audit_payload(result: ResumeResult, *, snapshot_hash: str, prior_event_hash: str, timestamp: str = "") -> WorkflowPauseResumeAuditPayload` |
| Carrier | NEW `WorkflowPauseResumeAuditPayload` typed Pydantic v2 BaseModel (cannot reuse existing `PauseResumeAuditPayload` per (2)) |
| Action-id pattern | `pause-workflow:<workflow_id>:<step_index>` / `resume-workflow:<workflow_id>:<step_index>` (workflow-layer carriers carry `workflow_id` + `step_index` directly per `PauseSnapshot` 8-field shape; distinct prefix discriminator from engine-layer `pause:` / `resume:` per CXA v2.9 §0.3 8-prefix slot — a 9th + 10th prefix slot would be owed at the CXA edge extension) |
| CXA cascade | NEW row at §2.3.7 (CP→OD bucket) for workflow-layer audit-write seam OR extension of the existing pause/resume rows to include workflow-layer-typed payload variant |
| CP composer site | NEW emission at `workflow_driver.py` pause-trigger detection branch + resume-on-snapshot-context entry-point branch; F2 state-ledger entry anchoring per the existing 8a/8b/8c/8d pattern (compose → state-ledger write → converter → audit-write) |

Estimated 6-9 commits, multi-axis (OD spec + OD plan + impl + CP composer site + tests + CXA amendment).

**Adjacent defects surfaced (not patched per FM-2).**

(i) `harness-cp/CLAUDE.md` line 170 row text "workflow-layer audit-write residual remains OPEN per spec §14.14 change-note (d) for follow-on operator-discretion arc" should ideally update to "CLOSED-as-WON'T-FIX per fork §11 2026-05-24" — but this is a pointer-update at the per-axis CLAUDE.md status row, not a spec amendment. Pre-existing convention treats per-axis CLAUDE.md rows as bookkeeping that may evolve as residuals close; patching this row is scope-appropriate at this closure arc (handled below).

(ii) Runtime spec v1.21 change-note (d) prose at line 26 still says "workflow-layer audit-write requires a separate OD spec extension (out of v1.21 scope)" — the prose is technically accurate (a separate extension IS required IF the arc opens) but does not record the won't-fix closure. NOT patched per FM-2 no-spec-amendment discipline (the spec records a deferred-arc routing target; the routing-target now resolves to won't-fix at this fork §11; the spec does not need to absorb the routing resolution).

(iii) Workspace CLAUDE.md root §1.1 H_T-CP-22 row (if present) — not pointer-bumped to reference fork §11 closure. NOT patched per FM-2 (workspace CLAUDE.md root is canonical per §9.1 filing footer; pointer bumps to fork-doc residuals belong at design-phase back-flow, not at fork-doc closure).

**Cross-axis cascade.** ZERO at this arc. No spec amendment; no CXA amendment; no plan revision; no impl commit; no new test surface. Pure fork-doc bookkeeping closure.

**Status post-§11.** Pause/resume-helper-contract-FULLY-LANDED + production-wiring-RETIRED-at-batch-18 + **workflow-layer-audit-write-CLOSED-as-WON'T-FIX (this arc, 2026-05-24)**. The fork's pause/resume residual is now: typed engine-layer carrier (Sub-arc A `5d6051d`) + converter dispatch (Sub-arc A `5d6051d`) + canonical production-invocation contract + engine-layer helpers (§10 arc, 3 commits) + production callsite via CP composer narrow-scope arc (batch-18 H_T-CP-22 RETIRED) + workflow-layer audit-write closed-as-won't-fix per (1)+(2)+(3) above. Recovery path preserved if a concrete consumer surfaces.

**Memory updates this arc.**

- MEMORY.md `[[fork-u-cp-72]]` index entry to reflect workflow-layer audit-write won't-fix closure (recovery path preserved).
