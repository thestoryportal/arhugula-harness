"""Liveness deadline for the same-host cross-process advisory locks (``B-93``).

Every blocking ``fcntl.flock`` acquisition in this workspace was a bare
``flock(fd, LOCK_EX)`` / ``LOCK_SH`` with **no** bound: a holder that never
released wedged every same-host writer with no error, no log and no timeout.
The exposure the register row names is ``CanonicalMemoryStore.write_record_guarded``,
which holds the root-wide ``cross_process_scope_lock`` across a *caller-supplied
precondition callable* whose cost the store explicitly "knows nothing about".

**Vehicle: hand-rolled, ratified.** The `B-93` + `B-45` Class 2 fork
(``.harness/class_2_fork_b93_b45_lock_deadline_windows_backend.md`` §12) was
RATIFIED 2026-08-05 as **Reading B** with decision 3 = a HAND-ROLLED extension
of the existing primitive, explicitly **NOT** ``filelock`` — seven of the nine
acquisition sites are exclusive-only and need no shared face, so adopting a
dependency (and its lock-file-IDENTITY migration at every converted site) buys
nothing this leg needs. ``filelock`` is revisited only if the Windows half
(`B-45`, deferred on witnessability) ever goes YES.

**Shape: non-blocking probe + caller-owned bounded retry** — the row's own
close-out step (1). The same shape a real Windows backend would take
(``msvcrt.LK_NBLCK`` is likewise a non-blocking probe), so this leg performs the
code motion a later Windows leg needs rather than one it must undo.

**The deadline is END-TO-END per entry surface, not per acquisition.** One entry
surface can block at up to THREE distinct acquisition sites in sequence (for
``cross_process_write_lock``: the directory lock, then the legacy sidecar, then
the file lock) *and* can retry its whole acquisition on an inode-replacement
race. A per-acquisition bound would leave the entry surface with no end-to-end
guarantee while reading like a total one — the exact "partial guarantee that
reads as a total one" the fork's §5 Variant F was dominated on. Each entry
surface therefore mints ONE :class:`CrossProcessLockDeadline` and threads it
through every acquisition beneath it, so the caller-visible bound is the bound
the caller was given.

Home: ``harness-core`` per the fork's ratified sub-decision A-i. All four
carriers must raise ONE nominal type — one in ``harness-is``
(``cross_process_ledger_lock``, six of the nine sites) and three in
``harness-runtime`` — and ``harness-core`` has zero workspace dependencies so
nothing can cycle. Direct precedent: ``ValidatorEscalationGateTimeoutError``
(``validator_escalation_errors.py``), re-homed here for exactly this
carrier-home reason. Defining it in ``harness-runtime`` is ILLEGAL — it inverts
the IS 0-outbound invariant (``harness-is/CLAUDE.md`` §2.3).

``fcntl`` is imported lazily INSIDE :func:`flock_until_deadline`, never at module
scope: ``harness_core`` is imported eagerly by every axis, and an unconditional
top-level ``import fcntl`` would break ``import harness_core`` outright on
Windows. This module changes NO Windows behaviour — the Windows carve-outs stay
exactly where they are (`B-45`, deferred).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

__all__ = [
    "DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS",
    "CrossProcessLockDeadline",
    "CrossProcessLockTimeoutError",
    "flock_until_deadline",
]


DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS = 300.0
"""Default end-to-end budget for one cross-process lock entry surface.

Deliberately CONSERVATIVE (five minutes), and the value is the one knob this
leg chose rather than inherited — the fork ratified *that* a deadline exists,
not *what* it is. The asymmetry that sets it: the harm `B-93` registers is
entirely PROSPECTIVE (``write_record_guarded`` has one production caller, whose
precondition is bounded at one ``read_record`` per cited source), whereas a
deadline short enough to fire on a legitimately slow same-host section would
convert a working system into a failing one — a REGRESSION on a substrate
hardened across four closed register rows. Five minutes is far longer than any
same-host advisory-lock section this workspace holds and far shorter than
"forever with no diagnostic", which is the property being bought.

Overturnable by a later arc with a grounded shorter bound; every entry surface
takes a per-call ``deadline_seconds`` override, so no caller is stuck with it.
"""

_INITIAL_POLL_SECONDS = 0.001
_MAX_POLL_SECONDS = 0.005
"""Poll backoff, 1 ms doubling to a 5 ms ceiling.

The ceiling is the added release-to-acquire latency a contended waiter pays
versus the kernel's own blocking wakeup. Kept small deliberately: these locks
sit on the audit-sidecar and pause-journal append paths, where a coarse poll
would be an observable throughput cost. An UNCONTENDED acquisition pays NOTHING
— the first probe succeeds and the loop never sleeps — so the cost is paid only
where a caller was previously blocked anyway.

