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
2. `verify_rotation_pairs(ledger)` walks every distinct rotation-correlation value in the supplied ledger, raising `RotationPairIntegrityBreach` on the first violation of: exactly-2-siblings; per-entry recomputed-hash match; consecutive key periods; differing key ids; chain-hash continuity across the pair; canonical-UUID-valued correlation attribute.
3. Entries with no `audit.rotation_correlation_id` attribute are ignored by `verify_rotation_pairs` — non-rotation entries are unaffected.

**Acceptance criteria — NEW §24.8 accessor (this delta's genuinely new scope):**

4. `find_rotation_pair_evidence(ledger, correlation_id)` scopes its check to ONLY entries carrying the supplied `correlation_id` — entries under a different or absent correlation id never raise and never affect the result (per-id scoping distinct from §24.7's whole-ledger walk).
5. Fewer than 2 matching entries → returns `RotationPairEvidence(correlation_id=correlation_id, pair_present=False)` (all other fields `None`) — an ABSENCE-of-evidence result, NEVER a `RotationPairIntegrityBreach` raise. Witness: `test_find_rotation_pair_evidence_zero_matching_entries_returns_pair_present_false` + `test_find_rotation_pair_evidence_one_matching_entry_returns_pair_present_false` (mutation probe: treating a lone match as a breach raise fails both tests).
6. 3 or more matching entries → raises `RotationPairIntegrityBreach` (excess is unambiguous tamper — mirrors §24.7's `!= 2` raise). Witness: `test_find_rotation_pair_evidence_three_matching_entries_raises_integrity_breach`.
7. Exactly 2 matching entries → REUSES the shared per-pair-check helper (the SAME crypto/consecutive-period/differing-key-id/chain-continuity checks §24.7 already performs, extracted into one private helper consumed by BOTH surfaces — zero duplicated cryptographic logic). A violation of any check RAISES `RotationPairIntegrityBreach` — success returns `RotationPairEvidence(pair_present=True, outgoing_key_period=<lower>, incoming_key_period=<higher>, outgoing_key_id=<lower-period sibling's key_id>, incoming_key_id=<higher-period sibling's key_id>)`. Witness: `test_find_rotation_pair_evidence_valid_pair_returns_populated_evidence` + `test_find_rotation_pair_evidence_tampered_hash_raises_integrity_breach` + `test_find_rotation_pair_evidence_non_consecutive_periods_raises_integrity_breach` + `test_find_rotation_pair_evidence_same_key_id_raises_integrity_breach` + `test_find_rotation_pair_evidence_broken_chain_continuity_raises_integrity_breach` (mutation probe on each: reverting the corresponding check in the shared helper makes the tampered fixture pass, failing the test).
8. `verify_rotation_pairs` (§24.7) is BYTE-UNCHANGED in observable behavior after the shared-helper extraction — the existing §24.7 test suite (already landed at PR #938) passes unmodified against the refactored module. Witness: the existing `verify_rotation_pairs` test file re-run green with zero edits.

**Tests (mutation-probed per Workflow v1.18 PD-8):** the 6 NEW witnesses at criteria #5–7 above, plus criterion #8's non-regression re-run.

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
