# Spec: Control Plane — v1.120 (delta over v1.119)

*Delta-only file. v1.119 and every earlier C-CP-01 … C-CP-29 body are preserved verbatim
except at **three** amendment sites, all additive and byte-identical when the new input is
empty: (1) C-CP-17 §17.3 — `PRE_ACTION` inheritance, first-match selection and exact-name
`tool_filter` semantics; (2) C-CP-25 — one new `execute_workflow` input,
`inherited_hitl_placements`, and how the per-step placement set is composed from it; (3)
C-CP-26 property 7 (v1.110/v1.111 §1) — the captured gate-config hash covers the inherited
prefix. No new contract number is minted. A Runtime-side delta is owed and is NOT zero
(§0.7); this delta does not specify or claim it.*

**Filed:** 2026-09-24
**Authority:** operator decision "Yes, inherit matching placements" (2026-09-24), recorded
in `evaluation/production-readiness-arch/profile-contract-decision-1.md` §"Parent
PRE_ACTION placement inheritance decision"; independent Opus design
`evidence-parent-preaction-inheritance-design-opus-1/review.txt` (blueprint accepted in LIT
`arhugula-harness-trial-193` `cmt-64772dd8-97ad-4049-afda-db7692cfe6e9`).
**Predecessor:** `Spec_Control_Plane_v1_119.md`

## §0 Change-note (v1.119 → v1.120)

### §0.1 The gap

A sub-agent child runs under its own manifest's `hitl_placements` alone. A parent that
declared a `PRE_ACTION` placement therefore stops governing the moment work is delegated:
a child with no placements, or a narrower one, acts unattended on exactly the actions the
parent required a human for. The operator ratified that the child must carry its parent's
matching `PRE_ACTION` placements, transitively, without letting a child declaration remove
or narrow them.

Two prerequisites the ratified answer does not itself settle, both settled here:

- `HITLPlacement.tool_filter` matching semantics were "deferred to implementation
  discretion" (C-CP-17 §17.3) and no source reads the field, so "preserve the parent's tool
  filter" had no meaning to preserve.
