# Adversarial Review — B3-impl-3 (R-FS-1 arc #23, U-RT-120 "EDIT replace-not-merge")

## Summary
- Mode: Phase-7 pre-merge impl-arc review against cleared `Spec_Harness_Runtime_v1.md` §14.8.2 step 4i + NOTE 6-ii
- Branch: `r-fs-1-arc-23-b3-impl-3-edit-carrier-drift` @ `2fb955d` (1 commit ahead of `main`)
- Artifacts reviewed: `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py`; `harness-runtime/tests/test_lifecycle_hitl_gate_composer.py`; `.harness/class_1_fork_hitl_edit_carrier_drift_str_vs_mapping.md`
- Date: 2026-06-14
- **TAXONOMY NOTE (load-bearing — per SKILL.md line 14).** Two Class-1/2/3 scales are in play and they are **inverted**. The prompt's output legend is the **§2.7.6 Phase-7 fork scale**: Class 1 = halt-execution (blocker), Class 2 = in-execution operator decision (gate), Class 3 = informational (non-blocking). All finding tags below use the **§2.7.6 scale**. Separately, the fork doc's `class_1_` filename is the **§4.3 back-flow routing class** (design-substrate revision required at the follow-on arc) — that is correct and is *not* a finding-severity.
- Finding count (§2.7.6 scale): Class 1 (halt): 0 · Class 2 (operator decision): 0 · Class 3 (informational): 3
- **Disposition recommendation: APPROVE.** The diff is an honest split-AC partial-landing: the materializable half (typed raise surfacing the carrier drift) lands; the unmaterializable half (functional `str→Mapping` EDIT) routes to a registered BUILD arc. No silent absorption, no disguised defer-close, no X-AL-3 violation. Three Class 3 (informational) findings are doc-hygiene / probe-closure notes — none block merge.

---

## Re-grounding ledger (every cite read directly at HEAD)

