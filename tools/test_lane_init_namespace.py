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
evasions found so far are regression cases below, so a simplification that reintroduces one
fails here rather than passing silently.

This is a lexical SCANNER, not a shell parser, and that distinction is the honest bound on it.
It recognises `unset` statements separated by `;`, `&&`, `||` or `&`, strips comments
quote-aware, and excludes `unset -f` by the statement's own flags. It does NOT evaluate the
shell: a name list reached by variable indirection (`unset $VARS`) carries no literal token to
find, a statement continued across physical lines with a backslash is scored per line, and a
cleanup legitimately split across two `unset` statements reads as two partial ones. Those
shapes are registered as forward work rather than chased here -- none occurs in lane-init.sh
today, and only the first is a SILENT miss; the other two fail loud.

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

#: Shell statement separators. `;` alone missed the one-line-guard form
#: (`[ cond ] && unset ...`), which is the dominant idiom in the file being checked -- 44
#: occurrences in tools/hooks/lane-init.sh -- so a cleanup site refactored into that shape
#: was invisible. `&` is included so a backgrounded statement cannot hide one either; the
#: alternation is ordered longest-first so `&&` is never split as two `&`.
_SEPARATORS = re.compile(r"&&|\|\||;|&")


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

    Split on every shell statement separator first: an `unset -f` statement and a namespace
    `unset` can share a line, and treating the line as one unit is precisely the bypass this
    function exists to remove. `;` alone was not enough -- a guarded one-liner
    (`[ cond ] && unset ...`) kept the namespace `unset` out of any segment that STARTS with
    it, which is how the same bypass class survived a second time.
    `unset -f` removes FUNCTIONS and is not a namespace cleanup, so it is dropped here by
    inspecting the statement's own flags rather than by matching the substring anywhere.
    """
    statements = []
    for part in _SEPARATORS.split(_strip_comment(line)):
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
            # The WHOLE identifier, then membership -- not a hand-narrowed class.
            # `[A-Z_]+` stops at the first digit, so `_LI_ROOT2` was extracted as
            # `_LI_ROOT` and a typo'd cleanup read as complete while the real
            # `_LI_ROOT` survived in the caller (codex r11 P3). A shell identifier is
            # [A-Za-z0-9_]+; extracting it whole lets NAMESPACE membership below do the
            # deciding, which is one rule fewer, not one more.
            names = set(re.findall(r"_LI_[A-Za-z0-9_]+", args))
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


def test_a_guarded_one_line_unset_is_not_invisible():
    """The third evasion of the same class (merge-gate witness lens, round 4).

    Splitting only on `;` and requiring each segment to START with `unset` made a cleanup
    written as a one-line guard silently invisible -- and that guard form occurs 44 times in
    the file this module checks, so it was a likelier future shape than either evasion the
    module was originally written for.
    """
    for sep in ("&&", "||", "&"):
        text = f'  [ -n "$x" ] {sep} unset _LI_ROOT _LI_Q _LI_WT'
        assert subset_violations(text) == [(1, ["_LI_SRC"])], (sep, subset_violations(text))


def test_a_complete_guarded_unset_is_not_falsely_flagged():
    assert subset_violations('  [ -n "$x" ] && unset _LI_SRC _LI_ROOT _LI_Q _LI_WT') == []


def test_a_near_miss_name_does_not_count_as_clearing_the_real_one():
    """A cleanup typo must not read as complete (codex r11 P3).

    `_LI_ROOT2` is a different variable from `_LI_ROOT`. Extracting names with
    `_LI_[A-Z_]+` stopped at the digit and yielded `_LI_ROOT`, so this statement
    looked like it cleared the whole namespace while the real `_LI_ROOT` stayed set
    in the caller -- silent, and exactly the bypass class the awk predecessor died of.
    Widen the character class back and this reddens.
    """
    assert subset_violations("  unset _LI_SRC _LI_ROOT2 _LI_Q _LI_WT") == [(1, ["_LI_ROOT"])]
    # ...and the honest spelling still passes, so the fix did not just break everything.
    assert subset_violations("  unset _LI_SRC _LI_ROOT _LI_Q _LI_WT") == []


def test_unset_f_alone_is_not_a_cleanup_site():
    """`unset -f` drops FUNCTIONS, so it is never a namespace cleanup site.

    The first input is the discriminating one and the reason this test exists: its
    names are in the namespace, so only the flag inspection can exclude it. Delete
    that branch and this line reddens with [(1, ["_LI_SRC", "_LI_ROOT"])]. The
    original lowercase fixture below is kept, but it cannot witness the branch --
    `_LI_[A-Z_]+` never matches a lowercase name, so it is discarded as
    not-a-cleanup-site before the flags are ever read.
    """
    assert subset_violations("  unset -f _LI_Q _LI_WT") == []
    assert subset_violations("  unset -f lane_stack_allowed _li_reset") == []


def test_an_unset_of_unrelated_names_is_not_a_cleanup_site():
    assert subset_violations("  unset _li_have _li_tmp OTHER") == []
