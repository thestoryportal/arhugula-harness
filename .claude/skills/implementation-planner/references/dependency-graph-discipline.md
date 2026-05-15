# Dependency-Graph Discipline Reference

This reference is loaded when authoring requires the acyclic-invariant verification procedure, foundational-first ordering, cross-axis dependency callout convention, transitive-dependency discipline, or cycle resolution worked examples.

---

## 1. The acyclic invariant

The aggregate dependency graph must be a DAG (directed acyclic graph). Cycles are not "complex dependencies that need careful ordering" — cycles indicate an atomization defect. There are exactly three causes:

1.1 **Two units are doing the same work split.** Unit A and Unit B both author part of the same coherent change; each references the other because each is incomplete on its own. Resolution: coalesce A and B into one unit.

1.2 **One unit is doing two things.** Unit A author both a foundational substrate (e.g., an enum) and a consumer that uses the substrate; another unit B uses the enum and is depended on by A's consumer half. The cycle is A ↔ B because A's substrate half is depended on by B, but B is depended on by A's consumer half. Resolution: split A into A.foundational (substrate only) and A.consumer (consumer only); A.foundational has no dependency on B; A.consumer depends on B.

1.3 **A perceived bidirectional need is actually unidirectional with mutual visibility.** Unit A needs Unit B's type to compile; Unit B does not need Unit A's type at all — but the author misread "B references A" from a configuration table mentioning A's name. Resolution: drop the spurious edge B → A; the graph is acyclic with A → B.

In all three cases, the cycle is a signal to re-examine atomization. The planner does not "carefully order cyclic dependencies" — there is no such ordering.

---

## 2. Topological sort verification procedure

After atomization and dependency declaration, verify a topological sort exists by the leaf-stripping algorithm:

2.1 Initialize: the set of "remaining units" = all plan units.

2.2 Loop:
- Find all leaves in the remaining set — units whose dependencies are all outside the remaining set (i.e., their dependencies are either `(none)` or only on already-removed units).
- If at least one leaf exists, remove it from remaining. Record removal order — this is the topological sort.
- If no leaves exist and remaining is non-empty, the residue is a cycle (or set of strongly connected components). Identify the cycle's participants and apply §1 resolution.

2.3 Terminate when remaining is empty (graph is acyclic; topological sort recorded) OR when a residue persists (cycle found; re-atomize).

The topological sort is the recommended execution order. It is not a commitment; the executor MAY parallelize independent branches. The sort exists to demonstrate acyclic-ness, not to constrain execution.

---

## 3. Foundational-first ordering

Foundational units have minimal or no dependencies. Concretely, foundational units are those whose `Spec linkage` cites a contract that declares **substrate** for other contracts to consume. Categories observed across the project:

| Foundational category | Typical shape | Example (synthetic) |
|---|---|---|
| Data type declaration | Enum or sealed class | `SandboxTier` enum per a sandboxing-axis contract |
| Schema declaration | Attribute namespace | `lease.*` attribute namespace per a control-plane contract |
| Taxonomy declaration | N-class enumeration with per-class metadata | N-class lifecycle event taxonomy |
| Manifest format declaration | JSON/YAML schema for declarative config | Routing manifest schema |
| Substrate seam contract | Cross-axis interface declaration | Span-attribute namespace seam between info-substrate and control-plane |

These anchor the graph. Consumer units depend on them. If a foundational unit's content depends on a consumer unit, the foundational is mis-classified — either the unit is actually a consumer that misnames itself as foundational, or the dependency is spurious. Re-examine.

**Heuristic.** Foundational units should be authorable from spec alone — no other units' products needed at author-time. If authoring a "foundational" unit requires reading another unit's intended product, it is not foundational.

---

## 4. Cross-axis dependency callouts

When a unit in axis X depends on a unit in axis Y, annotate the dependency with the axis label:

```
Depends on: [U-AS-2, U-CP-7 (cross-axis: CP), U-AS-4]
```

Cross-axis dependencies are not defects; they are **integration points** that reviewers should examine deliberately. The annotation makes the integration visible. Without the annotation, cross-axis coupling becomes invisible to readers scanning a single axis's section.

