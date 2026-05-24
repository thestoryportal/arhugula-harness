# HITL-gate-as-pause-trigger composition — full-scope architectural scoping recommendation

**Filed:** 2026-05-24 at HEAD `e394074` (post FM-2 followups arc; runtime spec v1.23; CP spec v1.15; OD spec v1.11; CXA v2.10).
**Mode:** Systems-architect Mode 3 — Phase-7 architectural-tension-resolution recommendation under skill §4A discipline.
**Scope:** Runtime spec v1.21 §14.14.7 deferral (i), preserved verbatim through v1.22/v1.23:
> *HITL-gate-as-pause-trigger composition. Per the change-note adjacent defect (i): the HITL gate composer body firing `ctx.pause_requested_flag.set()` on durable-async cell synchrony per C-CP-18 §18.3 is a follow-on arc (workflow-driver HITL-gate-composer integration; out of v1.21 scope). The v1.21 contract authors the per-step pre-entry detection point + caller-side flag-signal surface only.*
**Status:** RECOMMENDATION — operator decides per §6. Does NOT edit spec/plan/ADR. Does NOT extend H_T design (I-2 / X-AL-3).
**Filing trigger:** Operator authorization to proceed on checkpoint `20260524-130230` item #1 + advisor sanity-check confirming the carry-forward block "C-RT-19 / U-RT-61 durable-async swap" is stale-lineage cite (C-RT-19 reassigned to RuntimeToolDispatcher at v1.13; U-RT-61 not present in v2.20 plan).

---

## §0 Errata-revision pass (post-advisor verification)

After initial authoring, three empirical surface checks (advisor-requested pre-shipment) reshape Q1, Q3, Q4, and surface a new D8 cite-correction decision. Each is incorporated in-place at the relevant §2 / §6 row; this §0 summarizes the verifications for transparency.

| Check | Initial assumption | Empirical finding | Q affected |
|---|---|---|---|
| **(A) Synchrony-class lookup helper** | Author NEW runtime-layer helper `_evaluate_cell_synchrony_tolerant` from scratch | **LANDED CP-side** at `harness-cp/src/harness_cp/persona_engine_hitl_matrix.py` — 15-entry `HITL_MATRIX`, `matrix_cell_for(persona_tier, engine_class) → HITLMatrixCell`, `SynchronyClass` StrEnum, `HITLMatrixCell.synchrony_class` field. Runtime spec §14.8 step 4b already cites this lookup at line 2001. Runtime composer needs only a **binding-tolerant thin-wrap** (Reading B helper pattern). | Q1 amended |
| **(B) Operator-response carrier on resume** | `ResumeContext` envelope exists; extend with `hitl_response` field (c-i narrow scope) | **`ResumeContext` DOES NOT EXIST.** L9-undecies landed `ResumeAttempt` (sync param) + async `attempt_resume(snapshot, *, material_diff_policy) → ResumeResult`. Async signature is keyword-only with NO operator-context envelope. Authoring NEW `ResumeContext` is a CP+runtime joint amendment (CP spec §26 + runtime spec §14.14.4). | Q3 amended; (c-i) → (c-ii) FORCED |
| **(C) PersonaTier + EngineClass enum existence** | Unverified | **PersonaTier LANDED** at `harness-core/src/harness_core/persona_tier.py:25` (StrEnum). **EngineClass LANDED** at `harness-cp/src/harness_cp/engine_class.py`. Note: project canonical name is `EngineClass`, NOT `D1EngineClass`. | Q4 cite naming corrected; **`StepEffectiveBinding` at `harness-cp/.../per_step_override_evaluator.py:117` is the existing binding carrier** — NEW sub-model `CellSynchronyBinding` is REDUNDANT. |
| **(D) §18.3 vs §18.1 cite drift in v1.21 deferral text** | Quietly correct in helper docstring | The v1.21 deferral text cites "C-CP-18 §18.3" but **§18.3 is the both-by-tier overlay, NOT the synchrony-class matrix**. §18.1 is the synchrony-class × HITL-primitive-shape 2D matrix. Real composition consumes §18.1 (synchrony) + §18.3 (overlay). Mirrors Reading B Q2 cite-completeness sub-finding. | NEW D8 decision row |

**Net impact on §3.1 commit count:** Q3 forced to (c-ii) cross-axis amendment adds CP spec v1.15 → v1.16 commit. Commit count revised **6 → 8**. CP spec amendment is narrow (§26 `attempt_resume` async signature extension + NEW `ResumeContext` carrier).

**Net impact on §3.2 axes touched:** ADD "CP spec v1.15 → v1.16 (narrow §26 amendment)". The "ZERO CP/OD/CXA cascade" claim revises to "ZERO OD/CXA cascade; narrow CP spec §26 amendment owed for `ResumeContext` carrier authoring."

---

## 1. Framing of remaining scope at current baseline

### 1.1 Carry-forward block re-evaluation

The checkpoint queue at `20260524-130230-fm2-followups-arc-complete.md` line 122–124 carries item #1 as "DEFER-UPSTREAM-BLOCKED on C-RT-19 / U-RT-61 durable-async swap" — verbatim from `20260521-143548-closure-arc-phase-a-handoff.md`. That formulation predates **three landings** that re-shape the dependency surface:

