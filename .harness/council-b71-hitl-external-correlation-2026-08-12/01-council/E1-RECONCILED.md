# E1 reconciled disposition — B-71 external correlation identity

*Composed by the council orchestrator 2026-08-12 from the five ledgered positions
(A1 C1/C10 primaries; A2 C9/C5/C11 consultants) and the two B-stage cross-reads.
**E1 is reconciled to internal zero**: C1's cross-read closes with "None with C10,
C9, C5, or C11 — every seam closes COHERE or REFINE-accepted"; C10's closes with
"None blocking" plus two conditions it holds as spec-leg MUSTs (both adopted below).*

---

## 0. Orchestrator re-grounding (the three load-bearing claims, verified at HEAD e033c1ce)

Per the subagent-reports-need-regrounding discipline, the claims the design rests on
were re-verified directly, not accepted from the agents' summaries:

1. **`StepExecutionContext` declares no `run_id`** — VERIFIED by direct read
   (`workflow_driver_types.py:287-300`: workflow_id / parent_action_id /
   parent_gate_level / parent_sandbox_tier / parent_actor / parent_entry_hash /
   parent_idempotency_key / tenant_id / step_index / branch_index / agent_role /
   hitl_placements). C1's S1 conclusion holds: `parent_idempotency_key` is the ONLY
   run-scoped seed in composer scope.
2. **The HITL F2 write keys on the composed action id** — VERIFIED
   (`hitl_gate_composer.py:1566-1570`: `action_id=Identifier(str(hitl_action_id))`,
   `idempotency_key=Identifier(str(hitl_action_id))` on the same `EntryPayload`).
3. **`entry_version` is absent from the pause protocol** — VERIFIED (0 occurrences in
   `harness-cp/src/harness_cp/pause_resume_protocol_types.py`).

**ORCHESTRATOR-ADDED CORROBORATION (sharpens C9's finding beyond what the council
had).** The workspace has ALREADY solved this exact aliasing class once, on the
sibling write path, and the HITL write is the un-fixed sibling.
`workflow_driver.py:674-684` documents `branch_path` (U-CP-83 / C-CP-25 §25.16)
existing for precisely this reason: *"N parallel branches at the same declared
`step_index` do not collapse to one ledger entry under the IS writer's
`idempotency_key`-only dedup (C-IS-07 §7.5)"*, with the `SINGLE_THREADED_LINEAR`
path passing `branch_path=None` and composing the prior key **byte-identically**
(regression-safe). The step-ledger write got the branch discriminator; the HITL F2
write at `:1566-1586` keys on the workflow-scoped `hitl_action_id` and did not.
This (a) independently confirms the key-only dedup premise from the CP side, (b)
confirms the defect is real rather than theoretical, and (c) **supplies the fix its
precedent shape**: a branch discriminator folded into the composed key, `None` on
the linear path, byte-identical when absent — exactly the widening C9-R3 proposes.

---

## 1. The reconciled design

**One opaque correlation token** — `escalation_instance_id: str | None = None`, the
sole new field on `HITLEscalationBrief` (`validator_framework_types.py:134-151`).
`branch_index` is on **neither** carrier (C5-T1, accepted by C1 at S2).

