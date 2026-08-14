# Spec: Control Plane — v1.119 (delta over v1.118)

*Delta-only file. v1.118 and every earlier C-CP-01 … C-CP-29 body are preserved verbatim
except at the **five** carrier amendment sites named below — all additive,
`None`-defaulted, and byte-identical when absent: (1) C-CP-28 §25.2's
`HITLEscalationBrief` gains `escalation_instance_id` (§0.3, §25.2.Z) and the
operator-facing webhook `payload_body` gains four additive keys (§0.6);
(2) C-CP-25 §25's `StepExecutionContext` gains the internal basis carrier (§0.4.1,
§25.17); (3) C-CP-26 §26's per-branch pre-dispatch gate-owning resume state gains the
persisted echo (§0.4.2, §26.9); (4) C-CP-25 §25's `StepExecutionContext` gains the
**echo read carrier** (§0.4.3, §25.18) — without it the §0.4.2 read order names a value no
consumer can reach, and the persist-once contract is unsatisfiable rather than merely
unimplemented; (5) C-CP-21's `PreDispatchUniformFallbackOnlyLocation` gains the **public
correlation projection** (§0.4.4, §2.2.A) — the design record's own precondition, without
which the correlation loop terminates in a struct no operator reads. A Runtime-side delta
is owed and is NOT zero (§0.13). This is the
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

### §0.3 §25.2.Z (NEW) — canonical-reading amendment

**Base version.** This amendment composes over **v1.19 §25.2.Y.1**, the most recent
canonical-reading amendment to this carrier — NOT v1.18. A first draft of this delta
composed over v1.18 and thereby (a) re-declared `fail_detail_hash` as a required `str`,
silently REGRESSING v1.19's widening, and (b) reused the already-occupied `§25.2.Y`
label. Both are corrected here; the label is fresh (`§25.2.Z`) and the body below carries
v1.19's field types forward verbatim. The carrier is a Pydantic `BaseModel`, per v1.19's
own note.

The v1.10 §25.2 `HITLEscalationBrief` body, as canonically supplemented at v1.18 §25.2.X.1
and v1.19 §25.2.Y.1, is canonically read at v1.119 as:

```python
class HITLEscalationBrief(BaseModel):
    parent_step_id: str
    parent_action_id: str
    fail_class: ValidatorFailClass | None = None         # preserved verbatim from v1.18 §25.2.X.1
    fail_detail_hash: str | None = None                  # preserved verbatim from v1.19 §25.2.Y.1
    escalation_reason: str                               # preserved verbatim
    proposed_response_palette: frozenset[HITLResponse]   # preserved verbatim — see §0.6 (NOT suppressed)
    escalation_instance_id: str | None = None            # NEW at v1.119 §25.2.Z — see §0.4
```

