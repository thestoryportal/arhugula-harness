# Adversarial Review — R-FS-1 arc #5 (B1-spec-2): Runtime spec v1.47 → v1.48

## Summary

- **Artifact reviewed:** `design-substrate/Spec_Harness_Runtime_v1.md` (uncommitted delta, v1.47 → v1.48)
- **Scope:** Phase-7 pre-merge design-substrate amendment review (runtime-side materialization of the 5 non-`SINGLE_THREADED_LINEAR` topology driver strategies)
- **Date:** 2026-06-13
- **Reviewer:** harness-adversarial-reviewer (SKILL.md methodology adopted)
- **Finding count:** Class 1 (blocking): **0** · Class 2 (substantive): **0** · Class 3 (informational/doc-hygiene): **3**
- **VERDICT:** `APPROVE-WITH-CLASS-3`

### Class-taxonomy declaration (mandatory, per SKILL.md disambiguation box)

This review uses the **§2.7.6 Phase-7 fork-class scale** that the task's acceptance criteria specify, **NOT** the SKILL.md §4.1 review-severity scale. Under §2.7.6:

- **Class 1 = blocking** (halt-execution: spec contradiction / phantom cite / X-AL-3 silent-extension / cross-spec drift that breaks byte-exact resolution).
- **Class 2 = substantive but non-blocking** (in-execution operator decision).
- **Class 3 = informational / doc-hygiene** (non-blocking).

This is the scale the in-arc precedent uses (IS §5.4 line 497 self-labels its reciprocal-cross-ref item a "**Class 3 informational** doc-coordination item"). The SKILL.md §4.1 scale (where Class 3 = severe) is **deliberately not used here** — the task's verdict line ("BLOCKING ≥1 Class 1") binds the §2.7.6 reading.

---

## Verdict rationale

The amendment is a **faithful runtime-side materialization** of contracts already committed and P-cleared at CP spec v1.32 §25.10–§25.18 and IS spec v1.8 §5.4. It mints no new C-RT contract number, adds no new `ctx` field, widens no stage-5 post-condition, and restates no CP §25.x strategy mechanics. Every cite resolves byte-exact (enumerated below). The three Class-3 findings are doc-hygiene nits, none of which is a contract defect; all are non-blocking and most are out-of-scope-for-this-leg.

---

## Class 1 findings (blocking)

**None.** Every probe the task enumerated was executed and cleared. See "Findings considered and rejected" for the full audit trail.

---

## Class 2 findings (substantive, non-blocking)

**None.**

---

## Class 3 findings (informational / doc-hygiene)

### F3-01 — `failure_cause` invariant phrased as biconditional in the change-note vs one-way implication in the §9 body

- **Location:** Change-note table (diff hunk 1, the `§9 C-RT-09 RunResult` row): "`failure_cause is not None iff 'failed'`". Contrast the canonical §9 body invariant at `Spec_Harness_Runtime_v1.md:2460`: "`status == 'failed'` implies `failure_cause is not None`" (one-way), and the field table at `:2454`: "`None unless status == 'failed'`".
- **Defect:** The change-note states the invariant as a **biconditional** (`iff`) while the canonical contract body (`:2460`) states it as a **one-way implication**. The biconditional is *not factually wrong* — the field-table at `:2454` ("None unless `status=='failed'`") does establish the reverse direction too, so the existing contract is in fact bidirectional — but the change-note's `iff` is looser than the precise invariant the spec body commits, and could read as overstating what `:2460` says.
- **Why Class 3 (discriminator: drift only):** No contradiction, no broken cite, no semantic divergence. `'partial' → failure_cause stays None` is consistent under *both* readings (one-way and biconditional). This is pure phrasing-precision in a change-note (not a contract body). Resolution path: optionally align the change-note's phrasing to the §9 body's one-way implication, or leave as-is (both resolve true). Non-blocking; foldable into any future runtime touch.
- **Decision-claim label:** *decided*.

