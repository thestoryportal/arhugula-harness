---
artifact: design-substrate/Spec_Memory_Substrate_v1.md
version: v1.1
cleared_at: 2026-07-28T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-1-fork-ratification (B-86 spec leg; spec-writer apply pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_1_fork_b86_memory_scope_provider_family_keying.md (RATIFIED Class 1 fork, filed 2026-07-28 — §5 recommendations Q1 + Q2, §6 drafting targets)
  - .harness/forward-register.yaml — row B-86 (design_substrate_gated), with forward rows B-89 + B-90
merge_commit: pending (pre-merge at filing time; B-86 spec-leg apply PR)
reviewer_chain:
  - Opus grounding agent (2026-07-28) — direct code + spec read with file:line evidence; confirmed the defect at HEAD f79dbe85 and the C-MEM-03 / C-MEM-11 / C-MEM-13 spec silence
  - advisor() transcript-aware pass (2026-07-28) — GO plus 4 framing adjustments, including deliberating on the post-B-89 counterfactual rather than today's broken state
  - genuinely-convened council (2026-07-28) — C10 (action-safety / blast-radius) + C3 (state / memory / persistence) co-primary, C6 (model routing) consultant; the Q1 C10↔C3 tension surfaced and probe-resolved in favour of chain-primary keying, with C10's requirement satisfied at the dispatch-side predicate
  - spec-writer apply pass (2026-07-28) — this delta; no decision taken at the apply pass
supersedes: Spec_Memory_Substrate_v1-cleared-2026-07-09.md
---

# Clearance — Spec_Memory_Substrate_v1 v1.1 (B-86 spec leg)

v1 → v1.1 amends three C-MEM contracts and leaves the Memory threat model untouched. **C-MEM-03** gains a new subsection fixing `MemoryScope.provider_family`'s value domain (a `ProviderFamily` value — `anthropic`, `openai`, `google`, `local_open_weight` — never a provider key, model identifier, or CLI-profile identifier; non-value identifiers are unretrievable under family-scoped requests; normalization forward-only), the previously-undocumented but load-bearing `null` semantics (unpartitioned wildcard, **not** unknown-deny), and the run-level derivation rule (composed once at run-scope composition from the fallback chain's primary family binding, never re-derived per dispatch) with its paired writer-side obligation (capture writes under the run's composed record scope and constructs no independent scope). **C-MEM-13** gains a cross-family withholding invariant: on a `standard_memory_tools` dispatch whose candidate family differs from `MemoryScope.provider_family`, the tool schemas and the scope reference must not be exposed, the dispatch proceeds without model-facing memory access, and the withholding is recorded with a named denial reason — harness-authored capture unaffected. **C-MEM-14**'s exposure obligation is qualified against that invariant: a withheld exposure is a ledgered outcome, not a contract violation.

The amendment is **conformance repair, not design extension**. The threat-model invariant "Retrieval and injection enforce project, workflow, tenant, provider-family, CLI-profile, and visibility scope before ranking." (line `:481` at fork-filing HEAD `f79dbe85`) already mandated the boundary at v1; it never said what the boundary is keyed to, leaving the mandate unfalsifiable at the contract level. v1.1 supplies the value domain, derivation rule, and dispatch-boundary condition that make the cleared invariant checkable, and that invariant itself stands byte-unchanged — the X-AL-3 posture this leg rests on.

Scope discipline: zero new record type, zero new field, zero new enum member, zero change to any ledger, packet, or telemetry shape. C-MEM-01, C-MEM-02, C-MEM-04 through C-MEM-12, the Memory threat model, and C-MEM-15 through C-MEM-20 are preserved verbatim; the C-MEM-03 / C-MEM-13 / C-MEM-14 field shapes, vocabularies, tables, and pre-existing invariants are byte-unchanged, with subsections and invariants appended only.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The impl leg — the C-MEM-13 withholding guard (fork §5 Q2), the `B-89` writer-side repair, and the incidental `B-90` fold-in — is a separate, not-yet-opened arc, decomposed at `Implementation_Plan_Memory_Substrate_v1.md` v1.1 as U-MEM-26.
- Two items are carried, not discharged, at v1.1: C6's stated limit (family equality is necessary but not sufficient; the within-family local-terminal posture is addressed outside this contract) and C3's open question on promotion eligibility of records captured during a cross-family fallback leg (C-MEM-10 policy territory).
- The predecessor marker `Spec_Memory_Substrate_v1-cleared-2026-07-09.md` recorded the retroactive Phase-7 in-flight absorption of v1; this marker supersedes it for version-currency purposes and does not invalidate it.
- See `.harness/clearance/README.md` for marker discipline.
