# Phase 7d Retirement Events — Batch 28

| Field | Value |
|---|---|
| Batch number | 28 |
| Filed at | 2026-05-28 (post H_T-OD-5 within-PARTIAL surface-coverage advance at batch-27; same-session U-OD-40 validator + webhook bundled atomic unit arc landing) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; U-OD-40 production binding empirically MET via integration test at `test_u_od_40_validator_webhook_integration.py` (1 validator dispatch + 1 webhook dispatch → 2 audit-ledger entries with per-surface action_id-prefix discrimination) |
| Predecessor batch | `phase-7d-retirement-events-batch-27.md` (2026-05-28, H_T-OD-5 within-PARTIAL surface-coverage advance 1/4 → 2/4 at U-OD-39 tool dispatch landing) |

---

## §0 Batch context

**Status type: 1 state transit (H_T-OD-5 PARTIAL → RETIRE-READY).** Closure-event-class: bundled producer-site landing closing the remaining 2 of 4 billable dispatch surfaces enumerated at OD spec v1.8 §C-OD-26.2 (validator.evaluate + hitl.webhook.deliver). With this batch, OD-5 surface coverage transits 2/4 → 4/4 = 100% wired across all enumerated producer-site contracts. Structural-criterion-B MET at LLM + tool + validator + webhook all 4 surfaces wired empirically via integration tests. Full RETIRED transit gates on operator deployment-time opt-in (mirror H_T-AS-8d operator-opt-in RETIRE-READY pattern).

**X-AL-3 Class 1 fork applied + ratified at this arc.** Validator surface binding required spec extension at harness-cp: NEW `ValidatorPostEvaluateHook` Protocol surface authored at CP spec v1.24 §28.10 per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) operator-ratified 2026-05-28 Q-set (Q1=B Hook Protocol over decorator; Q2=harness-cp Protocol home; Q3=best-effort swallow; Q4=optional ctor param None default; Q5=β NO new CXA edge). Mirror precedent: U-RT-101 SkillActivationHook (`SkillActivationHook` Protocol authored at harness-runtime; runtime spec v1.32 §14.17; class_1_fork_as_8d Reading B 2026-05-28).

**Counting math (post-batch-27):**

Pre-batch-28:
- Workspace ledger cumulative: 33/54 RETIRED + 1/54 RETIRE-READY (AS-8d) + 5/54 PARTIAL (CP-8 + CP-9 + CP-11 + CP-14 + CP-17 + OD-5) + 13/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = **39/54 = 72.2% pipeline-advanced**
- OD-axis: 2/8 RETIRED + 2/8 PARTIAL (OD-5 + OD-6) + 4/8 STILL-BOUNDED (OD-1/3/4/7); OD-5 had 2/4 surfaces wired (LLM + tool)

Post-batch-28 (H_T-OD-5 PARTIAL → RETIRE-READY transit):
- Workspace ledger cumulative: 33/54 RETIRED + **2/54 RETIRE-READY** (AS-8d + OD-5) + **4/54 PARTIAL** (CP-8 + CP-9 + CP-11 + CP-14 + CP-17 — OD-5 transits out) + 13/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = **39/54 = 72.2% pipeline-advanced (unchanged — within-tier transit PARTIAL → RETIRE-READY does NOT change pipeline-advanced count)**
- OD-axis: 2/8 RETIRED + **1/8 RETIRE-READY (OD-5 NEW)** + 1/8 PARTIAL (OD-6 only) + 4/8 STILL-BOUNDED (OD-1/3/4/7); **OD-5 now has 4/4 surfaces wired (LLM + tool + validator + webhook)**
- Surface-coverage view at OD-5: 100.0% wired (was 50.0% post-batch-27); pipeline path to RETIRED: operator deployment-time opt-in at production runtime (mirror AS-8d pattern)

