---
artifact: design-substrate/Implementation_Plan_Memory_Substrate_v1.md
version: v1.1
cleared_at: 2026-07-28T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-1-fork-ratification (B-86 spec leg; plan delta paired with Spec_Memory_Substrate_v1 v1.1)
back_reference:
  - .harness/class_1_fork_b86_memory_scope_provider_family_keying.md (RATIFIED Class 1 fork, filed 2026-07-28 — §5 Q1 + Q2, §6 drafting targets, §7 forward items B-89 + B-90)
  - .harness/clearance/spec-memory-substrate-v1-1-cleared-2026-07-28.md (the paired spec-leg marker)
merge_commit: pending (pre-merge at filing time; B-86 spec-leg apply PR)
reviewer_chain:
  - Opus grounding agent (2026-07-28) — direct code + spec read with file:line evidence
  - advisor() transcript-aware pass (2026-07-28) — GO plus 4 framing adjustments
  - genuinely-convened council (2026-07-28) — C10 + C3 co-primary, C6 consultant; Q1 tension probe-resolved, Q2 carried C3's tools/capture cut as a condition of concurrence
  - spec-writer apply pass (2026-07-28) — plan delta authored alongside the spec delta in the same PR
---

# Clearance — Implementation_Plan_Memory_Substrate_v1 v1.1 (B-86 spec leg, plan delta)

v1 → v1.1 adds ONE new atomic unit, **U-MEM-26 — Enforce run-level memory scope keying and cross-family tool withholding**, decomposing the impl leg of `Spec_Memory_Substrate_v1.md` v1.1. The unit carries the C-MEM-13 cross-family withholding guard at the standard-memory-tools context resolution (withhold the tool schemas and the scope reference, proceed without model-facing memory access, record a named denial reason, leave harness-authored capture untouched) and the `B-89` writer-side repair (the capture path consumes the run's composed record scope instead of constructing its own `MemoryScope`), which incidentally closes `B-90`'s `tenant` / `workload_class` omission. Contracts C-MEM-03, C-MEM-13, C-MEM-14; requirements R-MEM-09, R-MEM-12; axis runtime plus control plane; depends on U-MEM-07, U-MEM-14, U-MEM-16.

Witnesses required by the unit: a cross-family servable dispatch landing withheld-and-reported with the dispatch still completing; a same-family control proving exposure is unchanged; a capture-unaffected assertion on the withheld dispatch; a capture-scope assertion that written records carry the composed scope's `provider_family`, `tenant`, and `workload_class`; and a round-trip proving a newly captured record is retrievable by a family-scoped request of its own family. The forward-only migration residual (pre-repair records written with a non-value identifier remain unretrievable and are not rewritten) is stated as an acceptance criterion rather than left implicit.

Back-reference reconciliation inside the plan: §3 axis placement, §4 dependency edges (three new), §4.1 coverage map (R-MEM-01 range plus R-MEM-09 and R-MEM-12 membership), §7 grouping (new G6 review boundary), and §9 completion range. Every U-MEM-01..25 unit body, §1, §2, §6, and §8 are preserved verbatim.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- This is a spec-leg-only filing: no `harness-*/src` or `harness-*/tests` file is touched by the PR that lands it. U-MEM-26 is the not-yet-opened impl arc.
- Two items are explicitly out of U-MEM-26's scope and recorded as such in the unit body: C6's within-family local-terminal limit, and the C-MEM-10 promotion-eligibility question for records captured during a cross-family fallback leg.
- See `.harness/clearance/README.md` for marker discipline.
