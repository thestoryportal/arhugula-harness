# Class 1 Fork — CP spec §25 / C-CP-25 contract-ID collision

**Filed:** 2026-05-24 during checkpoint #2 traversal (`§25-renumbering drift CP spec hygiene`) — Phase 7 sub-phase 7b at workspace HEAD `c0b9c87` (post pause/resume Sub-arc A doc reconciliation arc).

**Status:** ✅ FULLY-CLOSED 2026-05-24 across two-arc 7-commit total (status-line refreshed 2026-05-27) — arc 1 ratified + applied Reading A at CP spec v1.13 (`baeb595`/`50bb8b9`/`01d11c8`); arc 2 cascade-absorbed across runtime spec v1.18→v1.19 + CP plan v2.18→v2.19 + runtime plan v2.17→v2.18 + adjacent fork doc retag + workspace `CLAUDE.md` row bumps (`8f75589`/`8cd2aba`/`3864f4e` + closure bundle). Body §9 explicitly declares "**OPEN cite-cascade tracker → FULLY-CLOSED. ... The fork is now FULLY-RESOLVED + FULLY-APPLIED + CASCADE-CLOSED.**" Top **Status:** field stale at original OPEN-as-routing-target framing through both arcs. Species 3 (resolved-but-carry-stale-inherited) per workflow v1.9 §7.4.7.2. The trailing "Reading B full validator-composer arc remains OPEN at §3.2" clause is a **cross-reference to `[[fork-validator-composer-arc-stage-4-absence]]` §3.2** (separate scope, never gated on this fork's closure) — that arc was **APPLIED at runtime spec v1.22 on 2026-05-24** (commit `918f94a`); the `remains OPEN` framing was itself a species-3 stale cross-reference, refreshed at the 2026-06-01 fork-doc Status audit.

_Original filing footer:_ OPEN (routing target: systems-architect Mode 3 disambiguation recommendation → operator ratification → spec-writer apply pass).

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

## §7 Systems-architect Mode 3 recommendation (2026-05-24)

**Skill activation.** `systems-architect` Mode 3 (tension-resolution) per skill §4A. Filed at session HEAD `baeb595`. **Recommendation, not decision.** Operator holds decision authority per skill §4A.4.

### §7.1 Tension restated (per skill §4A.2 step 1)

Two contracts share the same `§25` section number and the same `C-CP-25` contract ID at CP spec authoring substrate. Verbatim quotes:

> `Spec_Control_Plane_v1_6.md:185` — `## §25 C-CP-25 — Workflow execution driver (v1.4 amendment — new contract scoped to SINGLE_THREADED_LINEAR topology + pure-pattern-no-engine / save-point-checkpoint engine classes)`

> `Spec_Control_Plane_v1_10.md:106` — `## §25 (NEW) C-CP-25 — ValidatorFramework`

Each contract has substantive body content + downstream cite traffic per §1 + §2.

### §7.2 Authority-chain placement (skill §4A.2 step 2)

Per workspace `CLAUDE.md` §1.3 + skill §2.7 anti-pattern "Authority-chain inversion": **the earlier artifact is canonical for the later**. Apply the chain `ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1`.

| Contract | Anchor ADR(s) | First-author event | First-author date |
|---|---|---|---|
| **WorkflowDriver (v1.6-meaning §25 / C-CP-25)** | ADR-F3 v1.1 §Decision (iv) (workflow lifecycle event surface — F-level foundational) + ADR-D5 v1.4 (drain protocol composition) | CP spec v1.6 §25 introduction at v1.4 → v1.5 → v1.6 chain | **2026-05-20** (per CP spec v1.6 line 28 Revision history) |
| **ValidatorFramework (v1.10-meaning §25 / C-CP-25)** | ADR-D3 v1.2 (validation contract — D-level derivative) + ADR-D5 v1.4 (escalation discipline) + ADR-D6 v1.2 (validator observability namespace) | CP spec v1.10 §25 (NEW) introduction at v1.10 | **2026-05-21** (per CP spec v1.10 line 5 change-note) |

**First-author primacy:** WorkflowDriver authored 2026-05-20; ValidatorFramework authored 2026-05-21. WorkflowDriver claimed `§25 / C-CP-25` first.

**The decisive empirical finding** at `Spec_Control_Plane_v1_10.md` line 5 + line 44:

> "All v1.9 content (including §13.5.1 NEW NOTE 4 + NOTE 5 + NOTE 6 from path-(i) absorption) preserved verbatim. No signature change to any v1.9 contract; no field-projection table change."
>
> "**Sections preserved verbatim from v1.9.** All v1.9 content outside the four amendment sites preserved unchanged. C-CP-01 through C-CP-24 (v1.9 §1 through §24) preserved verbatim."

The v1.10 change-note explicitly preserves v1.9 content verbatim — which includes the v1.6 §25 / C-CP-25 WorkflowDriver content carried through v1.7/v1.8/v1.9 preserved-verbatim chain. **v1.10 simultaneously preserves §25 (per the change-note) and overwrites §25 (per the §"§25 (NEW)" section header)**. This is an internal contradiction within v1.10's own authoring text.

**`Spec_Control_Plane_v1_10.md` line 57 "Adjacent defects surfaced (not patched per FM-2 no-extension discipline)" reads:**

> "**None** — apply pass is fidelity-pure transcription of ratified draft content."

The fidelity-pure claim is empirically violated by the section-number collision with the v1.9-preserved-verbatim v1.6 §25.

### §7.3 Five-axis decomposition (skill §2.1)

| Axis | WorkflowDriver | ValidatorFramework |
|---|---|---|
| Control plane | per-step iteration discipline + drain protocol + lifecycle event emission (workflow-execution iteration scope) | per-step deterministic validation gate (validation-fired-between-dispatch-and-acceptance scope) |
| Information substrate | composes with C-CP-08 §8.2 idempotency-key join + state-ledger append per C-IS-05 | composes with `validator.*` 11-attr OD canonical schema at C-OD-29 |
| Action surface | n/a (workflow-execution layer above tool dispatch) | composes with tool dispatch per runtime spec v1.18 §14.9 |
| Operational discipline | lifecycle event emission boundaries against §5.1 8-class taxonomy; 4 driver-owned + 1 runtime-owned failure modes | `validator.evaluate` / `validator.fail` / `validator.revalidation` / `validator.escalation` span emission; 5-class `ValidatorFailClass` taxonomy |
| Deployment surface | scoped to `SINGLE_THREADED_LINEAR` topology + `pure-pattern-no-engine` / `save-point-checkpoint` engines | runs every step across all topologies (opt-out via no-op validator per Decision 2.D3) |

Distinct sub-roles within CP-axis. **The tension is naming, not architectural.** Both contracts have coherent independent design substrate and clear axis-decomposition.

### §7.4 Probabilistic-deterministic boundary (skill §2.2)

Both contracts live on the **deterministic side** (outer harness). No boundary issue.

### §7.5 F/D/I classification (skill §2.3)

| Contract | Class | Anchor |
|---|---|---|
| WorkflowDriver | **F-derived** (anchored on F-ADR-F3 v1.1 §Decision (iv) workflow lifecycle event surface foundational commitment) | F3 foundational |
| ValidatorFramework | **D-level** (anchored on D-ADR-D3 v1.2 validation contract derivative) | D3 derivative |

Both contracts are below the foundational ADR layer; both materialize derivative commitments. Neither is foundational at the spec layer — but WorkflowDriver's anchor is one rung closer to the F-tier (F3 vs D3). Marginal asymmetry favors WorkflowDriver retaining canonical-ID primacy.

### §7.6 Reading evaluation

**Reading A — Rename v1.10 NEW (ValidatorFramework) → C-CP-28 / §28.**
- **Authority-chain support: STRONG.** Conforms the late-authoring offender to the early-authoring canonical. Restores fidelity-pure status to v1.10's own preservation claim ("All v1.9 content preserved verbatim"). Preserves WorkflowDriver's first-author primacy + F-derivative anchor proximity.
- **Cite-cascade size:** ~19 file-hits + targeted cite-replace at v1.10 spec + runtime spec v1.18 §14.13 + runtime plan v2.17 L9-decies cluster + CP plan v2.18 §10-CP-A units + harness-cp/CLAUDE.md ValidatorFramework row + ValidatorFramework forks (`[[fork-validator-composer-arc-stage-4-absence]]`).
- **Risk:** rewrites cite-paths at within-session recently-published artifacts (runtime spec v1.18 + runtime plan v2.17 both freshly committed). Mitigated because all rewrites are mechanical search/replace of "C-CP-25" / "§25" → "C-CP-28" / "§28" in ValidatorFramework-context lines; no signature change; no semantics change. The L9-decies impl artifacts (U-RT-83/84/85) do not encode the contract ID at runtime — they import `ValidatorFramework` by class name from `harness_cp.validator_framework_types`. Citation-only fix.
- **Downstream contract numbering:** CP spec currently uses C-CP-25 (collision) + C-CP-26 (PauseResumeProtocol) + C-CP-27 (PerServerTrustEvaluator). Reading A's new ID C-CP-28 fits naturally after the v1.10 sequence.

**Reading B — Rename v1.6 (WorkflowDriver) → C-CP-28 / §28.**
- **Authority-chain support: WEAK.** Inverts first-author primacy. Punishes the early-authoring canonical. Conflicts with workspace skill §2.7 "Authority-chain inversion" anti-pattern (in spirit — here applied to within-spec temporal authoring order, not between-artifact chain order, but the structural principle is the same).
- **Cite-cascade size:** ~37 file-hits at older artifacts (v1.6 spec self-cites; CP plan v2.18 U-CP-56 + U-CP-57; harness-runtime/CLAUDE.md driver-axis; StepExecutionContext / StepDispatcher cite paths).
- **Risk:** rewrites the pre-existing canonical authoring site. Historical-cite hygiene cost. v1.6 was correct at authoring time; conforming the correct artifact to absorb a later-authored defect is a fidelity inversion.

**Reading C — In-place §25a / §25b + C-CP-25a / C-CP-25b sub-IDs.**
- **Authority-chain support: WEAK.** Introduces non-standard sub-letter ID convention with no precedent across the workspace. C-CP-01 through C-CP-27 use integer-only IDs. C-IS / C-AS / C-OD / C-RT similarly integer-only. Sub-letter IDs would set a precedent and inconsistency cost.
- **Cite-cascade size:** all 67 + 119 bare cites reshaped per-meaning. Largest cascade.
- **Risk:** preserves historical evidence of the collision in the spec structure (arguably a positive for forensic readability) but at the cost of non-standard IDs + largest mechanical cascade + ongoing reader-cognition cost on every future cite.

**Reading D — Defer; classify as Class 3 documentation drift; ride future spec touch.**
- **Authority-chain support: NONE.** Leaves an active fidelity defect in place. Inconsistent with §3 Class 1 upclassification rationale.
- **Cite-cascade size:** 0 immediate, ∞ deferred.
- **Risk:** future adversarial reviews must continue disambiguating by context. ADD / PRD revisions propagate the ambiguity. Any new contract authored after v1.12 inherits the broken ID-allocation discipline.

### §7.7 Recommendation

**Reading A** — Rename v1.10 NEW (ValidatorFramework) → C-CP-28 / §28. [HIGH]

Three convergent chain anchors:

1. **First-author primacy** (workspace `CLAUDE.md` §1.3 authority-chain ordering applied within-spec to temporal authoring order): WorkflowDriver first-authored 2026-05-20 at v1.6; ValidatorFramework second-authored 2026-05-21 at v1.10.

2. **v1.10's own preservation claim** (`Spec_Control_Plane_v1_10.md:5,44`): explicitly preserves v1.9 content verbatim → includes v1.6 §25 / C-CP-25 → contradicts v1.10's de-facto override. Restoring fidelity-pure transcription requires renaming v1.10 NEW, not v1.6.

3. **F-derivative anchor proximity** (skill §2.3 F/D/I classification): WorkflowDriver anchors on ADR-F3 §Decision (iv) (F-level); ValidatorFramework anchors on ADR-D3 v1.2 (D-level). Both are sub-foundational at spec layer; marginal anchor-proximity asymmetry favors WorkflowDriver retaining canonical-ID primacy.

### §7.8 Tiebreaker check (skill §4A.2 step 5)

**Tiebreaker fact:** confirm `Spec_Control_Plane_v1_10.md` line 5 + line 44 "All v1.9 content preserved verbatim" preservation claim was made by the spec-writer apply pass at Phase A.2 ratified-drafts ingestion (2026-05-21) without an explicit "supersede v1.6 §25 / C-CP-25 WorkflowDriver" deletion clause.

**Empirical verification at HEAD `baeb595`:**
```bash
grep -n "supersede\|deprecate\|replace.*§25\|deletes\|removes.*WorkflowDriver" design-substrate/Spec_Control_Plane_v1_10.md
```
Result: zero hits. v1.10 never declared supersession of v1.6 §25 / C-CP-25. The collision was an authoring oversight, not a deliberate supersession.

**Tiebreaker passes.** Recommendation determinacy criterion MET.

### §7.9 Fork classification confirmation (skill §4A.2 step 6)

**Class 1 (halt-execution)** per `Project_Workflow_v1_8.md` §2.7.6. Filing classification at §3 reconfirmed. Implies: any new CP spec authoring + downstream cite resolution at adversarial-review surface should halt until the apply pass lands.

**Operative caveat:** the halt scope is narrow — bare-cite resolution at active artifacts must disambiguate by context (recommended interim discipline: use "C-CP-25 §25 ValidatorFramework" or "C-CP-25 §25 WorkflowDriver" double-qualifier at any new bare-cite site). Existing in-flight work is not blocked by the filing.

### §7.10 Downstream artifacts to absorb the resolution (skill §4A.2 step 4)

If Reading A is operator-ratified:

| Artifact | Amendment scope |
|---|---|
| `Spec_Control_Plane_v1_10.md` | Rename §25 → §28; rename C-CP-25 → C-CP-28 across the ValidatorFramework body; amend v1.10 change-note adjacent-defects section to record the rename (v1.10 → v1.10.1 micro-bump or v1.13 amendment with §"NEW §28" + "RETIRED §25-ValidatorFramework" sub-clause) |
| `Spec_Control_Plane_v1_11.md` + `v1_12.md` | If they reference §25/C-CP-25 in ValidatorFramework context, retag. (Empirically: v1.11 referenced §25 ValidatorFramework preservation per change-note; v1.12 referenced §25.2.1 WorkflowDriver per its own scope — but the WorkflowDriver §25.2.1 cite is correct and is preserved verbatim.) |
| `Spec_Harness_Runtime_v1.md` v1.18 | §14.13 + §14.13.1 – §14.13.6 references "CP spec v1.11 §25" with ValidatorFramework meaning → retag to "CP spec v1.11 §28" |
| `Implementation_Plan_Control_Plane_v2_18.md` | U-CP-58/59/60/61 + cluster 10-CP-A coverage matrix retag (§25 → §28 in ValidatorFramework context); U-CP-56 + U-CP-57 (WorkflowDriver) preserved verbatim |
| `Implementation_Plan_Harness_Runtime_v2_17.md` | L9-decies cluster — 13+ cite sites "CP spec v1.11 §25" in ValidatorFramework context → "CP spec v1.11 §28" |
| `harness-cp/CLAUDE.md` | §1.3 ValidatorFramework scope row + §4.1 H_T-CP-21 substitution row + per-axis-CLAUDE bookkeeping |
| `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` | §1.1 grep-verified inventory cite-paths retag |
| `Cross_Axis_Composition_Document_v2_8.md` (or successor) | If references CP §25 ValidatorFramework → retag |
| Workspace `CLAUDE.md` | §2.3 CP row note (if it cites §25 ValidatorFramework directly) — empirical: it does not, references C-CP-25 in CP spec row at v1.10 + v1.11 + v1.12 entries; those bare cites benefit from re-qualifying |
| Adversarial Review docs | Adversarial_Review_06_Runtime_v2_14.md + Adversarial_Review_07 (cleared); any cite of §25 ValidatorFramework retag at next adversarial review touch |

**Spec authoring mechanic.** Per the delta-only spec-file preservation chain, the rename is most cleanly applied at a new v1.13 spec authoring (introducing "§28 (NEW after rename)" + change-note "RENAME §25 (NEW v1.10) → §28; per `[[fork-cp-spec-section-25-contract-id-collision]]` Reading A apply pass"). v1.10 stays preserved-verbatim for historical fidelity; the rename is recorded as an additive amendment at v1.13. Alternative: in-place v1.10.1 micro-bump that rewrites the v1.10 file body; less clean per workspace delta-only-spec convention.

### §7.11 Operator decides (skill §4A.4)

Operator holds decision authority per workspace `CLAUDE.md` §1.3 + skill §4A.4. This recommendation is `Status: PROPOSING` per skill §4A.3. Routing target: AskUserQuestion at session close → ratification → `spec-writer` apply pass + downstream cite cascade reconciliation per §7.10 → adversarial review at the resulting CP spec version.

**Recommendation summary line:**

> Reading A (rename v1.10 NEW ValidatorFramework → C-CP-28 / §28) is recommended at [HIGH] confidence. Tiebreaker passes. Three convergent chain anchors per §7.7. Operator decides.

### §7.12 Filing footer (architect recommendation)

| Field | Value |
|---|---|
| Skill | `systems-architect` Mode 3 (tension-resolution) |
| Activation | Operator request via AskUserQuestion 2026-05-24 ("Open systems-architect Mode 3 recommendation arc now") |
| Recommendation status | PROPOSING → operator-ratification gate |
| Recommended reading | A — rename v1.10 NEW → C-CP-28 / §28 [HIGH] |
| Tiebreaker | PASSES (v1.10 declared no supersession of v1.6 §25 / C-CP-25) |
| Fork class | Class 1 (halt-execution; narrow scope per §7.9 caveat) |
| Apply-pass routing | `spec-writer` (CP spec v1.10 → v1.13 amendment + downstream cite cascade) |
| Cross-axis cascade | ZERO (collision contained within CP spec authoring; OD / AS / IS / CXA unaffected at semantics layer; runtime spec / runtime plan cite-only retag) |

---

## §8 Reading A ratification + apply-pass footer (2026-05-24)

**Trigger.** Operator ratification via AskUserQuestion 2026-05-24 — operator selected "Ratify Reading A; open spec-writer apply pass now" at session HEAD `50bb8b9` (post architect Mode 3 recommendation commit). Ratification followed Mode 3 §7 recommendation at [HIGH] confidence on three convergent chain anchors + tiebreaker pass per §7.8.

**Apply-pass artifact landed this session.**

| Artifact | Disposition |
|---|---|
| `design-substrate/Spec_Control_Plane_v1_13.md` | NEW delta file authored by `spec-writer` per skill §6 workflow. v1.13 amends the v1.10 NEW §25 / C-CP-25 ValidatorFramework body to §28 / C-CP-28; v1.12 substantive content preserved verbatim outside the rename. ZERO contract change; ZERO signature change; ZERO acceptance-criterion change; ZERO behavior change; fidelity-pure citation-correction patch. |
| Workspace `CLAUDE.md` §2.3 CP spec row | Version bump v1.12 → v1.13 (co-published this session per v1.13 change-note Downstream absorption §(a)). |

**Apply-pass artifacts owed (next-arc cascade).** Per v1.13 change-note Downstream absorption §(b)–(i):

| Artifact | Routing target |
|---|---|
| `Spec_Harness_Runtime_v1.md` v1.18 cite retag | `spec-writer` follow-on arc — runtime spec is single-file (not delta-chain); cite retag absorbed at v1.18 → v1.19 micro-bump or in-place v1.18 amendment. ~6 cite sites. |
| `Implementation_Plan_Control_Plane_v2_18.md` → v2.19 | `implementation-planner` revision-pass — cluster 10-CP-A units (U-CP-58/59/60/61) Implements/Files/Signatures cite retag C-CP-25 → C-CP-28; U-CP-56 (WorkflowDriver-lineage) preserved verbatim. |
| `Implementation_Plan_Harness_Runtime_v2_17.md` → v2.18 | `implementation-planner` revision-pass — L9-decies cluster 13+ cite sites "CP spec v1.11 §25" → "CP spec v1.13 §28". |
| `harness-cp/CLAUDE.md` cite retag | Per-axis bookkeeping arc — §1.3 ValidatorFramework scope row + §4.1 H_T-CP-21 substitution row. |
| `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` cite retag | Adjacent fork doc bookkeeping at next-touch arc. |
| `Cross_Axis_Composition_Document_v2_8.md` (or successor) | CXA next-touch arc — if §2.3.7 composer-arc absorption row references C-CP-25 ValidatorFramework, retag to C-CP-28. |
| Adversarial Review 06 + 07 cite drift (bookkeeping-only; cleared pre-v1.13) | Cite retag at next adversarial review touch OR at implementation-planner cite-cascade arc. |

**Fork class disposition.** Class 1 (halt-execution) per §7.9 — narrow-scope halt: new CP spec authoring + adversarial-review surface cite-resolution. Existing in-flight work was not blocked. Class 1 halt-status LIFTED at this v1.13 apply pass: new CP spec authoring may proceed against the disambiguated §25 (WorkflowDriver) / §28 (ValidatorFramework) ID space; cite-cascade across runtime spec + plans + workspace bookkeeping is owed at follow-on arcs but does not block other Phase-7 work.

**Status post-§8.** OPEN → ARCHITECT-RECOMMENDED → **READING-A-RATIFIED-AND-APPLIED-AT-CP-SPEC** → cascade absorption owed at runtime spec / plan files / workspace bookkeeping (next-arc routing). The fork remains OPEN as a cite-cascade tracker; FULLY-CLOSED at all §7.10 + §8 cascade artifacts absorbing the rename.

**Single-session arc.** 3 commits in this session:
1. `baeb595` — Class 1 fork filing
2. `50bb8b9` — systems-architect Mode 3 §7 recommendation
3. (this commit) — spec-writer apply pass: CP spec v1.13 NEW + workspace CLAUDE.md row bump + §8 ratification footer

**Pattern reinforced.** Fidelity-pure rename-the-offender resolution mirrors the meta-arch-side sibling fork `.harness/class_1_fork_meta_arch_cp_spec_renumbering_drift.md` Reading A pattern at Meta-Arch v1.5 `b2cf37b`. Both arcs: when a renumbering collision surfaces, fidelity-pure resolution renames the offender (later-authored), not the canonical (first-authored).

---

## §9 Cite-cascade arc closure (2026-05-24, follow-on session)

**Trigger.** Operator request "start the cite-cascade arc" at follow-on session opening (checkpoint resume at HEAD `01d11c8`). Session goal: complete the §7.10 + §8 cascade absorption owed across runtime spec / plan files / workspace bookkeeping / adjacent fork doc, lifting the OPEN-as-cite-cascade-tracker status.

**Cite-cascade absorption arc closed across 4 commits this follow-on session** (artifact #4 adjacent-fork-doc retag bundled with artifact #5 cascade-closure commit; 5 distinct artifacts absorbed across 4 commits).

| # | Artifact | Disposition |
|---|---|---|
| 1 | `Spec_Harness_Runtime_v1.md` v1.18 → **v1.19** (in-place; single-file spec, not delta-chain) | 17 ValidatorFramework-context cite sites retagged §25.x → §28.x / C-CP-25 → C-CP-28 across §3 + §4 + §14.13 + §14.13.1 + §14.13.2 + §14.13.3 + §14.13.6 + 2 historical change-notes (v1.14→v1.15 path β fork + v1.16→v1.17 §(b)). v1.6-lineage WorkflowDriver cites (§25.2.1 StepExecutionContext + §25.3.3.4 step-dispatch boundary + §25.3.3 step-body-opaque) preserved verbatim per advisor-confirmed discrimination rule. Commit `8f75589`. |
| 2 | `Implementation_Plan_Control_Plane_v2_18.md` → **v2.19** (NEW delta file; delta-only convention) | §0(i) adjacent-defect note refreshed ("non-blocking; routing to future arc" → RESOLVED at CP spec v1.13). NEW §1 cluster 10-CP-A canonical-reading amendment table for U-CP-58/59/60/61 (delta-only preservation: v2.15/v2.16 plan files containing unit bodies NOT edited — canonical reading at v2.19 retags per §1 table). U-CP-56 (v1.6-lineage WorkflowDriver at §25.2.1) preserved verbatim. Commit `8cd2aba`. |
| 3 | `Implementation_Plan_Harness_Runtime_v2_17.md` → **v2.18** (NEW delta file; delta-only convention) | NEW §1 L9-decies cluster canonical-reading amendment with 23-site per-line retag enumeration table (U-RT-83 + U-RT-84 + U-RT-85 unit bodies + Implements/Files/Signatures/Depends-on/AC/coverage-matrix/cite-precision-audit/spec-carrier-inventory/adversarial-review-checkpoint-matrix sites). Delta-only preservation: v2.17 plan file NOT edited — canonical reading retags per §1. Cluster-boundary edges to U-CP-58/59/60/61 unchanged at edge-declaration level. Commit `3864f4e`. |
| 4 | `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` (in-place edit) | Lines 127 + 152 ValidatorFramework-context cite retag: line 127 `C-CP-25/26/27` enumeration → `C-CP-28 (ValidatorFramework, renamed from v1.10 C-CP-25 at v1.13) / C-CP-26 / C-CP-27`; line 152 `C-CP-25 ValidatorFramework Protocol` → `C-CP-28 ValidatorFramework Protocol`. Bundled with §5 commit. |
| 5 | Workspace `CLAUDE.md` §2.3 CP spec row + §2.3 runtime spec row + §2.4 CP plan row + §2.4 runtime plan row + fork doc §9 closure footer (this) + MEMORY.md fork-cp-spec-section-25 index entry | Row version bumps + change-note appendings: CP spec v1.13 row trailing sentence amended to record cascade APPLIED status; runtime spec row bumped v1.18 → v1.19; CP plan row bumped v2.18 → v2.19; runtime plan row bumped v2.17 → v2.18. |

**Empirical inventory confirmed at session open.** Per workspace `CLAUDE.md` §4.3 fidelity discipline, follow-on session ran empirical grep across all §7.10 routing targets:
- `harness-cp/CLAUDE.md` — empirical grep ZERO §25/C-CP-25 spec-section cite-shape hits (only `ValidatorFramework` code-symbol references at retirement-status rows, NOT spec section cites). NO retag owed at harness-cp/CLAUDE.md.
- `Cross_Axis_Composition_Document_v2_9.md` — empirical grep ZERO §25/C-CP-25/ValidatorFramework spec-section cite hits. NO retag owed at CXA v2.9.
- `Adversarial_Review_06` + `Adversarial_Review_07` cite drift — bookkeeping-only at next adversarial-review touch per §7.10 + §8 routing.

**Discrimination rule application.** Per advisor consultation at runtime spec retag arc opening (advisor confirmed: "v1.13 §1 explicitly enumerates §25.x → §28.x mapping byte-exact; cite-cascade against whatever v1.13 actually anchors"): each cite site contextually discriminated per surrounding prose:
- **WorkflowDriver context** (step-failure mapping / step-body-opaque / `try/except` boundary / step.kind routing / `StepExecutionContext` plumbing / `SUB_AGENT_DISPATCH` / `single-sub-agent` / `fan-out` / `topology expansion`) → preserved as `§25.x` / `C-CP-25 §25.x` per v1.6-lineage primacy
- **ValidatorFramework context** (validator hook / 5-class outcome routing / `ConcreteValidatorFramework.evaluate` / Protocol envelope / `ValidatorFailClass` enum / `ValidatorEvaluation` envelope / driver-hook True-arm / `workflow_driver.py:668` 5-class outcome routing) → retagged to `§28.x` / `C-CP-28 §28.x` per v1.13 §1 rename

**Status post-§9.** **OPEN cite-cascade tracker → FULLY-CLOSED.** All §7.10 + §8 routing target artifacts absorbed the rename per applicable convention (in-place for single-file spec / NEW delta for delta-only plan-chain / in-place for adjacent fork doc / canonical-reading-table for predecessor plan files preserved byte-exact). The fork is now FULLY-RESOLVED + FULLY-APPLIED + CASCADE-CLOSED. Reading B full validator-composer arc (cross-reference to `[[fork-validator-composer-arc-stage-4-absence]]` §3.2; separate scope, never gated on this fork's closure) was APPLIED at runtime spec v1.22 on 2026-05-24 (cross-ref refreshed at the 2026-06-01 fork-doc Status audit; the prior `remains OPEN` framing was a species-3 stale cross-reference).

**Adjacent defects preserved across cascade arc.**
(i) `§28` non-sequential numbering at CP spec v1.13 (preserved per fidelity-pure rename; NOT addressed at cascade).
(ii) Delta-only canonical-reading amendment pattern (preserved per established convention; interpretive layer surfaced at CP plan v2.19 §"Adjacent defects (ii)" + runtime plan v2.18).
(iii) Adversarial Review 06 + 07 cite drift (bookkeeping-only; cite retag at next adversarial-review touch).
(iv) Filing footer staleness at runtime spec (carry-forward from v1.13..v1.18; NOT patched per FM-2).

**Pattern catalogued.** Two-arc fork resolution: arc 1 (filing + ratification + apply at canonical artifact) + arc 2 (cite-cascade absorption across downstream artifacts). Cascade arc 2 benefits from fresh context window per FM-4 risk-aware scoping operator-deferred from arc 1. Cumulative session deliverable across both arcs: **7 commits total** (3 at arc 1 last session: `baeb595` → `50bb8b9` → `01d11c8`; 4 at this arc: `8f75589` → `8cd2aba` → `3864f4e` → (this) bundling adjacent-fork-doc retag + workspace CLAUDE.md row bumps + fork §9 closure footer + MEMORY.md index update).

---

*End of fork doc. Routing: FULLY-CLOSED at §9 cascade absorption. Reading B full validator-composer arc (cross-reference to `[[fork-validator-composer-arc-stage-4-absence]]` §3.2; separate scope, never gated on this fork's closure) was APPLIED at runtime spec v1.22 on 2026-05-24 (cross-ref refreshed at the 2026-06-01 fork-doc Status audit; the prior `remains OPEN` framing was a species-3 stale cross-reference).*
