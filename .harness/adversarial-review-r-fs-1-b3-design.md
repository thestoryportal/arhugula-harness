# Adversarial Review — R-FS-1 B3 Smart-HITL Design

**Reviewer:** genuine dedicated harness-adversarial-reviewer agent (adopted `.claude/skills/harness-adversarial-reviewer/SKILL.md`, Phase-7 pre-implementation mode; 26 tool-uses, re-grounded every cite by direct read). **Artifact:** `.harness/r-fs-1-b3-smart-hitl-design-v1.md`. **HEAD:** `8608bc1`. **Date:** 2026-06-14.

**VERDICT: APPROVE-WITH-CLASS-2.** All six fork-vs-impl calls correct by direct read; the keystone AS-IS claim confirmed in code; §19.5 currency clean at v1.32; **no silently-absorbed fork** (the X-AL-3 failure mode does not occur). One Class-2 reasoning refinement (G3) + three Class-1 inline fixes — none changes a classification. (A subsequent advisor pre-done #4 pass caught one further completeness gap — G2c, the deny-row-unreachable trap — folded into §4.1 of the design doc; recorded below at §post-review.)

---

## Findings (applied)

### F2-01 (Class 2 — current-phase reasoning refinement) — G3 carrier drift
- **Doc claim (§5):** `gate_result.edited_proposal` is `str`; `step_payload` may be structured; spec NOTE 6-ii "assumes a string-shaped payload."
- **Direct read:** the runtime `AskUserQuestionResult.edited_proposal` IS `str` (`ask_user_question_surface.py:86`; `.encode("utf-8")` at `hitl_gate_composer.py:432/737`) — so the doc's literal claim is *correct for the object it names*. BUT `WorkflowStep.step_payload: Mapping[str,Any]` (`workflow_driver_types.py:99`) and the CP-canonical `HITLGateResult.edited_proposal: Mapping[str,Any] | None` (`hitl_placement.py:197`) are **structured**. The real issue is a **runtime-`str` ↔ CP-`Mapping` carrier drift**, not "NOTE 6-ii assumes str" (NOTE 6-ii's "verbatim" presumes the structured CP carrier).
- **Omitted branch:** §14.8.3 v1.12 provides structured elicitation (`ctx.elicit(message, schema)`, spec line 3379). A structured `edited_proposal` → `Mapping → Mapping` replace = plain IMPL, no sub-fork.
- **Disposition:** G3's IMPL core STANDS; reasoning re-attributed to the carrier drift + the IMPL-via-structured-elicitation branch added. **APPLIED** at design-doc §5 (D-edit.A / D-edit.B).

### F1-01 (Class 1) — §19.5 in-`max()` reading is an inference
- §19.5 header reads "Operator-policy override of any `max()` floor" (CP spec v1.2 line 1696); §19.1 annotations byte-exact (lines 1634/1639). "in-`max()`" vs "post-`max()`" is a sound inference, not spec-stated. **APPLIED** — `[MODERATE]` tag at §1.3.

### F1-02 (Class 1) — guard the G1 "no-fork" branch
- The "no-fork" branch is valid only if ZERO new declared override-policy field is minted; any persisted policy field = a new contract surface → the narrow fork is owed. **APPLIED** — silent-absorption guard at §8.1 F-B3-1.

### F1-03 (Class 1) — confidence tags absent
- **APPLIED** — tagged the two inference-bearing claims.

---

## Findings checked and STANDING (rejected as defects)

1. **Keystone AS-IS "gate always fires even when wired":** `gate_level_rule.py:150-154` all 3 tiers → ASK; `:185-186` `max()`; `:195-202` `hitl_required = computed ∈ {ASK,DENY}` ⟹ always True. **CONFIRMED.**
2. **G1 producer-discovery:** `StepEffectiveBinding` (`per_step_override_evaluator.py:126-151`) carries no `blast_radius_tier`/`per_tool_gate_level`; INFERENCE→READ_ONLY sound; `ToolContract.blast_radius_tier` (`tool_contract.py:80`); `compute_child_blast_radius_ceiling`/`_blast_radius_of` (`sub_agent_gate_level_descent.py:43,137`). **SOUND.**
3. **G4a/G4b split:** runtime §14.8.2 step 4f (line 3356) + RT-FAIL-HITL-GATE-TIMEOUT row (line 3482) wire degradation as audit-attribute-only + always-raise; `on_hitl_timeout` persona_tier-only (`hitl_timeout_degradation.py:166` `_ = invocation`); kinds are control-flow (C-CP-21 §21.6, `:40-50`). G4a=IMPL, G4b=Class-1 FORK. **CORRECT.**
4. **G3 step 4i non-compliance:** composer `pass` (`hitl_gate_composer.py:1130-1139`) vs spec MUST-replace (lines 3366, 3458). **CORRECT.**
5. **G5 HandoffContext:** §14.7.3 line 3178 `summary_text=""` is the v1.6 MVP shape, deferred = "Summarization model invocation per C-CP-21 §21.4"; doc dispositions it as explicitly-in-scope follow-on (§7/§8.3). **NOT scope-narrowing.**
6. **G2b cross_trust=NONE:** spec §14.8.2 step 4d (line 3353) + NOTE 6-iv — cross-trust is §14.15-only. **CORRECT (NO GAP).**
7. **§19.5 delta-chain currency:** no v1.16→v1.32 delta re-tables §19.5 / "operator-policy override"; §19.5+§19.1 canonical at v1.2; v1.15 §19.1.1 is the axis-set clarification. **CLEAN at v1.32.**
8. **Stale-carry / docstring-vs-body:** `hitl_gate_composer.py:56-81` IS the stale docstring the ledger misread; body (`:909-927`) routes the Reading-B helpers. Doc's "machinery-built-unwired" re-grounding **accurate**.
9. **4b⊥4c orthogonality + already-built (matrix_cell_for / 4-span / VALIDATOR_ESCALATION §14.15 re-entry):** engine_class not in §19.1 axis set; VALIDATOR_ESCALATION wrap-time-filtered (spec step 3 line 3348). **CORRECT.**
10. **Forward-looking cite phantom:** every spot-checked path/symbol/§-cite resolves byte-exact at HEAD. **NONE.**

---

## Post-review (advisor pre-done #4, after the adversarial pass)

**G2c — deny-row narrowing green-but-unreachable.** Trace: after G1-as-scoped, wrap-time `gate_level = max(per_tool, blast, persona)`; persona tops at ASK, blast tops at ASK (`gate_level_rule.py:136` no DENY entry), and §3.2 resolves only `blast_radius` → `per_tool_gate_level` getattr-defaults AUTO → `gate_level ∈ {AUTO, ASK}` never DENY → the §19.4 deny-row palette narrowing (the only wrap-time narrowing) never fires → G2's `gate_level` threading is behaviorally inert. `ToolContract` (`tool_contract.py:77-80`) carries `minimum_tier`+`blast_radius_tier` but **no per-tool gate-level**, though C-AS-03 frontmatter (`tier ∈ {auto,ask,deny}`, AS spec line 1155) + C-AS-12 §12.1 (line 1002) declare it. **Folded into design-doc §4.1 as G2c** (faithful carrier factor-out, IMPL; ships with G2). No classification changed.

---

*Filed per the B1 precedent (`.harness/adversarial-review-r-fs-1-arc-6-b1-plan.md`). The decorrelated review trail for the B3-design PR: advisor ×4 + Codex [P2] + this genuine adversarial agent.*
