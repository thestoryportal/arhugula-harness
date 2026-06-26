# Implementation Breakdown — C-IS-02 §2 (Artifact-tier layering schema)

**Source contract.** `design-substrate/Spec_Information_Substrate_v1.md` §2 C-IS-02 (lines 144–172).
**Contract surface.** Five-tier model with tier-to-artifact-class mapping and tier composition contract.
**PRD requirement satisfied.** R-IS-01 (files-as-artifacts at canonical filesystem paths; artifact-tier layering as the layering contract).
**ADR commitments honored.** ADR-F2 v1.2 §Decision (artifact-tier layering composing `working` / `episodic` / `semantic` / `procedural` / `durable`); ADR-F2 v1.2 §Rationale (a) (P-IS-1 D-on-schema variation); ADD §2.2 Synthesis.

---

## 1. Decomposition rationale

C-IS-02 §2 exposes four distinct, separately-testable specification surfaces:

1. The **five-tier enumeration** (table column "Tier" + "Semantic role", lines 158–164) — a pure typed primitive.
2. The **substrate-residence policy** ("Substrate residence" column + composition-contract bullet at line 168) — a tier→substrate lookup, FS-only vs FS+git.
3. The **survival-scope contract** ("Survives across" column + composition-contract bullet at line 169) — declarative per-tier survival guarantees.
4. The **cross-tier traceability binding** (composition-contract bullet at line 170) — durable→procedural reference via `action_id`.

The four surfaces are split into four atomic units rather than collapsed because each has a distinct acceptance surface, a distinct test, and (for U-IS-C — survival) and (U-IS-D — traceability) a distinct dependency edge. This sits at the high end of the IS plan's ~1–2-units-per-contract density (17 units / 10 contracts) but is defensible: surfaces 2–4 each carry a contract bullet of their own in the spec. The enum and the residence policy are deliberately *not* collapsed — the spec itself separates the table (the canonical enum) from the composition contract (the residence rule), and "atomic" favors the split.

Acceptance criteria are held at signature/schema grade only. C-IS-02's "Deferred to implementation discretion" surface (line 172 — specific path strings such as `.harness/working/`, tier-internal subdivisions, cross-deployment-surface residence overrides) is explicitly excluded from all unit acceptance criteria; those bind at C-IS-01 path-string discretion and later phases.

---

## 2. Atomic units

### U-IS-C02-A — Artifact-tier enum primitive

- **Scope.** Define the five-value artifact-tier enum as a typed primitive in `harness-core`: `working`, `episodic`, `semantic`, `procedural`, `durable`. Each value carries its semantic-role docstring per the table (lines 160–164: per-run scratch / per-run history + in-flight conversational state / cross-run knowledge / workflow-class procedural artifacts / append-only ledgers).
- **Deliverable.** `ArtifactTier` enum (Python `enum.Enum`, Pydantic-v2-serializable) plus tier→artifact-class mapping noting that the `procedural` tier maps to the C-IS-01 artifact classes Skills, prompts, routing manifest, and the `durable` tier maps to the state-ledger.
- **Acceptance criteria.**
  - Enum has exactly five members in the canonical order `working`, `episodic`, `semantic`, `procedural`, `durable`.
  - Each member's semantic role matches the spec table verbatim.
  - Round-trips through Pydantic v2 serialization.
- **Depends on.** None (foundational primitive). Cited upstream: C-IS-01 (artifact classes referenced by the `procedural`/`durable` role mapping).
- **Trace.** C-IS-02 §2 table (lines 156–164); ADR-F2 v1.2 §Decision; R-IS-01.

### U-IS-C02-B — Tier-to-substrate-residence policy

- **Scope.** Implement the substrate-residence mapping: `working` and `episodic` → filesystem only (no git); `semantic`, `procedural`, `durable` → filesystem AND git (composition-contract bullet, line 168, the canonical reading aligned to the table).
- **Deliverable.** A pure function / lookup table `substrate_residence(tier: ArtifactTier) -> SubstrateResidence`, where `SubstrateResidence` distinguishes `FILESYSTEM_ONLY` vs `FILESYSTEM_AND_GIT`.
- **Acceptance criteria.**
  - `working` and `episodic` resolve to `FILESYSTEM_ONLY`.
  - `semantic`, `procedural`, `durable` resolve to `FILESYSTEM_AND_GIT`.
  - Mapping is total over the five-member enum (every tier resolves).
  - No specific path strings appear (deferred to implementation discretion per line 172).
- **Depends on.** U-IS-C02-A (consumes `ArtifactTier`).
- **Trace.** C-IS-02 §2 composition contract — Substrate residence (line 168); ADR-F2 v1.2 §Decision combined-tier role; R-IS-01.

### U-IS-C02-C — Tier survival-scope contract

