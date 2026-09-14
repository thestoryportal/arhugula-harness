"""stale-carry text / counts (C-HE-31 §1, deterministic): a count that disagrees with the table
it introduces, and placeholder tokens left in shipped markdown."""

from __future__ import annotations

import re

from .core import MechFinding, Subject, line_of

PLACEHOLDER = re.compile(r"(?<![\w<])(TBD|XXX|TODO\(spec\)|<NNN>|<N>|vX\.Y)(?![\w>])")
NUMBER_WORDS = {
    word: n
    for n, word in enumerate(
        "zero one two three four five six seven eight nine ten eleven twelve".split()
    )
}
COUNT_TABLE = re.compile(
    rf"\b(?P<count>\d+|{'|'.join(NUMBER_WORDS)})\s+(?P<noun>contracts|rows|units|files|tests|stores)"
    r"\s*:?[ \t]*\n(?P<table>(?:[ \t]*\|[^\n]*(?:\n|$))+)",
    re.I,
)
SEPARATOR = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def _claimed(count: str) -> int:
    return int(count) if count.isdigit() else NUMBER_WORDS[count.lower()]


def _data_rows(table: str) -> int:
    """A separator on the second line is what makes the first a header; neither is data."""
    lines = table.splitlines()
    has_header = len(lines) > 1 and SEPARATOR.match(lines[1]) is not None
    return len(lines) - 2 * has_header


class Check:
    check_id = "stale_carry"
    kind = "deterministic"

    def run(self, subject: Subject) -> list[MechFinding]:
        texts = subject.changed_texts(".md")
        counts = [
            MechFinding(
                f"{rel}:{line_of(text, m.start())}",
                f"claims {_claimed(m['count'])} {m['noun']} but the table has "
                f"{_data_rows(m['table'])} data rows",
                "a count claim matches the table it introduces",
            )
            for rel, text in texts
            for m in COUNT_TABLE.finditer(text)
            if _claimed(m["count"]) != _data_rows(m["table"])
        ]
        placeholders = [
            MechFinding(
                f"{rel}:{line_of(text, m.start())}",
                f"placeholder token {m.group(1)!r}",
                "no placeholder tokens in shipped text",
            )
            for rel, text in texts
            for m in PLACEHOLDER.finditer(text)
        ]
        return counts + placeholders
