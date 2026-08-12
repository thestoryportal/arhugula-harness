# E3 — out-of-family evaluator (Codex / GPT-5.6-class), COLD read

*(`just codex-review` on the committed council tree at `e33c947f`, 2026-08-12.
Decorrelation honored: Codex read the artifact and the code, never the adversarial
findings and never advisor's evaluation. Findings verbatim.)*

**Headline:** *"The reconciled design contains identity-carrier, liveness, and
crash-recovery contradictions that would propagate into the specification and
implementation. In particular, its branch-index-only reverse carrier cannot
preserve tree-wide uniqueness."*

## [P1] Key persisted tokens by tree-wide branch identity — E1-RECONCILED.md:60

> Nested fan-outs can contain both a root branch 0 and a nested branch 0; the
> existing `test_pre_dispatch_gate_owning_branches_at_different_tree_positions_never_collide`
> explicitly covers this case. A depth-zero `Mapping[int, str]` inherited unchanged
> cannot represent both tokens, so the nested composer may select the root token or
> one entry may overwrite the other, recreating duplicate webhook/audit keys and
> incorrect pause-view correlation. Key this carrier by a tree-wide identity or use
> subtree-scoped mappings instead of bare `branch_index`.

**Orchestrator note:** the cited witness EXISTS —
`harness-cp/tests/test_workflow_driver_hitl_uniform_fallback_property4.py`. This is
precisely the executed collision test advisor demanded, already built by the B-72 arc.

## [P1] Derive resolvability after sole-member status is known — E1-RECONCILED.md:65-66

> For a pause with exactly one pre-dispatch gate owner,
> `compute_hitl_uniform_fallback_eligible_run_id` returns that owner immediately
> (`workflow_driver.py:2891-2897`), so its request **is** answerable through the
> uniform response. This design instead statically marks pre-dispatch requests as
> held and binds the reply affordance to that posture; because posture-change
> redelivery is deferred, a sole request never advertises an actionable state and
> **may remain paused**. Emit or update this status from the tree-wide sole-member
> computation rather than branch context alone.

**Orchestrator verification — CONFIRMED.** `workflow_driver.py:2895-2897` reads
`if len(unaddressed) == 1: return unaddressed[0]`. A sole pre-dispatch owner IS
returned as uniform-fallback-eligible. **The design would introduce a LIVENESS
FAILURE while trying to prevent an operator trap** — telling the operator not to
reply to the one request whose reply would actually resolve the run. Missed by all
five in-family voices, the in-family adversarial, and the in-family advisor. This
is the decorrelation dividend.

## [P2] Stabilize the crash fallback across entry-version changes — E1-RECONCILED.md:55

> If webhook token X is delivered, the process crashes before the signal is
> persisted, and the workflow resumes after `entry_version` changes, no persisted
> token exists to win and the fallback recomputes from a different
> `parent_idempotency_key` (`workflow_driver.py:3312-3316`). It therefore emits Y,
> defeating the stated mint-to-persist crash fallback and producing the ghost
> request and pause-view mismatch this mechanism is intended to prevent. **The
> broader follow-up registration does not close this B-71 window**; exclude
> `entry_version` from the seed or land an enforced guard with this mechanism.