The v1.10 file body is NOT edited — delta-only spec-chain preservation discipline per
v1.13 §1.3 + v1.17 §6.5.5 + v1.18 §25.2.X + v1.19 §25.2.Y verbatim-layer-integrity
precedent.

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
2. **Basis (B), hashed before composition — the digest is PINNED.** The token derives
   from the run-scoped internal identity of the gate-owning branch plus its placement
   POSITION, through this exact formula:

   ```
   escalation_instance_id =
       sha256(
           "hitl-escalation-instance:"          # domain separator, ASCII, literal
           + pre_dispatch_gate_owning_identity  # f"{snapshot_run_id}:pre-dispatch-gate:{branch_index}"
           + ":"
           + placement.position.value           # the enum's string VALUE, not the member name
       ).hexdigest()                            # lowercase hex, 64 chars, never truncated
   ```

   All inputs are UTF-8. **The formula is a contract surface, not implementation
   discretion** — this is an idempotency-key family, and two otherwise-compliant
   implementations that disagreed on algorithm, encoding, domain separator, or whether
   `placement` means the position or the whole object would produce different tokens for
   one unresolved run, breaking webhook dedup and the audit join. The domain separator
   follows the workspace's existing seed convention (`compose_child_run_id_seed`'s
   `"child-run:"` prefix). sha256/hex satisfies §0.4(1)'s ≥128 bits with margin.

   The pre-hash material contains a `run_id` **verbatim** and MUST NOT reach any exported
   carrier — see §0.5.

   **The guarantee is per (branch × placement POSITION), not per placement DECLARATION —
   stated as a bound, because it is narrower than §0.2's headline.** A workflow may declare
   two placements at the same position, and both are valid and executed (witnessed today by
   `test_two_pre_action_placements_emit_per_placement_canonical_4_spans`). The basis hashes
   the position's string VALUE, so those two escalation instances receive the **same** token
   and the same composed key, and the C-IS-07 §7.5 key-only dedup drops the second audit
   entry exactly as it did before this delta — for that shape only.

   **This is a declared residual, NOT a silent one, and it is deliberately not repaired
   here.** The identity basis is (B), resolved by the design record §4-bis on an executed
   collision witness, and it names the placement POSITION. Widening the digest with a
   placement-declaration discriminator would change a ratified basis at spec-application
   time — the silent design extension X-AL-3 forbids — so the honest action is to narrow
   the claim and register the remainder. §0.2's "distinct per escalation instance" is
   therefore read against the (branch × position) instance, and the duplicate-declaration
   shape is registered as **its own forward-register row, `B-165`** — not merely as prose
   here, so it can be selected and tracked independently once `B-71` closes. A leg that needs it must revisit the basis
   through the design record, not through an implementation choice.

2-bis. **The token-PRESENT composed key is PINNED too, for the same reason the digest is.**
   §0.12 pins only the token-ABSENT result (byte-identical to the pre-arc two-argument
   key). Leaving the present-case format open would let two otherwise-compliant
   implementations append, prefix, or re-hash the same token and both pass every
   distinctness test — and then a deployment change **while a gate is unresolved** would
   emit a different webhook `Idempotency-Key` and F2 ledger key for the same escalation,
   duplicating the effect the dedup exists to prevent. That is the identical argument
   §0.4(2) makes for the digest, and it applies with equal force one layer out:

   ```
   compose_hitl_action_id(parent_action_id, placement_position, escalation_instance_id)
     = f"hitl:{parent_action_id}:{placement_position.value}"                 # token absent
     = f"hitl:{parent_action_id}:{placement_position.value}:{escalation_instance_id}"
                                                                            # token present
   ```

   Appended as a **suffix**, separated by the same `":"` the existing shape uses, never
   truncated, never re-hashed. The absent form is character-for-character the pre-arc key.
   **This pins the OUTPUT, not the call shape** — the parameter list above is illustrative
   of the inputs, and whether the token arrives as a third argument, a widened context, or
   otherwise stays Runtime-owned implementation discretion per §0.13.
3. **Mint authority is singular.** One authoritative *minter* (the runtime composer at
   the §14.8.8.1 step 1 construction site) and one authoritative *read* (a persisted
   value wins over any recompute). `ValidatorResult.escalation_brief` is a second
   constructor of the TYPE but never a minter of the FIELD; a non-`None` value arriving
   from it is **ignored-and-diagnosed** at the trust seam, never honoured.

   **The trust seam has an address, and it is named here** because a normative rule with
   no owning site is unimplementable by inspection. The seam is the point where a
   validator-supplied `ValidatorResult.escalation_brief` is accepted into the escalation
   path — today that brief is forwarded to the composer directly, so an operator-authored
   validator could set the field and have it delivered. The rule is enforced by
   **overwriting the field with the harness-minted value (or `None`) at that acceptance
   point**, before the brief reaches any composer, key, or exported carrier. Ignoring
   without overwriting is not sufficient: the value would still ride the payload. The
   diagnosis half is subject to §0.7's advisory softening — the condition MUST be
   surfaced through whatever diagnostic channel exists, and becomes a typed requirement
   when that carrier's own leg lands.
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

### §0.4.1 §25.17 (NEW) — the basis-carrying context field on `StepExecutionContext`

