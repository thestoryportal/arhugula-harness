# Leg-brief template — orchestrator → implementer

The transferable core of the 2026-07/08 Fable-orchestrator + Opus-implementer sessions. An implementer (Claude Agent subagent or `codex exec` run) sees ONLY its brief: no conversation context, no operator directives, nothing. If it's not in the brief, it does not exist. Every merged leg this window (#1161–#1182) used this shape.

## Invocation (Codex)

```sh
git worktree add .codex-worktrees/<leg-id> -b <branch> origin/main
codex exec --cd .codex-worktrees/<leg-id> "$(cat .codex/briefs/<leg-id>.md)"
```

Orchestrator profile: gpt-5.6, reasoning high (interactive session). Implementer runs: gpt-5.6-codex, reasoning medium-high. Max 2 concurrent on this machine (Intel i5/16GB). Profiles are user-level (`~/.codex/config.toml`) per Codex policy — the repo `.codex/config.toml` carries only project-scoped settings.

## Brief skeleton

```markdown
You are landing <LEG NAME> in the arhugula-v2 workspace. You are in an isolated
worktree. Produce a reviewable PR — NEVER merge. Do NOT touch .harness/roadmap_status.md.

## The decision/ratification driving this leg
<Operator words verbatim-in-substance, incl. WHICH alternatives were rejected and how
they were presented. The implementer must not re-widen or re-litigate a settled choice.>

## Your authority — READ FIRST, IN FULL
<Numbered list: fork doc / spec head at exact version / register row / plan unit.
State which artifact WINS on conflict. Name the disciplines that bind: no C-* minting,
byte-exact cites at YOUR head, programmatic recounts each round, PD-9 soundness exit,
PRESERVED-VERBATIM clauses for untouched neighbors.>

## Deliverables
<Numbered, each independently checkable. Spec deltas name their amendment SITES.
Register touches say REPLACED-not-appended. Always include: clearance marker,
CLAUDE.md head-pointer bump, lineage append, check tools
(forward_register/arc_ledger/substitution_ledger --check, just overlay-check,
codex_context_guard check, ruff), then out-of-family review to convergence.>

## Process
- Branch <name> off current origin/main. NEVER `git add -A` — stage explicit paths.
- Commit footer: <attribution + session link>.
- Push + open PR (body: decision verbatim, sites, remainder owed). Do NOT merge.
- Bad output looks like: <3–5 negative examples SPECIFIC to this leg — relocating
  spec prose instead of citing; paraphrasing a ratification broader than the
  operator's selection; count claims drifting between rounds; a witness that
  passes with the fix reverted>.

## Report back
<Exact fields: sites-as-landed quoted; X-yes/no + why; remainder recorded;
check-tool results; review rounds; PR number; deviations.>
```

## Orchestrator obligations around a brief

1. **Ground before writing** — verify at HEAD every cite the brief hands over; a brief inherits your errors at full fidelity.
2. **Read the artifact, not the report** — validate the leg's diff against the brief's deliverables yourself; implementer self-assessments over-claim.
3. **Gate before merge** — three lenses (see `merge-gate-lenses/README.md`); scoped re-gate on any post-approval fix commit, empirical not formal.
4. **Merge sequence** — gate-log row commit → merge → terminating refresh as the IMMEDIATE next commit (`tools/roadmap_status_refresh.py --refresh --pr N --date D --notes "..."` then `--check`) → worktree removal.
5. **Honest disposition beats shipping** — a premise falsified at the gate becomes a premise-falsified close with a reopening trigger, not a rework-to-save-the-arc.
