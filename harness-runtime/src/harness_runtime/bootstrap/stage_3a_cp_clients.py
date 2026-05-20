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

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.providers import materialize_provider_clients_stage
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate stage 3a CP_CLIENTS fields on `ctx`."""
    _ = workload_class
    assert ctx.keyring_resolver is not None, "stage 0 must construct ctx.keyring_resolver"

    stage = await materialize_provider_clients_stage(config, ctx.keyring_resolver)
    ctx.providers = dict(stage.providers)
