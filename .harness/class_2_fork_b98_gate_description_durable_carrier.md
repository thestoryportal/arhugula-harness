# Class 2 Fork — B-98: gate description / question text is absent from every durable pause carrier

**Status: FILED 2026-08-01, awaiting operator ratification.** Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-96`'s, `B-97`(a)'s and `B-107`'s: **filing (this PR) → operator ratification →
spec leg (if owed) → impl leg.**

**Register row.** `B-98` at `.harness/forward-register.yaml:3026`–`:3053` (`status:
registered_finding`, no `pr:`) + prose at `.harness/post-phase-8-forward-register.md:1030`–`:1038`.
The row's `pr:` pointer and any status change ride the **ratification** leg, not this PR.

**Grounding HEAD.** `987f330b`. Every `§`/line cite below was re-resolved by direct read at this
HEAD. Three anchors the row's own text implies are **confirmed byte-exact and not silently
normalized**: `HITLPlacementKind` is a `StrEnum` at `hitl_placement.py:55` ✓; **zero** durable pause
carriers declare a field of that type ✓; and the row's *"every `placement` occurrence … is docstring
prose"* is **substantively true with ONE correction, recorded rather than normalized.** Recounted
programmatically at this HEAD *(figures corrected at out-of-family round 2 [P2] — the first pass
matched case-insensitively and over-counted by one)*: **16** lowercase `placement` substrings, of
which **3** sit inside the word *"replacement"*, leaving **13** genuine — **12 docstring prose plus
ONE `TYPE_CHECKING` import path** (`:46`, `from harness_cp.hitl_placement import HITLResult`), which
is an import, not prose. **Field declarations: 0** — the load-bearing half of the claim, untouched.
(A case-insensitive match yields 17/14 by additionally catching `HITLPlacementKind` in prose at
`:225`; §10.)

**Spec-side carry, verified UNMOVED.** The exclusion row *"gate description / question text | **Not
present in the durable snapshot at all.**"* lives at `Spec_Harness_Runtime_v1.md:3533`, inside
`### §14.14.9.2` (heading at `:3476`), and is **byte-identical** at the v1.109 head this HEAD
carries (`:1`) — i.e. preserved verbatim across the v1.108 (`B-97`(a)) and v1.109 (`B-100`) deltas,
exactly as the task framing states. Its siblings are the CP carry at
`Spec_Control_Plane_v1_112.md:54` (§0.6) and the Runtime change-note carry at
`Spec_Harness_Runtime_v1.md:73` finding (ii).

**What this filing does NOT do.** It does not re-open `B-69`'s ratified read-only projection
(shipped; the exclusion is deliberate and the record says so). It does not re-litigate `B-71`
(run-instance correlation on `HITLEscalationBrief` — three falsified premises are on that row's
record; a fourth mechanism claim is the non-convergent-hardening pattern this workspace stops on).
It does not pre-empt `B-99`'s reopening condition. It **corrects the row's own close_out** where
grounding falsifies its framing, and composes the result into the operator's decision.

---

## §1 The question, and what carries it

An operator who reads durable pause state at HEAD learns **where** a workflow is paused and **through
which resolution channel**, but not **what was asked**. The row's `close_out` therefore demands a
**capture-side carrier decision — which field, on which resume-state carriers, with what hash
disposition — BEFORE any read-side projection field is added**, and names the C10 ⊥ C11 tension the
`B-69` convening surfaced without resolving: *action-safety wanting a closed vocabulary and no
unbounded free-text channel in durable state, against operator-loop wanting a description a human can
actually act on* (`.harness/forward-register.yaml:3048`–`:3051`).

**This filing's grounding pass finds the row's three sub-decisions are NOT the decision, and that the
real one is a fourth the row does not name.** `[HIGH]`

- **"Which field" is pre-answered in an unexpected direction.** There is no author-written gate
  description anywhere in the product — but there *is* real text, and **on the route that actually
  produces a durable pause the operator ALREADY RECEIVES IT**, out of band, in the webhook payload
  (`webhook_brief_adapter.py:76`–`:89`). What the operator cannot do is **join** that webhook to the
  location the accessor returns. **The durable gap is CORRELATION, not description** — and
  correlation is `B-71`'s surface, which this row declares distinct on a narrower basis than the
  grounding supports (§3(i)).
- **"Which carriers" is pre-answered too — at TWO sites, not one.** `PauseSnapshot` top-level (which
  serves the `HitlAddressable` variant for free, because that variant projects from the paused
  child's **own** snapshot rather than the parent's branch row) **plus** a per-row sibling on
  `PreDispatchGateOwningBranchResumeState`, which a top-level field structurally cannot serve — one
  parent snapshot may carry several such rows with different placement data (§3(iv)).
- **"What hash disposition" is fully pre-answered** by a five-instance in-house precedent, the most
  recent of which is a bare scalar on this exact type (§3(v)).
- **The undecided question is the CHANNEL.** There *is* real free text in the HITL path —
  `HITLEscalationBrief.escalation_reason: str` (`validator_framework_types.py:150`) — and it is
  **discarded at one named line**, `workflow_driver.py:5375`–`:5394`, where `harness-cp` catches
  `harness-runtime`'s `HITLPauseRequestedSignal` **by class name** and reads nothing off it (§3(ii)).
  Whether to open that hop is the decision; the payload type is a second-order question **inside** it
  (§3(iii)).

---

## §2 Current behaviour at HEAD `987f330b`

| Surface | State |
|---|---|
| **The durable envelope** | `PauseSnapshot` (`pause_resume_protocol_types.py:745`, `extra="forbid"`, `frozen=True` at `:757`) — **15 fields** (AST-counted; the class docstring still says *"8-field"*, the Class 3 cite-hygiene item the `B-69` record already routed into its impl arc). None is text |
| **Durable resume-state carriers** | **12** nested models in the same file. The four that matter here: `PausedChildBranchResumeState` (`:893`, **4 fields** — `branch_index` `:913`, `step_id` `:918`, `child_snapshot: PauseSnapshot` `:924`, `child_workflow_id` `:934`); `PreDispatchGateOwningBranchResumeState` (`:208`, **5 fields**, incl. `hitl_gate_config_hash` `:265`); `EffectFencePausedBranchResumeState` (`:947`); `OrchestratorEffectFencePausedResumeState` (`:671`) |
| **The one contentful HITL field on the envelope** | `hitl_gate_config_hash: str \| None = None` (`:786`) — a **sha256 digest**, not text. `B-79` slice 2 / CP v1.111 §1.2 property 7. Present ONLY for a `HITL_PENDING` capture at the three single-owner sequential sites (`:791`–`:793`) |
| **`HITLPlacementKind`** | `hitl_placement.py:55`, a **closed 3-value** `StrEnum` — `PRE_ACTION="pre-action"` `:63`, `SUB_AGENT_BOUNDARY="sub-agent-boundary"` `:66`, `VALIDATOR_ESCALATION="validator-escalation"` `:69`. **Closed at D5** per its own docstring (`:58`–`:59`): *"extension is a Workflow §4.1.2 Class-2 D5 revision"* |
| **Fields typed `HITLPlacementKind`, repo-wide, non-test** | **THREE**, and **none is durable**: `HITLPlacementTrigger.placement_kind` (`hitl_placement.py:109`, a static 3-row spec table); `HITLPlacement.position` (`:186`, the workflow-**definition** input); `RuntimeHITLGateComposer.applicable_placements` (`hitl_gate_composer.py:845`, a live bootstrap-constructed dataclass). Plus one function parameter, `compose_hitl_action_id(..., placement_position)` (`:426`) |
| **TWO durable-pause routes, and they differ in what the operator saw** | **Route 1 — `DURABLE_ASYNC` cell synchrony** (`hitl_gate_composer.py:2013`): escalates at `:2021`–`:2028` and **always raises (`NoReturn`, comment `:2020`) BEFORE reaching the sync ask**; `:2029` says *"Fall through to step 4f sync-blocking"* only for the other branch. **Route 2 — timeout escalation** (`:2150`–`:2158`): the operator *was* asked, then timed out, then escalated. Both raise `HITLPauseRequestedSignal` and both end at the same capture |
| **The sync-gate question text (route 2 only)** | `prompt=f"HITL gate at {placement.position.value}"` (`hitl_gate_composer.py:2051`), with `options=sorted(palette)` (`:2048`). `VALIDATOR_ESCALATION` placements are filtered out of `matching` at `:1778`, so only **two** of the three values are wrap-time reachable |
| **The webhook payload — the operator surface on BOTH routes** | `webhook_brief_adapter.py:76`–`:84`: `escalation_reason`, `parent_step_id`, `fail_class`, `fail_detail_hash`, `proposed_response_palette`; plus `approval_id=brief.parent_action_id` (`:86`) and `idempotency_key` (`:87`) — the latter being `f"hitl:{parent_action_id}:{placement_position.value}"` (`hitl_gate_composer.py:436`), which **embeds the placement position** |
| **The one real free-text field in the HITL path** | `HITLEscalationBrief.escalation_reason: str` (`validator_framework_types.py:150`). Its **two** production values at the composer are hard-coded literals — `"durable_async_cell_synchrony"` (`hitl_gate_composer.py:2026`) and `"hitl_timeout_escalate_secondary_channel"` (`:2158`) |
| **The richest human-readable rendering** | `compose_escalation_prompt` (`escalation_prompt.py:18`), whose returned string (`:41`–`:47`) interpolates `parent_step_id`, `parent_action_id`, `fail_class`, `escalation_reason` and the palette. **Never durable** — it is composed at the gate and never reaches a snapshot |
| **The capture signature** | `PauseResumeProtocol.capture_pause_snapshot` (`pause_resume_protocol.py:411`) admits `workflow_id`, `run_id`, `step_index`, `pause_reason`, the six resume carriers, and `hitl_gate_config_hash`. **No text parameter exists**, and `extra="forbid"` makes a smuggled one unrepresentable |
| **The hash** | `_compute_snapshot_hash` (`pause_resume_protocol.py:726`–`:841`) — an **explicit** canonical dict (`:754`–`:759`: `workflow_id`/`run_id`/`step_index`/`state_summary`), **not** a `model_dump` of the model, plus **seven** conditional keys each added only when non-`None`. `pause_reason`, `created_at`, `state_ledger_anchor` are **not** covered |
| **The read surfaces — TWO, both text-free** | (a) `read_paused_workflow_state` (`api.py:925`) → `PausedWorkflowState` (`pause_state_projection.py:403`, **4 fields**: `workflow_id` `:420`, `created_at` `:423`, `staleness_token` `:427`, `locations` `:433`) over a closed union of **4 variants / 10 source shapes / 7 carriers** (`:386`–`:400`). (b) `harness-inspect` pause-journal enumeration (Runtime §13.7, heading `:1288`), whose term 4 (`:1301`) forbids it to **deserialize a `PauseSnapshot` at all** |
| **What the `hitl_responses`-keying variant shows** | `HitlAddressableLocation` (`pause_state_projection.py:168`): `pause_reason` + `step_index` (base, `:161`/`:164`), `child_run_id` `:179`, `step_id` `:182`, `branch_index` `:183`. **No `step_kind`** — declared absent by type because its source carrier declares none (`:170`–`:172`) |

