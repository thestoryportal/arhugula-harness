# Class 1 (halt-execution) — U-CP-74 EntryPayload field-set + response_hash semantic drift

**Filed:** 2026-05-29 (Phase 7 sub-phase 7b — U-CP-74 pre-substantive halt)
**Parent fork:** `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (Phase 6 design arc landing 2026-05-28 — this is a nested fork surfaced at first 7b consumption attempt against the landed design substrate)
**Status:** APPLIED-IN-FULL 2026-05-29 (β.i + Q-β.i-1(a) + Q-β.i-3(b) — CP spec v1.26 commit `ec4a2f7` + CP plan v2.29 commit `4cc730b`; see closure-back-reference at file foot)
**Halt point:** U-CP-74 (foundational unit of cluster {U-CP-74..79}); cluster traversal halted; ZERO production code written; ZERO test authored; worktree `worktree-u-cp-74-state-ledger-canonicalization` at clean tree on commit `e6c2f2c`.

---

## Defect locus

| Surface | CP spec v1.25 §16.5.3 + §16.5.5 declaration | Actual IS HEAD at `e6c2f2c` |
|---|---|---|
| `EntryPayload` field set | `(action_id, idempotency_key, actor, response_hash)` — 4 fields, composer supplies `response_hash`, IS computes `timestamp` + `prior_event_hash` (per Q4 ratification) | `(action_id, idempotency_key, actor, timestamp)` at `harness-is/src/harness_is/state_ledger_write.py:62` — composer supplies `timestamp`, IS computes `response_hash` + `prior_event_hash` |
| `response_hash` semantic | SHA-256 over composer-specific OUTCOME canonical bytes per §16.5.5 (post-override step-config / `WorkloadBindingSelectionResult` / etc.) — records what HAPPENED at the composer site | SHA-256 over `canonicalize(entry)` — i.e., over the entry's own 5-field canonical form (action_id, idempotency_key, actor, timestamp, prior_event_hash) per `harness-is/src/harness_is/entry_hash.py:73` + C-IS-06 §6.2 |
| Composer-side responsibility | Compute outcome canonical bytes → SHA-256 → emit as `response_hash` field on EntryPayload | Compute clock-read `timestamp` → emit as `timestamp` field on EntryPayload |

Both drifts compound. The "outcome bytes" semantic at §16.5.5 has nowhere to land — there is no field on the actual IS HEAD `EntryPayload` that would carry it, and IS recomputes `response_hash` from the entry's canonical form independent of any composer-supplied value.

## Distinct from Gap C drift

Spec §16.5.8 already acknowledges a Gap C drift at runtime spec §12.3 callable signature:

> Gap C drift at runtime spec §12.3 (`Callable[[StateLedgerEntry], EntryHash]` vs IS HEAD `Callable[[EntryPayload], WriteResult]`) remains Class 3 informational per `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` §"Gap class C". Per Q4 ratification, the §16.5 composer contract authored here matches the IS HEAD callable shape (`EntryPayload` → `WriteResult`); runtime spec amendment to align §12.3 prose is deferred to next runtime-spec revision pass.

That is the type-shape + sync/async drift. The drift filed here is **distinct**: the spec's enumeration of `EntryPayload`'s 4 fields names `response_hash` where IS HEAD has `timestamp`, AND the spec's semantic for `response_hash` does not match the IS HEAD semantic for the field of that name. Both drifts coexist; closure of Gap C does not close this one.

## Skill §6 halt-condition triggers

Per `phase-7-implementation` SKILL.md §6:

| Halt trigger | Class | Triggered by this defect |
|---|---|---|
| Cited spec contract section under-specifies the surface | 1 | ✓ §16.5.3 misdeclares IS HEAD field set |
| Plan signature cannot be materialized at target stack | 1 | ✓ CP plan v2.28 §2 U-CP-74 AC #3 + #8 mandate response_hash computation over post-override step-config canonical bytes; no `EntryPayload` field can carry that value on actual IS HEAD |

Both conditions trigger → Class 1 halt + back-flow routing per `phase-7-back-flow-routing` SKILL.md §3.1.

## Meta-finding — impl-time-grounding-pass gap

The Phase 6 design arc at parent fork §"Phase 6 design arc landing (2026-05-28)" notes:

> Impl-time grounding pass catalogued as workspace pattern candidate `[[impl-time-grounding-pass-pre-merge-revision]]`. When design-substrate authoring depends on assumed function names / module shapes, run a grep sweep against the target modules BEFORE committing to the design-substrate enumeration.

The PR #37 grounding pass caught **2 architectural reclassifications + 3 function-name mismatches**. It did NOT catch the EntryPayload field-set drift because grounding inspected module/symbol existence, not type-definition field-sets of consumed types. This is the same workspace pattern with a sharpened failure mode: future grounding passes against externally-consumed type definitions should include field-set diff against the actual type, not just existence check on the type's module path.

Cataloguing this as a sharpening of `[[impl-time-grounding-pass-pre-merge-revision]]`: **grounding must verify type field-sets when the design substrate enumerates per-field semantics for an externally-defined type.**

## Three resolution shapes for design phase

### (α) Extend IS HEAD `EntryPayload` to carry `response_hash` with outcome-bytes semantic

| Aspect | Detail |
|---|---|
| Mechanism | Add `response_hash: Bytes32` field to `EntryPayload`; remove IS-internal `compute_response_hash` auto-compute; composer supplies outcome-bytes hash directly |
| IS-axis cascade | `EntryPayload` field-set change at `state_ledger_write.py:62`; `compute_response_hash` semantic change at `entry_hash.py:73`; potentially every workload-class extension record that subclasses `StateLedgerEntry`; IS plan v2.3 → v2.4 revision; possibly C-IS-05 §5 + C-IS-06 §6.2 spec revision; U-IS-07 + U-IS-08 unit revisions |
| CP-axis impact | Matches spec v1.25 §16.5.3 verbatim; CP plan v2.28 unchanged; U-CP-74..79 implementable as authored |
| Pros | No CP-axis re-revision; outcome-bytes semantic preserved as designed |
| Cons | Largest cascade footprint; IS HEAD field-set is load-bearing for U-IS-11 idempotency dedup discipline + JSONL persistence format at C-IS-07 §7.3 — changes ripple to every consumer; existing U-CP-34 LANDED edge at `2e417e0` may need re-revision |

### (β) Hold IS HEAD verbatim; rewrite spec §16.5.3 + §16.5.5 to map composer outputs to actual 4 fields

| Aspect | Detail |
|---|---|
| Mechanism | CP spec v1.25 → v1.26: rewrite §16.5.3 EntryPayload declaration to `(action_id, idempotency_key, actor, timestamp)` matching IS HEAD; relocate outcome-bytes semantic — three options for "what HAPPENED" preservation: (β.i) fold outcome-hash into `idempotency_key` derivation suffix (idempotency_key bytes become `\|\| sha256(outcome_canonical_bytes)` per-composer); (β.ii) extend `action_id` discriminator with outcome-hash suffix; (β.iii) drop outcome-bytes semantic entirely (composer records only the IS-canonical-form hash via IS-internal `compute_response_hash`) |
| IS-axis cascade | ZERO |
| CP-axis cascade | CP spec v1.25 → v1.26 (§16.5.3 field-set correction + §16.5.5 semantic relocation); CP plan v2.28 → v2.29 (U-CP-74..79 ACs + signatures re-author against corrected EntryPayload); CXA v2.16 unchanged |
| Pros | Lowest cascade footprint; preserves architectural commitment to (S) sibling-variant landed at parent fork; matches IS HEAD as-is; no risk of breaking U-CP-34 LANDED edge |
| Cons | Loses spec's stated "what HAPPENED" semantic at the EntryPayload surface unless folded into `idempotency_key` (β.i) or `action_id` (β.ii); β.iii drops it entirely |

### (γ) Sibling typed wrapper `CPStateLedgerEntryPayload` at CP-side + runtime-wiring translation stage

| Aspect | Detail |
|---|---|
| Mechanism | NEW CP-side type `CPStateLedgerEntryPayload(action_id, idempotency_key, actor, outcome_hash, timestamp)` carrying outcome-bytes hash explicitly; runtime-wiring stage translates `CPStateLedgerEntryPayload → EntryPayload` for IS append + persists `outcome_hash` side-band (e.g., separate CP-side outcome-hash ledger at `state.cp_outcomes.jsonl`) |
| IS-axis cascade | ZERO at HEAD; potentially adds NEW side-band ledger primitive (out-of-scope for this fork) |
| CP-axis cascade | CP spec v1.25 → v1.26 (§16.5.3 rewrites to declare `CPStateLedgerEntryPayload` wrapper + IS-side `EntryPayload` mapping); CP plan v2.28 → v2.29 (U-CP-74..79 signatures re-author against wrapper); new runtime-spec wiring stage at `Spec_Harness_Runtime_v1.md` §14.X for wrapper-to-EntryPayload translation + outcome-hash side-band persistence |
| Pros | Mirrors (S) sibling-variant precedent from parent fork — explicit typed CP-side surface preserves outcome-bytes semantic without IS-axis cascade |
| Cons | Two-typed-ledger architecture grows to three-typed (CPAuditLedgerEntry + EntryPayload + CPStateLedgerEntryPayload + side-band outcome-hash ledger); cascade footprint between α and β; introduces new side-band ledger primitive (operational complexity); spec authoring effort larger than β |

## Recommendation: **(β.i) — Hold IS HEAD, fold outcome-bytes hash into idempotency_key derivation**

### Decisive structural argument

The parent fork resolved at (S) sibling-variant on the structural argument that **hash-bytes-immutability at signed-payload surfaces** is the workspace's decisive constraint (per CP spec v1.7 §13.5.1 NOTE 3 + the CP→OD seam precedent). The same constraint applies to IS HEAD: `EntryPayload` shape is load-bearing for IS-anchored hash-chain invariants at U-IS-08/09/10 + JSONL persistence format at C-IS-07 §7.3 + cross-axis composition at every dependent axis. Changing IS HEAD field-set or `compute_response_hash` semantic ripples to every consumer downstream — same constraint that foreclosed (W) at parent fork.

(α) violates the same structural commitment that (W) violated.
(γ) is architecturally consistent with (S) at parent fork but introduces a new side-band ledger primitive — operational complexity grows.
(β) is the structural mirror of (S): hold the downstream-axis HEAD verbatim, adapt the CP-side composer surface.

### Sub-variant choice (β.i)

| β sub-variant | Trade-off |
|---|---|
| β.i — fold outcome-hash into `idempotency_key` derivation | Outcome-bytes semantic PRESERVED at `idempotency_key` discriminator. Per §16.5.4, idempotency_key already canonicalizes per-composer disambiguation bytes; appending outcome-canonical-bytes hash to the discriminator preserves the "what HAPPENED" record at the dedup key. Idempotency semantic preserved: same composer site + same inputs + same outcome → same key. Different outcomes at same inputs (rare but possible at non-deterministic composers) → different keys → both records persist (which is correct for state-ledger replay) |
| β.ii — extend `action_id` discriminator with outcome-hash suffix | Outcome-bytes semantic partially preserved at `action_id`. Pollutes the kebab-case canonical `action_id` enum at §16.5.3 — `action_id` becomes per-outcome-hash variable rather than per-surface-kind constant. Forecloses `action_id`-based filtering downstream |
| β.iii — drop outcome-bytes semantic | Outcome-bytes semantic LOST. Composers record only what was attempted (idempotency_key inputs), not what happened (outcome). Reduces state-ledger expressiveness; Q5(a) ratification (hash-over-outcome-bytes) at parent architect rec is silently absorbed |

β.i preserves Q5(a) ratification verbatim; β.ii pollutes action_id taxonomy; β.iii absorbs the Q5(a) decision silently.

### Sub-questions for β.i ratification

If operator chooses β.i, design phase must resolve:

**Q-β.i-1: idempotency_key derivation suffix shape.** Two readings:
- (a) Append outcome-hash to existing per-composer disambiguator bytes: `workflow_id \|\| step_id \|\| override_id \|\| policy_id \|\| sha256(outcome_canonical_bytes).hex()` — preserves existing §16.5.4 row 1 formula verbatim with single-segment suffix.
- (b) Replace per-composer disambiguator final segment with outcome-hash: `workflow_id \|\| step_id \|\| sha256(outcome_canonical_bytes).hex()` — collapses disambiguator+outcome into single hash segment.

Recommendation: **(a)**. Preserves §16.5.4 formula chain verbatim; adds one segment per row; idempotency-key bytes grow by 65 bytes (1 record-separator + 64 hex chars); SHA-256 hash output unchanged.

**Q-β.i-2: outcome-canonical-bytes scheme at composer site.** The shared `_canonicalize_outcome_bytes` helper at U-CP-74 module `state_ledger_canonicalization.py` still has a role under β.i — it produces the canonical bytes the per-composer idempotency_key suffix consumes. Helper signature unchanged from CP plan v2.28 §2 U-CP-74 declaration.

**Q-β.i-3: response_hash semantic at §16.5.5 after relocation.** Two readings:
- (a) Drop §16.5.5 table entirely; document at NEW §16.5.5 that response_hash is IS-internal per C-IS-06 §6.2 (composer does not control it).
- (b) Reframe §16.5.5 as documentation of the outcome-bytes scheme consumed by idempotency_key derivation per Q-β.i-1.

Recommendation: **(b)**. Preserves the table's per-composer outcome-bytes-recipe content; reframes the destination from `response_hash` field to `idempotency_key` discriminator.

## Routing per skill §3.1

| Defect locus | Routing channel |
|---|---|
| CP spec v1.25 §16.5.3 + §16.5.5 (field-set misdeclaration + semantic misroute) | **Phase 5 spec revision-pass** at design-phase workspace |
| CP plan v2.28 §2 U-CP-74..79 ACs + signatures (downstream of spec) | **Phase 6 plan revision-pass** at design-phase workspace (cascade from spec revision) |

Resolution sequence:
1. Operator ratifies (α / β / γ) at this fork doc via AskUserQuestion
2. If β: operator ratifies (β.i / β.ii / β.iii) sub-variant
3. If β.i: operator ratifies (Q-β.i-1) (a/b), (Q-β.i-3) (a/b) sub-questions
4. Design phase opens at relevant workspace (in-CLI per parent fork precedent)
5. CP spec v1.25 → v1.26 amendment (β.i case)
6. CP plan v2.28 → v2.29 cascade
7. CXA v2.16 unchanged (β.i case)
8. Phase 7 sub-phase 7b resumes at this worktree against re-issued substrate
9. Closure-back-reference posted at this fork doc + parent fork doc per workspace convention

## Halt state at filing

| State element | Value |
|---|---|
| Halt point | U-CP-74 pre-substantive (Step 3 of phase-7-implementation per-unit shape — read deps; advisor confirmed mismatch BEFORE Step 5 implementation) |
| Halt timestamp | 2026-05-29 (post PR #37 merge `e6c2f2c` by ~30 minutes) |
| Cluster status | {U-CP-74, U-CP-75, U-CP-76, U-CP-77, U-CP-78, U-CP-79} all PENDING — none consumed |
| Production code | ZERO (no `.py` files authored or modified) |
| Test code | ZERO (no `tests/` files authored or modified) |
| Spec amendment | ZERO (this is a fork doc filing, not a spec change) |
| Worktree branch | `worktree-u-cp-74-state-ledger-canonicalization` at `e6c2f2c` + this fork doc commit |
| Advisor applications this filing | 2 (verification of reading + resolution-shape pre-substantive sanity check) |

## See also

- `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (parent fork — Phase 6 design arc landed PR #37 2026-05-28)
- `architect_recommendation_u_rt_35_gap_b_within_path_a.md` (parent fork sibling-variant resolution — (S) ratified)
- `[[impl-time-grounding-pass-pre-merge-revision]]` (workspace pattern; this filing sharpens to require type-field-set diff)
- `[[spec-prose-plan-body-drift-pattern]]` (sibling drift pattern at runtime spec §12.3)
- `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 (no silent design extension — the rule this filing honors)
- `Spec_Information_Substrate_v1.md` C-IS-05 §5 + C-IS-06 §6.2 (IS HEAD authority for EntryPayload + response_hash semantic)
- `Spec_Control_Plane_v1_25.md` §16.5.3 + §16.5.5 + §16.5.8 (defect locus)
- `Implementation_Plan_Control_Plane_v2_28.md` §2 U-CP-74 (cited atomic unit at halt point)

---

*This is a Class 1 halt-execution fork. Phase 7 sub-phase 7b cluster traversal HALTED at U-CP-74 pending operator ratification of resolution shape + design-phase artifact re-issue per `phase-7-back-flow-routing` SKILL.md §4.5.*

---

## β.i resolution applied (2026-05-29)

Closure-back-reference per workspace fork-doc convention. The β.i resolution + Q-β.i-1(a) + Q-β.i-3(b) operator-ratified at AskUserQuestion 2026-05-29 absorbed across 2 design-substrate artifacts within a single in-CLI design arc on branch `worktree-u-cp-74-state-ledger-canonicalization`:

| Layer | Artifact | Commit | Status |
|---|---|---|---|
| CP spec v1.25 → v1.26 surgical amendment at §16.5.3 + §16.5.4 + §16.5.5 chapeau + §16.5.8 + §16.5.9 invariant 2 + change-note | `design-substrate/Spec_Control_Plane_v1_26.md` | `ec4a2f7` | **FILED** 2026-05-29 |
| CP plan v2.28 → v2.29 surgical cascade at §2 U-CP-74..79 AC #2 + AC #3/#4 + Implements citation + Tests-list | `design-substrate/Implementation_Plan_Control_Plane_v2_29.md` | `4cc730b` | **FILED** 2026-05-29 |
| Workspace `CLAUDE.md` row 79 (CP spec) + row 90 (CP plan) bumps | `CLAUDE.md` | `ec4a2f7` + `4cc730b` | **FILED** 2026-05-29 |
| CXA v2.16 | (UNCHANGED — no cross-axis cascade per β.i ZERO-IS-axis-cascade structural argument) | n/a | n/a |
| IS spec / IS plan / OD spec / OD plan / AS spec / AS plan / runtime spec / runtime plan | (UNCHANGED — no cross-axis cascade) | n/a | n/a |

**Status: APPLIED-IN-FULL.** Halt-execution discharged. Cluster {U-CP-74..79} unblocks at re-issued substrate per `phase-7-back-flow-routing` SKILL.md §4.7 resume condition: re-issued artifacts preserve halted progress (unit atomization unchanged; signatures preserve outer surface; AC #2 + AC #3/#4 cascade absorbed at composer-internal logic; helper acceptance at U-CP-74 AC #8 unchanged).

Cluster resumption owed at this worktree against `Spec_Control_Plane_v1_26.md` + `Implementation_Plan_Control_Plane_v2_29.md` substrate.
