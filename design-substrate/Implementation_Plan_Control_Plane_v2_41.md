# Implementation Plan: Control Plane — v2.41 (delta over v2.40)

*v2.41 is the CP plan leg of the RATIFIED **B-33 rotation-correlation carrier arc** (`.harness/class_1_fork_b33_rotation_correlation_carrier.md`, **RATIFIED 2026-07-21 — operator selected OPTION A**), absorbing **CP spec v1.105** (`Spec_Control_Plane_v1_105.md` — AMENDED §20.3.1 row 7 + NEW §20.3.2). The two spec surfaces are homed at the SAME co-covering pair v2.38 already amended for the sibling §20.3.1 audit-walk arc — **U-CP-45** (rotation + 6-step verification; the `verify_rotation_6_steps` extension itself) and **U-CP-44** (F5 signing-key resolution; the physical-key-distinctness comparator, since it consults the SAME key-identity surface U-CP-44 already owns) — **ZERO new atomic units**. Unit count unchanged (102 — the v2.40 total). All sections except the §0 change note and the two unit amendments + coverage delta below are PRESERVED VERBATIM from v2.40 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.40 → v2.41)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_40.md` (v2.40 — the B-65 apply arc's CP plan leg; U-CP-85 amendment).

### §0.2 Revision context — CP spec v1.105 absorption

Per the fork's ratification-gate plan-delta clause: `verify_rotation_6_steps`'s existing coverage at U-CP-45 (v2.38's §3 amendment, shared with U-CP-44 as the §20.3.1 co-covering pair) pins the pre-B-33 acceptance criteria (row 7's "backend-aware implementation remains B-33's scope" deferral, restated verbatim at U-CP-45's v2.38 acceptance row "(§3 row 7.) Rotation-pair steps 3–6 PRESERVED VERBATIM; their backend-aware implementation remains B-33's scope — not this arc.") — stale against CP spec v1.105 §1, which retires that deferral. This delta amends BOTH co-covering units: U-CP-45 gains the `verify_rotation_6_steps` extension's own acceptance criteria; U-CP-44 gains the physical-key-distinctness comparator's acceptance criteria (a NEW capability of the F5 signing-key resolution surface, consulted BY U-CP-45's extension but logically owned where the other key-identity surfaces live).

### §0.3 Sections revised

§0 (this change note); §1 (U-CP-45 amendment); §2 (U-CP-44 amendment); §3 (coverage delta). All other sections — every other `U-CP-NN` body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.40.

### §0.4 Scope discipline

AMENDED-unit scope only. ZERO new atomic units; ZERO new contract IDs (C-CP-20 already exists — §20.3.2 is a NEW subsection under it, same contract). ZERO DAG topology change beyond the cross-axis co-land notes below (no new edges). Per the fork's explicit hard scope fence (§3): this delta builds the verifier + injected-evidence plumbing + test-consumer witnesses ONLY — it does NOT build the real `execute_key_rotation` write path (the other five `RotationVerificationStep` steps besides the two extended here remain `B-22`-gated simulated narration; a real production caller of `verify_rotation_6_steps` is a separate later arc, per the fork's own §3 sequencing note that the write-path producer gap is bigger than it looks and explicitly out of THIS leg).

---

## §1 U-CP-45 amendment — `verify_rotation_6_steps` OD-anchored rotation-boundary extension (CP v1.105 §1)

The v2.38 U-CP-45 body (`Implements: … C-CP-20 §20.3, §20.3.1`; the §3 row-7 acceptance criterion "Rotation-pair steps 3–6 PRESERVED VERBATIM; their backend-aware implementation remains B-33's scope — not this arc") is PRESERVED VERBATIM as a HISTORICAL record of the prior deferral; v2.41 SUPERSEDES that ONE criterion (retiring the deferral it named) and adds:

**Implements (addition):** + C-CP-20 §20.3.1 row 7 (AMENDED at CP v1.105 §1 — retires the B-33 deferral) + C-CP-20 §20.3.2 (NEW at CP v1.105 §2 — the `RotationPairEvidenceProvider` Protocol + `RotationPairEvidence` DTO + `RotationPairIntegrityBreach` + `RotationPairEvidenceUnavailableError`, consumed by this unit's extension).

**Superseded criterion:** the v2.38 acceptance row *"(§3 row 7.) Rotation-pair steps 3–6 PRESERVED VERBATIM; their backend-aware implementation remains B-33's scope — not this arc"* is RETIRED — this IS that implementation, at the two named steps below (steps 3-6's OTHER members — `STAGE_NEW_KEY`, `ROTATE_SIGNING_TO_NEW`, `RETIRE_OLD_KEY` — remain simulated per `B-22`'s unrelated deployment-surface scope; only `WRITE_DUAL_VERIFY_ENTRY` and `PROBE_VERIFY_AT_READ` gain real behavior).

**Acceptance criteria (v2.41 additions):**

1. **(CP v1.105 §1 — `WRITE_DUAL_VERIFY_ENTRY` presence/uniqueness.)** `verify_rotation_6_steps` gains optional keyword-only parameters `rotation_correlation_id: str | None = None` and `evidence_provider: RotationPairEvidenceProvider | None = None`. When BOTH are supplied, `WRITE_DUAL_VERIFY_ENTRY` calls the ALREADY-LANDED `harness_is.rotation_window_verification.verify_rotation_window` (IS spec v1.12 §7.7, U-IS-20) over `audit_ledger_entries` — a `VALID` result (non-empty, every entry's `rotation_correlation_id` present and identical) makes the step succeed; any `INVALID` result (empty window / presence failure / uniqueness failure) makes the step FAIL with the specific `RotationWindowFailureType` named in the detail.
2. **(CP v1.105 §1 — `PROBE_VERIFY_AT_READ` OD-anchored evidence.)** When both new parameters are supplied, `PROBE_VERIFY_AT_READ` calls `evidence_provider.evidence_for(rotation_correlation_id)`. `pair_present=True` → step succeeds, detail names the returned `outgoing_key_period`/`incoming_key_period`. `pair_present=False` → step FAILS with an EXPLICIT "no OD-anchored evidence for this rotation boundary" detail — distinct wording from a `RotationPairIntegrityBreach` raise (which propagates as an exception, not a `StepResult`, per criterion #4 below). Witness: `test_probe_verify_at_read_pair_present_true_succeeds_with_periods_in_detail` + `test_probe_verify_at_read_pair_present_false_fails_with_explicit_absence_detail` (mutation probe: treating `pair_present=False` as `succeeded=True` fails the second test).
3. **(Sequential-halt gate extended.)** `ROTATE_SIGNING_TO_NEW` and `RETIRE_OLD_KEY` are gated on ALL THREE of `{VERIFY_HASH_CHAIN_LINK, WRITE_DUAL_VERIFY_ENTRY, PROBE_VERIFY_AT_READ}` succeeding (extended from the pre-v1.105 single-gate-on-hash-chain-link discipline) — any one of the three failing blocks both downstream steps with the existing `blocked` detail shape. Witness: `test_write_dual_verify_entry_failure_blocks_rotate_and_retire` + `test_probe_verify_at_read_failure_blocks_rotate_and_retire` (mutation probe: removing either from the gate lets `ROTATE_SIGNING_TO_NEW` succeed despite the upstream failure).
4. **(Fail-loud tamper propagation — codex-anticipated P1.)** A `RotationPairIntegrityBreach` raised by the injected `evidence_provider` (OD-detected cryptographic/structural tamper, translated by the Runtime adapter per Runtime plan v2.53 U-RT-147) PROPAGATES as a raised exception out of `verify_rotation_6_steps` — it is NEVER caught and folded into a `StepResult(succeeded=False)`, mirroring the codebase's existing fail-loud discipline for `RotationPairIntegrityBreach`/`HashChainBreach`/`AuditSignatureInvalid` elsewhere. A `RotationPairEvidenceUnavailableError` (infrastructure availability, never a verdict) likewise PROPAGATES unwrapped — the caller re-runs once availability is restored, mirroring §20.3.1 row 5's availability-is-not-a-verdict posture for the audit walk. Witness: `test_evidence_provider_integrity_breach_propagates_uncaught` + `test_evidence_provider_unavailable_error_propagates_uncaught` (mutation probe: wrapping either in a try/except that returns a failed `StepResult` instead of re-raising fails both tests).
5. **(Absent-parameter posture — deliberately not byte-compatible, per CP spec v1.105's own justification.)** When EITHER `rotation_correlation_id` or `evidence_provider` is absent, `WRITE_DUAL_VERIFY_ENTRY` and `PROBE_VERIFY_AT_READ` report `succeeded=False` with an EXPLICIT incomplete detail — NEVER the pre-v1.105 simulated `succeeded=True`. Witness: `test_absent_correlation_id_or_evidence_provider_reports_explicit_incomplete_not_simulated_true` (mutation probe: reverting to the pre-v1.105 unconditional `succeeded=True` default for these two steps passes a stale assertion and fails this one).
6. **(Scope fence — explicit non-goal, per fork §3.)** This unit does NOT build a real production caller of `verify_rotation_6_steps`/`execute_key_rotation` — `execute_key_rotation`'s own `rotation_complete`/`rotation_state_partial` computation (`all(s.succeeded for s in steps)`) is UNCHANGED and automatically reflects the extended step set; no new call site is wired in this arc.

**Tests (mutation-probed per PD-8):** the 6 witnesses named at criteria #2-#5 above.

---

## §2 U-CP-44 amendment — physical-key-distinctness boundary attestation (CP v1.105 §2)

The existing U-CP-44 body (F5 signing-key resolution, `Implements: C-CP-20 §20.3.1`) is PRESERVED VERBATIM; v2.41 adds:

**Implements (addition):** + C-CP-20 §20.3.2 (NEW at CP v1.105 §2 — the physical-key-distinctness comparator).

**Acceptance criteria (v2.41 additions):**

1. **(CP v1.105 §2 row 5 — the comparator.)** A NEW optional `key_identity_resolver` Protocol (`physical_identity_for(key_id: str) -> str`) is declared alongside the existing F5 signing-key resolution surface. `verify_rotation_6_steps`'s `PROBE_VERIFY_AT_READ` step (U-CP-45 above), WHEN a resolver is supplied, additionally confirms an evidence-confirmed pair's `outgoing_key_id` and `incoming_key_id` resolve to DIFFERENT physical identities — a same-identity resolution RAISES `RotationBoundaryPhysicalKeyCollisionError` (a NEW, DISTINCT failure mode from `RotationPairIntegrityBreach`: the OD-side pair may be well-formed while the physical keys are the same underlying material under two labels). Witness: `test_physical_key_distinctness_different_identities_passes` + `test_physical_key_distinctness_same_identity_raises_collision_error` (mutation probe: comparing key_id STRINGS instead of resolved physical identities passes the collision case and fails the second test).
2. **(Resolver absent — skip, not fail.)** `key_identity_resolver` defaults `None`; absent, the attestation is SKIPPED (not failed) — not every deployment's `SigningBackend` exposes a physical-identity mapping (ADR-F5 concrete-backend-selection deferral). Witness: `test_physical_key_distinctness_resolver_absent_skips_attestation_step_still_succeeds`.
3. **(Reference implementation shape, non-binding home decision.)** `AwsKmsSigningBackend.key_arns` (ADR-D8, B-36) is the reference `key_identity_resolver` implementation available today (ARN as physical identity) — this criterion does not mandate a specific module location for the concrete adapter; the Protocol is the binding contract.

**Tests (mutation-probed per PD-8):** the 3 witnesses named above.

---

## §3 Coverage matrix delta (v2.40 → v2.41)

| Contract surface | Units covering (delta) |
|---|---|
| C-CP-20 §20.3.1 row 7 (AMENDED at CP v1.105 §1 — retires B-33 deferral) | **U-CP-45 (amended)** (consuming IS spec v1.12 §7.7 + OD plan v2.30 U-OD-56 cross-axis) |
| C-CP-20 §20.3.2 (NEW at CP v1.105 §2) | **U-CP-45 (amended, the Protocol consumption)** + **U-CP-44 (amended, the physical-key-distinctness comparator)** |

DAG: unchanged topology; cross-axis co-land pin recorded (not a DAG edge): U-CP-44/U-CP-45 ⊕ U-RT-147 (the composition-root adapter) land in the one B-33 impl arc, mirroring the U-CP-44/45 ⊕ U-RT-138 co-land pin the sibling §20.3.1 audit-walk arc already established.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_41.md` (delta over v2.40) |
| Authored at | Phase 7 — B-33 rotation-correlation carrier arc, spec+plan leg (2026-07-23) |
| Authoring authority | CP spec v1.105 (`Spec_Control_Plane_v1_105.md`) + `.harness/class_1_fork_b33_rotation_correlation_carrier.md` (RATIFIED 2026-07-21, Option A) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_40.md` (v2.40 — B-65 apply arc) |
| Siblings (same arc) | `Implementation_Plan_Operational_Discipline_v2_30.md` + `Implementation_Plan_Harness_Runtime_v2_53.md` + `Cross_Axis_Composition_Document_v2_22.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
