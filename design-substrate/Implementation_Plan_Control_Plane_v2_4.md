# Implementation Plan — Control Plane v2.4

**Status:** Proposed

**Date:** 2026-05-15

**Revision:** v2.4 — verbatim-divergence conformance revision pass; absorbs the operator-ratified §4A resolution recorded at `.harness/verbatim_audit_cp_plan.md` (the CP-plan verbatim-divergence cluster). Conforms the 7-unit verbatim-divergence cluster (U-CP-01, U-CP-10, U-CP-19, U-CP-22, U-CP-43, U-CP-46, U-CP-47) to the cited `Spec_Control_Plane` vocabulary, with cross-unit propagation handled in the same pass.

**Revision date:** 2026-05-15

**Source set:** CP spec v1.3 (§3.5/§9.1 amendments) + CP spec v1.2 (§10–§24 preserved-verbatim contracts) + ADR-D1 v1.2 + ADR-D5 v1.3 + ADR-D6 v1.2 + ADD v1.3 + PRD v1.1 (substrate versions unchanged from v2.3; absorption deepened at the 7-unit cluster + literally-enumerating consumer U-CP-48)

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar discipline (use-latest-version body-citation-alignment per §7.4; byte-exact citation per §7.4.2); `implementation-planner` SKILL.md §8 revision-pass sub-mode + §9 cross-mode citation + fidelity discipline. `CLAUDE.md` §1.3 canonical authority chain: per-axis spec v1.x is canonical for per-axis plan v2.x — the plan is the artifact in error in every divergence row, the spec conforms it.

**Entry authorization:** Operator ratification of the §4A conform-to-spec recommendation for the 7-unit cluster (`.harness/verbatim_audit_cp_plan.md` §4A.7 operator action 1). U-CP-11 (§4A.7 action 2) and U-CP-08 (§4A.7 action 3) are carried — not resolved — per §0.8 below.

---

## §0 Change-note (v2.3 → v2.4)

### §0.1 Scope

This revision pass absorbs the operator-ratified **§4A Resolution Recommendation — CP-plan verbatim-divergence cluster** appended to `.harness/verbatim_audit_cp_plan.md`. That audit report is the **canonical systemic-tension record** for the cluster (per the Phase-7 checkpoint decision recorded at the §4A preamble: no per-unit Tension 005+ proliferation; the cluster is tracked in the single audit record). The §4A recommendation classified the cluster as a single systemic pattern — un-audited "verbatim" acceptance-criterion claims in the Phase-6 CP plan whose signatures do not transcribe the cited Phase-5 spec contract — and the operator ratified the authority-chain-determinate reading: conform the plan to the spec.

Seven CP plan units carry an acceptance criterion asserting a signature is materialized "per §X **verbatim**" against a `Spec_Control_Plane` contract whose vocabulary the signature does not transcribe. All seven are conformed at this pass:

- **U-CP-01** — `ROUTING_NAMESPACE_SCHEMA` 4-attribute set conformed to CP spec §1.4 attribute table.
- **U-CP-10** — `LifecycleEventClass` 8-class enum + span-name map conformed to CP spec §5.1.
- **U-CP-19** — `ResumptionKind` 5-class enum + bindings conformed to CP spec §8.1.
- **U-CP-22** — `TopologyPattern` 6-pattern enum + `CascadePolicy` domain + admissibility conformed to CP spec §10.1/§10.2/§10.3 per the **already-decided Tension 002 direction** (operator sign-off 2026-05-15; CP-AL-1 conformed at commit `45f104f`). This unit's plan-file body still carried stale Set-1 text; v2.4 completes the unfinished plan-side absorption of an already-settled decision.
- **U-CP-43** — `GateLevel` enum + `*_GATE_LEVEL_FLOOR` constants conformed to CP spec §19.1 (with §16.2 cardinality cross-check). **Partial conformance** — see §0.8 carried items.
- **U-CP-46** — `AUDIT_NAMESPACE_SCHEMA`, `HITL_SPAN_NAMESPACE_SCHEMA`, `PERSONA_TIER_AUDIT_EMISSION` conformed to CP spec §20.4/§20.5/§20.6.
- **U-CP-47** — `ValidatorFailClass` enum, `VALIDATOR_FAIL_METADATA`, `VALIDATOR_FAIL_NAMESPACE_SCHEMA` conformed to CP spec §21.1/§21.5.

**Cross-unit propagation (same pass).** Conforming a foundational enum renames every downstream consumer that **literally enumerates** the renamed values in plan text. The §4A recommendation lists candidate consumers (U-CP-22 `TopologyPattern` → U-CP-23/24/25/31/13/35/53; U-CP-10/19/43/47 → U-CP-12/20/27/39/45/46/48). Each named consumer was inspected for **literal value enumeration** vs **symbolic type reference**:

- **Literally enumerates → full body revised at v2.4:** U-CP-23 (`PER_WORKLOAD_CLASS_TOPOLOGY` default-pattern values); U-CP-48 (`TRANSIENT_STAIRCASE_TRANSITIONS` enumerates `ValidatorFailClass` values).
- **Symbolic reference only → preserved as pointer (rename propagates at code-emission time, not in plan text):** U-CP-24, U-CP-25, U-CP-31, U-CP-13, U-CP-35, U-CP-53, U-CP-27, U-CP-39, U-CP-45 — all reference the renamed enums by **type name** only in `Inputs:` / `Signatures:` record-field type positions, never enumerating the value tokens in acceptance-criterion text. U-CP-12 (full v2.3 body) and U-CP-20 (full v2.2 body) were also inspected: U-CP-20 references `ResumptionKind` symbolically only (its `PER_RESUMPTION_OBSERVABLE_BEHAVIOR` keys on the `ResumptionKind` type; the v2.2 acceptance text does not enumerate the value tokens) — pointer-preserved. **U-CP-12 v2.3 acceptance #4 literally enumerates the `LifecycleEventClass` value tokens** — its full v2.3 body is re-included at v2.4 with acceptance #4 + the affected test name conformed; all other v2.3 U-CP-12 content (the F2-02 + F2-03 retry-surface absorption) is carried forward verbatim.

**Verbatim-claim discipline (v2.4 authoring invariant).** This revision pass exists because the prior plan carried "verbatim" claims that did not transcribe the cited spec. Every acceptance criterion in this file asserting "verbatim" / "exactly N" / "matches §X" was authored by opening the cited `design-substrate/` spec section, copying the canonical value names + cardinality directly from the spec text, and pasting into the plan — never transcribing from memory or from the superseded plan body. Per-claim verification is recorded at §0.10.

### §0.2 Sections preserved verbatim

| Section | Preservation rationale |
|---|---|
| §1.1 Contract inventory; §1.2 Cluster decomposition realized; §1.3 Substrate-version citation alignment | Substrate versions unchanged at v2.4; cluster decomposition unchanged; no contract added/removed |
| §1.4 F2-12 carry-forward declaration (✅ CLOSED at v2.2) | No regression; preserved as closure record |
| U-CP-02 through U-CP-09 | No verbatim divergence; U-CP-07 carried verbatim from v2.3 (its v2.3 retry.* absorption is on the audit clean-list) |
| U-CP-11, U-CP-13, U-CP-14 through U-CP-18 | No literal-enumeration of a renamed value; U-CP-11 carried (pending operator decision — see §0.8) |
| U-CP-20, U-CP-21 (v2.2 bodies) | U-CP-20 references `ResumptionKind` symbolically only; U-CP-21 on audit clean-list |
| U-CP-24, U-CP-25, U-CP-26, U-CP-27 | Symbolic enum reference only; rename propagates at code-emission |
| U-CP-28 through U-CP-42 | No verbatim divergence; no literal-enumeration of a renamed value |
| U-CP-44, U-CP-45 | Symbolic enum reference only |
| U-CP-49 through U-CP-55 | No verbatim divergence; U-CP-55 v2.2 body preserved |
| §3 dependency graph (Levels 0–8; edge enumeration; cycle audit) | No graph delta at v2.4 — enum/namespace renames do not change graph topology |
| §4 coverage matrix | No coverage delta at v2.4 — same contracts covered; only the vocabulary is corrected |
| §[carry-forwards] | Inherited unchanged ([CF-1] F2-12 ✅ CLOSED) |

### §0.3 Sections revised (v2.3 → v2.4)

| Section | Revision shape | Resolves |
|---|---|---|
| U-CP-01 Signatures + acc #1 + tests | `ROUTING_NAMESPACE_SCHEMA` 4-attribute set conformed to CP spec §1.4: `routing.provider`, `routing.model`, `routing.layer`, `routing.binding_rationale` | §4A cluster — U-CP-01 |
| U-CP-10 Signatures + acc #1 + acc #2 + tests | `LifecycleEventClass` 8 values + span-name map conformed to CP spec §5.1 | §4A cluster — U-CP-10 |
| U-CP-19 Signatures + acc #1 + acc #2 + tests | `ResumptionKind` 5 values + `RESUMPTION_KIND_BINDINGS` conformed to CP spec §8.1 | §4A cluster — U-CP-19 |
| U-CP-22 Signatures + acc #1 + acc #2 + acc #3 + tests | `TopologyPattern` 6 values conformed to CP spec §10.1; `CascadePolicy` domain conformed to CP spec §10.2 string-literal field domain; acc #2 section cite corrected §10.3→§10.2; admissibility conformed to CP spec §10.3 | §4A cluster — U-CP-22 (Tension 002 plan-side absorption) |
| U-CP-43 Signatures + acc #1 + acc #3 + acc #4 + tests | `GateLevel` enum conformed to CP spec §19.1/§16.2 `{auto, ask, deny}`; `BLAST_RADIUS_GATE_LEVEL_FLOOR` + `PERSONA_TIER_GATE_LEVEL_FLOOR` conformed verbatim to CP spec §19.1; `MCP_TRUST` + `DEPLOYMENT_SURFACE` floors flagged (carried) | §4A cluster — U-CP-43 (partial) |
| U-CP-46 Signatures + acc #1 + acc #2 + acc #3 + acc #4 + dependent acc + tests | `AUDIT_NAMESPACE_SCHEMA` 7 attrs conformed to CP spec §20.4; `HITL_SPAN_NAMESPACE_SCHEMA` restructured to the 4-span/per-span-attribute shape of CP spec §20.6 (section cite corrected §20.5→§20.6); `PERSONA_TIER_AUDIT_EMISSION` conformed to CP spec §20.5 (section cite corrected §20.4→§20.5) | §4A cluster — U-CP-46 |
| U-CP-47 Signatures + acc #1 + acc #2 + acc #3 + tests | `ValidatorFailClass` 5 values conformed to CP spec §21.1; `VALIDATOR_FAIL_METADATA` conformed to CP spec §21.1; `VALIDATOR_FAIL_NAMESPACE_SCHEMA` 3 attrs conformed to CP spec §21.5 | §4A cluster — U-CP-47 |
| U-CP-23 Signatures + acc #2 + tests (consumer) | `PER_WORKLOAD_CLASS_TOPOLOGY` default-pattern values conformed to U-CP-22 conformed `TopologyPattern`; cross-checked against CP spec §11.1 | Cross-unit propagation — U-CP-22 |
| U-CP-12 acc #4 + one test name (consumer; full v2.3 body re-included) | `LifecycleEventClass` value-token enumeration in acc #4 conformed to U-CP-10 conformed enum; all other v2.3 content carried verbatim | Cross-unit propagation — U-CP-10 |
| U-CP-48 acc #2 + acc #5 + tests (consumer) | `TRANSIENT_STAIRCASE_TRANSITIONS` enumeration of `ValidatorFailClass` values conformed to U-CP-47 conformed enum; `PALETTE_RESTRICTION_TABLE` `HITLResponse` set unaffected (U-CP-37 is on audit clean-list) | Cross-unit propagation — U-CP-47 |

### §0.4 Coverage matrix delta

**No coverage matrix delta at v2.4.** Every contract covered before this pass remains covered, and no contract newly enters coverage. The revision conforms the *vocabulary* of already-covered acceptance criteria to the cited spec sections; it does not add or remove a contract-to-unit mapping. The §4 coverage matrix is preserved verbatim per §0.2. (Stated explicitly per `implementation-planner` SKILL.md §8 step 5 — a vocabulary-conformance pass with no contract-set change has a null coverage delta.)

