"""`harness_runtime.shutdown` — shutdown primitives (U-RT-45 lands flush; U-RT-46 lands close).

Per `Spec_Harness_Runtime_v1.md` v1.1 §10 (C-RT-10 — shutdown sequence contract).

**U-RT-45 scope.** Land `flush_observability(ctx, *, timeout_millis)` —
step 2 of the C-RT-10 sequence. NOT the full `shutdown()` orchestrator
(U-RT-46) and NOT the close-resources steps 3-5 (U-RT-46). One-step-per-unit
discipline mirrors U-RT-43's 9-stage modular split.

**Flush surfaces.** C-RT-10 step 2 commits 4 surfaces:

1. **`tracer_provider.force_flush(timeout_millis)`** — actual work. OTel SDK's
   `TracerProvider.force_flush` is synchronous and returns `bool`; we run
   it on a bounded DAEMON worker (`_run_blocking_bounded`) so the bounded-wait
   discipline survives (the call can block for up to `timeout_millis` per
   OTel docs) — NOT `asyncio.to_thread` (B-147): a timed-out workflow worker
   spawned by `asyncio.to_thread` from `harness_runtime.api.run` can still
   occupy the loop's default executor when shutdown begins, so a to_thread
   submission queues without starting and the deadline expires unobserved
   (no `ShutdownReport` ever returned; reproduced at PR #1290 merge-gate
   Lens 1 with a real saturated executor).

2. **Ledger fsync** — actual work. The IS state-ledger writer closes its
   file handle after every append (`with handle.canonical_path.open("a")
   as fh`); at flush time we open the path RO, `os.fsync(fd)`, close.
   macOS `F_FULLFSYNC` remains **deferred to implementation discretion**
   (Track A); the shared parent directory's entry durability is covered by
   the sidecar surface's dir-fsync (surface 4).

3. **Cost-attribution chain flush** — no-op. U-RT-31 landed
   `RuntimeCostAttributionChain` as stateless-by-design (every step is a
   pure OD function). Class 3 drift filed at
   `.harness/class_3_drift_u_rt_45_cost_chain_stateless.md`. Reported as
   `FlushReport.cost_chain_noop = True`.

4. **Audit-writer flush** — the IS refs append through `LedgerWriter.append`
   (U-RT-32, covered by surface 2), and the FULL signed entries live in the
   B-47 item-(e) sidecar — fsynced FIRST (file, then parent directory for
   directory-entry durability, then the ledger; mirrors the sidecar-first
   write ordering so power loss cannot leave a flushed ref whose signature
   or very filename was still buffered).

**Per-resource exception isolation.** Per C-RT-10 invariant ("Resources
that fail to close cleanly are surfaced individually; shutdown does not
abort on first failure"), each flush is gated by its own try/except. A
failure of one resource is recorded in `FlushReport.failures` and the
other resources still flush.

**Idempotency.** Calling `flush_observability(ctx)` twice is safe — both
surfaces (tracer + ledger fsync) are idempotent at the underlying primitive
level. `shutdown()` (U-RT-46) keeps a per-context cached report and returns
it on second invocation; `ShutdownReport.already_shutdown` carries the
distinguishing signal.

**U-RT-46 `shutdown()` orchestrator** lands the full C-RT-10 reverse-stage
close sequence. Step 1 drain sets `ctx.drained_flag` (in-flight wait STRUCK
per `[[fork-u-rt-44-workflow-loop-drain]]`); step 1b drains the stage-5
sub-agent-dispatch executor (B-48 U-RT-141) — BEFORE the observability
flush, so a job still finishing during the drain gets its spans/audit
entries written before the tracer/exporters close (codex round-4 [P1]);
step 2 delegates to `flush_observability` above; step 3 closes the
collector daemon, tracer provider (sync API wrapped in `asyncio.to_thread`),
and every provider client; steps 4-5 are no-ops at HEAD per the
close-surface map (MCP clients/host are placeholders per U-RT-22;
index/cache have no close surface; worktree leases none-allocated until
U-RT-49+); step 6 reads the audit-ledger head hash for consistency
verification. Per-resource exception isolation; budgeted-remaining timeout
pattern.
"""

from __future__ import annotations

import asyncio
import atexit
import functools
import os
import stat
import sys
import threading
import time
import weakref
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from weakref import WeakValueDictionary

from pydantic import BaseModel, ConfigDict

from harness_runtime.lifecycle.audit_offload import run_off_loop_detach_on_cancel

if TYPE_CHECKING:
    from harness_runtime.types import HarnessContext, ServerName

__all__ = [
    "AlreadyShutDown",
    "FlushReport",
    "FlushTimeoutError",
    "ShutdownReport",
    "ShutdownTimeout",
    "flush_observability",
    "shutdown",
]


# ---------------------------------------------------------------------------
# Blocking fsync halves — run in worker threads via `asyncio.to_thread`
# (codex round-47 P2: a stalled filesystem must not hang the event loop past
# the advertised timeout; `asyncio.wait_for` bounds the wait, the worker may
# linger on the stalled syscall while shutdown proceeds).
# ---------------------------------------------------------------------------


