# Session audit — U-HE-35 (2026-08-26): workflow efficiency, quantified

**Verdict in one paragraph.** The U-HE-35 arc shipped correctly, but the session paid
roughly twice what the same output should cost. The main session made 418 API calls
(≈21.0M input-equivalent tokens, 81% of it re-reading an average 410k-token context),
plus 286 subagent calls (≈4.5M). Of the 17h02m wall span, only 5h19m was foreground
work (a 9h11m operator pause, a 2h08m background live probe and a 24-minute
background door account for the rest); subtracting the external waits inside the loop leaves about two hours of agent-active time.
The four largest avoidable costs, in order: the codex review loop running 10 rounds
where the complementary findings audit shows 4–6 were reachable (≈40% of main-session
cost, 2h18m); context-size compounding that made the last 27% of calls cost 42% of
the session; a merge-gate stage whose spec-conformance lens spent ≈1.3M tokens over
three runs and found nothing; and three mechanical leaks — whole-file mutation-pin
re-pinning (12 re-pins, 45% of the PR's commits), rtk grep-rewrite failures (29 wasted
calls), and `just codex-check` runs whose reds were environmental (27.7 minutes). The
earned costs — the background probe, the CI waits, the budget refusal, the door — should
stay as they are.

Complementary audit (do not re-read for classification detail): the review-loop
findings audit at `.harness/session-audit-2026-08-26-u-he-35-preflight-suite.md`
(29 findings; 11 already in the suite's ledger, 17 inferable, 0 beyond reach;
counterfactual 4–6 rounds; zero in-commit skill repairs). This document costs what that
one classified, and audits everything else in the loop.

## Evidence and method

Every number below comes from one of these sources, named inline as [T], [G], [R],
[L], [Q], [P], [A], [S]:

- **[T] Transcript** `~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/b6bed0d9-79b6-4d82-8c35-bc94342f1706.jsonl`
  (2,819 records; identity verified: 448 `reviewer_concurrency_probe` mentions, first
  timestamp 2026-08-26T04:14:20Z, last 21:16:17Z). Usage is **deduplicated by
  `requestId`** — the file stores 804 assistant records for 418 API calls (thinking,
  text and tool_use blocks each carry a copy of the same usage block), so naive sums
  double-count by 1.9×. Subagent transcripts: the 12 files under
  `b6bed0d9-…/subagents/`, deduplicated the same way.
- **Cost index.** "IET" (input-equivalent tokens) = input + 1.25×cache-write +
  0.1×cache-read + 5×output — the relative price ratios for Claude models. It is a
  ranking instrument, not a dollar figure; the raw token classes are given alongside.
- **[G] Gate log** `.harness/merge-gate-log.jsonl`, the 80 `arc_id=u-he-35` rows
  (29 `codex_review_wrapper`, 36 `reviewer_concurrency_probe`, 15 `merge-gate-*`).
- **[R] Reservation** `uv run python tools/reservations.py show --arc-id u-he-35`.
- **[L] Round logs** `.harness/tmp/u-he-35-rounds/` — 12 files: `r1..r11.log` plus
  `r9-verdict.log`. `r9.log` is a `GATE_REFUSED (SWEEP_MISSING)` transcript and
  `r11.log` a `GATE_REFUSED (BUDGET_EXHAUSTED)` one; the brief's "r1..r10 + r9-verdict
  + r9" listing double-counted r9 and missed r11.
- **[Q] Arc-metrics queue** `~/.gstack/projects/arhugula-v2/arc-metrics-queue/u-he-35.json`.
- **[P] PR #1460** via `gh pr view 1460 --json commits`: **29 commits** (the brief said 24),
  merged 20:25:41Z at `b6146ce90d00`; #1461 merged 20:42:12Z at `7b3976f3d`.
- **[A] Findings audit** `.harness/session-audit-2026-08-26-u-he-35-preflight-suite.md`.
- **[S] Workspace source** cited as `path:line`.

Stage windows are cut at the transcript timestamps of the events that bound them
(skill loads, task notifications, commits); the boundaries are listed in §2 so the
split is reproducible.

## 1. Findings ranked by cost

Main-session total for scale: 418 calls, 355,092 output tokens, 1.82M cache-write,
169.44M cache-read, 836 uncached input → **20.99M IET** [T]. Subagents: 286 calls,
4,795 output, 1.27M cache-write, 29.0M cache-read → **4.52M IET** [T]. Grand total
≈25.5M IET. Foreground wall 5h19m.

