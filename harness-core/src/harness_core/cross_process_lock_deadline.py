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

import math
import time
from dataclasses import dataclass, field

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
retries at 1 s. No portable primitive gives a kernel-parked wait WITH a timeout
(``F_SETLKW`` has none either; a watchdog thread would orphan an acquisition in
exactly the wedged-holder case this bound targets). One shipped witness depended
on the old handoff ordering and was re-pinned at this arc; see
``test_shadow_git_rollback.py``'s concurrent-append test.

**ONE CONSEQUENCE REACHES A PRODUCTION CONTRACT — register row ``B-112``**
(out-of-family review round 1 [P1], accepted; reproduced 12/20 by the reviewer's
own contention probe). ``append_ledger_entry`` validates a CALLER-SAMPLED
timestamp against PHYSICAL APPEND ORDER under a ``_CLOCK_SKEW_TOLERANCE`` of
ZERO, so a waiter whose timestamp was sampled BEFORE it queued can now be
overtaken by a later-arriving writer and be refused with
``NonMonotonicTimestampError``. **The lock layer cannot fix this and should not
try**: no acquisition ordering makes a timestamp sampled arbitrarily long before
acquisition correct, and the ordering flock itself guarantees is unspecified.
**The remedy already exists in the cleared spec** — C-IS-07 §7.6 (IS spec v1.11)
added ``WRITER_OWNED_TIMESTAMP``, which samples the timestamp INSIDE the write
critical section so sampling order EQUALS append order, monotonic by
construction and immune to any lock's fairness. Selecting it per caller is a
semantic decision about whose clock a given entry records, so it is registered
rather than applied wholesale here.
"""


_BUDGET_REFUSAL = (
    "cross-process lock deadline must be a finite positive number of seconds, "
    "got {value!r} — a non-positive budget would refuse every contended "
    "acquisition without waiting, and a non-finite one would never expire (the "
    "unbounded block this bound removes)"
)


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
    expires_at: float = field(init=False)
    """DERIVED, never supplied — the clock starts when the deadline is created.

    Out-of-family review rounds 2 [P2] and 3 [P2], accepted, in two steps. Round
    2 established that validating only in :meth:`starting_now` left the illegal
    state one constructor call away (``CrossProcessLockDeadline(nan, nan)`` makes
    ``remaining_seconds()`` return ``nan``, so ``remaining <= 0`` is never true
    and a contended acquisition polls FOREVER). Round 3 showed that validating
    the two fields INDEPENDENTLY was still not enough: a caller could declare
    ``budget_seconds=0.001`` with an expiry an hour out, and every timeout
    message would then report a 1 ms budget for an hour-long wait — a diagnostic
    that lies about the very thing this type exists to make legible.

    Both are closed by removing the SECOND AUTHORITY rather than policing a
    relationship between two: the expiry is now COMPUTED from the budget, so the
    fields cannot disagree by construction and there is nothing left to
    cross-validate.
    """

    def __post_init__(self) -> None:
        if not math.isfinite(self.budget_seconds) or self.budget_seconds <= 0.0:
            raise ValueError(_BUDGET_REFUSAL.format(value=self.budget_seconds))
        object.__setattr__(self, "expires_at", time.monotonic() + self.budget_seconds)

    @classmethod
    def starting_now(cls, deadline_seconds: float | None = None) -> CrossProcessLockDeadline:
        """Mint a deadline running from this instant.

        ``None`` selects :data:`DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS`.

        Validation and the expiry computation both live at ``__post_init__``,
        deliberately: a mirrored check here would be unreachable defensive code —
        its PD-8 probe came back GREEN precisely because ``__post_init__`` already
        refuses every value it would have caught, and a guard no mutation can
        defeat is a guard that is not doing anything. This classmethod now adds
        exactly one thing the constructor cannot: resolving ``None`` to the
        default budget.
        """
        return cls(
            DEFAULT_CROSS_PROCESS_LOCK_DEADLINE_SECONDS
            if deadline_seconds is None
            else float(deadline_seconds)
        )

    def remaining_seconds(self) -> float:
        """Seconds left before expiry; zero or negative once expired."""
        return self.expires_at - time.monotonic()


def flock_until_deadline(
    fd: int,
    operation: int,
    *,
    deadline: CrossProcessLockDeadline,
    lock_target: str,
    contention_observed: bool = False,
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

    An UNCONTENDED acquisition never sleeps — the FIRST probe takes the lock —
    so a deadline that has already expired still succeeds when nothing holds the
    lock. The bound is on WAITING, not on the acquisition itself.

    **``contention_observed`` withdraws that first-probe exemption**, and the
    three ABBA arms MUST pass it *(out-of-family review round 7 [P2],
    accepted)*. Those arms run their OWN non-blocking probe, see
    ``BlockingIOError``, release the directory lock and only then call this
    helper — so by the time the first probe here runs, contention is an
    ESTABLISHED FACT and the caller has already waited. Exempting that probe
    would let a holder who releases during the handoff hand the lock to a caller
    whose budget had already expired: the exemption exists for the case where
    nothing was ever contended, and this is not that case.

    **It NEVER RETURNS HOLDING A LOCK IT ACQUIRED PAST THE DEADLINE.** Checking
    expiry only *before* probing cannot deliver that: the checking thread can be
    descheduled, the holder release meanwhile, and the next probe then succeed
    on a spent budget — the bound would hold "usually", which is the kind of
    guarantee that reads as total and is not. The check therefore sits on the
    SUCCESS path, after the acquisition, where there is no window left to lose:
    a retry that lands late is UNLOCKED and refused *(out-of-family review
    rounds 2 and 6 [P2], accepted — round 2 moved the check after the sleep,
    round 6 established that only the success path closes it)*.

    Errors other than contention (``ENOTSUP`` on an un-flockable object,
    ``EBADF``) propagate unchanged from the first probe, preserving the
    classification the acquisition sites already perform.
    """
    import fcntl  # POSIX-only; every caller gates win32 before reaching here.

    poll_seconds = _INITIAL_POLL_SECONDS
    first_probe = not contention_observed
    while True:
        try:
            fcntl.flock(fd, operation | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            if first_probe or deadline.remaining_seconds() > 0.0:
                return
            # Acquired, but only after the budget was spent. Release what we
            # just took — a caller that gets a lock here would believe it
            # acquired within its deadline — and refuse. Unlocking BEFORE
            # raising keeps the invariant every caller's unwind relies on: on
            # any exit other than a successful return, the lock is not held.
            fcntl.flock(fd, fcntl.LOCK_UN)
            raise CrossProcessLockTimeoutError(
                lock_target=lock_target,
                budget_seconds=deadline.budget_seconds,
            )
        first_probe = False
        remaining = deadline.remaining_seconds()
        if remaining <= 0.0:
            raise CrossProcessLockTimeoutError(
                lock_target=lock_target,
                budget_seconds=deadline.budget_seconds,
            )
        time.sleep(min(poll_seconds, remaining))
        poll_seconds = min(poll_seconds * 2.0, _MAX_POLL_SECONDS)