**Owning contract: C-CP-25** (`StepExecutionContext` is the WorkflowDriver carrier). This is a canonical-reading amendment in the same sense as §0.3: additive, `None`-defaulted, and the prior file bodies are not edited.

The minter at the §14.8.8.1 step 1 construction site holds a `StepExecutionContext` and
nothing run-identifying: `StepExecutionContext` declares **no** run identity. The basis at
§0.4(2) is therefore unreachable from the mint site as the carrier stands, and an
implementation would have to either use a run-blind basis — the exact defect this row
exists to close — or invent a field. This delta names it rather than leaving it to
implementation discretion:

| | |
|---|---|
| **Field** | `pre_dispatch_escalation_basis: str \| None = None`, on `StepExecutionContext` |
| **Value** | the branch's run-scoped internal identity as defined at §0.4(2), **pre-hash**; `None` on every population that has no pre-dispatch gate-owning branch |
| **Producer** | the fan-out branch-context composition site, which already computes this identity for the resume-side eligibility comparison — the value is read, not newly derived |
| **Propagation** | inherited by `model_copy` like the context's other additive carriers; a branch child never re-derives it |
| **Byte-identity** | `None`-defaulted, so every non-fan-out path is byte-identical to pre-arc |

**It is basis material, so §0.5's bar applies to it in full**: this field is *internal
carriage only*, MUST NOT be projected to any operator-facing key, and MUST be hashed per
§0.4(2) before it reaches `compose_hitl_action_id`. Naming it here is what makes the
one-way hash enforceable rather than aspirational.

### §0.4.2 §26.9 (NEW) — the persisted echo on the pre-dispatch gate-owning resume state

**Owning contract: C-CP-26** (PauseResumeProtocol carriers). Canonical-reading amendment, additive and `None`-defaulted; the prior file bodies are not edited.

§0.4(5) promises that a persisted value wins over recompute. That promise needs a
carrier, and the driver currently records only per-branch metadata with no token field —
so without this, every resume would recompute and the persist-once contract would be
unsatisfiable as written:

| | |
|---|---|
| **Field** | `escalation_instance_id: str \| None = None`, on the per-branch pre-dispatch gate-owning resume state (the carrier that already holds `branch_index`, `step_id`, `step_kind`, `hitl_gate_config_hash`) |
| **Value** | the **post-hash** token exactly as delivered — never the pre-hash basis |
| **Keying** | per branch entry; the existing `branch_index` within its containing snapshot is the key. No tree-wide index is introduced: the containing snapshot's own identity supplies tree-scoping, which is the same property the pre-dispatch internal identity already relies on |
| **Serialization** | an opaque string; consumers may compare it for equality and nothing else (§0.4(1)) |
| **Absence** | `None` means *not yet persisted* — the mint→persist window of §0.8 — and licenses the deterministic recompute, never a fresh mint |
| **WRITER** | the **pause-signal / snapshot producer**, which copies the minted token from the brief into this field as it composes the per-branch entry. Naming the writer is not optional: without it the field is declared, never populated, and the echo is `None` forever — which is the §0.4.3 defect in mirror image, on the write side |

**A CARRIED-FORWARD row preserves its echo; it is never rebuilt as `None`.** When a
recovered gate-owning branch is withheld by warm-up scheduling, the snapshot builders
reconstruct its row from the carried-forward set **without a new brief in hand**
(`workflow_driver.py:10442-10461` and `:14810-14829`). A reconstruction that defaulted the
field would silently reset a persisted token to `None`, and the next resume would recompute
in defiance of §0.4(5) — **rotating the key of an escalation the operator is still holding**
if the basis has since changed. The prior row's value is therefore copied forward verbatim;
"no new brief" licenses preservation, never a reset. Found by out-of-family review, which
traced the real re-pause path rather than the mint path.

**The write is what closes the loop, and it is stated because declaring a field is not
the same as filling it.** The minter at §14.8.8.1 step 1 places the token on the
`HITLEscalationBrief`; nothing in that step reaches the snapshot. If the producer does not
copy it across, every resume finds `None`, takes the recompute arm, and the persist-once
contract is again satisfied only by accident. Out-of-family review caught this as the
write-side twin of the §0.4.3 read-side gap.

