"""Effect-boundary fence — at-most-once EXECUTION of non-idempotent step effects.

R-FS-1 standalone arc ``B-EFFECT-FENCE`` (runtime spec §14.22 C-RT-31, new at
v1.60). The durable engine classes (E sub-program) guarantee at-most-once *claim
of a revision* (the U-RT-123 reconciler CAS), NOT at-most-once *execution* of the
workflow steps a resume re-runs. A non-idempotent external effect (``git_push`` /
``send_email`` / any side-effecting MCP tool) fires *inside* the re-executed step,
and the per-step ledger COMMIT (`workflow_driver.py` `_append_step_ledger_entry`)
lands AFTER the dispatch returns — so a crash anywhere in the window

    dispatch(step) → call_tool() [EFFECT FIRES] → … → _append_step_ledger_entry()

leaves the effect fired but the step *uncommitted*. On resume, the driver's
``_determine_resume_at`` (shared by all four durable engine classes) finds the
step absent from the contiguous-materialized prefix → ``resume_at`` = that step →
the loop re-dispatches it → the same external effect fires a SECOND time. The
prefix-skip protects only COMMITTED steps; this window is precisely the
effected-but-uncommitted step nothing else covers, and is DISTINCT from the
reconciler's *revision-claim* fail-close.

This module is the hand-rolled (I-6 — no vendored Temporal/DBOS activity-dedup)
**per-effect fence at the tool sink**. It mirrors the U-RT-123 reconciler's
crash-atomic POSIX ``O_EXCL``/``os.link`` claim, applied at the
``RuntimeToolDispatcher`` ``call_tool`` sink keyed on the per-(run, step, tool)
composed ``idempotency_key``:

  * ``try_reserve(key)`` does the atomic claim. The FIRST caller wins (``True`` →
    fire the effect). ANY later caller of the SAME key loses (``False``) — both
    the cross-process RESUME re-dispatch AND an in-process RETRY (the
    ``RetryBreakerToolDispatcher`` re-calls the bare dispatcher) re-reach the sink
    with the same key. The sink maps a lost claim to ``EffectFenceReservedUncommittedError``.
  * COMMIT = the EXISTING per-step ledger entry (one source of truth); the fence
    adds only the RESERVE (pre-fire) marker. No second commit record.

**Semantic = at-most-once, NOT exactly-once.** A reserve written before a crash
that fired no effect (the fire-then-crash-before-commit window is genuinely
ambiguous to the harness) fail-closes the re-dispatch to HITL (§22.1) rather than
risk a double-execution — the honest residual, mirroring the reconciler's
fail-closed posture. Genuine *suppress-and-continue* (returning the prior
output so the resumed run proceeds) awaits the output-carrying substrate of the
registered ``B-ENGINE-OUTPUT-REPLAY`` arc; until then a fenced re-dispatch raises.

**Operationally surprising (documented, not hidden):** because the fence blocks
*every* re-entry of a key, a transient ``call_tool`` failure of a non-idempotent
effect fail-closes its retry instead of retrying. That is the *correct*
conservative behavior for a non-idempotent effect (you cannot safely retry an
effect that may already have fired); an idempotent tool does not need the fence
(per-tool fence opt-in is the registered ``B-EFFECT-FENCE-PER-TOOL`` follow-on).

**Single-host** (the reconciler's bound posture): the default ``LOCAL_SINGLE_HOST``
flock-free claim is atomic on a local filesystem. Cross-host effect-fencing is
distributed-impossible under {I-6 ∧ no-unsafe-TTL} and folds into the deferred
F-CC multi-host recovery item — exactly as for the reconciler.
"""

from __future__ import annotations

import hashlib
import os
import socket
import uuid
from pathlib import Path
from typing import Protocol, runtime_checkable

__all__ = [
    "EffectFenceProtocol",
    "EffectFenceReservedUncommittedError",
    "RuntimeEffectFence",
]