| # | Finding | Cost (measured) | Avoidable share | Evidence |
|---|---|---|---|---|
| F1 | Codex loop ran 10 rounds; 4–6 reachable | S2 = 2h18m wall (72m28s external codex + 65m31s absorption), 199 calls, 168k output, 8.40M IET (40% of main) | 4–6 rounds ≈ 55–83 min, 3.4–5.0M IET | [T] launch/notification pairs; [A] counterfactual |
| F2 | Context compounding | avg 410k ctx/call, final 770k; calls after the pause (S6–S11: 111 calls, 27% of calls) = 8.74M IET, 42% of main | ≈2M IET: S3+S10+S11 cost 2.87M at ≥540k context and would cost ≈0.8M at fresh-session context | [T] per-call usage |
| F3 | Merge-gate stage | 41m wall; main 67 calls / 4.84M IET; 10 lens subagents 4.27M IET; total 9.1M IET (36% of grand total) for 9 findings | spec lens: 3 runs, 0 findings, 1.34M IET; witness r3 rerun 0.38M IET + 4m54s | [T] subagents; [G] merge-gate rows |
| F4 | Cache re-warm after long idle | 09:53:38 call wrote 543,923 cache tokens; 19:06:09 wrote 547,755 → 1.36M IET (6.5% of main) | operator pause unavoidable; probe wait avoidable only by handing off | [T] `cache_creation_input_tokens` |
| F5 | rtk grep-rewrite failures | 101 grep-shaped Bash calls; 8 hard failures (`--glob`, `\|` → "regex parse error", unclosed group, BSD `sed ,+8p`); 24 "N matches in M files" summaries with content stripped, 21 immediately re-queried → 29 wasted calls ≈ 1.2M IET, ≈10–12 min | all | [T] Bash results |
| F6 | `just codex-check` ×3 | 348 s + 352 s + ≈960 s = 27.7 min (8.7% of foreground wall); run 2 red only on `ROOT_CHECKOUT_EDIT`; run 3 hit the 600 s foreground timeout → 16 min idle at ship | ≈20 min | [T] durations; `tail` 04:35:33, 04:44:19, 19:07:27 |
| F7 | Mutation-pin churn | 13 pin commits of 29 (45%); 14 probe runs = 137 s; 25 API calls / 10.7M ctx ≈ 1.07M IET (5% of main) | 12 of 13 pins | [P] commit list; [T] `mutation_probe.py` calls |
| F8 | Edit/Write hook latency | 100 Edit/Write calls, 945 s inside the round-trip (median 8.9 s) = 15.75 min, 5% of foreground wall | most, if `ruff` resolves without `uv run` | [T] tool_use→tool_result deltas; `tools/hooks/postedit-lint.sh:1-12` |
| F9 | Worktree detour | 04:44:19→04:52:06 = 7m47s, 13 calls, 0.31M IET; `wt-clean` still registered; 3 "local state" refusals + 2 guard HARD-STOPs | all | [T]; `git worktree list` |
| F10 | In-session audit at 540k context | S3: 14 calls, 31k output, 0.93M IET; same work at fresh-session context ≈ 0.3M | ≈0.6M IET | [T] S3 window |
| F11 | Skill-body injections | 196 KB ≈ 49k tokens (6.4% of final context): laws:code 56.7 KB, context-save 53.8 KB, ship-pr 40.7 KB, defect-class-preflight 19.3 KB, merge-gate 14.4 KB, roadmap-continue 11.3 KB; cache-read drag ≈ 0.57M IET (2.7%) | context-save preamble; laws:code is not workspace-owned | [T] `isMeta` user blocks |
| F12 | Hook chatter in context | `hook_success` attachments 149 KB ≈ 37k tokens (PreToolUse:Bash 143 × ≈0.75 KB = 108 KB; Stop 33 = 17 KB; PostToolUse:Edit 22 = 16 KB) | PreToolUse:Bash notices when nothing was rewritten | [T] attachments |
| F13 | Refused launches + log collision | r9 first launch refused `SWEEP_MISSING` (06:45:38; relaunch 06:47:01, 92 s + 1 call); r9 relaunch reused `r9.log` → `PUBLISH FAILED (exit 4)` at 06:55:49, salvage 4 calls / ≈1.5 min; r11 launched into an exhausted budget (07:10:52, refused 07:11:01) | all; plus metrics corruption (F15) | [T]; [L] |
| F14 | Attestation label discovery by trial | 3 `NOT attested` calls (04:52:06 preflight; 05:08:19, 06:46:27 sweep), ≈30 s + 1 call each ≈ 0.12M IET | all | [T] `review-attest-*` results |
| F15 | Arc-metrics round snapshot corrupted | `review_rounds: 12`, `p1_rounds: [1, 11]`, 11 `round_wall_s` entries — file positions, with the two `GATE_REFUSED` logs counted as rounds (the real P1 rounds are r1 and r10) | data-integrity, not tokens | [Q]; [L] |
| F16 | Gate-log attribution never populated | `unique_catch`, `cause_attribution`, `disposition` are null on all 44 finding rows | the incident-17 question is unanswerable from the ledger | [G] |
| F17 | Zero-call instruments | `advisor()` 0 (and not provisioned — see §4 item 1), `just overlay-query` 0, `red-first` 0, graft MCP 0 (CLI 4), C-HE-27 verify/absorb/edit spans 0, preflight repair loop 0/10, TaskCreate 0, unreconciled subagent 0 | see §4 for per-item impact | [T] tool names; [R] phases |