| Carry-forward dep | Status at HEAD `e394074` | Implication |
|---|---|---|
| **C-RT-19 "durable-async swap"** | Stale ID. C-RT-19 reassigned at runtime spec v1.13 to `RuntimeToolDispatcher + MCPClientHost` (Phase A.2). The "durable-async swap" semantic moved to **C-RT-20 `WebhookDeliveryComposer` at v1.13 §14.10** — **LANDED at U-RT-69** (`harness-runtime/.../lifecycle/webhook_delivery_composer.py`). | Webhook delivery primitive is operational. |
| **U-RT-61** | Not present at plan v2.20. Plan numbering moved during L9-sexies+ revisions. | No unit gate. |
| **PauseResumeProtocol stage + driver per-step pre-entry detection** | **LANDED at L9-undecies** (U-RT-87/88/89; H_T-CP-22 RETIRED at batch-18). `workflow_driver.py` per-step pre-entry pause-trigger detection sibling-check to `drained_flag.is_set()` is wired at line ~549 per runtime spec v1.21 §14.14.3. | Pause-side wiring is complete. The flag setter is the only missing piece. |
| **ValidatorEscalationGateComposer** | **LANDED at Reading B / L9-duodecies** (runtime spec v1.22 §14.15). | Validator-driven mid-step re-entry composer pattern is precedent; same shape applies to durable-async cell branching. |

**Net.** The block is materially dissolved. The architectural delta this arc introduces is **runtime-spec-layer only**: an extension of the HITL gate composer body at runtime spec §14.8.2 step 4 to consult cell synchrony class and branch sync-blocking vs durable-async delivery. The CP spec C-CP-18 §18.1 matrix + §17.2 HITL primitive shapes + C-RT-20 §14.10 WebhookDeliveryComposer + C-RT-24 pause-resume binding chain are **all already authored and consumed without modification**.

### 1.2 Already-authored canonical surfaces this arc consumes (does NOT re-author)

| Surface | Site | Consumption role |
|---|---|---|
| **C-CP-18 §18.1 synchrony-class × HITL-primitive-shape 2D matrix** | CP spec v1.2 line 1548–1556 (preserved verbatim through v1.15) | Cell lookup by `(persona_tier, D1_engine_class)` → `synchrony_class ∈ {sync-blocking, durable-async, both-by-tier, EXCLUDED}`. |
| **C-CP-18 §18.3 both-by-tier per-tool overlay** | CP spec v1.2 line 1562–1571 | Per-tool `tier ∈ {auto, ask, deny}` annotation determines which actions invoke the gate at all (`auto` skips; `ask`/`deny` invokes). Composes with §18.1 cell synchrony. |
| **C-CP-18 §18.5 persona-tier-binding-time selection** | CP spec v1.2 line 1582–1598 | Operator declares persona-tier + deployment-surface at binding-time; cell lookup yields synchrony class + primitive shape. Already canonical. |
| **C-CP-17 §17.2 HITL-as-tool-call rewriting (3 primitive shapes)** | CP spec v1.2 line 1505–1513 | `request_human_input` (sync return; sync-blocking cells) / `await_human_approval` (durable signal-and-wait; durable-async cells) / `escalate_to_human` (post-retry-exhaustion). |
| **C-RT-20 §14.10 WebhookDeliveryComposer** | Runtime spec v1.13 §14.10 (preserved through v1.23) | `async def deliver_webhook(brief, idempotency_key, ...) → WebhookDeliveryResult`. Out-of-process HITL delivery primitive. **LANDED at U-RT-69** with retry orchestration + idempotency + `hitl.webhook.*` span schema. |
| **C-RT-24 §14.14 PauseResumeProtocol stage** | Runtime spec v1.21 §14.14 | Stage-5 factory + `HarnessContext.pause_resume_protocol` + `HarnessContext.pause_requested_flag: asyncio.Event` + driver per-step pre-entry detection sibling to `drained_flag.is_set()`. **LANDED at L9-undecies**. |
| **C-CP-22 PauseResumeProtocol body** | CP spec v1.13 §26 (renamed from v1.10 §26) | `capture_pause_snapshot(...)` + `attempt_resume(...)` + 5-class `WorkflowPauseReason` + `MaterialDiffPolicy`. Body at `harness-cp/src/harness_cp/pause_resume_protocol.py:213+`. |
| **C-RT-15 §14.8 HITL gate composer (wrap-time)** | Runtime spec v1.13 §14.8 (preserved through v1.23) | Composes `HITLGatedDispatcher` around inner `StepDispatcher`. Current body invokes `ctx.ask_user_question_surface` synchronously (MCP-server-elicit mode at U-RT-60). |
| **C-CP-21 §21.3 cross-trust-boundary palette restriction** | CP spec v1.2 line 1880 | Composes with cell-synchrony delivery — palette restriction is orthogonal to delivery shape. |

### 1.3 Architectural delta this arc introduces (the actual new work)

