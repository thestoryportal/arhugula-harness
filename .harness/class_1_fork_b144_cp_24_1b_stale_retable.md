# Class 1 fork — B-144: C-CP-24 §24.1.B's Attribute-count column was never re-tabled after two ratified supersessions, and the code manifest tracks a different venue per row

**Status:** ✅ APPLIED-AS-(A) (CP v1.116 → v1.117, this PR) — venue adjudicated via
loop-mode decorrelated review per
`[[feedback-noncoding-operator-decorrelated-adjudication]]`: out-of-family codex
verdict **VENUE: A**; transcript advisor verdict **VENUE: A** (agreement; RESOLVE row
logged at `.harness/loop_status.md`). Secondary scope call SPLIT (codex: hitl
in-delta; advisor: follow-up) — safer surgical option taken per the resolver's
split rule: hitl.* column-semantics minted as **B-153**, RESOLVE-SPLIT row logged.
Clearance `spec-control-plane-v1-117-cleared-2026-08-11.md`.

*Filed 2026-08-11 by the loop orchestrator (B-144 step-2 leg; step-1 single-venue
re-verification re-run this session at HEAD). All cites re-read at HEAD this session.*

## The discrepancy

§24.1.B (declared at exactly one venue in the 115-file CP delta chain,
`Spec_Control_Plane_v1_2.md:2152-2166` — re-verified by full-chain scan this session)
pins `retry.* = 4 attributes` and `harness.breaker.* = 7 attributes`. Both figures
were superseded at other venues and never carried back:

- **retry.\* 4 → 6 at CP v1.3** (`Spec_Control_Plane_v1_3.md:76`): a wholesale
  REPLACEMENT — all four v1.2 names (`retry.attempt` / `retry.cause` /
  `retry.backoff_ms` / `retry.policy`) retired, six live names substituted. The v1.3
  change-note routed a §24.4 downstream update but never named §24.1's own sub-table.
- **harness.breaker.\* 7 → 9 at OD v1.32** (`Spec_Operational_Discipline_v1_32.md`
  §"Cardinality": "Attribute count 7 → 9"; +`cause` +`cooldown_ms`,
  B-19-BREAKER-AMBIENT-ATTRS) — an amendment to the exact authority (C-OD-07 §7.1)
  §24.1.B's breaker row cites. Venue correction surfaced by the advisor reviewer and
  verified: this growth is an **OD-chain** delta; `Spec_Control_Plane_v1_32.md` has
  zero breaker mentions, so code comments citing a bare "v1.32" were mislabeled.

`cp_namespace_export_manifest.py` resolved the divergence inconsistently — `retry.*=4`
(stale §24.1.B) but `harness.breaker.*=9` (live §7.1) — conforming to neither venue as
a whole; its test asserted the mixture (sum 65).

## Classification + routing

**Class 1** (design-phase artifact requires revision — the spec-vs-spec ingestion-gap
shape, B-116-t3 precedent). Routed per root `CLAUDE.md` §4.3 / Workflow §2.7.6 to a
CP spec delta; resolved in-session under the U-HK-13 resolver (both decorrelated
reviewers, agreement on venue A) and landed as a bundled-absorption PR (§11.4): spec
delta + manifest/test cascade in one PR.

## The resolution (venue A)

`Spec_Control_Plane_v1_117.md` re-tables §24.1.B to the live counts (retry 6,
breaker 9 with explicit OD-v1.32 lineage), declared sum 65 → 67. Grounding that
collapsed the register's OD-facing worry: NO OD-side consumer of the 65 sum exists
(D6 ingestion is per-attribute-set); the sole consumer is CP's own acceptance-#6
test, whose docstring already records the sum as a moving figure (63 → 65 at the OD
v1.32 absorption). Venue B (historical-snapshot declaration) was rejected: it would
preserve a row counting a retired attribute set, contradict the cited C-OD-07 §7.1
authority, and force the manifest's breaker row to regress or carry a declared
divergence — institutionalizing the exact export-claim ↔ ingest-reality conflation
§24.1's composition-path summary says the table exists to prevent.

## Residuals

- **B-153 (minted this PR):** the hitl.* / Attribute-count column-semantics question
  (§0.5 of the delta) — explicitly NOT ratified by the re-table.
- The B-126 declared-count vs wire-count discipline (`RETRY_WIRE_REGISTER`) is
  unchanged: the wire still carries more `retry.`-prefixed keys than the declared 6.
