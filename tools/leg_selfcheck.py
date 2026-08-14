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

_CITE_RE = re.compile(
    r"(?<![\w/])((?:[\w.\-]+/)*[\w.\-]+\.(?:py|md|sh|toml|ya?ml|json)):(\d+)(?:\s*[-–]\s*(\d+))?"
)


def check_cites(by_file: dict[str, list[str]], report: Report) -> None:
    """Re-resolve every `path:NNN` the arc ADDED, at the CURRENT HEAD.

    This is the check that would have caught the `:1543`/`:2238` fold sites and
    the `_pre_dispatch_gate_owning_branch_identity` guard cites: a line number
    written from an earlier read drifts the moment the file is edited, and a
    review round is a very expensive way to discover that.
    """
    seen: set[tuple[str, int, int | None]] = set()
    checked = 0
    scanned = [
        line for path, lines in by_file.items() if not is_fixture_path(path) for line in lines
    ]
    for line in scanned:
        for m in _CITE_RE.finditer(line):
            rel, start_s, end_s = m.group(1), m.group(2), m.group(3)
            start = int(start_s)
            end = int(end_s) if end_s else None
            key = (rel, start, end)
            if key in seen:
                continue
            seen.add(key)
            path = ROOT / rel
            if not path.is_file():
                # Not every `word.md:12` is a repo cite (URLs, prose, other repos).
                # Only a path that RESOLVES is a claim this tool can judge; an
                # unresolvable one is reported advisory, never as a hard failure.
                report.add(
                    "cite",
                    ADVISORY,
                    f"{rel}:{start} — path does not resolve under the repo root "
                    "(not a repo cite, or the file moved)",
                )
                continue
            checked += 1
            try:
                total = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
            except OSError as e:  # pragma: no cover - unreadable file
                report.add("cite", ADVISORY, f"{rel}: unreadable ({e})")
                continue
            worst = max(start, end or start)
            if worst > total:
                report.add(
                    "cite",
                    HARD,
                    f"{rel}:{m.group(0).split(':', 1)[1]} — file has only {total} lines "
                    "at HEAD (stale cite)",
                )
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


def _claim_subject(line: str, path: str, at: int = 0) -> str:
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
    return best or f"(unattributed in {path})"


def check_counts(
    by_file: dict[str, list[str]],
    report: Report,
    context: dict[str, list[str]] | None = None,
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

    scanned = [(p, line) for p, lines in by_file.items() if _eligible(p) for line in lines]
    # Unchanged text immediately around the edits, so a single edited mirror can
    # still disagree with an untouched co-located one (codex round 1 [P1]).
    scanned += [(p, line) for p, lines in (context or {}).items() if _eligible(p) for line in lines]
    for path, line in scanned:
        low = line.lower()
        for pattern, bucket in _COUNT_NOUNS:
            for m in re.finditer(rf"{_NUM}\s+(?:\w+[- ]){{0,2}}?{pattern}", low, re.IGNORECASE):
                raw = m.group(1).lower()
                value = int(raw) if raw.isdigit() else _NUMBER_WORDS[raw]
                subject = _claim_subject(line, path, m.start())
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
    minted = sorted(
        {
            m.group(1)
            for path, lines in by_file.items()
            if path.lower().endswith(".md") and not is_fixture_path(path)
            for line in lines
            if (m := _MINT_RE.match(line))
        }
    )
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
    minted_families = {_artifact_family(path) for path in by_file if path.lower().endswith(".md")}
    for label in minted:
        siblings = sorted(
            f.name
            for f in family_dir.glob("*.md")
            if _artifact_family(f.name) in minted_families
            and any(
                (m := _HEADING_USE_RE.match(line)) and m.group(1) == label
                for line in f.read_text(encoding="utf-8", errors="replace").splitlines()
            )
        )
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
    new_ids = {
        m.group(1)
        for path, lines in (register_added or {}).items()
        if path.endswith("post-phase-8-forward-register.md")
        for line in lines
        if (m := _NEW_PROSE_HEADING_RE.match(line))
    }
    report.stats["register_rows_touched"] = len(ids)
    report.stats["register_rows_new"] = len(new_ids)
    detail = detail_fn or _detail_via_cli
    for rid in ids:
        rc, stdout = detail(rid)
        body = [ln for ln in stdout.splitlines() if ln.strip() and not ln.startswith("###")]
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
    check_cites(by_file, report)
    check_counts(by_file, report, context_by_file(diff))
    check_label_collisions(by_file, report)
    amended: set[str] = set()
    for path, nums in changed_line_numbers(diff).items():
        if path.endswith(("forward-register.yaml", "post-phase-8-forward-register.md")):
            amended |= rows_enclosing(path, nums)
    check_register_rows(added, paths, report, amended=amended, register_added=by_file)
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
