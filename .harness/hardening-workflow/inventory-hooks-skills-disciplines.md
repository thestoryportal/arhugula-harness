# Inventory — Hooks, Skills, Disciplines (AUTO vs MANUAL enforcement)

> The workflow's primary audit target. "AUTO" = a hook enforces it every time.
> "MANUAL" = it depends on Claude recalling to invoke a skill / follow a rule.
> All paths relative to repo root `/Users/robertrhu/Projects/arhugula-v2`.

---

## A. HOOKS (`tools/hooks/`, `tools/roadmap-audit/`, `tools/statusline/`) — wired in `.claude/settings.json`

### Libraries (sourced by hooks; not wired directly)
- `tools/hooks/lib.sh` — anti-drift keystone. `hook_project_dir()` (`:20-23`, `$CLAUDE_PROJECT_DIR` or git toplevel), `hook_emit()` (`:27-31`, additionalContext JSON), `hook_bounded()` (`:54-81`, portable watchdog), `hook_state_hash()` (`:85-87`, §12.1 recipe), `hook_roadmap_next()` (`:97-102`), `hook_write_checkpoint()` (`:110-138`), `loop_mode_active()` (`:145-149`, gate = `HARNESS_LOOP=1` env OR `.harness/.loop-active` marker — **all autonomy hooks are inert unless this is true**).
- `tools/hooks/loop_lib.sh` — ledger substrate (U-HK-11). `loop_log/loop_defer/loop_activate/loop_deactivate`, `loop_skip_set()` (`:101-116`, run-scoped DEFERRED-HIL item-IDs), `loop_pending_hil_summary()` (`:121-136`), `loop_gc_worktrees()` (report candidates at SessionStart; reap only from an explicit post-merge/closeout or loop-start call).
- `tools/hooks/resolve_lib.sh` — `/resolve` substrate (U-HK-13). `resolve_codex()` (`:15-19`, $0 subscription codex), `resolve_record/resolve_split`.

