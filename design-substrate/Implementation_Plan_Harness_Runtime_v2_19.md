# Implementation Plan — Harness Runtime v2.19

## Change-note (v2.18 → v2.19)

**Scope of revision.** AdvReview 07 Class 1 findings F1-02 + F1-03 inline doc-drift absorption per `Adversarial_Review_07_Runtime_v1_18_+_v2_17.md`. Two surgical fixes at U-RT-83 unit body authored at canonical v2.17 plan file:
- **F1-02:** AC #4 mis-attributes Pydantic v2 frozen-model validation to `ValidatorFrameworkConfig` (which is `@dataclass(frozen=True)` per spec §14.13.1 line 2469, NOT Pydantic v2). Validation discipline applies to outer `RuntimeConfig`. AC #4 reword absorbed at v2.19.
- **F1-03:** Files section recommended path `harness-runtime/src/harness_runtime/validator_framework_config.py` (top-level) characterized as parallel to §14.12 `MemoryToolBackendConfig` precedent. Empirical inventory at HEAD shows §14.12 precedent at `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py:93` (lifecycle/ subdirectory, types-aggregation file). Implementer-discretion clause at AC #3 absorbed the resolution: actual landing at `harness-runtime/src/harness_runtime/lifecycle/validator_framework_types.py:29` IS parallel to the cited precedent. v2.19 retags the recommended path to the empirically-landed location (which the implementer correctly resolved against the parallel-to claim).

**v2.18 substantive content preserved verbatim.** All v2.18 content (the L9-decies cluster canonical-reading amendment for §25/C-CP-25 cite-cascade absorption + 87-unit axis-led structure + DAG topology + coverage matrix + cluster table) preserved unchanged outside the F1-02 + F1-03 canonical-reading amendments enumerated at §1 below. The v2.17 + v2.16 + ... + v2 chain all preserved.

**Source of fix.** `Adversarial_Review_07_Runtime_v1_18_+_v2_17.md` Class 1 F1-02 + F1-03 (cleared with inline fixes per disposition).

**Amendments.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§1 (NEW) — U-RT-83 AC #4 reword (F1-02 absorption)** | NEW canonical-reading amendment at v2.19 recording the AC #4 reword. v2.17 AC #4 text "Both shapes pass Pydantic v2 frozen-model validation" canonically-read at v2.19 AS "Both shapes pass `RuntimeConfig` Pydantic v2 frozen-model validation; `ValidatorFrameworkConfig.default()` constructs without raising per dataclass `frozen=True` discipline (per spec v1.20 §14.13.1 line 2469 dataclass shape)." Delta-only preservation: v2.17 plan file NOT edited — canonical reading at v2.19 retags per §1. | AdvReview 07 F1-02 inline-fix resolution path |
| **§2 (NEW) — U-RT-83 Files section + change-note (d) reword (F1-03 absorption)** | NEW canonical-reading amendment at v2.19 recording the Files-section path retag. v2.17 U-RT-83 Files section recommended path `harness-runtime/src/harness_runtime/validator_framework_config.py` canonically-read at v2.19 AS `harness-runtime/src/harness_runtime/lifecycle/validator_framework_types.py` (the empirically-landed location at HEAD per `lifecycle/validator_framework_types.py:29`; matches the §14.12 `MemoryToolBackendConfig` precedent at `lifecycle/memory_tool_types.py:93` cited by v2.17 change-note (d)). Change-note (d) "parallel to ... lifecycle/memory_tool_*.py module-organization pattern" claim now empirically validated by actual landing. Delta-only preservation: v2.17 plan file NOT edited — canonical reading at v2.19 retags per §2. | AdvReview 07 F1-03 inline-fix resolution path (option (a) — update path to true §14.12 parallel) |

**Plan shape preserved.** v2.18's 87-unit axis-led structure preserved verbatim. No new units; no DAG topology change; no coverage matrix change. ZERO contract change; ZERO signature change; ZERO acceptance-criterion semantic change (the AC #4 reword is a documentation clarification — the testable observable is unchanged: `RuntimeConfig` constructs successfully in both shapes); ZERO field-set change; ZERO behavior change — fidelity-pure documentation patch under FM-2 no-extension discipline.

**Status posture.** Proposed (v2.18) → **Proposed (v2.19)**. v2.19 is a documentation-drift fix absorbing AdvReview 07 Class 1 F1-02 + F1-03; no new unit, no new contract, no new AC, no DAG change.

**Downstream absorption owed (post-v2.19).**
(a) Workspace `CLAUDE.md` §2.4 Runtime plan row version bump (v2.18 → v2.19); co-published this AdvReview 07 doc-drift fix arc.
(b) AdvReview 07 Class 1 F1-02 + F1-03 marked RESOLVED at this arc; F1-01 (spec-side) absorbed at runtime spec v1.19 → v1.20 (this session).

---

## §1 — U-RT-83 AC #4 reword (F1-02 absorption)

**Pre-v2.19 AC #4 text (at v2.17 plan body, line 68):**

> AC #4: `RuntimeConfig(validator_framework_config=None)` constructs successfully + `RuntimeConfig(validator_framework_config=ValidatorFrameworkConfig.default())` constructs successfully. Both shapes pass Pydantic v2 frozen-model validation.

**Post-v2.19 canonical reading:**

> AC #4: `RuntimeConfig(validator_framework_config=None)` constructs successfully + `RuntimeConfig(validator_framework_config=ValidatorFrameworkConfig.default())` constructs successfully. Both shapes pass `RuntimeConfig` Pydantic v2 frozen-model validation; `ValidatorFrameworkConfig.default()` constructs without raising per dataclass `frozen=True` discipline (per spec v1.20 §14.13.1 line 2469 dataclass shape — `ValidatorFrameworkConfig` is `@dataclass(frozen=True)`, NOT a Pydantic v2 BaseModel; validation discipline at the outer `RuntimeConfig` Pydantic model only).

