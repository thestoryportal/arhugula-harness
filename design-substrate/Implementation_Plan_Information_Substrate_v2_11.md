# Implementation Plan — Information Substrate (IS axis) — v2.11

*Delta over v2.10. This revision decomposes IS spec v1.17 §1.1, the installation pause-journal root that Runtime spec v1.137 Rule B7 requires, into one new foundational unit, U-IS-21. All v2.10 and earlier rows, unit bodies, criteria, dependency edges and coverage rows remain unchanged.*

**Status:** Proposed — not cleared. No clearance marker, artifact-head row or pointer is filed.

---

## §0 Authority and scope

The predecessor is `Implementation_Plan_Information_Substrate_v2_10.md`. IS spec v1.17 adds C-IS-01 §1.1 as the companion to Runtime spec v1.137 Rules B3, B7 and B8 and Runtime plan v2.68 U-RT-160 portion 160a (criteria 15 and 17). Owner profile-coder under LIT `cmt-792618a5`; scope and prerequisite owners in LIT `cmt-8b76cb48`; fork `.harness/class_1_fork_runtime_resume_cli_supersession.md`; authority `.harness/runtime-resume-contract-authority.md`.

The storage selection and its binding and retention evidence remain a separate prerequisite owned by Buford (integration lead). This plan selects no physical path, location for the declaration or retained volume. It adds no source, test, Control Plane delta or provisioning step.

## §1 New unit

### U-IS-21 — installation pause-journal root: declaration, per-tenant root and closed resolution result (IS spec v1.17 §1.1)

**Scope.** The IS-side types and pure decisions for the one installation-scoped pause-journal root. The Runtime root resolver (U-RT-160 portion 160a) performs every effect: it reads the installation state, observes the declared directory, supplies the real paths of the run's bound §1 directories, and enforces the result. U-IS-21 performs no I/O.

**Spec linkage.** C-IS-01 §1.1 (primary); §10.4 Runtime consumer row.

**Surfaces affected.** One new module `harness-is/src/harness_is/pause_journal_root.py`. `PathClass`, `PATH_CLASS_REGISTRY`, `PathBinding` and the path resolver are unchanged: the root is not a path class, so no binding can name it.

**Signature introduced** (from IS spec v1.17 §1.1):

```python
class UnresolvedCause(StrEnum):
    UNBOUND = "unbound"
    MALFORMED = "malformed"
    CONFLICTING = "conflicting"
    MISSING = "missing"
    OVERLAPPING = "overlapping"

class PauseJournalRootDeclaration(BaseModel):  # frozen, extra="forbid"
    installation_root: Path  # absolute and normalized; anything else is MALFORMED

@dataclass(frozen=True)
class Resolved:
    tenant_root: Path

@dataclass(frozen=True)
class Unresolved:
    cause: UnresolvedCause

PauseJournalRootResolution = Resolved | Unresolved

def parse_declarations(
    raw: Sequence[Mapping[str, object]],
) -> PauseJournalRootDeclaration | Unresolved: ...

def resolve_tenant_root(
    declaration: PauseJournalRootDeclaration,
    normalized_tenant_scope: str,
    bound_real_paths: Iterable[Path],
    installation_root_is_directory: bool,
) -> PauseJournalRootResolution: ...
```

**Depends on.** (none) — foundational. Like every IS unit it has zero outbound cross-axis edges. The inbound edge U-RT-160 portion 160a → U-IS-21 is declared from the Runtime side (Runtime plan v2.68, Dependencies and gates).

**Acceptance criteria.**

1. Cardinality: zero raw declarations yield `Unresolved(UNBOUND)`; two or more yield `Unresolved(CONFLICTING)`, including two equal ones; exactly one whose `installation_root` is relative, not normalized or not parseable yields `Unresolved(MALFORMED)`.
2. `installation_root_is_directory=False` yields `Unresolved(MISSING)`.
3. An installation root equal to, containing or inside any bound real path yields `Unresolved(OVERLAPPING)`.
4. Otherwise the result is `Resolved(installation_root / sha256(normalized_tenant_scope).hexdigest())`, and it is the same value for every non-overlapping set of bound paths (cross-binding identity, spec witness 1).
5. Two distinct tenant scopes yield distinct tenant roots, and no tenant root path contains its raw scope (spec witness 4).
6. The result type is closed: consumers match `Resolved | Unresolved` exhaustively. Neither function takes a `PathBinding`, `PathClass`, workload class, deployment surface or environment input from which a root could be selected, and there is no default or STATE_LEDGER-derived root (spec witness 3).
7. `PathClass` still has exactly four members and `PATH_CLASS_REGISTRY` is unchanged.

**Tests (mutation-probed).**

- `test_declaration_cardinality_and_shape_causes` (criteria 1–2; mutation: treating two equal declarations as one, or accepting a relative path, fails).
- `test_overlap_with_any_bound_path_fails_closed` (criterion 3; equal, ancestor and descendant cases; mutation: checking only STATE_LEDGER paths fails).
- `test_tenant_root_independent_of_bound_paths` (criterion 4; property over generated non-overlapping path sets).
- `test_tenant_roots_are_distinct_and_redacted` (criterion 5).
- `test_no_default_root` (criterion 6; mutation: returning a STATE_LEDGER-derived `pause-journal` path when unbound fails).
- `test_path_class_registry_unchanged` (criterion 7).

**Consumed witnesses.** Cross-process identity (spec witness 2: CLI, MCP server and daemon resolve the same tenant root) and the fail-closed refusal of each cause (exit 6 `protocol-not-bound`, Runtime spec v1.137 Rule B7 item 3) need real Runtime processes. They run at Runtime plan v2.68 criterion 15, and the old-location cutover at criterion 17, on the bound root.

**Non-goals.** No Runtime resolver, journal I/O, declaration storage location, refusal mapping, placement verification (Runtime Rule B3 keeps it), migration (Runtime Rule B8) or provisioning.

**Gate.** Implementation starts after IS spec v1.17 and this plan are ratified and applied. Accepting Runtime 160a and exposing `harness resume` also require the storage selection and its binding evidence (Runtime Rule B7 item 4).

## §2 Dependency graph

DAG delta: +1 node (U-IS-21, foundational, `Depends on: (none)`). No new within-axis edge; acyclicity is preserved. Cross-axis: one inbound edge from U-RT-160 portion 160a, in the established Runtime → IS direction.

## §3 Coverage

| Contract | Spec | Coverage |
|---|---|---|
| C-IS-01 §1.1 installation pause-journal root | IS spec v1.17 (NEW) | Covered at U-IS-21 (NEW) |
| C-IS-10 §10.4 Runtime consumer row | IS spec v1.17 | Export recorded; consumed at U-RT-160 portion 160a |

All other coverage rows are unchanged from v2.10.

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.11 (delta over v2.10) |
| Authority | IS spec v1.17 C-IS-01 §1.1; Runtime spec v1.137 Rules B3/B7/B8 and plan v2.68 U-RT-160 (criteria 15, 17); LIT `cmt-8b76cb48`, ratification `cmt-7cc5fc50` |
| Net delta | One new unit U-IS-21 and one DAG node; all earlier units, rows and criteria preserved |
| Source grounding | `harness-is/src/harness_is/path_class_registry.py`, `path_binding.py` and `path_resolver.py`, and `harness-runtime/src/harness_runtime/lifecycle/journal_workflow_pause_store.py` at this branch's base |
| Clearance | Owed after independent review and Buford's decision; none filed here |
