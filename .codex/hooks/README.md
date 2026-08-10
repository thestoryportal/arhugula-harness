# Codex Hooks

These hooks are a Codex-native compatibility layer for the Claude hooks in `.claude/settings.json`.

Every Claude hook behavior supported by Codex's lifecycle is wired here. The Codex-native guards remain additive:

- `codex-session-start.sh` registers the session under the shared git directory before
  sequentially running posture, roadmap audit, and read-only worktree hygiene reporting.
  Destructive GC is an explicit post-merge/closeout action, never a SessionStart action.
  The wrapper activates the lease only
  after startup succeeds; normal failures release immediately and an abandoned starting
  lease expires after a three-minute grace window, longer than the 105-second hook timeout.
  A repeated `SessionStart(source=compact)` for the same root session preserves the active
  lease, so failure or interruption of the compact-start cannot make that session reapable.
  Active leases record the Codex owner process identity; an abnormal owner exit makes the
  lease inactive without weakening live-session protection or requiring SessionEnd.
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
| `SessionStart` | session lease + roadmap audit + read-only hygiene report + Codex context guard | Equivalent plus Codex guard |
| `PreToolUse` | cache clear + permission guard + Codex boundary guard | Equivalent plus Codex guard |
| `PreToolUse Bash(git commit*)` | `codex_hook_adapter.py pre-commit` runs pyright and root validation only for commit commands | Equivalent |
| `PermissionRequest` | permission guard + Codex request classifier | Equivalent plus Codex classifier |
| `PreCompact` | generation-ordered atomic session-specific checkpoint | Direct |
| `PostCompact` | shared reinjection producer through the Codex adapter; compact SessionStart context uses the same producer | Equivalent effect |
| `PostToolUse` | roadmap refresh audit + adapter-driven edit lint | Equivalent; Codex `apply_patch` paths are parsed from `tool_input.command` |
| `PostToolUseFailure` | Codex `PostToolUse` receives structured nonzero Bash results; the adapter normalizes them into `capture-failure.sh`'s Claude payload | Behavior-equivalent adapter |
| `UserPromptSubmit` | prompt context + skill activation + prompt lint | Direct |
| `SubagentStart` / `SubagentStop` | existing subagent validation | Direct |
| `SessionEnd` | lease-first release + local-only cleanup in one three-second handler | Direct |
| `Stop` | Claude stop gate + git arc guard + loop stop, alongside the Codex context gate | Direct plus Codex guard |
| `StopFailure` | no dedicated Codex lifecycle event exists | Not event-exact; stop failures remain visible and recurring command failures still flow through the adapter |

## Hook contract map

Parity means **equivalent effect**, not byte-identical output schemas. The shared
Claude producers retain their Claude contracts; Codex adapters translate only the
effects that Codex accepts.

| Case | Claude producer and boundary | Codex effect |
|---|---|---|
| Safe `PreToolUse` allow | `permission-guard.sh` -> `permission-guard` adapter | No Codex opinion, even if the Claude producer includes `updatedInput`; it does not approve or rewrite execution. `PermissionRequest` decides approval through its supported boundary. |
| Hard `PreToolUse` deny | `permission-guard.sh` -> `permission-guard` adapter | Reconstructs only the supported deny decision and its reason; Claude-only fields never cross the Codex boundary. |
| Post-compaction context | `postcompact-reinject.sh` -> `post-compact` adapter | Universal `systemMessage` only, including producer diagnostics; the Claude-shaped producer output is not itself a Codex hook response. A silent producer yields no output and exit 0. |
| Compact model context | `postcompact-reinject.sh` -> `compact-context` adapter -> SessionStart wrapper | Appends only when `source=compact`; any producer failure preserves the rest of SessionStart and appends an explicit recovery instruction. |

Shared-producer tests prove the original Claude contracts. PostCompact translation
validity is covered by shared-producer and adapter behavioral tests. The installed-host runtime witness
keeps the real `PreToolUse:permission-guard` and `PostCompact:post-compact` adapters;
the remaining handlers for `SessionStart`, `PreToolUse`, `PostToolUse`, `PreCompact`,
`Stop`, and `SessionEnd` are recorder substitutes. Events outside that bounded set,
including `PermissionRequest`, are omitted from the live fixture; their contracts are
covered by hermetic shared-producer and registration tests.

Codex has no dedicated `PostToolUseFailure` or `StopFailure` event. The first is covered for
structured Bash results because `PostToolUse` fires for failed Bash calls. Its documented
`tool_response` type is any JSON value, so unstructured text is not itself a failure signal:
successful local tools may also return model-facing text. The second cannot be reproduced
exactly until Codex exposes that lifecycle event; it is the only hook-level compatibility gap.

Run `just codex-hook-runtime-witness` to verify the installed Codex CLI host itself. The
witness derives its matcher groups from `.codex/hooks.json`, removes provider credentials,
serves five deterministic Responses exchanges from `127.0.0.1`, forces one automatic
compaction, and proves PreCompact, accepted PostCompact output, compact SessionStart, Bash
and apply_patch Pre/PostToolUse, Stop, SessionEnd, and both allowed tool effects. It also
proves the exact registered command shapes, executes absolute-path equivalents three times
for permission and once for PostCompact, requires positive non-empty PostCompact output
evidence, and verifies that a force-push command's pre-effect marker stayed absent after
Codex parsed the real deny. It reports the installed Codex version and uses the production
`/usr/bin/python3` interpreter for both real adapters and
`--dangerously-bypass-hook-trust` only inside that vetted temporary fixture; normal sessions
still require explicit trust through `/hooks`.

The shared `PreToolUse` producer currently emits only `allow` or `deny` and never emits
`updatedInput`. The Codex adapter intentionally treats any future unsupported decision as a
structured deny and suppresses any future allow-side rewrite until that new producer contract
has explicit Codex coverage.

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
authoritative until SessionEnd or owner-process death, and registration/activation revalidate the worktree after
locking. The mutex and leases are keyed by stable Git worktree administration identity,
so a quarantine move cannot split their authority. The explicit remover alone moves a clean
candidate to an opaque sibling quarantine before its authoritative scans. This closes normal
lookups through the original pathname; retained cwd, file-descriptor, and Linux
mapping references are detected fail-closed before a final local-state scan and deletion.
The macOS `lsof` observation is time-bounded and timeout is unknown/fail-closed. A process-death recovery transaction restores interrupted
quarantines on TERM and lets a later removal pass recover after untrappable process death,
including a death between Git's directory rename and administrative-path update. The safety
boundary covers cooperative Claude/Codex writers that use the session lease plus processes
that already retain a kernel reference. It is not a security boundary against an
uncooperative same-UID process that deliberately discovers and writes into the opaque
quarantine; such a process can also rewrite repository metadata and permissions directly.
`just codex-worktree-gc --reap` uses this same status and removal entrypoint; it cannot
bypass Codex leases, quarantine, or the shared mutex.

Credential-gated work should advance to the exact credential boundary first. If
no HIL/operator-approval surface is available, log the pending gate with
`just codex-credential-gate ...`, update a human-facing roadmap/status surface,
and proceed only after the non-credential work is proven closed.

Claude remains the canonical source for the original hook intent. Codex maps the complete compatible behavior set without depending on Claude-specific environment variables; see `.codex/notes/claude-codex-parity.md` for the full runner audit.
