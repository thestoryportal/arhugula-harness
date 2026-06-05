# Research: Session-End Cleanup & Autonomous Loop Architecture

**Source:** Gemini research session
**Topic:** Triggering `session_cleanup.sh` on `/clear`; replacing HIL with a headless autonomous loop

---

## Key Constraints

- **No PreClear hook exists.** There is no lifecycle event that fires before `/clear` wipes context.
- **`SessionEnd` on `/clear` is unreliable.** Conversation history is typically already gone by the time a cleanup script attempts to read the transcript.
- **Hook scripts cannot inject `/clear` back into the session.** Hooks execute in a separate system shell process, disconnected from the Claude Code prompt-input loop. Attempting this creates a logical paradox and will not work.
- **LLM prompts requiring prior session memory cannot run after `/clear`.** Context is lost immediately.

---

## HIL Pattern: Hooking `/clear` for Workspace Cleanup

For Human-in-the-Loop workflows, configure `SessionEnd` to fire `session_cleanup.sh` when a clear occurs. Because context is already wiped at this point, **the script must only touch physical files and workspace state — not the LLM transcript.**

```json
{
  "hooks": [
    {
      "event": "SessionEnd",
      "matcher": "clear",
      "cmd": "bash ~/path/to/session_cleanup.sh"
    }
  ]
}
```

To re-inject environment variables or project constraints into the fresh context immediately after a clear, pair a `SessionStart` hook:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "clear",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Context cleared — resetting configuration...'"
          }
        ]
      }
    ]
  }
}
```

---

## Autonomous Loop Pattern: Replacing HIL with a Headless Orchestrator

The correct architecture for removing HIL from the loop is to **move control outside Claude Code** into an external shell orchestrator. Each `claude -p` invocation is a fully isolated process — equivalent to a `/clear` — with no shared message memory.

### Why `Stop` hook, not `SessionEnd`

`SessionEnd` fires only when the parent CLI process is killed. In an autonomous agent loop, use the **`Stop` hook**, which fires the moment Claude finishes its task and stops emitting tool calls.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/session-end-cleanup.sh"
          }
        ]
      }
    ]
  }
}
```

### State Bridge

Because the next iteration starts with a completely empty context window, `session-end-cleanup.sh` must write any essential state (sub-agent context, task queue position, logs) to a persistent file (e.g., `.agent_state.json`) before the session exits. The next iteration reads this file on `SessionStart`.

### Orchestrator Loop (`autonomous-runner.sh`)

```bash
#!/bin/bash

TASK_FILE=".agent_tasks.json"

while true; do
    # Stop when the atomic queue is exhausted
    if [ ! -f "$TASK_FILE" ] || jq -e '.queue == []' "$TASK_FILE" > /dev/null; then
        echo "All atomic units complete. Stopping autonomous loop."
        break
    fi

    echo "=== Starting New Isolated Session (Implicit Clear) ==="

    # Each invocation: fresh process, 0 token context, all 15 hooks fire normally
    claude -p "Process the next logged atomic unit from $TASK_FILE." \
           --permission-mode bypassPermissions

    sleep 2  # Allow OS file handles to release
done
```

### Why this works

| Property | Detail |
|---|---|
| **True context reset** | Each `claude -p` spawns a new OS process. No `--continue` flag means 0 shared message memory — identical to a manual `/clear`. |
| **No HIL intervention** | `--permission-mode bypassPermissions` prevents tool-execution confirmation prompts. |
| **Hook sequence intact** | All 15 hooks fire normally on `SessionStart`, `PreToolUse`, `PostToolUse`, and `Stop` within each isolated run. |
| **Indefinite operation** | Context exhaustion cannot accumulate across iterations because each iteration starts at 0 tokens. |

---

## Expansion: Additional Data Stream Pipelines

The same pattern extends to any data source that can be formatted as a time-bounded array. Use the A–C pipelines as rigid templates when prompting Claude to build new extraction scripts.

| Stream Type | Use Case | Signal Direction |
|---|---|---|
| `upwork_spend_velocity` | Labor-to-software arbitrage — freelance spend on manual tasks accelerating | Rising spend → software deficit |
| `builtwith_churn_rate` | Technographic defection — live site removal rate for a legacy competitor | Accelerating removals → 90-day head start before public reviews |
| `linkedin_role_velocity` | "Grunt work" hiring index — non-tech orgs hiring humans to patch a workflow | Rising postings → direct automation target |

---

## Single File Agents (SFAs) for TSFM Stream Types

Each data stream pipeline maps cleanly to a Single File Agent. SFAs are a strong fit for the quantitative, deterministic nature of TSFM integration.

**Advantages over monolithic agents:**

- **Stateless predictability** — e.g., `github_decay_agent.py` has one prompt, one tool (the TSFM broker), and one job. It spins up, executes its mandate, returns structured output, and exits.
- **Surgical debugging** — if `marketplace_review_velocity` returns false positives, open that SFA, adjust its system prompt or thresholds, and test in isolation without untangling a routing graph.
- **Parallel execution** — because SFAs encapsulate their own logic and API calls, the orchestrator can trigger multiple SFAs simultaneously to investigate an opportunity across several time-series vectors.
- **Clean orchestration handoffs** — an SFA translates the Semantic Broker's mathematical verdict into a markdown brief, handed off to the primary Synthesis agent. The master agent's context window stays free of raw data processing.

**Pattern:** Treat each stream type (A, B, C, …) as its own SFA. The result is a library of specialized quantitative analysts, each independently testable and composable by the orchestrator.

---

## References

- [GitHub #6428 — SessionEnd hook does not fire with `/clear`](https://github.com/anthropics/claude-code/issues/6428)
- [GitHub #26052 — Feature request: PreClear hook event](https://github.com/anthropics/claude-code/issues/26052)
- [GitHub #6534 — Trigger `/export` on `/clear`](https://github.com/anthropics/claude-code/issues/6534)
- [Claude Code Hooks Reference](https://docs.anthropic.com/claude-code/hooks)