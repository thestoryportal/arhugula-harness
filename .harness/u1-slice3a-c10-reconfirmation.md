# U-1 slice 3a — C10 blast-radius re-confirmation (child-scoped downgraded superset)

*Companion to `.harness/u1-slice1-c10-blast-radius-verdict.md` (the slice-1 verdict) and `.harness/u1-slice3-findings-and-f1-c10-gap.md` (the F1 finding). Filed with the slice-3a build (runtime spec v1.96 + CP spec v1.86). The finding required "a C10 re-confirmation that the child-scoped-superset + guard satisfies conditions 1/2." This is a **verification**, not an open fork — the design was settled by C1's slice-3 decomposition; the blast-radius position is named below.*

## The two conditions from the slice-1 C10 verdict

The slice-1 verdict accepted **Option A** (the full frozen tool superset visible per step, visibility-only, execution registry-gated) at single-privilege-tier **top-level** dispatch, UNDER two conditions:

- **Condition 1** — top-level, single-privilege-tier dispatch sees the full superset. *(Acceptable: no committed least-privilege-*visibility* contract; execution stays gated.)*
- **Condition 2** — sub-agent / downgraded dispatchers do NOT see the parent's full superset (they fall back or downgrade). *(This guard was assumed but never built — the F1 gap.)*

## Re-confirmation

**Condition 1 — UNCHANGED.** A top-level dispatch (`step_context.sub_agent_descent = False`, the `api.run` default) selects `frozen_tool_superset` exactly as slice 1/2. Byte-identical; no change to the top-level blast-radius position the slice-1 verdict already cleared.

**Condition 2 — NOW MATERIALIZED.** A descended sub-agent inference (`sub_agent_descent = True`) selects `child_frozen_tool_superset` = the parent union with **`EXTERNAL_IRREVERSIBLE` tools REMOVE'd** (ADR-D4 §1.5). The blast-radius argument:

1. **Monotone reduction.** The child superset is a strict SUBSET of the parent superset (the REMOVE filter can only DROP tools, never add). So a descended child's tool *visibility* is ≤ the parent's — the downgrade cannot INCREASE blast radius at any depth. Monotonic-sticky descent (once descended, all deeper children stay descended) + idempotent REMOVE (a grandchild re-filtering an already-filtered union drops nothing more) means the reduction holds at every level.
2. **Empty case is strictly safest.** When the parent registry held ONLY external-irreversible tools (child union empty), the descended dispatch emits `tools: []` (no visible tools) — NEVER the `payload.tools` fallback (which could re-expose the removed tool a child step declares). This is the maximal downgrade, not a bypass (out-of-family Codex [P2], fixed + regression-tested).
3. **Execution gating untouched.** The downgrade is **visibility-only**. The `RuntimeToolDispatcher` registry / per-server-trust / sandbox-tier / effect-fence gates are unchanged — a descended child still cannot EXECUTE a removed tool (it never could), and now also cannot SEE it. No execution-path change.
4. **Uniform (not tier-graded).** Under the ADR-D4 §1.5 child ceiling (`compute_child_blast_radius_ceiling` → uniform `READ_ONLY`), the REMOVE-half is tier-uniform: every descended child at any tier drops the same `EXTERNAL_IRREVERSIBLE` set. So two descendants get the SAME downgraded superset — the honest witness is **parent-includes-T / child-excludes-T** (NOT "two-tier children differ", which would only hold for a tier-graded downgrade the REMOVE-half is not).

**Verdict: conditions 1 and 2 both satisfied; no blast-radius regression.** Condition 2's assumed-but-unbuilt guard is now a real, monotone, execution-gated visibility downgrade. The scope that remains explicitly out of slice 3a (registered follow-ons): the `DOWNGRADE_TO_ASK` half of §1.5 (external-reversible → gate-level `ask`, a HITL-gate concern, not visibility) and per-privilege-tier graded downgrade (slice 3's `frozen_tool_superset_per_privilege_tier`, beyond the uniform READ_ONLY ceiling).

## Residual noted

The wrapper-stack `step_context` propagation (facade → retry/breaker/fallback → HITL composer → bare dispatcher) is **grep-confirmed** — each wrapper forwards the identical `step_context` object unchanged to its inner (`sync_dispatcher_facade.py:204`, `retry_breaker_fallback.py:829`, `hitl_gate_composer.py:971`/`_dispatch_inner`), and production per-role routing already reads `step_context.agent_role` at the bare dispatcher through this exact stack (covered by passing tests). A full-bootstrap-with-MCP-echo end-to-end (a `SUB_AGENT_DISPATCH` step whose child INFERENCE asserts the wire `tools[]`) is the ideal witness but balloons; grep-confirmation is the proportionate close given the latent/None-at-MVP severity.
