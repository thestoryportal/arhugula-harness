# Claude Code & Claude Agent SDK — Hooks Reference (capability ground-truth)

> Authoritative reference for what a hook CAN do. Every hardening proposal must be
> expressible here — do not propose a hook on an event that doesn't exist or a
> control output an event doesn't support.

**Sources** (all fetched 2026-06-03):
- Claude Code Hooks reference — https://code.claude.com/docs/en/hooks (canonical; `docs.claude.com/en/docs/claude-code/hooks` → 301 → this)
- Claude Code Hooks guide — https://code.claude.com/docs/en/hooks-guide
- Claude Agent SDK Hooks — https://code.claude.com/docs/en/agent-sdk/hooks
- Debug your config — https://code.claude.com/docs/en/debug-your-config

> **Currency note:** the canonical host migrated to `code.claude.com`; the current
> reference defines MANY more events than older `docs.anthropic.com` "9-event"
> snapshots. Treat any short event list as stale.

---

## 1. Hook events

A hook handler `type` is one of: `command` (shell), `http` (POST to URL),
`mcp_tool` (call a connected MCP tool), `prompt` (single-turn LLM yes/no),
`agent` (multi-turn subagent verification; **experimental**). When an event fires,
**all matching hooks run in parallel** and **identical hook commands are deduplicated**.

| Event | When it fires | Key input fields (beyond common) | Can block? |
|---|---|---|---|
| `SessionStart` | Session begins or resumes | `source` (`startup`/`resume`/`clear`/`compact`), `model` | No (exit 2 → shows stderr, continues) |
| `Setup` | `claude --init-only`, or `--init`/`--maintenance` in `-p` | `trigger` (`init`/`maintenance`) | No |
| `UserPromptSubmit` | User submits a prompt, before Claude processes it | `prompt`, `permission_mode` | **Yes** |
| `UserPromptExpansion` | A user-typed command expands into a prompt | `expansion_type`, `command_name`, `command_args`, `prompt` | **Yes** |
| `PreToolUse` | Before a tool call executes | `tool_name`, `tool_input`, `permission_mode` | **Yes** (primary tool gate) |
| `PermissionRequest` | A permission dialog is about to appear | `tool_name`, `tool_input`, `permission_mode` | Decides allow/deny. **Does NOT fire in `-p` headless mode** |
| `PermissionDenied` | Tool call denied by the auto-mode classifier | `tool_name`, `tool_input` | Return `{retry:true}` to let the model retry |
| `PostToolUse` | After a tool call **succeeds** | `tool_name`, `tool_input`, `tool_response` | `decision:"block"` (feedback only; cannot undo) |
| `PostToolUseFailure` | After a tool call **fails** | `tool_name`, `tool_input`, `tool_error` | `decision:"block"` |
| `PostToolBatch` | After a batch of parallel tool calls resolves | (none tool-specific) | `decision:"block"` |
| `Stop` | Claude finishes responding (**every turn end**, not only task completion; not on user interrupt) | `stop_hook_active` | **Yes** — `decision:"block"` makes Claude keep working |
| `StopFailure` | Turn ends due to an API error | error context | **Output & exit code IGNORED** |
| `SubagentStart` | A subagent is spawned | `agent_type` | No |
| `SubagentStop` | A subagent finishes | `agent_type`, `agent_id`, `agent_transcript_path`, `stop_hook_active` | **Yes** |
| `TaskCreated` | A task is being created (`TaskCreate`) | task context | **Yes** |
| `TaskCompleted` | A task is being marked completed | task context | **Yes** |
| `TeammateIdle` | An agent-team teammate about to go idle | teammate context | **Yes** |
| `Notification` | Claude Code sends a notification | `message`, `notification_type` | No |
| `MessageDisplay` | While an assistant message is displayed | `message` | No (can rewrite displayed text only) |
| `InstructionsLoaded` | A `CLAUDE.md` / rules file is loaded | `file_path`, `memory_type`, `load_reason` | No |
| `ConfigChange` | A config file changes during a session | `source`, `file_path` | **Yes** |
| `CwdChanged` | Working directory changes (e.g. a `cd`) | cwd in common fields | No |
| `FileChanged` | A watched file changes on disk (matcher = filenames) | `file_path`, `change_type` | No |
| `WorktreeCreate` | A worktree is being created (replaces default git behavior) | worktree context | **Yes** |
| `WorktreeRemove` | A worktree is being removed | worktree context | No |
| `PreCompact` | Before context compaction (matcher `manual`/`auto`) | — | **Yes** |
| `PostCompact` | After compaction completes | — | No |
| `Elicitation` / `ElicitationResult` | MCP server requests/returns user input | MCP context | **Yes** |
| `SessionEnd` | A session terminates (matcher = exit reason) | — | No |

