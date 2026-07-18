# Implementation Plan: Control Plane — v2.38 (delta over v2.37)

*v2.38 is the CP plan leg of the RATIFIED **B-51 / B-52 / B-54 OD audit-signing amendment arc** (`.harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md`, **RATIFIED 2026-07-18 — all ten gate items ratified AS RECOMMENDED**; three dyadic council convenings at the apply leg, **all-CONFIRM, zero deviations**), absorbing **CP spec v1.101** (`Spec_Control_Plane_v1_101.md` — the four CP-owned rider sections). The four spec surfaces are homed at FOUR EXISTING units — **U-CP-72** (the §13.5.1 tenant-bearing `cp_audit_to_od_audit` converter signature), **U-CP-73** (the §28.10.4 invariant-2 carve-out + the post-effect catch-ordering fence), **U-CP-44 + U-CP-45** (the §20.3.1 backend-aware blocking-walk reconciliation), and **U-CP-42** (the NEW §20.1.1 narrow historical exception) — **ZERO new atomic units** (every surface is an amendment of a unit already covering the parent contract section; no unit-less impl scope remains). Unit count unchanged (100). All sections except the §0 change note and the four unit amendments + coverage delta below are PRESERVED VERBATIM from v2.37 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.37 → v2.38)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_37.md` (v2.37 — the R-FS-1 R-plan-1 CP leg; U-CP-99/100).

### §0.2 Revision context — CP spec v1.101 absorption

Per the fork's ratification-gate plan-delta clause (filing codex round-11 P2 / round-12 P2), the CP plan lineage pins `cp_audit_to_od_audit` WITHOUT tenant scope — stale against CP v1.101 §1. **Empirically verified pin locations (this apply pass):** the §13.5.1 converter contract was absorbed at CP plan **v2.14 §0** (U-CP-28's `Implements` gains the `C-CP-13 §13.5.1` citation; converter declarative, no signature block in the unit body) and the converter's dispatch-logic unit is **v2.15 U-CP-72** (`harness-cxa/src/harness_cxa/cp_audit_conversion.py`). *(Surfaced finding — observed, not corrected: the fork and the CP v1.101 change-note cite the tenant-less plan pin as "(v2.17)"; `cp_audit_to_od_audit` does not occur in `Implementation_Plan_Control_Plane_v2_17.md` — the string's plan-chain occurrences are v2.14 / v2.15 / v2.28, so the "(v2.17)" cite does not resolve in this plan chain (it may intend the CXA v2.17 lineage). The staleness CLAIM itself is correct either way — no plan version pins a tenant-bearing converter.)*

The other three CP-owned rider sections (§28.10.4 invariant-2 carve-out + catch-ordering; §20.3.1 backend-aware walk; §20.1.1 historical exception) have existing covering units whose acceptance criteria predate the amendments — amended below.

### §0.3 Sections revised

§0 (this change note); §1–§4 (the four unit amendments); §5 (coverage delta). All other sections — U-CP-01..U-CP-100 bodies except the four amended below, all dependency graphs, §5 cross-cutting units, §6 open items — PRESERVED VERBATIM from v2.37.

### §0.4 Scope discipline

ADDITIVE / amended-unit scope only. ZERO new atomic units; ZERO new contract IDs; ZERO DAG topology change (amendments only — no new edges beyond the cross-axis co-land notes below). The CP witness classes of the CP v1.101 change-note ((a)–(e), each mutation-probed per Workflow v1.18 PD-8) are transcribed as `Tests:` criteria at their home units: (a) → U-CP-72; (b) + (e) → U-CP-73; (c) → U-CP-44/U-CP-45; (d) → U-CP-42. Runtime-side site enumeration for the catch-ordering fence and the ten-handler flag consult rides Runtime plan v2.49 (U-RT-136), per CP v1.101 §2's own §28.10.5 dep-graph split.

---

## §1 U-CP-72 amendment — tenant-bearing `cp_audit_to_od_audit` converter signature (CP v1.101 §1)

The v2.15 U-CP-72 body (8-prefix dispatch, ACs #1–#5) is PRESERVED VERBATIM; v2.38 adds:

**Implements (addition):** + C-CP-13 §13.5.1 (AMENDED at CP v1.101 §1 — the `tenant_id` converter-signature amendment). *(Citation refresh, no body change: U-CP-28's v2.14 `Implements` cite of §13.5.1 now resolves at the CP v1.101 amended signature block.)*

**Signature (amended):** `cp_audit_to_od_audit` gains ONE OPTIONAL keyword parameter `tenant_id: str | None = None` (the exact CP v1.101 §1 signature; every other parameter's contract unchanged — the v1.101 signature block's as-built annotations are descriptive restatement only).

**Acceptance criteria (v2.38 additions #6–#8; #1–#5 preserved verbatim):**

6. **(§1 rows 1–2.)** The converter FORWARDS `tenant_id` verbatim to `sign_audit_entry`'s same-named parameter (the same forwarding shape as the existing `backend` passthrough). The converter passes the RAW parameter through unmodified — it neither validates, normalizes, nor defaults the tenant value beyond passing `None` through; tenant-tag normalization is OD-owned (OD v1.34 §21.2.1 row 2) and happens at signing, never in the converter.
7. **(§1 row 3.)** Byte-compat drop-when-`None`: `tenant_id` absent/`None` → v1.100 behavior PRESERVED VERBATIM (four-tuple canonical message byte-for-byte; zero regression for every existing caller); present → the five-segment message per OD v1.34 §21.2.1 rows 1–2.
8. **(§1 row 4 — cross-referenced.)** `StepExecutionContext.tenant_id` is in scope at every converter-based production call site; the call-site threading itself is Runtime-owned (Runtime plan v2.49 U-RT-137, co-land with this amendment in the impl arc).

**Tests (v2.38 additions — mutation-probed per PD-8):**

> **Witness (a) — converter tenant-passthrough:** `test_converter_tenant_id_reaches_sign_audit_entry_unmodified_five_segment_message` + `test_converter_tenant_absent_entry_byte_identical_to_v1_100_path` (pairs with OD plan v2.29 U-OD-30 witness (b)).

---

## §2 U-CP-73 amendment — §28.10.4 invariant-2 carve-out + post-effect catch-ordering fence (CP v1.101 §2)

The v2.27 U-CP-73 body (Protocol declaration + firing site + 6-invariant enforcement) is PRESERVED VERBATIM; v2.38 adds:

**Implements (addition):** + C-CP-28 §28.10.4 invariant 2 (AMENDED at CP v1.101 §2).

**Acceptance criteria (v2.38 additions):**

- **(§2 row 1 — the carve-out.)** Under `audit_signing_fail_closed=ON`, members of the typed `AUDIT_SIGNING_HARD_FAILURES` family raised at the validator post-evaluate hook RAISE through the hook (the hook's audit-signing catch becomes flag-consulting).
- **(§2 row 2 — narrow scope.)** ALL other hook exception classes remain swallowed at the firing site per invariant 2 — cost-attribution computation failures, rate-table misses, span-attribute build errors, every non-family exception; the carve-out admits exactly the typed family (untyped signing failures reach it only via the OD v1.34 §21.2.3 row-5 typed-boundary routing — no widening to untyped classes).
- **(§2 row 3.)** Under flag OFF, current behavior PRESERVED VERBATIM (loudly-surfaced ERROR-log + return; invariant 2's swallow holds unconditionally).
- **(§2 row 4.)** Invariants 1, 3–6 unchanged — a raise under the carve-out still MUST NOT modify the `ValidatorEvaluation`, and the hook still fires at most once.
- **(§2 catch-ordering block — CP-contract half.)** At EVERY post-effect site class (provider response obtained; tool executed; webhook POSTed; sub-agent workflow completed), `AUDIT_SIGNING_HARD_FAILURES` is caught AHEAD of the generic per-attempt classifier catch, result-preservingly: a post-effect signing failure is NEVER classified `TRANSIENT_RETRY` (or any staircase class), NEVER advances candidates, NEVER records breaker failure; the already-obtained result is PRESERVED for the audit-failure report. Site-level enumeration and wiring are Runtime-owned (Runtime plan v2.49 U-RT-136 — co-land).

**Tests (v2.38 additions — mutation-probed per PD-8):**

> **Witness (b) — carve-out narrow-scope:** `test_flag_on_typed_family_raises_through_hook_and_nonmember_still_swallowed` + `test_flag_off_both_swallowed_as_today`. **Witness (e) — catch-ordering result-preserving:** `test_post_effect_signing_failure_caught_ahead_of_classifier_never_transient_retry_result_preserved` (never candidate-advance, never breaker-failure; the obtained result present in the audit-failure report).

---

## §3 U-CP-44 + U-CP-45 amendment — §20.3.1 backend-aware blocking audit-walk (CP v1.101 §3)

The v2.1-baseline U-CP-44 (F5 signing-key resolution, `Implements: C-CP-20 §20.3.1`) and U-CP-45 (rotation + 6-step verification, `Implements: … C-CP-20 §20.3, §20.3.1`) bodies are PRESERVED VERBATIM; v2.38 adds to both (walk-mechanics criteria at whichever unit the impl session finds carries the walk's per-entry step — the two are already the §20.3.1 co-covering pair per the v2.1 §4.1.20 coverage table):

**Acceptance criteria (v2.38 additions):**

- **(§3 row 1 — cycle-safe seam, codex round-2 P1.)** The walk's step-2 per-entry verification mechanics are performed via the OD v1.34 §21.2.2 backend-aware API (resolver keyed on stored `(algorithm, key_id)`; era decided by the authenticated cutover record; tenant scope as verifier input with the §21.2.1 row-2 normalization; typed taxonomy) — bound, not restated (definition site: OD plan v2.29 U-OD-55). **Mediation:** `harness-cp` MUST NOT import `harness-od` (`harness-od` already imports `harness-cp` for `SigningBackend` — a direct call cycles; the OD→CP canonical direction per CXA §2.3.3 also forbids it). The walk therefore takes the per-entry verifier as an INJECTED callable parameter — a `Protocol` declared CP-side (mirroring the §20.2.1 `SigningBackend` injection-seam precedent: bytes/entries in, taxonomy-typed outcome out, no OD import) — and the COMPOSITION ROOT in `harness-runtime` (which imports both packages; U-RT-138's inspect wiring is the production injection site) supplies the U-OD-55 verifier. Absent-injected-verifier → the walk's pre-v1.101 hash-chain-only behavior preserved (subject to the MTC UNVERIFIED-nonzero disposition at the inspect surface). Witness: `test_walk_verifier_injected_no_od_import` (the `harness-cp` package graph contains no `harness_od` import — mutation probe: adding one fails; the injected fake verifier's taxonomy outcomes drive walk verdicts). Co-land pin: ⊕ U-RT-138 (recorded at §0; the injection is runtime-owned wiring).
- **(§3 rows 2–3.)** §20.3.1's OWN blocking semantics UNRELAXED where the walk invokes verification (*"both fail the audit"*; §4.1.28 operator-escalation recovery); the OD API's non-blocking default is the library default on a DISJOINT invocation surface (dyad-3 probe) — not a weakening of this protocol.
- **(§3 row 4.)** An `AuditSignatureInvalid` verdict at the walk FAILS the audit exactly as a hash-chain breach does, with the typed discriminator (`AuditSignatureInvalid` ≠ `HashChainBreach`) preserved through the walk's failure report.
- **(§3 row 5.)** Backend availability errors (incl. unknown `key_id`) are NOT a verdict at the walk: surfaced as re-runnable INFRASTRUCTURE failure — the run is INCOMPLETE, neither passed nor failed-as-tampered; a re-run after availability is restored completes the walk.
- **(§3 row 6.)** §20.1.1-exempt rows and `legacy_baseline` identities are cross-checked against the cutover record and REPORTED explicitly in the walk's result (exempt / quarantined / UNVERIFIED), never silently passed.
- **(§3 row 7.)** Rotation-pair steps 3–6 PRESERVED VERBATIM; their backend-aware implementation remains `B-33`'s scope — not this arc.

**Tests (v2.38 additions — mutation-probed per PD-8):**

> **Witness (c) — walk-blocking:** `test_walk_audit_signature_invalid_fails_audit_as_hash_chain_breach_does` + `test_walk_availability_error_is_incomplete_not_pass_not_tamper_and_rerun_completes`.

---

## §4 U-CP-42 amendment — NEW §20.1.1 narrow cutover-scoped historical exception (CP v1.101 §4)

The v2.1-baseline U-CP-42 body (per-persona-tier cryptographic shape table, `Implements: C-CP-20 §20.1, §20.2`) is PRESERVED VERBATIM; v2.38 adds:

**Implements (addition):** + C-CP-20 §20.1.1 (NEW at CP v1.101 §4).

**Acceptance criteria (v2.38 additions):**

- **(§4 rows 1–2.)** At MULTI_TENANT_COMPLIANCE, a row MAY satisfy §20.1 row 3 without a verifiable per-entry signature IFF named by the authenticated cutover record's signed content-bound `(tenant_scope, entry_hash, verification_disposition)` triples; the exception's extent IS the record's content-bound identity set (never a date/version/row-position). Forward posture UNRELAXED: every post-cutover MTC row requires a real per-entry signature; the triple set is fixed at cutover-record authoring — a new row can never enter it; `audit_signing_fail_closed` explicit `false` remains INVALID at MTC.
- **(§4 row 3.)** Membership NEVER keyed on signature-value shape: an `unsigned:*`-SHAPED value on a row ABSENT from the record does NOT exempt it — such a row is a verification FAILURE per §3 above, not a legacy row.
- **(§4 rows 4–5.)** Exempt rows are REPORTED explicitly with their recorded disposition, never silently passed; the record's AUTHENTICATED / CONTENT-BOUND / TENANT-BOUND requirements and the trusted-source rule are OD-defined (OD plan v2.29 U-OD-55 acc #4) — cross-referenced, not restated.

**Tests (v2.38 additions — mutation-probed per PD-8):**

> **Witness (d) — historical-exception bounded-set:** `test_row_absent_from_cutover_record_not_exempted_including_unsigned_shaped_value` + `test_exempted_row_reported_explicitly_never_silent`.

---

## §5 Coverage matrix delta (v2.37 → v2.38)

| Contract surface | Units covering (delta) |
|---|---|
| C-CP-13 §13.5.1 (AMENDED at CP v1.101 §1 — `tenant_id`) | U-CP-28 (declarative cite, v2.14) + **U-CP-72 (amended acc #6–#8)** |
| C-CP-28 §28.10.4 invariant 2 (AMENDED at CP v1.101 §2) + post-effect catch-ordering | **U-CP-73 (amended)** (+ Runtime plan v2.49 U-RT-136 cross-axis wiring) |
| C-CP-20 §20.3.1 (AMENDED at CP v1.101 §3) | **U-CP-44 + U-CP-45 (amended)** (consuming OD plan v2.29 U-OD-55 cross-axis) |
| C-CP-20 §20.1.1 (NEW at CP v1.101 §4) | **U-CP-42 (amended)** |

DAG: unchanged topology; cross-axis co-land pins recorded (not DAG edges): U-CP-72 ⊕ U-RT-137 (tenant threading) and U-CP-73 ⊕ U-RT-136 (fence wiring) land in the one B-51/B-52/B-54 impl arc per fork gate item 10.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_38.md` (delta over v2.37) |
| Authored at | Phase 7 — B-51/B-52/B-54 OD audit-signing amendment arc apply leg (2026-07-18) |
| Authoring authority | CP spec v1.101 (`Spec_Control_Plane_v1_101.md`) + `.harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md` (RATIFIED 2026-07-18, all ten gate items AS RECOMMENDED; dyads 1–3 all-CONFIRM) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_37.md` (v2.37 — R-plan-1 U-CP-99/100) |
| Siblings (same arc) | `Implementation_Plan_Operational_Discipline_v2_29.md` + `Implementation_Plan_Harness_Runtime_v2_49.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