**Backward compatibility with already-durable snapshots is a CONTRACT, not an
implementation nicety.** This field lands on a row that already ships, and the per-branch
entry participates in the snapshot hash. A naive addition makes `model_dump` emit
`escalation_instance_id: null` for every pre-existing durable pre-dispatch pause, changing
the recomputed hash and causing a legitimate snapshot to be **rejected as corrupt** on
resume after upgrade. The field is therefore **dropped from the serialized form when
`None`**, exactly as `_strip_default_fanout_resume_fields` already drops
`hitl_gate_config_hash=None` from this same row for this same reason. That precedent is
cited rather than re-derived: the workspace has already decided how this class of
compatibility is handled, and a second mechanism would be a second authority.

**Read order is normative:** a consumer that finds a non-`None` echo MUST use it and MUST
NOT recompute; recompute is reachable only from `None`. §0.4.3 is what makes that order
*reachable*; without it the rule names a value the reading consumer cannot obtain.

### §0.4.3 §25.18 (NEW) — the echo READ carrier on `StepExecutionContext`

**Owning contract: C-CP-25.** Additive, `None`-defaulted, prior file bodies not edited —
the same canonical-reading shape as §0.3, §0.4.1 and §0.4.2.

§0.4.2 places the authoritative echo on the **resume state**. The reader that must obey
§0.4(5)'s persist-once rule is the **composer** at the §14.8.8.1 step 1 construction site,
and that site holds a `StepExecutionContext` — a carrier which, after §0.4.1, knows the
pre-hash *basis* and still knows nothing of the persisted *token*. The echo is therefore
written to a carrier the reader never consults, and §0.4.2's "MUST use it and MUST NOT
recompute" is **unsatisfiable as written** rather than merely unimplemented: on every
resume the composer would reach the recompute arm, which is precisely the branch §0.4(5)
declares to be the crash-fallback and not the normal path. Out-of-family review caught
this on the draft that carried only three amendments; naming the read carrier is the
minimum that makes the persist-once contract implementable at all.

| | |
|---|---|
| **Field** | `pre_dispatch_escalation_instance_id: str \| None = None`, on `StepExecutionContext` |
| **Value** | the **post-hash** token, exactly as persisted at §26.9 — never the pre-hash basis, and never a value recomputed by the reader |
| **Producer** | the **resume-side** branch-context composition site, which reads the §26.9 echo for the branch entry it is reconstituting and copies it verbatim. On a first (non-resume) escalation there is nothing persisted yet, so the field is `None` by construction |
| **Propagation** | inherited by `model_copy` like the context's other additive carriers; a branch child never re-derives it |
| **Byte-identity** | `None`-defaulted, so every non-fan-out and every first-escalation path is byte-identical to pre-arc |

**The composer's read order, stated as one rule over the two §25.x fields** (this is the
normative form of §0.4(5); the §0.4.2 sentence is the same rule seen from the writer's
side):

1. `pre_dispatch_escalation_instance_id` non-`None` → **use it verbatim.** Do not
   recompute, and do not compare it against a recompute — a mismatch is not an error the
   contract defines, and treating it as one would convert a benign basis evolution into a
   run-ending failure.
2. else `pre_dispatch_escalation_basis` non-`None` → **compute** per §0.4(2). This is the
   mint, and the mint→persist window of §0.8 is exactly the interval in which this arm is
   reachable on a path that already delivered.
3. else → this population has no pre-dispatch gate-owning branch;
   `HITLEscalationBrief.escalation_instance_id` stays `None` and the linear/validator path
   is byte-identical to pre-arc.