**Design-substrate edits at batch-28:**
- `Spec_Control_Plane_v1_24.md` NEW (X-AL-3 spec extension at §28.10 ValidatorPostEvaluateHook Protocol)
- `Implementation_Plan_Control_Plane_v2_27.md` NEW (NEW U-CP-73 singleton-extension unit)
- `Implementation_Plan_Operational_Discipline_v2_23.md` NEW (single-unit-body amendment at U-OD-40 LANDED status)
- `Implementation_Plan_Harness_Runtime_v2_29.md` NEW (single-unit-body amendment at U-RT-84 cost-attribution hook construction AC)
- `harness-od/CLAUDE.md` H_T-OD-5 row refresh — 4 of 4 surfaces wired + RETIRE-READY transit + operator-opt-in pattern citation
- `harness-cp/CLAUDE.md` §1.1 + §2.3 row refresh — CXA outbound count preserved (Q5=β no new edge); CP spec + plan version bumps
- `.harness/phase-7d-retirement-events-batch-28.md` NEW (this file)
- Workspace `CLAUDE.md` §2.3 + §2.4 row bumps (CP spec v1.24 + CP plan v2.27 + OD plan v2.23 + runtime plan v2.29)

---

## §1 Retirement event — H_T-OD-5 PARTIAL → RETIRE-READY transit (validator + webhook surfaces wired)

**Substitution identity:** H_T-OD-5 (Cost-attribution 5-step chain at billable spans per OD spec v1.8 §C-OD-26).

**Pre-batch state:** PARTIAL. Surface coverage 2/4 (LLM via U-OD-38 at `7104fd7`; tool via U-OD-39 at `7b09a02`). 2 surfaces remaining: validator.evaluate + hitl.webhook.deliver per OD spec v1.8 §C-OD-26.2 row enumeration.

**Closure-event lineage:**

1. **Empirical orientation + dep-graph constraint discovery** — Pre-substantive `harness-cp/pyproject.toml` grep confirmed: harness-cp depends on harness-core + harness-as ONLY (NOT harness-od). Therefore cost-attribution helper importing harness_od types cannot home at harness-cp directly. Same constraint that drove U-OD-39 to wrap inside RuntimeToolDispatcher (harness-runtime). Two structural patterns satisfy U-OD-40 AC #1: (A) wrap-at-factory decorator at harness-runtime (transparent; ZERO harness-cp spec extension); (B) hook Protocol at harness-cp + supplied at harness-runtime via factory binding (explicit observability seam; H_T design extension under X-AL-3).

2. **Operator AskUserQuestion 2026-05-28** — Q-set ratified. Q1=B Hook Protocol over A decorator (rationale: symmetry with U-RT-101 SkillActivationHook + explicit observability seam preference at harness-cp surface). Q2=harness-cp Protocol home (consumer-axis primacy). Q3=best-effort swallow per `_attribute_tool_cost_best_effort` precedent. Q4=optional ctor param None default. Q5=β NO new CXA edge.

3. **X-AL-3 Class 1 fork doc filed + ratified** — `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` at `95732d5`. Hook Protocol pattern (B) ratified despite assistant's initial decorator recommendation (per advisor pre-substantive consultation surfaces architectural trade-off; operator decides).

4. **CP spec extension** — CP spec v1.23 → v1.24 NEW §28.10 ValidatorPostEvaluateHook Protocol authoring at `b4ba823` (delta-only-spec-file convention; v1.23 + earlier preserved verbatim). 7 sub-sections authored: §28.10.1 Protocol declaration + §28.10.2 ctor extension + §28.10.3 firing site + §28.10.4 6 invariants + §28.10.5 deferred-to-discretion + §28.10.6 producer-side reference + §28.10.7 status posture.

5. **CP plan extension** — CP plan v2.26 → v2.27 NEW U-CP-73 singleton-extension unit at `40508c5`. Unit count 73 → 74. Cluster placement: singleton-extension at existing Cluster 10 ValidatorFramework substrate at L4-within-axis (mirrors runtime plan v2.20 L9-undecies + v2.28 L9-quindecies singleton-extension precedent).

6. **harness-cp impl** — at `9e502b0`: ValidatorPostEvaluateHook Protocol added to `validator_framework_types.py` (@runtime_checkable; async on_post_evaluate with 4 kw-only params; returns None). ConcreteValidatorFramework.__init__ extended with optional kw-only `post_evaluate_hook` param. evaluate() instrumented with time.monotonic_ns elapsed-time measurement + post-construction pre-return hook firing + best-effort exception swallow per §28.10.4 invariant 2. 13 NEW unit tests covering all 9 ACs from CP plan v2.27 §2 U-CP-73.

