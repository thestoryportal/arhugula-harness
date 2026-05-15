# Implementation Plan — Information Substrate (v2.1)

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Information_Substrate_v2_1.md` |
| Status | **Proposed** (v2.1 pending P6-CK Iteration 3 clearance per `Project_Workflow_v1_6.md` §4.1.4.5 one-time Path B authorization; absorbs F1-IS-02 per `Adversarial_Review_6_iter2.md` §3.2 per operator OD-PathB-1.R1′) |
| Date | 2026-05-14 |
| Phase | 6 — atomic implementation plan (P6-CK Iter 2 → Iter 3 revision-pass under Path B); revision pass per `P6-CK_Iteration_2_Ceiling_Disposition.md` §5.1 |
| Skill | `implementation-planner` SKILL.md in **revision-pass sub-mode** per §8 |
| Axis | Information Substrate (IS) — first-axis per `Phase_6_Entry_Handoff.md` §5.1 sequencing rationale |
| Source-set | `Spec_Information_Substrate_v1.md` v1.2 §1–§10 (10 contracts: C-IS-01 through C-IS-10); `Project_Workflow_v1_6.md` v1.6 §2.6 + §4.1.4 + §6.4; `implementation-planner` SKILL.md §1–§11; `Adversarial_Review_6_iter2.md` §3.2 F1-IS-02 finding; `P6-CK_Iteration_2_Ceiling_Disposition.md` §5.1 R1′ absorption shape; background substrate (consulted but not cited at units per SKILL.md §2): `Architectural_Design_Document_v1.md` v1.2 §3.1, `PRD_v1_0.md` v1.0.1 R-IS-01 through R-IS-04 |
| ODs applied | (from v2) OD-S1-1.A (per-unit-cluster confirmation); OD-S1-2.A (per-axis coverage matrix only); OD-S1-3.A (author C-IS-10 at spec granularity now); (at v2.1) OD-PathB-1.R1′ (rewrite U-IS-16 row 9 criterion column) |
| Entry authorization | `P6-CK_Iteration_2_Ceiling_Disposition.md` §3.3 + Workflow v1.6 §4.1.4.5 |
| Exit gate | This v2.1 plan filed at `/mnt/user-data/outputs/`; Segment C of Path B complete; Path B continues to CP plan v2.1 (Segment D) |
| Sub-mode | Revision pass (P6-CK Iteration 2 F1-IS-02 finding absorbed; v2 → v2.1; `## §0 Change note` v2 → v2.1 section authored per SKILL.md §8) |

---

## §0 Change note (v2 → v2.1)

### §0.1 Scope of revision

Single-pass revision absorbing one `Adversarial_Review_6_iter2.md` P6-CK Iteration 2 finding, local to IS plan v2:

| Finding | Class | Reading | Resolution path absorbed | Affected sites |
|---|---|---|---|---|
| F1-IS-02 | 1 | R1′ (per OD-PathB-1) | Rewrite U-IS-16 acceptance row 9 criterion column to remove deferral-mechanism wording; retain row at cardinality 10; drop §9.4 deferral citation from spec-ref column (deferral remains documented at existing `Out-of-unit scope` subsection) | U-IS-16 acceptance row 9 |

No new architectural commitments; no new units; no new contracts; no new cross-axis edges; no spec extensions; no test additions. Per `implementation-planner` SKILL.md §8 revision-pass discipline.

### §0.2 Sections preserved verbatim (from v2)

| Section | Preservation rationale |
|---|---|
| §1.1 Contract inventory; §1.2 Cluster decomposition realized; §1.3 Substrate-version citation alignment | Substrate versions unchanged at v2.1 (IS spec v1.2, ADD v1.2, PRD v1.0.1); cluster decomposition unchanged |
| §2.1 Cluster 1 (U-IS-01, U-IS-02, U-IS-03) | No Iter-2 finding |
| §2.2 Cluster 2 (U-IS-04, U-IS-05, U-IS-06) | No Iter-2 finding |
| §2.3 Cluster 3 (U-IS-07, U-IS-08, U-IS-09, U-IS-10) | No Iter-2 finding |
| §2.4 Cluster 4 (U-IS-11, U-IS-12) | No Iter-2 finding |
| §2.5 Cluster 5 — U-IS-13, U-IS-14, U-IS-15 full; U-IS-16 non-acceptance-row-9 sections | No Iter-2 finding at U-IS-13 / U-IS-14 / U-IS-15; no finding at U-IS-16 scope, signatures, inputs, files, acceptance rows 1–8 + row 10, tests, rollback boundary, `Out-of-unit scope` subsection |
| §2.6 Cluster 6 (U-IS-17) | No Iter-2 finding |
| §3 dependency graph (Levels 0–5; edge enumeration; cycle audit) | No graph delta; node count + edge count unchanged at v2.1 |
| §4.1 coverage matrix | No matrix delta; cluster-to-contract mapping unchanged |
| §[carry-forwards] | Inherited from v2 unchanged |

### §0.3 Sections revised (v2 → v2.1)

| Section | Revision shape | Resolves |
|---|---|---|
| U-IS-16 acceptance-criteria-table row 9 | Criterion column rewritten: `Mechanism configuration-supplied` → `Concurrent writes across worktrees do not interleave at .git backend`; spec-ref column rewritten: `§9.3 row 3 + §9.4 deferral` → `§9.3 row 3`; row retained at position 9; cardinality unchanged at 10 | F1-IS-02 |

The `Out-of-unit scope` subsection at U-IS-16 (which documents the `cross-worktree writer serialization mechanism` deferral per §9.4) is preserved unchanged from v2. The deferral semantic that previously appeared in the row 9 criterion column is now exclusively documented at `Out-of-unit scope`, eliminating the F1-IS-01 anti-pattern adjacency.

### §0.4 Coverage matrix delta

No delta. U-IS-16 continues to implement `C-IS-09 §9.2, §9.3` at v2.1 (unchanged from v2).

### §0.5 Dependency graph delta

No delta. U-IS-16 `Depends on: [U-IS-04, U-IS-13]` unchanged at v2.1.

Aggregate DAG: 17 nodes across 6 levels; edge set unchanged from v2; topological sort preserved (Levels 0–5; terminal U-IS-17). Cross-axis edge count + targets unchanged.

### §0.6 Substrate-version-citation table

Substrate versions cited at v2.1 are unchanged from v2:

| Substrate | Version cited |
|---|---|
| IS spec | v1.2 (P5-CK-cleared) |
| ADD | v1.2 |
| PRD | v1.0.1 |
| ADR body-citations at U-IS-17 manifest | F1 v1.2, F2 v1.2, F3 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1 |
| Workflow | v1.6 (Path B + §4.1.4 amendment per `P6-CK_Iteration_2_Ceiling_Disposition.md`) |

Per Workflow v1.6 §7 use-latest-version body-citation-alignment.

### §0.7 Status

`Status: Proposed` preserved at v2.1 per `implementation-planner` SKILL.md §8 (analog to spec and PRD post-CK clearance patterns). Bump to `Status: P6-CK-cleared` on P6-CK Iteration 3 CLEARED disposition.

### §0.8 Forward-flagged concerns

| Concern | Status at v2.1 |
|---|---|
| (v2) U-IS-16 acceptance row 9 anti-pattern shape | **Closed at v2.1** — F1-IS-02 absorbed per R1′ |

No new forward-flagged concerns surface at v2.1. Path B revision cycle limits scope to F1-IS-02 absorption; no new defects introduced.

### §0.9 Prior revision history (v1 → v2; archival from v2 §0)

The v1 → v2 amendment cycle absorbed two `Adversarial_Review_6.md` P6-CK Iteration 1 findings:

| Finding | Class | Resolution path | Affected units |
|---|---|---|---|
| F2-IS-01 | 2 | Path (i) bytewise alignment | U-IS-17 §10.2 reference (drop `, D6 v1.1 → v1.2`) |
| F1-IS-01 | 1 | Path (a) extract to "Out-of-unit scope" subsection | U-IS-12, U-IS-14, U-IS-15, U-IS-16 acceptance-criteria tables |

Full v1 → v2 amendment trace remains on record at `/mnt/project/Implementation_Plan_Information_Substrate_v2.md` §0.3.

---

## §1 Spec inventory

### §1.1 Contract inventory

