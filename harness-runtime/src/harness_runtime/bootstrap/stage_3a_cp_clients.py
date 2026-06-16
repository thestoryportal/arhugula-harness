"""Stage 3a CP_CLIENTS — provider SDK construction (Anthropic / OpenAI / Ollama).

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 3a post-conditions:
`ctx.providers: dict[str, ProviderClient]` has entries for `anthropic`,
`openai`, `ollama` per spec C-RT-04 line 283; each client passes an async
ping. `ollama_optional=True` permits a 2-provider stage on Ollama
unreachability (degraded; warning surfaced via the provider composer).

The composer (`materialize_provider_clients_stage`) is the only stage entry
point in the runtime that performs network I/O at bootstrap time. The
composer handles its own bounded retry per C-RT-05; this stage shim is
purely the orchestrator binding.
"""

from __future__ import annotations

from harness_core.workload_class import WorkloadClass

from harness_runtime.bootstrap.factories.mcp_client_host_factory import (
    materialize_mcp_client_host_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.providers import materialize_provider_clients_stage
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate stage 3a CP_CLIENTS fields on `ctx`.

    Per spec v1.16 §14.9.3 stage 3a post-conditions: provider clients
    constructed (existing) + `mcp_client_hosts` materialized via the new
    factory (U-RT-73/126). Both bind onto the mutable context for stage 7
    freeze.
    """
    _ = workload_class
    assert ctx.keyring_resolver is not None, "stage 0 must construct ctx.keyring_resolver"

    # Runtime spec v1.47 §2.1: provider construction is conditional on the
    # workflow being inference-bearing. A tool-only (non-inference) workflow
    # needs NO provider, so stage 3a skips construction entirely — no
    # network/keyring work, and no per-provider construction failure (missing
    # secret / unreachable / auth) can abort the bootstrap, regardless of the
    # `*_optional` flags. `ctx.providers` stays empty; stage 5 binds the
    # fail-loud sentinel as the LLM-dispatch core + omits the INFERENCE_STEP /
    # SUB_AGENT_DISPATCH registry rows. Inference-bearing workflows take the
    # unchanged ≥1-provider path (C9 fail-fast preserved).
    if ctx.requires_inference:
        stage = await materialize_provider_clients_stage(config, ctx.keyring_resolver)
        ctx.providers = dict(stage.providers)
    else:
        ctx.providers = {}

    # U-RT-73/126: stage 3a now also materializes the H_T-as-MCP-client hosts
    # (a `dict[ServerName, MCPClientHost]` keyed on each host's `server_name`).
    ctx.mcp_client_hosts = await materialize_mcp_client_host_stage(config)

    # spec v1.41 §14.9.8 arc (Gap B): start each host HERE per §14.9.3 stage-3a
    # ("subprocess spawn + protocol handshake + list_tools registry population
    # happen here") + §14.9.6 inv 1 ("each configured host started exactly
    # once"). Without this the registry is empty and a TOOL_STEP raises
    # RT-FAIL-TOOL-CONTRACT-UNKNOWN at dispatch step 1. Guarded on a configured
    # server: the empty-sentinel host (0 servers) is intentionally never started.
    # `start()` failure raises MCPHostStartupError (RT-FAIL-MCP-HOST-STARTUP) →
    # propagates to the bootstrap orchestrator → fail-closed abort per ADR-F4
    # v1.1 §Consequences (c). (B2-impl-2a: single host today; multi-host
    # materialization is U-RT-126-full / B2-impl-2b.)
    if config.mcp_clients:
        for host in ctx.mcp_client_hosts.values():
            await host.start()
