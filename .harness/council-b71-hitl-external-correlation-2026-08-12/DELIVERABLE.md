# B-71 design record — branch-distinct EXTERNAL correlation identity for HITL escalations

**Version:** v3 (2026-08-12) · **Status:** DESIGN RECORD — spec leg STILL NOT
authorizable; preconditions **1 + 2 + 3 CLOSED on executed evidence**, **4 BOUNDED**,
**5 OPEN** · **Arc:** council (CP layer) per
`.harness/council/council-workflow.harness-aware.yaml` v1

## Change-note (v2 → v3)

Discharges §5 **precondition 3** — re-derive `resolvability` so it cannot assert a
false negative. Witness:
`harness-cp/tests/test_b71_resolvability_cannot_be_a_static_stamp.py` (5 tests,
green, mutation-probed — making the resolver ignore `hitl_responses` turns 2 RED).
Resolution at **§4-ter** below. **No spec text, no plan delta, no production-code
change.** Precondition 5 remains open, so the spec leg is still not authorizable.

The arc also surfaced a **new sub-fork inside the v1 recommendation itself**: v1's §5
precondition 3 recommended the field "routes the operator to the pause view for live
status". The pause view **cannot provide live status** — witnessed, not argued. That
is registered, with a recommended disposition, at §4-ter.3.

## Change-note (v1 → v2)

Discharges §5 **precondition 1** (execute the nested-fan-out collision witness) and
**precondition 2** (resolve the basis fork on that evidence, not on argument), and
bounds **precondition 4**. The witness is
`harness-runtime/tests/test_b71_escalation_identity_basis_collision_witness.py`
(13 tests, green). It composes every candidate basis from the **real production
composers** and runs them over the realizable collision tree. Mutation-probed four
ways, one per load-bearing dimension — folding a run-distinct component into
`compose_branch_child_context` turns the (A) collision test RED; neutering
`pre_dispatch_gate_owning_branch_identity` turns 3 of the (B) tests RED; making that
identity ignore `branch_index` turns the same-run peer test RED; dropping `placement`
from the (B) basis turns the two-placement test RED.

§4 is rewritten from OPEN FORK to RESOLVED; §5's precondition list is re-stated with
per-precondition status. **No spec text, no plan delta, no production-code change** —
v2, like v1, is documentary plus its witness.

Two v1 claims are corrected by the evidence, both in the direction of *less*
confidence in the v1 escalation, not more:

1. v1 §4 withdrew the council's `(parent_idempotency_key, branch_index, placement)`
   pick on the ground that `compose_branch_child_context` inherits
   `parent_idempotency_key` verbatim. Verbatim inheritance is real
   (`workflow_driver_types.py:632-645`) but **does not produce the claimed
   collision**: it is inheritance *within one run*, where `branch_index` still
   separates the peers, and nested fan-out is **cross-run** (every
   `compose_branch_child_context` call site descends from a single per-run fan-out
   point; nesting is reached by dispatching a child run through
   `child_workflow_runner`). `parent_idempotency_key` descends from
   `_compute_run_idempotency_key(run_id, workflow_id, entry_version)`
   (`workflow_driver.py:646-665`), so it is run-distinguishing. That triple survives
   the collision witness.
2. The **collision is real, but it lands on candidate (A)**, not on the council's
   pick — and on a shape neither the council nor any of the three reviewers named.

## Change-note (— → v1)

First versioned design record for register row `B-71`, discharging the row's standing
instruction: *"next attempt must ground the branch-distinct-identity design BEFORE
drafting spec text."* Produced by a five-voice council (primaries C1 orchestration +
C10 action-safety; consultants C9 reliability, C5 validation-contract, C11
operator-loop), a ten-seam cross-read reconciled to internal zero, and three
decorrelated reviewers (in-family adversarial, in-family transcript-aware advisor,
out-of-family Codex). **No spec text, no plan delta, no code.** The one substantive
change this arc makes to the workspace is documentary: it records a settled design
skeleton, an OPEN fork at the identity basis, two live defects at HEAD, and six
registered follow-ons.

---

## 1. The problem, restated at HEAD

