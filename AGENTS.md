# AGENTS.md — Codex Compatibility Layer

This repository is developed primarily with Claude Code CLI. For Codex, this file is the authoritative compact projection of the project rules. The canonical governance remains in `CLAUDE.md`; load it only for targeted sections or exact lineage, not as default context.

## Startup Context

- Read `CONTEXT.md` (workspace root) first — the compact task router; it names the operative posture and that posture's entry points, and points back into `CLAUDE.md` for full governance.
- `CLAUDE.md` keeps every `§N.M` heading but its reference bodies live in governance packs — load a pack only when its rule fires, never preload the directory. Roster + load matrix: `docs/governance/README.md`. Packs: `docs/governance/project-framing.md` (§1.1, §7, §9, §9.1) · `docs/governance/stack-and-layout.md` (§3.3) · `docs/governance/substitution-and-clearance.md` (§4.1, §4.2, §4.5) · `docs/governance/skills-and-subphases.md` (§6, §7) · `docs/governance/design-phase-principles.md` (§10.x, design-phase posture only) · `docs/governance/roadmap-protocol.md` (§12.1–§12.3, §12.5.x) · `docs/governance/orchestration.md` (§13.2–§13.5). The safety kernel (§1.3, §3.1/§3.2, §4.3/§4.4, §5, §8, §11, §12.2.1, §12.4.1, §13.1, §14) stays in root verbatim. Artifact-head lineage is at `.harness/artifact-pointers/` — query with `rg`, never read wholesale.
- Read `.harness/roadmap_status.md`, `justfile`, `.codex/notes/codex-compatibility-outline.md`, and the relevant local `AGENTS.md` before substantive work.
- Read `.codex/notes/discipline-digest.md` — the runner-agnostic distillation of Claude-side memory disciplines (verification shapes, review-loop hygiene, repo git/CI mechanics). These bind Codex sessions identically.
- Read `.codex/notes/claude-codex-parity.md` when auditing runner parity, hook trust, permissions, reviewer routing, or skill discovery.
- If resuming in-flight work, check `.harness/handoff/README-resume.md` first — repo-committed cross-runner handoff state (in-flight branches, ratifications, fold instructions).
- For task-relevant historical lessons, query the Claude memory index at `~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/MEMORY.md`, then read only the linked topic files needed for the task. Treat gstack checkpoints under `~/.gstack/projects/arhugula-v2/checkpoints/` as additional resume evidence. Both are advisory until verified against HEAD, the handoff, and live repo instruments.
- Read `.codex/notes/deterministic-context-workflow.md` and run `just codex-preflight` before substantive work. This writes the required local context checkpoint.
- For axis-specific work, read the closest `harness-{is,as,cp,od}/AGENTS.md` first; consult the matching `CLAUDE.md` only when exact Claude lineage or axis posture is needed.
- For `C-*`, `U-*`, `H_T-*`, ADR, or CXA seam claims, ground with `just overlay-query` (the semantic overlay) instead of free-form recall.

## Working Pattern

- Use isolated worktrees for substantive edits. Prefer external or ignored worktree directories; `.codex-worktrees/` is ignored for operator-created local worktrees.
- Do not edit `design-substrate/**`, specs, plans, ADRs, or fork docs in the same arc as implementation files unless the task is explicitly a design-phase/back-flow arc.
- Do not run paid provider calls, credential-moving commands, destructive git commands, or network-dependent actions without explicit operator authorization.
- For credential-gated units, build to the exact credential boundary, prove all non-credential forward actions are closed, then log the gate with `just codex-credential-gate --unit ... --gate ... --forward-closed ... --resume ...` if no HIL/operator-approval surface is available. Update a human-facing tracking surface so the pending gate is visible on the next human engagement, then proceed to the next implementable unit.
- Preserve user work. Do not revert unrelated changes.
- Re-run `just codex-preflight` after long work, merges, rebases, resumes, or compaction; memory/checkpoints are advisory until re-grounded against HEAD. Use `just codex-checkpoint <label>` for explicit mid-arc context checkpoints.
- For autonomous coding arcs, initialize the controller/coder/validator/GitHub-shipping evidence loop with `just codex-autonomous-arc <arc-id>`, record gates with `just codex-loop-record ...`, and require `just codex-loop-check` before claiming the loop complete. Gate evidence is branch/HEAD/linked-worktree/worktree-fingerprint-bound; after a pre-commit diff change, re-record the affected gate and downstream pre-commit gates. The full loop is not complete until commit, push, PR, CI, merge, post-merge refresh or explicit non-applicability, local main sync, and worktree disposition are recorded; final disposition must prove the original arc worktree is no longer registered and the local topic branch is pruned.

