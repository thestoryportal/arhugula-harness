# `--uncommitted` review-pollution flaw — investigation, verification, fix, and open threads

*2026-06-26. Mode-agnostic process-substrate. The durable record of the verification arc the operator
opened on discovering that the loop's out-of-family Codex review was being run in `--uncommitted` mode
while ~2,500 untracked files were present. Honest closeout per advisor: the [P1] fix below does NOT
close the whole concern — §6 names what is still owed.*

---

## 1. The flaw

`just codex-review-uncommitted` reviews **staged + unstaged + untracked** changes. Since **2026-06-18**,
~2,500 untracked files exist under `dashboard-design/` (2,240) + `.agents/skills/` (untracked subset) +
`.codex/agents/` + `.claude/agents/` (dev-environment agent/skill config — H_E tooling, NOT the harness).
Any `-uncommitted` review run after Jun-18 was **diluted** — Codex's attention split across the untracked
noise. From this workspace's Claude Code transcripts: **13 sessions actually executed `-uncommitted`
post-Jun-18 (Jun 21–26)**, overlapping the recent R-FS-1 fan-out arc-closes (#683–#768). The prescribed
default `codex-review --base main` (branch-vs-main) is **structurally immune** (excludes untracked).

**Honest causal read (advisor):** Codex is **non-exhaustive in ANY mode** (proof: #683's cumulative review
range ⊇ #685's, yet #683 found 0 and #685 found the [P1]). So this does **NOT** establish that pollution
*caused* missed bugs — a clean review could miss the same thing. The process flaw is real; the causal story
is not provable. Re-running a non-exhaustive reviewer cannot prove "no bugs."

## 2. Verification method + result (the precise lever)

You cannot prove a negative with a probabilistic reviewer, so the residual risk was **bounded
deterministically**:

- **Deterministic re-run (exhaustive for its class):** full provider-free suite **5,032 passed / 0 failed**;
  pyright 0/0/0; ruff clean. (One intermittently-failing test — `test_branch_completed_when_in_flight_runs_to_completion`
  — is a PRE-EXISTING flaky timing race added 2026-06-13 #542, before the window; see §6.)
- **Diff-coverage of the window (`c5dd9189..HEAD`):** **94 %** — 1,638 changed lines, **93 uncovered**. The
  finite residual surface. ~75 are defensive (error messages, `raise`, malformed-line `continue`, torn-file
  fallbacks); **~18 are load-bearing** and **converge with the Codex sweep** on the
  **orchestrator-fence / ABORT_BRANCH / torn-marker corruption-recovery** neighborhood.
- **Convergence:** the probabilistic (Codex) + exhaustive (coverage) methods independently point at the same
  small region — strong signal that's where residual risk is, and it's *named*, not diffuse.

## 3. Confirmed + fixed defect — torn fan-out cardinality marker (#771)

The one candidate confirmed real **by witness** (RED-without-fix, passing controls), corroborated by coverage
(`engine_output_store.py:322-323` torn-handler uncovered): a **present-but-torn** cardinality marker
(`read_fanout_cardinality`→None, `fanout_cardinality_present`→True) was misread as absent at **two** consumer
sites — `workflow_driver.py:5513` (changed-cardinality guard → **silently dropped** in-flight branches) and
`:2296` (strict-tier maybe-ran analysis → **fresh-re-dispatch = DOUBLE-FIRE**, an at-most-once violation).
**Fixed in #771** (branch on `fanout_cardinality_present`; 5513 gated to non-orchestrator since the
orchestrator path at 5662 already handles it). 4 regression tests incl. an orchestrator-torn insurance
witness. advisor + `codex-review --base` (0 findings) + broad suite green.

## 4. Process remediations

| Item | Status |
|---|---|
| Loop → `codex-review --base main` (the immune mode) | **DONE** — `ship-pr/SKILL.md:15` `(or -uncommitted)` loophole removed (`roadmap-continue` already prescribed `--base`). |
| `.gitignore` for the untracked root cause | **PROPOSAL below (§5)** — operator decision (not applied). |

## 5. `.gitignore` proposal (for operator review — NOT applied)

The untracked noise pollutes any `-uncommitted` review + `git status`. Proposed **surgical** ignores
(the existing `.gitignore` already covers `dashboard-design/{impeccable,ui-ux-pro-max-skill}/` + `DESIGN.md`):

- **Unambiguous (0 tracked files — safe to ignore):** `.codex/agents/`, `.claude/agents/`,
  `dashboard-design/output/`, `dashboard-design/archive/`, `.agents/skills/*-workspace/` (mirrors the
  existing `.claude/skills/*-workspace/` convention — exactly Codex's [P3]).
- **Needs an operator call — DO NOT blanket-ignore:** `.agents/skills/` mixes **5 committed loop skills**
  (`roadmap-continue`, `ship-pr`, `self-heal`, `overlay-query`, `optimize-claude-md`) with ~25 untracked
  reference-clone skills (`bmad-*`, `council`, `fan-out`, `phase-7-*`, …). Are those reference clones to
  ignore, or workspace skills to commit? A blanket `.agents/skills/` ignore would be wrong.

## 6. OPEN THREADS — the fresh-context continuation (owed, NOT done)

The torn-marker fix closed ONE confirmed defect. Still owed, deliberately handed to a fresh context per
advisor (heavy / decorrelated-mechanism work):

1. **4 remaining [P2] candidate sites — untriaged.** From the Codex sweep (attributed to **code sites**, not
   PRs — Codex was non-exhaustive + cumulative): `workflow_driver.py:7961` (orchestrator-fence resume emits
   `WORKFLOW_START` not `RESUMPTION`), `:8220` (`ABORT_BRANCH` silently ignored for orchestrator fences),
   `:6307` (scoped-abort ledger *shape* depends on crash timing), `pause_resume_protocol.py:636` (nested-
   snapshot default-None fields change parent hash → reject valid old snapshots). Each needs a witness
   (real-vs-defended-vs-false-positive), then fix-or-dismiss.
2. **Adversarial-reviewer sweep over the ~18 uncovered load-bearing lines** — the operator's explicit
   "another mechanism must be leveraged" (a genuine `harness-adversarial-reviewer` dedicated-agent red-team,
   not core-agent self-review). The uncovered load-bearing cluster: `workflow_driver.py` effect-fence
   ABORT/paused disposition (`6637, 6812-6814, 9273`), the orchestrator-fence paths.
3. **Pre-existing flaky test `test_branch_completed_when_in_flight_runs_to_completion`** (#542, 2026-06-13) —
   a timing race (relies on sleep-ordering, not a deterministic barrier); fails ~1-in-5 with or without
   coverage. Test-hygiene fix (deterministic sync primitive); NOT a code-correctness bug.

**Operating posture for the continuation (operator directive 2026-06-26):** the operator is non-coding —
code-level findings are adjudicated by the **decorrelated mechanisms** (by-execution witnesses + `advisor()`
+ `codex-review --base` + `harness-adversarial-reviewer` dedicated agent), **not** surfaced to the operator.
Confirmed fixes land as CI-green + Codex-converged PRs; the operator is informed at the outcome level. The
credential/paid-call boundary is untouched (all the above are $0 / non-outward).