### F3-02 — `§14.5.3` body cites the per-role prompt seam as bare `C-CP-29 §29` where the change-note table and CP §25.14 use `§29.2`

- **Location:** `Spec_Harness_Runtime_v1.md:2995` (§14.5.3 "gap this closes"): "`PromptSelectionManifest.per_role_bindings` (C-CP-29 **§29**)". Contrast the change-note table row (diff hunk 1, §14.5.3 row): "per-role prompt (C-CP-29 **§29.2**)", and CP §25.14 (`Spec_Control_Plane_v1_32.md:99`) + CP §25.13 which use "§29.2".
- **Defect:** Inconsistent section granularity for the same seam within the same amendment — bare `§29` in one place, `§29.2` in two others. Bare `§29` is not *wrong* (§29.2 ⊂ §29; C-CP-29 §29 is the PromptSelectionManifest contract), but it is looser than the sibling cites and the CP source it mirrors.
- **Why Class 3 (discriminator: drift only):** Both cites resolve (C-CP-29 / §29 is the PromptSelectionManifest contract landed at CP v1.31; §29.2 is the per-role-bindings subsection). No phantom, no contradiction. Resolution path: tighten the `:2995` cite to `§29.2` for intra-amendment consistency, or leave (both resolve). Non-blocking.
- **Decision-claim label:** *decided*.

### F3-03 — IS §5.4's flagged reciprocal CP-side cross-reference is owed but not addressed here (correctly out of scope for this runtime leg)

- **Location:** Observation grounded at `Spec_Information_Substrate_v1.md:497`: "CP spec v1.32 §25.13 / §25.15 commits this per-branch value set but does not carry a reciprocal cross-reference to the sibling enums; that reciprocal CP-side note is flagged a **Class 3 informational** doc-coordination item (non-blocking; foldable into a future CP touch — e.g. **B1-spec-2** / B1-plan)."
- **Defect (informational only):** IS §5.4 names "B1-spec-2" as a candidate venue for the owed CP-side reciprocal cross-reference (CP §25.13/§25.15 → sibling disposition enums `SubAgentResultStatus` / `CascadeDecisionAtFanoutClose`). This arc **is** B1-spec-2 — but it edits the **runtime** spec, not CP. The reciprocal note belongs in CP §25.13/§25.15, which this runtime arc does not (and per X-AL-3 / posture discipline, should not) touch.
- **Why Class 3 and why NOT a defect of this amendment (discriminator: drift only):** The item is a **CP-side** doc-coordination nicety against an enum value-set that IS §5.4 itself certifies as "coherent and buildable." The "e.g. B1-spec-2" phrasing in IS §5.4 is illustrative, not binding — it does not obligate this *runtime* leg to edit *CP*. Surfacing it here is informational continuity, not a finding against the runtime amendment. Resolution path: fold the reciprocal cross-ref into a future CP touch (B1-plan / a CP §25 amendment); explicitly **NOT** owed by this runtime arc.
- **Decision-claim label:** *decided*.

---

## Findings considered and rejected (transparency — what was attacked and cleared)

Each entry below is an adversarial probe the task enumerated, executed against the primary source, and **cleared byte-exact**:

1. **Phantom-cite sweep — CP obligation numbers.** `CP §25.15.2 obl. 1/3/4` all resolve byte-exact at `Spec_Control_Plane_v1_32.md:119/121/122`: obl. 1 = "Dispatch-boundary-bounded" (→ `cancelled` = not-yet-dispatched); obl. 3 = "Audit-completeness (no silent landed effect)" (→ step-outcome at own entry); obl. 4 = "Discriminating `terminal_status`" with value-set `{cancelled, completed, timed_out}`. The amendment's claims about each obligation are accurate. **Cleared.**

