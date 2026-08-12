# C9 reaction — B-71 (E1-A2, verbatim)

*(Orchestrator note: returned by the genuine C9 agent invocation, 2026-08-12.)*

## Tensions surfaced

**T1 — C10's stability scope contradicts its own ghost-request mitigation (targets C10 MUST 4 / MUST NOT 8 / N2).**
C10 commits stability "for the lifetime of the pause it describes, including gate re-fires *within that pause*" (MUST 4) while N2/MUST 8 explicitly non-commit stability "across pause epochs, resume cycles." But the B-72 re-fire topology that motivates MUST 4 crosses pause epochs by construction: the gate re-fires **on resume** — pause epoch 1 → operator resumes → unresolved gate re-escalates (a fresh `deliver_webhook` invocation at `hitl_gate_composer.py:1328-1330`) → re-pause = epoch 2. Every re-fire delivery lands in the *next* epoch. The redelivery-dedup / no-ghost-requests story therefore requires exactly the cross-resume-cycle stability N2 disclaims. As written, a conforming implementation could rotate the token at each resume boundary and violate no MUST while producing the ghost stream MUST 4 exists to prevent. Rescope needed (refinement R2 below). C1's failure-mode table has the correct scope implicitly ("identical identity + identical idempotency key on every re-fire") — but C1 never flags that this contradicts C10's written non-commitment.

**T2 — the "four dedup consumers" enumeration is one-falsified and one-short (targets C10 idempotency-sweep paragraph).**
Verified against `webhook_delivery_composer.py` at HEAD:
- (i) **Falsified as cited.** There is no "pause-store record synthesized from the key" at `webhook_delivery_composer.py:455-466`. That range is the cost-attribution call: `span_id=f"webhook-deliver-{idempotency_key}"` (:455) plus the B-23 `dispatch_disambiguator=str(uuid.uuid4())` (:472). The actual pause store (`journal_workflow_pause_store.py`, 892 lines) contains **zero** occurrences of `idempotency` or `hitl` — it does not key on this key at all.
- (ii) Verified: cost attribution fires per attempt-batch on both success and failure (:337-353); the synthesized span_id (:455) collides across peer branches *today* — widening fixes that; the uuid disambiguator (:465-472) already prevents F2-anchor drops per call, so cross-re-fire span_id reuse is benign.
- (iii) Verified: `response_idempotency_key` echoes the inbound key "for caller-side dedupe at the audit layer" (:92-93, :332).
- (iv) Verified: `ATTR_WEBHOOK_IDEMPOTENCY_KEY` (:58, :270) — cardinality-benign.
- **Missing fifth consumer, and it is load-bearing:** `compose_hitl_action_id` has **three** call sites, not one. Beyond the webhook key (:1302), the same string is the CP audit entry `action_id` **and the F2 state-ledger `idempotency_key`/`step_id`** at `hitl_gate_composer.py:1543, 1552-1553, 1566-1586` (`idempotency_key=Identifier(str(hitl_action_id))` at :1568 and :1584), under the IS writer's *key-only* dedup (C-IS-07 §7.5, cited at `workflow_driver.py:678-680`). Two peers responding to same-placement gates compose byte-identical F2 keys → the second peer's HITL audit entry is dropped as an idempotent no-op — a live per-peer **audit-loss** aliasing defect *today*, independent of the webhook. (A third site at :2238-2243 recomputes the key for a span attribute only — benign, but must stay consistent.)

**T3 — widening site is a fork neither primary pinned down (targets C1 carrier point 3 + C10 MUST 3).**
C1 says append the discriminator in `compose_hitl_action_id` (:428-440); C10 constrains only "the key must become branch-distinct." These differ materially given T2: widening **inside the shared helper** heals the F2 audit aliasing too, but changes the OD audit-trace `hitl:` action_id shape (prefix-stable, suffix grows — C1's own §25.16 argument extends, but the audit family was not in either primary's blast-radius sweep). Widening **webhook-only** leaves the audit aliasing unfixed *and* severs the identity between the webhook key and the audit action_id — breaking the (iii) caller-side audit-dedupe join that assumes they are one family (:92-93). This must be an explicit decision with witness tests over all five consumers, not an implementation detail.

**T4 — C1's snapshot echo re-opens two-mint drift under version skew unless read-precedence is specified (targets C1 carrier point 2 + failure-mode "two-mint-site drift").**
C1 forecloses drift by "minting once and threading the value." True within one process lifetime. But across deployments, C10's N1/N2 explicitly permit derivation changes. Sequence: epoch-1 deployment mints X (delivered externally, echoed into `PreDispatchGateOwningBranchResumeState`); derivation changes; resume under the new deployment re-fires and **recomputes** → webhook now says Y while the operator's snapshot says X — exactly the drift C1 claims foreclosed, re-opened at the version boundary. Fix in R1.

## Refinements proposed

**R1 — persist-once with deterministic mint as first-write and crash-fallback.**
Mint deterministically at the composer (C1's site, :1259); echo into the resume state (C1's carrier 2); **on re-fire, if the persisted echo is present, reuse it verbatim — recompute only when absent.** Crash-between-mint-and-persist is covered by determinism (recompute reproduces X: the webhook fires at :1328 *before* the signal at :1336 and before any driver-side recording, so the external world can be ahead of the snapshot; only a deterministic fallback closes that window — a fresh-random mint fails here). Snapshot-restore-from-older-epoch re-presents that epoch's persisted value — consistent by construction. Older §1.3a hash-stripped snapshots without the field take the recompute path (and pre-feature snapshots never exported an identity, so a fresh mint is correct). This makes the durable carrier authoritative once written, immunizing the external identity against derivation changes (T4) without giving up crash tolerance.