def _fsync_sidecar_sync(sidecar_path: Path) -> None:
    """Sidecar file + parent-dir fsync (blocking half).

    Non-blocking + regular-file check (round-35 codex): a pre-created FIFO
    here made a blocking O_RDONLY open hang the ENTIRE shutdown before any
    failure could be recorded. Mirrors the writer's validated-open
    discipline; a non-regular target is recorded as an audit_sidecar flush
    failure, never a hang. The parent-dir fsync (codex round-11, PR B1)
    covers directory-entry durability for NEWLY CREATED files — the flushed
    ledger ref must not outlive the sidecar's very filename. POSIX-only:
    directories are not open()-able on Windows, where cross-process
    durability already sits at the documented B-45 platform posture.
    """
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
    if sys.platform != "win32":
        flags |= os.O_NOFOLLOW
    fd = os.open(str(sidecar_path), flags)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError(f"sidecar {sidecar_path} is not a regular file")
        os.fsync(fd)
    finally:
        os.close(fd)
    if sys.platform != "win32":
        dir_fd = os.open(str(sidecar_path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)


def _sidecar_guard_and_fsync_sync(audit_writer: Any, sidecar_path: Path) -> None:
    """Deletion-after-use guard + sidecar fsync (blocking half).

    The refs predicate (`sidecar_expected`) reads and deserializes the
    ENTIRE IS ledger — codex round-3 P2 (B-47 PR B2a): sampled on the
    event loop it blocked shutdown outside the bounded worker on a large
    ledger. The whole guard now runs INSIDE the bounded worker with the
    race-safe refs-before-exists ordering preserved (merge-gate round-1
    concurrency lens: the reverse order let a first-ever audit append
    land file+ref between the samples and record a spurious loss).
    """
    sidecar_expected = getattr(audit_writer, "sidecar_expected", None)
    refs_existed = sidecar_expected() if sidecar_expected is not None else False
    if refs_existed and not sidecar_path.exists():
        raise ValueError(
            f"audit sidecar {sidecar_path} is missing but IS audit "
            f"references exist — signed history deleted or lost"
        )
    if sidecar_path.exists():
        _fsync_sidecar_sync(sidecar_path)


def _fsync_ledger_sync(ledger_path: Path) -> None:
    """Ledger fsync (blocking half). Read-only fd is sufficient — fsync
    flushes the file's write-back buffer via the inode regardless of access
    mode."""
    fd = os.open(str(ledger_path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


async def _run_blocking_bounded[T](
    fn: Callable[[], T], timeout_seconds: float, *, thread_name: str
) -> T:
    """Run a blocking callable on a DAEMON thread with a bounded await.

    NOT `asyncio.to_thread` (codex round-48 P1; B-147): to_thread uses the
    loop's default executor, so (a) a saturated executor queues the
    submission indefinitely BEFORE the callable's own internal timeout can
    start counting, and (b) the executor's worker threads `asyncio.run`'s
    teardown JOINS — a genuinely stalled call would still hang process exit
    AFTER the timeout report was returned, defeating the bound at the
    process level. A daemon thread starts immediately and is never joined;
    the stalled call lingers harmlessly until process end. Raises
    `TimeoutError` on expiry (via `asyncio.timeout` — expiry converts the
    internal CancelledError at the block boundary); relays the worker's
    exception on failure; returns the callable's value on success.
    """
    loop = asyncio.get_running_loop()
    done = asyncio.Event()
    outcome: list[T] = []
    failure: list[BaseException] = []

    def _worker() -> None:
        try:
            outcome.append(fn())
        except BaseException as exc:  # relayed to the awaiting side
            failure.append(exc)
        finally:
            try:
                loop.call_soon_threadsafe(done.set)
            except RuntimeError:
                # Loop already closed — the awaiting side reported its
                # timeout long ago and the process is exiting; nothing is
                # listening for this completion signal anymore.
                pass

    threading.Thread(target=_worker, daemon=True, name=thread_name).start()
    async with asyncio.timeout(timeout_seconds):
        await done.wait()
    if failure:
        raise failure[0]
    return outcome[0]


async def _run_fsync_bounded(
    fn: Callable[[Path], None], path: Path, timeout_seconds: float
) -> None:
    """Run a blocking fsync half on a DAEMON thread with a bounded await.

    Thin wrapper over `_run_blocking_bounded` (see its docstring for the
    daemon-thread rationale); kept as the fsync-shaped call surface.
    """
    await _run_blocking_bounded(
        functools.partial(fn, path), timeout_seconds, thread_name="harness-flush-fsync"
    )


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

# In-flight tracer force_flush workers, keyed by `id(ctx)` (codex round-2 P1
# + round-3 P1/P2, B-147). Each ctx maps to the SET of daemon flush workers
# that may still be running — a set, not a single slot, because a standalone
# `flush_observability()` timeout followed by `shutdown()`'s own step-2
# re-flush yields two concurrent workers, and the later one completing must
# not erase evidence of the earlier one still exporting. A worker's own
# finally discards its event (popping the key when the set empties); the
# tracer surface's failure path discards too, so a `Thread.start()` that
# never launched a worker cannot leave a stale entry. `shutdown()` step 3b
# consults this to preserve C-RT-10's flush-before-close order — the
# provider close is skipped (and reported) while ANY flush worker is still
# in flight. All access under `_inflight_lock` (registration racing a
# concurrent worker's empty-set pop could otherwise strand an add on an
# orphaned set). An eternally-stalled worker leaks one Event alongside its
# already-lingering daemon thread — same bounded cost.
_InflightEntry = tuple["weakref.ref[Any] | None", set[threading.Event]]
_inflight_tracer_flush: dict[int, _InflightEntry] = {}
_inflight_lock = threading.Lock()


def _try_weakref(ctx: object) -> weakref.ref[Any] | None:
    """Weak identity for the registry entry (codex round-4 P2: a bare
    `id()` key can be reused by a later context after gc, making it adopt an
    unrelated stalled worker and skip its own tracer close). Duck-typed test
    contexts (`SimpleNamespace`) are not weakref-able — fall back to
    id-only identity there."""
    try:
        return weakref.ref(ctx)
    except TypeError:
        return None


def _entry_is_stale(entry: _InflightEntry, ctx: object) -> bool:
    ref, _events = entry
    return ref is not None and ref() is not ctx


def _register_inflight_tracer_flush(ctx: object, evt: threading.Event) -> None:
    ctx_key = id(ctx)
    with _inflight_lock:
        entry = _inflight_tracer_flush.get(ctx_key)
        if entry is None or _entry_is_stale(entry, ctx):
            events: set[threading.Event] = set()
            entry = (_try_weakref(ctx), events)
            _inflight_tracer_flush[ctx_key] = entry
        entry[1].add(evt)


def _discard_inflight_tracer_flush(ctx_key: int, evt: threading.Event) -> None:
    with _inflight_lock:
        entry = _inflight_tracer_flush.get(ctx_key)
        if entry is not None:
            entry[1].discard(evt)
            if not entry[1]:
                _inflight_tracer_flush.pop(ctx_key, None)


def _spawn_deferred_tracer_close(ctx: object) -> None:
    """Best-effort deferred close (codex round-5 P1): a step-3b close skipped
    for an in-flight flush would otherwise NEVER happen — `shutdown()` caches
    its report and every later call returns the cache — leaving a long-lived
    process's tracer provider open forever. A daemon watcher (never joined)
    waits for every currently-registered flush worker to finish, then closes
    the provider; C-RT-10's flush-before-close order is preserved because
    the close strictly follows the last worker's completion signal. The
    close failure is deliberately swallowed: the returned report already
    tagged `tracer_provider`, and this runs long after that report was
    delivered — there is no caller left to surface to."""
    with _inflight_lock:
        entry = _inflight_tracer_flush.get(id(ctx))
        events: tuple[threading.Event, ...] = (
            tuple(entry[1]) if entry is not None and not _entry_is_stale(entry, ctx) else ()
        )
    provider = getattr(ctx, "tracer_provider", None)
    shutdown_fn = getattr(provider, "shutdown", None)
    if shutdown_fn is None:
        return
    # OTel's own atexit backstop (`shutdown_on_exit=True` at construction,
    # `lifecycle/tracer_provider.py`) fires at process exit WITHOUT waiting
    # for daemon threads — it would close the provider concurrently with the
    # still-live force_flush and recreate exactly the race this deferral
    # exists to prevent (codex round-6 P1). The runtime owns the close from
    # here — but never remove the LAST cleanup mechanism before its
    # replacement is known good (codex round-7 P2): an ORDERED backstop is
    # registered first (at exit it closes only when no flush worker remains
    # live — spans are lost either way in that case, but never raced), the
    # SDK backstop is unregistered second, and the ordered backstop is
    # removed only after the watcher's close succeeds. A watcher that never
    # launches (Thread.start failure under thread exhaustion) or whose close
    # raises leaves the ordered backstop registered for one exit-time retry.

    # One-shot coordination between the watcher and the exit-time backstop
    # (codex round-8 P2): process exit can begin just as the last flush
    # event sets, putting both paths inside `shutdown_fn()` concurrently.
    # The lock serializes them; `closed` flips only on a SUCCESSFUL close,
    # so a raised close still leaves the backstop retry meaningful.
    close_lock = threading.Lock()
    close_state = {"closed": False}

    def _close_once_serialized() -> bool:
        with close_lock:
            if close_state["closed"]:
                return True
            try:
                shutdown_fn()
            except Exception:
                return False
            close_state["closed"] = True
            return True

    def _ordered_backstop() -> None:
        if all(evt.is_set() for evt in events):
            _close_once_serialized()

    def _watcher() -> None:
        for evt in events:
            evt.wait()
        if _close_once_serialized():
            atexit.unregister(_ordered_backstop)
        # else: ordered backstop stays registered; retries at exit

    atexit.register(_ordered_backstop)
    atexit_handler = getattr(provider, "_atexit_handler", None)
    if atexit_handler is not None:
        atexit.unregister(atexit_handler)
    try:
        threading.Thread(target=_watcher, daemon=True, name="harness-deferred-tracer-close").start()
    except Exception:
        # Watcher never launched — the ordered backstop remains the closer.
        pass


def _tracer_flush_in_flight(ctx: object) -> bool:
    with _inflight_lock:
        entry = _inflight_tracer_flush.get(id(ctx))
        if entry is None:
            return False
        if _entry_is_stale(entry, ctx):
            # id reuse after gc — the stalled worker belonged to a dead
            # context; it must not veto THIS context's close.
            _inflight_tracer_flush.pop(id(ctx), None)
            return False
        return bool(entry[1])


async def flush_observability(
    ctx: HarnessContext,
    *,
    timeout_millis: int = 30_000,
) -> FlushReport:
    """Flush observability state per C-RT-10 step 2.

    1. `tracer_provider.force_flush(timeout_millis)` — dispatched to a
       bounded daemon worker so a slow flush doesn't block the loop and a
       saturated default executor can't queue it past the deadline (B-147).
    2. `os.fsync` on `ctx.ledger_writer.handle.canonical_path` — opens RO,
       fsyncs, closes.
    3. Cost-attribution chain — no-op (stateless-by-design; Class 3 drift).
    4. Audit writer — sidecar file + parent dir fsynced BEFORE (2); the
       IS refs themselves are covered by (2).

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
    # ONE shared budget across all flush surfaces (codex round-48 P2):
    # per-surface full timeouts let this coroutine consume ~3x the caller's
    # remaining budget sequentially, violating the advertised top-level
    # shutdown deadline even for finite stalls. The tracer's force_flush
    # bounds itself internally with the full value (first surface — the
    # full value IS the remaining budget at that point); each later surface
    # gets only what is left on this monotonic deadline.
    deadline = time.monotonic() + timeout_millis / 1000.0

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
        # Bounded daemon worker, NOT `asyncio.to_thread` (B-147): a
        # timed-out workflow worker (spawned by `asyncio.to_thread` from
        # `harness_runtime.api.run` — CPython cannot kill its thread) can
        # still occupy the loop default executor here, so a to_thread
        # submission queues without starting; OTel's own `timeout_millis`
        # begins mattering only AFTER the call starts. The outer
        # `asyncio.timeout` bounds submission + execution by the remaining
        # shared budget; on expiry the surface reports like the fsync
        # surfaces below ('tracer' tag + timed_out) and the daemon worker
        # lingers harmlessly (never joined at teardown).
        #
        # The lingering worker is TRACKED per-ctx (codex round-2 P1 +
        # round-3 P1/P2): a timed-out force_flush may still be exporting on
        # its daemon thread when `shutdown()` reaches step 3b, and closing
        # the provider then would overlap teardown with an in-flight export
        # — violating C-RT-10's flush-before-close order. Registration is a
        # per-ctx SET (concurrent workers from a standalone flush timeout +
        # shutdown's re-flush each keep their own entry); the worker's own
        # finally discards its entry, and the non-timeout failure path below
        # discards too so a `Thread.start()` that never launched a worker
        # cannot strand a stale entry. Step 3b consults the registry and
        # skips the close while any flush worker is in flight.
        # A prior force_flush worker for THIS ctx may still be blocked
        # (codex round-4 P2): spawning another permanent daemon thread per
        # call could exhaust native threads under retry loops, and a
        # provider whose flush is wedged will wedge the new worker too.
        # Spend the CURRENT budget waiting for the prior worker(s) to finish
        # (codex round-8 P2: a later shutdown with a fresh budget must not
        # instantly cache a false failure while the worker completes within
        # that budget) — thread-free poll; the registry self-cleans on
        # worker completion. Only on budget exhaustion is this surface
        # reported timed out without a duplicate worker; step 3b's
        # flush-before-close skip still holds via the surviving
        # registration.
        waited_for_prior = False
        while _tracer_flush_in_flight(ctx):
            waited_for_prior = True
            if time.monotonic() >= deadline:
                raise TimeoutError("prior tracer force_flush still in flight")
            await asyncio.sleep(0.01)
        # Round-9 P2: a prior worker clearing AT the deadline must not spawn
        # a fresh worker that then runs on the ORIGINAL full internal
        # timeout with a ~zero outer bound (it would linger and defer the
        # provider close for no observable benefit). Recheck the remaining
        # budget and shrink the internal bound to it. The no-wait path keeps
        # the full `timeout_millis` (first surface — the full value IS the
        # remaining budget there, and callers observe the exact value).
        surface_timeout_millis = timeout_millis
        if waited_for_prior:
            remaining_after_wait = max(0.0, deadline - time.monotonic())
            if remaining_after_wait <= 0.0:
                raise TimeoutError("prior tracer force_flush consumed the budget")
            surface_timeout_millis = min(timeout_millis, max(1, int(remaining_after_wait * 1000)))

        flush_done = threading.Event()
        ctx_key = id(ctx)
        _register_inflight_tracer_flush(ctx, flush_done)

        def _tracked_force_flush() -> bool:
            try:
                return force_flush(surface_timeout_millis)
            finally:
                flush_done.set()
                _discard_inflight_tracer_flush(ctx_key, flush_done)

        try:
            result = await _run_blocking_bounded(
                _tracked_force_flush,
                max(0.0, deadline - time.monotonic()),
                thread_name="harness-flush-tracer",
            )
        except (TimeoutError, asyncio.CancelledError):
            # Worker genuinely in flight — `Thread.start()` runs
            # synchronously before the first await point, so by the time a
            # timeout OR a caller cancellation lands here the worker exists
            # and may still be running (codex round-4 P1). Registration
            # stays; the worker's own finally clears it whenever it
            # completes.
            raise
        except BaseException:
            # The worker either never launched (`Thread.start()` failure —
            # nothing would ever clear the entry) or already finished by
            # raising (its finally cleared it; discard is then a no-op).
            _discard_inflight_tracer_flush(ctx_key, flush_done)
            raise
        tracer_flushed = bool(result)
        if not tracer_flushed:
            timed_out = True
    except TimeoutError:
        failures.append("tracer")
        timed_out = True
    except Exception:
        failures.append("tracer")

    # Sidecar fsync FIRST (mirrors the sidecar-first write ordering —
    # codex round-5 P2: power loss between the two fsyncs must not leave
    # a flushed ref whose signature was still buffered).
    # Audit-writer surface: The IS refs append through the ledger (covered
    # by surface 2), but the FULL signed entries live in the item-(e) sidecar
    # (B-47 PR B1) — a separate file whose write-back buffer surface-2's
    # fsync does not touch (out-of-family Codex round-4 finding: a clean
    # shutdown followed by power loss could keep the ref and lose the
    # signature). Fsync it when it exists; absent sidecar (no audit entry
    # ever appended, or a non-runtime writer) is a clean no-op.
    try:
        audit_writer = getattr(ctx, "audit_writer", None)
        sidecar_path = getattr(audit_writer, "sidecar_path", None)
        # Absent writer/attribute or genuinely-first-use sidecar = clean
        # no-op. A MISSING sidecar whose IS refs exist is deletion-after-use
        # (codex round-43) — recorded as an audit_sidecar failure via the
        # writer's own first-use authority, consistent with its
        # missing-sidecar guard.
        if sidecar_path is not None:
            # The guard (full-ledger refs scan) AND the fsync both run in
            # the bounded worker — neither touches the event loop (codex
            # rounds 47 P2 / round-3 P2).
            await _run_fsync_bounded(
                functools.partial(_sidecar_guard_and_fsync_sync, audit_writer),
                sidecar_path,
                max(0.0, deadline - time.monotonic()),
            )
    except TimeoutError:
        failures.append("audit_sidecar")
        timed_out = True
    except Exception:
        failures.append("audit_sidecar")

    # Surface 2: ledger fsync. Open RO, fsync the fd, close. Per Track A
    # discretion, dir-fsync + F_FULLFSYNC deferred.
    #
    # `ctx.ledger_writer` is typed as the `types.LedgerWriter` Protocol
    # (attribute-less); the concrete at runtime is
    # `harness_runtime.lifecycle.state_ledger.LedgerWriter` (dataclass with
    # `handle: JsonlLedgerHandle`). Cast to the concrete to read
    # `handle.canonical_path`.
    try:
        ledger = ctx.ledger_writer
        ledger_path = ledger.handle.canonical_path
        # Bounded daemon worker — same stalled-filesystem hang class as the
        # sidecar surface above (codex round-47 P2 + round-48 P1/P2).
        await _run_fsync_bounded(
            _fsync_ledger_sync,
            ledger_path,
            max(0.0, deadline - time.monotonic()),
        )
        ledger_fsynced = True
    except TimeoutError:
        failures.append("ledger")
        timed_out = True
    except Exception:
        failures.append("ledger")

    # Cost-chain surface: stateless-by-design (U-RT-31) → no-op.

    return FlushReport(
        tracer_flushed=tracer_flushed,
        ledger_fsynced=ledger_fsynced,
        cost_chain_noop=True,
        timed_out=timed_out,
        failures=tuple(failures),
    )


# ---------------------------------------------------------------------------
# U-RT-46 — shutdown() orchestrator (C-RT-10 full sequence).
# ---------------------------------------------------------------------------


class ShutdownTimeout(TimeoutError):  # noqa: N818 — domain-anchored name
    """`RT-FAIL-SHUTDOWN-TIMEOUT` — shutdown exceeded the bounded `timeout`.

    `shutdown()` itself does NOT raise this — the timeout is surfaced via
    `ShutdownReport.timed_out = True`. The typed surface is escalation
    primitive for callers that want to convert the report flag to a raise.
    Subclasses `TimeoutError` so generic handlers catch it.
    """


class AlreadyShutDown(Exception):  # noqa: N818 — domain-anchored name
    """`RT-FAIL-ALREADY-SHUTDOWN` — second `shutdown()` invocation on same context.

    Like `ShutdownTimeout`, NOT raised by `shutdown()` itself — the second
    call returns the cached `ShutdownReport` with `already_shutdown=True`.
    The typed surface is an escalation primitive for callers who want a
    raise.
    """


class ShutdownReport(BaseModel):
    """Result of a `shutdown(ctx)` call.

    Composes the inner `FlushReport` (step 2) with the per-resource close
    outcomes for steps 3-5 and the audit-ledger head-hash verification at
    step 6. Per C-RT-10 fail-class taxonomy:

    - `RT-FAIL-PARTIAL-SHUTDOWN` → `failures` non-empty, `timed_out=False`.
    - `RT-FAIL-SHUTDOWN-TIMEOUT` → `timed_out=True`.
    - `RT-FAIL-ALREADY-SHUTDOWN` → `already_shutdown=True`.
    """

    model_config = ConfigDict(frozen=True)

    flush: FlushReport
    """Inner result of step 2 (`flush_observability`)."""

    already_shutdown: bool
    """`True` iff this is a second `shutdown(ctx)` call returning the cached
    report. Spec §10 invariant: "calling `shutdown(ctx)` twice is safe"."""

    timed_out: bool
    """`True` iff total shutdown wall-time exceeded the caller-supplied
    `timeout`. Composes with `flush.timed_out`."""

    failures: tuple[str, ...]
    """Per-resource failure tags (subset of `('flush:tracer', 'flush:ledger',
    'collector_daemon', 'tracer_provider', 'provider:<name>')`)."""

    audit_ledger_head_hash: str | None
    """Head hash of the audit ledger post-shutdown (hex). `None` iff ledger
    is at genesis (no entries) or reads fail."""


# Module-level idempotency registry. WeakValueDictionary maps `id(ctx)` to
# the live HarnessContext — the entry disappears when ctx is gc'd, so we
# don't get false-positives from id() reuse.
_shutdown_registry: WeakValueDictionary[int, HarnessContext] = WeakValueDictionary()
_cached_reports: dict[int, ShutdownReport] = {}


def _discard_cached_report(ctx_id: int) -> None:
    """`weakref.finalize` callback — drop the cached report when ctx is gc'd."""
    _cached_reports.pop(ctx_id, None)


async def _drain_dispatch_executor(ctx: HarnessContext, remaining: float) -> bool:
    """Step 3 stage-5 dispatch executor — `drain(deadline_seconds=remaining)`.

    B-48 (U-RT-141) gave stage 5 a real stateful resource: the grow-on-demand
    sub-agent-dispatch executor's daemon worker threads, holding frame leases
    until actual job termination. `drain()` is sync/polling (never joins a
    loop-bridged worker) so it is dispatched off the loop via `to_thread`.
    Returns True iff every outstanding job drained within the deadline.
    """
    dispatch_executor = getattr(ctx, "sub_agent_dispatch_executor", None)
    if dispatch_executor is None:
        return True
    _completed, still_outstanding = await asyncio.to_thread(
        dispatch_executor.drain, deadline_seconds=max(0.0, remaining)
    )
    return still_outstanding == 0


async def _close_collector_daemon(ctx: HarnessContext, remaining: float) -> bool:
    """Step 3 collector — `await daemon.stop(timeout_seconds=remaining)`."""
    daemon = ctx.collector_daemon
    stop = cast(Callable[..., object], daemon.stop)  # type: ignore[attr-defined]
    result = stop(timeout_seconds=max(0.0, remaining))
    if asyncio.iscoroutine(result):
        await result
    return True


async def _close_tracer_provider(ctx: HarnessContext) -> bool:
    """Step 3 tracer — sync OTel `shutdown()` dispatched off the loop."""
    shutdown_fn = cast(
        Callable[[], object],
        ctx.tracer_provider.shutdown,  # type: ignore[attr-defined]
    )
    await asyncio.to_thread(shutdown_fn)
    return True


def _entry_head_hash(entry: object) -> str | None:
    """Return the chain-head hash from a `StateLedgerEntry` (lowercase hex).

    Per C-IS-06: the chain head = `response_hash` of the most recent entry
    (the SHA-256 of its canonical content; each next-entry's
    `prior_event_hash` is `compute_response_hash(prior_entry)`). The
    `StateLedgerEntry` schema exposes `response_hash: Bytes32`; lowercase
    hex is the documented JSON-codec form per
    `harness_is/state_ledger_write.py` line 11.

    Returns `None` if the entry doesn't expose `response_hash` (defensive
    against duck-typed inputs at non-IS-typed call sites).
    """
    response_hash = getattr(entry, "response_hash", None)
    if response_hash is None:
        return None
    # Bytes -> lowercase hex; str -> assume already-hex (defensive).
    if isinstance(response_hash, (bytes, bytearray)):
        return response_hash.hex()
    return str(response_hash)


def _resolve_ctx_pidfile_path(ctx: HarnessContext) -> Path | None:
    """Resolve the pidfile path from `ctx.config` (U-RT-48).

    Returns `None` if config/repository_root isn't accessible at the schema
    level (defensive — `HarnessContext.config` is required post-bootstrap,
    so this should not return None in production paths; the guard is for
    test fakes that may stub `config` away).
    """
    try:
        config = ctx.config  # type: ignore[attr-defined]
    except AttributeError:
        return None

    from harness_runtime.admin.pidfile import resolve_pidfile_path

    try:
        return resolve_pidfile_path(config)
    except Exception:
        return None


def _read_audit_head_hash(ctx: HarnessContext) -> str | None:
    """Step 6 — read the audit-ledger head hash from `ctx.audit_writer.read_all()`.

    Returns the hex hash of the last entry, or `None` if the ledger is at
    genesis or the read fails. Non-raising — verification surface, not
    a hard gate.

    **Fix vs U-RT-46 (2026-05-20):** the prior version read `chain_hash`,
    which `StateLedgerEntry` does NOT expose. The schema field is
    `response_hash` per C-IS-05 §5 / C-IS-06; chain-head construction at
    C-IS-06 uses `compute_response_hash(prior_entry)`. The U-RT-46 tests
    passed because the fake `_FakeAuditWriter.read_all` returned namespaces
    with `chain_hash=`. Real `StateLedgerEntry` instances always returned
    `None`. Now delegates to `_entry_head_hash`.
    """
    try:
        read_all = cast(
            Callable[[], list[object]],
            ctx.audit_writer.read_all,  # type: ignore[attr-defined]
        )
        entries = read_all()
        if not entries:
            return None
        return _entry_head_hash(entries[-1])
    except Exception:
        return None


async def shutdown(
    ctx: HarnessContext,
    *,
    timeout: float = 30.0,
) -> ShutdownReport:
    """Execute the C-RT-10 reverse-stage shutdown sequence.

    Steps per spec §10:

    1. **Drain** — set `ctx.drained_flag`. The in-flight wait (AC #2 of
       U-RT-44) is STRUCK per `[[fork-u-rt-44-workflow-loop-drain]]`;
       resolution lands at U-RT-49 when the CP workflow loop materializes.
    1b. **Drain the stage-5 sub-agent-dispatch executor** (B-48 U-RT-141) —
       BEFORE the observability flush (codex round-4 [P1]): a job still
       finishing during this drain must get its spans/audit entries written
       while the tracer/exporters are still open, not after.
    2. **Flush observability** — delegates to `flush_observability(ctx)`.
    3. **Close collector/tracer/provider clients in reverse** — collector
       daemon, tracer provider, then every provider client. Stage-5's LLM
       emitter/dispatcher (pre-B-48) and stage-3b routing/registries remain
       stateless-by-design no-ops.
    4. **Close stage-2 resources** — MCP clients + host. Both are
       placeholder dataclasses at HEAD (U-RT-22); no-op until a real
       MCP runtime lands.
    5. **Close stage-1 resources** — ledger fsync (covered by step 2),
       index + cache (no close surface), worktree leases (none allocated
       until U-RT-49+).
    6. **Verify** — read audit-ledger head hash and record in report.

    Per spec §10 invariants:
    - Idempotent: second call with same ctx returns the cached report
      with `already_shutdown=True`.
    - Bounded by `timeout`: each step is allotted the remaining budget;
      exceeded budget surfaces via `ShutdownReport.timed_out=True`.
    - Per-resource exception isolation: one failure doesn't abort the
      others; each surfaces in `failures`.

    Parameters
    ----------
    ctx :
        Post-bootstrap `HarnessContext` from a `run()` invocation.
    timeout :
        Total wall-time bound in seconds. Default 30.0 per spec
        deferred-to-discretion.

    Returns
    -------
    ShutdownReport
        Per-step status. Callers wanting hard-fail semantics inspect
        `failures`, `timed_out`, and `already_shutdown`.
    """
    ctx_id = id(ctx)
    cached = _cached_reports.get(ctx_id)
    if cached is not None and _shutdown_registry.get(ctx_id) is ctx:
        # Second-call: return cached report with already_shutdown flag asserted.
        return cached.model_copy(update={"already_shutdown": True})

    deadline = time.monotonic() + timeout
    failures: list[str] = []
    timed_out = False

    # Step 1 — drain. Idempotent: `Event.set()` is a no-op if already set.
    ctx.drained_flag.set()

    # Step 1b — stage-5 sub-agent-dispatch executor (B-48 U-RT-141), drained
    # BEFORE observability flush (codex round-4 [P1] "drain dispatch jobs
    # before flushing observability"): a job still running when flush would
    # otherwise fire can emit spans/audit entries THROUGH the drain window —
    # draining first means every such write lands before step 2 flushes and
    # step 3b closes the tracer/exporters, instead of racing (or losing) a
    # write that happens during/after those close. Reverse-stage order:
    # LOOP_INIT (stage 5) opened after OD (stage 4), so it closes before the
    # collector/tracer close below regardless of this reordering.
    remaining = max(0.0, deadline - time.monotonic())
    # codex round-8 [P2] "enter draining state before scheduling the bounded
    # wait" — `_drain_dispatch_executor`'s `dispatch_executor.drain(...)`
    # call (which flips `_draining`) runs off-loop via `asyncio.to_thread`,
    # bounded below by `asyncio.wait_for`. At (or near) a zero-remaining
    # budget the whole coroutine can be cancelled before `drain()` ever gets
    # scheduled, so `_draining` never flips — `reserve`/`reserve_fanout`/
    # `submit` keep admitting + launching NEW work against an executor whose
    # shutdown is already underway. `begin_draining()` is plain synchronous
    # code (no await, no scheduling delay, no timeout budget) — call it
    # directly here so the admission surface ALWAYS closes regardless of how
    # much wall-clock budget remains; `drain()` below still runs its own
    # (idempotent) `begin_draining()` call as its first step.
    _pre_drain_executor = getattr(ctx, "sub_agent_dispatch_executor", None)
    if _pre_drain_executor is not None:
        _pre_drain_executor.begin_draining()
    try:
        # codex round-4 [P2] "include drain scheduling in the shutdown
        # deadline" — `_drain_dispatch_executor`'s own `asyncio.to_thread`
        # call is scheduled onto the loop's DEFAULT thread pool; if that pool
        # is saturated (other `to_thread` work queued ahead of it), the
        # SCHEDULING delay alone can push past `remaining` before `drain()`
        # ever starts counting its own internal budget. `asyncio.wait_for`
        # bounds the whole operation — scheduling delay plus drain time —
        # to `remaining`, mirroring the same fix already applied to step 3b
        # (`_close_tracer_provider`) below.
        drained_clean = await asyncio.wait_for(
            _drain_dispatch_executor(ctx, remaining), timeout=remaining
        )
        if not drained_clean:
            failures.append("sub_agent_dispatch_executor")
            timed_out = True
    except TimeoutError:
        failures.append("sub_agent_dispatch_executor")
        timed_out = True
    except Exception:
        failures.append("sub_agent_dispatch_executor")

    # Step 2 — flush observability.
    remaining = max(0.0, deadline - time.monotonic())
    flush_report = await flush_observability(ctx, timeout_millis=int(remaining * 1000))
    if flush_report.failures:
        failures.extend(f"flush:{tag}" for tag in flush_report.failures)
    if flush_report.timed_out:
        timed_out = True

    # Step 3a — collector daemon.
    remaining = max(0.0, deadline - time.monotonic())
    try:
        await _close_collector_daemon(ctx, remaining)
    except Exception:
        failures.append("collector_daemon")

    # Step 3b — tracer provider (sync; to_thread). Bounded by the remaining
    # budget: an unbounded `provider.shutdown()` (e.g. a stuck TCP teardown
    # against an OTLP collector) previously hung the whole shutdown sequence
    # indefinitely despite the docstring's "each step is allotted the
    # remaining budget" invariant.
    remaining = max(0.0, deadline - time.monotonic())
    try:
        if _tracer_flush_in_flight(ctx):
            # C-RT-10 flush-before-close (codex round-2 P1): at least one
            # timed-out force_flush worker is still exporting on its daemon
            # thread (a completed worker removes itself from the registry —
            # round-3 P1: a later re-flush completing must not erase the
            # evidence of an earlier worker still in flight). Closing the
            # provider now — or even submitting the close, which would
            # execute later regardless of the wait_for below — would overlap
            # teardown with the in-flight export (span loss / thread-unsafe
            # exporter teardown). Skip the close entirely and report it; a
            # deferred daemon watcher closes the provider once the lingering
            # flush completes (round-5 P1 — the cached report means no later
            # shutdown() call would ever retry this close).
            failures.append("tracer_provider")
            timed_out = True
            _spawn_deferred_tracer_close(ctx)
        else:
            await asyncio.wait_for(_close_tracer_provider(ctx), timeout=remaining)
    except TimeoutError:
        failures.append("tracer_provider")
        timed_out = True
    except Exception:
        failures.append("tracer_provider")

    # Step 3c — provider clients. Per-provider try/except; one failure
    # doesn't block the others. Bounded by the remaining budget (same
    # unbounded-hang gap as step 3b — a stuck provider `aclose()` blocked
    # every subsequent close step). `remaining` is recomputed INSIDE the loop
    # (not once before it) — otherwise every provider after the first would
    # get re-allotted the SAME stale budget rather than what's actually left,
    # so N slow providers could each burn the full timeout and blow the
    # aggregate shutdown deadline by a factor of N (out-of-family Codex [P2]).
    for name, provider in ctx.providers.items():
        remaining = max(0.0, deadline - time.monotonic())
        try:

            async def _aclose(provider: Any = provider) -> None:
                aclose = cast(Callable[[], object], provider.aclose)  # type: ignore[attr-defined]
                result = aclose()
                if asyncio.iscoroutine(result):
                    await result

            await asyncio.wait_for(_aclose(), timeout=remaining)
        except TimeoutError:
            failures.append(f"provider:{name}")
            timed_out = True
        except Exception:
            failures.append(f"provider:{name}")

    # Step 4 — MCP client hosts (spec v1.41 §14.9.8 arc, Gap F): drain each
    # per-server subprocess / connection per §14.9.6 inv 1 ("stage 7 SHUTDOWN
    # drains"). Runs in the same task as run_bootstrap (api.py) so each host's
    # anyio cancel scope closes in its owning task (the success-path teardown
    # crash without this). Guarded on a started host — the empty-sentinel /
    # unstarted host has nothing to drain. Per-resource exception isolation.
    # Bounded by the remaining budget (same unbounded-hang gap as steps 3b/3c).
    # (U-RT-125 reshape: `mcp_client_hosts` is a `dict[ServerName, MCPClientHost]`;
    # a single host today, ≥1 at B2-impl-2b.) `remaining` is recomputed INSIDE
    # the loop for the same reason as step 3c above — a stale pre-loop budget
    # would let each host burn the full timeout instead of what's actually
    # left, multiplying the aggregate shutdown time under multiple hosts.
    hosts: dict[ServerName, Any] = getattr(ctx, "mcp_client_hosts", None) or {}
    for host in hosts.values():
        remaining = max(0.0, deadline - time.monotonic())
        if getattr(host, "started", False):
            try:
                await asyncio.wait_for(host.shutdown(), timeout=remaining)
            except TimeoutError:
                failures.append("mcp_client_host")
                timed_out = True
            except Exception:
                failures.append("mcp_client_host")
    # Step 5 — ledger/index/cache/worktree: covered by step 2 / no close surface.

    # Step 5b — protected result store GC sweep (B-65-A; spec v1.103
    # §14.8.11 AC 7, codex round-4 [P2]) — the SHUTDOWN half of the
    # "GC sweep at bootstrap/shutdown" fallback (the BOOTSTRAP half runs at
    # `stage_4_od.py` and reaps a PRIOR process's abandoned entries; this
    # half reaps THIS process's own before exit, so a long-lived daemon that
    # never restarts still bounds the store between opportunistic in-write
    # sweeps). The exhaustion-deadlock hazard `asyncio.to_thread`'s DEFAULT
    # executor poses elsewhere (a sync driver occupying every worker) does
    # NOT apply here — `shutdown()` only runs AFTER `execute_workflow` has
    # already returned. But codex [P1] round 8 on this arc: a SEPARATE
    # hazard from the same default-executor choice DOES apply — `gc_sweep`
    # enumerates + decrypts every entry, which can genuinely run long, and
    # `asyncio.wait_for`'s timeout only abandons the AWAITING coroutine, not
    # the worker thread; the default executor's non-daemon workers are then
    # JOINED at interpreter exit regardless, so a slow sweep can hang
    # process exit long after this function's own bounded timeout already
    # fired and returned. Routing through the dedicated daemon-thread pool
    # (the same one the raise-site helper `resolve_result_ref_off_loop`
    # uses) fixes the hang-at-exit hazard — but codex [P2] round 9 found
    # that `run_audit_off_loop` itself was the WRONG variant: its
    # join-on-cancel is calibrated for AUDIT-WRITE durability (a fixed 10s
    # grace), and reusing it here let THIS function's own advertised
    # `timeout` overrun by up to that grace, since `wait_for`'s cancellation
    # had to wait for the inner join before propagating. This sweep has no
    # durability requirement of its own (an incomplete sweep just leaves
    # stale entries for the next opportunistic/bootstrap sweep) — so
    # `run_off_loop_detach_on_cancel` is used instead: it never joins, the
    # worker keeps running harmlessly on its daemon thread if still busy at
    # this function's own deadline, and `wait_for` bounds the wait exactly
    # as advertised. Best-effort: swept-key digests discarded, any
    # exception isolated per the same per-resource pattern as the steps
    # above.
    _protected_result_store = getattr(ctx, "protected_result_store", None)
    if _protected_result_store is not None:
        remaining = max(0.0, deadline - time.monotonic())
        try:
            await asyncio.wait_for(
                run_off_loop_detach_on_cancel(_protected_result_store.gc_sweep),
                timeout=remaining,
            )
        except TimeoutError:
            failures.append("protected_result_store")
            timed_out = True
        except Exception:
            failures.append("protected_result_store")

    if time.monotonic() > deadline:
        timed_out = True

    # Step 6 — audit-ledger head hash verification.
    audit_head = _read_audit_head_hash(ctx)

    # Per spec §13 pidfile lifecycle ("removes it at the end of shutdown()" —
    # U-RT-48). Done after step 6 but before caching the report so a removal
    # failure is recorded in the same report. Idempotent — second `shutdown()`
    # call short-circuits via the cached-report return above; the pidfile is
    # already gone.
    try:
        pidfile_path = _resolve_ctx_pidfile_path(ctx)
        if pidfile_path is not None:
            from harness_runtime.admin.pidfile import remove_pidfile

            remove_pidfile(pidfile_path)
    except Exception:
        failures.append("pidfile")

    report = ShutdownReport(
        flush=flush_report,
        already_shutdown=False,
        timed_out=timed_out,
        failures=tuple(failures),
        audit_ledger_head_hash=audit_head,
    )

    # Cache for idempotency. WeakValueDictionary lets ctx-gc clear the
    # registry; weakref.finalize clears the cached report alongside.
    _shutdown_registry[ctx_id] = ctx
    _cached_reports[ctx_id] = report
    weakref.finalize(ctx, _discard_cached_report, ctx_id)

    return report
