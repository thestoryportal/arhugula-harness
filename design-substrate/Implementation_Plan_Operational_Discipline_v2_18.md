# Implementation Plan — Operational Discipline v2.18

## Change-note (v2.17 → v2.18)

**Scope of revision.** Pause/resume back-flow arc (narrow scope per operator AskUserQuestion 2026-05-24 — "Narrow — OD-side helper only") absorption per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 + OD spec v1.10 → v1.11 NEW §C-OD-30.4 production-invocation contract (`Spec_Operational_Discipline_v1_11.md` co-published this session). U-OD-51 plan body amendment scope: **Implements** line + **Files** line + **Signatures** line + **ACs** revisions absorbing the v1.11 spec contract.

**v2.17 substantive content preserved verbatim.** All v2.17 content (U-OD-00 through U-OD-54; clusters 1 through 4-OD-E; DAG topology; coverage matrix; cross-axis edge enumeration; all unit bodies other than U-OD-51) preserved unchanged at v2.18. The v2.17 U-OD-41 cost-axis Sub-arc B absorption (5→8 ACs + Implements/Signatures/Files revisions) preserved verbatim. The v2.16 U-OD-51 cross-axis-block lift + PauseResumeAuditPayload absorption (Sub-arc A) preserved verbatim. The v2.15 + v2.14 + ... + v2 chain all preserved.

**Source of fix.** Pause/resume Sub-arc residual per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 (Sub-arc A FULLY-LANDED at `5d6051d` 2026-05-23; production-helper-contract authoring arc opened 2026-05-24 per operator narrow-scope ratification). Companion artifacts at this session: OD spec v1.11 (`Spec_Operational_Discipline_v1_11.md` — NEW §C-OD-30.4); impl arc landing helper(s) at `harness-od/src/harness_od/pause_resume_namespace.py` extension.

**Narrow-scope framing (carried from spec).** The arc lands the OD-side production-invocation contract + helper. **No production callsite exists** in the harness — `capture_pause_snapshot` + `attempt_resume` at `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147` are `NotImplementedError` stubs, and `harness-cp/src/harness_cp/workflow_driver.py` does not invoke `PauseResumeProtocol`. The helper authored at this arc lands as a contract + library surface ready for the CP composer authoring arc (separate scope; out of this arc; gates H_T-CP-22 PARTIAL → RETIRE-READY per `harness-cp/CLAUDE.md` §4.1). This is the structural asymmetry from cost-axis Sub-arc B — U-OD-51 production-callsite-construction AC is marked PARTIAL per `[[halt-route-split-AC-pattern]]`, deferred to CP composer arc.

**Amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-OD-51 plan body** | (a) **Implements** line: cite addition `OD spec v1.8 §C-OD-30.1 + §C-OD-30.2` → `OD spec v1.8 §C-OD-30.1 + §C-OD-30.2 + OD spec v1.11 §C-OD-30.4 (NEW production-invocation contract)`; (b) **Files** line: `harness-od/src/harness_od/pause_resume_namespace.py` retained (Sub-arc A landing site; this arc EXTENDS with helper module-level functions, no new module); (c) **Signatures** line: add helper signatures per §C-OD-30.4 — `_project_pause_event_to_audit_payload(event: PauseEvent, *, workflow_id: str, step_index: int, snapshot_hash: str, state_ledger_anchor: str, prior_event_hash: str, timestamp: str = "") -> PauseResumeAuditPayload` + `_project_resume_outcome_to_audit_payload(attempt: ResumeAttempt, outcome: ResumeOutcome, *, step_index: int, snapshot_hash: str, diff_summary_hash: str \| None, prior_event_hash: str, timestamp: str = "") -> PauseResumeAuditPayload`; (d) **ACs**: 10 ACs total (was 5) — AC #1-#5 (schema + dataclass + Pattern-P1 + Optional fields + verbatim-match unit test) preserved verbatim from Sub-arc A landing; NEW ACs #6 (`_project_pause_event_to_audit_payload` helper landing per §C-OD-30.4 signature + invariants), #7 (`_project_resume_outcome_to_audit_payload` helper landing per §C-OD-30.4 signature + audit_cp_response selection per §C-OD-30.4.1 step 3), #8 (path-disjoint field nullification per §C-OD-30.4.1 step 8 + §C-OD-30.4.4 invariant 3), #9 (production callsite construction DEFERRED per FM-2 + `[[halt-route-split-AC-pattern]]` — gates H_T-CP-22 PARTIAL → RETIRE-READY at CP composer arc; PARTIAL-LANDED at this arc), #10 (unit tests covering helper construction shape + path-disjoint enforcement + audit_cp_response semantics + action_id prefix invariant + pyright strict mode passes). | OD spec v1.11 §C-OD-30.4 + §C-OD-30.4.1 + §C-OD-30.4.4 + cp_audit_conversion.py existing converter dispatch pattern (Sub-arc A landed) + `harness-od/src/harness_od/pause_resume_namespace.py:176-273` existing PauseResumeAuditPayload class shape |

