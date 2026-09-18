---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-09-18 (U-HE-45 as-built plan record — Unit-status paragraph plus the Step 3 tick ONLY; Step 1–2 stays unticked because its --next-action half was not performed; no step text, scope sentence, contract number, row label or ordering changes)
cleared_at: 2026-09-18T04:15:00Z
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-45 section: dated Unit-status paragraph above the steps in the #1519/#1550 shape, then Step 3 ticked and Step 1–2 deliberately LEFT UNTICKED; the step sketches themselves are byte-unchanged)"
  - "PR #1569 (U-HE-45 merged 2026-09-18, dc68fd8c4779db6d78860ef4e4130668ce72f0c0 — door-merged; main's own post-merge CI success), PR #1574 (96e1739c5 — Step 3's terminating refresh, issued by the merge door's own continuation rather than a hand-authored PR)"
  - ".harness/forward-register.yaml B-273..B-284 (the §6 build order registered row-per-step with structured depends_on) and B-285, B-286, B-287, B-288 (the four findings this arc surfaced, registered rather than absorbed)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md §6 (the unified build order, its two gate columns and its Depends-on column — the contract text is UNCHANGED by this rev; the rows quote it, they do not amend it)"
  - ".claude/skills/defect-class-preflight/ (preflight class 17 added during this arc's r2 absorption and SUBTRACTED at r5; the shape is recorded as an evaluated-and-LEFT-OUT vocabulary in both carriers, following the `\\bdrift` precedent main added at #1568)"
  - ".harness/clearance/implementation-plan-he-loop-lanes-v1-u-he-27-step5-u-he-43-as-built-record-cleared-2026-09-17.md (the marker shape this one follows — every as-built revision to this plan file carries one)"
---

What changed and why it is a record, not an extension:

The U-HE-45 section gains a dated Unit-status paragraph and its Step 3 line is ticked. Step 1–2
is deliberately LEFT UNTICKED: the plan's own convention is that a checked box means the step was
carried out, and that combined step's second half (`--next-action`) was not performed, so ticking
it would record a required deliverable as complete. Out-of-family review caught exactly that in
this record's first draft.
No step text, scope sentence, contract number, row label or ordering changes; the sketches
are byte-unchanged, including the one the record explicitly says was not carried out as
written. `Spec_HE_Loop_Lanes_v1` §6 is quoted by the registered rows and is untouched.

The tick is narrower than it looks, which is why the paragraph exists. Three things the
sketch did not anticipate:

**Ten of the eleven steps had already landed.** The scope was authored when S1–S8 were all
ahead of execution. Grounding every row against landing evidence — cluster commits
`3b3e3a107` (S1) and `3b9146026` (S2), `47d4428ff`, `f0e64f217`, `7834cf47e`/`8638f2e75`/
`80c94811a` plus PRs #1409/#1412, and the merged reservations' PR numbers for S4c/S4d/S5/S6/S8
— found only **S7** carrying forward work, and it is `held` behind U-HE-40 (B-244) rather than
`open`. Round 1 of the arc registered all eleven as `open`; out-of-family review caught ONE
instance (S8, merged #1550) and grounding found the other nine. `B-287` registers the general
shape. Two instrument traps are recorded with it, because each would have produced the same
wrong answer a second time: reservations are ABSENT for U-HE-01..20 because those units BUILT
the reservation primitive, so absence there is not "unlanded"; and plan checkbox ticks LAG
execution, so a tick evidences recording and never landing.

**Step 1–2's `--next-action` half was not performed, and cannot be as written.** The sketch's
own suggested paragraph carries none of the five carriers `hook_roadmap_next` accepts
(`tools/hooks/lib.sh:286-292`) and would have returned empty with `U-*` tokens visible, which
`tools/test_roadmap_status_consumers.py:222` refuses — the exact shape that reddened U-HE-44's
refresh PR. Deeper than the wording: the parser's five carriers each name a unit or a plan doc,
while this arc's actionable frontier is FIVE register rows — `B-284`, `B-285`, `B-286`,
`B-287` and `B-288` — and a `B-*` id is unnameable by any carrier. Four are
`registered_finding` with empty `depends_on`; `B-284` is `open` with its sole dependency
`B-281` already `closed`, and `--open` applies NO dependency filtering. This line was wrong
TWICE before: it first named two rows, then four, each time corrected to a number taken from
recall rather than from running `--open` and counting. The five above are derived
programmatically from the register. Review
raised the pointer on FOUR consecutive rounds, and each rewrite only moved which BLOCKED thing
was named — U-HE-45 (just completed), then held U-HE-40, then the plan doc whose only remaining
S7 work is that same held unit. Registered as `B-288` rather than reworded a fifth time, with
`roadmap_status.md` landing byte-identical to main. An independent instance is already visible
on main: the post-#1571 paragraph names its four forward rows in prose with an empty carrier.

**The pilot-bar row's close condition is bespoke because the generic one was vacuous.** Every
other row's template reads "every unit in ‹units› landed"; the pilot bar's unit set is empty,
so that condition was satisfiable without a single passing pilot — on the row whose entire
purpose is to gate on passing pilots. It now names three distinct run_ids at 3–4 lanes each
reporting `pass: true`, and records that `pilot-2026-09-17-a` counts toward none of them,
because `pass` keys on whether a coordination HITL escalation OCCURRED rather than on whether
one remains outstanding, and the DEFERRED-HIL row is durable in an append-only ledger.

Named residual, so it is not lost to a ticked row: `phases` were never recorded on this arc's
reservation, so its C-HE-27 timing spans do not exist. The arc's own metrics capture IS queued
(`u-he-45.json`, decisions declared at 12), unlike u-he-44's, whose loss `B-285` records as
unrecoverable — `extract` refuses an arc holding a reservation and `queue` mandates a decision
count only the vanished closure session could declare.
