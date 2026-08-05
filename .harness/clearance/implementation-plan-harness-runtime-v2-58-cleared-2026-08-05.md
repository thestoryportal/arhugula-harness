---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_58.md
version: v2.58
cleared_at: 2026-08-05T00:00:00-06:00
clearance_type: ratified-fork-apply-pass
back_reference:
  - design-substrate/Spec_Harness_Runtime_v1.md v1.111 §14.8.11.1 (the spec surface this plan absorbs; cleared in the same PR at .harness/clearance/spec-harness-runtime-v1-111-cleared-2026-08-05.md)
  - .harness/class_2_fork_b96_gc_grace_elapsed_time_bound.md (FILED PR #1179; RATIFIED 2026-08-05 as READING C; its §9 impl-leg row is the obligation set U-RT-150 carries)
  - .harness/council-b96-grace-ceiling-2026-08-01.md (merged PR #1183; ceiling form C-2, and the §7.1 routing split that assigns the non-dot-leading record name to the IMPL leg)
  - .harness/forward-register.yaml row `B-96` (status UNCHANGED at `design_substrate_gated`)
  - PR '#1235' (this arc)
merge_commit: pending
reviewer_chain:
  - implementation-planner Phase-7 revision pass — absorbs Runtime spec v1.111 §14.8.11.1 into **ONE NEW unit (U-RT-150)** with **FIFTEEN** acceptance criteria; adds no contract beyond the spec, re-decomposes no existing unit, and makes no blanket zero-cascade claim.
  - empirical grounding pass at this leg — U-RT-145's AC #7 re-read at `Implementation_Plan_Harness_Runtime_v2_51.md` §1.1 and confirmed **still true and unchanged** under v1.111 (the reason a new unit is correct and an amendment is not); the highest existing `U-RT-*` id recomputed programmatically across the plan corpus (**149**) so `U-RT-150` is genuinely free; the `harness-inspect` admin CLI and its §13.7 pause-journal enumeration row confirmed present in code, so AC #8(b)'s *extension of an existing row* is buildable.
  - out-of-family Codex review (`just codex-review`, base `main`) — **round 1: TWO [P2], BOTH UPHELD and FOLDED.** (i) Term 2's publication bound was stated WITHOUT the fork §3(ii) qualification **(b)** — the no-backward-step wall-clock assumption the fork states verbatim as *"the lemma is stated with the assumption rather than without it"*; qualifications (a) and (c) had been carried, (b) had not. Term 2 now carries it with the fork's own scoping (not a defect this grace introduces; not owed by any leg; a monotonic clock is NOT the substitute, because the observation state is durable across process exit), and plan **AC #2** carries the matching scope so the witness cannot be read as proving an unconditional bound. (ii) The register's prose surface still asserted *"spec leg + impl leg owed"* at three sites after this leg lands; all three were amended **in place** (heading parenthetical, ratified bullet, superseded-state pointer) with the YAML `heading` mirror updated in the same commit and `forward_register.py --check` re-verified.
supersedes: implementation-plan-harness-runtime-v2-57-cleared-2026-07-31.md
---

# Clearance — `Implementation Plan Harness Runtime v2.58`

v2.58 absorbs **Runtime spec v1.111 §14.8.11.1** into **ONE NEW unit, U-RT-150**, carrying the durable, publication-bounded, elapsed-time GC reclaim grace in full: the conjunctive reclaim rule with no third path (AC #1), the publication bound witnessed against an under-reporting filesystem timestamp (AC #2), the locked post-re-verification wall-clock sampling point (AC #3), the fail-safe derived-index direction (AC #4), the closed two-member content set keyed over **both** sweep classes (AC #5), the fact-not-verdict reset emission (AC #6), the **conditional** retention statement including the negative half — that no surface may assert an unconditional `N × TTL` bound (AC #7), the two falsifiability surfaces with the three-way record-state report (AC #8), replace-not-accumulate over the union (AC #9), the **one-shot multi-invocation** witness that discriminates the ratified form from the retired Reading B (AC #10), the unreadable-record totality emitted as a fault (AC #11), the emission carrier / content / cardinality / redaction rules (AC #12), the re-grounding pass over the inverted grace-dependent witnesses (AC #13), the three new cross-process / bounded-reclaim / record-crash-atomicity witnesses (AC #14), and the disjoint, non-dot-leading record name (AC #15).

**ZERO existing units amended.** U-RT-145, U-RT-148 and U-RT-149 are **PRESERVED VERBATIM**. **ZERO new cluster; ONE new DAG edge (U-RT-145 → U-RT-150); ZERO cross-axis edge.**

Reviewed at clearance: that a **new unit** rather than an amendment of U-RT-145 is the correct shape — U-RT-145's AC #7 states v1.103's bounded-retention contract and **every clause of it remains true under v1.111**, so amending it would retroactively falsify a landed unit's closure criterion and obscure which obligations are new (the `B-97`(a) → U-RT-149 precedent, applied); that the plan **re-litigates nothing** — Readings A and B are settled, and AC #10 *witnesses* B's retirement rather than re-arguing it; and that **AC #13 is stated as a first-class obligation with a named failure mode** (*a green suite reached by weakening or deleting a witness is an acceptance FAILURE*), because the elapsed-time rule inverts assertions that are green today, including the `B-74` pin that flips to a positive live-entry-survives witness exactly as its own in-file comment instructs.

## Notes

- **Impl is NOT bundled.** Code + tests land as a separate follow-on arc, per the `B-33` / `B-39` / `B-59` / `B-69` / `B-70` / `B-72` / `B-97` / `B-107` precedent. **`B-96`, the `B-77` residual and `B-74` flip to `closed` only when U-RT-150 merges** — the register row stays `design_substrate_gated` at this leg.
- **Verification shape is a stated acceptance condition, not impl discretion.** AC #10 and AC #14(i) MUST be exercised as **real successive process invocations against one store root**, never as an in-process simulation — durability is precisely the property an in-process test cannot see, and asserting it in-process would reproduce the wired-but-unreachable failure mode this arc exists to close.
- **THE EXPANSION FLAG applies to this artifact too.** Five of the spec's twelve terms (#5, #6, #8, #11, #12) are **expansions beyond the fork's §8 ratification ask** (council record §7.2). A fresh operator decision on them would be a **Class 2** routing reaching U-RT-150's AC #5, #6, #8, #11 and #12 — and nothing else in this plan. Full statement at the companion spec marker.
- **One obligation is impl-leg by the council's own routing split and is carried here rather than in the spec:** the record's **non-dot-leading** name (AC #15), which closes the dotfile-skipping copy loss channel. The fork's soundness exit assigns carrier sub-option defects to the impl leg; condition #5's *content* restriction is a different object and is spec-leg.
- **NOT owed by this or any leg, restated so it is not re-derived:** narrowing `ttl_seconds` or adding a TTL floor; any numeric `k` or absolute reclaim ceiling; a hard periodic-sweep requirement; a fourth reordering of the publication path's two-stamp pipeline; carriers **(C-ii)** or **(C-iii)**.
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