> **NOTE for D7/D8:** `CwdChanged` (fires on a `cd`) and `FileChanged` exist but are
> NON-blocking. `WorktreeCreate` IS blockable. `PostToolUse(Bash)` is the practical
> place to inspect a `cd ... && git ...` command (it sees `tool_input.command`).

---

## 2. Hook input (stdin for `command` hooks)

**Common fields (every event):**
```json
{ "session_id":"…", "transcript_path":"/…/transcript.jsonl", "cwd":"/…",
  "permission_mode":"default", "hook_event_name":"PreToolUse",
  "effort":{"level":"high"}, "agent_id":"…", "agent_type":"Explore" }
```
- `permission_mode` ∈ `default` `plan` `acceptEdits` `auto` `dontAsk` `bypassPermissions`.
- `effort.level` ∈ `low`/`medium`/`high`/`xhigh`/`max`.
- `agent_id`/`agent_type` present only inside a subagent.

**Event-specific (selected):** `PreToolUse`/`PostToolUse`: `tool_name`, `tool_input`
(e.g. `{"command":"npm test"}` for Bash), `tool_response`/`tool_error`.
`UserPromptSubmit`: `prompt`. `SessionStart`: `source`, `model`.
`Stop`/`SubagentStop`: `stop_hook_active` (boolean — **check it to avoid infinite loops**).

---

## 3. Hook output / control protocol

### 3.1 Exit codes (`command` hooks)
| Exit | Meaning |
|---|---|
| `0` | Success. stdout parsed as JSON (below); if not JSON, treated as plain-text context (injected for `UserPromptSubmit`, `SessionStart`, `PostToolUse*`). For `PreToolUse`, exit 0 + empty = **no decision** (normal permission flow; does NOT approve). |
| `2` | **Blocking error**; stdout ignored, **stderr** is the message. BLOCKS for: `PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `ConfigChange`, `PreCompact`, `Elicitation`, `WorktreeCreate`. NON-blocking (stderr shown, continues) for: `PostToolUse`, `PostToolUseFailure`, `Notification`, `SessionStart`, `SessionEnd`, `CwdChanged`, `FileChanged`, `PostCompact`, etc. No effect: `StopFailure`, `PermissionDenied`, `WorktreeRemove`. |
| other | Non-blocking error; transcript shows `<hook> hook error`; continues. |

> **Do not mix:** exit 2 with stderr **or** exit 0 with JSON — JSON is ignored on exit 2.

### 3.2 Top-level JSON output (any event, exit 0)
```json
{ "continue": true, "stopReason": "…", "suppressOutput": false,
  "systemMessage": "…", "decision": "block", "reason": "…",
  "additionalContext": "…", "hookSpecificOutput": { "hookEventName": "PreToolUse" } }
```
- `continue:false` → **stops Claude entirely**; `stopReason` shown to the user (not Claude).
- `decision:"block"` (+ `reason`) — used by `UserPromptSubmit`, `PostToolUse(*)`, `PostToolBatch`, `Stop`, `SubagentStop`, `ConfigChange`, `PreCompact`.
- `additionalContext` — string injected into Claude's context.
- `systemMessage` — warning shown to the user.

### 3.3 `hookSpecificOutput` per event

**`PreToolUse`** (the primary tool gate):
```json
{ "hookSpecificOutput": { "hookEventName":"PreToolUse",
  "permissionDecision":"deny", "permissionDecisionReason":"…",
  "updatedInput": { "command":"npm run lint" } } }