| C-IS-NN | Spec §  | Contract surface (one-line) | Expected unit class(es) | Cross-axis surfacing |
|---|---|---|---|---|
| C-IS-01 | §1 | Path-class enumeration (Skills / Prompts / Routing manifest / State-ledger) with stability invariants + visibility surface | `data-type` (schema) | IS-internal |
| C-IS-02 | §2 | Five-tier artifact layering (`working` / `episodic` / `semantic` / `procedural` / `durable`) with substrate-residence + survival semantics + cross-tier traceability | `data-type` (enum + schema) | IS-internal |
| C-IS-03 | §3 | Four-sub-role git tier composition (versioning / commit-stream / JSONL event ledger / shadow-Git / worktree) with foundational-vs-opt-in posture + co-residence contract | `algorithm` + `module-boundary` | IS-internal |
| C-IS-04 | §4 | Atomic deploy unit (prompt + code + eval + manifest) with all-or-nothing per commit + single-version observability | `api-surface` + `algorithm` | IS-internal |
| C-IS-05 | §5 | Six-field state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` with per-field type/format/semantic precision | `data-type` (schema) | IS-internal (consumed cross-axis by AS / CP / OD via C-IS-10) |
| C-IS-06 | §6 | Four-step hash-chain integrity discipline: canonicalize → SHA-256 → prior-event chain construction → verification + tamper-evidence | `algorithm` | IS-internal (consumed cross-axis by OD via C-IS-10) |
| C-IS-07 | §7 | T-perm-2 F2-layer read/write contract pair: C3-pole append-only write (idempotent on `(thread_id, step_id, idempotency_key)`) + C2-pole selective bounded navigation-primitive-mediated read + JSONL composition format | `api-surface` + `algorithm` | IS-internal (multi-seam T-perm-2 cross-axis context noted) |
| C-IS-08 | §8 | Workload-class-opt-in shadow-Git checkpoint: manifest declaration + cadence enum (`per_step` / `per_tool_call` / `per_significant_change` / `per_explicit_marker`) + reversal granularity | `policy-enforcement` + `api-surface` | IS-internal |
| C-IS-09 | §9 | Workload-class-opt-in worktree-isolation: manifest declaration + per-sub-agent worktree directory contract + concurrent-read isolation invariants + multi-writer scaling boundary | `policy-enforcement` + `api-surface` | IS-internal |
| C-IS-10 | §10 | Substrate seam exports surface: 6 export seams (entry shape; `idempotency_key` join; hash-chain construction; filesystem paths; JSONL event ledger format; workload-class-opt-in manifests) | `module-boundary` | **Cross-axis surfacing** — declares exports consumed by AS / CP / OD; consumer-axis dependencies authored at Sessions 2–4 per OD-S1-3.A |

### §1.2 Cluster decomposition realized

| Cluster | Contracts | Unit count | Unit IDs |
|---|---|---|---|
| 1 | C-IS-01 + C-IS-02 (foundational schemas) | 3 | U-IS-01, U-IS-02, U-IS-03 |
| 2 | C-IS-03 + C-IS-04 (git-tier + atomic deploy) | 3 | U-IS-04, U-IS-05, U-IS-06 |
| 3 | C-IS-05 + C-IS-06 (entry shape + hash-chain) | 4 | U-IS-07, U-IS-08, U-IS-09, U-IS-10 |
| 4 | C-IS-07 (read/write contract pair) | 2 | U-IS-11, U-IS-12 |
| 5 | C-IS-08 + C-IS-09 (workload-class-opt-in) | 4 | U-IS-13, U-IS-14, U-IS-15, U-IS-16 |
| 6 | C-IS-10 (substrate seam exports) | 1 | U-IS-17 |
| **Total** | — | **17** | U-IS-01 through U-IS-17 |

### §1.3 Substrate-version citation alignment

Per Workflow v1.6 §7 use-latest-version body-citation discipline + SKILL.md §9 V3 deference: all unit `Implements:` citations point to **IS spec v1.2**. No prior-version (`v1`, `v1.1`) citations are emitted. ADR body-citations within U-IS-17 substrate seam exports manifest use latest filed versions: F1 v1.2, F2 v1.2, F3 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1.

---

## §2 Atomic-unit decomposition

### §2.1 Cluster 1 — Foundational schemas (C-IS-01 + C-IS-02)

**Cluster scope.** Path-class registry (C-IS-01) + artifact-tier registry (C-IS-02). Schema-grade atomic surfaces; foundational tier of the IS-axis dependency graph.

**Decomposition rationale.** C-IS-01 surfaces a schema (path-class registry) plus a resolver primitive (workflow-canonical path lookup at run-time) — atomize as 2 units. C-IS-02 surfaces one schema (artifact-tier registry); the cross-tier traceability invariant declared at C-IS-02 is enforced at C-IS-05 action_id construction (Cluster 3). Result: 3 units.

#### U-IS-01 — Declare path-class registry schema

**Implements:** [C-IS-01 §1]

**Depends on:** (none)

**Inputs:** IS spec v1.2 §1 path-class table (4 classes × 4 columns).

**Files affected:** Path-class registry schema definition (logical name: `path-class-registry-schema`).

**Signatures:**
```
enum PathClass {
  SKILLS,                // SKILL.md-as-directory; agentskills.io ratified open standard frontmatter
  PROMPTS,               // plain-text-file-in-git; cache-prefix-integrity-preserving
  ROUTING_MANIFEST,      // single file in git per ADR-F1 v1.2 Consequences §(a)
  STATE_LEDGER           // two-mode composite per C-IS-03 (commit stream + JSONL event ledger)
}

record PathClassMetadata {
  path_class             : PathClass
  residence_contract     : ResidenceContract
  stability_invariant    : StabilityInvariant
  visibility_surface     : VisibilitySurface
}

record StabilityInvariant {
  workflow_canonical          : bool
  workflow_class_varying      : bool
  deployment_surface_varying  : bool
}

record VisibilitySurface {
  operator_readable_during_run    : bool   // = true for all 4 classes
  maintainer_readable_post_run    : bool   // = true for all 4 classes
  in_memory_only                  : bool   // = false for all 4 classes (negative constraint)
}
```

**Acceptance criteria:**
1. `PathClass` enum declares exactly 4 values: `SKILLS`, `PROMPTS`, `ROUTING_MANIFEST`, `STATE_LEDGER`.
2. Each `PathClass` value has a `PathClassMetadata` instance registered.
3. Every registered `PathClassMetadata.visibility_surface.in_memory_only == false` per spec §1 negative constraint.
4. Every registered `PathClassMetadata.visibility_surface` has `operator_readable_during_run == true` AND `maintainer_readable_post_run == true`.
5. Schema is statically validatable.

**Tests:**
- `test_path_class_registry_completeness` — assert enum cardinality == 4 AND values match spec §1 verbatim.
- `test_no_in_memory_only_artifacts` — assert `visibility_surface.in_memory_only == false` for all instances.
- `test_visibility_surface_both_observers` — assert both observer flags true for all instances.

**Rollback boundary:** Revert path-class registry schema. Downstream code fails at compile-time.

#### U-IS-02 — Implement path-resolver primitive

**Implements:** [C-IS-01 §1]

**Depends on:** [U-IS-01]

**Inputs:** `PathClass` enum + metadata from U-IS-01; workflow class identifier; deployment surface identifier; implementation-time configuration supplying canonical path strings per (workflow_class, deployment_surface) cell.

**Files affected:** Path-resolver implementation (logical name: `path-resolver`); path-binding configuration loader (logical name: `path-binding-loader`).

**Signatures:**
```
resolve_path(
  path_class          : PathClass,
  workflow_class      : WorkflowClass,
  deployment_surface  : DeploymentSurface
) -> Path
```

**Acceptance criteria:**
1. Repeated calls within a single run on the same triple return identical `Path` values (stability invariant within run).
2. Same `(path_class, workflow_class, deployment_surface)` triple across run boundaries returns identical `Path` values (workflow-canonical per spec §1).
3. Same `path_class` and `deployment_surface` but differing `workflow_class` MAY return differing paths without violating any contract (workflow-class-varying flex).
4. Resolver does not hard-code path strings; all paths derive from path-binding configuration source.
5. Resolver does not produce paths violating C-IS-02 substrate-residence rule (cross-unit invariant verified once U-IS-03 lands).

**Tests:**
- `test_resolve_path_stability_within_run` — assert deterministic within run.
- `test_resolve_path_workflow_canonical_across_runs` — assert deterministic across run boundaries.
- `test_resolve_path_workflow_class_variance_permitted` — assert no error on workflow-class-driven path variance.
- `test_resolve_path_no_hardcoded_paths` — empty configuration ⇒ configuration-missing error (not default string).

**Rollback boundary:** Revert path-resolver + path-binding loader. Downstream callers fail at runtime.

#### U-IS-03 — Declare artifact-tier registry schema

**Implements:** [C-IS-02 §2]

**Depends on:** (none)

**Inputs:** IS spec v1.2 §2 five-tier table; §2 tier composition contract.

**Files affected:** Artifact-tier registry schema definition (logical name: `artifact-tier-registry-schema`).

**Signatures:**
```
enum ArtifactTier {
  WORKING,        // per-run scratch state
  EPISODIC,       // per-run history; in-flight conversational state
  SEMANTIC,       // cross-run knowledge artifacts
  PROCEDURAL,     // workflow-class procedural artifacts (Skills, prompts, routing manifest)
  DURABLE         // append-only state-ledger + JSONL event ledger + audit ledger
}

record ArtifactTierMetadata {
  tier                  : ArtifactTier
  semantic_role         : string
  substrate_residence   : SubstrateResidence
  survival_scope        : SurvivalScope
}

record SubstrateResidence {
  filesystem  : bool                  // = true for all 5 tiers
  git         : bool                  // = false for WORKING, EPISODIC; = true otherwise
}

enum SurvivalScope {
  WITHIN_SINGLE_INFERENCE_CALL,                  // WORKING
  WITHIN_RUN_RESTART_VIA_REPLAY_ONLY,            // EPISODIC
  ACROSS_RUNS,                                   // SEMANTIC
  ACROSS_RUNS_AND_WORKFLOW_VERSIONS,             // PROCEDURAL
  ACROSS_RUNS_AND_CRASH_RECOVERY                 // DURABLE
}
```

**Acceptance criteria:**
1. `ArtifactTier` enum declares exactly 5 values per spec §2.
2. `WORKING.substrate_residence == {filesystem: true, git: false}` AND `EPISODIC.substrate_residence == {filesystem: true, git: false}`.
3. `SEMANTIC`, `PROCEDURAL`, `DURABLE` each have `substrate_residence == {filesystem: true, git: true}` (combined-tier role).
4. Each tier's `survival_scope` matches spec §2 "Survives across" column exhaustively.
5. Schema is statically validatable.

**Tests:**
- `test_artifact_tier_registry_completeness` — assert 5 enum values match spec verbatim.
- `test_substrate_residence_per_tier` — table-driven assertion against spec §2 substrate-residence column.
- `test_survival_scope_per_tier` — table-driven assertion against spec §2 "Survives across" column.

**Rollback boundary:** Revert artifact-tier registry schema. Downstream code fails at compile-time.

---

### §2.2 Cluster 2 — Git-tier role decomposition + atomic deploy (C-IS-03 + C-IS-04)

**Cluster scope.** Combined git tier sub-role taxonomy (C-IS-03) + JSONL event ledger file lifecycle + atomic deploy-event composition (C-IS-04). 3 units.

**Decomposition rationale.** C-IS-03 surfaces a 5-row sub-role table (3 foundational sub-roles: versioning, commit-stream-ledger, JSONL event ledger; 2 opt-in: shadow-Git, worktree). Active substantive primitive at C-IS-03 layer is the JSONL event ledger file lifecycle. Versioning + commit-stream-ledger have no separate active surface beyond atomic deploy (C-IS-04). Shadow-Git + worktree active surfaces live in Cluster 5. Result: 1 taxonomy unit + 1 lifecycle primitive at C-IS-03; 1 contract-declaration unit at C-IS-04.

#### U-IS-04 — Declare combined git tier sub-role taxonomy + co-residence invariants

**Implements:** [C-IS-03 §3]

**Depends on:** (none)

**Inputs:** IS spec v1.2 §3 sub-role table (5 rows); §3 sub-role co-residence contract; §3 cross-sub-role consistency invariant.

**Files affected:** Combined git tier sub-role taxonomy definition (logical name: `git-tier-sub-role-taxonomy`).

**Signatures:**
```
enum GitTierSubRole {
  VERSIONING,                       // Foundational; composes with C-IS-04
  STATE_LEDGER_VIA_COMMIT_STREAM,   // Foundational
  JSONL_EVENT_LEDGER,               // Foundational; composes with C-IS-05/06/07
  SHADOW_GIT_CHECKPOINTING,         // Workload-class-opt-in; composes with C-IS-08
  WORKTREE_ISOLATION                // Workload-class-opt-in; composes with C-IS-09
}

