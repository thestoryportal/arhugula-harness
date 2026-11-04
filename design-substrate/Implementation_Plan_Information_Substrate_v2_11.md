# Implementation Plan — Information Substrate (IS axis) — v2.11

*Delta over v2.10. This revision decomposes IS spec v1.17 §1.1, the installation pause-journal root that Runtime spec v1.137 Rule B7 requires, into one new foundational unit, U-IS-21. All v2.10 and earlier rows, unit bodies, criteria, dependency edges and coverage rows remain unchanged.*

**Status:** Cleared for source consumption by `.harness/clearance/implementation-plan-information-substrate-v2-11-cleared-2026-11-04.md` after independent review GREEN `cmt-b58fbcee` and integration-lead ratification `cmt-9733f3e9` at exact H `eb607692`. Corrected after independent review HOLD `cmt-8720af2b` (F1–F3): the resolution takes no tenant input (tenants stay separated by the Runtime journal key in one flat root), takes the observed real path of the root, and preserves `harness-inspect` enumeration. After HOLD `cmt-e4e959b9` (disposition `cmt-49143c9e`), witness 5 also covers the pre-upgrade inventory under an unbound declaration.

---

## §0 Authority and scope

The predecessor is `Implementation_Plan_Information_Substrate_v2_10.md`. IS spec v1.17 adds C-IS-01 §1.1 as the companion to Runtime spec v1.137 Rules B3, B7 and B8 and Runtime plan v2.68 U-RT-160 portion 160a (criteria 15 and 17). Owner profile-coder under LIT `cmt-792618a5`; scope and prerequisite owners in LIT `cmt-8b76cb48`; fork `.harness/class_1_fork_runtime_resume_cli_supersession.md`; authority `.harness/runtime-resume-contract-authority.md`.

The storage selection and its binding and retention evidence remain a separate prerequisite owned by Buford (integration lead). This plan selects no physical path, location for the declaration or retained volume. It adds no source, test, Control Plane delta or provisioning step.

## §1 New unit

### U-IS-21 — installation pause-journal root: declaration and closed resolution result (IS spec v1.17 §1.1)

**Scope.** The IS-side types and pure decisions for the one installation-scoped pause-journal root. The Runtime root resolver (U-RT-160 portion 160a) performs every effect: it reads the installation state, observes the declared directory and its real path, supplies the real paths of the run's bound §1 directories, and enforces the result. U-IS-21 performs no I/O. Tenant separation stays in the Runtime journal key (Runtime spec v1.108 §14.14.8); U-IS-21 takes no tenant input and derives no tenant path.

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
class ExistingDirectory:
    real_path: Path  # observed by the Runtime effect boundary

@dataclass(frozen=True)
class NotADirectory:
    pass

ObservedRoot = ExistingDirectory | NotADirectory

@dataclass(frozen=True)
class Resolved:
    root: Path  # the declared installation root

@dataclass(frozen=True)
class Unresolved:
    cause: UnresolvedCause

PauseJournalRootResolution = Resolved | Unresolved

def parse_declarations(
    raw: Sequence[Mapping[str, object]],
) -> PauseJournalRootDeclaration | Unresolved: ...

def resolve_root(
    declaration: PauseJournalRootDeclaration,
    observed: ObservedRoot,
    bound_real_paths: Iterable[Path],
) -> PauseJournalRootResolution: ...
```

**Depends on.** (none) — foundational. Like every IS unit it has zero outbound cross-axis edges. The inbound edge U-RT-160 portion 160a → U-IS-21 is declared from the Runtime side (Runtime plan v2.68, Dependencies and gates).

**Acceptance criteria.**

1. Cardinality: zero raw declarations yield `Unresolved(UNBOUND)`; two or more yield `Unresolved(CONFLICTING)`, including two equal ones; exactly one whose `installation_root` is relative, not normalized or not parseable yields `Unresolved(MALFORMED)`.
2. `NotADirectory` yields `Unresolved(MISSING)`.
3. An observed real path equal to, containing or inside any bound real path yields `Unresolved(OVERLAPPING)`. Only real paths are compared, so a declared root that is a symlink alias of, or into, a bound directory overlaps.
4. Otherwise the result is `Resolved(declaration.installation_root)`, the same value for every non-overlapping set of bound paths (cross-binding identity, spec witness 1).
5. The result type is closed: consumers match `Resolved | Unresolved` exhaustively. Neither function takes a tenant scope, `PathBinding`, `PathClass`, workload class, deployment surface or environment input from which a root could be selected, and there is no default or STATE_LEDGER-derived root (spec witnesses 3 and 4).
6. `PathClass` still has exactly four members and `PATH_CLASS_REGISTRY` is unchanged.

**Tests (mutation-probed).**

- `test_declaration_cardinality_and_shape_causes` (criteria 1–2; mutation: treating two equal declarations as one, or accepting a relative path, fails).
- `test_overlap_compares_real_paths` (criterion 3; equal, ancestor, descendant and symlink-alias fixtures; mutation: comparing the declared path instead of the observed real path, or checking only STATE_LEDGER paths, fails).
- `test_root_independent_of_bound_paths` (criterion 4; property over generated non-overlapping path sets).
- `test_no_default_root` (criterion 5; mutation: returning a STATE_LEDGER-derived `pause-journal` path when unbound fails).
- `test_path_class_registry_unchanged` (criterion 6).

**Consumed witnesses.** Spec witnesses 2 (cross-process identity), 4 (tenants: `None`, non-ASCII and lone-surrogate scopes in one root under the §14.14.8 key, wrong tenant absent) and 5 (`harness-inspect` inventory over a populated root, and over the pre-upgrade directory while unbound), and the fail-closed refusal of each cause (exit 6 `protocol-not-bound`, Runtime spec v1.137 Rule B7 item 3), need real Runtime processes. They run at Runtime plan v2.68 criterion 15, and the old-location cutover and pre-upgrade inventory at criterion 17.

**Non-goals.** No Runtime resolver, journal I/O, journal key or tenant encoding, declaration storage location, refusal mapping, placement verification (Runtime Rule B3 keeps it), enumeration, migration (Runtime Rule B8) or provisioning.

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
| Authority | IS spec v1.17 C-IS-01 §1.1; Runtime spec v1.137 Rules B3/B7/B8 and plan v2.68 U-RT-160 (criteria 15, 17); Runtime spec v1 §13.7 and v1.108 §14.14.8; LIT `cmt-8b76cb48`, ratification `cmt-7cc5fc50`, review HOLD `cmt-8720af2b` |
| Net delta | One new unit U-IS-21 and one DAG node; all earlier units, rows and criteria preserved |
| Source grounding | `harness-is/src/harness_is/path_class_registry.py`, `path_binding.py` and `path_resolver.py`; `harness-runtime/src/harness_runtime/lifecycle/journal_workflow_pause_store.py` (key encoding) and `admin/inspect.py` (§13.7 enumeration) at this branch's base |
| Clearance | Cleared by `.harness/clearance/implementation-plan-information-substrate-v2-11-cleared-2026-11-04.md` (ratification `cmt-9733f3e9`) |
