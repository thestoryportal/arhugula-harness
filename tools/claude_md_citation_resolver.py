#!/usr/bin/env python3
"""U-CTX-14 (R-CTX-1 Arc 5) — the tracked-corpus `CLAUDE.md` §-citation resolver.

Root `CLAUDE.md` is about to be slimmed into governance packs (U-CTX-13). Invariant
I-1 (`CLAUDE.md` §8) requires canonical citations to resolve, so the slimming is only
safe while the root heading set stays a SUPERSET of every tracked `CLAUDE.md §N[.M]`
citation. This module is that gate: it inventories the citation corpus across all
tracked files, attributes each citation to the `CLAUDE.md` file it actually names,
and fails when a cited section does not exist in that file's heading set.

Counts are DERIVED AT EXECUTION, never pinned (plan errata E3): the corpus grows as
program docs land, so the tool PRINTS a per-directory census and no test asserts a
total. The gate is the resolution invariant, not the census.

Supported citation shapes (all grounded empirically against the tracked corpus):

  1. bare               `CLAUDE.md §4.3`
  2. backticked         `` `CLAUDE.md` §4.3 ``  (dominant shape)
  3. relative root      `./CLAUDE.md §3.3`
  4. axis-path-prefixed `harness-cp/CLAUDE.md §4.1`  -> the AXIS file, not root
  5. brace-expanded     `harness-{is,as,cp,od}/CLAUDE.md §4.1`  -> all four axis files
  6. glob               `harness-*/CLAUDE.md §4.1`  -> every matching axis file
  7. word form          `CLAUDE.md section 4.5`  (used where `§` is YAML-hostile)
  8. chained            `CLAUDE.md §2.3 + §2.4`, `§13.1/§13.2`, `§1.3, §4.2`

Deliberately NOT resolved (reported, never silently dropped):

  * EXTERNAL          — a `~`-rooted path (`~/.claude/CLAUDE.md §10`) names the
                        operator's private global file, which is outside this repo.
  * UNRESOLVABLE      — a `<dir>/CLAUDE.md` whose `<dir>` has no tracked `CLAUDE.md`
                        (e.g. the prose compound `Sibling-spec/CLAUDE.md`). Attributing
                        these to root would manufacture false failures; they are listed
                        with file:line in the report instead.

Reverse-order prose (`§7.4.2 (`CLAUDE.md` invariant I-1)`) is EXCLUDED by design:
the section token there belongs to the artifact named BEFORE it (`Project_Workflow_v1_8.md`
in the live instance), so a reverse matcher misattributes to root. Verified by direct read.

Usage:
    uv run python tools/claude_md_citation_resolver.py            # census + report
    uv run python tools/claude_md_citation_resolver.py --check    # non-zero on findings
    uv run python tools/claude_md_citation_resolver.py --json
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# This module is itself tracked, so the resolver scans its own docstring. Every shape
# example above cites a section that really exists — the docstring is a live fixture,
# not an exemption. Keep it that way when editing.
SECTION_SIGN = "§"

_SECTION = r"\d+(?:\.\d+)*"
# Path-ish run immediately preceding the filename. Backticks/quotes are excluded so
# `` `CLAUDE.md` `` yields an empty prefix (= root).
_PREFIX_CHARS = r"[~./A-Za-z0-9_*{},-]*"
# Empirical gap census over the tracked corpus: every real gap is <= 14 chars and is
# punctuation/whitespace/short connective. Digits and section signs are excluded so a
# gap can never swallow another citation.
_GAP = rf"[^0-9\n{SECTION_SIGN}]{{0,14}}?"

CITATION_RE = re.compile(
    rf"(?P<prefix>{_PREFIX_CHARS})CLAUDE\.md"
    rf"(?P<gap>{_GAP})"
    rf"(?:{SECTION_SIGN}\s?|[Ss]ection\s+|[Ss]ec\.\s*)"
    rf"(?P<section>{_SECTION})"
)

# A trailing sibling section joined by a short connective inherits the same target:
# `§2.3 + §2.4`, `§13.1/§13.2`, `§1.3, §4.2`. The connective is capped so ordinary
# prose between two different artifacts' cites can never chain.
# NB: no `\A` — it would anchor at string position 0 and defeat `match(line, cursor)`.
CHAIN_RE = re.compile(rf"[ ]*(?:[+,/&]|and)[ ]*{SECTION_SIGN}(?P<section>{_SECTION})")

# `## 1. Project framing` / `### 1.1 What this workspace builds` / `#### 12.2.1 ...`.
HEADING_RE = re.compile(rf"^#{{2,4}} +(?P<section>{_SECTION})\.? +\S")

# Root `CLAUDE.md` §14 declares its subsections as BOLD FIRST-CELL TABLE LABELS, not as
# `###` headings (`| **14.2 AskUserQuestion, never ...** | ... |`, CLAUDE.md:733-739 read
# directly). Those are cited as §14.N across the corpus and are real anchors, so the
# declared-section set is headings UNION bold first-cell table labels. The pattern is
# deliberately tight — row start, bold open, digits, space, text — so ordinary emphasis
# inside a cell cannot masquerade as a section anchor.
TABLE_ANCHOR_RE = re.compile(rf"^\| *\*\*(?P<section>{_SECTION}) +\S")

# A gap containing a filename means a DIFFERENT artifact intervenes between the
# `CLAUDE.md` anchor and the section token; the token is not a CLAUDE.md cite.
_GAP_DISQUALIFIER = ".md"

# Parentheticals are asides ("`CLAUDE.md` (workspace) §11.4"); their words do not make
# the gap a clause. An unclosed `(` is treated the same way.
_PARENTHETICAL_RE = re.compile(r"\([^)]*\)?")
_WORD_RE = re.compile(r"[A-Za-z]+")

ROOT_TARGET = "CLAUDE.md"


class Attribution(Enum):
    """How a citation's `<prefix>CLAUDE.md` anchor was resolved."""

    RESOLVED = "resolved"
    EXTERNAL = "external"
    UNRESOLVABLE = "unresolvable_target"


