---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.8
cleared_at: 2026-09-18T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.7-cleared-2026-09-02.md (prior head; v1.8 is a single-carve-out addition on top of it)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md (v1.8 change-note: X8 — C-HE-06 §6 gains an operator-confirmed release, and the Invariants bullet distinguishes UNCONFIRMED (not yet observed) from a TERMINAL non-success an operator has adjudicated)"
  - "tools/merge_door.py release_refusal() + the `release` subparser (same PR: the verb that reads the amended clause); justfile merge-door-release (the recipe); .claude/skills/ship-pr/SKILL.md (the operator-facing carrier)"
  - "tools/test_merge_door.py::test_release_verb_frees_the_door_from_the_cli (admit) and ::test_release_verb_refuses_a_lease_no_operator_has_adjudicated + ::test_release_verb_refuses_while_the_merge_run_is_still_pending + ::test_release_verb_refuses_when_no_run_exists_for_the_merge_sha + ::test_release_verb_refuses_a_green_run_and_routes_to_resume + ::test_release_verb_fails_closed_when_ground_truth_is_unreadable (refuse) for the ground-truth run gate, plus the outstanding-effect refusals for the content merge and for each of the three refresh markers, each mutation-probed"
  - "operator ASKED and ratified (2026-09-18, AskUserQuestion at the r4 halt): a lane may not amend a contract to dissolve a reviewer's objection to its own code, so the carve-out was surfaced as a halt and the amendment chosen before any spec byte moved (four alternatives offered: amend / ship compliant-but-useless / abandon / override); operator may reverse by a v1.9 note"
  - "council NOT convened (proportionality: one contract gains one admissible transition; no committed surface revisited, no contract number added or removed)"
  - "B-253 (.harness/forward-register.yaml, REGISTERED 2026-09-17) is the registered row for this wedge; this arc closes its part (3) — the CLI `release` verb — ONLY. Parts (1) tiebreaker-emits-its-own-refresh and (2) step (vii) distinguishing inherited drift remain open, and the row is not amended here because the register is fenced by the lane-init-shell-portability (#1561) and u-he-40 reservations. Surfaced by the merge-gate spec-conformance lens, which caught that the arc was presenting itself as closing the finding without citing the row."
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
carve-out is gated on the RUN ITSELF, queried from ground truth at release time. Two
proxies were tried across review rounds and both admitted states they should not: the
fact of a block (ten reasons reach `mark_blocked`, most never polling that run), then
the block's reason (`land` persists `post_merge_ci_not_green` on a 45-minute TIMEOUT
too, where the run was equally unobserved). The release path now reads the merge SHA's
own `main` run and admits ONLY a COMPLETED, non-success conclusion; pending, absent,
unreadable and green all refuse, the last routing the operator back to `land`.
The sha queried is the RESERVATION's `merge_sha` from step (vi), never
`blocked_at_sha`/`unblocked_from`, which names the merge commit on only two of the ten
block paths; `unblocked_from` remains required as the operator-confirmation half. The
admitted conclusions are C-HE-19 §1's domain minus SUCCESS, so no terminal-state
contract is widened. A landing that merely crashed mid-flight carries no block at all. Both of a landing's
outstanding effects stay fenced independently: the content merge must be settled, and a
terminating refresh that has been minted OR merely declared (`refresh`,
`refresh.attempted`, or the `refresh.intent` fence) refuses outright, since step (viii)
is mandatory and nothing local proves its outcome.

The amendment was ratified BEFORE it was written. Out-of-family review ran this arc to
convergence over many rounds — the gate log is the authority for the count, and an
enumeration in this prose drifted every round it was stated, so it is not restated here.
Every round but one found real defects in the mechanism, all fixed and mutation-probed. Round 4 refused the verb on the contract rather than the code, and was
correct to: a lane may not amend a contract to dissolve a reviewer's objection to its own
work. The arc halted there, surfaced the question with its alternatives, and resumed only
on the operator's answer. Later rounds then falsified three successive drafts of the
gate in this very note — that a block implied a CI observation, that the one CI-related
block reason implied it, and that X8 needed to carve out only the merge-run clause — and
each was corrected before anything landed: the gate now reads the run from ground truth
rather than inferring it, and the exception covers both clauses of the invariant. Reviewer pressure moved this
clause from a proxy to its authority; the record is kept because the proxies read as
obviously sufficient at the time.

This is a bundled-absorption at the landing PR per CLAUDE.md §11.4 — this marker is
the ratifying back-flow signal the X-AL-3 guard and the codex context guard
(`DESIGN_IMPL_MIX`) recognize.
