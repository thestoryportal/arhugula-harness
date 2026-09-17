"""cited symbol does not exist (C-HE-31 §1, deterministic): in changed markdown, a
`` `path:line` `` cite must name a file with at least that many lines, and a `` `name()` ``
cited beside a `` `path` `` must be defined in that file. Only cites with a directory component
are repo-relative cites; a bare basename is not one."""

from __future__ import annotations

import re

from .core import MechFinding, Subject

_PATH = r"[\w.-]+(?:/[\w.-]+)+"
FILE_LINE = re.compile(
    rf"`(?P<path>{_PATH}\.(?:py|sh|md|yml|yaml|toml|json)):(?P<start>\d+)(?:-(?P<end>\d+))?`"
)
SYMBOL_IN = re.compile(rf"`(?P<name>\w+)\(\)`[^`\n]*`(?P<path>{_PATH}\.(?:py|sh))`")


def _resolves(text: str | None, start: int, end: int) -> bool:
    """A file:line cite resolves iff its WHOLE range lies in the file: 1 <= start <= end <=
    len. Checking only `end` passed `tools/x.py:999-1` against any one-line file, because a
    reversed range put the smaller number where the bound was read (codex r11 P2)."""
    return 1 <= start <= end <= len((text or "").splitlines())


def _defines(name: str) -> re.Pattern[str]:
    n = re.escape(name)
    return re.compile(
        rf"^[ \t]*(?:(?:async[ \t]+)?(?:def|class)[ \t]+{n}\b|{n}[ \t]*\(\)[ \t]*\{{)", re.M
    )


class Check:
    check_id = "cited_symbol_exists"
    kind = "deterministic"
    replayable = True

    def run(self, subject: Subject) -> list[MechFinding]:
        texts = subject.changed_texts(".md")
        lines = [
            MechFinding(
                m.group(0).strip("`"),
                "cited file:line does not resolve (file missing or shorter than the cite)",
                "every file:line cite resolves at HEAD",
            )
            for _rel, text in texts
            for m in FILE_LINE.finditer(text)
            if not _resolves(
                subject.read(m["path"]), int(m["start"]), int(m["end"] or m["start"])
            )
        ]
        symbols = [
            MechFinding(
                f"{m['name']}()",
                f"cited symbol is not defined in {m['path']}",
                "every cited symbol exists where it is cited",
            )
            for _rel, text in texts
            for m in SYMBOL_IN.finditer(text)
            if _defines(m["name"]).search(subject.read(m["path"]) or "") is None
        ]
        return lines + symbols
