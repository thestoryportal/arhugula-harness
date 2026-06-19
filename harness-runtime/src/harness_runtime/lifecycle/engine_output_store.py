"""Durable per-run output-carrying event-history store (B-ENGINE-OUTPUT-REPLAY).

R-FS-1 standalone `B-*` arc **B-ENGINE-OUTPUT-REPLAY** (design-fork-first per
X-AL-3). Materializes the C-CP-08 §8.1 `engine_replay` "**activity outputs cached
and replayed**" clause that EVENT_SOURCED_REPLAY ships DEGENERATE today (the
"no re-execution of activities" clause is already delivered as skip-prefix; see
`.harness/r-fs-1-e-impl-1-finding.md` §2).

Why a dedicated store (not the IS F2 ledger)
--------------------------------------------
The F2 IS state-ledger (`harness_is.state_ledger_write.EntryPayload`, C-IS-07
§7.1) carries only a `response_hash` **digest** — never the activity output, by
design (the ledger is causality + integrity, not data storage). Extending the
`EntryPayload` to carry outputs would ripple the C-IS-05 §5.2 entry hash + the
JSONL shape + the IS contract for a CP/runtime-local replay concern — foreclosed
by I-6 (hand-roll, no vendored event-sourcing framework) + ADR-F2 (the ledger's
six-field shape is frozen). So the output history lives in a dedicated, harness-
owned store, mirroring the crash-survivable journal mechanism proven in
`JournalWorkflowPauseStore` (#475 → R-CC-1 arc #3): per-key JSONL file, `fsync` +
directory-fsync, torn-append self-healing, fail-closed-on-corruption.

The store ↔ ledger skew discipline (the load-bearing correctness rule)
----------------------------------------------------------------------
Two durable substrates now record per step: the **F2 ledger** (the `resume_at`
authority — the count of contiguous materialized steps) and **this store** (the
data). A crash between them de-syncs them, so the producer writes here BEFORE the
ledger-append that `resume_at` counts (`workflow_driver.py:_append_step_ledger_
entry`) — the B-EFFECT-FENCE RESERVE-before-COMMIT shape: the store always holds
≥ the ledger's materialized prefix. Consequently a resume drives rehydration by
`resume_at` (NOT "load whatever's in the store" — the store may hold one extra
uncommitted step from a crash-after-store-before-ledger) and FAILS CLOSED if an
output is missing for a step the ledger says is materialized (corruption — the
symmetric of B-FANOUT-PAUSE's identity-mismatch fail-close).

Keying
------
One file per `run_idempotency_key` — the SAME stable id the resume join
(`_determine_resume_at`) uses (the F2 step key is `f(run_idempotency_key,
step_index)`, and an EVENT_SOURCED_REPLAY restart re-runs with the same `run_id`
→ the same `run_idempotency_key`), so a capture-side write and a fresh-bootstrap
resume-side read find the same file (restart-survival).

Residence
---------
Co-located under the bootstrap-resolved `STATE_LEDGER` dir as an
`engine-output/` subdir — harness-internal *recovery substrate* (like the
pause-journal), NOT a canonical `PathClass` artifact (IS-AL-1 forecloses
inventing a canonical artifact class, not every internal file).

Authority: runtime spec C-RT-32 (NEW); `.harness/r-fs-1-e-impl-1-finding.md` §4.
Mechanism mirrors `JournalWorkflowPauseStore`.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

__all__ = [
    "ENGINE_OUTPUT_SUBDIR",
    "EngineOutputStore",
    "engine_output_dir_for",
]

#: Subdirectory under the resolved ``STATE_LEDGER`` directory holding the
#: per-run engine-output journals (co-location sibling of ``pause-journal``).
ENGINE_OUTPUT_SUBDIR = "engine-output"


def engine_output_dir_for(state_ledger_dir: Path) -> Path:
    """Return the engine-output directory co-located under the STATE_LEDGER dir.

    The single source of truth for the journal directory location, consumed by
    BOTH the stage-5 factory (deriving ``state_ledger_dir`` from the ledger
    writer handle) and the resume path — both compute the same path for the same
    ``(workflow_class, deployment_surface)``, so a capture-side write and a
    fresh-bootstrap resume-side read find the same file (restart-survival).
    """
    return state_ledger_dir / ENGINE_OUTPUT_SUBDIR


class EngineOutputStore:
    """Durable append-only per-run step-output journal (output-carrying history).

    ``record(run_key, step_index, step_id, output)`` appends one JSONL line to the
    run's ``<journal_dir>/<sha256(run_key)>.jsonl`` file (durably, ``fsync``-ed).
    ``read_outputs(run_key)`` reads every parseable line back into a
    ``{step_index: (step_id, output)}`` map (last-wins per index; an unparseable
    torn line is skipped). The caller (the resume rehydration site) validates
    prefix completeness against ``resume_at`` and fails closed on a gap.
    """

    def __init__(self, *, journal_dir: Path) -> None:
        self._journal_dir = Path(journal_dir)

    def record(
        self,
        run_key: str,
        step_index: int,
        step_id: str,
        output: Mapping[str, Any],
    ) -> None:
        """Append one step-output record to the run's file, durably (fsync-ed)."""
        record = {
            "step_index": int(step_index),
            "step_id": str(step_id),
            "output": dict(output),
        }
        # Deterministic, sorted-key serialization (mirrors the pause journal). The
        # output Mapping is the dispatcher's already-produced opaque value; the
        # store does NOT introspect it (the §25.3.3.4 step-body-opaque discipline).
        line = json.dumps(record, sort_keys=True)
        self._append(run_key, line)

    def read_outputs(self, run_key: str) -> dict[int, tuple[str, dict[str, Any]]]:
        """Return ``{step_index: (step_id, output)}`` for every parseable record.

        Empty when the run has no journal file. A torn trailing line (crash mid-
        append) is SKIPPED (it is the uncommitted step `resume_at` ignores anyway);
        a later record for the same `step_index` wins (idempotent re-record). The
        caller checks prefix completeness against `resume_at` (fail-closed on a gap).
        """
        path = self._journal_file(run_key)
        if not path.exists():
            return {}
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            # A read-level failure (incl. invalid-UTF-8) yields no recoverable
            # outputs → the caller's prefix-completeness check fails closed.
            return {}
        outputs: dict[int, tuple[str, dict[str, Any]]] = {}
        for line in text.splitlines():
            if not line.strip():
                continue
            parsed = self._parse_record(line)
            if parsed is not None:
                step_index, step_id, output = parsed
                outputs[step_index] = (step_id, output)
        return outputs

    def journal_exists(self, run_key: str) -> bool:
        """Whether a journal FILE exists for the run (regardless of readability).

        The resume rehydration uses this to discriminate, when `read_outputs`
        returns empty, between "no journal at all" (a config flip — the original run
        had `engine_output_replay=False`, so nothing was ever recorded → degrade to
        the empty-channel path) and "a journal exists but yields no readable records"
        (an unreadable / corrupt store → fail closed, never silently drop cached
        outputs). Per-decorrelated-review: advisor caught the config-flip degrade,
        Codex caught that a read-failure must NOT be collapsed into it."""
        return self._journal_file(run_key).exists()

    # -- durable journal I/O (mirrors JournalWorkflowPauseStore) --------------

    def _journal_file(self, run_key: str) -> Path:
        """The per-run journal file (filesystem-safe, collision-free name)."""
        digest = hashlib.sha256(run_key.encode("utf-8")).hexdigest()
        return self._journal_dir / f"{digest}.jsonl"

    def _append(self, run_key: str, line: str) -> None:
        """Append one JSONL record to the run's file, durably.

        The record is ``fsync``-ed before returning so a host crash after a
        ``record`` cannot lose an already-written output. Directory-fsyncs persist
        the new dirents (best-effort POSIX). Torn-append self-healing: a leading
        newline separates a prior crash's partial trailing line so it becomes its
        own (skipped) line rather than corrupting the next record. (Mirrors the
        pause-journal hardenings caught by out-of-family Codex.)
        """
        path = self._journal_file(run_key)
        journal_dir = path.parent
        dir_is_new = not journal_dir.exists()
        journal_dir.mkdir(parents=True, exist_ok=True)
        is_new_file = not path.exists()
        needs_leading_newline = (not is_new_file) and self._last_byte_is_not_newline(path)
        with path.open("a", encoding="utf-8") as handle:
            if needs_leading_newline:
                handle.write("\n")
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if is_new_file:
            self._fsync_dir(journal_dir)
        if dir_is_new:
            self._fsync_dir(journal_dir.parent)

    @staticmethod
    def _last_byte_is_not_newline(path: Path) -> bool:
        """Return ``True`` iff the file's last byte is not ``\\n`` (a torn append)."""
        try:
            with path.open("rb") as handle:
                handle.seek(-1, os.SEEK_END)
                return handle.read(1) != b"\n"
        except OSError:
            return True

    @staticmethod
    def _fsync_dir(directory: Path) -> None:
        """fsync a directory so a freshly-created file's dirent is durable.

        Best-effort: directory fsync is unsupported on some platforms/filesystems,
        where it is a no-op rather than a failure.
        """
        try:
            dir_fd = os.open(directory, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
        finally:
            os.close(dir_fd)

    @staticmethod
    def _parse_record(line: str) -> tuple[int, str, dict[str, Any]] | None:
        """Parse one journal line into ``(step_index, step_id, output)`` or ``None``.

        A corrupt / torn line returns ``None`` (skipped) — fail soft per-line; the
        caller's prefix-completeness check is the fail-closed gate for a MISSING
        committed step.
        """
        try:
            loaded = json.loads(line)
            if not isinstance(loaded, dict):
                return None
            record = cast("dict[str, object]", loaded)
            step_index = record["step_index"]
            step_id = record["step_id"]
            output = record["output"]
            if (
                not isinstance(step_index, int)
                or isinstance(step_index, bool)
                or not isinstance(step_id, str)
                or not isinstance(output, dict)
            ):
                return None
            return (step_index, step_id, cast("dict[str, Any]", output))
        except (ValueError, KeyError, TypeError):
            return None
