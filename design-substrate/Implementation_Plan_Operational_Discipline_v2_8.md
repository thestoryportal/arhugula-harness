# Implementation Plan — Operational Discipline (OD axis) — v2.8

**Status: Proposed.**

**Revision:** v2.8 — Phase 7 sub-phase 7b in-CLI revision pass. Resolves **five Class 1 defects** (U-OD-02, U-OD-08, U-OD-09, U-OD-12, U-OD-21) surfaced at OD axis-stream 7b execution-time, plus pins the F3 lifecycle-event taxonomy to OD spec C-OD-06 §6.1. v2.8 is a delta over v2.7: **only §3.1.2 U-OD-02, §3.2.5 U-OD-08, §3.3.1 U-OD-09, §3.4.2 U-OD-12, §3.5.3 U-OD-20, and §3.5.4 U-OD-21 are revised**; every other §0–§11 section is preserved verbatim from v2.7. Predecessor: v2.7 (U-OD-00 carrier-defect micro-revision).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 canonical authority chain + §4.3 back-flow routing (Class 1 fork resolution; design-phase back-flow deprecated 2026-05-15 — spec/plan fixes in-CLI per workspace discipline); `harness-od/CLAUDE.md` §5.1 (OD plan atomic-unit signature defect → Phase 6 plan revision); `implementation-planner` SKILL.md §8 revision-pass sub-mode.

**Entry authorization:** Operator ratification 2026-05-16 of the v2.8 revision pass — three forced fixes (U-OD-02 / U-OD-08 / U-OD-09 / F3-taxonomy pinning, determinate by the §1.3 authority chain) applied directly; three operator-decision points ratified: U-OD-21 carrier-growth (re-opens landed U-OD-20), U-OD-12 fix selection (implementation-planner recommendation), OD `CLAUDE.md` §1.1 F3-form correction (in-session).

---

## §0 Change-note

### §0.1 Trigger

During OD axis-stream 7b execution (2026-05-16), five units halted Class 1. All five share **one defect class** — signature-vs-acceptance-criterion / plan-vs-spec consistency — an axis neither prior OD audit covered: the verbatim audit (`verbatim_audit_od_plan.md`) checked cardinality; the materializability audit (`materializability_audit_od_plan.md`) checked type-carrier reachability; signature-vs-AC consistency was unaudited and produced five halts. The 17 OD units downstream of the five halted units are all transitively blocked. v2.8 resolves the five root defects so OD-7b can resume.

Tension records: `.harness/class_1_tension_u_od_02_cell_4_5_alternation.md`, `..._u_od_08_f3_lifecycle_event_set_divergence.md`, `..._u_od_09_tier_classification_design_gap.md`, `..._u_od_12_disjoint_set_string_collision.md`, `..._u_od_21_span_cost_record_missing_rollup_keys.md`.

### §0.2 The five defects + resolution

| # | Unit | Defect | Resolution (operator-ratified 2026-05-16) |
|---|---|---|---|
| D-1 | U-OD-02 | `PerCellBackendBinding.backend_class : BackendClass` is single-valued; `select_backend_class` returns a single `BackendClass`. But spec C-OD-02 §2.1 commits a **2-value backend-class disjunction** at cell-4 (`OTEL_ONLY` OR `DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE`) and cell-5 (`DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE` OR `OTEL_TO_VENDOR`). acc #3/#7 and the two `*_alternation_*` tests are un-materializable against the single-valued signature. | **Option A — widen the signature (forced; determinate per §1.3).** `backend_class` and the `select_backend_class` return widen to a non-empty `Set<BackendClass>` — cardinality 1 for cells 1/2/3/6/7/8, cardinality 2 for cells 4/5. Plan-internal conform-to-spec; §2.1 already commits the disjunction; no spec change. See §3.1.2. |
| D-2 | U-OD-08 | `F3LifecycleEventClass` 8-member set is **disjoint on 5 of 8 members** from spec C-OD-06 §6.1's eight event classes. The plan carries an invocation-shaped taxonomy (`CHAT_INVOCATION`/`TOOL_INVOCATION`/…); §6.1 commits the F3 capability-floor (iv) lifecycle taxonomy (`workflow.start`/`step.boundary`/…). AC #1/#3 both claim "§6.1 verbatim" — internally contradictory. | **Option A — conform plan to spec §6.1 (forced; determinate per §1.3).** `F3LifecycleEventClass` + `F3_LIFECYCLE_EVENT_MAPPINGS` + AC #1/#3 re-authored to the §6.1 eight-event table (span-placement + namespace + sampling-posture columns). Spec/ADR are senior; the plan diverged. No spec change. See §3.2.5. |
| D-3 | U-OD-09 | acc #2 asserts a "4 Required / 3 Conditional tier classification per §7.1". Spec C-OD-07 §7.1 declares **no tier classification** — the §7.1 table has columns `Attribute \| Type \| Source \| Definition`, no tier column. The `tier:` annotations are also un-materializable: `HARNESS_BREAKER_ATTRIBUTES : List<GenAiAttribute>` and `GenAiAttribute.tier : AttributeTier` (landed U-OD-04) — `AttributeTier` has no `REQUIRED`/`CONDITIONAL` members. This is the pre-identified FF-1 carry. | **Option B — strike acc #2 (forced; determinate per §1.3).** acc #2 prose, the `tier:` annotations, and the `test_required_tier_*` / `test_conditional_tier_*` tests are struck. `HARNESS_BREAKER_ATTRIBUTES` re-typed `List<GenAiAttribute>` → `List<string>` (the seven §7.1 attribute names). No spec basis exists to conform acc #2 *to* (X-AL-3 forecloses inventing one). See §3.3.1. |
| D-4 | U-OD-12 | acc #2 asserts `BASE_RATE_SAMPLED_EVENT_CLASSES ∩ ALWAYS_SAMPLED_EVENT_CLASSES == ∅`. But spec §9.2 / §10.1 split `files.operation` and `memory.operation` by the `kind` attribute (mutation → always-sampled; non-mutation → base-rate). Both bare strings are members of **both** `Set<string>` regimes. acc #2 is false at the string granularity the plan declares. | **Option B — re-scope acc #2 (implementation-planner recommendation, operator-delegated).** acc #2 re-worded: disjointness holds over event classes that are not `kind`-discriminated; `files.operation` / `memory.operation` are documented dual-regime classes whose regime is resolved by `kind` at the `sampling_decision` call site. Plan-layer AC correction; no signature change; **nothing landed re-opened** (U-OD-11 not in defect — see §0.3 rationale). See §3.4.2. |
| D-5 | U-OD-21 | `rollup_costs_by_axis(span_records : List<SpanCostRecord>, axis)` — acc #3 requires three rollup keys (family tag / `(provider, model)` / per-attempt provider). The landed `SpanCostRecord` (U-OD-20, 9 fields) carries **none** of them. `rollup_costs_by_axis` is un-materializable: no expression over `List[SpanCostRecord]` produces a non-trivial `group_key`. | **Option A — grow the carrier (operator-ratified; re-opens landed U-OD-20).** `SpanCostRecord` grows 9 → 12 fields: `provider_discriminator`, `gen_ai_provider_name`, `gen_ai_request_model` (all `string`). `rollup_costs_by_axis` projects the three keys; acc #3 becomes materializable verbatim. Cleanest read of spec C-OD-15 §15.1. See §0.3 (re-open declaration) + §3.5.3 + §3.5.4. |

### §0.3 U-OD-20 re-open declaration (D-5 consequence)

D-5's resolution re-opens **U-OD-20 — a LANDED unit** (`harness-od/src/harness_od/idempotency_join_dedup.py`). This is an explicit, operator-ratified landed-unit re-open, recorded here per the v2.7 §0.2 re-open precedent.

| Field | Value |
|---|---|
| Re-opened unit | U-OD-20 (landed 2026-05-16, L3 batch — pyright strict 0, in the 254-test green set) |
| Re-open scope | `SpanCostRecord` carrier field-set growth **only**: 9 fields → 12 fields. Three new fields appended — `provider_discriminator : string`, `gen_ai_provider_name : string`, `gen_ai_request_model : string`. No existing field changed; no function body changed; the idempotency-join / dedup-algorithm / per-attempt-cost surfaces are untouched. |
| Carrier consequence | `SpanCostRecord` is consumed by U-OD-21 (`rollup_costs_by_axis`) and U-OD-22 (per-cell dashboard binding, L6 — not yet landed). Field-set growth is **additive** — additive carrier growth does not regress existing U-OD-20 or U-OD-21 surfaces; the three new fields are new optional projections, not modifications of the 9 landed fields. U-OD-22 consumes the grown carrier when it lands. |
| Acyclicity | No edge change. `SpanCostRecord`'s three new fields are typed `string` (NOT `CrossFamilyTag` — which is declared at U-OD-21). String typing is deliberate: typing `provider_discriminator` as U-OD-21's `CrossFamilyTag` enum would create a U-OD-20 → U-OD-21 edge against the existing U-OD-21 → U-OD-20 carrier edge — a cycle (the `carrier-home-defect-pattern`). The family-tag value is carried as a string on the cost record; U-OD-21's `CrossFamilyTag` enum remains the bounded vocabulary that `rollup_costs_by_axis` validates the string against, at U-OD-21 where the enum lives. |
| Re-land discipline | U-OD-20 re-lands as a single coherent revert-boundary change (carrier growth + the four new field tests at §3.5.3); U-OD-21 then lands against the grown carrier. |

