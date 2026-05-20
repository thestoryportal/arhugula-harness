# Class 3 Drift — U-RT-45 cost-chain flush is a no-op against landed shape

**Class:** 3 (informational)
**Filed:** 2026-05-20 at U-RT-45 landing
**Surface:** `design-substrate/Spec_Harness_Runtime_v1.md` §10 (C-RT-10) step 2

## Drift

Spec §10 step 2 names four flush surfaces:

> **Flush observability state**: `await tracer_provider.force_flush(timeout_millis=...)`; sync ledger writers (`fsync` on `.harness/state.jsonl`); **flush cost-attribution chain in-memory state to audit ledger**.

The third surface ("flush cost-attribution chain in-memory state") presumes
the cost chain carries pending in-memory state. U-RT-31 landed
`RuntimeCostAttributionChain` as **stateless by design** (cost_attribution.py
docstring: "The chain is stateless — every step composes a pure OD function
or static table"). Every step (compute_per_attempt_cost, compose_total_cost,
attach_idempotency_key, rollup_fanout, dedupe_on_replay) is a pure function
over caller-supplied inputs.

At U-RT-45 the cost-chain "flush" is a documented no-op. `FlushReport.cost_chain_noop = True`.

## Resolution

**Spec revision pass owed** if a future cost-chain unit grows in-memory state
(no such unit is planned at HEAD). Until then, the U-RT-45 no-op + this
informational record + the inline comment in `harness_runtime/shutdown.py`
discharge the spec asymmetry.

Non-blocking; not a Class 1 because no AC fails at HEAD (the two materialized
flushes — tracer BSP + ledger fsync — fully satisfy both U-RT-45 ACs:
"all spans visible in collector sqlite" + "ledger chain head consistent").

## Provenance

- Spec source: `Spec_Harness_Runtime_v1.md` v1.1 §10 step 2
- Landed shape: `harness_runtime/lifecycle/cost_attribution.py` (U-RT-31, commit `1296aee`)
- Audit writer same shape: `harness_runtime/lifecycle/audit_writer.py` line 131 — `append` immediately routes through `ledger_writer.append`; no buffer.
