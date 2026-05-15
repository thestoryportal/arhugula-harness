# Implementation Plan — Control Plane v2.3

**Status:** Proposed

**Date:** 2026-05-14

**Revision:** v2.3 — P6-CK Iter 4 revision-cycle revision pass per `P6-CK_Iter4_Revision_Cycle_Entry_Handoff.md`; absorbs F2-01 + F2-02 + F2-03 from `Adversarial_Review_6_iter4.md`

**Revision date:** 2026-05-14

**Source set:** CP spec v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2 + ADD v1.3 + PRD v1.1 (substrate versions unchanged from v2.2; absorption deepened at U-CP-07 + U-CP-12)

**Authority chain:** `Project_Workflow_v1_7.md` §3.1 + §7 fidelity-grammar discipline; `implementation-planner` SKILL.md §8 revision-pass sub-mode

**Entry authorization:** P6-CK Iter 4 revision-cycle entry per `Adversarial_Review_6_iter4.md` Disposition Path A + OD-RevCycle-{1,2,3} confirmed at session-close menu (LLM-assisted revision; single combined session; governance-substrate propagation in same session); F3-02 disposition confirmed at revision-cycle session open: **defer to future IS-axis revision-pass** (default).

---

## §0 Change-note (v2.2 → v2.3)

### §0.1 Scope

Revision-cycle within Iter 4 scope per Workflow v1.7 → v1.8 §4.1.4.6.3 (proposed; non-blocking per Iter 4 entry-gate precedent). Absorbs three Class 2 findings from `Adversarial_Review_6_iter4.md` Disposition table:

- **F2-01** — U-CP-07 `retry.*` namespace at 4 attributes does not absorb CP spec v1.3 §3.5 6-attribute child-span schema amendment per ADR-D6 v1.2 §1.2.2.1, nor the new parent-span `retry.attempt` event 3-field schema per ADR-D6 v1.2 §1.2.2.2.
- **F2-02** — U-CP-12 acceptance #3 citation drift `§9.2 → §9.1` (canonical 4-attribute `engine.*` namespace declaration site at v1.3) + required-attribute composition gap (`engine.replay_disposition` not enumerated at U-CP-12 where U-CP-20 v2.2 acceptance #2 enumerates it; cross-unit agreement invariant violated at v2.2).
- **F2-03** — U-CP-12 `SAMPLING_DISPOSITIONS` does not absorb CP spec v1.3 §5.4 retry surface amendments: retry.attempt parent event sampling rules (base-rate at 1st attempt; always-sampled at 2nd onward; always-sampled at retry-budget-exit boundary per ADR-D6 v1.2 §1.2.2.4) + retry-attempt child span sampling row (base-rate at cell tunable per D6 §1.3; tail-keep on `retry.fail_class`) + dual-emission discipline per spec §3.5 + D6 §1.2.2.3.

**Pattern P2 self-audit scope-statement extension (v2.3 amendment per F1-01 analogous-discipline propagation).** The Pattern P2 verification at v2.3 covers ALL `per CP spec v1.3 §X.Y` citations and ALL `per ADR-D{N} v1.{N} §X.Y` citations across the entire plan body — not only F2-12-cascade-scoped citations. This extension mirrors the OD plan v2.3 §0.1 scope-statement extension authored in Segment 2 of this revision-cycle session (per F1-01 absorption discipline) and forecloses analogous scoping defects at future revision passes on the CP-plan side.

### §0.2 Sections preserved verbatim (from v2.2)

| Section | Preservation rationale |
|---|---|
| §1.1 Contract inventory; §1.2 Cluster decomposition realized; §1.3 Substrate-version citation alignment | Substrate versions unchanged at v2.3; cluster decomposition unchanged |
| §1.4 F2-12 carry-forward declaration (✅ CLOSED at v2.2) | No regression; preserved as v2.2 closure record |
| §2.1 Cluster 1 — U-CP-01 through U-CP-06 + U-CP-08 + U-CP-09 | No revision-cycle finding |
| §2.2 Cluster 2 — U-CP-10, U-CP-11, U-CP-13 | No revision-cycle finding |
| §2.3 Cluster 3 (D1 engine + replay; U-CP-14 through U-CP-21) | No revision-cycle finding; v2.2 amendments at U-CP-20 acceptance #5 + U-CP-21 4-attribute schema preserved intact |
| §2.4 Cluster 4 through §2.9 Cluster 9 (U-CP-22 through U-CP-55) | No revision-cycle finding; v2.2 amendments at U-CP-55 §24.4 closure path preserved intact |
| §3 dependency graph (Levels 0–8; edge enumeration; cycle audit) | No graph delta at v2.3 |
| §4 coverage matrix | Cell expansion at U-CP-07 + U-CP-12 per §0.4 below; cluster-to-contract mapping unchanged |
| §[carry-forwards] | Inherited from v2.2 unchanged ([CF-1] F2-12 ✅ CLOSED) |

### §0.3 Sections revised (v2.2 → v2.3)

