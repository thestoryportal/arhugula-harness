# U-1 slice 3 — design findings + F1 (a verified latent C10 gap in merged slice 1)

*Output of the U-1 slice-3 council design pass (2026-07-09). The pass lost 3/4 nodes to transient API stalls (C2 epoch, C4 partition, architect synthesis); C1 (orchestration) completed and surfaced a load-bearing finding I then verified by hand.*

## F1 — verified latent C10 condition-2 gap shipped in slice 1 (PR #919)

**Finding.** The slice-1 C10 blast-radius verdict (`.harness/u1-slice1-c10-blast-radius-verdict.md`) accepted Option A (full frozen tool superset visible per step) at **single-privilege-tier top-level dispatch**, under conditions — notably **condition 2: sub-agent / downgraded dispatchers stay `frozen_tool_superset = None` → fall back to `payload.tools`.** That guard was **assumed but never built.**

**Verified mechanism (re-grounded, not the subagent's summary):**
- `child_workflow_runner.py:10 / :126 / :130 / :221` — the child workflow **shares the parent `HarnessContext`** and **reuses the parent's `ctx.step_dispatchers`** (v1.6 MVP).
- `ctx.step_dispatchers` includes the parent `RuntimeLLMDispatcher` (the `ctx.llm_dispatcher` used for `INFERENCE_STEP` per `sub_agent_dispatch.py:42`), which has `frozen_tool_superset` bound at stage 5 (`stage_5_loop_init.py:307,352`).
- Therefore a **sub-agent (child-workflow) inference step emits the PARENT's frozen tool superset** — the child's Anthropic `tools[]` = the parent's full superset (with the breakpoint), not the child's downgraded set.

**Severity: LATENT + bounded.**
- At MVP, `compute_frozen_tool_superset` returns `None` (no MCP tools → empty union → `None` → the child short-circuits to `payload.tools`). **No leak at MVP.**
- **Visibility-only, execution intact:** the `RuntimeToolDispatcher` registry/trust/sandbox/effect-fence gate is unchanged — a downgraded sub-agent still cannot EXECUTE a removed tool; it merely SEES it in its inference context.
- It manifests only with **MCP tools configured AND privilege-tiered sub-agents** (a downgraded child seeing the parent's removed tools — undercutting the ADR-D4 §1.5 REMOVE-downgrade intent).

**Disposition: fold the fix into slice 3a (its proper home).** Slice 3a builds the child-scoped downgraded superset (below), which inherently closes F1 (the child computes its own superset from its own downgraded registry). An **interim minimal guard** (a child/sub-agent-originated dispatch skips the frozen-superset emit → falls back to `payload.tools`) is the honest floor if slice 3a is deferred. Not a hotfix emergency (latent + execution-gated + `None` at MVP), but a real condition-2 gap that must be closed before privilege-tiered-sub-agents + MCP-tools ship together. **Needs a C10 re-confirmation** that the child-scoped-superset + guard satisfies conditions 1/2.

## Slice-3 design (C1 completed; C2/C4/synthesis pending a re-run)

Slice 3 = the three ADR-D3 §1.5 / ADR-D4 §1.8 parts. C1's grounded decomposition:

**3a — sub_agent_breakpoint + close F1 (part a):**
1. Build `sub_agent_tool_registry(parent_hosts, blast_radius) → downgraded_hosts` — the ADR-D4 §1.5 **REMOVE** half (external-irreversible tools omitted from the child registry union). A committed contract with **no code** today → under FULL-SPEC a BUILD arc (not a fork).
2. Give the child its own child-scoped `frozen_tool_superset = compute_frozen_tool_superset(downgraded_hosts, ...)` (reuse the existing fn unchanged — it already derives from the passed registry). Witness by execution: a child whose parent registry has an external-irreversible tool T dispatches an inference step whose wire `tools[]` does NOT contain T; two children at different tiers get DIFFERENT supersets (the partition partitions — non-vacuous).
3. Enforce the F1 guard in the SAME slice (the fail-safe floor).

**3b — cacheable-epoch primitive (part b, C2 node FAILED — needs re-run):** workload-class × prompt-version-MAJOR. Today only a per-`(role,workload)` `version_sha` exists (a full hash; NO "major version"). Design the epoch keying + lifecycle (ttl 5min / 1hr per Persona §6) + invalidation semantics. **Design incomplete** — re-run C2.

**3c — ADR-D4 §1.8 concurrent-cache pre-warm (part c):** scope to PARALLELIZATION first (homogeneous, single epoch group — unambiguously non-vacuous). At the fan-out pre-flight (`workflow_driver.py` ~7053-7064), dispatch `branch[0]` to completion, then release `branch[1..N-1]` via the existing barrier. Witness with a fake Anthropic client counting cache-writes vs reads: serialized = 1 write + (N-1) hits; baseline = N writes (the miss storm). Register orchestrator-workers (epoch-grouped warm-up) + first-token signal + EO-multi-evaluator as forward arcs.

**Operator gates: NONE** (C1). All reversible in-repo architecture. Two items to SURFACE (not gate): the C10 re-confirmation, and the `sub_agent_tool_registry` REMOVE build (committed-but-unbuilt → FULL-SPEC build arc).

## Recommended next (for a fresh slice-3 arc)
1. Re-run the slice-3 design (C2 epoch + C4 partition + synthesis — the failed nodes) OR design them directly.
2. Build **3a** first (it closes F1 — the safety priority) with a C10 re-confirmation.
3. Then 3b (epoch) + 3c (PARALLELIZATION warm-up), each with its by-execution witness.