## Orchestrator + Implementer Pattern

- For multi-leg arcs, mirror the Claude Fable 5 orchestrator/Opus 5 implementer shape: ONE interactive `gpt-5.6-sol` orchestrator session (high reasoning, `--profile arhugula-forward`) plans, writes leg briefs, gates, merges, refreshes; `gpt-5.6-terra` implementer legs run as non-interactive `codex exec --profile arhugula-implementer` processes in isolated worktrees (`.codex-worktrees/<leg-id>`), one brief per leg.
- Briefs follow `.codex/notes/leg-brief-template.md` — a leg sees ONLY its brief; put the operator decision verbatim, the authority list, deliverables, negative examples, and the report-back shape in it.
- Cap concurrent implementer runs at 2 on the reference machine (Intel i5/16GB). The orchestrator reads each leg's DIFF, not its self-report, before gating.
- Model tiering lives in user-level profile overlays: `~/.codex/arhugula-forward.config.toml` pins the Fable 5-equivalent controller to `gpt-5.6-sol`/high, and `~/.codex/arhugula-implementer.config.toml` pins the Opus 5-equivalent implementer to `gpt-5.6-terra`/high. The tracked templates live under `.codex/notes/`; this repo's `.codex/config.toml` stays project-scoped by Codex policy.

## Claude-Native Context Mapping

- Claude `CLAUDE.md` files map to Codex `AGENTS.md` projections.
- Claude hooks map to `.codex/hooks.json` plus scripts under `.codex/hooks/`.
- Claude skills map to Codex repo/user skills under `.agents/skills` or installed Codex skills; package as plugins only when distribution is needed.
- Claude memory remains a queryable historical source rather than being discarded during the runner change. The mandatory runner-agnostic subset is distilled in `.codex/notes/discipline-digest.md`; task-specific details are retrieved from the Claude memory index and gstack checkpoints, then re-grounded against HEAD. Codex local memories are supplemental generated state under `CODEX_HOME`, not a replacement authority.

## Verification

- Start with the narrowest meaningful test or static check.
- For PR-ready code or governance changes, run `just codex-check` unless the change is documentation-only and a narrower documented gate is sufficient. Name `codex-check`, not `check`: the two gates differ only in that `check` omits `codex-parity-check`, and with it the `tools/hooks/test_*.sh` + `tools/statusline/test_*.sh` shell suites (CI runs them separately). This matches `.agents/skills/roadmap-continue/SKILL.md` and `.agents/skills/ship-pr/SKILL.md`, which already prescribe `just codex-check`.
- For governance/context changes, also verify instruction discovery or pointer integrity when applicable.
- For roadmap/status changes, update `.harness/roadmap_status.md` directly (recompute `workspace_state_hash`, `recently_completed`, `next_action` per CLAUDE.md §12.2); do not hand-maintain volatile facts inconsistently with the recipe there. `.harness/roadmap_status.md`'s `## Next action` holds only the live pointer — historical rounds live at `.harness/roadmap-next-action-archive.md`, queried by grep, never read wholesale.
- Run `just codex-closeout` before final response, commit, or PR; it writes a fresh pre-closeout checkpoint and hard-fails if the guard cannot verify it. Resolve hard findings and report warnings explicitly.
- If `.harness/codex_loop_state.json` exists, closeout also verifies the active autonomous loop has reached every pre-closeout gate from linked worktree readiness through decorrelated review.
- Before claiming green, report exactly which checks ran and which did not.

## PR Discipline

