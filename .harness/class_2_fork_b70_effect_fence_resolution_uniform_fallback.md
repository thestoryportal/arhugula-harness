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
| Status transition | `registered_finding` → `design_substrate_gated` (this filing) → `open` (spec-leg landing, below) |
| Next step | Operator/Claude-authored CP spec delta (§26.8.1 companion property) + plan delta + clearance marker, then impl leg — mirrors B-33/B-39/B-59 spec-leg-first precedent. Not opened by this filing. |

## §6 — Spec-leg landing (2026-07-24, same day)

Operator ratified "open the spec-leg now" via `AskUserQuestion` (over "hold registered with dormant siblings"). Landed: `Spec_Control_Plane_v1_107.md` (NEW §1, the §3 recommendation above — safety + liveness invariant, no property-5 equivalent) + `Implementation_Plan_Control_Plane_v2_43.md` (ONE deferred coverage-matrix row, zero unit amendment, mirroring how CP plan v2.42 §5 deferred the parallel `hitl_responses` property 4/5 invariants) + clearance markers `.harness/clearance/spec-control-plane-v1-107-cleared-2026-07-24.md` + `.harness/clearance/implementation-plan-control-plane-v2-43-cleared-2026-07-24.md`. `.harness/forward-register.yaml` B-70 row flipped `design_substrate_gated` → `open`. Impl leg (the resolver's tree-walk enumeration of the unaddressed effect-fence-pause set, wired at the LINEAR + ORCHESTRATOR + two fan-out consume sites) is the next buildable slice — NOT opened by this filing, per the B-33/B-39/B-59 precedent.

**Round-1 correction (out-of-family `just codex-review-uncommitted`, same day).** This fork's §3 draft (above) and the first draft of `Spec_Control_Plane_v1_107.md` §1.1 both omitted a THIRD effect-fence-pause carrier: `PauseSnapshot.orchestrator_effect_fence_resume` (`OrchestratorEffectFencePausedResumeState`, populated by `ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION` when the orchestrator's OWN `steps[0]` dispatch — not a worker's — fence-pauses; a 6th top-level `PauseSnapshot` carrier, never co-set with the other five). The shipped consume site at `workflow_driver.py` (~line 11044) also calls `effect_fence_resolution_for`, so the original two-carrier enumeration (LINEAR `effect_fence_resume` + fan-out `effect_fence_paused_branches`) would have left this third carrier's uniform-fallback exposure unfixed — exactly the cross-location misapplication B-70 exists to close. Fixed in the spec delta (§1.1's definition now covers all three sites) before commit; this carrier is likewise inherently gate-owning by construction (its own docstring: populated only at the true fence-holding dispatch, never a forwarded nested pause), so the "no property-5 equivalent" grounding conclusion is unaffected.

**Round-2 correction (out-of-family `just codex-review-uncommitted`, second same-day pass) — a deeper defect in the safety rule itself, not just the carrier enumeration.** The round-1-corrected draft phrased set membership uniformly by map-key presence and phrased the safety clause as "MAY resolve a location's `effect_fence_resolution_for(idempotency_key)` call ONLY when...". Out-of-family review found this a NO-OP for the LINEAR site specifically: `Spec_Control_Plane_v1_66.md` §1 states the LINEAR consume path (`workflow_driver.py` ~lines 4581-4585) reads `resume_context.effect_fence_resolution` DIRECTLY and UNCONDITIONALLY when set — it never calls `effect_fence_resolution_for`, and the keyed map is structurally INERT there ("a map supplied for a linear pause is inert"). A rule phrased only around `effect_fence_resolution_for` calls cannot prevent the LINEAR site from consuming the uniform value even when a co-existing fan-out/orchestrator pause is correctly forced to INERT under the rule — reproducing the exact cross-location misapplication this property exists to close, merely shifted onto the LINEAR side instead of closed. This round's fix (make a LINEAR pause UNCONDITIONALLY a member of the unaddressed set whenever present, never excludable) was itself SUPERSEDED at round 3 below — it introduced a worse defect.

**Round-3 correction (out-of-family `just codex-review-uncommitted`, third same-day pass) — round 2's fix would permanently livelock any 2+-simultaneous-LINEAR-pause resume.** Because round 2 counted a LINEAR pause as unaddressed REGARDLESS of any map entry, TWO simultaneously-paused LINEAR locations (e.g. two independent nested children, each a simple linear workflow, each hitting its own tool-step effect fence) could never be resolved by any operator input — the unaddressed set would always have size ≥2, forcing both to re-pause INERT forever even with correctly-keyed distinct `effect_fence_resolutions` entries supplied — a genuine liveness violation, unrecoverable resume, worse than the safety gap B-70 exists to fix. Root cause found by direct read: the LINEAR carrier `EffectFenceResumeState` ALREADY exposes its own `idempotency_key` (`pause_resume_protocol_types.py` line 541) — the map is inert TODAY only because the consume site chooses to read the raw field instead of calling the resolver method with that key, not because the carrier lacks one. Fixed in the spec delta: the LINEAR site becomes genuinely map-addressable (reusing its existing key, calling the existing `effect_fence_resolution_for` method) instead of being permanently excluded from addressing — membership is now uniformly determined by map-key presence across all three carriers, with no special-case carve-out. The impl leg's scope-discovery pass (CP plan v2.43 §5) is updated accordingly.

**Round-4 correction (out-of-family `just codex-review-uncommitted`, fourth same-day pass) — `resume_handle` scope limit, mirroring `B-69`.** For the crash-recovery `resume_handle` resume mode, the caller has no prior `RunResult.pause_snapshot` to read a paused location's `idempotency_key` from before `resume_context` must be constructed — identical to `B-69`'s already-registered finding for `hitl_responses`. Added an explicit scope-limit note to the spec (§1 round-4) stating such a caller is limited to the single-pause case when 2+ effect-fence-pause locations are simultaneously outstanding; claimed the same generalized `B-69` durable-pause-state read accessor closes this gap too, so no new `B-*` row was filed.

**Round-5 correction (out-of-family `just codex-review-uncommitted`, fifth same-day pass) — round 4's `B-69` citation was aspirational, not accurate.** `B-69`'s own registered close-out, as then-written, named only HITL child `run_id`s as the identity the accessor would expose — a caller building `effect_fence_resolutions` needs `idempotency_key`s, a distinct identity kind not committed to. Fixed by widening `B-69`'s own `.harness/forward-register.yaml` row (summary + close_out, generalized to cover both identity kinds) so the citation is accurate rather than merely asserted; still no new `B-*` row filed.