---

## §3 Five grounding findings that reshape the row

### (i) THE DEMAND QUESTION RE-GROUNDED — the description ALREADY REACHES THE OPERATOR; the durable gap is CORRELATION `[HIGH]`

**This finding replaces an earlier draft of this section that was FALSIFIED at out-of-family review
round 1 [P1], and the falsification is recorded rather than smoothed away (§10.1).** The draft
argued that the only operator-facing question text is the sync prompt at `hitl_gate_composer.py:2051`,
and therefore that "what was asked" is exactly one closed-vocabulary value. **That is false for the
route that actually produces a durable pause.**

**There are TWO routes to a durable `HITL_PENDING` capture, and route 1 never reaches the prompt.**

```python
if joint_binding_present and _synchrony_attr is SynchronyClass.DURABLE_ASYNC:   # :2013
    # ... "Always raises (NoReturn)."                                            # :2020
    await self._escalate_to_secondary_channel(..., escalation_reason="durable_async_cell_synchrony", ...)  # :2021-:2028
# End of step 4-bis. Fall through to step 4f sync-blocking.                       # :2029
```

Route 1 (`DURABLE_ASYNC`) escalates and raises **before** `:2050`'s `ask(...)`. Route 2 (timeout
escalation, `:2150`–`:2158`) reaches the prompt first, then times out, then escalates. **On both
routes the operator's actual surface is the webhook**, and it is not thin:

| Webhook carries | Cite |
|---|---|
| **CONTRACTUAL payload** — `escalation_reason` (the free text), `parent_step_id`, `fail_class`, `fail_detail_hash`, `proposed_response_palette` | `webhook_brief_adapter.py:76`–`:84` |
| `approval_id = brief.parent_action_id` | `:86` |
| `idempotency_key`, which *incidentally* renders as `f"hitl:{parent_action_id}:{placement_position.value}"` — **but this is NOT a contract** | `:87`; composed at `hitl_gate_composer.py:436`, whose own docstring says *"**Suggested** shape … deferred to implementation discretion at v1.11 per spec §14.8 deferred-list"* (`:430`–`:431`) |

**The placement is therefore NOT contractually available to a webhook consumer.** `[HIGH]`
*(Correction at out-of-family round 4 [P1]; an earlier draft read the key's current rendering as
though it were a field, which is precisely the mechanism-vs-contract confusion this workspace's own
§6.3 CONTRACT-not-mechanism ruling exists to prevent.)* **The consequence is a finer partition, and
it cuts both ways:**

- **the REASON TEXT is contractually delivered** (`payload_body["escalation_reason"]`, `:77`) — so a
  durable copy of it **duplicates**; and
- **the PLACEMENT is not** — it survives only inside an explicitly discretionary string, so a typed
  durable placement field is **genuinely net-new**, not redundant.

**And the delivery is not incidental — it is a CODE-ORDER PRECONDITION of the pause.** `[HIGH]`
Inside `_escalate_to_secondary_channel` the webhook is awaited at `hitl_gate_composer.py:1324`,
**before** `pause_requested_flag.set()` (`:1329`) and **before**
`raise HITLPauseRequestedSignal(...)` (`:1332`). A failed delivery propagates instead of pausing.
**So for every durable HITL pause that can exist, the webhook was delivered first, by construction.**

**So the operator, at the moment the pause becomes durable, already holds — CONTRACTUALLY — the
reason, the step, the fail class and the palette** (and, non-contractually, the placement inside an
opaque key). What they cannot do is **join** that webhook to
the location `read_paused_workflow_state` returns: the webhook keys on `parent_action_id` /
`parent_step_id`; the projection keys on `child_run_id` / `step_id` / `step_index`
(`pause_state_projection.py:168`–`:183`).

**AND THE WHOLE PAUSE CLASS IS UNREACHABLE IN STOCK BOOTSTRAP — a second-order fact that reframes
the row's urgency, surfaced at out-of-family round 3 [P1] and verified end-to-end.** `[HIGH]`

1. Default config → `webhook_delivery_composer_factory.py:104`–`:110` returns **`None`** (the
   documented opt-out branch: *"Pre-v1.26 production-default state preserved"*).
2. → `joint_binding_present` (`hitl_gate_composer.py:2009`–`:2012`) is **False** → the
   `DURABLE_ASYNC` branch at `:2013` never fires; `:2029` falls through to sync-blocking.
3. → On **opt-in**, the factory constructs the composer at `:123`–`:143` **with no `webhook_config`**
   — the v1.26 `WebhookDeliveryComposerConfig` is an **empty marker** whose endpoint substrate is
   explicitly deferred to a follow-on **FM-2** arc (factory docstring `:17`–`:22`).
