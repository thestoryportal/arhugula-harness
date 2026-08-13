# Spec: Control Plane — v1.119 (delta over v1.118)

*Delta-only file. v1.118 and every earlier C-CP-01 … C-CP-29 body are preserved verbatim
except at the single amendment site named below: C-CP-28 §25.2's `HITLEscalationBrief`
gains a sixth-plus-one field, `escalation_instance_id: str | None = None`, and the
operator-facing webhook `payload_body` gains three additive advisory keys. This is the
register row `B-71` spec leg, authorized by the design record at
`.harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md` **v6**, whose
five hard preconditions are all closed on executed, mutation-probed witnesses. No new
contract number is minted; no existing field changes type; the linear/validator
population is byte-identical to pre-arc. One cross-axis note is owed and stated (§0.7);
no OD, CXA, ADR, ADD or PRD artifact is amended.*

**Filed:** 2026-08-12
**Authority:** Register row `B-71`; design record
`.harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md` v6 §3 (the
settled design), §4-bis (identity basis (B), resolved on an executed collision witness),
§4-ter (the `resolvability` shape), §4-quater (the tracing-export leak bar), §4-quinquies
(the `entry_version` window, scoped two-mode). Precedent for a canonical-reading
amendment over this exact carrier: `Spec_Control_Plane_v1_18.md` §25.2.X.
**Predecessor:** `Spec_Control_Plane_v1_118.md`

## §0 Change-note (v1.118 → v1.119)

### §0.1 The defect

Two peer fan-out branches sharing a `child_workflow_id` produce **byte-identical**
operator-facing HITL escalation requests. `HITLEscalationBrief` (C-CP-28 §25.2, the
v1.10-lineage field-set as canonically supplemented at v1.18 §25.2.X) declares no run- or
branch-distinct member, and the delivery key is `compose_hitl_action_id(parent_action_id,
placement.position)` — workflow-scoped. The escalation fires **before** any child run
exists, so no dispatched-child `run_id` can serve as the discriminator; that fact
falsified the row's first three repair attempts.

The consequence is not merely cosmetic. The same composed `hitl_action_id` is the F2
state-ledger `idempotency_key` **and** `action_id`, so under the IS writer's key-only
dedup (C-IS-07 §7.5) the second peer's HITL audit entry is dropped as an idempotent
no-op — the same aliasing class the workspace already fixed for the sibling step-ledger
write via `branch_path` (U-CP-83 / C-CP-25 §25.16). This delta closes that as an absorbed
half, not a follow-on.

### §0.2 The amendment, in one sentence

`HITLEscalationBrief` gains an **optional, opaque, one-way correlation token** that is
distinct per escalation instance; the token is folded **once**, inside
`compose_hitl_action_id`, so the webhook `Idempotency-Key`, the CP audit `action_id` and
the F2 ledger key remain **one identity family**.

### §0.3 §25.2.Y (NEW) — canonical-reading amendment

The v1.10 §25.2 `HITLEscalationBrief` dataclass body, as canonically supplemented at
v1.18 §25.2.X, is canonically read at v1.119 as:

```python
@dataclass(frozen=True)
class HITLEscalationBrief:
    parent_step_id: str
    parent_action_id: str
    fail_class: ValidatorFailClass | None = None         # preserved verbatim from v1.18 §25.2.X
    fail_detail_hash: str                                # preserved verbatim
    escalation_reason: str                               # preserved verbatim
    proposed_response_palette: frozenset[HITLResponse]   # preserved verbatim — see §0.6 (NOT suppressed)
    escalation_instance_id: str | None = None            # NEW at v1.119 — see §0.4
```

The v1.10 file body is NOT edited — delta-only spec-chain preservation discipline per
v1.13 §1.3 + v1.17 §6.5.5 + v1.18 §25.2.X verbatim-layer-integrity precedent.

**Why Optional-with-`None`-default and not a model split.** The two real populations are
fan-out escalations (which have a branch-distinct instance) and linear/validator
escalations (which do not). A discriminated model split would force the
**operator-authored validator population** to choose a variant it cannot know, which is
the same falsified-premise shape that defeated this row's second attempt. `None` is the
honest value for "this escalation has no branch-distinct instance", and it keeps the
linear path byte-identical.

### §0.4 The token's contract

1. **Opaque, deterministic, one-way, ≥128 bits**, never truncated in the key or in any
   equality-bearing field. **Equality is the sole promised operation.** No consumer may
   parse, order, or derive anything from it.
2. **Basis (B), hashed before composition.** The token derives from the run-scoped
   internal identity of the gate-owning branch plus its `placement`, passed through a
   one-way hash **before** it enters `compose_hitl_action_id`. The pre-hash material
   (`{snapshot_run_id}:pre-dispatch-gate:{branch_index}`) contains a `run_id` **verbatim**
   and MUST NOT reach any exported carrier — see §0.5.