**R2 — rescope the stability commitment (resolves T1).**
C2/MUST 4 should read: *stable for the lifetime of the unresolved gate within one run — across gate re-fires and across pause-resume cycles*. Non-commitments: across runs; after the gate resolves/aborts; across a `new_run_id`-bearing resumption if that path is ever activated.

**R3 — widen once, inside `compose_hitl_action_id`, and witness-test five consumers (resolves T2/T3).**
One identity family across webhook key + CP audit action_id + F2 ledger key keeps the (iii) audit-layer join intact and closes the pre-existing per-peer F2 audit-loss aliasing as a side benefit. Impl-leg witnesses: webhook server-side dedup key distinctness; cost span_id distinctness; `response_idempotency_key` distinctness; span-attr cardinality; **F2 second-peer audit entry survives** (the new one). Re-fire dedup preserved: same branch's re-fire composes the identical widened key (N4 holds).

**R4 — no truncation below 128 bits of digest.**
The collision-recovery posture for a content-hash-class key is "treat as duplicate" — which *here* means cross-branch suppression, i.e. the exact defect B-71 exists to fix. Truncate for display if C11 wants, never in the key or the equality-bearing field.

## The re-fire/redelivery knob answered

**Mechanics at HEAD:** a re-fire is a *full fresh* `deliver_webhook` invocation — its own ≤3-attempt loop with 0.5s base delay (:117-169, :283-324), `Idempotency-Key` header on every attempt (:278-281). The harness holds **no dedup state and no retention window anywhere**: the composer is stateless per call, and the pause store never sees the key. The retention window in "same `idempotency_key` → same outcome within retention window" (spec §14.10.5 inv 1, :228-230) is the **consumer's**, not the harness's.

**Answer: re-delivery refreshes at the transport; suppression is a consumer-side retention policy — and it must stay that way.** The harness contract should be *at-least-once per re-fire, dedupable by stable key*. The harness MUST NOT add harness-side suppression: (a) new durable dedup store — framework-pull grain; (b) converts unresolved-gate visibility from at-least-once to at-most-once — the liveness failure mode; (c) the widened key is precisely what makes consumer-side suppression *safe*. `WebhookDeliveryExhaustedError` semantics per re-fire untouched (:283-324, :1286-1288).

## The stability-scope question answered (empirical, cited)

**`run_id`/`snapshot_run_id` is preserved across pause-resume cycles at HEAD — the two digest bases are the SAME stability class across resume cycles, but NOT the same sensitivity class.**

1. Depth-0 resume reuses the snapshot's run_id verbatim: `mcp_server.py:372` ("reuse the snapshot's `run_id` for audit/ledger coherence", :363-370).
2. Child re-entry likewise: `child_workflow_runner.py:230-236`.
3. The fresh-run_id escape hatch is dead at HEAD: `pause_resume_protocol_types.py:1176-1177` declares `new_run_id: str | None` — exactly one occurrence repo-wide (the declaration).
4. Property 6 already load-bears on preservation: resume compares live-frame run_id against snapshot-derived identity (`workflow_driver.py:8346-8348`, `:2875, 2890-2894`, `mcp_server.py:385-387`).

Consequences: C1's basis folds `workflow_id` + `entry_version` + `step_index` + `placement` — an `entry_version` bump at resume rotates C1's identity, and **no resume-validation guard covers entry_version** (material-diff checks at :8044-8148; integrity hash at `pause_resume_protocol_types.py:930`). C10's basis omits `placement` — no collision now (one gate per branch per epoch, B-79 config-hash guard), but under uniform-treatment extension a placement-blind basis hands two logical gates on one branch the same token AND key suffix → delivery loss by identity format. **Recommendation: digest over (run-scoped seed, branch_index, placement) with domain separation — placement in, `extras`/entry_version either out of the basis or guarded at resume.** With R1's persist-once, residual sensitivity shrinks to the mint-to-persist window. **Guard the preservation invariant itself:** state run_id-preservation-across-resume as a named precondition (or persist-once makes the identity survive even a future fresh-run_id resumption).

## Verdict on each primary's reliability-relevant falsifiable claims

C1: digest-basis-in-scope VERIFY; triple-uniqueness VERIFY (analytic); today's-key-collides VERIFY-AND-EXTEND (also F2 audit write :1568/:1584); snapshot-echo-implementable CAN'T-TELL (capture site unread); branch_index-stable VERIFY (:8071-8148); uuid-breaks-refire VERIFY; run_id-preserved VERIFY (upgraded to direct evidence).

C10: #1 VERIFY; #2 VERIFY; #3 VERIFY (never-diagnosed drop at :2890-2894); #4 VERIFY-AT-HEAD with named preconditions (dead new_run_id; derivation stability across deployments is exactly what N1/N2 refuse to promise → persist-once R1 is the failure-tolerant long-term design); #5 conclusion VERIFIED on a corrected enumeration (consumer (i) as cited does not exist; the missed F2 audit consumer also treats aliasing as loss).

— C9, reliability/recovery.
