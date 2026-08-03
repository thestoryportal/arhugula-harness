# U-HK Autonomous-Loop PROCESS Hardening Plan

> Scope is the U-HK process machinery ONLY: `tools/hooks/`, `tools/loop/`, `tools/roadmap-audit/`, `tools/statusline/`, `.claude/skills/`, `.claude/settings.json`. This plan NEVER touches `design-substrate/**`, the `harness-*/src` product code, or the H_T `R-NNN` roadmap. Every hook is capability-verified against `.harness/hardening-workflow/references/claude-code-hooks.md`. The hard-stop deny-list is never weakened — hardening only ADDS enforcement. Never-halt-unless-zero-units, defer-and-continue, and prefer-free-ollama are preserved throughout. All paths relative to repo root `/Users/robertrhu/Projects/arhugula-v2`. Host: Claude Code 2.1.162 (`if:` available ≥2.1.85, but the as-built convention is matcher + in-script `grep -E` inspection with ZERO `if:` clauses — this plan keeps that convention).

---

## 1. EXECUTIVE SUMMARY

**Diagnosis.** The inventory (`inventory-hooks-skills-disciplines.md:91-93`) is blunt: ~5 disciplines are AUTO (hook-enforced, reliable); **~14 are MANUAL** — they fire only if Claude *recalls*, at a decision-fork or a "done" declaration, to reach for `advisor()`/`/resolve`/`codex-review` or to run completeness/grounding checks. Memory is the single point of failure, and loop-mode momentum (`stop-loop.sh:89-93` injects an unconditional "drive the next item" continuation) biases toward advancing past the very moments these disciplines should fire. The session evidence (`session-evidence.md`) confirms the lapses end-to-end. Separately, the §9 "planned-as-enforcing-but-shipped-advisory" gaps are real and load-bearing: **D8** (`post-merge-refresh.sh`) only *injects a checklist* — nothing prevents merging PR #(N+1) while PR #N's terminating refresh is owed; **D1** (codex-review as default pre-merge reviewer) has no enforcement at all — `gh pr merge` is in the permission-guard allowlist (`permission-guard.sh:256`) and merges with no review-gate; **D6** is worse than advisory — the guard *contradicts* the operator-corrected loop-mode paid-call rule while ALSO under-denying the `mvp-*` recipes that actually bit this session. What now moves MANUAL→AUTO: a **D1 codex-pass merge gate** and a **D8 refresh-owed merge gate** (one ordered `gh pr merge` dispatcher), a **D7 cwd-split / arc-worktree deny** (the dominant 252-error class), **D14 per-step durable checkpoints** (cheap loss-window insurance), and a single **D2+D12 advisory Stop nudge** (review/execution before "done"). D6 is the one HYBRID held at an operator decision (the deny-list stays as the unauthorized backstop regardless). D3, D10, D13, §14.5, and the AUTO baseline correctly stay manual/as-is — their would-be hooks are either signal-saturated (desensitizing false positives) or not capability-expressible, and forcing them would degrade the channels the good nudges use.

### DISPOSITION TABLE (every discipline + §14 conventions)

| Discipline | Final disposition | Leverage | Risk |
|---|---|---|---|
| **D1** — codex-review default pre-merge reviewer | **HOOK-ENFORCE** merge-gate (PreToolUse(Bash) `gh pr merge` deny until codex-pass marker for HEAD) **+ RECIPE-HARDEN** (diff-scoped `--base`, model-asserted, timeout→kill-with-caveat) + skill-strengthen | high | low |
| **D2** — `advisor()` at forks + pre-done | **HYBRID** (skill-strengthen PRIMARY; one shared advisory Stop nudge, OPTIONAL) | high | med |
| **D3** — `/resolve` for reversible in-repo forks | **SKILL-STRENGTHEN** | med | low |
| **D4** — never-halt-unless-zero-units (interactive) | **HYBRID** (fold premature-halt detector into EXISTING `stop-loop.sh` as a one-shot prefix; skill-strengthen) | high | med |
| **D5** — defer-and-continue at a gate | **HYBRID** (wrapper already sound; skill-sharpen + the D4 hook is the backstop) | high | low |
| **D6** — loop-mode paid-call rule (creds-available → proceed) | **HYBRID — operator-gated** (deny-list intact as the unauthorized backstop; narrow operator-named allowlist applied ONLY post-ratification) | high | high |
| **D7** — cwd / worktree hygiene (252-error class) | **HOOK-ENFORCE** (marker-coupled context-aware PreToolUse(Bash) deny + create-time `git worktree add` guard) | high | low→med |
| **D8** — §12.2 post-merge refresh + §12.2.1 fixed-point | **HOOK-ENFORCE** (PreToolUse(Bash) `gh pr merge` deny until owed refresh cleared; merged with D1 in one dispatcher) | med | med |
| **D9** — §12.1 session-start hash audit + §12.2.1 carve-out | **LEAVE-AS-IS (AUTO)** | — | low |
| **D10** — posture check (§11) | **LEAVE-MANUAL** | low | low |
| **D11** — memory hygiene (cardinality≥2, 24,400 B cap, verify) | **HOOK-ENFORCE** (strengthen EXISTING SessionStart surface to imperative when materially over cap) | med | low |
| **D12** — completeness-by-execution before "done" | **HYBRID** (shares the D2 Stop nudge; skill-strengthen PRIMARY) | high | med |
| **D13** — empirical cite-grounding + cross-spec drift grep | **LEAVE-MANUAL** | low | high (of the *hook*; the manual path is fine) |
| **D14** — output-token resilience / loop durability | **HYBRID** (per-step durable checkpoint + targeted post-truncation recovery) **+ SKILL-STRENGTHEN** (§14.5 chunked writes) | high | low |
| **§14.2** — AskUserQuestion not bare `[y/n]` | **HOOK-ENFORCE** (low-FP advisory nudge; never blocks) | med | low |
| **§14.4/§14.5** — incremental / chunked writes | **SKILL-STRENGTHEN** (folds into D14; heredoc-nudge hook REJECTED on capability) | med | low |
| — §14.3 cache-clear before no-output conclusions | **LEAVE-AS-IS (AUTO)** | — | low |
| — lint on edit / at stop | **LEAVE-AS-IS (AUTO)** | — | low |
| — worktree GC at session start | **LEAVE-AS-IS (AUTO)** | — | low |
| — paid/secret/destructive-git deny-list (LOCKED) | **LEAVE-AS-IS (AUTO, LOCKED)** | — | low |

---

## 2. AUTO BASELINE THAT ALREADY WORKS

These ~5 disciplines are hook-enforced and verified reliable at the script level (2026-06-03). **Leave as-is.**

- **D9 — §12.1 session-start hash audit + §12.2.1 fixed-point carve-out** (`session-start.sh:49-103`): computes the §12.1 hash, honors the terminating-refresh carve-out (`:83-98`), guards the behind-origin case (`:69-77`), always `exit 0`. Reliable.
- **§14.3 cache-clear before no-output conclusions** (`precmd-clear-cache.sh`, PreToolUse(Bash), `settings.json:8-17`): clears `.pyc` before pytest/build; emits no permission decision (`exit 0` at `precmd-clear-cache.sh:37`) so it never fights the permission-guard. Reliable.
- **lint on edit / at stop** (`postedit-lint.sh` advisory + `stop-gate.sh:46-79` ENFORCING `decision:block`): the Stop gate fails *visible*, not fail-open, when ruff/uv are absent (`stop-gate.sh:69-72`). Reliable.
- **worktree GC at session start** (`loop_gc_worktrees`, `loop_lib.sh:265-299`): exact-SHA `headRefOid` identity (squash-safe), ignored-aware allowlist, `gh`-fail-safe to zero removals, self-excludes the current worktree. Reliable.
- **paid / secret / destructive-git deny-list (LOCKED)** (`permission-guard.sh:135-181`): tri-state, deny-checked-BEFORE-allow, fires before the permission-mode check → unbypassable even under `bypassPermissions` (`claude-code-hooks.md:201`). **Locked — hardening only ADDS to it.**

---

## 3. PER-DISCIPLINE HARDENING

### D1 — codex-review = default pre-merge reviewer

> **First-class pass (the dropped-cluster gap, re-derived).** Two enforcement LAYERS, because a Claude Code hook cannot run or time-bound codex: a merge-**GATE** (PreToolUse hook, shares the §4.2 D1+D8 dispatcher) and a review-**RUNNER** (a `just` recipe that earns the marker, where diff-scope + model-assert + timeout/kill-caveat live). This delivers the four operator-mandated properties — FAST, ENFORCED, MODEL-VERIFIED, TIMEOUT-BOUNDED — that an earlier analogy-to-D8 draft missed (it captured only ENFORCED).

**(a) Why it lapses.** Plan-intent (`inventory:77`, `ship-pr/SKILL.md:15-16`): `just codex-review` is the default out-of-family reviewer, run to convergence before merge. As-built, D1 is MANUAL with THREE distinct failure surfaces, all observed: (1) **no merge-gate** — `gh pr merge` is allowlisted (`permission-guard.sh:256`) so a merge proceeds with zero recorded review; (2) **slow → abandoned** — codex stalled 7–10 min and hit the 420s/580s Bash timeout twice, then was abandoned (`session-evidence.md:14-27`); (3) **wrong model, unasserted** — the recipe note (`justfile:205-209`) tells the human to *eyeball* the run banner's `model:` for `gpt-5.5`, but nothing asserts it, so a profile override silently shadowed the flag and ran `gpt-5.4` cross-session (`insights-report-2026-06-03.md:30-38`). The auth guard already blocks the *metered-key* fallback (`_require-codex-subscription`, `justfile:194-203`, `env -u OPENAI_API_KEY`) — but not the wrong-out-of-family-model bug.

**(b) Disposition.** HOOK-ENFORCE the merge-gate (the §4.2 D1+D8 dispatcher) **+ RECIPE-HARDEN** the runner that earns the marker (diff-scoped + model-asserted + timeout/kill-caveat) + SKILL-STRENGTHEN the ship-pr fallback.

