# R-CTX-1 U-CTX-21 — first eligible-cohort acceptance measurement (2026-08-11)

*Instrument of record: `just context-budget` (`tools/context_budget.py`), first-turn
metric over the `*/cli` headline cohort; post-compaction half via the E4
compaction-generation selector (TESTED at PR #1297, 32 witnesses). All numbers
re-derived live this session; JSON captures below are from
`--sessions N [--post-compaction] --json` runs at 2026-08-11T04:13–04:14Z.*

## 1. Cold-start (first-turn) — gate ≤76,000

First **post-slim** eligible session (started 2026-08-11T04:08:47Z, after #1301
merged at 2026-08-11T03:43:46Z; cohort `bg/cli`):

| Session | Cohort | input | cache_new | cache_read | TOTAL |
|---|---|---|---|---|---|
| 06fb5dd9 | bg/cli (post-slim) | 2 | 52,920 | 23,734 | **76,656** |

**Gate verdict: 76,656 > 76,000 — miss by 656 tokens (0.86%), n=1.** Not flipped;
see §4 for why the verdict is PENDING rather than routed to B-149 yet.

Pre-slim eligible baseline (same cohort, last 4 pre-merge sessions):

| Session | Started (UTC) | TOTAL |
|---|---|---|
| c2643c8a | 2026-08-10T14:25 | 131,020 |
| 9b1bdd92 | 2026-08-10T11:36 | 107,968 |
| 9a665850 | 2026-08-09T17:58 | 109,120 |
| 6ca5cd67 | 2026-08-09T09:31 | 106,831 |

Pre-slim median 108,544 → post-slim 76,656: **program delta ≈ −31.9k tokens
(−29.4%)**, consistent with the Floor-B projection (−28%) and better than the
~87k arithmetic projection recorded at B-148's build-state note. Excluded by
design: 2 `interactive/sdk-cli` sessions (lighter stack; the earlier 49,324 probe).

## 2. Component separation (A/B halves)

- **Static shared prefix ≈ 23,734 tokens** (`cache_read` — byte-identical across
  sessions; matches c2643c8a's first turn exactly): system prompt + tool schemas.
  Not a Floor-B lever (harness-owned, not repo-owned).
- **Variable half ≈ 52,920 tokens** (`cache_new`), decomposing into repo/operator
  surfaces (byte sizes measured 2026-08-11, ≈4 B/token):
  - project root `CLAUDE.md`: 44,853 B ≈ 11.2k tokens (was 123,442 B pre-Arc-5)
  - operator global `~/.claude/CLAUDE.md` + `RTK.md`: 14,555 B ≈ 3.6k tokens
  - auto-memory `MEMORY.md`: 18,817 B ≈ 4.7k tokens
  - skills listing incl. **4 removable design-skill descriptions: 2,531 B ≈
    600–700 tokens** (see §3)
  - remainder: deferred-tool + agent-type listings, MCP server instructions,
    SessionStart/UserPromptSubmit hook context, gitStatus block, first user turn.

## 3. Identified removable mass — decisive for the gate

The 4 design-skill dirs (`frontend-design`, `impeccable`, `taste-skill`,
`ui-ux-pro-max`) are on the ratified 21-name removal roster (D2/U-CTX-16) but
still present on disk — the unfinished machine-local half of errata E7. Their
descriptions (≈600–700 tokens) exceed the entire 656-token miss. Removal record +
operator command (classifier-blocked for the agent):
`.harness/r-ctx-1-e7-machine-local-orchestrator-step.md`.

## 4. Verdict + re-measure plan

**PENDING-REMEASURE, not routed to B-149.** Routing the >76k branch to the held
B-149 probes now would misattribute a known, already-ratified, removable
~650-token mass as structural remaining mass. Sequence: operator runs the E7
move → next fresh `*/cli` session → `just context-budget --sessions 1` →
expected ≈76.0k. If the re-measure still exceeds 76,000, THEN the residual split
(§2: static prefix 23.7k + root CLAUDE.md 11.2k + memory 4.7k + operator-global
3.6k + listings) routes to the held B-149 probes for the operator decision per
B-148's close-out note. n=1 caveat: the cohort should accumulate 2–3 post-slim
sessions (incl. an `interactive/cli` one) before treating any single reading as
the program number.

## 5. Post-compaction half (E4)

The selector runs and finds boundaries (verified live): the only compaction in
the 8-session window is **pre-slim** (c2643c8a, auto-compact at
2026-08-11T01:14Z, post-compaction first call = 214,373 — dominated by
conversation carryover, and predating the slims in any case). **No post-slim
compaction boundary exists yet**; the post-compaction acceptance number is
DEFERRED to the first post-slim session that compacts. The E4 obligation
(tested selector, not first-turn-only) is discharged as instrument; the
measurement itself awaits an eligible event.

## 6. Program-AC status recap (B-148 close-out)

| AC element | Status |
|---|---|
| Cold-start ≤76k, eligible cohort | 76,656 @ n=1 — PENDING-REMEASURE after E7 move |
| Post-compaction measurement (E4 selector) | Instrument tested + live; no post-slim boundary yet |
| Component-separated A/B | §2 above |
| CI gates green on main | Green at ea454fd7 (post-#1301 refresh) |
| Zero design-substrate diffs across program PRs | Verified per-PR 2026-08-11 (B-148 build-state note) |
| Register flip + memory + final refresh (U-CTX-22) | Blocked on the two PENDING rows above |
