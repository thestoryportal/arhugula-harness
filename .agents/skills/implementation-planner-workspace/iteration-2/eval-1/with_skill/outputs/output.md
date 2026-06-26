# Implementation Breakdown — C-IS-02 §2 (Artifact-Tier Layering Schema)

## Status block

- **Status:** Proposed
- **Scope:** Single-contract slice — C-IS-02 §2 (`Spec_Information_Substrate_v1.md`, "§2 C-IS-02 — Artifact-tier layering schema"). Not a full IS-axis plan; this is the implementation breakdown for one contract.
- **Phase:** Phase 6 implementation planning (skill: `implementation-planner`)
- **Source-set:** `Spec_Information_Substrate_v1.md` v1.2 (C-IS-02 §2 lines 144–172; C-IS-05 §5 consulted for cross-axis dependency identification, lines 248–282)
- **Exit gate:** P6-CK clearance

## Shape decision

This deliverable is a single-contract decomposition, so the four full-plan shapes (axis-led / component-led / milestone-led / dependency-graph-led) do not apply at slice scope. The internal structure is **dependency-graph-led within the slice**: the contract surface ("Five-tier model with tier-to-artifact-class mapping and tier composition contract") decomposes into one foundational schema unit and one consumer wiring unit, ordered by their dependency edge. Grounded in the C-IS-02 §2 sub-surface structure: the five-tier table + Substrate-residence + Survival-semantics bullets form one coherent schema surface; the Cross-tier-traceability bullet is a distinct wiring surface with an external dependency on C-IS-05.

## §1 Slice summary

C-IS-02 §2 commits a five-tier artifact layering schema — a tier enumeration (`working` / `episodic` / `semantic` / `procedural` / `durable`) with per-tier metadata (semantic role, substrate residence, survival scope) plus a three-part tier composition contract (substrate-residence rule, survival semantics, cross-tier traceability). The breakdown yields **2 atomic units**: U-IS-C02-1 (foundational — the tier enum, per-tier metadata, and the substrate-residence + survival-semantics composition rules, which are properties of the enum and fold into its acceptance criterion) and U-IS-C02-2 (consumer — the cross-tier traceability wiring, a distinct surface depending on the C-IS-05 state-ledger entry shape via `action_id`). U-IS-C02-1 is the foundational anchor. The `Deferred to implementation discretion` paragraph (specific path conventions, tier-internal subdivisions, deployment-surface overrides) is out-of-scope for both units.

## §2 Atomic units

### U-IS-C02-1: Five-tier artifact layering schema — tier enum, per-tier metadata, and composition rules

**Scope.** Author the five-tier artifact layering schema: the `working` / `episodic` / `semantic` / `procedural` / `durable` tier enumeration with each tier's per-tier metadata (semantic role, substrate residence, survival scope), and the substrate-residence classification rule plus survival-semantics guarantee that are properties of that enumeration. Single coherent change: one schema surface exposing the tier model to all consumers.

**Spec linkage.** `C-IS-02 §2` "Specification content" five-tier table (lines 158–164); `C-IS-02 §2` "Tier composition contract" — "Substrate residence" bullet (line 168) and "Survival semantics" bullet (line 169).

**Surfaces affected.** Artifact-tier schema definition module (the module exposing the tier enumeration and per-tier metadata to IS-axis and cross-axis consumers).

**Signatures introduced or modified.** A five-member tier enumeration `{working, episodic, semantic, procedural, durable}` per the C-IS-02 §2 table; per-tier metadata records carrying the three table-column properties — semantic role, substrate residence (filesystem-only for `working` / `episodic`; filesystem AND git for `semantic` / `procedural` / `durable`, per the "Substrate residence" bullet), and survival scope (run-bounded for `working` / `episodic`; durable-across-runs for `semantic` / `procedural` / `durable`, per the "Survival semantics" bullet). Signatures transcribed from the C-IS-02 §2 table and composition bullets; not redesigned.

**Depends on.** (none) — foundational schema unit; anchors the dependency graph.

**Acceptance criterion (functional).** The schema exposes exactly five tiers matching the C-IS-02 §2 table. For each tier, the queryable metadata returns: (a) the semantic role string per the table's "Semantic role" column; (b) a substrate-residence value where `working` and `episodic` resolve to filesystem-only and `semantic` / `procedural` / `durable` resolve to filesystem-AND-git, consistent with the "Substrate residence" bullet; (c) a survival scope where `working` / `episodic` are run-bounded and `semantic` / `procedural` / `durable` are durable-across-runs, consistent with the "Survival semantics" bullet. No concrete filesystem path string is bound (deferred per C-IS-02 §2 "Deferred to implementation discretion").

**Notes.** The "Substrate residence" and "Survival semantics" composition bullets are not separate units: each is a property of the per-tier metadata in this schema and is independently testable only as an attribute of the tier enum, so each folds into this unit's acceptance criterion (per spec-to-plan decomposition heuristic 2.4 — sub-discipline → acceptance criterion of the consuming unit).

