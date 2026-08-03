# Spec + Atomic-Unit Plan — Insights-Report Residue (H_E Workspace Tooling)

## Context

The 2026-08-03 /insights report was reviewed against the live workspace: ~11 of ~15 suggestions were already implemented or stale. This plan builds the **genuinely unimplemented residue** as six features, decomposed into 11 atomic units (U-WT-01..08 + U-HK-42..44) across ~8 PRs. All work is workspace-ops (mode-agnostic posture): hooks, skills, and `tools/*.py` scripts only — **no `design-substrate/**`, no `harness-*/src`, no arc-ledger.yaml rows, no §12 governance change, no permission-guard edits, no paid calls.**

Operator scope decisions (AskUserQuestion, 2026-08-03): parallel arcs = **staged v1** (no orchestration); supervisor = **registry + report** (no auto-kill/respawn).

Grounding corrections discovered during design (vs. the naive insights suggestions):
- `pyyaml>=6.0` is already a dev dep (`pyproject.toml:40`) and in `.venv` — the YAML hook uses `.venv/bin/python`, falling back to `uv run --quiet python`; **never** `uv run --with` (ephemeral env on every edit).
- `postedit-lint.sh` is already wired at PostToolUse `Edit|Write|MultiEdit` (`.claude/settings.json:200-204`) — zero settings change needed.
- `.harness/loop_status.md` + `.harness/.checkpoints/` are gitignored — the EXIT REPORT is a local operator artifact with zero CI/ledger surface.
- A test-first `red` gate already exists Codex-side (`tools/codex_loop.py:505-507`); merge-gate reviewer 3 already does read-only reasoned mutation probes — so feature 5 adds only what's missing (Claude-side adversary skill + a mechanical probe runner).

## Registration (with PR 1)