2. **Phantom-cite sweep — IS §5.4 fidelity.** `IS §5.4` (`Spec_Information_Substrate_v1.md:469`) verified: `terminal_status` value-set is exactly `{cancelled, completed, timed_out}` (**no `failed`** — `:487`); append-only invariant present (`:42`, `:487`); dispatch-boundary-disposition-not-step-outcome semantic present verbatim (`:489`). The runtime write-cadence (per-step entries `terminal_status=None`; terminal disposition at a fresh terminal entry, append-only, never mutating a prior entry) **faithfully honors** all three. Notably IS §5.4 itself cites "CP §25.15.2 obligation 4/3" — the runtime amendment mirrors IS's own cites. **Cleared.**

3. **X-AL-3 anti-extension probe (the load-bearing "no new stage-5 binding" claim).** Read the §2 stage-5 post-condition (`:2040`) + binding table (`:2201`): `ctx.topology_dispatcher` (`TopologyDispatcher`, CP runtime-bound, stage 5), `ctx.step_dispatchers` (StepKindDispatcherRegistry, stage 5), and `ctx.state_ledger_writer`/`ledger_writer` are **all already stage-5 bindings**. The amendment adds **no** new `ctx` field, **no** new stage, **no** new binding, **no** new runtime invocation surface (rides the existing C-RT-08 `execute_workflow`). The §2 stage-5 post-condition is genuinely not widened. **This is a faithful materialization of committed primitives, NOT a silent design extension. Cleared.**