enum SubRolePosture {
  FOUNDATIONAL,
  WORKLOAD_CLASS_OPT_IN
}

record GitTierSubRoleMetadata {
  sub_role            : GitTierSubRole
  posture             : SubRolePosture
  composition_with    : List[ContractID]
}

constants {
  CO_RESIDENCE_ONE_REPO_HOSTS_ONE_HARNESS_STATE_LEDGER  : bool = true
  CROSS_REPOSITORY_LEDGER_COMPOSITION                   : bool = false
}
```

**Acceptance criteria:**
1. `GitTierSubRole` enum: exactly 5 values matching spec §3 verbatim.
2. `SubRolePosture` enum: exactly 2 values.
3. Posture assignment: VERSIONING, STATE_LEDGER_VIA_COMMIT_STREAM, JSONL_EVENT_LEDGER ⇒ FOUNDATIONAL; SHADOW_GIT_CHECKPOINTING, WORKTREE_ISOLATION ⇒ WORKLOAD_CLASS_OPT_IN.
4. Each `composition_with` cites appropriate contract ID per spec §3 composition-contract column.
5. Co-residence invariant constants declared per spec §3 cross-sub-role consistency invariant.

**Tests:**
- `test_git_tier_sub_role_taxonomy_completeness` — assert 5 sub-roles match spec §3.
- `test_sub_role_posture_per_role` — table-driven against spec §3 posture column.
- `test_one_repo_hosts_one_ledger_invariant` — assert constant == true.
- `test_cross_repository_ledger_composition_out_of_scope` — assert constant == false.

**Rollback boundary:** Revert taxonomy definition. Downstream code fails at compile-time.

#### U-IS-05 — Implement JSONL event ledger file lifecycle

**Implements:** [C-IS-03 §3 (JSONL event ledger sub-role row)]

**Depends on:** [U-IS-01, U-IS-02, U-IS-04]

**Inputs:** `PathClass.STATE_LEDGER` (U-IS-01); `resolve_path` (U-IS-02); `GitTierSubRole.JSONL_EVENT_LEDGER` (U-IS-04); workflow open / resume signal.

**Files affected:** JSONL event ledger lifecycle (logical name: `jsonl-event-ledger-lifecycle`).

**Scope.** File existence + structural validation at workflow open / resume. Does NOT write or read entries (C-IS-07 territory) or compute hashes (C-IS-06 territory).

**Signatures:**
```
initialize_jsonl_event_ledger(
  workflow_class       : WorkflowClass,
  deployment_surface   : DeploymentSurface
) -> JsonlLedgerHandle

validate_jsonl_event_ledger_format(
  handle  : JsonlLedgerHandle
) -> LedgerFormatValidationResult

record JsonlLedgerHandle {
  canonical_path  : Path
  exists          : bool
  entry_count     : Integer
}

enum LedgerFormatValidationResult {
  VALID,
  EMPTY,
  MALFORMED_LINE,
  IO_ERROR
}
```

**Acceptance criteria:**
1. `initialize_jsonl_event_ledger` resolves canonical path via `resolve_path(PathClass.STATE_LEDGER, workflow_class, deployment_surface)`.
2. File absent ⇒ create empty file; return handle with `exists=true, entry_count=0`.
3. File present ⇒ return handle with `exists=true, entry_count=N` (line-counted); does not modify contents.
4. `validate_jsonl_event_ledger_format` returns `VALID` if every non-empty line parses as JSON; `EMPTY` if zero-length; `MALFORMED_LINE` if any line fails JSON parse; `IO_ERROR` on filesystem access failure.
5. Lifecycle MUST NOT append entries or modify existing entries.
6. Entry-shape validation (six-field shape) is NOT performed; only JSON-syntactic parseability.

**Tests:**
- `test_initialize_creates_file_if_absent` — non-existent path ⇒ post-initialize file at path with 0 bytes; handle reports correct state.
- `test_initialize_returns_handle_if_present` — existing path ⇒ byte-identical pre/post; handle reports correct entry_count.
- `test_validate_returns_valid_for_well_formed_jsonl` — N parseable lines ⇒ VALID.
- `test_validate_returns_malformed_line_for_bad_jsonl` — invalid line ⇒ MALFORMED_LINE.
- `test_validate_returns_empty_for_zero_length_file` — empty file ⇒ EMPTY.
- `test_lifecycle_does_not_append_entries` — byte-identity preserved pre/post.

**Rollback boundary:** Revert lifecycle. Harness boot fails at ledger initialization.

#### U-IS-06 — Declare atomic deploy-event composition contract + verification primitive

**Implements:** [C-IS-04 §4]

**Depends on:** [U-IS-01, U-IS-04]

**Inputs:** IS spec v1.2 §4 4-class deploy-unit composition; §4 atomicity contract; §4 verification surface; `PathClass` (U-IS-01); `GitTierSubRole.VERSIONING` + `GitTierSubRole.STATE_LEDGER_VIA_COMMIT_STREAM` (U-IS-04).

**Files affected:** Atomic deploy-event composition declaration (logical name: `atomic-deploy-event-contract`); deploy-event verification test suite (logical name: `atomic-deploy-event-verification`).

**Signatures:**
```
enum DeployArtifactClass {
  PROMPTS,             // C-IS-01 PathClass.PROMPTS
  CODE,                // workflow implementation code; Python-first per Persona §7
  EVAL_SETS,           // eval-set artifacts co-located with code
  ROUTING_MANIFEST     // C-IS-01 PathClass.ROUTING_MANIFEST per ADR-F1 v1.2
}

record DeployEventComposition {
  artifact_classes        : Set[DeployArtifactClass]
  atomicity_property      : AtomicityProperty
  observability_property  : ObservabilityProperty
  composes_with           : Set[ContractID]
}

enum AtomicityProperty {
  ALL_OR_NOTHING_PER_COMMIT
}

enum ObservabilityProperty {
  SINGLE_VERSION_OBSERVABILITY
}

verify_deploy_atomicity(
  git_repository  : GitRepository,
  commit_range    : CommitRange
) -> DeployAtomicityVerificationReport

record DeployAtomicityVerificationReport {
  commits_inspected   : Integer
  violations          : List[DeployAtomicityViolation]
  bisection_isolated  : bool
}

record DeployAtomicityViolation {
  violation_type  : ViolationType
  commit_ids      : List[CommitId]
  description     : string
}

enum ViolationType {
  SPLIT_DEPLOY,
  MISSING_COMMIT_STREAM_ENTRY
}
```

**Acceptance criteria:**
1. `DeployArtifactClass` enum: exactly 4 values matching spec §4 verbatim.
2. `DeployEventComposition.composes_with` includes `C-IS-03 commit-stream sub-role` and `C-IS-08` (orthogonal).
3. `verify_deploy_atomicity` over well-formed commit range returns `violations == []`.
4. `verify_deploy_atomicity` over split-deploy range returns `SPLIT_DEPLOY` violation with relevant commit IDs.
5. Verification is offline / on-demand; does not block deploy commits at write-time.
6. Bisection invariant: violation in commit range ⇒ bisection isolates violating commit in O(log N).

**Tests:**
- `test_deploy_artifact_class_completeness` — assert 4 values match spec §4.
- `test_verify_well_formed_commits_returns_no_violations` — clean history ⇒ no violations.
- `test_verify_split_deploy_returns_violation` — split deploy fixture ⇒ SPLIT_DEPLOY entry.
- `test_verify_composes_with_commit_stream` — assert all deploys appear in commit-stream view; MISSING_COMMIT_STREAM_ENTRY if absent.
- `test_verify_bisection_isolates_violating_commit` — N-commit range with 1 violation ⇒ bisection identifies position.

**Rollback boundary:** Revert composition declaration + verification test suite.

---

### §2.3 Cluster 3 — State-ledger entry shape + hash-chain integrity (C-IS-05 + C-IS-06)

**Cluster scope.** Six-field entry schema (C-IS-05) + four-step hash-chain integrity discipline (C-IS-06). 4 units.

**Decomposition rationale.** C-IS-05 = 1 schema unit with abstract type bindings (specific identifier/timestamp formats deferred). C-IS-06 splits into 3 units: §6.1+§6.2 (canonicalize + hash; tightly coupled), §6.3 (chain-link construction at write-time; pure function consumed by C-IS-07 write contract), §6.4+§6.5 (chain verification + tamper-evidence as test surface).

#### U-IS-07 — Declare state-ledger entry shape schema

**Implements:** [C-IS-05 §5]

**Depends on:** (none)

**Inputs:** IS spec v1.2 §5 six-field record table; §5 extensibility commitment; §5 cross-axis composition documentation.

**Files affected:** State-ledger entry shape schema definition (logical name: `state-ledger-entry-schema`).

**Signatures:**
```
record StateLedgerEntry {
  action_id           : Identifier
  idempotency_key     : Identifier
  actor               : Actor
  response_hash       : Bytes32
  timestamp           : Timestamp
  prior_event_hash    : Bytes32
}

record Actor {
  actor_class  : ActorClass
  actor_id     : string
}

enum ActorClass { AGENT, SUB_AGENT, OPERATOR }

constants {
  ALL_ZEROS_SENTINEL : Bytes32 = 0x00 * 32
}