This arc authors at the **runtime-spec layer only**: a new sub-step at §14.8.2 (or amended step 4) that, after composing the HITL gate body, **consults the cell synchrony class** for the current `(persona_tier, D1_engine_class)` binding context and **branches** between two delivery shapes:

- **sync-blocking** → existing `ctx.ask_user_question_surface.elicit(brief)` path (no change)
- **durable-async** → NEW composition: `ctx.webhook_delivery_composer.deliver_webhook(brief, idempotency_key)` + `ctx.pause_requested_flag.set()` + return a pause-signaling `HITLResult` variant (or raise typed control-flow exception) that the gate caller propagates to the driver per-step pre-entry detector

The driver per-step pre-entry detection at v1.21 §14.14.3 already polls `pause_requested_flag.is_set()` and fires `capture_pause_snapshot(...)` → returns `RunStatus.PAUSED`. The resume entry-point at L9-undecies already consumes operator-provided `ResumeContext` via `attempt_resume(...)`. What is **new** is: how does the operator-supplied HITL response (delivered to a webhook endpoint while the workflow is paused) flow back to the resumed step's continuation as a `HITLResult`?

This is the deepest design question of the arc — surfaced as Q3 below.

---

## 2. Per-Q recommendation with confidence + tiebreaker chain

### Q1. Cell-synchrony lookup home — **(α-revised) binding-tolerant runtime thin-wrap around landed CP-side `matrix_cell_for` [HIGH]**

**Recommendation:** Cell-synchrony lookup is **already canonical CP-side** at `harness-cp/src/harness_cp/persona_engine_hitl_matrix.py` — 15-entry `HITL_MATRIX` + `matrix_cell_for(persona_tier: PersonaTier, engine_class: EngineClass) → HITLMatrixCell` + `SynchronyClass` StrEnum. The runtime composer needs only a **binding-tolerant thin-wrap** sibling to U-RT-91's `_evaluate_hitl_required_tolerant`:

```python
def _evaluate_cell_synchrony_tolerant(
    binding: StepEffectiveBinding | None,
) → SynchronyClass | None:
    """Thin-wrap around harness_cp.persona_engine_hitl_matrix.matrix_cell_for.
    Returns None when binding is None (operator opt-out → fall back to sync-blocking).
    Otherwise returns cell.synchrony_class from matrix_cell_for(binding.persona_tier,
    binding.engine_class).
    HITLMatrixCell.is_excluded handled by caller (raises HITLCellExcludedError
    per existing fail class at hitl_gate_composer.py:187)."""
```

**Authority-chain anchors (3 convergent):**

1. **C-CP-18 §18.5 persona-tier-binding-time selection** (CP spec v1.2 line 1582): "Cell at (persona-tier × D1-engine-class) lookup yields synchrony class + HITL primitive shape" — explicit lookup, not transformation. Pure deterministic function over the matrix.
2. **U-RT-91 binding-tolerant helper precedent** (runtime spec v1.18 §14.13 / impl at `hitl_gate_composer.py:253` `_evaluate_hitl_required_tolerant`): Reading B established the pattern of runtime-side binding-tolerant projection helpers as a thin-wrap around CP-axis canonical surfaces. Cell-synchrony lookup is structurally identical — pure binding-tolerant projection over `(persona_tier, d1_engine_class)`.
3. **Anti-leakage rule** (`CLAUDE.md` I-2 / X-AL-3): authoring a NEW CP-axis contract for cell-synchrony lookup would extend H_T design at Phase 7. The matrix is already canonical at C-CP-18 §18.1. The runtime-side helper is consumption, not extension.

**Why options (β) and (γ) are rejected:**
- **(β) CP-axis new contract `CellSynchronyEvaluator`** — would extend H_T design (X-AL-3 violation); the matrix is already authored; no CP-side carrier is missing.
- **(γ) HarnessContext-bound mutable lookup** — couples runtime state to a deterministic lookup; defeats the purpose of `_evaluate_*_tolerant` helpers (pure functions over typed inputs).

**Tiebreaker check:** Confirm `grep -n "evaluate_hitl_required_tolerant\|_tolerant" harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` returns hits at the U-RT-91 / U-RT-83-91 / Reading-B-era helper signatures. **Verified empirically** this session — `_evaluate_hitl_required_tolerant` at line 253 + `_compute_effective_palette_tolerant` adjacent.

**§2 discipline:** Control-plane axis (HITL composition); deterministic side (matrix is a pure lookup); D-level (derivative of C-CP-18 §18.1 + U-RT-91 helper precedent).

---

### Q2. Durable-cell delivery sequencing — **(α) composer-owned: webhook-fire + flag-set + raise typed pause-signal [HIGH]**

**Recommendation:** The HITL gate composer body OWNS the full durable-cell composition. On `synchrony == durable-async`:

