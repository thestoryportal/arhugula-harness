# Adversarial Review — B3-impl-2 (smart-HITL timeout-degradation dispatch-on-mode)

## Summary

- **Mode:** Phase-7 pre-merge impl-arc adversarial review (per skill standing posture A; PR-ready branch `r-fs-1-b3-impl-2`, single commit `c06499e`).
- **Artifacts reviewed (impl):** `harness-cp/src/harness_cp/hitl_timeout_degradation.py`; `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py`; `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py`; + 3 test files.
- **Authority chain grounded (direct read):** runtime spec §14.8.9 (NEW v1.50) + §14.8.8.6; CP `CPAuditLedgerEntry` schema; OD `cp_audit_to_od_audit` converter; F-B3-2 fork; `AskUserQuestionResult` shape.
- **Date:** 2026-06-14.

> **Taxonomy disambiguation (load-bearing — see skill title-section).** This report's findings use the **§4.1 review-severity** scale: **Class 1 = minor (drift) · Class 2 = moderate (current-phase revision) · Class 3 = severe (phase re-opening)**. This is INVERTED from the **§2.7.6 Phase-7 execution-fork** scale the operator's output-spec named (Class 1 = halt / Class 2 = operator-decision / Class 3 = informational). **Every finding below states BOTH** its §4.1 review-severity AND, where a routing disposition results, its §2.7.6 fork class explicitly labelled — to prevent reading a §4.1 "severe" as a §2.7.6 "informational." The PRIMARY finding is a **blocking pre-merge impl fix**, NOT a design-back-flow fork (impl-doesn't-match-a-correct-spec → no spec/ADR revision owed → it is NOT a §2.7.6-Class-1 design-defect fork).

- **Finding count (by §4.1 severity):** Class 3: 0 · Class 2: 2 · Class 1: 3.
- **Highest-severity finding:** F2-01 (the fail-closed-timeout audit shape — the PRIMARY question).
- **Disposition recommendation:** **APPROVE-WITH-FINDINGS.** The vocab reconciliation (AC-2), the fail-open guard (AC-1), the control-flow dispatch (AC-3 at the disposition level), and the §21.6→§21.8 sweep are all sound and correct. F2-01 + F2-02 (two audit-shape defects on the timeout paths) are **blocking pre-merge fixes** — both are §4.1-Class-2 (current-phase impl revision; no spec change), and both are unverified by any test.

---

## PRIMARY-QUESTION VERDICT — (b): the fail-closed timeout OWES a REJECT-shaped audit entry

**Decision: (b).** The partial-timeout audit (`response=""`) on the fail-closed timeout path is **NOT** a faithful-enough disposition record — especially at multi-tenant-compliance — and it is **not** sanctioned by §14.8.9's "Deferred to implementation discretion" latitude. It is a genuine spec-vs-impl divergence requiring an impl fix before merge.

### Why (b), grounded

1. **The spec is explicit and on-point — the audit shape is NOT deferred.** Runtime spec `Spec_Harness_Runtime_v1.md:3786` (§14.8.9, the `fail-closed` disposition row) reads, verbatim:
   > `fail-closed` … → §14.8.2 step 4i `REJECT` → **emit the rejection audit entry (step 4h)** → raise `HITLGateRejectedError` → `RT-FAIL-HITL-GATE-REJECTED`

   "The rejection audit entry (step 4h)" is the entry step-4h composes on a **real REJECT** — which (per the `_compose_and_persist_audit` else-branch, `hitl_gate_composer.py:888-907`) carries `response="reject"` + `rejection_reason_hash = sha256(rejection_reason)`. The §14.8.9 "Deferred to implementation discretion" list (`:3796`) grants latitude on exactly three things — (a) the residual-hard-timeout boundary, (b) the escalate-when-unbound degrade-to-fail-closed fallback, (c) the fail-open config-error shape — **and the audit entry shape is not among them.** The change-note §14 taxonomy amendment (`:15` / line 11 of the v1.49→v1.50 change-note) independently confirms: `fail-closed` "routes through the REJECT path (`RT-FAIL-HITL-GATE-REJECTED` semantics on a timeout)."

2. **What the impl actually emits — an internally self-contradictory entry.** The timeout branch (`hitl_gate_composer.py:1255-1262`) calls `_compose_and_persist_audit(..., gate_result=None, raise_on_failure=False)` **unconditionally, before the mode dispatch**. With `gate_result=None`, the `_compose_and_persist_audit` partial branch (`:879-887`) sets `response_value = ""` and all hash fields `None`. The fail-closed path then raises `HITLGateRejectedError` (`:1299`) → `RT-FAIL-HITL-GATE-REJECTED`. So the persisted CP entry is `{response: "", rejection_reason_hash: None}` while the run's fail-class is REJECTED.

3. **The impl's OWN code flags this shape as vacuous.** `hitl_gate_composer.py:873-874` (the U-RT-116 auto-approve branch) explicitly states `response=""` is "the timeout `response=""` partial shape (which would read as a **vacuous/null entry, failing AC-1's spirit**)." B3-impl-1's AC-1 deliberately distinguished a real disposition from this exact `""` shape — and B3-impl-2 now routes a *disposition-bearing* REJECT through it.