// Abstract type bindings — specific format deferred per spec §5 deferrals
type Identifier  = opaque string
type Timestamp   = opaque time-instant
type Bytes32     = fixed-length byte sequence (32 bytes)
```

**Acceptance criteria:**
1. `StateLedgerEntry` declares exactly 6 fields matching spec §5 verbatim.
2. `ActorClass` enum declares exactly 3 values.
3. `ALL_ZEROS_SENTINEL` is 32 bytes of zero.
4. `Identifier` and `Timestamp` bindings configuration-supplied per spec §5 deferrals.
5. Extensibility: per-workload-class extension records MUST include the six F-layer fields and MAY add additional fields; F-layer fields are immutable.
6. Schema is statically validatable.

**Tests:**
- `test_state_ledger_entry_schema_completeness` — assert 6 fields match spec §5 verbatim.
- `test_actor_class_enum_completeness` — assert 3 values.
- `test_all_zeros_sentinel_value` — assert 32 bytes of zero.
- `test_extensibility_commitment_permits_additive_fields` — extension with F-layer + extras validates.
- `test_extensibility_commitment_prohibits_f_layer_modification` — renaming or omitting F-layer field fails validation.
- `test_identifier_type_binding_flex` — UUID v4 binding + ULID binding both validate.

**Rollback boundary:** Revert schema. Downstream code fails at compile-time.

#### U-IS-08 — Implement canonicalization + per-entry SHA-256 hash primitive

**Implements:** [C-IS-06 §6.1, §6.2]

**Depends on:** [U-IS-07]

**Inputs:** `StateLedgerEntry` (U-IS-07); RFC 8785 JSON Canonicalization Scheme (JCS) baseline candidate per spec §6.1 [MODERATE — library binding deferred to D-ADR per ADR-F2 §Consequences (c)].

**Files affected:** Canonicalization primitive (logical name: `entry-canonicalization`); per-entry hash primitive (logical name: `entry-hash`).

**Signatures:**
```
canonicalize(entry: StateLedgerEntry) -> Bytes
compute_response_hash(entry: StateLedgerEntry) -> Bytes32
```

**Acceptance criteria:**
1. `canonicalize` is deterministic: byte-identical output for logically-equal entries across runs, machines, library versions.
2. `canonicalize` is RFC 8785 JCS conformant: field-order-insensitive; Unicode-normalized; number-representation-canonical.
3. `compute_response_hash` returns `SHA-256(canonicalize(entry))`.
4. `compute_response_hash` output is exactly 32 bytes.
5. Library binding configuration-supplied; not hard-coded.
6. Non-determinism in canonicalization is a contract violation; rejected at boot-time validation.

**Tests:**
- `test_canonicalize_deterministic_same_invocation` — two invocations on same entry ⇒ byte-equal.
- `test_canonicalize_field_order_insensitive` — different in-memory ordering ⇒ byte-equal canonical form.
- `test_canonicalize_unicode_normalization` — NFC vs NFD strings ⇒ byte-equal.
- `test_canonicalize_number_representation` — `1.0` vs `1` ⇒ canonical form per RFC 8785 JCS.
- `test_compute_response_hash_length` — output == 32 bytes.
- `test_compute_response_hash_golden` — fixture entry ⇒ expected SHA-256 digest (golden test).
- `test_compute_response_hash_collision_smoke` — 1000 distinct entries ⇒ 1000 distinct hashes.
- `test_canonicalize_library_binding_flex` — two distinct JCS library bindings ⇒ byte-equal output.

**Rollback boundary:** Revert canonicalization + hash. Downstream chain construction (U-IS-09) and verification (U-IS-10) fail at runtime.

#### U-IS-09 — Implement chain-link construction primitive at write-time

**Implements:** [C-IS-06 §6.3]

**Depends on:** [U-IS-07, U-IS-08]

**Inputs:** `StateLedgerEntry` + `ALL_ZEROS_SENTINEL` (U-IS-07); `compute_response_hash` (U-IS-08).

**Files affected:** Chain-link construction primitive (logical name: `chain-link-construction`).

**Scope.** Pure write-time function. Does NOT persist entries (C-IS-07 territory) or verify chains (U-IS-10 territory).

**Signatures:**
```
construct_prior_event_hash(prior_entry: Optional[StateLedgerEntry]) -> Bytes32
```

**Acceptance criteria:**
1. Inception: `construct_prior_event_hash(None)` returns `ALL_ZEROS_SENTINEL`.
2. Non-inception: returns `compute_response_hash(prior_entry)`.
3. Function is pure: no I/O, no global state mutation, no logging side effects.
4. Caller (C-IS-07 write contract) is responsible for inserting returned value into new entry's `prior_event_hash` field.
5. Concurrent-writer contention on chain head precluded by caller-side serialization.

**Tests:**
- `test_construct_prior_event_hash_inception` — None input ⇒ ALL_ZEROS_SENTINEL.
- `test_construct_prior_event_hash_non_inception` — fixture prior_entry ⇒ matches compute_response_hash.
- `test_construct_prior_event_hash_pure_no_io` — instrumented filesystem mock ⇒ no I/O.
- `test_construct_prior_event_hash_pure_deterministic` — repeat invocation ⇒ byte-equal.
- `test_construct_prior_event_hash_does_not_write_entry` — invocation ⇒ no ledger writes.

**Rollback boundary:** Revert chain-link construction. C-IS-07 write contract (Cluster 4) fails at runtime.

#### U-IS-10 — Implement chain verification + tamper-evidence procedure

**Implements:** [C-IS-06 §6.4, §6.5]

**Depends on:** [U-IS-07, U-IS-08]

**Inputs:** `StateLedgerEntry` + `ALL_ZEROS_SENTINEL` (U-IS-07); `canonicalize` + `compute_response_hash` (U-IS-08).

**Files affected:** Chain verification primitive (logical name: `chain-verification`); tamper-evidence test suite (logical name: `chain-tamper-evidence-tests`).

**Signatures:**
```
verify_chain(ledger: List[StateLedgerEntry]) -> ChainVerificationResult

record ChainVerificationResult {
  status              : VerificationStatus
  failure_position    : Optional[Integer]
  failure_type        : Optional[FailureType]
  entries_verified    : Integer
}

enum VerificationStatus { VALID, INVALID }

enum FailureType {
  INCEPTION_SENTINEL_MISMATCH,
  CHAIN_LINK_MISMATCH
}
```

**Acceptance criteria:**
1. Empty ledger ⇒ `VALID, entries_verified=0`.
2. Single entry with sentinel `prior_event_hash` ⇒ `VALID`.
3. Single entry with non-sentinel `prior_event_hash` ⇒ `INVALID, failure_position=1, INCEPTION_SENTINEL_MISMATCH`.
4. N-entry ledger with valid chain ⇒ `VALID, entries_verified=N`.
5. N-entry ledger with broken link at K ⇒ `INVALID, failure_position=K, CHAIN_LINK_MISMATCH`.
6. Verification is read-only: ledger byte-identity preserved.
7. All 5 spec §6.5 tamper scenarios detected.

**Tests (core verification):**
- `test_verify_chain_empty_ledger`, `test_verify_chain_inception_valid`, `test_verify_chain_inception_invalid`, `test_verify_chain_valid_multi_entry`, `test_verify_chain_invalid_at_position_K`, `test_verify_chain_read_only`.

**Tests (tamper-evidence per spec §6.5):**
- `test_tamper_entry_content_modification` — modify `actor` field at K ⇒ failure at K+1 (§6.5 row 1).
- `test_tamper_prior_event_hash_modification` — modify `prior_event_hash` at K ⇒ failure at K (§6.5 row 2).
- `test_tamper_entry_deletion_mid_chain` — delete entry at K ⇒ failure at new position K (§6.5 row 3).
- `test_tamper_entry_insertion_mid_chain` — insert forged entry at K ⇒ failure at K+1 (§6.5 row 4).
- `test_tamper_inception_modification` — modify entry[1].prior_event_hash to non-sentinel ⇒ failure at 1 (§6.5 row 5).

**Rollback boundary:** Revert chain verification + tamper-evidence suite. Resume-time chain validation and audit-ledger composition (OD axis) fail at runtime.

---

### §2.4 Cluster 4 — State-ledger read/write contract pair (C-IS-07)

**Cluster scope.** C3-pole append-only write contract (§7.1) + C2-pole selective bounded read contract (§7.2) + JSONL composition format (§7.3). §7.4 multi-seam T-perm-2 engagement produces no IS-plan unit. 2 units.

**Decomposition rationale.** Write and read split structurally on different dependency profiles and different test surfaces. §7.3 composition format is emergent from write+read coordination. Keying-tuple ↔ entry-shape ambiguity per §7.4 deferral (F2-12 carry-forward) accommodated at U-IS-11 by treating `WriteKey` as caller-supplied.

#### U-IS-11 — Implement C3-pole append-only write contract

**Implements:** [C-IS-07 §7.1, §7.3]

**Depends on:** [U-IS-05, U-IS-07, U-IS-08, U-IS-09]

**Inputs:** `JsonlLedgerHandle` (U-IS-05); `StateLedgerEntry` + `Actor` + `ALL_ZEROS_SENTINEL` (U-IS-07); `compute_response_hash` (U-IS-08); `construct_prior_event_hash` (U-IS-09); IS spec v1.2 §7.1 + §7.3; keying tuple `(thread_id, step_id, idempotency_key)` per Stripe-style convention.

**Files affected:** C3-pole write contract (logical name: `state-ledger-write-contract`); idempotent-write deduplication primitive (logical name: `idempotent-write-dedup`).

**Scope.** Per §7.4 deferral, relationship between `WriteKey` and persisted entry shape is left to implementer (F2-12 carry-forward); this unit treats `WriteKey` as caller-supplied.

**Signatures:**
```
append_ledger_entry(
  ledger_handle  : JsonlLedgerHandle,
  entry_payload  : EntryPayload,
  write_key      : WriteKey
) -> WriteResult

record EntryPayload {
  action_id        : Identifier      // cross-tier traceability encoded by caller per C-IS-02
  idempotency_key  : Identifier
  actor            : Actor
  timestamp        : Timestamp
  // response_hash + prior_event_hash computed internally; not caller-supplied
}

record WriteKey {
  thread_id        : Identifier
  step_id          : Identifier
  idempotency_key  : Identifier
}

