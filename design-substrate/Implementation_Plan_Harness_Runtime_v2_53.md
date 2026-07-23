# Implementation Plan: Harness Runtime — v2.53 (delta over v2.52)

*v2.53 is the Runtime plan leg of the RATIFIED **B-33 rotation-correlation carrier arc** (`.harness/class_1_fork_b33_rotation_correlation_carrier.md`, **RATIFIED 2026-07-21 — operator selected OPTION A**), absorbing **Runtime spec v1.104 → v1.105** (NEW §13.6 — rotation-pair-evidence composition-root inputs). This delta authors **ONE NEW atomic unit, U-RT-147** (the composition-root adapter over OD spec v1.35 §24.8's `find_rotation_pair_evidence`, injected into the CP spec v1.105 `RotationPairEvidenceProvider` Protocol) — mirroring U-RT-138's shape for a DIFFERENT injected verifier (rotation-pair evidence, not the audit walk). All sections except the §0 change note and the NEW U-RT-147 body below are PRESERVED VERBATIM from v2.52 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.52 → v2.53)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_52.md` (v2.52 — the B-59 apply arc's Runtime plan leg; NEW U-RT-146).

### §0.2 Revision context — Runtime spec v1.105 absorption

The B-33 arc's CP-owned `RotationPairEvidenceProvider` Protocol (CP spec v1.105 §2) needs a concrete adapter over the OD-owned `find_rotation_pair_evidence` accessor (OD spec v1.35 §24.8) — the SAME composition-root pattern U-RT-138 already established for `AuditWalkVerifier`/`find_rotation_pair_evidence`'s sibling `verify_rotation_pairs`-family surface, but a DISTINCT adapter for a DISTINCT Protocol (the two injected verifiers are wired independently, per Runtime spec v1.105 §13.6's own "why a separate section" framing).

### §0.3 Sections revised

§0 (this change note); §1 (the NEW U-RT-147 body). All other sections — every existing `U-RT-NN` body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.52.

### §0.4 Scope discipline

ADDITIVE — ONE NEW atomic unit (U-RT-147), next free Runtime unit ID after v2.52's U-RT-146. ZERO amended units; ZERO new contract IDs. Per the fork's explicit hard scope fence (§3, mirrored at the CP plan v2.41 §0.4 scope discipline): this unit builds the adapter + its integration witness ONLY — it does NOT wire a real production caller of `verify_rotation_6_steps` (no new call site in the runtime lifecycle composers).

---

## §1 U-RT-147 — rotation-pair-evidence composition-root adapter (Runtime spec v1.105 §13.6)

**Implements:** Runtime spec v1.105 NEW §13.6 (the rotation-pair-evidence composition-root inputs + wiring-site declaration). Verification SEMANTICS OD-owned (OD spec v1.35 §24.8 — cross-referenced; API at OD plan v2.30 U-OD-56). Injection-target Protocol CP-owned (CP spec v1.105 §2 — cross-referenced; declared at CP plan v2.41 U-CP-44/U-CP-45).

**Depends on:** [U-RT-138 (cross-axis-adjacent: the sibling composition-root adapter for `AuditWalkVerifier` — this unit extends the SAME composition-root wiring surface with a second, independent adapter, not a modification of U-RT-138's own adapter), U-OD-56 (cross-axis: OD — the `find_rotation_pair_evidence` accessor this adapter wraps), U-CP-44/U-CP-45 (cross-axis: CP — the `RotationPairEvidenceProvider` Protocol + `RotationPairEvidence`/exception types this unit's adapter implements; co-land)].

**Files affected (logical):** the SAME composition-root module U-RT-138 wires (`harness-runtime`'s admin/inspect composition surface) — this unit adds a SECOND adapter class alongside U-RT-138's `AuditWalkVerifier` adapter, NOT a modification of it.

**Acceptance criteria:**

1. **(Runtime spec v1.105 §13.6 row 2 — the adapter.)** A NEW adapter class implements the CP-owned `RotationPairEvidenceProvider` Protocol's `evidence_for(correlation_id: str) -> RotationPairEvidence` by calling OD's `find_rotation_pair_evidence(ledger, correlation_id)` and mapping the result to the CP-owned `RotationPairEvidence` DTO (field-for-field — same shape, distinct type, no `harness_od` import anywhere in `harness-cp`, mirroring U-RT-138's own `AuditWalkVerifier` adapter mapping discipline).
2. **(Exception translation.)** OD's `RotationPairIntegrityBreach` raised by `find_rotation_pair_evidence` is caught and RE-RAISED as the CP-owned same-named `RotationPairIntegrityBreach` type, message-preserving (never silently swallowed, never folded into a "false" evidence result). Any OD-side ledger-load/lookup infrastructure failure (not a tamper signal) is wrapped in the CP-owned `RotationPairEvidenceUnavailableError`. Any other raise from the OD accessor (a `TypeError`/`KeyError`/programming error) PROPAGATES UNWRAPPED as a defect — the adapter performs NO blanket exception handling.
3. **(Wiring site — same composition root as U-RT-138, a second independent adapter.)** The adapter is constructed and injected at the SAME production composition-root site U-RT-138 already wires (the `harness-inspect`/admin composition surface) — WHEN the deployment configures the rotation-pair-evidence inputs (Runtime spec v1.105 §13.6 row 1, the signing-key identity mapping); the two adapters (this unit's, and U-RT-138's `AuditWalkVerifier` adapter) are constructed and injected INDEPENDENTLY — configuring one does not require configuring the other.
4. **(Physical-key-distinctness input threading — optional.)** WHEN the deployment's configured `SigningBackend` exposes a key-identity mapping (e.g. `AwsKmsSigningBackend.key_arns`), the composition root ALSO constructs the CP-owned `key_identity_resolver` (CP plan v2.41 U-CP-44) and threads it to `verify_rotation_6_steps` alongside this unit's `evidence_provider` — absent such a mapping, the physical-key-distinctness attestation is SKIPPED per CP spec v1.105 §2 row 5's own absent-resolver posture (this unit does not fabricate a resolver where none exists).

**Tests (mutation-probed per PD-8):** **Integration witness — real OD accessor through the adapter through the CP step:** `test_rt147_adapter_real_od_find_rotation_pair_evidence_through_verify_rotation_6_steps` (a genuinely valid OD-side pair drives `PROBE_VERIFY_AT_READ` to succeed through the FULL real chain — OD `find_rotation_pair_evidence` → adapter → CP `verify_rotation_6_steps`; an ABSENT pair drives the step to the explicit-incomplete failure, never a silent pass; a TAMPERED pair drives a `RotationPairIntegrityBreach` raise through the adapter unchanged — mutation probe: reverting the adapter's exception re-raise to a swallow-and-return-false makes the tampered-pair case silently report `succeeded=False` instead of raising, failing the test). **Independence witness:** `test_rt147_and_rt138_adapters_wired_independently` (configuring only the rotation-pair-evidence inputs constructs this unit's adapter without requiring the audit-walk verifier inputs, and vice versa).

**Rollback boundary:** revert the adapter + its composition-root wiring; `verify_rotation_6_steps` reverts to the CP plan v2.41 absent-parameter posture (explicit incomplete on the two extended steps) for every caller — no regression below that baseline (there is no pre-v2.53 real adapter to fall back to).

---

## §2 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_53.md` (delta over v2.52) |
| Authored at | Phase 7 — B-33 rotation-correlation carrier arc, spec+plan leg (2026-07-23) |
| Authoring authority | Runtime spec v1.105 (`Spec_Harness_Runtime_v1.md` §13.6) + `.harness/class_1_fork_b33_rotation_correlation_carrier.md` (RATIFIED 2026-07-21, Option A) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_52.md` (v2.52 — B-59 apply arc) |
| Siblings (same arc) | `Implementation_Plan_Operational_Discipline_v2_30.md` + `Implementation_Plan_Control_Plane_v2_41.md` + `Cross_Axis_Composition_Document_v2_22.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
