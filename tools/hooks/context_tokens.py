#!/usr/bin/env python3
"""Where this session's context sits against its ceiling, as one decided verdict.

The loop's Stop hook (`stop-loop.sh`) continues a turn by blocking the stop, and a block
sets `stop_hook_active` on the next Stop. memento's own ceiling hook reaches its
`stop_hook_active` branch only once a session is ALREADY over the ceiling, and what it does
there is declare its one forced close-out attempt spent and allow the stop
(`memento/hooks/scripts/context-ceiling.py:220-225`, upstream `promptctl/memento` @0d1f5bc) —
even for a loop session it never actually blocked. So in loop mode the ceiling has no
enforcer unless the loop hook is one. This is that enforcer's measuring half: it reads the
transcript, resolves the ceiling, and hands back one verdict for the shell to dispatch on.
[LAW:parse-dont-validate] the verdict is the stamp — `stop-loop.sh` reads it and re-derives
none of it, so there is nothing left downstream to re-check.

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

import importlib.util
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
# Claude Code's own record of what is installed where. An install path carries a VERSION
# segment the plugin name does not name — `.../cache/memento/memento/<version>`, 0.7.0 at the
# install this was written against — so it cannot be
# spelled out as a constant, and an earlier revision that did spell one out resolved to a
# directory of version directories: `lib/ceiling_config.py` was not under it, memento read as
# absent, and installing the plugin changed nothing at all. [LAW:one-source-of-truth] the
# manifest is where that path is decided, so it is read rather than reconstructed.
PLUGIN_MANIFEST = Path(
    os.environ.get("HARNESS_PLUGIN_MANIFEST")
    or Path.home() / ".claude" / "plugins" / "installed_plugins.json"
)
PLUGIN_KEY = "memento@memento"
# The settings files that decide whether Claude Code ACTIVATES a plugin here. The manifest
# above says what is installed on the machine and where; it does not say what runs in this
# project, and the two genuinely differ — an install recorded against another workspace is
# still in the shared cache, still has a standing `installPath`, and is still not enabled
# here. `enabledPlugins` is the key that decides, which is what `claude plugin list` reports
# as `Status: enabled` (probed 2026-09-19 against this project's own install).
ENABLEMENT_FILES = (
    Path(".claude") / "settings.local.json",
    Path(".claude") / "settings.json",
)
USER_SETTINGS = Path.home() / ".claude" / "settings.json"
ENABLEMENT_KEY = "enabledPlugins"


def enabled_here(project_dir):
    """Whether memento is enabled for this project, as a tri-state: True, False, or None
    when no settings file mentions it at all.

    The precedence is the one Claude Code actually implements, probed rather than assumed
    (2026-09-19, `claude plugin list` under a synthetic HOME with deliberately disagreeing
    layers): the FIRST layer that mentions the plugin decides, in the order local, project,
    user. The CLI states the rule itself when the layers disagree — "Disabled in
    ~/.claude/settings.json but still loads — project settings enable it, which overrides
    your user setting" — and a local `false` over a project `true` reports disabled.

    An earlier revision of this function ducked the question with `all(states)`: any explicit
    false disabled, on the reasoning that an unprobed order is a guess and the conservative
    direction is the recoverable one. It is the wrong trade. A user-level `false` left behind
    from some other project would have read as disabled HERE, where Claude Code loads the
    plugin — the hook would enforce the default ceiling and offer the fallback close-out for
    a session that genuinely has memento. Conservative in the wrong direction is still wrong,
    and the interface was there to be run the whole time. (codex, pass 2)

    A settings file that does not parse is left to raise, for the same reason the manifest is:
    a hook that cannot read its own configuration must say so rather than pick a number.
    [LAW:no-silent-failure]
    """
    project = Path(project_dir)
    for path in (*(project / name for name in ENABLEMENT_FILES), USER_SETTINGS):
        if not path.is_file():
            continue
        enabled = json.loads(path.read_text()).get(ENABLEMENT_KEY) or {}
        if PLUGIN_KEY in enabled:
            return bool(enabled[PLUGIN_KEY])
    return None


def applies_here(record, project_dir):
    """Whether Claude Code would apply this install record to this project.

    Enablement (above) is a global yes/no for the session; this is per RECORD. The manifest
    carries one record per install, so an upgrade made from another workspace sits beside
    this project's own with a newer `installedAt` and a different version's `installPath`.
    Taking the newest unconditionally would hand this session another workspace's version.

    A `user`-scope record applies everywhere. Otherwise the record's `projectPath` must be
    this project or an ancestor of it. That test is deliberately used to PREFER a record and
    never to reject the set: this repo's lanes run at sibling paths (`~/Projects/lane-1`),
    so a lane matches no record at all, and rejecting on that basis would read as
    "not installed" in every lane — the failure this whole arc exists to remove.
    """
    if record.get("scope") == "user":
        return True
    recorded = record.get("projectPath")
    if not recorded:
        return False
    here = Path(project_dir).resolve()
    recorded = Path(recorded).resolve()
    return recorded == here or recorded in here.parents


def memento_root(project_dir):
    """Where memento is installed AND enabled for this project, or None. Absence is a legal
    domain value.

    Two questions, and they are not the same one. The manifest answers *where on this machine*
    — it is global, and it carries a record per install, including installs made from other
    workspaces whose files sit in the same shared cache. `enabled_here` answers *whether this
    project runs it*. An earlier revision asked only the first, so a memento installed for
    some other repo would have supplied this project's ceiling layers and close-out launcher
    although Claude Code would never activate it here.

    `enabled_here` answers the first; `applies_here` narrows the second. The record's own
    `projectPath` cannot be the whole discriminator — it names where the install was made
    FROM, and this repo's lanes run at sibling paths (`~/Projects/lane-1`, not a child of
    `~/Projects/arhugula-v2`), so a path test used as a FILTER would read as "not installed"
    in every lane. Used as a PREFERENCE over the standing set it is right in both places: the
    main checkout takes its own record's version, and a lane, matching none, falls back to the
    newest install that stands rather than to nothing. The lane's fallback can still reach
    another workspace's version; that residual is named at B-303 (5) rather than papered over.

    MEMENTO_ROOT wins over both, which is how the suite points at a fixture instead of the
    operator's real install — and is also why the asserts in section 10 of `test_stop_loop.sh`
    pin it, and why the discovery path below is the one a real session takes and the one a
    pinned test can never exercise. It gets its own section there.

    A manifest that is absent means no plugin is installed; a manifest that is present and
    does not parse is a genuine failure and is left to raise, where `stop-loop.sh`'s loud arm
    records the session as unmeasured rather than as comfortably under a ceiling.
    [LAW:no-silent-failure] Records are taken newest-installed first, and the first one whose
    directory actually holds the module is the answer — a recorded path that no longer stands
    (an uninstall, a pruned cache) is not an error, it is simply not memento.
    """
    override = os.environ.get("MEMENTO_ROOT")
    if override:
        return Path(override)
    if not PLUGIN_MANIFEST.is_file() or enabled_here(project_dir) is not True:
        return None
    records = json.loads(PLUGIN_MANIFEST.read_text()).get("plugins", {}).get(PLUGIN_KEY) or []
    newest_first = sorted(records, key=lambda one: one.get("installedAt", ""), reverse=True)
    standing = [
        one
        for one in newest_first
        if one.get("installPath")
        and (Path(one["installPath"]) / "lib" / "ceiling_config.py").is_file()
    ]
    bound = [one for one in standing if applies_here(one, project_dir)]
    chosen = bound or standing
    return Path(chosen[0]["installPath"]) if chosen else None


def resolve_ceiling(root, session_id, cwd):
    """The ceiling in force, from memento's layers when memento is installed.

    [LAW:one-source-of-truth] memento owns this number wherever it exists — the operator can
    move it per-session or per-project with `ceiling`, and a copy kept here would be a second
    clock that disagrees the first time they do. Absence of the plugin is a legal domain
    value, not a failure, so it resolves to the default; an import that exists and *raises*
    is a genuine failure and is left to surface. [LAW:no-silent-failure]

    `shared_unrecorded` rather than `shared_at_start`, because the two differ in exactly one
    thing: the second WRITES the session's record of what the shared layers resolved to.
    memento's Stop hook owns that write — "one writer, which is what keeps two files in one
    directory from being two clocks" (`ceiling_config.py:294-305`) — and a reader that only
    wants the number takes the value the record would have held. Both return the same
    resolved ceiling, so nothing about the verdict changes; what changes is that this hook
    stops being a second author of a file upstream says has one.

    Loaded from its path and never entered into `sys.modules`. The earlier
    `sys.path.insert` + `import ceiling_config` cached the module under its NAME, which was
    harmless while the path was a frozen constant and stopped being harmless the moment
    `memento_root` made it vary: a second call in one process with a different root would
    silently be served the first root's module, with no error. Binding the module to the
    file it came from removes the alias rather than documenting it, and drops the
    `sys.path` mutation with it.
    """
    config = (root / "lib" / "ceiling_config.py") if root else None
    if not config or not config.is_file():
        return DEFAULT_CEILING
    spec = importlib.util.spec_from_file_location("memento_ceiling_config", config)
    ceiling_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling_config)

    directory = ceiling_config.session_directory(session_id)
    shared = ceiling_config.shared_unrecorded(
        directory / ceiling_config.SHARED_AT_START, ceiling_config.anchored(cwd)
    )
    return ceiling_config.in_force(directory, shared)


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


def close_out_recipe(root):
    """The close-out an attended session is told to run.

    memento's launcher when it is installed, because that one resets the session in place and
    carries a handoff across the reset; this workspace's own checkpoint skill otherwise, which
    saves the state but leaves ending the session to the operator.
    """
    launcher = (
        (root / "skills" / "message-in-a-bottle" / "bin" / "finalize-session") if root else None
    )
    if launcher and launcher.is_file():
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
    cwd = hook.get("cwd") or os.getcwd()
    root = memento_root(cwd)
    ceiling = resolve_ceiling(root, hook.get("session_id", ""), cwd)
    verdict = verdict_for(tokens, ceiling, headless)
    print(
        json.dumps(
            {
                "verdict": verdict,
                "tokens": tokens,
                "ceiling": ceiling,
                "close_out": close_out_recipe(root),
            }
        )
    )


if __name__ == "__main__":
    main()
