# Implementation Plan — Operational Discipline v2.3

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_3.md` |
| Status | **Proposed** — P6-CK Iter 4 revision-cycle revision pass (within Iter 4 scope per Workflow v1.7 → v1.8 §4.1.4.6.3 proposed; non-blocking per Iter 4 entry-gate precedent) |
| Revision | v1 → v2 → v2.1 → v2.2 → **v2.3 (P6-CK Iter 4 revision-cycle absorbing F1-01 + F2-04 + F3-01 + F3-02 acknowledged-deferred per `Adversarial_Review_6_iter4.md` Disposition)** |
| Revision date | 2026-05-14 |
| Phase | 6 — Implementation planning (P6-CK Iter 4 revision-cycle; analogous to `P6-CK_Iter1_Revision_Cycle_Close_Handoff.md` precedent) |
| Skill | `implementation-planner` (revision-pass sub-mode per SKILL.md §8) at v2.3 |
| Promotion path | Accepted at P6-CK Iter 4 revision-cycle close + cascade-substrate-clearance issuance per `P6-CK_Iter4_Revision_Cycle_Entry_Handoff.md` §7.2 |
| Source-set | OD spec v1.3 + CP plan v2.3 (Segment 1 of this revision-cycle session) + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2 + PRD v1.1; cross-axis IS substrate at C-IS-05 + C-IS-06 (informational composition reference at v2.3 acceptance #15) |
| Entry authorization | `P6-CK_Iter4_Revision_Cycle_Entry_Handoff.md` §7.1; revision-cycle session-open OD confirmations (LLM-assisted; single combined session; governance-substrate propagation in same session); F3-02 disposition confirmed at session open |
| Exit gate | P6-CK Iter 4 revision-cycle close (subject to clean cascade-substrate-clearance disposition) |

**Closure status (preserved from v2.2).** `closure_pending_at_v2_2 = false`; F2-12 ✅ **CLOSED** at v2.2 per cascade execution path filed at CP plan v2.2 U-CP-55 §24.4. No reopening at v2.3.

**F3-02 disposition (revision-cycle session open).** Defer to future IS-axis revision-pass (default/recommended); cross-axis dependency `U-IS-NN` placeholder at U-OD-20 preserved as informational at v2.3 acceptance #11 annotation.

---

## §0 Change-note (v2.2 → v2.3)

### §0.1 Scope of revision

P6-CK Iteration 4 revision-cycle revision pass per `Adversarial_Review_6_iter4.md` Disposition Path A entry (5 Class 2 + 2 Class 3 findings; OD-plan-side scope: 3 of 5 Class 2 + 2 of 2 Class 3) + revision-cycle session-open OD confirmations. Absorbs four OD-plan-side findings:

- **F1-01 (Class 2; reclassified from proposing Class 1 at operator-selected Reading 1)** — §0.8 row 2 citation drift `§1.5 → §14.5.1` (within-artifact citation correction) + §0.1 Pattern P2 self-audit scope-statement extension to cover non-§14.5.x citations.
- **F2-04 (Class 2)** — U-OD-20 hash-chain integrity composition formula absorption: 8-field SHA-256 composition per OD spec v1.3 §14.5.1 lines 165–178 + F2 state-ledger entry shape extension absorption per ADR-D1 v1.2 §1.1.2.2 (`original_trace_id` + `original_span_id` fields) + ledger-write site unit ownership (entailed sub-defect routed per F3-02 acknowledged-deferred disposition below).
- **F3-01 (Class 3)** — U-OD-20 acceptance #12 prose alignment to spec §14.5.2 8-row matrix enumeration (drift only; test invariant unchanged; v2.2 prose described a 20-cell Cartesian-product parameter space inconsistent with the spec's 8-row enumeration).
- **F3-02 (Class 3)** — U-OD-20 cross-axis dependency on IS-axis ledger-schema unit `U-IS-NN` placeholder: **deferred to future IS-axis revision-pass** per session-open OD (default/recommended disposition); informational acceptance annotation preserved at acceptance #11 at v2.3.

**Pattern P2 self-audit scope-statement extension (v2.3 amendment per F1-01 absorption).** The Pattern P2 verification statement at v2.2 §0.1 scoped to "all 'per OD spec v1.3 §14.5.x' claims verify against source file" is **extended at v2.3 to cover ALL "per OD spec v1.3 §X.Y" citations + ALL "per ADR-D{N} v1.{N} §X.Y" citations + ALL "per `Spec_Information_Substrate_v1.md` §X.Y" cross-axis citations across the OD plan body** — not only F2-12-cascade-scoped §14.5.x sub-sections. The §1.5 typo at v2.2 §0.8 row 2 fell outside the prior narrower scope; the extended scope forecloses analogous scoping defects at future revision passes. Workflow v1.7 §2.3.3.1 clause (iii) citation-anchor substrate-verification discipline applied across the extended scope. This extension is the analog of the CP plan v2.3 §0.1 Pattern P2 scope-statement extension authored in Segment 1 of this same revision-cycle session.

**Workflow v1.7 §7 fidelity-grammar discipline applied across all v2.3 amendment sites.** No Pattern P1 cross-artifact name drift (`original_trace_id` + `original_span_id` + 8-field SHA-256 composition + field-ordering all consistent across CP spec v1.3 + OD spec v1.3 + ADR-D1 v1.2 §1.1.2.2 + ADR-D6 v1.2 §1.5 + this OD plan v2.3). No Pattern P2 verbatim-claim-contradicted under extended scope (all v2.3 citations resolve to canonical declaration sites at source files).

### §0.2 Sections preserved verbatim (from v2.2)

| Section | Preservation rationale |
|---|---|
| §0a Front matter (OD selections + plan-level invariants + F2-12 ACTIVE→CLOSED engagement summary) | No revision-cycle finding at v2.3 |
| §1 Spec inventory §1.1 + §1.2 + §1.3 F2-12 CLOSED engagement location | No revision-cycle finding |
| §2 Atomic-unit decomposition Clusters 1 through 4 (U-OD-01 through U-OD-17) | No revision-cycle finding |
| §3.1 + §3.2 + §3.3 (U-OD-09 through U-OD-13) | No revision-cycle finding |
| §3.4 (U-OD-14 cardinality-safe through U-OD-17) | No revision-cycle finding |
| §3.5.1 U-OD-18 + §3.5.2 U-OD-19 + §3.5.4 U-OD-21 + §3.5.5 U-OD-22 | No revision-cycle finding |
| §3.5.3 U-OD-20 — acceptance criteria #1 through #10 + #13 + #14 + section heading + F2-12 engagement preamble + v2.2-amendment-site signature block (SpanCostRecord, dedupe_on_replay, cause_attribution_invariance_check, per_attempt_cost_attribution_roll_up, F2_12 records + constants) | No revision-cycle finding at these sites; v2.3 amendment scope limited to acceptance #11 (F3-02 annotation), #12 (F3-01 prose alignment), new #15 (F2-04 hash-chain absorption), corresponding signatures + tests |
| §3.6 + §3.7 (U-OD-23 through U-OD-33) | No revision-cycle finding |
| §3.8 (U-OD-34) | No revision-cycle finding |
| §4 Dependency graph | No graph delta at v2.3 |
| §5 Spec-traceability | Cell expansion at U-OD-20 per §0.4 below; cluster-to-contract mapping unchanged |
| §6 Persona linkage + §7 Cross-axis citation + §8 PRD-trace + §9 Forward-flagged + §10 ADR-trace + §11 Anti-pattern audit + §12 Coherence-pass summary | No revision-cycle finding |
| §[carry-forwards] [CF-1] F2-12 ✅ CLOSED at v2.2 | No v2.3 reopening |

### §0.3 Sections revised (v2.2 → v2.3)

| Site | Revision shape | Resolves |
|---|---|---|
| §0.1 Pattern P2 self-audit scope-statement | Extended to cover ALL OD spec citations + ALL ADR citations + ALL cross-axis IS spec citations (was scoped to "§14.5.x only" at v2.2) | F1-01 |
| §0.8 row 2 (hash-chain integrity composition forward-flag) | Citation `§1.5 → §14.5.1` correction; disposition transitioned to ✅ CLOSED at v2.3 by F2-04 absorption at U-OD-20 acceptance #15 + signatures + tests | F1-01 + F2-04 |
| U-OD-20 §3.5.3 section heading | Extended: "+ hash-chain integrity composition" added after "per-attempt cost-attribution"; v2.3 amendment-source annotation added | F2-04 |
| U-OD-20 `Implements` clause | Cross-cite added: C-IS-05 hash-chain construction discipline (cross-axis IS substrate) + ADR-D1 v1.2 §1.1.2.2 (F2 state-ledger entry shape extension) for v2.3 composition surface | F2-04 |
| U-OD-20 `Depends on` clause | F3-02 acknowledged-deferred annotation at `U-IS-NN` placeholder (cross-axis: IS — C-IS-10 §10.2) | F3-02 |
| U-OD-20 Inputs | Annotated v2.3 — hash-chain composition formula at OD spec v1.3 §14.5.1 lines 165–178; cross-axis IS substrate at C-IS-05 hash-chain construction discipline + ADR-D1 v1.2 §1.1.2.2 ledger entry shape extension; CP plan cross-axis substrate bumped v2.2 → v2.3 (Segment 1 filing) | F2-04 |
| U-OD-20 Cross-axis dependency resolution paragraph | F3-02 acknowledged-deferred declaration: IS-axis ledger-write site unit ownership remains the deferred resolution target; OD-side composition surface at acceptance #15 stands at v2.3 absent IS-axis resolution | F3-02 |
| U-OD-20 Files affected | Extended with hash-chain composition site (logical: `f2-state-ledger-hash-chain-composition` — v2.3 new) | F2-04 |
| U-OD-20 Signatures | New `F2StateLedgerEntry` record extended with `original_trace_id` + `original_span_id` fields per ADR-D1 v1.2 §1.1.2.2 + new `ledger_entry_hash` function declaring 8-field SHA-256 composition per OD spec v1.3 §14.5.1 lines 165–178 verbatim | F2-04 |
| U-OD-20 acceptance #11 (cross-axis edge) | Extended with F3-02 acknowledged-deferred annotation: `U-IS-NN` placeholder routes to future IS-axis revision-pass per session-open OD; OD-side composition surface at acceptance #15 independent of IS-axis resolution | F3-02 |
| U-OD-20 acceptance #12 (dedup algorithm correctness) | Prose alignment: replace "5 × {1, 2..N} × {present, absent}" Cartesian-product parameter-space framing with explicit 8-row enumeration per spec §14.5.2 (rows 1–8 verbatim with cells); note absence of `(2, reconciler_iteration)` and `(2, wal_consume)` rows per spec | F3-01 |
| U-OD-20 acceptance #15 (new) | Hash-chain integrity composition absorption — `ledger_entry_hash` MUST compute SHA-256 of canonical 8-field concatenation per OD spec v1.3 §14.5.1 lines 165–178 verbatim with field-ordering byte-exact; three-way seam (C3/C10/C11) preserved without Layer-3 promotion per F2-12 council §5.3 | F2-04 |
| U-OD-20 Tests | Extended: `_dedup_outcome_matrix_8_cells_match_spec_v1_3_verbatim` renamed for explicit version anchoring; new `_ledger_entry_hash_8_field_composition`; new `_ledger_entry_hash_field_ordering_matches_spec_v1_3_verbatim`; new `_ledger_entry_hash_output_bytes_32`; new `_f2_state_ledger_entry_carries_original_trace_id`; new `_f2_state_ledger_entry_carries_original_span_id`; new `_ledger_entry_hash_consumes_extended_f2_state_ledger_entry_shape` | F2-04 + F3-01 |
| U-OD-20 Rollback boundary | Extended: hash-chain composition regression + cross-axis IS substrate dissolution; v2.2-amendment rollback boundaries preserved verbatim | F2-04 |

### §0.4 Coverage matrix delta

| Coverage cell | At v2.2 | At v2.3 |
|---|---|---|
| C-OD-14 §14.5.1 hash-chain integrity composition formula (8-field SHA-256) | Not covered (forward-flagged at v2.2 §0.8 row 2 with §1.5 citation typo) | ✅ Covered at U-OD-20 acceptance #15 + signatures (`ledger_entry_hash` + extended `F2StateLedgerEntry`) + tests |
| C-OD-14 §14.5.2 dedup outcome matrix 8-row enumeration (cardinality precision) | Partially covered — test invariant correct (8 cells); acceptance #12 prose drifted to 20-cell parameter-space framing | ✅ Covered at U-OD-20 acceptance #12 (v2.3 prose aligned to 8-row enumeration) + test `_dedup_outcome_matrix_8_cells_match_spec_v1_3_verbatim` |
| Cross-axis to IS C-IS-05 + C-IS-06 hash-chain construction discipline (consumed at OD §14.5.1 composition) | Cross-axis edge declared via U-IS-NN placeholder; no acceptance criterion exercising the composition | ✅ Covered at U-OD-20 acceptance #15 (OD-side composition surface; IS-axis canonical site cross-cited) + F3-02 acknowledged-deferred at acceptance #11 |

Cluster-to-contract mapping unchanged.

### §0.5 Dependency graph delta

No dependency graph changes at v2.3. U-OD-20 `Depends on: [U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)]` preserved structurally; the cross-axis placeholder is annotated F3-02-acknowledged-deferred at acceptance #11 (informational; future IS-axis revision-pass resolves placeholder). Aggregate DAG node count + edge count + topological sort + acyclic invariant all unchanged from v2.2.

### §0.6 Substrate-version-citation table

No OD-side substrate-version delta from v2.2. v2.3 cross-axis citation set extended at U-OD-20 inputs to include `Spec_Information_Substrate_v1.md` C-IS-05 + C-IS-06 hash-chain construction discipline (informational composition; substrate version cited at v1 per prior cross-axis references); cross-axis CP plan citation bumped to v2.3 (Segment 1 filing of this revision-cycle session).

| Substrate | Version cited at v2.3 |
|---|---|
| ADR-D1 | v1.2 |
| ADR-D6 | v1.2 |
| ADD | v1.3 |
| PRD | v1.1 |
| OD spec | v1.3 |
| CP spec | v1.3 (cross-axis citation only) |
| CP plan | v2.3 (cross-axis substrate at U-OD-20 closure_path inheritance; bumped from v2.2 reflecting Segment 1 filing) |
| IS spec | v1 (cross-axis citation at U-OD-20 acceptance #15 + signatures; C-IS-05 + C-IS-06 hash-chain construction discipline) |
| Workflow | v1.7 (v1.8 amendment proposed at Path δ revision-log; non-blocking per Iter 4 entry-gate precedent) |

Per Workflow v1.7 §7 use-latest-version body-citation-alignment.

### §0.7 Status

`Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` requires P6-CK Iter 4 revision-cycle close clean disposition + cascade-substrate-clearance issuance per `P6-CK_Iter4_Revision_Cycle_Entry_Handoff.md` §7.2.

### §0.8 Forward-flagged concerns (v2.3 update)

| Concern | v2.3 disposition |
|---|---|
| U-OD-34 carry-forward inheritance at v2.1 | NOT in revision-cycle scope at v2.3; v2.1+v2.2 hybrid-fidelity acceptance #7 preserved verbatim |
| v2.2 §0.8 row 2 (OD spec v1.3 **§14.5.1** hash-chain integrity composition formula; **v2.2 cited §1.5 — typo corrected at v2.3 per F1-01 absorption**) | ✅ CLOSED at v2.3 by F1-01 citation correction + F2-04 substantive absorption at U-OD-20 acceptance #15 + `ledger_entry_hash` function + extended `F2StateLedgerEntry` record signatures + tests |
| v2.2 §0.8 row 3 (OD spec v1.3 §14.5.3 `replay_semantic_divergence` cause_attribution catalog extension — new C5 enum value) | NOT absorbed at v2.3 within revision-cycle scope (preserved from v2.2 as forward-flagged); affects future ADR-D5 revision pass + corresponding OD spec + plan absorption per v2.2 disposition; the OD plan v2.2 + v2.3 U-OD-20 acceptance #13 ESCALATION semantics reference the value, but the C5 catalog extension itself requires D5 revision-pass to canonicalize |
| **F3-02 acknowledged-deferred (v2.3 new)** — U-OD-20 cross-axis dependency on IS-axis ledger-schema unit `U-IS-NN` placeholder | Deferred to future IS-axis revision-pass per session-open OD (default/recommended disposition). Cross-axis edge declaration preserved as informational at U-OD-20 acceptance #11. **Note on F3-02's entailed sub-defect from F2-04 evidence** (ledger-write site unit ownership unspecified in OD plan v2.2): at v2.3 the OD-side composition surface for the hash-chain at U-OD-20 acceptance #15 is independent of the IS-axis canonical ledger-write site unit identification — U-OD-20 consumes the canonical 8-field SHA-256 composition formula at OD-side cost-attribution + dedup composition; the IS-axis ledger-write site unit (where chain construction is materialized at write-time per C-IS-05 + C-IS-06 §6.3) remains the deferred resolution target. |

### §0.9 Prior revision history (v1 → v2.2; archival)

[Preserved verbatim from v2.2 §0.9 (which preserves from v2.1 + v2 historical record).]

### §0.10 v2.3 coherence-pass summary

| Pass | Status |
|---|---|
| §1 Spec inventory | ✅ PASS — no substrate-version delta on OD side; v2.3 cross-axis citation extension at U-OD-20 inputs (C-IS-05 + C-IS-06 hash-chain construction discipline) is informational composition reference |
| §3 Atomic-unit decomposition | ✅ PASS — U-OD-20 revised per F2-04 + F3-01 + F3-02 acknowledged-deferred annotation; all other units preserved verbatim from v2.2 per strict-narrow revision-cycle scope discipline |
| §4 Dependency graph | ✅ PASS — no graph changes; acyclic invariant preserved |
| §5 Spec-traceability | ✅ PASS — U-OD-20 → C-OD-14 §14.4 + §14.5 (CLOSED at v1.3) + §14.5.1 (dedup algorithm preserved + **hash-chain integrity composition new at v2.3**) + §14.5.2 (orthogonality, prose-aligned at v2.3) + §14.5.3 + §14.5.4 all canonically cited; cross-axis cells to C-IS-05 + C-IS-06 declared as informational composition surface |
| §0.1 Pattern P2 self-audit scope-statement extension | ✅ PASS — extended scope covers ALL OD spec citations + ALL ADR citations + ALL cross-axis IS spec citations across plan body |
| §11 Anti-pattern audit | ✅ PASS — v2.2 §0.8 row 2 closed at v2.3 by substantive absorption (F1-01 + F2-04); row 3 (replay_semantic_divergence C5 catalog extension) preserved as forward-flagged; F3-02 acknowledged-deferred annotated at U-OD-20 acceptance #11 |
| Cross-artifact name-drift check | ✅ PASS — Pattern P1 verified at v2.3 amendment sites: `original_trace_id` + `original_span_id` + `prev_entry_hash` + `idempotency_key` + `engine_attrs` + `fail_class` + `cause_attribution` + `ts_iso8601` + 8-field SHA-256 composition + field-ordering all consistent across ADR-D1 v1.2 §1.1.2.2 + ADR-D6 v1.2 §1.5 + OD spec v1.3 §14.5.1 + IS spec C-IS-05 + this OD plan v2.3 |

**Pattern P2 (verbatim-claim-contradicted) prevention at v2.3 under extended scope.** U-OD-20 acceptance #12 8-row enumeration verified byte-exact against OD spec v1.3 §14.5.2 (lines 195–204). U-OD-20 acceptance #15 8-field SHA-256 composition + field-ordering verified byte-exact against OD spec v1.3 §14.5.1 (lines 165–178). §0.8 row 2 citation typo `§1.5 → §14.5.1` corrected (the canonical resolving section). All v2.3 `per OD spec v1.3 §X.Y` + `per ADR-D{N} v1.{N} §X.Y` + cross-axis `per C-IS-{N} §X.Y` citations verified per Workflow v1.7 §2.3.3.1 clause (iii).

---

## §0a Front matter

[§0a.1 OD selections + §0a.2 plan-level invariants + §0a.3 F2-12 engagement summary (transitioned to CLOSED at v2.2) preserved verbatim from v2.2.]

---

## §1 Spec inventory

[§1.1 Contract inventory + §1.2 Cluster decomposition realized + §1.3 F2-12 engagement location (CLOSED at v2.2) preserved verbatim from v2.2.]

---

## §2 Atomic-unit decomposition — Clusters 1 through 4

[U-OD-01 through U-OD-17 preserved verbatim from v2.2. No revision-cycle finding at any Cluster 1–4 unit.]

---

## §3 Cluster 5 — D6 cost-attribution + dashboard + collector

### §3.1 + §3.2 + §3.3

[Preserved verbatim from v2.2.]

### §3.4 Cluster decomposition U-OD-14 through U-OD-17

[Preserved verbatim from v2.2.]

### §3.5 Cluster decomposition U-OD-18 through U-OD-22

[§3.5.1 U-OD-18 + §3.5.2 U-OD-19 preserved verbatim from v2.2.]

#### §3.5.3 U-OD-20 — Compose idempotency-key join + dedup algorithm + per-attempt cost-attribution + hash-chain integrity composition + F2-12 ✅ CLOSED affected-contract notation (v2.3 amendment absorbing OD spec v1.3 §14.5.1 hash-chain composition formula per F2-04 + acceptance #12 prose alignment per F3-01 + F3-02 acknowledged-deferred cross-axis annotation)

**Implements (v2.3 amendment):** [C-OD-14 §14.4 idempotency-key join + §14.5 (CLOSED at v1.3) + §14.5.1 trace-ingestion dedup algorithm (preserved from v2.2 absorption) + §14.5.1 **hash-chain integrity composition formula** (NEW v2.3 absorption per F2-04 at acceptance #15 + signatures) + §14.5.2 replay-aware dedup with retry orthogonality (preserved from v2.2 absorption; **acceptance #12 prose realigned at v2.3 per F3-01**) + §14.5.3 cause_attribution invariance check (preserved from v2.2 absorption) + §14.5.4 per-attempt cost-attribution discipline (preserved from v2.2 absorption); **cross-cite `Spec_Information_Substrate_v1.md` C-IS-05 + C-IS-06 hash-chain construction discipline (canonical IS-axis substrate; OD-side composition surface declared at v2.3 acceptance #15)** + **cross-cite ADR-D1 v1.2 §1.1.2.2 F2 state-ledger entry shape extension (`original_trace_id` + `original_span_id` fields; consumed at v2.3 hash-chain composition)**]

**Depends on (v2.3 — F3-02 acknowledged-deferred annotation):** [U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2 — **F3-02 acknowledged-deferred per revision-cycle session-open OD (default/recommended disposition: defer to future IS-axis revision-pass); U-IS-NN placeholder preserved as informational at v2.3**)]

**Inputs (v2.3 amendment):** [v2.2 inputs preserved verbatim:] OD spec **v1.3** §14.4 idempotency-key join (Replay-safe composition row revised at v1.3); §14.5 F2-12 ✅ CLOSED affected-contract notation; §14.5.1 trace-ingestion dedup algorithm pseudocode; §14.5.2 replay-aware dedup with retry orthogonality (8-row dedup outcome matrix); §14.5.3 cause_attribution invariance check at deterministic_replay; §14.5.4 per-attempt cost-attribution discipline. **[v2.3 additions per F2-04:]** OD spec v1.3 §14.5.1 hash-chain integrity composition formula at lines 165–178 (8-field SHA-256 composition); cross-axis IS substrate at `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape + composition with cross-axis seams) + C-IS-06 (hash-chain integrity construction discipline §6.1–§6.5); ADR-D1 v1.2 §1.1.2.2 F2 state-ledger entry shape extension declaring `original_trace_id` + `original_span_id` fields. **[v2.3 bump:]** CP plan cross-axis substrate at U-CP-55 §24.4 closure_path bumped from CP plan v2.2 to **CP plan v2.3** (Segment 1 filing of this revision-cycle session; closure_path entries themselves preserved verbatim from CP plan v2.2 — the bump is informational versioning).

