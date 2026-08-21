---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-20 (S4b execution corrections, U-HE-21 only)
cleared_at: 2026-08-20T17:45:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.3-cleared-2026-08-19.md (the spec head this plan executes; C-HE-03 / C-HE-26 contracts UNCHANGED by this rev)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-21 as-built rev note items i-v, dated inline)"
  - "tools/roadmap-audit/session-start.sh:91 (the REAL session-start carrier; the reconcile-all pass landed with U-HE-18 -- the plan's tools/hooks/session-start.sh path never existed, registered at the U-HE-18 rev item (iii))"
  - "tools/hooks/test_skill_reservation_wiring.sh (the U-HE-21 grep witness; pins the landed session-start invocation + both skill carriers; same PR)"
merge_commit: "pending (pre-merge at filing time; same PR as the U-HE-21 unit)"
reviewer_chain:
  - "author grounding: the plan sketch's session-start edit is a no-op at HEAD (U-HE-18 already landed the C-HE-03 section 5 pass at the roadmap-audit hook, detached + activation-gated); the as-built witness pins the real path instead of editing a nonexistent file"
  - "lane-id mint fallback + same-lane re-entry clause + single-line back-fill are carrier-prose corrections against landed CLI semantics (selectable() is false for ANY head; HARNESS_LANE_ID's minting unit U-HE-31 has not landed) -- no contract surface changes"
  - "out-of-family codex round 1 (BLOCK, 1 P1 + 4 P2): env non-inheritance across Bash tool calls, resume-flow control bug, guard-autonomy friction (registered to U-HE-23), grep-witness weakness, artifact-heads filename tie-break -- all absorbed (rev item vi) except the guard edit, which routes to U-HE-23's reviewed guard-modification scope"
  - "out-of-family codex round 2 (BLOCK, 1 P1 + 4 P2): lane-id persistence (.harness/.lane-id, absorbed), ship-pr standalone review prefix (absorbed), witness needles (absorbed); the pending-vs-open door-timing P1 REGISTERED into the U-HE-19 item-(vii) flip-timing contradiction class routed to U-HE-22; the guard-friction re-raise HELD (rev item vii) -- register-and-hold, adjudication at the 3-lens merge gate"
  - "out-of-family codex round 3 (BLOCK, 1 P1 + 2 P2): the r1 guard-friction routing named the WRONG unit (U-HE-23 touches only merge_door.py) -- corrected to U-HE-25 with the three allowlist additions registered VERBATIM in U-HE-25's Scope; the witness gains a guard-adjudication leg that RUNS permission-guard on all six documented shapes in loop mode and pins the never-denied floor (all six adjudicate ask today; deny would structurally block the loop and is the regression pinned); the guard-friction class itself remains HELD per rev item (vii)"
  - "council NOT convened (proportionality: path/prose corrections of one unit's execution steps; every C-HE-* contract cited is unchanged)"
  - "out-of-family codex round 4 (BLOCK, 1 P1 + 3 P2): the headless ask->deny citation CONFIRMED (tools/04-loop/run.sh:18) -- absorbed as an explicit degradation clause (permission-refused reserve -> proceed unreserved + PR-body note; the landed U-HE-19 drain bootstrap + C-HE-03 section 6 holder gate keep append safety; headless scheduling-dedup arrives at U-HE-25); selectable->reserve TOCTOU absorbed (race loss == occupied path); lane-id mint write race absorbed (file-content-authoritative; atomic mint registered to U-HE-31); guard witness hardened (loud pipeline failure + force-push positive control)"
  - "out-of-family codex round 5 (BLOCK, 1 P1 + 5 P2): three NEW findings absorbed (canonical step-4 review invocation was still bare -- every mention now prefixed + witnessed; terminal-head resume overlap -- state checked before lane_id; unreserved back-fill incoherence -- ship-pr skip clause makes the headless degradation end-to-end); re-raises HELD per rev item (ix): require-allow witness gates on U-HE-25's scope, lane-id atomic mint is U-HE-31's, guard support stays classifier-blocked here and registered at U-HE-25"
  - "out-of-family codex round 6 (BLOCK, 2 P1 + 4 P2): both U-HE-25 registration matchers narrowed (exact CLI verbs; HARNESS_ARC_ID/HARNESS_LANE_ID only -- the two live P2s); degradation trigger broadened to ANY refused arc-open command + bare-review fallback with a witnessed ALLOW floor (P1a); the flip-timing class got a registered carrier line in U-HE-22's own Scope (P1b -- no longer only a rev-note residual); lane-id atomicity and witness-ask-as-success re-raises remain HELD (U-HE-31 / U-HE-25 registered scopes)"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes` v1.0 rev 2026-08-20 (S4b, U-HE-21 as-built)

The U-HE-21 landing revises only the unit's own execution record: an as-built rev note
(items i–v) documenting the stale `tools/hooks/session-start.sh` path (real carrier
`tools/roadmap-audit/session-start.sh`, whose C-HE-03 §5 `reconcile-all` pass landed with
U-HE-18 and is now PINNED by this unit's grep witness), the `HARNESS_LANE_ID` mint fallback
pre-U-HE-31, the same-lane re-entry clause over `selectable()`'s any-head refusal, the
single-line back-fill command shape, and the go-live witness — the first real open-time
reservation (`u-he-21`, gen 1, `arc_type=applying` declared at open) minted by this arc
dogfooding its own wiring, closing the U-HE-19 rev item (xi) hold.

This is a bundled-absorption of execution-time corrections at the landing PR, per
CLAUDE.md §11.4 — this marker is the ratifying back-flow signal the X-AL-3 guard and the
codex context guard (`DESIGN_IMPL_MIX`) recognize.