**This field is NOT basis material, and the distinction is load-bearing.** §0.5 bars the
*pre-hash* basis from every exported carrier; this field holds the **already-hashed**
token, which the delta exists to project. Conflating the two would either leak the basis
(if the bar were read as not applying to §25.17) or forbid the token's own delivery (if it
were read as applying to §25.18). The bar applies in full to `pre_dispatch_escalation_basis`
and does not apply to `pre_dispatch_escalation_instance_id`, whose value is by construction
the output of §0.4(2)'s one-way hash.

### §0.4.4 §2.2.A (NEW) — the token on the public pause-location projection

**Owning contract: C-CP-21** (the pause-view projection surface, published at
`Spec_Control_Plane_v1_112.md` §2.1/§2.2). Additive, `None`-defaulted, prior file bodies
not edited.

`PreDispatchUniformFallbackOnlyLocation` gains the **external token** as a read-only field.
The design record makes this a settled requirement rather than a nicety, in one sentence:
*"Without this the correlation loop terminates in a struct no operator reads."* An operator
holding a webhook request whose `Idempotency-Key` is branch-distinct has, without this
field, **no row in the pause view carrying the same value** — so the whole mechanism
delivers distinguishable requests that cannot be matched to anything the operator can act
on. An earlier draft of this leg deferred the entire pause-view half and thereby shipped
exactly that dead end.

| | |
|---|---|
| **Field** | `escalation_instance_id: str \| None = None`, on `PreDispatchUniformFallbackOnlyLocation` |
| **Value** | the **post-hash** token, identical to the one delivered on the webhook and persisted at §26.9 — one value, three surfaces, never recomputed per-surface |
| **Direction** | **read-only correlation, not addressing.** §0.7's one-way rule is unchanged and unqualified: no ingress surface accepts this token, and its presence on the projection does NOT make it a key |
| **Constraint restated** | `Spec_Control_Plane_v1_112.md` §2.2 constraint 2 applies verbatim — the **internal** identity still never appears on this surface. Only the hashed token does |
| **Absence** | `None` on every location that has no pre-dispatch gate-owning escalation — including every **already-durable** snapshot captured before this field existed. The field is **omitted from the serialized projection when `None`**, not emitted as `null`: a default `model_dump(mode="json")` would write `"escalation_instance_id": null` and the byte-identity promise would be false on exactly the legacy population it matters for. Same rule, same reason, as the §0.4.2 resume-state compatibility clause; a legacy-snapshot witness covers it |

**Why this is correlation and not the deferred addressing half.** §0.9 registers "the
pause-view addressing half" as NOT absorbed, and that stays true: addressing means the
operator can *resolve* a specific branch through the view, which requires the
uniform-response target selector this delta does not build. Publishing a value the
operator can **match** is strictly weaker and is the half the design record made a
precondition. Keeping the two apart is what lets this leg close the correlation loop
without opening the resolver arc.

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
`run_id`-shaped string; and raw basis material. This is a **structural** restriction in
the contract, not operator discipline — the C-CP-21 §21.3 palette-restriction precedent.

**ONE scoped exception, and its limit.** The branch **ordinal** is part of the pre-hash
basis, and `branch_context` (§0.6) exists to state it. The bar therefore does NOT cover
the ordinal rendered **as prose on `branch_context`** — without that carve-out the two
sections would contradict each other and no implementation could satisfy both. The
exception is exactly as narrow as the council scoped it: it is **not** precedent for
structured ordinal export. The ordinal MUST NOT appear as a typed/parseable field, on
any other key, or on any exported span attribute; and the carve-out extends to **nothing
else** in the basis — `snapshot_run_id` and the un-hashed identity stay barred without
qualification, including from `branch_context` itself.

**Cited, not settled here:** whether an OD redaction surface additionally filters these
attributes is unexamined; the bar above does not depend on it, since a redactor is a
mitigation rather than a contract.

### §0.6 The operator surface — four additive `payload_body` keys

All four are additive keys on the contractually-opaque `payload_body` Mapping (C-CP-21
§21.8); the wire body is byte-identical when they are absent.