- Two same-position placements at one root manifest are already admitted by §17.3 ("Multiple
  placements per workflow are admitted") with no rule for which governs an action.

### §0.2 §17.3 (AMENDED) — placement semantics

**(a) Inheritance.** A sub-agent child's applicable placement set is composed
**ancestor-first**: the placements inherited from its ancestors (outermost ancestor first,
then the nearer parent), then the child's own workflow declarations, then the ADD-only
per-step fold (C-CP-06 §6.2). Only `pre-action` placements are inherited; `sub-agent-boundary`
and `validator-escalation` placements belong to the declaring workflow and are never
carried down. Inheritance is transitive: a parent's inherited set is part of what it
passes on, so a grandchild carries both ancestors' placements in that order.

**(b) The parent's policy is preserved.** An inherited placement keeps its `tool_filter`,
`cascade_policy` and `timeout` unchanged. The child's own placements are retained for actions
no ancestor placement covers. A per-step `pre-action` override at a child step that already
has an inherited `pre-action` placement is the existing same-position no-op (§6.2:
the workflow placement wins); it cannot add a second gate or replace the inherited one.
`removed_placements` cannot remove `pre-action` (it is not a loosenable kind).

**(c) First-match governs.** For one action, the governing placement is the FIRST
`pre-action` placement, in the composed order of (a), whose `tool_filter` matches; there is
at most one, and a consumer evaluates the gate once for it. An inherited placement therefore
always outranks a child's for any action it covers; a narrower or duplicate child
declaration can neither suppress it nor add a second prompt. The rule is
`harness_cp.hitl_placement.select_governing_pre_action_placement`; a consumer MUST use it or
an exact equivalent rather than re-derive matching.

**(d) `tool_filter` matching is exact-name.** `None` matches every action. A non-`None`
filter matches a tool action only when that action's exact tool name is an element of the
filter, and never matches an inference (non-tool) action — the filter "limits which tools
trigger the gate". The filter is not a glob and not a regular expression.

**(e) Patterns are refused at construction.** A `tool_filter` entry that is empty or contains
any of `* ? [ ] { } ( ) | \ ^ $ + !`, and an empty filter tuple (which would silently never
gate), raise a validation error when the `HITLPlacement` is built. Plain names such as
`fs.write`, `read_file`, `mcp__srv__tool`, `srv:tool` are admitted. **This is a
behavior change for an existing manifest that declares such a pattern: it now fails to
load rather than being accepted and matching nothing.**

### §0.3 C-CP-25 (AMENDED) — the `execute_workflow` input

`execute_workflow` gains ONE additive keyword input,
`inherited_hitl_placements: tuple[HITLPlacement, ...] = ()`. It is a plain immutable value
(not a durable field) and is threaded explicitly to every site that composes a step's
placement set or captures the gate-config hash — the linear inline loop and each of the
five non-linear strategies, including the post-join synthesis step. At each composing site
the placement set becomes `fold_step_hitl_placements(manifest_entry.hitl_placements,
binding.hitl_placement, inherited=inherited_hitl_placements)`, which prepends
`inherited` before the ADD-only fold. Any element that is not a `pre-action` placement
raises `ValueError` before any state change.

An empty `inherited_hitl_placements` (every root run, and every existing caller) leaves the
composed tuple identical to `manifest_entry.hitl_placements` and every captured hash
byte-identical.

### §0.4 C-CP-26 property 7 (AMENDED) — the inherited prefix is bound into the hash

The captured HITL gate-config hash (v1.110 §1.1(a); LINEAR `resume_at`,
`EVALUATOR_OPTIMIZER`, `DECENTRALIZED_HANDOFF` and the pre-dispatch gate-owning fan-out
branch) is computed over the composed set of §0.2(a), inherited prefix included. Order is
part of the identity: the same placements in a different ancestor order hash differently.
An empty prefix yields the pre-v1.120 bytes. Consequently a parent whose `pre-action`
placements change between a child's pause and its resume — including removal or narrowing —
changes the child's recomputed hash and the existing fail-closed material diff (v1.110 §1.1(b))
refuses the resume before any child dispatch. No new snapshot field is authorized: the
parent recomputes the prefix from its own current per-step context on re-entry.

A child paused BEFORE this delta under a parent that has a `pre-action` placement recorded a
hash without the prefix and will therefore fail closed on resume once a caller supplies the
prefix. That is intended and is not a regression.

### §0.5 What this delta does NOT claim

- **Not runtime enforcement.** This delta and its CP commit create the carrier, fold,
  selection function, validation and hash binding. No production caller supplies
  `inherited_hitl_placements` yet, and the gate composer does not yet call the selection
  function, so a real child gate still prompts as before. The one-prompt-per-action audit
  witness through a real `ChildWorkflowRunner` and `RuntimeHITLGateComposer` belongs to the
  Runtime slice.
- **Not depth-greater-than-zero direct resume.** A child `resume_handle` that bypasses its
  parent would not receive the prefix. Closing that is register row `B-104`'s
  depth-greater-than-zero refusal; nothing here implies it is covered.
- **Not the model-emitted tool loop.** Per-call gates inside an inference step's tool loop
  ignore placements today and are unaffected.
- **Not `placement.cascade_policy` semantics.** It is carried as data, still not read by the
  composer.

### §0.6 Visible behavior changes at root, stated

- **Pattern filters now fail to load** (§0.2(e)).
- **When the Runtime slice lands,** a root manifest with two `pre-action` placements will
  prompt once (first match) rather than once per placement, and a filtered `pre-action`
  placement will stop gating tools outside its filter and inference steps. Those are Runtime
  effects and are owed by the Runtime delta; they do not occur in the CP-only commit.

### §0.7 The Runtime-side delta, owed and named

`ChildWorkflowRunner` must accept and forward `inherited_hitl_placements`; the sub-agent
dispatch site must capture the parent's folded `pre-action` placements from its own step
context; and the gate composer's normal step and resume Step 0 must select the governing
placement with `select_governing_pre_action_placement`. Not amended here.

**Version-number note.** Register row `B-104` had reserved CP v1.120 for its own spec leg;
this delta was assigned the number v1.120 on the v1.119 head at the lead's direction and may
need renumbering when both land.

## §1 Preservation guarantees

| Element | Disposition |
|---|---|
| v1.119 body + all earlier CP spec bodies (C-CP-01 … C-CP-29) | Preserved verbatim |
| C-CP-17 §17.1 (three-placement closed enum) and `HITLPlacement`'s four fields | Preserved verbatim — no field added; only `tool_filter` gains construction-time validation |
| `fold_step_hitl_placements`'s ADD-only, workflow-wins semantics | Preserved verbatim; gains one keyword-only `inherited` prefix, empty by default |
| `execute_workflow`'s existing parameters | Preserved verbatim; ONE additive keyword input |
| Captured gate-config hash for an empty prefix | Byte-identical |
| `PauseSnapshot` / resume-state carriers | No field added or changed |
| Runtime `ChildWorkflowRunner`, `RuntimeHITLGateComposer`, sub-agent dispatch | Not amended (§0.7) |
