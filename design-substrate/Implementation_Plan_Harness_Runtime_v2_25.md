# Implementation Plan — Harness Runtime v2.25

## Change-note (v2.24 → v2.25)

**Scope of revision.** Multi-amendment revision absorbing three upstream spec publications: (a) **runtime spec v1.25 → v1.26** NEW §14.16 C-RT-26 `materialize_webhook_delivery_composer_stage` contract surface + NEW RuntimeConfig optional field `webhook_delivery_composer_config` + NEW HarnessContext field `webhook_delivery_composer` + NEW `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` fail class + §14.8.8.1 step 0 precondition CANONICAL-READING AMENDMENT extending v1.25 single-binding to v1.26 OR-form joint-binding precondition (commit `cc16fc8`); (b) **CP spec v1.16 → v1.17** NEW §6.5 StepEffectiveBinding `persona_tier: PersonaTier` field extension + `resolve_step_binding(manifest_entry, step_id, *, persona_tier: PersonaTier)` signature widening (commit `9f22924`); (c) **CP spec v1.17 → v1.18** NEW §25.2.X canonical-reading amendment widening `HITLEscalationBrief.fail_class` from `ValidatorFailClass` to `ValidatorFailClass | None = None` (commit `fe4d622`). All three amendments authored at the same operator-ratified Reading A path 1 arc per fork doc `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` §3.1 (AskUserQuestion 2026-05-24 close). v2.25 lands NEW L9-quaterdecies 3-unit linear-chain cluster (U-RT-96/97/98) decomposing the C-RT-26 binding chain + amends L9-terdecies (U-RT-93/94/95) ACs to absorb the joint-precondition + persona_tier + fail_class=None propagation.