| Key | Shape | Contract |
|---|---|---|
| `escalation_instance_id` | the **bare** post-hash token | The correlation value itself, emitted verbatim so it can be **equality-matched** against §0.4.4's projection field. See the note below — without this key the correlation loop does not close. |
| `branch_context` | display-only prose | The branch's ordinal **in prose**, under an explicit no-format commitment. Barred by §0.5 from carrying identity material. Never parsed. |
| `resolvability` | the closed `PauseLocationVariant` vocabulary (`Spec_Control_Plane_v1_112.md` §2.1, the public projection surface) | The **resolution CHANNEL**, never the outcome. For this population, `uniform-fallback-only`. |
| `resolvability_note` | prose | States the sole-member RULE and routes the operator; promises no live status. |

**Why the BARE token is a key and not merely implied by the `Idempotency-Key`.** The
webhook's `Idempotency-Key` carries the *composed* value —
`hitl:{parent_action_id}:{position}:{token}` per §0.4(2-bis) — while §0.4.4's projection
carries the *bare* token. §0.4(1) permits **equality and nothing else**: no consumer may
parse, split, or derive. An operator holding the composed key therefore cannot legitimately
extract the token to match it against the pause-view row, and one holding the bare token
cannot reconstruct the composed key without knowing the fold — which §0.4(1) also forbids
them from assuming. Without this key the two surfaces carry values that are *related but
not comparable*, and the correlation loop this delta exists to close stays open. Emitting
the bare token is what makes §0.4.4's projection matchable, and it is the design record's
own `payload_body` requirement. Out-of-family review found the omission.

Restating the direction, because a bare token on the wire invites the wrong reading: this
is **correlation, not addressing**. §0.7 is unchanged and unconditional — no ingress
surface accepts the token, and its presence in `payload_body` does not make it a key.

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
enumeration published at `Spec_Control_Plane_v1_112.md` §2.1, which the pause-view
projection already assigns, so the webhook and the pause view
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
to match is **counted-as-unaddressed** — that half is normative and unconditional.

**The diagnosis is ADVISORY until its carrier lands.** The intended surface is a typed
disposition on the resume outcome, but `ResumeResult` and `RunResult` are **closed
schemas** with no such field, and the typed carrier is separately registered (§0.9). This
delta therefore does **not** require a typed diagnosis: an implementation MUST surface the
condition through whatever diagnostic channel it has, and the requirement becomes
normative when the carrier's own leg lands. Softening it here rather than requiring a
field that does not exist is deliberate — the alternative would make this contract
unimplementable without bundling a separately-registered schema change.

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
children; the pause-view **addressing** half (the **correlation** half IS absorbed, at
§0.4.4 — see that section for why the two separate cleanly); the unguarded `entry_version`
carrier across the pause boundary; the typed resume-outcome diagnostics carrier; and
**the duplicate same-position placement shape** (§0.4(2), register row **`B-165`**) — two
placements declared at one position collide on the token, because the ratified basis (B)
hashes the position and not the declaration. Repairing it means revisiting the basis at the
design record, which is back-flow, not spec application.

### §0.10 The sequencing condition, discharged

The council bound this leg to a sequencing condition: the **resume-outcome diagnostics
leg ships with the spec leg, or the diagnostic-strength wording softens in the same
commit**. This delta takes the **second** option, and — after out-of-family review showed a first
draft had softened the *narrative* while leaving the *requirement* intact — the softening
is now in §0.7's normative text itself:

- the **counted-as-unaddressed** half is normative and unconditional;
- the **diagnosis** is **advisory** until the typed carrier lands, because `ResumeResult`
  and `RunResult` are closed schemas with no such field. Requiring a typed disposition
  today would make this contract unimplementable without bundling a separately-registered
  schema change.

A reader of §0.7 must not infer a shipped `ResumeKeyDisposition` type, and — equally —
must not read the advisory status as permission to drop the condition: it becomes
normative when the carrier's leg lands.

### §0.11 Zero-change statements

