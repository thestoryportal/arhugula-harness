"""Hermetic tests for tools/rtk_shape_guard.py (U-SR-09 b4): the pure, quote-aware judgement
behind tools/hooks/rtk-shape-guard.sh. The (original, rewritten) pairs below are rtk 0.40.0's
real dry-run outputs, witnessed at U-SR-09; the shell suite drives the wrapper end to end."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rtk_shape_guard as g

GLOB = "--glob/-g"
PAREN = "unescaped paren"


def test_tokens_keep_quoted_separators_and_flags_whole():
    assert g.tokens("cd /tmp; grep -n 'a && f(' f | grep x") == [
        "cd", "/tmp", ";", "grep", "-n", "a && f(", "f", "|", "grep", "x",
    ]  # fmt: skip
    assert g.tokens("rg -g'*.py' needle") == ["rg", "-g*.py", "needle"]
    assert g.tokens("grep 'unbalanced") is None
    # a word that IS a separator when quoted stays a word (shlex alone would return a bare `|`)
    assert g.segments(g.tokens("grep '|' f | grep '(' g") or []) == [
        ["grep", "|", "f"],
        ["grep", "(", "g"],
    ]
    assert g.tokens('grep "a;b" f; echo') == ["grep", "a;b", "f", ";", "echo"]
    # codex u-sr-09 r2: an unquoted newline separates commands like `;`; a quoted one does not
    assert g.segments(g.tokens("cd /tmp\nrg -g '*.py' x") or []) == [
        ["cd", "/tmp"],
        ["rg", "-g", "*.py", "x"],
    ]
    assert g.tokens("grep 'a\nb' f") == ["grep", "a\nb", "f"]
    # codex u-sr-09 r4: a backslash-ESCAPED separator is data, like a quoted one
    assert g.segments(g.tokens('grep "f(" \\| wc') or []) == [["grep", "f(", "|", "wc"]]
    assert g.segments(g.tokens("a \\; b") or []) == [["a", ";", "b"]]


def test_segments_split_at_bare_separators_only():
    toks = g.tokens("a && b '||' c ; (d)")
    assert toks is not None
    assert g.segments(toks) == [["a"], ["b", "||", "c"], ["d"]]


# mutation-probe: drop the `has_glob(args)` arm in shapes()
@pytest.mark.parametrize(
    ("rewritten", "want"),
    [
        ('rtk grep --glob "*.py" "def main" tools', [GLOB]),
        ("rtk grep -g '*.py' main tools", [GLOB]),
        ("rtk grep -g*.py main tools", [GLOB]),  # attached value (codex r1 P2)
        ("rtk grep --glob=*.py main tools", [GLOB]),
        ("rtk grep -ng x tools", [GLOB]),  # g inside a short cluster
        ('rtk grep -rn "hook_emit(" tools/hooks', [PAREN]),
        ('rtk grep -n "x)" f.txt', [PAREN]),
        ("rtk grep -n 'a && f(' file", [PAREN]),  # quoted separator (codex r1 P2)
        ('rtk grep -n "a\\|f(" f.txt', [PAREN]),  # the [B] parse-error shape
        ("rtk grep -e 'f(' f.txt", [PAREN]),  # pattern given via -e
        ("rtk grep -g '*.py' 'f(' tools", [GLOB, PAREN]),
        # codex u-sr-09 r2: option grammar corners
        ("rtk grep -eF\\( file", [PAREN]),  # -e takes the rest of the cluster: F( is the pattern
        ("rtk grep -nA 2 'f(' file", [PAREN]),  # clustered -nA consumes its value
        ("rtk grep -nA2 'f(' file", [PAREN]),
        ("rtk grep -m1 'f(' file", [PAREN]),
        ("rtk grep 'f\\\\(' file", [PAREN]),  # even backslash run: the paren is live
        ("rtk grep --regexp='f(' file", [PAREN]),
        ("rtk grep -- '(' file", [PAREN]),  # after `--` the paren IS the pattern: rg still chokes
        ("rtk grep '\\[(]' file", [PAREN]),  # codex r4: an ESCAPED `[` opens no bracket expression
        # codex u-sr-09 r3: EVERY -e pattern is judged; a bracket expression is not a group
        ("rtk grep -e ok -e 'f(' file", [PAREN]),
        ("rtk grep --regexp ok --regexp='f(' file", [PAREN]),
        ("rtk grep '[a]f(' file", [PAREN]),  # a paren OUTSIDE the bracket expression
        ("rtk grep -n 'f(' file 2>/dev/null", [PAREN]),  # a redirection is not a pattern
    ],
)
def test_shapes_found(rewritten, want):
    toks = g.tokens(rewritten)
    assert toks is not None
    found = g.shapes(g.segments(toks)[0])
    assert [w for w in (GLOB, PAREN) if any(w in f for f in found)] == want


@pytest.mark.parametrize(
    "rewritten",
    [
        "rtk grep -n foo file.txt",
        'rtk grep -n "a\\|b" file.txt',  # alternation alone round-trips on 0.40.0
        'rtk grep -nE "f(x)" file.txt',
        'rtk grep -F "f(" file.txt',
        'rtk grep -P "f(x)" file.txt',
        'rtk grep -rnE "f(" tools',
        "rtk grep --fixed-strings 'f(' file.txt",
        'rtk grep -n "f\\(x\\)" file.txt',  # escaped: a BRE group, not a hard failure
        'rtk grep -n plain "dir (x)/file"',  # paren in a PATH operand, not the pattern
        "rtk grep -A 2 pat 'f(x).txt'",  # -A consumes its value; the operand is a path
        # codex u-sr-09 r2: option grammar corners
        "rtk grep -- -g file",  # `--` ends options: -g is the pattern operand
        "rtk grep -nE 'f(' file",
        "rtk grep -eE file",  # -e takes `E` as its pattern; no -E flag is set
        # codex u-sr-09 r3: parens inside a bracket expression are literals to both engines
        "rtk grep '[()]' file",
        "rtk grep '[^)]x' file",
        "rtk grep -e ok -e '[(]' file",
        "rtk grep '\\\\[(]' file",  # an ESCAPED escape: `\\` then a real bracket expression
        "rtk grep x 2>/dev/null",  # the redirection target is not an operand
    ],
)
def test_shapes_silent(rewritten):
    toks = g.tokens(rewritten)
    assert toks is not None
    assert g.shapes(g.segments(toks)[0]) == []


def test_judge_only_looks_at_rtk_grep_segments():
    assert g.judge('ls | grep "f("', 'rtk ls | grep "f("') is None  # pipeline grep untouched
    assert g.judge("egrep 'f(x)' f", "No rewrite for: egrep 'f(x)' f") is None
    assert g.judge('grep "f(" f', "grep 'f(") is None  # the rewrite does not lex: no verdict
    reason = g.judge('cd /tmp; grep -n "f(" f', 'cd /tmp; rtk grep -n "f(" f')
    assert reason is not None and PAREN in reason and "`rtk grep -n 'f(' f`" in reason
    # codex r4: an escaped `\|` is an operand, so the second grep is the pipeline's, untouched
    assert g.judge('grep "f(" \\| wc', 'rtk grep "f(" \\| wc') is not None


# mutation-probe: drop the `if any(isinstance(t, (Sep, Redirect)) …)` refusal in reissue()
def test_reissue_is_verbatim_for_one_command_and_quote_safe_otherwise():
    assert (
        g.reissue('grep -rn "hook_emit(" tools/hooks')
        == 'rtk proxy grep -rn "hook_emit(" tools/hooks'
    )
    assert (
        g.reissue('rg --glob "*.py" "def main" tools')
        == 'rtk proxy rg --glob "*.py" "def main" tools'
    )
    # quoted data is never rewritten (codex r1 P2): the argument '; grep literal' survives
    fix = g.reissue("grep -g '*.py' needle '; grep literal'")
    assert fix == "rtk proxy grep -g '*.py' needle '; grep literal'"
    # a compound command is NEVER re-joined (codex r4: a quoted glob `'*.py'` would stop
    # expanding; r3: a redirection would lose its fd) -- the caller re-issues by hand
    assert g.reissue('cd /tmp; grep -n "f(" *.py') is None
    assert g.reissue('grep -n "f(" f && echo ok') is None
    assert g.reissue("ls | grep 'a && f(' f") is None
    reason = g.judge('cd /tmp; grep -n "f(" *.py', 'cd /tmp; rtk grep -n "f(" *.py')
    assert (
        reason is not None
        and "Re-issue by hand" in reason
        and "'*.py'" not in reason.split("Re-issue")[1]
    )
    assert g.reissue("uv run x") is None  # not a grep/rg command: nothing to prefix
    assert g.reissue("grep 'unbalanced") is None
    # codex u-sr-09 r3: a redirection cannot be re-joined faithfully (`2>` vs `2 >`), so no
    # command is fabricated -- the reason tells the caller to re-issue by hand
    assert g.reissue("grep -g '*.py' x 2>/dev/null | wc -l") is None
    assert g.reissue("grep -g '*.py' x >out.txt") is None
    reason = g.judge(
        "grep -g '*.py' x 2>/dev/null | wc -l", "rtk grep -g '*.py' x 2>/dev/null | wc -l"
    )
    assert reason is not None and "Re-issue by hand" in reason and "2 '>'" not in reason
    assert "`rtk grep -g '*.py' x 2 > /dev/null`" in reason  # the segment echo keeps operators bare


def test_parse_args_grammar():
    p = g.parse_args(["-nA", "2", "-eF\\(", "--glob=*.py", "--", "-g", "x"])
    assert p.flags == {"n"} and p.values == {"A": "2", "e": "F\\(", "--glob": "*.py"}
    assert p.longs == {"--glob"} and p.operands == ["-g", "x"]
    assert g.patterns_of(p) == ["F\\("] and not g.regex_safe(p) and g.has_glob(p)
    p = g.parse_args(["-rnE", "f(", "tools"])
    assert p.flags == {"r", "n", "E"} and g.regex_safe(p) and g.patterns_of(p) == ["f("]
    p = g.parse_args(["--regexp", "f(", "-t", "py", "file"])
    assert p.values == {"--regexp": "f(", "t": "py"} and p.operands == ["file"]
    assert p.patterns == ["f("] and g.patterns_of(p) == ["f("]
    p = g.parse_args(["-e", "a", "-eb", "--regexp=c", "file"])
    assert p.patterns == ["a", "b", "c"] and g.patterns_of(p) == ["a", "b", "c"]
    assert g.patterns_of(g.parse_args(["x", "y"])) == ["x"]
    assert g.has_unescaped_paren("[()]") is False and g.has_unescaped_paren("[a]f(") is True
    assert g.has_unescaped_paren("\\[(]") is True and g.has_unescaped_paren("\\\\[(]") is False


def test_judge_reason_names_shapes_and_reissue():
    reason = g.judge("rg -g'*.py' needle tree", "rtk grep -g'*.py' needle tree")
    assert reason is not None
    assert GLOB in reason and "Re-issue as: rtk proxy rg -g'*.py' needle tree" in reason
    both = g.judge("rg -g '*.py' 'f(' tools", "rtk grep -g '*.py' 'f(' tools")
    assert both is not None and GLOB in both and PAREN in both


def test_cli_prints_the_reason_or_nothing_and_always_exits_0(capsys):
    assert g.main(["grep -n foo f", "rtk grep -n foo f"]) == 0
    assert capsys.readouterr().out == ""
    assert g.main(['grep -n "f(" f', 'rtk grep -n "f(" f']) == 0
    assert PAREN in capsys.readouterr().out
    assert g.main(["only-one-arg"]) == 0


@pytest.mark.skipif(
    not Path("/usr/bin/python3").exists() or shutil.which("/usr/bin/python3") is None,
    reason="the hook shell's /usr/bin/python3 is not present",
)
def test_runs_under_the_hook_shells_python():
    """The wrapper invokes this module with the system python (3.9 on the operator's
    machine); the venue must import and judge, not just the workspace 3.12."""
    r = subprocess.run(
        [
            "/usr/bin/python3",
            str(Path(__file__).resolve().parent / "rtk_shape_guard.py"),
            'grep -n "f(" f',
            'rtk grep -n "f(" f',
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0 and PAREN in r.stdout and r.stderr == "", r.stderr
