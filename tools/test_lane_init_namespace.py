"""The `_LI_*` namespace invariant of tools/hooks/lane-init.sh, and the checker's own tests.

lane-init.sh is SOURCED, so any `_LI_*` local it leaves defined is written into the caller's
interactive shell. Fifteen exit paths each clear the set with their own hand-written `unset`
list, and that duplication is the condition that guarantees one eventually drifts: the
merge-gate witness lens demonstrated it by dropping `_LI_SRC` from sites no behavioural
fixture reaches, leaving the whole shell suite green.

Why this lives here rather than in the shell suite. The invariant is structural -- "no exit
clears a strict subset" -- and a first attempt to assert it with an inline awk one-liner had a
COMPLETE BYPASS: `/unset -f/ { next }` skipped any physical line merely CONTAINING that
substring, so `unset -f lane_stack_allowed; unset _LI_ROOT _LI_Q _LI_WT` was invisible, and
`$0 !~ /_LI_SRC/` scanned the whole line, so a trailing comment naming the variable made a
real drop read as present. Both were verified against fixtures. Parsing a shell statement
correctly needs comment stripping, `;` splitting and flag handling; that is a parser, and a
parser belongs somewhere it can have its own tests -- which is the point of this module. The
evasions are regression cases below, so a future simplification that reintroduces either one
fails here instead of passing silently.

This is a deliberate static assertion, complementing rather than replacing behaviour: three
exits (library-load refusal, bad-index refusal, index exhaustion) are witnessed behaviourally
in tools/hooks/test_lane_init.sh and still redden independently. This covers the uniformity
those three cannot reach, and it catches a dropped name at a site added later.
"""

from __future__ import annotations

import re
from pathlib import Path

LANE_INIT = Path(__file__).resolve().parent / "hooks" / "lane-init.sh"

#: The members every cleanup site must clear together. `_LI_ORPHAN_DIR` is deliberately NOT
#: here: it is the exported surface `lane_stack_allowed` reads after sourcing returns, and it
#: is invalidated once at the top of the file rather than at each exit.
NAMESPACE = ("_LI_SRC", "_LI_ROOT", "_LI_Q", "_LI_WT")

_UNSET = re.compile(r"^\s*unset\b(?P<args>.*)$")


def _strip_comment(line: str) -> str:
    """Drop a trailing `#` comment, honouring quotes so a `#` inside a string survives.

    A whole-line scan is what let a comment naming `_LI_SRC` mask its removal from the
    actual argument list, so the comment is removed BEFORE any name matching happens.
    """
    out, quote = [], None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote and line[i - 1] != "\\":
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or line[i - 1].isspace()):
            break
        else:
            out.append(ch)
    return "".join(out)


def unset_statements(line: str) -> list[str]:
    """Every `unset` statement on one line, as its argument string.

    Split on `;` first: an `unset -f` statement and a namespace `unset` can share a line, and
    treating the line as one unit is precisely the bypass this function exists to remove.
    `unset -f` removes FUNCTIONS and is not a namespace cleanup, so it is dropped here by
    inspecting the statement's own flags rather than by matching the substring anywhere.
    """
    statements = []
    for part in _strip_comment(line).split(";"):
        m = _UNSET.match(part)
        if not m:
            continue
        args = m.group("args").strip()
        if args.startswith("-"):  # `unset -f NAME` / `unset -v NAME`: flagged form
            flags, _, rest = args.partition(" ")
            if "f" in flags:
                continue
            args = rest
        statements.append(args)
    return statements


def subset_violations(text: str) -> list[tuple[int, list[str]]]:
    """`(line number, missing names)` for every statement clearing a STRICT subset.

    A statement that names none of the namespace is not a cleanup site and is ignored; one
    that names some but not all is the drift this guards against.
    """
    out = []
    for n, line in enumerate(text.splitlines(), start=1):
        for args in unset_statements(line):
            names = set(re.findall(r"_LI_[A-Z_]+", args))
            touched = names & set(NAMESPACE)
            if not touched:
                continue
            missing = [v for v in NAMESPACE if v not in names]
            if missing:
                out.append((n, missing))
    return out


def test_every_cleanup_site_clears_the_whole_namespace():
    violations = subset_violations(LANE_INIT.read_text())
    assert not violations, "\n".join(
        f"lane-init.sh:{n} clears a strict subset, missing {', '.join(miss)}"
        for n, miss in violations
    )


def test_a_dropped_name_is_reported_with_its_line():
    text = "\n".join(["ok=1", "  unset _LI_ROOT _LI_Q _LI_WT", "ok=2"])
    assert subset_violations(text) == [(2, ["_LI_SRC"])]


def test_unset_f_sharing_a_line_does_not_mask_a_dropped_name():
    """The complete bypass the first implementation had (merge-gate witness lens, P1).

    `/unset -f/ { next }` skipped the entire line, so chaining the two statements hid a real
    drop. Reachable by an ordinary edit: this file already writes `unset ...; return 1` as
    one-liners.
    """
    text = "  unset -f lane_stack_allowed; unset _LI_ROOT _LI_Q _LI_WT"
    assert subset_violations(text) == [(1, ["_LI_SRC"])]


def test_a_comment_naming_the_variable_does_not_mask_its_removal():
    """The substring evasion (merge-gate witness lens, P2).

    Whole-line matching read the name in the trailing comment as the name in the argument
    list. This file's dense literate comments name these variables constantly.
    """
    text = "  unset _LI_ROOT _LI_Q _LI_WT  # keeping _LI_SRC alive, see the _LI_SRC note"
    assert subset_violations(text) == [(1, ["_LI_SRC"])]


def test_unset_f_alone_is_not_a_cleanup_site():
    assert subset_violations("  unset -f lane_stack_allowed _li_reset") == []


def test_an_unset_of_unrelated_names_is_not_a_cleanup_site():
    assert subset_violations("  unset _li_have _li_tmp OTHER") == []
