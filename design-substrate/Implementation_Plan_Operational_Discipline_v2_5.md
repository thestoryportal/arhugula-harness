# Implementation Plan — Operational Discipline (OD axis) — v2.5

*Revision-pass amendment to v2.4. Authored at Phase 7 (CLI workspace) — absorption of the operator-ratified `.harness/verbatim_audit_od_plan.md` §4A OD-plan verbatim-divergence cluster resolution. Skill: `implementation-planner` SKILL.md §8 revision-pass sub-mode. Authority chain: `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3.*

---

## §0 Change-note

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_4.md` (v2.4 — F3-02 Form A citation-precision absorption + C3-15 Path (i-refined) IS-consuming-edge delete/remap; Phase 6.5 Session 3 ζ). v2.4 is a delta file over v2.3 over v2.1; the full unit bodies for U-OD-01 – U-OD-34 reside at `Implementation_Plan_Operational_Discipline_v2_1.md` §3 (preserved verbatim into v2.2/v2.3/v2.4 except U-OD-20, revised at v2.2 cascade Step 6b and v2.4 Form A).

### §0.2 Revision scope

v2.4 → v2.5: absorption of the operator-ratified resolution recorded at `.harness/verbatim_audit_od_plan.md` **§4A — OD-plan verbatim-divergence cluster**.

That audit report is the **canonical systemic-tension record** for the cluster (per the Phase-7 checkpoint decision: no per-unit Tension 005+ proliferation; the report carries all ten cluster units plus folds in the already-filed Tension 004 = U-OD-04). The §4A Resolution Recommendation was operator-ratified per §4A.7 action 1: **conform the determinate OD verbatim-divergence cluster to the cited `Spec_Operational_Discipline` vocabulary**, in a single `implementation-planner` revision-pass, with cross-unit propagation in the same pass.

**Defect class absorbed.** Each conformed unit carried an acceptance criterion asserting a signature is materialized "per §X verbatim" / "exactly N per §X" against a `Spec_Operational_Discipline` contract whose value set, cardinality, or vocabulary the signature did not transcribe. The spec is canonical for the plan per `CLAUDE.md` §1.3; the plan is the artifact in error. v2.5 conforms the plan.

