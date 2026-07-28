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
  - just codex-review round 1 (2026-07-28) — [P2-c] closeout staleness absorbed here: U-MEM-26 gains an acceptance criterion re-opening the U-MEM-25 closeout evidence rows for C-MEM-03 / C-MEM-13 / C-MEM-14 and a verification line re-running the closeout check; [P1-b] recording-surface precision propagated into the unit's Implement + Acceptance wording (no C-MEM-08 operation kind introduced); [P1-a] asymmetric-null witness pair added to Verification
  - just codex-review round 2 (2026-07-28) — [P1] interim-window false certification: honest-annotation half applied (U-MEM-25 evidence rows scoped to v1 with `PENDING — U-MEM-26` markers), red-gate alternative DECLINED and the decline recorded with its CI-discipline rationale in this plan's change-note
  - just codex-review rounds 3-7 (2026-07-28) — R3 R-MEM version scoping in the evidence packet + CLAUDE.md §2.4 plan pointer; R4 write-boundary criterion across every durable MemoryScope write + closeout refresh widened to all six rows; R5 removed the round-4 `null` fallback (itself a scope-isolation defect under the asymmetric stored-null wildcard) and fixed the canonicalize-vs-deny contradiction; R6 added the compaction-decision and native-adapter tool-event write surfaces (both grounded as NOT discharged-by-construction, test-only call sites at HEAD) plus the U-MEM-09 / U-MEM-22 dependencies and the operational-discipline axis; R7 B-90 register transit to `open` and this marker body refreshed against the final post-R6 unit
---

# Clearance — Implementation_Plan_Memory_Substrate_v1 v1.1 (B-86 spec leg, plan delta)

v1 → v1.1 adds ONE new atomic unit, **U-MEM-26 — Enforce run-level memory scope keying and cross-family tool withholding**, decomposing the impl leg of `Spec_Memory_Substrate_v1.md` v1.1. The unit carries the C-MEM-13 cross-family withholding guard at the standard-memory-tools context resolution (withhold the tool schemas and the scope reference, proceed without model-facing memory access, record a named denial reason, leave harness-authored capture untouched) and the `B-89` writer-side repair (the capture path consumes the run's composed record scope instead of constructing its own `MemoryScope`), which incidentally closes `B-90`'s `tenant` / `workload_class` omission. Contracts C-MEM-03, C-MEM-13, C-MEM-14; requirements R-MEM-09, R-MEM-12; **axis runtime plus control plane plus operational discipline; depends on U-MEM-07, U-MEM-09, U-MEM-14, U-MEM-16, U-MEM-22** (U-MEM-09 owns promotion-record persistence, U-MEM-22 the C-MEM-19 telemetry surface; action surface is deliberately not claimed — the unit emits existing telemetry attribute values and defines no new member).

The unit also carries a **write-boundary criterion** covering every durable `MemoryScope` write, not the capture path alone: automatic capture, the promotion-record write that persists `candidate.suggested_scope` verbatim (fed by a caller/model-supplied hint or the tool-execution context), a statically-supplied `RuntimeMemoryContext` on the non-recomposing dispatcher path, the compaction-decision write, and the native-adapter tool-event write. Registered provider keys canonicalize through the existing provider-to-family authority; unregistered or out-of-domain identifiers are denied per C-MEM-09. `null` is explicitly **not** a fail-safe at a write — under C-MEM-03's asymmetric semantics a stored `null` is the unpartitioned wildcard, so degrading an unknown key to it would widen reach, against R-MEM-12. Grounding recorded in the plan: the compaction and native-adapter surfaces are **not** discharged by construction (both have test-only call sites at HEAD, so no composition root seeds either from the composed run scope).

Witnesses required by the unit: a cross-family servable dispatch landing withheld-and-reported with the dispatch still completing; a same-family control proving exposure is unchanged; a capture-unaffected assertion on the withheld dispatch; a capture-scope assertion that written records carry the composed scope's `provider_family`, `tenant`, and `workload_class`; and a round-trip proving a newly captured record is retrievable by a family-scoped request of its own family. The forward-only migration residual (pre-repair records written with a non-value identifier remain unretrievable and are not rewritten) is stated as an acceptance criterion rather than left implicit, as is the asymmetric-`null` witness pair, a witness per write-boundary surface, and the re-opening of **all six** `PENDING — U-MEM-26` closeout evidence rows (C-MEM-03 / C-MEM-13 / C-MEM-14 **and** R-MEM-01 / R-MEM-09 / R-MEM-12) with the packet's version-scoping wording lifted and a green re-run of the closeout check — the minimal form of the closeout-staleness fix, taken in preference to reddening the gate for the interim window because the checker is id-coverage-based rather than ordering-sensitive and a red `just check` on main would block every unrelated arc.

Back-reference reconciliation inside the plan: §3 axis placement (control plane, runtime, and operational discipline rows), §4 dependency edges (five new), §4.1 coverage map (R-MEM-01 range plus R-MEM-09 and R-MEM-12 membership), §7 grouping (new G6 review boundary), and §9 completion range. Every U-MEM-01..25 unit body, §1, §2, §6, and §8 are preserved verbatim.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- This is a spec-leg-only filing: no `harness-*/src` or `harness-*/tests` file is touched by the PR that lands it. U-MEM-26 is the not-yet-opened impl arc.
- Two items are explicitly out of U-MEM-26's scope and recorded as such in the unit body: C6's within-family local-terminal limit, and the C-MEM-10 promotion-eligibility question for records captured during a cross-family fallback leg.
- See `.harness/clearance/README.md` for marker discipline.
