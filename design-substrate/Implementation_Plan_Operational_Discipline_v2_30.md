# Implementation Plan: Operational Discipline — v2.30 (delta over v2.29)

*v2.30 is the OD plan leg of the RATIFIED **B-33 rotation-correlation carrier arc** (`.harness/class_1_fork_b33_rotation_correlation_carrier.md`, **RATIFIED 2026-07-21 — operator selected OPTION A**), absorbing **OD spec v1.35** (`Spec_Operational_Discipline_v1_35.md` — NEW §24.8 per-correlation-id rotation-pair evidence accessor). This delta authors **ONE NEW atomic unit, U-OD-56**, for TWO reasons found at grounding: (1) `sign_rotation_pair` + `verify_rotation_pairs` (OD spec v1.31 §24.7, landed at PR #938 via the standalone Phase-7 `B-AUDIT-KEY-ROTATION-RUNTIME` arc) have NEVER been covered by any canonical `U-OD-NN` unit — grepped every `Implementation_Plan_Operational_Discipline_v2*.md` file through the v2.29 head, zero hits on `verify_rotation_pairs`/"rotation pair"/§24.7 tied to a plan unit; this is a real plan-coverage gap, not an unlucky search, and U-OD-56 backfills it retroactively (the code is already-landed and already-tested — this unit documents existing acceptance, it does not re-implement anything); (2) the NEW §24.8 accessor is genuinely new work needing its own acceptance criteria. All sections except the §0 change note and the NEW U-OD-56 body + coverage delta below are PRESERVED VERBATIM from v2.29 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.29 → v2.30)

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_29.md` (v2.29 — the B-51/B-52/B-54 arc's OD plan leg; U-OD-30 amendment + NEW U-OD-55).

### §0.2 Revision context — OD spec v1.35 absorption + retroactive §24.7 coverage backfill

Per the fork's ratification-gate plan-delta clause: the B-33 arc's OD-owned surface is NEW §24.8, but grounding at open surfaced that its natural home — the §24.7 `verify_rotation_pairs`/`sign_rotation_pair` pair — carries NO existing `U-OD-NN` unit at all (landed via the standalone `B-AUDIT-KEY-ROTATION-RUNTIME` arc plan, `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §2, NOT the canonical `Implementation_Plan_Operational_Discipline_v2.x` chain). Authoring ONE unit that BOTH backfills the already-landed §24.7 surface's acceptance criteria AND carries the NEW §24.8 accessor's acceptance criteria keeps the coverage matrix honest (a `U-OD-NN` citation now resolves for §24.7, closing the gap) without inventing a second unit for content that is one cohesive module (`multi_tenant_trace_separation_and_audit_ledger.py`'s rotation-pair surface).

### §0.3 Sections revised

§0 (this change note); §1 (the NEW U-OD-56 body); §2 (coverage delta). All other sections — every existing `U-OD-NN` body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.29.

### §0.4 Scope discipline

ADDITIVE — ONE NEW atomic unit (U-OD-56), next free OD unit ID after v2.29's U-OD-55 (verified by grep across the full v2.1..v2.29 chain: highest existing is U-OD-55). ZERO amended units; ZERO new contract IDs (C-OD-24 already exists — §24.8 is a NEW subsection under it, same contract). ZERO DAG topology change beyond the one new node (in-degree per its own `Depends on` below).

---

## §1 U-OD-56 — rotation-pair dual-signature write path + per-correlation-id evidence accessor (C-OD-24 §24.7 backfill + NEW §24.8)

**Implements:** C-OD-24 §24.7 (`sign_rotation_pair` + `verify_rotation_pairs` — ALREADY LANDED, PR #938, retroactive coverage backfill per §0.2 above) + C-OD-24 §24.8 (NEW at OD spec v1.35 — `find_rotation_pair_evidence` + `RotationPairEvidence`).

**Depends on:** [U-OD-00 (the general audit-ledger payload + `AuditPayload`/`AuditLedgerEntry`/`compute_entry_hash` surface C-OD-24 is anchored to), U-OD-30 (cross-axis-adjacent: the same-module `sign_audit_entry`/`SigningBackend` seam `sign_rotation_pair` reuses for per-sibling signing)].

**Files affected (logical):** `harness-od/src/harness_od/multi_tenant_trace_separation_and_audit_ledger.py` (existing `sign_rotation_pair` / `verify_rotation_pairs`; NEW `RotationPairEvidence` + `find_rotation_pair_evidence` + the extracted shared per-pair-check helper).

**Acceptance criteria — §24.7 backfill (already satisfied by the landed PR #938 code; restated here as the unit's own acceptance record, not re-verified from scratch):**

1. `sign_rotation_pair` produces a co-signed sibling pair under consecutive `key_period` values and differing `key_id` values, both entries sharing one `audit.rotation_correlation_id`, the later-period sibling's `payload.prior_entry_hash` extending the earlier-period sibling's `entry_hash`.
2. `verify_rotation_pairs(ledger)` walks every distinct rotation-correlation value in the supplied ledger, raising `RotationPairIntegrityBreach` on the first violation of: exactly-2-siblings; per-entry recomputed-hash match; consecutive key periods; differing key ids; chain-hash continuity across the pair; a `uuid.UUID(...)`-parseable correlation attribute. **Precision correction (out-of-family review round-4 [P2]):** the landed check (`multi_tenant_trace_separation_and_audit_ledger.py:610`) is `uuid.UUID(correlation_id)` alone — it accepts any string `uuid.UUID` can PARSE (including non-canonical forms like uppercase hex or a missing-hyphens 32-hex-digit string), not a strict round-trip `str(uuid.UUID(value)) == value` canonical-form check. This backfill criterion is restated to describe the LANDED behavior accurately rather than overclaim a "canonical" guarantee the code doesn't enforce; whether to tighten the landed check to reject non-canonical-but-parseable forms is a SEPARATE, OUT-OF-THIS-LEG pre-existing gap in PR #938's code (this delta is spec+plan-only and does not touch it) — registered at `.harness/class_1_fork_b33_rotation_correlation_carrier.md`'s progress note for a future arc's disposition, not silently assumed closed.
3. Entries with no `audit.rotation_correlation_id` attribute are ignored by `verify_rotation_pairs` — non-rotation entries are unaffected.

**Acceptance criteria — NEW §24.8 accessor (this delta's genuinely new scope):**

4. `find_rotation_pair_evidence(ledger, correlation_id)` scopes its check to ONLY entries carrying the supplied `correlation_id` — entries under a different or absent correlation id never raise and never affect the result (per-id scoping distinct from §24.7's whole-ledger walk).
5. Exactly ZERO matching entries → returns `RotationPairEvidence(correlation_id=correlation_id, pair_present=False)` (all other fields `None`, `signatures_verified=False`) — an ABSENCE-of-evidence result, NEVER a `RotationPairIntegrityBreach` raise. Witness: `test_find_rotation_pair_evidence_zero_matching_entries_returns_pair_present_false`.
5a. **(Lone-sibling correction, OD spec v1.35 §24.8 row 3a — out-of-family review round-2 [P2] correction.)** Exactly ONE matching entry → raises `RotationPairIntegrityBreach` (a solitary tagged entry is a torn write / deleted sibling, NOT absence — distinct from criterion #5's zero-entries case). Witness: `test_find_rotation_pair_evidence_one_matching_entry_raises_integrity_breach` (mutation probe: folding this case back into criterion #5's "absence" bucket — i.e. returning `pair_present=False` instead of raising — makes this test fail while criterion #5's own zero-entries test stays green, proving the two cases are independently pinned).
6. 3 or more matching entries → raises `RotationPairIntegrityBreach` (excess is unambiguous tamper — mirrors §24.7's `!= 2` raise). Witness: `test_find_rotation_pair_evidence_three_matching_entries_raises_integrity_breach`.
7. Exactly 2 matching entries → REUSES the shared per-pair-check helper (the SAME crypto/consecutive-period/differing-key-id/chain-continuity checks §24.7 already performs, extracted into one private helper consumed by BOTH surfaces — zero duplicated cryptographic logic). A violation of any check RAISES `RotationPairIntegrityBreach` — success returns `RotationPairEvidence(pair_present=True, outgoing_key_period=<lower>, incoming_key_period=<higher>, outgoing_key_id=<lower-period sibling's key_id>, incoming_key_id=<higher-period sibling's key_id>, signatures_verified=False)`. Witness: `test_find_rotation_pair_evidence_valid_pair_returns_populated_evidence` + `test_find_rotation_pair_evidence_tampered_hash_raises_integrity_breach` + `test_find_rotation_pair_evidence_non_consecutive_periods_raises_integrity_breach` + `test_find_rotation_pair_evidence_same_key_id_raises_integrity_breach` + `test_find_rotation_pair_evidence_broken_chain_continuity_raises_integrity_breach` (mutation probe on each: reverting the corresponding check in the shared helper makes the tampered fixture pass, failing the test).
8. `verify_rotation_pairs` (§24.7) is BYTE-UNCHANGED in observable behavior after the shared-helper extraction — the existing §24.7 test suite (already landed at PR #938) passes unmodified against the refactored module. Witness: the existing `verify_rotation_pairs` test file re-run green with zero edits.
9. **(Evidence-semantics precision, OD spec v1.35 §24.8 row 8 — out-of-family review [P1] correction.)** `find_rotation_pair_evidence`'s docstring and `RotationPairEvidence.pair_present=True`'s own contract EXPLICITLY state that this accessor performs STRUCTURAL/hash-chain checks only — it does NOT invoke per-entry cryptographic signature verification against either sibling's historical key-period, and reusing OD's existing §21.2.2 backend-aware verifier (`per_family_audit_verification._verify_entry_signature`) for this purpose is NOT possible today (that function explicitly rejects any non-deployment-bound `audit_signature_key_period`, per its own in-code comment naming rotation-aware key-period selection as still-B-33-scope). Witness: `test_find_rotation_pair_evidence_docstring_and_module_note_disclaim_signature_verification` (a static assertion that the accessor's docstring names the structural-only scope — guards against a future edit silently dropping this disclosure and letting the evidence type overclaim what it certifies).
10. **(`signatures_verified` always `False` on every RETURNED evidence object in this delta, OD spec v1.35 §24.8 row 8a — out-of-family review round-2 [P1] correction, scope corrected round-3 [P2].)** `find_rotation_pair_evidence` returns `signatures_verified=False` on every call that RETURNS a `RotationPairEvidence` object in this delta — including the criterion #5 zero-match path and the criterion #7 valid-pair success path — because no rotation-period-aware cryptographic verifier exists yet. This is a machine-checkable, necessary-but-not-sufficient signal distinct from `pair_present`, consumed by CP spec v1.105 §2 row 5a. **The tampered/excess/one-entry cases (criteria #5a/#6/#7's failure branches) RAISE `RotationPairIntegrityBreach` and never return an evidence object at all — `signatures_verified` is not assertable on a raise, and this witness does NOT cover those cases** (out-of-family review round-3 [P2] correction: the original draft incorrectly named a "tampered" fixture here, which cannot produce a return value to assert against). Witness: `test_find_rotation_pair_evidence_always_returns_signatures_verified_false_in_this_delta` (asserts `signatures_verified is False` across ONLY the zero-match and valid-pair RETURNING fixtures; mutation probe: hardcoding `signatures_verified=True` on the valid-pair success path passes criterion #7's own witness but fails this one — the two witnesses are independently load-bearing).

**Tests (mutation-probed per Workflow v1.18 PD-8):** the 7 NEW witnesses at criteria #5/#5a/#6/#7 above, plus criterion #8's non-regression re-run, plus criteria #9/#10's disclosure witnesses.

**Rollback boundary:** revert `find_rotation_pair_evidence` + the shared-helper extraction; `verify_rotation_pairs`/`sign_rotation_pair` continue exactly as landed at PR #938 (no functional regression — this unit is purely additive over that surface).

---

## §2 Coverage matrix delta (v2.29 → v2.30)

| Contract surface | Units covering (delta) |
|---|---|
| C-OD-24 §24.7 (`sign_rotation_pair` + `verify_rotation_pairs`, landed PR #938) | **U-OD-56 (NEW — retroactive backfill; zero prior coverage)** |
| C-OD-24 §24.8 (NEW at OD spec v1.35 — `find_rotation_pair_evidence`) | **U-OD-56 (NEW)** |

DAG: U-OD-56 added as a new node; in-degree per its `Depends on` (U-OD-00, U-OD-30); no existing edge removed or rewired.

---

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_30.md` (delta over v2.29) |
| Authored at | Phase 7 — B-33 rotation-correlation carrier arc, spec+plan leg (2026-07-23) |
| Authoring authority | OD spec v1.35 (`Spec_Operational_Discipline_v1_35.md`) + `.harness/class_1_fork_b33_rotation_correlation_carrier.md` (RATIFIED 2026-07-21, Option A) |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_29.md` (v2.29 — B-51/B-52/B-54 arc) |
| Siblings (same arc) | `Implementation_Plan_Control_Plane_v2_41.md` + `Implementation_Plan_Harness_Runtime_v2_53.md` + `Cross_Axis_Composition_Document_v2_22.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
