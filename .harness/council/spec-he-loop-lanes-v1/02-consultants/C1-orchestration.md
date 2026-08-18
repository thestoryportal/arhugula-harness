# E1 A2 — C1 orchestration (consultant, reacting to C9/C10/C7)

## Scoping ruling on C9-F1

**OUT of v1 scope — but the spec states this only implicitly (§10), not in the binding clause.** Verified: spec §0.1 enumerates only `.claude/` carriers; no `.agents/` path in §5; §10 excludes the Codex-projection tree but as a *drift-class* exclusion, not a live-enforcement-gap exclusion. `.agents/skills/two-lane/SKILL.md` defines a lane as one `codex exec --profile arhugula-implementer` leg, cap 2 (`AGENTS.md:32`: "Cap concurrent implementer runs at 2 on the reference machine (Intel i5/16GB)") — governance under `AGENTS.md`'s Orchestrator + Implementer Pattern, a different authority than ADR-HE-1..4. `permission-guard.sh` is a Claude Code `PreToolUse` hook, architecturally incapable of fencing a `codex exec` subprocess. `.agents/skills/ship-pr/SKILL.md:96` issues `gh pr merge` directly, no lease reference.

**Why OUT despite D-A "full scope":** D-A governs depth across Parts A–D, not carrier breadth; no corpus artifact mentions Codex-exec lanes — a surface discovered at spec review, not scoped text. Folding it in would also require a Claude-authored spec to mandate edits into `.agents/` (cross-runner posture violation, `[[agents-md-is-the-codex-projection-not-claude-side]]`). Name the gap explicitly and register it forward.

**Required fix (both halves):**
1. C-HE-01 §1 sentence: "This contract's carrier surface is `.claude/skills/{two-lane,ship-pr,merge-gate,roadmap-continue}` and the shared `tools/`/`tools/hooks/*` primitives they invoke (§0.1). Codex-exec-driven lanes (`.agents/skills/two-lane/SKILL.md`, `codex exec --profile arhugula-implementer`) are a distinct carrier governed by `AGENTS.md`'s Orchestrator + Implementer Pattern (concurrency cap 2) and are OUT of scope for C-HE-06/07 merge-door enforcement in v1: `permission-guard.sh` has no jurisdiction over a `codex exec` process, and `tools/merge_door.py`/`safe-merge.sh` are not wired into `.agents/skills/ship-pr/SKILL.md:96`. If an operator runs a Claude-driven lane and a Codex-driven lane concurrently, C-HE-01 §3's 'exactly one merge door' invariant does NOT hold — a known, named residual."
2. §11 new row: "Cross-carrier merge-door fencing (Claude lane + Codex-exec lane concurrently can both reach `gh pr merge`) | forward register, joint Claude/Codex arc | not in v1 — requires a Codex-side hook-equivalent or rewiring `.agents/skills/ship-pr/SKILL.md:96` to `tools/hooks/safe-merge.sh` under Codex posture."

N=4 dial (C-HE-01 §2) and the `AGENTS.md:32` cap-of-2 govern two disjoint pools under two authorities; additive only as reference-machine resource pressure (worktrees, CPU, Docker ports) — one line in C-HE-11, not a correctness gap.

## Reactions to primaries

| primary | reaction | evidence | resulting fix |
|---|---|---|---|
| C9-F1 | REFINE | cap-of-2 traces to `AGENTS.md:32`, a different governance surface; `.agents/` is the Codex projection | Two-part fix above rather than either/or |
| C9 self-check | ACCEPT | — | Ruling rendered under C1 authority |
| C9-T4 | REFINE | C-HE-06 §8 conflates yield/hand-off shape with retry numbers | Add: "acquire-fail MUST yield control to the caller's next natural gate-pass event (a control-flow return, not a sleep-and-retry inside the acquire call)" before the numeric clause; C9's primitive-side rate limit is the companion, not a substitute |
| C7-T10 | TENSION | §6 gives S2 no hand-off contract to S3/S4a/S4d/S5/S6 | Add §6 row: "S2 hand-off contract: consumers MUST treat S2-GREEN as schema-present only; each consumer performs its own semantic-resolution check (arc_type join, phase-span location, concurrent_lanes key shape) before relying on the field" |
| C10-T1 | ACCEPT (topology) | `:184-198`, `:288-290` verified | Chokepoint is process-scoped (Claude hook) — the residual routed forward |

## Own findings

| id | class | contract | quote | defect | fix |
|---|---|---|---|---|---|
| C1-F1 | 2 | C-HE-01 §1/§3 | "Lanes MUST... land through exactly one merge door" | "Lanes" unqualified by carrier; invariant depends on reaching §10 | Carrier-scoping sentence in C-HE-01 §1 |
| C1-F2 | 2 | §6 S2 row | "S2 … Gates measurement: yes" | No hand-off contract to four downstream steps | S2 hand-off row |
| C1-F3 | 3 | C-HE-11 §1 | "`k` derived from `HARNESS_LANE_INDEX` set at lane init" | A Codex-exec leg has no `HARNESS_LANE_INDEX`; port collision residual | Note in C-HE-11 / same forward row |
| C1-F4 | 3 | C-HE-06 §8 | "arbitration never moves into it" | Two orthogonal commitments (yield shape, retry numbers) in one paragraph | Split §8 into two sentences |

## Position on T4 / T10 / T1

T4 RECONCILE(wording): C9's primitive rate limit + C1's yield-point sentence, both. T10 ACCEPT the DAG; RECONCILE via the S2 hand-off row. T1 ACCEPT as topology (single allowlisted chokepoint, reuse of the worktree-removal precedent); the process-scope boundary is the routed residual.

## Verified at HEAD

Spec §0.1, §5, §10, §11, C-HE-01, C-HE-06 §8, §6 S2 row · `.agents/skills/ship-pr/SKILL.md:96` literal merge, 0 matches for `merge_door|safe-merge|lease|acquire` · `.claude/skills/ship-pr/SKILL.md` no literal `gh pr merge --match-head-commit` line · `AGENTS.md:20-35` pattern section; cap at `:32` (cited `:31`, same block) · `permission-guard.sh:314-340`, `:427` bare `gh pr merge` allowed today.

## Voice self-check

Co-primary scan run: C9/C10 deferred scope to C1; no boundary leakage into Codex-side hook mechanics (cross-runner infra, routed forward), retry numbers (C9), or record semantics (C7).