7. **harness-runtime impl** — at `1c9ce1c` + `7247b1f` + `94f0333`:
   - NEW `cost_attribution_validator_dispatch.py` module (CPU-meter formula per Decision 2.D5 RATIFIED) + CostAttributingValidatorHook impl class. 9 NEW unit tests.
   - NEW `cost_attribution_webhook_dispatch.py` module (WebhookRate.flat_per_attempt + optional egress). 9 NEW unit tests.
   - validator factory `materialize_validator_framework_stage` signature widened with optional kw-only cost-attribution substrate params per CP spec v1.24 §28.10.5 mechanism (a); stage_4_od.py:89 updated to pass RATE_TABLE_V1 + ctx.cost_chain + ctx.audit_writer through.
   - WebhookDeliveryComposer.__init__ extended with optional cost-attribution substrate params (rate_table + cost_chain + audit_writer + workflow_id + parent_action_id + parent_idempotency_key + tenant_id). NEW `_attribute_webhook_cost_best_effort` method wraps the helper in try/except per best-effort discipline.
   - NEW integration test `test_u_od_40_validator_webhook_integration.py` exercising AC #5: 1 validator dispatch + 1 webhook dispatch → 2 audit-ledger entries via shared `_RecordingAuditWriter`; verifies action_id-prefix discrimination (workflow: vs hitl:).