@dataclass(frozen=True)
class Citation:
    source: str
    line: int
    raw_prefix: str
    section: str
    attribution: Attribution
    targets: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    source: str
    line: int
    target: str
    section: str

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.source, self.target, self.section)

    def render(self) -> str:
        return (
            f"{self.source}:{self.line}: {self.target} has no section {SECTION_SIGN}{self.section}"
        )


@dataclass(frozen=True)
class KnownBroken:
    """A citation that is genuinely broken at HEAD and is NOT this arc's to repair."""

    source: str
    target: str
    section: str
    rationale: str

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.source, self.target, self.section)


# The gate is green at HEAD, so the pre-existing breakage is enumerated here rather than
# hidden. Every entry was classified by direct read; none is a matcher shape-mismatch.
# Keyed on (file, target, section) — NOT line — so unrelated edits to these files cannot
# stale the baseline. A waiver whose citation stops being broken FAILS the gate, so the
# list cannot rot: fix the cite upstream and the gate tells you to delete the row.
KNOWN_BROKEN: tuple[KnownBroken, ...] = (
    KnownBroken(
        source=".claude/skills/ship-pr/SKILL.md",
        target="CLAUDE.md",
        section="15",
        rationale=(
            "Root CLAUDE.md ends at section 14; the skill cites a section that never "
            "existed. Repair belongs to the skill owner — .claude/skills/ is outside "
            "this unit's edit surface."
        ),
    ),
    KnownBroken(
        source=".harness/class_3_tension_cxa_v2_4_axis_back_edge.md",
        target="CLAUDE.md",
        section="2.1.4",
        rationale=(
            "Historical Class-3 fork record from the CXA v2.4 era, when root section 2.1 "
            "carried a numbered sub-row. Rewriting a filed fork doc would falsify the "
            "record it exists to preserve."
        ),
    ),
    KnownBroken(
        source=".harness/phase-7d-retirement-events-batch-6.md",
        target="CLAUDE.md",
        section="2.1.4",
        rationale=(
            "Same vanished anchor, carried in a filed Phase-7d retirement-event record. "
            "Retirement events are append-only history, not live pointers."
        ),
    ),
)


@dataclass(frozen=True)
class CitationReport:
    citations: tuple[Citation, ...]
    findings: tuple[Finding, ...]
    waived: tuple[Finding, ...]
    stale_waivers: tuple[KnownBroken, ...]
    heading_sets: dict[str, tuple[str, ...]]
    scanned_files: int
    skipped_binary: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.findings and not self.stale_waivers

    def census_by_directory(self) -> dict[str, int]:
        counts: Counter[str] = Counter()
        for citation in self.citations:
            head, _, tail = citation.source.partition("/")
            counts[head if tail else "<root-files>"] += 1
        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))

    def census_by_target(self) -> dict[str, int]:
        counts: Counter[str] = Counter()
        for citation in self.citations:
            for target in citation.targets:
                counts[target] += 1
        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))

    def census_by_attribution(self) -> dict[str, int]:
        counts: Counter[str] = Counter(citation.attribution.value for citation in self.citations)
        return dict(sorted(counts.items()))


def tracked_files(root: Path) -> tuple[Path, ...]:
    """Every file git tracks, as repo-relative paths. Fails loudly if git refuses."""
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    names = completed.stdout.decode("utf-8").split("\0")
    return tuple(Path(name) for name in names if name)


