"""The installation's one operator-owned installation-state document (IS spec v1.17 §1.1).

Every public ingress - `api.run`/`api.resume` (and the CLI one-shot commands that call them),
the daemon and `harness-inspect` - binds `INSTALLATION_STATE` from the same fixed
per-interpreter carrier, `<sys.prefix>/etc/arhugula/installation-state.json`, so one installed
interpreter has exactly one installation state. There is no parameter, environment, cwd,
config or CLI selector and no fallback carrier (Buford cmt-4deb3aa1); the Runtime never writes
the document.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from harness_is.pause_journal_root import Unresolved, UnresolvedCause

from harness_runtime.lifecycle.pause_journal_root_resolver import (
    INSTALLATION_STATE,
    STORAGE_UNSELECTED,
    InstallationState,
)

__all__ = ["installation_state_bound", "installation_state_path", "read_installation_state"]


def installation_state_path() -> Path:
    """This interpreter's installation-state carrier."""
    return Path(sys.prefix) / "etc" / "arhugula" / "installation-state.json"


def read_installation_state() -> InstallationState | Unresolved:
    """The operator's document as raw declarations, or MALFORMED when it has no such shape.

    An absent document declares nothing (`STORAGE_UNSELECTED`, so the root resolves unbound);
    any other read failure propagates. [LAW:single-enforcer] The declarations pass through
    unjudged: the root resolver alone parses them.
    """
    try:
        content = installation_state_path().read_bytes()
    except FileNotFoundError:
        return STORAGE_UNSELECTED
    try:
        document: object = json.loads(content, object_pairs_hook=_unique_keys)
    except ValueError:
        return Unresolved(UnresolvedCause.MALFORMED)
    match document:
        # Each item's shape is the resolver's to judge (MALFORMED), so it stays unknown here.
        case {"pause_journal_root_declarations": list(declarations)}:  # pyright: ignore[reportUnknownVariableType]
            return InstallationState(tuple(declarations))  # pyright: ignore[reportUnknownArgumentType]
        case _:
            return Unresolved(UnresolvedCause.MALFORMED)


def _unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """A JSON object whose every key is distinct.

    [LAW:no-silent-failure] `json.loads` would keep only a repeated key's last value, so a second
    `pause_journal_root_declarations` could silently replace the first; it is malformed instead.
    """
    document = dict(pairs)
    if len(document) != len(pairs):
        raise ValueError("repeated JSON object key")
    return document


@contextmanager
def installation_state_bound() -> Generator[None]:
    """Bind `INSTALLATION_STATE` from the carrier for the body; restore the prior binding after.

    [LAW:no-ambient-temporal-coupling] The ingress owns the binding's lifetime: asyncio tasks
    and `to_thread` workers started in the body inherit it, and the reset runs on error too.
    """
    token = INSTALLATION_STATE.set(read_installation_state())
    try:
        yield
    finally:
        INSTALLATION_STATE.reset(token)