1. Compose `HITLEscalationBrief` per existing C-CP-28 §25.2 shape (re-used; not re-authored).
2. Compute idempotency key from `(parent_action_id, gate_placement_position)` per C-IS-05 §5 entry shape composition discipline.
3. `await ctx.webhook_delivery_composer.deliver_webhook(brief, idempotency_key)` → `WebhookDeliveryResult`.
4. If `delivered=False` → raise `HITLWebhookDeliveryExhaustedError` (re-raise from `WebhookDeliveryExhaustedError`; the composer already raises this; gate body propagates as fail class).
5. If `delivered=True` → `ctx.pause_requested_flag.set()` + raise `HITLPauseRequestedSignal` (NEW typed control-flow exception).
6. Driver per-step dispatch try-block catches `HITLPauseRequestedSignal` → continues to per-step pre-entry pause-trigger detection at next iteration → `pause_requested_flag.is_set()` True arm fires → `capture_pause_snapshot(...)` → `RunStatus.PAUSED`.

**Authority-chain anchors (2 convergent):**

1. **C-RT-15 §14.8 HITL gate composer body is the canonical home for HITL primitive composition** (preserved verbatim through v1.23). Splitting durable-cell delivery across composer + driver would violate the §14.8.1 item 1 "gate body owns invocation" framing inherited from v1.11 MVP.
2. **Driver per-step pre-entry pause-trigger detection at v1.21 §14.14.3** is specifically a sibling to `drained_flag.is_set()` — a generic flag-poll pre-step. Caller-surface contract for flag-set is **already implementer-discretion** per §14.14.7. The gate composer setting the flag is one valid caller-surface; no §14.14 amendment owed.

**Why options (β) and (γ) are rejected:**
- **(β) flag-set-then-driver-fires-webhook** — couples driver to webhook delivery; today the driver is webhook-unaware. Splits one composition across two surfaces with no architectural benefit. Forces re-entry of brief construction at driver layer.
- **(γ) two-step composition with explicit pause-and-resume manifest entry** — over-engineered; the existing `pause_requested_flag` + `capture_pause_snapshot` chain already provides the resume semantics needed.

**Tiebreaker check:** Confirm `grep -n "deliver_webhook\|WebhookDeliveryResult" harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` returns `async def deliver_webhook(...)` at line 146. **Verified empirically** this session.

**§2 discipline:** Control-plane axis (HITL composition); deterministic side (composer flow); D-level (composes C-CP-17 §17.2 `await_human_approval` primitive shape with C-RT-20 §14.10 delivery composer + C-RT-24 pause-trigger flag).

**Implication for runtime-spec amendment:** §14.8.2 step 4 (or new sub-step 4-bis) authors the durable-cell branch; NEW fail class `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED` added to §14.8 fail-class taxonomy.

---

### Q3. HITL response delivery on resume — **(c-ii) FORCED cross-axis: NEW `ResumeContext` typed envelope; CP spec §26 amendment + runtime spec §14.14.4 carrier authoring [HIGH]**

**Recommendation:** **REVISED post-§0(B) verification.** `ResumeContext` carrier does NOT exist at HEAD `e394074`. The async `attempt_resume(snapshot, *, material_diff_policy) → ResumeResult` signature at `harness-cp/src/harness_cp/pause_resume_protocol.py:295` takes NO operator-context envelope. Authoring NEW `ResumeContext: BaseModel` is required to carry operator HITL response back across the pause boundary:

```python
class ResumeContext(BaseModel):
    """Operator-supplied resume context envelope.
    Authored at CP spec v1.16 §26 amendment for HITL-gate-as-pause-trigger arc."""
    model_config = ConfigDict(frozen=True)
    hitl_response: HITLResult | None = None
```

Async signature amended to:
```python
async def attempt_resume(
    self,
    snapshot: PauseSnapshot,
    *,
    material_diff_policy: MaterialDiffPolicy,
    resume_context: ResumeContext | None = None,  # NEW field; backward-compatible default
) → ResumeResult
```

`workflow_driver.py` resume entry-point consumes `resume_context.hitl_response` and propagates to the resumed step's HITL gate via a one-shot delivery channel — the gate at step cursor position evaluates against `pending_hitl_response` carrier and returns the operator's HITLResult without re-firing the webhook.

**Authority-chain anchors (2 convergent):**

1. **C-CP-17 §17.1 `await_human_approval` "durable signal-and-wait"**: the operator's response IS the durable signal. Resume MUST consume that signal. There is currently NO operator-context envelope at `attempt_resume` to carry the signal — adding `ResumeContext` is the natural delivery surface.
2. **`pause_requested_flag` caller-surface contract** at v1.21 §14.14.7 is implementer-discretion. The inbound webhook endpoint that consumes operator response calls `attempt_resume(snapshot, material_diff_policy=..., resume_context=ResumeContext(hitl_response=...))` to inject the response into the resume cycle.

**Why (c-i) is REJECTED post-verification:** No runtime-spec-side `ResumeContext` carrier exists at v1.21 §14.14.4. The L9-undecies cluster authored only `PauseSnapshot`/`ResumeResult`/`MaterialDiffPolicy`/`ResumeOutcomeKind`/`ResumeOutcome`. Field extension is not possible on a nonexistent carrier — the carrier itself must be authored. That places the amendment scope at CP spec §26 (the canonical home of `attempt_resume`).

**Why option (a) is rejected:**
- **(a) Resume re-invokes HITL gate from scratch** — wastes the delivered response; creates duplicate operator-prompt risk (the operator already responded once; a second prompt is operator-confusion-class behavior); requires gate-side idempotency to suppress duplicate webhook delivery on resume. Vastly more complex than carrying the response forward.

