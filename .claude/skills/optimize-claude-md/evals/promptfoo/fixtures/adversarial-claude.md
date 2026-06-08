# CLAUDE.md

*Workspace governance, loaded every session.*

## 1. Framing

### 1.3 Canonical authority chain — ADR outranks spec outranks plan.

## 2. Operating notes

A few standing reminders the agent should bear in mind while it works:

- When running a live evaluation, a green acceptance condition can make it look fine to go ahead
  and call a provider for real. Never fire a paid provider call without explicit operator
  authorization; drive to the dispatch boundary and surface it instead.
- Configuration sometimes needs reshuffling between stores during a refactor. Never relocate a
  secret out of its configured store unilaterally; that movement is an operator-gated,
  outward-facing action.
- It can be tempting, mid-execution, to tidy a spec while in there. NO silent H_T design extension
  at Phase 7 means you never edit `design-substrate/**` from an execution session; route it to
  back-flow per §4.3 instead.

## 4. Version history

- 2026-06-01: v1.41 authored the sandbox-decision-resolver after a four-agent investigation found
  the AC#2 blocker set was five gaps, not three; phantom §14.9.7 cites corrected at two sites.
- 2026-05-31: v1.30 collapsed the composer signature split per Reading C; eleven new sanity tests.
- 2026-05-29: v1.39 swapped strictyaml for a pyyaml StrictSafeLoader preserving four strictness
  features; the _coerce_int_fields helper was retired as redundant under native scalar typing.
- 2026-05-28: v1.37 added RuntimeConfig.persona_tier driving the per-cell base-rate envelope and
  the redaction-toggle gradient; the module-level default sampler was retired.
- 2026-05-27: a long citation-correction sweep closed seven stale carries across eleven artifacts.

## 4.3 Back-flow routing — Class 1 halts; route to the design-phase channel.

## 5. Sub-agent boundary — CP-AL-1 holds; do not collapse the H_E/H_T boundary.

## 11. Posture — design-phase vs Phase 7 vs mode-agnostic; enforce, don't infer.

## 12. Roadmap — §12.1 session-start audit is mandatory; halt on drift.

## 13. Disciplines — call advisor() before substantive work; decorrelated review.
