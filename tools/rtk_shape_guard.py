"""The rtk grep-rewrite shape judgement (U-SR-09 b4) -- pure, shell-quote-aware.

`tools/hooks/rtk-shape-guard.sh` is the thin PreToolUse wrapper: it asks rtk's own dry-run
(`rtk hook check`) what the rewrite will be, hands the ORIGINAL and the REWRITTEN command
to this module, and turns a non-empty answer into a deny. Everything that needs to read a
shell command lives here, on `shlex` with `punctuation_chars`, so a quoted `&&`, `;`, `(`
or `-g'*.py'` is one token and never a separator or a bare flag (codex u-sr-09 r1: the
sed-based first cut truncated `'a && f('` at the `&&`, missed the attached `-g'*.py'`,
and re-wrote a quoted `'; grep literal'` argument). Runs under the hook shell's
/usr/bin/python3 (3.9) as well as the workspace 3.12 -- no 3.10+ syntax at runtime.

Two shapes are judged on the `rtk grep …` segment (the ones rtk 0.40.0 mangles
deterministically -- the header of the wrapper carries the witnessed failures):
  glob   -- an rg-only `--glob`/`-g` (attached or separate value; any short cluster
            carrying `g`), which rtk hands to BSD grep: 'unrecognized option', exit 2;
  paren  -- an unescaped `(` or `)` in the PATTERN when no -E/-F/-P makes it mean the
            same thing to grep and rg: 'regex parse error … unclosed group', exit 2.
The re-issue prefixes every command-position `grep`/`rg` of the ORIGINAL with `rtk proxy`:
verbatim when the command is one simple command, re-joined with `shlex.quote` (equivalent,
not byte-identical) when it carries separators.
"""

from __future__ import annotations

import re
import shlex
import sys

SEPARATORS = frozenset({"|", "||", "&&", ";", "&", "(", ")"})
REWRITTEN_WORDS = ("rtk", "grep")
COMMAND_WORDS = frozenset({"grep", "rg"})
# grep/rg options that consume the NEXT token (so it is never mistaken for the pattern)
VALUE_OPTIONS = frozenset(
    {
        "-e", "--regexp", "-f", "--file", "-m", "--max-count", "-A", "--after-context",
        "-B", "--before-context", "-C", "--context", "-g", "--glob", "--iglob", "-t",
        "--type", "-T", "--type-not", "-d", "--directories", "-D", "--devices",
    }
)  # fmt: skip
REGEX_SAFE_LONG = frozenset({"--extended-regexp", "--fixed-strings", "--perl-regexp"})
_UNESCAPED_PAREN = re.compile(r"(?<!\\)[()]")


# Separator characters inside quotes are masked to private-use code points before lexing and
# restored after, so a word that IS a separator when quoted (`grep '|' f`, `echo '&&'`) stays
# a word: shlex strips the quotes and would otherwise hand back an indistinguishable `|`.
_MASK = {c: chr(0xE000 + i) for i, c in enumerate("|;&()")}
_UNMASK = {v: k for k, v in _MASK.items()}


def _mask_quoted(command: str) -> str:
    out: list[str] = []
    quote: str | None = None
    escaped = False
    for ch in command:
        if escaped:
            out.append(ch)
            escaped = False
        elif ch == "\\" and quote != "'":
            out.append(ch)
            escaped = True
        elif quote is None and ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif quote is not None and ch == quote:
            quote = None
            out.append(ch)
        elif quote is not None:
            out.append(_MASK.get(ch, ch))
        else:
            out.append(ch)
    return "".join(out)


class Sep(str):
    """A BARE shell separator token (`|`, `&&`, `;`, …). A quoted word with the same text is
    a plain `str`: the type carries the distinction the text cannot, so no consumer has to
    guess whether `|` was an operator or an argument. [LAW:types-are-the-program]"""

    __slots__ = ()


