#!/usr/bin/env python3
"""WO-U24 / WS-01 §3.2 — the live facts behind `workflow_policy.SelectionFacts`.

`trial_relation` is pure: the relation of one unit to the trial root in a native
`lit export` of the trial's store, following its `parent-child` edges (child -> parent).
`observe_trial_relation` is its one effect, that export at the canonical root. A unit whose
chain reaches the trial root is `confirmed`; one whose chain ends at another root is
`contradicted` (LIT verifies it is unrelated); a failed read, a malformed export, an absent
unit, a unit with two parents or a cycle is `unknown`, which `select_profile` holds.

`observe_admission` is the native admission of one operation on a unit. Under the paired
workflow its authority is the orchestration checkout's own judgment
(`ops/orchestration/selection_facts.py`: the live LIT claim, the routed roster and the acting
session's measured context), so this module runs that script and accepts only its one
observation line. Anything else — a missing checkout, a failed or slow run, extra or
malformed output — is `unknown`.

The module is stdlib-only and imports nothing else from `tools/`: the commit gate loads its
callers as the `tools` package under `python3 -I`, the merge door as flat modules, and both
must reach it. The callers pass `workflow_policy.CANONICAL_ROOT` and `TRIAL_ROOT`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from tools.workflow_policy import Observation

EXPORT_VERSION = 2
PARENT_EDGE = "parent-child"
READ_TIMEOUT_SECONDS = 30
ADMISSION_SCRIPT = Path("ops") / "orchestration" / "selection_facts.py"
# The script reads its own export and each acting transcript, so it gets more than one read.
ADMISSION_TIMEOUT_SECONDS = 120
# [LAW:one-source-of-truth] exception: the values of `workflow_policy.Observation`, which this
# stdlib-only module cannot import at runtime; a test pins them equal.
OBSERVATIONS: frozenset[str] = frozenset({"confirmed", "contradicted", "unknown"})
Operation = Literal["implementation", "integration"]


@dataclass(frozen=True)
class LitTree:
    """The issue IDs of one export and each child's single parent."""

    issues: frozenset[str]
    parent: Mapping[str, str]


def parse_tree(export: bytes) -> LitTree:
    """[LAW:parse-dont-validate] `lit export` bytes to their parent tree, or ValueError for a
    partial or malformed export, a dangling edge or a child with two parents."""
    data = _object(json.loads(export))
    if data.get("version") != EXPORT_VERSION:
        raise ValueError(f"lit export: version {EXPORT_VERSION} required")
    issues, relations = data.get("issues"), data.get("relations")
    if not (isinstance(issues, list) and isinstance(relations, list)):
        raise ValueError("lit export: issues and relations must be arrays")
    ids = [_text(issue, "id") for issue in cast(list[object], issues)]
    if len(set(ids)) != len(ids):
        raise ValueError("lit export: duplicate issue id")
    known = frozenset(ids)
    parent: dict[str, str] = {}
    for relation in cast(list[object], relations):
        if _text(relation, "type") != PARENT_EDGE:
            continue
        child, up = _text(relation, "src_id"), _text(relation, "dst_id")
        if not {child, up} <= known:
            raise ValueError(f"lit export: {child} -> {up} names an unknown issue")
        if parent.setdefault(child, up) != up:
            raise ValueError(f"lit export: {child} has two parents")
    return LitTree(known, parent)


def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("lit export: JSON object required")
    # Decoded JSON object keys are always strings.
    return cast(dict[str, object], value)


def _text(value: object, key: str) -> str:
    field = _object(value).get(key)
    if not isinstance(field, str) or not field:
        raise ValueError(f"lit export: {key} must be a nonempty string")
    return field


def trial_relation(tree: LitTree, unit: str, trial_root: str) -> Observation:
    """Pure: whether `unit`'s parent chain reaches `trial_root`."""
    if unit not in tree.issues:
        return "unknown"
    seen: set[str] = set()
    node = unit
    while node != trial_root:
        if node in seen:
            return "unknown"
        seen.add(node)
        up = tree.parent.get(node)
        if up is None:
            return "contradicted"
        node = up
    return "confirmed"


def observe_trial_relation(store: Path, unit: str, trial_root: str) -> Observation:
    """[LAW:effects-at-boundaries] the native export of the LIT store at `store`, judged once.
    Every failure to read it is `unknown`, the one value that holds enrolled work."""
    try:
        export = subprocess.run(
            ["lit", "export"],
            cwd=store,
            capture_output=True,
            check=True,
            timeout=READ_TIMEOUT_SECONDS,
        ).stdout
        return trial_relation(parse_tree(export), unit, trial_root)
    except (OSError, subprocess.SubprocessError, ValueError):
        return "unknown"


def parse_admission(output: bytes) -> Observation:
    """[LAW:parse-dont-validate] the script's stdout to its one observation, or ValueError
    for anything but exactly one JSON object line naming a known observation."""
    lines = output.splitlines()
    if len(lines) != 1:
        raise ValueError("admission: exactly one output line required")
    observed = _object(json.loads(lines[0])).get("admission")
    if observed not in OBSERVATIONS:
        raise ValueError(f"admission: unknown observation {observed!r}")
    return cast("Observation", observed)


def observe_admission(root: Path, unit: str, operation: Operation) -> Observation:
    """[LAW:effects-at-boundaries] the orchestration checkout at `root` judges `operation` on
    `unit` once, isolated from this process's imports; every failure is `unknown`."""
    try:
        output = subprocess.run(
            [sys.executable, "-I", str(root / ADMISSION_SCRIPT), "admission", unit, operation],
            cwd=root,
            capture_output=True,
            check=True,
            timeout=ADMISSION_TIMEOUT_SECONDS,
        ).stdout
        return parse_admission(output)
    except (OSError, subprocess.SubprocessError, ValueError):
        return "unknown"
