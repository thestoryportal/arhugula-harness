"""Runtime engine recovery loop producer for R-CXA-2.

Authority: C-CP-22 engine-layer pause/resume free functions, U-CP-78
`cp.pause-captured`, and U-CP-79 `cp.resume-attempted`.
"""

from __future__ import annotations

from dataclasses import dataclass

from harness_core import WorkflowID
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.pause_resume_protocol import (
    EnginePauseResumeSubstrate,
    PauseEvent,
    PauseReason,
    ResumeAttempt,
    ResumeOutcome,
    attempt_resume,
    bind_engine_pause_resume_substrate,
    capture_pause_snapshot,
)
from harness_is.state_ledger_write import WriteResult

from harness_runtime.lifecycle.cp_is_wiring import RuntimeCpIsWiring


@dataclass(frozen=True, slots=True)
class EnginePauseCaptureEmission:
    """Pause capture plus its CP→IS write result."""

    pause_event: PauseEvent
    write_result: WriteResult


@dataclass(frozen=True, slots=True)
class EngineResumeAttemptEmission:
    """Resume outcome plus its CP→IS write result."""

    resume_outcome: ResumeOutcome
    write_result: WriteResult


@dataclass(frozen=True, slots=True)
class RuntimeEngineRecoveryLoop:
    """Bind an engine substrate and emit R-CXA-2 engine-layer ledger entries."""

    wiring: RuntimeCpIsWiring
    substrate: EnginePauseResumeSubstrate
    actor: ActorIdentity

    async def capture_pause(
        self,
        *,
        workflow_id: str,
        step_id: str,
        pause_reason: PauseReason,
    ) -> EnginePauseCaptureEmission:
        """Capture an engine-layer pause and emit `cp.pause-captured`."""
        with bind_engine_pause_resume_substrate(self.substrate):
            pause_event = capture_pause_snapshot(WorkflowID(workflow_id), pause_reason)

        write_result = await self.wiring.emit_pause_captured_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            pause_event=pause_event,
            actor=self.actor,
        )
        return EnginePauseCaptureEmission(
            pause_event=pause_event,
            write_result=write_result,
        )

    async def attempt_resume(
        self,
        *,
        workflow_id: str,
        step_id: str,
        resume_event_id: str,
        resume_attempt_count: int,
        resume_at: str,
        resume_request_actor: ActorIdentity | None = None,
    ) -> EngineResumeAttemptEmission:
        """Attempt engine-layer resume and emit `cp.resume-attempted`."""
        attempt = ResumeAttempt(
            paused_workflow_id=WorkflowID(workflow_id),
            resume_at=resume_at,
            resume_request_actor=resume_request_actor or self.actor,
        )
        with bind_engine_pause_resume_substrate(self.substrate):
            resume_outcome = attempt_resume(attempt)

        write_result = await self.wiring.emit_resume_attempted_state_ledger_entry(
            workflow_id=workflow_id,
            step_id=step_id,
            resume_event_id=resume_event_id,
            resume_attempt_count=resume_attempt_count,
            resume_outcome=resume_outcome,
            actor=self.actor,
        )
        return EngineResumeAttemptEmission(
            resume_outcome=resume_outcome,
            write_result=write_result,
        )