| Unit | Divergent surface | Conformance | Cited spec § |
|---|---|---|---|
| U-OD-02 | `BackendClass` enum + per-cell `backend_class` rows | 3 values → 7 distinct classes; per-cell rows conformed | OD spec v1.2 §2.1 |
| U-OD-04 | span name format; `GenAiOperation`; `AttributeTier`; `BASE_METRIC_NAME`; acc #4 attribute-tier binding | 2-component → 3-component span name; 6 → 7 operations; 4 → 3 tiers; base metric → `gen_ai.client.operation.duration`; acc #4 conformed to §4.3 3-tier table | OD spec v1.2 §4.1, §4.2, §4.3, §4.5 |
| U-OD-09 (acc #3 only) | `BreakerScope` enum | 4 values → 2 values (`per_model` / `per_provider`) | OD spec v1.2 §7.1 |
| U-OD-11 | `ALWAYS_SAMPLED_EVENT_CLASSES` member set | cardinality 18 preserved; member set conformed | OD spec v1.2 §9.2 |
| U-OD-12 | `BASE_RATE_SAMPLED_EVENT_CLASSES` member set | cardinality 13 preserved; member set conformed | OD spec v1.2 §10.1 |
| U-OD-14 | `CARDINALITY_SAFE_ATTRIBUTES` + `CARDINALITY_PROHIBITED_ATTRIBUTES` member sets | cardinalities 13 / 6 preserved; both member sets conformed | OD spec v1.2 §11.2, §11.3 |
| U-OD-30 (acc #6 only) | `SignatureAlgorithm` enum | `HMAC_SHA256` → `rsa-pss-2048` | OD spec v1.2 §21.2 (chain-unanimous with ADR-D5 §1.4.1) |
| U-OD-32 | `BRIDGING_ARC_TRANSITIONS` member set | cardinality 8 preserved; transition set conformed (5 within-column + 3 diagonal) | OD spec v1.2 §22.1 |
| U-OD-33 | `PreservationDimension` member set | cardinality 5 preserved; dimension set conformed | OD spec v1.2 §22.2 |

Ten cluster units total. U-OD-28 is the tenth — carried, not conformed, per §0.7 (conformance target undetermined per §4A.4 item 2).

No new units; no unit retired; no contract re-decomposed. v2.5 is a vocabulary-conformance pass — same contracts, same dependency topology, value sets corrected to the spec.

### §0.3 Sections preserved verbatim from v2.4

| Section | Status |
|---|---|
| §0 (v2.4 change-note) | Superseded by this §0; v2.4 closure records preserved as predecessor history |
| §1 Spec inventory | Preserved verbatim |
| §2 Cluster topology | Preserved verbatim |
| §3.1.1 U-OD-01 | Preserved verbatim |
| §3.1.3 U-OD-03 | Preserved verbatim |
| §3.2.2 – §3.2.5 U-OD-05 – U-OD-08 | Preserved verbatim |
| §3.3.2 U-OD-10 | Preserved verbatim |
| §3.4.3 U-OD-13 | Preserved verbatim |
| §3.4.5 – §3.4.7 U-OD-15 – U-OD-17 | Preserved verbatim |
| §3.5 U-OD-18 – U-OD-22 | Preserved verbatim (U-OD-22 — see §0.6 consumer-scoping check; not literally enumerating, pointer-preserved) |
| §3.4 U-OD-20 (v2.4 amendment) | Preserved verbatim from v2.4 |
| §3.6 U-OD-23 – U-OD-31 | Preserved verbatim (U-OD-28 — carried per §0.7; body NOT revised) |
| §3.8.3 U-OD-34 (terminal aggregate exporter) | Preserved verbatim |
| §4.1 – §4.4 (within-axis dependency graph, acyclicity, topological sort) | Preserved verbatim |
| §4.5.1 IS-consuming edges (4 edges, v2.4) | Preserved verbatim from v2.4 |
| §4.5.2 AS-consuming edges (10 edges) | Preserved verbatim |
| §4.5.3 CP-consuming edges (12 edges) | Preserved verbatim |
| §4.5.4 (terminal aggregate cross-axis references) | Preserved verbatim |
| §5 Spec-traceability matrix | Preserved verbatim |

### §0.4 Sections revised

Nine unit bodies are full-revised at v2.5. Each revision conforms an enum/set signature and every dependent "verbatim" / "exactly N" / "matches §X" acceptance criterion to the cited spec section. Full revised bodies at §3 below.

| § | Unit | Substantive surface revised |
|---|---|---|
| §3.1.2 | U-OD-02 | `BackendClass` signature (3 → 7 values); acc #1 + #3 (per-cell row table) |
| §3.2.1 | U-OD-04 | `SPAN_NAME_FORMAT` (2 → 3 component); `GenAiOperation` (6 → 7); `AttributeTier` (4 → 3); `BASE_METRIC_NAME`; acc #1–#4, #6; tests |
| §3.3.1 | U-OD-09 | `BreakerScope` signature (4 → 2 values); acc #3 + dependent prose/tests. **acc #2 carried unchanged — see §0.7** |
| §3.4.1 | U-OD-11 | `ALWAYS_SAMPLED_EVENT_CLASSES` member set; acc #3 + dependent tests |
| §3.4.2 | U-OD-12 | `BASE_RATE_SAMPLED_EVENT_CLASSES` member set; acc #1 + dependent tests |
| §3.4.4 | U-OD-14 | `CARDINALITY_SAFE_ATTRIBUTES` + `CARDINALITY_PROHIBITED_ATTRIBUTES` member sets; acc #1 + #2 |
| §3.7.4 | U-OD-30 | `SignatureAlgorithm` signature (3rd value); acc #6 + dependent tests |
| §3.8.1 | U-OD-32 | `BRIDGING_ARC_TRANSITIONS` member set; acc #1 + dependent tests |
| §3.8.2 | U-OD-33 | `PreservationDimension` member set; acc #1 + #2 |

#### §0.4.1 Coverage matrix delta

**None at cluster-to-contract level.** Every conformed unit continues to implement the exact same `C-OD-*` contract(s) it implemented at v2.4 (`Implements:` fields unchanged at all nine units). The conformance corrects the *vocabulary* a unit transcribes from its already-cited contract; it does not add, drop, or re-target any contract coverage. The §5 spec-traceability matrix is unchanged.

#### §0.4.2 Dependency-graph delta

**No delta.** All 34 OD units preserved as graph nodes; every `Depends on:` edge preserved (the conformed units' `Depends on:` fields are unchanged — U-OD-02 `[U-OD-01]`, U-OD-04 `[]`, U-OD-09 `[U-OD-07]`, U-OD-11 `[U-OD-04, U-OD-05, U-OD-06, U-OD-09]`, U-OD-12 `[U-OD-01, U-OD-11]`, U-OD-14 `[U-OD-05, U-OD-13]`, U-OD-30 `[U-OD-01, U-OD-02, U-OD-28, + cross-axis]`, U-OD-32 `[U-OD-01, U-OD-11, U-OD-12, U-OD-15, U-OD-16, U-OD-17]`, U-OD-33 `[U-OD-05, U-OD-07, U-OD-11, U-OD-12, U-OD-17, U-OD-32, + cross-axis]`). Within-axis DAG acyclic; topological sort unchanged. Cross-axis edge enumerations (§4.5.1–§4.5.4) unchanged.

#### §0.4.3 §6 Filing footer

Version bumped to v2.5; change-note pointer added.

### §0.5 Cross-unit propagation — scoping result

§4A.4 named two propagation chains. Both were scoped by reading each named consumer's v2.1 body:

| Propagation chain (§4A.4) | Named consumers | Scoping result |
|---|---|---|
| U-OD-09 `BreakerScope` (4 → 2) → U-OD-14 `harness.breaker.scope` reference + breaker consumers | **U-OD-14** | U-OD-14's `CARDINALITY_SAFE_ATTRIBUTES` carries the **attribute-name string** `"harness.breaker.scope"`, not the `BreakerScope` *enum members*. Renaming the `BreakerScope` enum values does not change that attribute-name string. U-OD-14 is independently full-revised at v2.5 for its own §11.2/§11.3 member-set divergence; no *additional* edit is induced by the `BreakerScope` rename. No other unit literally enumerates `BreakerScope` members (U-OD-10 references `BreakerScope` only as a symbolic type in a cardinality-bound product expression — `[preserved verbatim]` pointer). |
| U-OD-02 `BackendClass` (3 → 7) → U-OD-28 placement matrix + U-OD-22 dashboard routing | **U-OD-28**, **U-OD-22** | **U-OD-22** (`§3.5.5`): body enumerates `DashboardBindingForm` / `AlertingHook` / `AlertingSignal` — it routes by *cell-class buckets* (solo / team / multi-tenant), never by literal `BackendClass` enum members. Symbolic backend-class reference only → `[preserved verbatim]` pointer. **U-OD-28** (`§3.7.2`): body enumerates `CollectorPlacement`; it does not literally enumerate `BackendClass`. U-OD-28's `Depends on: [U-OD-02]` edge is a symbolic type dependency, unaffected by the enum widening → no `BackendClass`-induced edit. (U-OD-28 is *separately* in the cluster for its own `CollectorPlacement` "verbatim" divergence — carried per §0.7, not conformed here.) |

**Conclusion:** no consumer unit literally enumerates a renamed/re-set value. All named consumers stay as `[preserved verbatim]` pointers. The propagation pass induced no additional full-revisions beyond the nine determinate units already in §0.4.

### §0.6 Forward-flagged concerns

| # | Concern | Disposition |
|---|---|---|
| FF-1 | **U-OD-09 acc #2 — Required/Conditional tier split.** Acc #2 asserts "4 Required / 3 Conditional tier classification per §7.1". OD spec §7.1 seven-attribute schema table declares **no tier classification at all** — there is no Required/Conditional split in §7.1. This is a plan-introduced H_T structure with no spec basis; there is nothing to conform it *to*. | **[carried — pending operator decision per §4A.7 action 2]**. Per `CLAUDE.md` I-2 / X-AL-3 (no silent H_T design extension at Phase 7), this is a §2.7.6 Class 1 fork of a distinct shape (design gap, not conformance tension). Resolution: either `spec-writer` extends §7.1 to commit the tier split, or the operator sanctions the plan-introduced split with recorded rationale. v2.5 conforms acc #3 (`BreakerScope`) only; **acc #2 prose, the `tier:` field annotations in the `HARNESS_BREAKER_ATTRIBUTES` signature, and the `test_required_tier_attributes_count_four` / `test_conditional_tier_attributes_count_three` tests are preserved verbatim from v2.1 at §3.3.1 and NOT conformed.** |
| FF-2 | **U-OD-28 — `CollectorPlacement` "exactly 7 values per §20.1 verbatim".** §20.1 is a per-cell placement matrix, not a 7-value enum declaration; the OD spec §1.2 collector-placement enum is **6-valued** (`in-process, sidecar, vendor-pipeline, sidecar with per-tenant routing, per-tenant collector instance, vendor-managed collector`). The plan's 7-value enum resolves to no 7-element verbatim surface in §20.1. | **[carried — pending operator decision per §4A.7 action 3]**. Decision-vocabulary label: *proposing* (§4A.4 item 2). The operator must confirm **which §20.1 surface the "verbatim" claim targeted** before the conformance target is fixed. U-OD-28 stays in the cluster but its conformance target is undetermined; v2.5 does **not** conform it and does **not** guess the target. U-OD-28's body is `[preserved verbatim]` from v2.1 at §3.7.2. |
| FF-3 | **U-OD-29 — `SandboxTier` `TIER_0..TIER_3` "per D2 v1.1 §1.2".** U-OD-29 asserts a `Tier-0..3` labeling; OD spec §20.3 itself uses `Tier-1..Tier-4` labels. The divergence target is an ADR (ADR-D2 §1.2), not a spec-§ verbatim claim of the audited shape. | **[carried — pending operator decision per §4A.7 action 4]**. Decision-vocabulary label: *open*. This pass did not read `ADR-D2.md` §1.2. The operator (or a follow-on pass) must verify ADR-D2 §1.2 directly to confirm whether `Tier-0..3` is ADR-sanctioned before U-OD-29 is classified. U-OD-29 is **not** in the conformed cluster and is **not** revised at v2.5. |
| FF-4 | **CXA-OD-IS-EDGE-DRIFT** (carried from v2.4 §0.9) | Unchanged; non-blocking; future composition-document revision pass. |
| FF-5 | **OD-INTERNAL-FORMALIZATION** (carried from v2.4 §0.9) | Unchanged; non-blocking. |

### §0.7 Carried-not-resolved items (pending operator decision per §4A.7)

Three items in the §4A cluster discussion are **carried, not resolved** at v2.5, per the explicit §4A.7 routing. They are recorded at §0.6 as FF-1 (U-OD-09 acc #2 — design gap), FF-2 (U-OD-28 — *proposing*; conformance target undetermined), FF-3 (U-OD-29 — *open*; ADR-D2 §1.2 verification required). v2.5 does **not** edit any of the three; conforming them would require either a spec extension (FF-1) — foreclosed by `CLAUDE.md` I-2 / X-AL-3 absent operator decision — or an undetermined target (FF-2) or an unverified ADR (FF-3).

### §0.8 Backref reconciliation (Pattern P2 self-audit)

- Every "verbatim" / "exactly N" / "matches §X" acceptance criterion authored or revised at v2.5 §3 was conformed by **opening the cited `Spec_Operational_Discipline_v1_2.md` section, copying the canonical value names directly from the spec table, and re-verifying the written plan body against the spec section after writing.** This is the mechanical copy-then-reverify discipline mandated by the §4A resolution (the defect this pass exists to remove was transcription-from-memory).
- Spec sections cross-checked: §2.1 (U-OD-02), §4.1/§4.2/§4.3/§4.5 (U-OD-04), §7.1 (U-OD-09), §9.2 (U-OD-11), §10.1 (U-OD-12), §11.2/§11.3 (U-OD-14), §21.2 (U-OD-30), §22.1 (U-OD-32), §22.2 (U-OD-33). All against `Spec_Operational_Discipline_v1_2.md` — §1–§13 + §14.1–§14.4 canonical-verbatim per `Spec_Operational_Discipline_v1_3.md` §0.1 attestation; none of the conformed surfaces is touched by the v1.3 §14.5 amendment.
- ADR-D5 §1.4 / §1.4.1 read directly for the U-OD-30 tiebreaker (§4A.5): `audit_signature_algorithm ∈ {ed25519 / ecdsa-p256 / rsa-pss-2048}` — confirms `rsa-pss-2048`, contradicts the plan's `HMAC_SHA256`. The chain (spec C-OD-21 §21.2 + ADR-D5 §1.4.1) is unanimous; U-OD-30's conformance is determinate.
- All preserved-verbatim units' citations carried unchanged from v2.4; no version bump required (spec is v1.2-canonical / v1.3-attested; no spec revision in this pass).
- CXA v2.1 cross-axis edge enumerations NOT updated (out-of-scope; CXA preserved at v2.1).

### §0.9 Coherence-pass summary

Coherence pass run over the nine full-revised units + their immediate dependency-graph neighbors per `implementation-planner` SKILL.md §8.6:

- **§4 sub-disciplines (per SKILL.md §4):** all nine revised units satisfy atomicity (single coherent change — one enum/set conformed per unit), spec-traceability (`Implements:` fields unchanged; section-level citations verified byte-exact against `Spec_Operational_Discipline_v1_2.md`), dependency-awareness (`Depends on:` unchanged; see §0.4.2), implementation-grade detail (signatures + acceptance + tests present).
- **No spec extension.** Every conformed value is copied *from* the spec; no value the spec does not declare is introduced. The one place where the plan exceeds the spec — U-OD-09 acc #2's tier split — is **not** conformed and **not** absorbed; it is surfaced as FF-1 (§0.6) per `CLAUDE.md` I-2.
- **Coverage matrix complete** (§0.4.1 — no delta). **Dependency graph acyclic** (§0.4.2 — no delta).
- **Internal-contradiction check:** the audit's core finding was that each divergent unit's acceptance criteria were internally contradictory (claiming "verbatim" against a non-matching set). After v2.5 conformance, each conformed unit's "verbatim" / "exactly N" claim now transcribes the cited spec section — the contradiction is removed for the nine determinate units. The two cluster units NOT conformed (U-OD-28) and the design-gap acceptance (U-OD-09 acc #2) retain their contradiction by design, flagged FF-1/FF-2 for operator disposition; they cannot land until the operator dispositions them.

Status posture: `Status: Proposed` per SKILL.md §8 (preserved until P6-CK / Phase-7 pre-implementation re-clearance).

---

## §1 Spec inventory

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_4.md` §1 (which preserves v2.3 → v2.1 §1).]

## §2 Cluster topology

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_4.md` §2.]

## §3 Atomic-unit decomposition

[All §3 sub-sections preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_4.md` (which preserves v2.3 → v2.1 §3, with U-OD-20 at v2.2/v2.4 amendment) **except the nine units full-revised below**: §3.1.2 U-OD-02, §3.2.1 U-OD-04, §3.3.1 U-OD-09, §3.4.1 U-OD-11, §3.4.2 U-OD-12, §3.4.4 U-OD-14, §3.7.4 U-OD-30, §3.8.1 U-OD-32, §3.8.2 U-OD-33.]

### §3.1.2 U-OD-02 — Declare per-cell backend class + candidate witness columns (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `BackendClass` enum + acc #1 + acc #3 conformed to OD spec v1.2 §2.1. All other surfaces (`CandidateWitness`, `PerCellBackendBinding`, `PER_CELL_BACKEND_BINDINGS`, acc #2/#4/#5/#6/#7/#8, rollback boundary, Persona linkage, Files affected) preserved verbatim from v2.1 §3.1.2.]

**Implements:** [C-OD-02 §2.1, §2.2, §2.3]

**Depends on:** [U-OD-01]

**Inputs:** OD spec v1.2 §2.1 per-cell backend class (eight cells; **seven distinct classes** — cell-4 admits a class disjunction at the design-time-flexible row); §2.2 per-cell candidate witness columns (per-cell candidate list per ADR-D6 v1.1 §1.1); §2.3 cell-class commitment invariant.

**Files affected:** Per-cell backend class + candidate witness column declaration (logical name: `od-per-cell-backend-class`).

**Persona linkage.** Persona §9 (deployment-surface candidate enumeration); §10.4 (compliance-readiness backend selection at multi-tenant cells).

**Signatures (v2.5 — `BackendClass` conformed to §2.1):**

```
// §2.1: "Eight cells; seven distinct classes" — the seven distinct backend
// classes enumerated across the §2.1 per-cell table (cell-4 admits a
// disjunction over two of these seven; no eighth class).
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
  candidate_name   : string                        // e.g., "Langfuse self-hosted single-node"
  vendor_class     : string                        // e.g., "Langfuse" | "Arize" | "Helicone" | "Datadog" | "Sentry"
  deployment_form  : string                        // e.g., "single-node OTLP endpoint"
}

record PerCellBackendBinding {
  cell_id         : CellID
  backend_class   : BackendClass
  candidates      : List<CandidateWitness>
}

const PER_CELL_BACKEND_BINDINGS : Map<CellID, PerCellBackendBinding>   // exactly 8 entries

fn select_backend_class(c : CellID) -> BackendClass
fn enumerate_candidates(c : CellID) -> List<CandidateWitness>
```

**Acceptance criteria (v2.5 — acc #1 + #3 conformed to §2.1; #2, #4–#8 preserved verbatim from v2.1):**

1. `BackendClass` enumerates exactly **7** distinct values per §2.1 verbatim — §2.1 states "Eight cells; seven distinct classes (cell-4 admits a class disjunction at the design-time-flexible row)". The seven classes are: `OTEL_ONLY`, `DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE`, `DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE`, `CLOUD_NATIVE_LLM_OBS_PLATFORM`, `OTEL_TO_VENDOR`, `SELF_HOSTED_MULTI_TENANT_LLM_OBS_PLATFORM`, `VENDOR_MANAGED_MULTI_TENANT_LLM_OBS_OR_CLOUD_NATIVE_MANAGED_AGENT_RUNTIME`.
2. `PER_CELL_BACKEND_BINDINGS` declares exactly 8 entries — one per ACTIVE cell.
3. Per-cell `backend_class` matches §2.1 row verbatim:
   - cell-1 (solo-developer × local-development) → `OTEL_ONLY` ("OTel-only")
   - cell-2 (solo-developer × self-hosted-server) → `DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE` ("Dedicated LLM-obs platform (single-node)")
   - cell-3 (solo-developer × managed-cloud) → `CLOUD_NATIVE_LLM_OBS_PLATFORM` ("Cloud-native LLM-obs platform")
   - cell-4 (team-binding × local-development) → `OTEL_ONLY` OR `DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE` ("OTel-only OR Dedicated LLM-obs platform (single-node)" — the §2.1 design-time-flexible disjunction row)
   - cell-5 (team-binding × self-hosted-server) → `DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE` OR `OTEL_TO_VENDOR` ("Dedicated LLM-obs platform (multi-node) OR OTel-to-vendor")
   - cell-6 (team-binding × managed-cloud) → `CLOUD_NATIVE_LLM_OBS_PLATFORM` ("Cloud-native LLM-obs platform")
   - cell-7 (multi-tenant-compliance × self-hosted-server) → `SELF_HOSTED_MULTI_TENANT_LLM_OBS_PLATFORM` ("Self-hosted multi-tenant LLM-obs platform")
   - cell-8 (multi-tenant-compliance × managed-cloud) → `VENDOR_MANAGED_MULTI_TENANT_LLM_OBS_OR_CLOUD_NATIVE_MANAGED_AGENT_RUNTIME` ("Vendor-managed multi-tenant LLM-obs OR cloud-native managed agent runtime")
4. Per-cell `candidates` carries the candidate list per ADR-D6 v1.1 §1.1 verbatim (Langfuse / Arize Phoenix / Helicone / vendor LLM-obs / Datadog / Sentry / Bedrock AgentCore / Vertex Agent Engine / LangSmith Enterprise / Langfuse Cloud Enterprise — candidates by cell).
5. `select_backend_class(EXCLUDED_CELL)` returns `Err` per U-OD-01 `reject_excluded_cell` composition; backend class is undefined at the EXCLUDED cell.
6. `enumerate_candidates` returns the candidate list per cell; candidates are witness columns — operators MAY select within the list at deployment-binding time.
7. Cell-class commitment invariant per §2.3: each ACTIVE cell carries exactly one `backend_class` (cell-4 alternation, and cell-5 alternation, are the rare/design-time-flexible-configuration witnesses per §2.1; both alternants are class-committed shapes at the respective cell).
8. Candidate witnesses are not exhaustive enumeration — they constitute the witness column per ADR-D6 v1.1 §1.1; deployment-binding-time operator binding within the witness column is permitted.

**Tests (v2.5 — cardinality + per-cell tests conformed to §2.1):** `test_backend_class_cardinality_seven`, `test_per_cell_bindings_cardinality_eight`, `test_cell_1_backend_class_otel_only`, `test_cell_2_backend_class_dedicated_single_node`, `test_cell_3_backend_class_cloud_native`, `test_cell_4_alternation_otel_or_dedicated_single_node`, `test_cell_5_alternation_dedicated_multi_node_or_otel_to_vendor`, `test_cell_6_backend_class_cloud_native`, `test_cell_7_backend_class_self_hosted_multi_tenant`, `test_cell_8_backend_class_vendor_managed_multi_tenant_or_managed_agent_runtime`, `test_select_backend_class_excluded_cell_returns_err`, `test_enumerate_candidates_per_cell_nonempty`.

**Rollback boundary:** Revert per-cell backend class + candidate witness columns. R-OD-01 satisfaction loses per-cell backend selection substrate; U-OD-28 per-cell collector placement matrix loses the candidate-bound backing-contract references; U-OD-22 per-cell cost-attribution dashboard binding loses backend class enum for cell-class-row routing. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 3-value `BackendClass` enum (the audited divergent state) — the revert is a regression to the verbatim-divergence defect and MUST NOT be performed absent a §4A re-disposition.

---

### §3.2.1 U-OD-04 — Implement OTel GenAI semconv 1.41.0 base-layer attributes (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `SPAN_NAME_FORMAT`, `GenAiOperation`, `AttributeTier`, `BASE_METRIC_NAME`, and acc #1–#4 + #6 conformed to OD spec v1.2 §4.1/§4.2/§4.3/§4.5. This absorbs the previously-filed Tension 004 into the v2.5 cluster pass per §4A.6. acc #5/#7/#8, hierarchy-correlation prose, `GenAiAttribute` / `BASE_LAYER_ATTRIBUTES` record shapes, rollback boundary preserved verbatim from v2.1 §3.2.1.]

**Implements:** [C-OD-04 §4.1, §4.2, §4.3, §4.4, §4.5]

**Depends on:** []

**Inputs:** OD spec v1.2 §4.1 span name format (`{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}` — 3-component); §4.2 operations enum (7 operations); §4.3 attribute tiers (Required (Stable) / Recommended (Development) / Opt-In content — **3 tiers**); §4.4 hierarchy correlation (`gen_ai.conversation.id` correlation key); §4.5 base metric (`gen_ai.client.operation.duration` histogram per spec).

**Files affected:** OTel GenAI semconv 1.41.0 base-layer attribute declaration (logical name: `od-otel-genai-base-layer`).

**Persona linkage.** Persona §10.2 (observability foundational primitives — token usage measurement at every LLM call).

**Signatures (v2.5 — conformed to §4.1/§4.2/§4.3/§4.5):**

```
// §4.1 verbatim — 3-component span name format
const SPAN_NAME_FORMAT : string =
  "{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}"

// §4.2 verbatim — gen_ai.operation.name ∈
// {chat, text_completion, embeddings, generate_content, create_agent,
//  invoke_agent, execute_tool}
enum GenAiOperation {
  CHAT,
  TEXT_COMPLETION,
  EMBEDDINGS,
  GENERATE_CONTENT,
  CREATE_AGENT,
  INVOKE_AGENT,
  EXECUTE_TOOL
}                                                  // exactly 7 operations per §4.2

// §4.3 verbatim — three tiers
enum AttributeTier {
  REQUIRED_STABLE,            // §4.3 — Required (Stable); always emitted
  RECOMMENDED_DEVELOPMENT,    // §4.3 — Recommended (Development); emitted unless
                              //        cardinality-safe-attribute discipline excludes
  OPT_IN_CONTENT              // §4.3 — Opt-In content; default-off per C-OD-12
}                                                  // exactly 3 tiers per §4.3

record GenAiAttribute {
  name        : string             // e.g., "gen_ai.provider.name", "gen_ai.request.model"
  tier        : AttributeTier
}

const BASE_LAYER_ATTRIBUTES : List<GenAiAttribute>   // OTel GenAI semconv 1.41.0 base set

// §4.5 verbatim — base metric
const BASE_METRIC_NAME : string = "gen_ai.client.operation.duration"   // histogram
```

**Acceptance criteria (v2.5 — #1–#4, #6 conformed to §4; #5/#7/#8 preserved verbatim from v2.1):**

1. `SPAN_NAME_FORMAT` matches §4.1 verbatim — the 3-component format `{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}`.
2. `GenAiOperation` enumerates exactly **7** operations per §4.2 verbatim: `chat`, `text_completion`, `embeddings`, `generate_content`, `create_agent`, `invoke_agent`, `execute_tool`.
3. `AttributeTier` enumerates exactly **3** tiers per §4.3 verbatim: Required (Stable), Recommended (Development), Opt-In content.
4. `BASE_LAYER_ATTRIBUTES` enumerates the OTel GenAI semconv 1.41.0 base set per §4.3 with per-attribute tier classification matching the §4.3 table verbatim:
   - **Required (Stable):** `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`
   - **Recommended (Development):** `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`, `server.address`, `server.port`, `gen_ai.conversation.id`
   - **Opt-In content:** `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`, `gen_ai.retrieval.documents`, `gen_ai.retrieval.query.text`
5. Parent-child trace context propagation per §4.4: child spans inherit `trace_id` from parent; `span_id` is unique per span; parent span ID is referenced via `parent_span_id` per OTel spec.
6. `BASE_METRIC_NAME == "gen_ai.client.operation.duration"` per §4.5 verbatim — the canonical base metric (histogram) with cardinality control per C-OD-11.
7. Base-layer attributes are the substrate over which OD specialization-layer namespaces (C-OD-05) compose; specialization namespaces add attributes but do NOT replace base-layer attributes.
8. Conformance to OTel GenAI semconv 1.41.0 is verifiable at runtime via OTel semantic convention validator.

**Tests (v2.5 — conformed to §4):** `test_span_name_format_byte_exact_three_component`, `test_genai_operation_cardinality_seven`, `test_genai_operation_includes_generate_content`, `test_attribute_tier_cardinality_three`, `test_base_layer_attributes_byte_exact_per_semconv_1_41_0`, `test_required_stable_tier_attributes_per_§4_3`, `test_recommended_development_tier_attributes_per_§4_3`, `test_opt_in_content_tier_attributes_per_§4_3`, `test_parent_span_id_propagation`, `test_trace_id_inherited_from_parent`, `test_base_metric_name_byte_exact_operation_duration`, `test_specialization_layer_does_not_replace_base_layer`, `test_otel_semconv_validator_passes`, `test_attribute_serialization_round_trip`, `test_span_name_resolves_at_span_emission_time`.

**Rollback boundary:** Revert OTel GenAI semconv 1.41.0 base-layer attribute declaration. R-OD-02 satisfaction loses base-layer substrate; downstream 8 direct dependents (U-OD-05 / U-OD-06 / U-OD-07 / U-OD-08 / U-OD-11 / U-OD-18 / U-OD-21 / U-OD-23) lose attribute-name foundation; span emission across the OD axis loses OTel semconv 1.41.0 conformance anchor. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 divergent state (2-component span name; 6-operation enum; 4-tier `AttributeTier`; `gen_ai.client.token.usage` base metric) — i.e., the Tension 004 verbatim-divergence defect; the revert MUST NOT be performed absent a §4A re-disposition.

---

### §3.3.1 U-OD-09 — Declare `harness.breaker.*` 7-attribute canonical schema (substrate-anchored-outside-CP) (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `BreakerScope` enum + acc #3 conformed to OD spec v1.2 §7.1. **acc #2 (Required/Conditional tier split) is NOT conformed — carried per §0.6 FF-1 / §0.7; acc #2 prose, the `tier:` annotations in `HARNESS_BREAKER_ATTRIBUTES`, and the `test_required_tier_*` / `test_conditional_tier_*` tests are preserved verbatim from v2.1 §3.3.1.** acc #1/#4–#9, `HARNESS_BREAKER_ATTRIBUTES`, `BreakerState`, `HarnessBreakerEvent`, `emit_breaker_trip_span_event`, Persona linkage, substrate-anchored rationale, rollback boundary preserved verbatim from v2.1 §3.3.1.]

**Implements:** [C-OD-07 §7.1, §7.2, §7.3]

**Depends on:** [U-OD-07]

**Inputs:** OD spec v1.2 §7.1 seven-attribute canonical schema (`harness.breaker.scope ∈ {per_model, per_provider}`); §7.2 quality-of-emission invariants; §7.3 C9↔C10 subscription contract reference.

**Files affected:** `harness.breaker.*` substrate-anchored canonical schema declaration (logical name: `od-harness-breaker-canonical-schema`).

**Substrate-anchored-outside-CP rationale.** [Preserved verbatim from v2.1 §3.3.1.] Per F-CP-01 Stage 3b alignment, the `harness.breaker.*` namespace is **substrate-anchored at the OD axis** rather than the CP axis. The CP-side `breaker.*` set is replaced under F-CP-01 alignment by this OD-canonical 7-attribute schema. The OD plan exports `harness.breaker.*` to the CP plan as a **CP-consuming** seam (per OD plan U-OD-09 → CP plan U-CP-54 §24.1.C cross-axis edge). This is the **OD → CP exporter** direction.

**Persona linkage.** Persona §4 (99.9% SLO; breaker-trip event is reliability-critical signal); §10.2 (compliance-readiness — breaker-trip events always-sampled at multi-tenant cells for tamper-evident audit ledger composition).

**Signatures (v2.5 — `BreakerScope` conformed to §7.1; all else preserved verbatim from v2.1):**

```
const HARNESS_BREAKER_ATTRIBUTES : List<GenAiAttribute> = [
  {name: "harness.breaker.scope",                  tier: REQUIRED},
  {name: "harness.breaker.from_state",             tier: REQUIRED},
  {name: "harness.breaker.to_state",               tier: REQUIRED},
  {name: "harness.breaker.trigger_count",          tier: REQUIRED},
  {name: "harness.breaker.permanent_fail_repeats", tier: CONDITIONAL},
  {name: "harness.breaker.tool_id",                tier: CONDITIONAL},
  {name: "harness.breaker.model_version",          tier: CONDITIONAL}
]                                                  // exactly 7 attributes
// NOTE [v2.5 FF-1]: the REQUIRED/CONDITIONAL tier annotations above are
// preserved verbatim from v2.1 and are NOT conformed at v2.5 — OD spec §7.1
// declares no tier classification for harness.breaker.* attributes. Carried
// for operator disposition per §0.6 FF-1 / §0.7.

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

**Acceptance criteria (v2.5 — acc #3 conformed to §7.1; acc #2 carried unchanged per §0.6 FF-1; #1/#4–#9 preserved verbatim from v2.1):**

1. `HARNESS_BREAKER_ATTRIBUTES` declares exactly **7** attributes per §7.1 verbatim.
2. **[carried — pending operator decision per §4A.7 / §0.6 FF-1; NOT conformed at v2.5]** Required vs Conditional tier classification per §7.1: 4 Required (scope / from_state / to_state / trigger_count); 3 Conditional (permanent_fail_repeats / tool_id / model_version). *FF-1 note: OD spec §7.1 declares no tier classification; this acceptance criterion has no spec basis and is a §2.7.6 Class 1 fork of design-gap shape carried for operator disposition. It is preserved verbatim from v2.1 and not conformed.*
3. `BreakerScope` enumerates exactly **2** values per §7.1 verbatim: `per_model`, `per_provider` (`harness.breaker.scope` ∈ `{per_model, per_provider}` per the §7.1 seven-attribute schema table, reconfirmed at §11.2 line `harness.breaker.scope | 2`).
4. `BreakerState` enumerates exactly 3 values (CLOSED / HALF_OPEN / OPEN) per §7.1 `from_state` / `to_state` ∈ `{closed, open, half_open}`.
5. Quality-of-emission invariants per §7.2: breaker-trip events are always-sampled at all cells (composes with U-OD-11 always-sampled set); attributes are cardinality-safe (no payload content; per-attribute cardinality bounded by `BreakerScope` enum × `BreakerState` enum × bounded integers).
6. C9↔C10 subscription contract per §7.3: breaker-trip events emitted at C9 reliability primitive ownership are subscribed by C10 action-safety gate as gating signal; this is a runtime cross-voice subscription, not a compile-time link.
7. Substrate-anchored-outside-CP per F-CP-01 Stage 3b: the OD axis owns the canonical schema; the CP plan's `breaker.*` set is replaced by this OD-canonical 7-attribute schema at C-CP-24 §24.1.C ingestion.
8. Cross-axis export per OD-S4-3.A: this unit is an **OD → CP exporter**; edge target = U-CP-54 (CP plan substrate seam exports manifest); contract anchor = C-CP-24 §24.1.C.
9. `emit_breaker_trip_span_event` emits the event at the parent span with all 7 attributes; returns `Err(BreakerEmissionError)` if Required attributes are missing.

**Tests (v2.5 — `test_breaker_scope_*` conformed to §7.1; `test_required_tier_*` / `test_conditional_tier_*` preserved verbatim per FF-1):** `test_harness_breaker_attributes_cardinality_seven`, `test_harness_breaker_attribute_names_byte_exact`, `test_required_tier_attributes_count_four` *(FF-1 carried — not conformed)*, `test_conditional_tier_attributes_count_three` *(FF-1 carried — not conformed)*, `test_breaker_scope_cardinality_two`, `test_breaker_scope_names_per_model_per_provider`, `test_breaker_state_cardinality_three`, `test_emit_breaker_trip_with_all_required_attrs_accept`, `test_emit_breaker_trip_missing_required_attr_reject`, `test_breaker_event_always_sampled_at_all_cells`, `test_breaker_attributes_cardinality_safe`, `test_cross_axis_export_to_u_cp_54_section_24_1_c_declared`, `test_substrate_anchored_outside_cp_per_f_cp_01_stage_3b`.

**Rollback boundary:** Revert `harness.breaker.*` substrate-anchored canonical schema. R-OD-02 + R-OD-03 satisfaction loses breaker-trip event schema; F-CP-01 Stage 3b alignment loses OD-axis substrate; CP plan U-CP-54 §24.1.C ingestion loses `harness.breaker.*` substrate-anchored-outside-CP reference; C9↔C10 subscription contract loses event substrate. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 4-value `BreakerScope` enum (the audited divergent state); the revert MUST NOT be performed absent a §4A re-disposition. The v2.5 pass did NOT touch acc #2's tier split (FF-1 carried).

---

### §3.4.1 U-OD-11 — Declare per-deployment-surface sampling mode + 18-entry always-sampled exception set (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `ALWAYS_SAMPLED_EVENT_CLASSES` member set + acc #3 conformed to OD spec v1.2 §9.2. Cardinality 18 was already correct; the member set is conformed. `SamplingMode`, `PER_DEPLOYMENT_SURFACE_SAMPLING`, `sampling_decision`, acc #1/#2/#4–#7, Persona linkage, rollback boundary preserved verbatim from v2.1 §3.4.1.]

**Implements:** [C-OD-09 §9.1, §9.2, §9.3]

**Depends on:** [U-OD-04, U-OD-05, U-OD-06, U-OD-09]

**Inputs:** OD spec v1.2 §9.1 per-deployment-surface sampling mode; §9.2 always-sampled exception set (**18 entries** — the §9.2 table); §9.3 sampling-discipline invariants.

**Files affected:** Sampling mode + always-sampled set (logical name: `od-sampling-mode-and-always-sampled-set`).

**Persona linkage.** Persona §6 (per-class cost ceiling — sampling efficiency at base-rate cells); §10.4 (compliance-readiness — always-sampled audit events).

**Signatures (v2.5 — `ALWAYS_SAMPLED_EVENT_CLASSES` member set conformed to §9.2):**

```
enum SamplingMode {
  HEAD_BASED_DEV,                      // local-development cells; head=1.0
  TAIL_BASED_PROD                      // self-hosted-server + managed-cloud cells
}

record PerDeploymentSurfaceSamplingMode {
  deployment_surface : DeploymentSurface
  sampling_mode      : SamplingMode
}

const PER_DEPLOYMENT_SURFACE_SAMPLING : Map<DeploymentSurface, SamplingMode> = {
  LOCAL_DEVELOPMENT     : HEAD_BASED_DEV,
  SELF_HOSTED_SERVER    : TAIL_BASED_PROD,
  MANAGED_CLOUD         : TAIL_BASED_PROD
}

// §9.2 verbatim — always-sampled exception set (head=1.0 across all cells).
// Member set conformed to the §9.2 table (18 rows).
const ALWAYS_SAMPLED_EVENT_CLASSES : Set<string> = {
  "sandbox.violation",
  "sandbox.tier_escalation",
  "hitl.gate.evaluated",
  "hitl.invocation.opened",
  "hitl.invocation.responded",
  "hitl.invocation.timed_out",
  "fallback.triggered",
  "breaker.tripped",
  "topology.fanout.opened",
  "topology.fanout.closed",
  "subagent.span",                                 // §9.2 row "subagent.span (root)"
  "mcp.tool.call",
  "audit.*",                                       // §9.2 row "audit.* (any event with audit.signature.* attributes)"
  "files.operation",                               // §9.2 row "files.operation at kind ∈ {upload, delete}"
  "memory.operation",                              // §9.2 row "memory.operation at kind ∈ {write, update, delete}"
  "validator.fail.*",                              // §9.2 row "validator.fail.* at validator.fail.permanence=permanent"
  "managed_agents.runtime",
  "skill.activation"
}                                                  // exactly 18 entries per §9.2

fn sampling_decision(
  cell_id : CellID,
  event_class : string,
  base_rate : float
) -> SamplingDecision
```

**Acceptance criteria (v2.5 — acc #3 conformed to §9.2; #1/#2/#4–#7 preserved verbatim from v2.1):**

1. `SamplingMode` enumerates exactly 2 values per §9.1.
2. `PER_DEPLOYMENT_SURFACE_SAMPLING` matches §9.1 row mapping verbatim.
3. `ALWAYS_SAMPLED_EVENT_CLASSES` has cardinality **18** per §9.2 verbatim, with member set conformed to the §9.2 table: `sandbox.violation`, `sandbox.tier_escalation`, `hitl.gate.evaluated`, `hitl.invocation.opened`, `hitl.invocation.responded`, `hitl.invocation.timed_out`, `fallback.triggered`, `breaker.tripped`, `topology.fanout.opened`, `topology.fanout.closed`, `subagent.span` (root), `mcp.tool.call`, `audit.*` (any event with `audit.signature.*` attributes), `files.operation` (`kind ∈ {upload, delete}`), `memory.operation` (`kind ∈ {write, update, delete}`), `validator.fail.*` (`validator.fail.permanence=permanent`), `managed_agents.runtime`, `skill.activation`.
4. Always-sampled set is independent of base-rate sampling: any event in the set samples at head=1.0 regardless of cell base-rate.
5. Sampling-discipline invariants per §9.3: always-sampled set is preserved across all 8 bridging-arc transitions (destination set ⊇ source set per U-OD-32 §22.3 verification dimension).
6. `sampling_decision` returns `SAMPLE_ALWAYS` for any event in `ALWAYS_SAMPLED_EVENT_CLASSES` regardless of `base_rate`; returns `SAMPLE_AT_BASE_RATE` otherwise.
7. Audit-ledger entries at multi-tenant cells are always-sampled per C-OD-21 composition; the `audit.*` event class entry covers this composition.

**Tests (v2.5 — member-set tests conformed to §9.2):** `test_sampling_mode_cardinality_two`, `test_per_surface_sampling_local_head_based`, `test_per_surface_sampling_self_hosted_tail_based`, `test_per_surface_sampling_managed_cloud_tail_based`, `test_always_sampled_event_classes_cardinality_eighteen`, `test_always_sampled_event_class_members_byte_exact_per_§9_2`, `test_sampling_decision_always_sampled_event`, `test_sampling_decision_base_rate_event_below_threshold`, `test_always_sampled_preserved_across_bridging_arc_transitions`, `test_audit_glob_in_always_sampled_set`, `test_breaker_tripped_in_always_sampled_set`.

**Rollback boundary:** Revert sampling mode + always-sampled set. R-OD-03 satisfaction loses sampling discipline; downstream U-OD-12 base-rate set composition loses always-sampled-exception complement; U-OD-25 drift detection event composition loses always-sampled membership reference; bridging-arc transition verification at U-OD-32 loses sampling-tightening invariant substrate. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 divergent member set; the revert MUST NOT be performed absent a §4A re-disposition.

---

### §3.4.2 U-OD-12 — Declare 13-entry base-rate-sampled set + per-cell tuning envelope (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `BASE_RATE_SAMPLED_EVENT_CLASSES` member set + acc #1 conformed to OD spec v1.2 §10.1. Cardinality 13 was already correct; the member set is conformed. `PerCellBaseRateEnvelope`, `PER_CELL_BASE_RATE_ENVELOPE`, `TailKeepRule`, `TAIL_KEEP_RULES`, acc #2–#6, rollback boundary preserved verbatim from v2.1 §3.4.2.]

**Implements:** [C-OD-10 §10.1, §10.2, §10.3]

**Depends on:** [U-OD-01, U-OD-11]

**Inputs:** OD spec v1.2 §10.1 base-rate-sampled set (**13 entries** — the §10.1 table); §10.2 tail-keep-on-classification; §10.3 per-cell base-rate tuning envelope.

**Files affected:** Base-rate set + per-cell tuning envelope (logical name: `od-base-rate-set-and-envelope`).

**Signatures (v2.5 — `BASE_RATE_SAMPLED_EVENT_CLASSES` member set conformed to §10.1):**

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
  default_rate      : float                        // operator-tunable per §10.3
  min_rate          : float                        // envelope floor
  max_rate          : float                        // envelope ceiling
}

const PER_CELL_BASE_RATE_ENVELOPE : Map<CellID, PerCellBaseRateEnvelope>   // exactly 8 entries

record TailKeepRule {
  classification_attribute : string
  keep_decision            : "ALWAYS_KEEP"
}

const TAIL_KEEP_RULES : List<TailKeepRule>
```

**Acceptance criteria (v2.5 — acc #1 conformed to §10.1; #2–#6 preserved verbatim from v2.1):**

1. `BASE_RATE_SAMPLED_EVENT_CLASSES` has cardinality **13** per §10.1 verbatim, with member set conformed to the §10.1 table: `chat` (`gen_ai.operation.name=chat`), `execute_tool`, `sandbox.enter`, `sandbox.exit`, `tool.call` (non-MCP tool calls only), `retrieval` (`gen_ai.operation.name=retrieval`), cache events (cache hit / cache miss / cache creation), `embeddings`, `text_completion`, `files.operation` (`kind ∈ {list, metadata, reference}` — non-mutation), `memory.operation` (`kind ∈ {read, list}` — non-mutation), `lease.acquired` / `lease.released`, `retry.attempt` at 1st attempt.
2. `BASE_RATE_SAMPLED_EVENT_CLASSES ∩ ALWAYS_SAMPLED_EVENT_CLASSES == ∅` — sets are disjoint (event class belongs to exactly one regime).
3. `PER_CELL_BASE_RATE_ENVELOPE` has cardinality **8** — one per ACTIVE cell. Per §10.3 envelope:
   - solo-developer × * → default 1.0 (everything sampled at design-time)
   - team-binding × * → default 0.05–0.5 (typical envelope)
   - multi-tenant-compliance × * → default 0.1–0.5 (compliance + cost balance)
4. `min_rate <= default_rate <= max_rate` per cell — envelope invariant.
5. Per §10.3 envelope tightening invariant across bridging-arc transitions (composition with U-OD-32 §22.3 sampling-discipline tightening dimension): `target_cell.max_rate <= source_cell.max_rate` along persona-tier axis at fixed deployment surface.
6. `TAIL_KEEP_RULES` declares the tail-keep-on-classification post-classification keep decisions per §10.2: failed traces (validator.fail.permanent / sandbox violations / breaker trips) ALWAYS_KEEP at tail-based-prod cells regardless of base-rate.

**Tests (v2.5 — member-set tests conformed to §10.1):** `test_base_rate_set_cardinality_thirteen`, `test_base_rate_event_members_byte_exact_per_§10_1`, `test_base_rate_and_always_sampled_disjoint`, `test_per_cell_envelope_cardinality_eight`, `test_envelope_invariant_min_default_max`, `test_solo_cells_default_rate_one_point_zero`, `test_team_cells_default_rate_in_envelope`, `test_multi_tenant_cells_default_rate_in_envelope`, `test_envelope_tightening_across_bridging_arc`, `test_tail_keep_rules_apply_post_classification`.

**Rollback boundary:** Revert base-rate set + per-cell envelope. R-OD-03 satisfaction loses base-rate discipline; downstream U-OD-22 alerting threshold scaling loses base-rate-scaling factor (`1.0 / base_rate`); bridging-arc transition verification loses base-rate-envelope-tightening substrate. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 divergent member set; the revert MUST NOT be performed absent a §4A re-disposition.

---

### §3.4.4 U-OD-14 — Declare cardinality-safe and cardinality-prohibited attribute classes (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `CARDINALITY_SAFE_ATTRIBUTES` and `CARDINALITY_PROHIBITED_ATTRIBUTES` member sets + acc #1 + #2 conformed to OD spec v1.2 §11.2 / §11.3. Both cardinalities (13 / 6) were already correct; both member sets are conformed. `assert_*` function signatures, acc #3–#7, rollback boundary preserved verbatim from v2.1 §3.4.4.]

**Implements:** [C-OD-11 §11.2, §11.3]

**Depends on:** [U-OD-05, U-OD-13]

**Inputs:** OD spec v1.2 §11.2 cardinality-safe attribute set (the §11.2 table — 12 rows enumerating 13 attribute names; `harness.breaker.from_state` / `to_state` are one row covering two attribute names); §11.3 cardinality-prohibited attribute set (the §11.3 table — 6 rows).

**Files affected:** Attribute-class enforcement (logical name: `od-attribute-class-enforcement`).

**Signatures (v2.5 — both member sets conformed to §11.2 / §11.3):**

```
// §11.2 verbatim — cardinality-safe attributes (admissible as metric
// dimensions). The §11.2 table has 12 rows; the harness.breaker.from_state /
// to_state row covers two attribute names — 13 attribute names total.
const CARDINALITY_SAFE_ATTRIBUTES : Set<string> = {
  "gen_ai.operation.name",
  "gen_ai.provider.name",
  "gen_ai.request.model",
  "gen_ai.response.finish_reasons",
  "sandbox.tier",
  "sandbox.tech",
  "sandbox.provider",
  "hitl.gate.level",
  "hitl.response.class",
  "harness.breaker.scope",
  "harness.breaker.from_state",
  "harness.breaker.to_state",
  "validator.fail.class"
}                                                  // exactly 13 entries per §11.2

// §11.3 verbatim — cardinality-prohibited attributes (span-only; NEVER
// metric dimensions). The §11.3 table has 6 rows.
const CARDINALITY_PROHIBITED_ATTRIBUTES : Set<string> = {
  "gen_ai.conversation.id",
  "session_user_tenant_ids",                       // §11.3 row "Session IDs, user IDs, tenant IDs"
  "idempotency_key",
  "mcp.primitive.signature.sha256",
  "skill.version_sha",
  "audit.signature.sha256_or_prior_hash"           // §11.3 row "audit.signature.sha256 / audit.signature.prior_hash"
}                                                  // exactly 6 entries per §11.3

fn assert_cardinality_safe_for_dashboard_dimension(attr : string) -> Result<(), CardinalityViolation>
fn assert_cardinality_prohibited_not_in_dashboard_dimension(attr : string) -> Result<(), CardinalityViolation>
```

**Acceptance criteria (v2.5 — acc #1 + #2 conformed to §11.2 / §11.3; #3–#7 preserved verbatim from v2.1):**

1. `CARDINALITY_SAFE_ATTRIBUTES` has cardinality **13** per §11.2 verbatim, with member set conformed to the §11.2 table (12 rows; `harness.breaker.from_state` / `to_state` is one row covering two attribute names): `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.finish_reasons`, `sandbox.tier`, `sandbox.tech`, `sandbox.provider`, `hitl.gate.level`, `hitl.response.class`, `harness.breaker.scope`, `harness.breaker.from_state`, `harness.breaker.to_state`, `validator.fail.class`.
2. `CARDINALITY_PROHIBITED_ATTRIBUTES` has cardinality **6** per §11.3 verbatim, with member set conformed to the §11.3 table: `gen_ai.conversation.id`, "Session IDs, user IDs, tenant IDs" (one §11.3 row), `idempotency_key`, `mcp.primitive.signature.sha256`, `skill.version_sha`, "`audit.signature.sha256` / `audit.signature.prior_hash`" (one §11.3 row).
3. Sets are disjoint: `CARDINALITY_SAFE_ATTRIBUTES ∩ CARDINALITY_PROHIBITED_ATTRIBUTES == ∅`.
4. Cardinality-prohibited attributes MAY appear as span attributes for trace-level join keys but MUST NOT appear as dashboard query dimensions (high-cardinality dashboard queries cause cardinality blowup).
5. `assert_cardinality_safe_for_dashboard_dimension` returns `Err(CardinalityViolation)` for any attribute not in `CARDINALITY_SAFE_ATTRIBUTES` when used as a dashboard dimension.
6. `assert_cardinality_prohibited_not_in_dashboard_dimension` returns `Err(CardinalityViolation)` for any attribute in `CARDINALITY_PROHIBITED_ATTRIBUTES` when used as a dashboard dimension.
7. Enforcement is at dashboard-query-construction time per cell's committed backend.

**Tests (v2.5 — member-set tests conformed to §11.2 / §11.3):** `test_cardinality_safe_cardinality_thirteen`, `test_cardinality_safe_members_byte_exact_per_§11_2`, `test_cardinality_prohibited_cardinality_six`, `test_cardinality_prohibited_members_byte_exact_per_§11_3`, `test_attribute_sets_disjoint`, `test_safe_attribute_accepted_as_dashboard_dim`, `test_prohibited_attribute_rejected_as_dashboard_dim`, `test_unknown_attribute_rejected_as_dashboard_dim`.

**Rollback boundary:** Revert cardinality-safe + cardinality-prohibited attribute classes. R-OD-03 satisfaction loses attribute-class enforcement; downstream U-OD-22 dashboard binding loses cardinality-safe attribute filter; cardinality blowup risk returns at high-cardinality dashboard queries. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 divergent member sets; the revert MUST NOT be performed absent a §4A re-disposition.

---

### §3.7.4 U-OD-30 — Declare per-tenant trace separation + cryptographic audit ledger composition (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `SignatureAlgorithm` enum + acc #6 conformed to OD spec v1.2 §21.2 (`audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}`; chain-unanimous with ADR-D5 §1.4.1 per §4A.5 tiebreaker). All other surfaces (`TenantSeparationStrategy`, `PerTenantSeparation`, `PER_TENANT_SEPARATION_BINDINGS`, `AuditSignatureAttributes`, the three function signatures, acc #1–#5, #7–#14, Cross-axis dependency resolution, Persona linkage, rollback boundary) preserved verbatim from v2.1 §3.7.4.]

**Implements:** [C-OD-21 §21.1, §21.2, §21.3]

**Depends on:** [U-OD-01, U-OD-02, U-OD-28, U-IS-NN (cross-axis: IS — C-IS-14 §14.2), U-IS-NN (cross-axis: IS — C-IS-13 §13.5), U-CP-NN (cross-axis: CP — C-CP-20 §20.4)]

**Inputs:** OD spec v1.2 §21.1 per-tenant trace separation; §21.2 cryptographic audit ledger composition (4 `audit.signature.*` attributes + 3 admissible signature algorithms — `audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}` per §21.2 / ADR-D5 v1.3 §1.4.1); §21.3 multi-tenant cell composition (cells 7, 8 only).

**Cross-axis dependency resolution.** [Preserved verbatim from v2.1 §3.7.4.] IS plan U-IS-NN implementing C-IS-14 §14.2; IS plan U-IS-NN implementing C-IS-13 §13.5; CP plan U-CP-NN implementing C-CP-20 §20.4. Resolution at U-OD-34.

**Files affected:** Per-tenant trace separation + cryptographic audit ledger (logical name: `od-multi-tenant-trace-separation-and-audit-ledger`).

**Persona linkage.** Persona §10.4 (compliance-readiness foundational primitives — per-tenant isolation + cryptographic audit attestation).

**Signatures (v2.5 — `SignatureAlgorithm` conformed to §21.2; all else preserved verbatim from v2.1):**

```
enum TenantSeparationStrategy {
  PER_TENANT_OTLP_COLLECTOR_ROUTING,
  PER_TENANT_BACKEND_PARTITION
}

record PerTenantSeparation {
  cell_id              : CellID                    // ∈ {cell-7, cell-8}
  strategy             : TenantSeparationStrategy
  tenant_id_attribute  : "tenant.id"
  cross_tenant_aggregation_forbidden : bool        // = true
}

const PER_TENANT_SEPARATION_BINDINGS : Map<CellID, PerTenantSeparation>   // exactly 2 entries (cells 7, 8)

// §21.2 verbatim — audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}
// (Ed25519 default; operator-tunable audit_signature_algorithm axis).
// Chain-unanimous with ADR-D5 v1.3 §1.4.1 per §4A.5 tiebreaker.
enum SignatureAlgorithm {
  ED25519,
  ECDSA_P256,
  RSA_PSS_2048
}                                                  // exactly 3 values per §21.2

record AuditSignatureAttributes {
  audit_signature_value      : string              // audit.signature.value
  audit_signature_algorithm  : SignatureAlgorithm  // audit.signature.algorithm
  audit_signature_key_id     : string              // audit.signature.key_id
  audit_signature_key_period : string              // audit.signature.key_period
}

const AUDIT_SIGNATURE_REQUIRED_AT_TIER_5_LEDGER : bool = true   // §21.2 + C-IS-14 §14.2

fn sign_audit_entry(payload : AuditPayload, key_id : string, algo : SignatureAlgorithm) -> AuditSignatureAttributes
fn verify_hash_chain_integrity(ledger : AuditLedger) -> Result<(), HashChainBreach>
fn assert_tenant_id_on_every_span_at_multi_tenant_cells(span : SpanRef, cell_id : CellID) -> Result<(), TenantIdMissingViolation>
```

**Acceptance criteria (v2.5 — acc #6 conformed to §21.2; #1–#5, #7–#14 preserved verbatim from v2.1):**

1. `TenantSeparationStrategy` enumerates exactly 2 values per §21.1 verbatim.
2. `PER_TENANT_SEPARATION_BINDINGS` declares exactly **2** entries — cell-7 and cell-8 only.
3. cell-7 → `PER_TENANT_OTLP_COLLECTOR_ROUTING` (self-hosted variant); cell-8 → `PER_TENANT_BACKEND_PARTITION` (managed-cloud variant) OR `PER_TENANT_OTLP_COLLECTOR_ROUTING` (deployment-binding alternation permitted per §21.1).
4. `tenant_id_attribute == "tenant.id"` byte-exact per §21.1.
5. `cross_tenant_aggregation_forbidden == true` per §21.1 + C-OD-21 §21.4 — composes with U-OD-31 enforcement.
6. `SignatureAlgorithm` enumerates exactly **3** values per §21.2 verbatim: `ed25519`, `ecdsa-p256`, `rsa-pss-2048` (`audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}`; Ed25519 default; operator-tunable `audit_signature_algorithm` axis per §21.2 / ADR-D5 v1.3 §1.4.1).
7. `AuditSignatureAttributes` declares exactly **4** attributes per §21.2 verbatim with byte-exact attribute names (`audit.signature.value` / `audit.signature.algorithm` / `audit.signature.key_id` / `audit.signature.key_period`).
8. `sign_audit_entry` produces `AuditSignatureAttributes` with all 4 fields populated per `algo` selection; missing `key_id` rejected at function precondition.
9. `verify_hash_chain_integrity` returns `Err(HashChainBreach)` if any entry's hash chain link is broken — composes with C-IS-13 §13.5 hash-chain integrity primitive.
10. `assert_tenant_id_on_every_span_at_multi_tenant_cells` returns `Err(TenantIdMissingViolation)` if a span at cell-7 or cell-8 lacks `tenant.id` attribute.
11. Audit ledger always-sampled at multi-tenant cells per U-OD-11 always-sampled set entry `audit.*`.
12. Cross-axis edges per OD-S4-3.A: edge targets `U-IS-NN` (C-IS-14 §14.2, C-IS-13 §13.5), `U-CP-NN` (C-CP-20 §20.4).
13. Specific signature algorithm selection deferred per §21.2 "Deferred to implementation discretion" — operators select within the 3-algorithm admissible set at deployment-binding time.
14. Key management deferred per ADR-D5 v1.3 §1.4.1 + §21.2 — OS keychain or HSM binding at deployment-binding time.

**Tests (v2.5 — `test_signature_algorithm_*` conformed to §21.2):** `test_tenant_separation_strategy_cardinality_two`, `test_per_tenant_separation_only_at_multi_tenant_cells`, `test_cell_7_self_hosted_strategy`, `test_cell_8_managed_cloud_strategy_options`, `test_tenant_id_attribute_byte_exact`, `test_cross_tenant_aggregation_forbidden`, `test_signature_algorithm_cardinality_three`, `test_signature_algorithm_names_byte_exact_ed25519_ecdsa_p256_rsa_pss_2048`, `test_audit_signature_attributes_cardinality_four`, `test_audit_signature_attribute_names_byte_exact`, `test_sign_audit_entry_complete`, `test_sign_audit_entry_missing_key_id_reject`, `test_verify_hash_chain_intact_accept`, `test_verify_hash_chain_broken_reject`, `test_assert_tenant_id_present_accept`, `test_assert_tenant_id_missing_reject_at_cell_7`, `test_assert_tenant_id_missing_reject_at_cell_8`, `test_audit_ledger_always_sampled`, `test_cross_axis_edge_to_u_is_nn_c_is_14_section_14_2`, `test_cross_axis_edge_to_u_is_nn_c_is_13_section_13_5`, `test_cross_axis_edge_to_u_cp_nn_c_cp_20_section_20_4`, `test_specific_algorithm_selection_deferred`.

**Rollback boundary:** Revert per-tenant trace separation + audit ledger composition. R-OD-04 + R-OD-08 satisfaction at multi-tenant cells loses tenant isolation + audit attestation; Persona §10.4 compliance-readiness foundational primitives lose runtime substrate; cross-axis IS Tier-5 audit ledger durability loses OD-side observability composition; cross-axis CP audit namespace 7-attribute schema loses OD-side signing-and-verification composition; U-OD-31 multi-tenant aggregation prohibition loses tenant-id-substrate foundation. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 `SignatureAlgorithm` 3rd value `HMAC_SHA256` (contradicted by both OD spec §21.2 and ADR-D5 §1.4.1 per the §4A.5 tiebreaker); the revert MUST NOT be performed absent a §4A re-disposition.

---

### §3.8.1 U-OD-32 — Declare 8-transition bridging-arc table + per-transition verification surface (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `BRIDGING_ARC_TRANSITIONS` member set + acc #1 conformed to OD spec v1.2 §22.1. Cardinality 8 was already correct; the transition set is conformed (5 within-column + 3 diagonal per §22.1). `BridgingArcTransition`, `TransitionAxis`, `VerificationDimension`, `verify_transition`, `reject_excluded_transition`, acc #2–#9, Persona linkage, rollback boundary preserved verbatim from v2.1 §3.8.1.]

**Implements:** [C-OD-22 §22.1, §22.3]

**Depends on:** [U-OD-01, U-OD-11, U-OD-12, U-OD-15, U-OD-16, U-OD-17]

**Inputs:** OD spec v1.2 §22.1 eight bridging-arc transitions in scope (**5 within-column + 3 diagonal**; multi-tenant × local-development cell EXCLUDED per C-OD-01 §1.4); §22.3 per-transition verification surface.

**Files affected:** Bridging-arc 8-transition table + per-transition verification surface (logical name: `od-bridging-arc-8-transition-table`).

**Persona linkage.** Persona §2 (bridging-arc traversal across persona-tier × deployment-surface matrix); §9 (deployment-surface progression).

**Signatures (v2.5 — `BRIDGING_ARC_TRANSITIONS` member set conformed to §22.1):**

```
record BridgingArcTransition {
  transition_id          : int                     // 1..8
  source_cell            : CellID
  target_cell            : CellID
  transition_type        : TransitionType
}

// §22.1 — transitions are typed within-column or diagonal.
enum TransitionType {
  WITHIN_COLUMN,
  DIAGONAL
}

// §22.1 verbatim — eight in-scope bridging-arc transitions (5 within-column +
// 3 diagonal), per Integration_Verification_Report.md §5.1. Member set
// conformed to the §22.1 table.
const BRIDGING_ARC_TRANSITIONS : List<BridgingArcTransition> = [
  {1, (SOLO_DEVELOPER, LOCAL_DEVELOPMENT),  (TEAM_BINDING, LOCAL_DEVELOPMENT),            WITHIN_COLUMN},
  {2, (SOLO_DEVELOPER, SELF_HOSTED_SERVER), (TEAM_BINDING, SELF_HOSTED_SERVER),           WITHIN_COLUMN},
  {3, (TEAM_BINDING, SELF_HOSTED_SERVER),   (MULTI_TENANT_COMPLIANCE, SELF_HOSTED_SERVER), WITHIN_COLUMN},
  {4, (SOLO_DEVELOPER, MANAGED_CLOUD),      (TEAM_BINDING, MANAGED_CLOUD),                WITHIN_COLUMN},
  {5, (TEAM_BINDING, MANAGED_CLOUD),        (MULTI_TENANT_COMPLIANCE, MANAGED_CLOUD),     WITHIN_COLUMN},
  {6, (SOLO_DEVELOPER, LOCAL_DEVELOPMENT),  (TEAM_BINDING, SELF_HOSTED_SERVER),           DIAGONAL},
  {7, (TEAM_BINDING, LOCAL_DEVELOPMENT),    (MULTI_TENANT_COMPLIANCE, SELF_HOSTED_SERVER), DIAGONAL},
  {8, (TEAM_BINDING, SELF_HOSTED_SERVER),   (MULTI_TENANT_COMPLIANCE, MANAGED_CLOUD),     DIAGONAL}
]                                                  // exactly 8 transitions per §22.1

enum VerificationDimension {
  CELL_MATRIX_REACHABILITY,
  SAMPLING_DISCIPLINE_TIGHTENING,
  CARDINALITY_BUDGET_TIGHTENING,
  REDACTION_CLASS_MONOTONIC_TIGHTENING,
  ATTRIBUTE_DEFAULT_OFF_PRESERVATION,
  COLLECTOR_PLACEMENT_PROGRESSION
}                                                  // exactly 6 verification dimensions per §22.3

record TransitionVerificationResult {
  transition_id     : int
  dimension         : VerificationDimension
  outcome           : VerificationOutcome
  violation_detail  : Option<string>
}

enum VerificationOutcome { PASS, FAIL }

fn verify_transition(
  transition  : BridgingArcTransition,
  dimensions  : List<VerificationDimension>
) -> List<TransitionVerificationResult>

fn reject_excluded_transition(
  source : CellID,
  target : CellID
) -> Result<(), ExcludedTransitionViolation>
```

**Acceptance criteria (v2.5 — acc #1 + #2 conformed to §22.1; #3–#9 preserved verbatim from v2.1):**

1. `BRIDGING_ARC_TRANSITIONS` declares exactly **8** transitions per §22.1 verbatim, with transition set conformed to the §22.1 table (5 within-column + 3 diagonal):
   - **1** (within-column): solo-developer × local-development → team-binding × local-development
   - **2** (within-column): solo-developer × self-hosted-server → team-binding × self-hosted-server
   - **3** (within-column): team-binding × self-hosted-server → multi-tenant-compliance × self-hosted-server
   - **4** (within-column): solo-developer × managed-cloud → team-binding × managed-cloud
   - **5** (within-column): team-binding × managed-cloud → multi-tenant-compliance × managed-cloud
   - **6** (diagonal): solo-developer × local-development → team-binding × self-hosted-server
   - **7** (diagonal): team-binding × local-development → multi-tenant-compliance × self-hosted-server
   - **8** (diagonal): team-binding × self-hosted-server → multi-tenant-compliance × managed-cloud
2. `TransitionType` enumerates exactly 2 values per §22.1: within-column + diagonal (the §22.1 transition table classifies each transition under the "Type" column as `within-column` or `diagonal`).
3. Source and target cells for each transition are ACTIVE (per U-OD-01); EXCLUDED_CELL (multi-tenant-compliance × local-development) appears in neither source nor target of any transition.
4. `reject_excluded_transition` returns `Err(ExcludedTransitionViolation)` for any transition involving EXCLUDED_CELL.
5. `VerificationDimension` enumerates exactly **6** dimensions per §22.3 verbatim.
6. `verify_transition` returns per-dimension `TransitionVerificationResult` with `PASS` or `FAIL` outcome and violation detail when `FAIL`.
7. PASS condition per dimension:
   - `CELL_MATRIX_REACHABILITY`: both source and target ∈ ACTIVE_CELLS
   - `SAMPLING_DISCIPLINE_TIGHTENING`: target's always-sampled set ⊇ source's always-sampled set (set inclusion)
   - `CARDINALITY_BUDGET_TIGHTENING`: target's per-cell rate limit ≤ source's per-cell rate limit (where both defined)
   - `REDACTION_CLASS_MONOTONIC_TIGHTENING`: `class_index(target) >= class_index(source)` per U-OD-17
   - `ATTRIBUTE_DEFAULT_OFF_PRESERVATION`: target's default-off content set ⊇ source's default-off content set
   - `COLLECTOR_PLACEMENT_PROGRESSION`: target's placement class is the admissible successor per U-OD-28 row mapping
8. Verification is verifiable at design time over the 8-transition × 6-dimension matrix → 48 verification checks total.
9. Per §22.4 excluded-transition rejection: any transition targeting multi-tenant-compliance × local-development is structurally rejected (cell EXCLUDED per C-OD-01 §1.4); reverse transitions are out of bridging-arc traversal scope (forward-only per Persona §2).

**Tests (v2.5 — transition-set tests conformed to §22.1):** `test_bridging_arc_transitions_cardinality_eight`, `test_bridging_arc_transition_members_byte_exact_per_§22_1`, `test_transition_type_cardinality_two`, `test_five_within_column_three_diagonal`, `test_no_transition_involves_excluded_cell`, `test_reject_excluded_transition_returns_err`, `test_verification_dimension_cardinality_six`, `test_verify_transition_returns_six_results`, `test_pass_cell_matrix_reachability_both_active`, `test_pass_sampling_discipline_target_includes_source`, `test_pass_cardinality_budget_target_le_source`, `test_pass_redaction_class_target_ge_source`, `test_pass_attribute_default_off_target_includes_source`, `test_pass_collector_placement_progression_admissible`, `test_fail_sampling_target_missing_source_event_class`, `test_fail_redaction_class_target_lt_source`, `test_48_verification_checks_total`.

**Rollback boundary:** Revert 8-transition bridging-arc table + per-transition verification surface. R-OD-08 satisfaction loses bridging-arc traversal substrate; Persona §2 bridging-arc progression loses design-time verification surface; downstream U-OD-33 per-dimension preservation invariants lose transition-table foundation; cross-axis composition with AS sandbox-tier monotonic ascension + CP per-tool/per-MCP-server cross-deployment monotonicity loses OD-side transition substrate. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 divergent transition set (deployment-surface-ascent transitions not in §22.1; the 3 §22.1 diagonals omitted); the revert MUST NOT be performed absent a §4A re-disposition.

---

### §3.8.2 U-OD-33 — Compose per-dimension preservation invariants across cross-axis dimensions (v2.5 conformance revision)

[Full-revised at v2.5 per §0.4 — `PreservationDimension` member set + acc #1 + #2 conformed to OD spec v1.2 §22.2. Cardinality 5 was already correct; the dimension set is conformed. `PreservationInvariant`, `InvariantForm`, `EnforcementLayer`, `PRESERVATION_INVARIANTS`, the two function signatures, acc #3–#8, Cross-axis dependency resolution, rollback boundary preserved verbatim from v2.1 §3.8.2 — except where acc #2's per-dimension invariant-form / enforcement-layer rows are re-keyed to the conformed dimension names.]

**Implements:** [C-OD-22 §22.2, §22.4]

**Depends on:** [U-OD-05, U-OD-07, U-OD-11, U-OD-12, U-OD-17, U-OD-32, U-AS-NN (cross-axis: AS — C-AS-12 §12.1 D2 sandbox-tier monotonicity), U-AS-NN (cross-axis: AS — C-AS-15 §15.6 sandbox-overhead composition), U-AS-NN (cross-axis: AS — C-AS-12 §12.4 per-tier reachability), U-CP-NN (cross-axis: CP — C-CP-19 D5 cross-deployment monotonicity)]

**Inputs:** OD spec v1.2 §22.2 per-dimension preservation invariants (the §22.2 table — **5 observability dimensions**); §22.4 invariant composition with persona-tier-axis ascent and deployment-surface-axis ascent.

**Cross-axis dependency resolution.** [Preserved verbatim from v2.1 §3.8.2.] AS plan U-AS-NN implementing C-AS-12 §12.1; AS plan U-AS-NN implementing C-AS-15 §15.6; AS plan U-AS-NN implementing C-AS-12 §12.4; CP plan U-CP-NN implementing C-CP-19. Resolution at U-OD-34.

**Files affected:** Per-dimension preservation invariants (logical name: `od-per-dimension-preservation-invariants`).

**Signatures (v2.5 — `PreservationDimension` member set conformed to §22.2):**

```
// §22.2 verbatim — the five observability dimensions of the §22.2
// per-dimension preservation invariants table.
enum PreservationDimension {
  SPAN_SCHEMA_INGESTION_CONTRACT,        // §22.2 — 15 specialization-layer namespaces per C-OD-05 §5.1
  SAMPLING_DISCIPLINE,                   // §22.2 — always-sampled set + base-rate envelope
  REDACTION_DISCIPLINE,                  // §22.2 — strict monotonic tightening per C-OD-13 §13.3
  TRACE_STORAGE_TIER,                    // §22.2 — monotonic-or-tightened per C-OD-01 §1.3
  GATE_LEVEL_MULTIPLICATIVE_TUNABLE      // §22.2 — ADR-D5 §1.5.2 + ADR-D2 §1.6 cross-deployment monotonicity
}                                        // exactly 5 dimensions per §22.2

record PreservationInvariant {
  dimension                       : PreservationDimension
  invariant_form                  : InvariantForm
  enforcement_layer               : EnforcementLayer
  cross_axis_composition_target   : Option<string>
}

enum InvariantForm {
  SUPERSET_TARGET_INCLUDES_SOURCE,                 // span-schema ingestion, sampling always-sampled set
  SCALAR_MONOTONIC_TIGHTENING_LE,                  // base-rate envelope
  CLASS_INDEX_MONOTONIC_ASCENT_GE                  // redaction discipline, trace storage tier, gate level
}

enum EnforcementLayer {
  DESIGN_TIME_VERIFICATION,                        // U-OD-32 verify_transition
  RUNTIME_ENFORCEMENT_AT_COLLECTOR_BOUNDARY,
  CROSS_AXIS_COMPOSITION_VERIFICATION              // session 5 cross-axis matrix
}

const PRESERVATION_INVARIANTS : Map<PreservationDimension, PreservationInvariant>   // exactly 5 entries

fn verify_per_dimension_preservation(
  transition : BridgingArcTransition,
  dimension  : PreservationDimension
) -> Result<(), PreservationViolation>

fn assert_cross_axis_composition_verified_at_session_5(
  dimension : PreservationDimension
) -> Result<(), CrossAxisCompositionPending>
```

**Acceptance criteria (v2.5 — acc #1 + #2 conformed to §22.2; #3–#8 preserved verbatim from v2.1):**

1. `PreservationDimension` enumerates exactly **5** values per §22.2 verbatim, with dimension set conformed to the §22.2 table: `SPAN_SCHEMA_INGESTION_CONTRACT` (Span schema ingestion contract), `SAMPLING_DISCIPLINE` (Sampling discipline), `REDACTION_DISCIPLINE` (Redaction discipline), `TRACE_STORAGE_TIER` (Trace storage tier), `GATE_LEVEL_MULTIPLICATIVE_TUNABLE` (Gate-level multiplicative tunable).
2. `PRESERVATION_INVARIANTS` declares exactly 5 entries with per-dimension invariant form + enforcement layer per the §22.2 preservation-invariant table:
   - `SPAN_SCHEMA_INGESTION_CONTRACT`: `SUPERSET_TARGET_INCLUDES_SOURCE` (15 specialization-layer namespaces per C-OD-05 §5.1 stable across all 8 transitions; collector-placement changes do not drop namespace ingestion), `DESIGN_TIME_VERIFICATION`
   - `SAMPLING_DISCIPLINE`: `SUPERSET_TARGET_INCLUDES_SOURCE` for the always-sampled set + `SCALAR_MONOTONIC_TIGHTENING_LE` for the base-rate envelope (always-sampled set per C-OD-09 §9.2 preserved; base-rate set per C-OD-10 §10.1 tightens monotonically per C-OD-10 §10.3), `DESIGN_TIME_VERIFICATION`
   - `REDACTION_DISCIPLINE`: `CLASS_INDEX_MONOTONIC_ASCENT_GE` (strict monotonic tightening per C-OD-13 §13.3; downgrade structurally rejected), `DESIGN_TIME_VERIFICATION`
   - `TRACE_STORAGE_TIER`: `CLASS_INDEX_MONOTONIC_ASCENT_GE` (monotonic-or-tightened per C-OD-01 §1.3; downgrade structurally rejected), `DESIGN_TIME_VERIFICATION`
   - `GATE_LEVEL_MULTIPLICATIVE_TUNABLE`: `CLASS_INDEX_MONOTONIC_ASCENT_GE` (ADR-D5 v1.3 §1.5.2 + ADR-D2 v1.1 §1.6 cross-deployment monotonicity; the 5-axis multiplicative tunable per `Spec_Action_Surface_v1.md` C-AS-12 §12.1 composes at every cell), `CROSS_AXIS_COMPOSITION_VERIFICATION`, target `C-AS-12 §12.1` + `C-CP-19`
3. `verify_per_dimension_preservation` returns `Ok` when the transition preserves the dimension per its invariant form; `Err(PreservationViolation)` with violation detail otherwise.
4. Cross-axis composition verification per §22.4: the `GATE_LEVEL_MULTIPLICATIVE_TUNABLE` dimension requires cross-axis composition verification at the Session 5 cross-axis matrix; the OD plan commits the OD-side surface — verification of AS + CP composition is the Session 5 deliverable.
5. `assert_cross_axis_composition_verified_at_session_5` returns `Err(CrossAxisCompositionPending)` when called at OD plan scope — the verification is deferred to Session 5 per OD-S4-2.A.
6. Cross-axis edges per OD-S4-3.A: 4 edges (3 AS edges + 1 CP edge per §22.2 cross-axis composition references). Resolution at U-OD-34.
7. T-perm-1 5-axis multiplicative tunable composition: the `GATE_LEVEL_MULTIPLICATIVE_TUNABLE` dimension composes the C-AS-12 §12.1 5-axis multiplicative tunable at every cell per §22.2.
8. Cross-deployment monotonicity invariant per §22.4: at deployment-surface ascent (transitions 6, 7, 8 per §22.1), the `GATE_LEVEL_MULTIPLICATIVE_TUNABLE` dimension MUST be monotonic-ascending (cross-axis composition with C-AS-12 §12.1 + C-CP-19 ensures this).

**Tests (v2.5 — dimension-set tests conformed to §22.2):** `test_preservation_dimension_cardinality_five`, `test_preservation_dimension_members_byte_exact_per_§22_2`, `test_preservation_invariants_cardinality_five`, `test_span_schema_invariant_form_superset`, `test_sampling_invariant_form_superset_and_scalar_le`, `test_redaction_invariant_form_class_index_ge`, `test_trace_storage_tier_invariant_form_class_index_ge`, `test_gate_level_invariant_form_class_index_ge`, `test_gate_level_enforcement_cross_axis_composition`, `test_verify_per_dimension_sampling_pass`, `test_verify_per_dimension_redaction_downgrade_reject`, `test_assert_cross_axis_composition_pending`, `test_gate_level_composition_c_as_12_section_12_1`, `test_cross_deployment_monotonicity_at_surface_ascent`, `test_cross_axis_edges_four_total`.

**Rollback boundary:** Revert per-dimension preservation invariants composition. R-OD-08 satisfaction loses 5-dimension preservation substrate; U-OD-32 transition verification loses per-dimension invariant references; cross-axis composition with AS sandbox-tier + CP gate-policy cross-deployment monotonicity loses OD-side composition anchor; T-perm-1 5-axis multiplicative tunable observability composition loses preservation-dimension foundation; Session 5 cross-axis matrix loses preservation-dimension scope. [v2.5 revert appendix:] Reverting v2.5 restores the v2.1 divergent dimension set (`CARDINALITY_BUDGET` + `SANDBOX_TIER` substituted for §22.2's `Span schema ingestion contract` + `Trace storage tier`); the revert MUST NOT be performed absent a §4A re-disposition.

---

## §4 Dependency graph

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_4.md` §4 in its entirety — §4.1 through §4.4 (within-axis dependency graph, acyclicity verification, topological sort) and §4.5.1 through §4.5.4 (cross-axis edge enumerations). Per §0.4.2, v2.5 introduces **no dependency-graph delta**: all 34 OD units preserved as nodes; every `Depends on:` edge preserved; within-axis DAG acyclic; topological sort unchanged; cross-axis edge enumerations unchanged.]