**Post-batch state:** **RETIRE-READY**. Surface coverage 4/4 (LLM + tool + validator + webhook). Structural-criterion-B MET via 4-of-4 surface coverage. U-OD-40 production-binding chain MET for both new surfaces; all 5 ACs from `Implementation_Plan_Operational_Discipline_v2_14.md` §3.4 empirically verified (AC #1 validator CPU-meter via _compute_validator_cost integer/fractional/zero/precision tests; AC #2 webhook flat-per-attempt + optional egress via _compute_webhook_cost flat-only/with-egress/zero-bytes/zero-flat/precision tests; AC #3 cost-record attached at span exit via attribute_*_cost_returns_attached_record tests; AC #4 audit-ledger entry written via attribute_*_cost_writes_audit_entry tests; AC #5 integration 1+1→2 cost-records via test_u_od_40_validator_webhook_integration).

**Verification-shape applied (per `[[verification-shape-sharpened-grep-vs-e2e]]`):** All 3 binding-chain stages verified empirically:
1. **Module-layer:** 9 + 9 = 18 unit tests at both new cost-attribution modules covering formula edge cases + Decimal precision + full chain shape + tenant routing + multi-dispatch cardinality.
2. **Constructor-layer:** validator factory signature widening verified via test_factory_signature_accepts_config_returns_framework_or_none (refreshed for v1.24 signature shape); composer ctor extension verified via integration test substrate construction.
3. **End-to-end-layer:** Production-shape integration test at `test_u_od_40_validator_webhook_integration.py` exercises validator framework instantiated with CostAttributingValidatorHook + WebhookDeliveryComposer with bound cost-attribution substrates against a mock httpx 200 OK response; asserts 2 audit-ledger entries with per-surface action_id-prefix discrimination.

**ZERO cross-axis cascade per Q5=β ratification:** CXA v2.9 unchanged (no new typed edge; convention-seam at §0.4 NOT amended per FM-2 single-focus arc scope). AS spec / OD spec / runtime spec (no new C-RT-NN contract — falls under existing C-RT-23 factory) / ADR / ADD / PRD all unchanged.

**Full RETIRED transit gates on:** Operator deployment-time opt-in via `RuntimeConfig.validator_framework_config = ValidatorFrameworkConfig(...)` (validator side) + WebhookDeliveryComposer factory wiring cost-attribution substrates at bootstrap (webhook side; factory amendment may be needed at follow-on arc — current composer construction site at `bootstrap/factories/webhook_delivery_composer_factory.py` does NOT yet thread cost substrates; runtime spec v1.26 §14.16 binding chain authoring authorizes operator-discretion mechanism). Mirror H_T-AS-8d batch-25 operator-opt-in RETIRE-READY pattern.

---

## §2 Counting math + axis status

**OD-axis (post-batch-28):**
- RETIRED: 2/8 = 25.0% (OD-2 + OD-8 authoring-only)
- **RETIRE-READY: 1/8 = 12.5% (OD-5 NEW)**
- PARTIAL: 1/8 = 12.5% (OD-6 collector daemon only — OD-5 transits out)
- STILL-BOUNDED: 4/8 = 50.0% (OD-1 + OD-3 + OD-4 + OD-7)
- Pipeline-advanced (R + RR + P): 4/8 = 50.0% (unchanged from batch-11/27)
- **OD-5 surface-coverage view: 4/4 = 100.0% wired (LLM + tool + validator + webhook); structural-criterion-B MET**

**Workspace ledger cumulative (post-batch-28):**
- 33/54 RETIRED + **2/54 RETIRE-READY (AS-8d + OD-5 NEW)** + **4/54 PARTIAL** + 13/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = **39/54 = 72.2% pipeline-advanced (unchanged from batch-27 — within-tier PARTIAL → RETIRE-READY transit does NOT change pipeline-advanced count under X-AL-2)**

**Operator-opt-in RETIRE-READY bucket (post-batch-28: 2 members):**
- H_T-AS-8d (batch-25; skill.activation hook surface per SkillActivationHook Protocol at runtime spec v1.32 §14.17)
- **H_T-OD-5 NEW (batch-28; cost-attribution 4-of-4 surface coverage; validator + webhook landed at this batch)**

Both members share the same operator-opt-in RETIRE-READY pattern shape: carrier binding chain MET + e2e empirical verification MET + full RETIRED gates on operator-supplied config at deployment time. The bucket grows 1 → 2 at batch-28.

**OD-5 RETIRE-READY → RETIRED remaining gate:** Operator deployment-time opt-in via:
- Validator side: `RuntimeConfig.validator_framework_config = ValidatorFrameworkConfig()` populates the framework with operator-supplied validators; cost-attribution hook auto-wires via factory mechanism (a) when all 3 substrates (rate_table + cost_chain + audit_writer) are bound at stage 4 OD (which they always are post-stage-4).
- Webhook side: Currently WebhookDeliveryComposer factory at `bootstrap/factories/webhook_delivery_composer_factory.py` does NOT thread cost-attribution substrates through. Follow-on arc may extend the factory signature to pass them through (analogous to validator factory amendment at this arc) — OR operator constructs the composer directly with cost substrates. Within-arc scope at batch-28 is binding-chain MET at the COMPOSER LEVEL (ctor accepts substrates); production-bootstrap thread-through deferred per FM-2 single-focus arc scope.

---

## §3 Class 3 informational findings

(i) **WebhookDeliveryComposer factory cost-attribution thread-through deferred.** The composer ctor at this batch accepts cost-attribution substrates as optional kwargs but the `materialize_webhook_delivery_composer_stage` factory at `bootstrap/factories/webhook_delivery_composer_factory.py` does NOT yet thread them through from `ctx` — operator construction or test construction can opt-in directly via ctor, but the default bootstrap path leaves cost-attribution off for webhook surface. Future doc-hygiene arc may extend the factory signature analogous to validator factory amendment at this arc; NOT patched at batch-28 per FM-2 (out-of-scope: would require runtime spec v1.26 §14.16 amendment for factory signature widening).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 |
| Classification | Within-tier PARTIAL → RETIRE-READY transit; bundled-producer-site landing closing 2 of 4 billable dispatch surfaces (validator.evaluate + hitl.webhook.deliver) per X-AL-2 structural-criterion-B MET via 4-of-4 surface-coverage |
| Apply-arc shape | Single-session full arc per operator AskUserQuestion 2026-05-28; ~8 commits: fork doc + CP spec v1.24 + CP plan v2.27 + harness-cp impl + 2 cost-helper modules + factory binding + integration test + OD plan v2.23 + runtime plan v2.29 + batch-28 ledger event + CLAUDE.md row bumps |
| Source of detection | Empirical orientation at U-OD-40 pre-substantive read (dep-graph constraint surfaces); operator Q-set ratification at AskUserQuestion 2026-05-28 |
| Cross-axis cascade | ZERO per Q5=β ratification (NO new CXA typed edge; convention-seam at CXA §0.4 NOT amended per FM-2) |
| X-AL-3 fork doc | `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) RATIFIED + APPLIED at this arc |
| Companion batches | `phase-7d-retirement-events-batch-27.md` (immediate predecessor — H_T-OD-5 within-PARTIAL surface-coverage advance at tool dispatch landing), `phase-7d-retirement-events-batch-25.md` (AS-8d operator-opt-in RETIRE-READY precedent — sibling pattern for OD-5), `phase-7d-retirement-events-batch-11.md` (initial OD-5 PARTIAL transit at U-OD-38 LLM landing — chronological lineage) |
| Status | ✅ FILED 2026-05-28 |