3. **Mint authority is singular.** One authoritative *minter* (the runtime composer at
   the §14.8.8.1 step 1 construction site) and one authoritative *read* (a persisted
   value wins over any recompute). `ValidatorResult.escalation_brief` is a second
   constructor of the TYPE but never a minter of the FIELD; a non-`None` value arriving
   from it is **ignored-and-diagnosed** at the trust seam, never honoured.
4. **Pre-dispatch availability by construction.** The basis fields are *inputs* to child
   run-id seeding, not outputs of dispatch, so the token exists before any child run —
   including under `PURE_PATTERN_NO_ENGINE`, where a child uuid is minted only at
   dispatch.
5. **Persist-once.** The snapshot echo is authoritative once written; deterministic
   recompute is the crash-fallback for the mint→persist window **only**. That window is
   two-mode and is stated at §0.8.
6. **Stability.** The unresolved gate's lifetime, within one run, across re-fires AND
   resume cycles. **Non-commitments,** stated so they are not later read as promises:
   across runs; after resolve/abort; across any activated `new_run_id` resumption.
7. **Delivery is at-least-once per re-fire, dedupable by the stable key.** The harness
   keeps **no** suppression store: the retention window belongs to the consumer, and
   harness-side suppression would convert unresolved-gate visibility from at-least-once
   to at-most-once — the liveness failure for an escalation channel.

### §0.5 The leak bar — extended to the tracing-export channel

The token is projected outward on the webhook. It is **also** exported over tracing,
which the design record established as a matter of fact rather than of policy: the
widening lands inside `compose_hitl_action_id`, and that function's output is what
`webhook.idempotency_key` carries on the OD-canonical `hitl.webhook.deliver` span
(C-OD-32). **Therefore the ≥128-bit one-way hashing at §0.4(2) is load-bearing for the
tracing channel, not only for the webhook**, and the hash MUST be applied before the
value enters the composer — after that point it is already on an exported carrier.

The following are **contractually barred** from any operator-facing or exported field of
this brief: `snapshot_run_id`; the internal pre-dispatch identity in un-hashed form; any
`run_id`-shaped string; and raw basis material of any kind. This is a **structural**
restriction in the contract, not operator discipline — the C-CP-21 §21.3
palette-restriction precedent.

**Cited, not settled here:** whether an OD redaction surface additionally filters these
attributes is unexamined; the bar above does not depend on it, since a redactor is a
mitigation rather than a contract.

### §0.6 The operator surface — three additive `payload_body` keys

All three are additive keys on the contractually-opaque `payload_body` Mapping (C-CP-21
§21.8); the wire body is byte-identical when they are absent.

| Key | Shape | Contract |
|---|---|---|
| `branch_context` | display-only prose | The branch's ordinal **in prose**, under an explicit no-format commitment. Barred by §0.5 from carrying identity material. Never parsed. |
| `resolvability` | the closed `PauseLocationVariant` vocabulary (C-CP-21 §2.1 of the projection surface) | The **resolution CHANNEL**, never the outcome. For this population, `uniform-fallback-only`. |
| `resolvability_note` | prose | States the sole-member RULE and routes the operator; promises no live status. |

**`resolvability` carries the channel, never the outcome — and this is a correctness
requirement, not a style choice.** Resolvability is **time-varying**: a branch that is
not resolvable while two gate-owners are unaddressed becomes resolvable the moment its
peer is answered. A value minted at escalation time cannot track that. A static
`held-for-sole-resolution` stamp would therefore tell the operator not to reply to the
one request whose reply resolves the run — a **false negative in exactly the situation
the operator most needs the truth**, and self-fulfilling, because obeying it withholds
the action that would end the parking. The channel is time-**invariant** and so can never
assert one.

**No new vocabulary is minted.** `resolvability` reuses the closed `PauseLocationVariant`
enumeration the pause-view projection already assigns, so the webhook and the pause view
cannot become two authorities over one concept.

**`resolvability_note` promises no live status.** The pause view cannot report live
eligibility — its projection is a function of the snapshot alone, and the durable-pause
read is ratified as NOT a liveness claim. The note therefore states the rule and routes
the operator to the view for the location set, never for a verdict.

### §0.6.1 The palette is NOT suppressed

An earlier reading of this design bound palette display to `resolvability` as a disarm
for the "palette advertises actionability the resolver discards" defect. **That binding
is WITHDRAWN and MUST NOT be implemented.** A time-invariant channel cannot disarm a
time-varying harm, and suppressing the palette in both states would hide a **valid**
uniform action in the sole-owner state — the same liveness failure this section's
`resolvability` rule exists to prevent, one level down.

`proposed_response_palette` is therefore **preserved verbatim** and continues to be
projected. The disarm is **informational**, carried by `resolvability_note`. The residual
— that in the 2-or-more-unaddressed state the palette still implies an action the
resolver will refuse — is **explicitly not closed by this delta**; closing it requires a
time-varying signal this contract forbids.