- Every substantive Codex setup change should land on a branch and open a PR.
- Strict CI gates are required: lint, typecheck, tests, semantic overlay, substitution ledger, and axis isolation when CI provides them.
- `just codex-review` is for out-of-family review of concrete diffs; it complements the transcript-brief review — an ISOLATED fresh-context reviewer handed a written session brief (in this venue a separate `codex exec` call, never the interactive controller reviewing its own work) — and does not replace that transcript-aware judgment. Where a session's approval surface exposes no isolated exec shape (unattended loop mode auto-allows only the merge-lens shape), the brief-review obligation ROUTES to the Claude-venue transcript-brief Agent review, handed the SAME written session brief (a merge-gate lens is NOT a discharge — lenses see only their specialty prompt and the diff, never the brief, and doc-only changes skip that gate entirely), and the routing is recorded; it is never discharged by controller self-review and never silently skipped.
- **Decorrelation flips with authorship**: when Codex is the AUTHOR, `codex review` is self-review — use `just gemini-review` as the out-of-family artifact reviewer, and reserve Claude (when quota permits) for gate-lens review rather than authoring.
- **Standing authorization — Antigravity (operator, 2026-08-01):** `just gemini-review` may use the operator's OAuth-authenticated `agy` CLI subscription and disclose the current repository diff for every forward arc. Do not request per-run approval. Never use Gemini/Google API keys, service-account credentials, Vertex project routing, or a direct provider API for this review. The wrapper must still fail closed on authentication, permission, empty-output, malformed-verdict, or reviewer-BLOCK outcomes.
- Substantive code PRs transit the 3-lens merge gate before merge: run each lens prompt at `.codex/notes/merge-gate-lenses/` as a FRESH `codex exec` (never the authoring session); all-approve required; BLOCK → fix → scoped re-gate on the delta; append the row to `.harness/merge-gate-log.md` before merging. Doc-only PRs may take a logged proportional skip.
- PR bodies must name tracking surfaces updated or explicitly state why roadmap/status/ledger updates were not applicable.

<!-- graft:start -->
## Graft — repo context graph

This repo is indexed in `graft/`: small linked markdown nodes that explain each
system and carry exact file:line spans, kept in sync with the code through git.

For ANY task here — understanding how something works, finding where code lives,
or scoping a change — get context from the graph before grepping or opening
source files. Re-ask freely (it's cheap) and reuse literal identifiers you
already have (symbol, error string, file name) as the query. New to this repo?
Run `graft map` first — a token-budgeted orientation (dir clusters, hubs,
hotspots), no LLM, no key.

- Run `graft ask "<your question>" --source` → ranked nodes with the relevant
  code spans inlined (each hit's ≤8-line crux by default; `--full` for whole
  definitions when the crux isn't enough). Match the tool to the task shape:
  for understanding or editing, the top node IS the answer — cite its
  `covers:` file:line spans and edit straight from `--source`. For
  exhaustive tasks ("every occurrence / every caller of this pattern"), ranked
  results are top-N, not complete — run `graft grep "<literal>"` instead
  (exhaustive over indexed files, grouped by enclosing symbol), falling back
  to raw `grep -rn` only for unindexed files.
- `graft skeleton <file>` → every definition's signature + span, ~10× cheaper
  than reading the file; use it to skim an API surface.
- `graft callers <symbol>` gives precomputed, exact edges — who calls this.
  Add `--direction out` for what it calls, or `--depth N` to walk
  transitively for the full blast radius. For structural questions, skip
  ranking and use this directly.
- Or browse: `graft/INDEX.md` lists every node; follow the links.
- Monorepos and folders of multiple repos rank fairly across sub-projects —
  hits carry `[scope/]` labels naming which one they're from. Narrow with
  `graft ask "<task>" --in <scope>/` once you know where you're working.

If a returned span is truncated ("+N more lines"), open the file at that exact
range before finalizing. Only open source files when a node genuinely lacks a
needed detail, and then at the exact file:line the node points to — never
re-read whole files.

After big code changes, refresh the graph with `graft build` (deterministic,
no API key, $0).
<!-- graft:end -->
