# Implementation Plan — Control Plane v2.21

## Change-note (v2.20 → v2.21)

**Scope of revision.** Single-unit-body amendment at U-CP-64 absorbing CP spec v1.15 → v1.16 NEW §26.8 `ResumeContext` typed Pydantic v2 BaseModel carrier authoring + §26.8.5 `PauseResumeProtocol.attempt_resume(...)` async signature widening (NEW keyword-only `resume_context: ResumeContext | None = None` parameter with backward-compatible default). Co-published with runtime spec v1.23 → v1.24 + runtime plan v2.22 → v2.23 NEW L9-terdecies cluster (U-RT-93/94/95) authoring at this session. ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO acceptance-criteria removal; ZERO cross-axis cascade.

**Source of fix.** CP spec v1.15 → v1.16 publication (this session, prior commit `aa841b0`) authoring NEW §26.8 ResumeContext carrier per ratified scoping doc `.harness/hitl_gate_as_pause_trigger_composition_scoping.md` Q3 (c-ii) FORCED — empirical-verification §0(B) finding confirmed `ResumeContext` does NOT exist at HEAD `e394074` (ZERO grep hits across harness-runtime / harness-cp / harness-core source trees), so the carrier itself must be authored CP-side; the runtime-side consumption is at runtime spec v1.24 §14.8.8.5 + runtime plan v2.23 L9-terdecies cluster.

**Authority basis for fix direction.** The narrow §26 amendment at CP spec v1.16 is the minimal cross-axis-locus for authoring the operator-response delivery surface across the pause-resume boundary. C-CP-17 §17.1 `await_human_approval` declares the durable-async HITL primitive shape; the resume signal must arrive at the resumed step via some operator-supplied context envelope. The async `attempt_resume(snapshot, *, material_diff_policy)` signature at v1.10 §26.1 has NO operator-context envelope, so the durable signal has no delivery surface. The minimal fix is: (a) author a typed `ResumeContext` envelope carrier; (b) widen `attempt_resume` to accept it as keyword-only with backward-compatible default. The U-CP-64 plan-body absorbs both at a single-unit-body amendment.

**One amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-CP-64 plan body** | (i) ADD `ResumeContext` Pydantic v2 BaseModel carrier landing to the Files-column at `harness-cp/src/harness_cp/pause_resume_protocol_types.py` (APPEND new BaseModel sibling to existing `WorkflowPauseReason` / `MaterialDiffPolicy` / `PauseSnapshot` / `ResumeResult` per U-CP-62 v2.17 amendment file path). Frozen Pydantic v2; single optional field `hitl_response: HITLResult | None = None`. (ii) AMEND Signatures line: `async def attempt_resume(self, snapshot, *, material_diff_policy, resume_context: ResumeContext | None = None) → ResumeResult` (NEW keyword-only parameter at end of kw-only list; backward-compatible default). (iii) ADD new AC #6 covering ResumeContext carrier landing (frozen BaseModel + single optional field + default-None backward-compat). (iv) AMEND Implements line: `Implements: CP spec v1.16 §26.1 attempt_resume signature (widened) + §26.6 invariants 4-5 + §26.8 ResumeContext carrier`. (v) Existing ACs #1-#5 preserved verbatim from v2.15 (preserved through v2.17 amendment) — Hash validation + material diff detection + STRICT/OPERATOR_ARBITRATE policy handling + U-CP-56 coexistence semantics all orthogonal to the new field per CP spec v1.16 §26.8.3 5-invariant orthogonality analysis. | CP spec v1.16 §26.8 + ratified scoping doc Q3 (c-ii) FORCED |

**Adjacent harmonization sites.** None — the amendment is one-unit-body only. U-CP-62 + U-CP-63 + U-CP-65 (rest of cluster 10-CP-B) preserved verbatim per v2.20 prior. DAG topology preserved verbatim (cluster 10-CP-B closure at `49617e7` per H_T-CP-22 batch-18 RETIRED ledger entry; U-CP-64 amendment is in-place body refresh, NOT re-decomposition). Coverage matrix preserved (§26.1 + §26.2 + §26.6 + NEW §26.8 → U-CP-62, U-CP-63, U-CP-64).