### U-IS-C02-2: Cross-tier traceability wiring — durable-tier entry → procedural-tier reference

**Scope.** Wire the cross-tier traceability composition: every `durable`-tier ledger entry references the `procedural`-tier artifacts in scope at the entry's write-time via the entry's `action_id` field, enabling replay of procedural-tier state at any prior durable-tier entry timestamp. Single coherent change at one wiring point.

**Spec linkage.** `C-IS-02 §2` "Tier composition contract" — "Cross-tier traceability" bullet (line 170); `C-IS-05 §5` state-ledger entry shape signature (the `action_id` field — six-field tuple table, lines 262–269) for the referenced field.

**Surfaces affected.** Cross-tier traceability wiring point coupling the durable-tier ledger entry to the procedural-tier artifact set.

**Signatures introduced or modified.** No new schema. The wiring consumes the `action_id` field of the C-IS-05 §5 six-field state-ledger entry tuple (`action_id` — "Identifier — unique per action occurrence") and the procedural-tier metadata from U-IS-C02-1. Signatures transcribed from C-IS-02 §2 and C-IS-05 §5; not redesigned.

**Depends on.** [U-IS-C02-1, U-IS-C05-ENTRY (cross-axis: IS — the C-IS-05 §5 state-ledger entry-shape unit; named here as the contract dependency; its unit ID is assigned by the C-IS-05 slice of the IS-axis plan)].

**Acceptance criterion (functional).** Given a `durable`-tier ledger entry with a populated `action_id`, the traceability wiring resolves the set of `procedural`-tier artifacts in scope at that entry's write-time.

**Acceptance criterion (integration).** When U-IS-C02-1 (procedural-tier identity) and the C-IS-05 §5 entry-shape unit (`action_id` field) are both present, replay of procedural-tier state at an arbitrary prior durable-tier entry timestamp is verifiable: selecting any historical durable-tier entry yields the procedural-tier artifact set that was in scope at that entry's write-time.

**Notes.** The dependency on the C-IS-05 §5 entry-shape unit is a within-IS-axis dependency surfaced by the C-IS-02 §2 "Cross-tier traceability" bullet's explicit "via the `action_id` field (per C-IS-05)" clause. It is annotated as a cross-contract dependency so the coupling is reviewable when this slice is merged into the full IS-axis plan; the consuming unit must not be ordered before the C-IS-05 entry-shape unit.

## §3 Dependency graph

Per-unit dependency lists:

- `U-IS-C02-1` — Depends on: (none)
- `U-IS-C02-2` — Depends on: [U-IS-C02-1, U-IS-C05-ENTRY (C-IS-05 §5 entry-shape unit; cross-contract within IS axis)]

Topologically sorted order (intra-slice): `U-IS-C02-1` → `U-IS-C02-2`.

External edge: `U-IS-C02-2` additionally depends on the C-IS-05 §5 state-ledger entry-shape unit (`U-IS-C05-ENTRY`, ID assigned by the C-IS-05 slice). When this slice merges into the full IS-axis plan, the C-IS-05 entry-shape unit must precede `U-IS-C02-2` in the aggregate topological sort.

Acyclic: yes. The intra-slice graph is a single edge `U-IS-C02-1 → U-IS-C02-2`; the external edge points into the C-IS-05 contract, which does not depend on C-IS-02 — no cycle.

## §4 Coverage matrix

Rows = C-IS-02 §2 sub-surfaces; columns = slice units. Cell marked where the unit cites the sub-surface at `Spec linkage`.

```
C-IS-02 §2 sub-surface                              | U-IS-C02-1 | U-IS-C02-2
----------------------------------------------------|------------|------------
Five-tier table (lines 158–164)                     |     X      |
Composition contract — Substrate residence (l.168)  |     X      |
Composition contract — Survival semantics (l.169)   |     X      |
Composition contract — Cross-tier traceability (l.170)|          |     X
C-IS-05 §5 entry shape (action_id field) [external] |            |     X
```

Every C-IS-02 §2 specification sub-surface has at least one column mark; every slice unit column has at least one row mark. No coverage gaps within the C-IS-02 §2 slice. The `Deferred to implementation discretion` paragraph (line 172) is intentionally uncovered — it is a non-commitment and is not unit scope.

## §5 Cross-cutting integration units

None. The C-IS-02 §2 slice does not produce an N:1 contract-to-unit collapse; both units sit at §2.

## §6 Open items

None blocking. One observation for the merge into the full IS-axis plan: `U-IS-C02-2`'s dependency `U-IS-C05-ENTRY` is a placeholder for the C-IS-05 §5 state-ledger entry-shape unit. When this slice is integrated, that dependency must be rebound to the actual C-IS-05 unit ID and the aggregate topological sort re-verified. No spec-shaped gap was surfaced during this decomposition — the C-IS-02 §2 contract is fully traceable and self-consistent with the C-IS-05 §5 `action_id` field it references; no `Phase_7_Class_N_Tension` record is warranted.