4. **The OD audit consumer sees the contradiction end-to-end.** `CPAuditLedgerEntry.response` is typed `str` and documented `∈ {approve, edit, reject, respond}` (`per_step_override_evaluator.py:78-79`) — `""` is **out-of-schema**; `rejection_reason_hash` is populated **iff `response == "reject"`** (`:84-85`). The converter `cp_audit_to_od_audit` projects `audit_namespace_attrs["<prefix>.response"] = cp_entry.response` (`harness-cxa/src/harness_cxa/cp_audit_conversion.py:118`) and includes `rejection_reason_hash` only when non-None (`:123-124`). So an OD/compliance ledger consumer reads `response = ""` (says "timeout/no-disposition") on an entry whose run fail-class is REJECTED (says "rejected"), with no `rejection_reason_hash` to attribute the system disposition. At multi-tenant-compliance (audit-critical, `audit_required=True`, override-prohibited), an entry that internally disagrees about whether the step was denied or merely timed out is not a faithful disposition record.

5. **Semantic distinctness matters too.** `AskUserQuestionResult.response` is "the **operator-selected** response class" (`ask_user_question_surface.py:78-79`). A timeout is a *system* disposition, not an operator selection — so the right entry is REJECT-shaped but with a **system** `rejection_reason` (e.g. `"timeout-fail-closed"`) that distinguishes it from an operator REJECT, not a borrowed-or-blank one.

### Concrete remediation (entry shape + call-site; mechanism left to impl per FM-C)

**Required:** split audit composition **by terminal disposition**, placed **after** the mode dispatch resolves, not the current unconditional pre-dispatch partial write.

- **Entry shape for the two REJECT-terminating timeout paths** (fail-closed; AND escalate-degraded-when-unbound — see F2-02): a step-4h **rejection** entry — `response = "reject"`, `rejection_reason_hash = sha256(<system reason, e.g. "timeout-fail-closed">)`, `gate_level = GateLevel.AUTO` (already correct). This makes the persisted entry agree with `RT-FAIL-HITL-GATE-REJECTED` and gives the OD consumer the populated `rejection_reason_hash` the C-CP-16 §16.2 reject-row requires.
- **Entry shape for the residual hard-timeout path** (persona_tier-None → `HITLGateTimeoutError`): **KEEP** the current `response=""` partial-timeout entry — it is internally consistent with `RT-FAIL-HITL-GATE-TIMEOUT` and matches the pre-existing v1.9 TIMEOUT contract (`hitl_gate_composer.py:233-234`). No change here.
- **Call-site:** the timeout `except AskUserQuestionTimeoutError` block, `hitl_gate_composer.py:1255-1304`. The `_compose_and_persist_audit(...)` call at `:1255` must move below the dispatch and become disposition-conditional (one shape for REJECT-terminating, the partial for residual-timeout).
- **Mechanism (impl-discretion — do not prescribe):** either a synthetic `AskUserQuestionResult(response=HITLResponse.REJECT, latency_ms=<elapsed>, rejection_reason="timeout-fail-closed")` fed into the existing else-branch, OR a new explicit `system_reject_reason: str | None` parameter to `_compose_and_persist_audit`. **NOTE for the synthetic route:** `AskUserQuestionResult` requires both `response` AND `latency_ms` (no default — `ask_user_question_surface.py:81`), with `rejection_reason` optional (`:94`) — supply `latency_ms` (e.g. the elapsed timeout duration).
- **Test owed (the blind spot that admitted the divergence):** no existing test asserts the **persisted entry shape** — the new composer tests assert only the exception type + the span attribute (see F1-03). Add an assertion that the REJECT-terminating timeout writes a CP entry with `response == "reject"` and a populated `rejection_reason_hash` (and that the residual-timeout path keeps `response == ""`).