**Plan shape preserved.** v2.17's 55-unit axis-led structure preserved verbatim. No new units; no DAG topology change at any cluster boundary; no cluster reorganization; no coverage matrix delta beyond U-OD-51's spec-cite addition; no cross-axis edge addition (the CXA v2.9 §0.3 8-prefix discriminator table already covers `pause:` + `resume:` per v2.6 7-row composer-arc absorption — NO CXA amendment owed); no AC count change at any unit other than U-OD-51 (5 → 10 ACs at U-OD-51 only).

**Status posture.** Proposed (v2.17) → **Proposed (v2.18)**. v2.18 is a spec-revision-driven plan revision — single-unit-body amendment at U-OD-51 absorbing the v1.11 spec contract.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).**

(i) **U-OD-51 Implementation status at HEAD.** Per pre-arc verification (HEAD `207ab44`): U-OD-51 Sub-arc A landed at `5d6051d` 2026-05-23 — `pause_resume_namespace.py` exists with `PauseResumeAuditPayload` class + `PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA` constant + converter integration at `cp_audit_conversion.py:289-299`. The new ACs (#6-#10) extend the existing module with module-level helper functions. NO Sub-arc A regression risk — helpers are pure-additive functions consuming existing types.

(ii) **`pause_resume_protocol.py` body stubs adjacency.** `capture_pause_snapshot` + `attempt_resume` at `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147` are `NotImplementedError` stubs. This is CP-axis scope (not OD-axis); the OD helpers consume the input types (`PauseEvent` + `ResumeAttempt` + `ResumeOutcome`) which DO exist as Pydantic BaseModels at the same file (lines 46-104). Helper landing does NOT depend on stub bodies being authored.

(iii) **`audit_cp_action_id` pattern divergence between cost-axis and pause/resume.** Cost-axis at U-OD-41 v2.17 uses `cost:<workflow_id>:<step_action_id>`. Pause/resume per §C-OD-30.2 + §C-OD-30.4.1 step 2 uses `pause:<workflow_id>:<step_index>` / `resume:<workflow_id>:<step_index>`. This divergence is preserved at v1.11 (per spec change-note (iii)) and reflected at U-OD-51 AC #6 + #7. Future arc MAY reconcile if `step_action_id`-style pattern proves preferable at CP composer arc.

(iv) **`PauseResumeAuditPayload` literal "AuditPayload" inheritance NOT used.** Per `pause_resume_namespace.py:176` docstring note (Sub-arc A landing): the class is a STANDALONE Pydantic v2 BaseModel that the converter uses to compose `AuditPayload.audit_namespace_attrs` dict — literal Python `class Foo(AuditPayload)` inheritance is NOT what the spec requires. The §C-OD-30.4 helper signatures preserve this discipline: return type is `PauseResumeAuditPayload` (the Pydantic BaseModel), not a subclass of any other type. v2.14 AC #2 wording "extends AuditPayload" preserved verbatim per FM-2; conceptual "extends" = sub-namespace discipline per §C-OD-24.6, not literal inheritance.

(v) **`step_index` semantics deferred to composer arc.** Per §C-OD-30.4.5 deferred-discretion: `step_index` source semantics (per-workflow monotonic counter, manifest-declared step ordinal, or workflow-driver dispatch index) is composer-arc discretion. Helpers consume `step_index` as an integer kwarg; impl arc tests use representative integer values without prescribing source semantics. Surfaced; not patched at U-OD-51 ACs.

**Downstream absorption owed (post-v2.18).**

(a) Workspace `CLAUDE.md` §2.4 OD plan row version bump (v2.17 → v2.18) + description amendment to enumerate the U-OD-51 absorption shape. APPLIED at this session.

(b) Co-published artifacts at this session: OD spec v1.11 (already co-published; see header) + impl arc landing helpers at `pause_resume_namespace.py` + unit tests.

(c) Memory entry `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` description amendment: advance pause/resume Sub-arc B status (helper contract authoring landed). APPLIED at fork doc §10 footer (co-published this session).

(d) Fork doc `.harness/class_1_fork_u_cp_72_cost_and_pause_resume_prefix_gap.md` §10 footer appendage documenting Sub-arc B opening + narrow-scope ratification + helper landing. Co-published this session.

---

## §1 — U-OD-51 plan-body amendment (v2.18)

The v2.14-authored U-OD-51 plan body (preserved verbatim through v2.15 + v2.16 + v2.17) is amended at v2.18 absorbing OD spec v1.11 NEW §C-OD-30.4. Pre-v2.18 plan body preserved verbatim outside the 4 amendment cells (Implements + Files + Signatures + ACs).

### U-OD-51 — pause/resume schema + PauseResumeAuditPayload dataclass + production-invocation helpers (REVISED v2.18)

- **Implements:** OD spec v1.8 §C-OD-30.1 (8 attributes) + §C-OD-30.2 (PauseResumeAuditPayload) + **OD spec v1.11 §C-OD-30.4 (NEW production-invocation contract — helpers + composition discipline + invariants)**
- **Files:** `harness-od/src/harness_od/pause_resume_namespace.py` (Sub-arc A NEW at `5d6051d`; v2.18 EXTENDS with module-level helper functions — no new module)
- **Signatures:**
  - Sub-arc A (preserved): `PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA`; `class PauseResumeAuditPayload(BaseModel)` (Pydantic v2 — not `@dataclass(frozen=True)` per Sub-arc A empirical landing at line 176; v2.14 AC #2 "AuditPayload" inheritance prose preserved verbatim per FM-2, conceptual sub-namespace discipline per §C-OD-24.6 not literal Python inheritance per §C-OD-30.2 docstring note at line 192-197)
  - **NEW at v2.18:** `_project_pause_event_to_audit_payload(event: PauseEvent, *, workflow_id: str, step_index: int, snapshot_hash: str, state_ledger_anchor: str, prior_event_hash: str, timestamp: str = "") -> PauseResumeAuditPayload`
  - **NEW at v2.18:** `_project_resume_outcome_to_audit_payload(attempt: ResumeAttempt, outcome: ResumeOutcome, *, step_index: int, snapshot_hash: str, diff_summary_hash: str | None, prior_event_hash: str, timestamp: str = "") -> PauseResumeAuditPayload`
- **Depends on:** [U-CP-62 (cross-axis: CP)] — preserved verbatim from v2.16 cross-axis-block lift (U-CP-62 landed at `49617e7`; the DAG edge is canonical regardless of upstream landed-vs-bounded state).
- **ACs:**
  1. Schema declares 8 attributes per §C-OD-30.1 *(preserved from v2.14)*
  2. PauseResumeAuditPayload extends AuditPayload with 8 pause/resume-specific fields (pause OR resume path) *(preserved from v2.14; conceptual extends per §C-OD-30.2 sub-namespace discipline at §C-OD-24.6, not literal Python inheritance per Sub-arc A empirical landing at `pause_resume_namespace.py:192-197`)*
  3. Pattern-P1 byte-exact alignment with CP spec v1.10 §26.4 *(preserved from v2.14; CP spec subsequently bumped to v1.13 with renamed identifiers per path γ; Pattern-P1 attribute names unchanged)*
  4. Optional fields per path (pause_reason populated on pause path; resume_outcome on resume path) *(preserved from v2.14)*
  5. Unit test: schema verbatim match *(preserved from v2.14; landed at `harness-od/tests/test_pause_resume_namespace.py` 27/27 PASS per Sub-arc A)*
  6. **`_project_pause_event_to_audit_payload` module-level helper landed at `harness-od/src/harness_od/pause_resume_namespace.py` per §C-OD-30.4 signature.** Helper constructs `PauseResumeAuditPayload` from `PauseEvent` carrier + composition kwargs; sets `audit_cp_action_id = f"pause:{workflow_id}:{step_index}"` per §C-OD-30.4.1 step 2; sets `audit_cp_response = "paused"` per §C-OD-30.4.1 step 3; nulls resume-path fields (`diff_detected`, `diff_policy`, `diff_summary_hash`, `resume_outcome` → `None`) per §C-OD-30.4.1 step 8; uses `prior_event_hash` + `timestamp` kwargs directly per §C-OD-30.4.1 steps 4-5.
  7. **`_project_resume_outcome_to_audit_payload` module-level helper landed at `harness-od/src/harness_od/pause_resume_namespace.py` per §C-OD-30.4 signature.** Helper constructs `PauseResumeAuditPayload` from `ResumeAttempt` + `ResumeOutcome` carriers + composition kwargs; sets `audit_cp_action_id = f"resume:{attempt.paused_workflow_id}:{step_index}"` per §C-OD-30.4.1 step 2 (extracting workflow_id from `attempt.paused_workflow_id` per §C-OD-30.4 helper-signature rationale); sets `audit_cp_response` per §C-OD-30.4.1 step 3 outcome-kind switch (`RESUME_CLEAN` → `"resumed"`; `RESUME_AFTER_REVALIDATION` → `"resumed"`; `ABORT_REVALIDATION_FAILED` → `"diff_detected"`; `ABORT_SNAPSHOT_CORRUPTED` → `"diff_detected"`); sets `diff_detected` from `outcome.outcome_kind != RESUME_CLEAN`; sets `diff_policy` per §C-OD-30.4.1 step 9 inlined approach (`None` for `RESUME_CLEAN`; enum value for non-clean — implementer-discretion at impl arc whether to plumb policy via composer or hard-code per outcome-kind branch per FM-2); sets `resume_outcome` from `outcome.outcome_kind.value`; nulls pause-path fields (`pause_reason`, `state_ledger_anchor` → `None`) per §C-OD-30.4.1 step 8.
  8. **Path-disjoint field nullification enforced at helper bodies** per §C-OD-30.4.4 invariant 3. Pause helper explicitly passes `None` for `diff_detected` / `diff_policy` / `diff_summary_hash` / `resume_outcome`. Resume helper explicitly passes `None` for `pause_reason` / `state_ledger_anchor`. Verified by pyright strict mode + unit tests asserting the null-fields per path.
  9. **Production callsite construction DEFERRED per FM-2 + `[[halt-route-split-AC-pattern]]` precedent.** No production callsite exists at this arc — `capture_pause_snapshot` + `attempt_resume` at `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147` are `NotImplementedError` stubs; `workflow_driver.py` does not invoke `PauseResumeProtocol` per `harness-cp/CLAUDE.md` §4.1 H_T-CP-22 PARTIAL gate. Helper construction at production callsite gates on CP composer authoring arc (separate scope; gates H_T-CP-22 PARTIAL → RETIRE-READY). The v1.11 typed-helper path + canonical-converter routing per §C-OD-30.4 is now AVAILABLE post this arc (helpers + converter branch all land — converter branch already operational from Sub-arc A). Migration of any future workflow_driver pause-event handler from raw `PauseResumeAuditPayload` construction → typed helper invocation requires CP composer arc landing; migration is OPERATIONAL refinement deferred per FM-2 (Sub-arc B narrow scope is helper landing; production callsite construction is a separate follow-on arc). **AC #9 success condition:** this deferral discipline documented at U-OD-51 plan body + change-note adjacent finding (ii) + spec §C-OD-30.4.5 deferred-discretion section; existing production code unchanged at this arc; helper lands as dead code until CP composer arc. **(PARTIAL-LANDED at v2.18.)**
  10. **Importable; pyright strict mode passes; unit tests green.** `from harness_od.pause_resume_namespace import _project_pause_event_to_audit_payload, _project_resume_outcome_to_audit_payload` resolves without error. Unit tests covering: (a) `_project_pause_event_to_audit_payload` round-trip — input `PauseEvent` fixture + kwargs → output `PauseResumeAuditPayload` with byte-exact field values; (b) `_project_resume_outcome_to_audit_payload` round-trip per 4 `ResumeOutcomeKind` cases (`RESUME_CLEAN` / `RESUME_AFTER_REVALIDATION` / `ABORT_REVALIDATION_FAILED` / `ABORT_SNAPSHOT_CORRUPTED`) — verifying audit_cp_response selection per AC #7; (c) path-disjoint nullification per AC #8 — pause helper output has null resume-path fields and vice-versa; (d) action_id prefix invariant per §C-OD-30.4.4 #2 — `audit_cp_action_id.startswith("pause:")` for pause helper output, `.startswith("resume:")` for resume helper output; (e) `audit_cp_timestamp` MVP sentinel — empty-string kwarg flows through unchanged; (f) `audit_cp_prior_event_hash` sentinel zero-hash — `"0" * 64` kwarg flows through unchanged; (g) frozen-model invariant — output `PauseResumeAuditPayload` instances are frozen (Pydantic v2 ConfigDict `frozen=True` per Sub-arc A landing at line 213); attempting field-assign raises `pydantic.ValidationError`. Existing 27 unit tests at `test_pause_resume_namespace.py` (Sub-arc A) + new helper tests (estimate 8-12 new tests) all green. Existing converter tests (16/16 at `test_u_cp_72_converter_6_prefix_extension.py`) preserved unchanged (helpers consume converter dispatch — no converter code edit).

---

## §2 — Preservation guarantees

| Section | Preservation |
|---|---|
| All v2.17 units other than U-OD-51 (54 units) | Preserved verbatim |
| v2.17 U-OD-41 cost-axis Sub-arc B absorption (5→8 ACs + Implements/Signatures/Files revisions) | Preserved verbatim |
| v2.16 U-OD-51 cross-axis-block lift + PauseResumeAuditPayload absorption (Sub-arc A) | Preserved verbatim |
| v2.15 U-OD-51 enum-citation absorption + all v2.14 + v2.13 + ... + v2 content | Preserved verbatim |
| v2.14 U-OD-51 AC #1-#5 (schema + dataclass + Pattern-P1 + Optional fields + verbatim-match unit test) | **Preserved verbatim** at v2.18 ACs #1-#5 |
| U-OD-51 plan body | **AMENDED at v2.18** per §1 above (Implements + Files + Signatures + ACs all revised; preserved AC #1-#5 verbatim; new ACs #6-#10; new helper signatures per v1.11 §C-OD-30.4) |
| U-OD-51 Depends-on cite | Preserved verbatim ([U-CP-62 (cross-axis: CP)]) |
| DAG topology + cluster placement at 4-OD-E | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_18.md` |
| Version | v2.18 |
| Filing event | Pause/resume back-flow arc (narrow scope per operator AskUserQuestion 2026-05-24) — Sub-arc B production-helper-contract authoring per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 + OD spec v1.11 NEW §C-OD-30.4. 2026-05-24 |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_17.md` (v2.17 substantive content preserved verbatim outside the single U-OD-51 plan-body amendment) |
| Successor | (none — current canonical) |
| Co-published with | `Spec_Operational_Discipline_v1_11.md` (already co-published at this session; see spec §1 §C-OD-30.4) + impl arc landings (helpers at `pause_resume_namespace.py` extension + new unit tests) + workspace `CLAUDE.md` §2.3 OD spec row + §2.4 OD plan row absorption |
| New units | 0 (single-unit-body amendment at U-OD-51) |
| Revised units | 1 — U-OD-51 (Implements + Files + Signatures + ACs absorbing v1.11 spec contract; 5 → 10 ACs at U-OD-51 only) |
| Cluster | No cluster change — U-OD-51 preserved at its existing cluster 4-OD-E placement |
| Status posture | Proposed (v2.17) → Proposed (v2.18). v2.18 is a spec-revision-driven plan revision — single-unit-body amendment at U-OD-51 absorbing the v1.11 spec contract. |
| Operator authority | AskUserQuestion 2026-05-24 — operator selected "Narrow — OD-side helper only" scope. Reverses fork doc §9 doc-only deferral. |
| Cross-axis dependencies | Unchanged at v2.18. U-OD-51's [U-CP-62 (cross-axis: CP)] dependency preserved verbatim. CXA v2.9 §0.3 8-prefix discriminator table already covers `pause:` + `resume:` per v2.6 7-row composer-arc absorption — NO CXA amendment owed at this arc. |
| Coverage verification | U-OD-51 spec-cite addition from `OD spec v1.8 §C-OD-30.1 + §C-OD-30.2` (2 cites at v2.14/v2.16/v2.17) → `OD spec v1.8 §C-OD-30.1 + §C-OD-30.2 + OD spec v1.11 §C-OD-30.4` (3 cites at v2.18). All cites verified against `design-substrate/` + `harness-od/src/` at HEAD; no `Phase_7_Class_N_Tension` filing required. |
| Related forks | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 (pause/resume Sub-arc residual — narrow scope ratification + helper-contract absorption) |
| Related memory | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (advance pause/resume Sub-arc B status); `[[halt-route-split-AC-pattern]]` (AC #9 PARTIAL-LANDED — production callsite construction deferred to CP composer arc); `[[verification-shape-sharpened-grep-vs-e2e]]` (helper is dead code until CP composer arc; H_T-CP-22 PARTIAL → RETIRE-READY gate is workflow_driver invocation, not helper authoring) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-24 |

*Filed at Phase 7 sub-phase 7b/7c as the OD-side pause/resume back-flow arc plan revision per fork doc §9 routing target. v2.17 substantive content preserved verbatim; single-unit-body amendment at U-OD-51 (5 → 10 ACs) absorbing OD spec v1.11 NEW §C-OD-30.4 helper-contract authoring. Co-published with OD spec v1.11 + impl arc helper landings. AC #9 PARTIAL-LANDED per `[[halt-route-split-AC-pattern]]` — production callsite construction deferred to CP composer arc (gates H_T-CP-22 PARTIAL → RETIRE-READY per `harness-cp/CLAUDE.md` §4.1).*
