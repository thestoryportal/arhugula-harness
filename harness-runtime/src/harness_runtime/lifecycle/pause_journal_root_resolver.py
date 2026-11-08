"""U-RT-160b: the one Runtime pause-journal root resolver (Runtime spec v1.137 Rules B3/B7).

Capture, the pre-bootstrap read, the root claim and the fresh-run supersession append all take
their journal directory from `resolve_pause_journal_root`, so no site derives it from a run's
STATE_LEDGER binding. The installation-state declaration is read from `INSTALLATION_STATE`, the
process's one installation-state source, which each public ingress binds from the operator's
document (`installation_state`). Until the operator declares a root the document is absent, the
value is `STORAGE_UNSELECTED`, which declares nothing and resolves `unbound`: every journal site
fails closed until storage is bound.

The decision is U-IS-21's pure `harness_is.pause_journal_root`; this module only observes the
filesystem for it and turns an unresolved result into a typed refusal.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from harness_is.pause_journal_root import (
    ExistingDirectory,
    NotADirectory,
    ObservedRoot,
    PauseJournalRootDeclaration,
    Resolved,
    Unresolved,
    UnresolvedCause,
    parse_declarations,
    resolve_root,
)

from harness_runtime.config.path_bindings import build_path_binding

if TYPE_CHECKING:
    from harness_runtime.types import RuntimeConfig

__all__ = [
    "INSTALLATION_STATE",
    "STORAGE_UNSELECTED",
    "InstallationState",
    "PauseJournalRootUnresolvedError",
    "installation_root_declaration",
    "resolve_pause_journal_root",
]


@dataclass(frozen=True)
class InstallationState:
    """The installation-state facts the root resolver reads: its raw root declarations."""

    pause_journal_root_declarations: tuple[Mapping[str, object], ...]


STORAGE_UNSELECTED: Final = InstallationState(pause_journal_root_declarations=())
"""No retained storage is selected, so nothing is declared (Buford cmt-8b76cb48: fail closed)."""

# [LAW:no-shared-mutable-globals] One owner: each public ingress binds it from the operator's
# document (`installation_state_bound`); asyncio tasks and `to_thread` workers inherit the
# binding, and nothing else writes it. An unreadable document is carried as its typed cause.
INSTALLATION_STATE: Final[ContextVar[InstallationState | Unresolved]] = ContextVar(
    "INSTALLATION_STATE", default=STORAGE_UNSELECTED
)


class PauseJournalRootUnresolvedError(Exception):
    """The installation has no usable pause-journal root; no journal site may proceed.

    `cause` is diagnostic only (C-IS-01 §1.1); the message names it, never a path.
    """

    def __init__(self, cause: UnresolvedCause) -> None:
        super().__init__(
            f"the installation's pause-journal root is unresolved ({cause.value}) "
            "(Runtime spec v1.137 Rule B7)"
        )
        self.cause: Final = cause


def installation_root_declaration() -> PauseJournalRootDeclaration | Unresolved:
    """The bound installation state's one root declaration, or why there is none."""
    match INSTALLATION_STATE.get():
        case InstallationState(pause_journal_root_declarations=raw):
            return parse_declarations(raw)
        case Unresolved() as unreadable:
            return unreadable


def resolve_pause_journal_root(config: RuntimeConfig) -> Path:
    """The installation's pause-journal root as a real path, or `PauseJournalRootUnresolvedError`.

    `config` contributes only its bound path-binding directories, which can make resolution
    fail as overlapping but never choose the root.
    """
    match installation_root_declaration():
        case Unresolved(cause=cause):
            raise PauseJournalRootUnresolvedError(cause)
        case declaration:
            pass
    bound_real_paths = (
        Path(os.path.realpath(entry.path))
        for entry in build_path_binding(config.path_bindings).entries
    )
    real_root = Path(os.path.realpath(declaration.installation_root))
    observed: ObservedRoot = ExistingDirectory(real_root) if real_root.is_dir() else NotADirectory()
    match resolve_root(declaration, observed, bound_real_paths):
        case Resolved():
            # [LAW:one-source-of-truth] The directory whose overlap was just judged, observed
            # once: a declared symlink retargeted later cannot re-address this resolution.
            return real_root
        case Unresolved(cause=cause):
            raise PauseJournalRootUnresolvedError(cause)
