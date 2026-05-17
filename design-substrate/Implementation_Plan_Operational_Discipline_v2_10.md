# Implementation Plan — Operational Discipline (OD axis) — v2.10

**Status: Proposed.**

**Revision:** v2.10 — Phase 7 sub-phase 7b in-CLI revision pass. Resolves the **FF-3 carried Class 1 fork** at U-OD-29 (`SandboxTier` 0-indexed in-unit enum vs the AS-axis-owned 1-indexed enum). v2.10 is a delta over v2.9: **only §3.7.3 U-OD-29 is revised**; every other §0–§11 section is preserved verbatim from v2.9. Predecessor: v2.9 (FF-2 — U-OD-28 collector-placement).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 authority chain + §4.3 back-flow routing; `harness-od/CLAUDE.md` §5.1; `implementation-planner` SKILL.md §8 revision-pass sub-mode.

**Entry authorization:** Operator ratification 2026-05-16 of the FF-3 resolution (resolve now — plan v2.10 micro-revision, land U-OD-29 at 7b). `.harness/class_1_tension_u_od_29_sandbox_tier_ff3.md`.

---

## §0 Change-note

### §0.1 Trigger

At OD-7b final-batch sequencing (2026-05-16), U-OD-29 was found to carry the **FF-3** fork (`Implementation_Plan_Operational_Discipline_v2_5.md` §0.6). U-OD-29's v2.1 body declares an **in-unit** `enum SandboxTier { TIER_0, TIER_1, TIER_2, TIER_3 }` (0-indexed, "per D2 v1.1 §1.2"). Three problems: (1) the AS axis **owns and has landed** `SandboxTier` as `TIER_1_PROCESS / TIER_2_CONTAINER / TIER_3_MICROVM / TIER_4_FULL_VM` (1-indexed); (2) the v2.6 R5 materializability audit reclassified `SandboxTier` for U-OD-29 as a **cross-axis AS edge** — U-OD-29 must not declare it in-unit; (3) the citation "D2 v1.1 §1.2" is wrong (ADR-D2 §1.2 is the sandbox provider-class enumeration; the four-tier set is ADR-F4 v1.1's "process / container / microVM / full-VM", transcribed at C-AS-01 §1.1). v2.10 conforms U-OD-29 to the AS-owned `SandboxTier` and OD spec C-OD-20 §20.3.

### §0.2 The defect + resolution

| # | Unit | Defect | Resolution (operator-ratified 2026-05-16) |
|---|---|---|---|
| FF-3 | U-OD-29 | In-unit `enum SandboxTier {TIER_0..TIER_3}` (0-indexed) — contradicts the AS-axis-owned, landed `SandboxTier` (1-indexed `TIER_1_PROCESS..TIER_4_FULL_VM`), contradicts the v2.6 R5 audit's cross-axis-AS-edge classification, and miscites D2 §1.2. `OtlpReachabilityClass` + `PER_SANDBOX_TIER_REACHABILITY` + acc keyed on the 0-indexed scheme. | **Conform to the AS-owned `SandboxTier` + OD spec C-OD-20 §20.3.** The in-unit `enum SandboxTier` is **struck**; `SandboxTier` is declared a cross-axis AS-consumed type (the AS-landed `harness_as.sandbox_tier.SandboxTier`, 4 values `TIER_1_PROCESS / TIER_2_CONTAINER / TIER_3_MICROVM / TIER_4_FULL_VM`). `OtlpReachabilityClass` + `SandboxTierReachability` + `PER_SANDBOX_TIER_REACHABILITY` + `assert_otlp_reachable_from_sandbox` re-keyed onto the 1-indexed tiers; the reachability-class-per-tier mapping conformed to §20.3. acc #1 re-worded (SandboxTier consumed, not declared; citation corrected to ADR-F4 four-tier set / C-AS-01 §1.1); acc #3/#4/#6 re-keyed. See §3.7.3. |

### §0.3 Scope

Only §3.7.3 (U-OD-29) is revised. No contract re-decomposed; no unit added or removed; unit count unchanged (35). U-OD-29's `Depends on` is amended only to make the `SandboxTier` cross-axis AS source explicit (see §0.4) — no within-axis edge changes.

### §0.4 Dependency-graph delta

