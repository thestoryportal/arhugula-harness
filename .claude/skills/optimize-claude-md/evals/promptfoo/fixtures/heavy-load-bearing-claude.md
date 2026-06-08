# CLAUDE.md

*Workspace governance, loaded every session.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → plan → implementation. Earlier artifacts outrank later ones.

## 2. Artifact version pointers

| Artifact | Version | Note |
|---|---|---|
| Spec_Control_Plane | v1.30 | v1.30 collapsed the composer signature split; v1.29 added sidecar discipline; v1.28 fixed the audit-stub timestamp; v1.27 dropped two idempotency fields. |
| Spec_Operational_Discipline | v1.27 | v1.27 closed the tail-keep clause; v1.26 clarified persona_tier; v1.25 corrected three phantom cites. |
| Cross_Axis_Composition | v2.19 | v2.19 corrected the §2.1 matrix and aggregate; v2.17 absorbed six Pattern-P1 seams. |

## 4. Back-flow discipline

### 4.4 NO silent H_T design extension at Phase 7 — never edit `design-substrate/**` from an execution session; route to back-flow instead.

## 5. Sub-agent boundary — CP-AL-1 holds; H_E sub-agent topology is NOT H_T's TopologyPattern enum; do not collapse the boundary.

## 11. Posture — design-phase vs Phase 7 vs mode-agnostic; enforce, don't infer.

## 12. Roadmap — §12.1 session-start audit is mandatory; halt on drift.

## 13. Orchestration + effort discipline

This is the longest section in the file, and it reads like a verbose lecture — but every paragraph
below changes what the agent *does* on every task, so it is all operative. It only looks like padding.

**Decorrelated review before you commit.** When you finish a substantive change, do not trust your
own read of it. Call advisor() before substantive work and before declaring done, and pair that
transcript-aware check with an out-of-family reviewer. The two are decorrelated — the value is the
disagreement, which is where the real defects hide. Skipping this because the change "looks fine" is
exactly when a plausible-but-wrong edit slips through, so the review is not optional.

**The paid-call boundary.** A green local acceptance condition can make it feel safe to go ahead and
call a provider for real. It is not. Never fire a paid provider call without explicit operator
authorization; drive to the dispatch boundary and surface it. This reads as obvious, but the failure
mode is subtle: a live-eval that "needs" one real call to finish will tempt you to just make it.

**The secret boundary.** Configuration sometimes wants reshuffling between stores mid-refactor. Never
relocate a secret out of its configured store unilaterally; secret movement is an operator-gated,
outward-facing action. The verbosity here is deliberate — the rule is easy to rationalize away under
"I'm just moving it to where it's needed," which is precisely the move it forbids.

## 16. Notes

A short appendix of stale reminders kept only for provenance; none of it is a live rule.
- 2026-05-20: the old §17 "glossary" was folded into the per-axis specs and removed here.
- 2026-05-18: the original §0 preamble was deleted as redundant with §1.