### Wired hooks (classification is the key column)
| Unit | Script | Event(s) | Class | Discipline |
|---|---|---|---|---|
| U-HK-02 | `precmd-clear-cache.sh` | PreToolUse(Bash) | NON-BLOCKING | Clear `.pyc` before pytest/build (stale-cache trap) |
| U-HK-05 | `precompact-checkpoint.sh` | PreCompact | NON-BLOCKING | Checkpoint state before compaction (synchronous) |
| U-HK-06 | `postcompact-reinject.sh` | PostCompact | CONTEXT-ONLY | Re-inject checkpoint pointer + roadmap next |
| U-HK-07 | `capture-failure.sh` | PostToolUseFailure, StopFailure | LOGGING | Log failures → `.harness/session-issues.jsonl`; nudge on cardinality≥2 (PostToolUseFailure only) |
| U-HK-08 | `prompt-context.sh` | UserPromptSubmit | CONTEXT-ONLY | Inject `[roadmap] next=…` + drift flag per prompt |
| U-HK-09 | `session-end-cleanup.sh` | SessionEnd | **ADVISORY** | Prune checkpoints keep-10; **list** merged branches/worktrees (NO auto-delete) |
| U-HK-10 | `stop-gate.sh` | Stop | **ENFORCING** | Fast ruff check/format on changed `.py` at turn-end; `decision:block` if findings; `stop_hook_active` guard |
| U-HK-12 | `permission-guard.sh` | PreToolUse(*), PermissionRequest(*) | **ENFORCING** | Tri-state: INERT (unless loop)→DENY-LIST→ALLOWLIST→ask. Deny-list (locked): paid LLM (`route_llm_call`/`llm_dispatch`) `:138-140`, recursive/forced `rm` `:161-162`, force-push/history-rewrite `:164-167`, branch/ref delete `:168-169`, secret/.env relocation `:171-173`, cred-store mutation `:173-174`, paid network (api.anthropic/openai) `:176-177`, creds-requiring `just` recipes `:179-180`. Allowlist `:183-259` (safe git/gh/uv/pytest prefixes). `_safe_path()` `:52-85`, `_bash_args_safe()` `:92-114`. **Loop-control wrappers (`tools/loop/defer.sh`/`halt.sh`) short-circuit to ALLOW `:151-156`.** |
| U-HK-14 | `stop-loop.sh` | Stop | **ENFORCING** | Loop-only. Halt marker present → stand down. Iteration cap (`HARNESS_LOOP_MAX`, default 25) → hard stop + set halt. Else: inject next-action + run-scoped skip-set as `decision:block` to continue. |
| U-HK-16 | `git-arc-guard.sh` | Stop | **ADVISORY** | systemMessage warns: uncommitted/untracked, unpushed commits, stale-local-default-behind-origin. Never blocks. |
| U-HK-17 | `subagent-validate.sh` | SubagentStart, SubagentStop | QUALITY GATE | SubagentStart: inject contract (advisory). SubagentStop: `decision:block` ONCE if final message empty (fail-open on transcript-shape mismatch). |
| U-HK-21 | `skill-activation-check.sh` | UserPromptSubmit | **ADVISORY** | `/cmd` typo → "did you mean" near-miss hint; SILENT on knowns (load-bearing). |
| U-HK-22 | `prompt-lint.sh` | UserPromptSubmit | **ADVISORY** | Flags ~18 bare-deictic prompts (`it`/`this`/`fix-it`); SILENT on idioms/`continue`/context. |
| U-HK-25 | `postedit-lint.sh` | PostToolUse(Edit\|Write\|MultiEdit) | **ADVISORY** | ruff on the just-edited `.py`; inject findings (non-blocking; PostToolUse can't undo). |
| U-HK-26 | `loop-gc.sh` | SessionStart | ADVISORY | LIST stale candidates + MEMORY.md cap in every mode; SessionStart never deletes. Explicit post-merge/closeout or `/loop-start` owns reaping. |
| U-HK-27 | `context-recovery.sh` | statusLine | NON-BLOCKING | Proactive `hook_write_checkpoint` at 60/75/85% context; chains operator statusline. **Only place `context_window.used_percentage` is exposed.** |
| U-HK-28 | `session-start.sh` (roadmap-audit) | SessionStart | **ENFORCING** | §12.1 hash audit + §12.2.1 fixed-point carve-out. Emits `[ROADMAP] ok/lag-expected/DRIFT`. Appends `loop_pending_hil_summary`. |
| U-HK-29 | `post-merge-refresh.sh` (roadmap-audit) | PostToolUse(Bash; only on `gh pr merge`) | **ADVISORY** | Detects substantive merge → pre-computes new hash → injects §12.2 refresh checklist. Does NOT edit the dashboard. |

**Verification:** all 17 wired scripts present + non-empty; `resolve_lib.sh` + `test_*.sh` are library/test (not wired). No gaps.

**Enforcement tally:** ENFORCING = U-HK-10, 12, 14, 28 (+17 quality-gate). ADVISORY = U-HK-09, 16, 21, 22, 25, 29. The rest are non-blocking housekeeping/context.

---

## B. LOOP RUNNER (`tools/loop/`)
- `run.sh` (U-HK-15, `:1-127`) — headless overnight runner. `loop_activate` (`:57`) → per-iteration compute skip-set (`:104`) + inject into prompt (`:105`) → `claude -p` background with `HARNESS_LOOP=1`+`HARNESS_LOOP_MAX` (`:116-117`). Halt check every iteration at start (`:89`). EXIT trap clears loop mode all paths (`:73-83`). Exits ONLY at max-iterations or `.loop-halt`.
- `defer.sh` (`:1-27`) — allowlisted wrapper; `loop_defer <id> <reason>` (DEFERRED-HIL row); requires id + non-empty reason. Loop ADVANCES after (not a halt).
- `halt.sh` (`:1-21`) — allowlisted wrapper; raises `.harness/.loop-halt` + STOP row. Called ONLY at true exhaustion (every forward item deferred).

**Intended loop:** start → iterate (ground→implement→PR→merge→refresh) → at a gate defer+advance → halt only at exhaustion/operator. **Gap to probe:** the headless `run.sh` enforces the cap + halt; does the INTERACTIVE `/loop-start` path (this session) get the same never-halt enforcement, or does it rely on Claude following the rule? (stop-loop.sh fires on Stop in both, but its continuation only happens in loop mode — verify it actually prevents a premature human-style halt.)

---

## C. SKILLS (`.claude/skills/`)
| Skill | Trigger | Encodes | Class |
|---|---|---|---|
| `loop-start` | `/loop-start` | `loop_activate` + `loop_gc_worktrees reap`; then drive §12; auto-approve tier; defer-and-continue; never-halt; /resolve for forks; advisor; **codex-review before merge**. | MANUAL (Claude follows the skill body) |
| `loop-stop` | `/loop-stop` | `loop_deactivate`. | — |
| `resolve` (U-HK-13) | `/resolve` (loop mode, reversible fork) | Frame → `resolve_codex` (out-of-family $0) + `advisor()` → agree=take+RESOLVE row; disagree=safer/reversible+RESOLVE-SPLIT. Hard-stops (paid/secret/destructive/missing-cred) NOT resolvable → defer. | MANUAL (invoked on recall) |
| `roadmap-continue` (U-HK-23) | "continue" | The §12 loop: §12.1 audit → §4/§12.4.1 derive → ground (advisor before cross-axis) → implement+test+`just check`+`codex-review` → surface only genuine gate → hand to ship-pr. | MANUAL |
| `ship-pr` (U-HK-23) | "ship it" | Pre-flight (`just check` green; **codex-review to convergence**; posture; X-AL-3); open PR; §12.2+§12.2.1 fixed-point refresh; §12.5.3 memory cascade. | MANUAL |
| `self-heal` (U-HK-24) | "get green" | Clear caches → suite → triage env-artifact vs logic → fix (advisor before non-trivial) → re-run to fixed point. | MANUAL |
| `fan-out` (U-HK-25) | "N approaches" | N parallel variant subagents + judge vs rubric. | MANUAL |
| `council/*` (c1..c11 + orchestrator) | design-decision + nameable tension | Dyadic-default multi-voice deliberation (§10.9). | MANUAL |

---

## D. CLAUDE.md DISCIPLINES — enforcement classification (the crux)

| ID | Discipline | §ref | AUTO or MANUAL | Intended enforcement |
|---|---|---|---|---|
| D9 | §12.1 session-start hash audit + §12.2.1 carve-out | §12.1 | **AUTO** | `session-start.sh` hook (+ manual fallback) |
| — | §14.3 cache-clear before no-output conclusions | §14.3 | **AUTO+manual** | `precmd-clear-cache.sh` + Claude habit |
| — | lint on edit / at stop | — | **AUTO** | `postedit-lint.sh` (advisory) + `stop-gate.sh` (enforcing) |
| — | worktree GC visibility at session start | §12.5.3 | **ADVISORY** | `loop-gc.sh`; explicit controller/`loop-start` owns reaping |
| — | paid-call / secret / destructive-git deny | §12.4.1 | **AUTO (loop)** | `permission-guard.sh` deny-list |
| D8 | §12.2 post-merge refresh + §12.2.1 fixed-point | §12.2 | **MANUAL** (hook only reminds) | `post-merge-refresh.sh` advisory + Claude/`ship-pr` |
| D1 | codex-review = default pre-merge reviewer | §13.1/§13.2 | **MANUAL** | Claude recall / `ship-pr` pre-flight |
| D2 | advisor() at decision-forks + pre-done | §13.1 | **MANUAL** | Claude recall |
| D3 | /resolve for reversible forks | resolve skill | **MANUAL** | Claude recall in loop mode |
| D4 | no-parking / never-halt-unless-zero-units | §12.4.1 | **MANUAL** (+stop-loop in loop) | `roadmap-continue` + Claude recall |
| D5 | defer-and-continue at a gate | U-HK-14/15 | **MANUAL** (+stop-loop) | skill + Claude recall |
| D6 | loop-mode paid-call rule (creds → proceed) | feedback memory | **CONFLICTED** | permission-guard HARD-DENIES paid calls even in loop → contradicts the corrected rule |
| D7 | autonomous git/worktree + cwd-safe hygiene | operator directive | **MANUAL / UNGUARDED** | none mid-loop (loop-gc only at SessionStart) |
| D10 | posture check (§11) | §11 | **MANUAL** | Phase-7 skills §0 preamble + Claude recall |
| D11 | memory hygiene (cardinality≥2, cap, verify) | §12.5 | **MANUAL** (cap is a hard file limit) | Claude recall; capture-failure nudges recurrence |
| D12 | completeness-by-execution before "done" | §13.1 | **MANUAL** | Claude recall |
| D13 | empirical cite-grounding + cross-spec drift grep | §13.1/§10.4 | **MANUAL** | Claude recall |
| D14 | output-token-limit resilience / loop durability (insights-report) | §14.4/§14.5 | **MANUAL** | Claude recall; U-HK-05/27 checkpoint substrate exists but may not trigger often enough mid-loop |
| — | §14.2 AskUserQuestion not [y/n]; §14.4/14.5 incremental/chunked writes | §14 | **MANUAL** | Claude recall |

**The pattern:** ~5 disciplines are AUTO (hook-enforced and reliable). **~14 are
MANUAL** (D1, D2, D3, D4, D5, D6-conflicted, D7, D8, D10, D11, D12, D13, D14, + §14
conventions) — these are what lapse, and what the hardening plan must address.
