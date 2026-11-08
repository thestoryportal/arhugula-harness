"""B-104: a durable root `resume_handle` is claimed and durably started before its body runs.

`api.resume` reads one exact root record before bootstrap and hands its address — the real
journal directory that read opened and the `JournalRecordRef` of that same read — to the
in-process `run_workflow` tool as a `DurableRootResume`. The tool's `asyncio.to_thread` worker
calls `run`, which places that directory under the verified external state root, refuses unless
the bootstrapped capture directory resolves to that same directory, claims the ref as
the journal's current latest root record, fsyncs ``started`` (`run_started`), and only then
runs the workflow body with a `ClaimedChildAdmission` over the root's `StartedProof` as CP's
`child_resume_authority`. Running in the worker is what makes the lease outlive a drain
timeout: the API may return ``drained`` while the worker still owns the lease, which
`run_started` releases only when the body returns.

A fresh root run is a `FreshRunAdmission` (Runtime spec v1.137 Rules B1-B3): before its body it
places the run's pause-journal root and supersedes the workflow's journal there at its admission
point, then runs with no authority. A
caller-supplied snapshot is `UNCLAIMED`: no claim and no authority. Both leave stage 5's refusing
child admission as the fallback.

A refusal before the body — placement, a refused or busy claim, a start that is not durable —
becomes a `ResumeClaimRefusedError` recorded on the request, because typed errors do not
survive the MCP text boundary; `api.resume` raises it. Faults once the body has begun (a
child's own refusal included) propagate as themselves.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Final

from harness_core import JournalRecordRef
from harness_core.cross_process_lock_deadline import CrossProcessLockTimeoutError
from harness_cp.workflow_driver_types import ChildResumeAuthority

from harness_runtime.config import state_placement
from harness_runtime.config.state_placement import StateRootPlacementError, place_state_dir
from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission
from harness_runtime.lifecycle.durable_pause_resume_protocol import DurablePauseResumeProtocol
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    EnginePauseLocator,
    JournalWorkflowPauseStore,
)
from harness_runtime.lifecycle.pause_journal_root_resolver import (
    PauseJournalRootUnresolvedError,
    resolve_pause_journal_root,
)
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimBusyError,
    ClaimRefusedError,
    ResumeClaimStore,
    RootLatestAdmission,
    StartedProof,
)
from harness_runtime.lifecycle.started_body_gateway import (
    GatewayPhase,
    GatewayRefusal,
    run_started,
)

if TYPE_CHECKING:
    from harness_runtime.types import HarnessContext

__all__ = [
    "UNCLAIMED",
    "DurableRootResume",
    "FreshRunAdmission",
    "FreshRunAdmissionError",
    "JournalDirectoryMismatchError",
    "ResumeAdmission",
    "ResumeClaimRefusedError",
    "RootResumeRefusal",
]

type Body[R] = Callable[[ChildResumeAuthority | None], R]

type Locate[R] = Callable[[R], EnginePauseLocator | None]
"""The engine-pause locator a root body's result owes the journal (B-314 fork §2), if any."""


def _owes_no_locator(_: object) -> None:
    return None


def _append_locator(journal: JournalWorkflowPauseStore, locator: EnginePauseLocator | None) -> None:
    # [LAW:single-enforcer] The one append site both root units share, after their body returns.
    match locator:
        case EnginePauseLocator():
            journal.capture_locator(locator)
        case None:
            pass


"""The workflow body: CP's `execute_workflow`, given the root's child authority (or none)."""


class RootResumeRefusal(StrEnum):
    """Why a durable root record was not admitted; its body never ran."""

    PLACEMENT = "placement"
    CLAIM_REFUSED = "claim-refused"
    CLAIM_BUSY = "claim-busy"
    START_REFUSED = "start-refused"


