# U-1 (B-18) cache_control breakpoint — slice-1 design (council-converged, 2026-07-09)

*Design output of the U-1 council pass (`u1-frozen-tools-council-design` workflow: C4 tools + C2 caching + C6 epoch; the architect-synthesis node failed transiently ×2 so this is the main-agent synthesis of the 3 converged facets). ADR-D3 §1.5 "prompt-cache breakpoint placement contract". Ready to implement — no operator gate on slice 1 (the paid live-cache-hit proof is the only gate, deferred to an e2e).*

## The convergent finding (C4 + C2, decorrelated agreement)

**Slice 1 = a TOOLS-block `cache_control` breakpoint, NOT system-prompt.** The tools array is *already* a list (`payload.tools: tuple[Mapping,...]`), so a marker on its last block needs **zero structured-system change** — it does **not** depend on runtime-spec OQ-1 (which defers the `system`-array form). It is exactly the operator's "frozen-tools-first" choice, and at MVP (`active_system_prompt=None`) the tool superset is the *only* non-empty prefix, so it is the sound non-vacuous cut.

## Slice-1 implementation (mirror the landed `active_system_prompt` pattern)

1. **Dispatcher field.** Add `frozen_tool_superset: tuple[Mapping[str, Any], ...] | None = None` on `RuntimeLLMDispatcher` (`llm_dispatch.py`, sibling to `active_system_prompt:533`). `None` → byte-identical legacy path (the local-first default; frozen dataclass preserved).
2. **Stage-5 computation.** In `materialize_runtime_tool_dispatcher_stage` (`bootstrap/factories/runtime_tool_dispatcher_factory.py:301`): compute the superset = **deterministically-ordered** (sort by tool name; JCS-canonical `input_schema`, reusing U-IS-08/U-AS-25 canonical-serialization machinery) union of every `ctx.mcp_client_hosts[*].tool_registry` contract projected to Anthropic `{name, description, input_schema}`, **plus** the memory-tool def when applicable (`step_has_memory_tool` / `memory_tool_registry`). Empty union → `None` (no MCP tools at MVP → dormant, correct). **Deterministic order is load-bearing:** nondeterministic order is a SILENT cache miss (cost regression), forbidden by no-silent-failure.
3. **Emission (translate-time only, ADR-F1-faithful).** In `_payload_to_anthropic_kwargs` (`:1670`): when `frozen_tool_superset` is set, `kwargs["tools"] = <superset>` (replacing `payload.tools`) and attach `{"cache_control": {"type": "ephemeral", "ttl": "5m"}}` to the **last** tool dict. **Skip when extended-thinking mode is set** (`thinking_mode` at :1620 — §1.5 extended-thinking-invalidates clause, handled at the epoch layer). OpenAI/Ollama translators **untouched**. `ProviderAgnosticPayload` stays frozen.
4. **Non-vacuity gate.** Only emit the breakpoint when the superset clears Anthropic's **≥4096-tok minimum cacheable prefix** (max model minimum in the epoch's routing set). Below floor → no marker (built-but-vacuous otherwise). Below-floor is a legitimate skip (dormant, like the observation half).
5. **Per-step decoupling.** The Anthropic branch always sends the full frozen superset (stable prefix); per-step tool STEERING rides `tool_choice` (invalidates messages-cache only — verified via claude-api skill § Invalidation hierarchy); per-step ENFORCEMENT stays at the landed `RuntimeToolDispatcher` gate (trust/sandbox/effect_fence, C10-owned). The wire `tools[]` must be the COMPLETE union (a per-step tool absent from the frozen set busts the cache).

## Witness (corrected — the "free emit→observe" is WRONG)

Both voices caught this: the built observation extractor `_extract_anthropic_cache_request_attrs` (`:327-370`) scans `payload.MESSAGES` only → it **structurally cannot witness a tools-block breakpoint**. So:
- **Offline (provider-free lane, in the arc):** assert `cache_control` on `kwargs["tools"][-1]` + **prefix byte-stability** across two dispatches in one epoch (`json.dumps(sorted...)` equality). This is the load-bearing "actually caches something" proof.
- **Live (`@pytest.mark.e2e`, credential-gated):** two identical-prefix dispatches → call 1 `usage.cache_creation_input_tokens > 0`, call 2 `usage.cache_read_input_tokens > 0` (`:1935-1936`). **This is a PAID Anthropic call → the one operator gate: build + mark e2e (kept out of provider-free lanes), surface at the paid-call boundary, do NOT auto-fire.**
- Optional small improvement: extend `_extract_anthropic_cache_request_attrs` to also scan the tools block, restoring an emit→observe path.

## Spec amendment (bundled-absorption arc + clearance marker)

Runtime spec: add the `frozen_tool_superset` dispatcher field + tools-block `cache_control` emission to the C-RT dispatcher contract (mirroring how `active_system_prompt` was added at R-PM-1). **No OQ-1 un-defer needed** (tools already a list). Clearance marker (DESIGN_IMPL_MIX exempt).

## Registered follow-on slices (do NOT fold into slice 1)

- **Slice 2:** resolve runtime-spec OQ-1 → promote `system` to a content-block array → extend the breakpoint to the full §1.5 parent position `[tools + system + template]`.
- **Slice 3:** `sub_agent_breakpoint` for orchestrator-workers/parallelization/EO cells (§1.5 second block, `frozen_tool_superset_per_privilege_tier`) + the cacheable-epoch primitive (workload-class × prompt-version-major, C6) + ADR-D4 §1.8 pre-warm/keep-alive.

## Epoch note (C6, for slices 2-3)

Anthropic caches are **model-scoped** (model-switch invalidates all), so the superset cache is inherently per-model; the explicit cacheable-epoch primitive (workload-class × prompt-version-major, ttl 5min/1hr per Persona §6 cost-ceiling) is a slice-3 concern. Slice 1 needs only: skip extended-thinking + send the stable superset per model.
