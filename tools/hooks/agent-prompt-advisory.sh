#!/usr/bin/env bash
# Subagent-prompt authoring advisory (U-SR-03, charter WR-08b). PreToolUse on the Agent
# tool: inject ONE advisory line so every fan-out is authored under laws:prompt.
#
# ADVISORY ONLY -- never denies. This hook emits `additionalContext` and nothing else, so it
# structurally cannot refuse an Agent call: a deny here would break the very delegate the
# rule asks you to spawn (charter WR-08: "advisory-inject, never deny"). The absence of any
# `permissionDecision` key is the mechanism, not a policy someone has to remember.
#
# Uncapped by design. `capture-failure.sh` caps its nudge because that one is a multi-line
# memory-candidate block observed re-emitting ~20x in a single session (U-CTX-07); this is
# one line whose whole purpose is coverage of EVERY Agent call. The passive memory it
# replaces (`feedback-subagent-prompts-are-laws-prompt-medium`) failed twice in 48h by being
# present but un-rehearsed, which is what a cap would reintroduce.
#
# Trigger: PreToolUse matcher "Agent". Test: tools/hooks/test_agent_prompt_advisory.sh.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PAYLOAD=$(hook_read_stdin)

# The settings matcher already scopes this to the Agent tool; re-reading `tool_name` makes
# the hook total over any payload it is handed, so a mis-wired matcher yields silence rather
# than an advisory on every Bash call.
[ "$(hook_json "$PAYLOAD" '.tool_name')" = "Agent" ] || exit 0

hook_emit "PreToolUse" \
  "[agent-prompt-advisory] A subagent sees ONLY this prompt — no transcript, no CLAUDE.md, no user requirements unless you wrote them in. Author it through a delegated laws:prompt agent; authoring inline is legal only when instantiating a skill-canonical template with literal values (merge-gate / fan-out / council-workflow each carry the rule)."
