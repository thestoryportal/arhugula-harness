#!/usr/bin/env python3
"""Session-start posture reminder for Codex."""

from __future__ import annotations

from pathlib import Path


def exists(path: str) -> str:
    return "present" if Path(path).exists() else "missing"


print("Codex project posture for arhugula-v2:")
print("- Read AGENTS.md first; consult CLAUDE.md only for targeted canonical lineage.")
print(f"- Roadmap status: .harness/roadmap_status.md is {exists('.harness/roadmap_status.md')}.")
print(f"- justfile is {exists('justfile')}; prefer just recipes for repo gates.")
print("- Use isolated worktrees for substantive edits and keep PRs reviewable.")
print("- Do not mix design-substrate edits with implementation without explicit back-flow scope.")