- One **R-IF-116** YAML block in `Project_Roadmap_v1.md` §5.1 (after line ~277 family; R-IF-113 is a gap — do not reuse): `surface: VII`, `posture: mode-agnostic`, `status: ACTIVE`, `scope.files` = [tools/hooks/**, tools/*.py, .claude/skills/**, .agents/skills/** (Codex-native mirrors), justfile, .gitignore, HARDENING_PLAN.md, wave5-hooks-status.md, this plan], `close_shape: {type: PR-merge, cascade: [R-IF-roadmap-refresh]}`. Auto-queues at §4 priority rank 1. Skill-text changes mirror into `.agents/skills/**` (parity contract — the Codex tree encodes its rituals independently).
- Hook units **U-HK-42/43/44** appended to `.harness/hardening-workflow/HARDENING_PLAN.md` §5 table (ends at U-HK-41, line ~376); wave outcome recorded in a `.harness/wave5-hooks-status.md` at close.
- Non-hook units use a new **U-WT-NN** (workspace-tooling) scheme — verified unused.
- **Do NOT touch `.harness/arc-ledger.yaml`** (any open row is a CI hard-fail; `arc_ledger.py:207-208`).
- Every PR follows ship-pr: CI green → **authorship-dependent out-of-family review** to convergence (`codex-review` for Claude-authored diffs; `gemini-review` for Codex-authored — a Codex-authored unit reviewed by codex would be self-review) → merge-gate 3-lens (code-touching) → serial merge → §12.2 terminating refresh. Build sessions start with the §12.1 audit (drift was flagged at plan time: local HEAD had moved past the recorded hash — reconcile first).

## Atomic units

### Feature 1 — YAML parse-check hook

**U-HK-42 — `*.yaml|*.yml` branch in postedit-lint** (S)
- Files: `tools/hooks/postedit-lint.sh` (~+18 lines), `tools/hooks/test_postedit_lint.sh` (+5 cases).
- Widen the gate at `postedit-lint.sh:24`: `case "$FILE" in *.py) KIND=py ;; *.yaml|*.yml) KIND=yaml ;; *) exit 0 ;; esac`. YAML branch inside `hook_bounded 10`: prefer `"$PROJECT_DIR/.venv/bin/python"` if executable else `uv run --quiet python`; body `list(yaml.safe_load_all(open(f)))` catching `yaml.YAMLError` → print `str(e)` (carries line/column), exit 0 always. Clean → silent; dirty → `hook_emit "PostToolUse" "[yaml] parse error in ${FILE}: … (advisory — CI ledger checks are the hard gate)"`.
- Header comment must state the honest limit: catches unquoted `: `/indentation errors; does **not** catch ` #NNN` comment-truncation (valid YAML). Do NOT add a `#`-regex advisory (FP-heavy; same rejection class as HARDENING_PLAN D3/D13).
- AC: (1) unquoted `: ` scalar → emits with path + line/column token; (2) valid multi-doc `.yml` → silent; (3) existing `.py` cases 1–6 pass byte-identically; (4) `.txt`/`.json`/missing → silent; (5) `.venv` python preferred, `uv run --quiet` fallback, `--with` never in argv.
- Test: extend existing harness — fake `$REPO/.venv/bin/python` keyed on a `YAML_BAD` marker; fallback case removes `.venv`, plants fake `uv`, asserts no `--with`.

### Feature 2 — Pre-review grounding pass

**U-WT-01 — grounding clause in ship-pr + roadmap-continue** (S) — **ship first**
- Files: `.claude/skills/ship-pr/SKILL.md` (new bullet between "Green." at :15 and "Out-of-family review." at :16), `.claude/skills/roadmap-continue/SKILL.md` (step 4, :28-29), new `tools/hooks/test_skill_grounding_clause.sh` (grep-based; U-HK-41 precedent).
- Clause (5 bullets, before codex round 1): re-read every `file:line` cite in diff + PR body at HEAD; recompute every count/arithmetic claim from source; confirm every `#NNN` is the PR it claims; confirm `just check` ran at current HEAD; state in the PR body that the pass ran.
- AC: both SKILL.md files contain the clause; in ship-pr it precedes the codex-review bullet (grep-asserted).

**U-WT-02 — `tools/grounding_pass.py`** (M) — **DEFERRED: build only if U-WT-01 alone hasn't collapsed review rounds after 3–4 arcs**
- Scope if built: extract `path:line` tokens → report nonexistent files / past-EOF lines; extract `#NNN` → verify via `gh pr view` (skip arm gracefully if `gh` absent). Exit 1 + list on findings. Explicitly NOT: prose arithmetic checking (NL inference, FP-heavy), YAML parse (U-HK-42 owns), check-freshness (existing gates own).
- Test: pure `scan_body(text, repo_root)` against `tmp_path` fixtures; `gh` collector monkeypatched; zero network in CI.

### Feature 3 — Arc-close EXIT REPORT

**U-WT-03 — `tools/arc_exit_report.py`** (M) + **U-WT-04 — ship-pr wiring** (S) — **one bundled PR** (8 skill lines aren't a PR; note the bundling in the PR body)
- Emission point: a ship-pr step after the branch-hygiene block (:147), before reflect/context-save (:186) — the only point where merge SHA, post-merge main-CI conclusion, and refresh commit all exist. (Stop hooks rejected: can't distinguish arc close from turn end. post-merge-refresh.sh rejected: fires before the refresh commit/CI conclusion exist.)
- Design: pure `render(data) -> str` + thin `collect()` shelling `gh`/`git` (monkeypatched in tests). Output: `.harness/.checkpoints/arc-exit-report-pr<NNN>.md` (gitignored; PR-keyed, date-free — a closeout resumed on a later date must overwrite the same file, not orphan a stale sibling) — head is a fenced yaml block: `pr / merge_state / merge_commit / main_ci{commit,conclusion,run_url} / refresh_commit / checkpoint{path,confirmed} / todo_for_human[]` + short prose tail. Index: one `loop_log EXIT-REPORT "pr=#N ci=<sha8>:<concl> refresh=<sha8> todos=<N> path=…"` row. **For todo_for_human[], add a small structured sibling of `loop_pending_hil_summary()` (`loop_lib.sh:166-186`) — e.g. `loop_pending_hil_list` emitting one full row per pending DEFERRED-HIL from the same ledger parse — because the existing summary is deliberately bounded to 3 details + a `+N more` suffix and cannot faithfully populate a machine-readable list (codex round-6). Share the ledger-parsing logic; do not fork a second parser.**
- AC: (1) yaml block round-trips through `yaml.safe_load` (the machine-readable witness); (2) missing refresh → `refresh_commit: null`, never fabricated; (3) non-success CI reported verbatim; (4) empty todo list present, not omitted; (5) idempotent per-PR re-run (same filename, overwrite).
- Test: `tools/test_arc_exit_report.py`, three fixtures (clean close / CI-not-green / no-refresh-owed), zero network. Justfile recipe `arc-exit-report`.

### Feature 4 — Subagent registry + orphan report (honest-observability v1)

Honesty framing (goes in the header comment): Agent-tool subagents are API tasks, not OS processes — no pid, no `kill -0`. Background-Bash pid fields in hook payloads are unverified — do not build on them. v1 tracks **subagents only** and reports "unreconciled," never "orphaned."

**U-HK-43 — registry write in subagent-validate.sh** (S–M)
- Files: `tools/hooks/subagent-validate.sh` (+~20 lines), `tools/hooks/test_subagent_validate.sh` (+5 cases), `.gitignore` (+`.harness/.agents-registry.jsonl`).
- `_registry_append()`: one `jq -nc` compact line `{ts, event, session, agent_id, transcript, cwd}` appended (`>>`, O_APPEND single-printf atomicity, guarded `[ ${#LINE} -lt 4000 ]` to stay under PIPE_BUF) at the top of both SubagentStart and SubagentStop branches; failure invisible (no behavior change to the existing gate). `agent_id` is the documented common subagent hook field (claude-code-hooks.md reference §hook-input) — it is the correlation key; empty-string tolerated when absent (fallback correlation = transcript path).
- AC: (1) Start → exactly one well-formed `event:"start"` line, emitted additionalContext byte-identical to today; (2) Stop + non-empty (accepted) message → one terminal `event:"stop"` line, silent as today; (3) Stop + empty message → **`event:"stop_blocked"` line (NOT terminal `stop` — the gate emits `decision:block` and the subagent retries; only an accepted result reconciles, so a session dying mid-retry stays visible to the U-HK-44 sweep)** AND existing `decision:block` still emitted; (4) unwritable registry dir → behavior identical to today, exit 0; (5) 5 concurrent Starts → exactly 5 independently-parseable lines, none torn (backgrounded invocations + `wait` in the test).

**U-HK-44 — unreconciled sweep + prune in loop-gc.sh** (S) — depends on U-HK-43
- Files: `tools/hooks/loop-gc.sh` (+~15 lines), `tools/hooks/test_loop_gc.sh` (+3–5 cases).
- Extend the existing `[hygiene]` SessionStart composition (do NOT add a new hook): entries with `start` and no `stop` — **keyed by `agent_id` when present, else transcript path; repeated `stop` events for the same key deduplicated (a blocked SubagentStop can retry), and a `stop` may only reconcile the matching key, never another agent's `start`** (codex round-3 finding) — whose transcript mtime > 30 min → `N unreconciled subagent(s)` clause naming the oldest; rows > 7 days pruned via tmp-file + `mv` **under the same advisory lock the U-HK-43 appender takes (python-`fcntl` flock pattern as in `hook_checkpoint_generation`, `lib.sh:157-189`; appender skips the registry write if the lock isn't free within ~0.2s — registry is advisory; prune skips this tick) — an unlocked `mv` swap races a concurrent `>>` onto the replaced inode and silently loses events** (codex round-5); absent registry → skip entirely (existing cheap-pre-check discipline).
- AC: (1) stale unreconciled → clause present; (2) all reconciled → clause absent, hook silent if nothing else flagged; (3) fresh (<30 min) unreconciled NOT flagged (live fan-outs must not alarm); (4) 8-day row pruned, file remains valid JSONL; (5) malformed line doesn't abort the sweep. mtime control via `touch -t`.
- CUT: no `tools/agent_registry.py` (two bash functions are the right size); no auto-kill/respawn.

### Feature 5 — Red-first adversarial test-first harness (opt-in)

**U-WT-06 — `tools/mutation_probe.py`** (M–L) — highest-risk unit (writes source by design); land after U-WT-01 discipline is in force
- Interface: `uv run tools/mutation_probe.py --file F --lines A-B --test "<cmd>"`. Steps: (0) refuse if `git status --porcelain F` non-empty (exit 2); (1) run test, require PASS (probe against red test is meaningless → exit 2, distinct message); (2) read original bytes to memory, comment out lines A–B (`# ` prefix); (2b) **require the mutated file to remain syntax-valid (`ast.parse` for `.py`, `bash -n` for `.sh`) — a syntax-invalid mutation makes even a vacuous test fail at import/collection, faking probe success; reject the range with exit 2, distinct message** (codex round-5); (3) run test, require FAIL **for a test-level reason, not a parse/collection error**; (4) restore in a `finally` from in-memory bytes + verify `git diff --quiet F`, hard-error loudly if restore failed; (5) exit 0 probe-pass / exit 1 `PROBE FAILED: test stayed green with F:A-B removed`. **No `git stash`, no `git checkout --` anywhere.**
- AC: (1) real test + load-bearing lines → pass; (2) vacuous test → fail with named message; (3) dirty file → refuse, file untouched; (4) test killed mid-run → file byte-identical afterward (signal-exit fixture proves the `finally`); (5) already-red test → exit 2 distinct, not false pass; (6) range whose removal breaks syntax (e.g. sole statement of a suite) → exit 2 rejected-range, NOT probe-pass, and a vacuous test paired with such a range must not be reported as killed.
- Test: `tools/test_mutation_probe.py` — throwaway `git init` repo in `tmp_path`, real + vacuous test fixtures, subprocess-driven, asserts cwd is `tmp_path` in every case. Justfile recipe `mutation-probe`.

**U-WT-05 — `.claude/skills/red-first/SKILL.md` + `.agents/skills/red-first/` Codex projection** (S–M) — depends on U-WT-06; both trees, tested (parity: a Claude-only skill is undiscoverable from the Codex flow)
- Roles: **Adversary** (plain Agent-tool subagent; writes failing tests + one `# mutation-probe: <file>:<lines>` annotation per test from the unit's ACs only — must NOT be the `harness-adversarial-reviewer` skill, which is review-only by hard rule; state this explicitly). **Implementer** (iterates to green; may not edit the test file — enforced by **recording the test file's `sha256` at Adversary handoff and comparing at completion** (a bare `git diff --name-only` cannot distinguish an untouched adversary test from an edited one, since the adversary's own writes are already in the diff; codex round-5), NOT by a permission-guard deny). **Completion gate**: every probe annotation passes under `just mutation-probe`; red evidence = failing output pasted in PR body (no Claude-side red ledger — `codex_loop.py` already has one; pasted output is the witness). Verdict lines follow merge-gate's fail-closed protocol.
- **CUT: no Breaker role** (merge-gate reviewer 3 already does reasoned probes on every code PR).
- Opt-in only — never auto-invoked from roadmap-continue/ship-pr. Dogfood: run `just mutation-probe` against U-HK-42's shipped tests and record the result in the PR body.
- Test: `tools/hooks/test_skill_red_first.sh` grep assertions (role sections, verdict protocol, not-adversarial-reviewer constraint, opt-in statement).

### Feature 6 — Parallel arcs, staged v1 (per operator decision)

**U-WT-08 — 2-lane pilot recipe** (S)
- Files: small `.claude/skills/two-lane/SKILL.md` + `.agents/skills/two-lane/SKILL.md` Codex projection + grep test covering both trees.
- Content: run two arcs in `.codex-worktrees/<slug-a>`/`<slug-b>` (existing machinery); **merges + refreshes strictly serial** through ship-pr — §12 unchanged, stated explicitly; on conflict → abandon second lane's branch and rebase, no merge-order heuristics; reap via `tools/hooks/safe-worktree-remove.sh` only; one lane holds the ship-pr fixed point at a time.
- No spawner script, no merge-queue lock (the §12 fixed point makes the queue structurally depth-1 — a lock is ceremony), no conflict automation. Follow-on orchestration registered only after ≥3 manual pilot runs surface a named recurring pain.

**U-WT-07 — `tools/arc_disjoint_check.py`** (M) — **DEFERRED: build only if the pilot proves lane selection is the bottleneck**
- Scope if built: pairwise `scope.files` glob-intersection over roadmap §5 / forward-register rows; exit 0 disjoint / 1 overlap (named) / 2 missing-scope (fail closed). Output must state the verdict is advisory (hand-authored scope lists can be stale).

## Build order (one unit per PR except the noted bundle)

| PR | Units | Size |
|---|---|---|
| 1 | U-WT-01 grounding clause + R-IF-116 registration | S |
| 2 | U-HK-42 YAML hook branch | S |
| 3 | U-HK-43 subagent registry write | S–M |
| 4 | U-HK-44 unreconciled sweep | S |
| 5 | U-WT-03 + U-WT-04 exit report (bundled) | M |
| 6 | U-WT-06 mutation-probe runner | M–L |
| 7 | U-WT-05 red-first skill (+ dogfood record) | S–M |
| 8 | U-WT-08 two-lane recipe + wave5 status doc + R-IF-116 close-or-carry | S |
| (9) | U-WT-02 grounding_pass.py — only if rounds haven't collapsed | M |
| (10) | U-WT-07 disjoint analyzer — only if pilot demands it | M |

Minimum-viable subset if scope must shrink: PRs 1–5.

## Standing cut list (do NOT build)

1. U-WT-07 / U-WT-02 until their trigger conditions fire. 2. Breaker agent (duplicates merge-gate reviewer 3). 3. `tools/agent_registry.py`. 4. Feature-6 spawner/lock/conflict automation. 5. Claude-side red-gate ledger. 6. `#`-truncation regex in U-HK-42. 7. permission-guard deny for "implementer may not edit tests" (would touch the protected guard — would need operator ratification; use the sha256-at-handoff comparison from U-WT-05 instead — a diff-name check cannot see implementer edits over adversary writes).

## Verification

- Per-unit hermetic tests as specified: hook tests auto-discovered by `tools/codex-parity-check.sh` glob (CI-blocking via ci.yml "Codex compatibility regressions"); Python tools via pytest under `just check`'s suite.
- End-to-end witnesses: U-HK-42 — edit a bad `.yaml` in a live session, observe the advisory; U-HK-43/44 — run a real fan-out, kill a session mid-flight, observe the `[hygiene]` clause next SessionStart; U-WT-03/04 — run ship-pr on PR 5 itself, confirm the report file + ledger row; U-WT-06 — mutation-probe U-HK-42's own tests (doubles as U-WT-05 dogfood); U-WT-01 — PR bodies from PR 2 onward state the grounding pass ran; track codex round counts across PRs 2–8 as the success metric.
- Ratification check: no paid calls, no governance changes, no permission-guard edits, no destructive auto-ops (U-WT-06 only under its refuse-if-dirty/restore-verified envelope, explicit invocation only).
