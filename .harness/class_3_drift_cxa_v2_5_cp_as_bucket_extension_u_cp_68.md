# Class 3 drift — CXA v2.5 §2.3.3 CP→AS bucket extension owed (U-CP-68 ToolContract seam)

**Filed:** 2026-05-21 at cluster 10-CP-C close.
**Routing:** Next CXA revision pass (deferred; non-blocking).
**Class:** 3 (informational; landed code carries the seam; CXA enumeration owes the row).

## What surfaced

Cluster 10-CP-C close added a new genuine typed CP→AS Pattern-P1 seam:

- **Edge:** `U-CP-68 → U-AS-03`
- **Consumer:** `harness_cp.per_server_trust_evaluator`
- **Producer:** `harness_as.tool_contract`
- **Symbol:** `ToolContract`
- **Driver:** CP spec v1.10 §27.1 — `PerServerTrustEvaluator.evaluate(...)`
  canonical signature declares `tool_contract: ToolContract | None`. Physical
  import is spec-mandated.

The workspace-wide Pattern-P1 enforcement check at
`harness-runtime/tests/integration/test_cxa_pattern_p1.py` was updated at the
U-CP-70 commit (`2e417e0`):

- `PATTERN_P1_SEAMS`: 24 → 25 entries (added `U-CP-68 → U-AS-03` row)
- `test_seam_count_is_25` (was `is_24`) — count assertion bumped

This keeps runtime enforcement in agreement with the landed code. The CXA
canonical enumeration document still cites 24-aggregate / 5-in-bucket counts;
the amendment is **owed**.

## CXA amendment scope (single additive patch)

| Document section | Current | Amended |
|---|---|---|
| CXA v2.5 §2.3.3 CP→AS bucket | 5 entries | 6 entries (+1 new row) |
| CXA v2.5 §2.1 aggregate count | 24 / 29 genuine | 25 / 29 genuine |
| Workspace `CLAUDE.md` §1.1 cardinality cite | 99 aggregate / 29 genuine | 99 / 29 (no change — still genuine seams; in-bucket count drifts) |
| `harness-cp/CLAUDE.md` §2.3 CP→AS outbound | 18 | 19 |
| `harness-cp/CLAUDE.md` §2.4 per-cluster CP→AS edge profile | 24 total → AS | 25 total → AS (cluster 10 attribution) |

Estimated CXA delta: ~30 lines (new §2.3.3 row + aggregate row update + a
NEW Cluster 10 row in §2.4 per-cluster profile).

## Why deferred (non-blocking)

Pattern matches the existing CXA v2.6 → v2.7/v2.8/v2.9 amendment chain for
cost-attribution row 8 (workspace `CLAUDE.md` §1.1 + §2.4 + CXA footers):
additive, bounded, no landed-code blast radius, no signature change. The
runtime enforcement check ALREADY enumerates the new seam — Pattern-P1
identity-equality is enforced in CI today via the test update at this
cluster-close commit.

The amendment is best paired with another CXA revision (e.g., the v2.9
cost-attribution amendment tied to U-CP-72 implementation per `handoff §6`).

## Related memory

- `[[fork-cost-record-audit-ledger-wiring-residual]]` — sibling deferred CXA
  amendment pattern at cost-attribution row 8.
- `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` — sibling
  CXA-vs-axis-CLAUDE.md count-drift family.

## Status

OPEN. Routes to next CXA revision pass.