```
- `permissionDecision` ∈ `allow` `deny` `ask` `defer`.
  - `allow` — skip the prompt. **Deny/ask rules (incl. managed deny lists) STILL apply — `allow` cannot loosen permissions.**
  - `deny` — cancel; reason fed back to Claude.
  - `ask` — show the normal prompt.
  - `defer` — **headless `-p` only** (exits with the call preserved for an SDK wrapper).
- `updatedInput` — modified input (with `allow`/`ask`). Multiple hooks → **last to finish wins** (non-deterministic) — avoid >1 hook rewriting the same input.
- **`PreToolUse` fires BEFORE any permission-mode check, so `deny` blocks even in `bypassPermissions` / `--dangerously-skip-permissions`. Hooks can TIGHTEN but not loosen.**

**`PermissionRequest`** (auto-approve a dialog — interactive only):
```json
{ "hookSpecificOutput": { "hookEventName":"PermissionRequest",
  "decision": { "behavior":"allow", "updatedInput": {…} } } }
```
- `decision.behavior` ∈ `allow`/`deny`. May include `decision.updatedPermissions` with `{"type":"setMode","mode":"acceptEdits","destination":"session"}`.
- **Does NOT fire in `-p` headless mode** → use `PreToolUse` there.

**`Stop`/`SubagentStop`/`PostToolUse`/`PreCompact`/`ConfigChange`:** block via top-level
`{"decision":"block","reason":"…"}`; inject via `hookSpecificOutput.additionalContext`.

**`UserPromptSubmit`:** block via `decision:"block"`(+`reason`) or exit 2; inject via
`additionalContext`; `suppressOriginalPrompt:true` replaces the prompt; `sessionTitle` sets the name.

**`SessionStart`:** `additionalContext`, `sessionTitle`, `initialUserMessage`, `watchPaths`, `reloadSkills`.

### 3.4 Combining multiple hooks
All matching hooks run; outputs merge. **For `PreToolUse` permission decisions the
MOST RESTRICTIVE wins: `deny` > `ask` > `allow`** (SDK: `deny` > `defer` > `ask` >
`allow`). `additionalContext` concatenates. One hook's `deny` does NOT stop sibling
hooks' side effects.

---

## 4. settings.json configuration shape

```json
{ "hooks": {
  "PreToolUse": [
    { "matcher": "Bash",
      "hooks": [ { "type":"command", "if":"Bash(rm *)",
        "command":"${CLAUDE_PROJECT_DIR}/.claude/hooks/x.sh", "timeout":30 } ] }
  ],
  "PostToolUse": [
    { "matcher": "Edit|Write",
      "hooks": [ { "type":"command", "command":"…" } ] }
  ]
}}
```
**Handler fields:** `type` (`command`/`http`/`mcp_tool`/`prompt`/`agent`); `command`
(with `args` → exec form no-shell; without → shell form supports pipes/`&&`/globs);
`if` (tool events only — permission-rule syntax filtering by tool name+args, e.g.
`"Bash(git *)"`, `"Edit(*.ts)"`; **requires Claude Code ≥ v2.1.85**); `timeout`
(seconds; default 10 min for command/http/mcp_tool, `UserPromptSubmit` 30s, `prompt`
30s, `agent` 60s); `async:true` / `asyncRewake:true`. Placeholders: `${CLAUDE_PROJECT_DIR}`,
`${CLAUDE_PLUGIN_ROOT}`.

**Matcher semantics:** `"*"`/`""`/omitted = all; letters/digits/`_`/`|` = exact or
`|`-list (`Edit|Write`, **case-sensitive**); any other char = JS regex. MCP tools:
`mcp__<server>__<tool>` (whole server: `mcp__memory__.*`, the `.*` is mandatory).
Matched field varies by event (tool events → `tool_name`; `SessionStart` → `source`;
`PreCompact` → `manual`/`auto`; etc.). **No matcher support:** `UserPromptSubmit`,
`PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated/Completed`, `WorktreeCreate/Remove`,
`CwdChanged`, `MessageDisplay`.

**Config locations (precedence: managed/policy wins):** `~/.claude/settings.json` ·
`.claude/settings.json` (project, committable) · `.claude/settings.local.json`
(gitignored) · managed policy · plugin `hooks/hooks.json`. `disableAllHooks:true`
disables (managed still run). **Config reload:** edits take effect in-session after a
brief file-stability delay (live file-watcher; **no restart**); re-run `/hooks` to
refresh the view. (The legacy "startup-snapshot, changes need review" framing is
SUPERSEDED on the current docs.)

---

## 5. Prompt- & agent-based hooks (LLM-evaluated)
- **`type:"prompt"`** — single-turn LLM (Haiku default; `model` override). Returns
  `{"ok":true|false,"reason":"…"}`. `ok:false`: `Stop`/`SubagentStop` → reason fed
  back (keep working); `PreToolUse` → tool denied; `PostToolUse`/`UserPromptSubmit`
  → turn ends with reason as warning. Timeout 30s.
- **`type:"agent"`** — **experimental** (prefer command hooks in production). Spawns a
  subagent that can read files / run commands; same `{"ok","reason"}`; default 60s;
  ≤50 tool turns; `$ARGUMENTS` supported.

---

## 6. Autonomous-loop & auto-approval guidance (LOAD-BEARING for this workflow)

- **Auto-approve a permission dialog (interactive):** `PermissionRequest` → `{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}`. **Keep the matcher narrow** — `.*`/empty auto-approves EVERY prompt incl. writes + shell. Does NOT fire in `-p`.
- **Auto-approve in headless/SDK loops:** `PreToolUse` with `permissionDecision:"allow"` (the doc's explicit guidance when `PermissionRequest` is unavailable). `allow` still cannot override deny/ask rules.
- **Unbypassable policy enforcement:** `PreToolUse` fires before any permission-mode check → `deny` blocks even in `bypassPermissions` mode. **Hooks tighten, never loosen.** (This is why the permission-guard's deny-list is a real blast-radius limiter.)
- **Stop-hook continuation loops (auto-continue):** a `Stop` hook returning
  `decision:"block"` (or a prompt/agent hook with `ok:false`) makes Claude keep
  working — the "don't stop until done" mechanism. **GUARDRAILS:** Claude Code
  **overrides a `Stop` hook after it blocks 8 times in a row** without progress;
  parse `stop_hook_active` and exit 0 when true to prevent runaway; raise the cap
  with env `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`. `Stop` fires on EVERY turn end, NOT on
  user interrupt.
- **SDK subagent loops:** a `UserPromptSubmit` hook that spawns subagents can
  infinite-loop if they re-trigger it — gate on a subagent indicator. Subagents do
  NOT inherit parent permissions. Hooks may NOT fire at `max_turns` (session ends first).
- **Security disclaimer (verbatim):** *"Claude Code hooks execute arbitrary shell
  commands on your system automatically. By using hooks, you acknowledge that you are
  solely responsible for the commands you configure; hooks can modify, delete, or
  access any files your user account can access; malicious or poorly written hooks
  can cause data loss or system damage; and you should thoroughly test hooks in a safe
  environment before production use."* Best practices: validate/sanitize inputs, quote
  shell vars, block path traversal, use absolute paths, skip sensitive files.

---

## 7. Claude Agent SDK hooks (programmatic) — differences

Registered via a `hooks` map in agent options (`ClaudeAgentOptions(hooks=…)` /
`query({options:{hooks:…}})`). Keys = event names; values = matcher groups
(`HookMatcher(matcher=…, hooks=[…])` / `{matcher, hooks:[cb]}`). Callbacks are
**in-process functions** returning the **same JSON output format** as shell hooks
(not stdout/exit codes). Return `{}` to allow unchanged. Async side-effect form:
`{"async":true,"asyncTimeout":30000}`. Precedence `deny>defer>ask>allow`.

**SDK event coverage (subset of Claude Code):** Both Python+TS: `PreToolUse`,
`PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStart`,
`SubagentStop`, `PreCompact`, `PermissionRequest`, `Notification`. TS-only adds
`PostToolBatch`, `MessageDisplay`, `SessionStart/End`, `Setup`, `TeammateIdle`,
`TaskCompleted`, `ConfigChange`, `WorktreeCreate/Remove`. Python lacks
`SessionStart`/`SessionEnd` in `HookEvent` (use settings-file shell hooks via
`setting_sources=["project"]`). `systemMessage` is shown to the *user*; pass
`additionalContext` to reach the *model*.

---

## 8. Flagged / not-fully-verified
- The exhaustive per-event input field tables (every optional field on `ConfigChange`,
  `FileChanged`, `WorktreeCreate`) live in the per-event sections of the reference and
  were not all transcribed; field *names* above are quoted as the docs present them.
- The legacy "hooks startup-snapshot" safety paragraph is **superseded** (live reload now).
- Security disclaimer §6 cross-sourced from the `#security-considerations` anchor.