**(c) LAYER 1 — merge-GATE (hook; the §4.2 dispatcher's D1 arm).**
- **Event + matcher:** `PreToolUse`, matcher `Bash` — the NEW `gh-pr-merge` dispatcher (`settings.json:8-17`), early-exit unless the command matches `gh +pr +merge` (the `post-merge-refresh.sh:44` pattern).
- **Check logic (THREE marker states for the current HEAD SHA):** (i) `.harness/.codex-pass-<sha>` present → PASS → allow (subject to the D8 refresh arm); (ii) `.harness/.codex-caveat-<sha>` present → KILLED-WITH-CAVEAT → allow BUT emit a loud `systemMessage` + the gate relies on the `loop_log CODEX-CAVEAT` row (never a silent pass — never-halt forbids deadlocking a merge on a genuine codex stall, but the bypass is loud + ledger-tracked); (iii) neither present, or the marker's SHA != current HEAD (stale → self-heal-ignored) → DENY (strict per DECISION-2(a)). HEAD is resolved cwd-safe via `git -C "$PROJECT_DIR" rev-parse HEAD` (inheriting D8's `post-merge-refresh.sh:98-99` pattern), so the gate is not itself vulnerable to the D7 cwd-split it sits beside.
- **Control output:** deny → `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[codex-gate] no codex-review pass recorded for HEAD <sha> — run `just codex-review-gated`, then merge (§13.1)"}}` (composes over the `:256` allow via deny>allow); caveat → allow + top-level `systemMessage` "[codex-gate] merging on a KILLED-WITH-CAVEAT codex pass (no verdict within timeout) — review owed".
- **Capability citation:** PreToolUse blocks (`claude-code-hooks.md:32`); `permissionDecision:deny`, `tool_input.command` visible (`:107-119`); deny before the permission-mode check → unbypassable (`:119,:201`); deny>allow (`:138-141`); fires in `-p` headless (`:33`); `systemMessage` shown to the user (`:97`). The hook only READS markers — it never runs codex.

**LAYER 2 — review-RUNNER (a NEW `just codex-review-gated` recipe extending `codex-review`, `justfile:211-217` — in-scope U-HK machinery; earns the marker):**
1. **FAST — the real levers are the TIMEOUT + the model-assert, NOT `--base`.** The recipe already diff-scopes (`codex review --base {{base}}`, branch-vs-base, not the whole monorepo, `justfile:212-213`) — and it diff-scoped DURING the 7–10 min stall this session, so `--base` is NOT what makes it fast (it was already present and still stalled). The genuine FAST levers are property 3's **timeout bound** (a bounded review is fast-or-caveat by construction) and property 2's **model-assert** (the gpt-5.4 profile-shadow bug plausibly burned much of those minutes on the wrong model). `--uncommitted` covers pre-commit (`:216-217`); use `--base <default-branch>` for the branch review.
2. **MODEL-VERIFIED:** capture the codex run-banner `model:` line and ASSERT it equals the intended out-of-family model (`gpt-5.5`, the config.toml default per `justfile:205-209`); on mismatch (a profile override shadowing the flag → the gpt-5.4 bug) → abort, write NO pass marker, `loop_log CODEX-MODEL-MISMATCH`. This AUTOMATES the manual "confirm the banner reads gpt-5.5" note into a hard assert.
3. **TIMEOUT-BOUNDED + kill-and-caveat:** wrap the codex call in `hook_bounded`/`timeout` (`lib.sh:54-81`; e.g. `CODEX_REVIEW_TIMEOUT` default ~300s). Clean converged pass → write `.harness/.codex-pass-<sha>` (sha = HEAD) + `loop_log CODEX-PASS`. Timeout → kill, write `.harness/.codex-caveat-<sha>` + `loop_log CODEX-CAVEAT "killed at <N>s, no verdict"`. NEVER write a pass marker on a stall.
- **Marker lifecycle:** SHA-keyed (a new commit invalidates BOTH states — self-heal-ignore on read when sha != HEAD); **ask-PROTECTED** — extend the Edit|Write ask-carve at `permission-guard.sh:213-214` with `*/.harness/.codex-pass-*|*/.harness/.codex-caveat-*` → ask, so the loop cannot self-author its own pass (the §4.2 cross-cutting safety invariant); REMOVE is implicit (SHA-keyed staleness).
- **SKILL-STRENGTHEN (fallback if the operator declines the hook):** `ship-pr/SKILL.md:15-16` → hard pre-condition "do NOT merge until `just codex-review-gated` recorded a converged pass (a written marker) THIS arc — execution, not assertion; a stall writes a CAVEAT, never a pass."

