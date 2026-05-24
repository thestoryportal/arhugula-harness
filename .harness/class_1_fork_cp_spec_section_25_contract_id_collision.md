# Class 1 Fork — CP spec §25 / C-CP-25 contract-ID collision

**Filed:** 2026-05-24 during checkpoint #2 traversal (`§25-renumbering drift CP spec hygiene`) — Phase 7 sub-phase 7b at workspace HEAD `c0b9c87` (post pause/resume Sub-arc A doc reconciliation arc).

**Status:** OPEN (routing target: systems-architect Mode 3 disambiguation recommendation → operator ratification → spec-writer apply pass).

**Filing skill:** `phase-7-implementation` §6 halt-condition "Cited spec contract section unreachable or under-specifies the surface" → upclassified from Class 3 documentation drift after empirical cite-inventory grep returned 67 bare `§25` + 119 bare `C-CP-25` cites across `design-substrate/` + axis CLAUDE.md substrate.

## §1 Empirical state

CP spec uses the same `§25` section number AND the same `C-CP-25` contract ID for two semantically distinct contracts introduced at different spec revisions:

| Lineage | Section | Contract ID | Contract name | Authoring site | Surface |
|---|---|---|---|---|---|
| **v1.6-meaning (WorkflowDriver)** | §25 (with §25.1 – §25.9; §25.2.1 StepDispatcher/StepExecutionContext) | C-CP-25 | `WorkflowDriver` | `Spec_Control_Plane_v1_6.md` (v1.4 introduced; v1.5+v1.6 amended §25.9 + §25.2.1) | per-step iteration discipline + drain protocol + lifecycle event emission; scoped to `SINGLE_THREADED_LINEAR` + `pure-pattern-no-engine` / `save-point-checkpoint` |
| **v1.10-meaning (ValidatorFramework)** | §25 (NEW) | C-CP-25 | `ValidatorFramework` | `Spec_Control_Plane_v1_10.md` (NEW) | per-step deterministic validation gate; 5-class `ValidatorFailClass` + 5-class `ValidatorOutcome`; substitution H_T-CP-21 |

The v1.10 change-note authored the NEW §25 / C-CP-25 ValidatorFramework without acknowledging the pre-existing §25 / C-CP-25 WorkflowDriver. v1.10 §"Adjacent defects surfaced (not patched per FM-2 no-extension discipline)" reads: "**None** — apply pass is fidelity-pure transcription of ratified draft content." The collision was not surfaced at v1.10 authoring time.

