# Implementation Plan — Information Substrate (IS axis) — v2.6

*Delta over v2.5. v2.6 is the IS-axis leg of **R-FS-1 arc #6 (B1-plan)** — the atomic-unit decomposition of the B1 sub-program's IS-side amendment, **IS spec v1.8 §5.4** (the `branch_metadata` D-derivative sidecar, the Route-Y branch-causality carrier for the 5 non-`SINGLE_THREADED_LINEAR` topology strategies). ONE NEW foundational unit (**U-IS-19** — the `BranchMetadata` carrier + the optional `branch_metadata` field on `StateLedgerEntry`/`EntryPayload` + its omit-when-`None` canonicalization contribution). Co-published with CP plan v2.32 (the 11 strategy/cross-cutting units) + runtime plan v2.43 (the PARTIAL projection + role-read). ZERO spec amendment (the spec is canonical at IS v1.8); ZERO contract change beyond the §5.4 carrier decomposition; ZERO cross-axis OUTBOUND edge (IS is consumer-most-upstream, 0 outbound — the consuming CP write-cadence unit declares the cross-axis edge from the CP side). v2.5 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.5 → v2.6)

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_5.md` (v2.5 — the H_T-IS-2 apply-pass impl-half IS-axis closure; U-IS-18 retired/relocated to U-RT-112).

### §0.2 Revision scope (v2.5 → v2.6)

v2.6 decomposes **IS spec v1.8 §5.4** (`branch_metadata` D-derivative sidecar, cleared at `.harness/clearance/Spec_Information_Substrate-v1_8-cleared-2026-06-13.md`) into ONE NEW foundational atomic unit. The sidecar is the **persisted carrier** the CP non-linear-topology `WorkflowDriver` composes (the **producer** lives at CP plan v2.32 U-CP-81 / U-CP-84); this IS unit authors only the **carrier shape + the canonicalization contribution** — the write-cadence (which entry carries the non-`None` `terminal_status`) is the CP producer's concern, decomposed at CP plan v2.32 U-CP-84.

| In scope at v2.6 | Out of scope |
|---|---|
| U-IS-19 — `BranchMetadata` record + `branch_metadata: BranchMetadata \| None` optional field on `StateLedgerEntry`/`EntryPayload` + omit-when-`None` canonicalization contribution (IS spec v1.8 §5.4) | All v2.5 / v2.4 unit bodies — preserved verbatim per §0.4 |
| DAG delta: +1 node (U-IS-19, foundational, `Depends on: (none)`) | The write-cadence (which entry carries `terminal_status`) — CP-producer concern at CP plan v2.32 U-CP-84 |
| Coverage matrix delta: +1 row (IS spec v1.8 C-IS-05 §5.4) | The branch-causality **producer** (composes `branch_metadata` at branch-spawn/termination) — CP plan v2.32 U-CP-81 / U-CP-84 |
| Cross-axis INBOUND edge note: CP plan v2.32 U-CP-84 → U-IS-19 (declared from the CP side; runtime/CP → IS, consumer-most-upstream direction) | Carrier-home `harness-core` vs `harness-is` (spec §5.4 deferred to impl; recorded as impl-discretion at U-IS-19 Note, NOT pinned) |

### §0.3 Sections preserved verbatim from v2.5

| Section | Status at v2.6 |
|---|---|
| §0 (v2.5 change-note) | Superseded by this §0 (historical record preserved at v2.5) |
| §1 Spec inventory | Refreshed: IS spec v1.3 → **v1.8** canonical at HEAD (the §5.4 sidecar lands at v1.8; the §5.1/§5.2/§5.3 sidecar/resolver/store lineage is unchanged from prior decomposition). The unit bodies citing v1.3 contracts are NOT re-versioned (those contracts are byte-unchanged through v1.8 per the IS v1.8 "PRESERVED VERBATIM" list); only the NEW §5.4 row is added. |
| §2 — U-IS-01..U-IS-17 (preserved/revised units) | **PRESERVED VERBATIM** from v2.5 §2.1/§2.2 (see `Implementation_Plan_Information_Substrate_v2_5.md` + v2.4 for bodies, delta-only-plan-chain convention) |
| §2 — U-IS-18 | **PRESERVED as RETIRED** (relocated to U-RT-112 at v2.5; unchanged at v2.6) |
| §3 Dependency graph | Revised at the U-IS-19 node only (§3 below); all other within-axis edges + the acyclicity proof preserved verbatim from v2.5 §3 |
| §4 Coverage matrix | Revised: +1 row (C-IS-05 §5.4); all other rows preserved verbatim |
| §5 Auxiliary-type carrier audit | Extended: +1 auxiliary type (`BranchMetadata`); §5 below |

### §0.4 Authority chain — no operator gate

v2.6 absorbs a **cleared** spec amendment (IS v1.8 §5.4, adversarial APPROVE-WITH-CLASS-3 + Codex + advisor at PR #531) into the IS plan. No operator decision is owed: the carrier shape is fully specified at §5.4; the one spec-deferred choice (carrier-home `harness-core` vs `harness-is`) is implementer-discretion authorized at §5.4 ("Carrier-home deferred to B1-impl-N") and recorded as a U-IS-19 Note, NOT pinned by the planner (per the implementation-planner discipline — the plan does not make spec-deferred decisions). ZERO X-AL-3 risk (no spec amendment; plan-layer decomposition of a cleared contract).

### §0.5 Status posture

`Status: Proposed` (preserved until P6-CK / decorrelated-review clearance). Clearance marker filed at `.harness/clearance/Implementation_Plan_Information_Substrate-v2_6-cleared-2026-06-13.md` per workspace `CLAUDE.md` §4.5. Sibling co-publications: CP plan v2.32 + runtime plan v2.43 (the B1-plan cascade).

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.5 §1, **plus** the NEW §5.4 contract surface:

| Contract | Version | Status at v2.6 |
|---|---|---|
| C-IS-05 §5 (six-field shape) / §5.1 (`procedural_tier_snapshot_ref` sidecar) / §5.2 (resolver) / §5.3 (prompts store) | IS spec v1.8 (byte-unchanged from v1.3–v1.7 per the v1.8 PRESERVED-VERBATIM list) | Covered at prior units (U-IS-11 + U-RT-112 + the §5.3 store decomposition); unchanged |
| **C-IS-05 §5.4 (`branch_metadata` D-derivative sidecar)** | **IS spec v1.8 (NEW)** | **Covered at U-IS-19 (NEW this arc)** |
| C-IS-06 §6 hash-chain | IS spec v1.8 | Construction discipline UNCHANGED; the §5.4 sidecar travels the existing §6.1 canonical payload via the established omit-when-`None` pattern — U-IS-19 contributes the canonicalization-participation, NOT a §6 construction change |

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units

U-IS-01..U-IS-17 (preserved/revised at v2.5) + U-IS-18 (RETIRED at v2.5) — PRESERVED VERBATIM from v2.5. See `Implementation_Plan_Information_Substrate_v2_5.md` (and v2.4 for the v2.4-authored bodies) per the delta-only-plan-chain convention.

### §2.2 NEW unit (1)

#### U-IS-19 — `branch_metadata` D-derivative sidecar carrier (IS spec v1.8 §5.4)

**Scope.** Author the `BranchMetadata` record type and add the optional `branch_metadata: BranchMetadata | None = None` field to the persisted `StateLedgerEntry` and the `EntryPayload` write-carrier, with its omit-when-`None` contribution to the §6.1 canonical payload — the persisted carrier for fan-out branch causality + per-branch terminal disposition that the CP non-linear-topology `WorkflowDriver` composes (Route Y). One coherent schema-extension change at the D-derivative sidecar layer (the exact `procedural_tier_snapshot_ref` template, IS spec v1.8 §5.4).

**Spec linkage.** C-IS-05 §5.4 (primary — the `branch_metadata` sidecar + `BranchMetadata` record + the append-only + dispatch-boundary-disposition invariants + the omit-when-`None` canonicalization). C-IS-06 §6.1 (the canonical-payload participation when non-`None`, per the §5.1 omit-when-`None` precedent — construction discipline unchanged). ADR-F2 v1.2 §Consequences (c) (the D-derivative-sidecar extension authorization).

**Surfaces affected.** The state-ledger entry-shape definition (the `StateLedgerEntry` schema), the `EntryPayload` write-carrier schema, and the entry-canonicalization function (the omit-when-`None` inclusion path). The `BranchMetadata` record type carrier (residence impl-discretion — see Notes).

**Signatures introduced or modified** (transcribed from IS spec v1.8 §5.4, NOT redesigned):
- `BranchMetadata` — a three-field frozen record: `parent_action_id: Identifier`, `branch_index: int` (≥ 0), `terminal_status: Literal['cancelled', 'completed', 'timed_out'] | None` (the value-set + per-value semantics are CP-producer-owned per CP spec v1.32 §25.15.2 obl. 4).
- `StateLedgerEntry` / `EntryPayload` gain `branch_metadata: BranchMetadata | None = None` (the optional 8th field, alongside the §5.1 7th `procedural_tier_snapshot_ref`).

**Depends on.** (none) — foundational carrier unit. (IS 0-outbound: U-IS-19 declares NO dependency on any U-CP-* / U-RT-* unit — see §3.2 cycle guard.)

**Acceptance criterion (functional).** (1) `BranchMetadata(parent_action_id=…, branch_index=0, terminal_status=None)` constructs and is frozen. (2) A `StateLedgerEntry` / `EntryPayload` constructed with `branch_metadata=None` canonicalizes **byte-identically** to a pre-v1.8 entry (the field is omitted from the §6.1 canonical payload when `None`, per the `entry_hash.py` `if … is not None` discipline the §5.1 sidecar established) — a regression test asserts byte-identity against a stored pre-v1.8 fixture. (3) A `StateLedgerEntry` with non-`None` `branch_metadata` includes the nested record in the §6.1 canonical payload (and thus the §6.2 `response_hash`), tamper-evident per §6.5. (4) `terminal_status` accepts only `{cancelled, completed, timed_out} | None` — a value outside the set is rejected at construction (Pydantic `Literal`).

**Acceptance criterion (integration).** When the CP producer (CP plan v2.32 U-CP-84 write-cadence) appends a branch terminal entry carrying `branch_metadata` with a non-`None` `terminal_status`, the entry persists + reloads with the sidecar intact and the §6.3 chain remains verifiable (no historical-entry mutation). Verified at the B1-impl-N persisted-branch-causality assertion (CP §25.18) — the cross-axis integration surface.

**Notes.** (a) **Carrier-home is implementer-discretion, NOT pinned** — `harness-core` (shared) vs `harness-is` (co-located with the entry shape), exactly as IS spec v1.8 §5.4 + the v2.5 U-IS-18→U-RT-112 residence-transfer precedent leave residence to impl. The **one hard constraint:** NOT `harness-cp` (the IS axis is consumer-most-upstream with 0 outbound cross-axis edges; CP consumes the entry shape from IS, not the reverse). (b) **Producer-supplied, not resolver-derived** — unlike the §5.1 sidecar (derived by the §5.2 resolver), `branch_metadata` is composed by the CP `WorkflowDriver`; there is **no §5.2-analogue resolver unit** at the IS axis. (c) `branch_path` is NOT in this carrier — it is the CP-side §25.16 idempotency-key composition detail (CP plan v2.32 U-CP-83); `(parent_action_id, branch_index)` is the persisted causality key.

---

## §3 Dependency graph

### §3.1 Dependency-graph delta (v2.6)

| Operation | Detail |
|---|---|
| NEW node | U-IS-19 (`Depends on: (none)` — foundational carrier) |
| NEW within-axis edge | (none) — U-IS-19 is a leaf-foundational carrier; no existing IS unit depends on it at the IS axis (consumers are cross-axis, declared from the consumer side) |
| NEW cross-axis INBOUND edge (declared at CP plan v2.32) | U-CP-84 (write-cadence) → U-IS-19 (the CP producer consumes the IS carrier shape; runtime/CP → IS direction) |

### §3.2 Acyclicity preservation + IS-0-outbound cycle guard

**Cycle guard (load-bearing invariant).** U-IS-19 declares `Depends on: (none)` and — like every IS-axis unit — has **ZERO outbound cross-axis edge**: no U-IS-* depends on any U-CP-* or U-RT-* unit. The IS axis is consumer-most-upstream (the same invariant that pinned the §5.4 carrier-home "NOT `harness-cp`"). All B1 cross-axis edges therefore run **inbound** to U-IS-19 (CP/RT → IS), matching the `harness-runtime`/`harness-cp` → `harness-is` package dependency direction. ZERO new cycle: the cross-axis edge U-CP-84 → U-IS-19 is downstream-of-IS and cannot close a cycle with any IS-internal edge (U-IS-19 has none outbound).

IS-axis internal DAG (v2.5 units) PRESERVED VERBATIM plus the one foundational leaf U-IS-19. Acyclicity preserved at the IS-axis intra-axis layer + the cross-axis aggregate (the full B1 dependency graph + topological order is recorded at CP plan v2.32 §3, the arc's aggregate-graph home).

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.6)

| Spec contract | Atomic unit |
|---|---|
| IS spec v1.8 C-IS-05 §5.4 (`branch_metadata` D-derivative sidecar carrier + `BranchMetadata` record + omit-when-`None` canonicalization) | **U-IS-19** (NEW) |
| IS spec v1.8 C-IS-06 §6.1 (canonical-payload participation when non-`None`; construction discipline unchanged) | U-IS-19 (contributes the omit-when-`None` inclusion path; the §6 hash-chain construction unit is unchanged) |

All other C-IS-* rows PRESERVED VERBATIM from v2.5 §4. ZERO contract-coverage gap at the IS axis. (The cross-axis producer of `branch_metadata` — the write-cadence — is covered at CP plan v2.32 U-CP-84; the runtime PARTIAL projection + role-read at runtime plan v2.43.)

---

## §5 Auxiliary-type carrier audit

Extended from v2.5 §5 with one NEW auxiliary type:

| Auxiliary type | Carrier residence | Authority |
|---|---|---|
| `BranchMetadata` (`{parent_action_id, branch_index, terminal_status}`) | **Implementer-discretion** — `harness-core` vs `harness-is`; hard constraint NOT `harness-cp` (IS 0-outbound) | IS spec v1.8 §5.4 (residence deferred to B1-impl-N); U-IS-19 Note (a) |

All v2.5 §5 entries PRESERVED VERBATIM.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.6 (delta over v2.5) |
| Authored at | 2026-06-13 |
| Authoring authority | R-FS-1 arc #6 (B1-plan); IS spec v1.8 §5.4 (cleared PR #531); design `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` §8 (B1-plan cascade row) |
| Net delta | +1 NEW foundational unit (U-IS-19, `Depends on: (none)`); +1 auxiliary type (`BranchMetadata`); +1 coverage row (C-IS-05 §5.4); +1 cross-axis INBOUND edge (U-CP-84 → U-IS-19, declared CP-side); ZERO spec amendment; ZERO IS-outbound edge |
| Sibling co-publications | CP plan v2.32 (U-CP-80..90 — dispatch table + branch context/role + drain + idempotency + write-cadence + cascade_policy + 5 strategies); runtime plan v2.43 (U-RT-113 PARTIAL projection + U-RT-114 role-read); clearance markers; workspace `CLAUDE.md` §2.4 plan-head bumps |
| Cross-axis cascade | INBOUND only (CP/RT → IS); IS 0-outbound preserved |