4. → `deliver_webhook_for_brief` then raises `RuntimeError` at
   `webhook_delivery_composer.py:538`–`:542` (*"requires a non-None webhook_config supplied at
   composer construction"*) — at `hitl_gate_composer.py:1324`, i.e. **before** the flag and the
   signal.

**`_escalate_to_secondary_channel` is the ONLY producer of `HITLPauseRequestedSignal`, and that
signal is the ONLY source of the three `pause_reason=HITL_PENDING` captures**
(`workflow_driver.py:5383` / `:11192` / `:15628`; the B-32 relabels at `:10354`/`:10360` and
`:14695`/`:14701` are *derived* from a nested child's reason and so inherit the same precondition).
**Therefore no durable `HITL_PENDING` pause — and hence no `HitlAddressableLocation` — is
production-reachable at this HEAD without operator-supplied `WebhookConfig` that no shipped config
surface can supply.** Only tests inject it.

**This does not make the finding invalid — it dates it.** `B-98` describes a real gap in a pause
class whose *own* production reachability is gated behind the same FM-2 arc. That is a **grounding
fact the ratification is entitled to**, and it supplies the sharpest trigger in §4's demand test
(D-0).

**THE DURABLE GAP IS CORRELATION, NOT DESCRIPTION.** `[HIGH]` And correlation is `B-71`'s surface.
The row asserts the two are distinct — *"`B-71` is about DISAMBIGUATING two identical-looking
escalations; this row is about DESCRIBING one"* (`.harness/forward-register.yaml:3043`–`:3045`). That
distinction is **real but narrower than the row implies**: the describing is already done, out of
band, on the operator's side. Carrying a description into durable state would **duplicate** a value
the operator already received rather than supply one they lack — unless the resuming party is not the
webhook recipient, which is itself an unstated premise (§4 Reading C, D-1).

**The `B-69` ruling therefore survives, on a different and better ground than the draft claimed.**
§6.2's field table justifies position as *"**what `UniformFallbackOnly` gives the operator in place
of a key, and it is sufficient**"* (`.harness/council-b69-pause-state-accessor-2026-07-30.md:337`);
SEAM 3 closed *"`surfaced + resolved by symmetric empirical defeat`"* (`:234`), with C10 conceding
*"My closed-vocabulary counter-proposal was capture-side scope wearing the same costume I accused
C11's prose of wearing"* (`:238`); §10's routing row prices it as *"Explicitly declined for this arc
by the ergonomics voice"* (`:494`). None of that rests on the falsified premise.

**Stated against interest — twice.** `[HIGH]`
1. The gap is **not** nothing. `HitlAddressableLocation` is the variant an operator must key and it
   carries the least context — no `step_kind` (`pause_state_projection.py:170`–`:172`), and the pause
   happened **inside the child's workflow**, where a parent `step_kind` would not describe the gate
   anyway.
2. **The correlation reframe assumes the resumer is the webhook recipient.** For the design-time
   `solo-developer` persona that holds. It does **not** hold for `team-binding` or
   `multi-tenant-compliance` (the committed bridging arc, root `CLAUDE.md` §10.2), where the operator
   resuming may never have seen the webhook. **This filing does not claim the gap is imaginary — it
   claims the gap at the CURRENT persona tier is a join, not a missing string.**

### (ii) THERE IS A TEXT SOURCE — AND IT IS DISCARDED AT A FAMILY OF NAMED SITES `[HIGH]`

The row's framing implies free text is simply absent. It is not: it exists, it is composed, it is
delivered out-of-band, and then it is **dropped at a single identifiable hop**.

| Hop | Site | What is alive |
|---|---|---|
| 1 | `hitl_gate_composer.py:2021`–`:2028` | `dispatch()` → `_escalate_to_secondary_channel(..., escalation_reason="durable_async_cell_synchrony", ...)` |
| 2 | `:1289`–`:1296` | `durable_brief = HITLEscalationBrief(..., escalation_reason=escalation_reason, ...)` — **text alive** |
| 3 | `:1324`–`:1326` | `deliver_webhook_for_brief(durable_brief, idempotency_key, tenant_id=…)` — text leaves **out of band**, to the webhook only |
| 4 | `:1329` | `self.pause_requested_flag.set()` |
| 5 | `:1332`–`:1335` | `raise HITLPauseRequestedSignal(brief=durable_brief, delivery_result=…)` — **text alive, on the exception** |
| **6 — THE DROP** | `workflow_driver.py:5375`–`:5394` | `if type(exc).__name__ == "HITLPauseRequestedSignal":` → `capture_pause_snapshot(workflow_id=…, run_id=…, step_index=…, pause_reason=HITL_PENDING, hitl_gate_config_hash=_captured_hitl_gate_config_hash(step, manifest_entry, …))`. **`exc.brief` is never read.** |
| 7–9 | `pause_resume_protocol.py:411` → `:469` → `durable_pause_resume_protocol.py:124` | structurally text-free (`extra="forbid"`) |

**AND HOP 6 IS NOT ONE SITE — it is a FAMILY, which is a cost this filing initially under-priced.**
`[HIGH]` *(Surfaced at out-of-family round 5 [P1].)* The `:5375` catch is the **sequential** one. The
fan-out paths catch the same signal separately and keep **only the branch ordinal**:
`pre_dispatch_gate_owning_dispositions.add(branch_index)` at `workflow_driver.py:9614` and `:14247`
(with sibling catches at `:9843`–`:9861` and `:14000`–`:14008`), each discarding the signal's payload
before re-raising. **Every one of those sites feeds a
`PreDispatchGateOwningBranchResumeState` row — the per-row carrier §3(iv) shows a top-level field
cannot serve.** So A-2 and B must open the channel at **each** of them, not at one.

**The enumeration is capped BY RULE rather than by list**, so an unlisted site cannot silently escape
the obligation: *any `HITLPauseRequestedSignal` catch that records a durable disposition MUST retain
the payload, and the impl leg inventories them.* The four sites above are this filing's
verified-at-HEAD inventory, not a closed set.

**A grounding note that cuts A-2's value at these sites specifically.** `[MODERATE]` Both verified
fan-out catches record in their own comments that the gate which fired is a **`SUB_AGENT_BOUNDARY`**
gate on a `SUB_AGENT_DISPATCH` step (`:9608`–`:9609`; `:14233`–`:14235`). If that holds across all
four — which the impl leg must confirm rather than assume — then the *firing placement is invariant*
for this carrier and A-2's per-row payload would be a constant. **This is stated as a lead, not a
finding**; it would, if confirmed, mean the per-row half of A-2 buys nothing.

**Hop 6 is also a cross-axis boundary, and the code says so in its own comment**
(`workflow_driver.py:5368`):
*"harness-cp cannot import from harness-runtime per the workspace dependency graph"* — which is why
the catch is a **class-name string comparison** rather than an `except HITLPauseRequestedSignal`.
Reading anything off `exc` therefore means a duck-typed `getattr` against a runtime-owned shape from
inside CP, or re-homing the signal's payload to `harness-core` — a genuine **carrier-home** decision
(`[[carrier-home-defect-pattern]]`), not a field-add.

**And the text, once you look at it, is closed-by-provenance.** `escalation_reason` is typed `str`
(`validator_framework_types.py:150`) but its **two** production values at this composer are
hard-coded literals (`hitl_gate_composer.py:2026`, `:2158`) — precisely C10's `step_kind` complaint
at the `B-69` convening, *"closed-vocabulary by provenance not by type … the difference between a
promise and an invariant"* (`.harness/council-b69-pause-state-accessor-2026-07-30.md:242`). It is a
forward channel by **type**, not by current content.

### (iii) THE REAL FORK IS THE CHANNEL, NOT THE PAYLOAD — and this re-orders the row's decisions `[HIGH]`

Once (ii) is on the table the option set **splits along a seam the row does not draw**:

- **Driver-side capture (no new channel).** `_captured_hitl_gate_config_hash`
  (`workflow_driver.py:2738`) **already materialises** `applicable_placements: tuple[HITLPlacement, ...]`
  at `:2772` — at the exact pause-capture moment — and then discards everything but the sha256
  (`_hash_hitl_gate_config`, `:2712`–`:2735`). Carrying the **positions** costs one return value from
  a function already called at the capture site. This is the CP v1.99 shape verbatim: *"a value CP
  already received at the pause site but previously discarded"* (`Spec_Control_Plane_v1_99.md:9`).
  **But it yields the DECLARED (ADD-folded) configuration, not the FIRING placement** — the gate positions
  configured on the pausing step, which is a weaker answer to *"what was asked."*
- **Composer-side capture (opens hop 6).** The **firing** `placement.position` is known only inside
  the composer's `for placement in matching:` loop (`hitl_gate_composer.py:1786`), on the runtime
  side of the drop. Getting it — or `escalation_reason` — requires opening hop 6.

**Therefore: carrying a closed enum value (A-2) and carrying the brief's text (B) cost the SAME
channel and differ only in payload.** The row's C10 ⊥ C11 tension is real, but it lives *inside* the
"open hop 6" branch, not across the whole decision. In the "do not open hop 6" branch there is only
one buildable option (A-1) and no tension to convene on. `[MODERATE]` — this re-framing is a
reading of the seam, not a fact; the facts under it are `[HIGH]`.

### (iv) THE CARRIER ANSWER IS **TWO** SITES — and one of them is free `[HIGH]`

*(Sharpened at out-of-family round 1 [P2], which correctly caught an earlier draft's §1 bullet
claiming ONE top-level field reaches every variant. It does not, and the reason is structural — see
the second bullet below.)*

The row asks *"on which resume-state carriers."* The tree walk answers it.

`_walk` (`pause_state_projection.py:590`) recurses into `paused_child.child_snapshot` at `:681`–`:689`,
and emits the `HitlAddressable` entry from **that child's own snapshot** — `_gate_owning_leaf_entry(snapshot, child_position=child_position)`
at `:640`, gated on `reason is WorkflowPauseReason.HITL_PENDING` at `:639`. The parent's
`PausedChildBranchResumeState` supplies only `step_id`/`branch_index` positional context
(`_ChildPosition`, `:579`).

**Consequence 1 — the primary variant is FREE.** A field on `PauseSnapshot` — top-level, sibling to
`hitl_gate_config_hash` at `:786` — is visible to `HitlAddressable` automatically, with **no change
to `PausedChildBranchResumeState` at all**. The same field serves
`DepthZeroRootUniformFallbackOnlyLocation`, which `_gate_owning_leaf_entry` emits from the same
snapshot at depth 0.

**Consequence 2 — the pre-dispatch variant needs its OWN row-level field, and a top-level one cannot
substitute.** `PreDispatchUniformFallbackOnlyLocation` is constructed **per row** from
`resume_state.pre_dispatch_gate_owning_branches` (`pause_state_projection.py:650`–`:665`), and a
single parent snapshot may carry **several** such rows whose steps declare **different** placements.
A top-level scalar is therefore not merely inelegant here — it is **structurally incapable** of
representing the variant. The sibling site already exists:
`PreDispatchGateOwningBranchResumeState.hitl_gate_config_hash` (`pause_resume_protocol_types.py:265`),
which is per-row for exactly this reason.

**So the carrier answer is TWO sites, both already precedented, not a survey of twelve carriers —
and the split between them is forced by cardinality, not taste.** The docstring at `:795`–`:804`
pre-argues the top-level half for `hitl_gate_config_hash`: *"A single top-level field serves all
three sequential sites … a top-level field needs no such machinery since it is a bare scalar, not a
nested carrier dump"* — and `B-79` slice 1's separate per-branch field is the other half of the same
precedent.

### (v) THE HASH DISPOSITION IS PRE-DECIDED — AND ADDITIVITY REMOVES THE "DECIDE NOW" PRESSURE `[HIGH]`

**The mechanism.** `_compute_snapshot_hash` builds an **explicit** canonical dict
(`pause_resume_protocol.py:754`–`:759`), so a new `PauseSnapshot` field is **hash-invisible by
default** — it changes nothing unless threaded in as a keyword and given a conditional block. The
template for a bare scalar is `hitl_gate_config_hash`'s own, verbatim at `:835`–`:839`:

```python
if hitl_gate_config_hash is not None:
    canonical["hitl_gate_config_hash"] = hitl_gate_config_hash
```

For the nested `PreDispatchGateOwningBranchResumeState` sibling the path-aware recursive drop already
exists at `_strip_default_fanout_resume_fields:670`–`:671`.

**The precedent chain, resolved to its origin.** The row says *"per the drop-when-empty precedent"*
without naming it. It is:

| Arc | Field | Cite |
|---|---|---|
| **ORIGIN** — `B-HIERARCHICAL-PAUSE` | `FanOutResumeState.paused_child_branches`, drop-when-**empty** | `Spec_Control_Plane_v1_45.md:10`, `:36`; cleared at `.harness/clearance/Spec_Control_Plane-v1_45-cleared-2026-06-21.md:5` |
| v1.58 | `synthesis_step_id`, drop-when-`None`, **path-aware-recursive** | `Spec_Control_Plane_v1_58.md:29` |
| v1.65 | `effect_fence_paused_branches` | `Spec_Control_Plane_v1_65.md:31` |
| v1.97 | `PeerFanOutResumeState.paused_child_branches` | (the PARALLELIZATION analogue) |
| **v1.99 — nearest** | `PausedChildBranchResumeState.child_workflow_id`, drop-when-`None` at every depth | `Spec_Control_Plane_v1_99.md:9`, `:24`, `:40` |
| **B-79 — nearest BARE SCALAR** | `PauseSnapshot.hitl_gate_config_hash` | `pause_resume_protocol_types.py:786`, `:806`–`:810`; hash block `pause_resume_protocol.py:835` |

Distilled at `.harness/harness-context-carrier-and-hash-patterns.md:39` and the
`[[new-surface-audit-hash-and-config-not-carrier]]` pattern (`pause_resume_protocol.py:753`).

**A Class 3 cite-hygiene finding, recorded rather than absorbed.** `Spec_Control_Plane_v1_99.md:40`
attributes the discipline to *"v1.94's `synthesis_step_id`"*. **Falsified programmatically:**
`synthesis_step_id` first occurs at **v1.58** and appears in exactly `{58, 59, 65, 68, 97, 99}` —
**v1.94 does not contain the string at all.** The attribution is wrong by 36 versions. It changes no
disposition; it is filed here so a later arc citing v1.99's chain does not inherit it.

**AND THE LOAD-BEARING CONSEQUENCE — stated because it cuts against acting now.** `[HIGH]` The
`B-99` reopening condition rests on an asymmetry: *"an exclusion decided while the field is empty is
free, whereas the same exclusion **after** it carries ledger content is a **removal from a shipped
caller-facing contract**, which nobody makes"*
(`.harness/council-b69-pause-state-accessor-2026-07-30.md:347`; spec form at
`Spec_Harness_Runtime_v1.md:3528`). **That asymmetry runs the OTHER WAY for an ADDITION.** Adding a
drop-when-`None` field later is byte-compatible by construction (every precedent above says so
explicitly), and adding a field to the closed projection union later is likewise additive. **There is
therefore no "decide it now or pay more later" pressure on `B-98` — the pressure `B-99` correctly
identifies for an exclusion simply does not transfer to an inclusion.**

---

## §4 The readings

### Reading A-1 — carry the DECLARED (ADD-folded) `HITLPlacementKind` tuple, driver-side, no new channel

- **Field.** `hitl_gate_placements: tuple[HITLPlacementKind, ...] | None = None` on `PauseSnapshot`
  (sibling to `:786`) and on `PreDispatchGateOwningBranchResumeState` (sibling to `:265`).
- **Source.** `_captured_hitl_gate_config_hash` (`workflow_driver.py:2738`) returns the positions
  alongside the digest — the tuple is already in scope at `:2772`.
- **Semantics, named precisely** *(corrected at out-of-family round 5 [P2]; an earlier draft called
  this the "APPLICABLE" set, which it is not)*. The local is
  `fold_step_hitl_placements(manifest_entry.hitl_placements, binding.hitl_placement)` — the
  **DECLARED, ADD-folded workflow configuration**, captured *before* the composer applies any of its
  three narrowings: its own instance filter (`hitl_gate_composer.py:1767`), the
  `VALIDATOR_ESCALATION` removal (`:1778`), and `removed_placements` (`:1937`–`:1986`). **A-1 can
  therefore report a position that could not have fired.** Either the field is documented as *declared
  configuration* (honest, cheap, and still useful as orientation), or the effective set must be
  sourced — which needs the composer's own view and so collapses A-1 into A-2's channel cost. **The
  filing recommends the former**; the operator should know the field is configuration, not history.
- **Hash.** Drop-when-`None`, `pause_resume_protocol.py:835`–`:839` template; nested drop per `:670`–`:671`.
- **Read side.** One field on `HitlAddressableLocation`, `PreDispatchUniformFallbackOnlyLocation`
  and `DepthZeroRootUniformFallbackOnlyLocation`; Runtime §14.14.9.2's exclusion row (`:3533`)
  narrowed, not deleted (free text stays excluded).
- **Cost.** Smallest available. Zero cross-axis threading, zero new exception surface, zero OD change
  (a closed enum is not the "locations' associated payload" OD §30.5.1 limit 1 forbids).
- **Buys.** *Which gate positions were configured on the pausing step.*
- **Does NOT buy.** *Which placement fired.* On a step with one applicable placement these coincide;
  with two they do not, and the tuple cannot say which.

### Reading A-2 — carry the FIRING `HITLPlacementKind`, threaded across hop 6

As A-1, but the value is `placement.position` from `hitl_gate_composer.py:1786`, surfaced on
`HITLPauseRequestedSignal` (`:381`) and read at `workflow_driver.py:5375`.

- **Buys — and this is the ONE reading whose gain survives §3(i) intact.** `[HIGH]` The exact
  placement that gated, **typed**. The webhook does carry that value today, but only inside
  `idempotency_key`, whose composition `compose_hitl_action_id`'s own docstring calls a
  *"**Suggested** shape … deferred to implementation discretion"* (`hitl_gate_composer.py:430`–`:431`)
  — so no conforming consumer may parse it. **A-2 therefore adds genuinely net-new, contractually
  readable information; it is NOT redundant against the webhook.** *(Assessed as redundant at round 2
  [P2]; that over-corrected, and it is REVERSED here at round 4 [P1] on the mechanism-vs-contract
  distinction. Reading B's redundancy — over the contractual `escalation_reason` — is untouched.)*
- **Costs.** Opens hop 6. Requires either a duck-typed `getattr` from CP against a runtime-owned
  attribute, or re-homing the signal payload to `harness-core` — a carrier-home decision, and the
  one place this reading is materially bigger than A-1.
- **Payload risk.** Nil: a closed enum, itself D5-locked (`hitl_placement.py:58`–`:59`).

### Reading B — carry `HITLEscalationBrief.escalation_reason` (free text by type)

Thread `exc.brief.escalation_reason` (`validator_framework_types.py:150`) across hop 6 into a
`PauseSnapshot` field.

- **Buys.** A genuine reason string in durable state, and a forward channel that becomes richer if
  the brief ever does. **But it DUPLICATES rather than supplies** — the same string already reaches
  the operator in the webhook body (`webhook_brief_adapter.py:77`) on both durable routes. Its only
  net-new value is for a resumer who is **not** the webhook recipient (§3(i), against-interest 2).
- **Costs, and they compound.**
  1. **Same hop-6 / carrier-home cost as A-2**, plus a `str` of unbounded length crossing it — a size
     bound becomes a contract term, not an implementation detail.
  2. **An OD re-adjudication is OWED as a CHECK — and becomes a mandatory amendment only if the text
     is ALSO emitted.** *(Scope corrected at out-of-family round 3 [P2]; an earlier draft called it
     unconditionally FORCED, which overstated Reading B's cascade.)* OD v1.36 §30.5.1 (`:64`) has the
     read event emit **per-variant counts only**, and disclosure limit 1 (`:71`) forbids the
     locations' associated payload; §30.5.4 (`:104`) then declares the redaction contract **"NOT
     ENGAGED, because nothing redactable is emitted."** **Those rules govern the EMISSION, not the
     projection** — so a durable/caller-facing description with telemetry left unchanged leaves
     §30.5.4 literally true. What *does* change is limit 1's stated rationale, which is written as
     derived from the projection's own exclusions; once the projection stops excluding, the limit
     must be re-grounded on its own terms or amended. **This is the same precondition shape `B-99`
     registers** — *"a redaction contract as a **PRECONDITION** of any inclusion"*
     (`.harness/forward-register.yaml:3074`–`:3076`; council record `:493`) — arriving one door over,
     and it becomes hard the moment anyone proposes emitting the field.
  3. **The payoff is two hard-coded literals** (`hitl_gate_composer.py:2026`, `:2158`). A closed
     enum minted from them would be information-identical at zero channel risk — but minting one
     retypes a shipped C-CP-28 field, which is strictly larger than this row.
- **As the row frames it — an author-written *description* — it remains UNBUILDABLE without first
  minting an authoring surface** (a text field on `HITLPlacement`, `hitl_placement.py:176`) and
  threading it. `escalation_reason` is a *system* reason, not an author's description; substituting
  one for the other silently redefines what the row asked for.

### Reading C — DEFER, with the demand test STATED so the row reopens on evidence

Amend the `close_out` with §3's grounding; keep `status: registered_finding`; add a **falsifiable**
demand test — **four disjuncts, any one fires**:

- **D-0 — the pause class becomes production-reachable.** The **FM-2 webhook-config arc** lands
  (operator-supplied `WebhookConfig`, deferred at `webhook_delivery_composer_factory.py:17`–`:22`),
  so that a durable `HITL_PENDING` pause can occur outside tests at all (§3(i)). **This is the
  sharpest trigger and it dominates the other three**: until D-0, `B-98`'s harm surface cannot be
  produced in stock bootstrap, and the row is a finding about a dormant class.

- **D-1 — a description exists that the WEBHOOK DOES NOT ALREADY DELIVER to the resuming operator.**
  *(Tightened at out-of-family round 2 [P2], which correctly found the first form over-triggering.)*
  Either:
  - **(a) a description surface lands that is NOT projected into `WebhookPayload.payload_body`**
    (`webhook_brief_adapter.py:76`–`:84`) — e.g. `HITLPlacement` (`hitl_placement.py:176`) gains an
    author-written text field, which the brief does not carry and the webhook therefore cannot
    deliver; **or**
  - **(b) the resumer ceases to be the webhook recipient** — the webhook stops being the delivery
    channel, or a supported flow resumes a pause through an operator who never received it (i.e. the
    workspace advances past `solo-developer` on the committed bridging arc, root `CLAUDE.md` §10.2).

  **Explicitly NOT a D-1 on its own: `HITLEscalationBrief.escalation_reason`
  (`validator_framework_types.py:150`) acquiring a non-literal production value.** That value is
  projected into every webhook at `webhook_brief_adapter.py:77`, so a richer reason reaches the
  operator by the existing channel and creates no durable *lack* — it fires D-1 only in conjunction
  with (b). *Until D-1, a durable description duplicates rather than supplies (§3(i)).*
- **D-2 — the channel opens anyway.** Any arc threads content off `HITLPauseRequestedSignal`
  (`hitl_gate_composer.py:381`) across the `workflow_driver.py:5375` drop point. *The carrier-home
  cost `B-98` would pay is then already paid, and A-2/B become marginal.*
- **D-3 — an observed misdescription.** An operator-loop report of a response composed against the
  wrong gate that `pause_reason` + position + `step_kind` did not prevent. *The harm class, not the
  convenience.*

**Why "stated" matters.** *"Open only if the operator loop demands it"* is unfalsifiable as written;
D-1/D-2/D-3 are each checkable by grep or by an incident. This converts the row's gate from a vibe
into a trigger of the same shape `B-99` already uses.

---

## §5 The row's three decisions — two collapse, one is pre-decided, and a FOURTH is the real one

| Row decision | Disposition after grounding |
|---|---|
| **(1) Which field** — free text vs closed `HITLPlacementKind` | **RE-FRAMED, then collapses toward closed.** No author-written description exists; the only text is `escalation_reason`, two literals, closed-by-provenance (§3(ii)) — **and it already reaches the operator via the webhook** (§3(i)), so the durable question is whether to duplicate it, not whether to supply it |
| **(2) Which carriers** | **COLLAPSES to TWO** — `PauseSnapshot` top-level (serving `HitlAddressable` for free, since it projects from the child's **own** snapshot) **plus** a per-row `PreDispatchGateOwningBranchResumeState` sibling, which a top-level field cannot substitute for on cardinality grounds (§3(iv)) |
| **(3) Hash disposition** | **PRE-DECIDED** — drop-when-`None`, five in-house precedents, nearest bare-scalar template at `pause_resume_protocol.py:835` (§3(v)) |
| **(4) — NOT IN THE ROW: open hop 6?** | **THE ACTUAL DECISION.** Everything above the driver/composer seam is cheap and precedented; everything below it is a cross-axis carrier-home commitment (§3(iii)) |

---

## §6 Recommendation — **Reading C**, runner-up **A-1**, and AGAINST **B** and **B′**

`[MODERATE]` **Recommend C.**

1. **The pause class this row is about is NOT PRODUCTION-REACHABLE at HEAD.** `[HIGH]` The sole
   producer of `HITLPauseRequestedSignal` cannot get past `hitl_gate_composer.py:1324` without an
   operator-supplied `WebhookConfig` that no shipped config surface can provide (the FM-2 deferral,
   `webhook_delivery_composer_factory.py:17`–`:22`), and that raise precedes both the pause flag
   (`:1329`) and the signal (`:1332`). **`B-98` therefore describes a real gap in a dormant class**
   (§3(i)). Building a capture-side channel for a state that cannot occur outside tests is the
   clearest possible case for leaving a registered finding registered — and **D-0** exists so the row
   fires the moment that stops being true.
2. **The DESCRIPTION half of the row is already delivered, contractually.** `[HIGH]` Wherever this
   pause *can* exist, the webhook was delivered first by code order, carrying `escalation_reason`,
   `parent_step_id`, `fail_class` and the palette as contractual payload
   (`webhook_brief_adapter.py:76`–`:84`). **The durable gap for the text is a JOIN, not a missing
   string** — and the join is `B-71`'s surface, not this row's. *(Scope narrowed at round 4 [P1]:
   this argument covers the TEXT, which the payload carries contractually. It does NOT cover the
   PLACEMENT, which survives only in a discretionary key — see point 4.)*
3. **The `B-99` asymmetry runs the other way here.** (§3(v)) `B-99` must decide an **exclusion** now
   because reversing one later is a removal from a shipped contract. `B-98` proposes an **addition**,
   which every drop-when-`None` precedent makes byte-compatible whenever it lands. **There is no cost
   to waiting**, which is exactly the condition under which a registered finding should stay
   registered.
4. **The PLACEMENT half has a real, non-redundant gain — and it still does not carry the decision.**
   `[MODERATE]` *(Conceded at round 4 [P1], against this recommendation's interest.)* Because
   `compose_hitl_action_id`'s shape is explicitly discretionary (`hitl_gate_composer.py:430`–`:431`),
   a typed placement field is **net-new information no conforming consumer can obtain today** — so
   A-2's value is real, not redundant, and an earlier draft of this filing was wrong to say
   otherwise. **What still carries the decision is point 1**: net-new information about a state that
   cannot occur in stock bootstrap is not yet worth a cross-axis channel. Under D-0 this point
   inverts, which is exactly why D-0 is the dominant trigger.
5. **The undecided decision is a cross-axis one, and it should be paid for by a real requirement.**
   Opening hop 6 (§3(iii)) means a duck-typed CP read of a runtime shape or a `harness-core`
   re-homing. That is the kind of commitment made *for* a demand, not *in anticipation* of one.

**Runner-up: A-1.** `[MODERATE]` If the operator weights the `HitlAddressableLocation` thinness
decisively, **A-1 is the only reading with zero cross-axis cost**, and it is genuinely mechanical:
the tuple is already computed and discarded at `workflow_driver.py:2772`, the carriers are two, the
hash disposition is a five-line copy of `:835`–`:839`, and the payload is a D5-locked closed enum
that engages no OD posture. **A-1 is preferred over A-2 on COST, not on information** — round 4 [P1]
establishes A-2's answer is strictly better and genuinely net-new, but A-2 pays the whole cross-axis
channel, and where the declared set is singleton and unnarrowed the two coincide. **A-1 is preferred over C only
if the operator judges the orientation gap worth closing while the pause class is still dormant** —
it does not close a defect, it improves a read that nothing in stock bootstrap can currently produce.

**Recommend AGAINST B — and against B′, for DIFFERENT reasons that an earlier draft conflated.**
*(Separated at out-of-family round 5 [P1], which correctly found the draft charged B with an
authoring cost B does not incur.)*

- **B as defined at §4** — carry `exc.brief.escalation_reason`. **Its source already exists**, so it
  needs **no authoring surface**. It is recommended against because it **duplicates a value the
  webhook already delivers contractually** (`webhook_brief_adapter.py:77`), pays the multi-site
  channel of §3(ii), adds a size bound as a contract term, and re-grounds OD §30.5.1's
  disclosure-limit rationale — becoming a mandatory §30.5.4 amendment **only if the text is also
  emitted** (round 3 [P2]). Its two production values are hard-coded literals.
- **B′ — the row's own literal phrasing, an author-written *"free-text description"*.** This names
  something the product **does not have**, and is recommended against on the separate ground that it
  requires **first minting an authoring surface** (a text field on `HITLPlacement`,
  `hitl_placement.py:176`) before any carrier question arises. `escalation_reason` is a *system*
  reason and is not a substitute for it.

**The `close_out` must be amended, not executed** — and the amendment must keep B and B′ distinct, or
a later impl leg will price one and build the other.

**§6.1 Stated against interest.** `[HIGH]` C leaves a real thinness in place: the variant an operator
must key is the one with the least context, and the `harness-inspect` surface cannot help (Runtime
§13.7 term 4, `:1301`, forbids it to deserialize a snapshot at all). If a second operator-facing
consumer of pause state lands, C's cost compounds where A-1's would already be paid. **And the
correlation reframe that carries point 1 rests on an unstated premise the committed persona arc will
eventually break** — that the resumer received the webhook. That is true for `solo-developer` and
false for `team-binding` / `multi-tenant-compliance` (root `CLAUDE.md` §10.2), which is why D-1(b)
exists as a trigger rather than being argued away. This filing does not claim the gap is imaginary —
only that **at HEAD it is a join rather than a missing string, it is additively closeable at any
time, and no demand signal accompanies it.**

---

## §7 Council position — **probe-resolved for C / A-1; CONVENE, dyadic, ONLY if the operator selects A-2 or B**

The row's `council` field is an unconditional *"yes if opened"* on a named **C10 ⊥ C11** tension
(`.harness/forward-register.yaml:3048`–`:3051`). Per CLAUDE.md §10.9 amendment 5, a probe was run
before taking a position, and per `[[probe-resolves-fork-prescribed-council]]` the row's prescription
is not binding on the probe's result.

**What the probe resolved.** `[HIGH]` Two facts, each from a direct read. **(1)** The only
author-independent "description" the product renders is a closed-vocabulary value —
`f"HITL gate at {placement.position.value}"` (`hitl_gate_composer.py:2051`) — so C11's *"description
a human can act on"* and C10's *"closed vocabulary"* denote **the same value**, and there is no
preference gap between them to surface. **(2)** The richer free text that does exist
(`escalation_reason`) is **already delivered to the operator contractually**
(`webhook_brief_adapter.py:77`), so C11's ergonomics case does not need durable state to be served,
and C10's objection has nothing durable to object to. The `B-69` convening reached the adjacent form
of this — *"The seam closes not because I win but because the same empirical fact defeats both
proposals"* (council `:238`) — and this probe extends it from *"neither is buildable"* to *"the
buildable one is what both voices want, and the contested one is already delivered elsewhere."*

**What the probe did NOT resolve, and why the convening is registered rather than declined.** `[MODERATE]`
The tension **is** live inside the hop-6 branch (§3(iii)): once the channel is open, C10's objection
to an unbounded `str` in durable state and C11's want of the richest available reason genuinely
diverge, and OD §30.5.1 limit 1 (`:71`) plus §30.5.4 (`:104`) give C7/C8 a stake. So:

- **If the operator selects C or A-1 → NO convening owed.** The disposition is probe-resolved.
- **If the operator selects A-2 or B → a dyadic C10 ⊥ C11 convening is OWED before the spec leg**, and
  it is not decorative: the payload-type question is exactly what it would adjudicate, with the
  redaction posture as the concrete stake. Consider adding C7 as consultant if B.
- **Under C, the convening is additionally owed at D-0 or D-1** — D-0 because it makes the pause
  class real and so gives the tension a live surface, D-1 because it is precisely the condition under
  which free text the operator does *not* already hold starts to exist and the two positions
  separate.

This is a **reversal of the row's unconditional "yes"**, made on a probe rather than a preference,
and recorded as a reversal.

---

## §8 The ratification ask — ONE decision, four options

**PRIMARY.**

> **Does `B-98` resolve as C (DEFER: amend the `close_out` with §3's grounding, retire Reading B as
> written, and record the FOUR-disjunct demand test **D-0 / D-1 / D-2 / D-3** — D-0, the FM-2
> webhook-config arc making the pause class production-reachable at all, being the dominant one — so
> the row reopens on evidence rather than on judgement) — or as A-1 (carry the DECLARED, ADD-folded
> `HITLPlacementKind` tuple, captured driver-side from the value already computed and discarded at
> `workflow_driver.py:2772`, on `PauseSnapshot` + `PreDispatchGateOwningBranchResumeState`,
> drop-when-`None`, NO new cross-axis channel) — or as A-2 (the FIRING placement position, threaded
> across the `workflow_driver.py:5375` drop point, accepting the carrier-home commitment, and buying
> information no conforming webhook consumer can obtain today) — or as B (the brief's free-text
> `escalation_reason`, accepting the same channel PLUS a size bound PLUS an OD §30.5.1 rationale
> re-grounding — which becomes a mandatory §30.5.4 amendment only if the text is ALSO emitted)?**

**Recommended: C.** **Runner-up: A-1.** **Recommended against: B as written.**

**Carried by any answer, requiring no separate decision:**

- **The full demand test — D-0, D-1, D-2 AND D-3 — is recorded on the row**, with D-0 marked
  dominant. *(Called out at round 4 [P2]: an earlier draft of this bullet and of §9 listed only
  D-1/D-2/D-3, so landing the FM-2 webhook-config arc could have failed to reopen the row it is the
  sharpest trigger for.)*
- The `close_out` is **amended** to record (a) that the durable `HITL_PENDING` pause class is **not
  production-reachable in stock bootstrap** at HEAD, so the row describes a dormant class; (b) that
  the description **already reaches the operator contractually** via the webhook, delivery being a
  code-order precondition of the pause — so the durable gap for the TEXT is CORRELATION, narrowing
  (not abolishing) the row's own `B-71`-distinctness claim; (c) that the PLACEMENT is by contrast
  **not** contractually available, because `compose_hitl_action_id`'s shape is explicitly
  discretionary — so a typed placement field is net-new; (d) that **B and B′ are DISTINCT and must stay distinct in the row**: B carries the already-existing `exc.brief.escalation_reason` and needs **no** authoring surface, while B′ — the row's literal *"free-text description"* — needs one minted first, because no author-written description exists and a system reason is not a substitute; (e) the A-1 / A-2 split and that the undecided question
  is the **channel**, not the field; (f) that the carrier answer is **two** sites — top-level plus a
  per-row sibling, the split forced by cardinality (several pre-dispatch rows per snapshot), not by
  taste; (g) that the hash disposition is fully pre-decided by the five-instance drop-when-`None`
  precedent; and (h) that **additivity removes the "decide now" pressure** — the `B-99` exclusion
  asymmetry does not transfer to an inclusion.
- The `council` field flips from unconditional *"yes if opened"* to the §7 **conditional** form.
- The Class 3 cite-hygiene item at `Spec_Control_Plane_v1_99.md:40` (*"v1.94's `synthesis_step_id`"*,
  falsified — first occurrence v1.58) is recorded on the row's cross-ref, **not** patched here (a
  design-substrate edit does not ride a doc-only filing).

---

## §9 Sequencing, and what each leg owes

**Chain: this filing → ratification (+ the §7 dyadic **only** under A-2/B) → spec leg (A-1/A-2/B only) → impl leg.**

| Leg | Owed under **C** | Owed under **A-1** | Owed under **A-2 / B** |
|---|---|---|---|
| **Ratification** | operator answer; row `pr:` pointer; `close_out` amended per §8; `council` field flipped; `status` stays `registered_finding` | operator answer; `pr:`; `status: open` | operator answer; **the §7 dyadic C10 ⊥ C11 convening, resolving the payload-type question** (+ C7 if B); then `status: open` |
| **Spec leg** | **none owed** — no design extension | CP §26.2 carrier amendment (two fields, drop-when-`None`, byte-compat argued per the v1.99 template) + Runtime §14.14.9.2 exclusion row **narrowed** (free text stays excluded) + the projection field | as A-1, **plus** a carrier-home ruling for the hop-6 payload (CP-side declared shape vs `harness-core` re-homing); **B additionally**: a size bound as a contract term, and OD §30.5.1's disclosure-limit **rationale re-grounded** (it is written as derived from the projection's exclusions) — **an OD §30.5.4 amendment is owed ONLY IF the text is also EMITTED**; a durable/API-only field leaves *"nothing redactable is emitted"* true (round 3 [P2]) |
| **Impl leg** | none | `_captured_hitl_gate_config_hash` returns the declared positions; `capture_pause_snapshot` + `_compute_snapshot_hash` conditional block mirroring `:835`–`:839`; nested drop mirroring `:670`–`:671`; projection field; **byte-compat witness by mutation-probe** (an old snapshot re-hashes identically; revert the drop → assert it fails) | **the SHARED carrier + hash + projection mechanics of A-1, with the PAYLOAD SOURCE REPLACED — NOT A-1's field in addition to the selected one** *(corrected at round 5 [P1]: the earlier "as A-1 plus" wording would have landed both)*. Payload comes from the signal, so `_captured_hitl_gate_config_hash` is **not** extended. **Plus** the signal-payload surface threaded at **every** `HITLPauseRequestedSignal` catch that records a durable disposition (§3(ii)'s by-rule inventory — sequential `:5375`; fan-out `:9614` / `:14247` / `:9843`–`:9861` / `:14000`–`:14008`; **EVALUATOR_OPTIMIZER `:10963`→`:10965`, capture at `:11192`; DECENTRALIZED_HANDOFF `:15599`, capture at `:15628`** — added at round 6 [P2]), **plus** a witness that CP's read does not import `harness-runtime` |
| **Row disposition** | stays `registered_finding` with a **falsifiable** trigger; re-check on **D-0** (dominant) / D-1 / D-2 / D-3 | closes at the impl leg | closes at the impl leg |

**Not owed by any leg, explicitly:** re-opening `B-69`'s ratified projection scope; any change to
`B-71`'s correlation-id surface (three falsified premises are on that row — a fourth mechanism claim
is the stop condition); pre-empting `B-99`'s trigger; minting a new closed enum over
`escalation_reason` — which retypes a shipped C-CP-28 field and is its own decision if ever wanted.
**It is NOT information-identical to A-2** *(corrected at round 6 [P2]; an earlier draft said it was)*:
such an enum would encode the escalation **ROUTE** (`durable_async_cell_synchrony` vs the timeout
path), whereas A-2 encodes the **firing PLACEMENT** — and either route can arise at either placement,
so the two are orthogonal. The exclusion here is on scope grounds only, and must not be read as
foreclosing a type-safe variant of B from later design consideration.

**Priority note, carried to the ratification rather than decided here.** `[MODERATE]` If the operator
wants the operator-loop win, §3(i) says **`B-71` dominates `B-98`**: the description already reaches
the operator, and what is missing is the join `B-71` owns. `B-71` is itself genuinely open (its
council flipped from *"TBD, likely narrow"* to open after a fifth-round premise falsification, and it
needs co-design with `B-72` property 6's pre-dispatch identity mechanism). **This filing does not
recommend re-opening `B-71` — it records that the two rows are ordered, which the register does not
currently say.**

---

## §10 Cite re-verification at HEAD `987f330b`, and review record

**Code cites — all re-resolved by direct read at this HEAD.**
`harness-cp/src/harness_cp/pause_resume_protocol_types.py`: `:49` `WorkflowPauseReason` (6 members,
`:60`/`:63`/`:66`/`:69`/`:72`/`:76`) ✓ · `:112`/`:119` the two `question` prose hits ✓ · `:208`
`PreDispatchGateOwningBranchResumeState` (5 fields; `:265` `hitl_gate_config_hash`) ✓ · `:745`
`PauseSnapshot` ✓ · `:757` `extra="forbid"` ✓ · `:786` `hitl_gate_config_hash` ✓ · `:791`–`:793` the
three-sequential-site scope ✓ · `:795`–`:804` the top-level-scalar rationale ✓ · `:806`–`:810` the
drop-when-`None` note ✓ · `:893` `PausedChildBranchResumeState` (4 fields: `:913`/`:918`/`:924`/`:934`) ✓.
`harness-cp/src/harness_cp/pause_resume_protocol.py`: `:411` `capture_pause_snapshot` ✓ · `:599`
`_strip_default_fanout_resume_fields` ✓ · `:670`–`:671` the nested `hitl_gate_config_hash` drop ✓ ·
`:726`–`:841` `_compute_snapshot_hash` (base dict `:754`–`:759`; seven conditional keys; `:835`–`:839`
the bare-scalar block; digest `:840`–`:841`) ✓ · `:753` the `[[new-surface-audit-hash-and-config-not-carrier]]`
cite ✓.
`harness-cp/src/harness_cp/workflow_driver.py`: `:2712`–`:2735` `_hash_hitl_gate_config` ✓ · `:2738`–`:2775`
`_captured_hitl_gate_config_hash` (`applicable_placements` materialised at `:2772`) ✓ · `:5368` the
"cannot import from harness-runtime" comment ✓ · `:5375` the class-name catch ✓ · `:5378`–`:5393` the
capture call ✓ · `:5383` `pause_reason=HITL_PENDING` ✓ (siblings `:11192`, `:15628`).
`harness-cp/src/harness_cp/hitl_placement.py`: `:55` `HITLPlacementKind` ✓ · `:58`–`:59` the D5 closure
note ✓ · `:63`/`:66`/`:69` the three members ✓ · `:109` `HITLPlacementTrigger.placement_kind` ✓ ·
`:176`/`:186` `HITLPlacement.position` ✓.
`harness-cp/src/harness_cp/validator_framework_types.py`: `:134` `HITLEscalationBrief` (6 fields,
`:146`–`:151`; `:150` `escalation_reason: str`) ✓.
`harness-cp/src/harness_cp/pause_state_projection.py`: `:151` `_LocationBase` (`:161`/`:164`) ✓ ·
`:168`–`:183` `HitlAddressableLocation` (rationale `:170`–`:172`) ✓ · `:386`–`:400` the closed union ✓ ·
`:403`–`:433` `PausedWorkflowState` (4 fields) ✓ · `:555` `walk_pause_tree` ✓ · `:579` `_ChildPosition` ✓ ·
`:590` `_walk` (`:639` the HITL gate, `:640` the leaf entry, `:650`–`:665` pre-dispatch, `:681`–`:689`
the child recursion) ✓ · `:693` `_gate_owning_leaf_entry` ✓ · `:816` `project_pause_locations` ✓.
`harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py`: `:381` `HITLPauseRequestedSignal` ✓ ·
`:424`–`:436` `compose_hitl_action_id` ✓ · `:845` `applicable_placements` ✓ · `:1255` `_escalate_to_secondary_channel` ✓ ·
`:1289`–`:1296` the brief ✓ · `:1298` the idempotency key ✓ · `:1324`–`:1335` deliver + flag + raise ✓ ·
`:1778` the `VALIDATOR_ESCALATION` filter ✓ · `:1786` the per-placement loop ✓ · **`:2013` the
`DURABLE_ASYNC` branch, `:2020` the `NoReturn` note, `:2021`–`:2028` the escalate call, `:2029` the
"fall through to sync-blocking" comment ✓ (round-1 [P1])** · `:2026`/`:2158` the two
`escalation_reason` literals ✓ · `:2048`–`:2054` the `ask(...)` call, `:2051` the prompt f-string ✓.
**`harness-runtime/src/harness_runtime/lifecycle/webhook_brief_adapter.py:76`–`:84` the payload body,
`:86` `approval_id`, `:87` `idempotency_key` ✓ (round-1 [P1]).**
**Reachability chain (round-3 [P1]):
`harness-runtime/src/harness_runtime/bootstrap/factories/webhook_delivery_composer_factory.py:17`–`:22`
the FM-2 empty-marker deferral, `:104`–`:110` the opt-out `None` return, `:123`–`:143` the
no-`webhook_config` construction ✓ ·
`harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:138` the defaulted ctor
param, `:493` `deliver_webhook_for_brief`, `:538`–`:542` the `RuntimeError` ✓ ·
`harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:516` the stage-5 binding ✓ ·
`hitl_gate_composer.py:1298` the placement-bearing key, `:1303`–`:1304` the composer assert,
`:1324` the delivery, `:1329` the flag, `:1332` the signal ✓.**
`harness-runtime/src/harness_runtime/lifecycle/escalation_prompt.py:18` + `:41`–`:47` ✓ ·
`harness-runtime/src/harness_runtime/api.py:925` `read_paused_workflow_state` ✓ ·
`harness-runtime/src/harness_runtime/lifecycle/durable_pause_resume_protocol.py:124` the journal write ✓.

**Spec cites — all re-resolved at this HEAD.** `Spec_Harness_Runtime_v1.md:1` head **v1.109** ✓ (matches
root `CLAUDE.md` §2.3 — probed for pointer drift per `[[wrong-version-read-delta-only-baseline]]`, **none
found**) · `:73` change-note finding (ii) ✓ · `:1288` §13.7 heading, `:1301` term 4 ✓ · `:3476` §14.14.9.2
heading ✓ · `:3528` the `summary_text` exclusion row ✓ · `:3533` the **gate description** exclusion row,
byte-verified ✓. `Spec_Control_Plane_v1_112.md:54` §0.6 ✓ · `:147`–`:151` §2.4 ✓.
`Spec_Control_Plane_v1_45.md:10`/`:36` ✓ · `v1_58.md:29` ✓ · `v1_65.md:31` ✓ · `v1_99.md:9`/`:24`/`:40` ✓.
`Spec_Operational_Discipline_v1_36.md:45` §C-OD-30.5 heading, `:71` disclosure limit 1, `:104` the
redaction posture ✓. `.harness/council-b69-pause-state-accessor-2026-07-30.md:232`–`:242` SEAM 3,
`:337` the position row, `:347` the `summary_text` re-argument, `:494` the routing row ✓.
`.harness/forward-register.yaml:3026`–`:3053` the row, `:3074`–`:3076` `B-99`'s precondition ✓.

**Counts, recounted programmatically at this filing** *(corrected at round 2 [P2])*. `placement`
substring hits in `pause_resume_protocol_types.py`, **case-sensitive lowercase: 16** → **13 genuine**
+ **3** inside *"replacement"*; of the 13, **12 docstring prose + 1 `TYPE_CHECKING` import path**
(`:46`). Case-**insensitive**: **17** → **14** (the extra is `HITLPlacementKind` in prose at `:225`).
Field declarations of that token **0** · `PauseSnapshot` fields **15** (AST) · `PausedChildBranchResumeState`
**4** · `PreDispatchGateOwningBranchResumeState` **5** · `HITLPlacementKind` members **3** · non-test
field declarations typed `HITLPlacementKind` **3**, durable **0** · `_compute_snapshot_hash` canonical
base keys **4**, conditional keys **7** · projection variants **4** / source shapes **10** / carriers
**7** · `PausedWorkflowState` fields **4** · CP spec versions containing `synthesis_step_id`
**{58, 59, 65, 68, 97, 99}** (v1.94 absent) · readings **4**, viable **4**, recommended **1**.

**Findings recorded, not absorbed.** (a) The `Spec_Control_Plane_v1_99.md:40` mis-attribution (§3(v)) —
Class 3, no disposition change, routed to the ratification leg's row edit. (b) `PauseSnapshot`'s
*"8-field"* class docstring against a 15-field type — **already** owned by the `B-69` impl arc per the
council record's Class 3 row (`:495`); noted here only to confirm it is unchanged at this HEAD, **not**
re-registered.

### §10.1 Out-of-family review — `just codex-review-uncommitted`

**Round 1 — two findings, both UPHELD by direct verification, and the first changed the filing's
central ground.**

- **[P1] "Ground the fork on the durable-async operator payload" — UPHELD IN FULL, and it FALSIFIED
  this filing's §3(i) as first drafted.** The draft asserted that the only operator-facing question
  text is the sync prompt at `hitl_gate_composer.py:2051`, and built both the recommendation and
  A-2's "information-complete" claim on it. Direct read confirms the `DURABLE_ASYNC` branch at
  `:2013` calls `_escalate_to_secondary_channel` at `:2021`–`:2028`, which **always raises**
  (`NoReturn`, `:2020`), so **route 1 never reaches `:2050`** — `:2029`'s *"Fall through to step 4f
  sync-blocking"* applies only to the other branch. The operator's real surface is the webhook
  payload (`webhook_brief_adapter.py:76`–`:89`), which carries `escalation_reason`, `parent_step_id`,
  `fail_class`, `fail_detail_hash`, the palette, and an `idempotency_key` embedding
  `placement.position.value`. **Absorbed as a rewrite of §3(i)** (the two-route split; the
  description-already-reaches-the-operator finding; the CORRELATION-not-description reframe and its
  narrowing of the row's `B-71`-distinctness claim), propagated to §1, §2 (two new table rows), §4
  (A-2's completeness claim corrected; B re-priced as duplicating rather than supplying), §5, §6
  point 1 + point 3 + §6.1, §8, §9's new priority note, and this §10. **This is the round's real
  yield: without it the recommendation stood on a false premise, and the runner-up was over-valued.**
  *Recommendation UNCHANGED (still C) — but its ground is now the join, not the absence.*
- **[P2] "Correct the claim that one top-level field covers all variants" — UPHELD.** The draft's §1
  bullet said one top-level `PauseSnapshot` field reaches every HITL-bearing variant while §3(iv)
  said two sites — a genuine internal contradiction, and §3(iv) is the correct half. Verified:
  `PreDispatchUniformFallbackOnlyLocation` is built **per row** from
  `resume_state.pre_dispatch_gate_owning_branches` (`pause_state_projection.py:650`–`:665`), and one
  parent snapshot may carry several rows with different placement data, so a top-level scalar is
  **structurally incapable** of representing that variant. Absorbed at §1 bullet 2, §3(iv) (heading
  + the two-consequence split, with the cardinality argument stated), and §5 row (2).

**Round 2 — three [P2], all UPHELD, all against the round-1 absorption's own edges.**

- **[P2] "Remove the false route-2 value distinction" — UPHELD.** §6 point 3 credited route 2 with a
  marginal gain ("one closed value") on the assumption the placement was webhook-visible only on
  route 1. False: **both** routes reach the durable pause through `_escalate_to_secondary_channel`,
  which composes `idempotency_key = str(compose_hitl_action_id(parent_action_id, placement.position))`
  at `hitl_gate_composer.py:1298` and ships it as `WebhookPayload.idempotency_key`
  (`webhook_brief_adapter.py:87`). Absorbed at §6 point 3 and §4 Reading A-2 — a durable placement
  field adds **nothing over the webhook on either route**. *This strengthens the recommendation
  rather than weakening it.*
- **[P2] "Keep webhook-carried reasons out of D-1" — UPHELD, and it was a genuine trigger defect.**
  D-1(a) fired on `escalation_reason` going non-literal, but that value is projected into every
  webhook (`webhook_brief_adapter.py:77`), so the condition would have re-opened `B-98` in a scenario
  where the operator still holds the description — contradicting D-1's own premise and the filing's
  central duplication argument. Absorbed as a restructured D-1 keyed on **"not projected into
  `WebhookPayload.payload_body`"**, with the `escalation_reason` case explicitly named as a
  non-trigger absent (b).
- **[P2] "Recompute the placement-occurrence evidence" — UPHELD.** The first pass matched
  case-insensitively and reported 17/14. Case-sensitive lowercase is **16/13**; and `:46` is a
  `TYPE_CHECKING` import path, not docstring prose. Absorbed in the grounding header and the §10
  counts, with both figures and the prose-vs-import split stated. **The zero-field-declaration
  conclusion — the load-bearing half — is unaffected**, as the finding itself notes.

**Round 3 — one [P1] + one [P2], both UPHELD, and the [P1] is the strongest finding of the review.**

- **[P1] "Classify the webhook routes as unreachable in stock bootstrap" — UPHELD, verified
  end-to-end.** The four-step chain is byte-verified at §3(i): default config yields a `None`
  composer (`webhook_delivery_composer_factory.py:104`–`:110`), so `joint_binding_present`
  (`hitl_gate_composer.py:2009`–`:2012`) is False; on opt-in the factory constructs the composer with
  **no `webhook_config`** (`:123`–`:143`, the FM-2 deferral at `:17`–`:22`), so
  `deliver_webhook_for_brief` raises `RuntimeError`
  (`webhook_delivery_composer.py:538`–`:542`) at `hitl_gate_composer.py:1324` — **before** the pause
  flag (`:1329`) and the signal (`:1332`). Since that signal is the sole source of the three
  `HITL_PENDING` captures, **no durable `HITL_PENDING` pause is production-reachable at HEAD.**
  Absorbed at §3(i) as a new sub-finding **plus** the code-order-precondition observation it implies
  (delivery *precedes* the pause, so the webhook is guaranteed wherever the pause exists), and
  promoted into the demand test as **D-0**, which now dominates D-1/D-2/D-3. **It strengthens the
  recommendation and dates the row rather than invalidating it.**
- **[P2] "Do not force an OD amendment for an API-only field" — UPHELD as a SCOPE correction.**
  Reading B's cost #2 called an OD re-adjudication unconditionally FORCED. §30.5.1's disclosure
  limits govern the **emission** (per-variant counts only, `:64`), not the projection, so a
  caller-facing description with telemetry unchanged leaves §30.5.4's *"nothing redactable is
  emitted"* literally true. Absorbed as *"OWED as a check; mandatory only if the text is also
  emitted"*, with the residual — limit 1's rationale is written as derived from the projection's own
  exclusions — stated rather than dropped. **Reading B's cascade is smaller than the draft claimed;
  the recommendation against B rests on §3(i)'s duplication argument, not on this cost.**

**Round 4 — one [P1] + two [P2], all UPHELD; the [P1] REVERSES a round-2 over-correction.**

- **[P1] "Don't treat opaque idempotency keys as placement fields" — UPHELD, and it reverses round
  2's [P2] absorption.** Round 2 concluded a durable placement field was redundant because the
  webhook's `idempotency_key` already renders as `hitl:{action_id}:{placement}`. **That read a
  mechanism as a contract.** `compose_hitl_action_id`'s own docstring says *"**Suggested** shape …
  deferred to implementation discretion at v1.11 per spec §14.8 deferred-list"*
  (`hitl_gate_composer.py:430`–`:431`), so no conforming consumer may parse it — the very
  CONTRACT-not-mechanism distinction the `B-69` record makes at its §6.3. Absorbed as a **finer
  partition** at §3(i): the **reason text** is contractual payload (`webhook_brief_adapter.py:77`) and
  a durable copy duplicates it; the **placement** is not, so **A-2's gain is real and net-new**.
  Propagated to §4 (A-2's "Buys"), §6 (point 2 narrowed to the TEXT; **new point 4 concedes A-2's
  gain against this recommendation's interest**), the runner-up paragraph (A-1 preferred on **cost**,
  not information), and §8's option text. **Recommendation UNCHANGED** — it now rests on point 1
  (the pause class is dormant) rather than on a redundancy claim that was half wrong.
- **[P2] "Carry D-0 into the ratification trigger" — UPHELD, a real defect in the instruction.**
  §8's carried-by-any-answer bullet and §9's row-disposition cell still listed only D-1/D-2/D-3 after
  D-0 was added at round 3, so ratifying C could have written a register trigger that **omits the
  dominant one** — landing FM-2 would not have reopened the row. Absorbed at both sites, with D-0
  marked dominant, plus a dedicated §8 bullet.
- **[P2] "Keep B's OD work conditional on emission" — UPHELD.** §8 and §9 still called the OD
  §30.5.4 amendment "forced" after round 3 had made it conditional in §4 — an internal contradiction
  that would have over-priced B in the operator's decision. Absorbed at both.

**Round 5 — two [P1] + one [P2] + one [P1], all UPHELD; all four are PRECISION defects in this
document rather than challenges to its disposition, and two raise A-2/B's price.**

- **[P1] "Account for every signal-drop site" — UPHELD, and it under-priced A-2/B.** The `:5375`
  catch is only the sequential one; the fan-out paths catch the same signal and keep **only the
  branch ordinal** (`workflow_driver.py:9614`, `:14247`, siblings at `:9843`–`:9861` and
  `:14000`–`:14008`) — and each feeds a `PreDispatchGateOwningBranchResumeState` row. Absorbed at
  §3(ii) as a **family, not a site**, capped **by rule** rather than by list so an unlisted catch
  cannot escape the obligation, and propagated to §9's impl-leg cell. **This strengthens the
  recommendation**: A-2/B's channel is four-plus sites wide. Also surfaced a lead against A-2 —
  both verified catches record the firing gate as `SUB_AGENT_BOUNDARY`, so the per-row payload may be
  a constant; recorded as a lead for the impl leg to confirm, not as a finding.
- **[P2] "Distinguish declared placements from applicable ones" — UPHELD.** The tuple at `:2772` is
  the ADD-folded **declared** configuration, captured before the composer's instance filter (`:1767`),
  `VALIDATOR_ESCALATION` removal (`:1778`) and `removed_placements` (`:1937`–`:1986`) — so A-1 can
  report a position that could not have fired. Absorbed by **renaming the reading** and stating the
  semantics and the gap explicitly, with the honest note that sourcing the *effective* set collapses
  A-1 into A-2's channel cost.
- **[P1] "Remove the nonexistent authoring cost from Reading B" — UPHELD.** §6 charged B with minting
  an authoring surface, but B as defined at §4 sources the already-existing `escalation_reason`.
  Absorbed by **splitting B from B′** (the row's literal author-written phrasing) and recommending
  against each on its own ground — so a later impl leg cannot price one and build the other.
- **[P1] "Do not implement A-1's payload under A-2 or B" — UPHELD.** §9's *"as A-1 plus"* would have
  landed A-1's field **in addition to** the ratified payload. Absorbed as *"shared carrier + hash +
  projection mechanics, payload source REPLACED"*.

**Round 6 — three [P2], ZERO against the disposition; all three were defects in CARRIED INSTRUCTIONS
and are fixed, and the exit declared after round 5 is HELD rather than reopened.**

- **[P2] "Include EO and handoff signal catches" — UPHELD.** §9's impl-leg inventory listed the
  sequential and fan-out catches but omitted **EVALUATOR_OPTIMIZER** (`workflow_driver.py:10963` →
  `:10965`, capture at `:11192`) and **DECENTRALIZED_HANDOFF** (`:15599`, capture at `:15628`) —
  precisely the two remaining `HITL_PENDING` capture sites §2 already names. An impl leg following
  the list would have populated the field for linear and fan-out pauses and silently skipped these.
  **This is the exact failure the §3(ii) by-rule cap exists to prevent, arriving in the one place the
  rule had been re-expanded into a list** — fixed by extending the inventory *and* keeping the rule
  as the binding form.
- **[P2] "Keep Reading B separate from B-prime" — UPHELD.** §8's carried close_out bullet still said
  *"Reading B as phrased needs an authoring surface"* after §6 had split B from B′ — and §8 is the
  text copied into the register, so the conflation would have survived exactly where it does the most
  damage. Fixed at the bullet.
- **[P2] "Treat escalation reason as distinct from placement" — UPHELD.** §9's not-owed list called a
  closed enum over `escalation_reason` *"information-identical to A-2"*. It is not: that enum encodes
  the escalation **route**, A-2 the firing **placement**, and either route can arise at either
  placement. Fixed, with the exclusion re-grounded on scope alone so it does not foreclose a
  type-safe B variant from later design.

**SOUNDNESS EXIT — declared after round 5, CONFIRMED at round 6, on SOUNDNESS rather than on
reviewer quiet.**
`[[deferred-mechanism-spec-leg-exit-on-soundness]]` is the governing discipline: a filing whose
disposition is a **deferral** exits when the disposition is sound and honestly priced, **not** when
the reviewer runs out of prose to sharpen. **Seventeen findings across six rounds**, every one
empirical, every one verified by direct read *before* absorption, every one absorbed as substance.
**The discriminator is met: rounds 4, 5 and 6 produced ZERO findings against the disposition** —
every one was a precision defect in how the options were described or instructed, and each absorption
made C *stronger*, never weaker. Round 6 in particular returned only [P2]s, none touching the
recommendation. Continuing would be the `[[non-convergent-adversarial-hardening-arms-race]]` pattern
this workspace stops on (its Q5 test — *does the finding invalidate the carrier's premise?* — has
answered NO for three consecutive rounds). **This filing is CLOSED to further mechanism rounds**; the
remaining open items are ratification decisions.

**Enumeration cap, stated as a binding rule** (the same discipline that closes §3(ii)): the four
signal-drop sites and the three composer narrowings listed above are this filing's
**verified-at-HEAD inventory, not a closed set**. Any surface of the same kind that this filing did
not list is bound **by the rule**, not excused by its absence from the list — the spec/impl leg
inventories rather than inherits.

**On the flip cap, stated honestly and against interest.** §3(i)'s ground moved across four rounds:
sync-prompt-is-the-surface → webhook-is-the-surface → webhook-on-both-routes → **plus** the pause
class is opt-in-unreachable → **and the key is a mechanism, not a contract**. Three of those moves are
monotone refinement in one direction; **the fourth (round 4 [P1]) is a genuine REVERSAL of a round-2
conclusion**, and it is recorded as such rather than presented as further refinement. That places this
filing **at the 3-flip cap on that element**, which is why the exit is declared here:
`[[reviewer-oscillation-register-and-hold]]`'s discipline says a further move on the same element
would call for **register-and-hold**, not a fifth patch. Two things bound the risk: the reversal
landed on a **strictly finer partition** (text vs placement) rather than re-adopting an abandoned
position, and **the recommendation (C) and runner-up (A-1) did not move at any round** — only the
arguments beneath them, which is the shape of a filing being ground rather than one oscillating.
**Round 5 did not move this element at all** — its four findings landed on option *descriptions* and
on A-2/B's *price*, which is the convergence signal the exit rests on.

---

## §11 RATIFICATION

**Status: RATIFIED 2026-08-01 as READING C — DEFER. The ratification leg is this filing's ONLY
remaining leg: §9's `C` column owes NO spec text and NO impl text, so there is no spec leg and no
impl leg to follow.**

The `B-92` / `B-97`(a) precedent is followed: the outcome is recorded here verbatim-in-substance
rather than only at the register row, so the decision travels with the filing a later session
actually reads.

### §11.1 The gate — the reading (operator `AskUserQuestion`, 2026-08-01)

> **Operator selected: READING C — DEFER, with the four-disjunct falsifiable demand test recorded so
> the row reopens on evidence rather than on judgement.**
>
> Ratified with **D-0 DOMINANT** — *the HITL-pause class going production-reachable* (the FM-2
> webhook-config arc landing, so that a durable `HITL_PENDING` pause can occur outside tests at all).
> **D-1, D-2 and D-3 are ratified in the forms §4 states them**, D-1 in its round-2 tightened
> two-disjunct form ((a) a description surface that the webhook does **not** already project, or
> (b) the resumer ceasing to be the webhook recipient).
>
> **NO CARRIER CHANGE.** No field is added to `PauseSnapshot`, to
> `PreDispatchGateOwningBranchResumeState`, or to any other durable pause carrier; the hash
> disposition question is not reached; and the read-side projection is untouched.

**Runner-up A-1 was NOT selected and is NOT partially adopted.** A deferral that quietly landed
"just the cheap half" of A-1 would be the silent-absorption failure mode this filing exists to avoid.

### §11.2 What the ratification carries, per §8's "carried by any answer" list

| §8 obligation | Disposition at this leg |
|---|---|
| The **full** demand test — D-0, D-1, D-2 **and** D-3 — recorded on the row, D-0 marked dominant | **APPLIED.** All four are on the row's `close_out`, D-0 first and named dominant, D-1 in its round-2 tightened form. *(§8's own round-4 note is honoured: an earlier draft listed only D-1/D-2/D-3, so landing FM-2 could have failed to reopen the row it is sharpest for.)* |
| `close_out` **amended** with §3's grounding, items (a) – (h) | **APPLIED** — the dormancy of the class, the webhook's contractual delivery of the TEXT (narrowing, not abolishing, the `B-71`-distinctness claim), the PLACEMENT being net-new by contrast, the **B / B′ distinction preserved**, the A-1 / A-2 split with the channel named as the undecided question, the two-carrier answer forced by cardinality, the pre-decided drop-when-`None` hash disposition, and additivity removing the decide-now pressure |
| `council` field flipped from unconditional *"yes if opened"* to §7's **conditional** form | **APPLIED, in §7's FULL three-clause form** — (i) under the selected C, **none is owed now**; (ii) a C10 ⊥ C11 dyadic is owed **before the spec leg** if **A-2 or B** is later opened (C7 added as consultant under B); **and (iii) UNDER C, the convening is ADDITIONALLY OWED AT D-0 OR D-1** — D-0 because it makes the pause class real and so gives the tension a live surface, D-1 because it is precisely the condition under which free text the operator does *not* already hold starts to exist and the two positions separate. *(Clause (iii) was omitted from this addendum's first draft and from the register row; caught at out-of-family review round 1 [P2] — an omission that would have let a D-0 or D-1 reopening skip a convening §7 requires.)* **A-1 needs none** |
| The Class 3 cite-hygiene item at `Spec_Control_Plane_v1_99.md:40` recorded on the row's cross-ref, **NOT patched here** | **APPLIED as recorded, NOT patched.** A design-substrate edit does not ride a doc-only ratification; the CP spec is untouched by this leg |
| `status` stays `registered_finding`; row `pr:` pointer | **APPLIED** — `pr: '#1180 + #pending'` (the filing, then this ratification leg) |

### §11.3 What this leg does NOT do — stated so each absence is a decision

**No design-substrate edit is owed or made for `B-98`.** §9's `C` column says *"none owed — no design
extension"*, and that is discharged by making none: CP spec §26.2 is untouched, Runtime §14.14.9.2's
exclusion row is untouched, and no plan unit is opened, amended, or cited. **No plan cite anywhere
contradicts this deferral** — `B-98` is cited at no implementation plan and at no acceptance
criterion, so there is no plan-side obligation left dangling by not building it. *(The Runtime spec
delta that DOES ride this PR belongs to `B-104`, a different row and a different ratified reading;
the two share a PR, not a scope.)*

**The §8 priority note is carried forward, not acted on.** `B-71` dominates `B-98` for the
operator-loop win — the description already reaches the operator, and what is missing is the join
`B-71` owns. This ratification does **not** re-open `B-71`; it records that the two rows are ordered,
which the register now says.
