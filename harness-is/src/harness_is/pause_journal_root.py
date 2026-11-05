"""Installation pause-journal root: declaration and closed resolution — U-IS-21.

Implements C-IS-01 §1.1 (IS spec v1.17), the companion to Runtime spec v1.137
Rule B7. Every process of one Runtime installation resolves the same pause-journal
root from one installation-state declaration, whatever its run's path bindings.
The root is deliberately not a `PathClass`, so no `path_bindings` entry can name,
bind or override it, and resolution takes no tenant input: tenants stay separated
by the Runtime journal key inside the one flat root (Runtime spec v1.108 §14.14.8).

This module is the pure decision only. The Runtime root resolver (U-RT-160 portion
160a) reads the installation state, observes the declared directory and the run's
bound §1 directories by real path, and enforces the result.

Authority: Implementation_Plan_Information_Substrate_v2_11.md §1 U-IS-21;
Spec_Information_Substrate_v1.md §1.1 (v1.17).
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePath

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class UnresolvedCause(StrEnum):
    """Why an installation has no usable pause-journal root (C-IS-01 §1.1).

    Diagnostic only: the Runtime refusal value does not carry it.
    """

    UNBOUND = "unbound"
    MALFORMED = "malformed"
    CONFLICTING = "conflicting"
    MISSING = "missing"
    OVERLAPPING = "overlapping"


class PauseJournalRootDeclaration(BaseModel):
    """The one installation-state declaration of the pause-journal root."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    installation_root: Path

    @field_validator("installation_root", mode="before")
    @classmethod
    def _absolute_and_normalized(cls, value: object) -> object:
        # [LAW:parse-dont-validate] The raw text is checked before `Path` would
        # silently normalize it, so a declaration such as `/srv/pj/` or `/srv/./pj`
        # is malformed rather than quietly rewritten into a different-looking root.
        text = str(value) if isinstance(value, PurePath) else value
        if (
            not isinstance(text, str)
            or "\x00" in text
            or not os.path.isabs(text)
            or os.path.normpath(text) != text
        ):
            raise ValueError("installation_root must be one absolute, normalized path")
        return text


@dataclass(frozen=True)
class ExistingDirectory:
    """The declared root exists as a directory at this observed real path."""

    real_path: Path


@dataclass(frozen=True)
class NotADirectory:
    """The declared root is absent or is not a directory."""


ObservedRoot = ExistingDirectory | NotADirectory


@dataclass(frozen=True)
class Resolved:
    """The installation's one pause-journal root, as declared."""

    root: Path


@dataclass(frozen=True)
class Unresolved:
    """No usable root; every journal read, write, append and claim must refuse."""

    cause: UnresolvedCause


PauseJournalRootResolution = Resolved | Unresolved


def parse_declarations(
    raw: Sequence[Mapping[str, object]],
) -> PauseJournalRootDeclaration | Unresolved:
    """Parse the installation state's declarations into exactly one, or a cause.

    Two equal declarations still conflict: cardinality is part of the contract,
    so a duplicated entry is a provisioning fault to surface, not to collapse.
    """
    # [LAW:no-defensive-null-guards] Absence is the typed UNBOUND arm; there is no
    # default or STATE_LEDGER-derived root to fall back to (Runtime Rule B8).
    match raw:
        case []:
            return Unresolved(UnresolvedCause.UNBOUND)
        case [single]:
            try:
                return PauseJournalRootDeclaration.model_validate(single)
            except ValidationError:
                return Unresolved(UnresolvedCause.MALFORMED)
        case _:
            return Unresolved(UnresolvedCause.CONFLICTING)


def resolve_root(
    declaration: PauseJournalRootDeclaration,
    observed: ObservedRoot,
    bound_real_paths: Iterable[Path],
) -> PauseJournalRootResolution:
    """Decide the root from the declaration and the Runtime's observations.

    Bound paths can only make resolution fail; they never choose the root, so two
    processes of one installation either obtain the same root or fail.
    """
    match observed:
        case NotADirectory():
            return Unresolved(UnresolvedCause.MISSING)
        case ExistingDirectory(real_path=root_real_path):
            # [LAW:types-are-the-program] Only observed real paths are compared, so a
            # declared symlink alias of, or into, a bound directory overlaps.
            if any(_nested(root_real_path, bound) for bound in bound_real_paths):
                return Unresolved(UnresolvedCause.OVERLAPPING)
            return Resolved(declaration.installation_root)


def _nested(first: Path, second: Path) -> bool:
    """Whether either real path equals or lies inside the other."""
    return first.is_relative_to(second) or second.is_relative_to(first)
