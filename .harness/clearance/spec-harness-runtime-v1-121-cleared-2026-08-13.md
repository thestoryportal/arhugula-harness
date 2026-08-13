---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.121
cleared_at: 2026-08-13T16:00:00-07:00
clearance_type: spec-writer-apply-pass
back_reference:
  - ".harness/forward-register.yaml B-71 row (the defect; council CONVENED + CLOSED 2026-08-12)"
  - ".harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md v6 (the design record)"
  - ".harness/clearance/spec-harness-runtime-v1-120-cleared-2026-08-12.md (predecessor)"
  - "PR #1326 (the leg's TRUE shape recorded on main — this Runtime delta is item 2 of the six it enumerates)"
co_requisite:
  - ".harness/clearance/spec-control-plane-v1-119-cleared-2026-08-13.md (the token contract; this file owns only the two call sites)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - out-of-family `just codex-review` at this leg's PR (to convergence)
supersedes: spec-harness-runtime-v1-120-cleared-2026-08-12.md
---

# Clearance — Spec_Harness_Runtime v1.121 (B-71 co-requisite: the escalation-token minter and the idempotency-key fold)

**Why this delta exists at all.** `B-71`'s defect is CP-observable but its two repair
sites are Runtime-owned. The CP leg's fourth out-of-family review round established that
`Spec_Harness_Runtime_v1.md` §14.8.8.1 step 2 specifies the **two-argument**
`compose_hitl_action_id(step_context.parent_action_id, placement.position)` — re-verified
against HEAD at this leg's grounding pass — so a CP delta that claimed no Runtime revision
was claiming zero by omission. Without this file, CP v1.119's carriers would ship with
nothing writing to them.

**What v1.121 changes — two canonical-reading amendments, no body edits.**

1. **§14.8.8.1 step 1** is the token's singular MINTER (CP v1.119 §0.4(3)). Canonically
   read as additionally populating `HITLEscalationBrief.escalation_instance_id` per CP
   §0.4.3's three-arm read order over the two `StepExecutionContext` carriers.
2. **§14.8.8.1 step 2** folds the token inside `compose_hitl_action_id` — at that one site,
   because CP §0.2 promises the webhook `Idempotency-Key`, the CP audit `action_id` and the
   F2 ledger key remain one identity family. A second key composed alongside would
   reintroduce the §0.1 aliasing on whichever the F2 writer used.

Both bodies are **PRESERVED VERBATIM**; the canonical reading rides in the change-note.
That is this file's established shape for a consumer-cite amendment (the v1.34 §14.8.8.1
step-3 `deliver_webhook` → `deliver_webhook_for_brief` precedent).

**What this clearance deliberately does NOT ratify.**

- **No signature shape.** Whether the token arrives as a third parameter, a widened context
  argument, or otherwise is implementation discretion settled by execution at U-RT-155.
  This is the file's own §14.8.8.10 CONTRACT-not-mechanism precedent, set at v1.106 after a
  draft prescribed a call shape that grounding falsified against the real call graph — and
  it is precisely the discipline `B-71`'s earlier attempts violated.
- **No token contract.** Shape, digest formula, leak bar and read order are CP v1.119's;
  this file restates none of them and cannot drift from them by construction.

**Not a design extension (X-AL-3).** ZERO new contract number, fail class, enum extension,
configuration field, `HarnessContext` field, plan unit beyond the filed delta, CXA row or
cross-axis edge. ZERO change to `HITLEscalationBrief`'s other six fields, to the 4-value
HITL response palette, or to any §14.8.8.1 step other than 1 and 2. The two other live
`compose_hitl_action_id` mentions (the §14.8.2 step 4h substep 8b-HITL cite and the
§14.8.8 helper construction-shape note) are narrative/suggestion surfaces, not call sites,
and are preserved verbatim — named here so "two sites, not four" is checkable rather than
assumed.

**Byte-identity is the seam's acceptance criterion.** With `escalation_instance_id` absent
(`None`) the fold MUST reproduce the pre-arc two-argument key exactly, leaving the
linear/validator population's webhook key, audit `action_id` and ledger key unchanged.

**Anchor convention.** This delta authors NO new in-file `:NNNN` anchors; both edited sites
are named by `§`/step. Prior-version change-note anchors remain historical records.

**Posture.** Design-phase (`design-substrate/**` + this `.harness/` clearance companion),
per workspace `CLAUDE.md` §11.2. Plan delta filed at
`Implementation_Plan_Harness_Runtime_v2_63.md` (U-RT-155); the impl leg follows and is not
in this arc.