When the plan shape is axis-led (per SKILL.md §6), cross-axis dependencies are also surfaced at the dependency-graph section (§3 of the plan) as a separate cross-axis edge list. Example:

```
Cross-axis dependency edges:
- U-AS-3 → U-CP-7 (action surface → control plane; operator policy floor)
- U-CP-12 → U-AS-15 (control plane → action surface; sandbox span composition)
- U-IS-4 → U-CP-5 (information substrate → control plane; idempotency-key
   derivation consumes lifecycle event substrate)
```

When the plan shape is component-led or milestone-led, cross-axis remains marked at the unit declaration; the §3 cross-axis edge list is optional but recommended for plans with > 5 cross-axis edges.

---

## 5. Transitive-dependency discipline

A unit declares its **direct** dependencies, not transitive ones. If A → B → C:

- A declares: `Depends on: [B]`
- B declares: `Depends on: [C]`
- C declares: `Depends on: (none)` (or its own dependencies)
- A does NOT declare: `Depends on: [B, C]`

The transitive closure (A → B, A → C) is computed at topological sort. Inline transitive declaration is:

5.1 **Redundant** — adds no information the topological sort doesn't compute.

5.2 **A maintenance burden** — if B's dependencies change, A's transitive declaration drifts. The plan revision pass would need to update all transitive declarations.

5.3 **A coherence-pass landmine** — reviewers cannot tell whether `Depends on: [B, C]` means "A directly needs both" or "A needs B which needs C and someone listed both for safety."

Direct dependencies only.

