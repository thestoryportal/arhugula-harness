---
name: optimize-claude-md
description: Review the workspace CLAUDE.md governance files for optimization (clarity, staleness, contradiction, byte-cap pressure) using the two decorrelated reviewers (out-of-family Codex + transcript-aware advisor) and propose the result as a REVIEWABLE PR — never a silent in-place edit. Use when the operator says "/optimize-claude-md", "tidy CLAUDE.md", "the instructions have drifted", or on a periodic cadence (~every N PRs / SessionEnd). Self-improvement of the agent's own governance docs (U-HK-20). Do NOT use to edit design-substrate, specs, or plans — those are out of scope by hard rule.
---

# optimize-claude-md — self-improving governance docs (U-HK-20)

The agent reviewing and improving its own instruction files. Because the failure mode of
a self-editing agent is *silent governance drift*, this skill has two hard invariants and
will not run without them.

## Two hard invariants (enforced, not advisory)

1. **PR-only — never a silent in-place edit.** Every change lands as a reviewable diff on
   a feature branch + PR. CI (X-AL-3 guard) and human/Codex review are the regression
   catch. If you find yourself about to `Edit` a CLAUDE.md and commit straight to the
   working branch the operator is on, STOP — that is the exact anti-pattern this skill
   exists to prevent.
2. **Scope = CLAUDE.md governance files ONLY. NEVER `design-substrate/**`.** In scope:
   the root `CLAUDE.md`, the axis-subdirectory `harness-{is,as,cp,od}/CLAUDE.md`, and
   `MEMORY.md` index hygiene. **Out of scope, hard rule:** anything under
   `design-substrate/**` (that is the X-AL-3 line — editing a spec/plan/ADR here would be
   silent H_T design extension), per-axis specs, plans, fork docs. Root CLAUDE.md is
   mode-agnostic (§11) and safe to target; the axis CLAUDE.md files are scope pointers,
   also safe. If a proposed optimization would require touching design-substrate, it is
   NOT this skill's job — route it to the proper design-phase arc (§4.3) and drop it.

## What "optimization" means here

Look for, in priority order:
- **Staleness / contradiction** — a cite that no longer resolves (verify byte-exact per
  §10.4 before flagging), a version pointer behind canonical HEAD (`[[design-substrate-version-identity-hazards]]`), a `[[pattern]]` that has been retired, two sections that now disagree.
- **Byte-cap pressure** — `MEMORY.md` is capped at 24,400 bytes (it has overflowed before).
  Index lines over ~200 chars, superseded entries still present, detail that belongs in a
  topic file. Compact descriptions; never drop provenance (it lives in git).
- **Clarity / redundancy** — a rule stated three times, a §section that could be tighter,
  a convention that drifted from how the workspace actually operates.

Do NOT "optimize" by deleting load-bearing discipline (the X-AL-3 triad, the §12 roadmap
protocol, the paid-call/secret boundary). Tightening wording is fine; removing a guardrail
is not. When unsure whether something is load-bearing, keep it and flag the question.

## The flow

```bash
source tools/hooks/lib.sh   # hook_project_dir, conventions
```

1. **Pick the target file(s)** — default the root `CLAUDE.md`; the operator may name one.
   Confirm the path is in scope (NOT under `design-substrate/`).
2. **Branch.** `git checkout -b optimize-claude-md-<date>` off the default branch (never
   edit the operator's working branch directly).
3. **Two decorrelated reviews of the current file:**
   - **Codex** (out-of-family, $0): `just codex-review-uncommitted` after staging a draft,
     or frame the file + your proposed deltas to `resolve_codex` — fresh eyes on the
     artifact, no transcript.
   - **advisor()** (transcript-aware): does the proposed delta drop a guardrail / contradict
     a committed surface this session established? It sees what Codex cannot.
   - Apply only deltas BOTH reviewers (or the operator) accept. A disagreement is a signal —
     surface it, take the more-conservative (keep-the-guardrail) option.
4. **Diff discipline.** Keep the PR small and legible — one theme per PR (staleness, OR
   byte-cap, OR clarity), not a sweeping rewrite. A 400-line CLAUDE.md rewrite is
   un-reviewable and defeats invariant 1.
5. **PR.** Open it with a body that lists each delta + its rationale + which reviewer
   flagged it. Label `roadmap-design-extension` if it adds a new R-NNN-worthy convention;
   otherwise it is mode-agnostic process-substrate. The X-AL-3 CI guard passes trivially
   (no `design-substrate/**` touched).
6. **Stop.** Do not merge it yourself unless the operator authorizes; the review is the point.

## Cadence

Manual (`/optimize-claude-md`) or periodic (~every 10–15 PRs, operator-tunable). Not every
session — governance docs should be stable; churning them is its own drift. Run it when the
operator notices friction or after a wave of substantive convention changes has accumulated.

## Notes

- This skill **proposes**; the operator + reviewers **dispose**. It never silently rewrites
  the rules the agent runs under.
- Division of labor mirrors §13.1: Codex = out-of-family artifact read; advisor = transcript-aware guardrail check. `[[hooks-codex-pilots-decorrelation-validated]]`.