**Discrimination note.** The testable observable at AC #4 is unchanged: both `RuntimeConfig` construction shapes succeed without raising. The fix disambiguates which model carries which validation discipline (outer `RuntimeConfig` = Pydantic v2 frozen-model; inner `ValidatorFrameworkConfig` = `@dataclass(frozen=True)`). Empirical evidence per spec §14.13.1 line 2469 + `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py:92-93` (parallel `MemoryToolBackendConfig` precedent is also `@dataclass(frozen=True)`).

**Delta-only plan-file preservation.** v2.17 plan file U-RT-83 AC #4 text preserved byte-exact. Canonical reading at v2.19 retags per the table above.

---

## §2 — U-RT-83 Files section + change-note (d) reword (F1-03 absorption)

**Pre-v2.19 Files section text (at v2.17 plan body, line 56):**

> `harness-runtime/src/harness_runtime/validator_framework_config.py` (NEW) — `ValidatorFrameworkConfig` empty-marker sub-model

**Pre-v2.19 change-note (d) text (at v2.17 plan body, line 30):**

> Carrier-home decision: `ValidatorFrameworkConfig` lives in `harness-runtime` at U-RT-83. Parallel to `MemoryToolBackendConfig` at `harness-runtime` per spec v1.17 §14.12 + v1.18 §14.13 (both RuntimeConfig sub-models live in the runtime package). [...]

**Post-v2.19 canonical reading.**

| v2.17 site | Pre-v2.19 cite | Post-v2.19 canonical reading | Empirical evidence |
|---|---|---|---|
| Files section (line 56) | `harness-runtime/src/harness_runtime/validator_framework_config.py` (top-level recommended path) | `harness-runtime/src/harness_runtime/lifecycle/validator_framework_types.py` (empirically-landed location at HEAD — implementer-discretion clause at AC #3 resolved the path to true §14.12 parallel) | `harness-runtime/src/harness_runtime/lifecycle/validator_framework_types.py:29` (actual `ValidatorFrameworkConfig` class definition at HEAD post-batch-17) |
| Change-note (d) (line 30) | "Parallel to `MemoryToolBackendConfig` at `harness-runtime` per spec v1.17 §14.12 + v1.18 §14.13" | Same claim; now empirically validated at file-path granularity — both sub-models land under `lifecycle/` subdirectory in types-aggregation files (`lifecycle/memory_tool_types.py` + `lifecycle/validator_framework_types.py`) | `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py:93` (parallel precedent) |

**Discrimination note.** The AC #3 implementer-discretion clause at v2.17 plan body ("or equivalent runtime-package-internal module organization at implementer discretion") absorbed the path-claim drift between the recommended top-level path and the cited §14.12 precedent. The implementer correctly resolved the drift by choosing `lifecycle/validator_framework_types.py` — which IS parallel to the cited precedent. v2.19 canonical reading updates the recommended path to match the empirically-landed location.

**Delta-only plan-file preservation.** v2.17 plan file U-RT-83 Files section + change-note (d) text preserved byte-exact. Canonical reading at v2.19 retags per the table above.

---

## §3 — Preservation guarantees

| Element | Disposition |
|---|---|
| All v2.18 units (U-RT-00 through U-RT-86) | Preserved verbatim outside U-RT-83 AC #4 + Files section canonical-reading absorption at §1 + §2 |
| v2.18 L9-decies cluster canonical-reading amendment for §25/C-CP-25 cite-cascade | Preserved verbatim |
| v2.17 L9-decies cluster body (U-RT-83 + U-RT-84 + U-RT-85) | Plan body preserved byte-exact at v2.17 file; canonical reading at v2.18 retags per §25→§28 cite-cascade; canonical reading at v2.19 retags per AdvReview 07 F1-02 + F1-03 absorption |
| v2.17 L9-novies / L9-octies / L9-septies / L9-sexies / earlier-cluster bodies | Preserved verbatim |
| v2.16 + v2.15 + ... + v2 chain | Preserved verbatim |
| DAG topology | Preserved verbatim (zero new edges; zero edge removals) |
| Coverage matrix | Preserved verbatim |
| Cluster table (10 clusters; 87 total atomic units) | Preserved verbatim |

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_19.md` |
| Authored at | AdvReview 07 Class 1 doc-drift fix arc 2026-05-24 (this session) |
| Authoring authority | `implementation-planner` skill AdvReview-absorption revision-pass per AdvReview 07 disposition (Class 1 inline fixes at next plan touch) |
| Predecessor authoring | `Implementation_Plan_Harness_Runtime_v2_18.md` (v2.18 substantive content preserved verbatim outside U-RT-83 AC #4 + Files section canonical-reading absorption) |
| Successor consumption | Workspace `CLAUDE.md` §2.4 row bump + AdvReview 07 closure note (this session) |
| Source review | `Adversarial_Review_07_Runtime_v1_18_+_v2_17.md` Class 1 F1-02 + F1-03 (CLEARED with inline fixes per disposition §"Disposition") |
| Co-published this session | Runtime spec v1.19 → v1.20 (F1-01 absorption) |

---

*End of runtime plan v2.19. AdvReview 07 Class 1 F1-02 + F1-03 RESOLVED. F1-01 RESOLVED at runtime spec v1.20 (co-published this session). AdvReview 07 fully closed at this arc; review doc closure note follows at workspace bookkeeping commit.*