ZERO change to: the other six `HITLEscalationBrief` fields; `ValidatorFailClass`;
`ValidatorOutcome`; `ValidatorNextAction`; `ValidatorResult`; the `ValidatorFramework`
Protocol signature; the 4-value HITL response palette; `ResumeContext`'s key shape
(property 1's map stays `child_run_id`-keyed); the pre-dispatch internal identity's
non-addressability. ZERO new contract number. ZERO new fail class. ZERO enum extension.
ZERO OD / CXA / ADR / ADD / PRD revision — `HITLEscalationBrief` is intra-CP-axis, and the
tracing-export observation at §0.5 *consumes* the existing C-OD-32 namespace without
amending it.

**The Runtime spec is deliberately NOT in that list — see §0.13.** An earlier draft of
this delta left Runtime unmentioned, which reads as a zero-change claim by omission; it is
not zero, and stating so is a precondition of this leg being landable.

**One cross-axis note, owed and stated:** the OD-canonical `hitl.webhook.deliver` span is
declared head=1.0 always-sampled at C-OD-32.3, while the implementation's always-sampled
member set omits it. That divergence is a registered OD conformance defect and is **not**
this delta's to resolve; §0.5's bar is written to hold under either resolution.

### §0.12 Byte-identical-when-absent

On the linear/validator path the new field is `None`, the four `payload_body` keys are
absent, and the wire body is byte-identical to pre-arc — the webhook adapter is an
explicit field-by-field mapper, so an unset Optional adds no key. The ledger/audit key
composition is likewise byte-identical when the discriminator is absent, per the
`branch_path` precedent at C-CP-25 §25.16.

### §0.13 The Runtime-side delta, owed and named

This delta is **not** self-contained at the CP axis, and the accompanying Runtime spec
delta is a hard co-requisite rather than a courtesy cross-reference. The three sites:

| Runtime site | Today | Owed |
|---|---|---|
| §14.8.8.1 **step 1** — the `HITLEscalationBrief` construction site | constructs the brief without `escalation_instance_id`; it is the **minter** named at §0.4(3) | must populate the field per §0.4.3's three-arm read order, from the two `StepExecutionContext` carriers |
| §14.8.8.1 **step 2** — `idempotency_key = compose_hitl_action_id(step_context.parent_action_id, placement.position)` | a **two-argument** call, workflow-scoped and branch-blind | must fold the token per §0.4(2-bis)'s pinned output, so the webhook `Idempotency-Key`, the CP audit `action_id` and the F2 ledger key stay **one identity family** per §0.2 |
| `project_brief_to_payload` — the brief→wire adapter reached from **step 3** | an explicit field-by-field mapper over a fixed field set, receiving no branch context | must project §0.6's four `payload_body` keys — including the BARE token, the one that makes the webhook equality-matchable against §0.4.4's projection; without this site nothing emits them and §0.6 is unimplementable at the only place the wire body is built |

**Why the widening has to land inside `compose_hitl_action_id` and not beside it.** §0.2's
one-identity-family promise is what makes the audit join work; composing a separate
branch-distinct key alongside the existing one would produce two keys for one escalation
and reintroduce the §0.1 aliasing on whichever of them the F2 writer happened to use. The
single fold point is also what makes §0.5's bar enforceable — there is exactly one place
where a pre-hash value could leak into an exported carrier, and §0.4(2) hashes before it.

**Signature shape is Runtime-owned and is NOT prescribed here.** Whether the token arrives
as a third parameter, as a widened context argument, or by any other shape is the Runtime
delta's call, verified by execution at its own leg — this file states only the CONTRACT
the composed key must satisfy. That restraint is the §14.8.8.10 CONTRACT-not-mechanism
precedent the Runtime spec set for itself at v1.106, and the same discipline that this
row's own earlier attempts violated by prescribing wiring they had not executed.

**Byte-identity across the seam.** With `escalation_instance_id` absent (`None`) the fold
MUST reproduce the pre-arc two-argument key exactly, so the linear/validator population's
webhook `Idempotency-Key`, audit `action_id` and ledger key are unchanged — the same
absent-discriminator rule §0.12 states on the CP side, restated here because it is the
seam's acceptance criterion.
