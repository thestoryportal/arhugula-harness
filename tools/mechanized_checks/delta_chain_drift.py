"""delta-chain version drift (C-HE-31 §1, deterministic): a `` `<Stem>_v<M>_<m>.md` §<sec> ``
cite whose section a LATER version of the same chain re-tables. The workspace convention
(CLAUDE.md §2) is to cite the version of last substantive definition, so a later heading for
the same section means the cite is stale."""

from __future__ import annotations

import re

from .core import MechFinding, Subject, line_of

CITE = re.compile(
    r"`(?P<stem>[A-Za-z]\w*?)_v(?P<major>\d+)_(?P<minor>\d+)\.md`\s*§\s*(?P<sec>\d+(?:\.\d+)*)"
)


def _retabling(subject: Subject, cite: re.Match[str]) -> list[str]:
    """Later versions of the cited chain, oldest first, that carry a heading for the section
    (a subsection heading such as `7.4.2.1` does not re-table `7.4.2`)."""
    version = re.compile(rf"(?:^|/){re.escape(cite['stem'])}_v{cite['major']}_(\d+)\.md$")
    heading = re.compile(rf"^#+[ \t]*§?[ \t]*{re.escape(cite['sec'])}(?![.\d])", re.M)
    later = sorted(
        (int(v[1]), rel)
        for rel in subject.universe
        for v in version.finditer(rel)
        if int(v[1]) > int(cite["minor"])
    )
    return [rel for _n, rel in later if heading.search(subject.read(rel) or "")]


class Check:
    check_id = "delta_chain_drift"
    kind = "deterministic"
    replayable = True

    def run(self, subject: Subject) -> list[MechFinding]:
        return [
            MechFinding(
                f"{rel}:{line_of(text, m.start())}",
                f"§{m['sec']} is re-tabled in {later}; cite the version of last substantive "
                "definition",
                "a delta-chain § cite names the version of last substantive definition",
            )
            for rel, text in subject.changed_texts(".md")
            for m in CITE.finditer(text)
            for later in _retabling(subject, m)
        ]
