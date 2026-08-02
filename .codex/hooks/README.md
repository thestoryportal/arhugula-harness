# Codex Hooks

These hooks are a Codex-native compatibility layer for the Claude hooks in `.claude/settings.json`.

Every Claude hook behavior supported by Codex's lifecycle is wired here. The Codex-native guards remain additive:

- `codex-session-start.sh` registers the session under the shared git directory before
  sequentially running posture, roadmap audit, and loop GC, so concurrent SessionStart
  handlers cannot race lease registration against removal. It activates the lease only
  after startup succeeds; normal failures release immediately and an abandoned starting
  lease expires after a three-minute grace window, longer than the 105-second hook timeout.
  A repeated `SessionStart(source=compact)` for the same root session preserves the active
  lease, so failure or interruption of the compact-start cannot make that session reapable.
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
| `SessionStart` | session lease + roadmap audit + loop GC + Codex context guard | Equivalent plus Codex guard |
| `PreToolUse` | cache clear + permission guard + Codex boundary guard | Equivalent plus Codex guard |
| `PreToolUse Bash(git commit*)` | `codex_hook_adapter.py pre-commit` runs pyright and root validation only for commit commands | Equivalent |
| `PermissionRequest` | permission guard + Codex request classifier | Equivalent plus Codex classifier |
| `PreCompact` / `PostCompact` | generation-ordered atomic session-specific checkpoint and reinjection scripts | Direct |
| `PostToolUse` | roadmap refresh audit + adapter-driven edit lint | Equivalent; Codex `apply_patch` paths are parsed from `tool_input.command` |
| `PostToolUseFailure` | Codex `PostToolUse` receives structured nonzero Bash results; the adapter normalizes them into `capture-failure.sh`'s Claude payload | Behavior-equivalent adapter |
| `UserPromptSubmit` | prompt context + skill activation + prompt lint | Direct |
| `SubagentStart` / `SubagentStop` | existing subagent validation | Direct |
| `SessionEnd` | lease-first release + local-only cleanup in one three-second handler | Direct |
| `Stop` | Claude stop gate + git arc guard + loop stop, alongside the Codex context gate | Direct plus Codex guard |
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

Fresh merge-gate reviewers run with `HARNESS_CODEX_REVIEW_ISOLATED=1`. The permission
guard accepts that marker only in the exact ephemeral/read-only lens command shape; inside
the child, controller checkpoint, cleanup, prompt, and loop-mutating hooks are inert while
the session lease remains active. Direct `git worktree remove` is denied because a hook
cannot hold a mutex after it exits; use `tools/hooks/safe-worktree-remove.sh <path>`. Its
kernel-owned lock survives long removals without age-based theft, active leases remain
authoritative until SessionEnd, and registration/activation revalidate the worktree after
locking. The remover atomically moves a clean candidate to an unpublished sibling
quarantine before its authoritative status scan, so writes through the original pathname
cannot enter the directory Git deletes; any state found inside quarantine is restored.
`just codex-worktree-gc --reap` uses this same status and removal entrypoint; it cannot
bypass Codex leases, quarantine, or the shared mutex.

Credential-gated work should advance to the exact credential boundary first. If
no HIL/operator-approval surface is available, log the pending gate with
`just codex-credential-gate ...`, update a human-facing roadmap/status surface,
and proceed only after the non-credential work is proven closed.

Claude remains the canonical source for the original hook intent. Codex maps the complete compatible behavior set without depending on Claude-specific environment variables; see `.codex/notes/claude-codex-parity.md` for the full runner audit.
