# Spec-to-Plan Decomposition Reference

This reference is loaded when authoring requires the per-contract procedure for surfacing atomic units, atomicity heuristics with worked examples, the spec-extension test, or contract-to-unit ratio guidance.

---

## 1. Per-contract decomposition procedure

For each specification contract:

1. **Read `Contract surface`.** The contract surface declares what the contract commits — function signatures, schemas, enumerations, composition formulas, taxonomies. This is the primary atomization target.
2. **Read specification content.** Each sub-section (§N.1, §N.2, ...) typically corresponds to one decomposable surface. Tables of schemas, enums, or lookup mappings often decompose as foundational substrate units that consumers depend on.
3. **Read `Deferred to implementation discretion`.** This is the boundary the planner must respect — deferred items are not unit scope. If a unit would commit to a deferred item, the unit is either wrong (spec extension defect) OR the specification has a gap that needs revision (back-flow finding). The planner does not bridge deferrals.
4. **Atomize per the four operational criteria** (SKILL.md §3). A complex contract typically yields 3–5 units; a simple contract typically yields 1–2.
5. **Verify trace-back.** Each unit cites the source contract by ID + section; verify by re-reading the cited section. Citation is not a label; it is a discipline.

---

## 2. Atomicity heuristics (worked examples)

Common spec-surface shapes and how they typically decompose:

### 2.1 Schema declaration → foundational unit

A schema or attribute-namespace declaration (e.g., a `lease.*` attribute namespace declared at a control-plane contract sub-section) is typically **one foundational unit** — anchor of the dependency graph. Foundational because consumers (other units that emit lease lifecycle events, the audit ledger absorber, the replay-resumption surface) depend on the schema being present before they can wire to it.

**Why one unit, not many.** A schema with N attributes is a single coherent change — the schema-definition file or module exposing the namespace. Splitting per-attribute is over-decomposition (each attribute is a single-line entry; rollback boundary at the attribute level is incoherent). Coalesce.

### 2.2 Composition formula consuming N resolvers → N + 1 units

A composition formula (e.g., a `max()` formula consuming five floor inputs) typically yields:

- N **foundational resolver units** (one per resolver function); each can be authored independently of the others.
- 1 **composition unit** depending on the N resolvers, wiring them at the formula's call-site signature.

**Why.** Each resolver has its own coherent change scope (e.g., the blast_radius_floor lookup, the operator_policy_floor lookup, the deployment-surface cross-product table). They are independently testable. The composition is the wiring layer; it is atomic at the wiring level but depends on all resolvers being present.

If two resolvers are tightly coupled (share a lookup table; share a call-site context contract), consider coalescing those two into one unit. Coupling that makes independent testing implausible is the signal for coalescing.

### 2.3 Taxonomy with N classes → 1 foundational + per-class consumer units

A taxonomy declared as a contract (e.g., an N-class lifecycle event taxonomy with per-class span name + per-class minimum attribute set) typically yields:

- 1 **foundational taxonomy-emission unit** — the emitter scaffold and the per-class span-name registry.
- Per-class **wiring units** in consuming axes if the cross-axis composition requires per-class handling. (If consumers can handle the taxonomy uniformly, the per-class units coalesce into the foundational.)

**Why split.** Per-class minimum attribute sets often have shape variation (some classes carry workflow.id, some carry lease.key, some carry retry.attempt_index). Wiring per class is per-class coherent change.

**When to coalesce.** If every class has identical attribute shape and only the span name varies, one emission unit suffices; the taxonomy is registry-driven.

### 2.4 Sub-discipline → acceptance criterion of consuming unit

A "sub-discipline" attached to a contract (e.g., a sampling discipline at a span-emission contract, or an idempotency-key derivation rule) typically attaches to the consuming unit's acceptance criterion rather than becoming a separate unit.

**Why.** Sub-disciplines are constraints on how the consuming unit behaves; they are testable as part of the unit's acceptance, not as separable change scope. A "sampling discipline" unit with no host emitter to sample is content-free.

**Counterexample.** If the sub-discipline has its own substantive scope (e.g., a sampling-policy registry consumed by multiple emitters), it becomes a foundational unit consumers depend on.

### 2.5 Cross-contract composition → dependency edge OR cross-cutting integration unit