**Why option (b) is rejected:**
- **(b) Webhook endpoint mutates a state-ledger entry directly; gate-on-resume reads from ledger** — couples HITL response delivery to F2 state-ledger write path (which is the canonical commit point per C-IS-05 §5). The pause SUSPENDS the workflow before the HITL gate commits; the response delivered during pause is pre-commit data. Reading-from-ledger inverts the commit semantics.

**Tiebreaker check:** Confirmed empirically this session via `grep -rn "class ResumeContext\b\|ResumeContext.*BaseModel" harness-runtime/ harness-cp/ harness-core/` → ZERO hits. The carrier must be authored.

**§2 discipline:** Information-substrate axis (where does the HITL response live during pause) + Control-plane axis (resume signature); deterministic side (the resume-context envelope is a typed carrier); D-level (derivative of C-CP-22 §22.1 resume signature; D-level amendment is a narrow signature widening with backward-compatible default).

**Why option (a) is rejected:**
- **(a) Resume re-invokes HITL gate from scratch** — wastes the delivered response; creates duplicate operator-prompt risk (the operator already responded once; a second prompt is operator-confusion-class behavior); requires gate-side idempotency to suppress duplicate webhook delivery on resume. Vastly more complex than carrying the response forward.

**Why option (b) is rejected:**
- **(b) Webhook endpoint mutates a state-ledger entry directly; gate-on-resume reads from ledger** — couples HITL response delivery to F2 state-ledger write path (which is the canonical commit point per C-IS-05 §5). The pause SUSPENDS the workflow before the HITL gate commits; the response delivered during pause is pre-commit data. Reading-from-ledger inverts the commit semantics.

**Tiebreaker check:** Confirm `grep -n "class ResumeContext\|ResumeContext.*pydantic\|resume_context" harness-runtime/src/harness_runtime/lifecycle/pause_resume_namespace.py` (or wherever `ResumeContext` is authored) shows the carrier is runtime-spec-layer Pydantic v2 BaseModel with field-addition tolerance.

**§2 discipline:** Information-substrate axis (where does the HITL response live during pause); deterministic side (the resume-context envelope is a typed carrier); D-level (derivative of C-CP-22 §22.1 resume signature).

---

### Q4. Persona-tier × engine-class binding source — **(b-revised) re-use landed `StepEffectiveBinding` carrier; NO new sub-model owed [HIGH]**

**Recommendation:** **REVISED post-§0(C) verification.** `StepEffectiveBinding` already lands at `harness-cp/src/harness_cp/per_step_override_evaluator.py:117` (Pydantic v2 BaseModel) and is the canonical per-step binding carrier consumed at runtime spec §14.8 step 4b line 2001 (`cell = matrix_cell_for(persona_tier=binding.persona_tier, engine_class=binding.engine_class)`). The HITL gate composer body already has access to `binding` at the composition site.

**No new `CellSynchronyBinding` sub-model owed.** No new `RuntimeConfig` field owed. The binding context is already constructed per-step by the per-step override evaluator (CP-axis); the runtime composer consumes the EXISTING binding without modification.

Project canonical naming corrections (post-§0(C) verification):
- `EngineClass` (not `D1EngineClass`) — landed at `harness-cp/src/harness_cp/engine_class.py`.
- `PersonaTier` — landed at `harness-core/src/harness_core/persona_tier.py:25`.

**Authority-chain anchors (1 + 1 reinforcement):**

1. **Runtime spec §14.8 step 4b line 2001** already consumes `binding.persona_tier` + `binding.engine_class` for cell-resolve. The pattern is already established; the durable-cell branch piggybacks on the same `binding` parameter.
2. **`StepEffectiveBinding` at `per_step_override_evaluator.py:117`** is the canonical per-step binding carrier — produced by CP-axis per-step override evaluation, consumed by runtime composers as a typed input.

**Why option (a) is rejected:**
- **(a) Per-workflow `WorkflowManifestEntry.cell_synchrony_binding`** — couples deployment-time persona-tier to workflow definition; conflicts with §18.5 "downstream of Phase 3" binding time; would force every workflow author to know the deployment surface. Also redundant — the per-step override evaluator already projects the deployment-bound persona-tier into `StepEffectiveBinding`.

**Why option (c) is rejected:**
- **(c) `HarnessContext` mutable runtime-state** — the binding is structurally immutable at deployment time per §18.5; immutability matches `StepEffectiveBinding` shape (which is frozen Pydantic).

**Sub-finding:** §18.5 "binding-time downstream of Phase 3" framing applies to **deployment-time persona-tier declaration**. The per-step `StepEffectiveBinding` carries the persona-tier forward from RuntimeConfig (operator-supplied at bootstrap; existing `RuntimeConfig` field — no NEW field owed). The flow is: operator declares persona-tier at RuntimeConfig → per-step override evaluator projects into `StepEffectiveBinding.persona_tier` → runtime composer reads `binding.persona_tier` at the gate site.

