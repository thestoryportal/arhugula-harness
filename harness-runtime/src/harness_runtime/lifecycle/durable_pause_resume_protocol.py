"""Durable variant of the CP ``PauseResumeProtocol`` (R-CC-1 arc #3, step 2).

The workflow-layer sibling of how ``JournalEnginePauseResumeSubstrate`` (#475) is
the durable variant of the engine substrate: a subclass of the CP-canonical
``harness_cp.pause_resume_protocol.PauseResumeProtocol`` whose
``capture_pause_snapshot`` ALSO persists the composed ``PauseSnapshot`` to a
``JournalWorkflowPauseStore`` before returning it. Everything else
(``attempt_resume``, the snapshot composition + ``snapshot_hash``) is inherited
unchanged.

Subclassing (not wrapping) is deliberate: the frozen ``HarnessContext``
``pause_resume_protocol`` field is ``is_instance_of``-validated as
``PauseResumeProtocol``, and the workflow driver consumes the protocol through a
duck-``cast`` — a subclass satisfies BOTH with **no edit to the frozen-context
field nor to the workflow driver** (design §7b runtime-only posture).

Resume reads happen at the ``api.resume`` boundary (a fresh
``JournalWorkflowPauseStore`` over the resolved journal dir resolved purely from
``config``, so it works across a restart), NOT inside ``attempt_resume`` —
``attempt_resume`` is the in-driver resume-admission gate and is inherited
verbatim. This subclass therefore only adds the *write* side (persist-on-capture);
the read side lives at the ``api.resume`` boundary.

Authority: runtime spec v1.46 §14.14 (durable variant of the C-RT-24
PauseResumeProtocol factory output); design
``r-cc-1-arc-3-workflow-durable-resume-design-v1.md`` §7b.

``B-103``: the journaling call is dispatched OFF the event loop — see
:meth:`DurablePauseResumeProtocol.capture_pause_snapshot`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness_cp.pause_resume_protocol import PauseContextReader, PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import (
    EffectFenceResumeState,
    EvaluatorOptimizerResumeState,
    FanOutResumeState,
    HandoffResumeState,
    OrchestratorEffectFencePausedResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    WorkflowPauseReason,
)

from harness_runtime.lifecycle.audit_offload import run_pause_journal_off_loop

if TYPE_CHECKING:
    from harness_runtime.lifecycle.journal_workflow_pause_store import (
        JournalWorkflowPauseStore,
    )

__all__ = ["DurablePauseResumeProtocol"]


class DurablePauseResumeProtocol(PauseResumeProtocol):
    """A ``PauseResumeProtocol`` that durably persists captured snapshots.

    Constructed by the stage-5 factory with the same constructor refs as the
    bare CP protocol plus a ``JournalWorkflowPauseStore`` (co-located under the
    resolved ``STATE_LEDGER`` dir). ``isinstance(self, PauseResumeProtocol)`` is
    ``True``, so the frozen ``HarnessContext`` accepts it and the workflow driver
    consumes it unchanged.
    """

    def __init__(
        self,
        *,
        state_ledger_writer: object,
        state_ledger_reader: object,
        pause_context_reader: PauseContextReader,
        store: JournalWorkflowPauseStore,
    ) -> None:
        super().__init__(
            state_ledger_writer=state_ledger_writer,
            state_ledger_reader=state_ledger_reader,
            pause_context_reader=pause_context_reader,
        )
        self._store = store

    async def capture_pause_snapshot(
        self,
        workflow_id: str,
        run_id: str,
        step_index: int,
        pause_reason: WorkflowPauseReason,
        *,
        fan_out_resume: FanOutResumeState | None = None,
        peer_fan_out_resume: PeerFanOutResumeState | None = None,
        handoff_resume: HandoffResumeState | None = None,
        evaluator_optimizer_resume: EvaluatorOptimizerResumeState | None = None,
        effect_fence_resume: EffectFenceResumeState | None = None,
        orchestrator_effect_fence_resume: OrchestratorEffectFencePausedResumeState | None = None,
        hitl_gate_config_hash: str | None = None,
    ) -> PauseSnapshot:
        """Compose the snapshot via the parent, then durably persist it.

        The snapshot is journaled BEFORE it is returned to the driver, so a crash
        after capture (but before the caller serializes the ``RunResult``) still
        leaves a resumable record on disk for ``api.resume(resume_handle=...)``.

        ``fan_out_resume`` (B-FANOUT-PAUSE, ORCHESTRATOR_WORKERS),
        ``peer_fan_out_resume`` (B-FANOUT-PAUSE-PARALLELIZATION), ``handoff_resume``
        (B-HANDOFF-PAUSE, DECENTRALIZED_HANDOFF), ``evaluator_optimizer_resume``
        (B-FANOUT-PAUSE-EVALUATOR-OPTIMIZER, EVALUATOR_OPTIMIZER), and
        ``hitl_gate_config_hash`` (B-79 impl leg slice 2, CP spec v1.111 §1.2
        property 7 — the LINEAR/EVALUATOR_OPTIMIZER/DECENTRALIZED_HANDOFF
        material-diff identity) are forwarded to the parent so a durable
        `cascade_policy=pause` snapshot carries (and journals) its resume state —
        without forwarding, the durable resume path would silently drop it (and
        the new kwarg would raise `TypeError` at the driver's capture call under
        durable config).

        **The journaling call runs OFF the event loop (`B-103`).** ``capture()``
        is synchronous and its ``_append`` takes ``cross_process_journal_lock``
        — a BLOCKING ``fcntl.flock(fd, LOCK_EX)``. Called directly from this
        ``async def`` it blocked the loop THREAD for as long as a second OS
        process held that lock: no other coroutine ran, no timer fired, the
        whole runtime stalled on one workflow's journal. Offloading moves the
        wait onto a worker; everything else about the write is byte-identical.
        This changes NEITHER of the two things `B-103` forbids — the lock's
        GRANULARITY is untouched (same per-workflow lock, same construction,
        same inode) and the READ path still takes no lock and stays sync.

        **Why not `asyncio.to_thread`.** ``to_thread`` queues onto the loop's
        DEFAULT executor, which is where the CP driver's sync
        ``execute_workflow`` already runs while awaiting loop coroutines — the
        documented exhaustion deadlock at `audit_offload`'s module docstring. A
        capture reached through that driver could queue behind the very drivers
        waiting on it and never start.

        **Why its OWN pool, not the shared audit one.** A journal-lock wait does
        not fit the audit pool's "short-lived, one sign + local writes" profile;
        four contended captures there would occupy every slot and stall
        unrelated audit-signing and ref-resolution work. Runtime spec v1.102
        §14.8.10.1 already ruled that same 4-worker pool INELIGIBLE for `B-48`'s
        offload on identical reasoning. See `run_pause_journal_off_loop`.

        **Why JOIN-on-cancel and not detach.** ``run_off_loop_detach_on_cancel``
        exists for effects with NO durability requirement (``shutdown()``'s
        opportunistic GC sweep — an incomplete one just leaves work for the next
        sweep). A pause capture is the opposite: this method's whole contract is
        that the snapshot is durable BEFORE it is returned. Joining preserves the
        ordering the pre-`B-103` synchronous call had for free. The guarantee is
        BOUNDED by ``PAUSE_JOURNAL_CANCEL_JOIN_GRACE_SECONDS``; past it the
        append may land late — a NEW window this arc introduces, registered at
        `B-105` rather than absorbed. See `run_pause_journal_off_loop` for the
        full residual statement.

        A saturated offload queue raises ``AuditSigningFailedError`` and is left
        to PROPAGATE: the pause was not journaled, and a durability failure on
        this path must be loud. Falling back to a direct synchronous call would
        silently reinstate the loop stall this method exists to remove.
        """
        snapshot = await super().capture_pause_snapshot(
            workflow_id,
            run_id,
            step_index,
            pause_reason,
            fan_out_resume=fan_out_resume,
            peer_fan_out_resume=peer_fan_out_resume,
            handoff_resume=handoff_resume,
            evaluator_optimizer_resume=evaluator_optimizer_resume,
            effect_fence_resume=effect_fence_resume,
            orchestrator_effect_fence_resume=orchestrator_effect_fence_resume,
            hitl_gate_config_hash=hitl_gate_config_hash,
        )
        await run_pause_journal_off_loop(self._store.capture, snapshot)
        return snapshot