class ResumeClaimRefusedError(Exception):
    """`RT-FAIL-RESUME-CLAIM-REFUSED` — the durable root record was not admitted (B-104).

    `reason` is the stable discriminator; the typed refusal it was mapped from (a
    `GatewayRefusal` or `StateRootPlacementError`) is the `__cause__`. The message names the
    reason only, never a path. `claim-busy` is the one retryable reason: another holder is live.
    """

    def __init__(self, reason: RootResumeRefusal) -> None:
        super().__init__(
            f"RT-FAIL-RESUME-CLAIM-REFUSED:{reason.value}: the durable root record was not "
            "admitted and its workflow body did not run (B-104)."
        )
        self.reason: RootResumeRefusal = reason


class JournalDirectoryMismatchError(Exception):
    """The run's bootstrapped capture directory is not the directory the record was read from.

    A declared pause-journal root symlink retargeted between the pre-bootstrap read and bootstrap
    would pair a record claimed in one directory with a run that captures and admits children in
    another (Runtime spec v1.137 Rule B3: one journal file). A `placement` refusal: no claim is
    made and the body never runs.
    """

    def __init__(self) -> None:
        super().__init__(
            "the bootstrapped pause-journal directory is not the directory the durable "
            "record was read from"
        )


type _PreBodyRefusal = GatewayRefusal | StateRootPlacementError | JournalDirectoryMismatchError


def _run_journal_root(ctx: HarnessContext) -> Path:
    """This run's pause-journal root: its durable capture directory, else a fresh resolution.

    [LAW:one-source-of-truth] A durable run's capture directory was resolved once at bootstrap;
    resolving the declared root again could name a different directory than its captures.
    """
    match ctx.pause_resume_protocol:
        case DurablePauseResumeProtocol(journal_dir=journal_dir):
            return journal_dir
        case _:
            return resolve_pause_journal_root(ctx.config)


def _reason_of(refusal: _PreBodyRefusal) -> RootResumeRefusal | None:
    """The root refusal for a typed pre-body refusal, or `None` for an unmapped combination."""
    match refusal:
        case StateRootPlacementError() | JournalDirectoryMismatchError():
            return RootResumeRefusal.PLACEMENT
        case GatewayRefusal(phase=GatewayPhase.CLAIM, cause=ClaimRefusedError()):
            return RootResumeRefusal.CLAIM_REFUSED
        case GatewayRefusal(phase=GatewayPhase.CLAIM, cause=ClaimBusyError()):
            return RootResumeRefusal.CLAIM_BUSY
        case GatewayRefusal(phase=GatewayPhase.START, cause=ClaimRefusedError()):
            return RootResumeRefusal.START_REFUSED
        case _:
            return None


class DurableRootResume:
    """The exact root record `api.resume` read, admitted inside the resume worker.

    [LAW:one-source-of-truth] `journal_dir` (the real path the read opened) and `ref` come from
    ONE pre-bootstrap read and are the record's only address: the worker never re-reads the
    journal or claims anywhere else, and the store re-proves under its journal lock that `ref`
    is still that directory's latest depth-0 record. Bootstrap's capture directory is only
    compared with it, never substituted for it.

    `refusal` has one writer (`run`, before any body) and one reader (`api.resume`, after the
    tool call raised); it stays `None` whenever the body was reached.
    """

    def __init__(self, *, journal_dir: Path, ref: JournalRecordRef) -> None:
        self.journal_dir: Final = journal_dir
        self.ref: Final = ref
        self.refusal: ResumeClaimRefusedError | None = None

    def run[R](self, ctx: HarnessContext, body: Body[R], locate: Locate[R] = _owes_no_locator) -> R:
        """Claim, durably start, run `body` with the root's child authority, release once,
        then journal the locator a resumed run that paused again owes (a new claimable record)."""
        entered = False
        try:
            placement = place_state_dir(
                self.journal_dir,
                ctx.config,
                ctx.verified_state_root,
                what="durable resume journal directory",
                # Looked up at call time: the same verifier stage 1 stamped the root with.
                filesystem_type=state_placement.linux_filesystem_type,
            )
            if _run_journal_root(ctx) != self.journal_dir:
                raise JournalDirectoryMismatchError
            store = ResumeClaimStore(placement=placement, tenant_id=ctx.config.tenant_id)

            def started_body(started: StartedProof) -> R:
                nonlocal entered
                entered = True
                # [LAW:no-ambient-temporal-coupling] Built only once `started` is durable; each
                # carried child claims through it and a grandchild through its child.
                return body(ClaimedChildAdmission(store, started))

            result = run_started(store, self.ref, RootLatestAdmission(), started_body)
        except (GatewayRefusal, StateRootPlacementError, JournalDirectoryMismatchError) as exc:
            reason = None if entered else _reason_of(exc)
            # A refusal raised inside the body is the body's, and an unmapped one is a fault.
            if reason is None:
                raise
            self.refusal = ResumeClaimRefusedError(reason)
            raise self.refusal from exc
        _append_locator(
            JournalWorkflowPauseStore(journal_dir=placement.path, tenant_id=ctx.config.tenant_id),
            locate(result),
        )
        return result


