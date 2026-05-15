# Implementation Plan — Operational Discipline v2.2

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_2.md` |
| Status | **Proposed** — F2-12 cascade Step 6b revision pass (TERMINAL cascade substrate step before Closure Declaration); promotion to Accepted at cascade close subject to OD-F212-5 P6-CK gate disposition |
| Revision | v1 → v2 (P6-CK iter-1 close mechanical revision) → v2.1 (P6-CK iter-2 F2-OD-01 hybrid revision absorbing structural-fidelity grammar at U-OD-20 + U-OD-34) → **v2.2 (F2-12 cascade Step 6b revision pass authored 2026-05-14 per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade Step 6b row + OD spec v1.3 absorption)** |
| Revision date | 2026-05-14 (v2.2 revision pass) |
| Phase | 6 — Implementation planning (post-Phase-3 F2-12 cascade Step 6b per `Project_Workflow_v1_7.md` §4.1.2; cascade-driven revision pass under `implementation-planner` SKILL.md §8 revision-pass sub-mode + Workflow v1.7 §7 fidelity-grammar) |
| Skill | `implementation-planner` (revision-pass sub-mode per SKILL.md §8) at v2.2 |
| Promotion path | Accepted at F2-12 cascade close (post-this artifact + Closure Declaration); OD-F212-5 disposition at Step 6 boundary determines whether fresh P6-CK Iteration 4 fires |
| Source-set | OD spec v1.3 (cascade Step 5b output) + CP plan v2.2 (cascade Step 6a output — cross-axis substrate consumed at U-OD-20 closure_path inheritance) + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2 + PRD v1.1 |
| Entry authorization | `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 cascade Step 6b row + ADD v1.3 §6.3.1 cascade execution path Step 6b row + CP plan v2.2 U-CP-55 §24.4 closure_path Step 6b pending-status entry |
| Exit gate | F2-12 cascade close (Closure Declaration filing); OD-F212-5 P6-CK gate disposition decision |

**Closure status (v2.2 amendment).** v2.2 — `closure_pending_at_v2_2 = false`; F2-12 ✅ **CLOSED** at this artifact per ADD v1.3 §6.3.1 cascade Step 6b row + OD spec v1.3 §14.5 closure + CP plan v2.2 cascade Step 6a closure_path Step 6b. Cascade close at Closure Declaration filing. The v2.1 closure status was "v1 — `closure_pending_at_v1 == true` per F2-12 carry-forward; closure target = OD plan v2 (now superseded by v2.1, this artifact, revision-pass mode per SKILL.md §8); F2-12 closure-path execution (steps 1–6 of canonical chain) remains OUT-OF-SCOPE at this revision pass per Path B Iter-2 close disposition; routed to parallel `council-orchestrator` C7+C9 session"; v2.2 transitions to ✅ CLOSED via the cascade execution path filed at CP plan v2.2 U-CP-55 §24.4 closure_path.

## §0 Change note (v2.1 → v2.2)

### §0.1 Scope of revision

F2-12 cascade Step 6b revision pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade execution path Step 6b row. The revision pass absorbs OD spec v1.3 §14.5 amendments (§14.5.1 dedup algorithm + §14.5.2 replay-aware orthogonality + §14.5.3 cause_attribution invariance check + §14.5.4 per-attempt cost-attribution discipline) into U-OD-20 (the sole F2-12 ACTIVE contract-bearing site in the OD plan per v2.1 §0a.3) and closes the F2-12 carry-forward at plan level. Six amendment sites:

| Finding ID (cascade-derived) | Class | Resolution shape | Amendment sites |
|---|---|---|---|
| F2-12-cascade-OD-01 | Cascade-driven | Closure status row in Status block transitioned from `closure_pending_at_v1 == true` (v2.1) to `closure_pending_at_v2_2 = false; F2-12 ✅ CLOSED at this artifact` (v2.2); cascade execution path filed at CP plan v2.2 U-CP-55 §24.4 | Status block Closure status row |
| F2-12-cascade-OD-02 | Cascade-driven | §0a.3 F2-12 ACTIVE engagement summary table transitioned to CLOSED status; sole contract-bearing notation site (U-OD-20) marked as cascade-closed | §0a.3 |
| F2-12-cascade-OD-03 | Cascade-driven | §1.3 F2-12 ACTIVE engagement location section transitioned to CLOSED status | §1.3 |
| F2-12-cascade-OD-04 | Cascade-driven | U-OD-20 section heading: "F2-12 ACTIVE affected-contract notation" → "F2-12 ✅ CLOSED affected-contract notation"; F2-12 ACTIVE engagement preamble revised to closure status | U-OD-20 section header + F2-12 ACTIVE engagement preamble |
| F2-12-cascade-OD-05 | Cascade-driven | U-OD-20 Inputs revised from OD spec v1.2 §14.4 + §14.5 → OD spec v1.3 §14.4 + §14.5 (closed) + §14.5.1 (dedup algorithm) + §14.5.2 (orthogonality) + §14.5.3 (invariance check) + §14.5.4 (per-attempt cost-attribution); CP plan U-CP-55 §24.4 closure_path → CP plan v2.2 U-CP-55 §24.4 closure_path (closed at Step 6a; Step 6b in-flight at this artifact) | U-OD-20 Inputs |
| F2-12-cascade-OD-06 | Cascade-driven | U-OD-20 Signatures revised: `dedupe_on_replay` ALGORITHM DEFERRED → algorithm specified per OD spec v1.3 §14.5.1; new `cause_attribution_invariance_check` function per §14.5.3; new `per_attempt_cost_attribution_roll_up` function per §14.5.4; `F2_12_AffectedContractNotation` record extended with `closure_status` + `closed_at_v2_2_step_6b` fields; `F2_12_DeferredSurface` enum extended with closure-status discriminator OR repurposed as historical-record enum (v2.2 chooses preserved-as-historical-record); `F2_12_CLOSURE_PATH` constant entries updated to filed-status + filing-date metadata | U-OD-20 Signatures |
| F2-12-cascade-OD-07 | Cascade-driven | U-OD-20 Acceptance criteria #3 (`dedupe_on_replay` algorithm deferred) → algorithm specified; #5 (deferred-surfaces cardinality 3) → "3 deferred surfaces at v1; all 3 closed at v2.2 cascade execution"; #8 (closure_path cardinality 6) → "closure_path now extends to 9-entry cascade execution path (Steps 1, 2a, 2b, 3, 4, 5a, 5b, 6a, 6b) plus Close; the v2.1 6-step structure is preserved as historical record"; #9 (closure_pending_at_v1 == true) → "closure_pending_at_v2_2 == false; F2-12 ✅ CLOSED"; #10 forward-routing → "closure execution path complete; cascade-close at Closure Declaration"; new acceptance criteria #12–#14 for dedup algorithm correctness + invariance check + per-attempt cost-attribution discipline | U-OD-20 Acceptance criteria + Tests |
| F2-12-cascade-OD-08 | Cascade-driven | §[carry-forwards] [CF-1] F2-12 → ✅ CLOSED | §[carry-forwards] |