### §0.5 Dependency graph delta

**No dependency graph delta at v2.4.** Enum and namespace renames do not change which units a unit depends on — the dependency edges are between *units*, not between *enum value tokens*. Every `Depends on:` declaration in the 7 conformed units + 3 revised consumers is preserved exactly. The aggregate DAG node count, edge count, topological sort, and acyclic invariant are all unchanged from v2.3. (Consumer scoping at §0.1 confirmed no consumer's dependency set changed: U-CP-23/U-CP-12/U-CP-48 retain their v2.1/v2.3 dependency declarations verbatim.)

### §0.6 Substrate-version-citation table

No substrate-version delta from v2.3.

| Substrate | Version cited at v2.4 |
|---|---|
| ADR-D1 | v1.2 |
| ADR-D5 | v1.3 |
| ADR-D6 | v1.2 |
| ADD | v1.3 |
| PRD | v1.1 |
| CP spec | v1.3 (§3.5/§9.1 amendments); v1.2 §10–§24 preserved-verbatim contracts cited at their v1.2 declaration sites per the v1.3 change-note "preserved verbatim into v1.3" clause |
| OD spec | v1.3 (cross-axis citation at U-CP-12 via U-IS-07 — carried from v2.3) |
| Workflow | v1.8 |

Per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment. The 7 cluster units cite `Spec_Control_Plane` sections at their canonical-current declaration version: §1.4/§5.1/§8.1/§10.1/§10.2/§10.3/§19.1/§16.2/§20.4/§20.5/§20.6/§21.1/§21.5 are all v1.2-declared sections preserved verbatim into v1.3 — cited as the latest filed version.

### §0.7 Status

`Status: Proposed` preserved per `implementation-planner` SKILL.md §8 status-posture clause — promotion to `Accepted` requires P6-CK clearance of this revision pass.

### §0.8 Forward-flagged concerns (v2.4)

| Concern | v2.4 disposition |
|---|---|
| v2.3 §0.8 rows (U-CP-07 retry.* + U-CP-12 §9.1 + §5.4 absorption) | ✅ CLOSED at v2.3; carried verbatim — not reopened |
| **U-CP-08 `FallThroughCause` enum** — spec §3.2 (`on_layer_exceed_budget`) declares **no enum**; it is a procedure. The plan invents a 4-value `FallThroughCause` enum. There is nothing to "conform to" — the chain is genuinely silent. | **[carried — pending operator decision per §4A.7]** Per §4A.4 item 1: a plan unit declaring an H_T structure the spec does not commit is a design extension (`CLAUDE.md` I-2 / X-AL-3) that Phase 7 may not silently absorb. Routes as a §2.7.6 Class 1 fork of a *distinct shape* — operator decides between (a) `spec-writer` extends CP spec §3.2 to commit the enum, or (b) operator sanctions the plan-extension with recorded rationale. **NOT conformed at this pass** — out of scope for the verbatim-conformance cluster. |
| **U-CP-11 `LEASE_NAMESPACE_SCHEMA`** — acc #1 claims "five attributes per §5.3 verbatim: `lease.id, lease.holder, lease.acquired_at, lease.duration_ms, lease.event_kind`"; CP spec §5.3 declares `lease.key, lease.holder, lease.ttl_ms, lease.mechanism, lease.release_cause`. Cardinality 5 holds; only `lease.holder` matches by name. | **[carried — pending operator decision per §4A.7]** Per §4A.4 item 2: whether `lease.id ≈ lease.key` / `lease.duration_ms ≈ lease.ttl_ms` is a naming-refinement or a divergence is an operator judgment the planner does not own. On the strict verbatim calibration this is the same shape as the seven cluster units. **If the operator applies the strict reading, U-CP-11 joins a follow-on conformance pass as the 8th unit.** NOT conformed at this pass. |
| **U-CP-43 4-axis input-set divergence (two facets).** CP spec §19.1's 4-axis `gate_level` `max()` is over `{per_tool_gate_level, blast_radius_floor, per_mcp_server_trust_floor, persona_tier_floor}`; the plan's 4-axis `GateLevelInput` is `{persona_tier, blast_radius_tier, deployment_surface, mcp_trust_tier}`. Two distinct divergences: **(a)** the `per_tool_gate_level` axis — which §19.1 explicitly requires as the C4-contract input — is **absent** from the plan's input set; **(b)** the `deployment_surface` axis is **added** by the plan, and §19.1 does not carry it (deployment-surface gating appears only inside `sandbox_tier_floor` at CP spec §19.3, the 5-axis D2 composition). Consequently `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` is a plan-invention with no §19.1 mapping to conform to. | **[carried — pending operator decision per §4A.7]** Same spec-silence shape as U-CP-08 — a plan structure the cited section does not commit, plus a required axis the plan omits. **This is a NEW carry surfaced at this conformance pass — it extends the §4A.7 enumerated carries (U-CP-08, U-CP-11) by one.** The operator should note a third carried item was added. Disposition options: (a) `spec-writer` extends §19.1 to add `deployment_surface` and reconcile `per_tool_gate_level`, or (b) operator confirms the plan's 4-axis input set intentionally diverges from §19.1 with recorded rationale. U-CP-43 acc #5 + #6 (the `MCP_TRUST` and `DEPLOYMENT_SURFACE` floors) and acc #9 are left flagged at the unit body; the `GateLevel` value rename and the two spec-verbatim floor tables (`BLAST_RADIUS`, `PERSONA_TIER`) ARE conformed. |
| **U-CP-23 `default_pattern` single-vs-dual structural mismatch** — pre-existing v2.1 defect surfaced by the v2.4 byte-aligned conformance. `PerWorkloadClassTopologyCommitment.default_pattern` is single-valued; CP spec §11.1 row 1 (`software-engineering`) declares two primary patterns. | **[flagged — pre-existing structural defect, operator disposition]** Not a verbatim divergence and not introduced at v2.4; the conformance pass made it visible. Restructuring `default_pattern` to multi-valued is beyond verbatim-conformance scope. Operator decides whether a follow-on plan revision restructures the field. Recorded at U-CP-23 acc #2 structural-mismatch note. |
| **U-CP-43 `MCP_TRUST_GATE_LEVEL_FLOOR`** — CP spec §19.1 names a "C10 **five**-tier framework" for `per_mcp_server_trust_floor` but does not enumerate the five tier values inside §19.1, and provides no verbatim per-tier→gate-level mapping. The plan enumerates 4 invented tier names (`TIER_1_FIRST_PARTY`…`TIER_4_UNTRUSTED`) mapped to invented `GATE_*` values. AS C-AS-10 §10.1 is a per-MCP-*transport* floor table, not a named 5-tier trust enum. | **[carried — pending operator decision per §4A.7]** Same spec-silence shape. §19.1 is silent on the per-trust-tier gate-level mapping (and on the tier value names). Cardinality drift (plan 4 vs spec narrative "five") cannot be resolved by conforming to a §19.1 enumeration that does not exist. Disposition: operator decides whether §19.1 (or AS C-AS-10) is `spec-writer`-extended to enumerate the trust-tier gate-level mapping, or the plan's per-tier table is sanctioned. The `GateLevel` value-name rename (`GATE_*` → `{auto, ask, deny}`) IS applied to the `MCP_TRUST` floor's value column at acc #5; the tier-key set and the per-tier mapping content are left flagged. |
| Tension 003 (`WorkloadClass` residence) | Per §4A.4 item 4: a genuine design-residence choice (which artifact declares `WorkloadClass`), not an authority-chain-determinate conformance. **NOT folded into this cluster** — remains separately open for operator decision. U-CP-23's `PER_WORKLOAD_CLASS_TOPOLOGY` consumes `WorkloadClass` symbolically; unaffected by this pass. |
| U-CP-13 / U-CP-52 marginal citation/naming drift (§4A.4 item 3) | Not folded into this pass. §4A.4 item 3 recommends folding the citation corrections as low-cost cleanup; the operator-ratified scope (§4A.7 action 1) is the 7-unit cluster only. Recorded here for operator visibility; neither is a fork. |

### §0.9 Prior revision history (v1 → v2.3; archival)

[Preserved verbatim from v2.3 §0.9 — itself preserved from v2.2 §0.9.]

### §0.10 v2.4 coherence-pass summary

| Pass | Status |
|---|---|
| §1 Spec inventory | ✅ PASS — no substrate-version delta; no contract added/removed; cluster decomposition unchanged |
| §2 Atomic-unit decomposition | ✅ PASS — 7 cluster units conformed + 3 literally-enumerating consumers (U-CP-23, U-CP-12, U-CP-48) revised; all other units preserved verbatim per revision-pass scope discipline (`implementation-planner` SKILL.md §8 step 4). Each conformed unit remains a single coherent change (one enum/namespace declaration or one composition surface) per SKILL.md §3.1 |
| §3 Dependency graph | ✅ PASS — no graph delta; acyclic invariant preserved (§0.5) |
| §4 Spec-traceability | ✅ PASS — every conformed acceptance criterion cites a verified `Spec_Control_Plane` section by ID + section number; citations point to canonical-current declaration sites |
| §4.4 No spec extension | ✅ PASS for the 7 conformed units — each conforms TO the spec, none extends it. ⚠️ Three spec-silence findings surfaced and **carried, not resolved** (U-CP-08, U-CP-43 `DEPLOYMENT_SURFACE`, U-CP-43 `MCP_TRUST`) per §0.8 — the planner did not invent a commitment to close any gap |
| Verbatim-claim re-verification | ✅ PASS — see Pattern P2 prevention below |

**Pattern P1 (cross-artifact name drift) prevention.** Each conformed signature's value names were verified bytewise against the cited `design-substrate/Spec_Control_Plane` table substrate during authoring: §1.4 routing attr table; §5.1 eight-event-class table + span-name column; §8.1 `resumption.kind` enum table; §10.1 six-pattern table + §10.2 `TopologyDeclaration` field domain; §19.1 `gate_level` rule + `blast_radius_floor` / `persona_tier_floor` blocks + §16.2 gate-level range; §20.4 seven `audit.*` table + §20.5 per-tier emission table + §20.6 four-span HITL table; §21.1 five-class fail table + §21.5 three `validator.fail.*` table.

**Pattern P2 (verbatim-claim-contradicted) prevention.** Every acceptance criterion in this file asserting "verbatim" / "exactly N" was re-verified post-authoring against the cited spec section: U-CP-01 acc #1 ↔ §1.4 (4 attrs); U-CP-10 acc #1+#2 ↔ §5.1 (8 classes + 8 span names); U-CP-19 acc #1+#2 ↔ §8.1 (5 kinds + 1:1 bindings); U-CP-22 acc #1 ↔ §10.1 (6 patterns), acc #2 ↔ §10.2 (3-value field domain), acc #3 ↔ §10.3 (admissibility); U-CP-43 acc #1 ↔ §19.1+§16.2 (3-value gate level), acc #3 ↔ §19.1 `blast_radius_floor`, acc #4 ↔ §19.1 `persona_tier_floor`; U-CP-46 acc #1 ↔ §20.4 (7 attrs), acc #2 ↔ §20.6 (4 spans), acc #4 ↔ §20.5 (per-tier table); U-CP-47 acc #1+#2 ↔ §21.1 (5 classes), acc #3 ↔ §21.5 (3 attrs). The SCREAMING_SNAKE_CASE rendering of spec lowercase-hyphen identifiers is a Python-stack naming convention preserved where the token stems match 1:1 (per audit Findings-rejected item 6); the conformance corrects the *stems*, not the casing.

---

## §1 Spec inventory

[§1.1 Contract inventory + §1.2 Cluster decomposition + §1.3 Substrate-version citation alignment preserved verbatim from v2.3.]

### §1.4 F2-12 carry-forward declaration (✅ CLOSED at v2.2; preserved at v2.4)

[Preserved verbatim from v2.3 §1.4. F2-12 closure record intact; no v2.4 reopening.]

---

## §2 Atomic-unit decomposition

### §2.1 Cluster 1 — Routing, fallback, breaker, retry (C-CP-01 through C-CP-04)

[U-CP-02 through U-CP-09 preserved verbatim from v2.3 (U-CP-07 carried with its v2.3 retry.* absorption — on the audit clean-list). U-CP-01 conformed at v2.4 per the §4A cluster resolution; full revised content below.]

#### U-CP-01 — Declare `routing.*` namespace + per-attribute schema (v2.4 amendment — `ROUTING_NAMESPACE_SCHEMA` 4-attribute set conformed to CP spec §1.4 verbatim per the §4A verbatim-divergence cluster resolution)

**Implements:** [C-CP-01 §1.4]

**Depends on:** (none)

**Inputs:** None (foundational; root unit of CP-axis routing namespace).

**Files affected:** CP-axis routing namespace declaration (logical: `routing-namespace-attribute-schema`).

**Signatures (v2.4 amendment):**

```
record RoutingAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  inherited_from : string  // "llm.inference parent span per OTel GenAI semconv 1.41.0"
}

const ROUTING_NAMESPACE_SCHEMA: List<RoutingAttributeSchema>  // exactly 4 entries

enum AttributeValueType { STRING, INT, FLOAT, BOOL, ENUM_REF }
enum Cardinality { LOW, MEDIUM, HIGH, PER_REQUEST }
```

**Acceptance criteria (v2.4 amendment):**

1. **(v2.4 amendment — 4-attribute set conformed to CP spec §1.4 verbatim per §4A cluster resolution; the v2.1/v2.3 set `routing.layer`/`routing.candidate`/`routing.decision_ms`/`routing.budget_exhausted` diverged from the cited contract.)** `ROUTING_NAMESPACE_SCHEMA` declares exactly four `routing.*` attributes per C-CP-01 §1.4 verbatim:
   - `routing.provider` — enum string (provider catalog); provider identity bound at call; source: F1 §1.2 capability surface
   - `routing.model` — string; model identifier within provider; source: F1 §1.2 capability surface
   - `routing.layer` — enum string ∈ `{manifest, embedding, llm_as_router, fallback}`; layer that produced the binding; source: §2 layered routing strategy
   - `routing.binding_rationale` — string (optional); short token enumeration of which manifest entry / which classifier label / which fallback trigger drove the binding; source: per-layer mechanism
2. Each attribute's `inherited_from` field cites parent `llm.inference` span per OTel GenAI semconv 1.41.0. The `routing.*` attributes attach to the `llm.inference` span emitted per `Spec_Action_Surface_v1.md` C-AS-14 §14.2 `anthropic.*` namespace (and cross-family analogs), namespace-rooted at `routing.*` per the OTel GenAI semconv extension. **[Preserved from v2.3 in intent; v2.4 wording aligned to §1.4 narrative.]**
3. The namespace does NOT carry independent sampling discipline; inherits from parent span per C-CP-24 §24.1.C. **[Preserved verbatim from v2.3.]**
4. D6 ingestion is **out-of-scope at this unit**; OD plan Session 4 ingests via U-CP-54 namespace export manifest. **[Preserved verbatim from v2.3.]**

**Tests (v2.4 amendment):** `test_routing_namespace_cardinality_four` [preserved]; `test_routing_attributes_match_spec_verbatim` (v2.4 — asserts the four §1.4 attribute names `routing.provider`/`routing.model`/`routing.layer`/`routing.binding_rationale`; replaces the deprecated v2.3 form which asserted the divergent set); `test_routing_inherits_from_llm_inference` [preserved]; `test_no_independent_sampling_discipline` [preserved].

**Rollback boundary:** Revert `ROUTING_NAMESPACE_SCHEMA` declaration. Routing observability degrades; cross-axis citation at U-CP-54 §24.1.C export manifest releases. **(v2.4 note: reverting the v2.4 conformance reintroduces the §4A verbatim divergence.)**

[U-CP-02 through U-CP-09 preserved verbatim from v2.3.]

### §2.2 Cluster 2 — F3 lifecycle + manifest (C-CP-05, C-CP-06)

[U-CP-11, U-CP-13 preserved verbatim from v2.3. U-CP-10 conformed at v2.4 per the §4A cluster resolution. U-CP-12 v2.3 body re-included with acc #4 conformed (cross-unit propagation from U-CP-10). Full revised content below.]

#### U-CP-10 — Declare 8-class F3 lifecycle event taxonomy (v2.4 amendment — `LifecycleEventClass` 8-class enum + span-name map conformed to CP spec §5.1 verbatim per the §4A verbatim-divergence cluster resolution)

**Implements:** [C-CP-05 §5.1]

**Depends on:** (none)

**Inputs:** None (foundational; root of F3 lifecycle event taxonomy).

**Files affected:** CP-axis lifecycle event class enum (logical: `lifecycle-event-class-enum`).

**Signatures (v2.4 amendment):**

```
enum LifecycleEventClass {
  WORKFLOW_START,                                     // spec §5.1 event class `workflow-start`
  STEP_BOUNDARY,                                      // spec §5.1 event class `step-boundary`
  FALLBACK_TRIGGER,                                   // spec §5.1 event class `fallback-trigger`
  RETRY_ATTEMPT,                                      // spec §5.1 event class `retry-attempt`
  BREAKER_TRIP,                                       // spec §5.1 event class `breaker-trip`
  LEASE_ACQUIRED,                                     // spec §5.1 event class `lease-acquired`
  LEASE_RELEASED,                                     // spec §5.1 event class `lease-released`
  RESUMPTION                                          // spec §5.1 event class `resumption`
}

record LifecycleEventClassMetadata {
  class             : LifecycleEventClass
  span_name         : string                          // canonical OTel span name
  parent_relation   : ParentRelation
}
const LIFECYCLE_EVENT_CLASS_METADATA: List<LifecycleEventClassMetadata>  // exactly 8 entries
```

**Acceptance criteria (v2.4 amendment):**

1. **(v2.4 amendment — 8-class taxonomy conformed to CP spec §5.1 verbatim per §4A cluster resolution; the v2.1/v2.3 enum carried the disjoint taxonomy `WORKFLOW_CHECKPOINT`/`WORKFLOW_FANOUT_OPEN`/`WORKFLOW_FANOUT_CLOSE`/`WORKFLOW_HITL_INVOCATION`/`WORKFLOW_RESUMPTION`/`WORKFLOW_FALLBACK_TRIGGERED`/`WORKFLOW_BREAKER_TRIPPED`.)** `LifecycleEventClass` declares exactly eight values per C-CP-05 §5.1 verbatim — the SCREAMING_SNAKE_CASE rendering of the §5.1 "Event class" column: `WORKFLOW_START` (`workflow-start`), `STEP_BOUNDARY` (`step-boundary`), `FALLBACK_TRIGGER` (`fallback-trigger`), `RETRY_ATTEMPT` (`retry-attempt`), `BREAKER_TRIP` (`breaker-trip`), `LEASE_ACQUIRED` (`lease-acquired`), `LEASE_RELEASED` (`lease-released`), `RESUMPTION` (`resumption`).
2. **(v2.4 amendment — span-name map conformed to CP spec §5.1 "Span name" column verbatim.)** Each value maps to a canonical OTel span name per §5.1:
   - `WORKFLOW_START` → `workflow.start`
   - `STEP_BOUNDARY` → `step.boundary`
   - `FALLBACK_TRIGGER` → `fallback.triggered`
   - `RETRY_ATTEMPT` → `retry.attempt`
   - `BREAKER_TRIP` → `breaker.tripped`
   - `LEASE_ACQUIRED` → `lease.acquired`
   - `LEASE_RELEASED` → `lease.released`
   - `RESUMPTION` → `workflow.resumption`
3. Taxonomy is closed at cardinality 8 — extension requires Workflow §4.1.2 Class-2 F3 revision. **[Preserved from v2.3.]**
4. D6 ingestion delegates to U-CP-54 §24.1.B. **[Preserved from v2.3.]**

**Tests (v2.4 amendment):** `test_lifecycle_event_class_cardinality_eight` [preserved]; `test_class_to_span_name_match_spec_verbatim` (v2.4 — asserts the eight §5.1 event-class names + the eight §5.1 span-name-column values; replaces the deprecated v2.3 form which asserted the divergent taxonomy and span names); `test_taxonomy_closed` [preserved].

**Rollback boundary:** Revert `LifecycleEventClass` enum. F3 lifecycle event substrate dissolves; U-CP-12 per-class attribute composition loses discriminator; U-CP-20 resumption observable behavior loses class anchor. **(v2.4 note: reverting reintroduces the §4A verbatim divergence.)**

#### U-CP-12 — Implement per-class attribute composition + per-class sampling discipline (v2.4 amendment — acceptance #4 `LifecycleEventClass` value-token enumeration conformed to U-CP-10 conformed enum per cross-unit propagation; all v2.3 F2-02 + F2-03 content carried verbatim)

**Implements:** [C-CP-05 §5.2 (per-class attribute composition including v1.3 `engine.replay_disposition` required-attribute at `workflow.resumption`), §5.4 (sampling discipline including v1.3 retry surface rows + retry-budget-exit-boundary discrimination + dual-emission); cross-cite C-CP-09 §9.1 (4-attribute `engine.*` namespace canonical declaration) for the `workflow.resumption` required-attribute composition] **[Preserved verbatim from v2.3.]**

**Depends on:** [U-CP-07, U-CP-10, U-CP-11, U-CP-15, U-CP-19, U-CP-21, U-IS-07 (cross-axis: IS)] **[Preserved verbatim from v2.3.]**

**Inputs:** [Preserved verbatim from v2.3 — retry.* 6-attribute child span schema + 3-field parent event schema; lifecycle event class enum (U-CP-10, now the v2.4-conformed taxonomy); lease namespace; `EngineClass`; `ResumptionKind` (now the v2.4-conformed enum); `engine.*` 4-attribute namespace; F2 state-ledger entry shape.]

**Files affected:** [Preserved verbatim from v2.3.]

**Cross-axis substrate consumed:** [Preserved verbatim from v2.3 — `STATE_LEDGER_ENTRY_SHAPE_EXPORT` (C-IS-10 §10.1 → U-IS-07).]

**Signatures:** [Preserved verbatim from v2.3 — `PerClassAttributeSet`, `SamplingRate`, `SamplingDisposition`, `PER_CLASS_ATTRIBUTE_SETS` (8 entries), `SAMPLING_DISPOSITIONS` (8 entries), and the v2.3 retry-surface additions `RetrySurfaceKind`, `SamplingOverrideRule`, `RetrySurfaceSamplingDisposition`, `RETRY_SURFACE_SAMPLING_DISPOSITIONS` (2 entries). The `PerClassAttributeSet.class` and `SamplingDisposition.class` fields are typed `LifecycleEventClass` — they consume U-CP-10's v2.4-conformed enum by type; no signature text change is required by the rename.]

**Acceptance criteria (v2.4 amendment to #4; all others preserved verbatim from v2.3):**

1. `PER_CLASS_ATTRIBUTE_SETS` declares exactly eight entries per C-CP-05 §5.2 verbatim, one per `LifecycleEventClass` value. **[Preserved verbatim from v2.3.]**
2. `workflow.checkpoint` event composes with F2 entry shape via U-IS-07 — required attributes include `action_id`, `prior_event_hash` from F2 six-field shape. **[Preserved verbatim from v2.3.]**
3. `workflow.resumption` event composes with U-CP-21 `engine.*` 4-attribute namespace per C-CP-09 §9.1; required attributes at `workflow.resumption`: `engine.class` + `engine.replay_disposition`; the required-attribute set agrees byte-exact with U-CP-20 acceptance #2. **[Preserved verbatim from v2.3.]**
4. **(v2.4 amendment — `LifecycleEventClass` value-token enumeration conformed to U-CP-10 v2.4-conformed enum per cross-unit propagation; the v2.3 text enumerated the disjoint taxonomy.)** `SAMPLING_DISPOSITIONS` declares per C-CP-05 §5.4 for the eight `LifecycleEventClass` entries — `WORKFLOW_START`, `STEP_BOUNDARY`, `FALLBACK_TRIGGER`, `RETRY_ATTEMPT`, `BREAKER_TRIP`, `LEASE_ACQUIRED`, `LEASE_RELEASED`, `RESUMPTION`. Per CP spec §5.4: `workflow.start` is always-sampled; `step.boundary` is base-rate (tail-keep on failure classification); `fallback.triggered`/`fallback.exhausted`, `breaker.tripped`, `retry.attempt` (2nd-fail onward), `lease.acquired`/`lease.released`, `workflow.resumption` carry the §5.4 per-row sampling rate. **Scope clarification (carried from v2.3):** the retry surface sampling discipline at CP spec v1.3 §5.4 (retry.attempt parent event + retry-attempt child span rows) lives outside the `LifecycleEventClass` taxonomy and is declared at acceptance #6 + #7 + #8 + #9 below using `RETRY_SURFACE_SAMPLING_DISPOSITIONS`. **(v2.4 note: the v2.3 text incorrectly asserted all eight entries `ALWAYS_SAMPLED` against the divergent taxonomy; v2.4 conforms the value-token list to the §5.1 taxonomy AND aligns the sampling-rate prose to the §5.4 per-row table — `step.boundary` is base-rate per §5.4, not always-sampled.)**
5. Per-class attribute composition is deterministic given inputs; runtime emission validates `required_attributes` set is fully populated. **[Preserved verbatim from v2.3.]**
6. `RETRY_SURFACE_SAMPLING_DISPOSITIONS` declares exactly two entries per CP spec v1.3 §5.4 + ADR-D6 v1.2 §1.2.2.4 verbatim. **[Preserved verbatim from v2.3.]**
7. retry.attempt parent event sampling rules — `always_sampled_overrides` declares exactly two ordered rules per CP spec v1.3 §5.4. **[Preserved verbatim from v2.3.]**
8. retry-attempt child span sampling — `default_rate = BASE_RATE`; `tail_keep_on_attribute = "retry.fail_class"`. **[Preserved verbatim from v2.3.]**
9. Dual-emission discipline per CP spec v1.3 §3.5 + ADR-D6 v1.2 §1.2.2.3. **[Preserved verbatim from v2.3.]**

**Tests (v2.4 amendment to one test name; all others preserved verbatim from v2.3):** `test_per_class_attribute_sets_cardinality_eight`, `test_checkpoint_composes_with_f2_entry`, `test_resumption_composes_with_engine_namespace`, `test_engine_replay_disposition_required_at_workflow_resumption`, `test_workflow_resumption_attribute_composition_agrees_with_u_cp_20_acceptance_2`, `test_sampling_dispositions_per_class_match_spec_5_4` (v2.4 — renamed from the v2.3 `test_sampling_dispositions_all_always_sampled`, which baked the divergent "all always-sampled" assertion; the v2.4 test asserts the §5.1 eight-class token set + the §5.4 per-row sampling rate), `test_sampling_dispositions_lifecycle_cardinality_eight_preserved`, `test_required_attributes_enforced`, `test_retry_surface_sampling_dispositions_cardinality_two`, `test_retry_attempt_parent_event_default_base_rate_first_attempt_with_budget`, `test_retry_attempt_parent_event_always_sampled_attempt_number_ge_two`, `test_retry_attempt_parent_event_always_sampled_at_budget_exit`, `test_retry_attempt_parent_event_override_rules_evaluated_first_match_wins`, `test_retry_attempt_child_span_default_base_rate_per_cell_tunable`, `test_retry_attempt_child_span_tail_keep_on_fail_class`, `test_dual_emission_both_paths_emit_per_retry`, `test_dual_emission_collapse_to_event_only_forbidden`, `test_dual_emission_collapse_to_span_only_forbidden`.

**Rollback boundary:** [Preserved verbatim from v2.3.]

[U-CP-13 preserved verbatim from v2.3 — `WorkflowManifestEntry.topology_pattern` is typed `TopologyPattern` (symbolic reference only; no value-token enumeration in acceptance text); the U-CP-22 rename propagates at code-emission time.]

### §2.3 Cluster 3 — D1 engine + replay (C-CP-07, C-CP-08, C-CP-09)

[U-CP-14 through U-CP-18, U-CP-20, U-CP-21 preserved verbatim from v2.3 (U-CP-20 v2.2 body — references `ResumptionKind` symbolically only; U-CP-21 v2.2 body — on the audit clean-list). U-CP-19 conformed at v2.4 per the §4A cluster resolution; full revised content below.]

#### U-CP-19 — Declare `ResumptionKind` 5-class taxonomy (v2.4 amendment — `ResumptionKind` enum + `RESUMPTION_KIND_BINDINGS` conformed to CP spec §8.1 verbatim per the §4A verbatim-divergence cluster resolution)

**Implements:** [C-CP-08 §8.1]

**Depends on:** [U-CP-15]

**Inputs:** `EngineClass` enum (U-CP-15).

**Files affected:** CP-axis resumption kind enum (logical: `resumption-kind-enum`).

**Signatures (v2.4 amendment):**

```
enum ResumptionKind {
  ENGINE_REPLAY,                                      // spec §8.1 `engine_replay`; event-sourced-replay engines
  SAVE_POINT_RESUME,                                  // spec §8.1 `save_point_resume`; save-point-checkpoint engines
  JOURNAL_RESUME,                                     // spec §8.1 `journal_resume`; pure-pattern-no-engine engines
  RECONCILER_CONVERGE,                                // spec §8.1 `reconciler_converge`; reconciler-loop engines
  SEGMENT_REPLAY                                      // spec §8.1 `segment_replay`; WAL-segment engines
}

record ResumptionKindBinding {
  engine_class    : EngineClass
  resumption_kind : ResumptionKind
}
const RESUMPTION_KIND_BINDINGS: List<ResumptionKindBinding>  // exactly 5 entries (1:1 with EngineClass)
```

**Acceptance criteria (v2.4 amendment):**

1. **(v2.4 amendment — 5-class taxonomy conformed to CP spec §8.1 `resumption.kind` column verbatim per §4A cluster resolution; the v2.1/v2.3 enum carried the divergent values `REPLAY_FROM_EVENT`/`RESTORE_FROM_CHECKPOINT`/`RECONSTRUCT_FROM_LEDGER`/`RECONVERGE_VIA_RECONCILER`/`RESUME_FROM_WAL_SEGMENT`.)** `ResumptionKind` declares exactly five values per C-CP-08 §8.1 verbatim — the SCREAMING_SNAKE_CASE rendering of the §8.1 `resumption.kind` column: `ENGINE_REPLAY` (`engine_replay`), `SAVE_POINT_RESUME` (`save_point_resume`), `JOURNAL_RESUME` (`journal_resume`), `RECONCILER_CONVERGE` (`reconciler_converge`), `SEGMENT_REPLAY` (`segment_replay`).
2. **(v2.4 amendment — 1:1 mapping conformed to CP spec §8.1 "Engine class" column verbatim.)** `RESUMPTION_KIND_BINDINGS` declares the 1:1 mapping `EngineClass → ResumptionKind` per §8.1:
   - `event-sourced-replay` → `ENGINE_REPLAY`
   - `save-point-checkpoint` → `SAVE_POINT_RESUME`
   - `pure-pattern-no-engine` → `JOURNAL_RESUME`
   - `reconciler-loop` → `RECONCILER_CONVERGE`
   - `WAL-segment` → `SEGMENT_REPLAY`
3. Taxonomy closed at cardinality 5; extension requires Workflow §4.1.2 Class-2 D1 revision. **[Preserved from v2.3.]**

**Tests (v2.4 amendment):** `test_resumption_kind_cardinality_five` [preserved]; `test_resumption_kind_bindings_1to1_with_engine_class` (v2.4 — asserts the five §8.1 `resumption.kind` value names + the §8.1 engine-class 1:1 mapping; replaces the deprecated v2.3 form which asserted the divergent values); `test_taxonomy_closed` [preserved].

**Rollback boundary:** Revert `ResumptionKind` enum + bindings. U-CP-20 resumption observable behavior loses kind discriminator; F2-12 carry-forward narrative loses anchor. **(v2.4 note: reverting reintroduces the §4A verbatim divergence.)**

[U-CP-20, U-CP-21 preserved verbatim from v2.3 — see §0.1 consumer-scoping note.]

### §2.4 Cluster 4 — D4 topology + sub-agent (C-CP-10, C-CP-11, C-CP-12)

[U-CP-24 through U-CP-27 preserved verbatim from v2.3 — symbolic enum reference only; no value-token enumeration in acceptance text. U-CP-22 conformed at v2.4 per the §4A cluster resolution (Tension 002 plan-side absorption). U-CP-23 revised at v2.4 per cross-unit propagation. Full revised content below.]

#### U-CP-22 — Declare 6-pattern `TopologyPattern` enum + admissibility predicate (v2.4 amendment — `TopologyPattern` + `CascadePolicy` conformed to CP spec §10.1/§10.2 verbatim; completes the plan-side absorption of the already-decided Tension 002)

**Implements:** [C-CP-10 §10.1, §10.2, §10.3]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying enum unit).

**Files affected:** CP-axis topology pattern enum (logical: `topology-pattern-enum`); CP-axis topology admissibility predicate (logical: `topology-admissibility-predicate`).

**Signatures (v2.4 amendment):**

```
enum TopologyPattern {
  SINGLE_THREADED_LINEAR,                             // spec §10.1 pattern 1 `single-threaded-linear`
  ORCHESTRATOR_WORKERS,                               // spec §10.1 pattern 2 `orchestrator-workers`
  DECENTRALIZED_HANDOFF,                              // spec §10.1 pattern 3 `decentralized-handoff`
  HIERARCHICAL_DELEGATION,                            // spec §10.1 pattern 4 `hierarchical-delegation`
  EVALUATOR_OPTIMIZER,                                // spec §10.1 pattern 5 `evaluator-optimizer`
  PARALLELIZATION                                     // spec §10.1 pattern 6 `parallelization`
}

// CP spec §10.2 declares `cascade_policy` as a string-literal FIELD DOMAIN on
// TopologyDeclaration, not a named enum. The plan materializes the domain as a
// named enum CascadePolicy whose values are the §10.2 domain literals verbatim.
enum CascadePolicy {
  PAUSE,                                              // spec §10.2 domain literal "pause"
  PROCEED,                                            // spec §10.2 domain literal "proceed"
  CASCADE_CANCEL                                      // spec §10.2 domain literal "cascade-cancel"
}

function is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool
    // §10.3 cross-pattern admissibility per workload class
```

**Acceptance criteria (v2.4 amendment):**

1. **(v2.4 amendment — 6-pattern taxonomy conformed to CP spec §10.1 verbatim per Tension 002 / §4A cluster resolution; the v2.1/v2.3 enum carried the divergent values `SINGLE_AGENT`/`SEQUENTIAL_HANDOFF`/`PARENT_FANOUT_AGGREGATE`/`RECONCILER_MESH`/`ROUTER_DELEGATE`/`PIPELINE_STAGES`.)** `TopologyPattern` declares exactly six values per C-CP-10 §10.1 verbatim — the SCREAMING_SNAKE_CASE rendering of the §10.1 six-pattern taxonomy table "Pattern" column: `SINGLE_THREADED_LINEAR` (`single-threaded-linear`), `ORCHESTRATOR_WORKERS` (`orchestrator-workers`), `DECENTRALIZED_HANDOFF` (`decentralized-handoff`), `HIERARCHICAL_DELEGATION` (`hierarchical-delegation`), `EVALUATOR_OPTIMIZER` (`evaluator-optimizer`), `PARALLELIZATION` (`parallelization`).
2. **(v2.4 amendment — `CascadePolicy` domain conformed to CP spec §10.2 verbatim; section citation corrected §10.3 → §10.2 — §10.2 is the `TopologyDeclaration.cascade_policy` field-domain declaration site, §10.3 is the disjoint admissibility prose.)** `CascadePolicy` declares exactly three values — the SCREAMING_SNAKE_CASE rendering of the CP spec §10.2 `TopologyDeclaration.cascade_policy` string-literal field domain `"pause" | "proceed" | "cascade-cancel"`: `PAUSE` (`pause`), `PROCEED` (`proceed`), `CASCADE_CANCEL` (`cascade-cancel`). **Note:** the spec declares a *field domain*, not a named enum — `enum CascadePolicy` is the permitted plan-side materialization of that domain (per the §4A.4 U-CP-22 note); the value tokens are the §10.2 domain literals verbatim.
3. **(v2.4 amendment — admissibility conformed to CP spec §10.3 verbatim; the v2.1/v2.3 acc #3 keyed an admissibility matrix on the invented pattern names.)** `is_admissible` returns `true` per C-CP-10 §10.3 cross-pattern admissibility annotations:
   - `HIERARCHICAL_DELEGATION` — admissible at `software-engineering` and `research` workloads when scope-bounded recursion is justified (fan-out cap 3 per parent; cascade-policy inherits parent cell)
   - `DECENTRALIZED_HANDOFF` — admissible at `pipeline-automation` per-stage-expert workflows (cascade-policy `CASCADE_CANCEL`; single-owner-at-a-time invariant)
   - `PARALLELIZATION` — admissible at `research` breadth-search and `content-creation` A/B-variant generation (cap 3–5; voting aggregator at synthesis)
   Per §10.3: non-primary patterns are admissible but not primary; the workflow-definition surface MUST accept them at the cells where they are admissible. The per-workload-class *primary* pattern is committed at C-CP-11 §11.1 (consumed at U-CP-23).
4. Taxonomy closed at cardinality 6; extension requires Workflow §4.1.2 Class-2 D4 revision. **[Preserved from v2.3.]**

**Tests (v2.4 amendment):** `test_topology_pattern_cardinality_six` [preserved]; `test_topology_pattern_values_match_spec_10_1_verbatim` (v2.4 — asserts the six §10.1 pattern names; replaces the deprecated v2.3 `test_topology_pattern_cardinality_six`-adjacent verbatim test); `test_cascade_policy_cardinality_three` [preserved]; `test_cascade_policy_values_match_spec_10_2_verbatim` (v2.4 — asserts the three §10.2 domain literals); `test_admissibility_per_workload_class_match_spec_10_3` (v2.4 — asserts the §10.3 annotations against the conformed pattern names; replaces the deprecated `test_admissibility_per_workload_class_match_spec` which keyed on invented names); `test_taxonomy_closed` [preserved].

**Rollback boundary:** Revert `TopologyPattern` + `CascadePolicy` enums + admissibility predicate. All downstream D4 units (Cluster 4 + Cluster 5) lose topology discriminator; sub-agent dispatch loses pattern selection. **(v2.4 note: reverting reintroduces the Tension 002 / §4A verbatim divergence and de-conforms CP-AL-1.)**

#### U-CP-23 — Declare per-workload-class topology commitment table (v2.4 amendment — `PER_WORKLOAD_CLASS_TOPOLOGY` default-pattern values conformed to U-CP-22 v2.4-conformed `TopologyPattern` per cross-unit propagation)

**Implements:** [C-CP-11 §11.1]

**Depends on:** [U-CP-22]

**Inputs:** `TopologyPattern` enum (U-CP-22; v2.4-conformed).

**Files affected:** CP-axis per-workload-class topology commitment (logical: `per-workload-class-topology-commitment`).

**Signatures:**

```
record PerWorkloadClassTopologyCommitment {
  workload_class       : WorkloadClass
  default_pattern      : TopologyPattern
  permitted_patterns   : Set<TopologyPattern>         // subset of TopologyPattern values
  rationale            : string                       // §11.1 verbatim
}
const PER_WORKLOAD_CLASS_TOPOLOGY: List<PerWorkloadClassTopologyCommitment>  // exactly 4 entries
```

**Acceptance criteria (v2.4 amendment to #2):**

1. `PER_WORKLOAD_CLASS_TOPOLOGY` declares exactly four entries per C-CP-11 §11.1 verbatim (one per workload class). **[Preserved from v2.3.]**
2. **(v2.4 amendment — default-pattern values conformed to U-CP-22 v2.4-conformed `TopologyPattern` per cross-unit propagation; the v2.1/v2.3 text enumerated the invented values `SEQUENTIAL_HANDOFF`/`PARENT_FANOUT_AGGREGATE`/`PIPELINE_STAGES`/`ROUTER_DELEGATE`.)** Default (primary) pattern per workload class, per C-CP-11 §11.1 "Primary topology pattern" column:
   - `software-engineering` → `EVALUATOR_OPTIMIZER` (writes); `ORCHESTRATOR_WORKERS` (reads/review/eval) — per §11.1 row 1
   - `content-creation` → `EVALUATOR_OPTIMIZER` — per §11.1 row 2
   - `pipeline-automation` → sequential default (`SINGLE_THREADED_LINEAR`); `ORCHESTRATOR_WORKERS` for idempotent parallel stages only — per §11.1 row 3
   - `research` → `ORCHESTRATOR_WORKERS` — per §11.1 row 4
   **(v2.4 conformance note:** CP spec §11.1's "Primary topology pattern" column names `evaluator-optimizer`, `orchestrator-workers`, "sequential default", `orchestrator-workers` — the v2.1/v2.3 plan's `SEQUENTIAL_HANDOFF`/`PARENT_FANOUT_AGGREGATE`/`PIPELINE_STAGES`/`ROUTER_DELEGATE` were the invented-vocabulary mappings. §11.1 row 3's "sequential default" is rendered as `SINGLE_THREADED_LINEAR` — the §10.1 pattern whose lifecycle ownership is "sole agent owns full lifecycle"; this is the §10.1-vocabulary reading of "sequential". If the operator reads §11.1 "sequential default" as intending a distinct sequenced-multi-stage pattern not in the §10.1 six-pattern set, that is a spec-residence question, not a plan-conformance question — flagged here for operator visibility, not resolved.)**
   **(v2.4 structural-mismatch note — pre-existing, surfaced by conformance.)** `PerWorkloadClassTopologyCommitment.default_pattern` is typed as a **single** `TopologyPattern` value, but CP spec §11.1 row 1 (`software-engineering`) declares **two** primary patterns — `evaluator-optimizer` (writes) and `orchestrator-workers` (reads/review/eval). The byte-aligned conformance surfaces this single-vs-dual mismatch: the §11.1 row 1 dual-pattern commitment cannot be represented in a single-valued `default_pattern` field. This is a **pre-existing v2.1 structural defect**, not introduced at v2.4 — the conformance pass merely makes it visible. Restructuring the `default_pattern` field to multi-valued is beyond the verbatim-conformance scope; recorded at §0.8 for operator disposition.
3. Permitted patterns per workload class composes with `is_admissible` from U-CP-22; no permitted pattern violates admissibility. **[Preserved from v2.3.]**
4. Workload-class commitment is the source-of-truth for U-CP-25 2D matrix anchoring. **[Preserved from v2.3.]**

**Tests (v2.4 amendment):** `test_per_workload_class_topology_cardinality_four` [preserved]; `test_default_patterns_match_spec_11_1` (v2.4 — asserts the §11.1 "Primary topology pattern" column rendered into the conformed `TopologyPattern` vocabulary; replaces the deprecated `test_default_patterns_match_spec` which baked the invented values); `test_permitted_composes_with_admissibility` [preserved].

**Rollback boundary:** Revert per-workload topology commitment. U-CP-25 2D matrix loses row anchor; workflow manifest validation at U-CP-13 loses topology default source. **(v2.4 note: reverting de-conforms the cross-unit propagation from U-CP-22.)**

[U-CP-24 through U-CP-27 preserved verbatim from v2.3.]

### §2.5 Cluster 5 through §2.6 — D4 sub-agent + D5 HITL (U-CP-28 through U-CP-42)

[U-CP-28 through U-CP-42 preserved verbatim from v2.3 — no verbatim divergence; no literal-enumeration of a renamed value. U-CP-31's `topology.cascade_policy` is a span-attribute *name* string declared at C-CP-14 §14.2 (its value enum is §14.2's `{pause, proceed, cascade-cancel}` domain — already spec-canonical; U-CP-31 references the `CascadePolicy` enum symbolically only in `Inputs:`).]

### §2.7 Cluster 7 — D5 gate-level + audit (C-CP-19, C-CP-20)

[U-CP-44, U-CP-45 preserved verbatim from v2.3 — symbolic enum reference only. U-CP-43 + U-CP-46 conformed at v2.4 per the §4A cluster resolution; full revised content below.]

#### U-CP-43 — Implement 4-axis multiplicative gate-level rule + monotonicity + `_hitl_required` predicate + persona-tier floor (v2.4 amendment — `GateLevel` enum conformed to CP spec §19.1/§16.2 verbatim; `BLAST_RADIUS` + `PERSONA_TIER` floors conformed verbatim; `MCP_TRUST` + `DEPLOYMENT_SURFACE` floors carried — see §0.8)

**Implements:** [C-CP-19 §19.1, §19.2, §19.4]

**Depends on:** [U-CP-26, U-AS-05 (cross-axis: AS), U-AS-13 (cross-axis: AS), U-AS-14 (cross-axis: AS), U-AS-15 (cross-axis: AS)]

**Inputs:** Default-downgrade rule (U-CP-26); per-MCP-server trust-tier (U-AS-13); `SandboxTier` enum (U-AS-05); 5-axis multiplicative tunable from AS C-AS-12 (U-AS-14, U-AS-15).

**Files affected:** CP-axis 4-axis multiplicative rule (logical: `four-axis-multiplicative-gate-level-rule`); cross-deployment monotonicity (logical: `gate-level-cross-deployment-monotonicity`); `_hitl_required` predicate (logical: `_hitl_required-predicate`); persona-tier floor (logical: `persona-tier-gate-level-floor`).

**Cross-axis substrate consumed.** `SANDBOX_TIER_FOUNDATIONAL_SUBSTRATE_EXPORT` (C-AS-16 §16.7 → U-AS-05); `PER_MCP_TRUST_TIER_EXPORT` (C-AS-16 §16.5 → U-AS-13); `FIVE_AXIS_MULTIPLICATIVE_TUNABLE_EXPORT` (C-AS-16 §16.2 → U-AS-14, U-AS-15).

**Signatures (v2.4 amendment):**

```
// v2.4 amendment — GateLevel conformed to CP spec §19.1 gate_level value domain
// + §16.2 "ranging {auto, ask, deny}" verbatim. The v2.1/v2.3 enum carried the
// divergent 4-value ladder GATE_NONE/GATE_NOTIFY/GATE_APPROVE/GATE_REVIEW_BOARD.
enum GateLevel { AUTO, ASK, DENY }                    // spec §19.1 / §16.2: {auto, ask, deny}

record GateLevelInput {
  persona_tier         : PersonaTier
  blast_radius_tier    : BlastRadiusTier
  deployment_surface   : DeploymentSurface
  mcp_trust_tier       : MCPTrustTier
}

record GateLevelComputation {
  inputs               : GateLevelInput
  per_axis_floors      : Map<Axis, GateLevel>
  composition_winner   : Axis
  computed_gate_level  : GateLevel
}

function gate_level(input: GateLevelInput) -> GateLevelComputation
    // multiplicative max() over the per-axis floors
function _hitl_required(input: GateLevelInput) -> bool
    // per CP spec §19.4: returns true when gate_level(input) ∈ {ask, deny}

const PERSONA_TIER_GATE_LEVEL_FLOOR: Map<PersonaTier, GateLevel>
const BLAST_RADIUS_GATE_LEVEL_FLOOR: Map<BlastRadiusTier, GateLevel>
const DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR: Map<DeploymentSurface, GateLevel>  // [carried — see §0.8]
const MCP_TRUST_GATE_LEVEL_FLOOR: Map<MCPTrustTier, GateLevel>                // [carried — see §0.8]
```

**Acceptance criteria (v2.4 amendment):**

1. **(v2.4 amendment — `GateLevel` conformed to CP spec §19.1 + §16.2 verbatim per §4A cluster resolution; the v2.1/v2.3 enum carried the divergent 4-value ladder.)** `GateLevel` declares exactly three values per C-CP-19 §19.1 `gate_level` value domain (`per_tool_gate_level` "C4 contract: `{auto, ask, deny}`") + C-CP-19 §16.2 ("the per-action gate level computed at C-CP-19 §19.1 multiplicative rule (ranging `{auto, ask, deny}`)"): `AUTO` (`auto`), `ASK` (`ask`), `DENY` (`deny`). Ordering monotonic per the §19.1/§19.4 escalation semantics: `AUTO < ASK < DENY` (`auto` → no HITL; `ask` → HITL rewrite; `deny` → structural rejection + HITL).
2. `gate_level` computes per §19.1 composition rule: `max()` over the per-axis floors. Composition deterministic given inputs. **(v2.4 note:** §19.1 enumerates the `max()` over `per_tool_gate_level`, `blast_radius_floor`, `per_mcp_server_trust_floor`, `persona_tier_floor` — see acc #9 for the §0.8-carried divergence between the plan's input axes and the §19.1 four axes.)**
3. **(v2.4 amendment — `BLAST_RADIUS_GATE_LEVEL_FLOOR` conformed to CP spec §19.1 `blast_radius_floor` block verbatim.)** `BLAST_RADIUS_GATE_LEVEL_FLOOR` per C-CP-19 §19.1 `blast_radius_floor`:
   - `read-only` → `AUTO`
   - `local-mutation` → `ASK` (configurable to `AUTO` at solo-developer per §19.1)
   - `external-reversible` → `ASK`
   - `external-irreversible` → `ASK` (with dual-control at multi-tenant-compliance per §19.1)
4. **(v2.4 amendment — `PERSONA_TIER_GATE_LEVEL_FLOOR` conformed to CP spec §19.1 `persona_tier_floor` block verbatim; the v2.1/v2.3 acc #3 claimed `SOLO_DEVELOPER → GATE_NONE` / `TEAM_BINDING → GATE_NOTIFY` / `MULTI_TENANT_COMPLIANCE → GATE_APPROVE`, which §19.1 does not state.)** `PERSONA_TIER_GATE_LEVEL_FLOOR` per C-CP-19 §19.1 `persona_tier_floor` — **all three persona tiers map to `ASK`**:
   - `solo-developer` → `ASK` (operator may override to `AUTO` for non-irreversible per §19.1)
   - `team-binding` → `ASK` (audit ledger required; no auto override on external-* per §19.1)
   - `multi-tenant-compliance` → `ASK` (audit ledger + cryptographic signature; dual-control on external-irreversible per §19.1)
5. **(v2.4 amendment — `MCP_TRUST_GATE_LEVEL_FLOOR` — `GateLevel` value-name rename applied; per-tier mapping content + tier-key cardinality CARRIED per §0.8.)** `MCP_TRUST_GATE_LEVEL_FLOOR` maps each `MCPTrustTier` value to a `GateLevel` ∈ `{AUTO, ASK, DENY}`. **CP spec §19.1 names a "C10 five-tier framework" for `per_mcp_server_trust_floor` but does not enumerate the five tier values nor a verbatim per-tier→gate-level mapping inside §19.1; AS C-AS-10 §10.1 is a per-MCP-transport floor table, not a named 5-tier trust enum.** The per-tier mapping and the tier-key set are therefore **[carried — pending operator decision per §0.8]** — the spec is genuinely silent on this surface. Only the `GateLevel` value-name conformance (`{AUTO, ASK, DENY}`) is applied at this pass.
6. **(v2.4 — `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` CARRIED per §0.8.)** `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` maps each `DeploymentSurface` value to a `GateLevel`. **CP spec §19.1's 4-axis `gate_level` `max()` does not include `deployment_surface` as an axis** — deployment-surface gating appears only inside `sandbox_tier_floor` at CP spec §19.3 (the 5-axis D2 composition). The spec §19.1 contains no per-deployment-surface→gate-level mapping. This floor table is **[carried — pending operator decision per §0.8]** (a NEW carry surfaced at this pass, extending §4A.7). Only the `GateLevel` value-name conformance is applied.
7. Cross-deployment monotonicity per §19.2: under bridging-arc traversal across persona tiers, `persona_tier_floor` ascends monotonically (never descends); tier downgrade is structurally prohibited and emits a manifest-validation error per §19.2. **(v2.4 note: §19.2 frames monotonicity on the persona-tier axis; the v2.1/v2.3 "across deployment surfaces" framing is aligned to the §19.2 persona-tier-axis text.)**
8. **(v2.4 amendment — `_hitl_required` conformed to CP spec §19.4 verbatim; the v2.1/v2.3 acc #8 said "true iff `computed_gate_level > GATE_NONE`".)** `_hitl_required` returns `true` iff `computed_gate_level ∈ {ASK, DENY}` per C-CP-19 §19.4. Consumed at U-CP-39 rewriting algorithm.
9. **Cross-finding precedent.** Per F-iter1-04 Path A closure: gate_level computation does not consume AS C-AS-12 sandbox-tier directly — the orthogonal axis composition (sandbox-tier × gate-level) is performed at U-CP-45 (5-axis composition), not here. **(v2.4 spec-silence flag:** the plan's 4-axis input set is `{persona_tier, blast_radius_tier, deployment_surface, mcp_trust_tier}`; CP spec §19.1's 4-axis `max()` is over `{per_tool_gate_level, blast_radius_floor, per_mcp_server_trust_floor, persona_tier_floor}`. The plan substituted `deployment_surface` for `per_tool_gate_level`. This input-set divergence is the substance of the §0.8 `DEPLOYMENT_SURFACE` carry — flagged here, NOT resolved.)**
10. `composition_winner` identifies which axis set the winning floor for the computed gate level. **(v2.4 orphan-sink note:** the v2.1/v2.3 acc #10 said `composition_winner` is "consumed for audit attribution at U-CP-46" via `audit.gate.composition_winner_axis`. That `audit.gate.*` attribute was dissolved at v2.4 U-CP-46 — it is not in CP spec §20.4 (see the U-CP-46 coverage-shrink note). The `composition_winner` field is therefore retained as an internal `GateLevelComputation` field with **no downstream audit sink at v2.4**; if gate-attribution audit is required H_T behavior, it is a `spec-writer` extension of §20.4 — flagged, not invented.)**

**Tests (v2.4 amendment):** `test_gate_level_cardinality_three` (v2.4 — replaces `test_gate_level_cardinality_four`); `test_gate_level_values_match_spec_19_1_16_2_verbatim` (v2.4 — asserts `{AUTO, ASK, DENY}`); `test_gate_level_monotonic_ordering` (v2.4 — `AUTO < ASK < DENY`); `test_gate_level_max_composition` [preserved]; `test_blast_radius_floor_match_spec_19_1` (v2.4 — asserts the §19.1 `blast_radius_floor` block); `test_persona_tier_floor_all_three_ask_per_spec_19_1` (v2.4 — asserts all three tiers → `ASK`; replaces the deprecated `test_persona_tier_floor_match_spec` which baked the divergent ladder); `test_cross_deployment_monotonicity` [preserved]; `test_hitl_required_predicate_ask_or_deny` (v2.4 — replaces `test_hitl_required_predicate_above_none`); `test_composition_winner_attribution` [preserved]. **Carried-item tests (NOT authored at v2.4):** tests for `MCP_TRUST_GATE_LEVEL_FLOOR` and `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` per-tier mappings are **deferred** pending the §0.8 operator decision — authoring them now would bake an unverified mapping.

**Rollback boundary:** Revert `GateLevel` enum + multiplicative rule + the conformed floors + predicate. R-CP-10 gate-level decision discipline fails; HITL invocation loses gate-level discriminator; U-CP-39 rewriting loses predicate; U-CP-27 sub-agent gate-level descent loses parent gate-level source; U-CP-45 5-axis composition loses CP-side input. Cross-axis AS edges to U-AS-05, U-AS-13, U-AS-14, U-AS-15 release. **(v2.4 note: reverting reintroduces the §4A verbatim divergence on `GateLevel` and the two conformed floor tables.)**

#### U-CP-46 — Declare 7 `audit.*` attributes + per-persona-tier emission table + HITL-event span schema (v2.4 amendment — `AUDIT_NAMESPACE_SCHEMA` conformed to CP spec §20.4 verbatim; `HITL_SPAN_NAMESPACE_SCHEMA` restructured + conformed to CP spec §20.6; `PERSONA_TIER_AUDIT_EMISSION` conformed to CP spec §20.5; section citations corrected)

**Implements:** [C-CP-20 §20.4, §20.5, §20.6]

**Depends on:** [U-CP-37, U-CP-38, U-CP-42, U-CP-43, U-CP-44, U-CP-45, U-CP-47]

**Inputs:** HITL palette (U-CP-37); placement + signature (U-CP-38); per-persona-tier crypto shape (U-CP-42); 4-axis gate-level rule + composition winner (U-CP-43; v2.4-conformed `GateLevel`); F5 signing-key resolution (U-CP-44); 5-axis composition + override (U-CP-45); validator-fail taxonomy (U-CP-47; v2.4-conformed).

**Files affected:** CP-axis audit namespace (logical: `audit-namespace-attribute-schema`); CP-axis hitl-span namespace (logical: `hitl-span-namespace-schema`); CP-axis per-persona-tier emission table (logical: `per-persona-tier-audit-emission-table`).

**Signatures (v2.4 amendment):**

```
record AuditAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  always_emitted_at : string                          // persona-tier condition per §20.4
}
const AUDIT_NAMESPACE_SCHEMA: List<AuditAttributeSchema>  // exactly 7 entries

// v2.4 amendment — CP spec §20.6 declares the HITL-event span schema as FOUR SPAN
// NAMES, each with its own per-span attribute list — NOT four flat attributes.
// The v2.1/v2.3 List<HITLSpanAttributeSchema> // exactly 4 entries flat-attribute
// shape is restructured to the per-span shape below.
record HITLSpanSchema {
  span_name        : string                           // one of the four §20.6 span names
  span_attributes  : List<string>                     // the per-span attribute list per §20.6
}
const HITL_SPAN_NAMESPACE_SCHEMA: List<HITLSpanSchema>  // exactly 4 entries (one per §20.6 span)

record PersonaTierEmissionRow {
  persona_tier              : PersonaTier
  emitted_audit_attributes  : Set<string>             // per §20.5 emission discipline
  optional_audit_attributes : Set<string>
}
const PERSONA_TIER_AUDIT_EMISSION: List<PersonaTierEmissionRow>  // exactly 3 entries
```

**Acceptance criteria (v2.4 amendment):**

1. **(v2.4 amendment — `AUDIT_NAMESPACE_SCHEMA` conformed to CP spec §20.4 verbatim per §4A cluster resolution; the v2.1/v2.3 schema carried the orthogonal gate/policy namespace `audit.gate.computed_level`/`audit.gate.composition_winner_axis`/`audit.policy.override_kind`/`audit.policy.override_scope`/`audit.policy.rotation_state_partial`/`audit.signature.key_id`/`audit.signature.verification_result` — only `audit.signature.key_id` overlapped the cited contract.)** `AUDIT_NAMESPACE_SCHEMA` declares exactly seven `audit.*` attributes per C-CP-20 §20.4 verbatim — the §20.4 "Attribute" column:
   - `audit.signature.sha256` — hex-encoded 64-character string; per-entry; per-event SHA-256 hash over ledger entry payload
   - `audit.signature.prior_hash` — hex-encoded 64-character string; per-entry; hash-chain link to prior event per C-IS-06
   - `audit.actor.id` — opaque string under each persona tier's actor-identity discipline; bounded (registry)
   - `audit.signature.value` — binary (64 bytes ed25519/ecdsa-p256; 256 bytes rsa-pss-2048); per-entry; per-entry cryptographic signature over `audit.signature.sha256`
   - `audit.signature.algorithm` — enum string ∈ `{ed25519, ecdsa-p256, rsa-pss-2048}`; low (deployment-bound)
   - `audit.signature.key_id` — opaque string (typical `harness.<deployment_id>.audit_signing_key.v<N>`); low-medium
   - `audit.signature.key_period` — integer (non-negative, monotonic per deployment); low
2. **(v2.4 amendment — `HITL_SPAN_NAMESPACE_SCHEMA` restructured to the 4-span/per-span-attribute shape of CP spec §20.6 verbatim; section citation corrected §20.5 → §20.6 — §20.6 is the HITL-event span schema, §20.5 is the per-persona-tier emission discipline. The v2.1/v2.3 form declared 4 flat attribute names — `hitl.gate.evaluated.placement` etc. — that do not appear in the spec.)** `HITL_SPAN_NAMESPACE_SCHEMA` declares exactly four entries per C-CP-20 §20.6 verbatim — the §20.6 "Span name" column, each with its §20.6 "Span attributes" list:
   - `hitl.gate.evaluated` — attributes: `hitl.gate.level`, `hitl.gate.persona_tier`, `hitl.gate.required` (bool)
   - `hitl.invocation.opened` — attributes: `hitl.gate.level`, `hitl.invocation.placement` ∈ `{pre-action, sub-agent-boundary, validator-escalation}`, `hitl.invocation.handoff_context_size_bytes`, `hitl.invocation.audit_ledger_entry_id`
   - `hitl.invocation.responded` — attributes: `hitl.response.class` ∈ `{approve, edit, reject, respond}`, `hitl.response.latency_ms`, `hitl.response.summary_hash`
   - `hitl.invocation.timed_out` — attributes: `hitl.timeout.duration_ms`, `hitl.timeout.degradation_mode_applied` ∈ `{fail-closed, escalate-secondary-channel, fail-open}`
3. Spans are **always-sampled (head=1.0, tail-keep-on-classification=true)** per CP spec §20.6 + `c7-observability` SKILL.md sampling discipline; spans carrying `audit.signature.*` attributes are always-sampled per §20.5.
4. **(v2.4 amendment — `PERSONA_TIER_AUDIT_EMISSION` conformed to CP spec §20.5 verbatim; section citation corrected §20.4 → §20.5 — §20.5 is the per-persona-tier emission discipline table. The v2.1/v2.3 per-tier content diverged wholesale.)** `PERSONA_TIER_AUDIT_EMISSION` declares per C-CP-20 §20.5 verbatim:
   - `solo-developer` — emits `audit.actor.id` only
   - `team-binding` — emits `audit.actor.id` + `audit.signature.prior_hash` (and optionally `audit.signature.sha256` + `audit.signature.value` + `audit.signature.algorithm` + `audit.signature.key_id` + `audit.signature.key_period` if team-binding deployment opts into signature posture)
   - `multi-tenant-compliance` — emits all seven `audit.*` attributes
5. Emission is **monotonic** along the persona-tier axis — the emitted set ascends across `solo-developer` → `team-binding` → `multi-tenant-compliance` per §20.5. Reordering is a Workflow §4.1.2 Class-2 D5 revision.
6. `audit.signature.*` attributes emit only at `team-binding` (opt-in) and `multi-tenant-compliance` (always) per §20.5; structurally absent at `solo-developer`.
7. D6 ingestion delegates to U-CP-54 §24.1.A (`audit.*` CP source: C-CP-20 §20.4; `hitl.*` CP source: C-CP-20 §20.6).
8. `hitl.invocation.responded` span fires only when a human response is received (timeout → `hitl.invocation.timed_out` span instead, per §20.6).
9. Attribute names are **byte-exact** per CP spec §20.4 / §20.6 verbatim; renaming requires a Workflow §4.1.2 Class-2 D5 revision.
10. Schema declaration is **purely descriptive** — emission mechanics owned by OD plan Session 4 D6 §1.2 + §1.3.
11. Cardinality enforcement: `AUDIT_NAMESPACE_SCHEMA.length == 7` and `HITL_SPAN_NAMESPACE_SCHEMA.length == 4` invariants verified at startup.

**(v2.4 coverage-shrink note — substantive, not a rename.)** The v2.1/v2.3 U-CP-46 acceptance #12/#15/#16/#17 described value-spaces for the plan-invented attributes `audit.signature.verification_result`, `audit.gate.composition_winner_axis`, `audit.policy.override_kind`, `audit.policy.override_scope`. CP spec §20.4 does not carry those attributes — the §20.4 seven-attribute set is entirely signature-focused. Conforming `AUDIT_NAMESPACE_SCHEMA` to §20.4 therefore **dissolves** the plan-invented `audit.gate.*` / `audit.policy.*` namespace and the acceptance criteria describing it (v2.1/v2.3 acc #12/#15/#16/#17 are not carried to v2.4). This is a substantive coverage shrink, not a name swap — recorded here so the operator sees the gate/policy audit-attribution surface the plan previously declared is **not** in the cited contract. If the operator judges that gate/policy audit attribution is required H_T behavior, that is a `spec-writer` extension of §20.4 (out of scope for this conformance pass) — flagged, not invented.

**Tests (v2.4 amendment):** `test_audit_namespace_cardinality_seven` [preserved]; `test_audit_attributes_match_spec_20_4_verbatim` (v2.4 — asserts the seven §20.4 `audit.*` names; replaces the deprecated form which asserted the divergent set); `test_hitl_span_namespace_cardinality_four` [preserved]; `test_hitl_span_schema_match_spec_20_6_verbatim` (v2.4 — asserts the four §20.6 span names + their per-span attribute lists; replaces the deprecated `test_hitl_span_attributes_match_spec_verbatim` which asserted 4 flat attributes); `test_per_persona_emission_cardinality_three` [preserved]; `test_solo_emits_actor_id_only` (v2.4); `test_team_emits_actor_id_plus_prior_hash` (v2.4); `test_multi_tenant_emits_all_seven` (v2.4); `test_monotonic_emission_ascending` [preserved]; `test_signature_attrs_absent_at_solo` (v2.4); `test_hitl_invocation_responded_fires_only_on_response` [preserved]; `test_attribute_names_byte_exact` [preserved]; `test_schema_purely_descriptive` [preserved]; `test_cardinality_invariants_at_startup` [preserved]. **Deprecated/dissolved (NOT carried):** `test_signature_verification_result_four_values`, `test_composition_winner_axis_four_values`, `test_override_kind_three_values`, `test_override_scope_three_values` — these tested the plan-invented `audit.gate.*` / `audit.policy.*` attributes dissolved per the coverage-shrink note.

**Rollback boundary:** Revert audit + HITL-span namespaces + per-persona emission table. R-CP-10 audit attribute composition fails; R-CP-11 HITL span schema fails; R-CP-12 multi-tenant-compliance audit attribute set fails; U-CP-54 §24.1.A export manifest loses CP-side source for `audit.*` + `hitl.*`; OD plan Session 4 D6 §1.2 ingestion loses CP source. **(v2.4 note: reverting reintroduces the §4A verbatim divergence.)**

### §2.8 Cluster 8 — D5 escalation + context revalidation (C-CP-21, C-CP-22)

[U-CP-49 through U-CP-55 preserved verbatim from v2.3. U-CP-47 conformed at v2.4 per the §4A cluster resolution. U-CP-48 revised at v2.4 per cross-unit propagation. Full revised content below.]

#### U-CP-47 — Declare 5-class fail taxonomy + `validator.fail.*` namespace (v2.4 amendment — `ValidatorFailClass`, `VALIDATOR_FAIL_METADATA`, `VALIDATOR_FAIL_NAMESPACE_SCHEMA` conformed to CP spec §21.1/§21.5 verbatim per the §4A verbatim-divergence cluster resolution)

**Implements:** [C-CP-21 §21.1, §21.5]

**Depends on:** [U-AS-03 (cross-axis: AS)]

**Inputs:** `SandboxFailClass` taxonomy (U-AS-03 cross-axis AS) — composition reference.

**Files affected:** CP-axis validator-fail class enum (logical: `validator-fail-class-taxonomy`); CP-axis validator-fail namespace (logical: `validator-fail-namespace-schema`).

**Cross-axis substrate consumed.** AS C-AS-04 `SandboxFailClass` taxonomy via U-AS-03 for cross-axis composition reference.

**Signatures (v2.4 amendment):**

```
// v2.4 amendment — ValidatorFailClass conformed to CP spec §21.1 retry-exit
// taxonomy verbatim. The v2.1/v2.3 enum carried the divergent fail-cause taxonomy
// SCHEMA_MISMATCH/TIMEOUT/RATE_LIMIT/PERMANENT_REJECTION/SANDBOX_VIOLATION.
enum ValidatorFailClass {
  TRANSIENT_RETRY,                                    // spec §21.1 `transient-retry`
  REFLEXION_RECOVERABLE,                              // spec §21.1 `Reflexion-recoverable`
  HITL_RECOVERABLE,                                   // spec §21.1 `HITL-recoverable`
  PERMANENT_FAIL_EXIT,                                // spec §21.1 `permanent-fail-exit`
  TERMINAL_FAIL_EXIT                                  // spec §21.1 `terminal-fail-exit`
}

record ValidatorFailMetadata {
  fail_class           : ValidatorFailClass
  routing              : string                       // §21.1 "Routing" column
  recovery_path        : string                       // §21.1 "Recovery path" column
}
const VALIDATOR_FAIL_METADATA: List<ValidatorFailMetadata>  // exactly 5 entries

record ValidatorFailAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const VALIDATOR_FAIL_NAMESPACE_SCHEMA: List<ValidatorFailAttributeSchema>  // exactly 3 entries
```

**Acceptance criteria (v2.4 amendment):**

1. **(v2.4 amendment — 5-class taxonomy conformed to CP spec §21.1 verbatim per §4A cluster resolution.)** `ValidatorFailClass` declares exactly five values per C-CP-21 §21.1 verbatim — the SCREAMING_SNAKE_CASE rendering of the §21.1 discriminated five-class `validator.fail.class` taxonomy table: `TRANSIENT_RETRY` (`transient-retry`), `REFLEXION_RECOVERABLE` (`Reflexion-recoverable`), `HITL_RECOVERABLE` (`HITL-recoverable`), `PERMANENT_FAIL_EXIT` (`permanent-fail-exit`), `TERMINAL_FAIL_EXIT` (`terminal-fail-exit`). Closed at cardinality 5; extension requires Workflow §4.1.2 Class-2 D5 revision.
2. **(v2.4 amendment — `VALIDATOR_FAIL_METADATA` conformed to CP spec §21.1 "Routing" + "Recovery path" columns verbatim.)** `VALIDATOR_FAIL_METADATA` declares per C-CP-21 §21.1:
   - `TRANSIENT_RETRY` — routing: Transient staircase (§21.2); recovery: C9 backoff + retry (full-jitter); cause-attribution-conditioned policy
   - `REFLEXION_RECOVERABLE` — routing: Transient staircase (§21.2); recovery: C5 reflect-step verbal feedback + C1 retry-loop
   - `HITL_RECOVERABLE` — routing: C11 HITL primitive (validator-HITL placement per §17.1 `validator-escalation`); palette `{approve, request-changes, reject}`; `request-changes` routes back as `Reflexion-recoverable`; recovery: HITL invocation
   - `PERMANENT_FAIL_EXIT` — routing: **SKIP STAIRCASE**; route directly to C11 HITL (validator-escalation per §17.1); palette `{approve, edit, reject, respond}`, restricted to `{approve, reject, respond}` at cross-trust-boundary actions; recovery: Direct HITL
   - `TERMINAL_FAIL_EXIT` — routing: **SKIP STAIRCASE**; workflow halts; HITL escalation per `c11-operator-local` SKILL.md with no recovery path; recovery: Halt + HITL notification
3. **(v2.4 amendment — `VALIDATOR_FAIL_NAMESPACE_SCHEMA` conformed to CP spec §21.5 verbatim; the v2.1/v2.3 schema carried `validator.fail.is_transient`/`validator.fail.retry_attempt` for the spec's `validator.fail.cause_attribution`/`validator.fail.permanence`.)** `VALIDATOR_FAIL_NAMESPACE_SCHEMA` declares exactly three attributes per C-CP-21 §21.5 verbatim:
   - `validator.fail.class` — enum string ∈ `{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}`; bounded (5)
   - `validator.fail.cause_attribution` — enum string from open set (`network_timeout`, `provider_outage`, `model_misfire`, `contract_violation`, `schema_violation`, `semantic_disagreement`, `policy_denial`, `human_rejection`, `time_budget_exhaust`, `capability_shortfall`) plus F5-introduced refinements (`secret_unknown`, `secret_unavailable`, `secret_expired`, `secret_locked`, `secret_revoked`); medium (open set)
   - `validator.fail.permanence` — enum string ∈ `{transient, permanent}`; derived from `validator.fail.class` (`permanent` if class ∈ `{permanent-fail-exit, terminal-fail-exit}`; `transient` otherwise); bounded (2)
4. `validator.fail.permanence` is the discriminator consumed by U-CP-48 transient staircase entry decision. **(v2.4 note: the v2.1/v2.3 acc #4 cited `is_transient` as the discriminator; conformed to the spec's `validator.fail.permanence` derived discriminator.)**
5. D6 ingestion delegates to U-CP-54 §24.1.A. **[Preserved from v2.3.]**

**Tests (v2.4 amendment):** `test_validator_fail_class_cardinality_five` [preserved]; `test_validator_fail_class_values_match_spec_21_1_verbatim` (v2.4 — asserts the five §21.1 retry-exit taxonomy values); `test_validator_fail_metadata_match_spec_21_1` (v2.4 — asserts the §21.1 Routing + Recovery columns); `test_validator_fail_namespace_cardinality_three` [preserved]; `test_validator_fail_attributes_match_spec_21_5_verbatim` (v2.4 — asserts `validator.fail.class`/`validator.fail.cause_attribution`/`validator.fail.permanence`); `test_validator_fail_permanence_derived_from_class` (v2.4). **Deprecated (NOT carried):** `test_schema_mismatch_permanent`, `test_timeout_transient`, `test_rate_limit_transient`, `test_permanent_rejection_escalates_hitl`, `test_sandbox_violation_composes_with_as` — these tested the divergent fail-cause taxonomy values.

**Rollback boundary:** Revert `ValidatorFailClass` enum + metadata + namespace. R-CP-11 validator-escalation HITL placement loses fail-class discriminator; U-CP-48 staircase loses cause input; U-CP-54 §24.1.A export manifest loses CP-side source. Cross-axis AS edge to U-AS-03 releases. **(v2.4 note: reverting reintroduces the §4A verbatim divergence.)**

#### U-CP-48 — Implement transient staircase + cause-attribution branching + palette restriction (v2.4 amendment — `TRANSIENT_STAIRCASE_TRANSITIONS` enumeration of `ValidatorFailClass` values conformed to U-CP-47 v2.4-conformed enum per cross-unit propagation)

**Implements:** [C-CP-21 §21.2, §21.4]

**Depends on:** [U-CP-07, U-CP-37, U-CP-47, U-AS-10 (cross-axis: AS), U-AS-29 (cross-axis: AS)]

**Inputs:** `RetryCause` enum (U-CP-07); HITL palette (U-CP-37); validator-fail taxonomy (U-CP-47; v2.4-conformed `ValidatorFailClass`); `secret.fail.class` taxonomy (U-AS-10 cross-axis); model catalog for summarization fallback (U-AS-29 cross-axis).

**Files affected:** CP-axis transient staircase (logical: `validator-fail-transient-staircase`); CP-axis cause-attribution branching (logical: `staircase-cause-branching`); CP-axis palette restriction rule (logical: `palette-restriction-rule`).

**Cross-axis substrate consumed.** AS C-AS-07 `secret.fail.class` taxonomy (U-AS-10); AS C-AS-13 §13.4 model-tier catalog (U-AS-29).

**Signatures:**

```
enum StaircaseStage {
  STAGE_1_REFLEXION,
  STAGE_2_RETRY_WITH_BACKOFF,
  STAGE_3_CROSS_FAMILY_FALLBACK,
  STAGE_4_LOCAL_TERMINAL,
  STAGE_5_HITL_ESCALATION
}

record StaircaseTransition {
  from_stage              : StaircaseStage
  on_cause                : ValidatorFailClass        // consumes U-CP-47 v2.4-conformed enum by type
  to_stage                : StaircaseStage
  preserves_cache_state   : bool
  emits_fallback_event    : bool
}
const TRANSIENT_STAIRCASE_TRANSITIONS: List<StaircaseTransition>

enum CrossTrustBoundaryState { NONE, CROSS_FAMILY_ACTIVE, LOCAL_TERMINAL_ACTIVE, UNTRUSTED_MCP_ACTIVE }

record PaletteRestriction {
  cross_trust_state    : CrossTrustBoundaryState
  restricted_palette   : Set<HITLResponse>
  rationale            : string
}
const PALETTE_RESTRICTION_TABLE: List<PaletteRestriction>  // exactly 4 entries

function advance_staircase(current: StaircaseStage, cause: ValidatorFailClass, attempt: int) -> StaircaseTransition
function compute_restricted_palette(state: CrossTrustBoundaryState) -> Set<HITLResponse>
```

**Acceptance criteria (v2.4 amendment to #2; all others preserved verbatim from v2.1):**

1. `StaircaseStage` declares exactly five stages per C-CP-21 §21.2 verbatim. **[Preserved verbatim from v2.1.]**
2. **(v2.4 amendment — `TRANSIENT_STAIRCASE_TRANSITIONS` `on_cause` enumeration conformed to U-CP-47 v2.4-conformed `ValidatorFailClass` per cross-unit propagation; the v2.1/v2.3 text enumerated the divergent values `SCHEMA_MISMATCH`/`TIMEOUT`/`RATE_LIMIT`/`SANDBOX_VIOLATION`/`PERMANENT_REJECTION`.)** `TRANSIENT_STAIRCASE_TRANSITIONS` implements C-CP-21 §21.2 cause-attribution branching, keyed on the conformed `ValidatorFailClass` retry-exit taxonomy. Per §21.2, the transient staircase runs for `validator.fail.class ∈ {TRANSIENT_RETRY, REFLEXION_RECOVERABLE}`; `PERMANENT_FAIL_EXIT` and `TERMINAL_FAIL_EXIT` **skip the staircase** (route directly to C11 HITL per §21.1):
   - `TRANSIENT_RETRY` / `REFLEXION_RECOVERABLE` — 1st validator fail → `STAGE_1_REFLEXION` / `STAGE_2_RETRY_WITH_BACKOFF` per §21.2 (retry with C9 backoff)
   - `TRANSIENT_RETRY` / `REFLEXION_RECOVERABLE` — 2nd validator fail → cause-attribution-conditioned branch per §21.2 (escalate model tier on `{model_misfire, provider_outage, capability_shortfall_transient}`; re-prompt on `{semantic_disagreement, contract_violation_not_yet_routed_to_Reflexion}`)
   - 3rd validator fail → C5 emits `PERMANENT_FAIL_EXIT` → routes to validator-escalation HITL placement per §17.1 (skip-staircase branch)
   - `PERMANENT_FAIL_EXIT` (any stage) → `STAGE_5_HITL_ESCALATION` — skip staircase per §21.1
   - `TERMINAL_FAIL_EXIT` (any stage) → workflow halts; HITL escalation per §21.1 (no recovery path)
   Stage 3 transitions emit `fallback.cross_family_triggered` + `fallback.cache_state_lost` per U-CP-09 + C-CP-04 §4.3.
   **(v2.4 conformance note:** the v2.1/v2.3 transition table keyed on `SCHEMA_MISMATCH`/`SANDBOX_VIOLATION`/`PERMANENT_REJECTION` — fail-*cause* tokens not in the §21.1 retry-exit taxonomy. The conformed table keys on the §21.1 retry-exit classes; specific fail-*cause* discrimination (which CP spec §21.2 routes via the 2nd-fail cause-attribution branch) is carried on `validator.fail.cause_attribution` per U-CP-47, not on `validator.fail.class`.)**
3. Stage 3 transitions emit `fallback.cross_family_triggered` + `fallback.cache_state_lost` per U-CP-09 + C-CP-04 §4.3. **[Preserved verbatim from v2.1.]**
4. `CrossTrustBoundaryState` declares exactly four values per §21.4 verbatim. **[Preserved verbatim from v2.1.]**
5. `PALETTE_RESTRICTION_TABLE` declares exactly four entries per §21.3 verbatim. **[Preserved verbatim from v2.1 in substance; v2.4 note: the `HITLResponse` value set `{APPROVE, EDIT, REJECT, RESPOND}` is unaffected — U-CP-37 `HITLResponse` is on the audit clean-list. The §21.3 palette-restriction rule restricts to `{approve, reject, respond}` (no `edit`) at cross-trust-boundary actions; the four `PALETTE_RESTRICTION_TABLE` entries (`NONE` → full; `CROSS_FAMILY_ACTIVE`/`LOCAL_TERMINAL_ACTIVE`/`UNTRUSTED_MCP_ACTIVE` → `{REJECT, RESPOND}`) are preserved. Citation note: the v2.1 acc #5 cited §21.4; the palette-restriction rule is at §21.3 — citation aligned.]**
6. Restriction composes with U-CP-37 palette completeness invariant. **[Preserved verbatim from v2.1.]**
7. `advance_staircase` deterministic given inputs; no inference path. **[Preserved verbatim from v2.1.]**

**Tests (v2.4 amendment):** `test_staircase_stage_cardinality_five` [preserved]; `test_staircase_runs_for_transient_and_reflexion_recoverable` (v2.4 — replaces `test_schema_mismatch_bypass_to_stage_5`/`test_timeout_advances_to_stage_2`/`test_rate_limit_advances_to_stage_2` which baked the divergent values); `test_permanent_fail_exit_skips_staircase` (v2.4 — replaces `test_permanent_rejection_immediate_stage_5`); `test_terminal_fail_exit_halts` (v2.4 — replaces `test_sandbox_violation_immediate_stage_5`); `test_budget_exhausted_advances_to_stage_3` [preserved]; `test_family_exhausted_advances_to_stage_4` [preserved]; `test_local_fail_advances_to_stage_5` [preserved]; `test_stage_3_emits_cache_state_lost` [preserved]; `test_cross_trust_state_cardinality_four` [preserved]; `test_palette_restriction_match_spec_21_3` (v2.4 — citation aligned §21.4 → §21.3); `test_none_full_palette` [preserved]; `test_cross_family_restricted_to_reject_respond` [preserved]; `test_local_terminal_restricted_to_reject_respond` [preserved]; `test_untrusted_mcp_restricted_to_reject_respond` [preserved]; `test_restriction_composes_with_completeness_invariant` [preserved].

**Rollback boundary:** Revert staircase + cause-branching + palette restriction. R-CP-11 validator-escalation HITL placement loses staircase progression; U-CP-39 rewriting algorithm loses palette restriction source; cross-trust-boundary state at HITL invocation degrades to full palette regardless of state. Cross-axis AS edges to U-AS-10, U-AS-29 release. **(v2.4 note: reverting de-conforms the cross-unit propagation from U-CP-47.)**

[U-CP-49 through U-CP-55 preserved verbatim from v2.3.]

### §2.9 Cluster 9 — Cross-axis composition + namespace export (C-CP-23, C-CP-24)

[U-CP-49 through U-CP-55 preserved verbatim from v2.3; U-CP-55 v2.2 body intact.]

---

## §3 Dependency graph

[Preserved verbatim from v2.3. No graph delta at v2.4 — enum/namespace renames do not change graph topology (§0.5). Aggregate DAG node count, edge count, topological sort, and acyclic invariant all unchanged.]

---

## §4 Coverage matrix

[Preserved verbatim from v2.3. No coverage delta at v2.4 — the revision conforms the vocabulary of already-covered acceptance criteria; no contract-to-unit mapping added or removed (§0.4).]

---

## §[carry-forwards]

[Preserved verbatim from v2.3: [CF-1] F2-12 ✅ CLOSED at v2.2; no v2.4 reopening. New v2.4 carries are recorded at §0.8, not here — §0.8 carries are pending-operator-decision items, distinct from the [CF-1] inter-version closure-tracking carry-forward.]

---

*End of Implementation Plan — Control Plane v2.4. Filed 2026-05-15 as a verbatim-divergence conformance revision pass absorbing the operator-ratified §4A resolution at `.harness/verbatim_audit_cp_plan.md`. Conforms the 7-unit cluster (U-CP-01, U-CP-10, U-CP-19, U-CP-22, U-CP-43, U-CP-46, U-CP-47) + 3 literally-enumerating consumers (U-CP-12, U-CP-23, U-CP-48) to the cited `Spec_Control_Plane` vocabulary. Three spec-silence items carried for operator decision per §0.8 — U-CP-08 (`FallThroughCause`), U-CP-11 (`LEASE_NAMESPACE_SCHEMA`), and U-CP-43 (`DEPLOYMENT_SURFACE` + `MCP_TRUST` gate-level floors); the U-CP-43 floors are a NEW carry surfaced at this pass, extending the §4A.7 enumerated carries. `Status: Proposed` until P6-CK clearance.*