**Source of fix.** Runtime spec v1.26 publication (commit `cc16fc8` this arc) + CP spec v1.17 publication (commit `9f22924` this arc) + CP spec v1.18 publication (commit `fe4d622` this arc). All three spec amendments are pre-implementation gap-fixes surfaced at impl(U-RT-94) HALT-on-discovery (post AC #9 carrier landing `ba072f4`) per fork doc §1 (primary finding: webhook binding chain absence) + §2 (adjacent finding: helper unreachability at production callsites pre-CP-v1.17). Operator AskUserQuestion 2026-05-24 close ratified Reading A path 1 — author the full webhook binding chain + extend `StepEffectiveBinding.persona_tier` + widen `HITLEscalationBrief.fail_class` to Optional.

**Authority basis for fix direction.** Three convergent precedents:
- **L9-decies (U-RT-83/84/85) — primary shape precedent.** Validator-composer Reading A absorption arc (runtime spec v1.18 §14.13 NEW C-RT-23 `materialize_validator_framework_stage`). The closest structural match for the C-RT-26 binding chain: U-RT-83 = RuntimeConfig field + ValidatorFrameworkConfig empty-marker + HarnessContext field; U-RT-84 = factory + stage-wiring + fail-class landing; U-RT-85 = real-bootstrap e2e against operator-supplied PASS fixture (mechanism α). The cluster has NO driver-consumer mutation at L2 — the consumer is at a downstream cluster (validator-framework is consumed at U-RT-94-era composers, not at L9-decies). C-RT-26 webhook binding chain has identical no-driver-consumer property: the consumer is U-RT-94 composer body, not a driver mutation. L9-decies pattern is the canonical match.
- **L9-undecies (U-RT-87/88/89) — naming convention precedent.** Pause-resume protocol binding-chain arc (runtime spec v1.21 §14.14 NEW C-RT-24 `materialize_pause_resume_protocol_stage`). The closest structural match for the 3-unit decomposition shape; L9-undecies is the -ies-suffix predecessor in the sequence septies/octies/novies/decies/undecies/duodecies/terdecies/**quaterdecies**. Per v2.20 cluster-naming discipline: "L9-undecies follows the existing -ies enumeration (septies/octies/novies/decies/undecies = 7th/8th/9th/10th/11th)"; v2.25 continues at 14th = quaterdecies. NOTE: L9-undecies' U-RT-89 DOES have a driver-consumer mutation (per-step pre-entry detection) — this is the divergence from L9-decies that motivates citing L9-decies as the primary shape precedent for v2.25.
- **Fork doc §3.1 Reading A path 1 operator ratification.** AskUserQuestion 2026-05-24 close: "Reading A path 1 — author full webhook binding chain + StepEffectiveBinding.persona_tier extension. ~10-12 commits across runtime spec v1.26 + CP spec v1.17 + runtime plan v2.25 + CP plan v2.22 + impl re-execution."

**Amendments.**

| Site | Amendment shape |
|---|---|
| **NEW §6 L9-quaterdecies cluster (3-unit linear chain)** | NEW units U-RT-96 → U-RT-97 → U-RT-98 decomposing runtime spec v1.26 §14.16 C-RT-26 binding chain + §3 C-RT-02 RuntimeConfig field + §4 C-RT-04 HarnessContext field + §14.16.4 fail-class landing + stage-5 LOOP_INIT factory wiring + real-bootstrap e2e exercise. Cluster mirrors L9-decies shape (no driver consumer at L2; e2e exercises factory output through `harness_runtime.api.run(...)`). Cluster-boundary edges: NONE to other v2.25 clusters at the binding-chain layer; cluster boundary to U-RT-94 is in the OTHER direction — L9-terdecies U-RT-94 GAINS a cluster-boundary dep on U-RT-97 (the factory landing makes `ctx.webhook_delivery_composer` available for the composer body to consume). |
| **§7.1 U-RT-93 ACs (amended at v2.25)** | NEW AC #5: helper drops getattr-tolerance for `binding.persona_tier` access — consumes `binding.persona_tier` directly per CP spec v1.17 §6.5 declared field. NEW AC #6: helper drops sentinel value pattern at `HITLEscalationBrief` construction; constructs `fail_class=None` directly per CP spec v1.18 §25.2.X Optional widening. NEW AC #7: drops pyright `reportUnusedFunction` suppression at impl-arc landing (per fork doc §2 + checkpoint Phase 3 step 8). v2.24 ACs #1-#4 preserved verbatim. |
| **§7.2 U-RT-94 ACs (amended at v2.25)** | NEW AC #11: §14.8.8.1 step 0 precondition AMENDED to OR-form joint-binding per runtime spec v1.26 canonical-reading amendment row 4 — `if ctx.pause_resume_protocol is None OR ctx.webhook_delivery_composer is None: fall through to step 4f (treat as SYNC_BLOCKING regardless of cell synchrony class); NO webhook delivery fires; NO flag-set fires; NO signal raise; NO orphan operator response`. NEW AC #12: composer constructor extended with 4 NEW fields — `pause_resume_protocol: PauseResumeProtocol | None`, `pause_requested_flag: asyncio.Event`, `webhook_delivery_composer: WebhookDeliveryComposer | None`, `resume_context_holder: ResumeContextHolder`. NEW AC #13: HITLEscalationBrief construction at §14.8.8.1 step 1 uses `fail_class=None` directly per CP spec v1.18 widening (no sentinel value pattern); `fail_detail_hash` parallel posture preserved per v1.18 change-note (no parallel widening at v1.18). NEW AC #14: U-RT-94 GAINS cluster-boundary dep on U-RT-97 (NEW L9-quaterdecies factory landing); composer body cannot exercise the durable-async branch until `ctx.webhook_delivery_composer` is bound at runtime — exercised at U-RT-95 e2e via U-RT-97 → U-RT-98 → operator-bound webhook composer materialization at HarnessContext. v2.24 ACs #1-#10 preserved verbatim except AC #1 (step 0 precondition single-binding from v2.24 is superseded by NEW AC #11 OR-form at v2.25 — v2.24 AC #1 reading is RETIRED per canonical-reading amendment chain). |
| **§7.3 U-RT-95 ACs (amended at v2.25)** | NEW AC #8: e2e test path (vi) operator-binds-pause-resume-protocol-but-not-webhook arm — operator supplies `RuntimeConfig.pause_resume_protocol_config` bound (non-empty) BUT `webhook_delivery_composer_config = None` (operator opt-out per v1.26 §3 default) + `StepEffectiveBinding` with cell == DURABLE_ASYNC → composer hits v1.26 §14.8.8.1 step 0 OR-form precondition (`ctx.webhook_delivery_composer is None`) → falls through to step 4f (sync AskUserQuestion path) → NO webhook delivery fires + NO flag-set + NO `HITLPauseRequestedSignal` raise. Test verifies precondition-arm preserves sync-blocking semantics under partial-binding. NEW AC #9: e2e test path (vii) bare-StepEffectiveBinding-without-persona_tier regression gate — post-CP-v1.17 landing, all production `StepEffectiveBinding` instances declare `persona_tier`; this test verifies that any future regression to a bare binding shape (e.g., test fixture forgetting to populate the field) causes a Pydantic validation error at binding construction (NOT a silent fallback to sync). Test fixture: attempts construct `StepEffectiveBinding(...)` without `persona_tier` argument; verifies `ValidationError` raised. v2.24 ACs #1-#7 preserved verbatim (path-v at v2.24 AC #7 covers operator-binds-webhook-but-not-pause-resume; path-vi at v2.25 AC #8 covers the symmetric arm). |

**Adjacent harmonization sites.** The U-RT-93 helper revision (NEW AC #5 + #6 + #7 at v2.25) gains a cluster-boundary dep on **U-CP-14** (CP plan v2.22 amendment at commit `491f162` — `StepEffectiveBinding.persona_tier` field landing via CP impl arc at checkpoint Phase 3 step 6). PENDING dependency until CP impl arc Phase 3 step 6 lands `harness-cp/src/harness_cp/per_step_override_evaluator.py:117` field declaration + caller updates. The U-RT-94 NEW AC #13 (fail_class=None direct usage) gains a cluster-boundary dep on **U-CP-59** (CP plan v2.22 amendment at commit `491f162` — `HITLEscalationBrief.fail_class: ValidatorFailClass | None = None` Optional widening via CP impl arc at checkpoint Phase 3 step 6). PENDING dependency until CP impl arc Phase 3 step 6 lands `harness-cp/src/harness_cp/validator_framework_types.py` annotation amendment. **Both PENDING deps must clear at impl arc sequencing before runtime impl Phase 3 steps 8+9 begin** — flagged per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` discipline (22nd application this arc).

**Sections preserved verbatim from v2.24.** All v2.24 change-note content + L9-terdecies cluster body at §2 + §3 preserved verbatim outside the listed AC amendment sites. All v2.23 substantive content preserved verbatim. All v2.22 + v2.21 + ... + v2 chain preserved.

**Status posture.** Proposed (v2.24) → **Proposed (v2.25)**. v2.25 is a multi-amendment revision absorbing upstream runtime spec v1.26 + CP spec v1.17 + CP spec v1.18 publications. Net new clusters: +1 (L9-quaterdecies). Net new units: +3 (U-RT-96 + U-RT-97 + U-RT-98). Net new ACs at L9-terdecies amendments: +9 (U-RT-93 +3 ACs #5 #6 #7; U-RT-94 +4 ACs #11 #12 #13 #14; U-RT-95 +2 ACs #8 #9). Net new cluster-boundary edges: 4 (U-RT-94→U-RT-97 within-axis; U-RT-93→U-CP-14 within-axis-cross-package PENDING; U-RT-94→U-CP-59 within-axis-cross-package PENDING; U-RT-98→U-RT-97 within-cluster); WITHIN-CLUSTER L9-quaterdecies edges: 2 (U-RT-96→U-RT-97; U-RT-97→U-RT-98). DAG remains acyclic — verified by topological sort at L9-quaterdecies + L9-terdecies adjacency. Unit-count change: 93 → 96.

**Downstream absorption owed (post-v2.25).**

(a) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.24 → v2.25); co-published this arc OR next bookkeeping commit.

(b) `harness-runtime` impl arcs per checkpoint Phase 3:
   - Step 7: impl(U-RT-96 + U-RT-97 + U-RT-98) — L9-quaterdecies cluster landing.
   - Step 8: impl(U-RT-93) revision — helper simplification (drop getattr-tolerance; drop sentinel pattern; drop pyright suppression) + test fixture updates.
   - Step 9: impl(U-RT-94) — composer constructor extension (4 new fields) + body amend (step 0 OR-form precondition + §14.8.8.1 6-step body with `fail_class=None`) + resume-side `consume_and_clear` integration preserved from v2.24.
   - Step 10: impl(U-RT-95) — driver catch + e2e with 9-case matrix (paths i-vii per v2.24 + v2.25 amendments).

(c) `harness-cp` impl per checkpoint Phase 3 step 6 (PENDING before runtime Phase 3 steps 8+9):
   - `StepEffectiveBinding.persona_tier: PersonaTier` field landing at `harness-cp/src/harness_cp/per_step_override_evaluator.py:117`.
   - `resolve_step_binding(...)` signature widening per CP spec v1.17 §6.5.
   - `HITLEscalationBrief.fail_class: ValidatorFailClass | None = None` Optional widening at `harness-cp/src/harness_cp/validator_framework_types.py`.
   - Caller updates across harness-cp + harness-runtime test fixtures.

(d) OD spec / OD plan / OD impl / CXA / ADR / ADD / PRD: ZERO cascade — all three spec publications are intra-axis (runtime spec v1.26 intra-runtime; CP spec v1.17 + v1.18 intra-CP; the webhook binding chain is intra-runtime; the persona_tier extension is intra-CP carrier; the fail_class Optional widening is intra-CP carrier).

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **L9-quaterdecies cluster-boundary into L9-terdecies is the FIRST runtime-plan cluster-to-cluster within-axis edge.** Prior clusters (L9-septies through L9-terdecies) had cluster-boundary edges ONLY to already-landed substrate (CP-axis carriers OR earlier runtime substrate). L9-quaterdecies → L9-terdecies edge (U-RT-97 → U-RT-94 dep) is the first NEW edge between two clusters introduced at the same plan revision arc (v2.25 introduces L9-quaterdecies + amends L9-terdecies to consume it). Impl-arc sequencing must respect this: U-RT-97 lands before U-RT-94 amendment can be exercised. Surfaced as adjacent finding; impl-arc sequencing enforced at Phase 3 step 7 (L9-quaterdecies) → step 9 (U-RT-94 amendment).

(ii) **U-RT-93 NEW AC #5 + #6 + #7 are post-CP-impl-landing requirements.** The helper revision cannot land until CP impl Phase 3 step 6 lands `StepEffectiveBinding.persona_tier` + `HITLEscalationBrief.fail_class | None`. PENDING dep declared at amendment table row §7.1; impl-arc sequencing enforced. NOT patched here; impl-arc-level concern.

(iii) **AC count drift at U-RT-94.** v2.23 baseline 8 ACs → v2.24 amended to 10 ACs (+ #9 #10) → v2.25 amends to 14 ACs (+ #11 #12 #13 #14). The U-RT-94 unit AC density is approaching the implementer-discretion consolidation threshold per phase-7-implementation skill §3 atomic-decomposition criterion 3.2 (single focused session). Implementer at U-RT-94 landing may consolidate ACs (e.g., merge #11 + #12 + #13 into a single composite "composer body amendment" AC covering precondition + constructor + fail_class) per implementer-discretion. v2.25 enumerates separately for clarity; consolidation at impl-arc landing is implementer-discretion.

(iv) **`WebhookDeliveryComposerConfig` empty-marker shape carried forward.** Per runtime spec v1.26 change-note adjacent defect (i): internal operator-supply shape (per-endpoint URL, per-retry-policy, etc.) deferred to implementation discretion at C-RT-26 landing arc per FM-2 no-extension discipline. Plan v2.25 carries the same posture — U-RT-96 lands the empty-marker dataclass; impl-arc extends with operator-supply shape at U-RT-96 landing (or follow-on arc) per implementer-discretion. Surfaced; NOT patched.

(v) **Pre-v1.26 phantom-cite at v1.23 / v1.24 change-notes (carried from runtime spec v1.26 adjacent defect (v)).** Plan-side analog: prior plan versions (v2.22 + v2.23) reference "the existing webhook_delivery_composer field" in narrative contexts where the field was never authored. v2.25 does NOT edit prior plan-version change-notes (delta-only plan-file preservation per workspace convention). Future readers should interpret pre-v2.25 "existing" claims as documentation drift carried until v2.25; the field is now genuinely existing per L9-quaterdecies U-RT-96 landing arc. Surfaced; NOT patched.

---

## §1 — U-RT-93 plan-body preservation (v2.24 carry-forward; amended at v2.25 §7.1)

The U-RT-93 declaration at v2.23 §1 + v2.24 §1 preservation is preserved verbatim at v2.25 outside the NEW AC #5 + #6 + #7 enumerated at §7.1 below. See §7.1 for the v2.25 amendment.

---

## §2 — U-RT-94 plan-body preservation (v2.24 carry-forward; amended at v2.25 §7.2)

The U-RT-94 declaration at v2.23 §2 + v2.24 §2 amendments is preserved verbatim at v2.25 outside the NEW AC #11 + #12 + #13 + #14 enumerated at §7.2 below. See §7.2 for the v2.25 amendment.

---

## §3 — U-RT-95 plan-body preservation (v2.24 carry-forward; amended at v2.25 §7.3)

The U-RT-95 declaration at v2.23 §3 + v2.24 §3 amendments is preserved verbatim at v2.25 outside the NEW AC #8 + #9 enumerated at §7.3 below. See §7.3 for the v2.25 amendment.

---

## §4 — Coverage matrix delta (v2.24 carry-forward; extended at v2.25 §8)

The coverage matrix delta at v2.24 §4 is preserved verbatim at v2.25. v2.25 EXTENDS the matrix per §8 below.

---

## §5 — Filing footer (v2.24)

Preserved verbatim from v2.24 §5; superseded as canonical filing footer by v2.25 §9 below.

---

## §6 — NEW L9-quaterdecies cluster (v2.25)

L9-quaterdecies is a NEW 3-unit linear-chain cluster decomposing runtime spec v1.26 §14.16 C-RT-26 `materialize_webhook_delivery_composer_stage` binding chain authoring. Cluster mirrors **L9-decies shape** (validator-composer Reading A absorption; U-RT-83/84/85): L0 = config + sub-model + HarnessContext field; L1 = factory + stage-wiring + fail-class; L2 = real-bootstrap e2e against operator-supplied PASS fixture. Naming continues the -ies enumeration at the 14th position (septies/octies/novies/decies/undecies/duodecies/terdecies/**quaterdecies**).

### §6.1 — Cluster shape

| Unit | Within-cluster level | Implements | Files | Depends on |
|---|---|---|---|---|
| U-RT-96 | L0 | Runtime spec v1.26 §3 C-RT-02 `RuntimeConfig.webhook_delivery_composer_config: WebhookDeliveryComposerConfig \| None` field landing + v1.26 §14.16.1 `WebhookDeliveryComposerConfig` empty-marker sub-model + v1.26 §4 C-RT-04 `HarnessContext.webhook_delivery_composer: WebhookDeliveryComposer \| None` field landing + `_MutableHarnessContext.webhook_delivery_composer` builder field + `_REQUIRED_FIELDS` membership extension (39→40) + `freeze()` propagation | `harness-runtime/src/harness_runtime/types.py` (EXTEND — ADD `WebhookDeliveryComposerConfig` empty-marker dataclass per `ValidatorFrameworkConfig`+`PauseResumeProtocolConfig` precedent + ADD `RuntimeConfig.webhook_delivery_composer_config` optional field + ADD `HarnessContext.webhook_delivery_composer` field); `harness-runtime/src/harness_runtime/bootstrap/mutable_context.py` (EXTEND — ADD `_MutableHarnessContext.webhook_delivery_composer` field + EXTEND `_REQUIRED_FIELDS` set membership 39→40 + EXTEND `freeze()` propagation block) | (none — foundational L0 within cluster); cluster-boundary: existing carrier class `WebhookDeliveryComposer` at U-RT-69 (`harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:94`) preserved verbatim |
| U-RT-97 | L1 | Runtime spec v1.26 §14.16.2 C-RT-26 `materialize_webhook_delivery_composer_stage(config: RuntimeConfig, ctx) → WebhookDeliveryComposer \| None` factory contract + v1.26 §14.16.3 stage-5 LOOP_INIT bootstrap-stage wiring + v1.26 §14.16.4 `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` fail-class landing | `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` (AMEND — update existing `materialize_webhook_delivery_composer_stage` function at line 262 to accept `RuntimeConfig` parameter; consume `config.webhook_delivery_composer_config`; return `None` on `None`-default opt-out; return `WebhookDeliveryComposer` instance on operator-bound config); `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (EXTEND — invoke `materialize_webhook_delivery_composer_stage(config, ctx)` at stage-5 LOOP_INIT bucket alongside `materialize_pause_resume_protocol_stage`; bind result to `ctx.webhook_delivery_composer`); `harness-runtime/src/harness_runtime/lifecycle/fail_classes.py` (EXTEND — ADD `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` enum value or sibling per existing fail-class registration pattern) | [U-RT-96] (within-cluster L0 → L1) |
| U-RT-98 | L2 | Real-bootstrap e2e test exercising the C-RT-26 binding chain end-to-end through `harness_runtime.api.run(...)` production bootstrap entry point per L9-decies (U-RT-85) verification-shape sharpening discipline | `harness-runtime/tests/integration/test_u_rt_98_webhook_delivery_composer_binding_chain.py` (NEW — e2e bootstrap test verifying webhook composer materialization at HarnessContext with operator-supplied `WebhookDeliveryComposerConfig` non-default + default-None opt-out arm); `harness-runtime/tests/test_bootstrap.py` (UPDATE — count assertion 39 → 40 at `_REQUIRED_FIELDS` membership test); `harness-runtime/tests/test_types.py` (UPDATE — count assertion if HarnessContext field count asserted); `harness-runtime/tests/test_u_rt_72_harness_context_extension.py` (UPDATE — field-set assertion + freeze() propagation assertion) | [U-RT-97] (within-cluster L1 → L2) |

### §6.2 — Cluster-internal DAG topology

Within-cluster linear chain: **U-RT-96 → U-RT-97 → U-RT-98**. Verified acyclic. L0 (U-RT-96) has no within-cluster predecessors. L2 (U-RT-98) has no within-cluster successors.

### §6.3 — Cluster-boundary edges (cross-cluster)

| Edge | Direction | Notes |
|---|---|---|
| U-RT-94 → U-RT-97 | L9-terdecies consumes L9-quaterdecies factory output | NEW at v2.25; U-RT-94 composer body cannot exercise the durable-async branch until `ctx.webhook_delivery_composer` is bound at runtime via U-RT-97 stage-5 LOOP_INIT factory invocation. Within-axis cross-cluster edge. Impl-arc sequencing: L9-quaterdecies lands FIRST (Phase 3 step 7), L9-terdecies amendments land SECOND (Phase 3 steps 8+9+10). |
| U-RT-93 → U-CP-14 | L9-terdecies helper consumes CP plan v2.22 StepEffectiveBinding.persona_tier landing | NEW at v2.25; PENDING dep until CP impl Phase 3 step 6 lands `StepEffectiveBinding.persona_tier` field at `harness-cp/.../per_step_override_evaluator.py:117`. Within-axis-cross-package edge. Impl-arc sequencing: CP Phase 3 step 6 lands FIRST, runtime Phase 3 step 8 (U-RT-93 helper revision) lands SECOND. |
| U-RT-94 → U-CP-59 | L9-terdecies composer-body consumes CP plan v2.22 HITLEscalationBrief.fail_class Optional widening | NEW at v2.25; PENDING dep until CP impl Phase 3 step 6 lands `HITLEscalationBrief.fail_class: ValidatorFailClass \| None = None` at `harness-cp/.../validator_framework_types.py`. Within-axis-cross-package edge. Impl-arc sequencing: CP Phase 3 step 6 lands FIRST, runtime Phase 3 step 9 (U-RT-94 composer body) lands SECOND. |

NO new cross-axis CXA edges authored at v2.25. ZERO cascade to CXA, OD, ADR, ADD, PRD per change-note row (d) above.

### §6.4 — L9-quaterdecies cluster-boundary edges (TO already-landed substrate)

- `WebhookDeliveryComposer` carrier class at C-RT-20 §14.10.1 / U-RT-69 (`harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:94`) — preserved verbatim; consumed by U-RT-97 factory body update.
- `materialize_webhook_delivery_composer_stage` function stub at `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:262` — preserved through U-RT-69 landing; U-RT-97 updates the function body to consume `RuntimeConfig` parameter.
- Stage-5 LOOP_INIT bootstrap stage at `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` — extended at U-RT-97 to invoke the C-RT-26 factory alongside existing C-RT-24 PauseResumeProtocol factory + ResumeContextHolder initialization (v1.25 §14.8.8.9.2).

### §6.5 — Operator-discretion implementation shape (FM-2)

U-RT-98 implementer selects e2e test fixture mechanism per FM-2 no-extension discipline (mirrors U-RT-85 + U-RT-89 + U-RT-92 + U-RT-95 enumeration patterns). Options:
- **Mechanism α (recommended default):** in-process emulator webhook endpoint via `_RecordingClient` httpx.AsyncClient test-double pattern (mirrors `test_lifecycle_webhook_delivery_composer.py`); verifies factory output is `WebhookDeliveryComposer` instance + binding via `ctx.webhook_delivery_composer is not None` at `harness_runtime.api.run(...)` completion when `RuntimeConfig.webhook_delivery_composer_config` is operator-bound; verifies `ctx.webhook_delivery_composer is None` when config is default-`None`.
- **Mechanism β:** real external HTTP endpoint (deferred per FM-2 to follow-on retirement-batch arc if a substitution row covers operational-against-external-webhook).

Mechanism α is the spec-coherent default per the verification-shape sharpening discipline at batch-16 §6 + batch-17 (U-RT-85) + batch-18 (U-RT-89) — exercises production bootstrap entry point (`harness_runtime.api.run(...)`), NOT `_FakeCtx` or `_MutableHarnessContext` test-locals.

### §6.6 — L9-quaterdecies unit declarations

#### U-RT-96 — RuntimeConfig + HarnessContext field landings + WebhookDeliveryComposerConfig empty-marker

- **Implements (v2.25):** Runtime spec v1.26 §3 C-RT-02 RuntimeConfig field row `webhook_delivery_composer_config: WebhookDeliveryComposerConfig | None` + v1.26 §14.16.1 `WebhookDeliveryComposerConfig` empty-marker sub-model + v1.26 §4 C-RT-04 HarnessContext field row `webhook_delivery_composer: WebhookDeliveryComposer | None`
- **Files (v2.25):** `harness-runtime/src/harness_runtime/types.py` (EXTEND — ADD `WebhookDeliveryComposerConfig` empty-marker dataclass per ValidatorFrameworkConfig+PauseResumeProtocolConfig precedent; ADD `RuntimeConfig.webhook_delivery_composer_config: WebhookDeliveryComposerConfig | None` field (default None); ADD `HarnessContext.webhook_delivery_composer: WebhookDeliveryComposer | None` field); `harness-runtime/src/harness_runtime/bootstrap/mutable_context.py` (EXTEND — ADD `_MutableHarnessContext.webhook_delivery_composer` field; EXTEND `_REQUIRED_FIELDS` set membership 39→40; EXTEND `freeze()` propagation block)
- **Signatures (v2.25):** `class WebhookDeliveryComposerConfig(BaseModel): ...` (frozen Pydantic v2 BaseModel; zero fields at v1.26 authoring scope per FM-2 internal-shape-deferred discipline)
- **Depends on:** (none — foundational L0 within cluster)
- **ACs:**
  1. `WebhookDeliveryComposerConfig` empty-marker Pydantic v2 BaseModel lands at `harness-runtime/src/harness_runtime/types.py` per runtime spec v1.26 §14.16.1. Frozen-outer (`model_config = ConfigDict(frozen=True)`); zero fields at this version per FM-2 deferred-internal-shape discipline.
  2. `RuntimeConfig.webhook_delivery_composer_config: WebhookDeliveryComposerConfig | None = None` field lands at `harness-runtime/src/harness_runtime/types.py` per runtime spec v1.26 §3 row. Default `None` (operator opt-out).
  3. `HarnessContext.webhook_delivery_composer: WebhookDeliveryComposer | None = None` field lands at `harness-runtime/src/harness_runtime/types.py` per runtime spec v1.26 §4 row. Default `None` (factory returns None when config is None).
  4. `_MutableHarnessContext.webhook_delivery_composer` builder field lands at `harness-runtime/src/harness_runtime/bootstrap/mutable_context.py:153`-adjacent. Initialized at builder construction; populated at stage-5 LOOP_INIT per U-RT-97.
  5. `_REQUIRED_FIELDS` set at `mutable_context.py:110` extends from 39 to 40 entries (adds `"webhook_delivery_composer"` membership).
  6. `freeze()` method at `mutable_context.py:307` propagates `webhook_delivery_composer` from `_MutableHarnessContext` to `HarnessContext` post-bootstrap.
  7. Pyright strict-mode passes on all modified modules. Unit tests for the field landings + `_REQUIRED_FIELDS` count + `freeze()` propagation land at U-RT-98 per cluster topology.

**Rollback boundary (v2.25).** Revert `WebhookDeliveryComposerConfig` class + RuntimeConfig field + HarnessContext field + `_MutableHarnessContext` field + `_REQUIRED_FIELDS` membership + `freeze()` propagation. U-RT-97 (L1 dependent) loses HarnessContext binding target; U-RT-94 (L9-terdecies cross-cluster dependent) regains the pre-v2.25 phantom-cite posture (which v1.26 closes).

---

#### U-RT-97 — materialize_webhook_delivery_composer_stage factory body + stage-5 LOOP_INIT wiring + fail-class

- **Implements (v2.25):** Runtime spec v1.26 §14.16.2 C-RT-26 factory contract + §14.16.3 stage-5 LOOP_INIT placement + §14.16.4 `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` fail-class
- **Files (v2.25):** `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` (AMEND — update existing `materialize_webhook_delivery_composer_stage` function body at line 262 to accept `RuntimeConfig` parameter; consume `config.webhook_delivery_composer_config`; return `None` on `None`-default; return `WebhookDeliveryComposer` instance on operator-bound config); `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (EXTEND — invoke `materialize_webhook_delivery_composer_stage(config, ctx)` at stage-5 LOOP_INIT bucket alongside `materialize_pause_resume_protocol_stage` per v1.26 §14.16.3 sibling placement); `harness-runtime/src/harness_runtime/lifecycle/fail_classes.py` (EXTEND — ADD `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` per existing fail-class registration pattern)
- **Signatures (v2.25):** `def materialize_webhook_delivery_composer_stage(config: RuntimeConfig, ctx) -> WebhookDeliveryComposer | None: ...` per runtime spec v1.26 §14.16.2
- **Depends on:** [U-RT-96] (within-cluster L0 → L1)
- **ACs:**
  1. `materialize_webhook_delivery_composer_stage(config: RuntimeConfig, ctx) -> WebhookDeliveryComposer | None` function body at `webhook_delivery_composer.py:262`-adjacent updated to consume `RuntimeConfig` parameter per v1.26 §14.16.2 signature. Existing function-stub body at U-RT-69 landing preserved as structural shell; body extended to consume `config.webhook_delivery_composer_config`.
  2. When `config.webhook_delivery_composer_config is None`: factory returns `None`; `ctx.webhook_delivery_composer` is bound to `None` at stage-5 LOOP_INIT completion (operator opt-out preserved per v1.26 §14.16.2 contract).
  3. When `config.webhook_delivery_composer_config is not None`: factory constructs `WebhookDeliveryComposer` instance per C-RT-20 §14.10.1 contract (the existing carrier class at `webhook_delivery_composer.py:94`) and returns the instance; `ctx.webhook_delivery_composer` is bound to the instance.
  4. Stage-5 LOOP_INIT bootstrap-stage handler at `bootstrap/stage_5_loop_init.py` invokes `materialize_webhook_delivery_composer_stage(config, ctx)` and binds the result to `ctx.webhook_delivery_composer` per v1.26 §14.16.3 sibling placement (alongside `materialize_pause_resume_protocol_stage` per C-RT-24 §14.14.3 + `ResumeContextHolder` initialization per v1.25 §14.8.8.9.2).
  5. `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` fail-class registered at `harness-runtime/src/harness_runtime/lifecycle/fail_classes.py` per v1.26 §14.16.4. On factory raise: bootstrap aborts; reverse-order rollback per C-RT-02 reverses stages 0..4 + sibling stage-5 bindings already constructed.
  6. Sibling ordering within stage 5 LOOP_INIT bucket is implementer-discretion per v1.26 §14.16.3 + change-note adjacent defect (ii); the §14.8.8.1 step 0 OR-form precondition (at U-RT-94 AC #11) consumes both bindings' joint-presence regardless of sibling order — observationally equivalent across orderings.
  7. Pyright strict-mode passes on all modified modules. Unit tests for factory binding behavior land at U-RT-98 per cluster topology.

**Rollback boundary (v2.25).** Revert `materialize_webhook_delivery_composer_stage` function body update + revert stage-5 LOOP_INIT invocation + revert fail-class registration. U-RT-98 (L2 dependent) loses e2e exercise target. U-RT-94 (L9-terdecies cross-cluster dependent) loses bound webhook composer at HarnessContext (composer body OR-form precondition falls through to sync-blocking).

---

#### U-RT-98 — Real-bootstrap e2e for webhook binding chain

- **Implements (v2.25):** Real-bootstrap e2e exercising C-RT-26 binding chain end-to-end through `harness_runtime.api.run(...)` production bootstrap entry point per L9-decies (U-RT-85) verification-shape sharpening discipline
- **Files (v2.25):** `harness-runtime/tests/integration/test_u_rt_98_webhook_delivery_composer_binding_chain.py` (NEW — e2e bootstrap test verifying webhook composer materialization at HarnessContext); `harness-runtime/tests/test_bootstrap.py` (UPDATE — count assertion 39 → 40 at `_REQUIRED_FIELDS` membership test if asserted); `harness-runtime/tests/test_types.py` (UPDATE — HarnessContext field-set assertion if asserted); `harness-runtime/tests/test_u_rt_72_harness_context_extension.py` (UPDATE — field-set + freeze() propagation assertion)
- **Signatures (v2.25):** No new signature; 2-3 test function declarations + fixture lifecycle
- **Depends on:** [U-RT-97] (within-cluster L1 → L2)
- **ACs:**
  1. **Operator-bound config arm:** test fixture supplies `RuntimeConfig` with `webhook_delivery_composer_config = WebhookDeliveryComposerConfig()` (non-None default); invokes `harness_runtime.api.run(...)` via production bootstrap entry point; asserts `ctx.webhook_delivery_composer is not None` post-bootstrap; asserts the bound instance is `WebhookDeliveryComposer` type per C-RT-20 §14.10.1.
  2. **Operator opt-out arm:** test fixture supplies `RuntimeConfig` with `webhook_delivery_composer_config = None` (default opt-out); invokes `harness_runtime.api.run(...)`; asserts `ctx.webhook_delivery_composer is None` post-bootstrap.
  3. **Joint-binding precondition substrate arm:** test fixture supplies both `webhook_delivery_composer_config` non-None AND `pause_resume_protocol_config` non-None; invokes `harness_runtime.api.run(...)`; asserts both `ctx.webhook_delivery_composer` and `ctx.pause_resume_protocol` are non-None — this is the substrate condition for the §14.8.8.1 step 0 OR-form precondition to evaluate False (i.e., durable-async branch reachable). Exercise is at U-RT-95 e2e; this AC verifies the binding substrate only.
  4. **Composer-depth parity with L9-decies (U-RT-85) + L9-undecies (U-RT-89) + L9-duodecies (U-RT-92) close-pattern shape:** tests construct `HarnessContext` via the **real** `harness_runtime.api.run(...)` (or equivalent production bootstrap entry point), NOT via `_FakeCtx` or `_MutableHarnessContext` test-locals. This is the critical AC enforcing the verification-shape discipline catalogued at batch-15 §6(a) + batch-16 §6 sharpening + applied at batch-17 (U-RT-85) + batch-18 (U-RT-89). Test FAILS at design-review if the test scaffolding bypasses production bootstrap.
  5. `_REQUIRED_FIELDS` count assertion at `test_bootstrap.py` updated 39 → 40 (if previously asserted).
  6. HarnessContext field-set assertions at `test_types.py` + `test_u_rt_72_harness_context_extension.py` updated to include `webhook_delivery_composer` membership.
  7. `freeze()` propagation assertion verifies post-bootstrap `HarnessContext.webhook_delivery_composer` value matches `_MutableHarnessContext.webhook_delivery_composer` builder-state per U-RT-96 wiring.
  8. Importable; pyright strict-mode passes. All integration test suite (broader workspace, including U-RT-85 + U-RT-89 + U-RT-92 already-landed e2e) remains green at U-RT-98 landing arc.

**Rollback boundary (v2.25).** Revert NEW test module + revert count-assertion updates. U-RT-97 substrate preserved.

---

## §7 — L9-terdecies cluster amendments (v2.25 amendments on top of v2.24)

### §7.1 — U-RT-93 amendment (v2.25 amendment — NEW ACs #5 + #6 + #7)

The U-RT-93 declaration at v2.23 §1 + v2.24 carry-forward is preserved verbatim at v2.25 outside the listed NEW ACs. v2.23/v2.24 ACs #1-#4 preserved verbatim.

#### U-RT-93 — `_evaluate_cell_synchrony_tolerant` + `HITLPauseRequestedSignal` (v2.25 amendment — post-CP-v1.17 + post-CP-v1.18 helper simplification)

- **Implements (v2.25):** v1.24 substrate (preserved) + CP spec v1.17 §6.5 `StepEffectiveBinding.persona_tier` field consumption (helper drops getattr-tolerance) + CP spec v1.18 §25.2.X `HITLEscalationBrief.fail_class | None` Optional widening (helper drops sentinel value pattern)
- **Files (v2.25):** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (AMEND at impl-arc Phase 3 step 8 — update `_evaluate_cell_synchrony_tolerant(binding)` helper body to consume `binding.persona_tier` directly per CP spec v1.17 §6.5 declared field; REMOVE pyright `reportUnusedFunction` suppression; AMEND `HITLEscalationBrief` construction sites to use `fail_class=None` directly per CP spec v1.18 widening — no sentinel value pattern); `harness-runtime/tests/test_lifecycle_hitl_pause_trigger_helpers.py` (AMEND — update duck-typed `_DuckBinding` fixture to real `StepEffectiveBinding` with `persona_tier` populated; OR retire the partial-binding-tolerance test as regression-gate-only)
- **Signatures (v2.25):** Helper signature unchanged at v2.25 (`def _evaluate_cell_synchrony_tolerant(binding: StepEffectiveBinding | None) -> SynchronyClass | None: ...`); body simplification only — drops getattr-tolerance pattern.
- **Depends on:** [U-CP-14 (within-axis-cross-package; PENDING)] (CP plan v2.22 `StepEffectiveBinding.persona_tier` field landing at CP impl Phase 3 step 6); [U-CP-59 (within-axis-cross-package; PENDING)] (CP plan v2.22 `HITLEscalationBrief.fail_class | None` Optional widening at CP impl Phase 3 step 6)
- **ACs (v2.25 amendments — new ACs only; v2.23/v2.24 ACs #1-#4 preserved verbatim):**
  5. **NEW at v2.25.** Helper `_evaluate_cell_synchrony_tolerant(binding)` body amended to consume `binding.persona_tier` directly (no `getattr(binding, "persona_tier", None)` fallback) per CP spec v1.17 §6.5 declared field. Behavior at production callsites post-CP-v1.17 + post-CP-impl-landing: helper returns `matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class` for any non-None binding (no fallback to `None`); production durable-async branch becomes reachable. Test fixture amendments at `test_lifecycle_hitl_pause_trigger_helpers.py` update `_DuckBinding` to real `StepEffectiveBinding` with `persona_tier` populated; OR retire partial-binding-tolerance test if regression-gate-only.
  6. **NEW at v2.25.** `HITLEscalationBrief` construction at v1.24 §14.8.8.1 step 1 composer-body site (referenced from U-RT-94 AC #2 v2.23 carry-forward) constructs with `fail_class=None` directly per CP spec v1.18 §25.2.X Optional widening. Drops the v2.24-era sentinel pattern (`fail_class=ValidatorFailClass.SCHEMA_VIOLATION + fail_detail_hash="0"*64` placeholder per `2cfc5dc`). `fail_detail_hash` parallel posture preserved per CP spec v1.18 change-note adjacent defect (i) (no parallel widening at v1.18; impl uses appropriate empty/null hash per existing pattern).
  7. **NEW at v2.25.** Pyright `reportUnusedFunction` suppression at helper landing site is REMOVED at U-RT-94 composer-body landing (Phase 3 step 9) when the consumer-site lands. Until then (Phase 3 step 8 helper revision), the suppression may be retained per implementer-discretion; the impl-arc removal target is U-RT-94 consumer-site landing.

**Rollback boundary (v2.25).** Revert helper body simplification + revert HITLEscalationBrief construction sites to sentinel pattern + retain pyright suppression. v2.23/v2.24 ACs preserved unchanged at rollback. U-RT-94 ACs #11-#14 (NEW at v2.25) regain dep-blocked posture on U-CP-14 + U-CP-59 PENDING resolution.

---

### §7.2 — U-RT-94 amendment (v2.25 amendment — NEW ACs #11 + #12 + #13 + #14)

The U-RT-94 declaration at v2.23 §2 + v2.24 §2 amendments (ACs #1-#10) is preserved verbatim at v2.25 outside the listed NEW ACs. v2.24 ACs #1-#10 preserved; v2.24 AC #1 single-binding step 0 precondition reading is SUPERSEDED by v2.25 AC #11 OR-form joint-binding reading per canonical-reading amendment chain.

#### U-RT-94 — HITL gate composer body amend (v2.25 amendment — OR-form precondition + composer constructor extension + fail_class=None direct + cross-cluster dep)

- **Implements (v2.25):** v2.23/v2.24 substrate (preserved) + runtime spec v1.26 §14.8.8.1 step 0 OR-form joint-binding precondition canonical-reading amendment + composer constructor extension consuming 4 NEW fields (`pause_resume_protocol`, `pause_requested_flag`, `webhook_delivery_composer`, `resume_context_holder`) per fork doc §3.1 step 5 + HITLEscalationBrief `fail_class=None` direct usage per CP spec v1.18 widening
- **Files (v2.25):** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (AMEND — extend `RuntimeHITLGateComposer.__init__(...)` constructor signature with 4 NEW fields: `pause_resume_protocol: PauseResumeProtocol | None`, `pause_requested_flag: asyncio.Event`, `webhook_delivery_composer: WebhookDeliveryComposer | None`, `resume_context_holder: ResumeContextHolder`; OR alternative: pass `ctx: HarnessContext` to `dispatch()` signature — architectural decision at impl-arc landing per implementer-discretion); existing `types.py` ResumeContextHolder + HarnessContext fields from v2.24 preserved verbatim
- **Signatures (v2.25):** No new top-level signature; in-place amendment of `RuntimeHITLGateComposer.__init__(...)` + `dispatch(...)` body. 4 NEW constructor fields per AC #12.
- **Depends on:** [U-RT-93] (within-cluster L0 → L1 — preserved from v2.23); within-axis: [U-RT-97 (within-axis cross-cluster; L9-quaterdecies L1)] (NEW at v2.25; webhook_delivery_composer binding chain factory landing); within-axis-cross-package: [U-CP-64] (CP plan v2.21 ResumeContext carrier — preserved from v2.23); within-axis-cross-package: [U-CP-59 (PENDING)] (NEW at v2.25; CP plan v2.22 HITLEscalationBrief.fail_class Optional widening at CP impl Phase 3 step 6)
- **ACs (v2.25 amendments — new ACs only; v2.23/v2.24 ACs #1-#10 preserved verbatim with v2.24 AC #1 superseded reading per canonical-reading amendment chain):**
  11. **NEW at v2.25 (supersedes v2.24 AC #1 reading).** §14.8.8.1 step 0 precondition AMENDED to OR-form joint-binding per runtime spec v1.26 canonical-reading amendment row 4: `if ctx.pause_resume_protocol is None OR ctx.webhook_delivery_composer is None: fall through to step 4f (treat as SYNC_BLOCKING regardless of cell.synchrony_class value); NO webhook delivery fires; NO flag-set fires; NO signal raise; NO orphan operator response`. The v2.24 single-binding reading (`if ctx.pause_resume_protocol is None: ...`) is RETIRED at v2.25 per canonical-reading amendment chain. Branch evaluation logic (synchrony-class evaluation when both bindings present) preserved from v2.23/v2.24 — `synchrony = _evaluate_cell_synchrony_tolerant(binding)` then dispatch on None/SYNC_BLOCKING/DURABLE_ASYNC. Unit test verifies OR-form precondition + 3 synchrony-class outcomes when both bindings present (4 total test cases for OR-form: both-bound True; pause-resume-only False; webhook-only False; neither-bound False).
  12. **NEW at v2.25.** `RuntimeHITLGateComposer.__init__(...)` constructor extended with 4 NEW fields: `pause_resume_protocol: PauseResumeProtocol | None = None`, `pause_requested_flag: asyncio.Event` (default new instance), `webhook_delivery_composer: WebhookDeliveryComposer | None = None`, `resume_context_holder: ResumeContextHolder` (default new empty instance). All 4 fields available because composer is constructed at stage-5 LOOP_INIT post-bucket-completion (after C-RT-24 PauseResumeProtocol + C-RT-26 WebhookDeliveryComposer + ResumeContextHolder all bound at HarnessContext). OR alternative per implementer-discretion: pass `ctx: HarnessContext` to `dispatch()` signature (deferred decision at impl-arc landing).
  13. **NEW at v2.25.** `HITLEscalationBrief` construction at §14.8.8.1 step 1 composer-body site uses `fail_class=None` directly per CP spec v1.18 §25.2.X Optional widening. NO sentinel value pattern (drops `fail_class=ValidatorFailClass.SCHEMA_VIOLATION + fail_detail_hash="0"*64` placeholder per v2.24-era pattern at `2cfc5dc`). Composer-body construction site amended to omit the explicit fail_class argument OR pass `None` directly. `fail_detail_hash` parallel posture preserved (no parallel widening at v1.18); impl uses appropriate empty/null hash per existing pattern. PENDING dep on U-CP-59 (CP impl Phase 3 step 6) for the type-system to admit `None`.
  14. **NEW at v2.25.** U-RT-94 gains cluster-boundary dep on **U-RT-97** (L9-quaterdecies L1 factory landing). The composer body cannot exercise the durable-async branch until `ctx.webhook_delivery_composer` is bound at runtime via U-RT-97 stage-5 LOOP_INIT factory invocation. Impl-arc sequencing: U-RT-97 lands FIRST (Phase 3 step 7); U-RT-94 composer body amendment lands SECOND (Phase 3 step 9). Verified at U-RT-95 e2e (Phase 3 step 10) via path (i)+(iv) durable-async pause-trigger + webhook-exhausted matrix cases.

**Rollback boundary (v2.25).** Revert constructor extension + revert OR-form precondition (restore v2.24 single-binding reading) + revert fail_class=None usage (restore v2.24-era sentinel pattern). v2.24 ACs #1-#10 preserved unchanged at rollback. U-RT-95 ACs #8-#9 (NEW at v2.25) lose substrate.

---

### §7.3 — U-RT-95 amendment (v2.25 amendment — NEW ACs #8 + #9)

The U-RT-95 declaration at v2.23 §3 + v2.24 §3 amendment (AC #7 path-v) is preserved verbatim at v2.25 outside the listed NEW ACs. v2.23 ACs #1-#6 + v2.24 AC #7 (path-v) preserved verbatim.

#### U-RT-95 — Driver catch + e2e (v2.25 amendment — NEW AC #8 path-vi + NEW AC #9 path-vii regression gate)

- **Implements (v2.25):** v2.23/v2.24 substrate (preserved) + runtime spec v1.26 §14.8.8.1 step 0 OR-form precondition symmetric-arm test path (vi) + post-CP-v1.17 `StepEffectiveBinding.persona_tier` regression-gate test path (vii)
- **Files (v2.25 — preserved from v2.24 + extended):** `harness-cp/src/harness_cp/workflow_driver.py` (preserved from v2.23 — driver-side catch logic unchanged at v2.25); `harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py` (EXTEND — v2.25 adds paths (vi) + (vii) covering OR-form precondition symmetric arm + persona_tier regression gate)
- **Depends on:** [U-RT-94] (within-cluster L1 → L2 — preserved from v2.23); cluster-boundary edges to already-landed L9-undecies + L9-quinquies + U-CP-64 preserved; NEW at v2.25 cluster-boundary edge to L9-quaterdecies (via U-RT-94's dep on U-RT-97); within-axis-cross-package: [U-CP-14 (PENDING)] (CP plan v2.22 StepEffectiveBinding.persona_tier landing at CP impl Phase 3 step 6) for path (vii) test-fixture construction
- **ACs (v2.25 amendments — new ACs only; v2.23 ACs #1-#6 + v2.24 AC #7 preserved verbatim):**
  8. **NEW at v2.25.** e2e test path (vi) operator-binds-pause-resume-protocol-but-not-webhook (SYMMETRIC to v2.24 AC #7 path-v): operator supplies `RuntimeConfig` with `pause_resume_protocol_config` bound (non-empty config per L9-undecies precedent) BUT `webhook_delivery_composer_config = None` (operator opt-out per v1.26 §3 default) + `StepEffectiveBinding` with `(persona_tier, engine_class)` matrix cell == `DURABLE_ASYNC` per C-CP-18 §18.1 → composer hits v1.26 §14.8.8.1 step 0 OR-form precondition (`ctx.webhook_delivery_composer is None` → True branch of OR) → falls through to step 4f (sync AskUserQuestion path) → NO webhook delivery fires + NO flag-set + NO `HITLPauseRequestedSignal` raise. Test verifies OR-form symmetric-arm preserves sync-blocking semantics + verifies absence of orphan-response bug per runtime spec v1.26 D9 + v1.26 OR-form extension. Test fixture: `_RecordingClient` from `test_lifecycle_webhook_delivery_composer.py` pattern (httpx.AsyncClient test-double); verify zero outbound POST attempts recorded; verify `ctx.pause_resume_protocol is not None` AND `ctx.webhook_delivery_composer is None` at HarnessContext bound state.
  9. **NEW at v2.25.** e2e test path (vii) bare-StepEffectiveBinding-without-persona_tier regression gate: post-CP-v1.17 + post-CP-impl-landing, all production `StepEffectiveBinding` instances declare `persona_tier`; this test verifies that any future regression to a bare binding shape (e.g., test fixture forgetting to populate the field, OR downgrade to pre-v1.17 carrier shape) causes Pydantic `ValidationError` at binding construction (NOT a silent fallback to sync-blocking via getattr-tolerance pattern, which would be a silent regression). Test fixture: attempts construct `StepEffectiveBinding(step_id="t", model_binding=<...>, engine_class=<...>, override_applied=False)` without `persona_tier` argument; verifies `pydantic.ValidationError` raised with `persona_tier` in error message. This is a NEGATIVE test — it should FAIL the construction, not pass the workflow. Documents the post-CP-v1.17 invariant that `persona_tier` is required at the canonical model.

**Rollback boundary (v2.25).** Revert NEW path (vi) + path (vii) test cases. v2.23 paths (i)-(iv) + v2.24 path (v) preserved unchanged at rollback. Composer-side v1.26 OR-form precondition at U-RT-94 AC #11 preserved (the precondition is at composer body, NOT at driver).

---

## §8 — Coverage matrix delta (v2.25)

Coverage matrix delta at v2.25 (extending v2.24 §4 coverage table):

| Spec contract | Plan unit(s) |
|---|---|
| Runtime spec v1.26 §14.16.1 `WebhookDeliveryComposerConfig` empty-marker (NEW at v1.26) | U-RT-96 AC #1 |
| Runtime spec v1.26 §3 C-RT-02 `webhook_delivery_composer_config` field (NEW at v1.26) | U-RT-96 AC #2 |
| Runtime spec v1.26 §4 C-RT-04 `webhook_delivery_composer` field (NEW at v1.26) | U-RT-96 AC #3 + U-RT-96 AC #4 + U-RT-96 AC #5 + U-RT-96 AC #6 |
| Runtime spec v1.26 §14.16.2 C-RT-26 factory contract (NEW at v1.26) | U-RT-97 AC #1 + AC #2 + AC #3 |
| Runtime spec v1.26 §14.16.3 stage-5 LOOP_INIT placement (NEW at v1.26) | U-RT-97 AC #4 + AC #6 |
| Runtime spec v1.26 §14.16.4 `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` fail-class (NEW at v1.26) | U-RT-97 AC #5 |
| Runtime spec v1.26 §14.8.8.1 step 0 OR-form precondition CANONICAL-READING AMENDMENT | U-RT-94 AC #11 + U-RT-95 AC #7 (v2.24 path-v) + U-RT-95 AC #8 (v2.25 path-vi) |
| Runtime spec v1.26 §14.8.8.6 composition claim CANONICAL-READING AMENDMENT | U-RT-94 AC #11 + AC #14 (cluster-boundary dep) |
| CP spec v1.17 §6.5 `StepEffectiveBinding.persona_tier` field extension | U-RT-93 AC #5 (helper getattr-tolerance drop) + U-RT-95 AC #9 (regression gate) + U-CP-14 (CP impl Phase 3 step 6 — PENDING dep) |
| CP spec v1.18 §25.2.X `HITLEscalationBrief.fail_class | None` Optional widening | U-RT-93 AC #6 (helper sentinel-pattern drop) + U-RT-94 AC #13 (composer-body direct None usage) + U-CP-59 (CP impl Phase 3 step 6 — PENDING dep) |
| U-RT-98 e2e exercise of C-RT-26 binding chain | U-RT-98 AC #1 + AC #2 + AC #3 + AC #4 |

Total coverage matrix rows added at v2.25: +11. All coverage matrix cells populated; ZERO uncovered spec contracts.

---

## §9 — Filing footer (v2.25)

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_25.md` |
| Version | v2.25 |
| Filing event | Multi-amendment revision absorbing runtime spec v1.25 → v1.26 (commit `cc16fc8`) + CP spec v1.16 → v1.17 (commit `9f22924`) + CP spec v1.17 → v1.18 (commit `fe4d622`) per operator-ratified Reading A path 1 at fork doc `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` §3.1 (AskUserQuestion 2026-05-24) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_24.md` (substantive content preserved verbatim outside §6 NEW L9-quaterdecies cluster + §7.1/§7.2/§7.3 L9-terdecies amendment-table extensions) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.4 runtime plan row bump v2.24 → v2.25; runtime spec v1.26 (commit `cc16fc8`); CP spec v1.17 (commit `9f22924`); CP spec v1.18 (commit `fe4d622`); CP plan v2.22 (commit `491f162`) |
| Operator authority | AskUserQuestion 2026-05-24 close ratifying Reading A path 1 per fork doc §3.1 |
| Unit-count change | +3 (93 → 96 — U-RT-96 + U-RT-97 + U-RT-98 NEW at L9-quaterdecies) |
| Cluster-count change | +1 (NEW L9-quaterdecies; predecessors L9-septies through L9-terdecies preserved) |
| DAG topology change | +1 cluster-boundary edge within-axis (U-RT-94 → U-RT-97); +2 within-axis-cross-package PENDING edges (U-RT-93 → U-CP-14; U-RT-94 → U-CP-59); +2 within-cluster edges (U-RT-96 → U-RT-97; U-RT-97 → U-RT-98); acyclic invariant preserved at topological-sort verification |
| Coverage matrix structural change | +11 rows (v1.26 NEW contracts + canonical-reading amendments + CP v1.17 + CP v1.18 cross-references) |
| Acceptance criterion count change | +24 (U-RT-96: +7 ACs; U-RT-97: +7 ACs; U-RT-98: +8 ACs; U-RT-93: +3 ACs #5 #6 #7; U-RT-94: +4 ACs #11 #12 #13 #14; U-RT-95: +2 ACs #8 #9) |
| Cross-axis cascade | None new (within-axis-cross-package to U-CP-14 + U-CP-59 PENDING; no CXA / OD / ADR / ADD / PRD edge authored at v2.25) |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing 3 upstream spec publications into NEW L9-quaterdecies cluster + L9-terdecies amendment extensions; fidelity-pure AC additions (+24 NEW ACs; ZERO renumbered ACs; v2.24 AC #1 reading at U-RT-94 superseded per canonical-reading amendment chain); NO contract addition at plan level; NO acceptance criterion removal; preservation audit PASSED |
| Date | 2026-05-25 |