def heading_sections(text: str) -> tuple[str, ...]:
    """Section ids a CLAUDE.md declares: `##`/`###`/`####` headings + bold table labels."""
    declared: list[str] = []
    for line in text.splitlines():
        for pattern in (HEADING_RE, TABLE_ANCHOR_RE):
            if (match := pattern.match(line)) is not None:
                declared.append(match.group("section"))
                break
    return tuple(declared)


def gap_is_appositive(gap: str) -> bool:
    """True when the gap reads as an appositive rather than a clause.

    Empirically, a real citation's gap is punctuation/markdown decoration plus at most
    ONE modifier word (`` `CLAUDE.md` framing (§1 ``, `CLAUDE.md root §1.1`,
    `CLAUDE.md NEW §12.4.1`). Two or more words outside parentheses form a clause whose
    section object belongs to a DIFFERENT artifact — the two live false positives are
    `` `harness-cp/CLAUDE.md` | No direct §7.4.7 cite `` (a Project_Workflow section, in
    the NEXT table cell) and `at harness-od/CLAUDE.md to require §9.1` (an OD-spec
    section). Both verified by direct read.
    """
    outside = _PARENTHETICAL_RE.sub(" ", gap)
    return len(_WORD_RE.findall(outside)) <= 1


def build_heading_sets(root: Path, targets: tuple[Path, ...]) -> dict[str, tuple[str, ...]]:
    """Parse every CLAUDE.md target. Fail-closed: a target with no §-headings is malformed."""
    sets: dict[str, tuple[str, ...]] = {}
    for target in targets:
        sections = heading_sections((root / target).read_text(encoding="utf-8"))
        if not sections:
            raise ValueError(
                f"{target.as_posix()}: no {SECTION_SIGN}-numbered section anchors parsed "
                "— refusing to gate against an empty heading set"
            )
        sets[target.as_posix()] = sections
    return sets


def _expand_prefix(directory: str, target_dirs: tuple[str, ...]) -> tuple[str, ...]:
    """Expand `harness-{is,as}` / `harness-*` against the directories that own a CLAUDE.md."""
    brace = re.search(r"\{([^}]*)\}", directory)
    if brace is not None:
        return tuple(
            expanded
            for alternative in brace.group(1).split(",")
            for expanded in _expand_prefix(
                directory[: brace.start()] + alternative.strip() + directory[brace.end() :],
                target_dirs,
            )
        )
    if "*" in directory or "?" in directory:
        return tuple(name for name in target_dirs if fnmatch.fnmatchcase(name, directory))
    return (directory,)


def resolve_prefix(
    prefix: str, target_dirs: tuple[str, ...]
) -> tuple[Attribution, tuple[str, ...]]:
    """Map a citation's path prefix onto the CLAUDE.md file(s) it names."""
    if "~" in prefix:
        return Attribution.EXTERNAL, ()
    normalised = prefix[2:] if prefix.startswith("./") else prefix
    if "/" not in normalised:
        # Bare, backticked, or English-compound (`root-CLAUDE.md`, `per-CLAUDE.md`):
        # no directory component means the workspace-root file.
        return Attribution.RESOLVED, (ROOT_TARGET,)
    directory = normalised.rstrip("/")
    resolved = tuple(
        f"{name}/{ROOT_TARGET}"
        for name in _expand_prefix(directory, target_dirs)
        if name in target_dirs
    )
    if not resolved:
        return Attribution.UNRESOLVABLE, ()
    return Attribution.RESOLVED, resolved