## §5 Spec-traceability

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_4.md` §5. Per §0.4.1, v2.5 introduces **no coverage-matrix delta**: every conformed unit's `Implements:` field is unchanged; the conformance corrects transcribed vocabulary, not contract coverage.]

---

## §6 Filing footer (v2.5)

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_5.md` |
| Version | v2.5 |
| Status | Proposed (v2.5 revision-pass close pending Phase-7 pre-implementation re-clearance) |
| Date | 2026-05-15 |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_4.md` (v2.4 — F3-02 Form A + C3-15 Path (i-refined) absorption) |
| Authoring discipline | `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Revision scope | Absorption of the operator-ratified `.harness/verbatim_audit_od_plan.md` §4A OD-plan verbatim-divergence cluster resolution — conform 9 determinate OD units (U-OD-02, U-OD-04, U-OD-09 acc #3, U-OD-11, U-OD-12, U-OD-14, U-OD-30 acc #6, U-OD-32, U-OD-33) to the cited `Spec_Operational_Discipline_v1_2.md` vocabulary; folds in the prior Tension 004 (U-OD-04) per §4A.6 |
| Carried-not-resolved | U-OD-09 acc #2 (FF-1 — design gap), U-OD-28 (FF-2 — *proposing*; conformance target undetermined), U-OD-29 (FF-3 — *open*; ADR-D2 §1.2 verification required) per §4A.7 |
| Systemic-tension record | `.harness/verbatim_audit_od_plan.md` (audit report + §4A Resolution Recommendation) — canonical cluster record per the Phase-7 checkpoint decision (no per-unit Tension 005+ proliferation) |
| Authority chain | `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 (spec canonical for plan) |

---

*End of Implementation Plan — Operational Discipline (OD axis) — v2.5.*
