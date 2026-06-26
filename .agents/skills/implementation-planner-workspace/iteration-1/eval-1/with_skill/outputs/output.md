# Implementation Breakdown — C-IS-02 §2 (Artifact-Tier Layering Schema)

## Status block

- **Status:** Proposed (P6-CK clearance pending)
- **Scope:** Single-contract decomposition — `C-IS-02 §2` only (not a full-axis plan)
- **Phase:** 6 — Implementation Planning
- **Skill:** `implementation-planner` (initial authoring mode)
- **Source-set:** `Spec_Information_Substrate_v1.md` (v1.2 per ADD v1.3 attestation; §2 C-IS-02 + §1 C-IS-01 + §5 C-IS-05 read as context)
- **Entry authorization:** Operator request — implementation breakdown for C-IS-02 §2
- **Exit gate:** P6-CK

---

## Shape decision (front-matter)

**Shape: contract-scoped, dependency-graph-led.** The task scopes to one specification contract (`C-IS-02 §2`), not the full IS axis, so the canonical axis-led / milestone-led shapes do not apply at this granularity. Within the single contract the unit ordering is dictated by the dependency-graph topology: the tier-enumeration schema is the foundational anchor; the cross-tier traceability composition is the downstream consumer. Grounded in the spec §2 internal structure (a five-tier table followed by a three-clause "Tier composition contract").

---

## §1 Plan summary

`C-IS-02 §2` ("Artifact-tier layering schema") commits a five-tier model — `working` / `episodic` / `semantic` / `procedural` / `durable` — via a tier-to-semantic-role / substrate-residence / survival-scope mapping table, followed by a three-clause **Tier composition contract** (substrate residence, survival semantics, cross-tier traceability). This is a schema-plus-composition contract: per the spec-to-plan decomposition reference §2.1, a tier enumeration is a single coherent foundational unit, and per §2.5 a cross-contract composition clause (here, `durable`→`procedural` traceability via the `action_id` field) is a distinct surface that becomes either a dependency edge or its own unit.

The contract decomposes into **2 atomic units**: one foundational tier-schema unit carrying the enum, the tier-property mapping, and the substrate-residence + survival-semantics invariants; one consumer unit implementing the cross-tier traceability composition (which depends on the schema unit and cross-axis on `C-IS-05`). Foundational anchor: **U-IS-CIS02-1**.

Citations honored: `C-IS-02 §2` (primary); `C-IS-05 §5` (cross-tier traceability `action_id` field source); `C-IS-01 §1` (canonical path classes the tier paths resolve under — context only, no extension).

---

## §2 Atomic units

### U-IS-CIS02-1: Five-tier artifact-layering schema — tier enum, tier-property mapping, residence + survival invariants

**Scope.** Author the artifact-tier layering schema: the five-member tier enumeration (`working`, `episodic`, `semantic`, `procedural`, `durable`) and the per-tier property record (semantic role, substrate residence, survival scope), with the substrate-residence rule and survival-semantics rule from the Tier composition contract enforced as schema-level invariants.

**Spec linkage.** `C-IS-02 §2` (five-tier table; Tier composition contract — "Substrate residence" clause; "Survival semantics" clause).

**Surfaces affected.** The artifact-tier schema definition module (the tier enumeration type and the per-tier property record/lookup); the tier-residence invariant predicate consumed by tier-write paths.

**Signatures introduced or modified.** Five-member tier enum `{working, episodic, semantic, procedural, durable}` per `C-IS-02 §2` table. Per-tier property record carrying the three table columns: `semantic_role`, `substrate_residence` (one of: filesystem-only; filesystem+git), `survival_scope` (run-bounded; durable-across-runs) — transcribed from the `C-IS-02 §2` five-tier table, not redesigned. Substrate-residence rule: `semantic` / `procedural` / `durable` reside on filesystem AND git; `working` / `episodic` reside on filesystem only. Survival-semantics rule: an artifact at tier T is guaranteed readable at all future times within T's declared survival scope.

**Depends on.** (none) — foundational schema unit; anchors the dependency graph for this contract.

**Acceptance criterion (functional).** The tier enum exposes exactly the five members named in `C-IS-02 §2`. Querying any tier returns its property record with `substrate_residence` and `survival_scope` matching the spec table row exactly: `working` → filesystem-only, run-bounded (single inference call); `episodic` → filesystem-only, run-bounded (multiple calls within a run); `semantic` / `procedural` / `durable` → filesystem+git, durable-across-runs. The tier-residence invariant predicate returns true exactly for the (tier, substrate) pairs the spec commits and false otherwise — i.e. a `working` or `episodic` artifact asserted to git fails the predicate.

**Notes.** Specific filesystem path strings per tier (`.harness/working/`, `.harness/episodic/`, `.harness/semantic/`, …), tier-internal subdivisions (per-workload-class subdirectories), and cross-deployment-surface tier-residence overrides per ADD §3 OD-2.A are explicitly **deferred to implementation discretion** by `C-IS-02 §2` — out of unit scope. The schema commits tier identity and the residence *class* (filesystem-only vs filesystem+git), not the path literals.

---

### U-IS-CIS02-2: Cross-tier traceability composition — durable-entry → procedural-artifact reference via `action_id`

**Scope.** Implement the cross-tier traceability contract: every `durable`-tier ledger entry carries a reference to the `procedural`-tier artifacts in scope at the entry's write-time, via the `action_id` field, enabling replay of procedural-tier state at any prior `durable`-tier entry timestamp.

**Spec linkage.** `C-IS-02 §2` (Tier composition contract — "Cross-tier traceability" clause); `C-IS-05 §5` (state-ledger entry shape — source of the `action_id` field referenced by the traceability clause).

