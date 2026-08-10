# R-CTX-1 — Context-Optimization Program: Atomic-Unit Implementation Plan (v1, APPROVED)

**Approved by operator 2026-08-10: "execute all waves (recommended)".**
Authored from the 3-model reconciliation (Codex gpt-5.6-sol × Claude Opus 5 × Fable 5 reconciler).
Reconciliation artifact: https://claude.ai/code/artifact/f045b45e-ecb1-43ae-873a-962fb16a7ba1
Source record: /Users/robertrhu/.claude/jobs/9b1bdd92/tmp/{neutral-brief,codex-r1,opus-r1,deliberation-divergences,codex-r2,opus-r2}.md
(job tmp is ephemeral — the reconciliation artifact + this plan are the durable record).

**Execution errata (2026-08-10, from codex out-of-family rounds 2–3 on PR #1293; ratified text preserved, corrections marked inline):** E1 (U-CTX-00 arc-ledger step impossible → informational note only) · E2 (Gate G1: Arc 4 additionally gates on the U-CTX-06 merge; #1292 is Codex-owned — poll, never touch) · E3 (U-CTX-14 citation count derived at build time, not hardcoded 635) · E4 (U-CTX-21 post-compaction half needs a compaction-generation selector or separate procedure — the first-turn metric alone is a non-measurement) · E5 (round 4: every serial-merge CI gate binds to a SHA — final-PR-head CI before merge, merge-SHA main CI before refresh, refresh CI before next merge).

## Ratifications (operator, 2026-08-10)
- **R1**: Arc 2's three rules (roadmap_status truncation + archive + query-not-Read for the .harness working set).
- **R2**: Floor B is TERMINAL. Arc 8 / Floor C parked in forward register with D-H probe preconditions. Do not run probes.
- **R3**: 12 machine-local bmad payloads: move ignore entries `.git/info/exclude` → `.gitignore` + documented reversible local removal.
- Earlier ratifications (this program): D1 runner-neutral `docs/governance/`; D2 design-skills + bmad removal both runners; D3 per-repo skill disconnect preserving other repos + Codex superpowers/CodeRabbit intact.

## Posture + hard constraints
- Mode-agnostic ops. **ZERO `design-substrate/**` edits in any PR** (X-AL-3). Audit every diff.
- No `git add -A`; explicit paths only. No force-push/history rewrite. No branch deletion (operator-only). Never `.agents`-before-`.claude` skill deletions. No paid provider calls. Worktree removal only via `tools/hooks/safe-worktree-remove.sh`.
- Parallel BUILD, strictly SERIAL merge: PR → CI green (evidence: terminal status+conclusion, poll ~80s) → `just codex-review` converged → `merge-gate` (code-touching only) → merge → **terminating refresh as immediate next commit** → main CI green → next merge. *(errata E5: every CI gate binds to a SHA, not a moment — (i) the pre-merge CI evidence must be for the FINAL PR head (any codex-review/merge-gate fix commit stales earlier runs; re-verify after the last commit) against current base main; (ii) after merge, verify the MERGE SHA's own main CI green BEFORE the terminating refresh; (iii) verify the refresh commit's CI before the next arc's merge.)*
- Codex coexistence: Arcs 3+ branch from post-#1292 main. Hook edits confined to PR-3 (one `/hooks` re-trust ceremony, flag operator immediately after merge). If Codex opens a colliding PR, halt affected agent and re-sequence.

## Token-efficiency doctrine (routing law)
1. **Batch, don't scatter** — one agent per ARC (units sequential inside it). Rationale: each subagent re-pays the full ~98k preload (review finding F-16). Six worker spawns total.
2. **Orchestrator-direct** for units under ~5 files of mechanical work.
3. Routing: **Fable 5** = orchestrator (gates, merges, refreshes, Waves 0–1 direct units, acceptance). **Opus 5 high** = Agents C (Arc 4) + D (Arc 5) — governance-heavy. **Sonnet 5 high** = Agents A (Arc 2), B (Arc 3), E (Arc 7), F (Arc 6). **Haiku: not used** (governance repo; error risk > savings).
4. Instrument-first: `just context-budget` lands in Wave 1.

## Waves and units

### Wave 0 — orchestrator-direct [NOW]
- **U-CTX-00 Program registration.** `R-CTX-1` rows in `.harness/forward-register.yaml` (program row + Arc 8/Floor C parked row carrying R2 + D-H probe preconditions verbatim) with snapshot + identity_digest bump same commit; arc-ledger gets an **informational comment note only** *(errata E1: the originally-worded "arc-ledger row/snapshot bump" is impossible — `rfs1_status: resolved` forbids any open standalone row per `tools/arc_ledger.py`'s `RFS1_ZERO_OPEN_ALLOWED` invariant and the forward-register header's own "do not fold" directive)*. AC: `tools/forward_register.py --check` + `tools/arc_ledger.py --check` green; row quotes R1–R3 with date.
- **U-CTX-01 Arc 0 config hygiene (snapshot-first).** Snapshot → `.harness/audit/ctx-opt-baseline-2026-08-10.md` (skillOverrides, plugin scopes, global mcpServers, symlinks) BEFORE changes. Then: +18 skillOverrides off (algorithmic-art, cate-theme, add-molab-badge, connect-chrome, scrape, skillify, setup-gbrain, sync-gbrain, ios-clean, ios-sync, ios-design-review, ios-qa, ios-fix, freeze, landing-report, make-pdf, benchmark-models, plan-tune; KEEP context-save/restore/_gstack-command/gstack (bin/ is runtime dep of context-save), icm-workspace, notebooklm, document-generate/-release, brainstorming, writing-plans, diagram, spec); uninstall local `understand-anything` plugin; global Neon/blender/pencil → destination projects (unknown dest → leave + note); disable context7; delete dangling `~/.claude/skills/library` symlink. AC: snapshot committed first; next-session listing reduced; every change has a one-line revert recipe.

### Wave 1 — orchestrator PR + one Sonnet worker, parallel [NOW]
- **U-CTX-02 Arc 1 MCP (orchestrator-direct, PR-1).** Remove `dribbble` + `harness-7a-scaffold` from `.mcp.json` (body cites RB-SUB-03); KEEP `notebooklm` registered-and-disabled; reconcile `settings.local.json` enabled/disabled lists; **ZERO edits to `tools/hooks/test_permission_guard.sh`** (D-B: guard matches `*route_llm_call*` substring at permission-guard.sh:296; test builds its own repo). Also lands `tools/context_budget.py` + `just context-budget` (first-turn input+cache_creation+cache_read, request-ID-deduplicated) + baseline number in PR body. AC: `bash tools/hooks/test_permission_guard.sh` passes UNMODIFIED; context-budget emits a number; CI green.
- **Agent A · Sonnet 5 · worktree — Arc 2 (PR-2):**
  - **U-CTX-03 roadmap_status truncation.** `## Next action` (292,017 of 316,894 B) → live pointer + latest round + one-line archive ref; rest → `.harness/roadmap-next-action-archive.md`. ACs = the three R1 rules: (1) path + EVERY heading preserved (fixed point `lib.sh:106-111`, `hook_roadmap_next` `lib.sh:113-118`, `roadmap_status_refresh.py:134-203` untouched); (2) archive never written by a terminating refresh — guard assertion added to `roadmap_status_refresh.py --check` that refresh changed-set stays exactly one path; (3) head byte budget ≤ 25,600 B enforced by same --check.
  - **U-CTX-04 Consumer witness suite** (red-first). Table-driven tests over ~20 dependents: session-start.sh (hash+next), post-merge-refresh.sh, prompt-context.sh, postcompact-reinject.sh, codex_context_guard.py, closure_certification.py, closure_gate.py, docs_completeness.py, arc_exit_report.py, roadmap_status_refresh.py. Closes the unread-closure_* gap. Mutation probe: revert truncation guard → witness RED.
  - **U-CTX-05 Query-not-Read prose.** One sentence each: root CLAUDE.md §12.1/§12.2, Project_Roadmap_v1.md §7.2, roadmap-continue/SKILL.md (PINNED body — run `bash tools/hooks/test_skill_*.sh` pre-commit; must not disturb pinned needles/ordering), AGENTS.md pointer. Archive named as mandated reading NOWHERE.
  - **U-CTX-06 claude-artifact-pointers per-family split.** `.harness/artifact-pointers/{is,as,cp,od,runtime,memory,cxa,plans}.md` + resolving stub at old path (BEFORE Arc 4 consumes it); query-first prose for forward-register.yaml/loop_status.md/arc-ledger.yaml pointing at existing tools/*.py. AC gate: `just check` green; YAML parse-check on touched .yaml.

### GATE G1 — PR #1292 merges. Arcs 3–7 rebase onto its final adapter contract. (Monitor-based watch.) *(errata E2: Agent C / Arc 4 additionally gates on the Arc 2 / U-CTX-06 MERGE — U-CTX-12 consumes the per-family `.harness/artifact-pointers/` files U-CTX-06 creates, so Arc 4 launches only after BOTH #1292 AND PR-2 are merged; Agent B / Arc 3 gates on #1292 only. 2026-08-10 operator directive: #1292 is Codex-owned and still under Codex's own out-of-family review — poll, never merge or touch it from this program.)*

### Wave 2 — two parallel workers [AFTER #1292]
- **Agent B · Sonnet 5 · worktree — Arc 3 hooks (PR-3, THE single hook PR):**
  - **U-CTX-07** capture-failure.sh signature → `EVENT:TOOL:ERRTYPE:exit_or_cmdhead` + per-session emission cap (first two always emitted) + tests.
  - **U-CTX-08** loop-gc hygiene block top-3 + "(+N more)" reusing `loop_lib.sh:201` + test.
  - **U-CTX-09** REMOVE dead `Bash(git commit*)` matcher (settings.json:28); correct `.codex/hooks/README.md:32`; bind `claude-codex-parity.md:12-13` counts to computed assertions.
  - AC: `bash tools/codex-parity-check.sh` + `codex_hook_runtime_witness.py` green. **PR body flags operator: run Codex `/hooks` re-trust immediately after merge (fail-open window until done).**
- **Agent C · Opus 5 · worktree — Arc 4 heads table (PR-4):**
  - **U-CTX-10** clearance-corpus repair: fix 71 YAML-fail markers (quote `: `/`#` scalars) or classify irreparables in a manifest; parse-check gate over `.harness/clearance/*.md`.
  - **U-CTX-11** `tools/artifact_heads.py`: fail-closed (NO silent regex fallback), family normalization (two filename conventions), version-aware sort; TWO gates (generated-vs-committed + marker-completeness) wired into `just check` + `codex-check` + `.github/workflows/ci.yml`.
  - **U-CTX-12** FULL archive reconciliation (every §2.3/§2.4 row into per-family files from U-CTX-06; IS v1.13, IS plan v2.9, Memory spec v1.3, Memory plan v1.3 written in; AS corrected to v1.14/v1.6 in ALL venues); root §4.1 BOTH stale tables re-derived from substitutions.yaml SSOT (49→54, AS=6→11, mechanism table); byte guard root CLAUDE.md < 131,072 B.
  - AC: generator output == committed table; completeness gate green; `rg 'Action_Surface_v1_4|v1\.13.*Action_Surface'` → zero live-doc hits.

### Wave 3 — two parallel workers [AFTER Wave 2 merges]
- **Agent D · Opus 5 · worktree — Arc 5 root → Floor B (PR-5, via /optimize-claude-md discipline):**
  - **U-CTX-13** `docs/governance/*.md` packs + root slimmed to ~26 KB. EVERY §N.M heading keeps number+position; body → pack behind resolving pointer. Safety kernel VERBATIM-IN-FORCE in root: §1.3, §3.1/§3.2, §4.3/§4.4, §5, §8, §11 posture, §12.2.1, §12.4.1, §13.1. `check_pointers.py --baseline` pre/post.
  - **U-CTX-14** CI citation resolver: root heading set ⊇ ALL tracked `CLAUDE.md §N` cites — **count derived at build time by `git grep`, never hardcoded** *(errata E3: the 635 figure — design-substrate 68, .harness 401, .claude 58, root-md 47, harness-* 40, tools 16, .github 4, .githooks 1 — was already 636 by round 3 of this PR's own review, because program docs add cites as they land; the resolver + its completeness gate must recount the corpus at execution, treating the reconciliation-time figures as historical)*. tools/ + CI wiring + test.
  - **U-CTX-15** Runner load matrix (rule → load path per runner, tested) + AGENTS.md/CONTEXT.md router updates (AGENTS.md:46 §12.2 cite preserved-or-updated atomically) + router set-EQUALITY test over docs/governance/.
- **Agent E · Sonnet 5 · worktree — Arc 7 skills (PR-6):**
  - **U-CTX-16** D2 tracked deletions: .claude-side + .agents bridges SAME commit (never .agents-first); dirs + `.gitignore:88-91` together; BOTH parametrize lists (test:979-991 AND :994-1010); parity-note "no deletion" line struck with ratification ref; 5 tracked bmads + bridges.
  - **U-CTX-17** R3: 12 bmad entries `.git/info/exclude` → `.gitignore`; documented reversible local removal; catalog assertion test: 21 names absent for this repo; `~/.codex/superpowers`, CodeRabbit surfaces (justfile, test_codex_loop.py), `~/.agents/skills` UNTOUCHED.
  - **U-CTX-18** `just loop-start`/`loop-stop` recipes added; skills RETAINED as thin dispatchers (conversion-by-deletion deferred — CX residual hold); `overlay-query` → skill-activation-check.sh `_BUILTINS`; AGENTS.md:15 → `just overlay-query`; description pass with trigger-preserving budgets (fixes 3 stale: phase-7-cross-axis "101 edges/v2.1"→111/v2.23; phase-7-implementation plan heads; +1). Pinned-body touches re-run test_skill_*.sh.

### Wave 4 — one worker [AFTER Arc 5 merges]
- **Agent F · Sonnet 5 · worktree — Arc 6 axis files (PR-7):**
  - **U-CTX-19** IS/CP/OD CI pins FIRST (mirroring test_substitution_ledger.py:102 shape).
  - **U-CTX-20** Axis §1.2 slimming → heads-row + archive pointer; harness-as §4.1 rows BYTE-VERBATIM (CI-pinned: `.harness/substitutions.yaml` + `tools/substitution_ledger.py` strings, `| H_T-AS-8e ` row prefix + SUBSTANTIVE_RETIRED + batch-52); axis AGENTS.md projections co-updated.

### Wave 5 — orchestrator acceptance [CLOSE]
- **U-CTX-21** Cold-start + post-compaction A/B (component-separated) vs Floor-B ~71k target; per-PR context-budget delta table. *(errata E4: `context_budget.py`'s first-turn metric alone CANNOT satisfy the post-compaction half — a post-compaction request is not the session's first turn. U-CTX-21 requires either a TESTED compaction-generation selector in the tool (first assistant call after each compaction boundary, selected by transcript compact markers) or a separate documented post-compaction acceptance procedure; closing on the first-turn number alone is a non-measurement.)*
- **U-CTX-22** Program close: register flip; memory entries (≥2-cardinality patterns); MEMORY.md byte-measured single-pass; /context-save; final terminating refresh.
- **Program AC:** measured preload ≤ 76k (gate; target 71k); all new CI gates green on main; `git log --stat` audit shows zero design-substrate diffs.

## Numbers (reconciled)
Baseline 98–100k. Floor-B target ~71k (−28%); range 67–71k; conservative −24%. roadmap_status lever ~76k/reading-session (46/58 sessions) — separate from preload headline. Subagent multiplier saving×(1+N) reported separately (merge-gate N=3). Withdrawn: 59.5k/−39%.

## Asset leverage
roadmap-continue (cadence) · ship-pr (PR/refresh ritual) · merge-gate (code PRs) · red-first (U-CTX-04/07/08/11/14) · overlay-query (grounding) · /optimize-claude-md (Arc 5) · just codex-review (every PR) · advisor() at wave gates · context-save at arc closes · mutation_probe.py · Monitor (#1292 gate) · TaskCreate/TaskList (unit tracking).

## Sub-agent brief contract (every worker)
Carries: unit ACs verbatim; the ratification text it implements; file allowlist (its arc's surfaces ONLY); the prohibitions block above; negative examples (what bad output looks like); reviewer chain; "return the diff summary — orchestrator reads the DIFF, not your self-report." Worktree isolation mandatory. H_E parallelism only — no H_T topology claims (CP-AL-1).
