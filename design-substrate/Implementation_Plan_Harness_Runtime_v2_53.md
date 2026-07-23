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

1. **(Runtime spec v1.105 §13.6 row 2 — the adapter.)** A NEW adapter class implements the CP-owned `RotationPairEvidenceProvider` Protocol's `evidence_for(correlation_id: str) -> RotationPairEvidence` by calling OD's `find_rotation_pair_evidence(ledger, correlation_id)` and mapping the result to the CP-owned `RotationPairEvidence` DTO (field-for-field, INCLUDING the `signatures_verified: bool` field added at OD spec v1.35 §24.8 row 8a / CP spec v1.105 §2 row 1 — out-of-family review round-2 [P1]; the adapter maps it verbatim, it never hardcodes `True` regardless of what OD returns — same shape, distinct type, no `harness_od` import anywhere in `harness-cp`, mirroring U-RT-138's own `AuditWalkVerifier` adapter mapping discipline). Witness: `test_rt147_adapter_maps_signatures_verified_field_verbatim_never_hardcoded` (mutation probe: hardcoding `signatures_verified=True` in the adapter's mapping passes every OTHER RT-147 test — since OD always returns `False` in this delta and no test fixture depends on the CP-side value being accurate — but fails this dedicated witness, which asserts the adapter's output tracks an OD-side stub returning `True` for one fixture and `False` for another).
2. **(Exception translation.)** OD's `RotationPairIntegrityBreach` raised by `find_rotation_pair_evidence` is caught and RE-RAISED as the CP-owned same-named `RotationPairIntegrityBreach` type, message-preserving (never silently swallowed, never folded into a "false" evidence result). Any OD-side ledger-load/lookup infrastructure failure (not a tamper signal) is wrapped in the CP-owned `RotationPairEvidenceUnavailableError`. Any other raise from the OD accessor (a `TypeError`/`KeyError`/programming error) PROPAGATES UNWRAPPED as a defect — the adapter performs NO blanket exception handling.
3. **(Adapter + factory ONLY — NO production call site, out-of-family review [P2] correction.)** Unlike U-RT-138 (which injects `AuditWalkVerifier` into a REAL existing `harness-inspect` invocation of the §20.3.1 walk), `verify_rotation_6_steps` has ZERO production callers today (CP plan v2.41 U-CP-45 criterion #6's explicit scope fence) — there is NO live call site to inject this adapter into without either constructing it dead (unused) or adding the very production caller both this arc and the sibling CP/Runtime deltas explicitly defer. This unit therefore builds ONLY: the adapter class + a composition-root FACTORY function constructing it from the same operator-facing inputs §13.6 declares (available for a FUTURE caller to use, not invoked by any caller THIS unit adds) + the required `key_identity_resolver` construction (criterion #4). Wiring the adapter into a real invocation of `verify_rotation_6_steps` is EXPLICITLY OUT OF SCOPE here — it lands together with whatever future arc adds the real production caller (mirroring the fork's own "no real `execute_key_rotation` write path" fence).
4. **(Physical-key-distinctness input threading — REQUIRED at the CP-side gate, NOT a factory-construction precondition, out-of-family review round-3 [P2] wording correction.)** The factory (criterion #3) NEVER RAISES for an absent `key_identity_resolver` — it always constructs the adapter successfully, mirroring how an absent `evidence_provider` never raises anywhere else in this arc. "Required" describes the DOWNSTREAM CP-side gate (CP spec v1.105 §2 row 5 / CP plan v2.41 U-CP-44 criterion #2): a deployment whose `SigningBackend` exposes no physical-identity mapping gets a successfully-CONSTRUCTED adapter pairing that structurally CANNOT reach a `succeeded=True` `PROBE_VERIFY_AT_READ` — the incompleteness is enforced at the CP-side consumption point, not by refusing construction here. This unit does NOT fabricate a resolver where none exists, and does NOT silently degrade to skipping the attestation.

**Tests (mutation-probed per PD-8):** **Reachability witness (out-of-family review round-3 [P1] correction — the ONLY way to prove the success path is real, since no shipped provider can produce it):** `test_rt147_adapter_with_stub_provider_forcing_signatures_verified_true_drives_probe_verify_at_read_success` (constructs the adapter's DTO-mapping logic against a STUB `RotationPairEvidenceProvider` returning `signatures_verified=True` — proving `verify_rotation_6_steps`'s gate composition is reachable in principle — mutation probe: hardcoding the CP-side gate to ignore `signatures_verified` passes this test trivially and must be caught by U-CP-45's own dedicated gate witness, not this one). **Real-OD-accessor witness (absent/tampered paths only — a genuine PASS through the real accessor is NOT reachable in this delta, per OD spec v1.35 §24.8 row 8a):** `test_rt147_adapter_real_od_find_rotation_pair_evidence_absent_and_tampered_paths` (constructs the adapter via the factory and calls `verify_rotation_6_steps` directly with it against the REAL `find_rotation_pair_evidence` — an ABSENT pair drives the step to the explicit-incomplete failure, never a silent pass; a TAMPERED pair drives a `RotationPairIntegrityBreach` raise through the adapter unchanged — mutation probe: reverting the adapter's exception re-raise to a swallow-and-return-false makes the tampered-pair case silently report `succeeded=False` instead of raising, failing the test; a VALID structural pair through the real accessor is asserted to reach the explicit "structural evidence present, signature verification not available" INCOMPLETE disposition, never `succeeded=True` — mutation probe: hardcoding the adapter's mapped `signatures_verified` to `True` for a valid pair passes this test incorrectly and must be rejected). **Independence witness:** `test_rt147_and_rt138_factories_independent` (constructing this unit's adapter via its factory does not require the audit-walk verifier's inputs, and vice versa). **Resolver-absent-still-constructs witness:** `test_rt147_factory_without_key_identity_mapping_still_constructs_an_adapter_pairing_that_cannot_succeed` (mutation probe: a factory that RAISES on an absent resolver, or one that silently omits the downstream incompleteness, both fail this test — the factory must construct successfully AND the resulting pairing must be structurally incapable of a `succeeded=True` gate result).

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
