"""The rtk grep-rewrite shape judgement (U-SR-09 b4) -- pure, shell-quote-aware.

`tools/hooks/rtk-shape-guard.sh` is the thin PreToolUse wrapper: it asks rtk's own dry-run
(`rtk hook check`) what the rewrite will be, hands the ORIGINAL and the REWRITTEN command
to this module, and turns a non-empty answer into a deny. Everything that needs to read a
shell command lives here, on `shlex` with `punctuation_chars`, so a quoted `&&`, `;`, `(`
or `-g'*.py'` is one token and never a separator or a bare flag (codex u-sr-09 r1: the
sed-based first cut truncated `'a && f('` at the `&&`, missed the attached `-g'*.py'`,
and re-wrote a quoted `'; grep literal'` argument). Runs under the hook shell's
/usr/bin/python3 (3.9) as well as the workspace 3.12 -- no 3.10+ syntax at runtime.

The option grammar is grep's/rg's, parsed ONCE by `parse_args` (codex u-sr-09 r2: three
separate scans each got a corner wrong -- `-eF\\(` read as a `-F` flag, `-nA 2` not
consuming its value, `--` not ending options): a short cluster is flags until its first
value-taking letter, which takes the rest of the token or the next token; `--` ends
options; `--opt=value` and `--opt value` both bind; EVERY `-e`/`--regexp` is a pattern
(codex r3: only the first was judged).

Two shapes are judged on the `rtk grep …` segment (the ones rtk 0.40.0 mangles
deterministically -- the header of the wrapper carries the witnessed failures):
  glob   -- an rg-only `--glob`/`-g` (attached or separate value; anywhere in a short
            cluster), which rtk hands to BSD grep: 'unrecognized option', exit 2;
  paren  -- an unescaped `(` or `)` in a PATTERN, outside a bracket expression (`[()]` is
            a literal to both engines -- codex r3), when no -E/-F/-P makes it mean the
            same thing to grep and rg: 'regex parse error … unclosed group', exit 2.
            "Unescaped" counts the backslashes: an even run leaves the paren live.
The re-issue is offered ONLY for one simple command -- `rtk proxy ` prepended to the
original text, byte-exact -- and never for a compound one: a token-by-token re-join cannot
be faithful (a redirection loses whether `2` was attached to `>`, codex r3; a quoted glob
`'*.py'` stops expanding, codex r4; `$VAR`, `~` and `$(…)` would follow), so the deny then
tells the caller to add the prefix by hand. A guard that only removes wasted calls must
never invent a command it cannot vouch for. [LAW:no-silent-failure]
"""

from __future__ import annotations

import re
import shlex
import sys
from dataclasses import dataclass, field

SEPARATORS = frozenset({"|", "||", "&&", ";", "&", "(", ")"})
REWRITTEN_WORDS = ("rtk", "grep")
COMMAND_WORDS = frozenset({"grep", "rg"})
# short options that take a value: the rest of the cluster, or the next token
VALUE_SHORT = frozenset("efmABCgtTdD")
# long options that take a value (`--opt value` or `--opt=value`)
VALUE_LONG = frozenset(
    {
        "--regexp", "--file", "--max-count", "--after-context", "--before-context",
        "--context", "--glob", "--iglob", "--type", "--type-not", "--directories",
        "--devices",
    }
)  # fmt: skip
PATTERN_OPTIONS = frozenset({"e", "--regexp"})
REGEX_SAFE_SHORT = frozenset("EFP")
REGEX_SAFE_LONG = frozenset({"--extended-regexp", "--fixed-strings", "--perl-regexp"})
GLOB_LONG = frozenset({"--glob", "--iglob"})
# a paren preceded by an EVEN number of backslashes (zero included) is unescaped
_UNESCAPED_PAREN = re.compile(r"(?<!\\)(?:\\\\)*[()]")
# a bracket expression (`[()]`, `[^)]`, `[]abc]`): parens inside are literals to both engines;
# an ESCAPED `[` (odd backslash run) opens none (codex r4)
_BRACKET_EXPR = re.compile(r"(?<!\\)((?:\\\\)*)\[\^?\]?[^\]]*\]")
# a bare punctuation token that is a redirection, not a separator (`>`, `>>`, `>&`, `<`, …)
_REDIRECT = re.compile(r"^[<>&]*[<>][<>&]*$")