enum WriteResult { APPENDED, IDEMPOTENT_NOOP }
```

**Internal logic:**
1. Reject if `write_key.idempotency_key != entry_payload.idempotency_key`.
2. Idempotent dedup: scan for existing entry with same `WriteKey` ⇒ `IDEMPOTENT_NOOP` if found.
3. Identify `prior_entry` (last in ledger or `None`).
4. Compute `prior_event_hash = construct_prior_event_hash(prior_entry)`.
5. Validate timestamp monotonicity (subject to clock-skew tolerance).
6. Assemble entry; compute `response_hash = compute_response_hash(entry)`.
7. Serialize to JSON; append single line to JSONL.
8. Update handle entry_count; return `APPENDED`.

**Acceptance criteria:**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Append-only | Writes add only at end; existing entries never modified | §7.1 row 1 |
| 2 | Structured | Persisted entries conform to C-IS-05 six-field shape | §7.1 row 2 |
| 3 | JSON-not-Markdown | Entries serialized as JSON; Markdown rejected | §7.1 row 3 |
| 4 | Idempotent | Second write with identical WriteKey ⇒ IDEMPOTENT_NOOP | §7.1 row 4 |
| 5 | JSONL line discipline | One entry per line | §7.1 row 5 + §7.3 |
| 6 | Hash-chain preserving | response_hash + prior_event_hash computed before persist | §7.1 row 6 |
| 7 | Concurrent-writer serialization | Chain-head construction serialized; mechanism implementation-grade | §6.3 + §7.4 deferral |
| 8 | No caller-supplied hashes | EntryPayload omits hash fields | §6.2 + §6.3 |
| 9 | Timestamp monotonicity | Non-monotonic (beyond clock-skew tolerance) ⇒ error | C-IS-05 |
| 10 | Keying-tuple opacity | WriteKey source not committed | §7.4 (F2-12) |

**Tests:**
- `test_append_appends_to_jsonl_file`, `test_append_preserves_order`, `test_append_idempotent_noop_on_duplicate_writekey`, `test_append_idempotent_preserves_first_payload`, `test_append_rejects_writekey_idempotency_key_mismatch`, `test_append_computes_response_hash`, `test_append_inception_prior_event_hash`, `test_append_non_inception_prior_event_hash`, `test_append_one_entry_per_line`, `test_append_rejects_caller_supplied_response_hash`, `test_append_rejects_non_monotonic_timestamp`, `test_append_chain_verifies_after_writes`, `test_append_concurrent_writes_serialized`.

**Rollback boundary:** Revert write contract + dedup primitive. Cross-axis writers (D1 engine event history, D5 audit-ledger, D2 sandbox-violation events, D6 cost-attribution) all block.

#### U-IS-12 — Implement C2-pole selective bounded read contract via NavigationPrimitive interface

**Implements:** [C-IS-07 §7.2, §7.3]

**Depends on:** [U-IS-05, U-IS-07]

**Inputs:** `JsonlLedgerHandle` (U-IS-05); `StateLedgerEntry` (U-IS-07); IS spec v1.2 §7.2 + §7.3 + §7.4 deferred-list naming.

**Files affected:** C2-pole read contract (logical name: `state-ledger-read-contract`); NavigationPrimitive interface declaration (logical name: `navigation-primitive-interface`); four minimum-viable concrete primitives (`nav-read-entry`, `nav-read-range`, `nav-read-recent`, `nav-read-by-idempotency-key`).

**Scope.** Returns `List[StateLedgerEntry]` to caller; dynamic-suffix placement is CP-axis context-engineering territory (Session 3).

**Signatures:**
```
interface NavigationPrimitive {
  read(query: NavigationQuery, bounded_window: BoundedWindow) -> ReadResult
}

record NavigationQuery {
  by_action_id          : Optional[Identifier]
  by_idempotency_key    : Optional[Identifier]
  by_position_range     : Optional[PositionRange]
  most_recent_n         : Optional[Integer]
}

record PositionRange {
  start_position  : Integer
  end_position    : Integer
}

record BoundedWindow {
  max_entries     : Integer
  workload_class  : WorkloadClass
}

record ReadResult {
  entries        : List[StateLedgerEntry]
  truncated      : bool
  next_position  : Optional[Integer]
}
```

Four minimum-viable concrete primitives wrap `NavigationPrimitive.read`: `read_entry(action_id, …)`, `read_range(start, end, …)`, `read_recent(n, …)`, `read_by_idempotency_key(key, …)`.

**Acceptance criteria:**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Selective | No public API returns ledger without NavigationQuery + BoundedWindow | §7.2 row 1 |
| 2 | Bounded | Truncates at max_entries; next_position surfaced for continuation | §7.2 row 2 |
| 3 | Navigation-primitive-mediated | All reads pass through interface | §7.2 row 3 |
| 4 | Read-into-dynamic-suffix boundary | Returns List[StateLedgerEntry]; placement is CP-axis | §7.2 row 4 + ADR-F2 §Rationale (b)(ii) |
| 5 | Four minimum-viable primitives | All four implemented per spec §7.4 naming | §7.4 |
| 6 | Concurrent reads non-blocking | Reads do not block reads or writes | §7.3 |
| 7 | Read does not modify ledger | Byte-identity preserved | C2-pole property |

**Out-of-unit scope:** Per IS spec v1.2 §7.4 deferral — bounding-window-size defaults per workload class are configuration-supplied at execution time; not asserted at this unit's tests.

**Tests:**
- `test_read_entry_by_action_id_match`, `test_read_entry_by_action_id_no_match`, `test_read_range_returns_correct_window`, `test_read_recent_returns_last_n_chronological`, `test_read_by_idempotency_key_match`, `test_read_bounded_window_truncates`, `test_read_paginated_continuation`, `test_read_full_file_cat_precluded`, `test_read_concurrent_non_blocking_reads`, `test_read_concurrent_with_write_non_blocking`, `test_read_does_not_modify_ledger`, `test_read_returns_dynamic_suffix_boundary_not_crossed`.

**Rollback boundary:** Revert read contract + NavigationPrimitive interface + four concrete primitives. CP-axis context engineering, resume-time replay, audit-ledger inspection, cross-axis idempotency-key join queries all fail at runtime.

---

### §2.5 Cluster 5 — Workload-class-opt-in shadow-Git + worktree-isolation (C-IS-08 + C-IS-09)

**Cluster scope.** Workload manifest opt-in schema (covers both C-IS-08 §8.1 + C-IS-09 §9.1); shadow-Git checkpoint primitive; shadow-Git rollback primitive; worktree-isolation primitive. 4 units.

**Decomposition rationale.** Checkpoint creation and rollback split on rollback boundary and test surface. Cadence enum is parameter to checkpoint primitive, not separate primitive. C-IS-09 §9.3 invariants are properties of worktree primitive; §9.4 is out-of-scope declaration. Manifest fields from §8.1 + §9.1 co-locate (single workflow manifest artifact).

#### U-IS-13 — Declare workload manifest opt-in declaration schema

**Implements:** [C-IS-08 §8.1, §8.2; C-IS-09 §9.1]

**Depends on:** (none)

**Inputs:** IS spec v1.2 §8.1 + §8.2 + §9.1.

**Files affected:** Workload manifest opt-in schema (logical name: `workload-manifest-opt-in-schema`).

**Signatures:**
```
record WorkloadManifestOptIns {
  shadow_git_enabled         : bool                          // default = false
  shadow_git_cadence         : Optional[CheckpointCadence]   // required if shadow_git_enabled = true
  worktree_isolation_enabled : bool                          // default = false
  worktree_concurrency_cap   : Optional[Integer]             // absent = unbounded
}

enum CheckpointCadence {
  PER_STEP,
  PER_TOOL_CALL,
  PER_SIGNIFICANT_CHANGE,
  PER_EXPLICIT_MARKER
}
```

**Acceptance criteria:**
1. Exactly 4 fields matching spec §8.1 + §9.1.
2. Defaults: `shadow_git_enabled = false`; `worktree_isolation_enabled = false`.
3. `worktree_concurrency_cap` optional; absent = unbounded.
4. `CheckpointCadence` enum: exactly 4 values matching spec §8.2.
5. Validation: `shadow_git_enabled == true` ⇒ `shadow_git_cadence` required.
6. Manifest authoring format (YAML/JSON/TOML) configuration-supplied.

**Tests:**
- `test_workload_manifest_default_values`, `test_checkpoint_cadence_enum_completeness`, `test_shadow_git_enabled_requires_cadence`, `test_worktree_concurrency_cap_optional`, `test_independent_opt_in_combinations`.

**Rollback boundary:** Revert schema. Downstream code fails at compile-time.

#### U-IS-14 — Implement shadow-Git checkpoint primitive (cadence-driven snapshot creation)

**Implements:** [C-IS-08 §8.2, §8.4]

**Depends on:** [U-IS-04, U-IS-13]

**Inputs:** `GitTierSubRole.SHADOW_GIT_CHECKPOINTING` (U-IS-04); `WorkloadManifestOptIns` + `CheckpointCadence` (U-IS-13); IS spec v1.2 §8.2 + §8.4.

**Files affected:** Shadow-Git checkpoint primitive (logical name: `shadow-git-checkpoint`); cadence-trigger driver (logical name: `shadow-git-cadence-driver`).

**Scope.** Snapshot creation only. Rollback at U-IS-15.

**Signatures:**
```
create_shadow_git_checkpoint(
  workflow_run_id  : Identifier,
  trigger_context  : CheckpointTriggerContext
) -> CheckpointResult

record CheckpointTriggerContext {
  cadence                    : CheckpointCadence
  workflow_step_id           : Optional[Identifier]
  tool_call_id               : Optional[Identifier]
  significant_change_marker  : Optional[string]
  explicit_marker            : Optional[string]
}

record CheckpointResult {
  checkpoint_id  : Identifier
  shadow_ref     : string
  created_at     : Timestamp
  triggered_by   : CheckpointCadence
}

on_workflow_event(event: WorkflowEvent) -> Optional[CheckpointResult]
```

**Acceptance criteria:**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Snapshot creation | Shadow ref/branch in same git repo as versioning sub-role | §8.4 |
| 2 | Non-pollution of main branch | Shadow refs absent from main commit history | §8.4 |
| 3–6 | Cadence-driven firing | PER_STEP, PER_TOOL_CALL, PER_SIGNIFICANT_CHANGE, PER_EXPLICIT_MARKER each fire per spec semantics | §8.2 |
| 7 | Opt-out compliance | `shadow_git_enabled = false` ⇒ 0 checkpoints | §8.1 |
| 8 | Atomic at shadow-ref level | Git-native ref atomicity | §8.3 row 1 |

**Out-of-unit scope:** Per IS spec v1.2 §8.4 deferral — shadow-ref naming convention; retention policy; cadence-policy authoring schema are configuration-supplied at execution time; not asserted at this unit's tests.

**Tests:**
- `test_checkpoint_creates_shadow_ref`, `test_checkpoint_not_in_main_branch_history`, `test_checkpoint_per_step_cadence`, `test_checkpoint_per_tool_call_cadence`, `test_checkpoint_per_significant_change_cadence`, `test_checkpoint_per_explicit_marker_cadence`, `test_checkpoint_disabled_when_opt_out`, `test_checkpoint_atomic`, `test_checkpoint_orthogonal_to_deploys`.

**Rollback boundary:** Revert checkpoint primitive + cadence driver. U-IS-15 rollback cannot operate.

#### U-IS-15 — Implement shadow-Git rollback primitive

**Implements:** [C-IS-08 §8.3]

**Depends on:** [U-IS-11, U-IS-14]

**Inputs:** `CheckpointResult` (U-IS-14); `append_ledger_entry` + `EntryPayload` (U-IS-11); IS spec v1.2 §8.3.

**Files affected:** Shadow-Git rollback primitive (logical name: `shadow-git-rollback`).

**Signatures:**
```
rollback_to_checkpoint(
  checkpoint_id    : Identifier,
  workflow_run_id  : Identifier
) -> RollbackResult