- **Scope.** Encode each tier's "survives across" guarantee as a declarative contract: `working` survives a single inference call within a run; `episodic` survives multiple inference calls within a run (restart only via durable-execution engine replay); `semantic` survives run termination and carries into future runs; `procedural` survives run termination + workflow versioning and carries across workflow versions; `durable` survives run termination + restart + crash recovery (chain-integrity-verified per C-IS-06). The contract guarantees artifacts at tier T are readable at all future times within T's survival scope (composition-contract bullet, line 169).
- **Deliverable.** A `survival_scope(tier: ArtifactTier) -> SurvivalScope` mapping plus a `run_bounded(tier) -> bool` predicate (`True` for `working`/`episodic`, `False` for the three durable-survival tiers).
- **Acceptance criteria.**
  - Each tier's survival scope matches the spec table "Survives across" column verbatim.
  - `run_bounded` is `True` exactly for `working` and `episodic`.
  - Mapping is total over the five-member enum.
- **Depends on.** U-IS-C02-A (consumes `ArtifactTier`).
- **Trace.** C-IS-02 §2 table + composition contract — Survival semantics (line 169); ADR-F2 v1.2 §Decision; R-IS-01. Cross-reference (not a build dependency): C-IS-06 hash-chain integrity for `durable`-tier verification.

### U-IS-C02-D — Cross-tier traceability binding (durable → procedural)

- **Scope.** Implement the cross-tier traceability composition: every `durable`-tier ledger entry references the `procedural`-tier artifacts in scope at the entry's write-time via the `action_id` field, enabling replay of procedural-tier state at any prior durable-tier entry timestamp (composition-contract bullet, line 170).
- **Deliverable.** A traceability accessor that, given a `durable`-tier ledger entry, resolves the `procedural`-tier artifact set in scope at that entry's write-time via `action_id`. This unit consumes — and does NOT redefine — the C-IS-05 six-field state-ledger entry shape; it binds to the `action_id` field of that shape.
- **Acceptance criteria.**
  - Accessor resolves `procedural`-tier artifacts for a given `durable`-tier entry via its `action_id`.
  - Replay semantics: resolving against entry E yields the procedural-tier state as of E's write-time.
  - The six-field entry shape is imported, not redefined here.
- **Depends on.** U-IS-C02-A (consumes `ArtifactTier`); the C-IS-05 entry-shape carrier unit (the unit materializing the six-field state-ledger record / `action_id` field — per IS plan v2.2 footer, the entry-shape carrier in the established plan is U-IS-07). Forward/cross-contract dependency.
- **Trace.** C-IS-02 §2 composition contract — Cross-tier traceability (line 170); C-IS-05 (`action_id` field); ADR-F2 v1.2 §Decision; R-IS-01.

---

## 3. Within-contract dependency graph

```
U-IS-C02-A (tier enum)
   ├──> U-IS-C02-B (substrate-residence policy)
   ├──> U-IS-C02-C (survival-scope contract)
   └──> U-IS-C02-D (cross-tier traceability)  <-- also depends on C-IS-05 entry-shape carrier (U-IS-07)
```

Acyclic. Topological order: **A → {B, C} → D** (B and C are independent of each other and may execute in parallel). U-IS-C02-D additionally gates on the C-IS-05 entry-shape carrier landing first.

## 4. Coverage check

| Spec surface (C-IS-02 §2) | Unit |
|---|---|
| Five-tier enumeration + semantic role (lines 156–164) | U-IS-C02-A |
| Substrate residence — FS-only vs FS+git (line 168) | U-IS-C02-B |
| Survival semantics — per-tier survival scope (lines 160–164, 169) | U-IS-C02-C |
| Cross-tier traceability — durable→procedural via `action_id` (line 170) | U-IS-C02-D |
| Tier-to-artifact-class mapping (lines 146, 163–164) | U-IS-C02-A (mapping carried with the enum) |
| Deferred to implementation discretion (line 172) | Excluded by design — not an acceptance criterion of any unit |

All four C-IS-02 §2 specification surfaces are covered; the deferred surface is explicitly excluded.

## 5. Notes / boundary cautions

- Unit IDs above (`U-IS-C02-A`..`D`) are contract-scoped working labels. The canonical IS plan (`Implementation_Plan_Information_Substrate_v2_2.md`) numbers units U-IS-01..U-IS-17 globally; the actual C-IS-02 unit numbers are assigned by the plan's global topological numbering and were not re-derivable from the v2.2 file (its §2 is preserved-by-reference to v2.1, which is not co-resident in this workspace).
- C-IS-03 (combined git tier role decomposition) is a separate contract (§3) and is deliberately NOT pulled into these units.
- No framework dependency required — these are pure typed primitives and lookups in `harness-core` (Pydantic v2 + stdlib `enum`), consistent with the framework-pull discipline.