The ranking is by measured cost. F1–F3 are the only items where the fix moves the
session by a quarter or more; F4 is mostly unavoidable and is listed so the stage
numbers make sense; F5–F9 are mechanical and cheap to fix; F10–F17 are hygiene,
instrumentation and governance debts that cost little per session but compound.

### Why F1 is the whole game

The loop's round cycle was 13.8 minutes on average: launch → verdict 7m14s (the
agent idle, no tokens) → absorb → attest → relaunch 6m33s (the agent active, ≈20
calls). Per-round external durations [T]: 6:11, 6:13, 5:29, 5:47, 6:33, 8:18, 10:22,
7:37, 8:48, 7:10; absorption: 9:49, 5:03, 6:30, 9:04, 4:59, 3:53, 9:54, 8:26, 3:44,
4:09. Absorption cost 8.40M IET because each of its 199 calls re-read a context that
grew from 229k (end of S1) to 505k (end of S2) [T]. Removing four rounds removes
≈55 min and ≈3.4M IET directly, and shrinks every later call's context. Items 18–20 of
the inventory (pilot-gate hold, drift arms race, plan-skeleton deference) are the
causes; [A] already prices them as 4 + 2 + 2 rounds and the repairs are scoped there.

### Why F2 compounds everything else

Cache-read tokens are 81% of main-session IET. The per-call cost rose from ≈0.02M IET
at 140k context to ≈0.08M at 770k. Concretely, S10 close-out (14 calls) cost 1.11M IET
— more than the entire S0 grounding stage (29 calls, 0.52M) — because each close-out
call carried 750k tokens. Two habits drove the growth: one-command-per-call Bash
(288 Bash calls, 33 of them `sed -n` reads that the Read tool or a single script would
have batched) and authoring long documents in the closing session (S3 + S11 =
44k output tokens at ≥540k context). The workspace memory "session cost is quadratic
in turns" is confirmed with the actual exponent: total context processed (171M) is
418 calls × 410k average — halve the calls at the same context and the bill halves.

### F3: what each review layer uniquely caught

Codex (10 rounds, ≈72 min external) recorded 29 findings: 2 P1, 23 P2, 4 P3 [G]. The
merge-gate (3 rounds, 41 min) recorded 9: concurrency lens 4 (r1: `probe.py:232-237`
P2, `359-365` P3; r2: `256-260,359` P2, `251-255` P3), witness-adequacy lens 5 (all
r1: `probe.py:140-142`, `lanes_verify.py:633-636`, `probe.py:338,402-403` P2;
`455-461`, `test_…:498-505` P3), spec-conformance 0 [G]. Every gate finding landed
on code codex had already reviewed ten times, so the two layers are decorrelated in
fact, not just in design. The cost asymmetry is the point: the gate's 9 findings cost
9.1M IET (≈1.0M each) against codex's 29 at 8.4M (≈0.29M each, and the codex
minutes are on the operator's subscription). The spec lens alone consumed 1.34M IET
across three clean-approve runs (r1 49 calls / 6.65M cache-read; r2 25 / 2.13M; r3
12 / 0.86M) [T]. Serial-then-gate is not wrong, but the concurrency and witness lenses
found their defects in code that existed by mid-budget; a single mid-budget pass of
those two lenses would have let codex rounds 5–10 verify the gate's fixes instead of
the gate finding them after codex was spent. This is a trial to run, not a proven
saving — the measurable claim is "rounds-to-all-approve on the next arc with a
mid-budget pass vs. this arc's 13".

