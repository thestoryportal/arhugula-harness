"""Pre-bootstrap sink for the two §C-OD-30.5 events (OD spec v1.36 §30.5.2).

`B-69` impl leg. Both events — the §14.14.9 accessor read and a `resume()` refused
on the §30 staleness precondition — fire on the **first crash-recovery call in a
fresh process**, while the SDK ``TracerProvider`` and the audit writers are created
*during* bootstrap. A default no-op / proxy provider **records nothing**, so an
implementation that emits and moves on would satisfy the letter of §30.5.1 and
§30.5.2 while producing no telemetry at all — defeating both the no-silent-failure
rule and §30.5.3's causal-pair reconstruction, on the exact path this arc exists to
serve.

**The mechanism chosen, of the three §30.5.2 authorizes.** A minimal pre-bootstrap
audit initialization these two events can use: an append-only JSONL sink under the
resolved ``STATE_LEDGER`` directory, resolved purely from ``config`` +
``workflow.workload_class`` via ``PathResolver`` with no bootstrap side effects —
the SAME resolution the pause journal itself uses, and for the same reason (a fresh
process must find what a prior process wrote). Rejected alternatives: a deferred
buffer drained by the next bootstrap loses every event of a run that refuses
pre-bootstrap and never bootstraps at all (which is *every* staleness refusal);
an in-memory sink is not retrievable across the process boundary the witness
obligation names.

**No new ``PathClass``.** Like the pause journal (§14.14.8 residence note), this is
harness-internal audit substrate, not one of the four canonical *artifact* classes
the ``PathClass`` registry enumerates — IS-AL-1 forecloses inventing a canonical
artifact class, not co-locating an internal file.

Authority: `Spec_Operational_Discipline_v1_36.md` §C-OD-30.5;
`Spec_Harness_Runtime_v1.md` v1.107 §14.14.9.5 (trace emission REQUIRED on BOTH
outcomes, content SPLIT BY OUTCOME).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from harness_od.pause_resume_namespace import PauseStateAuditPayload
from pydantic import ValidationError

if TYPE_CHECKING:
    from harness_core.workload_class import WorkloadClass

    from harness_runtime.types import RuntimeConfig

__all__ = [
    "PAUSE_STATE_AUDIT_FILENAME",
    "PAUSE_STATE_AUDIT_SUBDIR",
    "PreBootstrapPauseStateSink",
    "pause_state_audit_dir_for",
    "pause_state_sink_for",
]

#: Subdirectory under the resolved ``STATE_LEDGER`` directory holding the sink.
PAUSE_STATE_AUDIT_SUBDIR = "pause-state-audit"

#: The single append-only sink file within that subdirectory.
PAUSE_STATE_AUDIT_FILENAME = "events.jsonl"


def pause_state_audit_dir_for(state_ledger_dir: Path) -> Path:
    """The §C-OD-30.5 sink directory co-located under the STATE_LEDGER dir."""
    return state_ledger_dir / PAUSE_STATE_AUDIT_SUBDIR


class PreBootstrapPauseStateSink:
    """An append-only, ``fsync``-ed JSONL sink for §C-OD-30.5 payloads.

    Deliberately tiny and dependency-free: it must work with NO ``HarnessContext``,
    NO ``TracerProvider`` and NO audit writer in existence.
    """

    def __init__(self, *, sink_dir: Path) -> None:
        self._sink_dir = Path(sink_dir)

    @property
    def path(self) -> Path:
        """The sink file this instance appends to / reads from."""
        return self._sink_dir / PAUSE_STATE_AUDIT_FILENAME

    def emit(self, payload: PauseStateAuditPayload) -> None:
        """Append one payload durably. Never silent: a write failure propagates."""
        line = json.dumps(payload.model_dump(mode="json"), sort_keys=True)
        self._sink_dir.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def read_all(self) -> tuple[PauseStateAuditPayload, ...]:
        """Every payload retrievable from the sink, oldest first.

        This is what the §30.5.2 witness obligation asserts against — the events
        must be **retrievable from a real sink**, never merely "an emit was
        invoked" against a proxy provider.
        """
        path = self.path
        if not path.exists():
            return ()
        rows: list[PauseStateAuditPayload] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(PauseStateAuditPayload.model_validate_json(line))
            except ValidationError:  # pragma: no cover — a torn trailing append
                continue
        return tuple(rows)


def pause_state_sink_for(
    config: RuntimeConfig, workload_class: WorkloadClass
) -> PreBootstrapPauseStateSink:
    """Resolve the sink for a workload PURELY from config — no bootstrap needed.

    Mirrors ``api._read_durable_pause_snapshot``'s own resolution so a capture-side
    process and a fresh crash-recovery process agree on the location.
    """
    from harness_is.path_class_registry import PathClass
    from harness_is.path_resolver import PathResolver

    from harness_runtime.config.path_bindings import build_path_binding

    resolver = PathResolver(build_path_binding(config.path_bindings))
    state_ledger_dir = resolver.resolve_path(
        PathClass.STATE_LEDGER,
        workload_class,
        config.deployment_surface,
    )
    return PreBootstrapPauseStateSink(sink_dir=pause_state_audit_dir_for(state_ledger_dir))
