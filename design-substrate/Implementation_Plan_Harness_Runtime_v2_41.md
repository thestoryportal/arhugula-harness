# Implementation Plan — Harness Runtime — v2.41

*Delta over v2.40. v2.41 is a Class 1 fork resolution Reading (A) apply pass per `.harness/class_1_fork_yaml_loader_step_payload_scalar_coercion_gap.md` operator-ratified 2026-05-29 absorbing runtime spec v1.38 → v1.39 §14.19 Q-H=b re-litigation + `_coerce_int_fields` retirement. Single-unit-body amendment at U-RT-104 (dependency declaration refresh + helper retirement). ZERO new units; ZERO DAG topology change; ZERO cross-axis cascade. Unit count 109 UNCHANGED. v2.40 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

## §0 Change note (v2.40 → v2.41)

### §0.1 What changed

| Element | v2.40 | v2.41 |
|---|---|---|
| U-RT-104 YAML parser dep | `strictyaml>=1.7` (per Q-H=b at G2) | **`pyyaml>=6.0`** (per Reading A re-litigation of Q-H=b; closes probe finding #16/#17) |
| U-RT-104 `_coerce_int_fields` helper | LANDED at v2.31 (coerce `workflow.entry_version` str → int from strictyaml.dirty_load stringification) | **RETIRED at v2.41.** Both YAML and TOML loaders preserve native int post-spec-v1.39 Reading A. Boundary-coercion code path no longer needed. |
| U-RT-104 `_check_version` simplification | Accepts `str` or `int` `version` value (str coerced via `int(str(raw))`) | **Rejects non-int `version` directly.** Native typing means `version: 1` arrives as int; `version: "1"` rejected at the boundary. |
| NEW U-RT-104 file | (none added at v2.40) | **NEW `lifecycle/strict_safe_loader.py`** (78 lines; pyyaml SafeLoader subclass preserving 4 strictness features). |
| §1 unit count | 109 | 109 (UNCHANGED) |
| §2 DAG | UNCHANGED | UNCHANGED |
| H_T-RT-35 transit framing | STAYS PARTIAL per v2.39 + v2.40 framing | UNCHANGED — STAYS PARTIAL; v2.41 is intra-U-RT-104 scope, not a §16.5 composer arc transit |
| CXA v2.16 → v2.17 transit | 6 PENDING → 1 LANDED + 5 carry per v2.38 | UNCHANGED — ZERO CXA transit at v2.41 (parser-implementation refactor, not §16.5 composer surface) |

### §0.2 Scope discipline

§0 (this change note); §1 U-RT-104 unit-body canonical-reading amendment + dep refresh + helper retirement; §2 DAG preservation (ZERO edge changes); §3 adjacent observations + carry-forward; §4 filing footer. All v2.40 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention except: (a) U-RT-104 dep `strictyaml>=1.7` → `pyyaml>=6.0`; (b) U-RT-104 `_coerce_int_fields` helper RETIRED; (c) §3 (l) extended with 57th advisor application narrative.

### §0.3 Authoring rationale + the v2.41 reframing

Use-the-product probe finding #16/#17 (PR #79): `strictyaml.dirty_load` stringifies every YAML scalar; LLM SDKs reject string-typed `max_tokens`. Operators cannot run any `inference-step` workflow via YAML manifest at HEAD. Empirical reproduction: YAML manifest → `RetryBreakerFallbackExhaustedError`; same shape transcribed to TOML (tomllib preserves int) → `status=completed`.

Reading A operator-ratified 2026-05-29: replace `strictyaml.dirty_load` with `pyyaml.safe_load` via thin `StrictSafeLoader` subclass. Strictness motivation preserved (78-line shim bans duplicate keys + non-empty flow style + anchors/aliases); native YAML 1.1 scalar typing gained.

Q-set ratification: Q1=A (replace parser via shim); Q2=α (fixture switches to `pipeline-automation` + `single-threaded-linear` + `max_tokens: 8`); Q3→routes-to-PR-#80 (closed at PR #81); Q4=b (§14.19.4 invariant 8 becomes empirically true at apply); Q-H=b explicitly re-litigated and superseded at v1.39.

## §1 U-RT-104 unit-body amendment

| Field | v2.40 | v2.41 |
|---|---|---|
| Implements | runtime spec v1.38 §14.19 C-RT-30 WorkflowManifestLoader (Reading A topology admissibility deferred to runtime) | **runtime spec v1.39 §14.19 C-RT-30 WorkflowManifestLoader** (Reading A: pyyaml StrictSafeLoader replaces strictyaml.dirty_load; preserves native scalar typing; ZERO body-text amendment at §14.19 narrative) |
| Files | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` + 7 typed exception subclasses | **+ NEW `harness-runtime/src/harness_runtime/lifecycle/strict_safe_loader.py`** (78 lines; pyyaml SafeLoader subclass) |
| Signatures | `WorkflowManifestLoader.load(...)` + `_check_step_id_uniqueness(...)` + `_check_version(...)` + `_build_carrier(...)` + `_coerce_int_fields(...)` + `_parse_yaml(...)` | **`_coerce_int_fields(...)` RETIRED** (native typing makes it redundant); `_parse_yaml(...)` body refactored (strictyaml → strict_safe_load); `_check_version(...)` body simplified (rejects non-int directly). Other signatures PRESERVED VERBATIM. |
| Depends on | enum-validity carriers + WorkflowManifest Pydantic carrier + `strictyaml>=1.7` dep | enum-validity carriers + WorkflowManifest Pydantic carrier + **`pyyaml>=6.0` dep** (replaces strictyaml; declared at `harness-runtime/pyproject.toml`) |
| AC #4 native scalar typing | (implicit; not asserted at AC level pre-v1.39) | **NEW AC: YAML manifest loader preserves native int/float/bool scalar types per spec v1.39 Reading A.** Verified at NEW test `test_yaml_native_scalar_typing_per_v1_39_reading_a` (asserts `payload["max_tokens"] == 8` and `isinstance == int`; `temperature == 0.7` and `isinstance == float`). |
| AC #5 strictness preservation | (implicit; strictyaml strictness was opaque) | **NEW AC: StrictSafeLoader bans duplicate keys + non-empty flow style + anchors/aliases.** Verified at 3 NEW tests covering each ban. |
| AC #1-#11 + #13-#14 | PRESERVED VERBATIM from v2.40 | PRESERVED VERBATIM |
| Test names | (32 existing tests) | **+ 4 NEW tests**: `test_yaml_native_scalar_typing_per_v1_39_reading_a` + `test_yaml_duplicate_key_rejected_per_strict_safe_loader` + `test_yaml_anchor_alias_rejected_per_strict_safe_loader` + `test_yaml_version_as_string_rejected_per_v1_39_native_type_discipline`. |

## §2 DAG preservation

ZERO node addition / removal. ZERO edge addition / removal. v2.40 DAG PRESERVED VERBATIM.

## §3 Adjacent observations + carry-forward

(a) **Q-H=b ratification at G2 was an incomplete decision.** Strictness motivation preserved at G2; scalar-coercion consequence NOT considered. v1.39 re-litigates Q-H=b by preserving strictness via a thin SafeLoader subclass while gaining native scalar typing. The "strictness vs typing" tradeoff that Q-H=b implicitly accepted is closed at v1.39 — both properties can co-exist.

(b) **Probe-pattern + sibling PR #80 (PR #81 apply).** PR #79 + PR #80 are sibling forks at the YAML loader: PR #79 = scalar coercion gap; PR #80 = topology admissibility asymmetry. Both surfaced at the same use-the-product probe 2026-05-29; both required Reading A apply within 24h. Both close MVP-scope operator-facing YAML CLI usability gaps. v2.41 is the second of two stacked apply arcs (PR #81 first per smaller-blast-radius advisor recommendation; PR #79 apply second per parser-replacement larger-blast-radius).

(c) **YAML 1.1 boolean ambiguity preserved at YAML level (operator hygiene via quoting).** pyyaml SafeLoader resolves `yes` / `no` / `on` / `off` / `true` / `false` as booleans per YAML 1.1; operators wanting string-typed `tenant_id: "yes"` must quote. This is YAML 1.2's native rule — strictyaml's quoting requirement was a workaround for the same problem. Documented at fork doc §4(b) silent-corruption hazard mitigation 4.

(d) **`ManifestAdmissibilityError` class preserved in taxonomy** (carried from v2.40 §3 (d)). Still used at CLI app for engine_class admissibility per v1.36 Reading β. v1.39 + v2.41 do NOT amend the class.

(e) **ZERO cross-axis cascade per Q5=NONE.** Intra-runtime-spec amendment. CP spec PRESERVED VERBATIM. CP plan PRESERVED VERBATIM. AS / OD / IS / CXA / ADR / ADD / PRD PRESERVED VERBATIM. Target_Stack_Commitment_v1 §5.1 PRESERVED VERBATIM (operates at framework-pull-discipline layer; YAML parser implementation is intra-runtime-axis per spec v1.39).

(l) **57th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture.** Pre-substantive advisor consultation 2026-05-29 caught: (1) "~15 line shim" claim was conversational — verify empirically before authoring spec text (actual shim 78 LOC; ~50 actual code body; well within ~50-line target); (2) write full Q-set into fork doc Status block, not just "Reading A"; (3) apply-PR shape sequential separate PRs per fork. Empirical shim verification (78 LOC; 10/10 strictness tests pass) confirmed Reading A feasibility BEFORE spec authoring.

(m) **NEW pattern catalogued — `g2-en-bloc-ratification-probe-surface`.** Q-H=b (PR #79) + Q-(loader-admissibility) (PR #80) BOTH ratified en-bloc at Phase 2a G2 2026-05-28; both surfaced as Class 1 forks at use-the-product probe 2026-05-29; both required Reading A apply within 24h. Sub-species candidate at workflow §7.4.7.2 — `5.en-bloc-ratification-with-probe-eligible-carve-out`; cardinality 2 (Q-H=b + Q-(loader-admissibility)). Workflow-doc revision candidate when third instance surfaces.

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.41 (delta over v2.40) |
| Authored at | 2026-05-29 |
| Authoring authority | runtime spec v1.39 §14.19 Q-H=b re-litigation + Reading A operator ratification at fork doc Status block (`.harness/class_1_fork_yaml_loader_step_payload_scalar_coercion_gap.md`) |
| Net delta | U-RT-104 dep `strictyaml>=1.7` → `pyyaml>=6.0`; `_coerce_int_fields` retired; `_check_version` simplified; NEW `strict_safe_loader.py` module (78 lines); 4 NEW tests; ZERO new unit; ZERO DAG change; ZERO cross-axis cascade |
| Production binding | Co-published this arc: NEW `harness-runtime/.../lifecycle/strict_safe_loader.py`; EDIT `workflow_manifest_loader.py`; UPDATE `pyproject.toml`; UPDATE `minimal.yaml` + `minimal.toml` fixtures per Q2=α. 1305/1305 harness-runtime + 794/794 harness-cp tests pass. |
| Cross-axis cascade | NONE. CP spec / CP plan / AS / OD / IS / CXA / ADR / ADD / PRD PRESERVED VERBATIM. Target_Stack_Commitment_v1 §5.1 PRESERVED VERBATIM. |
| Downstream artifacts owed | workspace `CLAUDE.md` §2.3 + §2.4 row bumps (runtime spec v1.38 → v1.39; runtime plan v2.40 → v2.41) — co-published this arc; fork doc Status PROPOSING → ✅ APPLIED-AS-READING-A — co-published this arc; clearance marker at `.harness/clearance/Spec_Harness_Runtime-v1_39-cleared-2026-05-29.md` per CLAUDE.md §4.5 — co-published this arc |