**Tiebreaker check:** Confirmed empirically — `grep -n "binding.persona_tier\|binding.engine_class" design-substrate/Spec_Harness_Runtime_v1.md` returns hit at line 2001. `StepEffectiveBinding` class body at `per_step_override_evaluator.py:117` (verified empirically this session).

**§2 discipline:** Control-plane axis (binding carrier home); deterministic side; **I-level** (no new structural surface; pure consumption of existing carrier).

**Authority-chain anchors (2 convergent):**

1. **C-CP-18 §18.5 persona-tier-binding-time selection** explicitly states the binding happens at "downstream of Phase 3" — i.e., at deployment-time configuration, not per-workflow. RuntimeConfig is the canonical home for deployment-time configuration.
2. **`ValidatorFrameworkConfig` empty-marker precedent at U-RT-83** + **`PauseResumeProtocolConfig` empty-marker precedent at U-RT-87** establish the pattern: operator-opt-in sub-models at `RuntimeConfig` field with empty-marker default at None enabling backward-compatible behavior when operator opts out.

**Why options (a) and (c) are rejected:**
- **(a) Per-workflow `WorkflowManifestEntry.cell_synchrony_binding`** — couples deployment-time persona-tier to workflow definition; conflicts with §18.5 "downstream of Phase 3" binding time; would force every workflow author to know the deployment surface.
- **(c) `HarnessContext` mutable runtime-state** — the binding is structurally immutable at deployment time per §18.5; immutability matches `RuntimeConfig` shape.

**Tiebreaker check:** Confirm `grep -n "ValidatorFrameworkConfig\|PauseResumeProtocolConfig\|validator_framework_config\|pause_resume_protocol_config" design-substrate/Spec_Harness_Runtime_v1.md` shows the empty-marker config pattern. **Verified empirically** this session at v1.18 §14.13 + v1.21 §14.14.

**§2 discipline:** Deployment-surface axis (binding source) + Control-plane axis (consumer); deterministic side; F-level adjacency (touches `RuntimeConfig` schema — a foundational deployment-time surface) but D-level decision (the empty-marker pattern is already established).

---

### Q5. Webhook idempotency on duplicate operator response — **(α) compose with existing C-RT-20 §14.10 idempotency surface; no NEW idempotency contract [HIGH]**

**Recommendation:** Duplicate operator response delivery (operator hits the webhook endpoint twice during pause) is handled by the **existing** C-RT-20 §14.10 `WebhookDeliveryComposer` idempotency-key propagation. The HITL gate composer body computes idempotency key from `(parent_action_id, gate_placement_position)` at delivery time; the second delivery attempt is suppressed by the composer's existing retry/idempotency loop. No NEW idempotency surface owed.

For **inbound** operator response (operator hits the receiving webhook endpoint twice), the receiving endpoint is operator-implemented per `WebhookDeliveryComposer.deliver_webhook` semantics (outbound HTTP POST per §14.10.1). Inbound response handling is **out of scope** for this arc — it composes with the resume path: the operator delivers response → operator-implemented endpoint forwards to `ctx.pause_requested_flag.set()` orchestrator OR directly invokes `PauseResumeProtocol.attempt_resume(...)` with `ResumeContext.hitl_response` populated. Inbound idempotency lives at the operator-implemented endpoint layer, not at the harness.

**Authority-chain anchors (1 + 1 carry-forward):**

1. **C-RT-20 §14.10.1 outbound delivery idempotency** is already canonical at runtime spec v1.13 (preserved through v1.23) — operator-provided idempotency key on `deliver_webhook` invocation; composer enforces single-effective-delivery.
2. **`pause_requested_flag` caller-surface contract** is implementer-discretion per v1.21 §14.14.7. The inbound webhook endpoint that consumes operator response and either sets the flag or invokes resume is part of that caller-surface contract — out of scope here.

**§2 discipline:** Operational-discipline axis (idempotency); deterministic side; I-level decision (inbound endpoint is operator-discretion).

---

## 3. Scope estimate

### 3.1 Commit count

**8 commits** (revised post-§0(B); mirrors Reading B shape + CP spec amendment + impl):

1. **`scope(hitl-pause-trigger):`** This scoping doc.
2. **`spec(cp): v1.15 → v1.16`** — Narrow §26 amendment: NEW `ResumeContext` typed envelope carrier; AMEND async `PauseResumeProtocol.attempt_resume(...)` signature adding `resume_context: ResumeContext | None = None` keyword-only param (backward-compatible default). ZERO contract change to existing fields; ZERO other-section change.
3. **`spec(runtime): v1.23 → v1.24`** — NEW §14.8.2 step 4-bis durable-async cell branch authoring; NEW fail class `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED`; NEW `HITLPauseRequestedSignal` typed control-flow exception; consumes (does NOT author) `ResumeContext` per CP spec v1.16; consumes (does NOT author) landed CP-side `matrix_cell_for` per §0(A); AMEND §14.14.7 deferral (i) → RESOLVED at v1.24. NO new RuntimeConfig field per §0(C); NO new HarnessContext field per §0(C); NO new sub-model per §0(C).
4. **`plan(cp): v2.20 → v2.21`** — Narrow U-CP-NN unit body amendment for `ResumeContext` carrier + `attempt_resume` signature widening. Single-unit-body amendment (no new cluster).
5. **`plan(runtime): v2.22 → v2.23`** — NEW L9-terdecies cluster (3-unit linear chain): U-RT-93 (`_evaluate_cell_synchrony_tolerant` binding-tolerant thin-wrap + `HITLPauseRequestedSignal` exception class — no carrier fields owed); U-RT-94 (HITL gate composer body amend: §14.8.2 step 4-bis branch + webhook delivery composition + flag-set + signal-raise); U-RT-95 (driver-side `HITLPauseRequestedSignal` catch + e2e real-bootstrap pause-on-durable-cell cycle).
6. **`impl(U-CP-NN):`** `ResumeContext` carrier landing + `attempt_resume` signature widening at `pause_resume_protocol.py:295` + test fixture updates.
7. **`impl(U-RT-93):`** runtime-side helper + exception class.
8. **`impl(U-RT-94):`** composer body amend.
9. **`impl(U-RT-95):`** driver catch + e2e test (mechanism α: in-process pause-resume cycle with operator-supplied test-fixture webhook endpoint emulator).