### §0.4 U-OD-12 fix selection rationale (D-4 — operator-delegated)

The operator delegated the U-OD-12 fix selection to the implementation-planner recommendation. Option A (re-key the regime sets on `(event_class, kind)`) is the cleaner *model* but forces the **landed** `sampling_decision(cell_id, event_class, base_rate)` function to grow a `kind` parameter — a signature change to the OD axis's central sampling entry point that ripples to every call site. Option B re-scopes the acceptance criterion to be honest about the string granularity (the spec's disjointness genuinely holds at `(event_class, kind)` pair granularity; the two dual-regime classes are documented, and their `kind`-discrimination is resolved at the `sampling_decision` call site, where the span emitter already carries `kind`). Option B is plan-internal, touches **nothing landed**, and yields a faithful acceptance criterion. The spec is satisfied either way; the bounded choice is selected. U-OD-11 is **not** re-opened (the U-OD-12 tension record confirms U-OD-11 is not itself in defect — its acc #3 cardinality-18 / §9.2-byte-exact criterion holds).

### §0.5 F3 lifecycle-event taxonomy pinning

The F3 lifecycle-event taxonomy appeared in **three divergent forms** across the corpus: the plan (U-OD-08, invocation-shaped — `CHAT_INVOCATION`/…), spec C-OD-06 §6.1 (the F3 capability-floor (iv) taxonomy — `workflow.start`/`step.boundary`/`fallback.triggered`/`retry.attempt`/`breaker.tripped`/`lease.acquired`/`lease.released`/`workflow.resumed`), and the OD subdirectory `harness-od/CLAUDE.md` §1.1 (a third form — `…/topology.fanout.opened/topology.fanout.closed`). Per the §1.3 authority chain, **spec C-OD-06 §6.1 is canonical**. v2.8 pins the taxonomy by (a) conforming U-OD-08 to §6.1 (D-2 above), and (b) correcting `harness-od/CLAUDE.md` §1.1 to the §6.1 taxonomy — an operator-ratified in-session edit applied alongside this plan revision (departing from the v2.7 §0.4 HARD-WALL pattern by explicit operator decision 2026-05-16). Post-v2.8, all three forms converge on §6.1.

### §0.6 Scope

Only §3.1.2 (U-OD-02), §3.2.5 (U-OD-08), §3.3.1 (U-OD-09), §3.4.2 (U-OD-12), §3.5.3 (U-OD-20), §3.5.4 (U-OD-21) are revised. No contract re-decomposed; no unit added or removed; unit count unchanged (35). No dependency-graph edge added or removed (§4.6). `harness-od/CLAUDE.md` §1.1 is corrected in-session per §0.5.

### §0.7 Sections preserved verbatim from v2.7

All of §0 (v2.7 change-note), §1, §2, §3 except the six units enumerated at §0.6, §4 except the §4.6 delta restatement below, §5–§11. The v2.7-revised §3.0 U-OD-00 and §3.7.4 U-OD-30 surfaces are unchanged. The 18 landed OD units are unchanged **except** U-OD-20's `SpanCostRecord` carrier (§0.3 re-open) and U-OD-09's pre-land revision (U-OD-09 is **not** landed — it halted at the L3 batch).

### §0.8 Coverage matrix delta

| Contract | v2.7 coverage | v2.8 coverage |
|---|---|---|
| C-OD-02 §2.1/§2.2/§2.3 | U-OD-02 (acc #3/#7 un-materializable) | U-OD-02 — acc #3/#7 materializable against the widened `Set<BackendClass>` signature |
| C-OD-06 §6.1 | U-OD-08 (member set divergent from §6.1) | U-OD-08 — `F3LifecycleEventClass` + `F3_LIFECYCLE_EVENT_MAPPINGS` byte-exact with the §6.1 eight-event table |
| C-OD-07 §7.1 | U-OD-09 (acc #2 tier split — no spec basis) | U-OD-09 — acc #1/#3/#4 cover §7.1 verbatim; acc #2 struck (no contract claim removed — the tier split was never a §7.1 commitment) |
| C-OD-10 §10.1 | U-OD-12 (acc #2 disjointness false at string granularity) | U-OD-12 — acc #2 re-scoped; disjointness criterion is honest at the declared granularity |
| C-OD-15 §15.1 | U-OD-21 (`rollup_costs_by_axis` un-materializable) | U-OD-21 — acc #3 materializable against the grown `SpanCostRecord` carrier |
| C-OD-14 §14.4 | U-OD-20 (`SpanCostRecord` 9 fields) | U-OD-20 — `SpanCostRecord` 12 fields; §14.4 idempotency-join surface unchanged |

No contract row loses a column mark; no plan-unit column loses a row mark. Coverage is complete.

### §0.9 Dependency-graph delta

**No delta.** None of the six revised units adds, removes, or re-points a `Depends on` edge. U-OD-02 (signature widening), U-OD-08 (member-set conformance), U-OD-09 (acc strike + retype), U-OD-12 (acc reword), U-OD-20 (additive carrier growth), U-OD-21 (rollup now materializable against the in-cone carrier) all preserve their v2.7 edge sets. The within-axis DAG is unchanged; the Kahn topological sort is unchanged; acyclicity holds. See §4.6.

---

## §3.1.2 U-OD-02 — Declare per-cell backend class + candidate witness columns [REVISED — v2.8]

[v2.5-conformed unit (preserved verbatim through v2.7). v2.8 delta (D-1): `PerCellBackendBinding.backend_class` and the `select_backend_class` return widen from a single `BackendClass` to a non-empty `Set<BackendClass>`; acc #1 unchanged (the 7-value enum is unchanged), acc #3 + acc #7 conformed to the set-valued signature. All other surfaces — `BackendClass` enum, `CandidateWitness`, `PER_CELL_BACKEND_BINDINGS`, `enumerate_candidates`, acc #2/#4/#5/#6/#8, Persona linkage, Files affected — preserved verbatim from v2.5.]

**Implements:** [C-OD-02 §2.1, §2.2, §2.3]

**Depends on:** [U-OD-01]

**Inputs:** OD spec v1.2 §2.1 per-cell backend class (eight cells; **seven distinct classes** — cell-4 AND cell-5 each admit a 2-value class disjunction at the design-time-flexible rows); §2.2 per-cell candidate witness columns; §2.3 cell-class commitment invariant.

**Files affected:** Per-cell backend class + candidate witness column declaration (logical name: `od-per-cell-backend-class`).

**Persona linkage.** Persona §9 (deployment-surface candidate enumeration); §10.4 (compliance-readiness backend selection at multi-tenant cells).

**Signatures (v2.8 — `backend_class` + `select_backend_class` return widened to `Set<BackendClass>` per D-1):**

```
// §2.1: "Eight cells; seven distinct classes" — preserved verbatim from v2.5.
enum BackendClass {
  OTEL_ONLY,                                       // §2.1 — cells 1, 4
  DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE,          // §2.1 — cells 2, 4
  DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE,           // §2.1 — cell 5
  CLOUD_NATIVE_LLM_OBS_PLATFORM,                   // §2.1 — cells 3, 6
  OTEL_TO_VENDOR,                                  // §2.1 — cell 5
  SELF_HOSTED_MULTI_TENANT_LLM_OBS_PLATFORM,       // §2.1 — cell 7
  VENDOR_MANAGED_MULTI_TENANT_LLM_OBS_OR_CLOUD_NATIVE_MANAGED_AGENT_RUNTIME  // §2.1 — cell 8
}                                                  // exactly 7 values per §2.1

record CandidateWitness {
  candidate_name   : string
  vendor_class     : string
  deployment_form  : string
}

// v2.8 (D-1): backend_class widened single BackendClass -> non-empty
// Set<BackendClass>. §2.1 commits a 2-value class disjunction at cell-4 and
// cell-5; a single-valued field cannot represent it. Cardinality of the set is
// 1 for the six committed cells (1/2/3/6/7/8) and 2 for the two
// design-time-flexible cells (4/5).
record PerCellBackendBinding {
  cell_id         : CellID
  backend_class   : Set<BackendClass>               // v2.8 — non-empty; |·| ∈ {1, 2}
  candidates      : List<CandidateWitness>
}

const PER_CELL_BACKEND_BINDINGS : Map<CellID, PerCellBackendBinding>   // exactly 8 entries

// v2.8 (D-1): return widened single BackendClass -> Set<BackendClass>.
fn select_backend_class(c : CellID) -> Set<BackendClass>               // non-empty; Err at EXCLUDED cell
fn enumerate_candidates(c : CellID) -> List<CandidateWitness>
```

**Acceptance criteria (v2.8 — acc #3 + #7 conformed to the set-valued signature; #1/#2/#4/#5/#6/#8 preserved verbatim from v2.5):**

1. `BackendClass` enumerates exactly **7** distinct values per §2.1 verbatim: `OTEL_ONLY`, `DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE`, `DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE`, `CLOUD_NATIVE_LLM_OBS_PLATFORM`, `OTEL_TO_VENDOR`, `SELF_HOSTED_MULTI_TENANT_LLM_OBS_PLATFORM`, `VENDOR_MANAGED_MULTI_TENANT_LLM_OBS_OR_CLOUD_NATIVE_MANAGED_AGENT_RUNTIME`.
2. `PER_CELL_BACKEND_BINDINGS` declares exactly 8 entries — one `PerCellBackendBinding` per ACTIVE cell.
3. **(v2.8 D-1.)** Each cell's `backend_class` is a non-empty `Set<BackendClass>` matching the §2.1 row verbatim:
   - cell-1 (solo-developer × local-development) → `{OTEL_ONLY}`
   - cell-2 (solo-developer × self-hosted-server) → `{DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE}`
   - cell-3 (solo-developer × managed-cloud) → `{CLOUD_NATIVE_LLM_OBS_PLATFORM}`
   - cell-4 (team-binding × local-development) → `{OTEL_ONLY, DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE}` (the §2.1 design-time-flexible disjunction row — "OTel-only OR Dedicated LLM-obs platform (single-node)")
   - cell-5 (team-binding × self-hosted-server) → `{DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE, OTEL_TO_VENDOR}` (the §2.1 design-time-flexible disjunction row — "Dedicated LLM-obs platform (multi-node) OR OTel-to-vendor")
   - cell-6 (team-binding × managed-cloud) → `{CLOUD_NATIVE_LLM_OBS_PLATFORM}`
   - cell-7 (multi-tenant-compliance × self-hosted-server) → `{SELF_HOSTED_MULTI_TENANT_LLM_OBS_PLATFORM}`
   - cell-8 (multi-tenant-compliance × managed-cloud) → `{VENDOR_MANAGED_MULTI_TENANT_LLM_OBS_OR_CLOUD_NATIVE_MANAGED_AGENT_RUNTIME}`
4. Per-cell `candidates` carries the candidate list per ADR-D6 v1.1 §1.1 verbatim (Langfuse / Arize Phoenix / Helicone / vendor LLM-obs / Datadog / Sentry / Bedrock AgentCore / Vertex Agent Engine / LangSmith Enterprise / Langfuse Cloud Enterprise — candidates by cell).
5. `select_backend_class(EXCLUDED_CELL)` returns `Err` per U-OD-01 `reject_excluded_cell` composition; backend class is undefined at the EXCLUDED cell.
6. `enumerate_candidates` returns the candidate list per cell; candidates are witness columns — operators MAY select within the list at deployment-binding time.
7. **(v2.8 D-1.)** Cell-class commitment invariant per §2.3: each ACTIVE cell carries a **non-empty** `backend_class` set — a singleton for the six committed cells (1/2/3/6/7/8) and a 2-element set for cell-4 and cell-5 (the rare/design-time-flexible-configuration witnesses per §2.1; both alternants are class-committed shapes at the respective cell). No cell carries an empty set; no cell carries a set of cardinality > 2.
8. Candidate witnesses are not exhaustive enumeration — they constitute the witness column per ADR-D6 v1.1 §1.1; deployment-binding-time operator binding within the witness column is permitted.

**Tests (v2.8 — `test_cell_4_*` / `test_cell_5_*` conformed to set-valued shape; cardinality tests added):** `test_backend_class_cardinality_seven`, `test_per_cell_bindings_cardinality_eight`, `test_cell_1_backend_class_singleton_otel_only`, `test_cell_2_backend_class_singleton_dedicated_single_node`, `test_cell_3_backend_class_singleton_cloud_native`, `test_cell_4_alternation_otel_or_dedicated_single_node` (asserts the 2-element set `{OTEL_ONLY, DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE}`), `test_cell_5_alternation_dedicated_multi_node_or_otel_to_vendor` (asserts the 2-element set `{DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE, OTEL_TO_VENDOR}`), `test_cell_6_backend_class_singleton_cloud_native`, `test_cell_7_backend_class_singleton_self_hosted_multi_tenant`, `test_cell_8_backend_class_singleton_vendor_managed_multi_tenant_or_managed_agent_runtime`, `test_backend_class_set_nonempty_all_cells`, `test_backend_class_set_cardinality_one_or_two_all_cells`, `test_select_backend_class_excluded_cell_returns_err`, `test_enumerate_candidates_per_cell_nonempty`.

**Rollback boundary:** Revert per-cell backend class + candidate witness columns. R-OD-01 satisfaction loses per-cell backend selection substrate; U-OD-28 per-cell collector placement matrix loses the candidate-bound backing-contract references; U-OD-22 per-cell cost-attribution dashboard binding loses backend class enum for cell-class-row routing. [v2.8 revert appendix:] Reverting v2.8 restores the single-valued `backend_class : BackendClass` signature — i.e. the D-1 un-materializable cell-4/cell-5 disjunction defect; the revert MUST NOT be performed absent a re-disposition.

---

## §3.2.5 U-OD-08 — Map F3 lifecycle events to span events [REVISED — v2.8]

[v2.1-base unit (preserved verbatim through v2.7). v2.8 delta (D-2): `F3LifecycleEventClass` + `F3_LIFECYCLE_EVENT_MAPPINGS` + acc #1/#2/#3 re-authored to the spec C-OD-06 §6.1 eight-event lifecycle table — the plan's invocation-shaped taxonomy is replaced by the §6.1 F3 capability-floor (iv) taxonomy. `LifecycleEventMapping` is grown to carry the §6.1 four-column table faithfully — `span_event_name` is renamed `event_class_name` (the §6.1 col-1 event-class string), and two fields are added (`span_placement_form` §6.1 col 2, `sampling_posture` §6.1 col 4); `attribute_namespaces` is retained. acc #4/#5/#6/#7/#8, the `F2_12_DEFERRAL_NOTE_AT_RETRY_ATTEMPT` constant, `Depends on`, Files affected, rollback boundary preserved verbatim from v2.1.]

**Implements:** [C-OD-06 §6.1, §6.2, §6.3]

**Depends on:** [U-OD-04, U-OD-05, U-OD-06, U-OD-07, U-CP-54 (cross-axis: CP — C-CP-24 §24.1.B F3 lifecycle event attributes)]

**Cross-axis dependency resolution.** CP plan U-CP-54 substrate seam exports manifest declares F3 lifecycle event attributes via C-CP-24 §24.1.B. Per OD-S4-3.A, the cross-axis edge is `Depends on: [U-CP-54 (cross-axis: CP — C-CP-24 §24.1.B)]`.

**Inputs:** OD spec v1.2 §6.1 F3 capability-floor lifecycle event mapping table (**eight event classes** — `workflow.start`, `step.boundary`, `fallback.triggered`, `retry.attempt`, `breaker.tripped`, `lease.acquired`, `lease.released`, `workflow.resumed` — each mapped to a span-placement form, attribute namespace, and sampling posture); §6.2 additive composition; §6.3 F2-12 deferral acknowledgement at `retry.attempt`.

**Files affected:** F3 lifecycle event-to-span-event mapping declaration (logical name: `od-f3-lifecycle-event-mapping`).

**Signatures (v2.8 — `F3LifecycleEventClass` + `F3_LIFECYCLE_EVENT_MAPPINGS` conformed to §6.1; `LifecycleEventMapping` grown to carry the §6.1 columns):**

```
// §6.1 verbatim — the F3 v1.1 capability-floor (iv) "observable lifecycle
// (eight event classes)" taxonomy. v2.8 (D-2): replaces the v2.1
// invocation-shaped taxonomy, which diverged 5/8 from §6.1.
enum F3LifecycleEventClass {
  WORKFLOW_START,                              // §6.1 — "workflow.start"
  STEP_BOUNDARY,                               // §6.1 — "step.boundary"
  FALLBACK_TRIGGERED,                          // §6.1 — "fallback.triggered"
  RETRY_ATTEMPT,                               // §6.1 — "retry.attempt"
  BREAKER_TRIPPED,                             // §6.1 — "breaker.tripped"
  LEASE_ACQUIRED,                              // §6.1 — "lease.acquired"
  LEASE_RELEASED,                              // §6.1 — "lease.released"
  WORKFLOW_RESUMED                             // §6.1 — "workflow.resumed"
}                                              // exactly 8 F3 event classes per §6.1

// v2.8 (D-2): grown from {f3_event_class, span_event_name,
// attribute_namespaces} to carry the §6.1 four-column table faithfully —
// span-placement form + attribute namespace + sampling posture.
record LifecycleEventMapping {
  f3_event_class       : F3LifecycleEventClass
  event_class_name     : string                  // §6.1 col 1 — e.g. "workflow.start"
  span_placement_form  : string                  // §6.1 col 2 — e.g. "span attribute on root span"
  attribute_namespaces : Set<string>             // §6.1 col 3 — the namespace(s); ∅ for step.boundary
  sampling_posture     : string                  // §6.1 col 4 — e.g. "always-sampled per C-OD-09"
}

const F3_LIFECYCLE_EVENT_MAPPINGS : Map<F3LifecycleEventClass, LifecycleEventMapping>   // exactly 8 entries

// §6.3 F2-12 deferral acknowledgement (non-contract-bearing) — preserved verbatim from v2.1.
const F2_12_DEFERRAL_NOTE_AT_RETRY_ATTEMPT : string =
  "retry.attempt sibling-span discipline at D6 ingestion is deferred per F2-12 carry-forward; v1 commits event + new sibling span per C-CP-03 §3.5; revisable at D6 v1.2"
```

**Acceptance criteria (v2.8 — acc #1/#2/#3 conformed to §6.1; #4–#8 preserved verbatim from v2.1):**

1. **(v2.8 D-2.)** `F3LifecycleEventClass` enumerates exactly **8** values per §6.1 verbatim: `WORKFLOW_START`, `STEP_BOUNDARY`, `FALLBACK_TRIGGERED`, `RETRY_ATTEMPT`, `BREAKER_TRIPPED`, `LEASE_ACQUIRED`, `LEASE_RELEASED`, `WORKFLOW_RESUMED` — the F3 capability-floor (iv) lifecycle taxonomy.
2. **(v2.8 D-2.)** `F3_LIFECYCLE_EVENT_MAPPINGS` declares exactly 8 entries; each `LifecycleEventMapping` carries the §6.1 row's event-class name, span-placement form, attribute namespace(s), and sampling posture.
3. **(v2.8 D-2.)** Per-class mapping, byte-exact with the §6.1 table:
   - `WORKFLOW_START` → "workflow.start"; span attribute on root span; `{engine.*}` (per C-CP-09 §9.1); per root span sampling (inherits).
   - `STEP_BOUNDARY` → "step.boundary"; span event on parent; `∅` (no dedicated namespace; inherits parent attribute set); per parent sampling.
   - `FALLBACK_TRIGGERED` → "fallback.triggered"; span event on parent + new sibling fallback span; `{fallback.*}` (per C-CP-03 §3.5); always-sampled per C-OD-09.
   - `RETRY_ATTEMPT` → "retry.attempt"; span event on parent + new sibling retry span; `{retry.*}` (per C-CP-03 §3.5); base-rate at 1st attempt, always-sampled at 2nd onward per C-CP-03 §3.5.
   - `BREAKER_TRIPPED` → "breaker.tripped"; span event on parent; `{harness.breaker.*}` (per C-OD-07 §7.1); always-sampled per C-OD-09.
   - `LEASE_ACQUIRED` → "lease.acquired"; span event on parent; `{lease.*}` (per C-CP-05 §5.3); base-rate per C-CP-05 §5.4.
   - `LEASE_RELEASED` → "lease.released"; span event on parent; `{lease.*}` (per C-CP-05 §5.3); base-rate per C-CP-05 §5.4.
   - `WORKFLOW_RESUMED` → "workflow.resumed"; span attribute on root span (post-resumption); `{engine.*}` (per C-CP-09 §9.1); always-sampled per C-CP-05 §5.4.
4. Additive composition invariant per §6.2: lifecycle event attributes compose additively with base-layer attributes; lifecycle event emission does NOT replace any base-layer attribute.
5. F2-12 deferral note at `retry.attempt` per §6.3 is **non-contract-bearing** — it acknowledges that the sibling-span discipline at D6 ingestion is deferred to D6 v1.2 per F2-12 carry-forward. v1 commitment per C-CP-03 §3.5 stands: event + new sibling span.
6. `F2_12_DEFERRAL_NOTE_AT_RETRY_ATTEMPT` carries the §6.3 acknowledgement verbatim; this constant is a forward-compatibility note, not a contract-bearing F2-12 ACTIVE engagement (which is contract-bearing exclusively at U-OD-20 §14.5).
7. Cross-axis edge per OD-S4-3.A: edge target = U-CP-54; contract anchor = C-CP-24 §24.1.B (F3 lifecycle event attributes).
8. F3 capability-floor anchor: this mapping is the F3 v1.1 capability-floor (iv) lifecycle event mapping composition at OD.

**Tests (v2.8 — per-class mapping tests conformed to the §6.1 eight-event table):** `test_f3_lifecycle_event_class_cardinality_eight`, `test_f3_lifecycle_event_class_members_byte_exact_per_§6_1`, `test_f3_lifecycle_event_mappings_cardinality_eight`, `test_workflow_start_mapping`, `test_step_boundary_mapping_no_namespace`, `test_fallback_triggered_mapping`, `test_retry_attempt_mapping`, `test_breaker_tripped_mapping`, `test_lease_acquired_mapping`, `test_lease_released_mapping`, `test_workflow_resumed_mapping`, `test_lifecycle_event_mapping_carries_span_placement_form`, `test_lifecycle_event_mapping_carries_sampling_posture`, `test_additive_composition_no_base_layer_replacement`, `test_f2_12_deferral_note_byte_exact`, `test_f2_12_deferral_note_non_contract_bearing`, `test_cross_axis_edge_to_u_cp_54_section_24_1_b_declared`.

**Rollback boundary:** Revert F3 lifecycle event-to-span-event mapping. R-OD-02 satisfaction loses lifecycle event ingestion substrate; downstream U-OD-10 namespace collision discipline loses event composition reference; downstream U-OD-11 always-sampled set composition loses lifecycle event class enumeration. [v2.8 revert appendix:] Reverting v2.8 restores the v2.1 invocation-shaped taxonomy — i.e. the D-2 §6.1-divergence defect; the revert MUST NOT be performed absent a re-disposition.

---

## §3.3.1 U-OD-09 — Declare `harness.breaker.*` 7-attribute canonical schema (substrate-anchored-outside-CP) [REVISED — v2.8]

[v2.5-conformed unit + v2.6 M-1 delta (acc #10 + `[U-OD-04]` edge). v2.8 delta (D-3): the FF-1-carried acc #2 (Required/Conditional tier classification) is **STRUCK** — OD spec C-OD-07 §7.1 declares no tier classification, and the `tier:` values are un-materializable against the landed U-OD-04 `AttributeTier` enum. `HARNESS_BREAKER_ATTRIBUTES` re-typed `List<GenAiAttribute>` → `List<string>`; the `tier:` annotations and the `test_required_tier_*` / `test_conditional_tier_*` tests are struck; acc #9 re-worded to enforce presence of the four non-optional `HarnessBreakerEvent` attributes (signature-faithful — `HarnessBreakerEvent` is preserved verbatim with three `Option`-typed fields). All other surfaces — `BreakerScope`, `BreakerState`, `HarnessBreakerEvent`, `emit_breaker_trip_span_event`, acc #1/#3/#4/#5/#6/#7/#8/#10, the `[U-OD-04]` edge, substrate-anchored rationale, Persona linkage — preserved verbatim from the v2.5/v2.6 body.]

**Implements:** [C-OD-07 §7.1, §7.2, §7.3]

**Depends on:** [U-OD-07, U-OD-04] — `[U-OD-04]` retained (v2.6 M-1): `emit_breaker_trip_span_event`'s `parent_span_ref : SpanRef` and `Result<EventEmission, …>` resolve to the U-OD-04 OTel-handle alias family. (v2.8 note: `HARNESS_BREAKER_ATTRIBUTES` no longer consumes `GenAiAttribute` from U-OD-04 — see Signatures — but the `[U-OD-04]` edge is independently justified by `SpanRef` / `EventEmission` and is preserved.)

**Inputs:** OD spec v1.2 §7.1 seven-attribute canonical schema (`harness.breaker.scope ∈ {per_model, per_provider}`; columns `Attribute | Type | Source | Definition` — **no tier classification**); §7.2 quality-of-emission invariants (all-seven-required-on-emission); §7.3 C9↔C10 subscription contract reference.

**Files affected:** `harness.breaker.*` substrate-anchored canonical schema declaration (logical name: `od-harness-breaker-canonical-schema`).

**Substrate-anchored-outside-CP rationale.** [Preserved verbatim from v2.5 §3.3.1.] Per F-CP-01 Stage 3b alignment, the `harness.breaker.*` namespace is **substrate-anchored at the OD axis** rather than the CP axis. The CP-side `breaker.*` set is replaced under F-CP-01 alignment by this OD-canonical 7-attribute schema. The OD plan exports `harness.breaker.*` to the CP plan as a **CP-consuming** seam (per OD plan U-OD-09 → CP plan U-CP-54 §24.1.C cross-axis edge). This is the **OD → CP exporter** direction.

**Persona linkage.** Persona §4 (99.9% SLO; breaker-trip event is reliability-critical signal); §10.2 (compliance-readiness — breaker-trip events always-sampled at multi-tenant cells for tamper-evident audit ledger composition).

**Signatures (v2.8 — `HARNESS_BREAKER_ATTRIBUTES` re-typed to `List<string>`; tier annotations struck per D-3; all else preserved verbatim from v2.5/v2.6):**

```
// v2.8 (D-3): re-typed List<GenAiAttribute> -> List<string>. The seven §7.1
// attribute names. The v2.1/v2.5 `tier:` annotations are STRUCK — OD spec §7.1
// declares no tier classification; the §7.1 table columns are
// Attribute | Type | Source | Definition, with no tier column. Per CLAUDE.md
// I-2 / X-AL-3 (no silent H_T design extension), there is no spec basis to
// conform a tier split to, and no AttributeTier member (landed U-OD-04) names
// REQUIRED / CONDITIONAL.
const HARNESS_BREAKER_ATTRIBUTES : List<string> = [
  "harness.breaker.scope",
  "harness.breaker.from_state",
  "harness.breaker.to_state",
  "harness.breaker.trigger_count",
  "harness.breaker.permanent_fail_repeats",
  "harness.breaker.tool_id",
  "harness.breaker.model_version"
]                                                  // exactly 7 attribute names per §7.1

// §7.1 verbatim — harness.breaker.scope ∈ {per_model, per_provider}
enum BreakerScope {
  PER_MODEL,
  PER_PROVIDER
}                                                  // exactly 2 values per §7.1

enum BreakerState {
  CLOSED,
  HALF_OPEN,
  OPEN
}                                                  // §7.1 from_state/to_state ∈ {closed, open, half_open}

record HarnessBreakerEvent {
  scope                    : BreakerScope
  from_state               : BreakerState
  to_state                 : BreakerState
  trigger_count            : int
  permanent_fail_repeats   : Option<int>
  tool_id                  : Option<string>        // when scope correlates with a specific tool per §7.1
  model_version            : Option<string>
}

fn emit_breaker_trip_span_event(
  parent_span_ref : SpanRef,
  event           : HarnessBreakerEvent
) -> Result<EventEmission, BreakerEmissionError>
```

**Acceptance criteria (v2.8 — acc #2 STRUCK per D-3; acc #9 re-worded to §7.2; #1/#3–#8/#10 preserved verbatim from v2.5/v2.6):**

1. `HARNESS_BREAKER_ATTRIBUTES` declares exactly **7** attribute names per §7.1 verbatim: `harness.breaker.scope`, `harness.breaker.from_state`, `harness.breaker.to_state`, `harness.breaker.trigger_count`, `harness.breaker.permanent_fail_repeats`, `harness.breaker.tool_id`, `harness.breaker.model_version`.
2. **[STRUCK — v2.8 D-3.]** *(The v2.5/v2.6 acc #2 asserted a "4 Required / 3 Conditional tier classification per §7.1". OD spec C-OD-07 §7.1 declares no tier classification — the §7.1 table has no tier column. The criterion had no spec basis (the pre-identified FF-1) and was un-materializable against the landed U-OD-04 `AttributeTier` enum. Struck per `CLAUDE.md` I-2 / X-AL-3: there is no contract claim to conform it to, and inventing a `BreakerTier` carrier would be a silent H_T design extension. The acceptance-criterion number 2 is retired in place; downstream criteria keep their numbers.)*
3. `BreakerScope` enumerates exactly **2** values per §7.1 verbatim: `per_model`, `per_provider`.
4. `BreakerState` enumerates exactly 3 values (CLOSED / HALF_OPEN / OPEN) per §7.1 `from_state` / `to_state` ∈ `{closed, open, half_open}`.
5. Quality-of-emission invariants per §7.2: breaker-trip events are always-sampled at all cells (composes with U-OD-11 always-sampled set); attributes are cardinality-safe (no payload content; per-attribute cardinality bounded by `BreakerScope` enum × `BreakerState` enum × bounded integers).
6. C9↔C10 subscription contract per §7.3: breaker-trip events emitted at C9 reliability primitive ownership are subscribed by C10 action-safety gate as gating signal; this is a runtime cross-voice subscription, not a compile-time link.
7. Substrate-anchored-outside-CP per F-CP-01 Stage 3b: the OD axis owns the canonical schema; the CP plan's `breaker.*` set is replaced by this OD-canonical 7-attribute schema at C-CP-24 §24.1.C ingestion.
8. Cross-axis export per OD-S4-3.A: this unit is an **OD → CP exporter**; edge target = U-CP-54 (CP plan substrate seam exports manifest); contract anchor = C-CP-24 §24.1.C.
9. **(v2.8 D-3 — re-worded.)** `emit_breaker_trip_span_event` emits the event at the parent span and returns `Err(BreakerEmissionError)` if any of the **four non-optional** `HarnessBreakerEvent` attributes — `scope`, `from_state`, `to_state`, `trigger_count` — is missing. The three optional attributes (`permanent_fail_repeats`, `tool_id`, `model_version`, typed `Option<…>` in `HarnessBreakerEvent`) are populated when applicable per the §7.1 Definition-column conditional language (e.g. `tool_id` "when scope is per-model and failures correlate with a specific tool"). *Spec-internal nuance: §7.2 states "all seven required on emission" while §7.1's Definition column gives `tool_id` / `model_version` / `permanent_fail_repeats` a conditional reading; the `HarnessBreakerEvent` `Option`-typing (preserved verbatim from v2.1) operationalizes the §7.1 conditional reading, and acc #9 enforces presence at the signature-enforceable granularity — the four non-optional fields.*
10. **(v2.6 M-1.)** `emit_breaker_trip_span_event`'s `parent_span_ref : SpanRef` and `Result<EventEmission, …>` resolve to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared); no `Span*` type is materialized inside U-OD-09.

**Tests (v2.8 — `test_required_tier_*` / `test_conditional_tier_*` STRUCK per D-3; `test_harness_breaker_attributes_*` conformed to the `List<string>` shape):** `test_harness_breaker_attributes_cardinality_seven`, `test_harness_breaker_attribute_names_byte_exact`, `test_harness_breaker_attributes_typed_list_of_string`, `test_breaker_scope_cardinality_two`, `test_breaker_scope_names_per_model_per_provider`, `test_breaker_state_cardinality_three`, `test_emit_breaker_trip_with_all_seven_attrs_accept`, `test_emit_breaker_trip_missing_required_attr_reject` (asserts `Err` when any of `scope` / `from_state` / `to_state` / `trigger_count` is missing), `test_breaker_event_always_sampled_at_all_cells`, `test_breaker_attributes_cardinality_safe`, `test_cross_axis_export_to_u_cp_54_section_24_1_c_declared`, `test_substrate_anchored_outside_cp_per_f_cp_01_stage_3b`, `test_span_ref_event_emission_resolve_to_u_od_04_carrier`. *(STRUCK: `test_required_tier_attributes_count_four`, `test_conditional_tier_attributes_count_three`.)*

**Rollback boundary:** Revert `harness.breaker.*` substrate-anchored canonical schema. R-OD-02 + R-OD-03 satisfaction loses breaker-trip event schema; F-CP-01 Stage 3b alignment loses OD-axis substrate; CP plan U-CP-54 §24.1.C ingestion loses `harness.breaker.*` substrate-anchored-outside-CP reference; C9↔C10 subscription contract loses event substrate. [v2.8 revert appendix:] Reverting v2.8 restores the FF-1-carried acc #2 tier split and the `List<GenAiAttribute>` typing — i.e. the D-3 no-spec-basis defect; the revert MUST NOT be performed absent a re-disposition.

---

## §3.4.2 U-OD-12 — Declare 13-entry base-rate-sampled set + per-cell tuning envelope [REVISED — v2.8]

[v2.5-conformed unit (preserved verbatim through v2.7). v2.8 delta (D-4): acc #2 (cross-set disjointness) is re-scoped — the spec §9.2 / §10.1 regime assignment splits `files.operation` and `memory.operation` by the `kind` attribute, so at the declared `Set<string>` granularity both bare strings are members of both regimes. acc #2 is re-worded to a criterion honest at that granularity. **No signature change; nothing landed re-opened** (U-OD-11 is not in defect — its acc #3 holds). All other surfaces — `BASE_RATE_SAMPLED_EVENT_CLASSES`, `PerCellBaseRateEnvelope`, `PER_CELL_BASE_RATE_ENVELOPE`, `TailKeepRule`, `TAIL_KEEP_RULES`, acc #1/#3/#4/#5/#6, `Depends on`, rollback boundary — preserved verbatim from v2.5.]

**Implements:** [C-OD-10 §10.1, §10.2, §10.3]

**Depends on:** [U-OD-01, U-OD-11]

**Inputs:** OD spec v1.2 §10.1 base-rate-sampled set (**13 entries** — the §10.1 table); §10.2 tail-keep-on-classification; §10.3 per-cell base-rate tuning envelope; §9.2 always-sampled exception set (the complement regime — for the dual-regime `kind`-discriminated classes, see acc #2).

**Files affected:** Base-rate set + per-cell tuning envelope (logical name: `od-base-rate-set-and-envelope`).

**Signatures (preserved verbatim from v2.5 — no signature change at v2.8):**

```
// §10.1 verbatim — base-rate-sampled set. Member set conformed to the
// §10.1 table (13 rows).
const BASE_RATE_SAMPLED_EVENT_CLASSES : Set<string> = {
  "chat",                                          // §10.1 — gen_ai.operation.name=chat
  "execute_tool",
  "sandbox.enter",
  "sandbox.exit",
  "tool.call",                                     // §10.1 — non-MCP tool calls only
  "retrieval",                                     // §10.1 — gen_ai.operation.name=retrieval
  "cache.events",                                  // §10.1 row "cache events (cache hit / cache miss / cache creation)"
  "embeddings",
  "text_completion",
  "files.operation",                               // §10.1 — kind ∈ {list, metadata, reference} (non-mutation)
  "memory.operation",                              // §10.1 — kind ∈ {read, list} (non-mutation)
  "lease.acquired_released",                       // §10.1 row "lease.acquired / lease.released"
  "retry.attempt.first"                            // §10.1 row "retry.attempt at 1st attempt"
}                                                  // exactly 13 entries per §10.1

record PerCellBaseRateEnvelope {
  cell_id           : CellID
  default_rate      : float
  min_rate          : float
  max_rate          : float
}

const PER_CELL_BASE_RATE_ENVELOPE : Map<CellID, PerCellBaseRateEnvelope>   // exactly 8 entries

record TailKeepRule {
  classification_attribute : string
  keep_decision            : "ALWAYS_KEEP"
}

const TAIL_KEEP_RULES : List<TailKeepRule>
```

**Acceptance criteria (v2.8 — acc #2 re-scoped per D-4; #1/#3–#6 preserved verbatim from v2.5):**

1. `BASE_RATE_SAMPLED_EVENT_CLASSES` has cardinality **13** per §10.1 verbatim, with member set conformed to the §10.1 table: `chat` (`gen_ai.operation.name=chat`), `execute_tool`, `sandbox.enter`, `sandbox.exit`, `tool.call` (non-MCP tool calls only), `retrieval` (`gen_ai.operation.name=retrieval`), cache events (cache hit / cache miss / cache creation), `embeddings`, `text_completion`, `files.operation` (`kind ∈ {list, metadata, reference}` — non-mutation), `memory.operation` (`kind ∈ {read, list}` — non-mutation), `lease.acquired` / `lease.released`, `retry.attempt` at 1st attempt.
2. **(v2.8 D-4 — re-scoped.)** Regime assignment is disjoint over **non-`kind`-discriminated** event classes: for every event class other than `files.operation` and `memory.operation`, membership is in exactly one of `BASE_RATE_SAMPLED_EVENT_CLASSES` / `ALWAYS_SAMPLED_EVENT_CLASSES`. `files.operation` and `memory.operation` are **dual-regime classes** — the spec §9.2 / §10.1 tables place them in *both* regimes, discriminated by the `kind` attribute (mutation `kind ∈ {upload, delete}` / `{write, update, delete}` → always-sampled per §9.2; non-mutation `kind ∈ {list, metadata, reference}` / `{read, list}` → base-rate per §10.1). For these two classes the regime is resolved by `kind` at the `sampling_decision` call site, where the span emitter carries `kind`. The spec's disjointness is a well-defined function over `(event_class, kind)` pairs (no pair is in both regimes); the bare-string set model declares the two dual-regime classes in both `Set<string>` constants by design, and acc #2 asserts the disjointness only where the `kind` discriminator does not apply.
3. `PER_CELL_BASE_RATE_ENVELOPE` has cardinality **8** — one per ACTIVE cell. Per §10.3 envelope:
   - solo-developer × * → default 1.0 (everything sampled at design-time)
   - team-binding × * → default 0.05–0.5 (typical envelope)
   - multi-tenant-compliance × * → default 0.1–0.5 (compliance + cost balance)
4. `min_rate <= default_rate <= max_rate` per cell — envelope invariant.
5. Per §10.3 envelope tightening invariant across bridging-arc transitions (composition with U-OD-32 §22.3 sampling-discipline tightening dimension): `target_cell.max_rate <= source_cell.max_rate` along persona-tier axis at fixed deployment surface.
6. `TAIL_KEEP_RULES` declares the tail-keep-on-classification post-classification keep decisions per §10.2: failed traces (validator.fail.permanent / sandbox violations / breaker trips) ALWAYS_KEEP at tail-based-prod cells regardless of base-rate.

**Tests (v2.8 — `test_base_rate_and_always_sampled_disjoint` re-scoped per D-4):** `test_base_rate_set_cardinality_thirteen`, `test_base_rate_event_members_byte_exact_per_§10_1`, `test_regime_disjoint_over_non_kind_discriminated_classes`, `test_files_operation_dual_regime_routed_by_kind`, `test_memory_operation_dual_regime_routed_by_kind`, `test_per_cell_envelope_cardinality_eight`, `test_envelope_invariant_min_default_max`, `test_solo_cells_default_rate_one_point_zero`, `test_team_cells_default_rate_in_envelope`, `test_multi_tenant_cells_default_rate_in_envelope`, `test_envelope_tightening_across_bridging_arc`, `test_tail_keep_rules_apply_post_classification`. *(The v2.5 `test_base_rate_and_always_sampled_disjoint` — which asserted unconditional bare-string disjointness — is replaced by `test_regime_disjoint_over_non_kind_discriminated_classes` plus the two dual-regime tests.)*

**Rollback boundary:** Revert base-rate set + per-cell envelope. R-OD-03 satisfaction loses base-rate discipline; downstream U-OD-22 alerting threshold scaling loses base-rate-scaling factor (`1.0 / base_rate`); bridging-arc transition verification loses base-rate-envelope-tightening substrate. [v2.8 revert appendix:] Reverting v2.8 restores the v2.5 unconditional-disjointness acc #2 — i.e. the D-4 false-at-string-granularity defect; the revert MUST NOT be performed absent a re-disposition.

---

## §3.5.3 U-OD-20 — Compose idempotency-key join + dedup algorithm + per-attempt cost-attribution + F2-12 ✅ CLOSED affected-contract notation [REVISED — v2.8, RE-OPENED]

[v2.2-amended unit (F2-12 cascade Step 6b) + v2.4 Form A acc #11 amendment + v2.6 M-1 `[U-OD-04]` edge; **LANDED** 2026-05-16. v2.8 delta (D-5): `SpanCostRecord` carrier grows 9 fields → 12 fields — three new `string` fields appended (`provider_discriminator`, `gen_ai_provider_name`, `gen_ai_request_model`) so the rollup keys U-OD-21 acc #3 requires are projectable from the carrier. acc #1 cardinality 9 → 12. **This is a re-open of a landed unit** — see §0.3. Re-open scope is the carrier field-set growth ONLY: the idempotency-join, dedup-algorithm, cause_attribution-invariance, per-attempt-cost-roll-up, and F2-12-closed-notation surfaces — `attach_idempotency_key_to_cost_record`, `dedupe_on_replay`, `cause_attribution_invariance_check`, `per_attempt_cost_attribution_roll_up`, `F2_12_*` records/consts, acc #2–#15, `Depends on`, rollback boundary — are preserved verbatim from the v2.2/v2.4/v2.6 body.]

**Implements:** [C-OD-14 §14.4 idempotency-key join + §14.5 (CLOSED at v1.3) + §14.5.1 trace-ingestion dedup algorithm + §14.5.2 replay-aware orthogonality + §14.5.3 cause_attribution invariance check + §14.5.4 per-attempt cost-attribution discipline]; **(v2.8 D-5:** the three new `SpanCostRecord` fields trace to C-OD-05 §5.1 row 15 (`provider_discriminator` family tag) + C-OD-04 §4.3 (`gen_ai.provider.name` / `gen_ai.request.model` base-layer attributes) + C-OD-15 §15.1 (the cross-family rollup that consumes them).**)*

**Depends on:** [U-OD-18, U-OD-19, U-OD-04, U-IS-12 (cross-axis: IS — C-IS-10 §10.2)] — unchanged at v2.8. The three new `SpanCostRecord` fields are `string`-typed; they introduce no new carrier dependency (see §0.3 acyclicity note — typing `provider_discriminator` as U-OD-21's `CrossFamilyTag` enum would create a U-OD-20 → U-OD-21 cycle; the family tag is carried as a string).

**Inputs:** [Preserved verbatim from v2.2/v2.4.] **(v2.8 D-5 addition:** C-OD-05 §5.1 row 15 `provider_discriminator` family-tag attribute; C-OD-04 §4.3 `gen_ai.provider.name` + `gen_ai.request.model` Required (Stable) base-layer attributes; C-OD-15 §15.1 cross-family rollup axes — the consumer of the three new fields.**)*

**Files affected:** Idempotency-key join composition + dedup algorithm + per-attempt cost-attribution + F2-12 closed-contract notation (logical name: `od-cost-attribution-idempotency-join-dedup-algorithm-and-f2-12-closed-notation`).

**Signatures (v2.8 — `SpanCostRecord` grown 9 → 12 fields per D-5; all other signatures preserved verbatim from v2.2/v2.4/v2.6):**

```
record SpanCostRecord {
  span_id              : string
  idempotency_key      : string                    // from parent span per C-IS-05
  total_cost           : float                     // from U-OD-19 SpanTotalCost
  total_latency_ms     : int                       // from U-OD-19 SpanTotalCost
  derived_keys         : List<string>              // for sub-agent inheritance per C-AS-15 §15.6
  engine_replay_disposition : ReplayDisposition    // v2.2 — per CP plan v2.2 U-CP-21 4-attribute schema
  retry_attempt_number      : Optional<int>        // v2.2 — per OD spec v1.3 §14.5.2 orthogonality
  retry_cause_attribution   : Optional<string>     // v2.2 — per OD spec v1.3 §14.5.3 invariance check
  is_replay_derived         : bool                 // v2.2 — set by dedup algorithm per §14.5.1
  // v2.8 (D-5): three rollup-key fields added so the cross-family rollup at
  // U-OD-21 (rollup_costs_by_axis, C-OD-15 §15.1) is materializable. The cost
  // record carries the provider identity of the span whose cost it records —
  // a faithful operationalization of §15.1 (rollup over spans bearing these
  // attributes). String-typed: avoids a U-OD-20 -> U-OD-21 carrier cycle (see
  // §0.3). provider_discriminator carries the C-OD-05 §5.1 row-15 family tag;
  // U-OD-21's CrossFamilyTag enum is the bounded vocabulary it validates against.
  provider_discriminator    : string               // v2.8 — C-OD-05 §5.1 row 15 family tag
  gen_ai_provider_name      : string               // v2.8 — C-OD-04 §4.3 (gen_ai.provider.name)
  gen_ai_request_model      : string               // v2.8 — C-OD-04 §4.3 (gen_ai.request.model)
}

// All functions below preserved verbatim from the v2.2/v2.4/v2.6 body:
//   attach_idempotency_key_to_cost_record, dedupe_on_replay,
//   cause_attribution_invariance_check, per_attempt_cost_attribution_roll_up,
//   propagate_to_subagent, and the F2_12_* records / constants.
```

**Acceptance criteria (v2.8 — acc #1 cardinality 9 → 12 per D-5; acc #2–#15 preserved verbatim from v2.2/v2.4):**

1. **(v2.8 D-5.)** `SpanCostRecord` declares **12 fields** (was 9 at v2.2) — the nine v2.2 fields plus `provider_discriminator`, `gen_ai_provider_name`, `gen_ai_request_model` (all `string`). The three new fields carry the span's provider identity so the C-OD-15 §15.1 cross-family rollup at U-OD-21 is materializable; per §0.3 they are additive — no v2.2 field is changed.
2.–15. [Preserved verbatim from the v2.2/v2.4 body — idempotency-key join (§14.4), `dedupe_on_replay` algorithm specified per §14.5.1, `F2_12_DeferredSurface` cardinality 3, F2-12 ✅ CLOSED notation, 9-entry `F2_12_CLOSURE_PATH`, `closure_pending_at_v2_2 == false`, cross-axis edge to U-IS-12 (acc #11, v2.4 Form A), dedup correctness (#12), cause_attribution invariance ESCALATION (#13), per-attempt cost-attribution roll-up (#14), closure-status-per-surface (#15). No v2.8 change.]

**Tests (v2.8 — `test_span_cost_record_nine_fields` → `test_span_cost_record_twelve_fields`; three field tests added; all other v2.2 tests preserved verbatim):** v2.2 test set preserved except `test_span_cost_record_nine_fields` replaced by `test_span_cost_record_twelve_fields`; new at v2.8: `test_span_cost_record_provider_discriminator_field`, `test_span_cost_record_gen_ai_provider_name_field`, `test_span_cost_record_gen_ai_request_model_field`, `test_span_cost_record_new_fields_string_typed_no_cross_unit_dependency`.

**Rollback boundary:** [Preserved verbatim from v2.2.] **v2.8 addition:** reverting removes the three `SpanCostRecord` rollup-key fields; `rollup_costs_by_axis` at U-OD-21 loses its key projection and the D-5 un-materializable defect reopens. The carrier growth is a single coherent revert-boundary change.

---

## §3.5.4 U-OD-21 — Compose cross-family `provider_discriminator` rollup + tokenization-version anchor [REVISED — v2.8]

[v2.1-base unit + v2.6 M-2 `[U-OD-20]` edge. v2.8 delta (D-5): the D-5 halt is resolved — `rollup_costs_by_axis` is now materializable because the U-OD-20 `SpanCostRecord` carrier (re-opened at §3.5.3) carries the three rollup-key fields. acc #3 is preserved verbatim from v2.1 (it becomes materializable as written); acc #9 (v2.6) extended to name the key projection. `Signatures` block unchanged — `rollup_costs_by_axis(span_records : List<SpanCostRecord>, axis)` is unchanged; only its carrier's field set grew. All other surfaces — `CrossFamilyTag`, `RollupAxis`, `CrossFamilyCostRollup`, `TokenizerVersionAnchor`, `TOKENIZER_VERSION_ANCHOR_REQUIREMENT`, `FallbackChainCostComposition`, acc #1/#2/#4/#5/#6/#7/#8, `Depends on`, rollback boundary — preserved verbatim from v2.1/v2.6.]

**Implements:** [C-OD-15 §15.1, §15.2, §15.3]

**Depends on:** [U-OD-04, U-OD-18, U-OD-20, U-CP-NN (cross-axis: CP — C-CP-04 cross-family fallback chain)] — unchanged at v2.8. The `[U-OD-20]` edge (v2.6 M-2) resolves `SpanCostRecord`, now the grown 12-field carrier.

> **Materializability (v2.8 — D-5 resolution).** v2.6 added the `[U-OD-20]` edge so `SpanCostRecord` resolves to an in-cone carrier — but the carrier's field shape did not carry the rollup keys acc #3 requires (family tag / `(provider, model)` / per-attempt provider). v2.8 §3.5.3 grows `SpanCostRecord` with `provider_discriminator` + `gen_ai_provider_name` + `gen_ai_request_model`. `rollup_costs_by_axis` now projects: `PER_PROVIDER_DISCRIMINATOR` groups by `provider_discriminator`; `PER_PROVIDER_AND_MODEL` groups by `(gen_ai_provider_name, gen_ai_request_model)`; `PER_FALLBACK_EVENT` reads per-attempt provider identity from `gen_ai_provider_name` (discriminated by `retry_attempt_number`). acc #3 is materializable verbatim. Acyclic — `[U-OD-20]` is the only edge; U-OD-20's three new fields are `string`-typed and introduce no U-OD-20 → U-OD-21 edge.

**Inputs:** OD spec v1.2 §15.1 cross-family `provider_discriminator` cost rollup (3 rollup axes); §15.2 tokenization-version anchor (2 options); §15.3 cross-family fallback chain composition reference per ADR-F1 v1.2 §Decision; the U-OD-20 `SpanCostRecord` 12-field carrier (`provider_discriminator` / `gen_ai_provider_name` / `gen_ai_request_model` rollup-key fields).

**Files affected:** Cross-family provider-discriminator rollup + tokenization-version anchor (logical name: `od-cost-attribution-cross-family-and-tokenizer`).

**Persona linkage.** Persona §10.2 (cost-attribution foundational — cross-family visibility under fallback chain advancement per ADR-F1 v1.2).

**Signatures (preserved verbatim from v2.1 — no signature change at v2.8; `SpanCostRecord` is the grown U-OD-20 carrier):**

```
enum CrossFamilyTag {                              // per c7-observability SKILL.md substrate (F2-10 closure)
  FRONTIER_MANAGED,
  FRONTIER_MANAGED_ALT,
  LOCAL_OLLAMA
  // extensible per chain composition
}

enum RollupAxis {
  PER_PROVIDER_DISCRIMINATOR,                      // per-family cost
  PER_PROVIDER_AND_MODEL,                          // per-(provider, model) cost
  PER_FALLBACK_EVENT                               // per-retry-attempt cost with family-tag rollup
}

record CrossFamilyCostRollup {
  rollup_axis              : RollupAxis
  group_key                : string
  total_cost               : float
  span_count               : int
}

fn rollup_costs_by_axis(
  span_records : List<SpanCostRecord>,             // SpanCostRecord = the grown 12-field U-OD-20 carrier
  axis         : RollupAxis
) -> List<CrossFamilyCostRollup>

enum TokenizerVersionAnchor {
  OPTION_A_ATTRIBUTE_ON_EVERY_SPAN,
  OPTION_B_VERSIONED_PRICE_TABLE
}

const TOKENIZER_VERSION_ANCHOR_REQUIREMENT :
  "Phase 6+ dashboard authors MUST select OPTION_A or OPTION_B; failing to anchor on tokenizer_version produces silent cost-dashboard breakage on model version transitions"

record FallbackChainCostComposition {
  parent_span_family_tag       : CrossFamilyTag
  per_attempt_provider         : string
  per_attempt_rate_key         : PriceRateKey
  cache_state_loss_on_cross_family : bool
}
```

**Acceptance criteria (v2.8 — acc #3 materializable verbatim against the grown carrier; acc #9 extended; #1/#2/#4–#8 preserved verbatim from v2.1/v2.6):**

1. `CrossFamilyTag` bounded enum per F2-10 closure (c7-observability SKILL.md primary anchor; ADR-F1 v1.2 §Decision composition context).
2. `RollupAxis` enumerates exactly 3 values per §15.1.
3. `rollup_costs_by_axis` returns aggregated rollups per axis: `PER_PROVIDER_DISCRIMINATOR` keys on family tag; `PER_PROVIDER_AND_MODEL` keys on `(provider, model)` tuple; `PER_FALLBACK_EVENT` preserves per-attempt provider identity. **(v2.8 D-5: materializable verbatim — the key values project from the U-OD-20 `SpanCostRecord` `provider_discriminator` / `gen_ai_provider_name` / `gen_ai_request_model` fields.)**
4. `TokenizerVersionAnchor` enumerates exactly 2 options per §15.2 verbatim.
5. `TOKENIZER_VERSION_ANCHOR_REQUIREMENT` carries §15.2 anchor text verbatim; downstream U-OD-22 dashboard binding MUST consume this anchor.
6. `FallbackChainCostComposition` per §15.3 verbatim: parent retains family tag; per-attempt provider updates per retry; per-attempt rate-key updates; cache state loss on cross-family transition (anthropic.cache_read_input_tokens = 0).
7. Cross-axis edge per OD-S4-3.A: `Depends on: [U-CP-NN (cross-axis: CP — C-CP-04 fallback chain unit)]`.
8. Source authority per F2-10 closure: `provider_discriminator` substrate is `c7-observability` SKILL.md (primary anchor); ADR-F1 v1.2 §Decision is composition context, not attribute-name declaration site.
9. **(v2.6 M-2; v2.8 D-5 extension.)** `rollup_costs_by_axis`'s `span_records : List<SpanCostRecord>` consumes the U-OD-20-declared `SpanCostRecord` via the `[U-OD-20]` `Depends on` edge; the three rollup keys project from the carrier's `provider_discriminator` (family tag — validated against `CrossFamilyTag` at this unit), `gen_ai_provider_name`, and `gen_ai_request_model` fields.

**Tests (v2.8 — rollup tests now executable against the grown carrier; key-projection tests added):** `test_rollup_axis_cardinality_three`, `test_rollup_per_provider_discriminator`, `test_rollup_per_provider_and_model`, `test_rollup_per_fallback_event_preserves_provider`, `test_rollup_key_projects_from_span_cost_record_fields`, `test_provider_discriminator_validated_against_cross_family_tag`, `test_tokenizer_anchor_two_options`, `test_tokenizer_anchor_requirement_byte_exact`, `test_fallback_chain_parent_family_tag_retained`, `test_fallback_chain_per_attempt_provider_updates`, `test_cache_state_loss_on_cross_family`, `test_provider_discriminator_source_authority_c7`, `test_cross_axis_edge_to_u_cp_nn_c_cp_04`, `test_span_cost_record_param_carrier_u_od_20_in_cone`, `test_depends_on_u_od_20_edge_declared`.

**Rollback boundary:** Revert cross-family provider_discriminator rollup + tokenization-version anchor. Cross-family cost visibility under fallback loses 3-axis rollup; tokenization-version drift loses dashboard-stability anchor; chain-advancement seam composition with ADR-F1 v1.2 loses per-attempt cost-attribution; U-OD-22 dashboard binding loses cross-family rollup query primitive. [v2.8 revert appendix:] Reverting v2.8 does not by itself reopen D-5 (the carrier growth is at U-OD-20); reverting U-OD-20's §3.5.3 carrier growth reopens the D-5 un-materializable rollup.

---

## §4.6 Dependency-graph delta (v2.8)

**No delta.** None of the six v2.8-revised units adds, removes, or re-points a `Depends on` edge:

| Unit | v2.8 change | Edge effect |
|---|---|---|
| U-OD-02 | `backend_class` widened to `Set<BackendClass>` | None — `BackendClass` is in-unit; no carrier change |
| U-OD-08 | `F3LifecycleEventClass` member set conformed to §6.1 | None — in-unit enum + record |
| U-OD-09 | `HARNESS_BREAKER_ATTRIBUTES` re-typed to `List<string>`; acc #2 struck | None — `[U-OD-04]` edge retained (justified by `SpanRef` / `EventEmission`); `GenAiAttribute` no longer consumed but the edge stands |
| U-OD-12 | acc #2 re-scoped | None — no signature change |
| U-OD-20 | `SpanCostRecord` grown 9 → 12 fields (`string`-typed) | None — string typing introduces no carrier dependency (deliberate, per §0.3 — avoids a U-OD-20 → U-OD-21 cycle) |
| U-OD-21 | `rollup_costs_by_axis` materializable against the grown carrier | None — `[U-OD-20]` edge already declared at v2.6 M-2 |

All v2.7 within-axis + cross-axis edges are preserved verbatim. The within-axis DAG is unchanged; the Kahn topological sort (v2.7 §4.6, with U-OD-00 at L1) is unchanged; acyclicity holds. All 35 units still consume.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_8.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-16 — v2.8 revision pass (five Class 1 defects U-OD-02/08/09/12/21 + F3 taxonomy pinning) |
| Authoring authority | Operator ratification 2026-05-16; `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_7.md` (U-OD-00 carrier-defect micro-revision) |
| Successor consumption | OD-7b resumes — the 17 blocked OD units land against this file (deferred cluster roots U-OD-02/08/09/12/21 cleared; cascade U-OD-03/10/22/24/25/28/29/30/31/32/33/34 unblocked). U-OD-20 re-lands (carrier growth) ahead of U-OD-21. |
| Revision policy | Canonical for the OD axis plan; revisions in-CLI per workspace discipline (`CLAUDE.md` §4.3 — design-phase back-flow deprecated 2026-05-15) |

*End of Implementation Plan — Operational Discipline v2.8. Delta over v2.7 — only §3.1.2 U-OD-02, §3.2.5 U-OD-08, §3.3.1 U-OD-09, §3.4.2 U-OD-12, §3.5.3 U-OD-20 (RE-OPENED — landed-unit carrier growth), §3.5.4 U-OD-21 revised. All other sections preserved verbatim from v2.7. No dependency-graph edge changed; unit count unchanged (35). `harness-od/CLAUDE.md` §1.1 F3-taxonomy correction applied in-session per §0.5.*
