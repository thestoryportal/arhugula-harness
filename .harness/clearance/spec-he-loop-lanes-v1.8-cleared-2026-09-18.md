---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.8
cleared_at: 2026-09-18T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.7-cleared-2026-09-02.md (prior head; v1.8 is a single-carve-out addition on top of it)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md (v1.8 change-note: X8 — C-HE-06 §6 gains an operator-confirmed release, and the Invariants bullet distinguishes UNCONFIRMED (not yet observed) from a TERMINAL non-success an operator has adjudicated)"
  - "tools/merge_door.py release_refusal() + the `release` subparser (same PR: the verb that reads the amended clause); justfile merge-door-release (the recipe); .claude/skills/ship-pr/SKILL.md (the operator-facing carrier)"
  - "tools/test_merge_door.py::test_release_verb_frees_the_door_from_the_cli (admit) and ::test_release_verb_refuses_a_lease_no_operator_has_adjudicated + ::test_release_verb_refuses_a_block_that_never_observed_the_merge_run[5 reasons] (refuse) for the `unblocked_reason` gate, plus the outstanding-effect refusals for the content merge and for each of the three refresh markers, each mutation-probed"
  - "operator ASKED and ratified (2026-09-18, AskUserQuestion at the r4 halt): a lane may not amend a contract to dissolve a reviewer's objection to its own code, so the carve-out was surfaced as a halt and the amendment chosen before any spec byte moved (four alternatives offered: amend / ship compliant-but-useless / abandon / override); operator may reverse by a v1.9 note"
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
carve-out is gated on the block's REASON. Ten distinct reasons reach `mark_blocked`
and only `post_merge_ci_not_green` means that run was observed and is terminally not
green; `base_toctou_first_parent_mismatch`, `containment_refusal:*`,
`door_failed_after_attempt:*`, `unreconcilable_at_resume:*`,
`refresh_skipped_without_optin` and `refresh_intent_unresolved` all block without ever
observing it, so an unblock alone attests nothing about that run. Since `unblock` nulls
`blocked_reason` on the successor it mints, the reason is carried forward as
`unblocked_reason` beside the `unblocked_from` sha, and that field is the gate. A
landing that merely crashed mid-flight carries no block at all. Both of a landing's
outstanding effects stay fenced independently: the content merge must be settled, and a
terminating refresh that has been minted OR merely declared (`refresh`,
`refresh.attempted`, or the `refresh.intent` fence) refuses outright, since step (viii)
is mandatory and nothing local proves its outcome.

The amendment was ratified BEFORE it was written. Five out-of-family review rounds ran on
this arc; rounds 1–3 and 5 found real defects in the mechanism, all fixed and
mutation-probed. Round 4 refused the verb on the contract rather than the code, and was
correct to: a lane may not amend a contract to dissolve a reviewer's objection to its own
work. The arc halted there, surfaced the question with its alternatives, and resumed only
on the operator's answer. Round 5 then falsified this note's own first draft of the gate
— which claimed a block implied a CI observation — and the carve-out was narrowed to the
one reason that carries it before anything landed.

This is a bundled-absorption at the landing PR per CLAUDE.md §11.4 — this marker is
the ratifying back-flow signal the X-AL-3 guard and the codex context guard
(`DESIGN_IMPL_MIX`) recognize.