| Claim | Cite | Verdict |
|---|---|---|
| `HITLGateResult.edited_proposal: Mapping[str, Any] \| None` | `harness-cp/src/harness_cp/hitl_placement.py:197` | ✅ EXACT (read line 197) |
| `AskUserQuestionResult.edited_proposal: str \| None` | `ask_user_question_surface.py:86` | ✅ EXACT (read line 86) |
| `AskUserQuestionElicitationSchema.edited_proposal: str \| None` + MCP flat-schema docstring | `mcp_backed_ask_user_question_surface.py:171-199` | ✅ EXACT (read 171-207; "flat objects with primitive properties only" at 184) |
| `WorkflowStep.step_payload: Mapping[str, Any]` (opaque per C-CP-25 §25.3.3.4) | `workflow_driver_types.py:99` | ✅ EXACT (read line 99 + docstring 91) |
| `gate_result` static type at 4i = `AskUserQuestionResult` | `ask_user_question_surface.py:114-119` `ask(...) -> AskUserQuestionResult` | ✅ CONFIRMED (surface attr typed `AskUserQuestionSurface`; `.ask` returns `AskUserQuestionResult`) |
| `_parse_edited_arguments` precedent (json.loads → Mapping + "JSON object of tool arguments" guard) | `r_cxa_2_producer_loop_factory.py:239` | ✅ EXACT (read 239-242) |
| NO `design-substrate/` backing for `_parse_edited_arguments` / "JSON object of tool arguments" | grep `design-substrate/` | ✅ CONFIRMED EMPTY (both exact-phrase greps exit 1; the lone `json.loads` hit is unrelated IS-7 JSONL prose) |
| Spec step 4i "edited proposal replaces step.step_payload" | `Spec_Harness_Runtime_v1.md:3442` | ✅ EXACT |
| Spec NOTE 6-ii "MUST replace-not-merge … deferred to a future workflow-mutation-discipline arc" | `Spec_Harness_Runtime_v1.md:3534` | ✅ EXACT |
| Design doc D-edit.A vs D-edit.B disposition | `.harness/r-fs-1-b3-smart-hitl-design-v1.md:186-192, 236` | ✅ EXACT |
| Sibling fork `class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md` | `.harness/` | ✅ EXISTS |
| Fork-doc orientation HEAD `16a4758` | `git log 16a4758` | ✅ RESOLVES (post-#555 main HEAD = branch-cut base; not phantom) |

---

## Adversarial probes (each re-grounded)

### Probe 1 — Audit-then-raise ordering; entry-vs-fail-class contradiction class (the B3-impl-2 sibling-bug pattern)
**Re-grounded:** `hitl_gate_composer.py:1406-1468`. Ordering is **correct and free of the contradiction class**.
- Step 4h (line 1410) sets `raise_on_audit_failure = gate_result.response != HITLResponse.REJECT` → for EDIT this is `True` (audit-compose failure would surface, not be swallowed). The audit is composed at `_compose_and_persist_audit` (line 1412) **before** the 4i raise (line 1458).
- The 8a-HITL audit (lines 948-967) for `response == EDIT` computes `edited_hash = sha256(gate_result.edited_proposal.encode("utf-8"))` (line 951) — i.e. over the operator's actual `str` edit. The persisted entry is **EDIT-shaped** (`response = "edit"`, populated `edited_proposal_hash`), which **agrees** with the operator's actual selection. This is NOT the B3-impl-2 vacuous-response="" / contradicting-fail-class bug: there, a vacuous entry preceded a contradicting raise. Here the entry faithfully records the real edit, and the subsequent raise (`HITLGateEditCarrierDriftError`) is a distinct application-gap fault that does not contradict the recorded fact. The pattern is symmetric to the REJECT path (entry preserved before `HITLGateRejectedError`).
- **VERDICT: clean.** See Probe 1b (Class 3) for the one residual nuance on NOTE 6-ii's "post-mutation hash" framing.

### Probe 2 — Does the blanket raise over-foreclose a materializable replace-not-merge case?
**Re-grounded the wired elicitation path end-to-end:** `mcp_backed_ask_user_question_surface.py:171-207` + `mcp_server.py` (`ctx.elicit(message, schema)`). The design doc D-edit.A path (line 189) names a structured-elicitation surface (`ctx.elicit(message, schema)`, runtime spec line 3379) that *would* deliver a `Mapping` and collapse the sub-fork to plain IMPL. **I checked whether that path is wired to deliver a `Mapping`. It is NOT.** The only wired `ctx.elicit` schema is `AskUserQuestionElicitationSchema`, whose `edited_proposal: str | None` (line 197) is string-typed **by MCP flat-schema necessity** ("flat objects with primitive properties only", line 184). Every wired EDIT path therefore yields a `str`, which cannot be applied verbatim to a `Mapping[str, Any]` step_payload. There is NO wired path delivering a `Mapping` edited_proposal to this composer.
- **VERDICT: the blanket raise does NOT over-foreclose.** D-edit.B is empirically forced by the flat-`str` elicitation wiring; D-edit.A is unreachable through the wired path. The arc's central claim is correct. (Consequence: there is also no §2.7.6 Class 2 here — D-edit.B is not an open operator choice, the wiring forecloses A.)

### Probe 3 — Does the new error avoid pre-minting a §14.8 RT-FAIL-* taxonomy code?
**Re-grounded the `HITLCellExcludedError` precedent:** `hitl_gate_composer.py:217-225`. `HITLCellExcludedError(Exception)` is a bare Exception subclass whose docstring says "new fail class (not in §14.8 taxonomy; surfaces as RuntimeError-shape error to driver)." The new `HITLGateEditCarrierDriftError` (lines 261-303) follows this precedent **exactly**: bare `Exception` subclass, docstring states "Driver maps to a fork-pending new fail class (NOT yet in the §14.8 taxonomy; surfaces as RuntimeError-shape error to the driver — matching the `HITLCellExcludedError` precedent)."
- **VERDICT: clean.** Correctly avoids pre-minting an `RT-FAIL-*` code (per the advisor guidance the arc cites). The carrier-healing arc owns eventual taxonomy registration.

### Probe 4 — Is the contrasting-baseline test genuinely contrasting? Are APPROVE/REJECT/RESPOND regression-safe?
**Re-grounded:** `test_lifecycle_hitl_gate_composer.py:853-911`.
- The test asserts (a) `pytest.raises(HITLGateEditCarrierDriftError, match="carrier drift")` (the new raise fires), (b) `inner.calls == []` (**the prior silent-drop — `pass`-then-dispatch with unchanged step — is GONE; inner NOT reached**), and (c) `audit.appends[0]` carries `audit.cp.edited_proposal_hash` (the operator edit is preserved). This is a **genuine** contrasting baseline: it asserts the old silent behavior is gone, not merely that the new raise fires.
- **Regression-safety re-grounded by execution:** ran the full composer suite (52 passed) + the EDIT/APPROVE/REJECT/RESPOND subset (9 passed) + adjacent HITL/elicitation tests (`test_lifecycle_server_ctx_elicit_callback.py`, `test_lifecycle_hitl_placement.py`, `test_run_workflow_elicitation_e2e.py` — 34 passed). APPROVE/REJECT/RESPOND branches unchanged. pyright strict on the changed source: 0 errors / 0 warnings / 0 informations.
- **VERDICT: clean.**

### Probe 5 — Does any OTHER caller / the durable-async path depend on EDIT dispatching the unchanged step?
**Re-grounded:** grepped all `RuntimeHITLGateComposer` callers (`mutable_context.py`, `stage_5_loop_init.py`, `types.py`, `hitl_placement.py` (CP Protocol decl), and tests). Checked every EDIT-referencing test.
- `test_run_workflow_elicitation_e2e.py:392` exercises `HITLResponse.APPROVE`, not EDIT.
- `test_lifecycle_server_ctx_elicit_callback.py:104-107` tests the SURFACE callback layer (returns an `AskUserQuestionResult` with `edited_proposal`), NOT `RuntimeHITLGateComposer.dispatch` — no dependency on EDIT dispatching the composer's unchanged step.
- `test_lifecycle_hitl_placement.py` references are palette-membership only.
- **Durable-async 4-bis path:** `hitl_gate_composer.py:1215-1251`. When joint-binding + `DURABLE_ASYNC` synchrony, `_escalate_to_secondary_channel` raises `HITLPauseRequestedSignal` (NoReturn) **before** the 4f/4g/4h/4i sync path. EDIT is only reachable on the sync-blocking path. The durable-async path **never dispatches through the EDIT branch**.
- **VERDICT: clean.** No caller depends on EDIT dispatching the unchanged step. The composer's own test file is the only place EDIT-through-composer is exercised, and that's the rewritten test.

### Probe 6 — Fork classification (Class 1 vs Class 2) + filename consistency
**Re-grounded:** Fork doc filed as Class 1 under §4.3 (under-specification → design-substrate artifact revision required at the follow-on workflow-mutation-discipline arc, which WILL edit `design-substrate/`). This is the correct **§4.3 routing class** — the follow-on arc amends NOTE 6-ii / mints a structured-edit contract. Filename `class_1_fork_hitl_edit_carrier_drift_str_vs_mapping.md` matches the code docstring reference (line 290-291), the comment reference (line 1457), the raised-message reference (lines 1465-1467), and the commit. **Consistent.**
- **VERDICT: Class 1 §4.3 routing is correct; not Class 2.** (Distinct from this review's finding-severity scale — see TAXONOMY NOTE in Summary.)

### Probe 7 — Phantom-cite check (do code/docstring/fork-doc cites resolve byte-exact?)
**Re-grounded:** every file:line and §-cite in the new code comments, docstrings, and fork doc — see the re-grounding ledger above. All resolve. Spec line numbers 3442 (step 4i) + 3534 (NOTE 6-ii) match exactly. The fork-doc HEAD `16a4758` is the legitimate branch-cut base (post-#555 main HEAD), not a phantom.
- **VERDICT: no phantom cites.**

---

## Class 1 (halt) findings — §2.7.6 scale
**NONE.**

## Class 2 (operator decision) findings — §2.7.6 scale
**NONE.** D-edit.B is not an open operator choice — the flat-`str` elicitation wiring empirically forecloses D-edit.A (Probe 2).

## Class 3 (informational, non-blocking) findings — §2.7.6 scale

### F3-01 — New error absent from module-docstring fail-class taxonomy
- **Location:** `hitl_gate_composer.py:95-102` (module docstring "Failure-mode taxonomy" block).
- **Defect:** The module docstring catalogs `HITLPlacementForeclosedAtV19Error`, `HITLCellExcludedError`, `HITLGateTimeoutError`, `HITLGateRejectedError`, `HITLGateAuditComposeError` — but the new `HITLGateEditCarrierDriftError` is not listed, despite being the sibling-shaped "new fail class; surfaces as RuntimeError to driver" entry the catalog exists to enumerate.
- **Negative framing (what would make it wrong / worse):** if this taxonomy block were the authoritative driver-side fail-class map consumed downstream, the omission would be a real coverage gap. It is documentation only; the error is live and tested. Non-blocking.
- **Discriminator:** §2.7.6 Class 3 (informational documentation drift). Resolution shape: add the new error to the docstring taxonomy block (inline doc fix).

### F3-02 — New error absent from `__all__` export list
- **Location:** `hitl_gate_composer.py:263-272` (`__all__`).
- **Defect:** `__all__` lists `HITLCellExcludedError`, `HITLGateAuditComposeError`, `HITLGateRejectedError`, `HITLGateTimeoutError`, `HITLPauseRequestedSignal`, `RuntimeHITLGateComposer` — but not `HITLGateEditCarrierDriftError`. The rewritten test imports it directly (`from harness_runtime.lifecycle.hitl_gate_composer import HITLGateEditCarrierDriftError`), so this works regardless; the omission is an export-surface inconsistency vs. its sibling exception classes.
- **Negative framing:** a downstream consumer doing `from ...hitl_gate_composer import *` would not get the new error, asymmetric to its siblings. Low blast radius (star-import is not the convention here). Non-blocking.
- **Discriminator:** §2.7.6 Class 3 (informational). Resolution shape: add `"HITLGateEditCarrierDriftError"` to `__all__`.

### F3-03 (Probe 1b closure) — NOTE 6-ii "post-mutation payload hash" framing when mutation is pre-empted
- **Location:** `hitl_gate_composer.py:948-967` (8a-HITL `edited_hash`) vs `Spec_Harness_Runtime_v1.md:3534` NOTE 6-ii ("The `edited_proposal_hash` audit field captures the post-mutation payload hash (not the diff)").
- **Defect:** NOTE 6-ii frames `edited_proposal_hash` as the **post-mutation** payload hash. In the EDIT raise path, no mutation occurs (the raise at 4i pre-empts step 5), so `edited_hash = sha256(operator_str)` is a hash of the operator's **pre-mutation input**, not a post-mutation payload. Technically the NOTE's framing is not satisfied for the raise path.
- **Negative framing (why non-blocking):** this is **pre-existing**, not introduced by this diff — the prior `pass` path also never mutated, so it never produced a post-mutation hash either; the diff does not worsen it (and in fact makes the no-mutation state explicit rather than silently dispatching). The interaction is already named in the fork doc §2 candidate (C) ("the `edited_proposal_hash` 'post-mutation payload hash, not the diff' note interacts here"), folding it into the carrier-healing BUILD arc. The honest interim hash-over-input is the most faithful artifact available when mutation is deferred.
- **Discriminator:** §2.7.6 Class 3 (informational; resolved-by-the-registered-arc). Resolution shape: the carrier-healing arc reconciles the audit-hash semantics when functional `Mapping`-EDIT lands.

---

## Findings considered and rejected (transparency)

1. **B3-impl-2 sibling-bug recurrence (vacuous entry + contradicting fail-class)** — checked Probe 1; the EDIT 8a-HITL entry faithfully records the operator's real edit (`edited_proposal_hash` over the actual `str`); no vacuous entry, no contradicting fail class. Not a finding.
2. **Blanket-raise over-foreclosure of a materializable EDIT** — checked Probe 2; grounded the full wired `ctx.elicit` path to the flat-`str` `AskUserQuestionElicitationSchema`. No wired `Mapping`-delivering path exists. The raise is correct for every wired EDIT. Not a finding.
3. **Pre-minting an RT-FAIL-* taxonomy code (X-AL-3-adjacent design extension)** — checked Probe 3; the new error follows the `HITLCellExcludedError` "not-in-taxonomy / RuntimeError-shape" precedent exactly. Not a finding.
4. **Non-contrasting baseline (asserts new raise but not that old silent-drop is gone)** — checked Probe 4; the test asserts `inner.calls == []` (silent-drop gone) AND audit-preservation AND the raise. Genuinely contrasting. Not a finding.
5. **APPROVE/REJECT/RESPOND regression** — verified by execution (52 + 9 + 34 tests pass; pyright 0/0/0). Not a finding.
6. **Other-caller / durable-async dependency on EDIT-dispatch-unchanged** — checked Probe 5; no caller depends on it; durable-async raises `HITLPauseRequestedSignal` before reaching 4i. Not a finding.
7. **Phantom cites in code/docstring/fork-doc** — checked Probe 7; all file:line and §-cites resolve byte-exact; fork-doc HEAD `16a4758` is the legitimate branch-cut base. Not a finding.
8. **Disguised defer-close (FULL-SPEC directive violation)** — checked: the fork §4 registers the carrier-healing arc as live forward work, sequenced in the R-FS-1 child-arc order (B3→E→B2→R→…) + roadmap §5 + post-phase-8 register. It is an honest interim landing + a registered BUILD arc, not an indefinite park. Not a finding.
9. **Silent absorption / X-AL-3 (inventing a str→Mapping conversion)** — checked: the diff explicitly REFUSES to invent a conversion (the `_parse_edited_arguments` json.loads shape has no design-substrate backing — grep confirmed empty); it raises instead, surfacing the drift to design-phase back-flow. This is the correct X-AL-3-avoiding move. Not a finding.
10. **Audit-suppression posture on the EDIT path** — checked `raise_on_audit_failure` at line 1410 = `True` for EDIT (only REJECT swallows). Correct; EDIT audit-compose failures surface. Not a finding.

---

## Disposition

**APPROVE.**

The diff is a textbook honest split-AC partial-landing (`[[halt-route-split-ac-pattern]]`): the materializable half — a typed raise (`HITLGateEditCarrierDriftError`) surfacing the runtime-`str` ↔ CP-`Mapping` carrier drift instead of the prior silent `pass`-then-dispatch that dropped the operator's edit — lands and is tested by execution; the unmaterializable half — functional `str→Mapping` EDIT (which would require minting decode/mutation semantics the cleared spec explicitly DEFERS) — routes to a **registered** carrier-healing BUILD arc with concrete sequencing (R-FS-1 child order + roadmap §5 + post-phase-8 register). This clears all three standing-directive tests:
- **X-AL-3:** the diff refuses to silently invent a `str→Mapping` conversion (the `_parse_edited_arguments` precedent has no design-substrate backing — verified empty grep); it raises and routes to back-flow. Correct.
- **FULL-SPEC honest-interim:** not a defer-close — functional EDIT is committed to the registered follow-on arc, not parked.
- **No silent absorption:** the prior silent-drop bug is eliminated and the contrasting-baseline test proves it.

No §2.7.6 Class 1 (halt) and no §2.7.6 Class 2 (operator decision) findings. Three §2.7.6 Class 3 (informational) findings — two one-line doc-hygiene fixes (F3-01 docstring taxonomy, F3-02 `__all__`) that MAY be folded into this PR or a trivial follow-up, and F3-03 a probe-closure note already owned by the registered arc. None gate merge.

Note for the reader: the fork doc's `class_1_` filename is the **§4.3 back-flow routing class** (design-substrate revision required at the follow-on arc) and is **correct** — it is unrelated to this review's finding-severity. "Class 1 fork" next to "APPROVE / 0 Class-1-findings" is not a contradiction; they are two different Class-1/2/3 axes (SKILL.md line 14 disambiguation).