def iter_citations(source: str, text: str, target_dirs: tuple[str, ...]) -> Iterator[Citation]:
    """Yield every `CLAUDE.md` §-citation in one file, chained siblings included."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in CITATION_RE.finditer(line):
            gap = match.group("gap")
            if _GAP_DISQUALIFIER in gap or not gap_is_appositive(gap):
                continue
            prefix = match.group("prefix")
            attribution, targets = resolve_prefix(prefix, target_dirs)
            sections = [match.group("section")]
            cursor = match.end()
            while (chained := CHAIN_RE.match(line, cursor)) is not None:
                sections.append(chained.group("section"))
                cursor = chained.end()
            for section in sections:
                yield Citation(
                    source=source,
                    line=lineno,
                    raw_prefix=prefix,
                    section=section,
                    attribution=attribution,
                    targets=targets,
                )


def scan(root: Path = ROOT, known_broken: tuple[KnownBroken, ...] = KNOWN_BROKEN) -> CitationReport:
    files = tracked_files(root)
    targets = tuple(path for path in files if path.name == ROOT_TARGET)
    if not any(path.as_posix() == ROOT_TARGET for path in targets):
        raise ValueError(f"{root}: no tracked root {ROOT_TARGET} — refusing to gate")
    heading_sets = build_heading_sets(root, targets)
    target_dirs = tuple(
        path.parent.as_posix() for path in targets if path.as_posix() != ROOT_TARGET
    )

    waiver_index = {entry.key: entry for entry in known_broken}
    citations: list[Citation] = []
    findings: list[Finding] = []
    waived: list[Finding] = []
    skipped: list[str] = []
    scanned = 0
    for path in files:
        try:
            text = (root / path).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            # Binary blobs and symlinks-to-nowhere carry no citations; recorded, not swallowed.
            skipped.append(path.as_posix())
            continue
        scanned += 1
        if ROOT_TARGET not in text:
            continue
        for citation in iter_citations(path.as_posix(), text, target_dirs):
            citations.append(citation)
            for target in citation.targets:
                if citation.section in heading_sets[target]:
                    continue
                finding = Finding(
                    source=citation.source,
                    line=citation.line,
                    target=target,
                    section=citation.section,
                )
                (waived if finding.key in waiver_index else findings).append(finding)

    observed = {finding.key for finding in waived}
    stale = tuple(entry for entry in known_broken if entry.key not in observed)
    return CitationReport(
        citations=tuple(citations),
        findings=tuple(findings),
        waived=tuple(waived),
        stale_waivers=stale,
        heading_sets=heading_sets,
        scanned_files=scanned,
        skipped_binary=tuple(skipped),
    )


def render(report: CitationReport) -> str:
    lines: list[str] = []
    lines.append(
        f"scanned {report.scanned_files} tracked text files "
        f"({len(report.skipped_binary)} binary/unreadable skipped)"
    )
    lines.append("")
    lines.append("heading sets (root superset the slimming must preserve):")
    for target, sections in sorted(report.heading_sets.items()):
        lines.append(f"  {target}: {len(sections)} sections")
    lines.append("")
    lines.append("citation census by citing directory (derived at execution — never pinned):")
    for directory, count in report.census_by_directory().items():
        lines.append(f"  {directory}: {count}")
    lines.append(f"  TOTAL: {len(report.citations)}")
    lines.append("")
    lines.append("citation census by attribution:")
    for kind, count in report.census_by_attribution().items():
        lines.append(f"  {kind}: {count}")
    lines.append("")
    lines.append("resolved citations by target file:")
    for target, count in report.census_by_target().items():
        lines.append(f"  {target}: {count}")

    unresolved = [c for c in report.citations if c.attribution is not Attribution.RESOLVED]
    if unresolved:
        lines.append("")
        lines.append("not resolved (reported, not gated — see module docstring):")
        for citation in unresolved:
            lines.append(
                f"  {citation.source}:{citation.line}: [{citation.attribution.value}] "
                f"{citation.raw_prefix}{ROOT_TARGET} {SECTION_SIGN}{citation.section}"
            )

    if report.waived:
        lines.append("")
        lines.append(
            f"known-broken baseline ({len(report.waived)} citations, pre-existing, "
            "enumerated at KNOWN_BROKEN):"
        )
        for finding in report.waived:
            lines.append(f"  {finding.render()}")

    lines.append("")
    if report.stale_waivers:
        lines.append(f"STALE BASELINE ENTRIES: {len(report.stale_waivers)}")
        for entry in report.stale_waivers:
            lines.append(
                f"  {entry.source}: {entry.target} {SECTION_SIGN}{entry.section} no longer "
                "broken — delete this KNOWN_BROKEN row"
            )
    if report.findings:
        lines.append(f"BROKEN CITATIONS: {len(report.findings)}")
        for finding in report.findings:
            lines.append(f"  {finding.render()}")
    elif not report.stale_waivers:
        lines.append("BROKEN CITATIONS: 0 — every cited section resolves")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve tracked CLAUDE.md section citations.")
    parser.add_argument("--check", action="store_true", help="exit non-zero on broken citations")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to scan")
    args = parser.parse_args(argv)

    # KNOWN_BROKEN's keys are repo-relative paths in THIS repository, so they are
    # meaningless (and would register as stale) against any other root.
    baseline = KNOWN_BROKEN if args.root.resolve() == ROOT else ()
    report = scan(args.root, known_broken=baseline)

    if args.json:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "scanned_files": report.scanned_files,
                    "total_citations": len(report.citations),
                    "census_by_directory": report.census_by_directory(),
                    "census_by_attribution": report.census_by_attribution(),
                    "census_by_target": report.census_by_target(),
                    "heading_counts": {k: len(v) for k, v in report.heading_sets.items()},
                    "findings": [
                        {
                            "source": f.source,
                            "line": f.line,
                            "target": f.target,
                            "section": f.section,
                        }
                        for f in report.findings
                    ],
                    "waived": [
                        {
                            "source": f.source,
                            "line": f.line,
                            "target": f.target,
                            "section": f.section,
                        }
                        for f in report.waived
                    ],
                    "stale_waivers": [e.key for e in report.stale_waivers],
                },
                indent=2,
            )
        )
    else:
        print(render(report))

    if args.check and not report.ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