| Element | Reconciled position | Owner / adjudication |
|---|---|---|
| **Basis** | Domain-separated one-way digest over `(parent_idempotency_key, branch_index, placement.position)`, **≥128 bits**, never truncated in the key or any equality-bearing field | C1 basis (C5-T3 adjudicated it strictly stronger than C10's hash-the-internal-identity: C10's omits `placement`, colliding two gates on one branch, and needs `snapshot_run_id`, which is out of composer scope); C10 accepted at S1; C9-R4 floor accepted by both |
| **Seed** | `parent_idempotency_key` as-is — the only run-scoped value in composer scope; threading `run_id` onto the frozen `StepExecutionContext` REJECTED (ripples to 6 strategies + places a keyable-shaped identity in every composer's reach) | C1 S1, orchestrator-verified |
| **`entry_version` exposure** | Folded one-way into the seed (`workflow_driver.py:3312-3316` → `:646-665`) and **unguarded across the pause**. Confined to the recompute fallback only, made inert by persist-once, stated as a named precondition, and the wider defect REGISTERED not absorbed | C9 raised; C1 confirmed + sharpened (0 occurrences, `snapshot_hash` covers only workflow_id+run_id+step_index+state_summary at `:929-930`) |
| **Mint authority** | ONE *authoritative* minter (`_escalate_to_secondary_channel`, `hitl_gate_composer.py:1259-1268`) + ONE *authoritative read* (persisted snapshot wins over recompute). The operator-authored validator population (`ValidatorResult.escalation_brief`, `validator_framework_types.py:170`) is a second constructor of the TYPE but never a minter of the FIELD — non-None from it is ignored-and-diagnosed at the consumption boundary | C5-T2/NC-2; C1 corrected its own false "one mint site" claim at S6; C10 required it as structural trust-seam enforcement |
| **Threading (mint)** | Widen the private helper to accept `step_context`; both callers already hold it (`:2039`, `:2172`). No Protocol change, no driver change, no context-field add on the mint path. Covers `PURE_PATTERN_NO_ENGINE` because the basis is an *input* to `compose_child_run_id_seed`, not an output of dispatch — charter constraint 4 satisfied by construction | C1 Q1-residual |
| **Persist-once** | The snapshot echo is authoritative once written; deterministic recompute is the crash-fallback for the mint→persist window only (webhook fires at `:1328` before the signal at `:1336`, so the external world can legitimately lead the snapshot) | C9-R1; accepted by C1 (S4) and C10 (S4) |
| **Echo wiring** | Widen the disposition collection `set[int]` → `dict[int, str \| None]`, populated at the FOUR capture sites (`:9680`, `:9926`, `:14073`, `:14313`) via duck-typed `getattr(signal, "brief", None)` (harness-cp cannot import harness-runtime — hence the existing name-matched catch), read at the TWO construction sites (`:10374`, `:14727`) | C1's own MEDIUM claim SPLIT-FALSIFIED against the code and closed with the alternative threading |
| **Reverse thread** | A fourth sibling of the resume-carried pass-through family (`workflow_driver_types.py:483-545`) carrying `Mapping[int, str]` (branch_index → persisted token), computed once at the depth-0 root, hash-inert, `None` default → byte-identical. Needed because the composer mints before the driver persists, so re-fire requires snapshot → composer flow that does not exist today | C1 S4 (a leg C10's persist-once acceptance had not priced) |
| **Carried-forward rows** | `_pre_dispatch_gate_owning_carried_forward` (`:10276-10281`) recovers §25.19 warm-up-cohort followers withheld from this round — no escalation fired, no signal, no token mintable. Under mint-only they are necessarily `None`; **only persist-once carries their identity forward** — an independent requirement for it | C1 S4 (ii) |
| **Stability** | Stable for the unresolved gate's lifetime **within one run, across re-fires AND resume cycles**. Non-commitments: across runs, after resolve/abort, across any activated `new_run_id` resumption (dead at HEAD) | C9-T1/R2 exposed C10's MUST-4/N2 self-contradiction (re-fires CROSS epochs by construction); C10 and C1 both accepted the rescope; epoch defined at C5-NC-6 |
| **Widening site** | ONCE, inside `compose_hitl_action_id` (`:428-440`) — webhook `Idempotency-Key`, CP audit `action_id`, and the F2 ledger key stay ONE identity family, preserving the `:92-93` caller-side audit join and closing the live F2 audit-loss | C9-R3; accepted by C10 (S3) and C1 (S3) |
| **Delivery** | At-least-once per re-fire, dedupable by stable key. **No harness-side suppression store** — the retention window is the consumer's; harness-side suppression would convert unresolved-gate visibility from at-least-once to at-most-once, the liveness failure mode for an escalation channel | C9 (the re-fire knob, answered) |
| **Operator surface** | Token + display-only prose `branch_context` (ordinal IN PROSE, explicit no-format commitment) + structured two-value `resolvability` (`addressable` \| `held-for-sole-resolution`) + `resolvability_note`; all `payload_body`-only (additive keys on the contractually-opaque Mapping, C-CP-21 §21.8) | C11 designed; C10 confirmed MUST-NOT-7 is satisfied (it governs the IDENTITY, not display prose); C1 accepted in full |
| **Palette binding** | Palette display bound to the `resolvability` posture. This fixes a **live pre-existing violation at HEAD**: `proposed_response_palette` is projected outward (`webhook_brief_adapter.py:81-83`) on requests whose responses the resolver silently drops (`pause_state_projection.py:338-341`) | C11-T2, unaudited by either primary; C10 framed it as an action affordance shipped across a trust boundary; C1 classed it FM-F in its own self-audit |
| **Projection amendment** | `PreDispatchUniformFallbackOnlyLocation` gains the EXTERNAL token; v1.112 §2.2 constraint 2 restated alongside — internal identity still never. Without it the correlation loop terminates in a struct no operator reads | C11-T3; C10 gave the two-rule blast-radius verdict; C1 called it the correction it could not have found from its own chair |
| **Ingress** | Advisory-correlation-only as a structural one-way rule (C5-NC-7, C-CP-21 §21.3 style). A match is counted-as-unaddressed **and diagnosed** via a typed `ResumeKeyDisposition`, landing on the resume outcome (primary) and the pause view (secondary) — a log line alone is insufficient | C5-NC-10 + C11's landing-site ranking |
| **The addressing half** | **NO real `run_id` transits the webhook channel this arc.** Capability handles live on the operator-held pause view; advisory correlation on the outward channel | C10 answered its own seam Q3; C1 accepted |
| **2+-concurrent shape** | **N distinct, stably-identified, statically-flagged requests, collectively parked.** Aggregate rejected on four control-flow grounds (no honest mint site; escalations are not simultaneous; an aggregate has no stable key as membership changes, defeating the dedup the design depends on; MUST-5 is satisfied statically without it). §1.1(c) INERT re-pause disclosed, not relabeled. The aggregate VIEW belongs on the projection | C1 answered C10's seam Q2 |
| **Scope** | Fan-out-only population first (presence/absence is the discriminator, C5-NC-3); placement-inclusive basis is what makes a later uniform extension additive rather than breaking | C1 S8, C10 S10 |

---

## 2. What this arc absorbs vs registers

**Absorbed in-arc** (all are the same mechanism this design already touches; splitting
them would ship the widening half-applied):
the F2 audit-loss fix (C9-R3), NC-2 mint-authority ignore-and-diagnose, the
palette/`resolvability` binding, the projection amendment, and the persist-once
reverse-thread field.

**Registered as follow-on `B-*` rows** (each an observable contract change to a
cleared mechanism → its own spec leg per X-AL-3):

1. **Uniform-response target selector** — a property-6 extension keying by the external token on a NEW resume-context field, never `hitl_responses`.
2. **Redelivery-on-posture-change** — no webhook re-fires when N-1 peers resolve and the last becomes sole-addressable (`workflow_driver.py:2851-2898`).
3. **Uniform-treatment extension** to depth-0 root and already-dispatched-child escalations.
4. **The addressing half** — what survives after C10's NO for the webhook channel is the pause-view-side capability question.
5. **Unguarded `entry_version` across the pause boundary** — NEW, from C1's S1 grounding. A bump across a pause silently rotates EVERY step idempotency key on resume, not just this token. Strictly wider than B-71, inside the resume material-diff guard family.
6. **Typed `ResumeKeyDisposition` + resume-outcome diagnostics carrier** — a named COMPANION leg, not a deferral; the design record commits to it.

---

## 3. The two hard conditions the design record must carry

Both are held by their voices as spec-leg MUSTs rather than open disputes, and both
are adopted:

**(a) Sequencing (C1).** Registration (6) — the resume-outcome diagnostics leg — must
land **with** the B-71 spec leg. C11's `resolvability_note` promises the operator that
*"the resume outcome reports that the response did not attach"*; if (6) slips, that
sentence ships as a falsehood and **the wording must be softened in the same commit**.

**(b) Scope (C1).** The unguarded-`entry_version` finding is REGISTERED, not absorbed.
Any move to fold it into this arc is a fork to surface, not a convenience — it is a
pre-existing CP defect strictly wider than B-71 and sits inside a cleared mechanism.

**(c) Leak bar (C10).** `branch_context` prose is contractually barred from carrying
`snapshot_run_id`, the internal identity, run_id-shaped strings, or raw basis material
— the display channel must not become the leak the opaque token was built to prevent.
And the S7 ordinal-in-prose acceptance is scoped to that display field; it is **not**
precedent for structured ordinal export.

---

## 4. Falsified premises retired

The charter recorded three falsified premises B-71 had carried. This deliberation
retires the fourth-attempt risk by answering what each got wrong:

- *"run_id already accessible at the brief site"* — confirmed FALSE and now explained: `StepExecutionContext` declares no `run_id` at all (orchestrator-verified §0.1).
- *"a required field add is safe"* — the reconciled design uses additive-Optional, and C5 showed a discriminated model split would re-commit exactly this error one level up (the operator-authored validator population cannot choose a variant).
- *"run_id disambiguates peers"* — superseded: peers share the parent run_id; the discriminator is the branch ordinal folded into a one-way digest, never the raw run identity.

Two claims raised IN this deliberation were also falsified against the code before
they could enter the design: C10's dedup-consumer (i) as cited (no pause-store
synthesis at `webhook_delivery_composer.py:455-466` — that range is cost attribution),
and C1's echo-implementability claim (the construction site has no signal in scope;
the capture sites do — carrier revision, not shape revision).

---

*E1 CLOSED, internal zero. Next: E2 adversarial review of this disposition, then E3
decorrelated evaluators (Codex cold primer + advisor transcript-aware), then the
consolidated reconcile, then the E4 bounded gate.*
