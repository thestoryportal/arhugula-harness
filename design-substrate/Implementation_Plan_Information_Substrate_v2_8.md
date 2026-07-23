# Implementation Plan — Information Substrate (IS axis) — v2.8

*Delta over v2.7. v2.8 is the IS-axis leg of the `B-33-A` spec-leg apply — the atomic-unit decomposition of **IS spec v1.12** (NEW §5.6 D-derivative sidecar field `rotation_correlation_id` on `StateLedgerEntry`/`EntryPayload`, C-IS-05; NEW §7.7 read-side presence/uniqueness invariants, C-IS-07), authored per the RATIFIED Class 1 fork `.harness/class_1_fork_b33_rotation_correlation_carrier.md` §4 Option A. ONE NEW foundational unit (**U-IS-20** — the carrier + its canonicalization contribution + the presence/uniqueness invariants). **SPEC-LEG ONLY** — mirrors the `B-59-A` spec-leg → impl-leg precedent (PRs #1080 → #1081): the carrier code, the CP-side `verify_rotation_6_steps` extension, and the composition-root OD-join are the separate impl leg, NOT decomposed here. ZERO cross-axis OUTBOUND edge (IS is consumer-most-upstream, 0 outbound — the consuming CP verifier unit declares the cross-axis edge from the CP side at the impl leg). v2.7 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.7 → v2.8)

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_7.md` (v2.7 — the B-48 apply-leg U-IS-11 amendment; writer-owned drain-path timestamp authority).

### §0.2 Revision scope (v2.7 → v2.8)

v2.8 decomposes **IS spec v1.12 §5.6 + §7.7** (`.harness/class_1_fork_b33_rotation_correlation_carrier.md`, RATIFIED 2026-07-21 Option A) into ONE NEW foundational atomic unit. The sidecar is the **persisted carrier** the CP rotation orchestration (`execute_key_rotation`) composes (the **producer** and the **consumer** — the `verify_rotation_6_steps` extension — both live at the separate CP-axis impl leg, out of scope here); this IS unit authors only the **carrier shape + the canonicalization contribution + the IS-chain-checkable presence/uniqueness invariants** — exactly the same scope split v2.6's U-IS-19 established for `branch_metadata` against the CP `WorkflowDriver` producer.

| In scope at v2.8 | Out of scope |
|---|---|
| U-IS-20 — `rotation_correlation_id: str \| None` optional field on `StateLedgerEntry`/`EntryPayload` + omit-when-`None` canonicalization contribution + presence/uniqueness read-side invariants (IS spec v1.12 §5.6 + §7.7) | All v2.7 / v2.6 / earlier unit bodies — preserved verbatim per §0.4 |
| DAG delta: +1 node (U-IS-20, foundational, `Depends on: (none)`) | The rotation-window write-cadence (which entries within a window carry the id) — CP-producer concern at the CP-axis impl leg |
| Coverage matrix delta: +2 rows (IS spec v1.12 C-IS-05 §5.6 + C-IS-07 §7.7) | The `verify_rotation_6_steps` 3-step extension, the OD-join composition-root-injected evidence DTO, and the B-36 `AwsKmsSigningBackend` key-identity boundary attestation — all CP-owned, decomposed at the CP-axis impl leg (not this arc) |
| Cross-axis INBOUND edge note: the CP-axis impl leg's rotation-orchestration + verifier units → U-IS-20 (declared from the CP side at that leg; runtime/CP → IS, consumer-most-upstream direction) | Carrier-home question — N/A here (the field lives directly on `StateLedgerEntry`/`EntryPayload`, no auxiliary record type to home elsewhere, unlike `BranchMetadata`) |

### §0.3 Sections preserved verbatim from v2.7

| Section | Status at v2.8 |
|---|---|
| §0 (v2.7 change-note) | Superseded by this §0 (historical record preserved at v2.7) |
| §1 Spec inventory | Refreshed: IS spec v1.11 → **v1.12** canonical at HEAD (the §5.6/§7.7 additions land at v1.12; all prior contract rows are byte-unchanged through v1.12 per the v1.12 "PRESERVED VERBATIM" list); only the NEW §5.6/§7.7 rows are added. |
| §2 — U-IS-01..U-IS-19 (preserved/revised/amended units) | **PRESERVED VERBATIM** from v2.7 §2 (see `Implementation_Plan_Information_Substrate_v2_7.md` and earlier for bodies, delta-only-plan-chain convention) |
| §3 Dependency graph | Revised at the U-IS-20 node only (§3 below); all other within-axis edges + the acyclicity proof preserved verbatim from v2.7 §3 |
| §4 Coverage matrix | Revised: +2 rows (C-IS-05 §5.6 + C-IS-07 §7.7); all other rows preserved verbatim |
| §5 Auxiliary-type carrier audit | UNCHANGED — U-IS-20 introduces no auxiliary record type (unlike U-IS-19's `BranchMetadata`); the field is a bare `str \| None` directly on the existing schema |

### §0.4 Authority chain — no operator gate

v2.8 absorbs a spec amendment authored in the SAME apply arc as this plan delta (IS spec v1.11 → v1.12, `.harness/class_1_fork_b33_rotation_correlation_carrier.md` §4, RATIFIED 2026-07-21 "OPTION A AS RECOMMENDED"). No FURTHER operator decision is owed at the plan layer: the carrier shape is fully specified at §5.6; the ratified Option A choice (typed additive sidecar vs first-class C-IS-05 field vs hold) is ALREADY DECIDED at the fork's §4 and reconciled against the actual IS carrier idiom at the spec's own change-note (v1.11 → v1.12) — this plan delta performs the mechanical atomic-unit decomposition of an already-cleared-shape contract, exactly as v2.6's absorption of IS spec v1.8 §5.4 did. ZERO X-AL-3 risk (spec + plan land together in this arc with a clearance marker each, per workspace `CLAUDE.md` §4.5; plan-layer decomposition of a spec amendment authored in the SAME PR is the standard spec-leg shape, mirroring the `B-59-A`/`B-65-A` precedent).

### §0.5 Status posture

`Status: Proposed` (pending P6-CK / decorrelated-review clearance). Clearance marker owed at `.harness/clearance/implementation-plan-information-substrate-v2-8-cleared-2026-07-22.md` per workspace `CLAUDE.md` §4.5, filed in the same PR as the IS spec v1.12 clearance marker. No sibling plan co-publication at this leg (SPEC-ONLY — the CP-axis impl leg, when opened, is its own separate PR + its own CP plan delta, mirroring `B-59-A` PR #1080 → #1081).

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.7 §1, **plus** the NEW §5.6/§7.7 contract surface:

| Contract | Version | Status at v2.8 |
|---|---|---|
| C-IS-05 §5 (six-field shape) / §5.1–§5.5 (sidecars + resolver + store) | IS spec v1.12 (byte-unchanged from v1.11 per the v1.12 PRESERVED-VERBATIM list) | Covered at prior units (U-IS-11, U-IS-19, U-RT-112, the §5.3 store decomposition); unchanged |
| **C-IS-05 §5.6 (`rotation_correlation_id` D-derivative sidecar)** | **IS spec v1.12 (NEW)** | **Covered at U-IS-20 (NEW this arc)** |
| C-IS-06 §6 hash-chain | IS spec v1.12 | Construction discipline UNCHANGED; the §5.6 sidecar travels the existing §6.1 canonical payload via the established omit-when-`None` pattern — U-IS-20 contributes the canonicalization-participation, NOT a §6 construction change |
| C-IS-07 §7.1–§7.6 (read/write contract pair) | IS spec v1.12 | UNCHANGED |
| **C-IS-07 §7.7 (rotation-correlation carrier read-side invariants)** | **IS spec v1.12 (NEW)** | **Covered at U-IS-20 (NEW this arc)** |

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units

U-IS-01..U-IS-19 — PRESERVED VERBATIM from v2.7. See `Implementation_Plan_Information_Substrate_v2_7.md` (and earlier files for pre-v2.7-authored bodies) per the delta-only-plan-chain convention.

### §2.2 NEW unit (1)

#### U-IS-20 — `rotation_correlation_id` D-derivative sidecar carrier + presence/uniqueness invariants (IS spec v1.12 §5.6 + §7.7)

**Scope.** Add the optional `rotation_correlation_id: str | None = None` field to the persisted `StateLedgerEntry` and the `EntryPayload` write-carrier, with its omit-when-`None` contribution to the §6.1 canonical payload — the persisted carrier a rotation-boundary verifier REQUIRES and JOINS to distinguish "rotation genuinely occurred across this window" from "the chain is merely intact." Author the field ALONE at this leg — no producer write-cadence, no consumer verifier extension (both are the separate CP-axis impl leg). One coherent schema-extension change at the D-derivative sidecar layer, following the exact `procedural_tier_snapshot_ref` / `branch_metadata` template (IS spec v1.12 §5.6).

**Spec linkage.** C-IS-05 §5.6 (primary — the `rotation_correlation_id` sidecar + the omit-when-`None` canonicalization + the shared-value-space contract with OD spec v1.31 §24.7). C-IS-07 §7.7 (the presence + uniqueness read-side invariants over the carrier). C-IS-06 §6.1 (the canonical-payload participation when non-`None`, per the §5.1/§5.4 omit-when-`None` precedent — construction discipline unchanged). ADR-F2 v1.2 §Consequences (c) (the D-derivative-sidecar extension authorization).

**Surfaces affected.** The state-ledger entry-shape definition (the `StateLedgerEntry` schema), the `EntryPayload` write-carrier schema, and the entry-canonicalization function (the omit-when-`None` inclusion path). No new auxiliary record type (contrast `BranchMetadata` at U-IS-19) — the field is a bare `str | None`.

**Signature introduced or modified** (transcribed from IS spec v1.12 §5.6, NOT redesigned):
- `StateLedgerEntry` / `EntryPayload` gain `rotation_correlation_id: str | None = None`.

**Depends on.** (none) — foundational carrier unit. (IS 0-outbound: U-IS-20 declares NO dependency on any U-CP-* / U-RT-* unit — see §3.2 cycle guard.)

**Acceptance criterion (functional — carrier, §5.6).** (1) `StateLedgerEntry(..., rotation_correlation_id=None)` constructs (the default; every existing call site unaffected). (2) A `StateLedgerEntry` / `EntryPayload` constructed with `rotation_correlation_id=None` canonicalizes **byte-identically** to a pre-v1.12 entry (the field is omitted from the §6.1 canonical payload when `None`, per the `entry_hash.py` `if … is not None` discipline the §5.1/§5.4 sidecars established) — a regression test asserts byte-identity against a stored pre-v1.12 fixture. (3) A `StateLedgerEntry` with non-`None` `rotation_correlation_id` includes the value in the §6.1 canonical payload (and thus the §6.2 `response_hash`), tamper-evident per §6.5 — a mutation-probed test flips a persisted id post-write and confirms `verify_chain` reports a hash mismatch at that entry.

**Acceptance criterion (functional — carrier construction validation, §5.6).** (4) `StateLedgerEntry(..., rotation_correlation_id=<value>)` / `EntryPayload(..., rotation_correlation_id=<value>)` REJECT a present-but-malformed value (not parseable as a canonical-form UUID) at construction — a detect-then-refuse check, never a silent accept — mirroring OD spec v1.31 §24.7's own "UUID string, or key absent" admission rule. A canonical-form UUID string constructs successfully; `None` constructs successfully (the default); a non-UUID non-empty string (e.g. `"not-a-uuid"`) raises.

**Acceptance criterion (functional — read-side invariants, §7.7).** (5) **Non-emptiness guard (the vacuous-pass fix).** A window-scoped check over an EMPTY `Sequence[StateLedgerEntry]` fails BEFORE the presence/uniqueness predicates run — per §7.7 invariant (c), an empty claimed window is an absence of evidence, not a vacuous pass; both (6)/(7) below presuppose this guard has already run. (6) **Presence helper.** A window-scoped presence check over a NON-EMPTY `Sequence[StateLedgerEntry]` returns pass when every entry in the sequence carries a non-`None` `rotation_correlation_id`, and fails (typed, not silent) when any entry in the sequence carries `None`. (7) **Uniqueness helper.** A window-scoped uniqueness check over the same non-empty sequence returns pass when the set of non-`None` `rotation_correlation_id` values across the sequence has cardinality ≤ 1, and fails (typed, not silent) when cardinality ≥ 2 (a torn/mixed window). All three helpers operate purely against the IS chain — no OD ledger, no signing backend — per §7.7's explicit scope boundary; they are the IS-side evidence a CP-owned consumer (the `B-33`-scoped `verify_rotation_6_steps` extension) composes with the OD-join at the impl leg, NOT the join itself.

**Acceptance criterion (non-goal — explicit scope fence).** (8) This unit MUST NOT implement `verify_rotation_6_steps`'s 3-step extension, the composition-root-injected OD-join evidence DTO, or any check against the B-36 `AwsKmsSigningBackend` key-identity mapping — all three are CP-owned per the fork's §2 point 4 axis-import-direction reasoning and are decomposed at the separate CP-axis impl leg. A PR closing this unit that also touches `harness-cp/**` has exceeded this unit's scope.

**Tests (mutation-probed per PD-8).**

- **Byte-identity control:** `test_pre_v1_12_entry_canonicalizes_byte_identically_with_none_rotation_correlation_id` (mutation probe: including the key when `None` breaks the byte-identity assertion against the pre-v1.12 fixture).
- **Hash-coverage witness:** `test_rotation_correlation_id_participates_in_response_hash` (mutation probe: reverting the omit-when-`None`-else-include canonicalization branch to always-omit makes a tampered id undetectable — the witness must fail).
- **Malformed-UUID rejection witness:** `test_rotation_correlation_id_rejects_non_uuid_present_value` (mutation probe: removing the construction-time validation lets `rotation_correlation_id="not-a-uuid"` construct silently — the witness must fail; a canonical-form UUID and `None` both still construct).
- **Empty-window vacuous-pass guard witness:** `test_rotation_window_check_fails_on_empty_sequence` (mutation probe: a check that runs presence/uniqueness directly against `[]` without the non-emptiness guard passes vacuously — the witness must fail; asserts the empty-sequence failure fires BEFORE any per-entry predicate).
- **Presence-invariant witness:** `test_rotation_window_presence_check_fails_on_a_none_entry_in_window` (mutation probe: a presence check that ignores a `None` member passes when it should fail).
- **Uniqueness-invariant witness:** `test_rotation_window_uniqueness_check_fails_on_two_distinct_ids_in_window` (mutation probe: a uniqueness check that only inspects the first non-`None` value passes a torn window when it should fail).
- **Round-trip witness:** `test_rotation_correlation_id_serializes_and_deserializes_through_jsonl_line` (mirrors the §5.1/§5.4 JSONL round-trip precedent at `_serialize_entry`/`_deserialize_entry`).

**Notes.** (a) **No auxiliary type, no carrier-home deferral.** Unlike U-IS-19's `BranchMetadata`, `rotation_correlation_id` is a bare scalar directly on `StateLedgerEntry`/`EntryPayload` — there is no separate record type whose residence (`harness-core` vs `harness-is`) needs deciding. (b) **Producer/consumer both deferred to the impl leg.** The write-cadence (which entries within a claimed rotation window carry the id; whether every window entry or only its boundary entries) is the CP rotation orchestration's concern at the impl leg, mirroring the §5.4 "which entry carries `terminal_status`" deferral pattern. (c) **UUID validation mechanism, not the requirement, left to impl.** IS spec v1.12 §5.6's field table REQUIRES rejection of a present-but-malformed value at construction (AC #4 above pins this); only the CONCRETE mechanism (stdlib `uuid.UUID(value)` parse-then-reject vs a validated `Identifier`-style newtype vs a Pydantic field validator) is left to impl discretion, the same latitude §5's "Deferred to implementation discretion" footer extends to other identifier fields' concrete representation.

---

## §3 Dependency graph

### §3.1 Dependency-graph delta (v2.8)

| Operation | Detail |
|---|---|
| NEW node | U-IS-20 (`Depends on: (none)` — foundational carrier) |
| NEW within-axis edge | (none) — U-IS-20 is a leaf-foundational carrier; no existing IS unit depends on it at the IS axis (the consumer is cross-axis, declared from the consumer side at the impl leg) |
| NEW cross-axis INBOUND edge | DEFERRED to the CP-axis impl leg (not declared at this spec-leg-only arc) — when opened, that leg's rotation-orchestration + verifier units will declare an edge into U-IS-20, mirroring the U-CP-84 → U-IS-19 precedent |

### §3.2 Acyclicity preservation + IS-0-outbound cycle guard

**Cycle guard (load-bearing invariant).** U-IS-20 declares `Depends on: (none)` and — like every IS-axis unit — has **ZERO outbound cross-axis edge**: no U-IS-* depends on any U-CP-* or U-RT-* unit. The IS axis is consumer-most-upstream (the same invariant that scopes U-IS-20's own AC #6 non-goal fence). The eventual cross-axis edge from the CP-axis impl leg's units into U-IS-20 (CP/RT → IS) cannot close a cycle with any IS-internal edge (U-IS-20 has none outbound) — exactly the U-IS-19 precedent.

IS-axis internal DAG (v2.7 units) PRESERVED VERBATIM plus the one foundational leaf U-IS-20. Acyclicity preserved at the IS-axis intra-axis layer.

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.8)

| Spec contract | Atomic unit |
|---|---|
| IS spec v1.12 C-IS-05 §5.6 (`rotation_correlation_id` D-derivative sidecar carrier + omit-when-`None` canonicalization) | **U-IS-20** (NEW) |
| IS spec v1.12 C-IS-07 §7.7 (presence + uniqueness read-side invariants over the carrier) | **U-IS-20** (NEW) |
| IS spec v1.12 C-IS-06 §6.1 (canonical-payload participation when non-`None`; construction discipline unchanged) | U-IS-20 (contributes the omit-when-`None` inclusion path; the §6 hash-chain construction unit is unchanged) |

All other rows PRESERVED VERBATIM from v2.7 §4. ZERO contract-coverage gap at the IS axis. (The cross-axis producer + consumer of `rotation_correlation_id` — the CP rotation orchestration and `verify_rotation_6_steps`'s extension — are covered at the separate CP-axis impl leg, not yet opened.)

---

## §5 Auxiliary-type carrier audit

UNCHANGED from v2.7 §5 — U-IS-20 introduces no auxiliary record type (see Note (a) above).

---

## §6 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.8 (delta over v2.7) |
| Authored at | Phase 7 — `B-33-A` spec leg (2026-07-22) |
| Authoring authority | IS spec v1.12 (C-IS-05 §5.6 + C-IS-07 §7.7, `Spec_Information_Substrate_v1.md`) + `.harness/class_1_fork_b33_rotation_correlation_carrier.md` (RATIFIED 2026-07-21, OPTION A AS RECOMMENDED) |
| Net delta | ONE NEW unit (U-IS-20, `Depends on: (none)`, foundational); ZERO amended units; ZERO new auxiliary type; +2 coverage rows (C-IS-05 §5.6 + C-IS-07 §7.7); ZERO IS-outbound edge |
| Siblings (same arc) | None — SPEC-LEG ONLY (mirrors `B-59-A` PR #1080; the CP-axis impl leg is a separate, not-yet-opened PR) |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