**Surfaces affected.** The cross-tier traceability resolver — the function that, given a `durable`-tier entry, resolves the `procedural`-tier artifact set in scope at that entry's write-time; the durable-tier write path's population of the `action_id` linkage.

**Signatures introduced or modified.** A resolver mapping a `durable`-tier ledger entry to the set of `procedural`-tier artifacts in scope at its write-time, keyed on the entry's `action_id` field. The `action_id` field shape is owned by `C-IS-05 §5`; this unit consumes it as the join key and does not introduce or redefine it.

**Depends on.** [U-IS-CIS02-1 (the tier schema — `durable` and `procedural` tier identities and residence), U-IS-CIS05-* (the `C-IS-05` state-ledger entry-shape unit(s) supplying the `action_id` field — cross-contract dependency within the IS axis)].

**Acceptance criterion (functional).** Given a `durable`-tier ledger entry with a populated `action_id`, the resolver returns the `procedural`-tier artifact set referenced by that `action_id`. The reference is one-directional (`durable` → `procedural`) per the spec clause.

**Acceptance criterion (integration).** Given a sequence of `durable`-tier entries written at distinct timestamps with evolving `procedural`-tier state, resolving any prior entry yields the `procedural`-tier artifact set as it stood at that entry's write-time — i.e. procedural-tier state is replayable at any prior durable-tier entry timestamp, as the spec clause commits.

**Notes.** The `action_id` field is defined by `C-IS-05` — this unit must cite `C-IS-05`'s latest filed version and consume the field as authored there; if `C-IS-05` does not in fact expose `action_id` at the shape this composition needs, that is a spec-internal reconciliation gap (a P5 back-flow finding), not something this unit resolves. See Open items OI-1.

---

## §3 Dependency graph

Per-unit direct dependencies:

```
U-IS-CIS02-1   Depends on: (none)
U-IS-CIS02-2   Depends on: [U-IS-CIS02-1, U-IS-CIS05-* (C-IS-05 entry-shape unit)]
```

Topologically sorted order:

```
1. U-IS-CIS02-1   (foundational — tier schema)
2. U-IS-CIS02-2   (consumer — cross-tier traceability; also requires the C-IS-05 entry-shape unit)
```

**Acyclic:** yes — a 2-node chain plus one external in-edge from the `C-IS-05` entry-shape unit; no cycle.

**Cross-axis callouts:** none. The `U-IS-CIS02-2` → `C-IS-05` dependency is **intra-axis** (both IS). It is flagged here as a *cross-contract* edge: when the full IS plan is assembled, `U-IS-CIS02-2` must declare the `C-IS-05` entry-shape unit by its real unit ID.

---

## §4 Coverage matrix

Rows = `C-IS-02 §2` sub-surfaces; columns = units in this breakdown.

```
                                              | U-IS-CIS02-1 | U-IS-CIS02-2 |
C-IS-02 §2 — five-tier table (enum + mapping)  |      X       |              |
C-IS-02 §2 — composition: substrate residence  |      X       |              |
C-IS-02 §2 — composition: survival semantics   |      X       |              |
C-IS-02 §2 — composition: cross-tier tracblty  |              |      X       |
```

Every `C-IS-02 §2` sub-surface has ≥1 unit; every unit cites ≥1 sub-surface. No coverage gap, no trace-omission within this contract's scope.

`C-IS-05 §5` appears as a cited dependency-source for `U-IS-CIS02-2` but is **not a row here** — `C-IS-05` is covered by its own contract's units in the full IS plan; this breakdown does not claim coverage of it.

---

## §5 Cross-cutting integration units

None. `C-IS-02 §2` decomposes cleanly into one foundational unit and one consumer unit; no N:1 cross-cutting collapse is warranted. The cross-tier traceability composition is a single bounded surface, kept as `U-IS-CIS02-2` rather than promoted to a §5 cross-cutting unit, because it composes exactly two contracts at one resolver.

---

## §6 Open items

- **OI-1 — `action_id` field availability in `C-IS-05`.** `C-IS-02 §2`'s cross-tier traceability clause names the `action_id` field "(per C-IS-05)". `U-IS-CIS02-2` is sound only if `C-IS-05 §5`'s six-field entry-shape signature in fact exposes a field usable as the `durable`→`procedural` join key. If it does not, the discrepancy is a spec-internal reconciliation gap — surface as a Plan Class 3 finding and back-flow to Phase 5; the planner does not bridge it. Non-blocking for `U-IS-CIS02-1`.
- **OI-2 — Deferred path conventions.** `C-IS-02 §2` defers tier path strings, tier-internal subdivisions, and OD-2.A deployment-surface residence overrides to implementation discretion. No unit in this breakdown commits them; if execution requires the residence-override *surface* to be a committed configuration shape (vs. an ad-hoc executor choice), that is a Phase 5 back-flow question per the spec-to-plan §5 counter-pattern test. Non-blocking.

---

## Coherence pass

- **Atomicity (§3).** Both units are single coherent changes (one schema; one resolver), single-session-sized, independently testable given declared dependencies, with coherent rollback boundaries. PASS.
- **Spec-traceability (§4.2).** Both units cite `C-IS-02 §2` by ID and sub-section; `U-IS-CIS02-2` additionally cites `C-IS-05 §5`. No ID-only citations. PASS.
- **Dependency-awareness (§4.3).** Graph is a 2-node DAG plus one external in-edge; acyclic; foundational unit declares `(none)`. PASS.
- **Implementation-grade detail (§4.4).** Surfaces named at logical level; signatures transcribed from the spec table, not redesigned; acceptance criteria testable. No library/framework/path-literal introduced. PASS.
- **No spec extension.** Verified against `C-IS-02 §2` "Deferred to implementation discretion" — no unit commits a deferred item; deferrals recorded as OI-2. PASS.
```
