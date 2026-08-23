---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-22 (U-HE-29 execution corrections, as-built — rev-note items (i)-(xix))
cleared_at: 2026-08-22T13:45:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.4-cleared-2026-08-20.md (the spec head this landing executes; C-HE-09 §1-§6 + Invariants and C-HE-20 §1 are consumed UNCHANGED)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-29 as-built rev note items i-xix; item (xix) records that the cutover migration built during review was CUT before merge, and says so ahead of items ii-xviii which document it)"
  - ".harness/forward-register.yaml (B-194, B-196, B-198, B-199 registered by this landing; B-195 and B-197 CLOSED with the migration they described)"
  - "tools/hooks/loop_lib.sh shared venue + structured column + shared AWK preludes + loop_notify_summary; tools/arc_exit_report.py ledger_path resolver (same PR)"
reviewer_chain:
  - "author grounding: the SessionStart carrier path correction (i); the arc_exit_report.py second-carrier absorption (ii) traced from a landing-order defect that would have failed every arc closure with exit 3; the deleted R-7 discrimination (iii) and its re-cut tests; the _loop_epoch phantom (iv); the two extracted row-format helpers (v); the TTL reducer's ACTIVATE strike (vi); the eight suites pinned to the shared venue (vii) incl. the monkeypatch.undo() hazard; the two further inverted scoping assertions (viii)"
  - "out-of-family review chain on the U-HE-29 PR covers the bundled rev note"
  - "council NOT convened (proportionality: execution-time corrections of one unit's sketch; every C-HE-* contract cited is unchanged and no design surface is extended)"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes` v1.0 rev 2026-08-22 (U-HE-29 as-built)

The U-HE-29 landing revises only the unit's own execution record: rev note items (i)–(x).
No `design-substrate/**` file is touched and no H_T design surface is extended (X-AL-3
holds); C-HE-09 §1–§6 + Invariants and C-HE-20 §1 are consumed exactly as cleared at
`spec-he-loop-lanes-v1.4-cleared-2026-08-20.md`.

The single item worth flagging for a reader is (ii): `tools/arc_exit_report.py` was a
second, unenumerated live carrier of the ledger venue, holding its own path derivation.
Landing the C-HE-09 §2 venue move without absorbing it would not have been a cosmetic
omission — `loop_log` would have appended to the shared venue while `append_ledger_row`'s
pre/post growth check watched the old per-worktree path, so the check could never witness
growth and every arc closed through `ship-pr` would have failed closed at exit 3. It is
absorbed by replacing the constant with a resolver that asks `loop_status_path` itself, so
the venue has exactly one authority across both carriers. Item (iii) records the
consequence: the pre-U-HE-29 worktree-vs-main ledger discrimination and its two provenance
notes are deleted rather than ported, because under one shared venue both notes would be
false claims about how the rows were sourced.

Items (i), (iv)–(x) are smaller as-built corrections: the SessionStart carrier's real path,
a phantom `_loop_epoch` helper replaced by a shared AWK prelude, two extracted row-format
helpers that keep `loop_resolve`'s self-verification byte-identical to the writer, the
ACTIVATE-reset strike reaching the TTL re-surfacer, the eight test suites pinned to the
shared venue, two further inverted skip-set scoping assertions, the manifest row that was
already present plus the new second-carrier row, and the U-HE-18 SessionStart activation
gate self-activating now that `loop_log_structured` exists.

## Re-sync 2026-08-23 — scope of this marker

The body above was written when the rev note ended at item (x). It now runs to **(xix)**, and
a reader trusting this marker as the canonical summary (CLAUDE.md §4.5) must not be left with
the earlier picture. What changed after (x):

**Items (xi)–(xviii): 23 out-of-family rounds and 3 decorrelated 3-lens merge-gate rounds.**
Substantively: the `ln`-based atomic publication of the venue header (staged to an `mktemp`
file so a partial header is never visible), `_loop_lane_id` resolving the persisted
`.harness/.lane-id` with BASHPID-correct process identity, the lane sanitisation and the
matched reader in `arc_exit_report`, the `[lane_id]` render, the mandatory absorption of
`arc_exit_report`'s second ledger-path derivation (without which every arc would have closed
at exit 3), and `merge_door._notify`'s retry. Item (xvii) records a CORRECTION to this arc's
own reasoning: the measurement that justified building a cutover migration was an artifact of
reducing an old-semantics ledger with the new rule.

**Item (xix): the cutover migration was CUT before merge.** ~318 lines plus 44 tests, removed
wholesale (net −1483) once measurement showed the pre-U-HE-29 per-worktree ledgers hold
nothing still open under the semantics their rows were written with. It had generated roughly
20 of the arc's 23 review rounds. The unit's own contracts — C-HE-09 §1–§6 and C-HE-20 §1 —
were settled at round 3 and never regressed through any of it, which is what this marker
clears.

**Forward register.** `B-198` carries the measurement and the conditions under which a drain
would be warranted; `B-195` and `B-197` are CLOSED with the migration (every race they
recorded was a property of it). Still open against the surviving surface: `B-194` (the lane
encoding is a destructive strip, so two ids differing only in stripped characters collide —
misclassification half fixed), `B-196` (per-arc `todo_for_human` scoping needs a per-item lane
SET, which §3 does not render; HEAD annotates and never drops) and `B-199` (`_notify` cannot
make a DEFERRED-HIL durable when every write fails; release-safety must precede propagation,
or an escaping exception strands the global merge-door lease).