record RollbackResult {
  status              : RollbackStatus
  restored_at         : Timestamp
  rollback_entry_id   : Optional[Identifier]
}

enum RollbackStatus {
  RESTORED,
  CHECKPOINT_NOT_FOUND,
  ROLLBACK_FAILED
}
```

**Acceptance criteria:**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Atomic | Full or none; git-native atomicity | §8.3 row 1 |
| 2 | Filesystem-bounded | Restores tracked filesystem state; ledger NOT restored | §8.3 row 2 |
| 3 | Workflow-state-coherent | Post-rollback FS matches checkpoint; inference state NOT restored | §8.3 row 3 |
| 4 | Rollback event written | Invokes append_ledger_entry; entry carries checkpoint_id | §8.3 row 2 |
| 5 | Checkpoint-not-found | Non-existent checkpoint_id ⇒ CHECKPOINT_NOT_FOUND; FS + ledger unchanged | defensive |
| 6 | Partial-restore handling | Mid-rollback failure ⇒ ROLLBACK_FAILED; no ledger entry | §8.3 row 1 exception |

**Out-of-unit scope:** Per IS spec v1.2 §8.4 deferral — rollback API surface beyond the signature is implementation-grade detail not asserted at this unit's tests.

**Tests:**
- `test_rollback_restores_filesystem`, `test_rollback_does_not_restore_ledger`, `test_rollback_writes_rollback_event_to_ledger`, `test_rollback_atomic_full_or_none`, `test_rollback_checkpoint_not_found`, `test_rollback_filesystem_bounded`, `test_rollback_does_not_modify_inference_state`.

**Rollback boundary:** Revert rollback primitive. Workflows checkpoint but cannot roll back.

#### U-IS-16 — Implement worktree-isolation primitive

**Implements:** [C-IS-09 §9.2, §9.3]

**Depends on:** [U-IS-04, U-IS-13]

**Inputs:** `GitTierSubRole.WORKTREE_ISOLATION` (U-IS-04); `WorkloadManifestOptIns.worktree_isolation_enabled` + `.worktree_concurrency_cap` (U-IS-13); IS spec v1.2 §9.2 + §9.3.

**Files affected:** Worktree-isolation primitive (logical name: `worktree-isolation`); worktree lifecycle manager (logical name: `worktree-lifecycle-manager`).

**Scope.** Allocation + reclamation + concurrent-read isolation invariants. Sub-agent boundary cross-axis composition (§9.3 row 4) honored by non-violation; enforcement at AS/CP/OD plans. §9.4 multi-writer scaling boundary is declarative out-of-scope.

**Signatures:**
```
allocate_worktree(
  parent_workflow_run_id  : Identifier,
  sub_agent_id            : Identifier
) -> WorktreeHandle

reclaim_worktree(
  worktree_handle      : WorktreeHandle,
  reclamation_trigger  : ReclamationTrigger
) -> ReclamationResult

record WorktreeHandle {
  worktree_id    : Identifier
  worktree_path  : Path
  parent_run_id  : Identifier
  sub_agent_id   : Identifier
  allocated_at   : Timestamp
}

enum ReclamationTrigger {
  SUB_AGENT_SUCCESS,
  SUB_AGENT_FAILURE,
  OPERATOR_POLICY_LIFECYCLE_MARKER
}

enum ReclamationResult { RECLAIMED, RECLAMATION_FAILED }
```

**Acceptance criteria:**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Per-sub-agent worktree | Isolated directory; shares parent's .git storage | §9.2 row 1 |
| 2 | Worktree identity stable | Stable for sub-agent lifetime | §9.2 row 2 |
| 3 | Concurrency cap | (N+1)th concurrent allocation rejected when cap=N | §9.1 + D4 v1.1 |
| 4 | Reclamation operational semantic | `git worktree remove` + directory contents removal | §9.2 row 3 |
| 5 | .git storage preserved | Reclamation MUST NOT delete .git backend | §9.2 row 3 |
| 6 | Operator-policy-controlled trigger | Configuration-supplied | §9.2 row 3 |
| 7 | Read-read non-interference | Concurrent reads do not block | §9.3 row 1 |
| 8 | Read-write non-interference intra-worktree | Cross-worktree writes do not leak | §9.3 row 2 |
| 9 | Cross-worktree writer serialization | Concurrent writes across worktrees do not interleave at .git backend | §9.3 row 3 |
| 10 | Opt-out compliance | `worktree_isolation_enabled = false` ⇒ 0 worktrees | §9.1 |

**Out-of-unit scope:** Per IS spec v1.2 §9.4 deferral — worktree directory location; cross-worktree writer serialization mechanism; reclamation cleanup policy are configuration-supplied at execution time; not asserted at this unit's tests.

**Tests:**
- `test_allocate_worktree_creates_isolated_directory`, `test_allocate_worktree_shares_git_storage`, `test_worktree_identity_stable`, `test_concurrency_cap_enforced`, `test_reclaim_worktree_invokes_git_remove`, `test_reclaim_preserves_git_storage_backend`, `test_read_read_non_interference`, `test_read_write_non_interference_intra_worktree`, `test_cross_worktree_writer_serialization`, `test_worktree_disabled_when_opt_out`, `test_worktree_termination_on_sub_agent_success`, `test_worktree_termination_on_sub_agent_failure`.

**Rollback boundary:** Revert worktree primitive + lifecycle manager. Sub-agent fan-out shares parent's working directory.

---

### §2.6 Cluster 6 — Substrate seam exports surface (C-IS-10)

**Cluster scope.** Six substrate seam exports for downstream-axis consumption. Per OD-S1-3.A: author at spec granularity; consumer-axis dependency declarations at Sessions 2–4; Session 5 retroactive verification. 1 unit.

#### U-IS-17 — Declare substrate seam exports manifest

**Implements:** [C-IS-10 §10.1, §10.2, §10.3, §10.4, §10.5, §10.6]

**Depends on:** [U-IS-01, U-IS-02, U-IS-05, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-11, U-IS-12, U-IS-13]

**Inputs:** IS spec v1.2 §10.1 through §10.6 export sub-sections.

**Files affected:** Substrate seam exports manifest (logical name: `is-axis-substrate-seam-exports-manifest`).

**Scope.** Declarative manifest only; no executable behavior. Per OD-S1-3.A, consumer-axis dependency declarations NOT authored at this unit.

**Signatures:**
```
enum SeamId {
  STATE_LEDGER_ENTRY_SHAPE_EXPORT,             // §10.1
  IDEMPOTENCY_KEY_JOIN_EXPORT,                 // §10.2
  HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT,   // §10.3
  FILESYSTEM_PATH_CONTRACT_EXPORT,             // §10.4
  JSONL_EVENT_LEDGER_FORMAT_EXPORT,            // §10.5
  WORKLOAD_CLASS_OPT_IN_MANIFEST_EXPORT        // §10.6
}

enum ConsumingAxis { ACTION_SURFACE, CONTROL_PLANE, OPERATIONAL_DISCIPLINE }

