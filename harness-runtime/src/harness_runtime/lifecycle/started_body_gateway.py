"""B-104 Task 5a F4: run a body only after its claim's ``started`` frame is durable.

The single unit that owns the order for a resumed record: `claim` (which proves admission and
takes the lease), then `mark_started` (which fsyncs the ``started`` frame before returning), then
the body, then one release of the lease on every exit. It is non-invoking: no production path
calls it yet, and stage 5 still binds the always-refusing admission.

[LAW:types-are-the-program] The gateway takes a store, a ref, a typed admission and a
zero-argument body. It never accepts a `HeldClaim` or `StartedClaim` from its caller: the only
started claim in its scope is the one `mark_started` returns inside this call, so the body cannot
be reached on a claim that was merely claimed or handed in.
"""

from __future__ import annotations

from collections.abc import Callable

from harness_core import JournalRecordRef

from harness_runtime.lifecycle.resume_claim_store import Admission, ResumeClaimStore

__all__ = ["run_started"]


def run_started[R](
    store: ResumeClaimStore,
    ref: JournalRecordRef,
    admission: Admission,
    body: Callable[[], R],
    *,
    deadline_seconds: float | None = None,
) -> R:
    """Claim `ref`, durably start it, run `body`, and release the lease exactly once.

    Refusal, contention, a failed `started` write or fsync, and any body failure propagate
    unchanged. The body is never called unless `mark_started` returned, so a claim that is only
    claimed, refused, busy or whose `started` frame is not durable never reaches it. The lease is
    held through the whole body and released in `finally` on every exit, including
    `BaseException`; a claim whose body failed stays ``started`` (sticky), never re-runnable.
    """
    held = store.claim(ref, admission, deadline_seconds=deadline_seconds)
    try:
        # [LAW:no-ambient-temporal-coupling] The order is this statement sequence and nothing else:
        # the started frame is durable before the body is even referenced.
        _ = store.mark_started(held, deadline_seconds=deadline_seconds)
        return body()
    finally:
        held.close()
