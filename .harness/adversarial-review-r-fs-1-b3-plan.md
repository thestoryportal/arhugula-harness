# Adversarial Review — R-FS-1 B3-plan (arc #20) atomic-unit decomposition

## Summary

- **Artifact reviewed:** `design-substrate/Implementation_Plan_Control_Plane_v2_33.md` (+2 units U-CP-91/92, O-CP-3) + `design-substrate/Implementation_Plan_Harness_Runtime_v2_44.md` (+6 units U-RT-115..120) + `.harness/r-fs-1-b3-plan-decomposition.md` (decomposition summary + coverage matrix + DAG + §5 G2c finding).
- **Mode:** Phase-7 pre-implementation review (P6-CK-shaped; design-substrate PLAN amendment), pre-merge.
- **Date:** 2026-06-14 · **HEAD at review:** `a356929` (per the artifacts' own pin).
- **Class scale (TASK deliverable scale — stated explicitly to avoid the inverted-SKILL.md-scale misread):** **Class 1 = blocking · Class 2 = substantive (requires revising THIS plan before merge) · Class 3 = doc-hygiene (non-blocking).** NOTE: this is the *inverse* of the SKILL.md §4.1 review-severity scale (where Class 1 = minor). All Class labels below are on the TASK scale.
- **Finding count by class:** Class 1 (blocking): **0** · Class 2 (substantive): **0** · Class 3 (doc-hygiene): **1**.
- **Highest-severity finding:** F3-01 (U-CP-92 cross-ref AC under-scopes the `harness-runtime` docstring drift sites) — doc-hygiene, non-blocking.

## VERDICT: **APPROVE-WITH-CLASS-3**

The decomposition is correct, complete, zero-spec-extension, acyclic, delta-preserving, and the carried ACs all land. It is *cleaner than the design it decomposes* on the one substantive point (G2c): the plan correctly **corrects** the design §4.1 "pure-impl" mis-framing of the `per_tool_gate_level` producer rather than silently absorbing it, registering O-CP-3 and routing the impl-vs-fork classification to the skipped AS-leg gate (X-AL-3-clean). The single Class-3 finding (a docstring drift site outside U-CP-92's named cross-ref scope) is doc-hygiene and does not require revising the plan before merge — it can be folded into U-CP-92's reconciliation AC at impl or left to the B3-impl-2 executor.

---

## Per-claim findings (claims 1–9 per the review charter)

### Claim 1 — Coverage-matrix-complete — **VERIFIED, clean (no finding)**

Every cleared spec subsection + every design §8.2 gap maps to a unit OR an explicit disposition. Walked each mapping by direct read:

| Cleared spec / design gap | Plan disposition | Verified |
|---|---|---|
| runtime v1.49 **§3.8** (`HITLAutoApprovePolicy` + step-4c in-`max()` + AC-1/AC-2) | U-RT-116 (+ U-CP-91 carrier) | ✓ §3.8 read at runtime spec lines 2194-2235; AC-1/AC-2 land at U-RT-116 |
| runtime v1.50 **§14.8.9** (dispatch-on-mode + AC-1/2/3) | U-RT-119 (+ U-CP-92 vocab) | ✓ §14.8.9 read at lines 3766-3796; AC-1/AC-3 land at U-RT-119, AC-2 at U-CP-92 |
| design §8.2 **G1-blast** (`resolve_step_blast_radius`) | U-RT-115 | ✓ |
| design §8.2 **G2** (gate_level-once + thread to 4d) | U-RT-117 | ✓ |
| design §8.2 **G2c** (`per_tool_gate_level` producer) | **O-CP-3 REGISTERED** (not a unit; not pre-stamped fork; not authored as impl) | ✓ — see Claim 3 |
| design §8.2 **G3** (EDIT replace-not-merge) | U-RT-120 (sub-fork O-RT-3 conditional) | ✓ |
| design §8.2 **G4a** (degradation-mode attribute) | U-RT-118 | ✓ |
| design **G4b** (now §14.8.9-spec'd) | U-RT-119 | ✓ |
| F-B3-1 §3.2 `GateLevelInput` carrier-shape | U-CP-91 | ✓ |
| F-B3-2 vocab reconciliation + fail-open guard | U-CP-92 | ✓ |
| design §7 **G5** (HandoffContext summary) | OUT of scope (B3-impl-handoff) | ✓ — design §7 names it a distinct summarization-producer arc |
| **G2b** (palette `cross_trust_state=NONE`) | NO GAP (spec-correct, §14.8.2 line 3353) | ✓ |

No silent gap. The coverage matrices (CP §4.2, runtime §4.1a, decomposition §3) are mutually consistent.

### Claim 2 — ZERO spec extension — **VERIFIED, clean (no finding)**

Every unit transcribes signatures/types from the cleared specs + grounded code; no unit invents a new contract surface as if cleared.

- **U-CP-91** modifies the existing `GateLevelInput` (`gate_level_rule.py`, verified `frozen, extra="forbid"` at line 93) carrier-shape — explicitly a U-CP-43 plan-carrier concern per F-B3-1 §3.2 (NOT a C-CP-19 spec change). The unit even offers two reading-agnostic materializations (new optional field vs composer-synthesized lowered input), both no-new-contract. ✓
- **U-CP-92** reconciles the *existing* `TimeoutDegradationKind` enum to the cleared CP §21.8 + ADR-D5 §1.6 vocab-A — verified the target vocabulary is byte-cited from the cleared authorities, NO invented value. ✓
- **U-RT-115..120** all transcribe from §3.8 / §14.8.9 / §14.8.2 step-4c/4d/4f/4i + NOTE 6-ii. The one place a *new contract surface* WOULD be needed (G2c's `ToolContract.per_tool_gate_level` typed field) is correctly NOT authored as impl — it is flagged as O-CP-3 (Claim 3). ✓

### Claim 3 — G2c → O-CP-3 disposition — **VERIFIED CORRECT (sound; non-blocking; §2.7.6-Class-2 AS-leg routing note, NOT a reviewer defect)**

I re-grounded the load-bearing fact by direct read:

- **AS spec C-AS-03 §3.1** (lines 475-488): the typed `ToolContract` schema declares `name`, `description`, `input_schema`, `output_schema`, `minimum_tier`, `blast_radius_tier`, `required_secrets`, `...` — **NO `per_tool_gate_level` typed field.**
- **Landed `harness_as.tool_contract.ToolContract`** (lines 71-84): same seven fields, **no `per_tool_gate_level`.** Matches §3.1.
- `per_tool_gate_level` appears in the AS spec ONLY as (i) the C-AS-12 §12.1 `gate_level()` **formula axis** (line 1002, `# C4 contract: {auto, ask, deny}`) and (ii) the §3-frontmatter authoring token (line 1155). Confirmed.

So the design §4.1 "faithful carrier factor-out / pure-impl" framing is **partially falsified** — materializing a typed `ToolContract.per_tool_gate_level` field is the *missing-declaration-site* shape, whose impl-vs-fork classification is a ratification call, not the planner's. The plan's O-CP-3 disposition is the X-AL-3-clean call: (1) REGISTERS the owed AS-spec reconciliation (FULL-SPEC, nothing dropped); (2) does NOT pre-stamp "fork" (the inverse of the Codex-[P2] error the design already corrected); (3) does NOT author the carrier as cleared impl (the forbidden silent-absorption move); (4) routes classification to the skipped AS-leg gate.

**Important nuance verified (so this isn't mis-flagged):** `GateLevelInput.per_tool_gate_level` (CP-side, `gate_level_rule.py:95`) **already exists** and `gate_level()` consumes it directly (line 176, `per_tool_floor = input.per_tool_gate_level`). G2c is NOT "add the gate-level axis" — that axis is built. G2c is the *producer* that populates it from the tool contract, which has no source field. The plan/design draw this distinction precisely.

**The G2/G2c unbundling is sound, not a silent feature-defer.** I confirmed the deny-row narrowing is *unreachable-until-G2c regardless of whether G2 lands*: wrap-time `gate_level = max(per_tool, blast, persona)` where `BLAST_RADIUS_GATE_LEVEL_FLOOR` has no DENY entry (verified lines 136-141) and `PERSONA_TIER_GATE_LEVEL_FLOOR` is all-ASK (verified lines 150-154), so the only DENY-reaching axis is `per_tool_gate_level`, which defaults AUTO until the G2c producer lands. Shipping G2 (U-RT-117) alone is therefore behaviorally inert-but-harmless — the deny-row is not a *deferred behavior*, it is unreachable-in-production by construction until G2c. This is the sanctioned `[[halt-route-split-ac-pattern]]`. Routing note (SKILL.md §2.7.6 fork scale): the AS-leg of B3-spec was skipped (F-B3-1 cascade: AS spec ZERO; F-B3-2 CP/ADR-only) → O-CP-3 is a §2.7.6-Class-2-shaped owed AS-leg gate, correctly surfaced to the operator. **Not a reviewer Class-1/2 defect against this plan.**

### Claim 4 — Aggregate DAG acyclic + no edge to a non-existent unit — **VERIFIED, clean (no finding)**

Walked all 8 nodes + edges (CP §3.4.1, runtime §3.1a):

- Leaves (`(none)`): U-CP-91, U-CP-92, U-RT-115, U-RT-118, U-RT-120. ✓
- U-RT-116 → {U-RT-115, U-CP-91}; U-RT-117 → {U-RT-115, U-RT-116}; U-RT-119 → {U-RT-118, U-CP-92}. ✓
- Both cross-axis edges (U-RT-116→U-CP-91, U-RT-119→U-CP-92) run **RT→CP**, matching the `harness-runtime`→`harness-cp` package direction. No CP unit depends on any U-RT-* (both CP units are foundational leaves; the composer READS the CP carrier/enum, CP never reads back) → **no CP↔RT cycle.** ✓
- RT-internal: every edge points to a strictly-earlier node (115/118/120 foundational; 116→115; 117→115/116; 119→118) → no back-edge. ✓
- Topological order `U-CP-91, U-CP-92, U-RT-115, U-RT-118, U-RT-120 → U-RT-116, U-RT-119 → U-RT-117` is a valid linear extension. ✓
- Every dependency points to a real unit: U-CP-91/92 are co-published in v2.33; U-RT-115/116/118 are co-published in v2.44; the §14.8.8 webhook surface + `on_hitl_timeout` + both `edited_proposal` carriers all pre-exist at HEAD (verified `on_hitl_timeout` at `hitl_timeout_degradation.py:154`, EDIT carriers at `ask_user_question_surface.py` + `hitl_placement.py:197`). No phantom edge. ✓

### Claim 5 — Delta-only-plan-chain preservation — **VERIFIED, clean (no finding)**

Byte-level comparison (Python, not eyeball):

- **CP v2.32 → v2.33:** all 11 prior U-CP-80..U-CP-90 unit bodies are **byte-identical** (confirmed; an apparent U-CP-90 "diff" was a regex-boundary artifact — the prior version's regex capture ran to EOF because U-CP-90 was the last `####`-keyed unit; the actual unit *body* (1330 chars) is byte-identical). Line count 345→446 (+101) is additive. The §1 B1-coverage rows + §3.1–§3.3 B1 aggregate are marked PRESERVED VERBATIM and the §3.4 B3 aggregate is additive. ✓
- **Runtime v2.43 → v2.44:** U-RT-113 byte-identical (2697=2697); U-RT-114 body byte-identical (3024=3024; same EOF-capture artifact). Line count 158→314 (+156) additive. ✓
- Per-version-file change-note convention honored: each new file carries its own §0 change-note; prior change-notes are marked superseded-but-preserved-at-prior-version. ✓

No prior unit body was rewritten or truncated.

### Claim 6 — Carried ACs became explicit unit ACs — **VERIFIED, clean (no finding)**

- **F-B3-1 AC-1 (C10 audit-§20.1-emission-not-vacuous before skip goes live):** lands at **U-RT-116** integration AC — verbatim "Each policy-applied floor-lowering emits a non-vacuous §20.1 audit-ledger entry — verified by execution... The skip MUST NOT go live before this is verified wired" + `[[built-but-vacuous-reground-ledger-asis]]`. ✓
- **F-B3-1 AC-2 (EXTERNAL_REVERSIBLE not representable, contrasting-baseline):** lands at **U-RT-116** ("EXTERNAL_REVERSIBLE / EXTERNAL_IRREVERSIBLE are NOT representable... contrasting-baseline test"). ✓
- **F-B3-2 AC-1 (fail-open refused at ALL tiers, detect-then-refuse):** lands at **U-CP-92** integration AC (config/bootstrap guard refusing fail-open at any tier; contrasting-baseline at multi AND solo/team) AND cross-asserted at **U-RT-119** ("this unit asserts the dispatch path never reaches a fail-open branch"). The home is U-CP-92's reconciled-enum + bootstrap-validation; U-RT-119 asserts the dispatch consequence. Correctly split. ✓
- **F-B3-2 AC-2 (vocab matches CP §21.8/ADR-D5 §1.6, by execution):** lands at **U-CP-92** functional AC ("a test asserts the values match CP §21.8 + ADR-D5 §1.6 + the CP §20.6 span value-set, by execution — NOT a grep"; multi→fail-closed contrasting-baseline). ✓
- **F-B3-2 AC-3 (dispatch not vacuous, per-mode e2e):** lands at **U-RT-119** functional AC ("Per-mode by execution... fail-closed→step-rejected; escalate-secondary-channel→webhook-delivered+paused"). ✓

All carried ACs land in a unit, each preserving the "by execution not green-unit-test" sharpening.

### Claim 7 — Homing decision correct — **VERIFIED, clean (no finding)**

`RuntimeHITLGateComposer` is at `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (verified present, 57.2K) and is **NOT** in `harness-cp` (confirmed by negative search). So the gate-site logic (blast resolver, gate_level-once, palette-thread, EDIT-replace, degradation-attr/dispatch, `HITLAutoApprovePolicy` consumption) is correctly runtime-homed (U-RT-115..120). CP carries only the `GateLevelInput` carrier (U-CP-91) + the vocab reconciliation (U-CP-92); AS owes the G2c carrier (O-CP-3). Composer hardcode sites the plan cites all resolve: `gate_level = GateLevel.ASK` at line 406 (U-RT-117 ✓, plan cites 406 exactly); `hitl.timeout.degradation_mode_applied` at line 1070; `raise HITLGateTimeoutError` at line 1084 (U-RT-119 ✓, plan cites 1084 exactly); EDIT-branch `pass` at line 1139 (U-RT-120 ✓, plan cites 1139 exactly); `getattr(binding, "blast_radius_tier", None)` fallback at line 331 (U-RT-115 producer-discovery ✓); `_ = invocation` at `hitl_timeout_degradation.py:166` (U-RT-118 thin ✓). Unit placement matches the home. ✓

### Claim 8 — U-CP-91 stays plan-layer (no CP-spec fork owed) — **VERIFIED, clean (no finding)**

F-B3-1 §3.2 explicitly blesses the `GateLevelInput` floor-override carrier-shape as a U-CP-43 plan-carrier concern, NOT a C-CP-19 §19.1 spec change ("No CP-spec file is edited by F-B3-1"). Runtime spec §3.8 (line 2213) re-states it: "The exact `GateLevelInput` carrier-shape touch... is a B3-plan concern (U-CP-43 plan-carrier), NOT a C-CP-19 §19.1 spec change." U-CP-91 stays plan-layer; v2.33 §0.4 + §7 footer assert ZERO CP-spec fork. ✓

### Claim 9 — 9-item workspace pattern checklist — **VERIFIED, clean except F3-01**

Walked each: stale-carry-text (clean — the design §4.1 G2c mis-framing is **honestly corrected, not silently absorbed**: O-CP-3 point 1 explicitly states the design framing is "partially falsified"); **sibling-spec staleness → F3-01 (see below)**; forward-cite phantom (clean — no phantom unit/file/symbol; all cited carriers pre-exist); plan-against-not-built (clean — every AC cites a HEAD-present surface, verified); spec-prose-vs-plan-body drift (clean — ACs match §3.8/§14.8.9 bodies); verification grep-vs-e2e (clean — every load-bearing AC says "by execution, NOT grep/green-unit-test"); X-AL-3 anti-extension (clean — G2c registered not impl'd; U-CP-91 plan-layer; ZERO spec amendment); halt-route-split-AC (clean — correctly applied to G2/G2c + the G3 D-edit.B sub-fork O-RT-3); checkpoint-listed-as-open-but-applied (clean — F-B3-1/F-B3-2 both RATIFIED, specs cleared, markers present `Spec_Harness_Runtime-v1_49/50-cleared-2026-06-14.md`).

---

## Class 3 findings (doc-hygiene — non-blocking)

### F3-01 — U-CP-92's cross-ref AC under-scopes the `harness-runtime` docstring drift site

- **Location:** CP plan v2.33 U-CP-92 Scope + AC-2 ("update the **OD-spec / CP-plan / test** cross-references that name the old vocab") — the named cross-ref set omits the `harness-runtime` package.
- **Defect:** The SKILL.md §C cross-spec drift grep surfaces a live vocab-B reference OUTSIDE `hitl_timeout_degradation.py` and outside U-CP-92's named cross-ref list: `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:167-171` — a **docstring** on `HITLPlacementComposer.<timeout-resolve method>` (which delegates `return on_hitl_timeout(invocation, persona_tier)` at line 173) that carries (a) the vocab-B value names `SOLO_DEVELOPER → CONTINUE_AS_REJECT; TEAM_BINDING → ESCALATE_TO_REVIEW_BOARD; MULTI_TENANT_COMPLIANCE → ABORT_WORKFLOW` and (b) the wrong-section `C-CP-21 §21.6` cite. After U-CP-92 reconciles `TimeoutDegradationKind` → vocab-A, this docstring becomes **stale-as-described** (the method will return vocab-A values its docstring still describes as vocab-B; the `§21.6` cite is the same wrong-section error U-CP-92 fixes elsewhere).
- **Discriminator (TASK scale → Class 3):** Behavior is correct (pure delegation; no embedded enum) — only the docstring drifts. It does not require revising the plan's *units or DAG*; it is a one-line widening of U-CP-92's cross-ref scope. Not blocking, not substantive. (On the SKILL.md §4.1 scale this is discriminator (a)-adjacent doc-drift; on the TASK scale = Class 3 doc-hygiene.)
- **Resolution path (shape, not text):** widen U-CP-92's cross-ref clause to name the `harness-runtime` package docstring sites (specifically the `hitl_placement.py` timeout-resolve docstring + its `§21.6` cite) alongside OD-spec / CP-plan / tests. Equivalently, the B3-impl-2 executor sweeps `harness-*/src` for residual vocab-B docstrings as part of the reconciliation. Mitigant already present: U-RT-119 lands in the same runtime package, so an attentive implementer would likely catch it — but the AC as written does not mandate it.
- **NOT in scope (recorded so it isn't mis-flagged):** the vocab-B hits in `Implementation_Plan_Control_Plane_v2.md` / `_v2_1.md` / `_v2_9.md` are **prior delta-chain versions**, frozen-at-authoring by the delta-only convention — correctly left untouched; not drift.

---

## Findings considered and rejected (transparency — substantive checks applied that did NOT surface a defect)

1. **A4 fabricated-cite probe on the composer line numbers** — `gate_level=ASK`@406, `raise HITLGateTimeoutError`@1084, EDIT `pass`@1139 all resolve byte-exact at HEAD `a356929`. No phantom cite.
2. **`ToolContract` typed-field absence (the G2c keystone)** — confirmed by reading BOTH the AS spec C-AS-03 §3.1 schema AND the landed `tool_contract.py` body; the field is genuinely absent. The disposition is not built on a stale assumption.
3. **`GateLevelInput.per_tool_gate_level` confusion trap** — checked whether the plan conflates the CP-side axis (which EXISTS, line 95) with the AS-side carrier (absent). It does not — the distinction is drawn precisely; G2c is correctly framed as the *producer*, not the axis.
4. **Delta-only preservation (the worst silent-violation class)** — byte-compared every prior unit body; all identical. Dismissed the regex-boundary false-positive on the last-unit-in-prior-file rather than reporting it.
5. **DAG cross-axis cycle** — walked every edge for a CP→RT back-edge; none exists (CP units are foundational leaves).
6. **Carried-AC verification-shape** — checked each carried AC preserves "by execution NOT green-unit-test"; all do (the `[[built-but-vacuous]]` trap is explicitly cited at U-RT-116/118/119/U-CP-92).
7. **fail-open register-don't-extend** — verified U-CP-92 + U-RT-119 refuse fail-open at ALL tiers (not just multi), matching §14.8.9 AC-1's "solo/team not-yet-granted" + the F-B3-1 register-don't-extend mirror. The plan does not silently grant fail-open to any tier.
8. **G2b "no-gap" claim** — confirmed `cross_trust_state=NONE` at wrap-time is spec-correct (§14.8.2 line 3353, cross-trust is §14.15-re-entry-only), not a smuggled omission.
9. **Spec-currency / clearance** — both cleared markers (`Spec_Harness_Runtime-v1_49/50-cleared-2026-06-14.md`) exist and reference the B3 design (#549); §3.8 + §14.8.9 are present in the canonical spec head. The plan consumes a genuinely-cleared surface.
10. **vocab-A target byte-fidelity** — U-CP-92's target `{fail-closed, escalate-secondary-channel, fail-open}` + per-tier table (solo→fail-closed, team→escalate-secondary-channel, multi→fail-closed) matches the §14.8.9 byte-cited CP §21.8 + ADR-D5 §1.6 table. No invented value.

---

## Disposition

**APPROVE-WITH-CLASS-3.** No Class-1 (blocking) or Class-2 (substantive, plan-revision-requiring) findings. The decomposition is coverage-complete, zero-spec-extension, acyclic, delta-preserving, correctly-homed, and carries every AC. The G2c→O-CP-3 disposition is the X-AL-3-clean call and *improves* on the design it decomposes. The single Class-3 finding (F3-01, U-CP-92 cross-ref AC omits the `harness-runtime` docstring drift site) is doc-hygiene — fold it into U-CP-92's reconciliation scope at impl, or leave it to the B3-impl-2 residual-vocab sweep; it does not block merge.

## What I read (direct, this session)

- `.harness/r-fs-1-b3-plan-decomposition.md` (full)
- `.harness/r-fs-1-b3-smart-hitl-design-v1.md` (full — gap-set §2, §3.2 blast resolver, §4.1 G2c, §5 G3, §6.1 G4a, §8.2/§8.3)
- `design-substrate/Spec_Harness_Runtime_v1.md` §3.8 (lines 2194-2235) + §14.8.9 (lines 3766-3796)
- `design-substrate/Implementation_Plan_Control_Plane_v2_33.md` (full, 446 lines)
- `design-substrate/Implementation_Plan_Harness_Runtime_v2_44.md` (full, 314 lines)
- `.harness/class_1_fork_b3_1_hitl_auto_approve_policy_field.md` (full — RATIFIED)
- `.harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md` (full — RATIFIED)
- `design-substrate/Spec_Action_Surface_v1.md` C-AS-03 §3.1 (475-503) + C-AS-12 §12.1 formula axis (995-1009)
- Code ground-truth: `harness-as/src/harness_as/tool_contract.py` (ToolContract field schema, lines 71-84); `harness-cp/src/harness_cp/gate_level_rule.py` (GateLevelInput frozen/extra=forbid line 93, per_tool_gate_level axis line 95, floor tables 136-162, gate_level() body 165-187); `harness-cp/src/harness_cp/hitl_timeout_degradation.py` (vocab-B enum 41-49, per-tier table 65-88, §21.6 wrong-cite, WebhookConfig vocab-A line 106, `_ = invocation` line 166, `on_hitl_timeout` line 154); `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (home + hardcode sites 331/406/1070/1084/1139); `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py` (vocab-B docstring drift 162-173)
- Byte-level preservation diffs: CP v2.32↔v2.33 (11 prior units), runtime v2.43↔v2.44 (2 prior units)
- Cross-spec drift grep: vocab-B value names + UPPER enum names across `design-substrate/` + `harness-{cp,od,runtime}/src`
- `.harness/clearance/` (v1.49 + v1.50 markers present)