**Cross-axis dependency resolution (v2.3 amendment).** IS plan U-IS-NN implementing C-IS-10 §10.2 (idempotency-key join export) is the canonical resolution target for the IS-axis ledger-schema unit ownership. **At v2.3 this dependency is acknowledged-deferred to future IS-axis revision-pass per F3-02 disposition** (session-open OD: default/recommended — defer to future IS-axis revision-pass). The OD-side composition surface (this unit's hash-chain absorption at acceptance #15) is **independent of the IS-axis canonical ledger-write site unit identification** — U-OD-20 consumes the canonical 8-field SHA-256 composition formula at OD-side cost-attribution + dedup composition surface per OD spec v1.3 §14.5.1 lines 165–178; the IS-axis ledger-write site unit (where chain construction is materialized at write-time per C-IS-06 §6.3) is the deferred resolution target. The three-way seam (C3 storage primitive / C10 hash-chain integrity discipline / C11 sqlite implementation) is preserved without Layer-3 promotion per `F2-12_Council_Deliberation_Output.md` §5.3 reconciliation; U-OD-20 v2.3 acceptance #15 declares the OD-axis surface of this three-way seam.

**Files affected (v2.3 amendment):** [v2.2 files preserved:] idempotency-key join composition + dedup algorithm + per-attempt cost-attribution + F2-12 closed-contract notation (logical name: `od-cost-attribution-idempotency-join-dedup-algorithm-and-f2-12-closed-notation`). **[v2.3 addition:]** F2 state-ledger hash-chain composition site (logical name: `f2-state-ledger-hash-chain-composition` — OD-side composition surface for the 8-field SHA-256 chain construction declared at OD spec v1.3 §14.5.1; consumes the IS-axis canonical chain construction at C-IS-06 §6.3).

**F2-12 ✅ CLOSED engagement (preserved verbatim from v2.2).** [Preserved verbatim from v2.2; cascade-close declaration at OD plan v2.2 cascade Step 6b intact; no v2.3 reopening.]

**Signatures (v2.3 amendment — `F2StateLedgerEntry` record + `ledger_entry_hash` function added; existing v2.2 signatures preserved):**

```
# v2.2 signatures preserved verbatim:
# SpanCostRecord (9 fields), attach_idempotency_key_to_cost_record, dedupe_on_replay,
# DedupOutcome enum (5 variants including ESCALATE_REPLAY_SEMANTIC_DIVERGENCE),
# cause_attribution_invariance_check, InvarianceCheckResult enum,
# per_attempt_cost_attribution_roll_up, ParentOperationTotalCost record,
# propagate_to_subagent, F2_12_DeferredSurface enum (preserved as historical record),
# F2_12_AffectedContractNotation record, FilingStatus enum, RevisionStep record,
# F2_12_CLOSURE_PATH 9-entry constant, F2_12_NOTATION
# — all preserved verbatim from v2.2.

# v2.3 new — F2 state-ledger entry shape extension per ADR-D1 v1.2 §1.1.2.2
# Canonical record shape at IS axis per C-IS-05; OD-side composition reference for hash-chain consumption.
record F2StateLedgerEntry {
  idempotency_key    : string         // per C-IS-05 + §10.2 (harness-canonical join key)
  original_trace_id  : string         // v1.3 amendment per ADR-D1 v1.2 §1.1.2.2 (NEW at v1.3)
  original_span_id   : string         // v1.3 amendment per ADR-D1 v1.2 §1.1.2.2 (NEW at v1.3)
  engine_attrs       : EngineAttrs    // per ADR-D1 v1.2 §1.1.1 4-attribute engine.* namespace
  fail_class         : FailClass      // per C5 5-class fail-class taxonomy at c5-validation-contract SKILL.md s14 §7.5(d)
  cause_attribution  : string         // open-set enum from C5 cause_attribution catalog at c5-validation-contract SKILL.md s14 §7.5(a)
  ts_iso8601         : string         // entry timestamp (ISO 8601)
  prev_entry_hash    : Bytes32        // per C-IS-06 §6.3 chain construction (32-byte SHA-256 of prior entry)
  entry_hash         : Bytes32        // computed by ledger_entry_hash; per C-IS-06 §6.2 + this unit acceptance #15
}

# v2.3 new — hash-chain integrity composition per OD spec v1.3 §14.5.1 lines 165-178 verbatim
# OD-side composition surface; consumes IS-axis canonical chain construction at C-IS-06 §6.3.
fn ledger_entry_hash(
  entry           : F2StateLedgerEntry
) -> Bytes32
  # = SHA-256(
  #     entry.prev_entry_hash      ||
  #     entry.idempotency_key      ||
  #     entry.original_trace_id    ||   # v1.3 amendment per ADR-D1 v1.2 §1.1.2.2
  #     entry.original_span_id     ||   # v1.3 amendment per ADR-D1 v1.2 §1.1.2.2
  #     entry.engine_attrs         ||
  #     entry.fail_class           ||
  #     entry.cause_attribution    ||
  #     entry.ts_iso8601
  #   )
  # Field ordering byte-exact to OD spec v1.3 §14.5.1 lines 165-178.
  # Three-way seam (C3 storage primitive / C10 hash-chain integrity discipline / C11 sqlite
  # implementation per c11-operator-local SKILL.md §4.1.28) preserved without Layer-3 promotion
  # per F2-12_Council_Deliberation_Output.md §5.3 reconciliation.
```

**Acceptance criteria (v2.3 amendment):**

1.–10. [Preserved verbatim from v2.2 — `SpanCostRecord` 9 fields, `attach_idempotency_key_to_cost_record` replay-safe composition, `dedupe_on_replay` algorithm specified per §14.5.1, `propagate_to_subagent` per C-AS-15 §15.6, F2-12 closure status, ✅ closure realized at OD plan v2.2 cascade Step 6b, 9-entry `F2_12_CLOSURE_PATH`, `closure_pending_at_v2_2 == false`, closure execution path complete.]

11. **(v2.3 amendment to v2.2 #11 — F3-02 acknowledged-deferred annotation.)** Cross-axis edge per OD-S4-3.A: `Depends on: [U-IS-NN (cross-axis: IS — C-IS-10 §10.2 unit)]`. Resolution at U-OD-34 (preserved from v2.2). **At v2.3, F3-02 acknowledged-deferred per revision-cycle session-open OD: defer to future IS-axis revision-pass; `U-IS-NN` remains an informational placeholder at v2.3. The OD-side composition surface declared at this unit's acceptance #15 (hash-chain integrity composition per OD spec v1.3 §14.5.1) is independent of the IS-axis canonical ledger-write site ownership and stands at v2.3 absent the IS-axis resolution.** Future IS-axis revision-pass will resolve `U-IS-NN` to a concrete IS-axis ledger-schema unit; at that point this acceptance criterion's cross-axis edge will be canonical rather than placeholder, and the OD-side composition at #15 will gain cross-axis dependency to the canonical IS-axis unit.

12. **(v2.3 amendment to v2.2 #12 prose per F3-01 absorption.)** Dedup algorithm correctness — `dedupe_on_replay` MUST produce `DedupOutcome` consistent with OD spec v1.3 §14.5.1 pseudocode **for each of the 8 rows enumerated at the dedup outcome matrix at §14.5.2 (lines 195–204 verbatim):**
   - **row 1**: `(retry.attempt_number=1, engine.replay_disposition=deterministic_replay)` → `DROP` if F2 ledger entry matches (idempotency_key + trace_id + span_id + cause_attribution); `ESCALATE` per §14.5.3 invariance check if cause_attribution mismatch
   - **row 2**: `(1, checkpoint_resume)` → `RECORD_REPLAY_DERIVED` as new replay-derived span; cost accrues for attempt 1
   - **row 3**: `(2, deterministic_replay)` → `DROP` if F2 ledger entry for attempt 2 matches; `ESCALATE` if mismatch
   - **row 4**: `(2, checkpoint_resume)` → `RECORD_REPLAY_DERIVED` as attempt 2's replay-derived span; cost accrues for attempt 2
   - **row 5**: `(1, no_replay)` → `RECORD_FIRST_INGESTION` if first ingestion; `ERROR_UNEXPECTED_RE_INGESTION_FOR_NO_REPLAY` if re-ingestion (unexpected for `no_replay`)
   - **row 6**: `(2, no_replay)` → `RECORD` as new attempt 2; cost accrues for attempt 2
   - **row 7**: `(1, reconciler_iteration)` → `RECORD` with `reconciler.iteration_number` discriminator
   - **row 8**: `(1, wal_consume)` → `RECORD` with `wal.consumer_group` discriminator
   
   **Note on parameter-space cardinality (v2.3 prose alignment per F3-01).** The spec §14.5.2 8-row enumeration does NOT include `(retry.attempt_number=2, engine.replay_disposition=reconciler_iteration)` or `(retry.attempt_number=2, engine.replay_disposition=wal_consume)` rows; these dispositions are paired with `retry.attempt_number=1` in the spec enumeration. The v2.2 prose at this acceptance criterion described the parameter space as "5 × {1, 2..N} × {present, absent}" (implying a 20-cell Cartesian product), which drifted from the spec's explicit 8-row enumeration. **At v2.3 the prose is realigned to the 8-row enumeration; the test invariant is unchanged** (the v2.2 test `test_dedup_outcome_matrix_8_cells_match_spec` already asserted 8-cell match; renamed at v2.3 to `test_dedup_outcome_matrix_8_cells_match_spec_v1_3_verbatim` for explicit version anchoring).

13. (Preserved verbatim from v2.2 #13.) Invariance check ESCALATION semantics — `cause_attribution_invariance_check` MUST emit ESCALATE event with `validator.fail.class = TERMINAL_FAIL_EXIT` + `validator.fail.cause_attribution = "replay_semantic_divergence"` + `validator.fail.permanence = PERMANENT` on mismatch per OD spec v1.3 §14.5.3. The escalate event MUST be always-sampled per C-OD-09 §9.2 (validator.fail.permanence=permanent always-sampled).

14. (Preserved verbatim from v2.2 #14.) Per-attempt cost-attribution roll-up — `per_attempt_cost_attribution_roll_up` MUST compute `total_cost = Σ cost(retry-attempt child span_i) for i in 1..N` per OD spec v1.3 §14.5.4; `deterministic_replay` re-reads contribute ZERO to the sum (filtered via `is_replay_derived` flag set by dedup algorithm). The roll-up MUST compose with `C-OD-23` operator-burden eval primitive at the per-operation aggregation level without re-aggregation.

15. **(v2.3 new — hash-chain integrity composition formula absorption per F2-04.)** `ledger_entry_hash` MUST compute `SHA-256` over the canonical 8-field concatenation per OD spec v1.3 §14.5.1 lines 165–178 verbatim, in the exact field ordering:
    
    ```
    SHA-256(
      prev_entry_hash    ||
      idempotency_key    ||
      original_trace_id  ||
      original_span_id   ||
      engine_attrs       ||
      fail_class         ||
      cause_attribution  ||
      ts_iso8601
    )
    ```
    
    The function consumes the `F2StateLedgerEntry` record extended at v1.3 per ADR-D1 v1.2 §1.1.2.2 (the `original_trace_id` + `original_span_id` fields are v1.3 amendments to the v1.2 ledger entry shape). Composition surfaces:
    - **OD-side composition at U-OD-20** — this function declared at this unit's signatures per §14.5.1 lines 165–178 verbatim
    - **IS-axis canonical chain construction at C-IS-06 §6.3** (cross-axis citation; canonical at IS axis; OD-side acknowledges canonical site without re-declaring)
    - **sqlite ledger_entries schema implementation per `c11-operator-local` SKILL.md §4.1.28** (substrate authority for the on-disk shape)
    - **Three-way seam (C3 storage primitive / C10 hash-chain integrity discipline / C11 sqlite implementation)** preserved without Layer-3 promotion per `F2-12_Council_Deliberation_Output.md` §5.3 reconciliation
    
    The `entry_hash` field of each `F2StateLedgerEntry` is computed at write-time by this function; tamper-evidence verification per C-IS-06 §6.4 chain-verification-on-demand procedure is the canonical IS-axis surface. The v2.3 OD-side absorption acknowledges the IS-axis canonical site and declares the OD-side cost-attribution + dedup join consumes the extended 8-field entry shape. F3-02 acknowledged-deferred at acceptance #11 does NOT block this composition surface — the OD-side composition stands at v2.3 absent IS-axis canonical resolution.

**Tests (v2.3 amendment):**

[v2.2 tests preserved verbatim except as noted below; v2.3 new tests appended.]

v2.2 preserved tests (unchanged at v2.3):
- `test_span_cost_record_nine_fields`
- `test_idempotency_key_attached_to_cost_record`
- `test_dedupe_on_replay_drops_deterministic_re_read`
- `test_dedupe_on_replay_records_replay_derived_for_checkpoint_resume`
- `test_dedupe_on_replay_records_replay_derived_for_reconciler_iteration`
- `test_dedupe_on_replay_records_replay_derived_for_wal_consume`
- `test_dedupe_on_replay_errors_on_unexpected_re_ingestion_for_no_replay`
- `test_cause_attribution_invariance_check_passes_when_match`
- `test_cause_attribution_invariance_check_escalates_on_mismatch`
- `test_invariance_check_escalation_validator_fail_terminal_fail_exit`
- `test_invariance_check_escalation_replay_semantic_divergence_cause_attribution`
- `test_invariance_check_escalation_permanence_permanent`
- `test_invariance_check_escalation_always_sampled`
- `test_per_attempt_cost_attribution_roll_up_sums_attempts_1_to_n`
- `test_per_attempt_cost_attribution_roll_up_excludes_deterministic_replay_re_reads`
- `test_per_attempt_cost_attribution_composes_with_c_od_23_eval_primitive`
- `test_f2_12_closure_path_nine_entries`
- `test_f2_12_closure_status_closed`
- `test_propagate_to_subagent_derives_idempotency_key`

v2.3 amendment tests:
- `test_dedup_outcome_matrix_8_cells_match_spec_v1_3_verbatim` (v2.3 amendment — renamed from `test_dedup_outcome_matrix_8_cells_match_spec` for explicit version anchoring; assertion unchanged — 8-row byte-exact match against spec §14.5.2 lines 195–204)
- `test_dedup_outcome_matrix_excludes_attempt_2_reconciler_iteration_row` (v2.3 new — verifies spec absence is honored, no spurious row)
- `test_dedup_outcome_matrix_excludes_attempt_2_wal_consume_row` (v2.3 new — same)

v2.3 new tests for F2-04 hash-chain absorption:
- `test_ledger_entry_hash_8_field_composition` (v2.3 new — verifies SHA-256 input is concatenation of exactly 8 fields)
- `test_ledger_entry_hash_field_ordering_matches_spec_v1_3_verbatim` (v2.3 new — verifies the 8 fields are concatenated in exact order: `prev_entry_hash || idempotency_key || original_trace_id || original_span_id || engine_attrs || fail_class || cause_attribution || ts_iso8601` per spec §14.5.1 lines 165–178)
- `test_ledger_entry_hash_output_bytes_32` (v2.3 new — verifies SHA-256 output is 32 bytes; chain integrity baseline)
- `test_f2_state_ledger_entry_carries_original_trace_id` (v2.3 new — verifies `original_trace_id` field present per ADR-D1 v1.2 §1.1.2.2)
- `test_f2_state_ledger_entry_carries_original_span_id` (v2.3 new — verifies `original_span_id` field present per ADR-D1 v1.2 §1.1.2.2)
- `test_ledger_entry_hash_consumes_extended_f2_state_ledger_entry_shape` (v2.3 new — verifies the function consumes the v1.3-extended 9-field record shape, not the prior pre-extension shape)
- `test_ledger_entry_hash_deterministic_across_runs` (v2.3 new — given identical entry input, function produces identical 32-byte output; canonicalization determinism baseline per C-IS-06 §6.1)

**Rollback boundary (v2.3 amendment):** Revert v2.3 hash-chain composition absorption — revert `ledger_entry_hash` function + revert extended `F2StateLedgerEntry` record reference (`original_trace_id` + `original_span_id` fields) + revert acceptance #15 + revert tests for F2-04. Downstream impact: hash-chain integrity composition at OD plan layer regresses (v2.2 §0.8 row 2 reopens as F2-04 absorption regression); cross-axis IS-side canonical hash-chain construction at C-IS-06 §6.3 loses OD-side composition acknowledgment; tamper-evidence verification per C-IS-06 §6.4 retains IS-axis canonical site but loses OD-side cost-attribution + dedup join coordination; the §14.5.1 spec sub-section's hash-chain composition formula (lines 165–178) loses CP/OD plan-side coverage. F3-02 cross-axis dependency placeholder unaffected by revert (preserved at acceptance #11 informational; further-deferred to future IS-axis revision-pass). v2.2-amendment-site rollback boundaries (dedup algorithm + orthogonality + invariance check + per-attempt cost-attribution) preserved verbatim from v2.2 — F2-04 revert does NOT regress v2.2 closure substrate.

[§3.5.4 U-OD-21 + §3.5.5 U-OD-22 preserved verbatim from v2.2.]

### §3.6 + §3.7

[Preserved verbatim from v2.2.]

### §3.8 (U-OD-34)

[Preserved verbatim from v2.2; v2.1 hybrid-fidelity acceptance #7 preserved intact.]

---

## §4 Dependency graph

[Preserved verbatim from v2.2. No graph changes at v2.3. U-OD-20 `Depends on: [U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)]` preserved structurally; F3-02 acknowledged-deferred annotation at U-OD-20 acceptance #11 (informational; future IS-axis revision-pass resolves placeholder). Aggregate DAG node count + edge count + topological sort + acyclic invariant all unchanged from v2.2.]

---

## §5 Spec-traceability

[Preserved verbatim from v2.2 in structure. v2.3 cell expansion at U-OD-20 per §0.4 above: C-OD-14 §14.5.1 cell expanded to cover hash-chain integrity composition formula at lines 165–178; C-OD-14 §14.5.2 cell prose-aligned to 8-row enumeration; cross-axis cells to C-IS-05 + C-IS-06 declared as informational composition surface. Cluster-to-contract mapping unchanged.]

---

## §6 Persona linkage + §7 Cross-axis citation + §8 PRD-trace + §9 Forward-flagged + §10 ADR-trace + §11 Anti-pattern audit + §12 Coherence-pass summary

[Preserved verbatim from v2.2.]

---

## §[carry-forwards]

[Preserved verbatim from v2.2: [CF-1] F2-12 ✅ CLOSED at v2.2 with closure-summary content; no v2.3 reopening. F2-12 cascade Step 6b closure record at OD plan layer intact.]

---

*End of Implementation Plan — Operational Discipline v2.3. Filed at P6-CK Iter 4 revision-cycle Segment 2 close. Absorbs F1-01 + F2-04 + F3-01 + F3-02 acknowledged-deferred per `Adversarial_Review_6_iter4.md` Disposition. Next segment (Segment 3): governance-substrate propagation revisions (Entry Handoff §5 row 4 + Session Prompt §3.1 row 4 citation correction §1.5 → §14.5.1) + revision-cycle close handoff `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` filing + cascade-substrate-clearance disposition.*