def tokens(command: str) -> list[str] | None:
    """The command as shell words, bare separators typed `Sep` (quoted ones stay plain words
    inside their quotes); None when the command does not lex (an unbalanced quote) -- the
    caller treats that as "no verdict"."""
    lex = shlex.shlex(_mask_quoted(command), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        raw = list(lex)
    except ValueError:
        return None
    return [Sep(t) if t in SEPARATORS else "".join(_UNMASK.get(c, c) for c in t) for t in raw]


def segments(toks: list[str]) -> list[list[str]]:
    """The simple commands of a token list, split at bare separators (separators dropped)."""
    out: list[list[str]] = [[]]
    for t in toks:
        if isinstance(t, Sep):
            out.append([])
        else:
            out[-1].append(t)
    return [s for s in out if s]


def _is_short_cluster(tok: str) -> bool:
    return tok.startswith("-") and not tok.startswith("--") and len(tok) > 1


def regex_safe(args: list[str]) -> bool:
    """-E/-F/-P in any short cluster, or the long forms: a paren means the same to both."""
    return any(
        (_is_short_cluster(a) and any(c in "EFP" for c in a[1:])) or a in REGEX_SAFE_LONG
        for a in args
    )


def has_glob(args: list[str]) -> bool:
    """`--glob`, `--glob=…`, `-g`, `-g'*.py'` (attached), or `g` inside a short cluster
    (`-ng`). BSD grep has no `g` option in any spelling, so every form lands on exit 2."""
    return any(
        a == "--glob" or a.startswith("--glob=") or (_is_short_cluster(a) and "g" in a[1:])
        for a in args
    )


def pattern_of(args: list[str]) -> str | None:
    """The PATTERN operand: the value of the first `-e`/`--regexp` if given, else the first
    operand that is neither an option nor an option's value. None when there is none."""
    first_operand: str | None = None
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-e", "--regexp") and i + 1 < len(args):
            return args[i + 1]
        if a.startswith("--regexp=") or (a.startswith("-e") and _is_short_cluster(a)):
            return a.split("=", 1)[1] if a.startswith("--") else a[2:]
        if a in VALUE_OPTIONS:
            i += 2
            continue
        if a.startswith("-") and len(a) > 1:
            i += 1
            continue
        if first_operand is None:
            first_operand = a
        i += 1
    return first_operand


def shapes(rewritten_segment: list[str]) -> list[str]:
    """The mangled shapes one `rtk grep …` segment carries (empty = the rewrite is fine)."""
    args = rewritten_segment[len(REWRITTEN_WORDS) :]
    found: list[str] = []
    if has_glob(args):
        found.append(
            "an rg-only --glob/-g flag (rtk lands it on BSD grep: 'unrecognized option', exit 2)"
        )
    pat = pattern_of(args)
    if pat is not None and not regex_safe(args) and _UNESCAPED_PAREN.search(pat):
        found.append(
            "an unescaped paren in a BRE pattern (a literal to grep, a group to rg: "
            "'regex parse error', exit 2)"
        )
    return found


def reissue(original: str) -> str | None:
    """The ORIGINAL command with `rtk proxy` before every command-position grep/rg. Verbatim
    for one simple command; otherwise re-joined token by token (separators bare, words
    `shlex.quote`d) -- shell-equivalent, and quoted data is never touched. None when the
    original does not lex."""
    toks = tokens(original)
    if toks is None:
        return None
    if not any(isinstance(t, Sep) for t in toks):
        return "rtk proxy " + original.lstrip() if toks[:1] and toks[0] in COMMAND_WORDS else None
    out: list[str] = []
    at_command_position = True
    for t in toks:
        if isinstance(t, Sep):
            out.append(t)
            at_command_position = t != ")"
            continue
        if at_command_position and t in COMMAND_WORDS:
            out.extend(["rtk", "proxy"])
        out.append(shlex.quote(t))
        at_command_position = False
    return " ".join(out)


def judge(original: str, rewritten: str) -> str | None:
    """The deny reason for this (original, rtk-rewritten) pair, or None when nothing rtk does
    to it breaks: no `rtk grep` segment, only safe shapes, or a command that does not lex."""
    rtoks = tokens(rewritten)
    if rtoks is None:
        return None
    found: list[str] = []
    segment_text = ""
    for seg in segments(rtoks):
        if seg[: len(REWRITTEN_WORDS)] != list(REWRITTEN_WORDS):
            continue
        hits = shapes(seg)
        if hits:
            found.extend(hits)
            segment_text = segment_text or shlex.join(seg)
    if not found:
        return None
    fix = reissue(original)
    tail = f" Re-issue as: {fix}" if fix else ""
    return (
        f"[rtk-shape-guard] the rtk PreToolUse rewrite turns this into `{segment_text}`, "
        f"which carries {'; '.join(found)}.{tail}"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI: `rtk_shape_guard.py <original> <rewritten>` prints the deny reason (nothing when
    there is none). Always exit 0 -- the wrapper decides from the output, never the code."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        return 0
    reason = judge(args[0], args[1])
    if reason:
        sys.stdout.write(reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