U-OD-29's v2.1 `Depends on: [U-OD-28, U-AS-NN (cross-axis: AS — C-AS-12 §12.4)]` is amended to `[U-OD-28, U-AS-01 (cross-axis: AS — SandboxTier enum, C-AS-01 §1.1), U-AS-NN (cross-axis: AS — C-AS-12 §12.4 sandbox-tier reachability)]` — the cross-axis AS `SandboxTier` source is named explicitly (it was implicit / mis-declared in the v2.1 body, which declared the enum in-unit). This is a **cross-axis** edge addition; it does not change the within-axis OD DAG, the Kahn topological sort, or acyclicity. U-OD-29 remains a within-axis leaf (no OD unit depends on it).

### §0.5 Sections preserved verbatim from v2.9

All of §0 (v2.9 + v2.8 + v2.7 change-notes), §1, §2, §3 except §3.7.3 U-OD-29, §4 except the §4.6 restatement, §5–§11. The v2.9-revised U-OD-28, the v2.8-revised units (U-OD-02/08/09/12/20/21), and the v2.7-revised units (U-OD-00, U-OD-30) are unchanged.

### §0.6 Coverage matrix delta

| Contract | v2.9 coverage | v2.10 coverage |
|---|---|---|
| C-OD-20 §20.3 | U-OD-29 (`SandboxTier` 0-indexed in-unit — FF-3 halt) | U-OD-29 — `SandboxTier` consumed from the AS-owned enum; `OtlpReachabilityClass` + per-tier reachability map conformed to §20.3's 1-indexed tiers |

No contract row loses a column mark. Coverage complete.

---

## §3.7.3 U-OD-29 — Verify per-sandbox-tier OTLP reachability + F4 capability-floor composition [REVISED — v2.10]