Workflow v1.7 §7 fidelity-grammar discipline applied across all amendment sites: no Pattern P1 cross-artifact name drift (dedup-algorithm pseudocode + `engine.replay_disposition` enum values + `retry.attempt_number` + `retry.cause_attribution` + `replay_semantic_divergence` all consistent across CP spec v1.3 + OD spec v1.3 + CP plan v2.2 + this OD plan v2.2); no Pattern P2 verbatim-claim-contradicted (all "per OD spec v1.3 §14.5.x" claims verify against source file at `/mnt/user-data/outputs/Spec_Operational_Discipline_v1_3.md`); citation anchors substrate-verified per Workflow v1.7 §2.3.3.1 clause (iii).

### §0.2 Sections preserved verbatim (from v2.1)

All v2.1 content beyond the v2.2 revision scope is preserved verbatim. Specifically: §0 Change-notes v1 → v2 and v2 → v2.1 (preserved as historical record); §0a Front matter (OD selections + plan-level invariants — only §0a.3 F2-12 ACTIVE engagement summary revised at v2.2); §1 Spec inventory §1.1 + §1.2 (contract inventory + cluster decomposition — only §1.3 F2-12 ACTIVE engagement location revised at v2.2); §2 Atomic-unit decomposition §2.1 Cluster 1 through §2.4 Cluster 4 (preserved verbatim); §3 Cluster 5 — §3.1 + §3.2 + §3.3 (U-OD-09 through U-OD-13) + §3.4 (U-OD-14 cardinality-safe through U-OD-17) + §3.5 §3.5.1 U-OD-18 + §3.5.2 U-OD-19 + §3.5.4 U-OD-21 + §3.5.5 U-OD-22 (preserved verbatim) — only §3.5.3 U-OD-20 revised at v2.2; §3 Cluster 5 §3.6 + §3.7 (U-OD-23 through U-OD-33; preserved verbatim); §3 Cluster 5 §3.8 (U-OD-34 — preserved verbatim at v2.2; v2.1 amendments at acceptance #7 preserved); §4 Dependency graph + §5 Spec-traceability + §6 Persona linkage + §7 Cross-axis citation + §8 PRD-trace + §9 Forward-flagged + §10 ADR-trace + §11 Anti-pattern audit + §12 Coherence-pass summary (preserved verbatim — v2.2 amendment-site coherence inline per Workflow v1.7 §7); §[carry-forwards] (only F2-12 line revised at v2.2 to closure).

### §0.3 Sections revised (v2.1 → v2.2)

| Site | Revision | Source |
|---|---|---|
| Status block — Closure status row | `closure_pending_at_v1 == true` → `closure_pending_at_v2_2 = false; F2-12 ✅ CLOSED` | F2-12-cascade-OD-01 |
| §0a.3 F2-12 ACTIVE engagement summary | Table rows transitioned to closure status; sole contract-bearing notation site (U-OD-20) marked CLOSED via cascade Step 6b | F2-12-cascade-OD-02 |
| §1.3 F2-12 ACTIVE engagement location | Section heading: "F2-12 ACTIVE engagement location" → "F2-12 CLOSED engagement location"; closure path reference inline | F2-12-cascade-OD-03 |
| §3.5.3 U-OD-20 section heading | "Compose idempotency-key join + F2-12 ACTIVE affected-contract notation" → "Compose idempotency-key join + dedup algorithm + per-attempt cost-attribution + F2-12 ✅ CLOSED affected-contract notation (v2.2 amendment absorbing OD spec v1.3 §14.5)" | F2-12-cascade-OD-04 |
| U-OD-20 F2-12 ACTIVE engagement preamble | "This unit is the sole contract-bearing F2-12 carry-forward site" (active framing) → "This unit is the sole contract-bearing F2-12 carry-forward site, ✅ CLOSED at v2.2 cascade Step 6b" | F2-12-cascade-OD-04 |
| U-OD-20 Inputs | OD spec v1.2 → v1.3 reference update; §14.5.1 + §14.5.2 + §14.5.3 + §14.5.4 added; CP plan U-CP-55 §24.4 → CP plan v2.2 U-CP-55 §24.4 (closure_path filed) | F2-12-cascade-OD-05 |
| U-OD-20 Signatures | `dedupe_on_replay` algorithm specified per §14.5.1; new `cause_attribution_invariance_check` function per §14.5.3; new `per_attempt_cost_attribution_roll_up` function per §14.5.4; `F2_12_AffectedContractNotation` record extended; `F2_12_CLOSURE_PATH` constant entries updated to 9-entry filed-status + filing-date metadata | F2-12-cascade-OD-06 |
| U-OD-20 Acceptance criteria | #3 algorithm specified; #5 closure status; #8 9-entry closure_path; #9 closure_pending_at_v2_2 false; #10 closure execution path complete; new #12 (dedup algorithm correctness against §14.5.1 pseudocode); new #13 (invariance check ESCALATION semantics per §14.5.3); new #14 (per-attempt cost-attribution roll-up per §14.5.4) | F2-12-cascade-OD-07 |
| U-OD-20 Tests | Tests revised + new tests added covering: dedup algorithm correctness; orthogonality discriminators; invariance check ESCALATION to terminal-fail-exit; per-attempt cost roll-up; closure_path 9-entry cardinality; closure_status closed | F2-12-cascade-OD-07 |
| §[carry-forwards] [CF-1] F2-12 | Transitioned from active to ✅ CLOSED with closure-summary content | F2-12-cascade-OD-08 |

### §0.4 Coverage matrix delta

| Coverage cell | At v2.1 | At v2.2 |
|---|---|---|
| C-OD-14 §14.4 idempotency-key join | Replay-safe-composition row promissory ("dedup primitive is the idempotency-key join; algorithm closes at D6 v1.2") | Replay-safe-composition row specific to dedup algorithm per §14.5.1; closure realized |
| C-OD-14 §14.5 F2-12 ACTIVE engagement affected-contract notation | Active engagement at U-OD-20; closure deferred | ✅ CLOSED at U-OD-20 absorbing §14.5.1 + §14.5.2 + §14.5.3 + §14.5.4 |
| C-OD-14 §14.5.1 dedup algorithm (NEW at v1.3) | Did not exist at v1.2 spec; U-OD-20 declared algorithm DEFERRED | U-OD-20 algorithm specified per pseudocode |
| C-OD-14 §14.5.2 replay-aware orthogonality (NEW at v1.3) | Did not exist at v1.2 spec | U-OD-20 orthogonality discriminators absorbed |
| C-OD-14 §14.5.3 cause_attribution invariance check (NEW at v1.3) | Did not exist at v1.2 spec | U-OD-20 invariance check + ESCALATION to terminal-fail-exit absorbed |
| C-OD-14 §14.5.4 per-attempt cost-attribution (NEW at v1.3) | Did not exist at v1.2 spec | U-OD-20 per-attempt cost roll-up absorbed |

### §0.5 Dependency graph delta

No dependency graph changes at v2.2. U-OD-20 dependencies preserved (`[U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)]`); cross-axis dependency to U-CP-55 §24.4 closure_path inheritance preserved (now reads closed-status from CP plan v2.2 instead of declared-as-pending from CP plan v1).

### §0.6 Substrate-version-citation table (v2.2 amendment)

| Substrate | v2.1 version cited | v2.2 version cited |
|---|---|---|
| ADR-D6 | v1.1 | **v1.2** |
| ADR-D1 | v1.1 | **v1.2** |
| ADD | v1.2 | **v1.3** |
| PRD | v1.0.1 | **v1.1** |
| OD spec | v1.2 | **v1.3** |
| CP plan | v1 (at v2.1 closure_path step 6 declared as "OD plan v1 → v2 revision-pass") | **v2.2 (cascade Step 6a output; closure_path Step 6a filed)** |

### §0.7 Status

`Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until F2-12 cascade close (post-Closure Declaration) and OD-F212-5 P6-CK disposition resolution. OD plan v2.2 is the TERMINAL cascade substrate step before Closure Declaration; cascade close gates on this artifact + `F2-12_Closure_Declaration.md` filing.

### §0.8 Forward-flagged concerns (v2.2 update)

| Concern | v2.2 disposition | Forward-routed at v2.2 |
|---|---|---|
| U-OD-34 carry-forward inheritance at v2.1 | NOT in cascade scope at v2.2; v2.1 hybrid-fidelity acceptance #7 preserved | — |
| OD spec v1.3 §1.5 hash-chain integrity composition (extension to ledger_entries schema) | NOT absorbed at v2.2 within strict-narrow F2-12 cascade scope; affects U-OD-NN ledger-schema unit if exists | Forward-flagged for P6-CK Iteration 4 OR future revision pass |
| OD spec v1.3 §14.5.3 `replay_semantic_divergence` cause_attribution catalog extension (new C5 enum value) | NOT absorbed at v2.2 within strict-narrow F2-12 cascade scope; affects U-OD-NN validator.fail unit if exists; cross-references ADR-D5 v1.2 §1.10.1 forward-flag | Forward-flagged for future ADR-D5 revision pass + corresponding OD spec + plan absorption |

### §0.10 v2.2 coherence-pass summary

| Pass | Status |
|---|---|
| §1 Spec inventory | ✅ PASS — substrate-version citations updated to v1.3 OD spec + v1.2 D1/D6 + v1.3 ADD + v1.1 PRD; F2-12 ACTIVE engagement location at §1.3 transitioned to CLOSED |
| §3 Atomic-unit decomposition | ✅ PASS — U-OD-20 acceptance #3 + #5 + #8 + #9 + #10 + new #12/#13/#14 all aligned to OD spec v1.3 §14.5.1–§14.5.4; all other units preserved verbatim per strict-narrow scope discipline |
| §4 Dependency graph | ✅ PASS — no dependency graph changes at v2.2 |
| §5 Spec-traceability | ✅ PASS — U-OD-20 → C-OD-14 §14.4 + §14.5 (closed at v1.3) + §14.5.1 + §14.5.2 + §14.5.3 + §14.5.4 (new at v1.3) all canonically cited |
| §11 Anti-pattern audit | ✅ PASS — strict-narrow scope discipline enforced per cascade kickoff §3.2; forward-flagged concerns surfaced at §0.8 not absorbed at v2.2 |
| Cross-artifact name-drift check | ✅ PASS — Pattern P1 prevention verified: `engine.replay_disposition` + 5-value enum + `retry.attempt_number` + `retry.cause_attribution` + `replay_semantic_divergence` all consistent across CP spec v1.3 + OD spec v1.3 + CP plan v2.2 + this OD plan v2.2 |

---

## §0a Front matter

[§0a.1 OD selections + §0a.2 plan-level invariants preserved verbatim from v2.1.]

### §0a.3 F2-12 engagement summary (v2.2 amendment — transitioned from ACTIVE to CLOSED)

| Field | Value at v2.2 |
|---|---|
| F2-12 status | ✅ **CLOSED** at OD plan v2.2 cascade Step 6b per ADD v1.3 §6.3.1 + OD spec v1.3 §14.5 closure + CP plan v2.2 U-CP-55 §24.4 closure_path |
| F2-12 ACTIVE contract-bearing sites at v2.1 | 1 (U-OD-20) |
| F2-12 carry-forward inheritance sites at v2.1 | 1 (U-OD-34) |
| F2-12 ACTIVE contract-bearing sites at v2.2 | 0 (U-OD-20 transitioned to CLOSED at this revision) |
| F2-12 CLOSED contract-bearing sites at v2.2 | 1 (U-OD-20) |
| Sole closure-bearing notation site | U-OD-20 implementing C-OD-14 §14.4 + §14.5 (closed) + §14.5.1 (dedup algorithm) + §14.5.2 (orthogonality) + §14.5.3 (invariance check) + §14.5.4 (per-attempt cost-attribution) |
| Closure execution path | Steps 1, 2a, 2b, 3, 4, 5a, 5b, 6a ✅ filed; Step 6b ✅ filed (this artifact); Close ⏳ PENDING (`F2-12_Closure_Declaration.md`) |
| Cascade close gate | This artifact + Closure Declaration both required; this artifact is the TERMINAL cascade substrate step |

---

## §1 Spec inventory

[§1.1 Contract inventory + §1.2 Cluster decomposition preserved verbatim from v2.1.]

### §1.3 F2-12 CLOSED engagement location (v2.2 amendment — transitioned from ACTIVE to CLOSED)

**Status (v2.2 amendment).** ✅ **CLOSED** at OD plan v2.2 cascade Step 6b. The v2.1 section heading was "F2-12 ACTIVE engagement location (single contract-bearing site per session prompt §5.4 [CF-1] authoring approach (iii))"; v2.2 transitions to CLOSED location with sole U-OD-20 absorption complete.

| Contract-bearing site at v2.2 | C-OD-14 §14.4 + §14.5 (closed) + §14.5.1–§14.5.4 (new at v1.3); U-OD-20 absorbs |
|---|---|
| Closure path filed | CP plan v2.2 U-CP-55 §24.4 closure_path Step 1 → Step 6a ✅; Step 6b ✅ (this artifact); Close ⏳ |
| Cross-axis inheritance | OD spec v1.3 §14.5.1 dedup algorithm consumes D1 v1.2 §1.1.2.2 ledger entry shape extension; §14.5.2 orthogonality consumes D1 v1.2 §1.1.1 4-attribute namespace; §14.5.3 invariance check consumes C5 cause_attribution catalog; §14.5.4 per-attempt cost-attribution composes with §C-OD-23 operator-burden eval primitive |

---

## §2 Atomic-unit decomposition (Clusters 1–4)

[Preserved verbatim from v2.1.]

---

## §3 Cluster 5 — D6 cost-attribution + dashboard + collector

[§3.1 + §3.2 + §3.3 preserved verbatim from v2.1.]

### §3.4 Cluster decomposition U-OD-14 through U-OD-17

[Preserved verbatim from v2.1.]

### §3.5 Cluster decomposition U-OD-18 through U-OD-22

[§3.5.1 U-OD-18 + §3.5.2 U-OD-19 preserved verbatim from v2.1.]

#### §3.5.3 U-OD-20 — Compose idempotency-key join + dedup algorithm + per-attempt cost-attribution + F2-12 ✅ CLOSED affected-contract notation (v2.2 amendment absorbing OD spec v1.3 §14.5)

**Implements (v2.2 amendment):** [C-OD-14 §14.4 idempotency-key join + §14.5 (CLOSED at v1.3) + §14.5.1 trace-ingestion dedup algorithm (NEW at v1.3) + §14.5.2 replay-aware dedup with retry orthogonality (NEW at v1.3) + §14.5.3 cause_attribution invariance check at deterministic_replay (NEW at v1.3) + §14.5.4 per-attempt cost-attribution discipline (NEW at v1.3)]

**Depends on:** [U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)]

**Inputs (v2.2 amendment):** OD spec **v1.3** §14.4 idempotency-key join (Replay-safe composition row revised at v1.3 from promissory to dedup-algorithm-specific per OD spec v1.3 §14.5.1 reference); §14.5 F2-12 ✅ CLOSED affected-contract notation (was ACTIVE at v1.2; 3-deferred-surface structure preserved as historical record); §14.5.1 trace-ingestion dedup algorithm pseudocode (NEW at v1.3); §14.5.2 replay-aware dedup with retry orthogonality (orthogonality discriminators `retry.attempt_number` × `engine.replay_disposition`; 8-row dedup outcome matrix); §14.5.3 cause_attribution invariance check at deterministic_replay (invariance assertion + ESCALATION to terminal-fail-exit with `replay_semantic_divergence` cause_attribution); §14.5.4 per-attempt cost-attribution discipline (per-disposition cost accrual semantics + parent operation total cost roll-up); CP plan **v2.2** U-CP-55 §24.4 F2-12 carry-forward closure path (9-entry filed cascade execution chain at v2.2; was declared 6-step chain at v2.1).

**Cross-axis dependency resolution.** IS plan U-IS-NN implementing C-IS-10 §10.2 (idempotency-key join export); IS plan U-IS-17 substrate seam exports manifest is the resolution target. **At v2.2, additional cross-axis substrate at CP plan v2.2 U-CP-21 (4-attribute `engine.*` namespace) + U-CP-55 §24.4 (closure_path) is read.**

**Files affected:** Idempotency-key join composition + dedup algorithm + per-attempt cost-attribution + F2-12 closed-contract notation (logical name: `od-cost-attribution-idempotency-join-dedup-algorithm-and-f2-12-closed-notation`).

**F2-12 ✅ CLOSED engagement (v2.2 amendment).** This unit is the **sole contract-bearing F2-12 carry-forward site** in the OD plan, **✅ CLOSED at OD plan v2.2 cascade Step 6b** per the cascade execution path filed at CP plan v2.2 U-CP-55 §24.4. The v2.1 ACTIVE framing is transitioned to CLOSED at v2.2; closure-bearing notation preserves the historical 3-deferred-surface structure as record and adds the closure-status discriminator.

**Signatures (v2.2 amendment).**

```
record SpanCostRecord {
  span_id              : string
  idempotency_key      : string                    // from parent span per C-IS-05
  total_cost           : float                     // from U-OD-19 SpanTotalCost
  total_latency_ms     : int                       // from U-OD-19 SpanTotalCost
  derived_keys         : List<string>              // for sub-agent inheritance per C-AS-15 §15.6
  engine_replay_disposition : ReplayDisposition    // v2.2 new — per CP plan v2.2 U-CP-21 4-attribute schema
  retry_attempt_number      : Optional<int>        // v2.2 new — per OD spec v1.3 §14.5.2 orthogonality
  retry_cause_attribution   : Optional<string>     // v2.2 new — per OD spec v1.3 §14.5.3 invariance check
  is_replay_derived         : bool                 // v2.2 new — set by dedup algorithm per §14.5.1
}

fn attach_idempotency_key_to_cost_record(
  span                : SpanRef,
  parent_idempotency  : string,
  cost_record         : SpanCostRecord
) -> SpanCostRecord                                // preserved verbatim from v2.1

# v2.2 — dedup algorithm SPECIFIED per OD spec v1.3 §14.5.1 (was DEFERRED at v2.1)
fn dedupe_on_replay(
  span                : SpanRef,
  ledger_entry        : Optional<F2StateLedgerEntry>
) -> DedupOutcome
  # match span.engine_replay_disposition:
  #   case DETERMINISTIC_REPLAY:
  #     if ledger_entry.matches(trace_id, span_id, cause_attribution): DROP
  #     else if cause_attribution mismatch: ESCALATE per §14.5.3 invariance check
  #   case CHECKPOINT_RESUME | RECONCILER_ITERATION | WAL_CONSUME: RECORD replay-derived
  #   case NO_REPLAY: ERROR if ledger_entry exists; otherwise RECORD first-ingestion

enum DedupOutcome {
  DROP_DETERMINISTIC_REPLAY_RE_READ,
  RECORD_REPLAY_DERIVED,
  RECORD_FIRST_INGESTION,
  ERROR_UNEXPECTED_RE_INGESTION_FOR_NO_REPLAY,
  ESCALATE_REPLAY_SEMANTIC_DIVERGENCE
}

# v2.2 new — per OD spec v1.3 §14.5.3
fn cause_attribution_invariance_check(
  span                : SpanRef,
  ledger_entry        : F2StateLedgerEntry
) -> InvarianceCheckResult
  # iff span.engine_replay_disposition == DETERMINISTIC_REPLAY:
  #   assert span.retry_cause_attribution == ledger_entry.cause_attribution
  #   on mismatch: emit ESCALATE event with:
  #     validator.fail.class = TERMINAL_FAIL_EXIT
  #     validator.fail.cause_attribution = "replay_semantic_divergence"
  #     validator.fail.permanence = PERMANENT
  #     always-sampled per OD spec v1.3 C-OD-09 §9.2

enum InvarianceCheckResult {
  PASS,
  ESCALATE_REPLAY_SEMANTIC_DIVERGENCE,
  NOT_APPLICABLE  // non-deterministic_replay dispositions
}

# v2.2 new — per OD spec v1.3 §14.5.4
fn per_attempt_cost_attribution_roll_up(
  parent_operation_id : string,
  retry_attempt_costs : List<SpanCostRecord>  // ordered by retry_attempt_number
) -> ParentOperationTotalCost
  # total_cost = Σ cost(retry-attempt child span_i) for i in 1..N
  # deterministic_replay re-reads contribute zero (filtered before aggregation)

record ParentOperationTotalCost {
  parent_operation_id : string
  total_cost          : float                  // Σ per-attempt costs
  per_attempt_costs   : Map<int, float>        // attempt_number → cost
  replay_re_reads_excluded : int               // count of deterministic_replay drops
}

fn propagate_to_subagent(
  parent_idempotency : string
) -> string                                    // preserved verbatim from v2.1

# v2.2 — F2_12_DeferredSurface preserved as historical record; closure-status added
enum F2_12_DeferredSurface {
  SPAN_REEMISSION_SEMANTICS_UNDER_ENGINE_REPLAY,         // surface 1 — CLOSED at D1 v1.2 §1.1.1 + §1.1.2
  RETRY_ATTEMPT_SIBLING_SPAN_DISCIPLINE_AT_D6_INGESTION, // surface 2 — CLOSED at D6 v1.2 §1.2.2 (corrected to child-per-attempt)
  TRACE_INGESTION_DEDUP_COMPOSITION_ALGORITHM           // surface 3 — CLOSED at D6 v1.2 §1.5 + OD spec v1.3 §14.5.1
}

record F2_12_AffectedContractNotation {  // v2.2 amendment — closure_status fields added
  contract_id              : "C-OD-14"
  active_engagement_site   : "C-OD-14 §14.5"          // historical reference preserved
  closed_engagement_site   : "C-OD-14 §14.5 (closed) + §14.5.1 + §14.5.2 + §14.5.3 + §14.5.4"  // v2.2 new
  deferred_surfaces_at_v1  : Set<F2_12_DeferredSurface>   // exactly 3 surfaces; preserved as historical record
  closure_status_per_surface : Map<F2_12_DeferredSurface, Step>  // v2.2 new — each surface mapped to closing cascade step
  v1_commitment_level      : "cost-attribution-per-span formula + sandbox-tier overhead + per-sibling rollup + idempotency-key join"
  v2_2_commitment_level    : "v1 + dedup algorithm + replay-aware orthogonality + cause_attribution invariance check + per-attempt cost-attribution discipline"  // v2.2 new
  closure_path             : List<RevisionStep>           // v2.2: 9 entries (was 6 at v2.1)
  closure_pending_at_v1    : bool                         // historical: true
  closure_pending_at_v2_2  : bool                         // v2.2 new: false
  closure_status           : ClosureStatus                // v2.2 new: CLOSED_AT_CASCADE_STEP_6B
}

enum ClosureStatus {                                      // v2.2 new
  ACTIVE,
  CLOSED_AT_CASCADE_STEP_6B,
  CLOSED_AT_DECLARATION
}

record RevisionStep {
  step_number     : int
  step_label      : string                        // v2.2 new: "Step 1" / "Step 2a" / "Step 2b" / ...
  artifact        : string
  scope           : string
  filing_status   : FilingStatus                  // v2.2 new
  filing_date     : Optional<Date>                // v2.2 new
}

enum FilingStatus {                                       // v2.2 new
  FILED,
  PENDING
}

const F2_12_CLOSURE_PATH : List<RevisionStep> = [         // v2.2: 9 entries (was 6 at v2.1)
  {1,  "Step 1",  "Council deliberation",    "Substantive resolution substrate for all three sub-scopes",     FILED, "2026-05-14"},
  {2,  "Step 2a", "ADR-D1 v1.1 → v1.2",      "Sub-scope (i) span re-emission semantics",                     FILED, "2026-05-14"},
  {3,  "Step 2b", "ADR-D6 v1.1 → v1.2",      "Sub-scopes (ii) + (iii) retry + dedup",                        FILED, "2026-05-14"},
  {4,  "Step 3",  "ADD v1.2 → v1.3",         "Cross-axis consolidation absorbing D1 + D6 v1.2",              FILED, "2026-05-14"},
  {5,  "Step 4",  "PRD v1.0.1 → v1.1",       "R-CP-04 + R-CP-07 + R-OD-05 observable-behavior absorption",   FILED, "2026-05-14"},
  {6,  "Step 5a", "CP spec v1.2 → v1.3",     "C-CP-08 + C-CP-09 + §3.5 + §5.4 contract-surface absorption",  FILED, "2026-05-14"},
  {7,  "Step 5b", "OD spec v1.2 → v1.3",     "C-OD-14 §14.5 dedup algorithm + §14.5.1–§14.5.4 absorption",   FILED, "2026-05-14"},
  {8,  "Step 6a", "CP plan v2.1 → v2.2",     "U-CP-20 + U-CP-21 + U-CP-55 plan-level absorption",            FILED, "2026-05-14"},
  {9,  "Step 6b", "OD plan v2.1 → v2.2",     "U-OD-20 dedup + orthogonality + invariance + per-attempt",     FILED, "2026-05-14"}  // this artifact
  // Close: F2-12 Closure Declaration — PENDING
]

const F2_12_NOTATION : F2_12_AffectedContractNotation     // v2.2: closure_status = CLOSED_AT_CASCADE_STEP_6B
```

**Acceptance criteria (v2.2 amendment).**

1. `SpanCostRecord` declares **9 fields at v2.2** (was 5 at v2.1) per §14.4 + §14.5.2 + §14.5.3 verbatim. Per-span cost record carries parent's `idempotency_key` per C-IS-05, plus `engine_replay_disposition` + `retry_attempt_number` + `retry_cause_attribution` + `is_replay_derived` per OD spec v1.3 §14.5.2 orthogonality discriminators.
2. `attach_idempotency_key_to_cost_record` returns `SpanCostRecord` with `idempotency_key` set to parent's value; replay-safe composition with F2 state-ledger via `idempotency_key` enforced by the **dedup algorithm at `dedupe_on_replay`** (v2.2 amendment — was promissory at v2.1).
3. **`dedupe_on_replay` algorithm SPECIFIED per OD spec v1.3 §14.5.1 (v2.2 amendment — was DEFERRED at v2.1).** Algorithm pseudocode: match on `span.engine_replay_disposition`; `deterministic_replay` DROPs (zero additional cost accrual); `checkpoint_resume` / `reconciler_iteration` / `wal_consume` RECORD replay-derived; `no_replay` ERRORs on unexpected re-ingestion. Closure invariant: F2-12 sub-scope (iii) closes at this acceptance per OD spec v1.3 §14.5.1 + D6 v1.2 §1.5.
4. `propagate_to_subagent` returns derived `idempotency_key` per C-AS-15 §15.6 sub-agent boundary inheritance. [Preserved verbatim from v2.1.]
5. **`F2_12_DeferredSurface` enumerates exactly 3 values matching §14.5 v1.2 verbatim preserved as historical record (v2.2 amendment — was "3 deferred surfaces, active" at v2.1); at v2.2, `closure_status_per_surface` maps each surface to its closing cascade step**: surface 1 → Step 2a (D1 v1.2 §1.1.1 + §1.1.2); surface 2 → Step 2b (D6 v1.2 §1.2.2); surface 3 → Step 2b (D6 v1.2 §1.5) + Step 5b (OD spec v1.3 §14.5.1) + Step 6b (this unit).
6. `F2_12_NOTATION.contract_id == "C-OD-14"` and `active_engagement_site == "C-OD-14 §14.5"`. **At v2.2, `closed_engagement_site == "C-OD-14 §14.5 (closed) + §14.5.1 + §14.5.2 + §14.5.3 + §14.5.4"`.**
7. `F2_12_NOTATION.v1_commitment_level` matches §14.5 v1.2 verbatim (preserved). **At v2.2, `v2_2_commitment_level` matches §14.5 v1.3 verbatim closure: "v1 + dedup algorithm + replay-aware orthogonality + cause_attribution invariance check + per-attempt cost-attribution discipline".**
8. **`F2_12_CLOSURE_PATH` declares exactly 9 revision steps at v2.2 (was 6 at v2.1)** per cascade execution path inheritance from CP plan v2.2 U-CP-55 §24.4. The v2.1 6-step structure is preserved as the structural backbone; v2.2 expands to 9 entries reflecting the cascade-discovered sub-step decomposition (Step 2 split into 2a + 2b; Step 5 split into 5a + 5b; Step 6 split into 6a + 6b). Partial closure does NOT close the carry-forward; v2.2 closure_path has all 9 steps filed (Steps 1–6b ✅; Close pending).
9. **`F2_12_NOTATION.closure_pending_at_v2_2 == false` (v2.2 amendment; was `closure_pending_at_v1 == true` at v2.1).** Closure ✅ realized at OD plan v2.2 cascade Step 6b; cascade-close formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close.
10. **Closure execution path complete (v2.2 amendment; v2.1 "Forward-routing: parallel `council-orchestrator` C7+C9 session per ADD §6.3.1 active path" is closed at v2.2)** — cascade Steps 1 → 6b all filed; Closure Declaration pending.
11. Cross-axis edge per OD-S4-3.A: `Depends on: [U-IS-NN (cross-axis: IS — C-IS-10 §10.2 unit)]`. Resolution at U-OD-34. [Preserved verbatim from v2.1.]
12. **(v2.2 new) Dedup algorithm correctness — `dedupe_on_replay` MUST produce `DedupOutcome` consistent with OD spec v1.3 §14.5.1 pseudocode for each of the 5 `engine.replay_disposition` × `retry.attempt_number ∈ {1, 2..N}` × `ledger_entry ∈ {present, absent}` cells of the dedup outcome matrix at §14.5.2.**
13. **(v2.2 new) Invariance check ESCALATION semantics — `cause_attribution_invariance_check` MUST emit ESCALATE event with `validator.fail.class = TERMINAL_FAIL_EXIT` + `validator.fail.cause_attribution = "replay_semantic_divergence"` + `validator.fail.permanence = PERMANENT` on mismatch per OD spec v1.3 §14.5.3. The escalate event MUST be always-sampled per C-OD-09 §9.2 (validator.fail.permanence=permanent always-sampled).**
14. **(v2.2 new) Per-attempt cost-attribution roll-up — `per_attempt_cost_attribution_roll_up` MUST compute `total_cost = Σ cost(retry-attempt child span_i) for i in 1..N` per OD spec v1.3 §14.5.4; `deterministic_replay` re-reads contribute ZERO to the sum (filtered via `is_replay_derived` flag set by dedup algorithm). The roll-up MUST compose with `C-OD-23` operator-burden eval primitive at the per-operation aggregation level without re-aggregation.**

**Tests (v2.2 amendment).** v2.1 tests preserved except `test_dedupe_on_replay_algorithm_deferred` (replaced at v2.2 with `test_dedupe_on_replay_algorithm_specified_per_v1_3_section_14_5_1`); `test_f2_12_deferred_surface_cardinality_three` preserved (3 historical surfaces); `test_f2_12_deferred_surface_names_match_spec` preserved with v1.2 spec reference; `test_f2_12_notation_contract_id_c_od_14` preserved; `test_f2_12_notation_active_engagement_site` preserved (historical); `test_f2_12_v1_commitment_level_byte_exact` preserved; `test_f2_12_closure_path_cardinality_six` → `test_f2_12_closure_path_cardinality_nine` (v2.2); `test_f2_12_closure_path_step_order_matches_cp_55_24_4` preserved (now reads CP plan v2.2 closure_path); `test_f2_12_partial_closure_does_not_close` preserved; `test_f2_12_closure_pending_at_v1_true` preserved (historical); new at v2.2: `test_f2_12_closure_pending_at_v2_2_false`, `test_f2_12_notation_closed_engagement_site`, `test_f2_12_notation_v2_2_commitment_level_byte_exact`, `test_f2_12_notation_closure_status_closed_at_cascade_step_6b`, `test_f2_12_closure_path_all_six_steps_through_6b_filed`, `test_f2_12_closure_path_step_2_split_into_2a_2b`, `test_f2_12_closure_path_step_5_split_into_5a_5b`, `test_f2_12_closure_path_step_6_split_into_6a_6b`, `test_dedupe_on_replay_deterministic_replay_drops`, `test_dedupe_on_replay_checkpoint_resume_records_replay_derived`, `test_dedupe_on_replay_no_replay_errors_on_re_ingestion`, `test_dedup_outcome_matrix_8_cells_match_spec`, `test_cause_attribution_invariance_check_escalate_on_mismatch`, `test_cause_attribution_invariance_check_pass_on_match`, `test_cause_attribution_invariance_check_not_applicable_for_non_deterministic_replay`, `test_replay_semantic_divergence_event_always_sampled`, `test_per_attempt_cost_attribution_roll_up_sum_invariant`, `test_per_attempt_cost_attribution_deterministic_replay_excluded`, `test_span_cost_record_nine_fields`, `test_span_cost_record_engine_replay_disposition_field`, `test_span_cost_record_retry_attempt_number_field`, `test_span_cost_record_retry_cause_attribution_field`, `test_span_cost_record_is_replay_derived_field`, `test_closure_status_per_surface_total_over_three_surfaces`.

**Rollback boundary (v2.2 amendment).** Revert idempotency-key join + dedup algorithm + invariance check + per-attempt cost-attribution + F2-12 closed-contract notation back to v2.1 form. Cost-attribution-per-span loses dedup algorithm + per-attempt cost roll-up; F2-12 carry-forward closure regresses to ACTIVE at U-OD-20 (sole contract-bearing notation site); closure path inheritance from CP plan v2.2 U-CP-55 §24.4 loses Step 6b filed entry; D6 v1.2 closure half loses plan-side anchor. **Cascade close gate dissolves at this rollback; OD plan v2.2 cascade Step 6b filed status reverts; cascade-close Closure Declaration cannot be filed without re-filing this artifact.**

[§3.5.4 U-OD-21 + §3.5.5 U-OD-22 preserved verbatim from v2.1.]

---

[§3.6 + §3.7 + §3.8 preserved verbatim from v2.1.]

---

## §4 Dependency graph + §5 Spec-traceability + §6 Persona linkage + §7 Cross-axis citation + §8 PRD-trace + §9 Forward-flagged + §10 ADR-trace + §11 Anti-pattern audit + §12 Coherence-pass summary

[All sections preserved verbatim from v2.1 except v2.2 amendment-site inline verification per Workflow v1.7 §7 fidelity-grammar discipline (recorded at §0.10 above).]

---

## §[carry-forwards]

### [CF-1] F2-12 — D1 v1.1 → v1.2 + D6 v1.1 → v1.2 replay-trace-emission contract (✅ CLOSED at v2.2)

**Status (v2.2 amendment).** ✅ **CLOSED** at OD plan v2.2 cascade Step 6b filing per ADD v1.3 §6.3.1 + CP plan v2.2 U-CP-55 §24.4 closure_path. Plan-level absorption at Status block Closure status row + §0a.3 F2-12 engagement summary + §1.3 CLOSED engagement location + U-OD-20 acceptance #3 (dedup algorithm specified) + #5 (closure_status_per_surface) + #8 (9-entry closure_path) + #9 (closure_pending_at_v2_2 false) + #10 (closure execution path complete) + new #12 (dedup correctness) + #13 (invariance check ESCALATION) + #14 (per-attempt cost-attribution roll-up). Cascade close at `F2-12_Closure_Declaration.md` filing — only pending Closure step. Formal `closure_pending false` declaration deferred to that artifact.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_2.md` |
| Filing destination | `/mnt/user-data/outputs/Implementation_Plan_Operational_Discipline_v2_2.md` |
| Status | Proposed (pending F2-12 cascade close at Closure Declaration filing + OD-F212-5 P6-CK disposition) |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_1.md` (v1 → v2 → v2.1 baseline) |
| Substrate consumed | OD spec v1.3 + CP plan v2.2 + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2 + PRD v1.1 |
| Successor | `F2-12_Closure_Declaration.md` (cascade close; formal closure_pending false declaration) |
| F2-12 closure status | ✅ CLOSED at cascade Step 6b (this artifact) — TERMINAL cascade substrate step |
| Workflow discipline | `Project_Workflow_v1_7.md` §7 fidelity-grammar |
| Date | 2026-05-14 |

*Filed at F2-12 cascade Step 6b close — TERMINAL cascade substrate step before Closure Declaration. U-OD-20 absorbs OD spec v1.3 §14.5.1 dedup algorithm (was DEFERRED at v2.1; SPECIFIED at v2.2) + §14.5.2 replay-aware orthogonality (8-cell dedup outcome matrix at orthogonal discriminators retry.attempt_number × engine.replay_disposition) + §14.5.3 cause_attribution invariance check (with ESCALATION to terminal-fail-exit + new replay_semantic_divergence cause_attribution catalog value) + §14.5.4 per-attempt cost-attribution discipline (per-attempt cost roll-up + deterministic_replay re-reads excluded from total). F2_12_CLOSURE_PATH extended from 6-entry (v2.1) to 9-entry (v2.2) reflecting cascade-discovered sub-step decomposition (Step 2 → 2a+2b; Step 5 → 5a+5b; Step 6 → 6a+6b). Step 6 complete: 6a + 6b both filed. Cascade segment boundary per OD-F212-4.A; OD-F212-5 P6-CK disposition pending at Step 6 boundary. Recommended next cascade step: F2-12 Closure Declaration filing — formal `closure_pending false` declaration + per-sub-scope resolution summary + cascade-artifact inventory.*