**(d) Adversarial verdict + residual risk.** Verdict: capability-sound across both layers; the hook only reads markers (it cannot run/time-bound codex — correctly pushed to the recipe). Self-checks: (i) the killed-with-caveat allow is the only never-halt-safe choice for a genuine stall, BUT it must be LOUD + ledger-tracked or it degrades into a silent escape hatch — hence the mandatory `systemMessage` + `loop_log CODEX-CAVEAT` and the ask-protected marker (the loop can't fabricate a caveat to skip review); (ii) the model-assert fails toward "no pass marker → DENY → friction prompt" (safe direction); (iii) the SHA-key + self-heal-ignore prevents a stale marker passing a newer commit. **Residual (honest framing):** because codex stalled THIS session even WITH `--base` diff-scoping, the caveat path may be the COMMON case until the model-assert + a workable timeout are tuned — so in practice this gate enforces *force a review ATTEMPT each merge + log loudly + fail toward a tracked caveat*, NOT *block until a clean verdict*. That is still strictly better than the current zero-review merges, and the `CODEX-CAVEAT` cardinality is the operator's signal that codex itself needs fixing (a recurring caveat is a defect, not a free pass). A converged pass whose marker write was skipped denies → one friction prompt (correct err-toward-review). No deny-list weakening — this only ADDS a deny + a tracked allow-with-record.

**(e) As-built anchors:** `permission-guard.sh:256` (`gh pr merge` + `just codex-review` allowlisted; new deny overrides via deny>allow), `:213-214` (Edit|Write ask-carve to extend for the markers), `:238` (`gh pr merge --admin` → ask precedent), `justfile:194-203` (`_require-codex-subscription`, the metered-key guard already in place), `:205-209` (the manual model-confirm note to AUTOMATE), `:211-217` (`codex-review`/`-uncommitted` already `--base`/`--uncommitted` diff-scoped), `lib.sh:54-81` (`hook_bounded` for the timeout), `post-merge-refresh.sh:44` (the `gh +pr +merge` inspection pattern), `ship-pr/SKILL.md:15-16` (codex pre-flight, the manual fallback), `session-evidence.md:14-27` + `insights-report-2026-06-03.md:30-38` (skipped/stalled + wrong-model).

---

### D2 — advisor() at decision-forks + pre-done

**(a) Why it lapses.** Plan-intent (`inventory:78`, §13.1): `advisor()` before committing to a non-trivial approach AND before declaring complete. As-built: MANUAL. Evidence (`session-evidence.md:38-49`): called once before the first build, NOT at the second design fork, and not pre-done. Loop-mode momentum (`stop-loop.sh:89-93`) biases toward advancing.

**(b) Disposition.** HYBRID. The skill-strengthen half is the PRIMARY structural fix (covers the *undetectable* fork-half); a single shared advisory Stop nudge is an OPTIONAL pre-done backstop.

**(c) Fixes.**
- **SKILL-STRENGTHEN (ship FIRST, zero-risk, command-agnostic):** `loop-start/SKILL.md:44-49`, `roadmap-continue/SKILL.md:23-26`, `ship-pr/SKILL.md:12-22` — name `advisor()` explicitly at the at-a-fork and pre-done moments.
- **HOOK-ENFORCE (OPTIONAL, the D2+D12 SHARED nudge — see §4):** `Stop`, no matcher (4th Stop hook). PRE-DONE half only. Logic: (1) `stop_hook_active==true` → `exit 0`; (2) read `transcript_path`, extract last assistant text via the `subagent-validate.sh:63-68` `jq -rs` recipe, fail-open silent; (3) DONE-SIGNAL gate — proceed only on a tight done-declaration regex (`/(^|\n)\s*result:\s/` or a complete/done frame); (4) ADVISOR/CODEX-THIS-TURN gate — scan the turn-tail for `(.type=="tool_use" or .type=="server_tool_use") and .name=="advisor"` **[CORRECTED — advisor serializes as `server_tool_use`, not `tool_use`]** OR a Bash `tool_use` whose `.input.command =~ /\bcodex\b/`; found → `exit 0` silent; (5) only when (done-signal AND no advisor/codex this turn) → emit `additionalContext`, `exit 0`.
- **Control output:** `hookSpecificOutput.additionalContext` (ADVISORY, `exit 0`, **NEVER `decision:block`**) — a review nudge ("§13.1 wants `advisor()` before declaring done; if already reviewed or trivial, ignore"). **Not counted against the 8× `decision:block` cap** (`claude-code-hooks.md:205-207`).
- **Capability citation:** Stop fires every turn-end, no matcher (`claude-code-hooks.md:38,172`); `stop_hook_active` (`:79`); Stop `additionalContext` injects (`:130`) and reaches the model (`:238`); the 8× cap is on `decision:block`, not `additionalContext` (`:205-207`). **Empirical correction:** advisor = `server_tool_use` (164 calls / 61 transcripts, 0 `tool_use`) — the as-specified `type=="tool_use"` matcher detects 0/164 real advisor calls.

**(d) Adversarial verdict + residual risk.** Verdict: skill-strengthen is the correct primary fix; the Stop hook is capability- and safety-sound but its advisor detector is **empirically broken** — require the `server_tool_use` fix before any hook lands, or it false-positive-nudges every done-declaration including the turn `advisor()` just ran. Residual after the fix: the fork-half remains skill-only (no Stop signal exists for a mid-turn fork); the pre-done nudge is best-effort outside loop-mode continuation (additionalContext lands reliably when a sibling Stop blocks). Both acceptable. No safety residual.

**(e) As-built anchors:** `inventory:78`, `session-evidence.md:38-49`, `subagent-validate.sh:39,54,57-68`, `git-arc-guard.sh:30-31` (stop_hook_active parity), `settings.json:96-118`, `loop-start/SKILL.md:44-49`, `roadmap-continue/SKILL.md:23-26`, `ship-pr/SKILL.md:12-22`.

---

### D3 — /resolve for reversible in-repo forks

**(a) Why it lapses.** Plan-intent (`inventory:79`, resolve skill): in loop mode, reversible in-repo forks route to `/resolve` (Codex + advisor dual-review). As-built: MANUAL. Evidence (`session-evidence.md:55-60`): ≥3 reversible forks decided solo (InMemorySpanExporter-vs-NoOp; deterministic-fake-leaf; same-vs-cross-family ollama chain shape). Structurally identical to D2's fork-half — the trigger is an internal cognitive state, not an external event.

**(b) Disposition.** SKILL-STRENGTHEN. The candidate hook detector ("Claude weighing ≥2 options in-text", `session-evidence.md:65`) is correctly REJECTED on signal quality: this design-heavy workspace weighs options on most substantive turns → no principled precision threshold → a desensitizing false-positive machine that would *also* erode the good D2/D12 nudge on the shared Stop surface.

**(c) SKILL-STRENGTHEN.** The substrate is sound (`resolve/SKILL.md:12-23` already encodes the dual-review + the hard-stop carve-out: paid/secret/destructive/missing-cred NOT resolvable). The gap is upstream INVOCATION → fix in the loop-driving skills: `loop-start/SKILL.md:48` ("auto-deciding reversible in-repo choices via `/resolve`"), `roadmap-continue/SKILL.md:23-24`. Optional belt-and-suspenders: fold a generic "reversible-fork? consider `/resolve`" line into the SAME D2 pre-done Stop nudge (only when done-declared AND no advisor/codex/resolve this turn), NOT a mid-turn option detector; any advisor sub-check must use the corrected `(tool_use|server_tool_use)` shape.

**(d) Adversarial verdict + residual risk.** Verdict KEEP. A missed `/resolve` costs decorrelated-review *quality* on a low-blast-radius reversible fork; irreversible forks are caught by the permission-guard deny-list regardless (`permission-guard.sh:138-181`). No safety residual.

**(e) As-built anchors:** `inventory:79`, `session-evidence.md:55-66`, `resolve/SKILL.md:12-23`, `loop-start/SKILL.md:48`, `roadmap-continue/SKILL.md:23-24`.

---

### D4 — never-halt-unless-zero-units (interactive / `/loop-start`)

> **Re-unified diagnosis (D4 ∧ D5 ∧ D6 = ONE incident).** The session-evidence incident (`session-evidence.md:69-95`) is a single event with three faces: Claude hit a paid item whose **credentials were present in main's `.env`**, treated the single defer as a **STOP** (the D5 face: defer-as-halt), wrote `result: … deferred to operator` and mis-logged a creds-present non-blocker as `DEFERRED-HIL` (the D4 face: premature halt with units remaining), because the guard's **paid-call rule contradicted the operator-corrected "creds-available → proceed"** (the D6 face). After operator correction, `just mvp-r300-cross-family` ran LIVE and PASSED. The fix is correspondingly three-part and must read as one: **D4** makes the premature halt *detectable and corrected* inside the existing loop continuation; **D5** is already mechanically sound (`defer.sh` advances by construction) and needs only a skill-sharpen + the D4 backstop; **D6** is the operator-gated paid-call decision (§6) that resolves whether "proceed" is authorized — the deny-list stays as the unauthorized backstop either way.

**(a) Why it lapses.** As-built: `stop-loop.sh:82-96` injects a GENERIC unconditional next-action and never inspects what Claude just did; no premature-halt detector exists. The generic block fired this session but could not recognize the halt as erroneous.

**(b) Disposition.** HYBRID — fold a premature-halt detector into the EXISTING `stop-loop.sh` continuation (NOT a 4th Stop hook) + skill-strengthen.

**(c) HOOK-ENFORCE (augment the existing block).**
- **Event + matcher:** `Stop`, no matcher (folds into the existing stop-gate→git-arc-guard→stop-loop chain, `settings.json:96-117`).
- **⚠️ MANDATORY CORRECTION — STRIKE the `stop_hook_active` addition.** The cluster proposal to "add the `stop-gate.sh:30-31` `stop_hook_active` idiom to `stop-loop.sh`" is a **never-halt safety violation** and is STRUCK. The omission at `stop-loop.sh:28-30` is DELIBERATE and documented: "Bounding is the iteration COUNTER … not `stop_hook_active` alone — a sustained loop must survive past the first continuation, which `stop_hook_active` would forbid." After turn-1's `decision:block`, every subsequent Stop carries `stop_hook_active=true`; copying the idiom would make stop-loop ALLOW THE STOP at turn 2 with forward units remaining — the exact premature halt D4 forbids. Bound the corrective ONLY via the existing iteration counter (`stop-loop.sh:83`) + a **one-shot prefix**.
- **Check logic:** ADD the missing stdin plumbing (stop-loop.sh reads NO stdin today, `:34-96`): `hook_read_stdin` + extract `transcript_path`, grep the LAST assistant message for a premature-halt signal (done/complete/`result:`/deferred-to-operator/awaiting-operator) WHILE iteration<MAX AND `.loop-halt` absent AND not-every-forward-item-in-skip-set. When present → set a ONE-SHOT `[never-halt]` reason PREFIX, then fall back to the generic advance next turn (so no two consecutive blocks are identical-no-progress and cannot stack toward the 8× cap). Fail-open if `transcript_path` is unreadable (parity with `subagent-validate`).
- **Control output:** the EXISTING `{"decision":"block","reason":…}` (`claude-code-hooks.md:38,129-130`) with the conditionally-prefixed reason. NEVER `continue:false`. NEVER an added `stop_hook_active` early-exit. Adds NO new Stop blocker — rides the existing block path.
- **Capability citation:** Stop `decision:block` continues (`claude-code-hooks.md:38`); `transcript_path` common field (`:68`); Stop block/inject (`:129-130`); the 8× cap (`:205-207`) — bounded by the existing counter + the one-shot prefix, NOT applicable to a sustained loop counter.
- **SKILL-STRENGTHEN:** `loop-start/SKILL.md:46-49` interactive never-halt prose (the skill half is already sound).

**(d) Adversarial verdict + residual risk.** Verdict MODIFY: fold the detector in, but STRIKE the `stop_hook_active` addition and bound via the existing counter + one-shot prefix; add the missing stdin/`transcript_path` read. Residual: heuristic transcript-grep mis-fires occasionally (bounded to one advisory line). The D4/D6 paid-call tie remains operator-owned — the corrective may tell Claude to PROCEED while permission-guard still denies the paid TOOL; the item then genuinely defers+advances (never silently halts), which is acceptable. No never-halt breakage once `stop_hook_active` is not added.

**(e) As-built anchors:** `stop-loop.sh:28-30` (DELIBERATE `stop_hook_active` omission — refutes the proposal), `:34-96` (reads NO stdin), `:82-96` (generic unconditional continuation — the gap), `stop-gate.sh:30-31` (the idiom NOT to copy), `git-arc-guard.sh:13,69-70` (middle Stop hook is systemMessage-only — does NOT consume the 8× cap), `loop-start/SKILL.md:46-49`, `test_stop_loop.sh:32-35`.

---

### D5 — defer-and-continue at a gate

**(a) Why it lapses.** The mechanism did NOT fail — `defer.sh:21-26` requires id + non-empty reason and advances by construction; `loop_lib.sh:91-94` writes the `DEFERRED-HIL` row; `loop_lib.sh:101-116` scopes the run-scoped skip-set via the leading item token (correctly NOT skipping an item merely *mentioned* in a reason); `halt.sh:17-20` raises `.loop-halt` only at true stand-down. The lapse was Claude *choosing* halt + mis-classifying a creds-present non-blocker as a `DEFERRED-HIL` gate (`session-evidence.md:69-95` — the same incident as D4/D6).

**(b) Disposition.** HYBRID — wrapper already sound; skill-sharpen + the D4 Stop hook is the enforcement backstop. No new mechanism.

**(c) SKILL-STRENGTHEN.** `loop-start/SKILL.md` + `roadmap-continue`: state defer≠halt explicitly — a `DEFERRED-HIL` advances; only `halt.sh` stands down, and only when EVERY forward item is deferred; a gate is genuine only if the input is truly unavailable (for paid runs, creds-present in main `.env` means proceed).

**(d) Adversarial verdict + residual risk.** Verdict KEEP. **Explicit dependency:** D5's enforcement backstop is the D4 Stop hook; this holds ONLY if D4 ships WITHOUT the `stop_hook_active` early-exit (which would break never-halt and defeat the backstop). Residual: a mis-classified non-gate logged `DEFERRED-HIL` stays skipped run-scoped even though buildable — a hook cannot un-write a ledger row Claude authored; the D4 corrective prefix partially mitigates by prompting a re-check but cannot retract the row.

**(e) As-built anchors:** `defer.sh:21-26`, `loop_lib.sh:91-94`, `loop_lib.sh:101-116`, `halt.sh:17-20`, `session-evidence.md:69-95`.

---

### D6 — loop-mode paid-call rule (creds-available → proceed)

> **DECISION — not resolved in this plan body.** See §6 for the framed operator decision (2-3 options + recommendation + blast-radius). The guard change is NOT applied until ratified. The deny-list stays intact as the unauthorized-paid backstop in every option — this is an ADD of a narrow allow, never a weakening.

**(a) Why it lapses.** TWO compounding grounded lapses. **(1) Guard contradicts the corrected rule:** `permission-guard.sh` hard-denies paid calls in loop mode (`route_llm_call`/`llm_dispatch` `:138-140`; `curl/wget/http` to api.anthropic/openai/googleapis `:176-177`; `just mech-beta|mech-gamma|daemon` `:179-180`) — matching the OLD U-HK-12 intent and CONTRADICTING the operator's corrected "loop-mode + creds-available → PROCEED" (`session-evidence.md:76-99`, `insights-report-2026-06-03.md:18-26`). **(2) Manual-defer recurrence:** the recipe that bit this session — `just mvp-r300-cross-family` (`justfile:115-116`, paid) — is NOT matched by the `:179-180` deny regex (only `mech-beta|mech-gamma|daemon`), so the guard did NOT deny it; Claude DEFERRED by manual recall and wrongly logged `DEFERRED-HIL`, then ran LIVE+PASSED after correction. D6 is simultaneously **over-broad-deny on raw surfaces AND under-broad-deny on the `mvp-*` recipes**. Multi-session recurrence (operator-corrected more than once).

**(b) Disposition.** HYBRID — operator-gated.

**(c) HOOK-ENFORCE (DESCRIPTIVE ONLY — applied post-ratification).**
- **Event + matcher:** `PreToolUse`, matcher `*` (existing wiring; in-script `grep -E` does the real matching). The loop is headless (`run.sh:117` invokes `claude -p … --permission-mode default`), so `PermissionRequest` does NOT fire (`claude-code-hooks.md:33`) and PreToolUse(Bash) is the correct and only enforcement event.
- **Check logic:** add a NARROW allow short-circuit mirroring the EXISTING defer/halt short-circuit (`permission-guard.sh:151-156`), placed AFTER `loop_mode_active()` and BEFORE the paid-deny at `:176-180`. Fires iff (a) `loop_mode_active()` true; (b) `TOOL=Bash` and `CMD` matches a recipe from an operator-seeded tracked allowlist as the FINAL token; (c) passes the `:151-156` strictness VERBATIM (no `[;&|<>]`, no backtick, no `$(...)`, no newline, no `${?[A-Za-z_]}`). On match → `emit_allow` + an explicit `loop_log ALLOW-PAID` row. On any fail → fall through to the UNCHANGED deny-list. Raw paid surfaces (`:138-140,:176-177,:179-180`) STAY denied.
- **FOUR REQUIRED MODIFICATIONS before this is safe to apply** (all carried forward):
  1. **[BLOCKER] ask-protect the allowlist path.** `permission-guard.sh:209-216` traces show `.harness/paid-allowlist.txt` is not design-substrate, not a secret pattern, inside the worktree → `_safe_path` returns 0 → `emit_allow`. So in loop mode the guard would AUTO-APPROVE the loop writing its own paid-allowlist, then run `just <that-recipe>` → unilateral paid spend during the unattended run, defeating the LOCKED `feedback-background-agent-no-unilateral-paid-calls`. **Fix:** add `.harness/paid-allowlist.txt` to the Edit|Write ask-carve at `:213-214` (a case arm that falls through to ask), OR relocate it to a path `_safe_path` already denies. Without this the (i)/(ii) distinction collapses.
  2. **Final-token anchor.** Change the recipe match to `just[[:space:]]+<RECIPE>[[:space:]]*$` (recipe = LAST token, no trailing args). `justfile:13` sets `positional-arguments := true`; a trailing-arg passthrough (`just mvp-r300-cross-family extra args`) would be an injection vector the deny-list does not re-scan (the allow short-circuits before `:158-181`) and `_bash_args_safe` is skipped on this branch. Every paid recipe the operator would list is zero-arg, so this is correct; an arg-taking paid recipe correctly falls to ask.
  3. **Drop the `(bash[[:space:]]+)?` alternative** for the recipe case — `just` is a PATH binary, not a script path; `bash just <recipe>` is meaningless. The bash-prefix copied from the defer/halt short-circuit does not belong here.
  4. **Add the audit row.** `emit_allow` (`:117-124`) does NOT `loop_log`; explicitly call `loop_log ALLOW-PAID` on the allowed path so each unattended paid run leaves a reviewable ledger entry.
- **Do NOT gate on cred-presence:** the env-var probe false-absents (dotenv-load is `just`-scoped, `justfile:11`) and the file-probe false-absents in a worktree (`hook_project_dir` returns the worktree path, `lib.sh:20-23`); leave missing-key handling to the recipe's `_require-*` guard (`justfile:66-71,103-108`). Asymmetry → err toward DENY (false-deny = one `DEFERRED-HIL` + advance; false-allow = real money + locked-constraint breach).
- **Control output:** PreToolUse `permissionDecision:'allow'` for the named-recipe path; everything unlisted continues to deny/ask. Capability HOLDS: there is NO managed/settings `deny` key anywhere, so the deny-list is entirely in-script — in-script ORDERING (allow before `:176-180`) governs, and the §3.3 "allow cannot loosen a managed deny" caveat has no managed deny to fight. The sibling `precmd-clear-cache.sh` emits no permission decision (`:37`) → §3.4 most-restrictive merge does not override the allow.
- **Capability citation:** `claude-code-hooks.md §3.3:113-119` (PreToolUse `permissionDecision ∈ allow|deny|ask|defer`; allow cannot loosen managed deny — none exists here) + `§6:199` (PermissionRequest absent in `-p` → headless uses PreToolUse allow) + `:201` (PreToolUse deny unbypassable) + `§3.4:138-139` (deny>ask>allow).

**(d) Adversarial verdict + residual risk.** Verdict MODIFY (do not KEEP, do not REJECT). The core mechanism is capability-sound and faithful to the operator correction + the locked deny-list, but it MUST close the self-write hole (BLOCKER), anchor the final token, drop the bash-prefix, and log the row — then ratify option (i) and apply. Residual after all four fixes: the authorization surface is operator-curation ONLY (the loop cannot self-author the allowlist); arg-taking paid recipes fall to ask; each allowed paid run writes an `ALLOW-PAID` row; unlisted/raw paid surfaces stay hard-denied. Remaining: a named zero-arg recipe is costlier than believed (bounded, one-line tracked edit); the strictness check must be the `:151-156` copy VERBATIM; worktree-vs-main resolution of the allowlist fails safe to ask once ask-protected.

**(e) As-built anchors:** `permission-guard.sh:34,138-140,151-156,176-177,179-180,209-216,117-124`, `precmd-clear-cache.sh:37`, `run.sh:117`, `lib.sh:145-149,20-23`, `loop_lib.sh:75-83,91-94`, `justfile:11,13,26-27,66-71,103-108,115-116,99-100,123-124` (mvp-r300-ollama is FREE, never denied — prefer-free-ollama preserved), `settings.json:18-26,28-38` (0 `if:` clauses, NO `deny` key), `session-evidence.md:76-99`, `insights-report-2026-06-03.md:18-26`.

---

### D7 — autonomous git / worktree + cwd-safe hygiene (the 252-error class)

> **One enforcement story from three cluster proposals.** P3 (marker-coupled context-aware deny) is the principled core; P1 (always-on narrow deny) folds into it; P2 adds the create-time `git worktree add` guard P3 does not cover. The `.arc-worktree` marker lifecycle ships BEFORE the guards that read it.

**(a) Why it lapses.** Plan-intent (`inventory:83`, operator directive): cwd-safe autonomous git/worktree hygiene. As-built: MANUAL/UNGUARDED mid-loop — `loop_gc_worktrees` (`loop_lib.sh:271`) is reap/report ONLY; no create-time lifecycle, no cwd-split guard (grep: no cwd-split/git-`-C`-main deny in `tools/hooks/*.sh`). Evidence: a `cd <main> && git` ran in MAIN; the 252-fail Command-Failed class is the dominant tool-error class (`session-evidence.md:135-148`, `insights-report:42-46`); a reused misnamed worktree.

**(b) Disposition.** HOOK-ENFORCE (context-aware deny + create-time guard).

**(c) HOOK-ENFORCE.**
- **Core deny (P3 + P1): event + matcher** `PreToolUse`, matcher `Bash` — a NEW standalone hook (separate from permission-guard, so NOT gated by `loop_mode_active` — runs in every session). Reads a NEW `.harness/.arc-worktree` marker (abs-path + branch + base-SHA).
- **Check logic:** in-script read `.harness/.arc-worktree`. If absent → `exit 0` (**fail-open** — a missing marker NEVER enforces). Staleness self-heal: if the recorded path is missing OR the branch is not live → clear + `exit 0`. Else if `tool_input.command` is a state-mutating git op whose effective target tree != the recorded arc worktree (e.g. `git -C <main>` / `cd <main> && git commit` while the marker says we are in arc worktree X, verb ∈ commit|add|merge|push|reset|rebase|`checkout -b`) → `deny`. Always `exit 0` on parse failure. NOTE: read-only verbs (status|diff|log|rev-parse|`worktree list`) stay allowed, and the marker (not a blanket predicate) is what distinguishes a split BUG from a sanctioned cross-tree op (memory `deleting-active-worktree-from-within-session` mandates `git -C main` deletes; the hooks themselves use `git -C`, `lib.sh:117-118,125`).
- **Create-time guard (P2): event + matcher** `PreToolUse`, matcher `Bash` [PRIMARY — arc worktrees are created via raw `Bash(git worktree add)`, `settings.local.json:13` allowlists `Bash(git worktree *)`, `test_loop_gc.sh:40-45` uses it; `WorktreeCreate` fires ONLY for the native EnterWorktree path and MISSES the Bash path]. Inspect `tool_input.command` for `git\s+(-C\s+\S+\s+)?worktree\s+add`; validate the destination matches `.claude/worktrees/<arc-slug>` and does not reuse a live worktree → `deny`/normalize a malformed/duplicate path. SECONDARY: `WorktreeCreate` as a matcher-less (`claude-code-hooks.md:173` — no matcher support) backstop for the native path only.
- **Control output:** core deny → `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[arc-worktree] state-mutating git is targeting <tree> but the active arc worktree is <recorded>; operate in the arc worktree or close the arc first"}}`. Create guard → same shape with an `[arc-lifecycle]` reason. `WorktreeCreate` arm → `exit 2` + stderr OR top-level `{"decision":"block","reason":…}` (`claude-code-hooks.md §3.1:89` WorktreeCreate is in the exit-2 BLOCKS set).
- **Capability citation:** PreToolUse can block; deny tightens even in bypass (`claude-code-hooks.md:32,§3.3:107-119,:119,:201`); deny>ask>allow (`§3.4:138-140`); fires in `-p` headless (`:33`); Bash matcher = tool_name → inspect `tool_input.command` (`§4:168-174`); WorktreeCreate blockable but no matcher (`:51,§3.1:89,§4:173`).

**`.arc-worktree` marker lifecycle (mirrors `loop_activate`/`loop_deactivate`):** WRITE at arc start (record worktree abs-path + branch + base SHA), mirroring `loop_lib.sh:140-146`; REMOVE at arc close / PR merge (an in-scope ship-pr/loop-stop surface, OR `loop_gc` on reap of that worktree clears its marker), mirroring `loop_lib.sh:158-163`; SELF-HEAL on each read (verify the path exists + branch is live; else clear); FAIL-OPEN when absent. `loop_gc`'s `git worktree remove` (`loop_lib.sh:258`) can desync a stale marker — the self-heal/clear accounts for it.

**(d) Adversarial verdict + residual risk.** Verdict MODIFY (P3 is the principled superset of P1; P2's Bash arm is the load-bearing create-path guard, WorktreeCreate is a matcher-less secondary). Residual: fail-open (correct for false-positives) means the 252-class is NOT caught whenever no `.arc-worktree` marker is set (ad-hoc work outside a tracked arc) — state this to the operator; a missed REMOVE point reintroduces the stale-marker hazard; a worktree created by a mechanism that is neither Bash nor EnterWorktree misses both backstops; a correctly-named-but-wrong-base worktree is not caught by a naming-keyed predicate.

**(e) As-built anchors:** `permission-guard.sh:34` (existing guard is loop-gated → cwd guard must be SEPARATE), `loop_lib.sh:140-146,158-163,258,271-299`, `lib.sh:145-149,117-118,125`, `precmd-clear-cache.sh:24` (Bash hook reads `tool_input.command` in-script — the convention), `settings.local.json:13` (Bash `git worktree add` path), `test_loop_gc.sh:40-45`, `settings.json:141-161` (matcher-less `{hooks:[…]}` shape), `session-evidence.md:135-148`.

---

### D8 — §12.2 post-merge refresh + §12.2.1 fixed-point

**(a) Why it lapses.** Plan-intent (`inventory:76`, §12.2): a substantive merge owes a terminating refresh before the next substantive merge. As-built: MANUAL/toothless — `post-merge-refresh.sh:44-103` only INJECTS a checklist; nothing prevents merging PR #(N+1) while PR #N's terminating refresh is owed, so the dashboard drifts and the §12.1 hash audit (`session-start.sh:79-103`) later reports DRIFT. The D7 cwd-split also made the manual refresh error-prone (`session-evidence.md:135-148`).

**(b) Disposition.** HOOK-ENFORCE (deny the NEXT substantive `gh pr merge` until the prior owed refresh exists) — **merged with D1 into one ordered dispatcher (§4)**.

**(c) HOOK-ENFORCE.**
- **Event + matcher:** `PreToolUse`, matcher `Bash` (early-exit unless `gh +pr +merge`, the `post-merge-refresh.sh:44` pattern; sibling under the Bash matcher group, `settings.json:8-17`). Loop-gated (INERT in HIL).
- **Check logic:** on a `gh pr merge`: FIRST exempt if the target is the terminating refresh PR (reserved-prefix `ops: roadmap status refresh ` + dashboard-only, per `post-merge-refresh.sh:78-84`) → allow through. ELSE if origin/<default> advanced past the dashboard's pinned `git_head` to a non-refresh tip (`post-merge-refresh.sh:62-84`) AND no `.refresh-owed-<sha>` marker exists → `deny`. All git reads via `git -C "$PROJECT_DIR"` / `git ls-tree` at the merged ref (cwd-safe, `post-merge-refresh.sh:98-99`).
- **⚠️ MANDATORY — refresh-merge exemption (else self-deadlock).** The §12.2.1 terminating refresh itself lands as a REFRESH PR merged via `gh pr merge` (`ship-pr/SKILL.md:38-45`). At that instant origin is past dashboard-head at the prior substantive tip with NO marker — exactly D8's deny condition — so D8 as-written would DENY the very merge that clears the owed refresh. The live `PostToolUse` reminder in this session (PR #287 substantive merge, refresh now owed) is a concrete instance. **Fix:** the dispatcher's exemption arm above (detect the refresh PR by reserved-prefix + dashboard-only, allow unconditionally) MUST run first; equivalently/additionally write `.refresh-owed-<sha>` at the START of the refresh ritual, not on its success path.
- **Control output:** `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[refresh-gate] PR #N's terminating refresh is owed (§12.2.1) — land the dashboard-only refresh, or ACK with .refresh-owed-<sha>, before the next substantive merge"}}`. Composes via deny>allow over the sibling permission-guard allow.
- **Capability citation:** PreToolUse can block (`claude-code-hooks.md:32`); `permissionDecision:deny`, `tool_input.command` visible (`:107-119`); deny before permission-mode check, unbypassable (`:119,:201`); deny>ask>allow (`:138-141`).

**`.refresh-owed-<sha>` marker:** like D1/D7 markers, ask-protect it (extend the `permission-guard.sh:213-214` Edit|Write ask-carve) so the loop cannot self-author the ACK; keyed to the owed SHA; the operator chooses ACK-marker vs require-the-actual-refresh (§6).

**(d) Adversarial verdict + residual risk.** Verdict MODIFY: sound capability and a real toothless-advisory gap, but as-written the deny DEADLOCKS its own resolution; add the refresh-merge exemption (or write the marker before the refresh merge) before enforcing. Residual: a substantive merge mis-titled with the reserved refresh prefix could slip the gate (the same false-negative `post-merge-refresh.sh:77` documents — require the dashboard-only conjunct, not the title alone); the marker-vs-actual-refresh strictness choice trades §12.2.1 strictness for loop throughput.

**(e) As-built anchors:** `post-merge-refresh.sh:44,62-84,98-99`, `ship-pr/SKILL.md:38-45` (refresh lands via `gh pr merge` — the self-deadlock source), `permission-guard.sh:256` (`gh pr merge` allowlisted — new deny overrides via deny>allow), `:213-214` (ask-carve for the marker), `settings.json:8-17`, `session-evidence.md:135-148`.

---

### D9 — §12.1 session-start hash audit + §12.2.1 carve-out

**(a) Why it lapses.** It does not — AUTO and reliable. **(b) Disposition.** LEAVE-AS-IS (AUTO). **(c)** No change: `session-start.sh:49-103` computes the §12.1 hash, honors the §12.2.1 fixed-point carve-out (`:83-98`), guards behind-origin (`:69-77`), always `exit 0`. **(d)** Verdict KEEP — verified reliable. **(e)** `session-start.sh:49-103`, `settings.json:162-178`.

---

### D10 — posture check (§11)

**(a) Why it lapses.** Posture is a judgment-level stance re-asserted at skill entry; no lifecycle event fires "a posture check is due", and "posture honored" is not derivable from `tool_name`/`tool_input`/transcript shape on any event (`claude-code-hooks.md §1`). **(b) Disposition.** LEAVE-MANUAL. **(c)** The skill §0 preambles (`phase-7-implementation/SKILL.md`, `ship-pr/SKILL.md`, `council/*`) + CLAUDE.md §11 remain the carriers. A `type:prompt` Stop hook COULD LLM-grade it (`claude-code-hooks.md:186-194`, Haiku/30s) but would fire EVERY turn end → per-turn latency + a Haiku call + advisory noise → net-negative; rejected. **(d)** Verdict KEEP — not expressible as a deterministic hook; posture is a soft quality stance, not a safety invariant (those are separately hook-enforced); residual = silent posture lapses, bounded. **(e)** `phase-7-implementation/SKILL.md`, `ship-pr/SKILL.md`, `claude-code-hooks.md:186-194`.

---

### D11 — memory hygiene (cardinality≥2, 24,400 B cap, verify-before-conclude)

**(a) Why it lapses.** Detection is NOT the gap — `loop-gc.sh:54-57` already emits a SessionStart `additionalContext` when `MEMORY.md` > 24,400 B (portable memory path `:47-53`), and the session-end report carries it. The gap is that detection has no teeth (soft `additionalContext` the model has ignored — `MEMORY.md` is **25.6 KB > 24.4 KB right now**). `capture-failure.sh:43-45` nudges only on tool/API failure recurrence, not the memory-owed/verify-before-conclude disciplines.

**(b) Disposition.** HOOK-ENFORCE (strengthen the EXISTING SessionStart surface to imperative when materially over cap). The correct ceiling: SessionStart CANNOT block (`claude-code-hooks.md:28`) — the strongest lever is an imperative line, not a hard gate.

**(c) HOOK-ENFORCE.**
- **Event + matcher:** `SessionStart` (strengthen `loop-gc.sh:54-57`), matcher `*` (`settings.json:162-177`); optionally `UserPromptSubmit` (no matcher; `prompt-context.sh` already wired, `settings.json:141-160`).
- **Check logic:** keep cap detection as-is. When `MEMORY.md` exceeds the cap by a material margin (>~26,000 B), escalate the `additionalContext` from a passive flag to an imperative first-action ("`MEMORY.md` is <SZ> B and being TRUNCATED — compact the index NOW: one line <200 chars, move detail to `memory/<slug>.md`"). For the cardinality half, extend `capture-failure.sh`'s signature log + reuse its ≥2 nudge (`capture-failure.sh:43-45`).
- **Control output:** SessionStart `additionalContext` (`claude-code-hooks.md:135`) — imperative phrasing. NOT a block (SessionStart non-blockable, `:28`).
- **Capability citation:** `claude-code-hooks.md:28` (SessionStart cannot block), `:135` (SessionStart `additionalContext`), `:88` (SessionStart/UserPromptSubmit plain-text injected).

**(d) Adversarial verdict + residual risk.** Verdict KEEP — strengthen the existing surface to imperative phrasing (the correct ceiling), reuse `capture-failure`'s ≥2 nudge; no safety surface touched. Residual: the cap stays ignorable (the loader truncates independently of any hook — proven by the current over-cap state); only the model actually compacting (or `/optimize-claude-md`) fixes it; verify-before-conclude stays a reasoning discipline, not a detectable event. Keep the imperative a single line, not a hard gate (which SessionStart cannot be anyway).

**(e) As-built anchors:** `loop-gc.sh:54-57,47-53`, `session-end-cleanup.sh`, `capture-failure.sh:43-45`, `ship-pr/SKILL.md:53`, `optimize-claude-md/SKILL.md`.

---

### D12 — completeness-by-execution before "done"

**(a) Why it lapses.** Plan-intent (`inventory:86`, §13.1): before declaring complete, completeness shown by EXECUTION (ran tests / `just check` / the workflow), not asserted. As-built: MANUAL. Evidence (`session-evidence.md:74`): the session declared `result:` while DEFERRING the live confirmation; codex-review (an execution gate) was skipped/stalled on both merges (`session-evidence.md:14-27`).

**(b) Disposition.** HYBRID — shares the D2 Stop nudge (ONE hook); skill-strengthen PRIMARY.

**(c) Fixes.**
- **SKILL-STRENGTHEN (command-agnostic, ship FIRST):** `ship-pr/SKILL.md:14` → hard pre-condition "do not declare shippable until `just check` RAN GREEN this arc (execution, not assertion)"; `roadmap-continue/SKILL.md:27-28` step-4 → "before reporting done, confirm the suite/`just check` actually executed; a deferred live run is NOT completeness (session-evidence D4)"; cross-ref self-heal (`inventory:61`).
- **HOOK-ENFORCE (the D2+D12 SHARED Stop hook — see §4):** extend the D2 pre-done hook (do NOT add a separate hook). After the same loop-guard + done-signal regex + transcript-tail read: ALSO scan the turn-tail for an EXECUTION signal — a Bash `tool_use` whose `.input.command` matches `/\bjust\s+(check|test|codex-review|mvp-)/` OR `/\b(pytest|uv run … pytest)\b/` OR `/\bbash -n\b/`. Compose: done-declared AND no advisor/codex `[advisor via (tool_use|server_tool_use)]` → include the D2 reviewer line; done-declared AND no execution signal → include the D12 completeness line; BOTH ran → `exit 0` silent. Fail-open silent on shape mismatch. D12's execution-detection arm is SOUND as-written (Bash serializes as `type==tool_use` with `.input.command`); the **inherited** bug is the D2 reviewer line's advisor matcher — same `server_tool_use` fix.
- **Control output:** `hookSpecificOutput.additionalContext` (ADVISORY, `exit 0`, NEVER block). D12 line: completeness by EXECUTION not assertion ("if you ran it earlier this arc or it is non-code, ignore; else run the suite/`just check` before closing").
- **Capability citation:** identical to D2 — `claude-code-hooks.md:130,238,205-207`. Execution-command grep mirrors `permission-guard.sh:42` inspecting Bash `tool_input.command`.

**(d) Adversarial verdict + residual risk.** Verdict MODIFY: D12's own execution arm is sound, but it SHARES the D2 Stop hook and therefore inherits the broken advisor matcher — require the same `(tool_use|server_tool_use)` fix; ship the command-agnostic skill-strengthen first. Residual: cross-turn-execution false negative (a test run an earlier turn of the same arc won't appear in this turn's tail — mitigated by "if you already ran it earlier, ignore"); false-positive on a pure-docs/dashboard-refresh "done" (mitigated by the tight done-regex + "if non-code, ignore"); execution-regex staleness (covered by the command-agnostic skill-strengthen). One shared hook with one composed emission is strictly better than two hooks racing two `additionalContext` emissions. No safety residual.

**(e) As-built anchors:** `inventory:86`, `session-evidence.md:74,14-27`, `subagent-validate.sh:39,54,57-68`, `permission-guard.sh:42` (Bash `tool_input.command` inspection precedent), `ship-pr/SKILL.md:14`, `roadmap-continue/SKILL.md:27-28`.

---

### D13 — empirical cite-grounding + cross-spec drift grep

**(a) Why it lapses.** Plan-intent (`inventory:87`, §13.1/§10.4): every spec/§ citation grounded by an adjacent empirical read/grep at HEAD, plus a cross-spec drift grep before relying on a cross-document claim. As-built: MANUAL, the LEAST detectable of the cluster. The would-be signal ("cited a §/spec without an adjacent grep") is saturated as NORMAL prose in this doc-heavy workspace (MEMORY.md is wall-to-wall §-cites; CLAUDE.md §-pointers; R-NNN refs in most governance turns) → a torrent of false positives; "adjacent grep" is undefinable at transcript level (a grounding Read can precede a cite by several turns).

**(b) Disposition.** LEAVE-MANUAL. **(c)** Strengthen the SKILL backstop: `roadmap-continue/SKILL.md:23` "Ground first" → "when you cite a spec/§/contract, READ it at HEAD in the same step (`wrong-version-read-delta-only-baseline`, `design-substrate-version-identity-hazards`); do not cite from memory"; `ship-pr/SKILL.md:17-19` → "if the change relies on a cross-document claim, grep BOTH documents at HEAD for drift before relying on it (§10.4)"; reinforce "cite = read-at-HEAD" in the doc-authoring roles (spec-writer/implementation-planner/systems-architect). The well-defined wrong-VERSION slice (stale-cache reads) is ALREADY auto-guarded by `precmd-clear-cache.sh` (U-HK-02, `settings.json:11-17`) and the §12.1 hash-drift audit via `session-start.sh` (U-HK-28, `settings.json:162-178`).

**(d) Adversarial verdict + residual risk.** Verdict KEEP (leave-manual). A desensitizing FP-heavy hook costs more than an occasional ungrounded cite AND would degrade the D2/D12 nudge's credibility on the shared Stop surface; the highest-blast-radius version (wrong-VERSION reads) is already covered by U-HK-02 + U-HK-28; residual bounded to human-judgment grounding. **OUT-OF-SCOPE note:** a narrow phantom-cite `PostToolUse(Edit|Write)` variant (fire when an edit INSERTS a new §/contract cross-reference to a design-substrate file ABSENT at HEAD) is capability-valid and high-precision BUT touches **design-substrate reference checking → SCOPE VIOLATION** for this U-HK machinery; it is listed only as a flagged out-of-scope future item in §6, NOT built here.

**(e) As-built anchors:** `inventory:87`, `settings.json:11-17,162-178`, `precmd-clear-cache.sh`, `roadmap-continue/SKILL.md:23`, `ship-pr/SKILL.md:17-19`.

---

### D14 — output-token-limit resilience / loop durability

> **Unified across two clusters.** Cluster 3 (durability/recovery — HYBRID) + cluster 5 §14.5 (chunked writes — SKILL-STRENGTHEN). The two failure modes are correctly kept separate: (a) CONTEXT-window fill (already covered by `context-recovery.sh:23-39` at 60/75/85%) vs (b) OUTPUT-token-cap truncation of a single response (the D14 gap). CRUX: an output-cap hit is an API error that ends the turn via `StopFailure` (`claude-code-hooks.md:39` — "Output & exit code IGNORED"), NOT via Stop — so recovery cannot come FROM StopFailure output, and no event exposes a running output-token count, making the "bias-to-concise / checkpoint-when-long" trigger genuinely unhookable (→ skill).

**(a) Why it lapses.** Plan-intent (§14.4/§14.5, `insights-report:53-68`): per-step durability + concise/chunked writes so an output-cap truncation never loses iteration state. As-built: MANUAL — `run.sh:119` only logs the FAILURE path (success writes no durable per-iteration row); the Stop continue path (`stop-loop.sh:82-95`) calls NO `hook_write_checkpoint`; `session-start.sh` and `prompt-context.sh` read NEITHER `session-issues.jsonl` NOR the checkpoint (no post-truncation recovery). ≥6 sessions hit output-cap errors making work unrecoverable for review.

**(b) Disposition.** HYBRID (durable checkpoint + targeted recovery) + SKILL-STRENGTHEN (§14.5 chunked writes).

**(c) HOOK-ENFORCE / runner edits (cluster-3 Pieces A, B, C).**
- **Piece A — Stop checkpoint:** extend `stop-loop.sh` to call `hook_write_checkpoint "loop turn ${ITER}/${MAX} progress" skip_gh` on the continue path (after the iteration-cap check, near `:82-83`, BEFORE the `jq` emit at `:95`), behind `loop_mode_active` (`:44`). LOAD-BEARING: `hook_write_checkpoint` is STDOUT-SILENT (`lib.sh:110-138` — every write is captured or redirected) so it cannot corrupt the `decision:block` continuation JSON; it adds NO new Stop block (rides the EXISTING block path) → the 8× cap and never-halt are untouched.
- **Piece B — targeted post-truncation recovery:** extend `session-start.sh` (headless) + `prompt-context.sh` (interactive) to read the StopFailure breadcrumb and, only if a RECENT StopFailure row exists, re-inject the `precompact-latest.md` pointer. **⚠️ MANDATORY trigger fix:** change the grep from the unverified `'"error_type":"max_output_tokens"'` (`error_type` is NOT a documented capability-ref field) to the DOCUMENTED `'"event":"StopFailure"'` (the row's event = `.hook_event_name` at `capture-failure.sh:26`; `hook_event_name` IS a common field, `claude-code-hooks.md §2:79`). Strictly fail-safe — also fires on rate_limit/auth StopFailures, where re-injecting the last-checkpoint pointer is equally harmless. FRESHNESS-SCOPE by the row's `ts` (`capture-failure.sh:31`); headless, additionally bound to rows newer than the run's ACTIVATE.
- **Piece C — runner ledger:** `run.sh` after `wait "$CHILD"`, add a success-path `loop_log COMPLETED "iteration ${i} finished"` (today only the failure path logs, `:119`). No hook involved.
- **Control output:** Piece A KEEPS the existing `{"decision":"block","reason":…}` (`claude-code-hooks.md §1:38`); checkpoint is a stdout-silent side effect. Piece B-headless: SessionStart `additionalContext` (`§3.3:135`; cannot block — correct); Piece B-interactive: UserPromptSubmit `additionalContext` (`§3.3:133`). NO StopFailure output relied on anywhere (its inertness respected, `:39`).
- **Capability citation:** `claude-code-hooks.md §1:38` (Stop decision:block continues) + `:39` (StopFailure output IGNORED), `§2:79` (`hook_event_name` is the documented field the FIXED trigger uses — `error_type` is NOT in the ref), `§3.3:129/133/135`, `§4:174` (UserPromptSubmit no matcher), `§6:205` (8× cap untouched — Piece A adds no new block).

**(c′) SKILL-STRENGTHEN (cluster-5 §14.5).** `loop-start` + `roadmap-continue` + `ship-pr`: add a §14.5 durability clause — write large artifacts in CHUNKS (create then append), persist progress to a durable file after each sub-step so an output-cap truncation never loses iteration state, keep responses concise (CLAUDE.md §14.4/§14.5, verbatim source). The U-HK-05 PreCompact + U-HK-27 statusLine checkpoint substrate is the existing safety net.

**(d) Adversarial verdict + residual risk.** Verdict MODIFY then build: Pieces A (cap-safe) + C + the skill discipline are sound and high-leverage; Piece B is mandatory-fixed by triggering on `"event":"StopFailure"` with a freshness window (without it Piece B delivers ZERO recovery while appearing wired). Residual: the in-flight-turn loss window (Piece A cannot save the truncating turn) is irreducible — no hook intercepts an in-flight truncation; the only further lever is the SKILL discipline (correctly routed to the skill); interactive recovery stays best-effort; breadcrumb staleness across same-worktree sessions bounded by the freshness window. All acceptable. No safety residual (no permission decisions, no deny-list/never-halt/defer/ollama surface).

**(e) As-built anchors:** `run.sh:119,116-118`, `stop-loop.sh:44,82-95`, `lib.sh:110-138`, `precompact-checkpoint.sh:28`, `context-recovery.sh:23,27-39`, `capture-failure.sh:26,28,31,34-36,38-41`, `postcompact-reinject.sh:28-31`, `session-start.sh` (reads neither breadcrumb nor checkpoint), `prompt-context.sh` (reads neither), `settings.json:96-117,162-178,141-160`, `.gitignore:89,92,96,97`, `CLAUDE.md:756-757` (§14.4/§14.5 verbatim).

---

### §14.2 — AskUserQuestion not bare [y/n]

**(a) Why it lapses.** `insights-report-2026-06-03.md:48-51` records recurring text-based `[y/n]` across 2+ sessions requiring user correction; no hook detects a Claude-authored `[y/n]` today.

**(b) Disposition.** HOOK-ENFORCE (low-FP advisory nudge; NEVER blocks).

**(c) HOOK-ENFORCE.**
- **Event + matcher:** `Stop` (fold into stop-loop's reason, loop) AND/OR `UserPromptSubmit` (HIL, cheaper next-turn injection; `prompt-lint.sh` already there, `settings.json:141-160`), no matcher.
- **Check logic:** detect a Claude-authored interactive `[y/n]` in the last assistant message via `transcript_path`: regex `\[y/n\]` / `\(y/n\)` / "type yes or no" near a question mark, EXCLUDING quoted/code-fenced spans and `prompt-lint.sh`'s curated idiom set (mirror its conservatism, `prompt-lint.sh:9-13,38-53`). Append a one-line §14.2 nudge (use AskUserQuestion in HIL or `/resolve`+`defer.sh` in loop). Pure advisory — NEVER `decision:block` on its own.
- **Control output:** `additionalContext` (Stop via the existing block reason, `claude-code-hooks.md:129-130`; or UserPromptSubmit `additionalContext`, `:88`). NOT `decision:block`.
- **Capability citation:** `claude-code-hooks.md:68` (`transcript_path`), `:88` (UserPromptSubmit/PostToolUse plain-text injected), `:129-130` (Stop `additionalContext`).

**(d) Adversarial verdict + residual risk.** Verdict KEEP — a clean low-FP advisory; mirror `prompt-lint.sh`'s conservatism, never block, keep ONE-SHOT to avoid compounding with the D4 prefix in stop-loop's reason. Residual: occasional false nudge on a documented/quoted `[y/n]` (bounded to one advisory line); the skill (§14.2 in loop-start/roadmap-continue) is primary.

**(e) As-built anchors:** `prompt-lint.sh:9-13,38-53` (the conservative exact-match pattern to mirror; `settings.json:155-158`), `insights-report-2026-06-03.md:48-51`.

---

### §14.4 / §14.5 — incremental / chunked writes

**(a) Why it lapses.** §14.4/§14.5 exist because heredoc/base64 Bash writes truncate on large files and one-giant-response writes hit the output cap, but nothing detects the anti-pattern at the moment it is attempted.

**(b) Disposition.** SKILL-STRENGTHEN (folds into D14's skill clause). **The heredoc/base64 mega-write advisory HOOK is REJECTED — see §6 rejection register.**

**(c) SKILL-STRENGTHEN.** Carried by the D14 §14.5 clause in `loop-start` / `roadmap-continue` / `ship-pr` + the CLAUDE.md §14.4/§14.5 convention (`CLAUDE.md:756-757`).

**(d) Adversarial verdict + residual risk.** The proposed PreToolUse(Bash) `additionalContext` nudge is REJECTED on **capability**: the per-event ref sections do NOT grant PreToolUse a context-injection output — `§3.1:88` scopes plain-text stdout injection to UserPromptSubmit/SessionStart/PostToolUse* and lists PreToolUse SEPARATELY only as "exit 0 + empty = no decision"; `§3.3:129-135` enumerates the `additionalContext` injectors and PreToolUse is ABSENT (its schema `:108-119` exposes only `permissionDecision`/`permissionDecisionReason`/`updatedInput`); the sole support is the generic `§3.2:98`, contradicted by the per-event detail. RELOCATION DOES NOT SAVE IT: PostToolUse(Bash) DOES support `additionalContext` (`§3.3:129`) but fires AFTER the write executed and truncated (`:35`) — too late to steer pre-write. No in-scope event both fires pre-write AND injects advisory context. Fallback: the §14.5 skill discipline + CLAUDE.md convention cover it with no safety or durability regression.

**(e) As-built anchors:** `CLAUDE.md:756-757`, `claude-code-hooks.md:88,129-135,108-119,98,35`, `lib.sh:145-149` (the loop-mode gate the rejected hook would have used).

---

## 4. CROSS-CUTTING HOOK RECONCILIATION

The as-built ALREADY wires THREE Stop hooks in order (`settings.json:96-117`) — `stop-gate.sh`(45s) → `git-arc-guard.sh`(20s) → `stop-loop.sh`(20s) — and PreToolUse = `precmd-clear-cache.sh`(Bash) + `permission-guard.sh`(*). Multiple disciplines target the SAME event. They must combine into this wiring without (i) exhausting the 8× Stop-block override cap, (ii) two hooks rewriting the same `updatedInput`, or (iii) fighting each other (PreToolUse most-restrictive-wins).

### 4.1 Stop event — {D2 pre-done, D4 never-halt, D12 completeness, §14.2} + the existing 3

**Critical cap fact (corrects a recurring cluster assumption):** the 8× `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` is a SHARED budget over consecutive no-progress `decision:block` emissions. Of the three existing Stop hooks, only TWO can block: `stop-gate.sh` (lint `decision:block`) and `stop-loop.sh` (continuation `decision:block`). `git-arc-guard.sh:13,69-70` emits `systemMessage` ONLY and checks `stop_hook_active` (`:31`) — it NEVER blocks and does NOT consume the cap. **After hardening there are still exactly TWO blocking Stop emitters.**

Resolution:
- **D2 + D12 + §14.2 advisory nudges → ONE merged advisory-Stop script** (a 4th Stop hook, wired after stop-loop). It emits `hookSpecificOutput.additionalContext` with `exit 0` and **NEVER `decision:block`** → it does NOT add a blocking competitor and does NOT consume the 8× cap (`claude-code-hooks.md:205-207`). One script composes the (corrected) advisor/codex scan (D2 reviewer line), the execution scan (D12 completeness line), and the `[y/n]` scan (§14.2 nudge) into a SINGLE emission — avoiding two/three hooks racing separate `additionalContext` emitters. NB execution is PARALLEL, not sequential (`claude-code-hooks.md:24`); "after stop-loop" is wiring order in settings.json, not a runtime sequence — `additionalContext` concatenates regardless (`:140`). All three sub-scans require the corrected `(.type=="tool_use" or .type=="server_tool_use")` advisor matcher.
- **D4 never-halt → folded into the EXISTING `stop-loop.sh` block** (NOT a new hook). It rides stop-loop's existing `decision:block` continuation as a ONE-SHOT reason prefix and then falls back to the generic advance, so it adds NO new blocker and cannot stack identical-no-progress blocks toward the cap. **It does NOT add the `stop_hook_active` early-exit** (§3 D4 correction) — that would break never-halt at turn 2.
- **Anti-compounding:** the D4 one-shot prefix (in stop-loop's reason) and the §14.2 nudge (in the merged advisory script's `additionalContext`) live in DIFFERENT emissions; keep each one-shot so a stuck item does not bloat the continuation and desensitize the reader.

Net Stop wiring: `stop-gate`(block) → `git-arc-guard`(systemMessage) → `stop-loop`(block, now with the D4 one-shot prefix) → `merged-advisory`(additionalContext, exit 0). Blocking emitters: still exactly 2.

### 4.2 PreToolUse(Bash) — {D1 gh-pr-merge gate, D6 paid-call, D7 cwd-split, D8 refresh-gate} + the existing permission-guard

PreToolUse most-restrictive-wins: **deny > ask > allow** (`claude-code-hooks.md §3.4:138-140`). The existing `permission-guard.sh` emits at most one decision; `precmd-clear-cache.sh` emits none (`:37`). New denies from a sibling hook OVERRIDE permission-guard's `allow` (including the `gh pr merge` allowlist entry at `:256`) — which is exactly the intended tightening. Resolution by **clearly separated detection so no two hooks decide the same call**, plus ONE merge dispatcher where two disciplines genuinely gate the same command:

- **D1 + D8 gate the SAME command (`gh pr merge`) → ONE ordered `gh-pr-merge` dispatcher** (a NEW sibling under the Bash matcher group). Order: (1) if the target is the terminating refresh PR (reserved-prefix + dashboard-only) → ALLOW through (the D8 self-deadlock exemption, MUST be first); (2) ELSE check the D1 codex marker for HEAD — PASS (`.codex-pass-<sha>`) → continue; KILLED-WITH-CAVEAT (`.codex-caveat-<sha>`) → allow + loud `systemMessage` (never-halt-safe, ledger-tracked, never a silent pass); ABSENT or stale-SHA → `deny` (D1); (3) ELSE if a prior substantive refresh is owed and unACKed → `deny` (D8). One script, one decision per merge — never two competing denies. Loop-gated (D8 arm); D1's marker-gate may run in every session or loop-gated per the operator's choice (§6).
- **D7 cwd-split / arc-worktree → a SEPARATE standalone hook** (always-on, NOT loop-gated — it must enforce in interactive sessions too). It decides only state-mutating git ops whose target tree mismatches the `.arc-worktree` marker, and `git worktree add` destination validation. It NEVER decides a `gh pr merge` (different command class) → no overlap with the D1+D8 dispatcher.
- **D6 paid-call → folded INTO `permission-guard.sh`** as a narrow allow short-circuit BEFORE its own paid-deny (`:176-180`), applied ONLY post-ratification (§6). It decides only `just <named-recipe>` (final-token-anchored, zero-arg) — a command class neither the D1+D8 dispatcher nor the D7 hook touches. Because it lives inside permission-guard, there is no cross-hook `allow`-vs-`deny` race on the same call; and a sibling deny (none target `just <recipe>`) would still win by most-restrictive if one ever did.
- **No `updatedInput` collisions:** none of these hooks rewrite `updatedInput` — D1/D6/D7/D8 emit `deny`/`allow` decisions only, never `updatedInput`, so the "last-to-finish-wins" non-determinism (`§3.3:118`) cannot arise.
- **Marker-write safety (shared across D1/D7/D8):** every NEW marker (`.harness/.codex-pass-<sha>`, `.harness/.codex-caveat-<sha>`, `.harness/.arc-worktree`, `.harness/.refresh-owed-<sha>`) and the D6 `.harness/paid-allowlist.txt` MUST be ask-protected by extending the Edit|Write ask-carve at `permission-guard.sh:213-214`, so the loop cannot self-author (via a direct Write/Edit/Bash-redirect tool call) the artifact that authorizes its own merge/paid-call. **Security model:** the legitimate marker-WRITERS — the `just codex-review-gated` runner (D1), and the arc-lifecycle / `ship-pr` / `loop-gc` surfaces (D7/D8) — are the sanctioned paths and must themselves be allowlisted (e.g. add `codex-review-gated` to the permission-guard `just` allowlist, `:256`) so the loop can EARN a marker by actually running the review/refresh; only DIRECT tool-writes of a marker are ask-gated, which is exactly what blocks fabrication. The `.codex-caveat-<sha>` marker is included because it grants the allow-with-caveat MERGE BYPASS — an un-ask-protected caveat marker would let the loop self-author a review-skip. This is the single most important cross-cutting safety invariant of the whole plan.

---

## 5. ORDERED IMPLEMENTATION SEQUENCE

High-leverage × low-risk first; one-unit-per-PR; each unit ships with a NAMED hermetic `test_*.sh` fixture mirroring the U-HK test pattern (e.g. `test_stop_loop.sh`, `test_permission_guard.sh`, `test_subagent_validate.sh`). New ids U-HK-30…U-HK-44.

| Unit | Discipline | One-line scope | Hermetic test | Leverage | Risk | Deps |
|---|---|---|---|---|---|---|
| **U-HK-30** | D14 Piece A+C | per-step durable checkpoint on stop-loop continue (stdout-silent) + run.sh success-path `loop_log` | `test_stop_loop_checkpoint.sh`: synthetic loop turn → assert `precompact-latest.md` written + continuation JSON intact | high | low | — |
| **U-HK-31** | D7 cwd-split | ask-carve the NEW markers at permission-guard.sh:213-214 (`.arc-worktree`, `.codex-pass-*`, `.codex-caveat-*`, `.refresh-owed-*`, `paid-allowlist.txt`) — the shared self-write guard | `test_permission_guard_marker_carve.sh`: loop Edit of each marker → assert falls to ask (no emit_allow) | high | low | — |
| **U-HK-32** | D7 arc-worktree | `.arc-worktree` marker lifecycle (write/remove/self-heal/fail-open) mirroring loop_activate | `test_arc_worktree_marker.sh`: write→stale path→assert self-heal clears; absent→assert no-op | high | low | U-HK-31 |
| **U-HK-33** | D7 cwd-split | standalone PreToolUse(Bash) context-aware deny (state-mutating git vs marker; create-time `git worktree add` guard) | `test_cwd_split_guard.sh`: `git -C <main> commit` w/ worktree marker → deny; `git status` → allow; legit `git -C main` per memory → allow when no marker | high | med | U-HK-32 |
| **U-HK-34** | D1 codex-gate | gated `codex-review-gated` runner: diff-scoped `--base`, assert resolved model == gpt-5.5 (else abort, no marker), `timeout`→kill-with-caveat; writes `.codex-pass-<sha>` OR `.codex-caveat-<sha>` (SHA-keyed, self-heal) | `test_codex_review_gated.sh`: clean→pass marker; model-mismatch→abort+no marker; timeout→caveat marker; SHA A then HEAD=B→ignored | high | low | U-HK-31 |
| **U-HK-35** | D1 + D8 | ONE ordered `gh pr merge` dispatcher (refresh-PR exempt → codex PASS allow / CAVEAT allow+loud / ABSENT deny → refresh-owed deny) | `test_gh_pr_merge_gate.sh`: refresh PR→allow; no marker→deny; caveat marker→allow+systemMessage; owed refresh→deny; all clear→allow | high | med | U-HK-34, U-HK-31, U-HK-41 |
| **U-HK-36** | D8 refresh-owed | `.refresh-owed-<sha>` marker (write-at-ritual-start or ACK) + dashboard-only recognizer reuse | `test_refresh_owed_marker.sh`: substantive merge sets owed; refresh lands → cleared | med | low | U-HK-35 |
| **U-HK-37** | D4 never-halt | fold premature-halt detector into stop-loop.sh (stdin/transcript read; one-shot prefix; **NO `stop_hook_active`**) | `test_stop_loop_neverhalt.sh`: synthetic `result: deferred` w/ units remaining → assert one-shot prefix; turn-2 → assert still continues (never-halt holds) | high | med | U-HK-30 |
| **U-HK-38** | D2+D12+§14.2 | ONE merged advisory-Stop nudge (corrected `server_tool_use` matcher; reviewer+execution+`[y/n]` scans; additionalContext, never block) | `test_stop_advisory_nudge.sh`: done + no advisor → nudge; done + `server_tool_use` advisor → silent; done + `just check` Bash → execution silent | high | med | — |
| **U-HK-39** | D11 memory | escalate loop-gc.sh SessionStart surface to imperative >~26 KB; extend capture-failure ≥2 cardinality nudge | `test_loop_gc_memory_cap.sh`: 27 KB MEMORY.md → imperative additionalContext; 24 KB → passive/none | med | low | — |
| **U-HK-40** | D14 Piece B | post-truncation recovery in session-start.sh + prompt-context.sh (trigger `"event":"StopFailure"` + freshness window) | `test_stopfailure_recovery.sh`: recent StopFailure row + checkpoint → re-inject pointer; stale/none → silent | high | low | U-HK-30 |
| **U-HK-41** | D2/D3/D5/D12/D13/D14/§14.5 skills | skill-strengthen pass (loop-start, roadmap-continue, ship-pr, resolve, doc-authoring roles) — command-agnostic, zero-risk | `test_skill_strengthen.sh` (grep assertions on SKILL.md clauses) OR doc-only review | high | low | — |
| **U-HK-42** | insights-residue (no D-finding) — postedit-lint | YAML parse branch (`*.yaml`/`*.yml`, `.venv`-python `safe_load_all`, advisory) | `test_postedit_lint.sh` (cases 7–11) | med | low | — |
| **U-HK-43** | insights-residue (no D-finding) — subagent-validate | subagent registry JSONL append (start/stop, atomic single-line) | `test_subagent_validate.sh` (+5) | med | low | — |
| **U-HK-44** | insights-residue (no D-finding) — loop-gc | unreconciled-subagent sweep + 7d prune in `[hygiene]` report | `test_loop_gc.sh` (+3) | med | low | U-HK-43 |
| **U-HK-D6** | D6 paid-call | (HELD) narrow operator-named allowlist short-circuit + 4 required mods — **applied ONLY post-ratification** | `test_paid_allowlist_gate.sh`: listed zero-arg recipe → allow+ALLOW-PAID row; `<recipe> extra` → ask; unlisted/raw → deny | high | high | §6 ratification, U-HK-31 |

Notes: **U-HK-41 (skill-strengthen) and U-HK-30 (durability) are the cheapest high-leverage wins — ship them first** (the skill pass is the PRIMARY fix for D2/D3/D5/D12/D13 and is zero-risk; U-HK-30 is cheap loss-window insurance). The D1 marker-gate (U-HK-34/35), D7 cwd-guard (U-HK-31→33), and the D4/D2 Stop work follow. **Ordering invariant:** the D1 deny-gate (U-HK-35) must NOT land before U-HK-34 (the runner that earns the marker) AND U-HK-41's D1 clause (which teaches the loop to RUN `codex-review-gated`) — else a strict-DENY denies the first merge with no taught path to satisfy it; hence U-HK-35 deps both. **U-HK-D6 is gated on the §6 ratification point and is NOT applied until then.**

---

## 6. OPERATOR-DECISION REGISTER

Batched so the operator answers once.

### DECISION-1 (HEADLINE) — D6 loop-mode paid-call authorization

**Decision:** how does the guard distinguish an *authorized* loop-mode paid run from an *unauthorized* one, WITHOUT a blanket creds-present allow (forbidden by `feedback-background-agent-no-unilateral-paid-calls`)? The guard change is NOT applied until this is decided. The deny-list stays as the unauthorized backstop in every option.

- **(i) Narrow per-recipe operator-named allowlist [RECOMMENDED].** Authorization = (loop active) AND (target ∈ an operator-seeded, ask-protected, zero-arg recipe allowlist), matched as the final token. *Blast radius:* false-allow is bounded to the finite curated set (a one-line tracked edit to add/remove); the loop cannot self-author it (ask-protected per U-HK-31); each allowed run writes an `ALLOW-PAID` ledger row. This is the only option faithful to BOTH the operator correction AND the locked no-unilateral-paid constraint.
- **(ii) Loop-created marker — DISQUALIFIED (self-authorization).** A marker the loop can write is exactly the self-write hole the D6 cluster found for `paid-allowlist.txt`. *Blast radius:* unilateral paid spend during the unattended run, before any PR review → defeats the locked constraint. Do not adopt.
- **(iii) One audited wrapper recipe.** A single `just`-recipe wrapper that runs a paid call with mandatory ledger logging. *Blast radius:* folds into (i) (the wrapper is the one allowlisted recipe); simpler surface but less granular than per-recipe curation.

**Recommendation: (i)**, applied ONLY after ratification and ONLY with the four required modifications (ask-protect the allowlist [BLOCKER], final-token anchor, drop the bash-prefix, add the `ALLOW-PAID` row). Asymmetry → err toward DENY: false-deny = one `DEFERRED-HIL` + advance (never-halt preserved); false-allow = real money + locked-constraint breach. Do NOT gate on cred-presence (env-probe and file-probe both false-absent in the loop's worktree).

### DECISION-2 — D1 codex-gate strictness + scope

- **(a) Absent-marker behavior:** strict DENY (recommended — err toward review) vs fail-open allow. *Blast radius:* strict = an arc whose codex pass was genuinely run but whose marker write was skipped costs one friction prompt; fail-open = a merge can slip with no decorrelated review (the current lapse).
- **(b) Gate scope:** loop-only vs every session. *Recommendation:* loop-only initially (matches the autonomy surface), widen if interactive merges also skip review.
- **(c) Killed-with-caveat policy:** allow-with-loud-`systemMessage` + `loop_log CODEX-CAVEAT` row (RECOMMENDED — never-halt-safe; a recurring caveat cardinality is itself the signal that codex is broken) vs strict DENY on caveat (maximal review rigor, but can deadlock a genuine codex stall against never-halt).
- **(d) Model assertion:** confirm the intended out-of-family reviewer model is `gpt-5.5` (config.toml default, `justfile:205-209`) and that a model-mismatch HARD-ABORTS the review with no pass marker written (RECOMMENDED — closes the gpt-5.4 profile-shadow bug).

### DECISION-3 — D8 refresh-owed strictness

- ACK-marker (`.refresh-owed-<sha>` written at ritual start, then the next merge proceeds) vs require-the-actual-dashboard-only-refresh-commit before the next substantive merge. *Blast radius:* require-the-refresh most directly enforces §12.2.1 but adds loop friction; ACK trades strictness for throughput. **Either way the refresh-PR-merge exemption is mandatory** (else the gate deadlocks its own resolution). *Recommendation:* require-the-refresh (the dashboard drift this prevents is the §12.1 audit's DRIFT report).

### DECISION-4 — D11 memory-cap framing + threshold

- Confirm the material-over-cap escalation threshold (e.g. >26,000 B) and whether imperative compaction is a REQUIRED first loop action (by convention) vs advisory. *Note:* `MEMORY.md` is over-cap NOW (25.6 KB), which argues for the stronger framing — but it remains advisory at the hook layer (SessionStart cannot block, `claude-code-hooks.md:28`).

### REJECTION REGISTER (disciplines whose proposed HOOK is rejected — fallback recorded, never silently dropped)

- **§14.5 heredoc/base64 mega-write advisory hook → REJECTED on capability** (no in-scope event both fires pre-write AND injects `additionalContext`; PreToolUse lacks the output, PostToolUse fires too late). **Fallback:** the D14 §14.5 skill clause (U-HK-41) + CLAUDE.md §14.4/§14.5 convention.
- **D3 "≥2 options" mid-turn detector → REJECTED on signal quality** (no principled precision threshold; desensitizes the shared Stop surface). **Fallback:** skill-strengthen the loop-body skills (U-HK-41); optional fold into the U-HK-38 pre-done nudge.
- **D10 posture `type:prompt` Stop grader → REJECTED on cost/noise** (fires every turn; Haiku call + latency; net-negative). **Fallback:** skill §0 preambles + CLAUDE.md §11 (LEAVE-MANUAL).
- **D13 broad cite-grounding hook → REJECTED on signal quality** (cite-prose is saturated; would degrade the D2/D12 nudge). **Fallback:** skill-strengthen + the existing U-HK-02/U-HK-28 auto-guards (LEAVE-MANUAL).

### FLAGGED OUT-OF-SCOPE (do NOT build here)

- **D13 narrow phantom-cite `PostToolUse(Edit|Write)` variant** — capability-valid and high-precision, BUT touches design-substrate reference checking → **SCOPE VIOLATION** for this U-HK machinery. Listed only as a possible SEPARATE future unit for explicit operator request; NOT in this plan's sequence.

---

> **Enforced invariants (every proposal above):** U-HK machinery ONLY — no `design-substrate/**`, no `harness-*/src`, no `R-NNN` roadmap. Every hook capability-verified against `claude-code-hooks.md` (event exists AND the control output is supported). The hard-stop deny-list is never weakened — D6 only ADDS a narrow operator-gated allow with the deny-list intact as the unauthorized backstop. Never-halt-unless-zero-units preserved (D4 STRIKES the `stop_hook_active` addition; the merged advisory nudge never blocks; exactly TWO blocking Stop emitters remain). Defer-and-continue preserved (`defer.sh` advances; false-deny → `DEFERRED-HIL` + advance). Prefer-free-ollama preserved (`mvp-r300-ollama` is FREE and never deny-listed).
