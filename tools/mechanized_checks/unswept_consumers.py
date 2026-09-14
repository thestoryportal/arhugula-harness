"""unswept consumers (C-HE-31 §1, deterministic): a `def`/`class`/shell function this change
removed that is now defined nowhere in the tree, yet is still referenced. An edited signature
(removed and re-added) or a moved definition (still defined elsewhere) is not a removal."""

from __future__ import annotations

import re
from pathlib import Path

from .core import MechFinding, Subject, line_of

DEF_EDGE = re.compile(
    r"^(?P<sign>[-+])[ \t]*"
    r"(?:(?:async[ \t]+)?(?:def|class)[ \t]+(?P<py>\w+)|(?P<sh>\w+)[ \t]*\(\)[ \t]*\{)",
    re.M,
)
DEFINITION = re.compile(
    r"^[ \t]*(?:(?:async[ \t]+)?(?:def|class)[ \t]+(\w+)|(\w+)[ \t]*\(\)[ \t]*\{)", re.M
)
CODE_SUFFIXES = (".py", ".sh", ".js", ".ts", ".toml", ".yml", ".yaml")


class Check:
    check_id = "unswept_consumers"
    kind = "deterministic"

    def run(self, subject: Subject) -> list[MechFinding]:
        edges = [(m["sign"], m["py"] or m["sh"]) for m in DEF_EDGE.finditer(subject.diff)]
        code = [
            (rel, text)
            for rel in subject.universe
            if rel.endswith(CODE_SUFFIXES) or Path(rel).name == "justfile"
            for text in [subject.read(rel)]
            if text is not None
        ]
        defined = {py or sh for _rel, text in code for py, sh in DEFINITION.findall(text)}
        readded = {name for sign, name in edges if sign == "+"}
        return [
            MechFinding(
                f"{rel}:{line_of(text, m.start())}",
                f"reference to {name!r}, which this change removed and nothing defines",
                "every consumer of a removed symbol is swept (graft callers <sym> --depth all)",
            )
            for name in sorted({name for sign, name in edges if sign == "-"})
            if name not in readded
            if name not in defined
            for rel, text in code
            for m in re.finditer(rf"\b{re.escape(name)}\b", text)
        ]
