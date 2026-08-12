# Implementation Plan: Operational Discipline — v2.35 (delta over v2.34)

*v2.35 absorbs the B-141 cascade (B-138 operator-ratified disposition (a), CP spec
v1.116; OD spec v1.41) into the OD plan's execution authority as ONE SUPERSESSION NOTE
on the U-OD-20-era acceptance framing that pins the §14.5.3 invariance-check ESCALATION
to `terminal-fail-exit`. No new unit, cluster, DAG node, dependency edge, or CXA row is
introduced; NO landed unit's body is amended (the B-97(a)/B-118 precedent — supersession
rides as a note, the landed criteria stand as HISTORY). Every unit body, dependency
graph, and all other plan content are PRESERVED VERBATIM.*

**Status:** Proposed

---

## §0 Change-note (v2.34 → v2.35)

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_34.md` (v2.34 — the `B-123` realization
leg; NEW U-OD-60).

### §0.2 The stale as-value sites

The v2.2-era U-OD-20 absorption criteria
(`Implementation_Plan_Operational_Discipline_v2_2.md:55` Tests row "invariance check
ESCALATION to terminal-fail-exit"; `:66` absorption-table row "invariance check +
ESCALATION to terminal-fail-exit absorbed"; `:167` Inputs row; `:368` filing footer —
preserved through the delta chain, no later delta re-states them) pin the C-OD-14
§14.5.3 escalation's `validator.fail.class` value to `terminal-fail-exit`, the C5
retry-exit value that B-138's operator-ratified disposition (a) (CP spec v1.116,
2026-08-09) placed out-of-domain at the wire name. OD spec v1.41 supersedes the
§14.5.3 escalation-table row to `semantic_inconsistency` (`ValidatorFailClass` domain);
this delta re-pins the plan authority so OD spec and OD plan agree (root `CLAUDE.md`
§1.3 chain), the exact sibling of CP plan v2.52's U-CP-41/U-CP-47-era note in the same
PR.

### §0.3 The supersession note (landed unit NOT amended)

**NOTE on U-OD-20 (as-value supersession, v2.35).** The §14.5.3
cause_attribution-invariance ESCALATION carries `validator.fail.class =
semantic_inconsistency` (a `ValidatorFailClass` domain member per CP spec v1.116 /
B-138 disposition (a); OD spec v1.41) — the U-OD-20-era criteria's
"ESCALATION to terminal-fail-exit" phrasing is superseded AS VALUE; the escalation
mechanism, `cause_attribution = replay_semantic_divergence`, `permanence = permanent`,
the always-sampled arm (which keys on `permanence`, unaffected), and the invariance
check itself are unchanged. The C5 retry-exit ROUTING classification of this failure
remains `terminal-fail-exit` per ADR-D5 v1.6 §1.10 — demoted from the wire name, not
deleted. The as-built witness is
`harness-od/tests/test_idempotency_join_dedup.py::test_replay_semantic_divergence_event_attributes`,
asserting `semantic_inconsistency` as of the B-141 cascade PR. The v2.2 criteria stand
as HISTORY (landed-unit text is not retroactively edited); any future re-validation arc
reads THIS note as the operative value authority.

### §0.4 Scope discipline

NOTE-ONLY — **ZERO new units**; **ZERO amended unit bodies**; **ZERO new contract
IDs**; **ZERO roster/namespace/DAG/CXA change**; **ZERO code change owed by this delta
itself** (the carrier/witness updates land in the same PR under OD spec v1.41's §0.3
same-PR cascade). Back-flow record
`.harness/b-141-validator-fail-class-cascade-2026-08-12.md`; clearance marker
`implementation-plan-operational-discipline-v2-35-cleared-2026-08-12.md`.

---

*End of v2.35 delta. The v2.34 body and all prior deltas stand unchanged beneath this
file per the delta-only-plan-chain convention.*