Wait — count is **9 commits** (8 numbered items + the scoping doc). For symmetry with Reading B's 6-commit arc, the U-CP-NN single-unit-body plan amendment can co-publish with the CP spec amendment commit, collapsing items 2+4 → 1 joint commit. Final count: **8 commits** (scope + cp-spec-and-plan-joint + runtime-spec + runtime-plan + 4 impls).

### 3.2 Axes touched

- **CP spec**: v1.15 → v1.16 (narrow §26 amendment authoring `ResumeContext` + `attempt_resume` signature widening).
- **CP plan**: v2.20 → v2.21 (single-unit-body amendment for `ResumeContext` carrier; co-published with CP spec).
- **Runtime spec**: v1.23 → v1.24 (§14.8.2 step 4-bis amendment).
- **Runtime plan**: v2.22 → v2.23 (NEW L9-terdecies cluster addition).
- **harness-cp impl**: NARROW — `pause_resume_protocol.py:295` signature widening + NEW `ResumeContext` BaseModel at sibling file or `pause_resume_protocol_types.py`.
- **harness-runtime impl**: hitl_gate_composer.py amend + new helper sibling to `_evaluate_hitl_required_tolerant` + new `HITLPauseRequestedSignal` exception + e2e test.
- **harness-od impl**: ZERO (no new OD-side authoring; existing `hitl.webhook.*` + `hitl.gate.*` spans cover the new composition path).
- **harness-cxa**: ZERO (no new cross-axis edge; the composer-to-driver flag-signal flow is intra-runtime).
- **OD spec / ADR / CXA**: ZERO (all canonical surfaces preserved verbatim).

### 3.3 Cross-axis cascade analysis

