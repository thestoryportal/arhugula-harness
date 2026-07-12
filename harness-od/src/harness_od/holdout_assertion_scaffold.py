"""Assertion-stub scaffolding — the "automate" phase, B-OD17-EVAL-LOOP-TOOLING.

The "automate" half of the Husain manual-review -> categorize -> automate ->
align loop: per the R-FS-2 registered scope, "automate" means operator-
authored assertion stubs checked into the repo — tooling scaffolds the file,
a human writes the assertion. This module writes the scaffold only; it never
fills in a real assertion body and never evaluates one.

Hard boundary (`[[eval-harness-refused-as-governance-gate]]`): the generated
stub always raises `NotImplementedError` until an operator edits it by hand.
No model call, heuristic, or automatic pass/fail decision is generated here
— that would be exactly the model-judge-as-governance-gate shape this
workspace has standing-refused.
"""

from __future__ import annotations

import re
from pathlib import Path

from harness_od.holdout_review_ledger import ReviewEntry, read_review_ledger

__all__ = [
    "scaffold_assertion_stub_source",
    "scaffold_pending_stubs",
]

_SAFE_IDENT_RE = re.compile(r"[^a-zA-Z0-9_]")


def _stub_function_name(trace_id: str) -> str:
    """A valid Python identifier suffix derived from `trace_id`.

    Non-identifier characters are replaced with `_`; a leading digit (trace
    ids are frequently hex) is prefixed with `t` so the result is never a
    syntax error as a function-name suffix.
    """
    safe = _SAFE_IDENT_RE.sub("_", trace_id)
    return f"t{safe}" if safe[:1].isdigit() else safe


def _stub_path(entry: ReviewEntry, output_dir: Path) -> Path:
    return output_dir / f"test_holdout_{_stub_function_name(entry.trace_id)}.py"


def scaffold_assertion_stub_source(entry: ReviewEntry) -> str:
    """Render the scaffolded stub source for one reviewed trace.

    Always raises `NotImplementedError` — the operator replaces that line
    with a real assertion once they decide what "correct" means for this
    trace's category. The category + notes are carried in the docstring so
    the operator has the review context in front of them when they write it.
    """
    fn_name = _stub_function_name(entry.trace_id)
    notes = entry.notes or "(none)"
    return (
        f'"""Holdout assertion stub — {entry.primitive.value}, trace '
        f'{entry.trace_id!r} (scaffolded, C-OD-17 §17.3 "automate" phase).\n\n'
        "Tooling-generated. Operator-authored assertion required before this\n"
        "test can pass — until then it fails loudly rather than silently\n"
        'passing on an unauthored placeholder.\n"""\n\n'
        "from __future__ import annotations\n\n\n"
        f"def test_holdout_{fn_name}() -> None:\n"
        f'    """Category: {entry.category!r}. Notes: {notes!r}."""\n'
        "    raise NotImplementedError(\n"
        f'        "operator-authored assertion pending for trace {entry.trace_id!r} '
        f'({entry.primitive.value})"\n'
        "    )\n"
    )


def scaffold_pending_stubs(ledger_path: Path, output_dir: Path) -> list[Path]:
    """Scaffold a stub file for every reviewed trace that lacks one.

    Idempotent by construction: an already-written stub file is left
    untouched (never overwritten) so an operator's in-progress hand-authored
    assertion is never clobbered by a re-run. Returns the paths of the files
    actually written this call (empty when every reviewed trace already has
    a stub).
    """
    written: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for entry in read_review_ledger(ledger_path):
        path = _stub_path(entry, output_dir)
        if path.exists():
            continue
        path.write_text(scaffold_assertion_stub_source(entry))
        written.append(path)
    return written
