---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-23 (U-HE-31 execution corrections, as-built — rev-note items (i)-(iv) plus the outside-Files-list paragraph)
cleared_at: 2026-08-23T21:30:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.4-cleared-2026-08-20.md (the spec head this landing executes; C-HE-11 §1/§2/§4/§5 and C-HE-13 §3's cause-family restriction are consumed UNCHANGED — no contract number, guarantee, or §8.1 row is amended)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-31 as-built rev note items i-iv; item (i) records that HARNESS_LANE_INDEX_FORCE — spelled in the unit's own drafted Step 1/Step 3 code — was REMOVED, so the drafted body is superseded in place rather than silently contradicted)"
  - ".harness/spec/store-audit-he-loop-lanes.md (two rows added for stores this unit creates: the `QUEUE_DIR/lanes/.orphaned-<lane>` fence and the `<lane>.repair` / `.lane-id.repair` cleanup lock; C-HE-30's own 'no runtime path creates a store this page does not list' rule)"
  - ".harness/forward-register.yaml (B-200, B-201, B-202 registered by this landing; B-202 extended at round 15 with the stranded-claim symptom after the fix for it was built and then reverted)"
  - "tools/hooks/lane-init.sh + tools/lane_ports.py + the teardown release in tools/hooks/lib.sh (same PR)"
reviewer_chain:
  - "out-of-family review chain (Codex, 17 rounds on the U-HE-31 PR) covers the bundled rev note; the chain converged at round 17, which returned ONLY the three registered classes and no new defect"
  - "merge-gate 3-lens review: concurrency APPROVE; witness-adequacy BLOCK (no test distinguished the two arms of the release's rc case — a branch swap passed, fixed and mutation-probed); spec-conformance BLOCK (the `.orphaned-<lane>` store was undocumented AND invisible to the audit witness's extractor, and this arc's lib.sh edit staled the C-HE-04 mutation-probe pin — both fixed, the pin re-probed back to the 14-unprobed baseline)"
  - "author grounding: the store-audit extractor's `$var/<name>$interp` blind spot was the reason the missing store could not have been caught, so the extractor was fixed alongside the page — deleting the page row now reddens the suite, where before the literal did not exist to the witness at all"
  - "council NOT convened (proportionality: execution-time corrections to one unit's drafted sketch; every C-HE-* contract cited is unchanged and no design surface is extended — the two new stores are implementation carriers of C-HE-11 §1's own 'released at lane teardown', documented rather than designed)"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes_v1` (U-HE-31 as-built rev, 2026-08-23)

U-HE-31 landed lane initialisation against C-HE-11 §1/§2/§4/§5 with its scope intact. This
marker records the **execution-time corrections** the landing folded back into the plan, and
ratifies the design+implementation mix in one PR as a bundled-absorption arc (workspace
`CLAUDE.md` §11.4) rather than silent absorption.

**Why the plan changed at all.** The unit's drafted Step 1/Step 3 bodies carried two index
knobs with different rules — `HARNESS_LANE_INDEX_FORCE` skipped the reuse-by-path scan while a
preset claimed nothing. That asymmetry *was* a defect: a preset issued after a normal init
added a second claim for one worktree, so two shells in one lane could drive different Compose
projects, ports and volumes. The built script therefore carries ONE rule — a worktree holds at
most one claim, and an index is usable only when a claim positively names this worktree — and
one knob. The as-built note states this in place, so a future reader of the drafted code is not
left to discover the contradiction.

**What the spec's companion page gained, and why it is documentation rather than design.**
C-HE-11 §1 already requires the lane index to be "released at lane teardown". Making that
release *safe* needs two on-disk facts the contract does not name: a fence recording that an
index was released without a verified-clean Docker teardown (because `up` ADOPTS an existing
project rather than failing, so a recycled index would silently inherit a dead lane's
containers), and an exclusive lock serialising a corpse repair or an orphan cleanup. Both are
implementation carriers of the contract's own sentence, so they are listed on the store-audit
page — which C-HE-30 requires of any runtime path that creates a store — not proposed as new
design.

**No contract amendment.** No `C-HE-*` guarantee, contract number, §8.1 row, or store count in
`Spec_HE_Loop_Lanes_v1.md` changes in this PR. The §8.1 rows for C-HE-11 named
`tools/hooks/test_lane_init.sh` and `tools/test_compose_lanes.py` before this landing; both now
exist, registered in `tools/lanes_verify.py` as four `phase0` rows and one `env` row matching
the spec's own phase0/env split.

## Notes

- Phase 7 consumers may rely on the plan's U-HE-31 body **as amended by its as-built note** —
  in particular, `HARNESS_LANE_INDEX_FORCE` does not exist.
- Three obligations are registered rather than absorbed: **B-200** (per-lane telemetry
  endpoints — the stack is isolated, its consumers still dial lane 0), **B-201** (a failed
  `gc.auto 0` write warns rather than refusing the lane; its close-out condition is U-HE-32's
  bounded retry, the next unit), and **B-202** (a claim↔cleanup lock and available-memory
  inside the Docker VM — one missing primitive with three symptoms).
- See `.harness/clearance/README.md` for marker discipline.