class EffectFenceReservedUncommittedError(Exception):
    """A re-dispatch reached the tool sink for an effect a prior attempt reserved.

    The effect's ``idempotency_key`` was already claimed by a prior attempt that
    did NOT commit (else the step would be prefix-skipped on resume and never
    re-reach the sink). The external effect MAY already have fired, so re-firing
    it would risk an at-least-once double-execution. The sink raises this
    (fail-closed to §22.1 HITL) rather than re-fire — the honest at-most-once
    posture. NOT a transient class: a retry always re-loses the claim, so the
    ``RetryBreakerToolDispatcher`` must treat it as permanent.
    """

    def __init__(self, *, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key
        super().__init__(
            "effect-fence: idempotency_key already reserved by a prior "
            "uncommitted attempt; re-firing the non-idempotent effect is "
            f"foreclosed (at-most-once) — fail-closed to HITL (key={idempotency_key!r})"
        )


@runtime_checkable
class EffectFenceProtocol(Protocol):
    """The reserve-before-fire surface the tool dispatcher consults at the sink."""

    def try_reserve(self, idempotency_key: str) -> bool:
        """Atomically claim the effect. ``True`` = won (fresh) → fire; ``False`` =
        already reserved by a prior attempt → the caller fail-closes."""
        ...


class RuntimeEffectFence:
    """Durable single-host effect fence — crash-atomic ``O_EXCL``/``os.link`` claim.

    ``harness_runtime``-private; never leaks into a cleared CP Protocol (a runtime
    substrate within §14.9 impl-discretion, not a new cross-axis contract). The
    claim mechanism is the U-RT-123 ``_claim_resume_revision`` pattern verbatim,
    re-keyed from ``(workflow, resource_version)`` to the per-effect
    ``idempotency_key``.
    """

    def __init__(self, *, fence_dir: Path) -> None:
        self._fence_dir = fence_dir

    @property
    def fence_dir(self) -> Path:
        """The durable claim-file directory."""
        return self._fence_dir

    def _claim_file(self, idempotency_key: str) -> Path:
        """The atomic claim file for one effect ``idempotency_key``.

        The key is already per-(run, step, tool) scoped (the run-scoped
        ``_compute_step_idempotency_key`` composed with ``step_id``/``tool_id`` at
        the dispatcher), so a flat directory keyed by its digest is collision-free
        ACROSS runs — a fresh run derives a different ``run_idempotency_key`` → a
        disjoint claim namespace (the U-RT-123 finding O-E3b-1 run-scoping lesson).
        """
        digest = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()
        return self._fence_dir / f"{digest}.claim"

    def try_reserve(self, idempotency_key: str) -> bool:
        """Crash-atomic claim of the effect ``idempotency_key``.

        Returns ``True`` iff THIS call won the right to fire the effect; ``False``
        iff the key was already reserved (a resume re-dispatch or an in-process
        retry of the same effect). Hand-rolled (I-6) via the POSIX atomic
        create-exclusive primitive: write a best-effort incarnation stamp
        (``host:pid`` — for observability, NOT the win/lose discriminator) to a
        uuid-unique temp (``fsync``-ed), then ``os.link`` it into place. ``link``
        is atomic and raises ``FileExistsError`` if the claim exists, so a crash
        can only ever leave an orphan temp, never a half-published claim; the won
        claim's dirent is ``fsync``-ed so a crash cannot lose it and let a second
        dispatch re-create the claim and double-fire.
        """
        path = self._claim_file(idempotency_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        stamp = f"{socket.gethostname()}:{os.getpid()}".encode()
        tmp = path.parent / f"{path.name}.{uuid.uuid4().hex}.tmp"
        try:
            fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                os.write(fd, stamp)
                os.fsync(fd)
            finally:
                os.close(fd)
            try:
                os.link(tmp, path)
            except FileExistsError:
                return False  # the effect is already reserved → lose the claim
            self._fsync_dir(path.parent)
            return True
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    @staticmethod
    def _fsync_dir(directory: Path) -> None:
        """``fsync`` the directory so the won claim's dirent survives a crash."""
        dir_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        except OSError:
            # Some filesystems reject directory fsync; the link itself is durable
            # enough on those (best-effort, mirroring the reconciler substrate).
            pass
        finally:
            os.close(dir_fd)