The CP plan v2.18 change-note §0(i) (this session's predecessor session) surfaced the collision as adjacent finding: "§25-renumbering drift across CP spec v1.10 ... v1.6 §25.2.1 StepExecutionContext authoring site lives at the v1.6 spec file canonically ... v1.10 introduced the renumbering ambiguity. The v1.12 amendment (this session) cites `§25.2.1` per the v1.6 canonical authoring site — the cite is operatively correct ... but the §25 renumbering drift at v1.10 surfaces a section-numbering hygiene issue at the cross-version interpretation surface. Surfaced; routing to a future CP spec hygiene revision arc; non-blocking at v1.12 + v2.18 publication."

This fork doc upclassifies the CP plan v2.18 §0(i) "non-blocking adjacent finding" to **Class 1** based on empirical cite-inventory.

## §2 Downstream cite inventory (HEAD `c0b9c87`)

Counts via `grep -rn` across `design-substrate/` + workspace + axis `CLAUDE.md` substrate. Counts INCLUDE the spec-internal self-cites.

| Form | Count | Disambiguation criterion |
|---|---|---|
| Bare `§25` (not followed by `.` subsection digit) | 67 | requires contextual reading of surrounding prose |
| Bare `C-CP-25` (not followed by ` §25.x`) | 119 | requires contextual reading of surrounding prose |
| Per-meaning-distinguishing keyword co-located in file | WorkflowDriver-meaning: 37 file-hits / ValidatorFramework-meaning: 19 file-hits | files citing the distinguishing class-name |

The 37 vs 19 split is illustrative-only — file-hit counts are NOT line-counts and a file may cite both meanings. The point: both meanings have substantial cite footprints, and many bare cites resolve only via surrounding-prose context.

### §2.1 Notable cite sites by meaning

**WorkflowDriver-meaning (v1.6-lineage) cites include:**
- `Spec_Control_Plane_v1_6.md` self-cites throughout §25 / §25.1 / §25.2 / §25.2.1 / §25.3 / §25.4 / §25.5 / §25.6 / §25.7 / §25.8 / §25.9 + Filing footer
- `Implementation_Plan_Control_Plane_v2_18.md` U-CP-56 (StepExecutionContext 9th-field per Path A fork resolution)
- v1.12 change-note (this session's predecessor) §1 + §1 amendment site
- `harness-cp/CLAUDE.md` §1.3 + §3 scope inclusion table
- `harness-runtime/CLAUDE.md` driver-axis sections
- Plan-body U-CP-56 + U-CP-57 (driver materialization)

**ValidatorFramework-meaning (v1.10-lineage) cites include:**
- `Spec_Control_Plane_v1_10.md` self-cites throughout §25 ValidatorFramework
- `Implementation_Plan_Control_Plane_v2_18.md` U-CP-58 + U-CP-59 + U-CP-60 + U-CP-61 (ValidatorFramework materialization cluster 10-CP-A)
- `Spec_Harness_Runtime_v1.md` v1.18 §14.13 + §14.13.1 – §14.13.6 (C-RT-23 ValidatorFramework stage-4 factory)
- `Implementation_Plan_Harness_Runtime_v2_17.md` L9-decies cluster (U-RT-83/84/85) at every cite of "CP spec v1.11 §25" — 13+ in-file cites
- `harness-cp/CLAUDE.md` §1.3 scope inclusion (ValidatorFramework row)
- `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §1.1 + §3.1 (Reading A grep-verified inventory)

## §3 Why this is Class 1, not Class 3

**Class 3 (documentation drift)** applies when downstream cite-resolution is unambiguous in context. **Class 1 (halt-execution)** applies when downstream cite-resolution requires reader inference and could plausibly mis-route.

Empirical Class 1 evidence:

1. **Contract ID re-use is not a section-number-only issue.** "C-CP-25" is the canonical identifier consumed at adversarial review, coverage matrices, and per-axis CLAUDE.md scope tables. Two contracts sharing one ID is structurally ambiguous regardless of section-number rendering.

2. **Both meanings have active in-flight implementation arcs.** As of HEAD `c0b9c87`: U-CP-56 (v1.6-meaning) just landed at `0cfd23a` (this session predecessor); U-CP-58/59/60/61 (v1.10-meaning) landed at L9-decies cluster boundary; runtime plan v2.17 L9-decies (v1.10-meaning consumer) just landed at `37e9d67`. Concurrent active citation traffic to both meanings.

3. **Adversarial review surface.** Adversarial Review 06 + 07 cleared L9-octies + L9-decies at "0 Class 3" while both reviews cite "CP spec v1.11 §25" with the v1.10-meaning. Future adversarial reviews against any §25 / C-CP-25 surface require operator-supplied context to disambiguate.

4. **PRD + ADD attestation surface.** ADD v1.3 attests CP spec at v1.2; PRD references "C-CP-25" without sub-section — at any future ADD / PRD revision the disambiguation propagates.

## §4 Candidate readings (operator-decision)

| Reading | Mechanics | Cite-cascade size | Pros | Cons |
|---|---|---|---|---|
| **A — Rename v1.10 NEW to C-CP-28 / §28** | v1.10 ValidatorFramework becomes C-CP-28 / §28; v1.6 WorkflowDriver stays C-CP-25 / §25 byte-exact | ~19 file-hits to retag at runtime spec v1.18 + runtime plan v2.17 + CP plan v2.18 §10-CP-A units + harness-cp/CLAUDE.md ValidatorFramework row + spec v1.10 itself + downstream OD / CXA cites of ValidatorFramework | preserves the earlier (v1.6) canonical authoring site verbatim; CP spec v1.10 was the offender — fixing the offender is fidelity-preserving | retags freshly-landed L9-decies cluster artifacts (within-session); cascades into runtime spec v1.18 (just published); requires CXA cite reconciliation |
| **B — Rename v1.6 to C-CP-28 / §28** | v1.6 WorkflowDriver becomes C-CP-28 / §28; v1.10 ValidatorFramework stays C-CP-25 / §25 byte-exact | ~37 file-hits to retag at CP spec v1.6 self-cites + v1.12 + CP plan v2.18 U-CP-56 + harness-cp/CLAUDE.md WorkflowDriver row + harness-runtime/CLAUDE.md driver-axis + StepExecutionContext / StepDispatcher cite paths | preserves the later (v1.10) authoring site (and the larger forward-design-substrate frame); reduces cite churn at recently-published artifacts | rewrites the pre-existing canonical (v1.6) authoring site — historical-cite hygiene cost is higher; violates "first author wins" heuristic |
| **C — In-place disambiguation via §25a / §25b sub-IDs (and C-CP-25a / C-CP-25b)** | §25 + C-CP-25 split into §25a (WorkflowDriver) + §25b (ValidatorFramework); cite-sites updated mechanically | ~67 bare-§25 + ~119 bare-C-CP-25 cites — but mostly resolves via search-and-replace per-meaning grouping | preserves both authoring sites' first-author rights; signals the historical collision in the spec structure | introduces non-standard sub-letter IDs ("§25a" — no precedent in workspace); harder to grep cleanly without per-meaning case work; arguably more cosmetic than structural |
| **D — Defer; classify as Class 3 documentation drift; ride future spec touch** | No spec amendment; CP plan v2.18 §0(i) note preserved; future spec touch surfaces the drift | 0 immediate cite changes | minimal effort; preserves session focus on other priorities | leaves ambiguous cite surface in place; future adversarial reviews must continue to disambiguate by context; structurally a punt |

**Note on Reading A vs B size asymmetry.** The 19 vs 37 split reflects file-hits, not commits. Reading A retags the smaller surface but touches *recently-published* artifacts (within-session); Reading B retags the larger surface but touches *older / settled* artifacts. Effort cost is closer than the raw counts suggest.

## §5 Cross-axis cascade

ZERO downstream cross-axis cascade triggered by this filing. The collision is contained within CP spec authoring scope. Cite reconciliation at runtime spec / runtime plan / per-axis CLAUDE.md happens at the spec-writer apply arc (when one of the readings is operator-ratified). OD spec / AS spec / IS spec / CXA do not cite C-CP-25 / §25 directly.

## §6 Filing footer

| Field | Value |
|---|---|
| Filed | 2026-05-24 (checkpoint #2 traversal session) |
| Filing arc | Workspace HEAD `c0b9c87` (post pause/resume Sub-arc A doc reconciliation) |
| Filing skill | `phase-7-implementation` §6 halt-condition (upclassified from Class 3 documentation drift after empirical cite-inventory) |
| Authority chain | CP plan v2.18 §0(i) adjacent finding (predecessor session) + CP spec v1.12 §1 §25.2.1 amendment cross-reference (predecessor session) |
| Resolution arc | (1) systems-architect Mode 3 disambiguation recommendation against the 4 readings; (2) operator ratification via AskUserQuestion; (3) spec-writer apply pass + downstream cite cascade reconciliation; (4) adversarial-review at CP spec v1.13 (or whichever spec version the apply pass produces) |
| Status | OPEN at filing |
| Related memory | `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (this filing prevented unilateral spec hygiene amendment); `[[fork-meta-arch-cp-spec-renumbering-drift]]` (sibling — meta-arch-side cite renumbering drift, distinct surface but parallel shape) |

---

*End of fork doc. Routing: surface readings to operator at filing session close; defer spec-writer apply pass until operator selects a reading.*