class _Unclaimed:
    """A fresh run or caller-supplied snapshot: outside the claim contract, no authority."""

    refusal: Final = None

    def run[R](self, ctx: HarnessContext, body: Body[R], locate: Locate[R] = _owes_no_locator) -> R:
        _ = ctx, locate
        return body(None)


UNCLAIMED: Final = _Unclaimed()


class FreshRunAdmissionError(Exception):
    """A fresh root run failed at its admission point; its workflow body did not run.

    The message names no path or identifier; the failed resolution, placement or journal
    operation is the `__cause__`.
    """

    def __init__(self) -> None:
        super().__init__(
            "the fresh run's pause-journal root resolution, placement or supersession append "
            "failed and its workflow body did not run (Runtime spec v1.137 Rule B3)"
        )


class FreshRunAdmission:
    """One fresh depth-0 run's admission: supersede the workflow's journal, then run the body.

    [LAW:single-enforcer] Runtime spec v1.137 Rule B1: the one place a supersession record is
    written. Each `run_workflow` invocation builds its own, so neither `run_id` nor `failure`
    is ever shared with a concurrent invocation. `failure` has one writer (`run`, before any
    body) and stays `None` whenever the body was reached.

    Rule B3: the journal directory is the run's pause-journal root, placed under the verified state
    root like every other journal site, so a durable run supersedes in the file it captures to.
    """

    def __init__(self, *, workflow_id: str, run_id: str) -> None:
        self.workflow_id: Final = workflow_id
        self.run_id: Final = run_id
        self.failure: FreshRunAdmissionError | None = None

    def run[R](self, ctx: HarnessContext, body: Body[R], locate: Locate[R] = _owes_no_locator) -> R:
        """Append the supersession record at the admission point, run `body` unclaimed, then
        journal the locator an engine-native pause owes."""
        try:
            placement = place_state_dir(
                _run_journal_root(ctx),
                ctx.config,
                ctx.verified_state_root,
                what="pause-journal root",
                filesystem_type=state_placement.linux_filesystem_type,
            )
            store = JournalWorkflowPauseStore(
                journal_dir=placement.path, tenant_id=ctx.config.tenant_id
            )
            store.supersede(self.workflow_id, self.run_id)
        except (
            PauseJournalRootUnresolvedError,
            StateRootPlacementError,
            OSError,
            CrossProcessLockTimeoutError,
        ) as exc:
            # [LAW:no-silent-failure] Rule B3: a failed resolution, placement or append fails the
            # run before its first step (witness I.16 F1).
            self.failure = FreshRunAdmissionError()
            raise self.failure from exc
        result = body(None)
        _append_locator(store, locate(result))
        return result


type ResumeAdmission = DurableRootResume | _Unclaimed
"""What a resumed `run_workflow` body runs through; a fresh one runs through `FreshRunAdmission`."""
