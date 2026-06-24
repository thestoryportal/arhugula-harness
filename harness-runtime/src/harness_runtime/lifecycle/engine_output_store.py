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
    "ENGINE_OUTPUT_BRANCHES_SUFFIX",
    "ENGINE_OUTPUT_SUBDIR",
    "EngineOutputStore",
    "engine_output_dir_for",
]

#: Subdirectory under the resolved ``STATE_LEDGER`` directory holding the
#: per-run engine-output journals (co-location sibling of ``pause-journal``).
ENGINE_OUTPUT_SUBDIR = "engine-output"

#: Per-run directory suffix holding the CONCURRENT fan-out branch journals
#: (B-FANOUT-OUTPUT-REPLAY). The linear store keys one ``{digest}.jsonl`` FILE
#: per run (single-writer); a concurrent fan-out has N branch writers, so each
#: branch gets its OWN file under ``{digest}.branches/`` — no shared-file
#: contention (the advisor's per-branch-FILE keying). No collision with the
#: linear ``{digest}.jsonl`` file (a ``.branches`` DIR vs a ``.jsonl`` file).
ENGINE_OUTPUT_BRANCHES_SUFFIX = ".branches"


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

    # -- B-FANOUT-OUTPUT-REPLAY: concurrent-fan-out branch capture ------------
    #
    # The STORE is the SOLE authority for which-branches-completed on a fan-out
    # crash-resume: the durable F2 ledger is BINARY for a concurrent fan-out
    # (branch terminals buffer into per-branch `BufferingLedgerWriter`s and drain
    # ATOMICALLY at the barrier per CP §25.12 D1.b), so a mid-fan-out crash leaves
    # an EMPTY ledger but the per-branch journals hold the completed outputs.
    # `step_id` is recorded at CAPTURE time — the load-bearing identity that lets
    # the existing resume material-diff guard detect a changed body on replay.

    def record_branch(
        self,
        run_key: str,
        branch_index: int,
        step_id: str,
        terminal_status: str,
        output: Mapping[str, Any] | None,
    ) -> None:
        """Append one branch terminal-DISPOSITION record to the branch's OWN file, durably.

        The store records the branch's terminal **disposition** (``completed`` /
        ``timed_out``) for EVERY branch that reaches a terminal boundary — NOT only
        output-bearing clean successes — so a crash-resume can distinguish recover-and-fold
        (``completed`` with ``output``), recover-as-terminal (``completed`` with ``output is
        None`` — a ran-and-errored branch whose effect LANDED, never re-dispatched, never
        folded), and the irreducibly-ambiguous ``timed_out`` (a deadline-cut in-flight
        dispatch may or may not have landed → the caller FAILS CLOSED). An output-only
        schema made every non-clean-success disposition invisible (the at-most-once
        fail-open class); recording disposition closes it.

        Per-branch file (``{digest}.branches/branch-{branch_index}.jsonl``) so N concurrent
        branch writers never contend on a shared handle. RESERVE-before-COMMIT: the caller
        fsyncs this BEFORE the branch's terminal ledger-append, so the store always holds
        >= the (binary) ledger's committed branch set.
        """
        record = {
            "step_id": str(step_id),
            "terminal_status": str(terminal_status),
            "output": dict(output) if output is not None else None,
        }
        line = json.dumps(record, sort_keys=True)
        self._append_path(self._branch_file(run_key, branch_index), line)

    def read_branch_records(
        self, run_key: str
    ) -> dict[int, tuple[str, str, dict[str, Any] | None]]:
        """Return ``{branch_index: (step_id, terminal_status, output | None)}`` for every
        READABLE branch.

        Empty when no fan-out branch journals exist (config flip / first run). The
        ``branch_index`` is the filename authority (``branch-{n}.jsonl``); a present but
        UNREADABLE branch file is omitted here and surfaced by `present_branch_indexes` so
        the caller fails closed (never silently re-dispatching a corrupt branch). ``output``
        is ``None`` for a terminal-no-output branch (ran-and-errored / timed-out).
        """
        branches_dir = self._branches_dir(run_key)
        if not branches_dir.exists():
            return {}
        records: dict[int, tuple[str, str, dict[str, Any] | None]] = {}
        for path in branches_dir.glob("branch-*.jsonl"):
            branch_index = self._branch_index_from_name(path.name)
            if branch_index is None:
                continue
            parsed = self._read_last_branch_disposition(path)
            if parsed is not None:
                records[branch_index] = parsed
        return records

    def present_branch_indexes(self, run_key: str) -> set[int]:
        """Return the set of branch ordinals whose journal FILE exists (any state).

        The fail-closed discriminator (the branch-level analogue of
        `journal_exists`): ``present_branch_indexes - read_branch_outputs.keys()``
        is the set of branch files that EXIST but yield no readable record — a
        corrupt branch the caller must fail closed on rather than re-dispatch.
        """
        branches_dir = self._branches_dir(run_key)
        if not branches_dir.exists():
            return set()
        indexes: set[int] = set()
        for path in branches_dir.glob("branch-*.jsonl"):
            branch_index = self._branch_index_from_name(path.name)
            if branch_index is not None:
                indexes.add(branch_index)
        return indexes

    def record_orchestrator(
        self,
        run_key: str,
        step_id: str,
        output: Mapping[str, Any],
    ) -> None:
        """Capture the ORCHESTRATOR_WORKERS ``steps[0]`` output (not a branch).

        The orchestrator output rides the `FanOutResumeState.orchestrator_output`
        field on resume; captured to a dedicated ``orchestrator.jsonl`` under the
        branches dir so it does not collide with the ``branch-*`` worker files.
        """
        record = {"step_id": str(step_id), "output": dict(output)}
        line = json.dumps(record, sort_keys=True)
        self._append_path(self._orchestrator_file(run_key), line)

    def read_orchestrator_output(self, run_key: str) -> tuple[str, dict[str, Any]] | None:
        """Return the captured ``(step_id, output)`` orchestrator record, or None.

        None means ABSENT (no orchestrator captured). A present-but-unreadable
        orchestrator file is surfaced by `orchestrator_present` so the caller fails
        closed (the symmetric of the per-branch corrupt-detection).
        """
        path = self._orchestrator_file(run_key)
        if not path.exists():
            return None
        return self._read_last_branch_record(path)

    def orchestrator_present(self, run_key: str) -> bool:
        """Whether an orchestrator journal FILE exists (regardless of readability)."""
        return self._orchestrator_file(run_key).exists()

    # -- durable journal I/O (mirrors JournalWorkflowPauseStore) --------------

    @staticmethod
    def _digest(run_key: str) -> str:
        """The filesystem-safe, collision-free per-run name component."""
        return hashlib.sha256(run_key.encode("utf-8")).hexdigest()

    def _journal_file(self, run_key: str) -> Path:
        """The per-run LINEAR journal file (filesystem-safe, collision-free name)."""
        return self._journal_dir / f"{self._digest(run_key)}.jsonl"

    def _branches_dir(self, run_key: str) -> Path:
        """The per-run directory holding the CONCURRENT fan-out branch journals."""
        return self._journal_dir / f"{self._digest(run_key)}{ENGINE_OUTPUT_BRANCHES_SUFFIX}"

    def _branch_file(self, run_key: str, branch_index: int) -> Path:
        """The per-branch journal file under the run's branches dir."""
        return self._branches_dir(run_key) / f"branch-{int(branch_index)}.jsonl"

    def _orchestrator_file(self, run_key: str) -> Path:
        """The ORCHESTRATOR_WORKERS ``steps[0]`` journal under the branches dir."""
        return self._branches_dir(run_key) / "orchestrator.jsonl"

    @staticmethod
    def _branch_index_from_name(name: str) -> int | None:
        """Parse ``branch-{n}.jsonl`` → ``n``; None for any other filename."""
        prefix, suffix = "branch-", ".jsonl"
        if not (name.startswith(prefix) and name.endswith(suffix)):
            return None
        try:
            return int(name[len(prefix) : -len(suffix)])
        except ValueError:
            return None

    def _read_last_branch_record(self, path: Path) -> tuple[str, dict[str, Any]] | None:
        """Return the last readable ``(step_id, output)`` in a branch/orchestrator file.

        ``None`` when the file is unreadable or holds no parseable record (corrupt) —
        the caller's presence-vs-readability check is the fail-closed gate. A torn
        trailing line is skipped; a later record for the same file wins (idempotent
        re-record), mirroring the linear `read_outputs` last-wins discipline.
        """
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        result: tuple[str, dict[str, Any]] | None = None
        for line in text.splitlines():
            if not line.strip():
                continue
            parsed = self._parse_branch_record(line)
            if parsed is not None:
                result = parsed
        return result

    def _read_last_branch_disposition(
        self, path: Path
    ) -> tuple[str, str, dict[str, Any] | None] | None:
        """Return the last readable ``(step_id, terminal_status, output | None)`` in a
        branch file (the disposition-bearing branch reader; the orchestrator stays on the
        2-field `_read_last_branch_record`).

        ``None`` when unreadable / no parseable record (the presence-vs-readability
        fail-closed gate). Torn trailing line skipped; later record wins. ``output`` may be
        ``None`` (a terminal-no-output branch). ``terminal_status`` defaults to ``completed``
        when absent (keeps the parser total)."""
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        result: tuple[str, str, dict[str, Any] | None] | None = None
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                loaded = json.loads(line)
            except (ValueError, TypeError):
                continue
            if not isinstance(loaded, dict):
                continue
            record = cast("dict[str, object]", loaded)
            step_id = record.get("step_id")
            terminal_status = record.get("terminal_status", "completed")
            output = record.get("output")
            if not isinstance(step_id, str) or not isinstance(terminal_status, str):
                continue
            if output is not None and not isinstance(output, dict):
                continue
            result = (step_id, terminal_status, cast("dict[str, Any] | None", output))
        return result

    @staticmethod
    def _parse_branch_record(line: str) -> tuple[str, dict[str, Any]] | None:
        """Parse one branch/orchestrator line into ``(step_id, output)`` or ``None``."""
        try:
            loaded = json.loads(line)
            if not isinstance(loaded, dict):
                return None
            record = cast("dict[str, object]", loaded)
            step_id = record["step_id"]
            output = record["output"]
            if not isinstance(step_id, str) or not isinstance(output, dict):
                return None
            return (step_id, cast("dict[str, Any]", output))
        except (ValueError, KeyError, TypeError):
            return None

    def _append(self, run_key: str, line: str) -> None:
        """Append one JSONL record to the run's LINEAR file, durably."""
        self._append_path(self._journal_file(run_key), line)

    def _append_path(self, path: Path, line: str) -> None:
        """Append one JSONL record to ``path``, durably (fsync-ed).

        The record is ``fsync``-ed before returning so a host crash after a
        ``record`` cannot lose an already-written output. Directory-fsyncs persist
        the new dirents (best-effort POSIX). Torn-append self-healing: a leading
        newline separates a prior crash's partial trailing line so it becomes its
        own (skipped) line rather than corrupting the next record. (Mirrors the
        pause-journal hardenings caught by out-of-family Codex.)
        """
        journal_dir = path.parent
        # The chain of not-yet-existing ancestor directories `mkdir(parents=True)` will
        # create (deepest first). A single mkdir for the first fan-out sidecar write can
        # create BOTH the `{digest}.branches` per-run dir AND the top-level `engine-output`
        # dir; fsyncing only the leaf loses an intermediate dir's dirent on a host crash
        # even though `record_branch` returned (out-of-family Codex [P2]). Each new dir's
        # dirent lives in ITS parent → fsync every new dir's parent below.
        new_dirs: list[Path] = []
        probe = journal_dir
        while not probe.exists():
            new_dirs.append(probe)
            if probe.parent == probe:
                break
            probe = probe.parent
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
        for new_dir in new_dirs:
            self._fsync_dir(new_dir.parent)

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
