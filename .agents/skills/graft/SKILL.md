---
name: graft
description: Use when locating code, understanding a flow, tracing callers, or scoping a refactor in this repo — get context from the graft wiring graph before grepping or reading source files.
---

# Canonical Claude Workflow Bridge

Read `.claude/skills/graft/SKILL.md` completely from the workspace root before acting, including every reference it routes for the task. That canonical skill body is the full workflow; this Codex entrypoint does not summarize, trim, or replace it. Resolve its relative references from the canonical skill directory.

Apply these runner translations only:

- Root `AGENTS.md` is the Codex instruction entrypoint and already carries a marker-fenced Graft block; targeted `CLAUDE.md` sections remain canonical lineage.
- The `graft` CLI is runner-agnostic — every command in the canonical body works identically here. The MCP surface (`graft_find_code`, `graft_find_all`, `graft_trace_calls`, `graft_file_api`, `graft_repo_map`) is available only where a host exposes it; fall back to the CLI otherwise.
- Claude's graft hooks (`SessionStart`, `UserPromptSubmit`, `Stop`, `PostToolUse`) have **no Codex counterpart by explicit decision** — they inject retrieval context into Claude's own prompt and session lifecycle, and Codex exposes no equivalent injection point. See the Graft row in `.codex/notes/claude-codex-parity.md`. Practically: no context pack is injected for you, so **invoke graft explicitly** rather than waiting for a prompt-time nudge, and the per-turn token-savings tally the canonical body asks for is only available when a command prints its own savings line.
- `graft/` is a gitignored, per-checkout build artifact. A fresh worktree has no graph until `graft build` runs (`$0`, no key, seconds). Tools that read the artifact directly must fail loud rather than report an empty result — `tools/graft_reachability.py` is the worked example.
- Claude-only scratch paths translate to a safe `/tmp` or ignored workspace scratch path. All Git, CI, worktree, paid-call, secret, and destructive-action guardrails remain binding.