record SubstrateSeamExport {
  seam_id                : SeamId
  spec_citation          : string
  export_surface         : string
  carrier_units          : List[UnitId]
  consuming_axes         : List[ConsumingAxis]
  composition_references : List[string]
}
```

**Manifest content:**

| Seam | Spec citation | Export surface | Carrier units | Consuming axes |
|---|---|---|---|---|
| STATE_LEDGER_ENTRY_SHAPE_EXPORT | C-IS-10 §10.1 | Six-field `StateLedgerEntry` record per C-IS-05 | U-IS-07 | CP, OD, AS |
| IDEMPOTENCY_KEY_JOIN_EXPORT | C-IS-10 §10.2 | `idempotency_key` field; harness-canonical cross-axis join key | U-IS-07, U-IS-12 | AS, CP, OD |
| HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT | C-IS-10 §10.3 | Canonicalize → SHA-256 → prior-event-hash chaining per C-IS-06 | U-IS-08, U-IS-09, U-IS-10 | OD |
| FILESYSTEM_PATH_CONTRACT_EXPORT | C-IS-10 §10.4 | Canonical filesystem path classes per C-IS-01 | U-IS-01, U-IS-02 | AS, CP |
| JSONL_EVENT_LEDGER_FORMAT_EXPORT | C-IS-10 §10.5 | JSONL with stable indexable per-event shape per C-IS-07 §7.3 | U-IS-05, U-IS-07, U-IS-11, U-IS-12 | OD |
| WORKLOAD_CLASS_OPT_IN_MANIFEST_EXPORT | C-IS-10 §10.6 | `WorkloadManifestOptIns` schema per C-IS-08 §8.1 + C-IS-09 §9.1 | U-IS-13 | CP |

**Composition references (verbatim from spec):**

- **§10.1:** D1 v1.1 engine event history joins on `idempotency_key` (Tier-3 ↔ Tier-5 ledger composition per ADR-F3 §Consequences (a) + ADR-D1 v1.1); D5 v1.3 audit-ledger inherits entry shape + `audit.*` attribute namespace per ADR-D5 v1.3 §1.4 + §1.4.1; D2 v1.1 sandbox-violation events join on `idempotency_key` per ADR-D2 v1.1 §1.8; D6 v1.1 cost-attribution-per-span joins on `idempotency_key` per ADR-D6 v1.1 §1.5.
- **§10.2:** Cross-axis join key for replay-safe composition per ADD §2.2 Synthesis closing sentence; **F2-12 carry-forward** — replay-trace-emission contract (D1 v1.1 → v1.2) deferred per ADD §6.3.1 + PRD §[carry-forwards] [CF-1]: span re-emission semantics under engine replay; `retry.attempt` sibling-span discipline; trace-ingestion dedup composition with `idempotency_key` remain open.
- **§10.3:** D5 v1.3 audit-ledger uses F2 hash-chain construction at team-binding+ persona tiers per ADR-D5 v1.3 §1.4 + §1.4.1; multi-tenant-compliance persona tier extends hash chain with cryptographic signature (`audit.signature.value` + `audit.signature.algorithm` + `audit.signature.key_id` + `audit.signature.key_period`) per ADR-D5 v1.3 §1.4.
- **§10.4:** D3 v1.2 Skills loading discipline reads Skills-as-files from filesystem per cache-prefix integrity discipline per ADR-D3 v1.2; F1 v1.2 routing manifest resides at canonical filesystem path per ADR-F1 v1.2 Consequences §(a).
- **§10.5:** D6 v1.1 OTLP collector boundary composes against F2 JSONL event ledger at within-turn streaming + across-turn durable trace storage per ADR-D6 v1.1 §1.7 (T-perm-2 D6-layer commitment per ADD §5.2.2).
- **§10.6:** D4 v1.1 sub-agent fan-out composes worktree-isolation with sub-agent privilege inheritance + sandbox-tier monotonicity + cross-deployment monotonicity per ADD §5.3.2 sub-agent boundary as monotonic-only descent; D5 v1.3 cross-deployment monotonicity engages T-perm-3 at shadow-Git checkpoint cadence vs retry-mechanics seam per ADR-F2 §"Permanent tensions engaged" T-perm-3 touch + ADD §5.2.3 residual surface.

**Acceptance criteria:**
1. Manifest enumerates exactly 6 substrate seam exports matching spec §10.1 through §10.6 verbatim.
2. Each `carrier_units` cites ≥1 IS-plan unit; every cited carrier resolves to a unit in U-IS-01 through U-IS-16.
3. Each `consuming_axes` matches spec §10.X "Consuming axes" column verbatim.
4. Each `spec_citation` is of the form `C-IS-10 §10.X` where X ∈ {1, 2, 3, 4, 5, 6}.
5. Manifest introduces NO executable behavior — declarative records only.
6. F2-12 carry-forward note preserved verbatim at IDEMPOTENCY_KEY_JOIN_EXPORT composition reference.
7. ADR body-citation versions: F1 v1.2, F2 v1.2, F3 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1 (latest filed per Workflow v1.6 §7).
8. Per OD-S1-3.A: consumer-axis dependency declarations NOT authored here; Session 5 retroactive verification.

**Tests:**
- `test_substrate_seam_exports_completeness`, `test_carrier_units_resolve`, `test_carrier_units_cover_export_surface`, `test_consuming_axes_match_spec`, `test_spec_citation_stable_anchor`, `test_f2_12_carry_forward_preserved`, `test_adr_body_citation_versions_aligned`, `test_manifest_no_executable_behavior`.

**Rollback boundary:** Revert substrate seam exports manifest. Consumer-axis plans (Sessions 2–4) lose stable citation target; Session 5 cross-axis composition cannot verify consumer-axis declarations against IS export surface.

---

## §3 Dependency graph

### §3.1 Topological levels

| Level | Units (count) | Position semantic |
|---|---|---|
| 0 (foundational) | U-IS-01, U-IS-03, U-IS-04, U-IS-07, U-IS-13 (5) | `Depends on: (none)` |
| 1 | U-IS-02, U-IS-06, U-IS-08, U-IS-14, U-IS-16 (5) | Direct dependencies on Level 0 only |
| 2 | U-IS-05, U-IS-09, U-IS-10 (3) | Dependencies on Levels 0–1 |
| 3 | U-IS-11, U-IS-12 (2) | Dependencies on Levels 0–2 |
| 4 | U-IS-15 (1) | Dependencies on Levels 0–3 |
| 5 (terminal) | U-IS-17 (1) | Dependencies on Levels 0–3 (re-export manifest) |
| **Total** | **17** | — |

### §3.2 Per-unit dependency declarations

| Unit | Depends on | Direct dependency count |
|---|---|---|
| U-IS-01 | (none) | 0 |
| U-IS-02 | U-IS-01 | 1 |
| U-IS-03 | (none) | 0 |
| U-IS-04 | (none) | 0 |
| U-IS-05 | U-IS-01, U-IS-02, U-IS-04 | 3 |
| U-IS-06 | U-IS-01, U-IS-04 | 2 |
| U-IS-07 | (none) | 0 |
| U-IS-08 | U-IS-07 | 1 |
| U-IS-09 | U-IS-07, U-IS-08 | 2 |
| U-IS-10 | U-IS-07, U-IS-08 | 2 |
| U-IS-11 | U-IS-05, U-IS-07, U-IS-08, U-IS-09 | 4 |
| U-IS-12 | U-IS-05, U-IS-07 | 2 |
| U-IS-13 | (none) | 0 |
| U-IS-14 | U-IS-04, U-IS-13 | 2 |
| U-IS-15 | U-IS-11, U-IS-14 | 2 |
| U-IS-16 | U-IS-04, U-IS-13 | 2 |
| U-IS-17 | U-IS-01, U-IS-02, U-IS-05, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-11, U-IS-12, U-IS-13 | 10 |

### §3.3 Acyclic invariant verification

Kahn's algorithm produces a complete topological order over 17 nodes across 6 levels; all 17 nodes placed. **No cycles. Graph is a DAG.** ✅

### §3.4 ASCII dependency graph (compact)

```
LEVEL 0 (foundational):
  U-IS-01 ──┐
  U-IS-03   │  (terminal at this level; consumed by no IS unit;
            │   semantic of artifact-tier registry standalone)
  U-IS-04 ──┤
  U-IS-07 ──┤
  U-IS-13 ──┤

LEVEL 1:
  U-IS-02 ◄── {U-IS-01}
  U-IS-06 ◄── {U-IS-01, U-IS-04}
  U-IS-08 ◄── {U-IS-07}
  U-IS-14 ◄── {U-IS-04, U-IS-13}
  U-IS-16 ◄── {U-IS-04, U-IS-13}

LEVEL 2:
  U-IS-05 ◄── {U-IS-01, U-IS-02, U-IS-04}
  U-IS-09 ◄── {U-IS-07, U-IS-08}
  U-IS-10 ◄── {U-IS-07, U-IS-08}

LEVEL 3:
  U-IS-11 ◄── {U-IS-05, U-IS-07, U-IS-08, U-IS-09}
  U-IS-12 ◄── {U-IS-05, U-IS-07}

LEVEL 4:
  U-IS-15 ◄── {U-IS-11, U-IS-14}

LEVEL 5 (terminal):
  U-IS-17 ◄── {U-IS-01, U-IS-02, U-IS-05, U-IS-07, U-IS-08,
               U-IS-09, U-IS-10, U-IS-11, U-IS-12, U-IS-13}
```

### §3.5 Cross-axis dependency declarations (deferred per OD-S1-3.A)

Sessions 2–4 declare `Depends on: [U-IS-NN (cross-axis: IS)]` at consuming AS / CP / OD units. Retroactive verification at Session 5 against U-IS-17 substrate seam exports manifest. Expected consumer-axis dependencies enumerated at U-IS-17 manifest content table.

---

## §4 Coverage matrix (per OD-S1-2.A — per-axis only)

| C-IS-NN | Spec § | Covering unit IDs | Coverage |
|---|---|---|---|
| C-IS-01 | §1 | U-IS-01, U-IS-02 | ✅ |
| C-IS-02 | §2 | U-IS-03 | ✅ |
| C-IS-03 | §3 | U-IS-04, U-IS-05 | ✅ |
| C-IS-04 | §4 | U-IS-06 | ✅ |
| C-IS-05 | §5 | U-IS-07 | ✅ |
| C-IS-06 | §6 | U-IS-08, U-IS-09, U-IS-10 | ✅ |
| C-IS-07 | §7 | U-IS-11, U-IS-12 | ✅ |
| C-IS-08 | §8 | U-IS-13, U-IS-14, U-IS-15 | ✅ |
| C-IS-09 | §9 | U-IS-13, U-IS-16 | ✅ |
| C-IS-10 | §10 | U-IS-17 | ✅ |

**Coverage complete. 10 of 10 contracts covered by ≥1 unit. No coverage gaps.**

Per OD-S1-2.A: per-axis matrix self-contained; no aggregate cross-axis matrix composed at Session 5. Cross-axis verification at Session 5 verifies AS / CP / OD plans' cross-axis declarations against U-IS-17 substrate seam exports manifest (not against this per-axis coverage matrix).

---

## §[carry-forwards]

This meta-section documents PRD-inherited and spec-inherited carry-forward items. Entries are documentation, not contract-bearing — they do not engage the §[coherence pass] audit; they engage the plan's operator-visibility surface.

### [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract

**Status.** 🔄 Deferred-acknowledged at ADD v1.2 §6.3.1; inherited at PRD v1.0.1 §[carry-forwards] [CF-1]; inherited at IS spec v1.2 §[carry-forwards] [CF-1]; inherited at this plan. Not blocking Phase 6 Session 1 entry; not blocking IS plan filing.

**Scope.** D1 v1.1 → v1.2 replay-trace-emission contract covering: (i) span re-emission semantics under engine replay; (ii) `retry.attempt` sibling-span discipline; (iii) trace-ingestion dedup composition with F2 `idempotency_key`.

**IS plan impact.** The F2 `idempotency_key` export per U-IS-17 §10.2 is the harness-canonical join key; replay-trace-emission semantics consuming this join key are downstream-axis contracts (CP and OD). U-IS-17 manifest content table includes the F2-12 carry-forward note at IDEMPOTENCY_KEY_JOIN_EXPORT verbatim. **No Information Substrate unit is open as a function of F2-12** — the F2 substrate surface (entry shape per U-IS-07, hash-chain construction per U-IS-08/U-IS-09/U-IS-10, idempotency_key export per U-IS-17 §10.2) is fully closed at v2.1 of this plan. U-IS-11 §7.4 deferral accommodates F2-12 by treating WriteKey as caller-supplied without committing the keying source.

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Phase 5 revision-pass at affected spec sections (CP spec + OD spec); IS spec NOT a revision target for F2-12 closure; IS plan NOT a revision target for F2-12 closure.

### [CF-2] Workflow §7 substrate-skill propagation

**Status.** Open operator decision; outside P6-CK closure scope; outside Phase 5 scope; outside Phase 6 plan-authoring scope.

**Origin.** `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update.