**Sections preserved verbatim from v2.20.** All v2.20 substantive content + v2.19 / v2.18 / v2.17 / v2.16 / v2.15 / ... / v2 chain preserved verbatim outside the single U-CP-64 amendment site. U-CP-43 GateLevelInput conform at v2.20 (B2 plan-follows-spec) preserved unchanged. U-CP-56 StepExecutionContext 9th-field workflow_id at v2.18 preserved. All cluster 10-CP-A + 10-CP-B unit bodies preserved.

**Status posture.** Proposed (v2.20) → **Proposed (v2.21)**. v2.21 is a single-unit-body amendment absorbing upstream CP spec §26 amendment. NO new units; NO new cluster; NO DAG topology change; NO cluster-boundary edge addition; NO coverage matrix structural change; NO unit re-decomposition; NO acceptance criterion removal (one NEW AC #6 added; ACs #1-#5 preserved verbatim).

**Downstream absorption owed (post-v2.21).**

(a) Workspace `CLAUDE.md` §2.4 CP plan row version bump (v2.20 → v2.21); co-published this arc.

(b) `harness-cp` impl — `pause_resume_protocol_types.py` APPEND new `ResumeContext` BaseModel + `pause_resume_protocol.py:295` AMEND async `attempt_resume(...)` signature widening with `resume_context: ResumeContext | None = None` keyword-only param. 16/16 existing pause/resume tests pass unchanged (no behavior change with default None per CP spec v1.16 §26.8.5 backward-compatibility framing). Co-published this arc OR next sequential `phase-7-implementation` skill invocation.

(c) `harness-runtime` impl + runtime plan v2.22 → v2.23 — NEW L9-terdecies cluster (U-RT-93/94/95) consuming `ResumeContext.hitl_response` at runtime-side composer per runtime spec v1.24 §14.8.8.5; co-published this arc per scoping doc §3.1 commit chain.

(d) OD spec / OD plan / OD impl / CXA / ADR — ZERO cascade per scoping doc §3.3 (verified: OD spec §C-OD-30.4 PauseResumeAuditPayload composes from PauseEvent + ResumeOutcome, not from ResumeContext; CXA v2.10 unchanged; ADR/ADD/PRD unchanged).

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **`ResumeContext` future-extensibility (per CP spec v1.16 §26.8 change-note adjacent defect (i)).** v1.16 + v2.21 author the carrier with a single field `hitl_response: HITLResult | None = None`. Future operator-discretion arcs may extend with additional fields (e.g., `operator_burden_override`, `revalidation_skip_reason`, `resume_idempotency_key`). Surfaced; NOT patched at v2.21 per FM-2 no-extension — the scoping doc Q3 authorized ONLY `hitl_response`. Subsequent fields routed to follow-on operator-discretion arcs.

(ii) **`ResumeContext.hitl_response` semantic at non-HITL pause reasons (per CP spec v1.16 §26.8 change-note adjacent defect (ii)).** When `snapshot.pause_reason ∈ {EXPLICIT_OPERATOR, TIMEOUT_BOUNDARY, EXTERNAL_DEPENDENCY}`, `resume_context.hitl_response` should be None. The §26.6 invariants do NOT currently enumerate a per-pause-reason validity check on `ResumeContext`. Runtime-side consumer (v1.24 §14.8.8.5) is the appropriate check site, NOT the CP-side carrier definition. Surfaced; NOT patched at v2.21 per FM-2.

---

## §1 — U-CP-64 plan-body amendment (v2.21)

The U-CP-64 declaration last canonically authored at `Implementation_Plan_Control_Plane_v2_17.md` §3 is amended at v2.21 as follows. Original v2.17 content preserved verbatim except for the additions enumerated below. v2.18 / v2.19 / v2.20 did not touch U-CP-64 (v2.18 amended U-CP-56 only per StepExecutionContext 9th-field workflow_id; v2.19 was citation-cascade absorption only; v2.20 amended U-CP-43 GateLevelInput conform only).

### U-CP-64 — PauseResumeProtocol.attempt_resume() + material-diff detection + ResumeContext carrier landing (v2.21 amendment — Files-column EXTEND adding `pause_resume_protocol_types.py` ResumeContext + Signatures line widening + NEW AC #6 covering ResumeContext carrier landing)

**Amendment delta (v2.17 → v2.21).** Files-column EXTEND adding `pause_resume_protocol_types.py` ResumeContext BaseModel landing. Signatures line widening adding `resume_context: ResumeContext | None = None` keyword-only parameter to async `attempt_resume(...)` signature. NEW AC #6 covering ResumeContext carrier landing discipline. v2.15 + v2.17 ACs (#1-#5) preserved verbatim — orthogonal to the new field per CP spec v1.16 §26.8.3 5-invariant orthogonality analysis (snapshot-immutability + snapshot-hash-validation + material-diff-state-ledger-anchor + per-pause-reason-routing + U-CP-56-prefix-replay-coexistence all orthogonal to `ResumeContext`).

- **Implements:** CP spec v1.16 §26.1 attempt_resume signature (widened) + §26.6 invariants 1-5 + **§26.8 ResumeContext carrier (NEW at v2.21)**
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND — adds `PauseResumeProtocol.attempt_resume()` class method; OLD free-function `attempt_resume(attempt: ResumeAttempt)` at lines 128–147 preserved verbatim per CP spec v1.11 §26 NEW NOTE coexistence) + `harness-cp/src/harness_cp/pause_resume_protocol_types.py` (EXTEND — APPEND NEW `ResumeContext` Pydantic v2 BaseModel sibling to existing `WorkflowPauseReason` / `MaterialDiffPolicy` / `PauseSnapshot` / `ResumeResult` per U-CP-62 v2.17 amendment file path)
- **Signatures:** `async def attempt_resume(self, snapshot, *, material_diff_policy, resume_context: ResumeContext | None = None) -> ResumeResult` (class method on `PauseResumeProtocol`; NEW keyword-only parameter `resume_context` at end of kw-only list per CP spec v1.16 §26.8.5; backward-compatible default `None`); NEW `ResumeContext(BaseModel)` frozen Pydantic v2 with single field `hitl_response: HITLResult | None = None`
- **Depends on:** [U-CP-62, U-CP-63]
- **ACs (preserved verbatim from v2.15 through v2.17 chain; NEW AC #6 added at v2.21):**
  1. Snapshot hash validated on resume; corruption → `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`
  2. Material diff detected when `state_ledger_anchor` no longer reachable from current entry chain
  3. STRICT policy: diff → `CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED`
  4. OPERATOR_ARBITRATE policy: diff → `CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED` + HITL escalation
  5. Coexist with U-CP-56 prefix-replay-based resumption (Path A-modified preserved)
  6. **NEW at v2.21.** `ResumeContext` Pydantic v2 BaseModel lands at `pause_resume_protocol_types.py` per CP spec v1.16 §26.8.1 — frozen (`model_config = ConfigDict(frozen=True)`) + single optional field `hitl_response: HITLResult | None = None` + default-None backward-compat preserved. `PauseResumeProtocol.attempt_resume(...)` async signature widening (NEW keyword-only `resume_context: ResumeContext | None = None` parameter at end of kw-only list) lands at `pause_resume_protocol.py:295`. Method body INGESTS but does NOT consume `resume_context` at the CP-side implementation at v2.21 per CP spec v1.16 §26.8.5 method-body-posture-at-v1.16 framing — the runtime-side consumer at runtime spec v1.24 §14.8.8.5 (U-RT-94 amend at runtime plan v2.23) is the propagation site. 16/16 existing pause/resume unit tests + 4/4 e2e tests at `harness-runtime/tests/integration/test_u_rt_89_pause_resume_full_execution_path.py` pass unchanged (existing callers at L9-undecies `workflow_driver.py:477` async-bridge invocation pass no `resume_context` → receives None default → identical control flow to pre-v1.16 baseline).

**Rollback boundary (preserved verbatim from v2.15; ResumeContext landing added at v2.21).** Revert the `PauseResumeProtocol.attempt_resume()` class method + revert ResumeContext BaseModel append. U-CP-65 (span emission) loses resume-site emission. The 3 CP-FAIL classes go un-raised. U-RT-94 + U-RT-95 (cross-axis runtime-side consumers per runtime plan v2.23 L9-terdecies cluster) lose typed-envelope substrate; the runtime composer falls back to no operator-response delivery surface on resume.

---

## §2 — Cluster 10-CP-B preservation + DAG topology

DAG topology preserved verbatim from v2.17 (cluster 10-CP-B at `49617e7` closure per H_T-CP-22 batch-18 RETIRED ledger entry):
- U-CP-62 (L0) — `WorkflowPauseReason` + `MaterialDiffPolicy` + `PauseSnapshot` + `ResumeResult` schemas (v2.17 amendment preserved verbatim)
- U-CP-63 (L1) — `PauseResumeProtocol.capture_pause_snapshot()` (v2.17 amendment preserved verbatim; depends on [U-CP-62])
- U-CP-64 (L2) — `PauseResumeProtocol.attempt_resume()` + material-diff detection + **NEW ResumeContext carrier (v2.21)** (depends on [U-CP-62, U-CP-63])
- U-CP-65 (L3) — span emission (preserved verbatim from v2.16; cross-axis soft-dep U-OD-51)

Cluster-boundary edges to v2.21 amendment:
- NEW: U-RT-94 (runtime plan v2.23 L9-terdecies L1) depends on U-CP-64 (within-axis-cross-package on `ResumeContext` carrier + `attempt_resume` widened signature) — cross-axis edge declared at runtime plan v2.23 cluster body, NOT here per cross-axis-edge declaration-at-consumer-site convention.

Coverage matrix preserved verbatim — §26.1 + §26.2 + §26.6 + NEW §26.8 → U-CP-62, U-CP-63, U-CP-64.

---

## §3 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_21.md` |
| Version | v2.21 |
| Filing event | CP spec v1.15 → v1.16 narrow §26 amendment absorption per ratified scoping doc Q3 (c-ii) FORCED |
| Predecessor | `Implementation_Plan_Control_Plane_v2_20.md` (substantive content preserved verbatim outside U-CP-64 amendment site) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.4 CP plan row bump v2.20 → v2.21; CP spec v1.16 (commit `aa841b0` prior); runtime spec v1.24 (commit `c73c25d` prior); runtime plan v2.22 → v2.23 (this session); harness-cp impl (`pause_resume_protocol_types.py` ResumeContext + `pause_resume_protocol.py:295` signature widening); harness-runtime impl (hitl_gate_composer.py amend + new helper + new exception + e2e test); tests |
| Operator authority | AskUserQuestion 2026-05-24 ("Ratified") at session opening checkpoint `20260524-130230` item #1; ratified scoping doc Q3 (c-ii) FORCED |
| Unit-count change | None (73 → 73 — single-unit-body amendment) |
| Cluster-count change | None |
| DAG topology change | None (cluster-boundary edge to U-RT-94 declared at consumer site per convention) |
| Coverage matrix structural change | None (§26.1 + §26.2 + §26.6 + NEW §26.8 → U-CP-62, U-CP-63, U-CP-64; rows unchanged) |
| Acceptance criterion count change at U-CP-64 | +1 (5 → 6; NEW AC #6 covering ResumeContext carrier landing + signature widening) |
| Cross-axis cascade | Within-axis-cross-package (runtime plan v2.23 U-RT-94 depends on U-CP-64); ZERO new CXA-level cross-axis edges |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream CP spec v1.16 §26.8 publication into U-CP-64 plan body; fidelity-pure single-unit-body amendment (NEW AC #6 + Signatures widening + Files-column EXTEND); NO contract addition; NO unit re-decomposition; NO DAG topology change; preservation audit PASSED |
| Date | 2026-05-24 |
