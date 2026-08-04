---
name: red-first
description: Use only when the operator explicitly asks for a red-first unit — an adversary session writes failing, probe-annotated tests from the acceptance criteria before any implementation, and an implementer session drives them green without editing them.
---

# Canonical Claude Workflow Bridge

Read `.claude/skills/red-first/SKILL.md` completely from the workspace root before acting, including every reference it routes for the task. That canonical skill body is the full workflow and the source of truth for the roles, the sha256 handoff fence, the `# mutation-probe: <file>:<lines>` annotation format, the completion gate and the fail-closed `RED-FIRST:` verdict lines; this Codex entrypoint does not summarize, trim, or replace it. Resolve its relative references from the canonical skill directory.

Apply these runner translations only:

- Root `AGENTS.md` is the Codex instruction entrypoint; targeted `CLAUDE.md` sections remain canonical lineage.
- The canonical Adversary phase's "plain Agent-tool subagent" means a fresh, separate `codex exec` session with a self-contained brief, subject to current delegation policy. It is never the session that will implement the unit, and — as the canonical body states — never the `harness-adversarial-reviewer` skill, which reviews completed artifacts and does not author tests.
- The canonical Implementer phase runs in its own separate session, so the handoff digest is recorded and re-compared across a real session boundary rather than inside one context.
- Run the completion gate's probe as `just mutation-probe --file F --lines A-B --test "<that test's node-specific command>"`, once per annotation. Use the annotation's own node-specific command and never a file-level one: the probe accepts any test failure in the command it is given, so a file-level run clears on a sibling test's red while the annotated test stays green.
- The canonical red-evidence requirement is satisfied by the verbatim failing output in the PR body; no separate Codex-side red ledger is written, since `codex_loop.py` already keeps one.
- Invocation stays operator-request-only: never chain this skill automatically from roadmap-continue or ship-pr. All Git, CI, worktree, paid-call, secret, and destructive-action guardrails remain binding.