A contract section that declares composition with N downstream namespaces (e.g., a §5.5-style composition table mapping the contract's surface to engine.*, topology.*, hitl.*, audit.*, validator.*, sandbox.* namespaces) typically becomes either:

- **Dependency edges in the graph** — each consuming unit declares the composing contract as a dependency. Lightweight; works when each consumer's composition is bounded.
- **A cross-cutting integration unit at plan §5** — when the composition logic is substantive (e.g., the wiring point where lifecycle events fan out to all six downstream namespaces is one coherent change, not six).

The choice depends on whether the composition is **at one wiring point** (cross-cutting unit) or **distributed across consumer units** (dependency edges). Both are valid; the planner picks the shape that produces fewer trivial units.

---

## 3. Spec extension test (per unit)

For each draft unit, run the three-part test:

| Test | Question | If yes |
|---|---|---|
| Library/framework | Does the unit name a library, framework, protocol, runtime, language, or specific technology not named in the cited spec contract? | **Spec extension defect.** Remove the technology reference; if the binding is needed, back-flow to Phase 5. |
| Schema fields | Does the unit's signature add fields, attributes, or behavior not declared in the cited spec contract? | **Spec extension defect.** Remove the extension; verify the contract's `Specification content` and `Deferred to implementation discretion` sections to confirm. |
| Acceptance behavior | Does the unit's acceptance criterion verify a behavior not committed by the spec contract? | **Spec extension defect.** The plan tests what the spec commits; behaviors beyond the spec are out-of-scope. |

In every case, the defect's resolution is **back-flow to Phase 5** if the surface is genuinely needed — the spec must commit to it. The planner never decides.

The test is also the planner's anti-fabrication discipline at unit granularity. A unit that names something the spec does not commit is a fabrication and a Class-1 (severe) finding under V3's discipline.

---

## 4. Contract → unit ratio guidance

| Ratio | Typical contract shape | Action |
|---|---|---|
| **1:1** | Simple contract; one coherent surface; one unit covers it. Example: a single function signature with no internal decomposition. | Author one unit. |
| **1:N (N=2–5)** | Moderate contract; multiple sub-surfaces; foundational + consumer decomposition. Example: a composition formula with N resolver inputs; a taxonomy with N classes; a multi-table lookup contract. | Author foundational unit + N consumer units. |
| **N:1** | Multiple closely-coupled contracts collapsed into one cross-cutting integration unit. Rare; use sparingly. Example: a wiring-point integration where N contracts compose at one call site. | Author one cross-cutting integration unit at plan §5; cite all N contracts in `Spec linkage`. |

Ratios above 1:5 indicate the contract is over-fragmented at the spec level (P5 finding) OR the planner is over-decomposing (anti-pattern §10 over-decomposition; coalesce).

---

## 5. Deferred-to-implementation items: NOT unit scope

This deserves its own discipline because it is the most common spec-extension failure mode.

A contract's `Deferred to implementation discretion` list enumerates items the spec deliberately did not commit. Examples encountered across the project:

- "Specific {sandboxing-technology} per cell"
- "Specific {durable-execution engine} per cell"
- "Specific {observability-backend} ingestion shape"
- "Specific {hash-algorithm} for idempotency keys"

These items are **not implementation surfaces the planner commits.** The planner's units must NOT:

- Name the specific technology ("use Firecracker microVM"; "use Temporal"; "use OTLP+Tempo")
- Author acceptance criteria that test the specific technology's behavior
- Name the specific algorithm ("use SHA-256")

If the executor needs the spec to commit, the path is:

1. Surface the gap as a Plan Class 3 finding (severe; back-flow to Phase 5).
2. Phase 5 revises the spec to commit (or to declare the deferral non-binding for a specific surface).
3. Phase 6 revision-pass absorbs the spec revision per SKILL.md §8.

**Counter-pattern.** Some deferred items are deferred *to the executor* — meaning the executor picks at execution time, but the plan still has a unit that establishes the deferral as a configuration surface. Example: "specific X policy is deferred to operator configuration" → the plan may have a unit "configuration surface for X policy" (the configuration mechanism is committed; the specific policy value is not). The test is whether the spec commits the surface-shape, not the value.

---

## 6. Multi-version contract citation discipline

When a contract has been revised (e.g., a contract v1.0 → v1.1 absorbed an adversarial-review finding), the unit cites the **latest filed version** per Workflow v1.5 §7 use-latest-version body-citation-alignment. Citing a prior version is a defect surfaced at coherence pass — it indicates the unit was authored against stale substrate. Resolution: re-read the latest version; update the citation; verify the unit's signature/surface still aligns with the latest contract content; revise the unit if not.

This is structurally analogous to the spec-writer Path A revision-pass discipline established at iter-1 and consolidated to Workflow §7 at iter-2.