| Section | Revision shape | Resolves |
|---|---|---|
| U-CP-07 `Implements:` | Scope extension note (still C-CP-03 §3.5; v2.3 absorbs retry.* extension + parent-event schema + dual-emission per ADR-D6 v1.2 §1.2.2) | F2-01 |
| U-CP-07 Note on substrate authority | Extended to declare retry.* substrate authority (C9 SKILL + C5 SKILL + ADR-D1 v1.2 §1.1.1 for `engine.replay_disposition`) | F2-01 |
| U-CP-07 Signatures (`RETRY_NAMESPACE_SCHEMA` cardinality) | 4 → 6 entries; `RetryAttributeSchema` record extended with `source_authority` field | F2-01 |
| U-CP-07 Signatures (new `RetryAttemptEventField` record + `RETRY_ATTEMPT_EVENT_SCHEMA` constant) | New 3-entry constant per CP spec v1.3 §3.5 + ADR-D6 v1.2 §1.2.2.2 | F2-01 |
| U-CP-07 acceptance #3 | 4-attribute enumeration replaced by 6-attribute enumeration with full type + source authority | F2-01 |
| U-CP-07 acceptance #5 | Annotation that v2.3 ingestion inherits extended 6-attribute namespace + 3-field event schema | F2-01 |
| U-CP-07 acceptance #6 (new) | Parent-span `retry.attempt` event 3-field schema enumeration verbatim per ADR-D6 v1.2 §1.2.2.2 | F2-01 |
| U-CP-07 acceptance #7 (new) | Dual-emission discipline + child-per-attempt topology + `retry.original_span_id` self-reference at attempt 1 + F2 state-ledger join contract | F2-01 |
| U-CP-07 acceptance note (new, post-#7) | `RetryCause` 5-value internal enum (acceptance #4) vs `retry.cause_attribution` C5 open-set span attribute (acceptance #3) orthogonality declared | F2-01 |
| U-CP-07 tests | Extended: cardinality-six (replaces cardinality-four); attribute verbatim; event schema cardinality-three; event field verbatim; optional `parent.next_delay_ms` at budget-exit; dual-emission required; child-per-attempt topology; `retry.original_span_id` self-reference at attempt 1; `engine.replay_disposition` inheritance from parent | F2-01 |
| U-CP-07 rollback boundary | Extended: dual-surface dissolution + downstream U-CP-12 retry surface sampling absorption regression | F2-01 |
| U-CP-12 `Implements:` | Cross-cite C-CP-09 §9.1 added for `workflow.resumption` required-attribute composition (v2.3 amendment per F2-02) | F2-02 |
| U-CP-12 Inputs | Annotated v2.3 — retry.* now 6-attribute child span schema + 3-field parent event schema | F2-03 |
| U-CP-12 Files affected | Extended with retry surface sampling table (logical: `retry-surface-sampling-table`) | F2-03 |
| U-CP-12 Signatures (new `RetrySurfaceKind` enum + `SamplingOverrideRule` record + `RetrySurfaceSamplingDisposition` record + `RETRY_SURFACE_SAMPLING_DISPOSITIONS` constant) | New types absorbing retry surface sampling discipline per CP spec v1.3 §5.4 + ADR-D6 v1.2 §1.2.2.4 | F2-03 |
| U-CP-12 acceptance #3 | Citation `§9.2 → §9.1`; required-attribute enumeration: `engine.class` + `engine.replay_disposition`; cross-unit agreement invariant with U-CP-20 acceptance #2 (v2.2) | F2-02 |
| U-CP-12 acceptance #4 | Scope clarification note (v2.3) — 8-entry `SAMPLING_DISPOSITIONS` covers LifecycleEventClass surface only; retry surface declared at new acceptance #6 + #7 + #8 + #9 | F2-03 |
| U-CP-12 acceptance #6 (new) | `RETRY_SURFACE_SAMPLING_DISPOSITIONS` declares exactly 2 entries: retry.attempt parent event + retry-attempt child span | F2-03 |
| U-CP-12 acceptance #7 (new) | retry.attempt parent event sampling rules (ordered overrides: attempt_number ≥ 2 → always-sampled; parent.attempts_remaining == 0 → always-sampled) | F2-03 |
| U-CP-12 acceptance #8 (new) | retry-attempt child span sampling (base-rate per cell tunable; tail-keep on `retry.fail_class`) | F2-03 |
| U-CP-12 acceptance #9 (new) | Dual-emission discipline — per-path independent sampling decisions, both emission attempts per retry | F2-03 |
| U-CP-12 tests | Extended with engine.replay_disposition required-attribute, cross-unit-agreement invariant, retry-surface cardinality-two, parent-event default + override rules, budget-exit always-sampled, child-span base-rate + fail_class tail-keep, dual-emission per-path tests | F2-02 + F2-03 |
| U-CP-12 rollback boundary | Extended: retry surface sampling regression + dual-emission contract dissolution + cross-unit U-CP-20 agreement loss | F2-02 + F2-03 |

### §0.4 Coverage matrix delta

| Coverage cell | At v2.2 | At v2.3 |
|---|---|---|
| C-CP-03 §3.5 retry.* namespace (6-attribute child span + 3-field parent event + dual-emission discipline) | Not covered (forward-flagged at v2.2 §0.8 row 4) | ✅ Covered at U-CP-07 acceptance #3 + #6 + #7 |
| C-CP-05 §5.2 `workflow.resumption` required-attribute composition (including `engine.replay_disposition`) | Partial — covered at U-CP-20 acceptance #2 only; U-CP-12 acceptance #3 cited wrong section (§9.2) and elided `engine.replay_disposition` (v2.2 §0.8 row 3) | ✅ Covered at U-CP-12 acceptance #3 + U-CP-20 acceptance #2 with cross-unit agreement invariant |
| C-CP-05 §5.4 sampling discipline (retry.attempt parent event + retry-attempt child span rows + retry-budget-exit-boundary discrimination + dual-emission) | Not covered (forward-flagged at v2.2 §0.8 row 5) | ✅ Covered at U-CP-12 acceptance #6 + #7 + #8 + #9 |
| C-CP-09 §9.1 engine.* required-attribute composition at workflow.resumption (consuming surface at U-CP-12) | Covered at U-CP-20 only; U-CP-12 acceptance #3 cited §9.2 (drift) | ✅ Covered at U-CP-12 acceptance #3 (citation corrected to §9.1) + U-CP-20 acceptance #2 |

Cluster-to-contract mapping unchanged: Cluster 1 → C-CP-01 through C-CP-04; Cluster 2 → C-CP-05 + C-CP-06; Clusters 3–9 preserved per v2.2 structure.

### §0.5 Dependency graph delta

No dependency graph changes at v2.3. U-CP-07 `Depends on: (none)` preserved (foundational substrate-supplying unit). U-CP-12 `Depends on: [U-CP-07, U-CP-10, U-CP-11, U-CP-15, U-CP-19, U-CP-21, U-IS-07 (cross-axis: IS)]` preserved. Aggregate DAG node count + edge count + topological sort + acyclic invariant all unchanged from v2.2.

### §0.6 Substrate-version-citation table

No substrate-version delta from v2.2.

| Substrate | Version cited at v2.3 |
|---|---|
| ADR-D1 | v1.2 |
| ADR-D6 | v1.2 |
| ADD | v1.3 |
| PRD | v1.1 |
| CP spec | v1.3 |
| OD spec | v1.3 (cross-axis citation at U-CP-12 via U-IS-07) |
| Workflow | v1.7 (v1.8 amendment proposed at Path δ revision-log; non-blocking per Iter 4 entry-gate precedent) |

Per Workflow v1.7 §7 use-latest-version body-citation-alignment.

### §0.7 Status

`Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` requires P6-CK Iter 4 revision-cycle close clean disposition + cascade-substrate-clearance issuance per `P6-CK_Iter4_Revision_Cycle_Entry_Handoff.md` §7.2.

### §0.8 Forward-flagged concerns (v2.3 update)

| Concern | v2.3 disposition |
|---|---|
| v2.2 §0.8 row 3 (U-CP-12 acceptance #3 §9.2 citation drift + required-attribute composition gap) | ✅ CLOSED at v2.3 by F2-02 absorption |
| v2.2 §0.8 row 4 (retry.* 6-attribute namespace + parent-event 3-field schema absorption) | ✅ CLOSED at v2.3 by F2-01 absorption at U-CP-07 |
| v2.2 §0.8 row 5 (§5.4 sampling table retry dual-emission absorption) | ✅ CLOSED at v2.3 by F2-03 absorption at U-CP-12 |
| `RetryCause` 5-value internal enum at U-CP-07 acceptance #4 vs `retry.cause_attribution` open-set span attribute at acceptance #3 | Distinct surfaces documented at U-CP-07 acceptance note (v2.3 new). `RetryCause` is the U-CP-48 internal retry-decision branching enum (preserved verbatim per strict-narrow scope); `retry.cause_attribution` is the OTel span attribute from C5 cause_attribution catalog at `c5-validation-contract` SKILL.md s14 §7.5(a). Orthogonality acknowledged at v2.3; not a defect. |

### §0.9 Prior revision history (v1 → v2.2; archival)

[Preserved verbatim from v2.2 §0.9.]

### §0.10 v2.3 coherence-pass summary

| Pass | Status |
|---|---|
| §1 Spec inventory | ✅ PASS — no substrate-version delta; cluster decomposition unchanged |
| §2 Atomic-unit decomposition | ✅ PASS — U-CP-07 + U-CP-12 revised per F2-01 / F2-02 / F2-03; all other units preserved verbatim from v2.2 per strict-narrow scope discipline (U-CP-48 verbatim dependency on `RetryCause` enum preserved; cross-unit agreement with U-CP-20 acceptance #2 explicitly asserted at U-CP-12 acceptance #3) |
| §3 Dependency graph | ✅ PASS — no graph changes; acyclic invariant preserved |
| §4 Spec-traceability | ✅ PASS — U-CP-07 → C-CP-03 §3.5 (6-attribute retry.* child span + 3-field retry.attempt parent event + dual-emission); U-CP-12 → C-CP-05 §5.2 + §5.4 + C-CP-09 §9.1 (required-attribute composition at workflow.resumption + retry surface sampling discipline); every revised acceptance criterion cites verified spec/ADR section at v1.3/v1.2 substrate |
| §0.1 Pattern P2 self-audit scope-statement extension | ✅ PASS — extended scope covers ALL CP spec + ADR section citations across plan body |
| §10 Anti-pattern audit | ✅ PASS — v2.2 §0.8 rows 3 + 4 + 5 closed at v2.3 by substantive absorption; no new anti-pattern surfaced; `RetryCause`-vs-`retry.cause_attribution` orthogonality acknowledged as design-distinct surfaces, not duplication |

**Pattern P1 (cross-artifact name drift) prevention.** U-CP-07 6-attribute names verified bytewise against CP spec v1.3 §3.5 table + ADR-D6 v1.2 §1.2.2.1 table substrate. U-CP-07 3-field event field names verified bytewise against CP spec v1.3 §3.5 + ADR-D6 v1.2 §1.2.2.2 table substrate. U-CP-12 retry surface entity_id strings verified bytewise against CP spec v1.3 §5.4 table substrate. U-CP-12 cross-unit agreement on `workflow.resumption` required-attribute set verified against U-CP-20 acceptance #2 (v2.2 amendment).

**Pattern P2 (verbatim-claim-contradicted) prevention.** U-CP-07 acceptance #3 + #6 + #7 citation-fidelity verified against CP spec v1.3 §3.5 lines 76–86 + ADR-D6 v1.2 §1.2.2.1–§1.2.2.3. U-CP-12 acceptance #3 citation verified against CP spec v1.3 §9.1 (line 200) + table at lines 204–209. U-CP-12 acceptance #6 + #7 + #8 + #9 citations verified against CP spec v1.3 §5.4 (lines 114–124) + ADR-D6 v1.2 §1.2.2.4. All citations point to canonical declaration sites.

---

## §1 Spec inventory

[§1.1 Contract inventory + §1.2 Cluster decomposition + §1.3 Substrate-version citation alignment preserved verbatim from v2.2 (which preserved from v2.1 with v2.2 substrate-version bumps already applied per v2.2 §0.6).]

### §1.4 F2-12 carry-forward declaration (✅ CLOSED at v2.2; preserved at v2.3)

[Preserved verbatim from v2.2 §1.4. F2-12 closure record intact; no v2.3 reopening.]

---

## §2 Atomic-unit decomposition

### §2.1 Cluster 1 — Routing, fallback, breaker, retry (C-CP-01 through C-CP-04)

[U-CP-01 through U-CP-06 preserved verbatim from v2.2. U-CP-07 revised at v2.3 per F2-01 absorption; full revised content below. U-CP-08 + U-CP-09 preserved verbatim from v2.2.]

#### U-CP-07 — Declare `fallback.*` + `harness.breaker.*` + `retry.*` namespaces (v2.3 amendment — retry.* extended to 6-attribute child span schema + parent-span event 3-field schema + dual-emission discipline per F2-01 absorption)

**Implements (v2.3 amendment):** [C-CP-03 §3.5 (fallback.* + harness.breaker.* + retry.* namespace declarations; v2.3 absorbs retry.* extension to 6-attribute child span schema per ADR-D6 v1.2 §1.2.2.1 + parent-span `retry.attempt` event 3-field schema per ADR-D6 v1.2 §1.2.2.2 + dual-emission discipline per ADR-D6 v1.2 §1.2.2.3; consumed at U-CP-12 per-class attribute composition + retry surface sampling discipline per F2-03 absorption)]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying data-type unit).

**Files affected (v2.3 amendment):** CP-axis fallback namespace (logical: `fallback-namespace-schema`); CP-axis harness-breaker namespace (logical: `harness-breaker-namespace-schema`); CP-axis retry namespace (logical: `retry-namespace-schema`); CP-axis retry-attempt parent event schema (logical: `retry-attempt-event-schema` — v2.3 new).

**Note on substrate authority (v2.3 amendment).** Per C-CP-24 §24.1.B narrative: `harness.breaker.*` is substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure + Workflow v1.3 §2.3.3.1 clause (iii); canonical schema at OD C-OD-07 §7.1. CP plan emits the CP-side composition surface (this unit's namespace) without claiming canonical authorship. `retry.*` (v2.3 amendment per ADR-D6 v1.2 §1.2.2) is substrate-anchored across three sources: `c9-reliability-recovery` SKILL.md (per-attempt counter, jittered backoff parameters); `c5-validation-contract` SKILL.md s14 §7.5(a) cause_attribution catalog (medium-cardinality open-set ~15 values) + s14 §7.5(d) 5-class fail-class taxonomy; ADR-D1 v1.2 §1.1.1 (`engine.replay_disposition` 5-value enum composition with inheritance from parent operation). Canonical retry.* schemas at ADR-D6 v1.2 §1.2.2.1 (6-attribute child span) + §1.2.2.2 (3-field parent event).

**Signatures (v2.3 amendment):**

```
record FallbackAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const FALLBACK_NAMESPACE_SCHEMA: List<FallbackAttributeSchema>  // exactly 9 entries

record HarnessBreakerAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  source_authority: string  // "c9-reliability-recovery SKILL.md (substrate-anchored outside CP)"
}
const HARNESS_BREAKER_NAMESPACE_SCHEMA: List<HarnessBreakerAttributeSchema>  // exactly 7 entries

record RetryAttributeSchema {
  attribute_name   : string
  value_type       : AttributeValueType
  cardinality      : Cardinality
  source_authority : string  // (v2.3 amendment) — per-attribute substrate authority annotation
}
const RETRY_NAMESPACE_SCHEMA: List<RetryAttributeSchema>  // exactly 6 entries (v2.3 amendment from 4)

// v2.3 new: parent-span retry.attempt event 3-field schema per ADR-D6 v1.2 §1.2.2.2
record RetryAttemptEventField {
  field_name : string
  value_type : AttributeValueType
  optional   : bool          // true for `parent.next_delay_ms` when `parent.attempts_remaining == 0`
}
const RETRY_ATTEMPT_EVENT_SCHEMA: List<RetryAttemptEventField>  // exactly 3 entries

enum RetryCause {            // preserved verbatim from v1; distinct from retry.cause_attribution span attribute (see acceptance note)
  TRANSIENT_PROVIDER_ERROR,
  RATE_LIMIT,
  TIMEOUT,
  CAPABILITY_SHORTFALL,
  VALIDATOR_FAIL_TRANSIENT
}
```

**Acceptance criteria (v2.3 amendment):**

1. `FALLBACK_NAMESPACE_SCHEMA` declares exactly nine attributes per C-CP-03 §3.5 verbatim: `fallback.layer`, `fallback.candidate_chosen`, `fallback.candidates_skipped`, `fallback.cause`, `fallback.cross_family`, `fallback.cross_family_triggered`, `fallback.exhausted`, `fallback.depth`, `fallback.cache_state_lost`. **[Preserved verbatim from v2.2.]**
2. `HARNESS_BREAKER_NAMESPACE_SCHEMA` declares exactly seven attributes per C-CP-03 §3.5 + OD C-OD-07 §7.1 canonical schema verbatim: `harness.breaker.id`, `harness.breaker.state`, `harness.breaker.scope`, `harness.breaker.trip_count`, `harness.breaker.trip_window_seconds`, `harness.breaker.fail_count_in_window`, `harness.breaker.fail_threshold`. Each attribute carries `source_authority = "c9-reliability-recovery SKILL.md"`. **[Preserved verbatim from v2.2.]**
3. **(v2.3 amendment — 4-attribute schema replaced with 6-attribute schema per F2-01 absorption.)** `RETRY_NAMESPACE_SCHEMA` declares exactly six attributes per C-CP-03 §3.5 + ADR-D6 v1.2 §1.2.2.1 verbatim:
   - `retry.attempt_number` (integer; 1-indexed; sequential attempt counter within the parent operation — attempt 1 is the initial attempt, attempt N is the N-th retry; source: `c9-reliability-recovery` SKILL.md per council §6.2)
   - `retry.original_span_id` (string; 16-hex OTel W3C Trace Context format; recovered from F2 state-ledger entry filtered by `idempotency_key`; on attempt 1 self-references the current `span_id`, on attempts 2..N references the attempt-1 `span_id`; source: F2 state-ledger entry shape per ADR-D1 v1.2 §1.1.2.2)
   - `retry.delay_ms` (integer; jittered delay applied before this attempt per C9 full-jitter backoff; source: `c9-reliability-recovery` SKILL.md per council §6.2)
   - `retry.cause_attribution` (string; open-set enum from C5 cause_attribution catalog at `c5-validation-contract` SKILL.md s14 §7.5(a); medium cardinality bounded at ~15 values per D6 substrate)
   - `retry.fail_class` (enum: `{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}`; from C5 5-class fail-class taxonomy at `c5-validation-contract` SKILL.md s14 §7.5(d))
   - `engine.replay_disposition` (composition; bounded-5 enum per ADR-D1 v1.2 §1.1.1; inherits parent operation's value — discriminates orthogonally with `retry.attempt_number` at ADR-D6 v1.2 §1.5.1 dedup)
4. `RetryCause` declares exactly five values discriminating retry-causation; consumed at U-CP-48 cause-attribution-conditioned branching. **[Preserved verbatim from v2.2.]** See acceptance note below on `RetryCause`-vs-`retry.cause_attribution` orthogonality (v2.3 new).
5. D6 ingestion is **out-of-scope at this unit**; OD plan Session 4 ingests via U-CP-54 §24.1.B export manifest. **[Preserved from v2.2; v2.3 annotation:]** At v2.3, ingestion inherits the extended 6-attribute retry.* namespace + 3-field retry.attempt event schema per ADR-D6 v1.2 §1.2 row retry.*; OD plan U-OD-20 §14.5.4 per-attempt cost-attribution acceptance is the downstream consumer.
6. **(v2.3 new — parent-span retry.attempt event 3-field schema absorption per F2-01.)** `RETRY_ATTEMPT_EVENT_SCHEMA` declares exactly three event fields per C-CP-03 §3.5 + ADR-D6 v1.2 §1.2.2.2 verbatim:
   - `parent.attempt_count` (integer; total attempts so far for this operation: initial attempt + retries to date; reads from per-operation counter; source: `c9-reliability-recovery` SKILL.md per council §6.2)
   - `parent.attempts_remaining` (integer; `max_attempts - parent.attempt_count`; zero means retry budget exhausted)
   - `parent.next_delay_ms` (integer; **optional** — omitted when `parent.attempts_remaining == 0` per spec verbatim "omitted at retry-budget-exit boundary"; jittered delay before next attempt per C9 full-jitter backoff)
7. **(v2.3 new — dual-emission discipline + child-per-attempt topology per F2-01 + ADR-D6 v1.2 §1.2.2.3 + council §6.3.)** Per C-CP-03 §3.5 + ADR-D6 v1.2 §1.2.2.3: the retry-attempt mechanism MUST emit BOTH the parent-span `retry.attempt` event AND the new retry-attempt child span at each retry. Collapse to event-only or span-only is forbidden — event-only loses per-attempt operation-level instrumentation (cost-attribution at OD plan U-OD-20 §14.5.4 cannot accrue per-attempt cost; per-attempt diagnostic spans are missing from the trace tree); span-only loses parent-perspective retry-trigger marking (operator scanning the parent span's event timeline cannot see retry occurred at trigger time without traversing children). Topology per `c1-orchestration-control` SKILL.md authority at ADR-D6 v1.2 §1.2.2 council §6.3: retry-attempt child spans are CHILDREN of the parent operation span (linked via OTel-standard `parent_span_id`); attempts are SIBLINGS to each other under the same parent. The v1.1 §1.2 "sibling-span" terminology is corrected at v1.2 to "child-per-attempt" per the council authority — CP plan inherits the corrected terminology at v2.3 per substrate.

**Acceptance note — `RetryCause` (acceptance #4) vs `retry.cause_attribution` (acceptance #3) orthogonality (v2.3 new).** Two distinct surfaces are present at v2.3 and preserved:

- `RetryCause` enum (5 values: `TRANSIENT_PROVIDER_ERROR`, `RATE_LIMIT`, `TIMEOUT`, `CAPABILITY_SHORTFALL`, `VALIDATOR_FAIL_TRANSIENT`) is the **internal retry-decision branching enum** consumed at U-CP-48 cause-attribution-conditioned branching. It governs whether retry occurs at all and which downstream branching path is taken at retry-decision time. Closed 5-value taxonomy.
- `retry.cause_attribution` (string; open-set enum from C5 cause_attribution catalog at `c5-validation-contract` SKILL.md s14 §7.5(a); medium cardinality ~15 values) is the **OTel span attribute** emitted on the retry-attempt child span at emission time. It captures the C5-classified cause at richer cardinality than `RetryCause` for observability and post-hoc analysis.

The two surfaces are orthogonal. `RetryCause` is the discriminator for internal control flow; `retry.cause_attribution` is the externally-observable span attribute. Strict-narrow scope discipline preserves `RetryCause` verbatim at acceptance #4 to honor U-CP-48 verbatim dependency, while v2.3 acceptance #3 absorbs the broader C5 cause_attribution catalog at the OTel surface per ADR-D6 v1.2 §1.2.2.1. Not a drift; not a duplication.

**Tests (v2.3 amendment):**

- `test_fallback_namespace_cardinality_nine` [preserved from v2.2]
- `test_fallback_attributes_match_spec_verbatim` [preserved from v2.2]
- `test_harness_breaker_namespace_cardinality_seven` [preserved from v2.2]
- `test_harness_breaker_source_authority` [preserved from v2.2]
- `test_retry_namespace_cardinality_six` (v2.3; replaces deprecated `test_retry_namespace_cardinality_four`)
- `test_retry_attributes_match_spec_v1_3_verbatim` (v2.3; covers all 6 attribute names + types + source authority)
- `test_retry_cause_cardinality_five` [preserved from v2.2 — `RetryCause` internal enum at acceptance #4]
- `test_retry_attempt_event_schema_cardinality_three` (v2.3 new)
- `test_retry_attempt_event_fields_match_spec_v1_3_verbatim` (v2.3 new — covers all 3 field names + types + optional flag for `parent.next_delay_ms`)
- `test_retry_attempt_event_parent_next_delay_ms_optional_when_budget_zero` (v2.3 new — verifies optional-field-omission at `parent.attempts_remaining == 0`)
- `test_dual_emission_discipline_required` (v2.3 new — both event + span emission attempts per retry)
- `test_retry_attempt_child_topology_under_parent_operation` (v2.3 new — `parent_span_id` links child to parent operation, not to prior attempts)
- `test_retry_original_span_id_self_reference_at_attempt_1` (v2.3 new)
- `test_retry_original_span_id_attempt_1_span_id_at_attempts_2_through_n` (v2.3 new)
- `test_engine_replay_disposition_inheritance_from_parent_operation` (v2.3 new — retry-attempt span inherits parent operation's `engine.replay_disposition` value)

**Rollback boundary (v2.3 amendment):** Revert `RETRY_NAMESPACE_SCHEMA` to 4-attribute v2.2 form + revert `RetryAttemptEventField` record + revert `RETRY_ATTEMPT_EVENT_SCHEMA` constant + revert dual-emission acceptance criterion at #7. Downstream impact: U-CP-12 retry surface sampling absorption regresses (v2.2 §0.8 row 5 reopens; U-CP-12 acceptance #6 + #7 + #8 + #9 dissolve at the same revert); ADR-D6 v1.2 §1.2.2 absorption at CP plan layer dissolves; cost-attribution-per-attempt at OD plan U-OD-20 §14.5.4 acceptance loses CP-side substrate (cross-axis dependency to OD plan); F2-12 sub-scope (ii) closure substrate at CP plan layer dissolves (cascade Step 6a closure status regresses). `FALLBACK_NAMESPACE_SCHEMA` + `HARNESS_BREAKER_NAMESPACE_SCHEMA` + `RetryCause` enum unaffected by revert.

[U-CP-08 + U-CP-09 preserved verbatim from v2.2.]

### §2.2 Cluster 2 — F3 lifecycle + manifest (C-CP-05, C-CP-06)

[U-CP-10 + U-CP-11 preserved verbatim from v2.2. U-CP-12 revised at v2.3 per F2-02 + F2-03 absorption; full revised content below. U-CP-13 preserved verbatim from v2.2.]

#### U-CP-12 — Implement per-class attribute composition + per-class sampling discipline (v2.3 amendment — acceptance #3 citation correction + required-attribute enumeration per F2-02; retry surface sampling discipline absorbed per F2-03)

**Implements (v2.3 amendment):** [C-CP-05 §5.2 (per-class attribute composition including v1.3 `engine.replay_disposition` required-attribute at `workflow.resumption`), §5.4 (sampling discipline including v1.3 retry surface rows + retry-budget-exit-boundary discrimination + dual-emission); cross-cite C-CP-09 §9.1 (4-attribute `engine.*` namespace canonical declaration) for the `workflow.resumption` required-attribute composition per F2-02 absorption]

**Depends on:** [U-CP-07, U-CP-10, U-CP-11, U-CP-15, U-CP-19, U-CP-21, U-IS-07 (cross-axis: IS)]

**Inputs (v2.3 amendment):** Fallback/retry/harness-breaker namespaces (U-CP-07; retry.* now 6-attribute child span schema + 3-field parent event schema per v2.3 absorption); lifecycle event class enum (U-CP-10); lease namespace (U-CP-11); `EngineClass` enum (U-CP-15); `ResumptionKind` enum (U-CP-19); `engine.*` namespace 4-attribute schema (U-CP-21 per v2.2 amendment, including `engine.replay_disposition`); F2 state-ledger entry shape (U-IS-07 cross-axis).

**Files affected (v2.3 amendment):** CP-axis per-class attribute composition (logical: `per-class-attribute-composition`); CP-axis per-class sampling table (logical: `per-class-sampling-table`); CP-axis retry surface sampling table (logical: `retry-surface-sampling-table` — v2.3 new).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` (C-IS-10 §10.1 → U-IS-07) for `workflow.checkpoint` event attribute composition (`action_id`, `prior_event_hash` fields).

**Signatures (v2.3 amendment — additions for retry surface; existing types preserved):**

```
record PerClassAttributeSet {
  class               : LifecycleEventClass
  required_attributes : Set<string>                   // names from declared namespaces
  optional_attributes : Set<string>
}
const PER_CLASS_ATTRIBUTE_SETS: List<PerClassAttributeSet>  // exactly 8 entries (preserved verbatim from v1)

enum SamplingRate {
  ALWAYS_SAMPLED,                                     // head = 1.0
  BASE_RATE                                           // head per deployment-bound base rate
}

record SamplingDisposition {                          // preserved verbatim from v1; covers LifecycleEventClass surface
  class             : LifecycleEventClass
  head_rate         : SamplingRate
  tail_keep         : bool
}
const SAMPLING_DISPOSITIONS: List<SamplingDisposition>  // exactly 8 entries (preserved verbatim from v1)

// v2.3 new: retry surface sampling discipline per CP spec v1.3 §5.4 + ADR-D6 v1.2 §1.2.2.4
enum RetrySurfaceKind {
  PARENT_EVENT,                                       // retry.attempt event emitted on parent operation span
  CHILD_SPAN                                          // retry-attempt child span (one per attempt)
}

record SamplingOverrideRule {
  condition_predicate : string                        // human-readable per spec §5.4 (e.g., "retry.attempt_number >= 2", "parent.attempts_remaining == 0")
  override_rate       : SamplingRate                  // at v1.3, always ALWAYS_SAMPLED on match
}

record RetrySurfaceSamplingDisposition {
  entity_id                : string                   // "retry.attempt" (parent event) | "retry-attempt-child-span"
  entity_kind              : RetrySurfaceKind
  default_rate             : SamplingRate             // BASE_RATE at v1.3 for both entries
  always_sampled_overrides : List<SamplingOverrideRule>  // ordered; first match wins; parent event only at v1.3
  tail_keep_on_attribute   : Optional<string>         // "retry.fail_class" for child span; None for parent event
}
const RETRY_SURFACE_SAMPLING_DISPOSITIONS: List<RetrySurfaceSamplingDisposition>  // exactly 2 entries (v2.3 new)
```

**Acceptance criteria (v2.3 amendment):**

1. `PER_CLASS_ATTRIBUTE_SETS` declares exactly eight entries per C-CP-05 §5.2 verbatim, one per `LifecycleEventClass` value. **[Preserved verbatim from v2.2.]**
2. `workflow.checkpoint` event composes with F2 entry shape via U-IS-07 — required attributes include `action_id`, `prior_event_hash` from F2 six-field shape. **[Preserved verbatim from v2.2.]**
3. **(v2.3 amendment — citation correction §9.2 → §9.1 + required-attribute enumeration per F2-02 absorption.)** `workflow.resumption` event composes with U-CP-21 `engine.*` 4-attribute namespace per C-CP-09 **§9.1** (v2.3 citation correction from §9.2 — canonical 4-attribute namespace declaration site at CP spec v1.3 §9.1 lines 200 + 204–209 per ADR-D1 v1.2 §1.1.1; §9.2 is "Per-row Tier-3 / Tier-5 mapping" and is not the canonical declaration site at v1.3). Required attributes at `workflow.resumption`: `engine.class` (5-value enum per `EngineClass`) + `engine.replay_disposition` (5-value enum per `ReplayDisposition`; closed-mapped to `engine.class` per `REPLAY_DISPOSITION_MAPPING` at U-CP-21 v2.2 acceptance #3). The required-attribute set agrees byte-exact with U-CP-20 acceptance #2 (v2.2 amendment line 147: "required attributes include `engine.class` + `engine.replay_disposition` per U-CP-21 4-attribute `engine.*` namespace") — cross-unit consistency invariant at v2.3.
4. `SAMPLING_DISPOSITIONS` declares per C-CP-05 §5.4 verbatim for the eight `LifecycleEventClass` entries: `WORKFLOW_START`, `WORKFLOW_CHECKPOINT`, `WORKFLOW_RESUMPTION`, `WORKFLOW_FANOUT_OPEN`, `WORKFLOW_FANOUT_CLOSE`, `WORKFLOW_HITL_INVOCATION`, `WORKFLOW_FALLBACK_TRIGGERED`, `WORKFLOW_BREAKER_TRIPPED` all `ALWAYS_SAMPLED` (operator-burden and tamper-evidence relevance). **[Preserved verbatim from v2.2.]** **Scope clarification (v2.3):** the retry surface sampling discipline at CP spec v1.3 §5.4 (retry.attempt parent event + retry-attempt child span rows) lives outside the `LifecycleEventClass` taxonomy (which U-CP-10 closes at cardinality 8) and is declared at new acceptance #6 + #7 + #8 + #9 below using `RETRY_SURFACE_SAMPLING_DISPOSITIONS`.
5. Per-class attribute composition is deterministic given inputs; runtime emission validates `required_attributes` set is fully populated. **[Preserved verbatim from v2.2.]**
6. **(v2.3 new — retry surface declaration per F2-03 absorption.)** `RETRY_SURFACE_SAMPLING_DISPOSITIONS` declares exactly two entries per CP spec v1.3 §5.4 + ADR-D6 v1.2 §1.2.2.4 verbatim:
   - entry 1: `entity_id = "retry.attempt"`, `entity_kind = PARENT_EVENT`, `default_rate = BASE_RATE`, `always_sampled_overrides` per acceptance #7 below, `tail_keep_on_attribute = None`
   - entry 2: `entity_id = "retry-attempt-child-span"`, `entity_kind = CHILD_SPAN`, `default_rate = BASE_RATE`, `always_sampled_overrides = []` (empty), `tail_keep_on_attribute = "retry.fail_class"` per acceptance #8 below
7. **(v2.3 new — retry.attempt parent event sampling rules per F2-03 + CP spec v1.3 §5.4 + ADR-D6 v1.2 §1.2.2.4.)** For the `retry.attempt` parent event entry in `RETRY_SURFACE_SAMPLING_DISPOSITIONS`, `always_sampled_overrides` declares exactly two ordered rules per CP spec v1.3 §5.4 row 4 ("base-rate at 1st attempt; always-sampled at 2nd onward per C-CP-03 §3.5; ALWAYS-SAMPLED at retry-budget-exit boundary (`parent.attempts_remaining == 0`) per D6 v1.2 §1.2.2.4") + Cluster 4 §2.2.3 [HIGH] staircase-visibility substrate:
   - rule 1: `condition_predicate = "retry.attempt_number >= 2"`, `override_rate = ALWAYS_SAMPLED` (staircase visibility from 2nd attempt onward)
   - rule 2: `condition_predicate = "parent.attempts_remaining == 0"`, `override_rate = ALWAYS_SAMPLED` (retry-budget-exit boundary; tamper-evidence-relevant per D6 v1.2 §1.2.2.4)
   Override-ordering semantics: rules evaluated in declared order; first match wins. Default rate applies when no rule matches (the case of 1st attempt with retry budget remaining): `BASE_RATE`.
8. **(v2.3 new — retry-attempt child span sampling per F2-03 + CP spec v1.3 §5.4 row 5 + ADR-D6 v1.2 §1.3 + §1.2.2.4.)** For the retry-attempt child span entry in `RETRY_SURFACE_SAMPLING_DISPOSITIONS`: `default_rate = BASE_RATE` at cell tunable per ADR-D6 v1.2 §1.3 sampling discipline; `tail_keep_on_attribute = "retry.fail_class"` — when tail-sampling determines a trace was kept on classification, retry-attempt child spans whose `retry.fail_class` attribute carries a fail-class taxonomy value (per `c5-validation-contract` SKILL.md s14 §7.5(d) 5-class taxonomy) are preserved.
9. **(v2.3 new — dual-emission discipline per F2-03 + CP spec v1.3 §3.5 line 86 + ADR-D6 v1.2 §1.2.2.3.)** At each retry the runtime MUST emit BOTH paths: (a) the parent-span `retry.attempt` event subject to sampling per acceptance #6 entry 1 + #7 rules, AND (b) the retry-attempt child span subject to sampling per acceptance #6 entry 2 + #8 rules. Collapse to event-only or span-only is forbidden per ADR-D6 v1.2 §1.2.2.3 (event-only loses per-attempt operation-level instrumentation + per-attempt cost-attribution; span-only loses parent-perspective retry-trigger marking). Runtime invariant: every retry produces exactly one event-emission attempt at the parent span + exactly one child-span-emission attempt; sampling decisions apply per-path independently (a parent event may sample-out while a child span samples-in per their respective rules, or vice versa, but both emission attempts happen unconditionally per retry).

**Tests (v2.3 amendment):**

- `test_per_class_attribute_sets_cardinality_eight` [preserved from v2.2]
- `test_checkpoint_composes_with_f2_entry` [preserved from v2.2]
- `test_resumption_composes_with_engine_namespace` [preserved from v2.2 in name; v2.3 body asserts citation §9.1 + 4-attribute required set + cross-unit agreement with U-CP-20]
- `test_engine_replay_disposition_required_at_workflow_resumption` (v2.3 new — verifies `engine.replay_disposition` ∈ `required_attributes` for `WORKFLOW_RESUMPTION`)
- `test_workflow_resumption_attribute_composition_agrees_with_u_cp_20_acceptance_2` (v2.3 new — cross-unit agreement invariant per F2-02(b) resolution path)
- `test_sampling_dispositions_all_always_sampled` [preserved from v2.2 — scope: 8-entry LifecycleEventClass surface]
- `test_sampling_dispositions_lifecycle_cardinality_eight_preserved` (v2.3 new — explicitly asserts the LifecycleEventClass-surface cardinality is unchanged at v2.3)
- `test_required_attributes_enforced` [preserved from v2.2]
- `test_retry_surface_sampling_dispositions_cardinality_two` (v2.3 new)
- `test_retry_attempt_parent_event_default_base_rate_first_attempt_with_budget` (v2.3 new — verifies default BASE_RATE applies when neither override rule matches)
- `test_retry_attempt_parent_event_always_sampled_attempt_number_ge_two` (v2.3 new — staircase visibility)
- `test_retry_attempt_parent_event_always_sampled_at_budget_exit` (v2.3 new — `parent.attempts_remaining == 0` always-sampled per ADR-D6 v1.2 §1.2.2.4)
- `test_retry_attempt_parent_event_override_rules_evaluated_first_match_wins` (v2.3 new — ordered-evaluation invariant)
- `test_retry_attempt_child_span_default_base_rate_per_cell_tunable` (v2.3 new)
- `test_retry_attempt_child_span_tail_keep_on_fail_class` (v2.3 new)
- `test_dual_emission_both_paths_emit_per_retry` (v2.3 new — per-path independence invariant per acceptance #9)
- `test_dual_emission_collapse_to_event_only_forbidden` (v2.3 new)
- `test_dual_emission_collapse_to_span_only_forbidden` (v2.3 new)

**Rollback boundary (v2.3 amendment):** Revert per-class attribute composition + sampling table + retry surface sampling table. F3 lifecycle event emission loses per-class discrimination; D6 §1.2 + §1.3 ingestion loses CP-side composition. Retry surface absorption regresses — acceptance #6 + #7 + #8 + #9 dissolve at revert; CP spec v1.3 §5.4 retry rows + dual-emission discipline at §3.5 lose CP plan coverage (v2.2 §0.8 row 5 reopens). `workflow.resumption` required-attribute composition agreement with U-CP-20 acceptance #2 (v2.2 amendment) regresses to v2.2 partial-coverage state (v2.2 §0.8 row 3 reopens). Cross-axis IS edge to U-IS-07 releases.

[U-CP-13 preserved verbatim from v2.2.]

### §2.3 Cluster 3 — D1 engine + replay (C-CP-07, C-CP-08, C-CP-09)

[Preserved verbatim from v2.2: U-CP-14 through U-CP-19 (v2.2 preserved from v2.1) + U-CP-20 (v2.2 amendment to acceptance #5: F2-12 ✅ CLOSED + `engine.replay_disposition` required-attribute at acceptance #2) + U-CP-21 (v2.2 amendment to 4-attribute schema + `REPLAY_DISPOSITION_MAPPING` constant).]

### §2.4 Cluster 4 through §2.9 Cluster 9

[U-CP-22 through U-CP-55 preserved verbatim from v2.2; v2.2 amendment at U-CP-55 §24.4 closure manifest acceptance #3 + #4 preserved intact.]

---

## §3 Dependency graph

[Preserved verbatim from v2.2. No graph changes at v2.3. Aggregate DAG: U-CP-07 anchors at Level 0 (foundational; `Depends on: (none)`); U-CP-12 at Level 3 (consumer of U-CP-07, U-CP-10, U-CP-11, U-CP-15, U-CP-19, U-CP-21, U-IS-07 cross-axis). Acyclic invariant preserved; topological sort unchanged.]

---

## §4 Coverage matrix

[Preserved verbatim from v2.2 in structure. v2.3 coverage delta per §0.4 above: U-CP-07 cell expanded to cover C-CP-03 §3.5 retry.* 6-attribute namespace + retry.attempt parent event 3-field schema + dual-emission discipline; U-CP-12 cell expanded to cover C-CP-05 §5.4 retry surface sampling discipline + C-CP-09 §9.1 `engine.*` required-attribute composition at `workflow.resumption`. No cluster-to-contract mapping changes.]

---

## §[carry-forwards]

[Preserved verbatim from v2.2: [CF-1] F2-12 ✅ CLOSED at v2.2 with closure-summary content; no v2.3 reopening. F2-12 cascade Step 6a closure record at CP plan layer preserved.]

---

*End of Implementation Plan — Control Plane v2.3. Filed at P6-CK Iter 4 revision-cycle Segment 1 close. Absorbs F2-01 + F2-02 + F2-03 per `Adversarial_Review_6_iter4.md` Disposition. Next segment (Segment 2): OD plan v2.2 → v2.3 (F1-01 §0.8 row 2 + §0.1 scope-statement extension; F2-04 hash-chain composition formula absorption at U-OD-20; F3-01 acceptance #12 prose alignment; F3-02 acknowledged-deferred per session-open OD).*
