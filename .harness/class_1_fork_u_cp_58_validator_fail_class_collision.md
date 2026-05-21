# Class 1 Fork — `ValidatorFailClass` namespace collision at U-CP-58 / 10-CP-A entry

## Filing metadata

| Field | Value |
|---|---|
| Filed at | 2026-05-21, HEAD `7d13593` |
| Halt point | U-CP-58 implementation entry (10-CP-A cluster open) |
| Sub-phase | 7b per-axis-stream — CP-axis |
| Fork class | Class 1 (spec under-specification) |
| Detection source | Carrier-surface inspection before unit landing per [[fork-carrier-home-defect-pattern]] discipline |
| Routing target | Phase 5 CP spec revision-pass — `Spec_Control_Plane_v1_10.md` §25.2 (or §25.8 deferred-to-discretion expansion) |

## Defect description

CP spec v1.10 §25.2 (NEW C-CP-25 ValidatorFramework) declares an enum `ValidatorFailClass` with **5 pre-emit fail-categorization members**:

```python
class ValidatorFailClass(Enum):
    SCHEMA_VIOLATION = "schema_violation"
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    SAFETY_POLICY = "safety_policy"
    RESOURCE_CONSTRAINT = "resource_constraint"
    EXTERNAL_REJECTION = "external_rejection"
```

Existing landed code at `harness-cp/src/harness_cp/validator_fail_taxonomy.py` (U-CP-47, materializing CP spec v1.2 §21.1 / preserved through v1.3 / referenced by all subsequent revisions) binds the identifier `ValidatorFailClass` to a **different 5-member semantic surface** — post-fail retry-exit classification:

```python
class ValidatorFailClass(StrEnum):  # C-CP-21 §21.1
    TRANSIENT_RETRY = "transient-retry"
    REFLEXION_RECOVERABLE = "Reflexion-recoverable"
    HITL_RECOVERABLE = "HITL-recoverable"
    PERMANENT_FAIL_EXIT = "permanent-fail-exit"
    TERMINAL_FAIL_EXIT = "terminal-fail-exit"
```

**Collision surface.**
- Same identifier (`ValidatorFailClass`)
- Same package (`harness_cp`)
- Overlapping semantic domain (both relate to validator failures, but C-CP-21 is *retry-decision after a fail* and C-CP-25 is *fail-categorization before a downstream span emit*)
- Distinct submodule files (existing: `validator_fail_taxonomy.py`; planned: `validator_framework_types.py` per U-CP-58)

**Why this is a defect, not an absorbable drift.**
- Python permits two same-name enums in distinct submodule files of the same package, but the import-discipline collision is cognitively load-bearing — every consumer must qualify by submodule path or risk silent shadowing if either module is later re-exported at `harness_cp/__init__.py`.
- The C-CP-21 enum is referenced by `harness-cp/src/harness_cp/validator_fail_transient_staircase.py` + downstream U-CP-47 landings; renaming it costs a multi-site refactor.
- C-CP-25 §25.2 produces a typed `ValidatorResult.fail_class: ValidatorFailClass | None` field — consumers of `ValidatorResult` cannot disambiguate which `ValidatorFailClass` is meant without spec authority.
- §25.8 "Deferred to implementation discretion" addresses only `ValidatorNextAction` value names + `fail_detail_hash` content shape — **silent** on the collision.

## Resolution alternatives (operator decides)