### §0.7 Ingress — advisory-correlation-only, as a structural one-way rule

**No ingress surface accepts this token.** It is not a key, and no field of
`ResumeContext` or any resume surface may be keyed by it. A submitted value that happens
to match is **counted-as-unaddressed AND diagnosed** — a typed disposition landing on the
resume outcome, with the pause view as the secondary surface. A log line alone is
insufficient.

**The webhook carries no ingress keys at all.** No real `run_id` transits it; addressing
capability lives exclusively on the operator-held pause view. This is unchanged by the
delta and is restated because the new field is the first outward-projected identifier on
this carrier and must not be mistaken for an address.

### §0.8 The `entry_version` recompute window — scoped, two-mode

The token is delivered to the webhook **before** the pause signal is raised, so the
external world can legitimately hold a token before any snapshot exists. The recompute
window runs from successful delivery until the snapshot is recoverable, and **who closes
it depends on the pause-protocol mode**:

| Mode | The window closes when | Closed by |
|---|---|---|
| `durable=True` | the snapshot is journaled | the harness |
| `durable=False` (the default) | the caller persists the returned pause snapshot | **the caller** — the harness does not do it for them |

Outside the window the token reproduces, because the run identity the basis is composed
from is preserved across resume. **At the default the guarantee is therefore conditional
on caller behaviour the harness cannot enforce**; a deployment that needs the
unconditional property MUST opt into `durable=True` rather than assume it.

The residual inside the window — an operator holding a token the resumed run cannot
reproduce — is **not closed by this delta** and cannot be closed by the token's shape. It
requires a durability change against the deliver-before-signal ordering, which is a
separate arc.

### §0.9 Absorbed here vs registered elsewhere

**Absorbed** (one mechanism; splitting would ship the widening half-applied): the
per-peer HITL audit-entry loss at §0.1; mint-authority ignore-and-diagnose (§0.4(3));
the `resolvability` / `resolvability_note` surface (§0.6); the persist-once reverse-thread
field (§0.4(5)).

**NOT absorbed, and registered** — each an observable contract change to a cleared
mechanism, so each owes its own leg: the uniform-response target selector; redelivery on
posture change; uniform-treatment extension to depth-0 root and already-dispatched
children; the pause-view addressing half; the unguarded `entry_version` carrier across the
pause boundary; and the typed resume-outcome diagnostics carrier.

### §0.10 The sequencing condition, discharged

The council bound this leg to a sequencing condition: the **resume-outcome diagnostics
leg ships with the spec leg, or the diagnostic-strength wording softens in the same
commit**. This delta takes the **second** option, deliberately and visibly:

§0.7 requires that an ingress match be *"counted-as-unaddressed AND diagnosed — a typed
disposition landing on the resume outcome, with the pause view as the secondary
surface"*. The **typed carrier** for that disposition does not exist yet and is registered
as a follow-on (§0.9). Until it lands, §0.7's diagnostic requirement is a **contract
obligation on the consumer of this spec, not a claim that the carrier exists** — an
implementation satisfying §0.7 today must surface the disposition through whatever typed
resume-outcome surface it has, and the follow-on leg replaces that with the canonical one.

This is stated rather than left implicit precisely because the council made it a
condition: a reader of §0.7 must not infer a shipped `ResumeKeyDisposition` type.

### §0.11 Zero-change statements

ZERO change to: the other six `HITLEscalationBrief` fields; `ValidatorFailClass`;
`ValidatorOutcome`; `ValidatorNextAction`; `ValidatorResult`; the `ValidatorFramework`
Protocol signature; the 4-value HITL response palette; `ResumeContext`'s key shape
(property 1's map stays `child_run_id`-keyed); the pre-dispatch internal identity's
non-addressability. ZERO new contract number. ZERO new fail class. ZERO enum extension.
ZERO OD / CXA / ADR / ADD / PRD revision — `HITLEscalationBrief` is intra-CP-axis, and the
tracing-export observation at §0.5 *consumes* the existing C-OD-32 namespace without
amending it.

**One cross-axis note, owed and stated:** the OD-canonical `hitl.webhook.deliver` span is
declared head=1.0 always-sampled at C-OD-32.3, while the implementation's always-sampled
member set omits it. That divergence is a registered OD conformance defect and is **not**
this delta's to resolve; §0.5's bar is written to hold under either resolution.

### §0.12 Byte-identical-when-absent

On the linear/validator path the new field is `None`, the three `payload_body` keys are
absent, and the wire body is byte-identical to pre-arc — the webhook adapter is an
explicit field-by-field mapper, so an unset Optional adds no key. The ledger/audit key
composition is likewise byte-identical when the discriminator is absent, per the
`branch_path` precedent at C-CP-25 §25.16.
