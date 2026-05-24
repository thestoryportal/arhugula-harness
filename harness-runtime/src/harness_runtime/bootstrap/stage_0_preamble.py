"""Stage 0 PREAMBLE — populate `ctx.config` + sub-config-derived resources.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 0 post-conditions:
`ctx.config: RuntimeConfig` populated; sub-configs (path bindings, secrets,
OTel, collector) materialized; `drained_flag: asyncio.Event` initialized.

Also constructs orchestrator-internal handles used downstream:
- `KeyringSecretResolver` for stage 3a provider construction.
- `Actor` for stage 1 state-ledger writer construction (runtime identity =
  `Actor(actor_class=AGENT, actor_id="harness-runtime")`; per
  `[[u-rt-43-implementation-plan]]` §10 — using AGENT avoids an IS spec
  change that would otherwise require adding a `RUNTIME` actor class).
"""

from __future__ import annotations

import asyncio

from harness_core.workload_class import WorkloadClass
from harness_is.state_ledger_entry_schema import Actor, ActorClass

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.config.provider_secrets import make_keyring_resolver
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate the stage 0 PREAMBLE fields on `ctx`."""
    _ = workload_class  # unused at stage 0; threaded for uniformity
    ctx.config = config
    ctx.drained_flag = asyncio.Event()
    # U-RT-87 — `pause_requested_flag` sibling-pattern to `drained_flag` per
    # runtime spec v1.21 §4 + §14.14.3. Caller-side pause-signaling primitive
    # consumed at workflow_driver per-step pre-entry detection.
    ctx.pause_requested_flag = asyncio.Event()
    ctx.keyring_resolver = make_keyring_resolver(config.provider_secrets)
    ctx.actor = Actor(actor_class=ActorClass.AGENT, actor_id="harness-runtime")