| Path | Action | Cost | Authority chain impact |
|---|---|---|---|
| (α) Rename NEW C-CP-25 enum | C-CP-25 §25.2 renamed to `ValidatorFrameworkFailClass` (or similar disambiguated name) | Low — pre-implementation; spec single-site rename + `ValidatorResult.fail_class` type annotation update | CP spec v1.10 → v1.11 (Class 1 revision); plan U-CP-58 AC #2 amended to cite new name |
| (β) Rename EXISTING C-CP-21 enum | C-CP-21 §21.1 renamed to `ValidatorRetryExitClass` (or similar semantic-accurate name); rebound across `validator_fail_taxonomy.py` + `validator_fail_transient_staircase.py` + downstream | Medium — post-implementation rename; ~5-10 callsites + tests | CP spec v1.10 §21.1 retroactively renamed via §0 change-note; plan U-CP-47 trace updated; backwards-compat alias for landed substitutions |
| (γ) Accept same-name distinct-submodule coexistence | C-CP-25 enum lands at `validator_framework_types.py`; consumers required to qualify by submodule path; package `__init__.py` MUST NOT re-export either at top level | Zero refactor; high cognitive load + audit-risk | CP spec v1.10 §25.8 extended to ratify the discipline: "ValidatorFailClass identifier coexists at two submodule paths; consumers MUST qualify by submodule; package re-export forbidden" |
| (δ) Merge the two semantic domains into a single enum | Combine both 5-member sets into a single 10-member ValidatorFailClass with shared semantics | High — semantic conflation across two distinct contracts (C-CP-21 retry-exit vs C-CP-25 pre-emit) | CP spec v1.10 §21.1 + §25.2 jointly revised; ADR-D5 v1.4 attestation owed |

**Recommended.** (α) — rename NEW C-CP-25 enum. Lowest cost, preserves landed C-CP-21 surface, no ripple to existing tests/callsites, single-site spec amendment.

## Halt state

| Element | Value |
|---|---|
| Workspace HEAD | `7d13593` (workspace pointer absorption commit; clean tree post-Closure-Arc-design-merge) |
| Halted task | #2 `10-CP-A: ValidatorFramework — U-CP-58 → U-CP-59 → U-CP-60 → (U-OD-50) → U-CP-61` |
| Halted unit | U-CP-58 entry — at carrier-surface inspection (pre any-LOC-written) |
| Cascade halts | #3 (10-CP-B blocked by #2) → #4 (10-CP-C blocked by #3) → #6 (L9-sexies blocked by #4); #5 (4-OD-E remainder) independent; can proceed in parallel |
| Tests at halt | 2410 green (unchanged from session-start) |

## Resumption discipline

Per `phase-7-back-flow-routing` skill §4.5–§4.7:

1. Operator authorizes resolution path (α / β / γ / δ) or re-classifies as Class 2.
2. CP spec v1.10 → v1.11 (or §25.8 extension) absorbed at spec-writer apply-pass.
3. Plan U-CP-58 + downstream U-CP-59/60 cited-name updates if applicable.
4. Workspace `CLAUDE.md` §2.3 CP-spec row version-bump.
5. Resume U-CP-58 implementation against re-issued substrate.

## Cross-references

- Plan unit declaration: `Implementation_Plan_Control_Plane_v2_15.md` §1 U-CP-58
- Spec contract: `Spec_Control_Plane_v1_10.md` §25.2
- Conflicting landed code: `harness-cp/src/harness_cp/validator_fail_taxonomy.py` (U-CP-47, C-CP-21 §21.1)
- Downstream existing consumer: `harness-cp/src/harness_cp/validator_fail_transient_staircase.py`
- Skill discipline: `.claude/skills/phase-7-back-flow-routing/SKILL.md` §4 + §5.1
- Workspace authority: `CLAUDE.md` §4.3 (silent absorption is the worst failure mode)

## Filing footer

| Field | Value |
|---|---|
| Filer | phase-7-back-flow-routing skill at U-CP-58 entry halt |
| Filer authority | Workspace root CLAUDE.md §4.3 + skill §1.3 critical-failure-mode classification |
| Predecessor | Phase A.2 contract drafts (`.harness/Phase_A_2_Contract_Drafts_v1.md`) + spec-writer apply pass (`.harness/Spec_Phase_A_2_Authoring_Log_v1.md`) |
| Successor consumption | Operator resolution → spec-writer apply pass → resume U-CP-58 |
