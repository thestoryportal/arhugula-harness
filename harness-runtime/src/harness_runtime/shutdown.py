"""`harness_runtime.shutdown` — shutdown primitives (U-RT-45 lands flush; U-RT-46 lands close).

Per `Spec_Harness_Runtime_v1.md` v1.1 §10 (C-RT-10 — shutdown sequence contract).

**U-RT-45 scope.** Land `flush_observability(ctx, *, timeout_millis)` —
step 2 of the C-RT-10 sequence. NOT the full `shutdown()` orchestrator
(U-RT-46) and NOT the close-resources steps 3-5 (U-RT-46). One-step-per-unit
discipline mirrors U-RT-43's 9-stage modular split.

**Flush surfaces.** C-RT-10 step 2 commits 4 surfaces:

1. **`tracer_provider.force_flush(timeout_millis)`** — actual work. OTel SDK's
   `TracerProvider.force_flush` is synchronous and returns `bool`; we wrap
   it in `asyncio.to_thread` so the bounded-wait discipline survives (the
   call can block for up to `timeout_millis` per OTel docs).

2. **Ledger fsync** — actual work. The IS state-ledger writer closes its
   file handle after every append (`with handle.canonical_path.open("a")
   as fh`); at flush time we open the path RO, `os.fsync(fd)`, close.
   The directory entry's durability is **deferred to implementation
   discretion** (production-grade `fsync(dir_fd)` + macOS `F_FULLFSYNC`
   not required at Track A).

3. **Cost-attribution chain flush** — no-op. U-RT-31 landed
   `RuntimeCostAttributionChain` as stateless-by-design (every step is a
   pure OD function). Class 3 drift filed at
   `.harness/class_3_drift_u_rt_45_cost_chain_stateless.md`. Reported as
   `FlushReport.cost_chain_noop = True`.

4. **Audit-writer flush** — implicit. `RuntimeAuditLedgerWriter.append`
   routes immediately through `LedgerWriter.append` (U-RT-32). The ledger
   fsync at surface (2) discharges audit-writer durability.

**Per-resource exception isolation.** Per C-RT-10 invariant ("Resources
that fail to close cleanly are surfaced individually; shutdown does not
abort on first failure"), each flush is gated by its own try/except. A
failure of one resource is recorded in `FlushReport.failures` and the
other resources still flush.

**Idempotency.** Calling `flush_observability(ctx)` twice is safe — both
surfaces (tracer + ledger fsync) are idempotent at the underlying primitive
level. U-RT-46's `shutdown()` orchestrator adds an explicit `AlreadyShutDown`
guard once the close-resources steps land.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from typing import TYPE_CHECKING, cast

from pydantic import BaseModel, ConfigDict

from harness_runtime.lifecycle.state_ledger import LedgerWriter as _ConcreteLedgerWriter

if TYPE_CHECKING:
    from harness_runtime.types import HarnessContext

__all__ = [
    "FlushReport",
    "FlushTimeoutError",
    "flush_observability",
]


# ---------------------------------------------------------------------------
# Typed surfaces.
# ---------------------------------------------------------------------------


class FlushTimeoutError(TimeoutError):
    """`RT-FAIL-FLUSH-TIMEOUT` — `flush_observability` exceeded the bounded wait.

    Subclasses `TimeoutError` so generic timeout handlers catch it.
    `flush_observability` itself does NOT raise this — the timeout is
    surfaced via `FlushReport.timed_out = True` (per C-RT-10 invariant:
    failures are reported, not abort-on-first). The typed surface exists
    for upstream callers that want to elevate the report to a raise.
    """


class FlushReport(BaseModel):
    """Result of a `flush_observability(ctx)` call.

    Frozen Pydantic; consumed by U-RT-46's `shutdown()` orchestrator to
    populate the outer `ShutdownReport` per C-RT-10 fail-class taxonomy.
    """

    model_config = ConfigDict(frozen=True)

    tracer_flushed: bool
    """`True` iff `tracer_provider.force_flush(timeout_millis)` returned `True`."""

    ledger_fsynced: bool
    """`True` iff `os.fsync` on the ledger path succeeded."""

    cost_chain_noop: bool
    """Always `True` at HEAD — the cost chain is stateless-by-design (U-RT-31).
    Spec §10 step 2 over-specification per
    `.harness/class_3_drift_u_rt_45_cost_chain_stateless.md`."""

    timed_out: bool
    """`True` iff any sub-flush exceeded `timeout_millis` (tracer reports
    `False` on internal timeout; we surface the same signal up)."""

    failures: tuple[str, ...]
    """Per-resource failure tags: subset of `('tracer', 'ledger')`."""


# ---------------------------------------------------------------------------
# Flush primitive.
# ---------------------------------------------------------------------------


async def flush_observability(
    ctx: HarnessContext,
    *,
    timeout_millis: int = 30_000,
) -> FlushReport:
    """Flush observability state per C-RT-10 step 2.

    1. `tracer_provider.force_flush(timeout_millis)` — dispatched to a
       thread so a slow flush doesn't block the loop.
    2. `os.fsync` on `ctx.ledger_writer.handle.canonical_path` — opens RO,
       fsyncs, closes.
    3. Cost-attribution chain — no-op (stateless-by-design; Class 3 drift).
    4. Audit writer — covered by (2) (append-through to ledger).

    Per-resource exceptions are caught and reported in `FlushReport.failures`;
    the function does not raise. Callers wanting hard-fail semantics inspect
    `FlushReport.failures` and `FlushReport.timed_out`.

    Parameters
    ----------
    ctx :
        Post-bootstrap `HarnessContext` from a `run()` invocation.
    timeout_millis :
        Bounded wait for the tracer flush. Per spec §10 deferred-to-discretion,
        the default at this primitive level is the OTel default (30,000 ms);
        the U-RT-46 `shutdown()` orchestrator will surface a top-level
        `timeout: float = 30.0` parameter and pass through `int(timeout * 1000)`.

    Returns
    -------
    FlushReport
        Per-surface status. Caller decides escalation policy.
    """
    failures: list[str] = []
    tracer_flushed = False
    ledger_fsynced = False
    timed_out = False

    # Surface 1: tracer BSP force_flush. OTel's `force_flush` is sync and
    # returns False on internal timeout; we treat that as `timed_out=True`.
    try:
        # `ctx.tracer_provider` is typed `object` at the schema level
        # (C-RT-04 informational typing) but concretely is the OTel SDK
        # `TracerProvider` set by stage 4 (`ctx.tracer_provider = tracer.provider`).
        # Cast at call site; no schema commitment beyond duck-typing
        # `.force_flush(timeout_millis: int) -> bool`.
        force_flush = cast(
            Callable[[int], bool],
            ctx.tracer_provider.force_flush,  # type: ignore[attr-defined]
        )
        result = await asyncio.to_thread(force_flush, timeout_millis)
        tracer_flushed = bool(result)
        if not tracer_flushed:
            timed_out = True
    except Exception:
        failures.append("tracer")

    # Surface 2: ledger fsync. Open RO, fsync the fd, close. Per Track A
    # discretion, dir-fsync + F_FULLFSYNC deferred.
    #
    # `ctx.ledger_writer` is typed as the `types.LedgerWriter` Protocol
    # (attribute-less); the concrete at runtime is
    # `harness_runtime.lifecycle.state_ledger.LedgerWriter` (dataclass with
    # `handle: JsonlLedgerHandle`). Cast to the concrete to read
    # `handle.canonical_path`.
    try:
        ledger = cast(_ConcreteLedgerWriter, ctx.ledger_writer)
        ledger_path = ledger.handle.canonical_path
        # Read-only fd is sufficient — fsync flushes the file's write-back
        # buffer via the inode regardless of access mode.
        fd = os.open(str(ledger_path), os.O_RDONLY)
        try:
            os.fsync(fd)
            ledger_fsynced = True
        finally:
            os.close(fd)
    except Exception:
        failures.append("ledger")

    # Surface 3: cost-chain. Stateless-by-design (U-RT-31) → no-op.
    # Surface 4: audit-writer. Append-through to ledger → covered by (2).

    return FlushReport(
        tracer_flushed=tracer_flushed,
        ledger_fsynced=ledger_fsynced,
        cost_chain_noop=True,
        timed_out=timed_out,
        failures=tuple(failures),
    )