4. **`failure_cause` invariant consistency probe.** Existing invariant (`:2460`) is the one-way implication `'failed' ⟹ failure_cause is not None`; field-table (`:2454`) says "None unless `status=='failed'`". `'partial' → failure_cause stays None` is consistent with both. No contradiction with the existing invariant. (The change-note's looser `iff` phrasing is noted as F3-01, not a contradiction.) **Cleared.**

5. **Exit-code consistency probe (`'partial' → 1`).** `§14.18.2` (`:396`) **already** lists `RunResult.status in {FAILED, PARTIAL, DRAINED} → 1` ("strict — PARTIAL maps to 1"). The CLI mirror `_CP_STATUS_TO_EXIT_CODE` at `harness-runtime/src/harness_runtime/cli/app.py:225` **already** maps `"partial": EXIT_WORKFLOW_FAIL`. The amendment's "no exit-map edit" claim is **byte-exact true**. **Cleared.**

6. **Code ground-truth — `_CP_TO_RT_STATUS`.** `harness-runtime/src/harness_runtime/api.py:872` currently maps `_CpRunStatus.PARTIAL: "failed"` (defensive placeholder, comment at `:869-871`); the runtime Literal at `:862` is `["completed", "drained", "failed", "paused"]` (no `"partial"` yet). The amendment correctly describes the current state and correctly defers the flip to B1-impl-N (design-substrate-only arc). **Cleared.**

7. **Code ground-truth — `_MVP_DEFAULT_AGENT_ROLE`.** `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:281` binds `_MVP_DEFAULT_AGENT_ROLE = AgentRole("default")`, used at `:490`. The amendment's "discarded at dispatch" gap description is accurate; the role-read flip is correctly deferred to B1-impl-N. **Cleared.**

8. **Minted-vs-extended probe.** No new C-RT contract number is introduced. The three sites extend C-RT-09 §9 (status Literal widen), C-RT-02 §2 (new §2.2 subsection), and C-RT-15 §14.5 (new §14.5.3 subsection) — exactly as the change-note claims and exactly mirroring how v1.45 added `'paused'` and v1.47 added §2.1. CP §25.18 (`:168`) independently authorizes this exact runtime extension shape. **Cleared.**

9. **Cross-spec-prose-drift probe (the workspace's #1 defect class).** §2.2 and §14.5.3 **cite** CP §25.10–§25.16 strategy mechanics; they do **not** restate, duplicate, or contradict them. The five strategies' control-flow semantics live only in CP §25.11; the runtime sections author only the composition layer (materialization site, buffered-drain, write-cadence, role-read). No strategy mechanic is copied into the runtime spec. **Cleared.**

10. **PRESERVED-VERBATIM integrity.** `git diff` shows exactly 5 hunks: (1) title + new change-note block; (2) §2.2 insert before §3; (3) status Literal widen at `:2448`; (4) §9 invariant line at `:2459`; (5) §14.5.3 insert before §14.6. `git diff --stat` = 67 insertions / 3 deletions (the 3 deletions = the title line, the status Literal line, and the §9 invariant line, each a 1-line modify). **No stray edit outside the 3 claimed sites + title + change-note. C-RT-08 §8 `run()` untouched. Cleared.**

11. **ADR-cite resolution.** `ADR-F3 v1.1 §Decision (iv)` resolves byte-exact (`ADR-F3.md:23`: "(iv) observable lifecycle exposing workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired/released, and resumption events") — the amendment's "same closed-at-8 lifecycle event surface, no new event class" is faithful. `ADR-D4 v1.1 §1.2` (six-pattern topology taxonomy) resolves (`ADR-D4.md:1`, mirrors CP §25.10's own ADR-D4 §1.2 cite at `:30`). `ADR-F2 v1.2 §Consequences` resolves (`ADR-F2.md:6` = v1.2; §Consequences at `:38` carries the worktree-isolation `:48` + single-threaded-write / concurrent-write-coordination `:55/:68` language). **Cleared.**

12. **Runtime-internal + sibling-baseline cite resolution.** `CP §25.2.1 Path A` resolves byte-exact (`Spec_Control_Plane_v1_6.md:274`: "§25.2.1 StepDispatcher Protocol + StepExecutionContext (v1.6 amendment per operator-ratified **Path A**)" — the section title literally names Path A). `IS §6.3` resolves (`Spec_Information_Substrate_v1.md:543`: "§6.3 Chain construction at write-time"). `CP §25.18` B1-spec-2 enumeration (`:159-169`), `§25.12` D1/D1.b (`:75`), `§25.13` Route-Y seam (`:87`), `§25.14` role seam (`:95`), `§25.15.1` cascade_policy table with `PARTIAL`+`degraded=true` (`:111`) all resolve. The sibling-baseline cites mirrored from CP §25.x (`C-CP-05 §5.1 closed-at-8`, `C-CP-01 §1.3`, `C-CP-29 §29/§29.2`, `C-IS-09 §9.1`) are the **identical cites CP §25.x itself makes** (already P-cleared at CP v1.32) — faithful mirror-by-transitivity; C-CP-05/C-CP-01 confirmed as contracts in CP v1.2 baseline, C-CP-29 per_role_bindings in CP v1.31, C-IS-09 worktree-isolation in IS spec. **Cleared.**

---

## Disposition

**APPROVE-WITH-CLASS-3.** Zero blocking (Class 1) findings; zero substantive (Class 2) findings; three Class-3 doc-hygiene observations (F3-01 change-note `iff`-vs-implication phrasing; F3-02 bare `§29`-vs-`§29.2` granularity; F3-03 the CP-side reciprocal cross-ref, which is out of scope for this runtime leg). None blocks merge.

The amendment satisfies its own stated discipline: it materializes — without minting — the runtime leg of contracts already committed at CP §25.10–§25.18 and IS §5.4; it cites rather than restates CP strategy mechanics (resisting the cross-spec-prose-drift defect class); it adds no new primitive, no new `ctx` field, no new stage-5 binding (X-AL-3 clears); and every cite resolves byte-exact. This is a faithful, surgical, scope-disciplined design-substrate delta.

**Recommended action:** merge. The three Class-3 nits may be folded into this arc's PR opportunistically (F3-01/F3-02 are one-line tightenings in this same file) or deferred; F3-03 is explicitly a future CP-side touch, not this arc's.
