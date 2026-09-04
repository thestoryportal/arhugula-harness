#!/usr/bin/env python3
"""Per-ROUND mechanical self-check for an in-flight arc ("leg").

Why this exists, in one paragraph. The `B-71` spec leg took TEN `just
codex-review` rounds. Rounds 1-6 found genuine scope gaps in the artifact;
**rounds 7-10 found defects the absorption rounds themselves introduced** —
an ungrounded code claim, counts that drifted five times across mirrors, a
`§`-label already owned by an older spec version, and an over-correction that
left every behavioural AC unowned. Those four have ONE shape: *a local view was
trusted where the property was global.* A claim's truth is global (the code); a
count's truth is global (all carriers); a label's freeness is global (the whole
delta chain); a register row's readability is global (the rendered prose, not
the YAML). Memories already existed for three of the four and all three were
violated — because the checks were run per ARC, and the defects were introduced
per ROUND. More memories cannot fix that. Making the global checks mechanical
and running them BEFORE EVERY PUSH can.

Roughly 7 of the ~12 findings on that leg were mechanically detectable by the
checks below. Round count — not token count — is what costs wall-clock (ten
serialised review rounds at ~10 min each), so this is the lever.

What it is NOT: a correctness oracle. Every check here answers a question with a
global, cheaply-computable answer. Where a property is genuinely non-mechanical
(is the register row's leading sentence the CURRENT state?), this prints it for
a human to read and says so, rather than pretending to check it. A check that
silently degrades into a rubber stamp would be worse than no check.

Usage:
    python tools/leg_selfcheck.py                 # diff vs origin/main (or main)
    python tools/leg_selfcheck.py --base <ref>
    python tools/leg_selfcheck.py --uncommitted   # include the working tree
    python tools/leg_selfcheck.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The `--detail` boundary is IMPORTED, never re-typed: this module parses the prose
# half of that output, and a second copy of the delimiter would be exactly the
# two-carriers drift B-235 exists to remove.
from forward_register import PROSE_DELIMITER  # noqa: E402

# --- finding model -----------------------------------------------------------

HARD = "HARD"
ADVISORY = "ADVISORY"


@dataclass
class Finding:
    check: str
    severity: str
    message: str

    def render(self) -> str:
        return f"  [{self.severity}] {self.check}: {self.message}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)

    def add(self, check: str, severity: str, message: str) -> None:
        self.findings.append(Finding(check, severity, message))

    @property
    def hard(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == HARD]


# --- git plumbing ------------------------------------------------------------


class BaseRefError(ValueError):
    """The requested base ref does not resolve (fails the run; never silent)."""


def _run(args: list[str]) -> str:
    """Best-effort: used for PROBES whose failure is a legitimate answer
    (`rev-parse --verify` on a ref that may not exist)."""
    out = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return out.stdout


def _run_checked(args: list[str]) -> str:
    """Used where an empty result would be indistinguishable from "nothing to
    check". A base ref can resolve and `git diff base...HEAD` still fail — two
    valid commits with no merge base, for instance — and swallowing the return
    code turned that into an empty diff, zero findings and `leg-selfcheck OK`
    (codex round 3 [P2]; same family as the unresolvable-base fail-open found in
    round 1). Fail closed instead."""
    out = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise BaseRefError(
            f"`{' '.join(args)}` failed (exit {out.returncode}): "
            f"{out.stderr.strip()[:200] or 'no stderr'}"
        )
    return out.stdout


def _ref_exists(ref: str) -> bool:
    return bool(_run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"]).strip())


def resolve_base(explicit: str | None) -> str:
    """Resolve the base ref, FAILING LOUDLY on one that does not exist.

    A gate that cannot find its base must not report success. `git diff
    <bad-ref>...HEAD` writes its error to stderr and prints nothing to stdout,
    so an unvalidated base yielded an empty diff, zero findings, and a cheerful
    `leg-selfcheck OK` — a rubber stamp produced by a typo. That is the
    silent-failure mode this workspace's own discipline forbids, and it is
    worse here than elsewhere because the whole point of the tool is to be
    trusted before a push.
    """
    if explicit:
        if not _ref_exists(explicit):
            raise BaseRefError(
                f"base ref {explicit!r} does not resolve to a commit — refusing to "
                "report a result against an empty diff"
            )
        return explicit
    for cand in ("origin/main", "main"):
        if _ref_exists(cand):
            return cand
    if _ref_exists("HEAD~1"):
        return "HEAD~1"
    raise BaseRefError(
        "no usable base ref (tried origin/main, main, HEAD~1) — pass --base explicitly"
    )


def diff_text(base: str, uncommitted: bool) -> str:
    """The arc's own added lines. `--uncommitted` also folds in the working tree,
    so the check is runnable BEFORE the commit that would otherwise hide a defect
    until the next review round.

    `--uncommitted` is ADDITIVE, not a re-diff: a line introduced by a commit on
    this branch and then deleted in the working tree still appears, because the
    two diffs are concatenated rather than merged. So a finding you have just
    fixed in the tree can persist until you commit. That is the safe direction
    (it over-reports, never under-reports), but it means the authoritative run
    is the committed one — which is also the one the push actually ships.
    """
    parts = [_run_checked(["git", "diff", f"{base}...HEAD"])]
    if uncommitted:
        parts.append(_run_checked(["git", "diff", "HEAD"]))
    return "\n".join(parts)


def added_by_file(diff: str) -> dict[str, list[str]]:
    """Added lines grouped by the file they landed in.

    Grouping (rather than one flat list) is load-bearing for the count check:
    an ARCHIVE move re-adds hundreds of lines of historical prose that are not
    this arc's claims at all, and counting them produced five false "count
    disagreement" findings on this tool's own first run.
    """
    out: dict[str, list[str]] = defaultdict(list)
    current: str | None = None
    for ln in diff.splitlines():
        m = re.match(r"^\+\+\+ b/(.+)$", ln)
        if m:
            current = m.group(1)
            out.setdefault(current, [])
            continue
        if ln.startswith("+") and not ln.startswith("+++") and current is not None:
            out[current].append(ln[1:])
    return dict(out)


def added_with_positions(diff: str) -> dict[str, list[tuple[int, str]]]:
    """Added lines with their new-file line numbers.

    Needed because two EXISTING register rows given body-only edits contribute no
    heading to the added set, so both rows' claims collapsed onto one
    `(unattributed in file)` subject and produced a HARD disagreement on
    perfectly valid per-row counts (codex round 11 [P2]). Positions let each
    added line resolve to its enclosing row in the full file.
    """
    out: dict[str, list[tuple[int, str]]] = defaultdict(list)
    current: str | None = None
    lineno = 0
    for ln in diff.splitlines():
        m = re.match(r"^\+\+\+ b/(.+)$", ln)
        if m:
            current = m.group(1)
            out.setdefault(current, [])
            continue
        h = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", ln)
        if h:
            lineno = int(h.group(1))
            continue
        if current is None:
            continue
        if ln.startswith("+") and not ln.startswith("+++"):
            out[current].append((lineno, ln[1:]))
            lineno += 1
        elif ln.startswith(" "):
            lineno += 1
    return dict(out)


def enclosing_row_at(path: str, lineno: int) -> str | None:
    """The register/plan row whose block encloses `lineno`, read from HEAD."""
    full = ROOT / path
    if not full.is_file():
        return None
    best: str | None = None
    for i, line in enumerate(full.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if i > lineno:
            break
        m = _ROW_ID_RE.match(line) or _UNIT_HEADING_RE.match(line)
        if m:
            best = m.group(1)
    return best


def context_with_positions(diff: str) -> dict[str, list[tuple[int, str]]]:
    """Unchanged context lines WITH their new-file positions.

    Discarding context positions meant two body-only hunks in an aggregate file,
    each whose unchanged context carries its own row's count, both attributed to
    `(unattributed in file)` and produced a false HARD disagreement (codex round
    12 [P2])."""
    out: dict[str, list[tuple[int, str]]] = defaultdict(list)
    current: str | None = None
    lineno = 0
    for ln in diff.splitlines():
        m = re.match(r"^\+\+\+ b/(.+)$", ln)
        if m:
            current = m.group(1)
            out.setdefault(current, [])
            continue
        h = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", ln)
        if h:
            lineno = int(h.group(1))
            continue
        if current is None:
            continue
        if ln.startswith("+") and not ln.startswith("+++"):
            lineno += 1
        elif ln.startswith(" "):
            out[current].append((lineno, ln[1:]))
            lineno += 1
    return dict(out)


def context_by_file(diff: str) -> dict[str, list[str]]:
    """Unchanged CONTEXT lines, grouped by file.

    Widens the count check past added-lines-only (out-of-family review, round 1,
    [P1]): when only ONE mirror is edited, a plan newly claiming 15 acceptance
    criteria never disagrees with itself, so the check passed while an UNCHANGED
    mirror two lines up still said 16. Diff context is the cheapest sound
    widening — it is the unchanged text immediately around every edit, which is
    exactly where a co-located mirror (a section preamble above the body being
    edited) lives, and it costs no extra file reads and adds no whole-file noise.

    Its LIMIT is real and is registered, not papered over: a mirror in a file the
    arc never touched, or further than the diff's context radius, is still
    invisible here. Ground-truth recounting for arbitrary nouns is not soundly
    mechanizable in general; see `B-167`.
    """
    out: dict[str, list[str]] = defaultdict(list)
    current: str | None = None
    for ln in diff.splitlines():
        m = re.match(r"^\+\+\+ b/(.+)$", ln)
        if m:
            current = m.group(1)
            out.setdefault(current, [])
            continue
        if ln.startswith(" ") and current is not None:
            out[current].append(ln[1:])
    return dict(out)


#: Ids whose prose heading a diff DELETES. Module-level so the positional
#: resolver and the register check agree without threading another parameter.
_DELETED_ROW_IDS: set[str] = set()


def changed_line_numbers(diff: str) -> dict[str, set[int]]:
    """New-file line numbers touched, per file, parsed from `@@` hunk headers.

    Needed because an AMENDED register row does not re-add its `- id:` /
    `### B-*` declaration — only the changed field or bullet — so scanning added
    lines for an id found nothing and check 4 silently skipped exactly the case
    it matters most for: an implementation closing a finding by editing its
    existing row (codex round 3 [P1]).
    """
    out: dict[str, set[int]] = defaultdict(set)
    current: str | None = None
    lineno = 0
    for ln in diff.splitlines():
        m = re.match(r"^\+\+\+ b/(.+)$", ln)
        if m:
            current = m.group(1)
            out.setdefault(current, set())
            continue
        h = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", ln)
        if h:
            lineno = int(h.group(1))
            continue
        if current is None:
            continue
        if ln.startswith("+") and not ln.startswith("+++"):
            out[current].add(lineno)
            lineno += 1
        elif ln.startswith("-") and not ln.startswith("---"):
            # A deleted ROW HEADING names an id that no added line mentions and
            # that rows_enclosing (which reads the post-deletion file) resolves to
            # an ADJACENT row — so a row whose whole prose block is deleted was
            # never re-checked and the gate exited green (codex round 14 [P2]).
            m_del = _ROW_ID_RE.match(ln[1:])
            if m_del:
                _DELETED_ROW_IDS.add(m_del.group(1))
            # A DELETION advances no new-file position, so recording nothing left
            # `amended` empty for a deletion-only edit — and deleting a row's
            # final prose body is EXACTLY the heading-only regression this gate
            # exists to block (codex round 5 [P2]).
            #
            # Record the position BEFORE the deletion as well (codex round 7
            # [P2]): when the removed line was a row's LAST body line, the
            # new-file `lineno` is already the NEXT row's heading, so attributing
            # only that position made rows_enclosing pick the FOLLOWING row and
            # the emptied row was never checked — the gate exited green on
            # precisely the regression it exists to block.
            out[current].add(max(1, lineno))
            out[current].add(max(1, lineno - 1))
        elif ln.startswith(" "):
            lineno += 1
    return dict(out)


def rows_enclosing(path: str, lines: set[int]) -> set[str]:
    """Register row ids whose block encloses any of `lines`, read from the file
    at HEAD — the enclosing-row resolution an added-lines scan cannot do."""
    full = ROOT / path
    if not full.is_file() or not lines:
        return set()
    boundaries: list[tuple[int, str]] = []
    for i, line in enumerate(full.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        m = _ROW_ID_RE.match(line)
        if m:
            boundaries.append((i, m.group(1)))
    if not boundaries:
        return set()
    found: set[str] = set()
    for n in lines:
        prior = [rid for start, rid in boundaries if start <= n]
        if prior:
            found.add(prior[-1])
    return found


def added_lines(by_file: dict[str, list[str]]) -> list[str]:
    return [ln for lines in by_file.values() for ln in lines]


#: Historical carriers. Lines APPENDED to these are relocated history, not
#: claims this arc is making, so count-claim scanning must skip them.
_HISTORY_PATHS = ("archive", "-log", "_log")


def is_history_path(path: str) -> bool:
    name = Path(path).name.lower()
    return any(tok in name for tok in _HISTORY_PATHS)


def is_fixture_path(path: str) -> bool:
    """Test files, which are excluded from every content check.

    This is not convenience — it is the only sound answer to a self-reference
    that bit twice on this tool's own first runs. A checker that scans the repo
    for INVALID shapes will always find them in the tests that exercise it: the
    suite for this module deliberately contains a cite whose line number is past
    end-of-file, and a pair of sentences claiming different counts of the same
    noun. Both were reported as real defects.

    Note the corollary, learned the same way: this rule covers test FILES, so
    prose ANYWHERE ELSE must not spell out a defective example literally. An
    earlier draft of this very docstring quoted the out-of-range cite verbatim
    and the gate — correctly — flagged its own explanation. Describe the shape;
    do not write it.

    The cost is real and stated: a genuinely stale cite inside a test docstring
    is not caught here. The alternative — letting the gate red on its own
    fixtures — gets the gate muted, which costs every check, not one.
    """
    p = path.lower()
    return Path(p).name.startswith("test_") or "/tests/" in p


# --- check 1: cite resolution ------------------------------------------------

#: `path:N`, `path:N-M`, and the repo's common list forms `path:6,10,47,51` and
#: `path:119/121/122`. Capturing only the FIRST number let a stale later location
#: pass unseen (codex round 6 [P2]).
_CITE_RE = re.compile(
    r"(?<![\w/])((?:[\w.\-]+/)*[\w.\-]+\.(?:py|md|sh|toml|ya?ml|json))"
    r":(\d+(?:\s*[-–/,]\s*\d+)*)"
)


def _cite_line_numbers(spec: str) -> list[int]:
    return [int(n) for n in re.findall(r"\d+", spec)]


def _resolve_cited_path(rel: str, source: str) -> Path | None:
    """Repo-root first, then RELATIVE TO THE CITING FILE's directory — the repo's
    common sibling shorthand (a `design-substrate` file citing
    `Spec_Harness_Runtime_v1.md:...`) resolved at the root only, so an existing
    sibling was downgraded to "unresolvable" and a stale line number passed
    (codex round 6 [P2])."""
    root_rel = ROOT / rel
    if root_rel.is_file():
        return root_rel
    sibling = (ROOT / source).parent / rel
    if sibling.is_file():
        return sibling
    return None


def _target_line_count(path: Path, rel: str, base_ref: str | None) -> int | None:
    """Line count of a cited target, read from the SNAPSHOT being judged.

    A committed run judges committed HEAD, but reading the working tree let local
    WIP that adds lines make a stale committed cite pass (codex round 12 [P2]).
    In committed mode read the blob from HEAD; fall back to the working tree only
    when the path is untracked there.
    """
    if base_ref is not None:
        try:
            blob = _run_checked(["git", "show", f"HEAD:{rel}"])
            return len(blob.splitlines())
        except BaseRefError:
            # ABSENT AT HEAD is unresolved, not a reason to consult the working
            # tree: a committed line citing a file that exists only as untracked
            # WIP otherwise reported "resolved" while the push omits its target
            # entirely (codex round 13 [P2]). Working-tree fallback belongs to
            # --uncommitted alone.
            return None
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:  # pragma: no cover
        return None


def deleted_paths(diff: str) -> set[str]:
    """Paths this diff deletes (`+++ /dev/null`)."""
    out: set[str] = set()
    prev: str | None = None
    for ln in diff.splitlines():
        m = re.match(r"^--- a/(.+)$", ln)
        if m:
            prev = m.group(1)
            continue
        if ln.startswith("+++ /dev/null") and prev:
            out.add(prev)
        if ln.startswith("+++ "):
            prev = None
    return out


def check_cites(
    by_file: dict[str, list[str]],
    report: Report,
    committed_ref: str | None = None,
    removed: set[str] | None = None,
) -> None:
    """Re-resolve every `path:NNN` the arc ADDED, at the CURRENT HEAD.

    This is the check that would have caught the `:1543`/`:2238` fold sites and
    the `_pre_dispatch_gate_owning_branch_identity` guard cites: a line number
    written from an earlier read drifts the moment the file is edited, and a
    review round is a very expensive way to discover that.
    """
    # Keyed by the CITING SOURCE too: resolution is source-relative, so two
    # documents in different directories citing the same sibling shorthand
    # (`DELIVERABLE.md:100`) are DIFFERENT claims. A (rel, spec) key collapsed
    # them and skipped the second — stale, and green (codex round 8 [P2]).
    seen: set[tuple[str, str, str]] = set()
    checked = 0
    # History carriers (`*-log*`, `*_log*`, `*archive*`) are skipped here as in the count
    # scan: a gate-log row records a reviewer finding's location AT THE HEAD IT REVIEWED, and
    # that line number drifts by design as the arc absorbs the finding -- it is evidence of
    # a past head, not a claim this arc makes about the current one (S1, the first tracked
    # `.harness/merge-gate-log.jsonl` rows).
    scanned = [
        (path, line)
        for path, lines in by_file.items()
        if not is_fixture_path(path) and not is_history_path(path)
        for line in lines
    ]
    for source, line in scanned:
        for m in _CITE_RE.finditer(line):
            rel, spec = m.group(1), m.group(2)
            key = (source, rel, spec)
            if key in seen:
                continue
            seen.add(key)
            path = _resolve_cited_path(rel, source)
            if path is None:
                if rel in (removed or set()):
                    # A path THIS DIFF deletes is unambiguously a stale repo cite,
                    # not a possible external reference (codex round 14 [P2]).
                    report.add(
                        "cite",
                        HARD,
                        f"{rel}:{spec} — this diff DELETES {rel}, so the cite is stale",
                    )
                    continue
                # Not every `word.md:12` is a repo cite (URLs, prose, other repos).
                # Only a path that RESOLVES is a claim this tool can judge; an
                # unresolvable one is reported advisory, never as a hard failure.
                report.add(
                    "cite",
                    ADVISORY,
                    f"{rel}:{spec} — path does not resolve at the repo root or "
                    f"beside {source} (not a repo cite, or the file moved)",
                )
                continue
            checked += 1
            resolved_rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else rel
            total = _target_line_count(path, resolved_rel, committed_ref)
            if total is None:
                report.add("cite", ADVISORY, f"{rel}: unreadable")
                continue
            nums = _cite_line_numbers(spec)
            # `n > total` alone accepted `file.py:0` as resolved: line 0 never
            # exists, so a placeholder or zero-based cite failed open (codex
            # round 8 [P2]).
            stale = [n for n in nums if n > total]
            invalid = [n for n in nums if n < 1]
            if stale or invalid:
                parts = []
                if invalid:
                    parts.append(f"line(s) {', '.join(map(str, invalid))} are not valid (< 1)")
                if stale:
                    parts.append(
                        f"line(s) {', '.join(map(str, stale))} are past end-of-file "
                        f"({total} lines at HEAD)"
                    )
                report.add("cite", HARD, f"{rel}:{spec} — {'; '.join(parts)}; stale cite")
    report.stats["cites_resolved"] = checked


# --- check 2: count consistency ----------------------------------------------

_NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}

#: The nouns whose counts drifted on the `B-71` leg, plus the obvious siblings.
#: Each maps to a canonical bucket so "AC"/"acceptance criteria" collide.
_COUNT_NOUNS: list[tuple[str, str]] = [
    (r"carrier amendments?", "carrier amendments"),
    (r"amendments?", "amendments"),
    (r"acceptance criteria", "acceptance criteria"),
    (r"ACs?\b", "acceptance criteria"),
    (r"mutation[- ]probe(?:s| obligations)?", "mutation probes"),
    (r"probes?\b", "mutation probes"),
    (r"payload_body keys?", "payload_body keys"),
    (r"payload keys?", "payload_body keys"),
    (r"sites?\b", "sites"),
    (r"follow[- ]ons?", "follow-ons"),
    (r"artifacts?\b", "artifacts"),
]

#: The number itself. The negative lookbehind is what keeps this from reading a
#: PR reference or a section number as a count claim: on this tool's own first
#: run `Post-#935 follow-on refresh` and `§12.2 owed follow-on` were both
#: reported as "follow-ons" counts of 935 and 2. `#` excludes PR refs, `.`
#: excludes the tail of a dotted section label, `-` excludes date fragments.
_NUM = r"(?<![#\w.\-])(\d+|" + "|".join(_NUMBER_WORDS) + r")"


#: A count claim's SUBJECT. Without one, every claim for a noun lands in a single
#: repo-wide bucket, so a legitimate co-land ("U-CP-102 has 16 acceptance criteria",
#: "U-RT-155 has 11") reports a HARD disagreement — which is exactly the shape of the
#: B-71 leg this gate was built for, i.e. it would have false-positived on its own
#: motivating arc (codex round 2 [P2]). A unit id on the line is the subject when
#: present; otherwise claims are compared only WITHIN one file, which still catches
#: the preamble-vs-body drift the context widening exists for, without comparing two
#: unrelated artifacts' unattributed numbers.
_UNIT_ID_RE = re.compile(r"\bU-[A-Z]+-\d+\b")


#: A plan/spec unit heading, so an aggregate artifact's counts attribute to the
#: unit they sit under rather than to the file as a whole.
_UNIT_HEADING_RE = re.compile(r"^\s*#{1,6}\s+.*?\b(U-[A-Z]+-\d+)\b")


def _claim_subject(line: str, enclosing: str, at: int = 0) -> str:
    """The unit a count claim at offset `at` belongs to: the NEAREST unit id at
    or before it on the line.

    Taking the line's FIRST unit id attributed every count on a multi-unit line
    to one subject, so a single summary sentence — "U-CP-102 = 16 acceptance
    criteria ... U-RT-155 = 11 acceptance criteria", exactly the shape the
    upcoming co-land uses — became two conflicting claims for U-CP-102 and
    hard-failed the pre-push gate (codex round 3 [P1]).
    """
    best: str | None = None
    for m in _UNIT_ID_RE.finditer(line):
        if m.start() <= at:
            best = m.group(0)
        else:
            break
    if best is None:
        # A claim before ANY unit id on the line still belongs to the first one
        # named there, if any — a leading "16 acceptance criteria for U-CP-102".
        nxt = _UNIT_ID_RE.search(line)
        best = nxt.group(0) if nxt else None
    return best or enclosing


# --- B-167 step 1: a FORMAT-SCOPED acceptance-criteria recount ------------------
#
# `check_counts` below compares claims against each other and never recounts.
# `B-167` asked whether a recount against GROUND TRUTH is buildable at all. Step 1
# of its close-out says to answer that BY EXECUTION against the real plan corpus
# rather than by argument. It was, and this is the result.
#
# MEASURED over every `Implementation_Plan_*.md` in `design-substrate/` (388 blocks
# carrying an acceptance-criteria section):
#
#   * 287 are DERIVABLE — an unqualified header plus a contiguous 1..N numbered
#     list and no top-level bullets. The recount is exact on these.
#     (re-derived 2026-08-16 under fence-aware block segmentation: an earlier pass
#     counted `#` comments INSIDE fenced code as unit headings, splitting two real
#     blocks, and read `U-CP-00b` as `U-CP-00`.)
#   * 101 are NOT — amendment / additions blocks that renumber into a PARENT unit's
#     space (one observed list starts at `0`) or carry no numbered list at all.
#     A recount of these is meaningless: the numbers belong to another artifact.
#   * Of the derivable blocks only 8 reference their own criteria numbers at all,
#     so IN-BLOCK corroboration is nearly absent. All 8 agree once references to
#     ANOTHER plan's unit are excluded (the one apparent contradiction, U-RT-147,
#     cites `CP plan v2.41 U-CP-45`'s criterion, not its own).
#
# So the recount's value is exactly what `B-167` wanted and no more: it derives a
# ground-truth number that an EXTERNAL claim can be checked against. It is not
# self-checking, and it is NOT wired into any gate here — `B-167` step 3 owes a
# false-positive measurement against already-merged arcs before that is earned.

_AC_HEADER_RE = re.compile(r"\*\*Acceptance criteria([^*]*)\*\*")
_AC_NEXT_SECTION_RE = re.compile(r"\n\*\*[A-Z][^*\n]{3,}\*\*")
_AC_ITEM_RE = re.compile(r"^([0-9]+)\. ", re.MULTILINE)
_AC_BULLET_RE = re.compile(r"^[-*] ", re.MULTILINE)
_MP_HEADER_RE = re.compile(r"\*\*Mutation-probe obligations[^*]*\*\*")
_MP_CRITERIA_RE = re.compile(r"[Cc]riteri(?:on|a)\s+#?([0-9][0-9,\s and#]*)")


def derive_acceptance_criteria_count(unit_block: str) -> int | None:
    """Recount a unit block's acceptance criteria, or `None` when not exact.

    Returns a count ONLY for a FRESH enumeration: an acceptance-criteria header
    with no parenthetical qualifier, followed by a numbered list running
    contiguously from 1. Returns `None` for everything else — an amendment or
    additions block, a list that starts anywhere but 1, a gap in the numbering,
    or no list at all.

    `None` means "not exactly derivable here", never "zero". A caller must treat
    the two differently: reporting a disagreement against a `None` would be the
    false-positive class that gets a gate muted.
    """
    header = _AC_HEADER_RE.search(unit_block)
    if header is None:
        return None
    # A parenthetical qualifier marks a delta against a parent unit's numbering
    # ("(v2.41 additions):", "(v2.4 amendment):"). Its numbers are not this
    # block's to count.
    qualifier = header.group(1).strip()
    if qualifier not in ("", ".", ":"):
        return None

    rest = unit_block[header.end() :]
    nxt = _AC_NEXT_SECTION_RE.search(rest)
    section = rest[: nxt.start()] if nxt else rest

    numbers = [int(m.group(1)) for m in _AC_ITEM_RE.finditer(section)]
    if not numbers or numbers != list(range(1, len(numbers) + 1)):
        return None
    # A MIXED section — a numbered list plus top-level bullet criteria — is not
    # exactly countable by the numbered list alone, and counting it anyway is
    # worse than declining: it yields a confidently INCOMPLETE ground truth.
    # The corpus really carries this shape (`U-RT-138` is 4 numbered + 1 bullet;
    # `U-RT-141` is 6 + 2), and an earlier draft of this helper returned 4 and 6.
    if _AC_BULLET_RE.search(section):
        return None
    return len(numbers)


def derive_mutation_probe_count(unit_block: str) -> int | None:
    """Recount the criteria a unit block's mutation-probe obligation names.

    The second recipe `B-167` step 1 supplies. The obligations line enumerates the
    criteria carrying a `# mutation-probe:` annotation ("Criteria 4, 6, 7, 10, 11,
    12, 14, 15 and 16 each carry..."), so the derived count is the size of that
    set — de-duplicated, because a block may name the same criterion twice.

    Returns `None` when no obligations section names any criterion, so a caller
    cannot mistake "not stated" for "zero probes owed".

    Only the obligations SECTION is read. An earlier ad-hoc run of this recipe
    over a whole block also matched a `Criteria 9 and ...` reference belonging to
    unrelated prose, which is the same cross-reference trap that made a naive
    corroboration check mis-score `U-RT-147`.
    """
    header = _MP_HEADER_RE.search(unit_block)
    if header is None:
        return None
    rest = unit_block[header.end() :]
    nxt = _AC_NEXT_SECTION_RE.search(rest)
    section = rest[: nxt.start()] if nxt else rest

    found: set[int] = set()
    for run in _MP_CRITERIA_RE.findall(section):
        found.update(int(x) for x in re.findall(r"\d+", run))
    return len(found) or None


def check_counts(
    by_file: dict[str, list[str]],
    report: Report,
    context: dict[str, list[str]] | None = None,
    positions: dict[str, list[tuple[int, str]]] | None = None,
) -> None:
    """Detect DISAGREEMENT between count claims, which is the actual defect.

    Deliberately NOT a recount against ground truth: "how many ACs does this
    unit really have" is unbounded to compute for every noun in every artifact.
    What IS bounded, and is exactly what went wrong five times on `B-71`, is
    that the SAME noun was claimed with DIFFERENT numbers across the spec
    preamble, the section body, the plan delta, the clearance marker and the
    register row. Two different answers to one question is a defect regardless
    of which is right — so that is what this reports.
    """
    claims: dict[tuple[str, str], dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))

    # PROSE ARTIFACTS ONLY. Every carrier that drifted on the `B-71` leg was a
    # `.md` (spec preamble, section body, plan delta, clearance marker,
    # artifact-pointers, the prose register) or the register `.yaml` — a count
    # mirror does not live in source. Scanning source made this tool read its
    # OWN test fixtures ("It has 3 sites." / "It has 9 sites.") as a real
    # disagreement on its first committed-branch run.
    def _eligible(path: str) -> bool:
        return (
            path.lower().endswith((".md", ".yaml", ".yml"))
            and not is_history_path(path)
            and not is_fixture_path(path)
        )

    def _with_enclosing(source: dict[str, list[str]]) -> list[tuple[str, str, str]]:
        """(path, enclosing-row-or-file, line), preserving order.

        The whole-FILE fallback collapsed unrelated rows in an aggregate carrier:
        two register rows added in one round, each legitimately claiming a
        different count, shared one subject and produced a HARD block (codex
        round 10 [P2]). Track the nearest preceding row/unit heading instead.
        """
        out: list[tuple[str, str, str]] = []
        pos_map = positions or {}
        for path, lines in source.items():
            if not _eligible(path):
                continue
            # Occurrences, in order: a {text: line} map kept only the LAST
            # occurrence, so identical context text repeated in a later row
            # attributed an earlier row's claim to that later row and hid a real
            # disagreement (codex round 13 [P2]).
            occurrences: dict[str, list[int]] = defaultdict(list)
            for ln, text in pos_map.get(path, []):
                occurrences[text].append(ln)
            consumed: dict[str, int] = defaultdict(int)
            enclosing = f"(unattributed in {path})"
            for line in lines:
                m = _ROW_ID_RE.match(line) or _UNIT_HEADING_RE.match(line)
                if m:
                    enclosing = m.group(1)
                else:
                    # A body-only edit contributes no heading, so resolve the
                    # enclosing row from the file at HEAD by POSITION.
                    slots = occurrences.get(line, [])
                    idx = consumed[line]
                    at = slots[idx] if idx < len(slots) else None
                    if at is not None:
                        consumed[line] = idx + 1
                        resolved = enclosing_row_at(path, at)
                        if resolved:
                            enclosing = resolved
                out.append((path, enclosing, line))
        return out

    scanned = _with_enclosing(by_file)
    # Unchanged text immediately around the edits, so a single edited mirror can
    # still disagree with an untouched co-located one (codex round 1 [P1]).
    scanned += _with_enclosing(context or {})
    for _path, enclosing, line in scanned:
        low = line.lower()
        if len(set(_UNIT_ID_RE.findall(line))) > 1:
            # A line naming two or more units cannot be attributed by position:
            # "U-CP-102 = 16 ... U-RT-155 = 11" wants nearest-PRECEDING, while
            # "16 ... for U-CP-102; 11 ... for U-RT-155" wants nearest-FOLLOWING,
            # and both shapes are ordinary prose here. Two successive heuristics
            # each produced a FALSE hard disagreement on the other shape, so this
            # stops guessing: an ambiguous line is skipped and said to be skipped.
            # For a gate that BLOCKS pushes, silence beats a confident wrong answer.
            report.add(
                "count",
                ADVISORY,
                f"multi-unit line NOT count-checked (unattributable): {line.strip()[:120]}",
            )
            continue
        # MOST-SPECIFIC noun wins. `_COUNT_NOUNS` is ordered specific -> generic,
        # and the intervening-word matcher lets a generic pattern swallow a
        # specific phrase: "3 carrier amendments" matched `amendments?` too (the
        # matcher consumes "carrier"), so 3 landed in the generic bucket and
        # collided with a perfectly consistent "5 amendments" total — a HARD
        # block on valid prose (codex round 9 [P2]). Claiming spans left-to-right
        # in specificity order makes the first (most specific) match own the text.
        claimed: list[tuple[int, int]] = []
        for pattern, bucket in _COUNT_NOUNS:
            for m in re.finditer(rf"{_NUM}\s+(?:\w+[- ]){{0,2}}?{pattern}", low, re.IGNORECASE):
                if any(m.start() < end and start < m.end() for start, end in claimed):
                    continue
                claimed.append((m.start(), m.end()))
                raw = m.group(1).lower()
                value = int(raw) if raw.isdigit() else _NUMBER_WORDS[raw]
                subject = _claim_subject(line, enclosing, m.start())
                claims[(subject, bucket)][value].append(line.strip()[:150])

    for (subject, bucket), by_value in sorted(claims.items()):
        if len(by_value) > 1:
            values = ", ".join(str(v) for v in sorted(by_value))
            report.add(
                "count",
                HARD,
                f"{bucket!r} for {subject} is claimed with {len(by_value)} DIFFERENT "
                f"values ({values}) — mirrors of the SAME subject disagree; recount "
                "programmatically and fix every carrier",
            )
            for value in sorted(by_value):
                for example in by_value[value][:2]:
                    report.add("count", ADVISORY, f"  {subject} {bucket}={value}: {example}")
    report.stats["count_nouns_seen"] = len(claims)


# --- check 3: § label collision ----------------------------------------------

#: A newly-MINTED label, not a cite: a markdown heading, or a bolded run-in
#: heading, that introduces `§X.Y`. A bare `§25.4` in prose is a reference and
#: is expected to already exist elsewhere — flagging those would make this
#: check pure noise.
#: A section is DECLARED by a markdown heading. An earlier version also accepted a
#: bolded run-in (`**§2.2 substantive content preserved verbatim...**`), but those
#: are prose REFERENCES to a section, not declarations of one, and they accounted
#: for the remaining measured false positives.
_MINT_RE = re.compile(r"^\s*#{1,6}\s+§(\d+(?:\.[\w-]+)+)")
#: The label token includes any non-numeric segments: the CXA chain uses
#: `§0.5.refresh` / `§0.5.preserved` / `§0.5.new` as THREE distinct labels, and
#: capturing only `0.5` reported them as one number reused three times (measured:
#: 31 of 265 artifacts firing, nearly all of it this one shape).
_HEADING_USE_RE = re.compile(r"^\s*#{1,6}\s+§(\d+(?:\.[\w-]+)+)")


#: An artifact's version-chain FAMILY: `Spec_Control_Plane_v1_119.md` and
#: `Spec_Control_Plane_v1_32.md` are the same family, so a label minted in one is
#: judged against the other — while an unrelated axis's spec is not consulted at all.
_VERSION_SUFFIX_RE = re.compile(r"_v\d+(?:_\d+)*$", re.IGNORECASE)


def _artifact_family(name: str) -> str:
    stem = Path(name).stem
    return _VERSION_SUFFIX_RE.sub("", stem).lower()


def _normalize_heading(line: str) -> str:
    """Heading text with markup, the label itself, and case removed, so a verbatim
    re-table in a delta compares EQUAL to its original."""
    text = re.sub(r"^\s*#{1,6}\s+", "", line)
    text = re.sub(r"^§\d+(?:\.[\w-]+)+\s*", "", text)
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()


#: Memoised per (directory, family-set) for the process. The previous code
#: re-globbed the directory AND re-read every artifact once per MINTED LABEL,
#: which is quadratic in production, not only in the corpus test that measured
#: it at 45s (codex round 8 [P2]).
_SIBLING_INDEX_CACHE: dict[tuple[str, frozenset[str]], dict[str, set[str]]] = {}


def _sibling_label_index(family_dir: Path, families: frozenset[str]) -> dict[str, set[str]]:
    key = (str(family_dir.resolve()), families)
    cached = _SIBLING_INDEX_CACHE.get(key)
    if cached is not None:
        return cached
    index: dict[str, set[str]] = defaultdict(set)
    for f in sorted(family_dir.glob("*.md")):
        if _artifact_family(f.name) not in families:
            continue
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:  # pragma: no cover
            continue
        for line in body.splitlines():
            m = _HEADING_USE_RE.match(line)
            if m:
                index[m.group(1)].add(f.name)
    result = dict(index)
    _SIBLING_INDEX_CACHE[key] = result
    return result


def check_label_collisions(
    by_file: dict[str, list[str]], report: Report, substrate_dir: Path | None = None
) -> None:
    """A `§` label's freeness is a property of the WHOLE delta chain.

    `§25.17`/`§25.18` were minted on the `B-71` leg and were already CP v1.32's.
    Nothing local to the file being edited can see that — the chain is many
    files — so the check has to scan all of `design-substrate/`.
    """
    # MARKDOWN ONLY. `§` labels are minted in prose artifacts, never in source —
    # and a Python comment that happens to open `# §12.2.1` is byte-identical to
    # an h1 heading, which this tool reported as a minted label on its own first
    # run. Scoping by file type is what makes the heading shape unambiguous.
    # (family, label): unioning every changed family let a label minted only in a
    # CP artifact be queried against Runtime siblings merely because a Runtime
    # file was also touched — cross-family false warnings that contradict the
    # family isolation this check is built on (codex round 10 [P2]).
    minted_pairs = sorted(
        {
            (_artifact_family(path), m.group(1))
            for path, lines in by_file.items()
            if path.lower().endswith(".md") and not is_fixture_path(path)
            for line in lines
            if (m := _MINT_RE.match(line))
        }
    )
    minted = sorted({label for _, label in minted_pairs})
    report.stats["labels_minted"] = len(minted)
    report.stats["labels"] = [f"§{label}" for label in minted]
    if not minted:
        return

    # WHAT IS SOUND HERE, MEASURED RATHER THAN ASSUMED — and the answer is
    # "advisory", which is why this check reports instead of blocking.
    #
    # Four designs were measured against the real 247-artifact corpus by
    # re-minting every artifact's own headings and counting hard failures:
    #   (i)   "label heads a section in >1 artifact" — `§0.1` is used by 149
    #         unrelated specs/plans; almost every spec arc would fail
    #         (codex round 2 [P1]).
    #   (ii)  "label carries >1 distinct TITLE in its version family" — 241/265
    #         (91%). The per-axis specs are DELTA chains where
    #         `§0.1 Revision context` legitimately differs in every version.
    #   (iii) narrowing the label token (`§0.5.refresh` / `.preserved` / `.new`
    #         are THREE labels, not one) and then accepting only real markdown
    #         headings (a bolded `**§2.2 ... preserved verbatim**` is a prose
    #         REFERENCE, not a declaration): 31/265, then 6/247.
    #   (iv)  the surviving 6 are not all defects: a plan delta legitimately
    #         carries `### §0.1 Net delta from v2.12` AND `### §0.1 Net delta
    #         from v2.11` in ONE file, so a HARD rule here would block every
    #         routine plan-delta arc.
    #
    # No variant reaches a precision that justifies BLOCKING, because the corpus
    # reuses section numbers by convention both across versions and within delta
    # files. So the check surfaces what it knows — the other places this label is
    # used — and lets the author judge, which is the value the B-71 defect
    # actually needed (nobody looked). Making it hard would get it muted, and a
    # muted gate costs every check, not one. Residual registered at `B-167`.
    for path, lines in by_file.items():
        if not path.lower().endswith(".md") or is_fixture_path(path):
            continue
        seen: dict[str, list[str]] = defaultdict(list)
        full = ROOT / path
        source = (
            full.read_text(encoding="utf-8", errors="replace").splitlines()
            if full.is_file()
            else lines
        )
        for line in source:
            m = _HEADING_USE_RE.match(line)
            if m and m.group(1) in minted:
                seen[m.group(1)].append(_normalize_heading(line))
        for label, titles in sorted(seen.items()):
            if len(set(titles)) > 1:
                report.add(
                    "label",
                    ADVISORY,
                    f"§{label} numbers {len(set(titles))} DIFFERENT sections within "
                    f"{path} — one document must not reuse a section number "
                    f"({'; '.join(sorted(set(titles))[:3])})",
                )

    family_dir = substrate_dir or (ROOT / "design-substrate")
    for family, label in minted_pairs:
        index = _sibling_label_index(family_dir, frozenset({family}))
        siblings = sorted(index.get(label, ()))
        if len(siblings) > 1:
            report.add(
                "label",
                ADVISORY,
                f"§{label} also heads a section in {len(siblings) - 1} sibling "
                f"version(s) ({', '.join(siblings[:4])}) — CONFIRM this is a "
                "deliberate re-table and not a reused number (the B-71 defect); "
                "no mechanical rule can tell them apart in a delta chain",
            )


# --- check 4: register row renders its current state -------------------------

_ROW_ID_RE = re.compile(r"^(?:- id:|### )\s*([BR]-[A-Z0-9]+(?:-[A-Z0-9]+)*)")
_NEW_PROSE_HEADING_RE = re.compile(r"^### \s*([BR]-[A-Z0-9]+(?:-[A-Z0-9]+)*)")
#: The register's structural current-state marker. Present on 35 of 165 rows at
#: the time this gate landed, so it is required of NEW rows and merely reported
#: for legacy ones — a corpus-wide hard requirement would red 130 valid rows.
_CURRENT_STATE_RE = re.compile(r"^\s*-\s+\*\*Current state[.:]?\*\*")
#: The lead bullets a NEW row may open with. All three are timeless framings
#: ("what this is", "what was true", "what is true now") — none can go stale
#: into a misleading directive the way a leading instruction does.
_ACCEPTED_LEAD_RE = re.compile(
    r"^\s*-\s+\*\*(What it is|What it was|Current state)[.:]?\*\*", re.IGNORECASE
)


def _detail_via_cli(rid: str) -> tuple[int, str]:
    out = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "forward_register.py"), "--detail", rid],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return out.returncode, out.stdout


def check_register_rows(
    added: list[str],
    paths: list[str],
    report: Report,
    detail_fn: Callable[[str], tuple[int, str]] | None = None,
    amended: set[str] | None = None,
    register_added: dict[str, list[str]] | None = None,
    base_ids: set[str] | None = None,
    uncommitted: bool = False,
) -> None:
    """`--detail <ID>` renders the PROSE carrier, not the YAML `summary`.

    A row written only into `forward-register.yaml` prints just its heading —
    so the next session reading `--detail` sees a title and nothing else and
    concludes the row is empty. The "leads with current state, not a superseded
    instruction" half is genuinely non-mechanical, so the leading bullet is
    PRINTED for a human rather than pattern-matched into a fake verdict.
    """
    if not any(
        p.endswith(("forward-register.yaml", "post-phase-8-forward-register.md")) for p in paths
    ):
        return
    scoped = {
        line
        for path, lines in (register_added or {}).items()
        if path.endswith(("forward-register.yaml", "post-phase-8-forward-register.md"))
        for line in lines
    } or set(added)
    ids = sorted(
        {m.group(1) for line in scoped if (m := _ROW_ID_RE.match(line))} | set(amended or ())
    )
    # A row is NEW when this arc adds its prose HEADING (`### B-166 · ...`);
    # merely amending an existing row's body never re-adds that line.
    candidate_new = {
        m.group(1)
        for path, lines in (register_added or {}).items()
        if path.endswith("post-phase-8-forward-register.md")
        for line in lines
        if (m := _NEW_PROSE_HEADING_RE.match(line))
    }
    # Correcting an EXISTING row's title re-adds its `### B-*` line, which would
    # classify a legacy row as new and hard-fail it for lacking the newly
    # required Current-state bullet (codex round 6 [P2]). Newness is a property
    # of the BASE: a row is new only if its id was absent there.
    known = base_ids if base_ids is not None else set()
    new_ids = {rid for rid in candidate_new if rid not in known}
    report.stats["register_rows_touched"] = len(ids)
    report.stats["register_rows_new"] = len(new_ids)
    detail = detail_fn or _detail_via_cli
    # `--detail` renders the WORKING TREE, while a normal run diffs committed
    # HEAD. A committed YAML-only row with an uncommitted prose fix therefore
    # reported OK, and the push still shipped the heading-only committed row
    # (codex round 11 [P2]). Fail closed on that mismatch rather than validating
    # content the push will not carry.
    if ids and detail_fn is None and not uncommitted:
        dirty = [
            line[3:].strip()
            for line in _run(["git", "status", "--porcelain"]).splitlines()
            if line[3:]
            .strip()
            .endswith(("forward-register.yaml", "post-phase-8-forward-register.md"))
        ]
        if dirty:
            report.add(
                "register",
                HARD,
                f"register carrier(s) have UNCOMMITTED changes ({', '.join(dirty)}) but "
                "this run judges committed HEAD — `--detail` would validate prose the "
                "push will not carry. Commit them, or re-run with --uncommitted.",
            )
            return
    for rid in ids:
        rc, stdout = detail(rid)
        # `--detail` prints a CANONICAL close_out header, then PROSE_DELIMITER on its own
        # line, then the prose block. Only the prose half is what these two checks judge:
        # counting the header as body would make `not body` unreachable and silently
        # retire the YAML-only-row detection below.
        #
        # The frame is parsed as an EXACT UNINDENTED LINE, never a substring. A substring
        # split lets row CONTENT choose the framing: a close_out containing the delimiter
        # text would split inside the header, carry its own remaining lines into the prose
        # half, and a heading-only row would stop reporting HEADING ONLY (codex r1 [P2]).
        # The CLI renders every close_out line with a two-space indent, so an unindented
        # delimiter line cannot be produced by row content at all.
        # An injected `detail_fn` (tests) may emit no delimiter, in which case the whole
        # output IS the prose half.
        lines = stdout.splitlines()
        try:
            cut = lines.index(PROSE_DELIMITER) + 1
        except ValueError:
            cut = 0
        body = [ln for ln in lines[cut:] if ln.strip() and not ln.startswith("###")]
        if rc != 0:
            report.add("register", HARD, f"{rid}: --detail exited {rc}")
        elif not body:
            report.add(
                "register",
                HARD,
                f"{rid}: --detail renders a HEADING ONLY — the row has no prose body in "
                ".harness/post-phase-8-forward-register.md (a YAML-only row reads as empty)",
            )
        elif rid in new_ids and not _ACCEPTED_LEAD_RE.match(body[0]):
            report.add(
                "register",
                HARD,
                f"{rid}: NEW row LEADS with {body[0].strip()[:80]!r} — a new row must open "
                "with `**What it is.**`, `**What it was.**` or `**Current state.**`, never "
                "with an instruction. `any()` was not enough: a row whose FIRST bullet is a "
                "superseded directive and whose LATER bullet says Current state is exactly "
                "the stale-lead defect this check exists to prevent (codex round 2 [P2]).",
            )
        elif rid in new_ids and not any(_CURRENT_STATE_RE.match(ln) for ln in body):
            report.add(
                "register",
                HARD,
                f"{rid}: NEW row has no `- **Current state.**` bullet — a new row must "
                "say what is true NOW, not only what it is about (the superseded-lead "
                "defect). Enforced for NEW rows only: just 35 of 165 existing rows carry "
                "the bullet, so requiring it corpus-wide would red 130 legitimate legacy "
                "rows and get this gate muted.",
            )
        else:
            report.add(
                "register",
                ADVISORY,
                f"{rid}: leads with — {body[0].strip()[:160]} "
                "(READ IT: does it state the CURRENT state, or a superseded instruction?)",
            )


# --- driver ------------------------------------------------------------------


def untracked_added(uncommitted: bool) -> dict[str, list[str]]:
    """Brand-new, not-yet-added files, as all-added lines.

    `git diff HEAD` omits untracked files entirely, so a leg that CREATES an
    artifact and runs the mode advertised for pre-commit use saw zero changed
    files and skipped every check (codex round 4 [P2]). A new artifact is
    exactly where a fresh stale cite or a fresh minted label lives.
    """
    if not uncommitted:
        return {}
    out: dict[str, list[str]] = {}
    listing = _run_checked(["git", "ls-files", "--others", "--exclude-standard"])
    for rel in listing.splitlines():
        rel = rel.strip()
        if not rel:
            continue
        full = ROOT / rel
        if not full.is_file():
            continue
        try:
            out[rel] = full.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:  # pragma: no cover
            continue
    return out


def register_ids_at(ref: str) -> set[str]:
    """Row ids present in the register at the BASE ref — the preimage against
    which "new" is judged."""
    out: set[str] = set()
    for rel in (".harness/post-phase-8-forward-register.md", ".harness/forward-register.yaml"):
        try:
            blob = _run_checked(["git", "show", f"{ref}:{rel}"])
        except BaseRefError:
            continue
        for line in blob.splitlines():
            m = _ROW_ID_RE.match(line)
            if m:
                out.add(m.group(1))
    return out


def run(base: str, uncommitted: bool) -> Report:
    diff = diff_text(base, uncommitted)
    by_file = added_by_file(diff)
    for rel, lines in untracked_added(uncommitted).items():
        by_file.setdefault(rel, []).extend(lines)
    added = added_lines(by_file)
    paths = sorted(by_file)
    report = Report()
    report.stats["base"] = base
    report.stats["changed_files"] = len(paths)
    report.stats["added_lines"] = len(added)
    check_cites(by_file, report, None if uncommitted else "HEAD", deleted_paths(diff))
    ctx_pos = context_with_positions(diff)
    all_pos = {
        path: added_with_positions(diff).get(path, []) + ctx_pos.get(path, [])
        for path in set(added_with_positions(diff)) | set(ctx_pos)
    }
    check_counts(by_file, report, context_by_file(diff), all_pos)
    check_label_collisions(by_file, report)
    _DELETED_ROW_IDS.clear()
    amended: set[str] = set()
    for path, nums in changed_line_numbers(diff).items():
        if path.endswith(("forward-register.yaml", "post-phase-8-forward-register.md")):
            amended |= rows_enclosing(path, nums)
    amended |= set(_DELETED_ROW_IDS)
    check_register_rows(
        added,
        paths,
        report,
        amended=amended,
        register_added=by_file,
        base_ids=register_ids_at(base),
        uncommitted=uncommitted,
    )
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Per-round mechanical self-check for an arc.")
    ap.add_argument("--base", default=None, help="base ref (default: origin/main, else main)")
    ap.add_argument(
        "--uncommitted",
        action="store_true",
        help="also fold the working tree into the diff (run it BEFORE committing)",
    )
    ap.add_argument("--json", action="store_true", help="machine-readable findings")
    args = ap.parse_args(argv)

    try:
        report = run(resolve_base(args.base), args.uncommitted)
    except BaseRefError as e:
        print(f"leg-selfcheck: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "stats": report.stats,
                    "findings": [f.__dict__ for f in report.findings],
                    "hard": len(report.hard),
                },
                indent=2,
            )
        )
        return 1 if report.hard else 0

    print(
        f"leg-selfcheck vs {report.stats['base']}: "
        f"{report.stats['changed_files']} file(s), {report.stats['added_lines']} added line(s), "
        f"{report.stats.get('cites_resolved', 0)} cite(s) resolved, "
        f"{report.stats.get('labels_minted', 0)} label(s) minted, "
        f"{report.stats.get('register_rows_touched', 0)} register row(s) touched"
    )
    for f in report.findings:
        print(f.render())
    if report.hard:
        print(f"LEG SELFCHECK FAILED: {len(report.hard)} hard finding(s)", file=sys.stderr)
        return 1
    print("leg-selfcheck OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