[v2.1-base unit (preserved verbatim through v2.9). v2.10 delta (FF-3): the in-unit `enum SandboxTier` is **struck** — `SandboxTier` is consumed from the AS-axis-owned landed enum (cross-axis AS). `OtlpReachabilityClass`, `SandboxTierReachability`, `PER_SANDBOX_TIER_REACHABILITY`, `assert_otlp_reachable_from_sandbox`, and acc #1/#3/#4/#6 re-keyed onto the 1-indexed AS tiers and conformed to OD spec §20.3. acc #2/#5/#7/#8, `OtlpReachabilityClass` as a concept, the `F4_CAPABILITY_FLOOR_LIFECYCLE_EMISSION_ANCHOR` const, Files affected, rollback boundary preserved verbatim from v2.1 except as re-keyed.]

**Implements:** [C-OD-20 §20.3]

**Depends on:** [U-OD-28, U-AS-01 (cross-axis: AS — `SandboxTier` enum, C-AS-01 §1.1 four-tier sandbox-isolation tier-set), U-AS-NN (cross-axis: AS — C-AS-12 §12.4 sandbox-tier reachability)]

**Inputs:** OD spec v1.2 §20.3 per-sandbox-tier OTLP reachability invariant (the four 1-indexed sandbox tiers must reach the OTLP collector — Tier-1 process via localhost socket; Tier-2 container via localhost socket or explicit network-config; Tier-3 microVM via per-microVM agent or egress allow-list; Tier-4 full-VM via vendor-managed collector); the AS-axis-owned `SandboxTier` enum (ADR-F4 v1.1 four-tier sandbox-isolation tier-set — `process / container / microVM / full-VM` — landed at the AS axis as `TIER_1_PROCESS / TIER_2_CONTAINER / TIER_3_MICROVM / TIER_4_FULL_VM`); F4 v1.1 capability-floor (iv) lifecycle-event-emission composition; AS plan C-AS-12 §12.4 sandbox-tier reachability declarations.

**Cross-axis dependency resolution.** `SandboxTier` is AS-axis-owned (ADR-F4 four-tier set; C-AS-01 §1.1) — U-OD-29 consumes the AS-landed enum, it does **not** declare a sandbox-tier enum in-unit (v2.6 R5 audit classification). The C-AS-12 §12.4 reachability edge resolves per OD-S4-3.A.

**Files affected:** Per-sandbox-tier OTLP reachability (logical name: `od-per-sandbox-tier-otlp-reachability`).

**Signatures (v2.10 — in-unit `SandboxTier` struck; surfaces re-keyed onto the AS 1-indexed enum + conformed to §20.3):**

```
// v2.10 (FF-3): the v2.1 in-unit `enum SandboxTier { TIER_0..TIER_3 }` is
// STRUCK. SandboxTier is the AS-axis-owned enum (ADR-F4 v1.1 four-tier
// sandbox-isolation tier-set; C-AS-01 §1.1), consumed cross-axis from the
// AS axis:  SandboxTier ∈ { TIER_1_PROCESS, TIER_2_CONTAINER,
//                           TIER_3_MICROVM, TIER_4_FULL_VM }
// U-OD-29 declares NO sandbox-tier enum.

// OtlpReachabilityClass — the four §20.3 reachability shapes, one per AS tier.
enum OtlpReachabilityClass {
  LOCALHOST_SOCKET,                                // §20.3 — Tier-1 process: in-process collector via localhost socket
  EXPLICIT_NETWORK_CONFIG,                         // §20.3 — Tier-2 container: localhost socket OR host.docker.internal / sidecar
  PER_MICROVM_AGENT_OR_EGRESS_ALLOWLIST,           // §20.3 — Tier-3 microVM: per-microVM agent OR egress allow-list
  VENDOR_MANAGED_COLLECTOR_REACHABILITY            // §20.3 — Tier-4 full-VM: vendor-managed collector
}

record SandboxTierReachability {
  sandbox_tier                 : SandboxTier        // AS-owned (cross-axis)
  reachability_class           : OtlpReachabilityClass
  per_tier_egress_required     : bool               // false for Tier-1 process; true for Tier-2/3/4
  composes_with_cell_placement : bool               // = true
}

const PER_SANDBOX_TIER_REACHABILITY : Map<SandboxTier, SandboxTierReachability>   // exactly 4 entries

fn assert_otlp_reachable_from_sandbox(
  sandbox_tier   : SandboxTier,
  cell_placement : CollectorPlacement                // the v2.9 §20.1 7-value enum (U-OD-28)
) -> Result<(), ReachabilityViolation>

const F4_CAPABILITY_FLOOR_LIFECYCLE_EMISSION_ANCHOR :
  "Lifecycle events (per U-OD-08 F3 mapping) MUST emit from every sandbox tier; failure to emit constitutes F4 v1.1 capability-floor (iv) violation"
```

**Acceptance criteria (v2.10 — acc #1/#3/#4/#6 conformed to the AS `SandboxTier` + §20.3; #2/#5/#7/#8 preserved verbatim from v2.1):**

1. **(v2.10 FF-3.)** `SandboxTier` is **consumed from the AS-axis-owned enum** (ADR-F4 v1.1 four-tier sandbox-isolation tier-set — `process / container / microVM / full-VM`; C-AS-01 §1.1; landed at the AS axis as `TIER_1_PROCESS / TIER_2_CONTAINER / TIER_3_MICROVM / TIER_4_FULL_VM`). U-OD-29 declares **no** sandbox-tier enum in-unit. The enum has exactly 4 values, 1-indexed.
2. `OtlpReachabilityClass` enumerates exactly 4 values per §20.3.
3. **(v2.10 FF-3.)** `PER_SANDBOX_TIER_REACHABILITY` declares exactly 4 entries, one per AS `SandboxTier` value, with the §20.3 reachability class per tier: `TIER_1_PROCESS → LOCALHOST_SOCKET`; `TIER_2_CONTAINER → EXPLICIT_NETWORK_CONFIG`; `TIER_3_MICROVM → PER_MICROVM_AGENT_OR_EGRESS_ALLOWLIST`; `TIER_4_FULL_VM → VENDOR_MANAGED_COLLECTOR_REACHABILITY`.
4. **(v2.10 FF-3 — re-keyed.)** `assert_otlp_reachable_from_sandbox` returns `Err(ReachabilityViolation)` when: `TIER_2_CONTAINER`, `TIER_3_MICROVM`, or `TIER_4_FULL_VM` lacks the §20.3-required network reachability to the collector under the cell placement; `TIER_1_PROCESS` lacks localhost-socket reachability to an in-process collector.
5. F4 v1.1 capability-floor (iv) composition per `F4_CAPABILITY_FLOOR_LIFECYCLE_EMISSION_ANCHOR` verbatim — lifecycle events MUST emit from every sandbox tier regardless of collector placement.
6. **(v2.10 FF-3 — re-keyed.)** `TIER_3_MICROVM` and `TIER_4_FULL_VM` reachability composes with the AS plan C-AS-12 §12.4 egress policy — the most-isolated tiers MAY egress to a private/vendor-managed collector endpoint but MUST NOT egress to arbitrary public ingestion endpoints.
7. Per-tier reachability composes additively with the per-cell collector placement from U-OD-28 — both must be satisfied for span emission to succeed.
8. Cross-axis edge per OD-S4-3.A: edge target `U-AS-NN` for C-AS-12 §12.4 sandbox-tier reachability; the `SandboxTier` enum is consumed cross-axis from the AS axis (C-AS-01 §1.1).

**Tests (v2.10 — conformed to the AS 1-indexed `SandboxTier`):** `test_sandbox_tier_consumed_from_as_axis_not_declared_in_unit`, `test_sandbox_tier_cardinality_four`, `test_reachability_class_cardinality_four`, `test_per_tier_reachability_cardinality_four`, `test_tier_1_process_localhost_socket`, `test_tier_2_container_explicit_network_config`, `test_tier_3_microvm_per_microvm_agent_or_egress_allowlist`, `test_tier_4_full_vm_vendor_managed_collector`, `test_assert_reachable_tier_1_in_process_accept`, `test_assert_reachable_tier_3_reject_public_endpoint`, `test_f4_capability_floor_lifecycle_anchor_byte_exact`, `test_lifecycle_event_emission_required_at_every_tier`, `test_reachability_composes_additively_with_placement`, `test_cross_axis_edge_to_u_as_nn_c_as_12_section_12_4`.

**Rollback boundary:** Revert per-sandbox-tier OTLP reachability. F4 v1.1 capability-floor (iv) lifecycle-event-emission discipline loses tier-side enforcement; the most-isolated tiers lose egress-policy composition with OTLP collector placement; cross-axis composition with AS plan C-AS-12 §12.4 loses the OD-side reachability anchor; sandbox-tier-bounded spans risk silent lifecycle-event drop. [v2.10 revert appendix:] Reverting v2.10 restores the v2.1 in-unit 0-indexed `SandboxTier {TIER_0..TIER_3}` — i.e. the FF-3 defect; the revert MUST NOT be performed absent a re-disposition.

---

## §4.6 Dependency-graph delta (v2.10)

| Edge | Direction | Effect |
|---|---|---|
| `U-OD-29 → U-AS-01` (NEW, cross-axis: AS) | U-OD-29 consumes the AS-owned `SandboxTier` enum (C-AS-01 §1.1) | Cross-axis edge — makes explicit the `SandboxTier` source the v2.1 body mis-declared in-unit. Does not affect the within-axis OD DAG, the Kahn topological sort, or acyclicity. |

All v2.9 within-axis + cross-axis edges otherwise preserved verbatim. U-OD-29 remains a within-axis leaf — no OD unit depends on it. The within-axis topological sort is unchanged; all 35 units consume.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_10.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-16 — v2.10 revision pass (FF-3 — U-OD-29 `SandboxTier` conformance) |
| Authoring authority | Operator ratification 2026-05-16 (FF-3 — resolve now); `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_9.md` (FF-2 — U-OD-28 collector-placement) |
| Substrate consumed | `.harness/class_1_tension_u_od_29_sandbox_tier_ff3.md`; the AS-axis-landed `SandboxTier` enum (ADR-F4 v1.1 four-tier set; C-AS-01 §1.1); OD spec C-OD-20 §20.3 |
| Successor consumption | U-OD-29 lands against this file — OD axis-stream 7b closes at 35/35. |
| Revision policy | Canonical for the OD axis plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Operational Discipline v2.10. Delta over v2.9 — only §3.7.3 U-OD-29 revised (FF-3 — in-unit `SandboxTier` struck, conformed to the AS-owned enum + OD spec §20.3). All other sections preserved verbatim. One cross-axis edge added (U-OD-29 → U-AS-01); within-axis DAG unchanged; unit count unchanged (35).*