# Separator characters inside quotes are masked to private-use code points before lexing and
# restored after, so a word that IS a separator when quoted (`grep '|' f`, `echo '&&'`) stays
# a word: shlex strips the quotes and would otherwise hand back an indistinguishable `|`.
# An unquoted newline is a command separator the shell honours and shlex would swallow as
# whitespace (codex u-sr-09 r2), so it is rewritten to `;` in the same pass. A backslash-
# ESCAPED separator (`\|`) is data too -- shlex drops the backslash and would hand back a
# bare `|` (codex r4) -- so the escaped character is masked exactly like a quoted one.
_MASK = {c: chr(0xE000 + i) for i, c in enumerate("|;&()<>")}
_UNMASK = {v: k for k, v in _MASK.items()}


def _mask_quoted(command: str) -> str:
    out: list[str] = []
    quote: str | None = None
    escaped = False
    for ch in command:
        if escaped:
            out.append(_MASK.get(ch, ch))
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
        elif ch == "\n":
            out.append(" ; ")
        else:
            out.append(ch)
    return "".join(out)


class Sep(str):
    """A BARE shell separator token (`|`, `&&`, `;`, …). A quoted word with the same text is
    a plain `str`: the type carries the distinction the text cannot, so no consumer has to
    guess whether `|` was an operator or an argument. [LAW:types-are-the-program]"""

    __slots__ = ()


class Redirect(str):
    """A BARE redirection operator token (`>`, `>>`, `>&`, `<`, …). Not a separator -- it
    stays inside its simple command -- but a re-join cannot reproduce it faithfully (shlex
    drops whether a leading fd digit was attached), so its presence forbids a fabricated
    re-issue. [LAW:types-are-the-program]"""

    __slots__ = ()


def _typed(raw: str) -> str:
    if raw in SEPARATORS:
        return Sep(raw)
    if _REDIRECT.match(raw):
        return Redirect(raw)
    return "".join(_UNMASK.get(c, c) for c in raw)


