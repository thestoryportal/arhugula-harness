---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.8
cleared_at: 2026-09-18T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.7-cleared-2026-09-02.md (prior head; v1.8 is a single-carve-out addition on top of it)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md (v1.8 change-note: X8 — C-HE-06 §6 gains an operator-confirmed release, and the Invariants bullet distinguishes UNCONFIRMED (not yet observed) from a TERMINAL non-success an operator has adjudicated)"
  - "tools/merge_door.py release_refusal() + the `release` subparser (same PR: the verb that reads the amended clause); justfile merge-door-release (the recipe); .claude/skills/ship-pr/SKILL.md (the operator-facing carrier)"
  - "tools/test_merge_door.py::test_release_verb_frees_the_door_from_the_cli and ::test_release_verb_refuses_a_lease_no_operator_has_adjudicated (the admit/refuse witnesses for the `unblocked_from` gate), plus the four outstanding-effect refusals, each mutation-probed"
  - "operator ASKED and ratified (2026-09-18, AskUserQuestion at the r4 halt): a lane may not amend a contract to dissolve a reviewer's objection to its own code, so the carve-out was surfaced as a halt with three alternatives (ship compliant-but-useless / abandon / override) and the amendment chosen before any spec byte moved; operator may reverse by a v1.9 note"
  - "council NOT convened (proportionality: one contract gains one admissible transition; no committed surface revisited, no contract number added or removed)"
supersedes: ".harness/clearance/spec-he-loop-lanes-v1.7-cleared-2026-09-02.md"
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.8 (merge-door-release-verb landing)

C-HE-06 §4 step (ix) ends every landing with "release via §6", and §6 enumerates
release among the three transitions its marker CAS governs — but no CLI verb exposed
it, so the door's own documented recovery was unreachable from a shell. Building the
verb surfaced the deeper gap: the state it exists to recover — a landing whose own
merge commit reddened `main` — is one the contract permitted no exit from. Step (vii)
polls that merge SHA's own run and the commit's bytes are immutable, so `land`
re-blocks forever; `unblock` mints a successor lease rather than opening the door; and
`gc` skips live leases. Observed twice in one session: #1570 blocked at (viii) on
`refresh_pr_ci_not_green`, and #1573 blocked at (vii) with a permanently red merge SHA.

X8 resolves it by distinguishing two readings of one word. "Unconfirmed" in the
Invariants bullet means *not yet observed* — an outcome still in flight, which must
never be released past. A run that HAS been observed and reached a terminal
non-success is confirmed, badly, and the contract had no sentence for it. The
carve-out is gated on `unblocked_from`, which is a chain the state machine already
enforces rather than a convention: `unblocked_from` is written only by `unblock`,
`unblock` requires `state: blocked`, and `blocked` is written only after (vii)/(viii)
resolved non-success — so an operator has adjudicated the outcome before the release
path opens, and a landing that merely crashed mid-flight carries no block and is
refused. Both of a landing's outstanding effects stay fenced independently: the
content merge must be settled, and a MINTED terminating refresh (either sidecar)
refuses outright, since step (viii) is mandatory and nothing local proves its outcome.

The amendment was ratified BEFORE it was written. Four out-of-family review rounds ran
on this arc; rounds 1–3 found real defects in the mechanism, all fixed and
mutation-probed. Round 4 refused the verb on the contract rather than the code, and
was correct to: a lane may not amend a contract to dissolve a reviewer's objection to
its own work. The arc halted there, surfaced the question with its alternatives, and
resumed only on the operator's answer.

This is a bundled-absorption at the landing PR per CLAUDE.md §11.4 — this marker is
the ratifying back-flow signal the X-AL-3 guard and the codex context guard
(`DESIGN_IMPL_MIX`) recognize.
