---
artifact: design-substrate/Spec_Control_Plane_v1_106.md
version: v1.106
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b39_nested_hitl_response_threading.md (RATIFIED 2026-07-23 — Q1=(A), Q2 original=(A))
  - AskUserQuestion 2026-07-23 (Q2 carrier-shape reconcile, this session — operator selected the keyed-field-inside-ResumeContext reading over the fork's originally-ratified Mapping-at-the-api.resume()-boundary reading)
merge_commit: pending (pre-merge at filing time; B-39 spec-leg PR)
reviewer_chain:
  - operator ratification (2026-07-23) — Q1=(A) retire ResumeContextHolder; Q2 original=(A) Mapping-at-boundary
  - advisor() reconcile (this session) — surfaced the shipped effect_fence_resolutions precedent against Q2's originally-ratified carrier shape
  - operator AskUserQuestion (2026-07-23) — Q2 revised to keyed-field-inside-ResumeContext, no api.resume() signature change
  - just codex-review-uncommitted (2026-07-23, round 1) — out-of-family, found 4 P1 wiring defects in the §1 mechanism draft
  - Explore grounding pass (2026-07-23, round 1) — confirmed all 4 P1s against the real production call graph, file:line precise
  - advisor() (2026-07-23, round 1) — recommended pulling §1 back to CONTRACT altitude rather than a 4th mechanism attempt
  - just codex-review-uncommitted (2026-07-23, round 2) — out-of-family, found the round-1-corrected hitl_responses key shape (branch_path) collides on repeated same-child_workflow_id dispatch
  - advisor() (2026-07-23, round 2) — verified via grep that run_id (not branch_path) is genuinely recursion-stable before endorsing the re-key
  - just codex-review (2026-07-23, round 3, branch-vs-main against open PR #1092) — out-of-family, found 3 P1s of an addressability/safety class distinct from rounds 1-2's wiring-correctness class
  - advisor() (2026-07-23, round 3) — diagnosed the 3 findings as one recurring sub-problem (addressability of a specific paused child) plus a sequencing gap; recommended narrow-scope-plus-register over a 4th mechanism-invention attempt
  - just codex-review (2026-07-23, round 4, branch-vs-main against the round-3 fix commit) — out-of-family, found round 3's own new §1.2 property 4 was itself defective (strands transitively-paused container branches; unassignable to U-CP-64)
  - advisor() (2026-07-23, round 4) — applied the non-convergent-adversarial-hardening-arms-race discriminator ("did my fix cause this finding?" = yes); recommended converting property 4 from a mechanism to a black-box invariant and moving it to the deferred bucket, rather than a 5th mechanism attempt
---

# Clearance — Spec_Control_Plane_v1_106 (B-39 arc, spec leg; FOUR same-day correction passes)

**Round-2 correction (same-day, after round 1's own correction below).** Round
1's §0 keyed `hitl_responses` by C-CP-25 §25.16 `branch_path`
(`compose_branch_path`), reasoning it is "globally unique at arbitrary
recursion depth." A second `just codex-review-uncommitted` pass found this
FALSE: `branch_path` derives from `parent_action_id` → `action_id =
f"workflow:{workflow_id}:step:{step_index}"` — scoped by the STATIC
workflow/manifest identifier, with NO run-instance component. Two PEER
branches dispatching the SAME `child_workflow_id` (an explicitly supported
scenario per this arc's own register history) produce byte-IDENTICAL
`branch_path` values for their respective children's internal steps, so a
grandchild paused under child-instance-A and the equivalent grandchild under
child-instance-B would collide on one map entry. Traced the fix via grep
(per advisor's blocking gate, not skipped): `child_run_id` — derived by
`compose_child_run_id_seed` (`sub_agent_dispatch.py`) as
`sha256("child-run:" + parent_idempotency_key + ":" + branch_path + ":" +
child_workflow_id)`, where `parent_idempotency_key` folds in
`run_idempotency_key = sha256(run_id, workflow_id, ...)` — genuinely
propagates run-instance distinctness at every recursion level, unlike
`action_id`. Fix: `hitl_responses` now keys by the paused child's own
`run_id` (`PausedChildBranchResumeState.child_snapshot.run_id`, an EXISTING
`PauseSnapshot` field — no new carrier field needed). The round-1-added
`PausedChildBranchResumeState.branch_path` field (round-1 §2) is REMOVED as
unnecessary. `hitl_response_for(branch_path)` → `hitl_response_for(
child_run_id)`. Everything else below (Q1/Q2 decisions, the §1 CONTRACT
altitude, the round-1 wiring corrections) is UNCHANGED by this pass.

**Round-1 correction pass (same-day, after this marker's original filing).** The
§1 body originally cleared here prescribed exact wiring — `execute_workflow`
gaining `resume_context`/`resolved_hitl_response` parameters, `attempt_resume`
as the depth-0 delivery entry point, and worker-re-dispatch sites in
`workflow_driver.py` directly threading the new parameters into a recursive
call. Out-of-family review (`just codex-review-uncommitted`) plus an
`Explore` grounding pass found THREE of these assertions empirically false:
the real depth-0 delivery path runs through `harness_runtime/api.py`'s
`resume()` + `lifecycle/mcp_server.py`, not `attempt_resume`; nested-child
re-dispatch crosses into `harness-runtime`'s `RuntimeSubAgentDispatcher`/
`child_workflow_runner.py`, not a direct intra-CP recursive call; and a bare
per-call parameter does not preserve one-shot-per-resume-cycle under the
EXISTING retry composition (`RetryBreakerFallbackDispatcher` re-invokes the
composer's `dispatch()` on every retry attempt within one invocation).
advisor() recommended — and this pass adopts — pulling §1 back to CONTRACT
altitude: state what the replacement mechanism must guarantee (per-branch-
distinct delivery; one-shot preserved under retry; no new global sharing),
leave the exact wiring to the impl leg. A round-1 NEW §2 added
`PausedChildBranchResumeState.branch_path` (mirroring
`EffectFencePausedBranchResumeState.idempotency_key`'s working precedent)
so `hitl_responses` is actually constructible by an external caller — this
was the 4th Codex P1 finding at round 1 and IS a genuine spec-level (not
wiring) fix. **This §2 field was ITSELF removed at round 2** (see the
round-2 correction block above) once `hitl_responses` moved to keying by
`child_run_id` instead of `branch_path` — the addressability need is now
met by the already-existing `child_snapshot.run_id`, no new field required.
The Q1/Q2 carrier-shape decisions below (original clearance content) are
UNCHANGED by round 1 or round 2 — only §1's mechanism-altitude claims (round
1) and §0's key shape (round 2) moved.

v1.105→v1.106: Q1=(A) — `ResumeContextHolder` (the single ctx-level sidecar
that made nested-paused-child HITL-response delivery structurally
one-shot-unsafe and branch-ambiguous) is RETIRED **as a ctx-level,
run-tree-wide-shared binding** — `HarnessContext` no longer carries the
field. **What the replacement mechanism must guarantee (CONTRACT, §1.2,
post-correction):** per-branch-distinct resolution (each concurrently-paused
branch gets its OWN `hitl_response_for(child_run_id)` answer — keyed by the
paused child's own `run_id`, round-2-corrected, NOT `branch_path` — resolved
against the UNMUTATED original `resume_context` — an unaddressed grandchild
must fall back to the TRUE original uniform default, never an ancestor's
resolved answer; an early draft's `resume_context.model_copy(update=
{"hitl_response": resolved})` per-hop-narrowing idea was rejected for
exactly this corruption and is recorded so it is not reinvented); one-shot
delivery preserved under retry (the EXISTING `RetryBreakerFallbackDispatcher`
re-invokes the HITL composer's `dispatch()` on every retry attempt within
one `execute_workflow` invocation — a bare, unconditionally-re-read value
does NOT satisfy this, contra an earlier draft's "structural by
construction" claim); no new global/run-tree-wide sharing. **What is
explicitly NOT specified:** whether `execute_workflow` gains new parameters
(an earlier draft asserted a specific two-parameter signature and named
`attempt_resume` as the depth-0 entry point and direct CP-internal recursion
as the nested-child path — out-of-family review + empirical grounding found
these false; the real depth-0 path is `harness_runtime/api.py`'s `resume()`
+ `lifecycle/mcp_server.py`, and nested-child re-dispatch crosses into
`harness-runtime`'s `RuntimeSubAgentDispatcher`/`child_workflow_runner.py`).
Wiring is impl discretion, verified by execution at the impl leg.

Q2 (how a single `resume()` call delivers DISTINCT responses to 2+
concurrently-paused children) was originally ratified as a `Mapping[str,
ResumeContext]` widening of `api.resume()`'s public signature. Empirical
grounding at this spec leg found a SHIPPED sibling mechanism —
`ResumeContext.effect_fence_resolutions: dict[str, EffectFenceResolution]` +
`effect_fence_resolution_for(key)` — already solving the identical
multi-branch-distinct-resolution problem entirely INSIDE the single
`ResumeContext` object, with no public-API expansion. This was surfaced to
the operator via a second `AskUserQuestion` (framed as a reconcile per the
advisor-recommended discipline, not a silent substitution) with both
readings shown side-by-side; the operator selected the keyed-field reading.
v1.106 therefore adds `ResumeContext.hitl_responses: dict[str, HITLResult]`
+ `hitl_response_for(child_run_id)` — the composition shape (default + per-
key override) mirrors `effect_fence_resolutions`, but the KEY differs
(round-2-corrected): `child_run_id` (the paused child's own `run_id`), not
`branch_path` — `branch_path` was found to collide when two peer branches
dispatch the SAME `child_workflow_id`, since it derives from a workflow_id-
scoped identifier with no run-instance component, whereas `run_id`
genuinely propagates run-instance distinctness through arbitrary recursion
depth (see the round-2 correction block above). `api.resume()`'s public
signature is UNCHANGED at this delta.

**Round-3 correction (same-day, branch-vs-main `just codex-review` against open PR #1092 — the correct pre-merge review mode, distinct from rounds 1-2's `-uncommitted` mode which reviews working-tree-relative diffs polluted by untracked clutter).** Three findings, of a NEW class (addressability/safety, not wiring-correctness): (1) `hitl_response_for`'s uniform-fallback ("absent key → uniform `hitl_response`") is safe only when exactly one child is paused this cycle; with 2+, it risks silently misapplying one branch's response — possibly an EDIT payload with audit-attribution stakes — to an unrelated sibling. Fixed: §1.2 gains property 4, a RESOLVER-level obligation (the resolver, not the pure-lookup `hitl_response_for`, must gate the fallback on the concurrent-paused count); §0's docstrings updated to state this; the identical gap in the shipped, cleared `effect_fence_resolution_for` sibling is registered as a separate pre-existing finding, not fixed here. (2) The plan's AC #8 asserted standalone `resume_context_holder` field removal — landing it alone (before its 3 effect-fence-reader consumption sites are re-pointed) breaks the CURRENTLY-WORKING effect-fence resume mechanism. Fixed: AC #8 withdrawn; folded into the SAME deferred delivery-mechanism bucket as §1.2's contract — physical removal + re-pointing now MUST co-land atomically at the impl leg (§1.4 spec text + CP plan v2.42's own correction). (3) `hitl_responses`/`child_run_id` addressing assumes the caller possesses a prior `PauseSnapshot` — true on the `pause_snapshot`-supplied resume path, but NOT on `api.resume()`'s OTHER mode, `resume_handle` (crash-recovery: caller supplies only `workflow_id`; runtime reads the journal itself), where the caller has no snapshot to read a paused child's `run_id` from before `resume_context` must be constructed. Fixed via advisor-recommended narrowing (not solving): §0 states this as an explicit scope limit — `hitl_responses` addressing is `pause_snapshot`-path-only; `resume_handle` callers are limited to the single-child uniform-fallback case; a follow-on durable-pause-state read accessor is registered (`.harness/forward-register.yaml`), not designed here. advisor()'s diagnosis: findings (1) and (3) trace to ONE recurring sub-problem across rounds 1→2→3 — "how does a `resume()` caller name one specific paused child" (R1: not exposed → added a field; R2: exposed field collides → rekeyed; R3: rekeyed field unreachable on one resume mode → narrowed scope) — the convergence-failure signal that justified a round-3 pass rather than declaring round-2's zero-P1 `-uncommitted` result (itself now understood as an artifact of reviewing the wrong diff mode) sufficient.

**Round-4 correction (same-day, branch-vs-main `just codex-review` against the round-3 fix commit — recursion of the round-3 pattern one level: the fix itself became the finding).** Round 3's NEW §1.2 property 4 prescribed a resolver MECHANISM (count HITL-paused children; gate the uniform fallback to the single-paused-child case; else force INERT re-pause). Review found this DOUBLY wrong: (1) it would strand a transitively-paused container/ancestor branch (blocked only because an unresolved DESCENDANT exists below it, never itself gate-owning) by forcing INERT re-pause instead of unconditional recursion toward the actually-addressed gate-owning descendant — breaking traversal for any nested multi-branch pause; (2) the CP plan assigned this obligation to U-CP-64, which only owns the `ResumeContext` carrier, not the resolver — no declared unit could implement or test it. Fix (advisor()-recommended): property 4 is CONVERTED from a mechanism to a black-box safety+liveness invariant, and MOVED to the SAME impl-leg-deferred bucket as properties 1-3 — no longer owned by U-CP-64. A NEW property 5 formally distinguishes gate-owning branches (subject to `hitl_responses` addressing) from transitively-paused container/ancestor branches (never subject to it, always unconditionally traversable). §0's docstrings + the CP plan's AC #7 revert to carrier-level-only assertions; the multi-branch mutation-probe test is removed from AC #7. All 4 spec/plan artifacts + all 4 clearance markers revised a fourth time.

This is the spec leg only — the impl arc (code + tests) follows as a
separate PR per the B-33/B-59 precedent, and additionally owes the
by-execution call-graph verification this spec leg deliberately declined to
assert (§1.3). Plan delta `Implementation_Plan_Control_Plane_v2_42.md`
(U-CP-64 amended only, post-correction — U-CP-86/88/89 unamended, their
propagation-mechanism role deferred to impl-leg scope-discovery) and the
sibling Runtime spec/plan deltas carry the acceptance criteria.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
