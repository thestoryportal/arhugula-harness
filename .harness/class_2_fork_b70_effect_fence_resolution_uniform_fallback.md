# Class 2 Fork — B-70: `effect_fence_resolution_for`'s uniform-fallback safety gap

**Filed:** 2026-07-24 · autonomous-loop grounding pass (register `B-70`, registered 2026-07-23 at the
B-39 spec-leg PR #1092, out-of-family Codex round 3). **Classification: Class 2** (narrow, non-cross-domain
recommendation — no council convened; `council: no` at the register row, unchanged by this grounding). No
`design-substrate/**` file is edited by this filing; `B-70` flips `registered_finding` → `design_substrate_gated`
with this filing (the same discriminator B-48/B-59/B-39 applied: a real gap that needs a spec-level CONTRACT
property before code is `design_substrate_gated`, not `registered_finding` — the latter would signal
buildable-now and risks routing an impl PR before the contract is stated).

## §1 The defect (confirmed by direct grounding, 2026-07-24)

`Spec_Control_Plane_v1_106.md` §1.2 property 4 fixed a safety gap in the NEW `ResumeContext.hitl_responses`/
`hitl_response_for` mechanism: when 2+ gate-owning branches are concurrently paused, the uniform
`hitl_response` field may resolve a branch's `hitl_response_for(child_run_id)` call **only when that branch
is the sole member of the unaddressed gate-owning set this cycle** — otherwise every member must re-pause
INERT. Property 4's own text explicitly states this fix was "deliberately NOT extended to
`effect_fence_resolution_for`/`effect_fence_resolutions`... it ships the identical uniform-fallback-to-
every-unaddressed-branch safety gap, already SHIPPED and CLEARED prior to this arc... registered as `B-70`."

Direct read of `harness-cp/src/harness_cp/workflow_driver.py` confirms the mechanics: the singular
`resume_context.effect_fence_resolution` field is consulted independently at **every** `execute_workflow`
call (at every recursion depth) whenever that call's own `resume_snapshot.effect_fence_resume is not None`
(line ~4582), with no cross-depth/cross-branch "am I the only one waiting" check — unlike the fan-out-peer
`effect_fence_resolutions` map (keyed by `idempotency_key`), which already provides correct per-branch
addressing for peers under the SAME barrier. If two distinct locations in one resume tree are simultaneously
effect-fence-paused (e.g. a top-level linear pause AND a nested child's own linear pause, or two peers under
different barriers), an operator supplying only the uniform `effect_fence_resolution` (no keyed map) gets
that single SKIP_AS_FIRED/RE_FIRE/ABORT judgment applied to **all** of them — silently wrong for any location
whose correct resolution differs.

## §2 Grounding conclusions (the two questions this fork was filed to resolve)

**Q1 — Does effect-fence pausing have a "container/gate-owning" split analogous to HITL's property 5?**
**No.** Confirmed two ways: (a) `EffectFencePausedBranchResumeState`'s own docstring states `step_kind` is
"always tool-step in production — only a TOOL_STEP's dispatch reaches the runtime tool fence" — an ancestor
`SUB_AGENT_DISPATCH` branch merely forwarding a nested descendant's pause is captured via the generic
`SubAgentChildPausedError` → `PausedChildBranchResumeState` path (any `RunStatus.PAUSED` child, any
pause_reason), **never** via `EffectFencePausedBranchResumeState` — that carrier is only ever populated at
the true fence-holding location. (b) `Spec_Control_Plane_v1_106.md` §2 (REMOVED at correction pass) states
this canonically: "the effect-fence mechanism does not cross a recursion boundary the way HITL child-pause
delivery does" — `idempotency_key` is already globally unique per held reserve, independent of recursion
depth, so there is no branch_path/run_id-style keying collision to fix. **Every** captured
`effect_fence_resume`/`effect_fence_paused_branches` entry is inherently gate-owning by construction; B-70's
own close_out conditional ("if containers exist, mirror property 5; if not, a plain count-based invariant is
safe") resolves to the simpler branch. This makes B-70's eventual fix narrower in shape than B-39's — no
property-5 equivalent is needed, only a property-4 equivalent.

**Q2 — Does the fix need a spec property, or is it pure impl-to-cleared-spec?** **It needs a spec property.**
Restricting when the singular `effect_fence_resolution` fallback auto-applies is an observable CONTRACT
change to a currently-shipped, P5-CK-cleared mechanism (whether a given resume auto-resolves or safely
re-pauses INERT) — the same class of change property 4 itself was, not a bug-fix against unambiguous spec
text. Per X-AL-3 this is design-substrate-gated, not a Phase-7 code fix.

## §3 Recommendation (for the eventual spec-leg arc; not built by this filing)

Add a new property to `Spec_Control_Plane_v1_106.md` §26.8.1 (companion to, not a rewrite of, the existing
effect-fence resolution semantics), mirroring §1.2 property 4's SAFETY + LIVENESS shape:

- **Safety.** For a resume cycle, let the "unaddressed effect-fence-pause set" be every location in the
  resume tree whose own `effect_fence_resume` (LINEAR) is set, or whose own `effect_fence_paused_branches`
  entry (fan-out) exists, and whose `idempotency_key` is NOT a key in `effect_fence_resolutions`. The uniform
  `effect_fence_resolution` fallback MAY resolve a location's `effect_fence_resolution_for(idempotency_key)`
  call ONLY when that location is the sole member of the unaddressed set this cycle; when 2+ members exist,
  every member re-pauses INERT.
- **Liveness.** A transitively-paused container/ancestor branch (never itself gate-owning per §2 above) MUST
  still be traversed/re-entered regardless of the effect-fence set's contents — it never itself holds an
  `idempotency_key` and so is never a member of the set.
- **No property-5 equivalent needed** (per §2 grounding above) — every member of the unaddressed set is
  already gate-owning by construction; the resolver does not need to distinguish container from gate-owning
  locations the way the HITL resolver does.
- Impl discretion (deferred to the impl leg, mirroring §1.3): HOW the resolver enumerates the unaddressed set
  across the full resume tree (a tree-walk of `paused_child_branches` collecting every nested
  `effect_fence_resume`/`effect_fence_paused_branches` entry) — verified by execution against the real
  recursion structure, not asserted here.

## §4 Scope note

This is registered narrower-blast-radius than B-39 (an idempotency SKIP/RE_FIRE/ABORT judgment call, not a
human-authorized decision with audit-attribution stakes, per property 4's own text) and has NO currently-known
live production trigger (no automated caller resolves 2+ simultaneously effect-fence-paused locations with
only the uniform field today) — genuinely buildable once prioritized, not urgent. `council: no` stands; the
recommendation above is mechanical parity with an already-ratified pattern, simplified by the absence of a
container/gate-owning split.

## §5 Filing footer

| Field | Value |
|---|---|
| Register row | `B-70` (`.harness/forward-register.yaml`) |
| Prose home | `.harness/post-phase-8-forward-register.md` §"B-70" |
| Status transition | `registered_finding` → `design_substrate_gated` (this filing) |
| Next step | Operator/Claude-authored CP spec delta (§26.8.1 companion property) + plan delta + clearance marker, then impl leg — mirrors B-33/B-39/B-59 spec-leg-first precedent. Not opened by this filing. |