def tokens(command: str) -> list[str] | None:
    """The command as shell words, bare separators typed `Sep` and bare redirections typed
    `Redirect` (quoted ones stay plain words inside their quotes); None when the command does
    not lex (an unbalanced quote) -- the caller treats that as "no verdict"."""
    lex = shlex.shlex(_mask_quoted(command), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        raw = list(lex)
    except ValueError:
        return None
    return [_typed(t) for t in raw]


def segments(toks: list[str]) -> list[list[str]]:
    """The simple commands of a token list, split at bare separators (separators dropped;
    redirection tokens stay in their command as plain words for the option parser, which
    treats them as operands it never judges)."""
    out: list[list[str]] = [[]]
    for t in toks:
        if isinstance(t, Sep):
            out.append([])
        else:
            out[-1].append(t)
    return [s for s in out if s]


@dataclass
class Args:
    """A grep/rg argument list PARSED once: which short flags and long options are set, the
    first value each value-taking option received, EVERY pattern given via `-e`/`--regexp`,
    and the operands in order. Every shape question is answered from this, never from a
    re-scan of the raw tokens."""

    flags: set[str] = field(default_factory=set)
    longs: set[str] = field(default_factory=set)
    values: dict[str, str] = field(default_factory=dict)
    patterns: list[str] = field(default_factory=list)
    operands: list[str] = field(default_factory=list)


def parse_args(args: list[str]) -> Args:
    """grep/rg option grammar: `--` ends options; `--opt=v` / `--opt v` bind a value for
    VALUE_LONG; a short cluster (`-nA2`, `-nA 2`, `-eF\\(`) is flags up to its first
    VALUE_SHORT letter, which takes the rest of the token or, if empty, the next token.
    Every `-e`/`--regexp` value is appended to `patterns` (grep ORs them all)."""
    parsed = Args()

    def bind(key: str, value: str) -> None:
        parsed.values.setdefault(key, value)
        if key in PATTERN_OPTIONS:
            parsed.patterns.append(value)

    i = 0
    while i < len(args):
        a = args[i]
        if isinstance(a, Redirect):
            # the operator and its target are shell syntax, not grep's -- and so is a
            # leading fd digit shlex split off (`2>/dev/null` -> `2`, `>`, `/dev/null`;
            # codex u-sr-09 r7: the `2` had become the pattern)
            if (
                parsed.operands
                and parsed.operands[-1].isdigit()
                and args[i - 1] is parsed.operands[-1]
            ):
                parsed.operands.pop()
            i += 2
            continue
        if a == "--":
            parsed.operands.extend(args[i + 1 :])
            break
        if a.startswith("--") and len(a) > 2:
            name, eq, val = a.partition("=")
            parsed.longs.add(name)
            if name in VALUE_LONG:
                if eq:
                    bind(name, val)
                elif i + 1 < len(args):
                    bind(name, args[i + 1])
                    i += 1
            i += 1
            continue
        if a.startswith("-") and len(a) > 1:
            for j, c in enumerate(a[1:], start=1):
                if c in VALUE_SHORT:
                    rest = a[j + 1 :]
                    if rest:
                        bind(c, rest)
                    elif i + 1 < len(args):
                        bind(c, args[i + 1])
                        i += 1
                    break
                parsed.flags.add(c)
            i += 1
            continue
        parsed.operands.append(a)
        i += 1
    return parsed


def regex_safe(parsed: Args) -> bool:
    """-E/-F/-P (or the long forms) are set: a paren means the same thing to grep and rg."""
    return bool(parsed.flags & REGEX_SAFE_SHORT) or bool(parsed.longs & REGEX_SAFE_LONG)


def has_glob(parsed: Args) -> bool:
    """`-g …` / `--glob …` / `--iglob …` was given. BSD grep has no `g` option in any
    spelling, so every form lands on exit 2."""
    return "g" in parsed.values or bool(parsed.longs & GLOB_LONG)


def patterns_of(parsed: Args) -> list[str]:
    """The PATTERN operands: every `-e`/`--regexp` value if any were given, else the first
    operand (grep's positional pattern). Empty when there is none."""
    if parsed.patterns:
        return list(parsed.patterns)
    return parsed.operands[:1]


def has_unescaped_paren(pattern: str) -> bool:
    """A live `(`/`)` outside any bracket expression, with an even backslash run before it."""
    return _UNESCAPED_PAREN.search(_BRACKET_EXPR.sub(r"\1", pattern)) is not None


def rewritten_at(segment: list[str], original: list[str] | None = None) -> int | None:
    """Index of the `rtk grep` pair that IS the rewrite of `original`: the rewritten segment
    equals the original with `rtk` inserted before its grep/rg word (`env FOO=1 grep x` ->
    `env FOO=1 rtk grep x`; an `rg` word becomes `grep`). A stray `rtk grep` pair that is
    data (`printf %s rtk grep 'f('`, codex u-sr-09 r8) does not satisfy that relation and
    is not a rewrite. Without an original (segments could not be aligned) the first pair
    counts -- the conservative reading. None when the segment carries no rewrite."""
    for i in range(len(segment) - 1):
        if tuple(segment[i : i + 2]) != REWRITTEN_WORDS:
            continue
        if original is None:
            return i
        if (
            i < len(original)
            and original[i] in COMMAND_WORDS
            and segment[:i] == original[:i]
            and segment[i + 2 :] == original[i + 1 :]
        ):
            return i
    return None


def original_word(segment: list[str]) -> str | None:
    """The grep/rg word an ORIGINAL segment ran (the first COMMAND_WORDS token, past any
    prefix), or None when it ran neither."""
    return next((t for t in segment if t in COMMAND_WORDS), None)


def native_failures(rewritten_segment: list[str], original: str | None, at: int) -> list[str]:
    """What the ORIGINAL command fails on by itself, independent of the rewrite: a paren
    in a pattern under an `rg` original, a `-g`/`--glob` under a `grep` original. A deny
    that names a rewrite defect must not promise a re-issue that fails on these
    (codex u-sr-09 r10)."""
    parsed = parse_args(rewritten_segment[at + len(REWRITTEN_WORDS) :])
    out: list[str] = []
    if (
        original == "rg"
        and not regex_safe(parsed)
        and any(has_unescaped_paren(p) for p in patterns_of(parsed))
    ):
        out.append("rg reads a bare `(`/`)` in the pattern as a group")
    if original == "grep" and has_glob(parsed):
        out.append("grep has no -g/--glob")
    return out


def shapes(
    rewritten_segment: list[str], original: str | None = None, at: int | None = None
) -> list[str]:
    """The mangled shapes one rewritten segment carries (empty = the rewrite is fine).
    `original` is the word the caller actually ran: a paren is judged only for a `grep`
    original (BRE; `rg "f("` fails natively and no remedy helps -- codex r6) and a glob
    only for an `rg` original (`grep -g` never worked); an unknown original is judged for
    both, the conservative reading. `at` is the rewrite's index when the caller already
    established it against the original segment."""
    at = rewritten_at(rewritten_segment) if at is None else at
    if at is None:
        return []
    parsed = parse_args(rewritten_segment[at + len(REWRITTEN_WORDS) :])
    found: list[str] = []
    if original in (None, "rg") and has_glob(parsed):
        found.append(
            "an rg-only --glob/-g flag (rtk lands it on BSD grep: 'unrecognized option', exit 2)"
        )
    if (
        original in (None, "grep")
        and not regex_safe(parsed)
        and any(has_unescaped_paren(p) for p in patterns_of(parsed))
    ):
        found.append(
            "an unescaped paren in a BRE pattern (a literal to grep, a group to rg: "
            "'regex parse error', exit 2)"
        )
    return found


def reissue(original: str) -> str | None:
    """`rtk proxy ` prepended to the ORIGINAL text, byte-exact -- offered only when the
    original is ONE simple grep/rg command (no separator, no redirection). None otherwise:
    for anything compound the caller re-issues by hand, because no re-join of shlex tokens
    is faithful to the shell (codex r3 redirections, r4 globs)."""
    toks = tokens(original)
    if toks is None or not toks or toks[0] not in COMMAND_WORDS:
        return None  # a prefixed command (`env FOO=1 grep …`) is re-issued by hand too
    if any(isinstance(t, (Sep, Redirect)) for t in toks):  # a tuple: 3.9 has no X | Y here
        return None
    return "rtk proxy " + original.lstrip()


def _render(toks: list[str]) -> str:
    """Tokens back to one shell line for the REASON's segment echo only (never a command to
    run): bare separators/redirections stay bare, every other word is `shlex.quote`d."""
    return " ".join(t if isinstance(t, (Sep, Redirect)) else shlex.quote(t) for t in toks)


def judge(original: str, rewritten: str) -> str | None:
    """The deny reason for this (original, rtk-rewritten) pair, or None when nothing rtk does
    to it breaks: no `rtk grep` segment, only safe shapes, or a command that does not lex."""
    rtoks = tokens(rewritten)
    if rtoks is None:
        return None
    # rtk rewrites command words in place, so the original's segments align with the
    # rewritten ones by index; a count mismatch (a shape this lexer reads differently from
    # rtk) leaves the original word unknown and both shapes judged (conservative)
    otoks = tokens(original)
    rsegs = segments(rtoks)
    osegs = segments(otoks) if otoks is not None else []
    aligned = len(osegs) == len(rsegs)
    found: list[str] = []
    native: list[str] = []
    segment_text = ""
    for i, seg in enumerate(rsegs):
        oseg = osegs[i] if aligned else None
        at = rewritten_at(seg, oseg)
        if at is None:
            continue
        word = original_word(oseg) if oseg is not None else None
        hits = shapes(seg, word, at)
        native.extend(native_failures(seg, word, at))
        if hits:
            found.extend(hits)
            segment_text = segment_text or _render(seg)
    if not found:
        return None
    fix = reissue(original) if not native else None
    if native:
        tail = (
            f" The command also fails on its own ({'; '.join(native)}) -- fix that first;"
            " then `rtk proxy ` before the grep/rg word skips the rewrite."
        )
    elif fix:
        tail = f" Re-issue as: {fix}"
    else:
        tail = (
            " Re-issue by hand with `rtk proxy ` before each grep/rg word (a compound command"
            " is never re-joined for you: quoting, globs and redirections would not survive)."
        )
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
