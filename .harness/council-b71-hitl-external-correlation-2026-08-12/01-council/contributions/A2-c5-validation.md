# C5 reaction — B-71 (E1-A2, verbatim)

*(Orchestrator note: returned by the genuine C5 agent invocation, 2026-08-12.
Full verbatim content preserved from the agent's final message.)*

## Tensions surfaced

**T1 — `branch_index` on the brief contradicts C10 constraint 7, and the contradiction is structural, not stylistic. (Targets C1.)** C1's carrier 1 puts `branch_index: int | None` on `HITLEscalationBrief`. But the brief *is* the webhook projection source (`deliver_webhook_for_brief` at `hitl_gate_composer.py:1328-1330`). A field on the brief is a field on the wire unless the adapter filters it, and a filtered projection ("the brief carries X but the payload doesn't") is a worse contract than either alternative: it splits the brief's meaning by consumer and invites exactly the drift the frozen model exists to prevent. C10 ground 3 + MUST NOT 7 rule the ordinal out externally. Adjudication: `branch_index` goes on **neither** carrier — it already lives where it's needed inbound (`PreDispatchGateOwningBranchResumeState(branch_index, ...)`), making the brief copy redundant inbound and forbidden outbound.

**T2 — Both primaries treat the composer as "the" constructor; the type has TWO constructor populations, one of them operator-authored external code. (Targets both.)** The in-repo grep finds exactly one production construction site (`hitl_gate_composer.py:1293`) — but the second population lives *outside the repo*: `ValidatorResult` is the "Operator-supplied Validator return shape" (`validator_framework_types.py:155`) carrying `escalation_brief: HITLEscalationBrief | None` (`:170`); the brief's own docstring names `ValidatorFramework.evaluate()` as constructor (`:138-139`); validator-origin briefs flow into the driver at `workflow_driver.py:5669` and into the escalation gate at `:5692-5695`, and narrow palettes at `effective_palette.py:130-131`. Adding identity fields to the shared type means **operator validator code becomes an authorized minter of correlation identity** — nothing distinguishes "None because linear" from "None because validator-authored" from "non-None because an operator's validator fabricated a value" (possibly colliding with a real token). The spec leg owes an explicit **mint-authority clause** (NC-2) and the impl leg an ignore-and-diagnose rule at the validator-brief consumption boundary. Without it, C10's tree-wide-distinctness commitment is unenforceable.

**T3 — The two primaries specify two DIFFERENT digest bases; the spec leg must pick one, and C1's is strictly stronger. (Targets C10, mildly.)** C10 MUST 2 recommends hashing the internal identity (`f"{snapshot_run_id}:pre-dispatch-gate:{branch_index}"`); C1's basis is `(parent_idempotency_key, branch_index, placement.position)`. Contract-relevant differences: (i) C10's basis omits `placement` — a pre-dispatch owner can hold a `PRE_ACTION` gate on an `INFERENCE_STEP`/`TOOL_STEP`, so one branch can own gates at more than one placement; under C10's basis those collide, violating C10's own C1 commitment. (ii) C10's basis needs `snapshot_run_id` in composer scope — it is *not* there, while `parent_idempotency_key` already folds the run_id in. C1's basis satisfies every C10 MUST. Verdict: adopt C1's basis under C10's construction discipline; the spec leg states the basis **normatively but as non-contractual internals** (NC-4).

**T4 — "One pause epoch" is load-bearing in C10's C2/N2/MUST 8 and defined nowhere. (Targets C10.)** The witness tests C10 demands cannot be written against an undefined interval. NC-6 drafts the definition.

## Field-set adjudication (committal)

- `escalation_instance_id` (opaque token): **typed brief** (`str | None = None`) — feeds both webhook and signal from one mint; payload_body automatically via adapter; snapshot echo yes.
- `branch_index`: **NEITHER** carrier. Drop from the design (already in `PreDispatchGateOwningBranchResumeState` inbound).
- Display-only comprehension context (prose): **payload_body only**.
- Resolvability posture flag (MUST 5): normative claim either way; carrier (brief field vs payload-only) flagged to the B seam.

Net brief delta: **one field**, not C1's two.

## Extension-shape verdict

**Optional-with-None-default, single field — and with `branch_index` dropped, Optional is not a compromise; it is the honest discriminated shape.** `str | None` *is* a discriminated union of exactly the two populations. The illegal-states argument bites only against C1's **two**-field proposal (two illegal states: id set with index None, and converse). A model-level split (`LinearEscalationBrief | FanOutEscalationBrief`) fails: required-shape change on a frozen CLOSED-schema contract rippling through `ValidatorResult.escalation_brief` (:170), the signal payload (:1336-1339), `effective_palette.py:79`, the adapter, and the operator-authored validator population (T2) — falsified premise (ii) re-committed one level up. The B-97(a) additive-Optional precedent governs.

## Normative clauses the spec leg owes (drafted)

1. **NC-1 (field).** `HITLEscalationBrief` gains `escalation_instance_id: str | None = None` (C-CP-28 §25.2 family, additive-Optional; existing constructors valid unchanged; linear paths byte-identical).
2. **NC-2 (mint authority).** Minted **only** by the runtime HITL gate composer at escalation composition. `ValidatorResult.escalation_brief` producers MUST leave the field `None`; a non-None value from the validator population is **not honored** — treated as `None` + NC-10 diagnostic.
3. **NC-3 (population condition).** Non-None iff the escalation carries fan-out branch context. Presence/absence is itself the population discriminator.
4. **NC-4 (opacity + non-commitment).** Equality is the sole promised operation. No internal structure, no parse promise (N1); the derivation basis — recommended: domain-separated digest over `(parent_idempotency_key, branch_index, placement.position)` — is implementation guidance, explicitly excluded from the external contract, changeable between pause epochs (N2).
5. **NC-5 (uniqueness + stability).** Distinct among concurrently-outstanding requests tree-wide; stable across redelivery, transport retry, and gate re-fire within one pause epoch; no stability across epochs or runs.
6. **NC-6 (pause-epoch definition).** A pause epoch begins when the gate's `PreDispatchGateOwningBranchResumeState` record is durably recorded at pause-entry and ends when that record is consumed or invalidated by the next successful resume validation (`workflow_driver.py:~8067-8102` family). Re-fires within the same recorded state are one epoch.
7. **NC-7 (ingress rejection — §21.3 analogue).** Advisory-correlation-only, structural one-way rule (C-CP-21 §21.3 style, `Spec_Control_Plane_v1_2.md:1880-1890` precedent): no ingress surface accepts the token or any never-keyable match as a key. A match is counted-as-unaddressed AND diagnosed per NC-10, extending `workflow_driver.py:2824-2848`.
8. **NC-8 (idempotency-key composition).** Delivery key gains the token as a suffix iff non-None (`hitl:{parent_action_id}:{placement}:{token}`); None → today's shape byte-exact; `hitl:` prefix preserved (OD 8-prefix audit discriminator, CXA v2.9 §0.3). Same-branch retries still dedup. Impl leg owes witness tests over the dedup consumers.
9. **NC-9 (§21.8 payload_body interaction + resolvability posture).** The token rides `payload_body` as an additive key; `payload_body` remains contractually opaque per C-CP-21 §21.8's deferred clause. Under property 6(c) 2+-concurrent-unaddressed, the request carries the MUST-5 non-individually-actionable posture; carrier flagged to the B seam.
10. **NC-10 (diagnostic).** Per below.

## Diagnostic/fail-class answer for N3

**The ingress no-op is a typed diagnostic event, not a fail-class signal — assigning it one of the five retry-exit classes would be a category error.** Nothing fails: the pause persists (property 4 INERT re-pause); no retry to route. C5 specifies a **typed disposition enum on the resume resolver's per-key adjudication** — e.g. `ResumeKeyDisposition ∈ {ADDRESSED, UNKNOWN_KEY, NEVER_KEYABLE_INTERNAL_MATCH, CORRELATION_TOKEN_MATCH}` — replacing the silent exclusion at `pause_state_projection.py:338-341` / `workflow_driver.py:2824-2848`. Two distinct non-honored dispositions required: supplying the *internal* identity (probe/leak) vs supplying the *external* token we handed them (invited mistake). The second is precisely diagnosable **because of** determinism (recomputable at ingress from durable state, bounded by outstanding-gate count). Emission surfaces: (i) the OD audit trail under the existing `resume:` action_id prefix (no new prefix minted); (ii) a span attribute on the resume-validation span, naming C7's call.

— C5, validation contract