**Counterexample.** If A genuinely needs both B and C directly (e.g., A's signature consumes types from both, neither through the other), both are declared. The test is: does A use C's product without going through B's product? If yes, C is a direct dependency.

---

## 6. Cycle resolution worked examples

### 6.1 Cycle from category confusion

**Scenario.**
- U-CP-1 = lifecycle event taxonomy declaration (the eight event classes + per-class span name registry).
- U-CP-7 = `engine.*` span attribute namespace declaration consumed by every lifecycle event class.

Author writes: `U-CP-1 Depends on: [U-CP-7]` (because the taxonomy emits spans that carry engine.* attributes) AND `U-CP-7 Depends on: [U-CP-1]` (because engine.* is consumed by the taxonomy's events).

Cycle: U-CP-1 ↔ U-CP-7.

**Resolution.** U-CP-1 is the foundational taxonomy declaration; the taxonomy declares span names + per-class minimum attribute sets; the attribute sets reference engine.* by name but do not depend on engine.* being implemented for U-CP-1's product to be complete. U-CP-7 declares the engine.* namespace; it consumes nothing from U-CP-1. The cycle dissolves: U-CP-1 has `Depends on: (none)`; U-CP-7 has `Depends on: (none)`. Neither depends on the other; both are foundational.

A separate consumer unit (U-CP-15 = lifecycle event emitter wiring) depends on both: `U-CP-15 Depends on: [U-CP-1, U-CP-7]`.

**Diagnosis.** The original author conflated "X references Y at the surface" with "X depends on Y for completeness." Schema references in declarations are not implementation dependencies. The taxonomy is complete when its declaration is complete, independent of whether engine.* is implemented yet.

### 6.2 Cycle from one-unit-doing-two-things

**Scenario.**
- U-AS-3 = sandbox_tier composition function (per a composition formula contract).
- U-AS-5 = mcp_server_trust_tier_floor resolver (one of the five floor inputs to U-AS-3).

Author writes: `U-AS-3 Depends on: [U-AS-5]` (composition consumes the resolver) AND `U-AS-5 Depends on: [U-AS-3]` (the resolver needs the composition's call-site context type).

Cycle: U-AS-3 ↔ U-AS-5.

**Resolution.** U-AS-5 does not depend on U-AS-3. It depends on the call-site context schema (which is its own foundational — call it U-AS-0). U-AS-3 also depends on U-AS-0. The corrected graph: U-AS-0 → U-AS-5 → U-AS-3; U-AS-0 → U-AS-3.

**Diagnosis.** The author confused "U-AS-5 consumes a type that U-AS-3 also consumes" with "U-AS-5 depends on U-AS-3." Shared-substrate dependency does not create a cycle — both depend on the substrate, neither depends on the other.

### 6.3 Cycle from two-units-doing-same-work-split

**Scenario.**
- U-IS-4 = idempotency-key derivation function (consumes lifecycle event substrate to derive root and step keys).
- U-CP-5 = lifecycle-event substrate emission (emits the events that carry idempotency keys).

Author writes: `U-IS-4 Depends on: [U-CP-5]` (derivation consumes events) AND `U-CP-5 Depends on: [U-IS-4]` (events need idempotency keys to emit).

Cycle: U-IS-4 ↔ U-CP-5.

**Resolution.** The two units are co-authoring the same coherent change — idempotency-key keys are an attribute of lifecycle events; the derivation and the emission are mutually constitutive at the spec level. Splitting them into two units creates the cycle. Coalesce into one unit: U-IS-4-CP-5 = lifecycle-event substrate with idempotency-key derivation (cite both contracts at `Spec linkage`).

**Alternative resolution** (when coalescing is undesirable): re-examine the spec to see whether idempotency keys are derived **after** event emission (U-CP-5 emits an event with a placeholder; U-IS-4 fills the key post-emission) OR **before** (U-IS-4 derives the key; U-CP-5 emits the event with the key present). The spec answer determines which unit is foundational. If the spec is silent, the gap is a back-flow finding to Phase 5.

**Diagnosis.** Two units co-authoring one coherent change is a decomposition defect; coalesce or back-flow.

---

## 7. Coverage discipline at unit-level dependencies

A unit's declared dependencies must be **sufficient** for its acceptance criterion. The test:

For each acceptance-criterion clause, identify what other units' products the verification requires. If a required product is not declared as a dependency, the omission is a defect.

Example. Unit U-AS-3 acceptance criterion: "Given a tool contract with declared `minimum_tier` and a call_site_context with declared blast_radius_tier ..., the function returns the `max()` of the five floor inputs."

Required products from other units:
- `SandboxTier` enum (U-AS-1's product) — needed for "returns ... SandboxTier"
- `blast_radius_floor` resolver (U-AS-2's product) — needed for "max() of the five floor inputs"
- `sandbox_tier_floor` resolver (U-AS-4's product) — same
- `mcp_server_trust_tier_floor` resolver (U-AS-5's product) — same
- `operator_policy_floor` resolver (U-AS-6's product) — same

If U-AS-3 declares `Depends on: [U-AS-1, U-AS-2]` only, the omissions (U-AS-4, U-AS-5, U-AS-6) are coverage defects — surfaced at coherence pass.

The rule: every product referenced by acceptance must be declared as a dependency.

---

## 8. Dependency-graph textual representation in the plan

The plan's §3 dependency graph section presents the graph in a readable textual form. Recommended shape:

```
## §3 Dependency graph

### Foundational layer (Depends on: (none))
- U-IS-1: durable-state schema declaration
- U-AS-1: SandboxTier enum
- U-CP-1: lifecycle event taxonomy

### Layer 1
- U-AS-2: blast_radius_floor resolver (depends on U-AS-1)
- U-AS-4: sandbox_tier_floor resolver (depends on U-AS-1)
- U-CP-5: lifecycle event emission (depends on U-CP-1)
- ...

### Layer 2
- U-AS-3: sandbox_tier composition (depends on U-AS-1, U-AS-2, U-AS-4, U-AS-5, U-AS-6)
- U-CP-15: lifecycle event emitter wiring (depends on U-CP-1, U-CP-5, U-CP-7)
- ...

### Cross-axis dependency edges
- U-AS-6 → U-CP-?? (operator policy floor consumes CP-side policy registry)
- ...

### Topological sort (one valid order)
U-IS-1, U-AS-1, U-CP-1, U-AS-2, U-AS-4, U-AS-5, U-AS-6, U-CP-5, ..., U-AS-3, ..., U-CP-15
```

Layer-based grouping makes acyclic-ness visible at a glance. The topological sort line gives the executor a default ordering; parallel branches in the layered view are explicit.
