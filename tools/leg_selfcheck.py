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


def _run(args: list[str]) -> str:
    out = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return out.stdout


def resolve_base(explicit: str | None) -> str:
    if explicit:
        return explicit
    for cand in ("origin/main", "main"):
        if _run(["git", "rev-parse", "--verify", "--quiet", cand]).strip():
            return cand
    return "HEAD~1"


def diff_text(base: str, uncommitted: bool) -> str:
    """The arc's own added lines. `--uncommitted` also folds in the working tree,
    so the check is runnable BEFORE the commit that would otherwise hide a defect
    until the next review round."""
    parts = [_run(["git", "diff", f"{base}...HEAD"])]
    if uncommitted:
        parts.append(_run(["git", "diff", "HEAD"]))
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


def added_lines(by_file: dict[str, list[str]]) -> list[str]:
    return [ln for lines in by_file.values() for ln in lines]


#: Historical carriers. Lines APPENDED to these are relocated history, not
#: claims this arc is making, so count-claim scanning must skip them.
_HISTORY_PATHS = ("archive", "-log", "_log")


def is_history_path(path: str) -> bool:
    name = Path(path).name.lower()
    return any(tok in name for tok in _HISTORY_PATHS)


# --- check 1: cite resolution ------------------------------------------------

_CITE_RE = re.compile(
    r"(?<![\w/])((?:[\w.\-]+/)*[\w.\-]+\.(?:py|md|sh|toml|ya?ml|json)):(\d+)(?:\s*[-–]\s*(\d+))?"
)


def check_cites(added: list[str], report: Report) -> None:
    """Re-resolve every `path:NNN` the arc ADDED, at the CURRENT HEAD.

    This is the check that would have caught the `:1543`/`:2238` fold sites and
    the `_pre_dispatch_gate_owning_branch_identity` guard cites: a line number
    written from an earlier read drifts the moment the file is edited, and a
    review round is a very expensive way to discover that.
    """
    seen: set[tuple[str, int, int | None]] = set()
    checked = 0
    for line in added:
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


def check_counts(by_file: dict[str, list[str]], report: Report) -> None:
    """Detect DISAGREEMENT between count claims, which is the actual defect.

    Deliberately NOT a recount against ground truth: "how many ACs does this
    unit really have" is unbounded to compute for every noun in every artifact.
    What IS bounded, and is exactly what went wrong five times on `B-71`, is
    that the SAME noun was claimed with DIFFERENT numbers across the spec
    preamble, the section body, the plan delta, the clearance marker and the
    register row. Two different answers to one question is a defect regardless
    of which is right — so that is what this reports.
    """
    claims: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    scanned = [
        line for path, lines in by_file.items() if not is_history_path(path) for line in lines
    ]
    for line in scanned:
        low = line.lower()
        for pattern, bucket in _COUNT_NOUNS:
            for m in re.finditer(rf"{_NUM}\s+(?:\w+[- ]){{0,2}}?{pattern}", low, re.IGNORECASE):
                raw = m.group(1).lower()
                value = int(raw) if raw.isdigit() else _NUMBER_WORDS[raw]
                claims[bucket][value].append(line.strip()[:150])

    for bucket, by_value in sorted(claims.items()):
        if len(by_value) > 1:
            values = ", ".join(str(v) for v in sorted(by_value))
            report.add(
                "count",
                HARD,
                f"{bucket!r} is claimed with {len(by_value)} DIFFERENT values ({values}) "
                "in this arc's added lines — mirrors disagree; recount programmatically "
                "and fix every carrier",
            )
            for value in sorted(by_value):
                for example in by_value[value][:2]:
                    report.add("count", ADVISORY, f"  {bucket}={value}: {example}")
    report.stats["count_nouns_seen"] = len(claims)


# --- check 3: § label collision ----------------------------------------------

#: A newly-MINTED label, not a cite: a markdown heading, or a bolded run-in
#: heading, that introduces `§X.Y`. A bare `§25.4` in prose is a reference and
#: is expected to already exist elsewhere — flagging those would make this
#: check pure noise.
_MINT_RE = re.compile(r"^\s*(?:#{1,6}\s+|\*\*)\s*§(\d+(?:\.\d+)+)")
_HEADING_USE_RE = re.compile(r"^\s*(?:#{1,6}\s+|\*\*)\s*§(\d+(?:\.\d+)+)")


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
            if path.lower().endswith(".md")
            for line in lines
            if (m := _MINT_RE.match(line))
        }
    )
    report.stats["labels_minted"] = len(minted)
    report.stats["labels"] = [f"§{label}" for label in minted]
    if not minted:
        return

    existing: dict[str, set[str]] = defaultdict(set)
    for path in sorted((substrate_dir or (ROOT / "design-substrate")).glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:  # pragma: no cover
            continue
        for line in text.splitlines():
            m = _HEADING_USE_RE.match(line)
            if m:
                existing[m.group(1)].add(path.name)

    for label in minted:
        owners = existing.get(label, set())
        # >1 owner means the label heads a section in more than one artifact of
        # the chain. Exactly 1 is the normal case (this arc's own file).
        if len(owners) > 1:
            report.add(
                "label",
                HARD,
                f"§{label} heads a section in {len(owners)} artifacts "
                f"({', '.join(sorted(owners))}) — a minted label must be free "
                "across the whole delta chain",
            )


# --- check 4: register row renders its current state -------------------------

_ROW_ID_RE = re.compile(r"^(?:- id:|### )\s*([BR]-[A-Z0-9]+(?:-[A-Z0-9]+)*)")


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
    ids = sorted({m.group(1) for line in added if (m := _ROW_ID_RE.match(line))})
    report.stats["register_rows_touched"] = len(ids)
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
        else:
            report.add(
                "register",
                ADVISORY,
                f"{rid}: leads with — {body[0].strip()[:160]} "
                "(READ IT: does it state the CURRENT state, or a superseded instruction?)",
            )


# --- driver ------------------------------------------------------------------


def run(base: str, uncommitted: bool) -> Report:
    by_file = added_by_file(diff_text(base, uncommitted))
    added = added_lines(by_file)
    paths = sorted(by_file)
    report = Report()
    report.stats["base"] = base
    report.stats["changed_files"] = len(paths)
    report.stats["added_lines"] = len(added)
    check_cites(added, report)
    check_counts(by_file, report)
    check_label_collisions(by_file, report)
    check_register_rows(added, paths, report)
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

    report = run(resolve_base(args.base), args.uncommitted)

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
