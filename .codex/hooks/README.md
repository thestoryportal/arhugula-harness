# Codex Hooks

These hooks are a Codex-native compatibility layer for the Claude hooks in `.claude/settings.json`.

Every Claude hook behavior supported by Codex's lifecycle is wired here. The Codex-native guards remain additive:

- `session_start.py` prints the minimum project posture Codex should remember at startup.
- `pre_tool_use_policy.py` blocks only high-confidence boundary violations, especially X-AL-3 design/implementation mixing in a single command.
- `permission_request.py` surfaces paid-provider, credential, destructive, and network-sensitive requests for operator review.
- `stop_gate.py` reports worktree and verification posture without claiming success. An
  incomplete active arc remains visible in its `systemMessage` but is advisory at the Stop
  event, so Codex can yield at a genuine operator gate; explicit `just codex-closeout`,
  commit, and PR gates remain hard. Failure to create the Stop checkpoint itself remains
  hard: without a durable checkpoint, the hook cannot honestly claim the session is safe
  to resume.

## Parity map

| Claude lifecycle | Codex mapping | Status |
|---|---|---|
| `SessionStart` | roadmap audit + loop GC + Codex context guard | Equivalent plus Codex guard |
| `PreToolUse` | cache clear + permission guard + Codex boundary guard | Equivalent plus Codex guard |
| `PreToolUse Bash(git commit*)` | `codex_hook_adapter.py pre-commit` runs pyright and root validation only for commit commands | Equivalent |
| `PermissionRequest` | permission guard + Codex request classifier | Equivalent plus Codex classifier |
| `PreCompact` / `PostCompact` | existing checkpoint and reinjection scripts | Direct |
| `PostToolUse` | roadmap refresh audit + adapter-driven edit lint | Equivalent; `apply_patch` replaces Claude `Edit|Write|MultiEdit` |
| `PostToolUseFailure` | Codex `PostToolUse` receives structured nonzero Bash results; the adapter normalizes them into `capture-failure.sh`'s Claude payload | Behavior-equivalent adapter |
| `UserPromptSubmit` | prompt context + skill activation + prompt lint | Direct |
| `SubagentStart` / `SubagentStop` | existing subagent validation | Direct |
| `SessionEnd` | existing cleanup | Direct |
| `Stop` | Claude stop gate + git arc guard + loop stop, followed by the Codex context gate | Direct plus Codex guard |
| `StopFailure` | no dedicated Codex lifecycle event exists | Not event-exact; stop failures remain visible and recurring command failures still flow through the adapter |

Codex has no dedicated `PostToolUseFailure` or `StopFailure` event. The first is covered for
structured Bash results because `PostToolUse` fires for failed Bash calls. Its documented
`tool_response` type is any JSON value, so unstructured text is not itself a failure signal:
successful local tools may also return model-facing text. The second cannot be reproduced
exactly until Codex exposes that lifecycle event; it is the only hook-level compatibility gap.

## Trust and startup failures

Codex trusts command hooks by exact definition hash. After `.codex/hooks.json` changes land, open `/hooks` in the Codex TUI, review the project hook definitions, and trust them. Do not use `--dangerously-bypass-hook-trust` as the durable setup.

The 2026-08-01 `SessionStart` / `Stop` failures had three independent causes: the context
guard classified operator-local design skills, dashboard output, and memory output as
root-checkout edits; Stop hard-failed an intentionally incomplete arc at a genuine operator
gate; and the ported lint hook inherited an unwritable default uv cache. Precise `.gitignore`
entries preserve local assets, Stop reports incomplete-loop posture without failing the hook,
and every uv-backed lint/pre-commit hook defaults to `/tmp/arhugula-uv-cache`. Checkpoint
creation failures and the explicit closeout guard remain hard.

Credential-gated work should advance to the exact credential boundary first. If
no HIL/operator-approval surface is available, log the pending gate with
`just codex-credential-gate ...`, update a human-facing roadmap/status surface,
and proceed only after the non-credential work is proven closed.

Claude remains the canonical source for the original hook intent. Codex maps the complete compatible behavior set without depending on Claude-specific environment variables; see `.codex/notes/claude-codex-parity.md` for the full runner audit.