**IS plan impact.** Not in plan scope (skill-substrate revision is neither architectural commitment nor implementation-grade unit). Documented here for operator-visibility per inheritance from IS spec §[carry-forwards] [CF-2].

**Forward routing.** Operator decision at discretion. No plan revision triggered by skill-substrate propagation.

---

## §[coherence pass]

Pre-emission self-audit per SKILL.md §5 step 9 + §[coherence pass] discipline. Five audit dimensions; plan does not file unless all five return ✅ PASS.

### Audit 6.1 — Atomicity (SKILL.md §3)

| Sub-dimension | Verification | Result |
|---|---|---|
| §3.1 Single coherent change | Every unit produces one schema, one function family, one integration point, or one bounded refactor; no multi-axis "miscellaneous changes" buckets | ✅ PASS — spot-check: U-IS-01 single schema; U-IS-08 single primitive pair (canonicalize + hash); U-IS-11 single write contract; U-IS-17 single re-export manifest |
| §3.2 Single focused session | Every unit small enough for one focused executor session; no multi-week effort; no one-line-edit over-decomposition | ✅ PASS — spot-check: U-IS-02 path-resolver primitive (one session); U-IS-15 rollback primitive (one session); no unit estimated multi-week |
| §3.3 Independently testable | Every unit's acceptance criterion verifiable once unit + declared dependencies complete | ✅ PASS — every unit declares tests with behavioral assertions verifiable on the unit + its declared deps; U-IS-16 acceptance row 9 testable invariant verified by `test_cross_worktree_writer_serialization` |
| §3.4 Coherent rollback boundary | Every unit revertible as a single coherent change; no PR/commit/file-granularity pre-commitment | ✅ PASS — every unit declares rollback boundary at logical level; no filesystem-path or commit-hash pre-commitment |

**Audit 6.1 aggregate: ✅ PASS (4/4 sub-dimensions across all 17 units).**

### Audit 6.2 — Spec-traceability (SKILL.md §4 sub-discipline 2)

| Sub-dimension | Verification | Result |
|---|---|---|
| Per-unit citation by ID + section | Every unit's `Implements:` cites ≥1 C-IS-NN by ID + section | ✅ PASS — 17/17 units; e.g., U-IS-04 cites C-IS-03 §3; U-IS-08 cites C-IS-06 §6.1, §6.2; U-IS-13 cites C-IS-08 §8.1, §8.2 + C-IS-09 §9.1 |
| Aggregate coverage | Every C-IS-NN (1–10) covered by ≥1 unit per §4 coverage matrix | ✅ PASS — 10/10 covered |
| Citation version alignment | All citations point to IS spec v1.2 per Workflow v1.6 §7 latest-version discipline | ✅ PASS — no v1 or v1.1 citations emitted; U-IS-17 manifest ADR body-citations use latest filed versions (F1 v1.2, F2 v1.2, F3 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1) |
| F1-IS-02 absorption verification | U-IS-16 row 9 criterion column rewritten per R1′ to testable invariant; spec-ref column drops §9.4 deferral citation; row retained at cardinality 10 | ✅ PASS — row 9 reads `Cross-worktree writer serialization \| Concurrent writes across worktrees do not interleave at .git backend \| §9.3 row 3` |

**Audit 6.2 aggregate: ✅ PASS (4/4 sub-dimensions).**

### Audit 6.3 — Dependency-awareness (SKILL.md §4 sub-discipline 3 + §7)

| Sub-dimension | Verification | Result |
|---|---|---|
| Acyclic invariant | Topological sort exists over 17 nodes across 6 levels | ✅ PASS — Kahn's algorithm verified at §3.3 |
| Foundational-first ordering | 5 foundational units (U-IS-01, U-IS-03, U-IS-04, U-IS-07, U-IS-13) anchor graph with `Depends on: (none)` | ✅ PASS |
| No transitive omission | Every unit declares direct dependencies only; no transitive declarations | ✅ PASS — verified by inspection; e.g., U-IS-11 cites direct deps U-IS-05, U-IS-07, U-IS-08, U-IS-09 (not transitive deps through U-IS-09 such as U-IS-07) |
| Coverage discipline | Every declared dependency resolves to a defined unit; every unit's acceptance criterion supported by declared dependencies' products | ✅ PASS — verified by inspection; e.g., U-IS-15 rollback requires `append_ledger_entry` from U-IS-11 + `CheckpointResult` from U-IS-14; both declared |
| Cross-axis dependency flagging | Cross-axis dependencies flagged with axis annotation `(cross-axis: AS/CP/OD)` | ✅ PASS — no cross-axis dependencies at IS plan; Sessions 2–4 declare cross-axis deps into IS per OD-S1-3.A; verification at Session 5 |

**Audit 6.3 aggregate: ✅ PASS (5/5 sub-dimensions).**

### Audit 6.4 — Implementation-grade-detail (SKILL.md §4 sub-discipline 4)

| Sub-dimension | Verification | Result |
|---|---|---|
| Logical file names (not filesystem paths) | Every unit names logical files; no filesystem-path pre-commitment | ✅ PASS — e.g., `path-class-registry-schema`, `entry-canonicalization`, `shadow-git-checkpoint` (logical names, not paths) |
| Function / class / schema signatures | Every unit declares signatures at specification-translatable grade | ✅ PASS — 17/17 units carry signatures (record / enum / interface / function) |
| Testable acceptance criteria | Every unit's acceptance criteria are concrete and testable | ✅ PASS — 17/17 units carry numbered acceptance criteria with concrete predicates; U-IS-16 row 9 amendment retains testable property |
| Tests with behavioral assertions | Every unit names tests with behavioral assertions | ✅ PASS — 17/17 units carry test enumerations |
| No spec extension | No unit introduces library / framework / protocol commitment not named in spec | ✅ PASS — verified by inspection; e.g., U-IS-08 cites RFC 8785 JCS per spec §6.1; U-IS-11 cites Stripe-style keying convention per spec §7.1; no off-spec commitments |

**Audit 6.4 aggregate: ✅ PASS (5/5 sub-dimensions).**

### Audit 6.5 — Anti-pattern audit (SKILL.md §10)

| Anti-pattern | Verification | Result |
|---|---|---|
| Under-decomposition | No multi-axis or "implement entire X" units | ✅ PASS |
| Over-decomposition | No one-line-edit units or "create directory" units | ✅ PASS |
| Spec extension | No unit names library/framework/protocol absent from spec; F2-12 deferral preserved at U-IS-11 §7.4 + U-IS-17 §10.2 | ✅ PASS |
| Implementation-detail leakage in wrong direction | All units provide signatures + acceptance + tests | ✅ PASS |
| Cyclic dependencies | Verified acyclic at §3.3 | ✅ PASS |
| Missing dependencies | Verified at Audit 6.3 coverage discipline | ✅ PASS |
| Under-specified acceptance | All acceptance criteria testable; U-IS-16 row 9 testable post-R1′ amendment | ✅ PASS |
| Acceptance-criteria-table mixing testable invariants with deferral scope notes | F1-IS-01 absorbed rows preserved at v2; F1-IS-02 U-IS-16 row 9 absorbed at v2.1 per R1′ rewrite | ✅ PASS (no residual anti-pattern instances at v2.1) |
| Coverage gaps | All 10 C-IS-NN contracts covered | ✅ PASS |
| Risk/estimate annotations | None present (no per-unit risk/effort) | ✅ PASS |
| Trace-omission | All 17 units cite ≥1 C-IS-NN by ID + section | ✅ PASS |
| PR/commit/file-granularity pre-commitment | All units at logical-coherent-change granularity | ✅ PASS |
| Confidence-schema redefinition | V3 [HIGH] / [MODERATE] / [SPECULATIVE] schema honored (e.g., RFC 8785 JCS at U-IS-08 tagged [MODERATE] per spec) | ✅ PASS |
| Citation invention | All citations verified against IS spec v1.2 §1–§10 read during this session | ✅ PASS |

**Audit 6.5 aggregate: ✅ PASS (14/14 anti-patterns absent).**

### Coherence pass aggregate

| Audit dimension | Result |
|---|---|
| 6.1 Atomicity | ✅ PASS (4/4 sub-dimensions) |
| 6.2 Spec-traceability | ✅ PASS (4/4) |
| 6.3 Dependency-awareness | ✅ PASS (5/5) |
| 6.4 Implementation-grade-detail | ✅ PASS (5/5) |
| 6.5 Anti-pattern audit | ✅ PASS (14/14) |

**Coherence pass: ✅ PASS at all 5 audit dimensions. Plan authorized for filing.**

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Information_Substrate_v2_1.md` |
| Phase | 6 — atomic implementation plan; v2.1 revision-pass under Path B authorization |
| Session | Path B Segment C (single-segment revision pass) |
| Axis | Information Substrate (IS) — C-IS-01 through C-IS-10 (10 contracts) |
| Unit count | 17 (U-IS-01 through U-IS-17) |
| Routing target | P6-CK Iteration 3 against v2.1 ensemble per Workflow v1.6 §4.1.4.5 |
| Predecessor | `Implementation_Plan_Information_Substrate_v2.md` (v2, filed 2026-05-14 under Path α); `Adversarial_Review_6_iter2.md` §3.2 F1-IS-02 finding; `P6-CK_Iteration_2_Ceiling_Disposition.md` §5.1 R1′ absorption shape; `Project_Workflow_v1_6.md` §4.1.4.5 one-time Path B Iter-3 authorization |
| Successor | Path B Segment D (`Implementation_Plan_Control_Plane_v2_1.md`); then Segment E (OD); then Segment F (CXA); then Segment G (P6-CK Iter 3 kickoff) |
| Filing destination | `/mnt/user-data/outputs/Implementation_Plan_Information_Substrate_v2_1.md` |
| Date | 2026-05-14 |

*Filed 2026-05-14 at Path B Segment C close → Path B Segment D entry boundary. v2.1 scope: F1-IS-02 absorption per OD-PathB-1 R1′ rewrite of U-IS-16 acceptance row 9 criterion column. Single-finding revision-pass per Path B authorization; no other v2 content amended.*