Two peer fan-out branches sharing a `child_workflow_id` produce **byte-identical**
operator-facing HITL escalation requests. `HITLEscalationBrief`
(`validator_framework_types.py:134-151`) declares no run- or branch-distinct member,
and the delivery key is `compose_hitl_action_id(parent_action_id, placement)`
(`hitl_gate_composer.py:428-440`, used at `:1302`) — workflow-scoped. The escalation
fires **before** any child run exists, so no dispatched-child `run_id` can serve as
the discriminator (this is what falsified the row's three prior attempts).

## 2. Two live defects this arc surfaced at HEAD (independent of the fix)

**D-1 — per-peer HITL audit-entry loss.** The same composed `hitl_action_id` is the
F2 state-ledger `idempotency_key` **and** `action_id`
(`hitl_gate_composer.py:1566-1570`, orchestrator-verified). Under the IS writer's
key-only dedup (C-IS-07 §7.5) the second peer's HITL audit entry is dropped as an
idempotent no-op. **The workspace already fixed this exact aliasing class for the
sibling step-ledger write** via `branch_path` (U-CP-83 / C-CP-25 §25.16), documented
at `workflow_driver.py:674-684`: *"N parallel branches at the same declared
`step_index` do not collapse to one ledger entry under the IS writer's
`idempotency_key`-only dedup."* The HITL write is the un-fixed sibling — which both
confirms the defect and supplies the fix its precedent shape (branch discriminator
folded in; `None` on the linear path; byte-identical when absent).

**D-2 — the palette advertises actionability the resolver discards.**
`proposed_response_palette` is projected outward (`webhook_brief_adapter.py:81-83`)
on pre-dispatch requests whose responses are silently dropped
(`pause_state_projection.py:338-341`). An action affordance shipped across a trust
boundary that the ingress will not honor. Live today, independent of B-71.

## 3. The settled design (survived all three reviewers)

- **One opaque token**, `escalation_instance_id: str | None = None` — the sole new
  field on `HITLEscalationBrief`. `branch_index` on **neither** carrier. Optional-with-
  `None`-default is the honest discriminated shape of the two real populations
  (fan-out escalations vs linear/validator ones); a model split would re-commit
  falsified premise 2 one level up, because the operator-authored validator
  population cannot choose a variant.
- **Opaque, deterministic, one-way, ≥128 bits**, never truncated in the key or any
  equality-bearing field. Equality is the sole promised operation.
- **Mint authority:** one *authoritative minter* (the runtime composer at
  `_escalate_to_secondary_channel`, `hitl_gate_composer.py:1259-1268`, reached by
  widening the private helper to take `step_context` — both callers already hold it
  at `:2039`/`:2172`) and one *authoritative read* (persisted value wins over
  recompute). `ValidatorResult.escalation_brief` (`validator_framework_types.py:170`)
  is a second constructor of the TYPE but never a minter of the FIELD — non-`None`
  from it is ignored-and-diagnosed at the trust seam.
- **Pre-dispatch availability by construction** — the basis fields are *inputs* to
  `compose_child_run_id_seed`, not outputs of dispatch, so `PURE_PATTERN_NO_ENGINE`
  (where the child uuid is minted only at dispatch) is covered. Charter constraint 4
  satisfied.
- **Persist-once:** the snapshot echo is authoritative once written; deterministic
  recompute is the crash-fallback for the mint→persist window only (the webhook fires
  at `:1328` before the signal at `:1336`, so the external world can legitimately lead
  the snapshot). Independently required by the carried-forward population
  (`workflow_driver.py:10276-10281`), which has **no live mint at all**.
- **Stability:** the unresolved gate's lifetime **within one run, across re-fires AND
  resume cycles**. Non-commitments: across runs, after resolve/abort, across any
  activated `new_run_id` resumption (dead at HEAD).
- **Widening lands once**, inside `compose_hitl_action_id`, so the webhook
  `Idempotency-Key`, the CP audit `action_id`, and the F2 ledger key stay **one
  identity family** — preserving the caller-side audit join and closing D-1.
  Verified absorbable: all consumers trace to the one shared function.
- **Delivery:** at-least-once per re-fire, dedupable by stable key. **No harness-side
  suppression store** — the retention window is the consumer's; harness-side
  suppression would convert unresolved-gate visibility from at-least-once to
  at-most-once, the liveness failure for an escalation channel.
- **Ingress:** advisory-correlation-only as a **structural** one-way rule (the
  C-CP-21 §21.3 palette-restriction precedent — restriction in the contract, not
  operator discipline). No ingress surface accepts the token; a match is
  counted-as-unaddressed **and diagnosed** via a typed disposition landing on the
  resume outcome (primary) and the pause view (secondary). A log line alone is
  insufficient.
- **The webhook carries no ingress keys.** No real `run_id` transits it; addressing
  capability lives on the operator-held pause view. Fan-out-only population first;
  presence/absence is the discriminator.
- **Operator surface:** token + display-only prose `branch_context` (the ordinal in
  prose, under an explicit no-format commitment, **contractually barred** from
  carrying `snapshot_run_id`, the internal identity, run_id-shaped strings, or raw
  basis material) + a structured `resolvability` + `resolvability_note`; all
  `payload_body`-only (additive keys on the contractually-opaque Mapping, C-CP-21
  §21.8). Palette display bound to the posture — the disarm for D-2.
- **Public projection:** `PreDispatchUniformFallbackOnlyLocation` gains the EXTERNAL
  token, with v1.112 §2.2 constraint 2 restated alongside — internal identity still
  never. Without this the correlation loop terminates in a struct no operator reads.
- **2+-concurrent shape:** N distinct, stably-identified requests, collectively
  parked. Aggregate rejected on four control-flow grounds (no honest mint site; the
  escalations are not simultaneous; an aggregate has no stable key as membership
  changes, defeating the dedup the design depends on; the posture is satisfiable
  statically). The aggregate VIEW belongs on the projection.
- **Byte-identical, scoped:** the ledger/audit key composition is byte-identical on
  the linear path by construction (`None` discriminator, per the `branch_path`
  precedent); the webhook wire body is byte-identical because
  `project_brief_to_payload` (`webhook_brief_adapter.py:47`) is an explicit
  field-by-field mapper, so an unset Optional adds no key.

## 4-ter. PRECONDITION 3, RESOLVED (v3) — `resolvability` carries the CHANNEL, never the OUTCOME

### 4-ter.1 The two witnessed facts

**Fact 1 — resolvability is TIME-VARYING, so no mint-time stamp can carry it.**
`compute_hitl_uniform_fallback_eligible_run_id(root_snapshot, resume_context)` takes
the resume context, and its verdict for one *unchanged* branch flips with what else
has been addressed. The witness holds a pre-dispatch branch and its tree fixed and
varies only the `ResumeContext`: with its peer unanswered there are two unaddressed
gate-owners and nobody is eligible; **answer the peer and the same branch becomes the
sole unaddressed owner and IS resolvable** by the uniform fallback
(`workflow_driver.py:2895-2897`). A stamp minted at escalation time — before any
answer exists — would have had to guess which of these is true. **This retires the
`held-for-sole-resolution` stamp on evidence, not on argument:** it is a false
negative in exactly the situation the operator most needs the truth, and, as v1 noted,
posture-change redelivery is a registered follow-on that would never correct it.

Note the mix the witness needs, because it is also the realistic operator scenario:
one pre-dispatch branch **plus one HITL-addressable child**. Two pre-dispatch peers
cannot show the flip — a pre-dispatch identity is `never_keyable`
(`workflow_driver.py:2890-2894`), so it counts as unaddressed unconditionally and two
of them are never resolvable. The live question is "I answered the other one; am I now
the sole owner?"

**Fact 2 — the operator-facing read cannot answer it either.** Two independent
grounds, the second the stronger:

- *Within one journaled record:* `project_pause_locations` takes `root_snapshot`
  **alone** (`pause_state_projection.py:816`, pinned against the signature so a future
  widening must revisit this disposition), and `PausedWorkflowState` (`:403-435`)
  carries `workflow_id` / `created_at` / `staleness_token` / `locations` and no resume
  context. So responses staged in a `ResumeContext` cannot reach the projection.
- *Across records — the ratified one, **CITED not executed**:*
  `read_paused_workflow_state` (`harness_runtime/api.py:925`) declares, per Runtime spec
  v1.110 §14.14.9.1 (the RATIFIED `B-104` Reading D, Component 1), that the journal is
  append-only and writes **no pause-resolved marker**, so a resolved pause is
  **byte-indistinguishable** from an outstanding one. The read is explicitly *"NOT
  authority for the workflow is paused right now, and must not be presented to an
  operator ... as an outstanding-pause assertion."* **The witness does not invoke the
  accessor or the journal** — it constructs snapshots and compares CP projections. So a
  change that made Runtime record resolution, or filter resolved records, would leave
  all five tests green while this ground silently expired. It is carried as a **cited
  contract**, not an executed behaviour, and a Runtime round-trip is named as owed
  below (out-of-family Codex).

**A counter-hypothesis was raised and evaluated, not waved off.** Out-of-family Codex
argued Fact 2 fails in production, because a partial resume journals a NEWER snapshot
excluding the resolved peer — so reading *that* record would show the pre-dispatch
branch as the lone gate-owner. The structural half is real and is now pinned by the
witness: a snapshot carrying only the pre-dispatch branch does project exactly one
gate-owning location. What defeats the inference is the accessor's own ratified
contract above — an operator seeing one gate-owning location cannot conclude they are
*currently* sole, because the record may be stale and nothing in it says which. The
counter makes Fact 2 rest on a **spec-ratified** limit rather than on the projection
signature alone, which is a firmer footing than the v3 first draft had.

### 4-ter.2 The derived shape

**`resolvability` carries the resolution CHANNEL, and the channel vocabulary already
exists.** `PauseLocationVariant` (`pause_state_projection.py:98-116`, CP spec v1.112
§2.1) is a closed four-value enum of exactly this: `HITL_ADDRESSABLE` /
`EFFECT_FENCE_ADDRESSABLE` / `UNIFORM_FALLBACK_ONLY` / `TRANSITIVELY_PAUSED`. The
pre-dispatch location already carries `UNIFORM_FALLBACK_ONLY`, whose own docstring
draws precisely the line this precondition needs: *"Gate-owning, ALWAYS unaddressed,
resolvable ONLY by the uniform fallback **when it is the sole member** of the
unaddressed gate-owning set."* The channel is asserted; the sole-membership is not.

Three consequences, in order of how load-bearing they are:

1. **A channel value can never become a false negative.** It is true at mint and still
   true at resume, in every eligibility state — witnessed invariant across the flip.
   An outcome-bearing value has no such property and no minter can give it one.
2. **Do not mint a new vocabulary.** A second enum meaning the same thing would be a
   second authority over one concept, and the two would drift — the failure this
   record has already paid for twice. `resolvability` should carry the SAME closed
   variant the pause view assigns, so the webhook and the view cannot disagree.
3. **`resolvability_note` states the RULE, not a status.** It may say the branch is
   pre-dispatch, that it is never addressable by keyed response, and that a single
   uniform reply resolves it **only if it is the sole unaddressed gate-owning branch
   at resume**. It must not claim to report whether that is currently so.

### 4-ter.3 NEW SUB-FORK — v1's own recommendation over-promised

v1 §5 precondition 3 recommended the field "routes the operator to the pause view for
live status". Fact 2 falsifies the second half: **there is no live status at that
surface.** The routing half is fine — the view is where the operator sees the
locations — but the record must not promise a readout the view structurally cannot
produce. Three dispositions:

- **(a) Widen the view.** Give `project_pause_locations` a `ResumeContext` and report
  eligibility per location. Genuinely useful and the only option that makes the v1
  wording true — but it amends a **cleared public projection contract** (CP spec
  v1.112 §2.1), so it is its own spec leg under X-AL-3, and per Fact 2 it would ALSO
  have to answer the `B-104` staleness limit before a per-location eligibility flag
  could be presented to an operator at all. **It belongs to register row `B-155`** —
  *"No webhook re-fires when a parked pre-dispatch branch becomes sole-addressable"* —
  which already owns exactly this population and this live-posture question. (A v3
  first draft filed it under follow-on (4) / `B-157`; that row is the *already-
  dispatched children* addressing half — a different population and a different
  contract. Corrected on out-of-family review.)
- **(b) State the rule, promise no readout.** `resolvability_note` carries the
  channel plus the sole-member condition in prose; the operator is routed to the view
  for the location set, not for a verdict. Honest, needs no contract change, and
  survives (a) landing later.
- **(c) Route to the resolver instead.** Rejected: there is no operator-facing
  resolver surface to route to, so this trades a half-true promise for a fully empty
  one.

**Recommended: (b) for this spec leg, with (a) filed to `B-155`.** (b) is the
only one that is true at HEAD, and it does not foreclose (a) — when the view can
report eligibility, the note narrows rather than being rewritten.

### 4-ter.4 What precondition 3 does NOT close — witnessed vs cited

Same split §4-bis.5 applies to the basis decision, applied here.

**Witnessed** (executed, mutation-probed — neutering the resolver's consultation of
`hitl_responses` turns 2 of the 5 RED): the eligibility flip itself; that the
projection's sole input is the snapshot; that a snapshot with a genuinely TERMINAL peer
projects one gate-owning location; that the channel value is invariant across the flip.

**Cited, not witnessed** — two, both named as owed on the spec leg:

1. **The `B-104` liveness limit.** The witness never invokes
   `read_paused_workflow_state` or the journal, so the "a resolved pause is
   byte-indistinguishable from an outstanding one" ground is a **ratified contract
   read**, not an executed behaviour. A Runtime round-trip — pause, resolve, read, and
   assert the read still reports the resolved pause — would convert it. Until then, a
   Runtime change that began recording resolution would silently invalidate this half
   without reddening anything here.
2. **Shape coverage.** The witness covers the **HITL** uniform-fallback resolver. The
   effect-fence sibling (`compute_effect_fence_uniform_fallback_eligible_key`) has the
   same sole-member shape and is unexamined; out of B-71's scope (this row is HITL
   escalations), named so a later arc does not read this section as covering it.

