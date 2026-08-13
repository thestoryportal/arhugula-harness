---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_53.md
version: v2.53
cleared_at: 2026-08-13T16:00:00-07:00
clearance_type: Phase-7-absorbed-via-back-flow-record
back_reference:
  - .harness/clearance/spec-control-plane-v1-119-cleared-2026-08-13.md
  - .harness/clearance/spec-harness-runtime-v1-121-cleared-2026-08-13.md
  - "register row B-71; council CONVENED + CLOSED 2026-08-12; leg shape recorded on main at PR #1326"
co_requisite:
  - .harness/clearance/implementation-plan-harness-runtime-v2-63-cleared-2026-08-13.md
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - out-of-family `just codex-review` at this leg's PR (to convergence)
supersedes: implementation-plan-control-plane-v2-52-cleared-2026-08-12.md
---

# Clearance — Implementation_Plan_Control_Plane v2.53 (B-71 CP-side execution authority)

**What v2.53 adds.** ONE new unit, **U-CP-102**, owning the four additive carrier
amendments CP spec v1.119 declares (`HITLEscalationBrief.escalation_instance_id`;
`StepExecutionContext.pre_dispatch_escalation_basis` and
`.pre_dispatch_escalation_instance_id`; the per-branch resume-state echo) plus the three
advisory `payload_body` keys, with ten acceptance criteria and four mutation-probe
obligations.

**Why a new unit rather than criteria on the landed carriers.** The four sites belong to
units long landed under C-CP-25 / C-CP-26 / C-CP-28. Amending their criteria in place would
rewrite history verified against a different contract — the failure v2.52 §0.2 avoided by
riding supersession as a note — and would scatter one mechanism across three units whose
landings cannot be sequenced against each other. `B-71` is one mechanism: minted once,
folded once, persisted once, read before recompute. Its carriers are jointly meaningless in
isolation.

**Declared reach, stated rather than implied.** U-CP-102 sits in the C-CP-28 cluster and
declares fields on C-CP-25 and C-CP-26 carriers. Recorded explicitly because an undeclared
reach is how a plan acquires a hidden coupling edge. It adds **no new dependency edge into
any landed unit** — every amendment is additive and `None`-defaulted, so no landed unit's
acceptance is invalidated and none must re-run to remain true.

**The Runtime co-requisite is bidirectional and is a plan-level fact.** U-CP-102 declares
carriers; U-RT-155 writes and folds. Carriers with no minter stay `None` forever; a minter
with no carriers has nothing to write. They land in one arc — recorded so a future session
cannot schedule one alone and read a green suite as evidence the mechanism works.

**Not a design extension (X-AL-3).** No contract number is minted (the spec leg mints
none); no existing field changes type; no landed unit body is amended; no OD / IS / AS /
CXA / ADR / ADD / PRD change. The follow-ons registered at CP spec §0.9 are explicitly out
of scope and each owes its own leg.

**Posture.** Design-phase (`design-substrate/**` + this `.harness/` clearance companion),
per workspace `CLAUDE.md` §11.2. This delta assigns the work; the code lands at the impl
leg, which is not in this arc.
