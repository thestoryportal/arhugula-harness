"""E2b — assemble one reviewer prompt: template + structural pack + PR diff (handoff-s2 §2 D).

The E2 template names the repository the reviewer may read. E2 pointed every reviewer at
the live checkout (README "Known defects" item 3); here the path is the worktree checked
out at the reviewed PR's head, so callers and tests come from the reviewed commit
([LAW:one-source-of-truth]: the tree the pack was computed from is the tree the reviewer
reads).

usage: e2b_assemble.py <template> <diff-file> <pack-file|none> <worktree-path> > prompt.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

E2_REPO_PATH = "/Users/robertrhu/Projects/arhugula-v2"  # the literal the E2 template carries
NO_PACK = "(no structural context provided)"


def assemble(template: str, diff: str, pack: str | None, worktree: str) -> str:
    for token in ("{{PACK}}", "{{DIFF}}", E2_REPO_PATH):
        if token not in template:  # [LAW:no-silent-failure] a drifted template is a loud exit
            raise SystemExit(f"e2b_assemble: template lacks {token!r}")
    return (
        template.replace(E2_REPO_PATH, worktree)
        .replace("{{PACK}}", pack if pack is not None else NO_PACK)
        .replace("{{DIFF}}", diff)
    )


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        return 2
    template, diff_file, pack_file, worktree = sys.argv[1:]
    pack = None if pack_file == "none" else Path(pack_file).read_text()
    sys.stdout.write(
        assemble(Path(template).read_text(), Path(diff_file).read_text(), pack, worktree)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