**HANDOFF FAIRNESS IS NOT PRESERVED, and this is the one real behavioural cost
of the bound — recorded rather than discovered later.** A blocking
``flock(LOCK_EX)`` parks the waiter in the kernel, which grants the lock on
release before the ex-holder can realistically re-acquire it; a POLLING waiter
is asleep at that instant, so an ex-holder that releases and immediately
re-acquires wins the next round. Consequence: a waiter's acquisition can be
DELAYED by a hot re-acquiring holder, where before it was effectively handed
off. This changes ORDERING, never EXCLUSION — mutual exclusion is the same
kernel ``flock`` it always was, and a waiter still cannot enter while a holder
is inside. Starvation is bounded on both ends: by the poll ceiling, and by the
deadline itself (a default 300 s budget would need five minutes of unbroken
re-acquisition to actually fail).

The property is intrinsic to the ratified shape, not to this implementation:
``filelock`` — the alternative vehicle the fork evaluated and declined — polls
identically (``poll_interval=0.05``, ten times coarser), and ``msvcrt.LK_LOCK``
retries at 1 s. No portable primitive gives a kernel-parked wait WITH a timeout.
One shipped witness depended on the old handoff ordering and was re-pinned at
this arc; see ``test_shadow_git_rollback.py``'s concurrent-append test.
"""


class CrossProcessLockTimeoutError(Exception):
    """A same-host cross-process advisory lock was not acquired within its deadline.

    Nominally DISTINCT from every precondition/conflict outcome in the tree —
    notably ``MemoryStoreGuardedWriteConflictError``, which reports that a
    guarded write's precondition became false. This reports a LIVENESS outcome:
    the critical section was never entered, nothing was read, nothing was
    written. A caller that conflates the two would report a provenance change
    that did not happen.

    Derives from ``Exception`` (the ``harness-core`` error precedent) rather
    than ``OSError``/``TimeoutError`` deliberately: the acquisition sites sit
    inside ``except OSError`` arms that classify ``ENOTSUP`` and would otherwise
    swallow this into an unrelated degradation path.
    """

    def __init__(self, *, lock_target: str, budget_seconds: float) -> None:
        super().__init__(
            f"cross-process lock not acquired within its {budget_seconds:g}s "
            f"deadline (target: {lock_target}) — a same-host holder did not "
            f"release; the critical section was NOT entered"
        )
        self.lock_target = lock_target
        self.budget_seconds = budget_seconds


@dataclass(frozen=True, slots=True)
class CrossProcessLockDeadline:
    """An ABSOLUTE end-to-end deadline for one lock entry surface.

    Absolute (a ``time.monotonic()`` instant) rather than a relative budget, so
    that threading it through a multi-site entry surface — or through a retry
    loop that re-runs the whole acquisition — cannot silently re-arm the clock.
    A relative float passed down the same path would be indistinguishable from
    a fresh budget at every hop, which is exactly the failure mode the
    end-to-end contract exists to exclude.
    """

    budget_seconds: float
    expires_at: float

    @classmethod
    def starting_now(cls, deadline_seconds: float | None = None) -> CrossProcessLockDeadline:
        """Mint a deadline running from this instant.

        ``None`` selects :data:`DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS`.
        """
        budget = (
            DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS
            if deadline_seconds is None
            else float(deadline_seconds)
        )
        if budget <= 0.0:
            raise ValueError(
                f"cross-process lock deadline must be positive, got {budget!r} — "
                f"a non-positive budget would make every contended acquisition "
                f"fail without waiting"
            )
        return cls(budget_seconds=budget, expires_at=time.monotonic() + budget)

    def remaining_seconds(self) -> float:
        """Seconds left before expiry; zero or negative once expired."""
        return self.expires_at - time.monotonic()


def flock_until_deadline(
    fd: int,
    operation: int,
    *,
    deadline: CrossProcessLockDeadline,
    lock_target: str,
) -> None:
    """Acquire ``operation`` (``LOCK_EX`` / ``LOCK_SH``) on ``fd`` within ``deadline``.

    The bounded-retry replacement for a bare blocking ``fcntl.flock(fd, op)``:
    probe non-blocking, and on contention sleep a bounded backoff and re-probe
    until the deadline expires, then raise
    :class:`CrossProcessLockTimeoutError`.

    Acquires on success and returns; on ANY exit other than success the lock is
    NOT held, so the caller's existing unwind (fd close, directory-lock release,
    in-process ``RLock`` release) is the same unwind it already ran for a
    raising ``flock``.

    An UNCONTENDED acquisition never sleeps — the first probe takes the lock —
    so a deadline that has already expired still succeeds when nothing holds the
    lock. The bound is on WAITING, not on the acquisition itself.

    Errors other than contention (``ENOTSUP`` on an un-flockable object,
    ``EBADF``) propagate unchanged from the first probe, preserving the
    classification the acquisition sites already perform.
    """
    import fcntl  # POSIX-only; every caller gates win32 before reaching here.

    poll_seconds = _INITIAL_POLL_SECONDS
    while True:
        try:
            fcntl.flock(fd, operation | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            pass
        remaining = deadline.remaining_seconds()
        if remaining <= 0.0:
            raise CrossProcessLockTimeoutError(
                lock_target=lock_target,
                budget_seconds=deadline.budget_seconds,
            )
        time.sleep(min(poll_seconds, remaining))
        poll_seconds = min(poll_seconds * 2.0, _MAX_POLL_SECONDS)
