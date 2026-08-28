# Witness — PreToolUse honors `hookSpecificOutput.additionalContext` on this runtime

**Recorded 2026-08-28, U-SR-03 (charter WR-08b), at branch `feat/he-lanes-u-sr-03`.**

This file exists because the claim it records was disputed twice by out-of-family review
(codex u-sr-03 r1 and r5), each time on the premise that "the repository's hook contract
permits only `permissionDecision` / `permissionDecisionReason` / `updatedInput` for
PreToolUse," and therefore that `tools/hooks/agent-prompt-advisory.sh` is a runtime no-op and
WR-08b is unmet. The premise is checkable and the conclusion is falsifiable; both were
checked, and the record is kept here so the next reader meets the evidence rather than
re-deriving the doubt.

## The premise: no such contract exists in this repository

`permissionDecision` appears in exactly five tracked files, none of which is a field
specification for the event:

    tools/hooks/permission-guard.sh          - emits it (the guard's own decision path)
    tools/hooks/test_permission_guard.sh     - asserts the guard's output
    tools/hooks/test_skill_reservation_wiring.sh
    tools/hooks/agent-prompt-advisory.sh     - this arc, in a comment
    tools/hooks/test_agent_prompt_advisory.sh - this arc, asserting the key is ABSENT

`.codex/hooks/README.md` tabulates which EVENTS each runner wires, not which fields each
event honors. So the repository pins no PreToolUse field contract, and the reviewer's premise
is an inference from the guard's usage — a reasonable prior, but not a repository fact, and
not evidence about runtime behavior.

## The observation: the advisory reached the model, verbatim

One `Agent` call was made from a session with this hook wired at `PreToolUse` matcher
`Agent`. The advisory was injected into the orchestrator's context and appeared as:

    PreToolUse:Agent hook additional context: [agent-prompt-advisory] A subagent sees ONLY
    this prompt — no transcript, no CLAUDE.md, no user requirements unless you wrote them in.
    Author it through a delegated laws:prompt agent; authoring inline is legal only when
    instantiating a skill-canonical template with literal values (merge-gate / fan-out /
    council-workflow each carry the rule).

That single observation establishes three things at once, each of which had been in question:
PreToolUse honors `additionalContext` on this runtime; `Agent` is a valid matcher for the
Agent tool (the docs' matcher examples are explicitly non-exhaustive, and they filter on tool
NAME); and the hook configuration is picked up without a session restart. The probe agent
also returned normally, so the advisory did not interfere with the call it rode on.

## What the automated test does and does not prove

`tools/hooks/test_agent_prompt_advisory.sh` drives the hook as a child process and asserts
its emission: the event name, the advisory text, its single-line shape, the absence of any
decision-bearing key, and that it fires on every Agent call. It CANNOT assert that the host
honors the field — no shell test can, because the honoring happens in the runtime that
invokes the hook, not in the hook. That gap is real, it is the reviewer's valid half, and
this file is the instrument that closes it: a recorded observation, not an inference.

## Standing disposition

The behavioral claim ("the advisory never reaches the model") is **refuted by direct
observation** and is held refuted. The scope observation ("the test proves emission, not
honoring") is **accepted** and is answered by this record plus the limit now stated in the
test body.

If a future runtime change makes this stale, the check is one Agent call: the advisory line
either appears in the turn's context or it does not. Re-run it before removing the hook.