Neither weakens the precondition-3 disposition: the `held-for-sole-resolution` stamp is
retired by the **witnessed** flip alone, and the channel-not-outcome shape follows from
that flip. The cited half bounds only how firmly the *pause-view routing* wording can
be stated.

---

## 4-bis. THE FORK, RESOLVED (v2) — basis (B), on executed evidence

§4 below is preserved verbatim as it stood at v1. This section supersedes its
verdict; read §4 for the fork as posed, and this section for how it closed.

### 4-bis.1 The collision tree the witness actually runs

A root PARALLELIZATION run of `wf-root` fans out two peer branches; **both** are
`SUB_AGENT_DISPATCH` steps pointing at the **same** `child_workflow_id`. This is not
a contrived shape — it is the shape `compose_child_run_id_seed`'s own docstring names
as live (`sub_agent_dispatch.py:371-380`: *"two sibling SUB_AGENT_DISPATCH workers
that dispatch the SAME `child_workflow_id` would derive the SAME child run_id →
ALIASED durable output + fence state → cross-branch corruption EVEN WITHOUT A
CRASH"*), and it is the reason `branch_path` was folded into the child-run seed at
U-CP-83. Each child run is itself a PARALLELIZATION run whose own branch 0 fires a
pre-dispatch escalation. The two child runs are genuinely distinct (the witness pins
this first, so the collision assertions are not vacuous).

### 4-bis.2 The evidence

Both stability columns are scoped to the **recompute** path. On the ordinary resume
path the persisted echo is read and nothing is recomputed, so no basis rotates there
and the columns do not apply — see the (C) paragraph below.

| Basis | Tree-wide distinct? | Recompute w/ `entry_version` bump, `run_id` recovered | Recompute w/ no `run_id` to recover |
|---|---|---|---|
| **(A)** `(parent_action_id, branch_index, placement)` | **NO — COLLIDES** | reproduces | reproduces |
| **(C)** `(parent_idempotency_key, branch_index, placement)` — the council's pick | yes | **NO — rotates** | no |
| **(B)** run-scoped internal identity + `placement` | **yes** | **yes — reproduces** | no |

(A)'s two "reproduces" cells are not a virtue: a basis that is constant because it
carries no run identity at all reproduces trivially, which is the same property that
collides.

**(A) is falsified.** A PARALLELIZATION branch's `parent_action_id` is
`_parallelization_fanout_action_id(workflow_id)` (`workflow_driver.py:8187` →
`:7168-7177`), which takes `workflow_id` **and nothing else** — it carries no run
identity at all. Two sibling child runs of the same `child_workflow_id` therefore
compose the identical triple, and the collision propagates through the real
`compose_hitl_action_id` (`hitl_gate_composer.py:428-440`, used at `:1302`) into the
webhook `Idempotency-Key`, the CP audit `action_id`, and the F2 ledger key at once.
This recreates B-71's own defect inside the fix — the failure v1 §4 predicted, on a
different shape than the one it predicted it on. The orchestrator-workers sibling has
the same run-blindness (`orchestrator_action_id = f"workflow:{workflow_id}:step:0"`,
`workflow_driver.py:12137`), so the defect is not PARALLELIZATION-local.

**(C) loses to (B) on precondition 4, not on uniqueness — and by a narrower margin
than this section first claimed.** The v2 first draft asserted (C) rotates on the
*ordinary* resume path, i.e. on every resumed escalation. **That was wrong, and
out-of-family Codex round 3 [P1] caught it.** Under the persist-once rule (§3) the
ordinary path reads the persisted echo and recomputes **nothing** — so on that path
neither basis rotates, and `entry_version` is irrelevant to both. The question only
bites in the **recompute** path, which is the mint→persist crash window for (B) and
(C) alike.

The discriminator survives inside that window, which is where precondition 4 lives:
`entry_version` is folded into `run_idempotency_key`
(`workflow_driver.py:3312-3316`), so **when a recompute happens with the child's
`run_id` recovered, (C) produces a different token and (B) reproduces the original**
(both witnessed). Choosing (C) would therefore make the unguarded-`entry_version`
defect (registered separately as a follow-on) load-bearing for token recovery in
exactly the window the token most needs to be recoverable in; (B) is insensitive to
it. Real, but a thinner margin than "every resumed escalation" — and the fork's
resolution does not rest on it, because **(A) is falsified outright on uniqueness**,
which is a stronger and independent ground.

**(B) survives both.** Its run component is the child's `run_id`, which a resume
reuses from the snapshot rather than re-deriving, so the token does not rotate on an
`entry_version` bump. Its only residual is the crash-BEFORE-persist window — which is
*precisely* the window the persist-once rule at §3 already declares and scopes ("the
snapshot echo is authoritative once written; deterministic recompute is the
crash-fallback for the mint→persist window only"). The witness pins that boundary in
both directions.

### 4-bis.3 The two objections that defeated (B) at the cross-read

- **"It omitted `placement`."** Fixed, and the fix is what the witness tests — every
  basis in the table carries `placement`.
- **"`snapshot_run_id` is not in composer scope."** The real objection, and it stands
  as stated: `StepExecutionContext` carries no run identity
  (`workflow_driver_types.py` field set — `workflow_id`, `parent_action_id`,
  `parent_idempotency_key`, `step_index`, `branch_index`, `tenant_id`, …; no
  `run_id`). It is **not** a blocker on the basis, because the driver **already
  composes exactly this identity** for exactly this branch population, at
  `workflow_driver.py:8346` and `:12670`, via
  `pre_dispatch_gate_owning_branch_identity(run_id, branch_index)`
  (`pause_state_projection.py:500`) — where `run_id` *is* in scope. Getting it to the
  mint site is one additive `StepExecutionContext` field, the shape the context
  already carries six times (`hitl_uniform_fallback_eligible_run_id`,
  `effect_fence_uniform_fallback_eligible_key`,
  `effect_fence_tree_wide_abort_present`, `sub_agent_descent`, `resume_context`,
  `child_resume_snapshot`) — each `None`-defaulted and byte-identical when absent.
  **The spec leg must carry this thread explicitly; it is not free.**

### 4-bis.4 What carries forward unchanged

The three-way-convergent finding stands and is re-pinned by the witness: **the
reverse-thread carrier must be keyed by a tree-wide identity, never by bare
`branch_index`** — the witness shows a bare-ordinal carrier collapsing the two
branches while (B) separates them, so the separation is attributable to the run
component alone.

### 4-bis.5 Scope honesty — what is witnessed, what is cited

The distinction matters on this row more than most: three of its four falsified
premises were claims that entered the record without being run.

**Witnessed** (executed, mutation-probed on both the (A) and (B) paths): every basis
value is read off a `StepExecutionContext` that the real `compose_branch_child_context`
produced, from a fan-out parent whose two identity fields are composed by the real
`_parallelization_fanout_action_id` / `_compute_run_idempotency_key` /
`_compute_step_idempotency_key`, threaded through the real `compose_branch_path` and
`compose_child_run_id_seed`. (A)'s collision, (C)'s survival-then-`entry_version`
rotation, (B)'s survival, verbatim inheritance's actual reach, and the
bare-ordinal carrier's collapse are all witnessed.

**Cited, not witnessed** — three, each load-bearing somewhere in §4-bis:

1. **The resume reuses the paused child's `run_id`** rather than re-deriving it
   (`child_workflow_runner.py:230-234`). This is what supplies the recovered `run_id`
   **inside the mint→persist recompute window** — the only place the B/C distinction
   applies at all, since on the ordinary resume path the persisted echo is read and
   nothing is recomputed (§4-bis.2). The witness proves only the half that is its own:
   that (B) takes no `entry_version` input, so a recovered `run_id` reproduces its
   token where (C)'s rotates. A live resume is not exercised.
2. **The fan-out parent context's field population.** The witness mirrors
   `workflow_driver.py:8185-8200` as a struct literal rather than reaching it through
   `execute_workflow`. Every *derived* field is production-composed — so a change to
   any composer is caught — but a change to how the driver *populates* the fan-out
   parent is not.
3. **Shape coverage.** PARALLELIZATION fan-out only. HIERARCHICAL_DELEGATION recursion
   and the DECENTRALIZED_HANDOFF stage chain (`workflow_driver.py:15375-15441`, where
   `parent_action_id` chains off the previous stage's `action_id` and `branch_index`
   is not a fan-out ordinal) are unexamined. (A) is already falsified, so those shapes
   cannot rescue it; whether they add a *further* constraint on (B) is open.

All three are **named residuals on the spec leg**, not silent gaps. None of them can
un-falsify (A) — the collision is witnessed directly — so the fork's resolution does
not rest on any of them; they bound how far the *stability* claims reach.

---

## 4. THE OPEN FORK — the identity basis (do not draft spec text against a guess)

*(v1 text, preserved verbatim; superseded by §4-bis above.)*

The council selected `(parent_idempotency_key, branch_index, placement.position)` and
rated tree-wide uniqueness [HIGH]. **That rating is withdrawn.**
`compose_branch_child_context` (`workflow_driver_types.py:586-650`) inherits
`parent_idempotency_key` **and** `step_index` verbatim into branch child contexts
(the branch-scoped key is composed downstream at U-CP-83, for ledger writes, not into
this context field). A nested fan-out's branch 0 and the root fan-out's branch 0, at
the same placement, therefore compose the **same triple** — recreating B-71's own
defect inside the fix. Codex named an existing witness that covers exactly this tree
shape (`harness-cp/tests/test_workflow_driver_hitl_uniform_fallback_property4.py`,
verified to exist); advisor predicted the failure category in advance.

**Candidate (A) — `(parent_action_id, branch_index, placement)`.** The codebase's own
branch-causality convention; `compose_branch_child_context`'s docstring argues
`(parent_action_id, branch_index)` is unique *even under nested fan-out*, resting on
action_id global uniqueness (IS §5). **Open question:** `parent_action_id` is per-step
at `workflow_driver.py:5331`/`:10932` but is `_parallelization_fanout_action_id(workflow_id)`
at `:8187`, which on its signature does not include `step_index` — if so, two
parallelization fan-outs in one workflow share it and (A) fails too.

**Candidate (B) — the tree-wide internal identity**
(`{snapshot_run_id}:pre-dispatch-gate:{branch_index}`, `pause_state_projection.py:521`)
hashed one-way, with `placement` added. C10's original proposal. Both objections that
defeated it at the cross-read survive and must be answered: it omitted `placement`
(fixable) and `snapshot_run_id` is not in composer scope (the real one).

**Whichever is chosen, the reverse-thread carrier must be keyed by a tree-wide
identity — not bare `branch_index`** (three-way convergent finding).

## 5. Hard preconditions on the spec leg

**Status at v3: 1 CLOSED · 2 CLOSED · 3 CLOSED · 4 BOUNDED · 5 OPEN.** The spec leg
remains NOT authorizable — **5 is unaddressed** and 4 is bounded rather than closed.
Discharged preconditions are struck through; their original text is kept so each
discharge is auditable against what was actually asked.

1. ~~**Execute the nested-fan-out collision witness** against the chosen basis. Cheap —
   the witness file exists and the shape is already covered for the internal identity.~~
   **CLOSED at v2** — executed at
   `harness-runtime/tests/test_b71_escalation_identity_basis_collision_witness.py`
   (13 green, mutation-probed four ways). Note the correction: the pre-existing file Codex named
   (`harness-cp/tests/test_workflow_driver_hitl_uniform_fallback_property4.py:327`)
   witnesses the *internal* identity's tree-distinctness, which was already settled;
   it does **not** exercise any candidate EXTERNAL basis. The new module is the
   witness this precondition actually asked for.
2. ~~**Resolve the basis fork** (A) vs (B) on that evidence, not on argument.~~
   **CLOSED at v2 — basis (B).** (A) collides; (C), the council's original pick,
   survives uniqueness but loses on precondition 4: inside the mint→persist recompute
   window, with the child's `run_id` recovered, (C) rotates where (B) reproduces. (On the
   ordinary resume path the persisted echo is read and NOTHING is recomputed, so no basis
   rotates there — see §4-bis.2.)
   Full evidence + the answer to (B)'s in-scope objection at §4-bis.
3. ~~**Re-derive `resolvability` so it cannot assert a false negative.** A sole
   pre-dispatch owner IS answerable — `if len(unaddressed) == 1: return unaddressed[0]`
   (`workflow_driver.py:2895-2897`). A static `held-for-sole-resolution` stamp would
   tell the operator not to reply to the one request whose reply resolves the run, and
   posture-change redelivery is a registered follow-on that would never correct it.
   **Recommended:** the field states the branch is pre-dispatch and routes the operator
   to the pause view for live status, rather than asserting non-actionability.
   `resolvability_note` re-drafts against whichever shape is chosen.~~
   **CLOSED at v3 — the field carries the resolution CHANNEL, drawn from the existing
   closed `PauseLocationVariant`; never the outcome.** The `held-for-sole-resolution`
   stamp is retired on a witnessed flip, not on argument. **The v1 recommendation's own
   second half is falsified in passing** — the pause view cannot report live status
   (`project_pause_locations` takes the snapshot alone), so `resolvability_note` states
   the sole-member RULE and promises no readout. Full derivation, the surfaced sub-fork
   and its recommended disposition at §4-ter.
4. **Close or explicitly scope the entry_version crash window** — crash after delivery
   but before persist, then resume after an `entry_version` bump, recomputes a
   different token. Registering the wider defect does not close this window. ~~May
   dissolve for free under basis (A) or (B).~~
   **BOUNDED at v2, not closed.** It does not dissolve for free. Under the chosen
   basis (B) the window is exactly as originally described — crash after delivery,
   before persist — and no wider. Two things make it no wider: the ordinary resume path
   recomputes nothing at all (persist-once, §3), and *within* the window the child's
   `run_id` is recovered from the snapshot (**cited**, `child_workflow_runner.py:230-234`,
   not witnessed — see §4-bis.5). The witnessed half is that (B) takes no `entry_version`
   input, so a recovered `run_id` reproduces its token where (C)'s rotates. The spec leg still owes an explicit scope
   statement **and a live-resume witness for the cited half**; what v2 removes is the
   *unbounded* reading, which is what basis (C) would have had.
5. **Carry the observability disposition** — resolve the charter's "not a span
   attribute" premise against C1's `hitl.escalation.instance_id` proposal, and extend
   C10's leak-bar analysis from the webhook channel to the **tracing-export** channel
   (`webhook.idempotency_key` at `webhook_delivery_composer.py:58,270`;
   `hitl.invocation.audit_ledger_entry_id` at `hitl_gate_composer.py:2238-2242`).

Plus the three conditions carried from the council: **sequencing** (the resume-outcome
diagnostics leg ships with the spec leg or C11's wording softens in the same commit),
**scope** (the `entry_version` guard defect stays registered; folding it in is a fork
to surface), and the **`branch_context` leak bar**.

## 6. Absorbed in-arc vs registered

**Absorbed** (same mechanism; splitting ships the widening half-applied): the D-1
audit-loss fix, mint-authority ignore-and-diagnose, the palette/`resolvability`
binding, the projection amendment, the persist-once reverse-thread field.

**Registered as follow-on `B-*` rows** (each an observable contract change to a
cleared mechanism → its own spec leg per X-AL-3): (1) uniform-response target
selector; (2) redelivery-on-posture-change; (3) uniform-treatment extension to
depth-0 root and already-dispatched children; (4) the addressing half (pause-view-side
capability question — the webhook answer is settled NO); (5) unguarded `entry_version`
across the pause boundary (rotates **every** step idempotency key on resume, not just
this token); (6) typed `ResumeKeyDisposition` + resume-outcome diagnostics carrier —
a **named companion leg, not a deferral**, bound by the sequencing condition.

## 7. Why this arc did not produce a spec leg, and why that is the result

B-71 has failed three times, each on a uniqueness-or-accessibility premise that
entered a fix without being run to ground. This deliberation caught the fourth
**before it reached spec text**: the council reconciled to internal zero on a design
whose load-bearing uniqueness claim the reviewer stage then falsified, with the
in-family voices, the in-family reviewers, and the out-of-family reviewer each
contributing a finding the others missed. Two claims were falsified *inside* the
deliberation before they could enter the record (C10's cited dedup consumer; C1's own
echo-implementability claim), and the orchestrator's own re-grounding falsified a
third (the basis). That is the process working — not a stalled arc.

**v2 addendum.** The same pattern held one round further out: v1's own escalation —
the withdrawal of the [HIGH] uniqueness rating — was itself an argument, not a run
result, and running it to ground moved the defect from the basis v1 accused to a
different one, on a tree shape nobody in the deliberation had named. Two of the four
falsifications in this row's history were of claims *made by the falsifier*. The
operative discipline is not "distrust the council" but "no uniqueness claim enters
this row's record without an executed witness" — which is why preconditions 1 and 2
were written as *execute* and *resolve on that evidence*, and why 3 and 5, which are
argument-work rather than evidence-work, are still open.
