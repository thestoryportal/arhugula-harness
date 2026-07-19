# Implementation Plan — Information Substrate (IS axis) — v2.7

*Delta over v2.6. v2.7 is the IS-axis leg of the RATIFIED **B-48 sync sub-agent dispatch offload arc** (`.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md`, **RATIFIED 2026-07-18 — the operator selected OPTION B AS RECOMMENDED with all filing-settled riders**; §5 rider (d) names "IS spec **+ plan** back-flow" for the §4-item-7 drain-timestamp fix; the C1 ⊥ C9 apply-leg dyad `.harness/council-dyad-b48-apply-2026-07-18.md` returned **16/16 CONFIRM, ZERO deviations**), absorbing **IS spec v1.11** (the C-IS-07 drain-timestamp write-contract amendment: ONE ADDITIVE §7.1 row 7 "Timestamp authority (v1.11)" + NEW §7.6, `Spec_Information_Substrate_v1.md`). The amendment is homed at **ONE EXISTING unit — U-IS-11** (the C3-pole append-only write contract, `Implements: C-IS-07 §7.1, §7.3`, the unit owning `append_ledger_entry` at `harness_is.state_ledger_write`) — **ZERO new atomic units** (verified: no other unit implements the write contract; the v2.6 U-IS-19 carrier unit is untouched). IS 0-outbound preserved: the amendment adds NO dependency on any U-CP-* / U-RT-* unit. The CP-side half (the drain call-site change + the strict-xfail REMOVAL) is CP-owned at the same-arc CP plan v2.39 (U-CP-82 amendment) — cross-referenced, never restated. v2.6 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.6 → v2.7)

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_6.md` (v2.6 — the R-FS-1 B1-plan IS leg; U-IS-19 NEW).

### §0.2 Revision scope (v2.6 → v2.7)

v2.7 absorbs **IS spec v1.11** (the B-48 rider (d): C-IS-07 §7.1 row 7 + NEW §7.6 — writer-owned timestamp authority on the buffered/branch-drain append surface) into the plan, per the v1.11 change-note's own flag ("IS plan absorption of this contract change is owed to `implementation-planner` revision-pass"). The fix's routing authority is the ratified fork (its §4 item 7 carries the defect: `drain_branch_buffers` samples `drain_timestamp` BEFORE the IS `_WRITE_LOCK`, so two concurrent sibling drains can append in inverted order and raise `NonMonotonicTimestampError` — pinned by the strict xfail `test_concurrent_sibling_drains_invert_timestamp`).

| In scope at v2.7 | Out of scope |
|---|---|
| U-IS-11 amendment — writer-owned drain-path timestamp sampling inside the `_WRITE_LOCK` critical section + by-construction monotonicity witness (IS spec v1.11 §7.6) | All v2.6-and-earlier unit bodies — preserved verbatim per §0.3 |
| Coverage matrix delta: +1 row (C-IS-07 §7.6) | The CP drain call-site change + the strict-xfail REMOVAL — CP-owned at CP plan v2.39 U-CP-82 (the xfail lives in `harness-cp/tests/`) |
| DAG delta: NONE (amendment only; U-IS-11's edges unchanged; IS 0-outbound preserved) | Extending writer-owned authority to DIRECT appends — the §7.6 REGISTERED RESIDUAL, surfaced NOT absorbed; requires its own back-flow |
| | The executor offload itself — Runtime-owned at Runtime plan v2.50 (U-RT-140..144) |

### §0.3 Sections preserved verbatim from v2.6

All v2.6 sections stand except: this §0 (supersedes the v2.6 §0 as the head change-note; historical record preserved at v2.6); §1 spec inventory (refreshed: IS spec canonical at HEAD is **v1.11**; the §7.1 rows 1–6 and every other contract are byte-unchanged per the v1.11 PRESERVED-VERBATIM list — only the §7.1 row-7 addition + NEW §7.6 are new surface); §2 (the U-IS-11 amendment below — the v2.1-baseline U-IS-11 body is otherwise PRESERVED VERBATIM); §4 coverage matrix (+1 row). U-IS-01..U-IS-10, U-IS-12..U-IS-17, U-IS-18 (RETIRED), U-IS-19 — all PRESERVED VERBATIM.

### §0.4 Authority chain — no operator gate

v2.7 absorbs a RATIFIED fork rider already applied to the spec (IS v1.11, SPEC-APPLIED; clearance marker owed in the landing PR). The operator decision this arc surfaced is ALREADY TAKEN (Option B, 2026-07-18) — no further gate on this delta. The one spec-deferred choice (the API carrier by which the drain path requests writer-owned sampling — mode parameter / sentinel payload timestamp / dedicated writer entry-point; and whether the buffer-time placeholder field is retained diagnostically) is implementation discretion authorized at §7.6's deferred list and recorded at the U-IS-11 amendment Note, NOT pinned by the planner.

---

## §1 Spec inventory delta

PRESERVED VERBATIM from v2.6 §1, **plus**:

| Contract | Version | Status at v2.7 |
|---|---|---|
| **C-IS-07 §7.1 row 7 ("Timestamp authority (v1.11)") + NEW §7.6 (writer-owned drain-path timestamp authority)** | **IS spec v1.11 (NEW)** | **Covered at U-IS-11 (AMENDED this arc)** |

---

## §2 U-IS-11 AMENDMENT — writer-owned drain-path timestamp sampling (IS spec v1.11 §7.1 row 7 + §7.6)

The v2.1-baseline U-IS-11 body (`append_ledger_entry` + `EntryPayload`/`WriteKey`/`WriteResult`, ACs #1–#10) is PRESERVED VERBATIM; v2.7 adds:

**Implements (addition):** + C-IS-07 §7.1 row 7 + §7.6 (NEW at IS spec v1.11 — timestamp authority writer-owned on the buffered/branch-drain append surface).

**Depends on (unchanged):** [U-IS-05, U-IS-07, U-IS-08, U-IS-09] — NO new edges; NO cross-axis outbound edge (IS 0-outbound preserved; the CP drain producer consumes this contract from the CP side, CP plan v2.39 U-CP-82).

**Acceptance criteria (v2.7 additions; #1–#10 preserved verbatim):**

11. **(§7.6 "The contract".)** On the buffered/branch-drain append surface (the CP fan-out barrier drain feeding the single real writer, CP spec v1.32 §25.12 D1/D1.b), the persisted `timestamp` is WRITER-OWNED: sampled at each entry's append INSIDE the write serialization point (`_WRITE_LOCK` — the same critical section that reads the prior entry, computes `prior_event_hash`, and appends). Any caller/drain-supplied timestamp on the write payload on this path is a placeholder and is NOT the persisted value.
12. **(§7.6 consequence (a) — by construction.)** Sampling order equals physical-append order, so the C-IS-05 §5 monotonic-non-decreasing constraint holds BY CONSTRUCTION on this surface — concurrent sibling drains cannot invert. Consequence (b) is accepted contract: entries of one drain MAY carry distinct non-decreasing instants, each sampled at its own append (the pre-v1.11 one-drain-one-timestamp re-stamp semantic is superseded). Consequence (c): wall-clock regression between two lock-held samples remains a clock-source property under the C-IS-05 §5 clock-skew-tolerance framing, not a concurrency defect.
13. **(§7.6 "Surfaces that do NOT change".)** Every DIRECT append — the default `append_ledger_entry` contract: linear-workflow step appends, runtime audit/cost writes, administrative appends — keeps CALLER-SUPPLIED timestamp semantics BYTE-VERBATIM, enforced detect-then-refuse by the existing monotonicity rejection (AC #9 stands unchanged; `NonMonotonicTimestampError` beyond clock-skew tolerance). Silent widening of writer-owned authority to any direct surface is an acceptance FAILURE — the §7.6 REGISTERED RESIDUAL (extending it would change caller-supplied semantics for every existing direct producer and requires its own back-flow; surfaced, not absorbed).

**Tests (v2.7 additions — mutation-probed per PD-8):**

- **By-construction monotonicity witness:** `test_drain_surface_writer_owned_timestamps_monotonic_by_construction` — two threads driving interleaved drain-surface appends under the lock persist strictly non-decreasing timestamps in physical-append order regardless of capture order (mutation probe: revert to caller/drain-supplied outside-lock capture → the witness must fail with the inversion).
- **Placeholder-not-persisted witness:** `test_drain_supplied_timestamp_is_not_the_persisted_value_on_drain_surface` (mutation probe: persisting the payload timestamp on the drain path fails).
- **Direct-path preservation control:** `test_direct_append_caller_supplied_semantics_byte_verbatim` — the existing direct-path tests (`test_append_rejects_non_monotonic_timestamp` et al.) pass unchanged, and a direct append's persisted timestamp IS the caller-supplied value (mutation probe: extending writer-owned sampling to the direct path fails this control).
- **Cross-reference (not an IS test):** the end-to-end sibling-drain witness is the CP-side strict xfail `test_concurrent_sibling_drains_invert_timestamp` (`harness-cp/tests/test_workflow_driver_buffered_append.py:534-535`, strict=True at HEAD), which flips to a PASSING witness and has its marker REMOVED at the same impl arc — owned at CP plan v2.39 U-CP-82 (co-land pin ⊕ U-IS-11); B-48 cannot close over an accepted-failing concurrency witness.

**Note (implementation discretion per §7.6's deferred list — NOT pinned):** the API carrier by which the drain path requests writer-owned sampling (a mode parameter on `append_ledger_entry` / a sentinel payload timestamp / a dedicated writer entry-point), constrained to preserve the direct-path caller-supplied contract byte-verbatim; and whether the pre-existing buffer-time placeholder field is retained on the write payload for diagnostic purposes.

**Rollback boundary (addition):** revert the writer-owned sampling; the drain surface regresses to outside-lock capture — the pinned sibling-drain inversion (`NonMonotonicTimestampError`) reopens and the CP-side xfail must be re-marked.

---

## §3 Dependency graph delta

NONE. U-IS-11's within-axis edges are unchanged ([U-IS-05, U-IS-07, U-IS-08, U-IS-09]); ZERO new nodes; ZERO new edges. IS ← nothing new and IS 0-outbound preserved (Kahn-trivially acyclic: the amendment adds no edge in either direction; the CP-side consumption edge — CP plan v2.39 U-CP-82's use of this contract — is declared CP-side per the consumer-most-upstream convention, exactly as the v2.6 U-CP-84 → U-IS-19 precedent).

---

## §4 Coverage matrix delta

| Spec contract | Atomic unit |
|---|---|
| IS spec v1.11 C-IS-07 §7.1 row 7 + §7.6 (writer-owned drain-path timestamp authority; by-construction monotonicity; direct-path preservation; registered residual surfaced) | **U-IS-11 (AMENDED)** |

All other rows PRESERVED VERBATIM from v2.6 §4. ZERO contract-coverage gap at the IS axis.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.7 (delta over v2.6) |
| Authored at | Phase 7 — B-48 sync sub-agent dispatch offload apply leg (2026-07-19) |
| Authoring authority | IS spec v1.11 (C-IS-07 §7.1 row 7 + §7.6, `Spec_Information_Substrate_v1.md`) + `.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md` (RATIFIED 2026-07-18, OPTION B AS RECOMMENDED; §5 rider (d)) + `.harness/council-dyad-b48-apply-2026-07-18.md` (16/16 CONFIRM, zero deviations) |
| Net delta | ONE amended unit (U-IS-11 — ACs #11–#13 + witnesses); ZERO new units; ZERO new edges; +1 coverage row (C-IS-07 §7.6); ZERO IS-outbound edge (preserved) |
| Siblings (same arc) | `Implementation_Plan_Harness_Runtime_v2_50.md` (U-RT-140..144 NEW) + `Implementation_Plan_Control_Plane_v2_39.md` (U-CP-82/85/86/88/89 amended) |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