---

## Class 2 findings (moderate — current-phase impl revision; §2.7.6: blocking pre-merge fix, NOT design back-flow)

### F2-01 — Fail-closed timeout emits the vacuous partial audit, not the spec-mandated REJECT entry (THE PRIMARY)

- **Location:** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1255-1262` (unconditional partial-audit write) + `:1299` (REJECT raise); `:879-887` (partial branch composing `response=""`). Spec authority: `design-substrate/Spec_Harness_Runtime_v1.md:3786`.
- **Defect:** see PRIMARY-QUESTION VERDICT above. The fail-closed timeout persists `{response:"", rejection_reason_hash:None}` then raises REJECTED, contradicting §14.8.9's "emit the rejection audit entry (step 4h)."
- **Discriminator (§4.1):** (a) — affects substantive content of the current-phase artifact (the impl); resolution is self-contained to `harness-runtime/src` + a test. Does NOT fire (b) or (c): the spec is correct and unchanged, so no upstream revision. → **§4.1 Class 2.**
- **§2.7.6 routing:** NOT a fork. Impl-to-correct-spec mismatch → blocking pre-merge impl fix. Do **not** open a spec/ADR arc.
- **Evidence:** `:873-874` impl-self-flags `response=""` as "vacuous/null … failing AC-1's spirit"; `per_step_override_evaluator.py:84-85` (`rejection_reason_hash` iff `response=="reject"`); `cp_audit_conversion.py:118,123-124` (OD consumer reads `response` + conditionally `rejection_reason_hash`).
- **Decision-vocabulary:** *decided.*
- **Resolution path:** see "Concrete remediation" above (shape + call-site decided; mechanism left open per FM-C).

### F2-02 — Escalate-secondary-channel paths write an audit entry that contradicts BOTH the degraded REJECT and the §14.8.8.6 pre-pause-no-audit rule

- **Location:** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1255-1262` (the unconditional pre-dispatch partial write) interacting with `:1275-1290` (escalate dispatch) + `:1299` (degraded REJECT). Spec authority: `design-substrate/Spec_Harness_Runtime_v1.md:3743` (§14.8.8.6).
- **Defect (two sub-cases, both from the same pre-dispatch unconditional write):**
  1. **escalate-degraded-when-unbound → REJECT:** when the joint binding is absent, the escalate path falls through to the same `raise HITLGateRejectedError` at `:1299`, but the audit entry already written at `:1255` is the `response=""` partial — **the identical defect as F2-01, on a second path.** The F2-01 remediation MUST cover this path too (it terminates in REJECT, so it owes the same REJECT-shaped entry).
  2. **escalate-bound → pause:** when the joint binding is present, `:1255` writes a partial-timeout audit entry **before** `_escalate_to_secondary_channel` (`:1282-1289`) delivers the webhook + raises `HITLPauseRequestedSignal`. But §14.8.8.6 (`:3743`) states the pre-pause path "does **NOT** compose the audit entry — the response is not yet available at that point; the audit entry materializes at resume-time." So this path writes a **spurious** pre-pause partial entry the spec says should not exist (the real audit should materialize at resume from the operator's delivered response).
- **Discriminator (§4.1):** (a) — substantive impl content; self-contained resolution. → **§4.1 Class 2.**
- **§2.7.6 routing:** NOT a fork (impl-to-correct-spec). Blocking pre-merge impl fix.
- **Evidence:** `:1255` is unconditional and precedes all dispatch branches; `:1282-1289` is the `NoReturn` pause raise; spec `:3743` is the explicit pre-pause-no-audit rule.
- **Decision-vocabulary:** *decided* on sub-case 1 (a clear REJECT-shape miss); *proposing* on sub-case 2 — Reading 1: the pre-pause partial entry is a spec violation of §14.8.8.6 and should be suppressed on the escalate-bound path (audit materializes at resume); Reading 2: the impl intends the timeout `hitl.invocation.timed_out` span + a thin partial entry as a distinct timeout-observability record separate from the resume-time entry, in which case the divergence is acceptable but **must be documented** with a code comment citing §14.8.8.6 and why the timeout path differs from the §14.8.8.1-step-3 durable-async cell path. The reviewer cannot pick the intended reading from the text alone.
- **Resolution path:** for sub-case 1, fold into the F2-01 disposition-conditional fix (REJECT-terminating ⇒ REJECT entry). For sub-case 2, either suppress the pre-pause entry on the escalate-bound branch (Reading 1) or add the §14.8.8.6-citing rationale comment (Reading 2) — operator/impl picks the reading.

---

## Class 1 findings (minor — documentation / coverage drift)

### F1-01 — `validate_no_fail_open` has no production caller (register-don't-extend is honest, but the standalone guard is test-only)

- **Location:** `harness-cp/src/harness_cp/hitl_timeout_degradation.py:138-160` (`validate_no_fail_open`); referenced only by a *comment* at `hitl_gate_composer.py:1296`.
- **Finding (verified empirically, not inferred):** `grep` of `harness-{runtime,cp,od,cxa}/src` for `validate_no_fail_open` returns **zero production call-sites** (only the function def, its own docstrings, and one explanatory composer comment). This is **honest and correctly self-described**: the docstring (`:145-153`) states the per-tier operator-override surface "is NOT built at HEAD; when it lands it MUST call this at bootstrap." The non-vacuity of AC-1 is carried by the **live** carrier — `WebhookConfig.degradation_mode`'s `_refuse_fail_open` field-validator (`:181-191`), which DOES fire at construction (test `test_webhook_config_refuses_fail_open_degradation_mode` exercises a real raise). And the canonical `TIMEOUT_DEGRADATION_TABLE` structurally cannot carry `fail-open` (it assigns none). So AC-1's detect-then-refuse is genuine at every surface that *can* carry a mode today; `validate_no_fail_open` is a correctly-registered guard for the not-yet-built deployment-supplied-table surface. This matches spec §14.8.9 AC-1 (`Spec_Harness_Runtime_v1.md:3792`) + the register-don't-extend disposition.
- **Discriminator (§4.1):** does not affect substantive content; the posture is accurate. → **§4.1 Class 1** (informational; no fix required). Surfaced for transparency that the standalone guard is test-exercised only — acceptable per the spec's explicit register-don't-extend mandate.
- **Decision-vocabulary:** *decided.*
- **Resolution:** none required; the disposition is honest. (Confirms the operator-prompt's "is the register-don't-extend disposition honest" question: **yes, verified.**)

### F1-02 — Defensive fail-open comment claims unreachability that is structurally true but not enforced at the dispatch site

- **Location:** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1295-1298`.
- **Finding:** the comment states fail-open "is UNREACHABLE — refused at config/bootstrap … the dispatch never reaches a fail-open branch (defensively the REJECT here is the C10 fail-safe even if it did)." This is accurate **today** (the canonical table cannot yield `FAIL_OPEN`, and the dispatch has no `FAIL_OPEN` branch — it falls into the final REJECT). But the unreachability rests on the table-content invariant (F1-01), not on a dispatch-site guard. The fall-through-to-REJECT is the correct C10 fail-safe, so this is defensively sound. Noting only that "UNREACHABLE" is an invariant-dependent claim, not an enforced one.
- **Discriminator (§4.1):** drift-only (comment precision). → **§4.1 Class 1.**
- **Decision-vocabulary:** *decided.*
- **Resolution:** optional — none required; the fall-through REJECT is the correct fail-safe.

### F1-03 — AC-3 tests assert dispatch control-flow but NOT the persisted audit-entry shape (the coverage gap that admitted F2-01)

- **Location:** `harness-runtime/tests/test_lifecycle_hitl_gate_composer.py:1772-1937` (the new timeout-dispatch tests).
- **Finding:** the new tests are **genuinely non-vacuous at the dispatch level** (AC-3 satisfied for control-flow): `test_timeout_fail_closed_routes_to_reject` asserts `pytest.raises(HITLGateRejectedError)` (a real contrasting baseline — the v1.9 unconditional `HITLGateTimeoutError` would fail it); `test_timeout_escalate_secondary_channel_delivers_webhook_and_pauses` asserts `webhook.delivered` AND `pause_requested_flag.is_set()`; `test_timeout_persona_tier_none_residual_hard_timeout` asserts the residual `HITLGateTimeoutError`; the G4a test asserts the span attribute via real span inspection. **However**, NO test inspects the **persisted `CPAuditLedgerEntry`** — none asserts `response`/`rejection_reason_hash` on the audit write. This is exactly the blind spot that let F2-01/F2-02 land green: the dispatch is verified, the audit shape is not.
- **Discriminator (§4.1):** test-coverage gap on a substantive contract (the audit shape) — does not by itself misstate content; classify drift-adjacent. → **§4.1 Class 1** (coverage), but **load-bearing for F2-01's verification**: the F2-01 fix is not "done" until a test asserts the entry shape.
- **Decision-vocabulary:** *decided.*
- **Resolution:** add the persisted-entry-shape assertion described in the F2-01 remediation (REJECT-terminating ⇒ `response=="reject"` + populated `rejection_reason_hash`; residual ⇒ `response==""`).

---

## Findings considered and rejected (transparency)

1. **X-AL-3 anti-extension (always-check, skill checklist #8).** `git diff main...HEAD --stat` touches ONLY `harness-cp/src`, `harness-cp/tests`, `harness-runtime/src`, `harness-runtime/tests` — **zero `design-substrate/**` edits.** No silent design extension; Phase-7 posture honored. The fail-open *non*-extension is explicit and correct (register-don't-extend per §14.8.9 AC-1). **Clean.**
2. **AC-2 vocabulary reconciliation correctness.** `TimeoutDegradationKind` now = `{fail-closed, escalate-secondary-channel, fail-open}` (`hitl_timeout_degradation.py:60-83`), matching CP §21.8 + ADR-D5 §1.6 + CP §20.6 per spec `:3793`. `TIMEOUT_DEGRADATION_TABLE` corrected: solo→FAIL_CLOSED, team→ESCALATE_SECONDARY_CHANNEL, multi→FAIL_CLOSED (NOT abort-workflow). `test_timeout_degradation_kinds_vocab_a` + `test_timeout_table_multi_is_not_abort_workflow` verify by execution. **Sound.**
3. **Cross-spec drift grep — residual vocab-B / wrong-section §21.6 (skill checklist #2/#6 + posture C).** Grepped `harness-{cp,runtime,od}/src` + tests for all three vocab-B value-names and `§21.6`. Result: every residual `continue-as-reject`/`escalate-to-review-board`/`abort-workflow` string is an **intentional explanatory reference** documenting the reconciliation (e.g. `hitl_timeout_degradation.py:22,58-59`; test `:114-122` asserts `"abort-workflow" not in {k.value...}`) — NOT an active enum value. The `§21.6` cites in `harness-od/src/{eval_vs_runtime_gate,tail_keep_classification}.py` + `webhook_delivery_composer.py:434` are a **different, correct** §21.6 usage (validator-failure-span sampling — which IS what §21.6 means), correctly left intact; the sweep fixed only the timeout-degradation §21.6→§21.8 cites. **Correct discrimination; no missed drift.**
4. **AC-1 fail-open guard non-vacuity (detect-then-refuse).** `WebhookConfig._refuse_fail_open` (`:181-191`) raises `FailOpenDegradationRefusedError` (subclasses `Exception`, NOT `ValueError`, so it propagates raw — a deliberate typed-config-refusal surface per the spec deferred-list latitude on the error shape); `validate_no_fail_open` (`:138-160`) raises on any tier carrying FAIL_OPEN. Contrasting baselines real: `test_webhook_config_refuses_fail_open_degradation_mode` + `test_validate_no_fail_open_refuses_at_every_tier` (all 3 tiers) + `test_webhook_config_accepts_granted_degradation_modes` (the 2 granted modes pass). **Genuine detect-then-refuse** (see F1-01 for the register-don't-extend honesty note). **Sound.**
5. **Factoring of `_escalate_to_secondary_channel` (DRY, no behavior change).** The §14.8.8.1 4-bis durable-async sequence (`:777-826`) is factored and reused verbatim by both the 4-bis branch (`:1180-1191`) and the timeout escalate dispatch (`:1282-1289`). Step-by-step the factored body matches the inlined original (brief compose → idempotency_key → deliver → flag.set → raise signal); `WebhookDeliveryExhaustedError` propagation preserved. **No behavior regression in the factoring itself.**
6. **G4a span-attribute sourcing (U-RT-118).** `hitl.timeout.degradation_mode_applied` now sourced from the `on_hitl_timeout` consult (`:1230-1232,1247-1250`), not the literal `"default"`. Persona_tier-None correctly falls back to `"default"` (no resolvable policy). `test_timeout_degradation_mode_applied_from_consult` verifies per-tier by span inspection. **Sound.**
7. **Carrier-home / cross-axis import direction (skill axis-domain CP/CXA).** The composer imports `TimeoutDegradationKind` + `on_hitl_timeout` from `harness_cp.hitl_timeout_degradation` (`hitl_gate_composer.py:140-143`) — runtime→CP is the correct consumption direction (runtime composes against CP contracts). No reverse harness-cp→harness-runtime leak introduced. **Clean.**
8. **`on_hitl_timeout` nullable widening (U-CP-92).** `invocation: HITLInvocation | None` (`:238`); the body is persona_tier-only (`_ = invocation`); `test_on_hitl_timeout_accepts_none_invocation` covers the None path. The widening is faithful to the U-CP-92 plan signature and does not weaken any consumer (the only consumer passes `None`). **Sound.**
9. **Halt-route-split-AC (skill checklist #9).** The arc's ACs (AC-1 guard / AC-2 vocab / AC-3 dispatch) are all materializable at HEAD against the cleared spec — no AC bundles an unmaterializable atom. The fail-open dispatch path is correctly NOT materialized (register-don't-extend), which is the right split, not a silent absorption. **Clean.**

---

## Disposition

**APPROVE-WITH-FINDINGS.** Per §4.1: no Class-3 findings → no phase re-opening; the highest severity is Class-2 (F2-01, F2-02) → current-phase **impl** revision (not ADR/spec revision — the spec is correct). **Both Class-2 findings are blocking pre-merge fixes**, not optional polish:

- **F2-01 (PRIMARY) + F2-02 sub-case 1** — the fail-closed AND escalate-degraded-when-unbound timeout paths must emit a REJECT-shaped step-4h entry (`response="reject"` + `rejection_reason_hash=sha256("timeout-fail-closed")`, `gate_level=AUTO`), placed after the mode dispatch; keep the partial `response=""` entry only for the residual hard-timeout path. **Plus** the missing persisted-entry-shape test (F1-03).
- **F2-02 sub-case 2** — resolve the escalate-bound→pause pre-pause partial-entry vs §14.8.8.6 (suppress on the bound path, OR document the intended timeout-observability divergence with a §14.8.8.6-citing comment). Operator/impl picks the reading.

**§2.7.6 fork classification of the whole arc: none.** Every finding is impl-to-correct-spec; no `design-substrate` revision is owed. Do not open a spec or ADR arc for any of these.

**What is sound and merge-ready once F2-01/F2-02/F1-03 land:** AC-2 vocab reconciliation (multi NOT abort-workflow), AC-1 fail-open detect-then-refuse at every live carrier, AC-3 control-flow dispatch, the `_escalate_to_secondary_channel` factoring, the G4a span sourcing, the U-CP-92 nullable widening, the §21.6→§21.8 sweep (correctly leaving validator-§21.6 intact), and X-AL-3 (zero design-substrate edit).

---

*Reviewer: harness-adversarial-reviewer (genuine skill adoption). Decorrelated check: advisor() consulted on the full transcript pre-verdict — concurred on (b), sharpened the F2-02 multi-path remediation + the taxonomy disambiguation + the empirical grounding of F1-01. All cites grounded by direct read at session-time per §13.1.*
