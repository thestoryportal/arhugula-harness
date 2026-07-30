# ICM context-budget targets (diagnostic, not gates)

Source: `ICM_Alignment_Audit_v1.md` §3 (ICM's 5-layer hierarchy) and §5 (the measured gap).
Token estimate convention = **bytes ÷ 4** (the audit's own method, so figures reconcile with it).

## The layered-context budget

| Layer | File | Role | Token target |
|---|---|---|---|
| L0 | root `CLAUDE.md` | Global identity / orientation | **~800** |
| L1 | `CONTEXT.md` (workspace root) | Task routing | ~300 |
| L2 | stage / subdir `CONTEXT.md` | Stage / scope contract | 200–500 |

Per-stage working goal: **2,000–8,000 focused tokens**. ICM's named anti-pattern:
**30,000–50,000 monolithic tokens** loaded regardless of task.

In this repo the per-axis `harness-*/CLAUDE.md` files are the closest **L2-analog** (scope
pointers), so they take the **200–500** target. The **L1 router exists** as of 2026-07-30 —
root `CONTEXT.md`, landed by `R-ICM-2` under the governance-only ICM adoption ratified that day
(`B-17`); `scripts/measure.py` discovers and classifies it as L1 against the ~300 target.

## How this skill uses the targets

The targets frame the *gap* and rank the *work*. They are **not truncation gates**. The audit
is explicit — and this is the whole reason the skill is propose-don't-dispose:

> "A naive 'shrink CLAUDE.md to 800 tokens' recommendation would destroy a governance system
> the repo documents as essential. The next-steps are framed as reconciliation, not teardown."

So:
- **Report** each file's tokens vs target (`scripts/measure.py`).
- **Rank** optimization by where the gap is largest AND the content is least load-bearing
  (history / lineage / pointer-bulk — see `load-bearing.md`), not by token count alone.
- **Never** auto-truncate to hit a number. A file that stays several× over target but sheds
  200 KB of relocatable lineage is a win; a file cut to 800 tokens that drops the X-AL-3 guard
  is a catastrophe.
- The realistic near-term target for the root file is **R-ICM-1**: split the always-loaded
  monolith into a lean orientation core + a referenced history/pointer doc loaded on demand —
  not "hit 800 tokens this pass."

## Measured baseline (2026-06-04 — sanity-check snapshot)

| File | Tokens | Target | Over |
|---|---|---|---|
| `CLAUDE.md` (L0) | 85,705 | ~800 | ~107× |
| `harness-od/CLAUDE.md` | 11,732 | 200–500 | ~23× |
| `harness-cp/CLAUDE.md` | 9,507 | 200–500 | ~19× |
| `harness-as/CLAUDE.md` | 7,258 | 200–500 | ~15× |
| `harness-is/CLAUDE.md` | 4,361 | 200–500 | ~9× |
| **Total always-loaded** | **118,563** | — | — |

Always re-run `scripts/measure.py` for live numbers; this table is only a snapshot to catch a
gross measurement error or a regression in the other direction.