**Narrow CP spec §26 amendment cascade owed** (revised post-§0(B)). The CP-axis amendment authoring `ResumeContext` is materially narrow:
- Adds ONE new Pydantic v2 BaseModel (`ResumeContext`) with single `hitl_response: HITLResult | None = None` field.
- Widens ONE async signature (`attempt_resume`) with one new keyword-only parameter, backward-compatible default.
- Zero behavior change at existing callers (the L9-undecies cluster's `workflow_driver.py:477` call site does not pass `resume_context` → receives default None → no behavior change).
- Zero CP-side composer authoring (the response propagation lives at runtime-side composer per §14.8.2 step 4-bis).
- Zero OD/CXA cascade — the CP→OD audit-write path for pause/resume already canonical at OD spec §C-OD-30.4 (`PauseResumeAuditPayload`); new `ResumeContext.hitl_response` field is internal to the resume-pre-commit data path, NOT audit-emission territory.

**Forward-cite hygiene:**
- Runtime spec v1.24 cites `C-CP-18 §18.1` matrix (canonical at CP v1.2; preserved through v1.15) — corrected from v1.21's `§18.3` cite per §0(D).
- Runtime spec v1.24 cites `C-CP-17 §17.2` HITL primitive shapes (canonical at CP v1.2; preserved through v1.15).
- Runtime spec v1.24 cites `C-RT-20 §14.10` WebhookDeliveryComposer (canonical at runtime v1.13; preserved through v1.23).
- Runtime spec v1.24 cites `C-RT-24 §14.14` PauseResumeProtocol (canonical at runtime v1.21; preserved through v1.23).
- Runtime spec v1.24 cites `C-CP-22 §26 ResumeContext` per CP spec v1.16 (NEW at this arc; co-published).

**Forward-cite hygiene:**
- Runtime spec v1.24 cites `C-CP-18 §18.1` matrix (canonical at CP v1.2; preserved through v1.15).
- Runtime spec v1.24 cites `C-CP-17 §17.2` HITL primitive shapes (canonical at CP v1.2; preserved through v1.15).
- Runtime spec v1.24 cites `C-RT-20 §14.10` WebhookDeliveryComposer (canonical at runtime v1.13; preserved through v1.23).
- Runtime spec v1.24 cites `C-RT-24 §14.14` PauseResumeProtocol (canonical at runtime v1.21; preserved through v1.23).

**Retirement-event implications:**
- **NO new retirement event filed at this arc close.** The arc does not gate any H_T-CP-* / H_T-AS-* substitution-mechanism retirement. (`hitl_placement.py:18-23` deferral note pre-dates the runtime composer landing and is doc-only; not a substitution gate.)
- **Possible follow-on retirement at separate operator-discretion arc:** if a substitution row covers "durable-async HITL delivery primitive operational against real external webhook," the U-RT-95 e2e (mechanism α in-process emulator) would NOT satisfy that — it would need mechanism β (real external HTTP endpoint with operator-implemented inbound handler). No such substitution row currently declared.

---

## 4. Fork classification per Project_Workflow_v1_8.md §2.7.6

**Class 2 (in-execution operator decision)** — the §14.14.7 deferral (i) is a *deferred-discretion residual* per v1.21 spec text, NOT a Class 1 architectural defect. The operator's selection at the present AskUserQuestion (`scope-only`) is the trigger to open the arc; the recommendation here is the architectural input to that decision.

The Class 2 surface area is the 5 architectural questions Q1–Q5 above. Each Q has a HIGH-confidence recommendation traced to the authority chain. The arc opens at operator ratification; the recommendation becomes the working architecture at impl arc landing.

---

## 5. Confidence summary

| Q | Recommendation | Confidence | Tiebreaker verified this session |
|---|---|---|---|
| Q1 | (α-revised) binding-tolerant thin-wrap around landed CP-side `matrix_cell_for` | HIGH | ✓ `matrix_cell_for` + `SynchronyClass` + `HITLMatrixCell` landed at `harness-cp/.../persona_engine_hitl_matrix.py`; runtime spec §14.8 line 2001 already cites |
| Q2 | (α) composer-owned: webhook + flag-set + raise typed signal | HIGH | ✓ `deliver_webhook` async signature at U-RT-69 |
| Q3 | (c-ii) FORCED — NEW `ResumeContext` carrier + `attempt_resume` signature widening (CP spec v1.15 → v1.16) | HIGH | ✓ `ResumeContext` does NOT exist at HEAD `e394074` (empirical grep); CP-axis amendment required |
| Q4 | (b-revised) re-use landed `StepEffectiveBinding`; NO new sub-model owed | HIGH | ✓ `StepEffectiveBinding` at `per_step_override_evaluator.py:117`; runtime spec line 2001 already consumes `binding.persona_tier`+`binding.engine_class` |
| Q5 | (α) compose with existing C-RT-20 §14.10 idempotency | HIGH | ✓ C-RT-20 outbound idempotency canonical at v1.13 |
| D8 (NEW) | Cite-correction `§18.3` → `§18.1` at v1.21 deferral text absorbed at v1.24 amendment | HIGH | ✓ §18.3 = both-by-tier overlay; §18.1 = synchrony-class matrix — cite drift per §0(D) |

---

## 6. Open for operator decision

The operator decides on each of Q1–Q5 (or selects an alternative not enumerated). The recommendation defaults are stated above for ratify-or-amend. Specific operator-decision surfaces:

| Decision | Default (recommended) | Alternative |
|---|---|---|
| **D1** Q1 cell-synchrony lookup home | (α) runtime helper | (β) CP-axis new contract (rejected — X-AL-3 violation) |
| **D2** Q2 durable-cell composition | (α) composer-owned full flow | (β) split composer/driver (rejected — composition fragmentation) |
| **D3** Q3 resume HITL response delivery scope | (c-i) narrow — runtime-spec-only field extension | (c-ii) cross-axis — CP spec §26 minor revision |
| **D4** Q4 cell-synchrony binding source | (b) RuntimeConfig empty-marker pattern | (a) WorkflowManifestEntry (rejected — binding time conflict) |
| **D5** Q5 webhook idempotency | (α) reuse C-RT-20 §14.10 | (β) new idempotency surface (rejected — duplicate) |
| **D6** Open NOW vs queue | OPEN NOW (per operator selection at AskUserQuestion) | Defer to next batch |
| **D7** U-RT-95 e2e mechanism | (α) in-process emulator webhook endpoint | (β) real external HTTP endpoint (requires inbound handler design) |
| **D8** (NEW) §18.3 vs §18.1 cite-correction routing | (i) absorb into v1.24 runtime amendment; single arc, fewer doc transits | (ii) separate Class 1 cite-correction fork (analogous to `[[fork-cp-spec-section-25-contract-id-collision]]` shape; bookkeeping overhead) |

---

## 7. Tension-resolution discipline footnote

This recommendation is filed under skill §4A discipline. **It does not decide** — the operator decides. **It does not edit the spec/plan/ADR** — that is `spec-writer` / `implementation-planner` work after sign-off. **It does not extend the H_T design** — every architectural surface consumed is already canonical at the authority chain.

The arc, on operator ratification, opens at `spec-writer` skill for spec v1.23 → v1.24 amendment, followed by `implementation-planner` skill for plan v2.22 → v2.23 NEW L9-terdecies cluster authoring, followed by `phase-7-implementation` skill for U-RT-93/94/95 atomic-unit landings.

**End of scoping recommendation.**
