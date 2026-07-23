# Spec: Control Plane — v1.106 (delta over v1.105)

*Delta-only file. The v1.105 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta is the CP-owned rider of the RATIFIED `B-39` nested paused-child HITL-response-routing arc's **spec leg** (`.harness/class_1_fork_b39_nested_hitl_response_threading.md`, ratified 2026-07-23: Q1=(A) retire `ResumeContextHolder` entirely; Q2 revised at spec-leg grounding time via a second operator `AskUserQuestion` — see change-note below — to a keyed-field-inside-`ResumeContext` carrier, NOT the fork's originally-ratified `Mapping[str, ResumeContext]` API-boundary shape). Touches C-CP-25 (§26 area — the `PauseResumeProtocol`/`execute_workflow` composition) + C-CP-26 (`ResumeContext` carrier, §26.8). No CP contract is added or removed; this is a carrier-field amendment. **This delta went through THREE same-day out-of-family review rounds — rounds 1-2 via `just codex-review-uncommitted` (working-tree diff), round 3 via `just codex-review` (branch-vs-`main`, the correct pre-merge mode per the `ship-pr` skill; run after PR #1092 opened).** Round 1 (`just codex-review-uncommitted` + an `Explore` grounding pass) found §1's first draft prescribed exact call-graph wiring that was empirically false against the actual production call graph (the real depth-0 delivery path runs through `harness_runtime/api.py`'s `resume()` + `lifecycle/mcp_server.py`, not `pause_resume_protocol.py`'s `attempt_resume`; nested-child re-dispatch crosses into `harness-runtime`'s `RuntimeSubAgentDispatcher`/`child_workflow_runner.py`, not a direct intra-CP recursive call; and a bare per-call parameter does not preserve one-shot-across-retries) — §1 was rewritten to state the CONTRACT the replacement mechanism must satisfy, leaving wiring to the impl leg, mirroring how the ORIGINAL v1.24 §14.8.8.8 landing of `ResumeContextHolder` itself deferred its own binding-site mechanism. Round 2 (a second `just codex-review-uncommitted` pass, after round 1's fixes landed) found the round-1-corrected §0 `hitl_responses` key shape (`branch_path`) is ALSO wrong — it collides when two peer branches dispatch the SAME `child_workflow_id`, since `branch_path` derives from a workflow_id-scoped `action_id` with no run-instance component. §0 was rewritten to key by the paused child's own `run_id` instead (`PausedChildBranchResumeState.child_snapshot.run_id`, an EXISTING field — genuinely unique across recursion depth AND repeated same-child-workflow-id dispatch, per the `compose_child_run_id_seed` derivation chain traced at §0's own keying-defect note), and the round-1-added `PausedChildBranchResumeState.branch_path` field (§2) was REMOVED as unnecessary once keying moved off `branch_path` entirely. **Round 3 (branch-vs-main `just codex-review`) found a THIRD defect, distinct from rounds 1-2's wiring-correctness class: an addressability/safety gap.** `hitl_response_for`'s uniform-fallback semantic (§0) — "a paused child absent from `hitl_responses` falls back to the uniform `hitl_response`" — is SAFE only when exactly one child is paused this resume cycle; with 2+ concurrently-paused children, an operator supplying only the uniform field (the pre-B-39-shaped call, and the common naive case) would have THAT SAME response — including a branch-specific EDIT payload — silently misapplied to every unaddressed sibling instead of the intended one. §1.2 gains a NEW required property (property 4) closing this at the RESOLVER level (the resolver iterating the paused set knows the concurrent-pause count; `hitl_response_for` itself, a pure per-key lookup, cannot); §0's `hitl_response_for` docstring and this file's "mirrors `effect_fence_resolutions` exactly" framing are corrected to state the deliberate divergence from the effect-fence sibling's fallback semantics (registered separately, not fixed here, as an identical pre-existing gap in the ALREADY-SHIPPED, ALREADY-CLEARED effect-fence mechanism — different blast radius: an idempotency judgment call, not a human-authorized EDIT payload with audit-attribution stakes). §1.4/plan-level: round 3 also found the plan's `resume_context_holder` field-removal AC was assertable as a standalone, independently-completable unit — landing it alone (before the 3 existing effect-fence peek-reader consumption sites are re-pointed) breaks the CURRENTLY-WORKING effect-fence SKIP/RE_FIRE/ABORT resume path; the CP plan delta folds physical removal + re-pointing into ONE atomic co-landing requirement (see the CP plan delta's own correction note). Round 3 additionally found the `hitl_responses`/`child_run_id` addressing scheme depends on the caller possessing a prior `PauseSnapshot` (the `pause_snapshot`-return resume path) — `api.resume()`'s OTHER supported mode, `resume_handle` (crash-recovery: caller supplies only a `workflow_id`, runtime reads the latest durably-journaled snapshot itself), gives the caller NO WAY to learn paused children's `run_id`s before `resume_context` must be constructed; §0 is narrowed to state this scope limit explicitly rather than silently leaving it unaddressed (registered as a follow-on needing a new durable-pause-state read accessor, NOT solved by this spec leg — see §0's new scope note and §3's cross-axis dispositions).*

**Filed:** 2026-07-23
**Authoring authority:** Class 1 fork `.harness/class_1_fork_b39_nested_hitl_response_threading.md` (RATIFIED 2026-07-23 — operator selected Q1=(A), Q2=(A) at fork ratification; Q2's exact carrier SHAPE was left to this spec leg per the fork's own §0 risk (2) — "the batched-map resolution semantics ... is the part the spec delta must pin down, not leave implicit in code" — and was revised at spec-leg grounding time via a second `AskUserQuestion`, below), applied per workspace `CLAUDE.md` §4.3 back-flow + §4.5 clearance discipline.
**Predecessor:** `Spec_Control_Plane_v1_105.md` (v1.105 — the B-33 rotation-correlation-carrier arc's spec leg; filed 2026-07-23)
**Revision shape:** Delta-only spec file per the CP delta-only convention. v1.105 + all earlier file bodies PRESERVED VERBATIM. v1.106 carries this change-note + TWO amendment sites: (1) `ResumeContext` (CP spec v1.16 §26.8.1, `harness_cp/pause_resume_protocol_types.py`) gains a NEW `hitl_responses` field + `hitl_response_for()` method, keyed by the paused child's own `run_id` (round-2-corrected; see §0's keying-defect note); (2) a CONTRACT-level statement (§1, rewritten at round 1) of what the `ResumeContextHolder` retirement's replacement delivery mechanism must guarantee — per-branch-distinct resolution and preserved one-shot-per-resume-cycle — WITHOUT prescribing the exact parameter/call-site shape, which is impl discretion. (A round-1 §2 `PausedChildBranchResumeState.branch_path` field addition was REMOVED at round 2 — no longer needed once `hitl_responses` keys off the already-existing `child_snapshot.run_id`.)

---

## Change-note (v1.105 → v1.106)

**Q2 carrier-shape correction at spec-leg grounding (operator re-touch, 2026-07-23).** The B-39 fork's ratified Q2=(A) reading was "extend `resume()`'s public signature to `resume_context: ResumeContext | Mapping[str, ResumeContext] | None`, keyed by `branch_path`." While grounding this spec leg (empirical read of `pause_resume_protocol_types.py:927-954`), a SHIPPED sibling mechanism was found solving the IDENTICAL problem — "multiple simultaneously-paused branches need independently-keyed responses in ONE `resume()` call" — differently: `ResumeContext.effect_fence_resolutions: dict[str, EffectFenceResolution] | None`, a keyed field INSIDE the single `ResumeContext`, read via `effect_fence_resolution_for(idempotency_key)` (default-value-with-per-key-override lookup; unaddressed keys fall back to the uniform `effect_fence_resolution` field; map entries matching no paused branch this round are harmlessly ignored). This closes the SAME multi-child-concurrent-pause capability as the originally-ratified `Mapping`-at-the-API-boundary reading, WITHOUT widening `api.resume()`'s public signature at all — and Q1=(A)'s own justification for retiring `ResumeContextHolder` ("same concept, two carriers" smell) applies with equal force to keeping `resume_context: ResumeContext | Mapping[...] | None` at the public boundary (a second carrier shape for the identical concept the shipped `effect_fence_resolutions` field already solves). Surfaced to the operator via `AskUserQuestion` (2026-07-23, framed as a reconcile per the advisor-recommended discipline, NOT a silent substitution of the ratified decision) with both readings shown side-by-side; **the operator selected the keyed-field-inside-`ResumeContext` reading** (no `api.resume()` signature change). This is the amendment authored below. `api.resume()`'s public signature is UNCHANGED at this delta (`resume_context: ResumeContext | None = None`, byte-identical to v1.16 §26.8.5).

**One amendment site — `ResumeContext.hitl_responses` (shares `effect_fence_resolutions`'s CARRIER shape — a default-plus-per-key-override dict — but deliberately DIVERGES on fallback SAFETY; see round-3 correction below and §1.2 property 4).**

`harness_cp/pause_resume_protocol_types.py`'s `ResumeContext` (CP spec v1.16 §26.8.1) gains:

```python
class ResumeContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    hitl_response: HITLResult | None = None                       # UNCHANGED (v1.16 §26.8.1)
    effect_fence_resolution: EffectFenceResolution | None = None  # UNCHANGED (existing sibling field)
    effect_fence_resolutions: dict[str, EffectFenceResolution] | None = None  # UNCHANGED (existing sibling field)

    hitl_responses: dict[str, HITLResult] | None = None
    """Per-branch-DISTINCT HITL responses, keyed by the paused CHILD's own
    `PausedChildBranchResumeState.child_snapshot.run_id` — **NOT** `branch_path`
    (corrected at this pass; see the keying-defect note below). `None` (the
    default) → every currently-HITL-paused branch resolves to the uniform
    `hitl_response` above — but ONLY WHEN EXACTLY ONE CHILD IS PAUSED THIS
    RESUME CYCLE (byte-identical to pre-B-39 single-branch behavior in that
    case). When supplied, a paused child whose OWN `run_id` appears as a key
    here is resolved with THIS map's value; a child whose key is absent falls
    back to the uniform `hitl_response` ONLY IF IT IS THE SOLE CHILD PAUSED
    THIS CYCLE — with 2+ children concurrently paused, an unaddressed child
    MUST re-pause INERT rather than silently inherit the uniform default (the
    decline-mirror, never an auto-re-fire, and never a cross-branch
    misapplication of a response — possibly carrying a branch-specific EDIT
    payload — intended for a sibling). This multi-child guard is a RESOLVER-
    level invariant (§1.2 property 4), not a property `hitl_response_for`
    alone can enforce — a pure per-key lookup has no visibility into how many
    siblings are paused this cycle; see round-3 correction note above. This
    is a `default + per-key override` composition (NOT a replacement of the
    single field) — the SAME CARRIER shape `effect_fence_resolutions` ships,
    but with a stricter fallback-safety gate for the reason above (the
    effect-fence sibling's identical uniform-fallback gap is registered, not
    fixed, as a pre-existing shipped-and-cleared issue — see round-3 note).
    Read via `hitl_response_for(child_run_id)`.

    **Scope limit (round-3 correction): `pause_snapshot`-return resume path
    only.** This addressing scheme requires the caller to already possess a
    `PausedChildBranchResumeState.child_snapshot.run_id` — obtainable only
    from a `RunResult.pause_snapshot` object the caller directly holds (the
    resume path where `api.resume(pause_snapshot=...)` is supplied). The
    OTHER resume mode `api.resume()` supports, `resume_handle` (crash-
    recovery: the caller supplies only a `workflow_id`; the runtime reads the
    latest durably-journaled snapshot itself, per §14.14.8), gives the caller
    NO prior snapshot to read a paused child's `run_id` from BEFORE
    `resume_context` must be constructed — so multi-child concurrent HITL
    addressing via `hitl_responses` is NOT YET SUPPORTED on the
    `resume_handle` path; such a caller is limited to the single-paused-child
    case (uniform `hitl_response` only) until a follow-on accessor exposing
    the durably-journaled pause state to `resume_handle` callers before
    `resume_context` construction is designed. This is a registered scope
    limitation, not a silently-dropped case — see §3's cross-axis
    dispositions.

    **Keying-defect note (why `run_id`, not `branch_path`; recorded so the
    `branch_path` reading is not reinvented).** A first draft of this field
    keyed by C-CP-25 §25.16 `branch_path` (`compose_branch_path`), reasoning
    that it is "globally unique at arbitrary recursion depth." Out-of-family
    review (`just codex-review-uncommitted`) found this FALSE: `branch_path`
    derives from `parent_action_id`, which derives from `action_id =
    f"workflow:{workflow_id}:step:{step_index}"` (`workflow_driver.py`) —
    scoped by the STATIC workflow/manifest identifier, with NO `run_id`
    component. When two PEER branches dispatch the SAME `child_workflow_id`
    (an explicitly supported scenario — see this arc's own register history),
    their respective children's INTERNAL `action_id`/`branch_path` values are
    byte-IDENTICAL (same `workflow_id`, same internal `step_index`), so a
    grandchild paused under child-instance-A and the equivalent grandchild
    paused under child-instance-B would COLLIDE on the same `branch_path` key
    — the map could not carry two distinct responses. `run_id`, by contrast,
    genuinely IS distinct per recursive dispatch instance: `child_run_id` is
    derived via `compose_child_run_id_seed` (`harness-runtime/lifecycle/
    sub_agent_dispatch.py`) as `sha256("child-run:" + parent_idempotency_key +
    ":" + branch_path + ":" + child_workflow_id)`, and `parent_idempotency_key
    = _compute_step_idempotency_key(run_idempotency_key, step_index, ...)`
    where `run_idempotency_key = sha256(run_id, workflow_id, ...)` — the
    SPAWNING invocation's OWN `run_id` is folded in at every level, so two
    peer branches spawning the same `child_workflow_id` (distinct `run_id`s at
    the spawning level, since `run_id` is unique per `execute_workflow`
    invocation) necessarily derive DISTINCT child `run_id`s, and this
    distinctness propagates to every further-nested grandchild by the same
    recursive argument. `run_id` is therefore genuinely unique across
    arbitrary recursion depth AND repeated same-`child_workflow_id` dispatch
    — the property `branch_path` was wrongly assumed to have. No new carrier
    field is needed to expose it: `PausedChildBranchResumeState.child_snapshot.
    run_id` (`PauseSnapshot.run_id: str`, already a REQUIRED existing field)
    already carries it — an operator reads `paused_child.child_snapshot.
    run_id` off a prior `RunResult.pause_snapshot` to build a `hitl_responses`
    key, with NO new public field addition (a prior draft of this spec leg
    added `PausedChildBranchResumeState.branch_path` for this purpose; REMOVED
    at this pass — `child_snapshot.run_id` already solves the identical
    addressability need, more robustly, with a smaller diff).

    HOW the resolved per-branch answer physically reaches the resumed step's
    gate composer (which parameter, which call site, at which recursion
    level) is deliberately UNSPECIFIED here — see §1's contract-level
    statement below; this field only fixes the CARRIER SHAPE an operator
    constructs, not the delivery mechanism.

    A pause that is NOT branch-scoped (the depth-0 root's own linear/fan-out-
    barrier gate) has no child `run_id` to key by (it IS the run); its gate
    always consumes the uniform `hitl_response` field directly, exactly
    mirroring how a LINEAR effect-fence pause consumes `effect_fence_resolution`
    directly (§26.8.1 sibling-field precedent, unamended by this delta)."""

    def hitl_response_for(self, child_run_id: str) -> HITLResult | None:
        """The operator's HITL response for one paused child's own `run_id`.

        A PURE per-key lookup-with-fallback: the `hitl_responses` map entry
        for `child_run_id` if present, else the uniform `hitl_response`
        default. `None` when neither is supplied → the branch re-pauses
        INERT (never an auto-re-fire). A `None` map and a map-without-this-
        key both fall through to the single default, so single-paused-child
        callers (the only shape that existed pre-B-39) are byte-unchanged.
        Keyed by `child_run_id` (`PausedChildBranchResumeState.child_snapshot.
        run_id`), NOT `branch_path` — see the keying-defect note above; the
        composition CARRIER shape (default + per-key override) mirrors
        `effect_fence_resolution_for` (§26.8.1), only the key differs.

        **This method alone does NOT enforce the multi-child fallback-safety
        guard (§1.2 property 4, round-3 correction).** It has no visibility
        into how many siblings are paused this resume cycle, so it cannot by
        itself refuse an unsafe uniform-fallback call. The RESOLVER invoking
        this method (impl-discretion, §1.3) MUST count the currently-paused
        children first and call this method's fallback branch ONLY when
        exactly one child is paused this cycle; with 2+ paused, the resolver
        MUST treat an absent map key as INERT re-pause, not call through to
        the uniform `hitl_response` default. This is a resolver-level
        obligation this pure method cannot discharge on its own."""
        if self.hitl_responses is not None:
            mapped = self.hitl_responses.get(child_run_id)
            if mapped is not None:
                return mapped
        return self.hitl_response
```

No new CP fail-class; no `ResumeResult` change; no `attempt_resume` signature change (already widened at v1.16 §26.8.5, unamended here).

---

## §1 (REWRITTEN at correction pass) — `ResumeContextHolder` retirement (Q1=(A)): CONTRACT, not mechanism

**§1.1 The defect this closes.** Per the fork's §1 crux: `ctx` (the `DriverContext`) is threaded IDENTICALLY, BY REFERENCE, to every recursion level — there is exactly ONE `ResumeContextHolder` slot (a runtime-owned sidecar, `Spec_Harness_Runtime_v1.md` §14.8.8.9) for an entire recursive run tree, at ANY depth. A keyed-map carrier bolted onto that single shared slot (the reverted pre-B-39 attempt) inherits two structural defects: never-one-shot-consumes (the slot has no natural per-invocation scope) and no branch-uniqueness guard (the slot is not keyed at all). `ResumeContextHolder` (`HarnessContext.resume_context_holder`) is RETIRED, FULL STOP — per Q1=(A)'s ratified decision, there is no ctx-level, run-tree-wide-shared binding at any name or shape in the replacement mechanism (out-of-family review, round 4: an earlier draft's "not the class, only the binding" framing risked reading as reopening Q1 for a retained-and-rescoped class; removed — Q1's retirement is not impl discretion). This spec leg fixes the CARRIER SHAPE (§0 above, `ResumeContext.hitl_responses`) and states below what the replacement delivery mechanism MUST guarantee; it deliberately does NOT prescribe which parameter, which function, or which call site delivers a resolved answer to a resumed step's gate — that is impl discretion, resolved empirically at the impl leg against the actual production call graph.

**§1.2 Required properties of the replacement mechanism (CONTRACT — binding on the impl leg; wiring is NOT specified here).**

1. **Per-branch-distinct resolution.** For any two DISTINCT concurrently-paused branches (peer siblings under `PARALLELIZATION`/`ORCHESTRATOR_WORKERS`, or nested parent/child under `HIERARCHICAL_DELEGATION` recursion), the mechanism MUST deliver each branch its OWN `hitl_response_for(child_run_id)` resolution (keyed by the paused child's own `run_id`, not `branch_path` — see §0's keying-defect note), computed against the SAME unmutated, operator-supplied `resume_context` object — never a value another branch already consumed, and never a value narrowed/mutated by an ancestor's own resolution (the exact grandchild-fallback-corruption bug a first draft of this section introduced and review caught — recorded so it is not reinvented: DO NOT narrow `resume_context.hitl_response` per recursion hop via e.g. `.model_copy(update={"hitl_response": resolved})`; `hitl_response_for`'s unaddressed-branch fallback must always resolve against the operator's TRUE original uniform default, at any depth).
2. **One-shot per resume cycle, preserved under retry.** Runtime spec §14.8.8.7 invariant 3 ("a paused step's resolved HITL response is consumed at most once per resume cycle") is UNCHANGED and MUST continue to hold under the EXISTING retry composition (`RetryBreakerFallbackDispatcher` wraps the HITL gate composer as `inner`; a single `execute_workflow` invocation's retry loop may re-invoke the composer's `dispatch()` multiple times for the SAME step). A bare per-call parameter re-supplied identically on every retry attempt does NOT satisfy this by itself — the replacement mechanism MUST distinguish "first post-resume dispatch of this resume cycle" from "a same-cycle retry attempt," the way the retired holder's `consume_and_clear()` did via its own mutable one-shot state. This is a CONTRACT requirement on the impl leg's chosen mechanism, not a prescription of which object holds that state.
3. **No new global sharing.** Whatever replaces the ctx-level slot MUST NOT reintroduce a single instance shared across the entire recursive run tree (that is the ORIGINAL defect, restated). Scoping the replacement no wider than "one resume cycle for one specific paused step" is sufficient to satisfy both properties above.
4. **Multi-child fallback-safety gate (round-3 correction, out-of-family review).** The resolver that calls `ResumeContext.hitl_response_for(child_run_id)` (§0) MUST first determine how many children are HITL-paused this resume cycle (it is iterating that set to resolve each one; the count is available at no extra cost). The uniform `hitl_response` fallback (an absent `hitl_responses` map, or a map without this child's key) MAY be applied ONLY when exactly one child is paused this cycle. With 2+ children concurrently paused, a child absent from `hitl_responses` MUST re-pause INERT — the resolver MUST NOT call through to the uniform default in that case. Without this gate, an operator supplying only the pre-B-39-shaped uniform `hitl_response` (the common naive call, and the byte-compatible default) would have that SAME response — possibly an EDIT payload scoped to one specific branch, with audit-trail attribution to that branch — silently misapplied to every OTHER concurrently-paused sibling, defeating this arc's own purpose (per-branch-distinct resolution, property 1 above). This is why `hitl_response_for` (§0) is documented as NOT self-sufficient to satisfy this property — the count-awareness is structurally a resolver-level fact, not a `ResumeContext` fact. **Deliberately NOT extended to `effect_fence_resolution_for`/`effect_fence_resolutions`** (the sibling mechanism, §26.8.1, unamended by this delta): it ships the identical uniform-fallback-to-every-unaddressed-branch shape, already SHIPPED and CLEARED prior to this arc. Fixing it is registered as a separate, pre-existing finding (not this arc's scope — different blast radius: an idempotency SKIP/RE_FIRE/ABORT judgment call, not a human-authorized decision with audit-attribution stakes) rather than silently left unflagged.

**§1.3 What is explicitly NOT specified here (impl discretion).** Which entry point supplies the resolved value for the depth-0 (root) pause; whether `execute_workflow` gains new parameters and what they are named; how a nested child's re-dispatch (which crosses the CP↔Runtime package boundary — CP's driver stamps step-execution state that Runtime's sub-agent dispatch layer reads and acts on, per the EXISTING `child_resume_snapshot`/`RuntimeSubAgentDispatcher`/`child_workflow_runner` seam this arc does not itself alter the shape of) receives its own resolved value. A prior draft of this section asserted specific answers to all three (naming `pause_resume_protocol.py`'s `attempt_resume` as the depth-0 entry point, and a direct intra-CP recursive `execute_workflow` call as the nested-child path) — out-of-family review plus empirical grounding found BOTH assertions false against the actual call graph (the real depth-0 entry point is `harness_runtime/api.py`'s `resume()` + `lifecycle/mcp_server.py`; nested-child re-dispatch genuinely crosses into `harness-runtime`). Rather than assert a fourth unverified mechanism, this spec leg states the CONTRACT (§1.2) and leaves the wiring to the impl leg, which MUST verify its chosen call graph by execution (not by grep) before landing — mirroring how the ORIGINAL v1.24 §14.8.8.8 landing of `ResumeContextHolder` itself deferred its own binding-site mechanism to its impl leg.

**§1.4 `DriverContext.resume_context_holder` Protocol field — RETIRED as a ctx-level binding (CONTRACT-level design commitment; physical removal is an ATOMIC co-landing requirement, round-3 correction).** The `DriverContext` Protocol (structurally satisfied by `HarnessContext` at runtime composition per C-CP-25 §25.3 composition discipline) no longer declares a run-tree-wide-shared `resume_context_holder` field, as a DESIGN commitment — this is fixed, not impl discretion (Q1=(A)). The PHYSICAL removal of the field is NOT independently completable, however: the 3 existing `getattr(ctx, "resume_context_holder", None)` consumption sites (the linear B-EFFECT-FENCE-PAUSE-RESOLUTION reader + the two fan-out — `PARALLELIZATION`/`ORCHESTRATOR_WORKERS` — effect-fence peek readers, all in `workflow_driver.py`) currently read effect-fence resolutions THROUGH this field. Because effect-fence resolution delivery is the SAME deferred-to-impl-leg delivery-mechanism question as HITL response delivery (§1.3), removing the field before its replacement delivery path exists would land a broken intermediate state — every one of those 3 readers would silently receive `None` via `getattr`'s default, causing effect-fence resume to ALWAYS re-pause INERT even when the operator supplied a resolution, a regression of a CURRENTLY-WORKING mechanism. The impl leg MUST land field removal and re-pointing all 3 consumption sites to their replacement delivery mechanism in the SAME change — never as two separately-sequenced, independently-completable units. The effect-fence resolution SEMANTICS (§26.8.1, unamended) are untouched by this delta — only the ctx-level-sidecar DELIVERY MECHANISM is retired, and its replacement (for BOTH HITL and effect-fence readers) is impl discretion per §1.3.

---

## §2 (REMOVED at correction pass) — operator-addressability, resolved without a new field

A prior draft of this section added `PausedChildBranchResumeState.branch_path`
(mirroring `EffectFencePausedBranchResumeState.idempotency_key`'s working
precedent) so an operator could read a paused child's key off `RunResult.
pause_snapshot`. Superseded by the §0 keying-defect correction: since
`hitl_responses` is now keyed by `child_run_id`, not `branch_path`, and
`PausedChildBranchResumeState.child_snapshot.run_id` (`PauseSnapshot.run_id:
str`) is an EXISTING, ALREADY-REQUIRED field that already carries exactly
this value — no new field is needed. `PausedChildBranchResumeState` is
UNCHANGED by this delta (zero new fields). No change to
`EffectFencePausedBranchResumeState` either (already exposes its own key, by
`idempotency_key`, which is unaffected by this correction — the effect-fence
mechanism does not cross a recursion boundary the way HITL child-pause
delivery does, so it never had the recursion-collision exposure `branch_path`
had).

---

## §3 — Preservation guarantees

| Element | Disposition |
|---|---|
| v1.105 §20.3.1 (AMENDED) + §20.3.2 (NEW) B-33 rotation-correlation-carrier content | Preserved verbatim |
| v1.16 §26.8.1-§26.8.5 `ResumeContext` carrier + `attempt_resume` widened signature | Preserved verbatim EXCEPT the additive `hitl_responses` field + `hitl_response_for` method (§0 above) — `hitl_response` field, `effect_fence_resolution(s)` fields, and `attempt_resume`'s own signature are BYTE-UNCHANGED |
| v1.10 §26.1-§26.7 `PauseResumeProtocol` substantive content | Preserved verbatim |
| `execute_workflow`'s existing parameters | Preserved verbatim — this delta adds NO new parameters to `execute_workflow` (a prior draft did; corrected — see §1.3) |
| `PausedChildBranchResumeState`'s existing fields | Preserved verbatim, UNCHANGED — zero new fields (§2: a prior draft added `branch_path`; removed, `child_snapshot.run_id` already suffices) |
| `DriverContext.resume_context_holder` field (ctx-level, run-tree-wide-shared binding) | **RETIRED as a design commitment** at this delta (§1.4) — the ONLY breaking removal in this file; PHYSICAL field removal is impl discretion in mechanism but NOT in sequencing — it MUST co-land atomically with re-pointing the 3 existing effect-fence consumption sites (§1.4, round-3 correction) |
| `hitl_response_for`'s uniform-fallback safety scope | NARROWED at round-3 correction: safe ONLY when exactly one child is paused this cycle (§0, §1.2 property 4) — a resolver-level obligation, not a carrier-level guarantee |
| `hitl_responses`/`child_run_id` addressing — resume-mode coverage | SCOPED at round-3 correction to the `pause_snapshot`-return resume path only; the `resume_handle` crash-recovery path is a registered, NOT-YET-SUPPORTED limitation (§0 scope-limit note) pending a follow-on durable-pause-state read accessor |

**Cross-axis dispositions.** Runtime-owned contract text (the `ResumeContextHolder` sidecar retirement, stated at the same CONTRACT altitude) lives at the same-arc `Spec_Harness_Runtime_v1.md` v1.106 §14.8.8.10 — cross-referenced, not restated here. OD / IS / AS specs UNCHANGED. **CXA classification: re-verified at this correction pass, not carried forward unexamined.** The nested-child-pause re-dispatch mechanism this arc's replacement wiring will land against (`StepExecutionContext.child_resume_snapshot` → `RuntimeSubAgentDispatcher` → `ChildWorkflowRunner` → `child_workflow_runner.py`, which re-enters `harness_cp.workflow_driver.execute_workflow`) is an EXISTING CP↔Runtime seam this arc does not itself widen or reclassify — this spec leg adds no new field to `StepExecutionContext`, no new parameter to the `ChildWorkflowRunner` Protocol, and no new cross-axis edge; whatever the impl leg's wiring turns out to be, it either reuses this existing seam (no CXA change) or, if it cannot, that is itself a Class 1/2 fork question for the impl leg to raise — NOT resolved by this spec leg. **Two round-3-registered follow-ons, NEITHER resolved by this spec leg:** (a) a durable-pause-state read accessor design enabling `resume_handle` callers to learn paused children's `run_id`s before `resume_context` construction (§0 scope-limit note) — needed to lift the `resume_handle`-path limitation; (b) the pre-existing, already-shipped `effect_fence_resolution_for` uniform-fallback gap (§1.2 property 4's "deliberately NOT extended" note) — same hazard class as this arc's own finding 1, but out of this arc's scope since the mechanism is already cleared. Both should be filed at `.harness/forward-register.yaml` as new `B-*` rows, not left as spec-text-only notes. Plan deltas `Implementation_Plan_Control_Plane_v2_42.md` (corrected at this pass) + `Implementation_Plan_Harness_Runtime_v2_54.md` (corrected at this pass) carry the acceptance criteria at the same contract altitude. Clearance marker at `.harness/clearance/spec-control-plane-v1-106-cleared-2026-07-23.md`.

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_106.md` |
| Version | v1.106 |
| Filing event | B-39 spec leg (Q1=(A) + Q2 revised-at-grounding=(keyed-field), per the fork's own §0 risk (2) deferral to this leg); THREE same-day correction passes after out-of-family review — rounds 1-2 (wiring-correctness class, `-uncommitted`) + round 3 (addressability/safety class, branch-vs-main `just codex-review`, run against open PR #1092) |
| Predecessor | `Spec_Control_Plane_v1_105.md` |
| Operator authority | Fork ratification 2026-07-23 (Q1/Q2 original); `AskUserQuestion` 2026-07-23 (Q2 carrier-shape reconcile, this session) |
| Co-published artifacts (this arc) | `Spec_Harness_Runtime_v1.md` v1.105→v1.106; `Implementation_Plan_Control_Plane_v2_42.md`; `Implementation_Plan_Harness_Runtime_v2_54.md`; clearance markers for both specs; workspace `CLAUDE.md` + `harness-cp/CLAUDE.md` pointer bumps |
| Impl leg | NOT bundled — per the B-33/B-59 spec-leg/impl-leg precedent this fork's §0 status line itself names, code + tests land as a separate follow-on arc; the impl leg additionally owes the by-execution call-graph verification this spec leg deliberately declined to assert (§1.3) |
| Cross-axis cascade | ZERO new seams asserted; re-verified (not carried forward) at the correction pass — §3 above |
