---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.115
cleared_at: 2026-08-11T10:55:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/b145-grounding-split-2026-08-11.md
  - .harness/forward-register.yaml B-145 row (grounded_2026_08_11 block)
  - "PR #1304 (the grounding split filing)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "B-145 grounding split (loop orchestrator, all cites re-read at HEAD, codex round-1 corrected — PR #1304)"
  - out-of-family `just codex-review` at this leg's PR (to convergence)
  - impl-time grounding pass at this leg (4 live occurrences re-verified; cross-spec drift grep clean — sibling mentions are historical delta records only)
supersedes: spec-harness-runtime-v1-114-cleared-2026-08-08.md
---

# Clearance — Spec_Harness_Runtime v1.115 (B-145 GAP-1 alias alignment)

**What v1.115 changes.** Four in-place step-bullet mention edits, nothing else:
the pre-rename v1.2-era attribute names `retry.backoff_ms` (retry bullets,
v1.114 offsets `:4229`/`:5685`) and `retry.cause_class` (fail-fast bullets,
`:4228`/`:5686`) are aligned to the canonical C-CP-03 §3.5 v1.3 names
`retry.delay_ms` / `retry.cause_attribution`. No attribute is added, removed,
or resemanticized; the five `retry.terminal` values and every other clause of
the four bullets are byte-preserved.

**Why this is a correction, not a design extension (X-AL-3).** The CP §3.5 v1.3
amendment (`Spec_Control_Plane_v1_3.md:76`) replaced the 4-attribute retry set
outright — none of the four v1.2 names survive — and the SAME Runtime sections
already bind the §3.5 6-attribute schema at their inner-span bullets
(`:4225`/`:5682` at v1.114). Both shipped producers emit the §3.5 names. The
four bullets were self-inconsistent drift within their own sections; wiring
them as-written would have put duplicate keys on the wire for every retry
attempt (grounding split, GAP-1 section).

**Paired same-arc code re-disposition (close-out step 5).** The two
`emitted=False` `RETRY_WIRE_REGISTER` rows in
`harness_cp/retry_fallback_namespace.py` are REMOVED (the two-venue union no
longer contains the aliases) with
`test_unemitted_keys_are_exactly_the_two_b145_registers` re-pinned to the
empty set in the same commit — the B-145 close-out's forced-edit discipline.

**Not touched here.** B-145 GAP-2a (tool-path escalate unreachable-by-
construction — its own control-flow/spec leg), the B-150 collector half
(C-RT-10 step-3a ordering), and the B-144 §24.1.B venue fork remain open legs.
