# R-CXA-1 AS->IS Edge-Scope Audit — 2026-06-09

## Purpose

This audit closes `R-CXA-1` must_pass #2:

> remaining ~12 AS source-unit audit-emission callbacks threaded through AsIsWiring or narrowed/back-flowed by edge-scope audit

The audit uses current semantic-overlay output and runtime code grounding, not the older CXA prose count alone.

## Grounding

`just overlay-query --seam AS` at this branch's base surfaced the current direct AS->IS overlay edges:

| AS source | IS target(s) | Current shape | Runtime callback owed? |
|---|---|---|---|
| `U-AS-19` `sandbox_event_idempotency.py` | `U-IS-07`, `U-IS-12` | Reads/imports IS `Identifier` carrier discipline for idempotency-key construction. | No. Read-only carrier use, not a ledger emission. |
| `U-AS-26` `secret_fetch_audit.py` | `U-IS-07`, `U-IS-09`, `U-IS-10` | Composes secret-fetch audit entries and uses IS chain helpers/types. | Yes, via the paired `U-AS-27 -> U-IS-11` write delegation at `RuntimeAsIsWiring`. |
| `U-AS-28` `anthropic_primitive_adoption.py` | `U-IS-01`, `U-IS-02` | Reads/imports IS path-class registry carriers. | No. Read-only carrier use, not a ledger emission. |

`just overlay-query --contract C-AS-08` identifies the secret-fetch AS files plus the runtime carrier `harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py`. `just overlay-query --file harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py` grounds the runtime seam at `C-AS-08`, `C-IS-05`, `C-IS-06`, `C-IS-07`, and `C-RT-12`.

## Resolution

The legacy "13 edges / remaining ~12 callbacks" wording is stale at current HEAD. The current direct AS->IS overlay inventory does not expose twelve unthreaded AS audit-emission callback sites. It exposes:

- Two AS source units with direct read-only IS carrier imports (`U-AS-19`, `U-AS-28`).
- One AS secret-fetch audit producer family (`U-AS-26` compose + `U-AS-27` durable write delegation) requiring runtime callback wiring.

PR #458 closed must_pass #1 by moving scoped secret-fetch audit production to the active `TOOL_STEP` dispatch site. This arc closes the remaining runtime write edge by threading the R-003 procedural-tier snapshot resolver into that production AS->IS callback:

- `RuntimeToolDispatcher` already emits `SecretFetchEvent` with workflow and step identity.
- Stage 5 now binds `ctx.procedural_tier_snapshot_resolver` before constructing the TOOL_STEP dispatcher.
- `RuntimeAsIsWiring.emit_secret_fetch_audit_entry(...)` now writes `EntryPayload.procedural_tier_snapshot_ref` when a resolver is bound.
- Direct/bootstrap/test AS->IS wiring without a resolver remains `None`-canonical.

## Verification

Focused runtime coverage proves both sides of the resolution:

- `test_emit_leaves_procedural_tier_snapshot_ref_none_without_resolver`
- `test_emit_populates_procedural_tier_snapshot_ref_when_resolver_bound`
- `test_factory_threads_procedural_snapshot_resolver_to_secret_audit_emitter`

Focused command:

```text
uv run pytest harness-runtime/tests/test_lifecycle_as_is_wiring.py harness-runtime/tests/test_u_rt_75_runtime_tool_dispatcher_factory.py harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py -q
```

Result: `47 passed`.

## Non-Goals

- No bootstrap-value secret fetch wiring. The Reading-D exclusion remains intact.
- No invented AS callback surfaces for read-only IS carrier imports.
- No design-substrate amendment in this implementation/accounting arc.
- No live provider or paid API call.
