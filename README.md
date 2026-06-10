# H_T — Multi-LLM Agent Harness Target Build

The target harness (**H_T**) — a multi-LLM agent harness — built across four
design axes (IS / AS / CP / OD) plus a cross-axis composition surface (CXA).

## Execution surface

**H_E** = Claude Code CLI. During Phase 7 sub-phase 7a, H_E provides bounded
substitutions for not-yet-built H_T primitives. The H_E ↔ H_T substrate
boundary lives at the MCP server process (X-AL-1).

## Workspace pointers

- `./CLAUDE.md` — workspace-level Claude Code guidance + canonical artifact pointers.
- `./Phase_7_Session_1_Entry_Directive_v1.md` — Phase 7 Session 1 entry context.
- `./Sub_Agent_Boundary_Specification_v1.md` — sub-agent topology + scope boundaries.
- `./design-substrate/` — canonical design-phase artifacts (locally co-resident).
- `./.harness/` — roadmap, fork, retirement, audit, and historical archive surfaces.

## Design-phase substrate

The canonical design substrate — ADRs (F1–F5, D1–D6), ADD v1.3, PRD v1.1,
per-axis specs v1.x, per-axis plans v2.x, CXA v2.1, Workflow v1.8,
Meta-Architecture v1 — resides in `./design-substrate/`. (Originally a separate
design-phase Claude.ai project; transferred local per
`Phase_7_Workspace_Design_Substrate_Manifest_v1.md` because Claude Code CLI
cannot reach the design-phase knowledge base.)

Historical root review/tension/scaffolding artifacts are archived at
`.harness/archive/root-historical/`; active governance entrypoints remain at the
repository root.

## Repo layout

A `uv` workspace with 6 members: `harness-core/` (shared types) plus the four
axes `harness-{is,as,cp,od}/` and `harness-cxa/` (cross-axis composition).

## Opening a Phase 7 session

```
cd <workspace_root>
claude
```

Then load `./Phase_7_Session_1_Entry_Directive_v1.md` and follow its §4.5
first-action sequence.

## Status

Workspace operational under DP-4 separate-workspace discipline. Phase 7
sub-phase 7a (Bootstrap) entry authorized per the Entry Directive §3.