Round-3 paste corruption (inventory item 3), priced: the concurrency lens's
`head_sha` was one character short → one `SendMessage` re-emit (20:05:24) and two
extra notifications; the witness lens's `base_sha` was spliced → the lens refused the
mid-flight correction and a full rerun ran 20:09:07–20:14:01 (31 calls, 2.65M
cache-read, 0.38M IET) [T]. Round 3 ended at 20:14:43 instead of ≈20:09; the arc's
critical path lengthened by ≈5 min. The laws:prompt delegate that authored the r3
prompts cost 1m13s and 0.11M IET — 3% of one lens run — so the delegation is cheap;
the transcription of binding values by hand is what cost.

## 2. Bottleneck map of the loop

Windows are cut at transcript events; "calls" are deduplicated API calls; wall is
UTC clock time [T].

| Stage | Window (UTC) | Wall | Calls | Output tok | Context (M tok) | IET (M) | What bounded it |
|---|---|---|---|---|---|---|---|
| S0 session start + grounding | 04:14:20–04:29:04 | 0:14 | 29 | 12,844 | 3.2 | 0.52 | `/roadmap-continue` at 04:25:11; reservation execute-start 04:29:04 [R] |
| S1 build + pin + preflight + codex-check ×2 + worktree detour | 04:29:04–04:53:30 | 0:24 | 60 | 38,204 | 12.0 | 1.49 | first commit 04:42:00; r1 launch 04:52:53 |
| S2 codex r1–r10 (launch→verdict→absorb→re-pin→attest→relaunch) | 04:53:30–07:12:03 | 2:18 | 199 | 168,311 | 72.4 | 8.40 | 10 background rounds; r11 refused 07:11:01 [L] |
| S3 operator Q&A + in-session findings audit | 07:12:03–07:45:33 | 0:33 | 15 | 32,986 | 7.9 | 0.99 | operator prompts 07:20, 07:26, 07:43 |
| S4 live C-HE-22 probe (background) + result commit | 07:45:33–09:54:31 | 2:08 | 4 | 2,726 | 2.2 | 0.86 | probe notification 09:53:25; cache re-warm 09:53:38 |
| S5 operator HIL pause | 09:54:31–19:05:55 | 9:11 | 0 | 0 | 0 | 0 | operator reply `#1` at 19:05:55 |
| S6 ship-pr: codex-check #3 + PR open + CI | 19:05:55–19:34:31 | 0:28 | 15 | 10,254 | 8.6 | 1.58 | codex-check 19:07:27→19:23:23 (600 s timeout → background); CI notification 19:34:31 |
| S7 merge-gate r1–r3 + absorption | 19:34:31–20:16:04 | 0:41 | 67 | 66,021 | 43.7 | 4.84 (+4.27 subagents) | r1 19:35–19:46, r2 19:52–19:58, r3 20:03–20:14 |
| S8 CI wait + merge | 20:16:04–20:25:51 | 0:09 | 6 | 1,291 | 4.3 | 0.44 | CI notification 20:24:46; merged 20:25:41 [P] |
| S9 door (#1461 refresh, background) | 20:25:51–20:50:12 | 0:24 | 0 | 0 | 0 | 0 | #1461 merged 20:42:12; main-CI-green notification 20:50:12 |
| S10 close-out (exit report, metrics, memory, context-save) | 20:50:12–20:54:23 | 0:04 | 14 | 10,365 | 10.2 | 1.11 | MEMORY.md cap refusal 20:51:44 then upsert 20:52:20 |
| S11 audit handoff authoring | 20:54:23–21:16:18 | 0:21 | 9 | 12,090 | 6.8 | 0.77 | operator prompt 21:07:41; laws:prompt delegate 21:10:58 |

Reading the map: the loop's serial spine (S1→S2→S6→S7→S8→S9) is 4h24m of wall.
Subtracting the waits the agent spent no tokens on — external codex review (72 min),
the three codex-check runs (28 min), the two CI waits (≈18 min) and the door
(24 min) — leaves ≈2h of agent-active time. Wall-clock reductions therefore come from fewer rounds and fewer
suite runs; token reductions come from fewer calls per round and a smaller context
per call. The two levers are independent and both are needed.

## 3. Inventory disposition — all 20 items

| # | Item | Disposition | Numbers |
|---|---|---|---|
| 1 | `advisor()` never invoked | **Confirmed, and revised:** not provisioned. The session's tool inventory has 10 names (`Agent, AskUserQuestion, Bash, Edit, Read, SendMessage, SendUserFile, Skill, ToolSearch, Write`); no `advisor` tool in `.claude/settings.json`, `~/.claude/settings.json` or `.mcp.json`; the 65 mentions are skill-body prose (`roadmap-continue/SKILL.md:106`, `merge-gate/SKILL.md:9,17`, `resolve/SKILL.md:35`) and the handoff | 0 calls; the CLAUDE.md §13.1 "always-on" discipline names an instrument the environment does not expose |
| 2 | `just overlay-query` never invoked | **Confirmed.** 0 Bash calls to it. Impact on the P1s: none attributable — [A] shows both P1 rules were already in loaded context; the miss was activation, not cite resolution | 0 calls |
| 3 | laws:prompt delegation + paste corruption | **Confirmed with numbers** (§1 F3): rerun 31 calls / 0.38M IET / 4m54s; re-emit 1 `SendMessage`; delegate itself 0.11M / 1m13s. Rounds 1–2 lens prompts freehand (3,118–3,834 bytes each [T]) | r3 ended ≈5 min late |
| 4 | C-HE-27 spans never fired | **Confirmed, cause found.** [R] `phases` holds only `queue` and `execute`. The verify/absorb/edit emission instructions live in `ship-pr/SKILL.md:95-108`; the ten review rounds ran under `roadmap-continue`, whose `SKILL.md:94-96,138` emits only queue/execute. The instrument is agent-discipline, not wrapper-automatic, and the discipline was not in context when the rounds ran | 0 of 60 expected edges (10 BLOCK rounds × verify/absorb/edit × start/end) |
| 5 | Preflight repair loop 0/10 | **Confirmed** by [A]; not re-audited here | 0 repairs, 29 new corpus rows |
| 6 | graft underused / rtk mangling | **Confirmed and quantified** (F5): 101 grep-shaped calls, 8 hard failures, 24 stripped summaries, 21 re-queries; graft MCP tools 0, graft CLI 4 | ≈29 wasted calls, ≈1.2M IET |
| 7 | `red-first` unused; annotation-grammar miss | **Confirmed use = 0; impact revised down.** The two-line annotation was caught by codex-check run 1 (04:35:33, 348 s) and fixed in one edit (04:41:30). `red-first/SKILL.md:53,135` documents the one-line `# mutation-probe: <file>:<lines>` form, so the skill would have prevented it — but that run also carried the environmental red (F6), so the grammar miss alone cost one edit, not a run | ≈1 call |
| 8 | Task tracking unused; nags | **Confirmed use = 0; cost refuted as noise.** 56 `task_reminder` attachments, each persisted as `{"content": [], "itemCount": 0}` (3.1 KB total); the rendered nudge is ephemeral, ≈100 tokens per turn it appears in. Tasks would have duplicated the reservation phases + round logs. No repair warranted | ≤0.03% of context |
| 9 | Unreconciled subagent `a288fb2fd8ed…` | **Confirmed** never reconciled (mentions only at session start 04:25 and in the handoff). The U-HK-44 clause at `tools/hooks/loop-gc.sh:11` reads "Never delete", so reconciliation is a manual-review item with no token cost; it is hygiene debt, not a session cost | 0 tokens |
| 10 | Mutation-pin churn ~7 re-pins | **Revised up:** 12 re-pins (13 pin commits of 29) [P]; 14 probe runs totalling 137 s (4–48 s each, median 7 s) — the brief's "20–60 s" overstated the probe, understated the count; the cost is the 25 API calls (10.7M ctx ≈ 1.07M IET) and 12 commits of history noise | 5% of main IET |
| 11 | ≥3 attest failures | **Confirmed = 3** (F14) | ≈0.12M IET, ≈1.5 min |
| 12 | r9 log collision | **Confirmed** (F13): `PUBLISH FAILED (exit 4)` 06:55:49; salvage via `round_log_publish.py r9-verdict.log` at 06:56:52; 4 calls | ≈1.5 min, ≈0.2M IET |
| 13 | codex-check ~5×, detour, wt-clean | **Revised: 3 runs, not 5** (F6); detour 7m47s / 13 calls / 0.31M IET (F9); `wt-clean` still registered at `~/.claude/jobs/9b1bdd92/tmp/wt-clean` (plus `basewt`, `docwt`, `refreshwt` from the same job, and 14 `prunable` entries in `git worktree list`) | 27.7 min + 7.8 min |
| 14 | Untracked dotfiles keep tree dirty | **Confirmed.** `ROOT_CHECKOUT_EDIT` red at 04:41:46 and in run 2; 11 answer files moved to `attest-stash` at 19:07:16 for run 3 and restored at 19:23:36 with `(eval):1: no matches found: …/attest-stash/*.md` (the files had already been restored — a zsh glob error, not data loss) | shares F6's ≈20 min |
| 15 | Session scale / 77% context | **Confirmed with corrected figures** (§1 header, F2, F4). "≈1.0–1.1M subagent tokens" revised: lens subagents processed 30.3M context tokens (29.0M cache-read) for 4.8k output = 4.52M IET | see §2 |
| 16 | Skill-body weight | **Confirmed but re-priced** (F11): 196 KB injected; context-save 53.8 KB is the trim candidate; token drag ≈2.7% — an attention cost more than a token cost | 0.57M IET |
| 17 | Two review layers, division of labor | **Answered from finding content** (§1 F3) because the ledger's attribution fields are null (F16). Gate caught 9 post-codex defects: 4 concurrency, 5 witness, 0 spec. Interleaving is a trial, not a proven win | 9.1M vs 8.4M IET |
| 18 | Pilot-gate hold 4 rounds | **Confirmed by [A]** (r1, r5, r9, r10 re-presses = 4 of 29 findings); priced here at ≈13.8 min and ≈0.84M IET per round → up to ≈55 min / 3.4M if the hold had been reversed at r1 | folded into F1 |
| 19 | Drift arms race r2→r7 | **Confirmed by [A]** (r2, r3, r5, r7); stopping at r5 saves ≈2 rounds ≈ 28 min / 1.7M IET | folded into F1 |
| 20 | Plan-skeleton deference → both P1s | **Confirmed by [A]**; r1 P1 cost one round's absorption; r10 P1 was the pilot-gate family's terminal form | folded into F1 |

## 4. Incidents the inventory missed

Swept for: tool results flagged `is_error` (6 Bash, 1 Edit), permission-rule
denials (`toolDenialKind` ×2 — both guard HARD-STOPs on the direct worktree removal,
04:51:03 and 04:51:57), the guard-blocked `sleep 240` at 04:53:13, foreground timeouts (1), inter-record gaps >8 min
(13), rtk failure signatures, hook attachment bytes, subagent reruns and
`SendMessage` re-emits, `GATE_REFUSED` (2), per-call `cache_creation` spikes, and
the metrics queue against the round logs [T][L][Q]. Six surfaced that the closing
session did not list:

1. **Cold-cache re-warm after long waits (F4).** Two calls wrote ≈544k and ≈548k
   cache tokens — 1.36M IET, 6.5% of the session — because the prompt cache expired
   during the 2h08m probe and the 9h11m pause. Nothing to repair for the pause; for
   any future multi-hour background wait, the cheaper shape is to hand off (write the
   facts, end the session, let the notification start a fresh one) rather than hold
   546k tokens of context warm.
2. **Edit/Write hook latency (F8).** 945 s inside 100 tool round-trips. The hook
   (`postedit-lint.sh`) runs ruff on the edited file and falls back to `uv run ruff`
   when `ruff` is not on PATH; a second PostToolUse hook (`graft-hooks.cjs post-edit`)
   runs on the same matcher (`.claude/settings.json` PostToolUse entries). Which of
   the two dominates was not measured here; 8.9 s median for a single-file lint says
   at least one is paying a process-startup cost on every edit.
3. **Arc-metrics round snapshot counts refused launches as rounds (F15).** The B-211
   lever cohort will record this arc as 12 rounds with P1s at rounds 1 and 11. The
   instrument meant to measure the skill-suite repairs is mis-measuring the arc that
   motivated them.
4. **Codex-check under a 600 s foreground timeout (F6).** The run was known to take
   >6 min (runs 1–2 took 348/352 s and run 3 ran the full 7,969-test suite); running
   it foreground produced a 10-minute dead gap (19:07:27→19:17:28) followed by a
   background hand-off anyway.
5. **Gate-log attribution fields unpopulated (F16).** `unique_catch`,
   `cause_attribution` and `disposition` exist in the row schema and are null on all
   44 rows; whoever designed them for the layer-attribution question never wired a
   writer.
6. **Worktree accumulation.** `git worktree list` returns 60 entries: 14 `prunable`
   under `/private/tmp`, 4 under this job's tmp dir, 20+ `.claude/worktrees/agent-*`.
   Not this session's creation, but this session added four and removed none because
   `safe-worktree-remove.sh` refuses a throwaway worktree with "local state"
   (`.venv`) and the guard hard-stops the direct `git worktree remove`.

## 5. Recommendations

### (a) Folds into the already-scoped skill-suite repair PR

The scoped PR carries five repairs from [A] plus laws:prompt durable wiring. These
belong in the same PR because they touch the same skill bodies:

- **a1. Emit C-HE-27 spans from the wrapper, not from agent discipline.** Move the
  verify/absorb/edit edge emission out of `ship-pr/SKILL.md:95-108` prose and into
  `review-with-failover-logged` (verify start/end are the wrapper's own process
  boundaries; absorb/edit can key off the first fix edit and the absorption commit).
  Until then, copy the emission block into `roadmap-continue` so it is in context
  during the rounds that need it. Evidence: 0 spans across 13 review rounds [R].
- **a2. Attestation: labels before answers.** The skill recipe should run
  `preflight-grep.sh` first and write its labels into the answers template; three
  attest calls failed only because answers were authored before the labels existed
  (F14).
- **a3. Relaunch guard + per-attempt log names.** Before any relaunch, check the
  budget (`r11` was launched into `BUDGET_EXHAUSTED`) and the sweep attestation
  (`r9`'s first launch was refused `SWEEP_MISSING`); name logs per attempt so a refused
  launch never claims the write-once round name (F13).
- **a4. Binding values by file, never by hand.** The two r3 corruptions were
  orchestrator transcription errors. Have `just merge-gate-binding` write the binding
  block to a file the lens agent reads; the prompt names the path. This is the
  concrete form of the laws:prompt wiring already in scope (F3).
- **a5. Confirm the mechanism-precedent-search rule is in the PR** (memory
  `mechanism-precedent-search-before-authoring.md` carries a wiring plan; [A] prices
  the miss at ≥7 of 29 findings).

### (b) New repair / eval / optimization items

- **b1. Pin scope.** Bind the mutation pin to the probed block's digest (the
  `--lines` range plus the test's body), or pin once at ship. Twelve re-pins, 13 of
  29 commits, 1.07M IET (F7). Witness: a test that edits an unrelated line and asserts
  the pin is still fresh.
- **b2. Arc-metrics round snapshot.** Derive rounds from log content (`codex-review:`
  terminal lines), skip `GATE_REFUSED` transcripts, and number rounds from the round
  id, not file position (F15). Witness: this arc's directory must yield 10 rounds,
  P1s at r1 and r10.
- **b3. Gate-log attribution.** Either write `unique_catch` / `cause_attribution` at
  emission (the merge-gate-emit recipe knows which codex rounds preceded it) or drop
  the fields — null-everywhere fields invite exactly the unanswerable question in
  item 17 (F16).
- **b4. rtk grep rewrite.** Three shapes fail deterministically: `\|` alternation
  (`grep -n "a\|b"` → rg "regex parse error"), `--glob` on a rewrite that lands on
  BSD grep, and `(`/`)` in fixed-string greps. Either fix the rewrite or add these
  shapes to the U-HK cache/rewrite hook's pass-through list. Until then the cheap
  habit is `rtk proxy grep …` or graft for symbol lookups (F5: 29 wasted calls).
- **b5. Measure the edit hook.** Time `postedit-lint.sh` and `graft-hooks.cjs
  post-edit` separately on one `.py` edit; if `uv run ruff` is the path taken,
  put `ruff` on PATH for hook shells (F8: 15.75 min).
- **b6. codex-check shape.** Always `run_in_background`; make the stop-gate test
  ignore `.harness/.preflight-answers-*` / `.sweep-answers-*` (or gitignore them, or
  home them under the job tmp dir) so the tree-dirty red cannot fire on attestation
  artifacts (F6, item 14). Two of three runs were red on environment only.
- **b7. Worktree hygiene.** Give `safe-worktree-remove.sh` a path for throwaway
  worktrees whose only "local state" is a `.venv`; then prune (`git worktree prune`
  plus removal of the four job-dir worktrees) — removal is guard-blocked for the
  agent, so this is an operator command (§4 item 6).
- **b8. `advisor()` provisioning.** Either expose the tool the CLAUDE.md §13.1
  discipline names, or rewrite §13.1, `roadmap-continue/SKILL.md:106`,
  `merge-gate/SKILL.md:9,17` and `resolve/SKILL.md:35` to the instrument that exists
  (a fresh-context `Agent` given the transcript summary, or `just codex-review` alone).
  A discipline that cannot be followed trains the agent to skip disciplines (item 1).
- **b9. Mid-budget lens trial.** On the next code arc, run the concurrency and
  witness-adequacy lenses once after round 4 and record rounds-to-all-approve against
  this arc's 13 (10 codex + 3 gate). Keep spec-conformance at ship only, and record
  its findings-per-IET (this arc: 0 per 1.34M) so a second zero can retire or shrink it.
- **b10. Session shape for audits.** Codify what this session did: the closing
  session writes a facts brief and a handoff prompt only; audits and long documents
  are authored in a fresh session. S3 alone would have cost ≈0.3M instead of 0.93M
  IET (F10).

### (c) Deletions and simplifications

- **c1. Re-pin commits** disappear with b1 — 12 fewer commits per 10-round arc.
- **c2. context-save preamble.** 53.8 KB of gstack-generic text per invocation
  (F11). Trim to the workspace-relevant subset or replace with the local checkpoint
  recipe (`~/.gstack/projects/arhugula-v2/checkpoints/` is the only sink used).
- **c3. PreToolUse:Bash hook notices** when no rewrite occurred: 143 attachments,
  108 KB, most of them "rtk rewrote nothing" chatter (F12). Emit only on rewrite or
  guard decision.
- **c4. Task-tool nags:** no workspace action; the cost is negligible and the
  workspace has no knob for it (item 8).
- **c5. The r11 launch step** in the loop recipe (launch-after-attest without a
  budget check) — subsumed by a3.

### (d) Additions

- **d1. Per-arc cost ledger.** The extraction used here (deduplicate by `requestId`,
  IET formula, stage windows from skill loads and task notifications) fits in a
  100-line `tools/` script and a `just arc-cost <transcript>` recipe; it would let
  the B-211/B-212 lever report show cost per arc, not only rounds per arc.
- **d2. Cache-warmth note in the loop skills.** Before any background wait expected
  to exceed the cache TTL at >400k context, prefer a handoff; the re-warm costs
  ≈0.7M IET at this context size (F4).
- **d3. Read-before-grep default.** For a file the agent will read anyway, the Read
  tool or a single Python script beats a chain of `sed -n` and `grep` Bash calls
  (33 `sed -n`, 101 grep-shaped calls, one API call each). This is a habit line for
  `roadmap-continue`, not a tool change.

## 6. What NOT to change

- **The background live probe (S4).** 2h08m of wall for 4 API calls; the agent
  paid nothing to wait and the probe's 35 samples landed as 36 gate-log rows and a
  GREEN result commit. The only cost was the cache re-warm on return (F4), which is
  cheaper than any alternative that keeps the session alive.
- **Background codex rounds with task notifications.** The 72 minutes of external
  review cost zero tokens; the shape is right. Only the relaunch guards (a3) need work.
- **The 10-round budget refusal.** It stopped the loop exactly where B-215 says, and
  [A] confirms the late rounds (r7 subtraction, r10 reversal) were the right
  decisions once made.
- **The merge-gate itself.** Its 9 findings were real and post-codex (F3); the cost to
  cut is the spec lens's yield and the paste path, not the gate.
- **CI waits (S6/S8) and the door (S9).** ≈39 minutes of wall with 6 API calls; all
  CI-bound, all background.
- **The laws:prompt delegate.** 1m13s and 0.11M IET per use — 3% of one lens run.
  Delegating is not the cost; hand-copying binding values was.
- **The mutation probe as a witness.** 137 s of probe runtime across the arc is
  cheap; only the whole-file pin scope (b1) is the defect.
- **The facts-brief → fresh-session audit pattern** that produced this document.
  It is the shape b10 asks to codify.

*Author: audit session (Claude), 2026-08-26. Read-only toward the repo except this
file. Sources: [T] transcript and its 12 subagent files; [G] `.harness/merge-gate-log.jsonl`;
[R] `tools/reservations.py show --arc-id u-he-35`; [L] `.harness/tmp/u-he-35-rounds/`;
[Q] `~/.gstack/projects/arhugula-v2/arc-metrics-queue/u-he-35.json`; [P] `gh pr view 1460/1461`;
[A] `.harness/session-audit-2026-08-26-u-he-35-preflight-suite.md`; [S] `.claude/settings.json`,
`tools/hooks/postedit-lint.sh`, `tools/hooks/loop-gc.sh`, `.claude/skills/{roadmap-continue,ship-pr,merge-gate,resolve,red-first}/SKILL.md`.*
