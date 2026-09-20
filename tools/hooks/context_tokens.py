#!/usr/bin/env python3
"""Where this session's context sits against its ceiling, as one decided verdict.

The loop's Stop hook (`stop-loop.sh`) continues a turn by blocking the stop, and a block
sets `stop_hook_active` on the next Stop. memento's own ceiling hook steps aside whenever
that flag is set (`memento/hooks/scripts/context-ceiling.py:220`, upstream `promptctl/memento`
@0d1f5bc), so in loop mode the ceiling has no enforcer unless the loop hook is one. This is
that enforcer's measuring half: it reads the transcript, resolves the ceiling, and hands back
one verdict for the shell to dispatch on. [LAW:parse-dont-validate] the verdict is the stamp —
`stop-loop.sh` reads it and re-derives none of it, so there is nothing left downstream to
re-check.

Verdicts, the domain's own enum:

  under      below the ceiling; the loop continues as it always does.
  relaunch   over the ceiling under the headless runner: allow the stop, because
             `tools/04-loop/run.sh` starts the next iteration itself. Blocking here would
             put a second session on one worktree, which is what plan decision 7 avoids.
  close-out  over the ceiling in an attended session: nothing will relaunch it, so the turn
             is blocked and the session is told to commit and close out.

The token sum mirrors memento's (`context-ceiling.py:48-49,106-112`): the newest assistant
record's usage, summed over all four prompt components, sidechains skipped. Both programs
read the same territory — Claude Code's transcript format — rather than one copying the
other, so neither is the other's second source of truth.

Usage: `context_tokens.py [--headless] < <Stop payload>`; the verdict goes to stdout as JSON.
A session whose context cannot be measured exits non-zero rather than reporting a number, and
the caller records that; see `main`. Tests: sections 9 and 10 of `tools/hooks/test_stop_loop.sh`,
which drive this file directly, beside the end-to-end arms in section 8.
"""

import json
import os
import sys
from pathlib import Path

# The floor when memento is not installed. Its own default, so a workspace that later adds
# memento without touching any config sees the number it already had.
DEFAULT_CEILING = 250_000
# memento's four prompt components. A session's context is all of them, not input_tokens
# alone: the cache fields are most of a long session's real position.
PROMPT_COMPONENTS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)
TAIL_CHUNK = 256 * 1024
# Where `claude plugin install memento@memento` puts the plugin. MEMENTO_ROOT overrides it,
# which is what lets the suite point at a fixture instead of the operator's real install.
MEMENTO_ROOT = Path(
    os.environ.get("MEMENTO_ROOT")
    or Path.home() / ".claude" / "plugins" / "cache" / "memento" / "memento"
)


def resolve_ceiling(session_id, cwd):
    """The ceiling in force, from memento's layers when memento is installed.

    [LAW:one-source-of-truth] memento owns this number wherever it exists — the operator can
    move it per-session or per-project with `ceiling`, and a copy kept here would be a second
    clock that disagrees the first time they do. Absence of the plugin is a legal domain
    value, not a failure, so it resolves to the default; an import that exists and *raises*
    is a genuine failure and is left to surface. [LAW:no-silent-failure]
    """
    config = MEMENTO_ROOT / "lib" / "ceiling_config.py"
    if not config.is_file():
        return DEFAULT_CEILING
    sys.path.insert(0, str(config.parent))
    from ceiling_config import (
        SHARED_AT_START,
        anchored,
        in_force,
        session_directory,
        shared_at_start,
    )

    directory = session_directory(session_id)
    return in_force(directory, shared_at_start(directory / SHARED_AT_START, anchored(cwd)))


def records_newest_first(transcript_path):
    """This session's records, newest first, reading only as far back as the caller consumes.

    Sidechains are a subagent's conversation and never describe this session's context.

    An unparseable line is tolerated in exactly one place: the last line of a file that does
    NOT end in a newline, which is what an append caught mid-write looks like. A trailing
    newline means every record in the file is complete, so a malformed one there is real
    corruption, not a torn write — tolerating it anyway would skip the newest record and fall
    through to an OLDER one with a LOWER usage, reading as a session comfortably under a
    ceiling it has in fact passed. A measurement that fails is recoverable; one that is
    quietly too low is the failure this whole gate exists to prevent. [LAW:no-silent-failure]
    """
    with open(transcript_path, "rb") as handle:
        handle.seek(0, os.SEEK_END)
        end, straddling_head = handle.tell(), b""
        # Only an unterminated file can have a torn last line; a trailing newline means the
        # writer finished every record it started.
        at_tail = False
        if end:
            handle.seek(end - 1)
            at_tail = handle.read(1) != b"\n"
        while end > 0:
            start = max(0, end - TAIL_CHUNK)
            handle.seek(start)
            lines = (handle.read(end - start) + straddling_head).split(b"\n")
            straddling_head = b"" if start == 0 else lines.pop(0)
            for line in reversed(lines):
                if not line.strip():
                    continue
                final_line, at_tail = at_tail, False
                try:
                    record = json.loads(line)
                except ValueError:
                    if final_line:
                        continue
                    raise ValueError(
                        f"{transcript_path}: unparseable record before the final line — the "
                        f"session's context cannot be measured from a corrupt transcript"
                    ) from None
                if not record.get("isSidechain"):
                    yield record
            end = start


def context_tokens(transcript_path):
    """The newest assistant record's usage — the live context as of the last completed turn."""
    for record in records_newest_first(transcript_path):
        if record.get("type") == "assistant":
            usage = record.get("message", {}).get("usage")
            if usage:
                return sum(usage.get(field, 0) for field in PROMPT_COMPONENTS)
    return 0


def verdict_for(tokens, ceiling, headless):
    """The one decision, made once. [LAW:single-enforcer]"""
    if tokens < ceiling:
        return "under"
    return "relaunch" if headless else "close-out"


def close_out_recipe():
    """The close-out an attended session is told to run.

    memento's launcher when it is installed, because that one resets the session in place and
    carries a handoff across the reset; this workspace's own checkpoint skill otherwise, which
    saves the state but leaves ending the session to the operator.
    """
    launcher = MEMENTO_ROOT / "skills" / "message-in-a-bottle" / "bin" / "finalize-session"
    if launcher.is_file():
        return (
            f"{launcher} --reset compact "
            f"'<handoff: what you were doing, where you stopped, the next step>'"
        )
    return (
        "/context-save-lean  (memento is not installed, so this saves the checkpoint "
        "but does not reset the session)"
    )


def main():
    headless = "--headless" in sys.argv[1:]
    hook = json.load(sys.stdin)
    transcript = hook.get("transcript_path")
    # An unmeasurable session exits non-zero so the caller's loud arm records it. Returning a
    # zero would be the worse failure: zero is a legal reading, it resolves to `under`, and
    # the loop would then run on past its ceiling with the ledger showing nothing wrong —
    # indistinguishable from a session genuinely below the line. A missing FILE raises out of
    # records_newest_first for the same reason. [LAW:no-silent-failure]
    if not transcript:
        sys.exit(
            "context_tokens: the Stop payload carries no transcript_path, so this "
            "session's context cannot be measured."
        )
    tokens = context_tokens(transcript)
    ceiling = resolve_ceiling(hook.get("session_id", ""), hook.get("cwd") or os.getcwd())
    verdict = verdict_for(tokens, ceiling, headless)
    print(
        json.dumps(
            {
                "verdict": verdict,
                "tokens": tokens,
                "ceiling": ceiling,
                "close_out": close_out_recipe(),
            }
        )
    )


if __name__ == "__main__":
    main()
