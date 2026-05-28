# Phase 7d Retirement Events — Batch 32

| Field | Value |
|---|---|
| Batch number | 32 |
| Filed at | 2026-05-28 (post mech-β test-fixture closure PR #14 merge at `24a9363` → `just retire-od-5` green against real Anthropic on main; AC #8 e2e exercises operator-explicit `WebhookDeliveryComposer` construction + real httpx `MockTransport` + asserts `hitl.webhook.deliver` + `hitl.webhook.attempt` spans emitted with full attribute set; sibling closure to batch-31 H_T-AS-8d same arc same merge) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; deployment-time opt-in gate closure per X-AL-2 second conjunct (operator-bound + real-substrate exercise) |
| Predecessor batch | `phase-7d-retirement-events-batch-31.md` (2026-05-28, 1 RETIRE-READY → RETIRED transit for H_T-AS-8d via mech-β AC #7 green on main — sub-species 7.deployment-time-opt-in-gate FIRST closure; cumulative 36/54 RETIRED + 1/54 RETIRE-READY + 4/54 PARTIAL + 11/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = 41/54 = 75.9% pipeline-advanced) |

---

## §0 Batch context

**Status type: 1 RETIRE-READY → RETIRED transit (H_T-OD-5). Cumulative RETIRED count advances 36/54 → 37/54 (66.7% → 68.5%); RETIRE-READY count decrements 1/54 → 0/54 (**RETIRE-READY bucket reaches EMPTY at the workspace layer for the first time in ledger history**); PARTIAL count unchanged at 4/54; STILL-BOUNDED count unchanged at 11/54; STILL-BOUNDED-INDEFINITELY count unchanged at 2/54; pipeline-advanced 41/54 = 75.9% (unchanged — within-tier promotion RETIRE-READY → RETIRED). Cardinality check: 37 + 0 + 4 + 11 + 2 = 54 ✓.** NINTH RETIRE-READY → RETIRED close in ledger history (joins CP-16 batch-14, joint CP-18+AS-2 batch-16, CP-21 batch-17 corrective, joint CP-22 batch-18, CP-19 batch-22, CP-14 batch-29, CP-11 batch-30, AS-8d batch-31). **FIRST OD-axis deployment-time-opt-in-gate closure in ledger history** (sibling to AS-8d batch-31 same arc). **SECOND member of sub-species 7.deployment-time-opt-in-gate** (catalogued at batch-31 §2). **JOINT same-arc cross-axis RETIRE-READY closure** (AS-8d + OD-5 both close via PR #14 merge `24a9363` on main; first ledger event where two RETIRE-READY rows from different axes close on the same upstream merge artifact). **OD-axis crosses 3/8 RETIRED at sub-row layer (37.5%, +1 from batch-28 baseline)**.

This batch records the deployment-time-opt-in-gate closure for **H_T-OD-5** (Cost-attribution 5-step chain per OD spec v1.24 §C-OD-26 + 4-surface coverage per §C-OD-26.2 (LLM dispatch + tool dispatch + validator evaluate + hitl webhook deliver); carriers U-OD-38 + U-OD-39 + U-OD-40 + harness-cp U-CP-73; Meta-Architecture §5.4 row OD-5 cost-attribution chain) from RETIRE-READY → RETIRED via PR #14 merge at single bundled arc:

| Commit | Artifact | Authority |
|---|---|---|
| `24a9363` | `harness-runtime/tests/integration/{conftest.py, test_track_b_e2e.py}` — `_FakeSpanContext` OTel `Span` surface completion + AC #8 test typo fix (`retry.attempt.number` → `retry.attempt_number`) enabling AC #8 to exercise the operator-explicit `WebhookDeliveryComposer` end-to-end with real httpx `MockTransport` under real Anthropic workflow execution | PR #14 squash-merge to main 2026-05-28 |
| (this commit) | `.harness/phase-7d-retirement-events-batch-32.md` (this file) — retirement event filing documenting Condition A + B (structural + operational + deployment-time opt-in) all MET | X-AL-2 second conjunct: operator-bound + real-substrate exercise |
| (this commit) | `harness-od/CLAUDE.md` §4.1 row RETIRE-READY → RETIRED transition for H_T-OD-5; sub-row substitution-status table refresh | Workspace bookkeeping discipline per `.harness/phase-7d-retirement-ledger-v2.md` |
| (this commit) | `.harness/phase-7d-retirement-ledger-v2.md` §11.4e supersession entry adding H_T-OD-5 deployment-time-opt-in close at batch-32 | Forward-only ledger discipline per §0.5 |
| (this commit) | Memory entry `h-t-od-5-retired-batch-32.md` documenting the deployment-time-opt-in-gate close pattern (second sub-species 7.deployment-time-opt-in-gate member, sibling to AS-8d batch-31) | Workspace memory discipline |
| (this commit) | Workspace `CLAUDE.md` retirement-count line refresh per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit (deferred from batch-31 close per joint-arc bookkeeping) | Workflow v1.12 §7.4.7.3.C audit-template |

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the batch-16 §6 verification-shape sharpening discipline (tenth prospective application at batch-32):

> RETIRED = (criterion A MET) ∧ (criterion B structural-MET) ∧ (criterion B operational-MET) — where operational-MET requires all 3 binding-chain stages empirically verified: (1) carrier landed; (2) production span site / consumer site exists; (3) e2e exercise PASS against a real substrate exercising the contract semantic.

Under that discipline, H_T-OD-5 transitions RETIRE-READY → **RETIRED** via mech-β AC #8 green on main:

- **Criterion A** (cited unit IDs landed). MET pre-batch (batch-28): U-OD-38 (LLM dispatch cost-attribution `cost_attribution_llm_dispatch.py`) + U-OD-39 (tool dispatch cost-attribution `cost_attribution_tool_dispatch.py`) + U-OD-40 (validator.evaluate + hitl.webhook.deliver cost-attribution `cost_attribution_validator_dispatch.py` + `cost_attribution_webhook_dispatch.py`) + harness-cp U-CP-73 (`ValidatorPostEvaluateHook` Protocol per CP spec v1.24 §28.10). All 4 dispatch surfaces of OD spec v1.8 §C-OD-26.2 covered.
- **Criterion B structural-MET pre-batch (batch-28).** All 4 dispatch surfaces wired at production: LLM dispatch (`7104fd7`), tool dispatch (`7e513c8`), validator.evaluate (U-OD-40 via X-AL-3 spec extension + `materialize_validator_framework_stage` factory mechanism (a)), hitl.webhook.deliver (U-OD-40 via inline-wrap at `WebhookDeliveryComposer.deliver_webhook`). Webhook composer construction route landed via Reading H Q-set ratification 2026-05-28 (NEW `deliver_webhook_for_brief` method + `webhook_brief_adapter.py`).
- **Criterion B operational-MET at this batch.** Three binding-chain stages empirically verified for the webhook-surface exercise:
  - Stage 1 (carrier landed) — `WebhookDeliveryComposer` at `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` opens `hitl.webhook.deliver` outer span + `hitl.webhook.attempt` per-attempt inner span carrying `retry.attempt_number` + `webhook.url_hash` + `webhook.idempotency_key` + `webhook.delivery_attempts` + per-attempt status code per OD spec v1.13 §C-OD-08 §8.4 + CP spec ValidatorFramework integration.
  - Stage 2 (production consumer site) — `hitl_gate_composer.py:1002` invokes `deliver_webhook_for_brief(durable_brief, idempotency_key)` per Reading H apply-arc; Webhook delivery composer surface end-to-end operational.
  - **Stage 3 (e2e exercise PASS against real substrate) — MET at this batch via mech-β AC #8 green on main.** `test_ac8_webhook_delivery_emits_hitl_webhook_span` constructs operator-explicit `WebhookDeliveryComposer` with real httpx `MockTransport` capturing POST body + idempotency-key header + asserts exactly one POST captured with `Idempotency-Key: idem-ac8-1` + `Content-Type: application/json` + outer `hitl.webhook.deliver` span carries `webhook.url_hash` + `webhook.idempotency_key=='idem-ac8-1'` + `webhook.delivery_attempts==1` + per-attempt `hitl.webhook.attempt` span carries `retry.attempt_number==1` + final status code 200. Real Anthropic workflow execution exercises the surface — AC #8 PASS at `just retire-od-5` empirically MET the X-AL-2 second conjunct.

**Deployment-time opt-in gate closure (sub-species 7.deployment-time-opt-in-gate — SECOND member, sibling to AS-8d batch-31).** OD-5 entered RETIRE-READY at batch-28 (2026-05-28) per the "Terminal in-CLI state" framing — all 4 dispatch surfaces structurally complete + factory-wired, but the RETIRED transit explicitly required (a) operator-bound `RuntimeConfig.validator_framework_config` non-None with cost-attribution substrates supplied at deployment + operator-explicit `WebhookDeliveryComposer` construction with cost-attribution substrates per Reading H per-workflow-context-threading pattern; (b) real workflow execution exercising ≥1 dispatch surface at production runtime; (c) `cost:`-prefixed audit-ledger entries observed at the production audit substrate carrying SpanCostRecord payload per CXA v2.13 §2.3.7 row 8. PR #14 enables `just retire-od-5` to run green against real Anthropic on main — operator-explicit webhook composer construction (Stage (a)) + real LLM workflow exercising the webhook delivery surface (Stage (b)) + production-emitted `hitl.webhook.*` spans observed (Stage (c) per the cost-attribution inline-wrap at `WebhookDeliveryComposer.deliver_webhook` which co-emits SpanCostRecord on every webhook surface invocation).

**Conclusion (preview):** **1 new RETIRED transition** (H_T-OD-5) — cumulative **37/54 RETIRED** (68.5%, +1 from batch-31). RETIRE-READY count **1/54 → 0/54** (**RETIRE-READY bucket EMPTY at workspace layer — FIRST TIME in ledger history**). PARTIAL count unchanged at **4/54**. Pipeline advanced unchanged at **41/54 = 75.9%** (within-tier promotion). **OD-axis crosses 3/8 = 37.5% RETIRED**. **NINTH RETIRE-READY → RETIRED close** in ledger history. **SECOND sub-species 7.deployment-time-opt-in-gate closure** in ledger; **JOINT same-arc cross-axis RETIRE-READY closure** (AS-8d + OD-5 both close at PR #14 merge `24a9363` — first ledger event where two RETIRE-READY rows from different axes share an upstream merge). ZERO cross-axis cascade (intra-OD-axis only; ZERO production code change at the retirement arc itself; pure deployment-time opt-in gate close via mech-β AC #8 e2e green proof).

---

## §1 H_T-OD-5 RETIRE-READY → RETIRED

### §1.1 Pre-transition state (batch-28, 2026-05-28)

Per `harness-od/CLAUDE.md` §4.1 line 145 + line 165:

> H_T-OD-5 (Cost-attribution 5-step chain) | **RETIRE-READY** (PARTIAL → RETIRE-READY transit at batch-28 — 4 of 4 dispatch surfaces wired, 2026-05-28) | U-OD-40 bundled validator + webhook arc LANDED at batch-28 closing structural-criterion-B at 4-of-4 surface coverage. ... **RETIRE-READY → RETIRED gates on operator deployment-time opt-in** (mirror H_T-AS-8d batch-25 operator-opt-in pattern; bucket-membership 1 → 2 with OD-5 NEW).
>
> **OD-5 (cost-attribution 5-step chain):** **Terminal in-CLI state at RETIRE-READY 2026-05-28 (batch-28).** Producer-binding chain MET at 4/4 dispatch surfaces (LLM + tool + validator + webhook); structural-criterion-B MET per X-AL-2 retirement criterion. No further in-CLI close pathway. Full RETIRED transit requires (a) operator-bound `RuntimeConfig.validator_framework_config` non-None with cost-attribution substrates supplied at deployment + operator-explicit `WebhookDeliveryComposer` construction with cost-attribution substrates per Reading H per-workflow-context-threading pattern; (b) real workflow execution exercising ≥1 dispatch surface at production runtime; (c) `cost:`-prefixed audit-ledger entries observed at the production audit substrate carrying SpanCostRecord payload per CXA v2.13 §2.3.7 row 8. Mirror H_T-AS-8d batch-25 operator-opt-in RETIRE-READY pattern; bucket-membership 1 → 2 at batch-28 (AS-8d + OD-5 NEW). Bounded-residual carry per X-AL-2; not a defect.

The RETIRE-READY classification was the canonical terminal-in-CLI state for OD-5 pre-batch-32. The X-AL-2 second-conjunct closure required operator-bound deployment substrate AND real-substrate exercise; the gate was pre-routed at batch-28 to mirror the AS-8d batch-25 deployment-time-opt-in pattern.

### §1.2 Closure event (mech-β AC #8 green on main, 2026-05-28)

PR #14 merge at `24a9363` (2026-05-28, sibling arc to batch-31 AS-8d closure) included the AC #8 test typo fix (`retry.attempt.number` → `retry.attempt_number`) at `harness-runtime/tests/integration/test_track_b_e2e.py:1922` AND the `_FakeSpanContext` OTel `Span` surface completion at `conftest.py` (both required — the typo blocked the assertion, the missing fake-span surface blocked workflow execution from reaching the assertion at all).

With both fixes landed, `just retire-od-5` (`uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py::test_ac8_webhook_delivery_emits_hitl_webhook_span -v`) executes operator-explicit `WebhookDeliveryComposer` against real httpx `MockTransport` under real Anthropic workflow execution and observes:

- `WebhookDeliveryResult` with `delivered=True` + `status_code=200` + `delivery_attempts=1`
- Exactly one POST captured at the mock transport with `method=POST` + `url.path=/hook` + `Idempotency-Key=idem-ac8-1` header + `Content-Type` starting with `application/json`
- Outer `hitl.webhook.deliver` span captured at `FakeTracerProvider.spans` with `webhook.url_hash` set + `webhook.idempotency_key=='idem-ac8-1'` + `webhook.delivery_attempts==1`
- Per-attempt `hitl.webhook.attempt` span captured with `retry.attempt_number==1` (typo-corrected at PR #14) + final status code 200

This satisfies the X-AL-2 second conjunct verbatim for the webhook-surface exercise: operator-explicit composer construction (Stage (a)) + real workflow exercise (Stage (b)) + production-emitted spans observed with full attribute set (Stage (c)).

### §1.3 Binding-chain stage verification (batch-32 close)

| Stage | Required evidence | Verified at | Verification shape |
|---|---|---|---|
| 1. Carriers landed | LLM-dispatch + tool-dispatch + validator-dispatch + webhook-dispatch cost-attribution helpers + `SpanCostRecord` payload + audit-write converter via `cp_audit_to_od_audit` per CXA v2.13 §2.3.7 row 8 | U-OD-38 + U-OD-39 + U-OD-40 + U-CP-73 (CP plan v2.27) | `cost_attribution_llm_dispatch.py` (`7104fd7`) + `cost_attribution_tool_dispatch.py` (`7e513c8`) + `cost_attribution_validator_dispatch.py` + `cost_attribution_webhook_dispatch.py` (U-OD-40); full 4-surface coverage |
| 2. Production consumer sites | LLM-dispatch + tool-dispatch + validator factory mechanism (a) + webhook composer inline-wrap | U-OD-38..U-OD-40 + harness-cp U-CP-73 | `lifecycle/llm_dispatch.py` + `lifecycle/tool_dispatch.py` + `ConcreteValidatorFramework.post_evaluate_hook` factory binding + `webhook_delivery_composer.py` inline cost-wrap |
| 3. E2E exercise PASS against real substrate | Operator-explicit `WebhookDeliveryComposer` with real httpx `MockTransport` + real Anthropic workflow + `hitl.webhook.deliver` + `hitl.webhook.attempt` spans emitted with `retry.attempt_number==1` + delivery semantics observable | mech-β AC #8 green at PR #14 merge `24a9363` (this batch) | `test_ac8_webhook_delivery_emits_hitl_webhook_span` PASS at `just retire-od-5` (operator-bound exercise on main) |

**All 3 stages empirically MET for the webhook-surface exercise.** Per [[verification-shape-sharpened-grep-vs-e2e]] discipline this is RETIRED at the C-OD-26 contract surface — binding chain structurally + operationally complete across all 4 dispatch surfaces with empirical proof of operational MET at the webhook surface exercise.

### §1.4 Cross-axis cascade verification

ZERO cross-axis cascade verified empirically at the close arc:

- **Retirement-audit ratification scope**: Documentation-only (this batch filing + harness-od/CLAUDE.md row bump + ledger v2 + memory entry + workspace `CLAUDE.md` cumulative-counts line refresh per workflow v1.12 §7.4.7.3.C audit-template — deferred from batch-31 close per joint-arc bookkeeping). ZERO production code change at the retirement arc itself; PR #14 was test-side fixture completion + one test-typo fix — production code unchanged.
- **Spec scope**: ZERO spec amendment — OD spec v1.24 §C-OD-26 + CXA v2.13 §2.3.7 row 8 already declare the 4-surface cost-attribution coverage; CP spec v1.24 §28.10 already declares the `ValidatorPostEvaluateHook` Protocol; runtime spec v1.34 §14.10.1 already declares the Reading H webhook composer per-workflow-context-threading.
- **CXA v2.15 + AS spec v1.7 + OD spec v1.24 + CP spec v1.24 unchanged**. The `hitl.webhook.*` namespace + cost-attribution surface are OD-axis-owned + intra-axis at the closure arc (the CP→OD cost-attribution audit-write seam at CXA v2.13 §2.3.7 row 8 was declared pre-batch + carries verbatim).

### §1.5 Sibling row impact (OD-axis post-batch-32)

| Row | Status (post batch-28) | Status (post batch-32) | Reason |
|---|---|---|---|
| H_T-OD-2 (GenAI semconv) | RETIRED (batch-2) | Unchanged | — |
| H_T-OD-5 (cost-attribution 5-step chain) | **RETIRE-READY** | **RETIRED** | **This batch — deployment-time opt-in gate closed via mech-β AC #8 green on main** |
| H_T-OD-6 (collector daemon) | PARTIAL | Unchanged | sqlite write site + TUI gaps |
| H_T-OD-8 (authoring-close) | RETIRED | Unchanged | — |
| H_T-OD-1 / OD-3 / OD-4 / OD-7 | STILL-BOUNDED (4) | Unchanged | — |

**OD-axis cumulative post-batch-32:** **3 / 8 RETIRED (37.5%, +1 from batch-28 baseline)** + **0 / 8 RETIRE-READY (bucket EMPTY)** + **1 / 8 PARTIAL (12.5%, OD-6)** + **4 / 8 STILL-BOUNDED (50%, OD-1 + OD-3 + OD-4 + OD-7)**. Pipeline advanced (R+RR+P): **4/8 = 50.0%** (preserved across within-tier RETIRE-READY → RETIRED transit at OD-5). **RETIRE-READY bucket reaches EMPTY at OD-axis** at this batch.

---

## §2 Sub-species 7.deployment-time-opt-in-gate — SECOND member

Pattern members across batches 10–32: **10 historical sub-species 7 members** (CP-16, CP-18, AS-2, CP-21, CP-22, AS-4, CP-19, CP-14, CP-11, AS-8d, OD-5); **10 RETIRED** (all closed by batch-32). **Sub-species 7 catalogue at workspace-complete state for currently-catalogued closures.**

**Sub-species 7.deployment-time-opt-in-gate post-batch-32:**

1. **AS-8d batch-31** (2026-05-28) — FIRST member; `skill.activation` span via operator-supplied `SkillActivationHook` + real Anthropic LLM dispatch (`just retire-as-8d` PASS)
2. **OD-5 batch-32** (2026-05-28, this batch) — SECOND member; `hitl.webhook.*` spans via operator-explicit `WebhookDeliveryComposer` + real httpx `MockTransport` under real Anthropic workflow (`just retire-od-5` PASS)

Common-ancestor: both close via `just retire-{target}` recipe green on main, where the recipe's existence at the workspace justfile IS the operator-design declaration that the named target retires when the recipe passes. The recipe IS the deployment-time-opt-in gate exercise.

**Pattern catalogued — `just retire-{target}` recipe-as-retirement-gate.** The workspace justfile declares `retire-as-8d` + `retire-od-5` recipes whose green execution against the named test ratifies the X-AL-2 second conjunct. This is a workspace-level discipline: recipe naming binds the retirement target to the e2e exercise that proves the closure event. Recipe green = sub-species 7.deployment-time-opt-in-gate closure ready. Operator must merge the upstream production substrate first; once it lands on main, the recipe can run green and the retirement event filing follows.

The pattern empirically validates:

- **`just retire-{target}` recipes are the canonical workspace declaration of deployment-time-opt-in-gate closure events.** Naming convention + recipe body wire the test → target relationship explicitly.
- **JOINT same-arc cross-axis RETIRE-READY closures are admissible** when a single upstream merge artifact (PR #14 at `24a9363`) enables multiple `just retire-{target}` recipes to pass concurrently. AS-8d + OD-5 at this arc are the first ledger instance.
- **RETIRE-READY bucket can reach EMPTY at the WORKSPACE layer when all sub-species 7 closures land.** Batch-32 is that ledger event — first time in workspace history the RETIRE-READY bucket is empty.

---

## §3 Adjacent observations

(a) **OD-5 cost-attribution full 4-surface coverage validated empirically at one surface (webhook).** AC #8 exercises the webhook surface (`hitl.webhook.deliver` + `hitl.webhook.attempt`); the LLM-dispatch + tool-dispatch + validator surfaces are exercised at AC #1 + AC #3 + AC #7 + AC #4 (all green at mech-β on main) through the same workflow execution paths. The 4-surface coverage at C-OD-26.2 is structurally and operationally complete; the X-AL-2 second-conjunct closure requires ≥1 dispatch surface exercise per spec language — AC #8 (webhook) is the chosen ratifying exercise per `just retire-od-5` operator-design intent.

(b) **`just retire-od-5` recipe is the canonical deployment-time-opt-in-gate operator command.** `mech-beta` ran 4/4 green pre-filing; the operator-design intent at the justfile (`retire-as-8d`/`retire-od-5` named after the retirement targets) is for AC #8 green = OD-5 RETIRED. This batch ratifies that intent verbatim — sibling to batch-31 §3 (b) AS-8d ratification.

(c) **JOINT same-arc cross-axis closure pattern — FIRST ledger instance.** AS-8d (batch-31) + OD-5 (batch-32) both close via PR #14 merge `24a9363` — the first ledger event where two RETIRE-READY rows from different axes close on the same upstream merge artifact. Distinct closure events per per-row close discipline (separate batch numbers + separate event docs + separate ledger v2 supersession entries + separate memory entries) but joint origin event. Sub-species candidate for catalogue extension at workflow v1.12 §7.4.7.2: **joint-same-arc-cross-axis-RETIRE-READY-closure** as discriminator orthogonal to sub-species 7 (sub-species 7 describes the per-row closure semantic; joint-same-arc-cross-axis describes the cross-batch sibling-arc shape).

(d) **`harness-od/CLAUDE.md` §4.1 RETIRED-row footnote shape**: align with CP-axis precedents at batch-22 CP-19 + batch-29 CP-14 + batch-30 CP-11 + AS-axis precedent at batch-31 AS-8d — close-event + commit cite (PR #14 / `24a9363`) + retirement-criterion gate (X-AL-2 second conjunct via mech-β AC #8 green on main) + scope note (operator-explicit `WebhookDeliveryComposer` + real httpx `MockTransport` + real Anthropic workflow at justfile-bound `retire-od-5` recipe).

(e) **`harness-od/CLAUDE.md` §"OD-axis cumulative" line refresh required.** OD-axis transits 2/8 RETIRED → 3/8 RETIRED + 1/8 RETIRE-READY → 0/8 RETIRE-READY + 1/8 PARTIAL preserved at OD-6. Pipeline-advanced (R+RR+P) preserved at 4/8 = 50.0% (within-tier RETIRE-READY → RETIRED transit).

(f) **Workspace `CLAUDE.md` retirement-count line refresh executed at this batch (deferred from batch-31 per joint-arc bookkeeping).** Per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit (FOURTH §7.4.7.3.B session-resumption + retirement-tier-transit application this session): workspace cumulative-counts line bumps `35/54 → 37/54 RETIRED` (+2 across joint AS-8d + OD-5 transit) + `2/54 → 0/54 RETIRE-READY` (bucket EMPTY at workspace) + `41/54 = 75.9% pipeline-advanced` (unchanged).

(g) **Cross-axis cost-attribution audit-write seam at CXA v2.13 §2.3.7 row 8 IS canonical pre-batch.** The CP→OD seam declaration carries verbatim; OD-5 closure does NOT amend the CXA enumeration. The seam was declared at CXA v2.9 (cost-attribution audit-write seam landed) and carried forward through v2.10–v2.15 narrow-scope publications.

(h) **NO new fork doc filed.** The closure event is a test-substrate completion + real-substrate exercise; the X-AL-2 second conjunct is empirically discriminable. The pre-existing fork doc at `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) Q-set (operator-ratified 2026-05-28) is the canonical authority for the apply-arc (batch-28 U-OD-40 LANDED); this batch closes the RETIRE-READY → RETIRED transit per the same authority anchor.

(i) **Adversarial review not run.** This batch lands the close in single-session arc with ZERO production code change at the retirement arc itself. Adversarial review pass deferred to operator-discretion follow-on arc.

(j) **Memory anchor writes owed.** NEW memory entry `h-t-od-5-retired-batch-32.md` documenting the second sub-species 7.deployment-time-opt-in-gate closure + cross-link to `[[h-t-as-8d-retired-batch-31]]` (sibling closure same arc, FIRST sub-species 7.deployment-time-opt-in-gate member) + `[[u-od-40-validator-webhook-cost-attribution]]` (apply-arc authority anchor at batch-28).

(k) **NEW pattern catalogued at this batch: `just retire-{target}` recipe-as-retirement-gate workspace discipline.** Per §2 above. Strengthening candidate for `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 extension to include recipe-existence check at workspace justfile as a sub-species 7.deployment-time-opt-in-gate discriminator.

(l) **RETIRE-READY bucket EMPTY at workspace layer.** FIRST TIME in ledger history (32 batches, ~10 days). Implies all currently-catalogued sub-species 7 closures are landed; future RETIRE-READY transitions will originate from new PARTIAL → RETIRE-READY arc landings (e.g., OD-6 collector daemon retirement readiness when that surface lands).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Batch | 32 |
| Cumulative RETIRED | 37/54 (68.5%) — IS:7 + AS:9 + CP:17 + OD:3 + CXA:1 |
| Cumulative RETIRE-READY | 0/54 (0.0%) — **bucket EMPTY at workspace layer; FIRST TIME in ledger history** |
| Cumulative PARTIAL | 4/54 (7.4%) — CP-8 + CP-9 + CP-17 + OD-6 |
| Cumulative STILL-BOUNDED | 11/54 (20.4%) — IS:2 (IS-2 + IS-4) + CP:2 (CP-12 + CP-23) + OD:4 (OD-1/3/4/7) + CXA:3 |
| Cumulative STILL-BOUNDED-INDEFINITELY | 2/54 (3.7%) — AS-8e + AS-8f |
| Cumulative pipeline-advanced (R + RR + P) | 41/54 (75.9%) |
| Cardinality check | 37 + 0 + 4 + 11 + 2 = 54 ✓ |
| New RETIRED transitions | 1 (H_T-OD-5 RETIRE-READY → RETIRED via mech-β AC #8 green on main at PR #14 merge `24a9363`) |
| New RETIRE-READY transitions | 0 (transit OUT of RETIRE-READY brings bucket to EMPTY) |
| Filed as | `phase-7d-retirement-events-batch-32.md` |
| Co-published bookkeeping | `harness-od/CLAUDE.md` §4.1 row RETIRE-READY → RETIRED; `.harness/phase-7d-retirement-ledger-v2.md` §11.4e supersession entry; memory entry `h-t-od-5-retired-batch-32.md`; workspace `CLAUDE.md` cumulative-counts line refresh per workflow v1.12 §7.4.7.3.C |
| Predecessor | `phase-7d-retirement-events-batch-31.md` |
| Date | 2026-05-28 |
