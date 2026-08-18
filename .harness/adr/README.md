# `.harness/adr/` — H_E architecture decision records

**Namespace rule.** Records here are `ADR-HE-N` and govern **H_E dev tooling** — `tools/`,
`tools/hooks/`, `.claude/skills/`, the autonomous loop and its lanes. The `design-substrate/`
series (`ADR-F1..F5` foundational, `ADR-D1..D8` derivative) is the **H_T** canon consumed by Phase 7
as product architecture.

The two must not share a number space. Filing an H_E tooling decision as `ADR-D9` would misfile
tooling as product architecture and collapse the substrate boundary `CLAUDE.md` invariant **X-AL-1**
places at the MCP server process; **CP-AL-1** independently forecloses reading H_E orchestration as
H_T's `TopologyPattern` enum. The `HE` prefix makes that collision structurally unrepresentable.

Records here therefore do **not** extend the H_T design and do not implicate invariant I-2 / X-AL-3.
Posture is **mode-agnostic** workspace-operational work per `CLAUDE.md` §11.2.

---

## The set

Filed 2026-08-17 against repo `17011f89c`, from the loop + lanes design corpus.

| Record | Decides | Status |
|---|---|---|
| [ADR-HE-1](ADR-HE-1_loop_lanes_coordination_architecture.md) — coordination architecture | How lanes build in parallel and land serially: lock-free filesystem CAS, three-state reservation, single-writer merge door, environment isolation | **Accepted** (F + 11 derivatives) · 4 proposed extensions · 2 open |
| [ADR-HE-2](ADR-HE-2_review_gate_and_completion_semantics.md) — review-gate and completion semantics | What makes a verdict count: parse-not-exit-code, `REVIEWER_UNAVAILABLE` as BLOCK-equivalent, CANCELLED as INCOMPLETE, D-C failover at an identical bar | **Accepted** (BUILD-PLAN Arc 1 + D-C) · 1 open |
| [ADR-HE-3](ADR-HE-3_record_and_measurement_substrate.md) — record and measurement substrate | What the loop records about itself: extend-don't-replace, the common finding field set, `arc_type` at open, explicit phase spans, the live shadow trial | **Accepted** (Arcs 2/3/7 + D-B/D-D) · 1 open collision |
| [ADR-HE-4](ADR-HE-4_defect_mechanization_and_grounding.md) — defect mechanization and grounding | Where loop cost is actually attacked: mechanize defect classes upstream of review, never cap review | **Accepted** §3.1 (D-A, Arcs 4–6) · **Proposed** §3.2 |

**The authority chain over all four is at [HE-1 §0](ADR-HE-1_loop_lanes_coordination_architecture.md#0-corpus-and-authority-chain)** —
BUILD-PLAN (operator-ratified) → design v1 (consolidated full-loop) → design v2 (head, lanes-narrow),
with earlier links governing where later ones are silent. Read it before citing any of the four, and
note that **three build sequencings coexist** across the corpus (Arc 1–7 ratified, Layer 0–4,
Phase 0/1/2) and are not interchangeable.

## Conventions

- Template per `.claude/skills/systems-architect` §2.4: Status · Context · Decision · Rationale ·
  Consequences · Alternatives considered (≥2) · References.
- `[V]` in a record means **verified at HEAD in the authoring session**, and each record's References
  section separates verified cites from council-recorded ones. Absence claims rot fastest — re-verify
  before relying on one.
- Superseding is by a new `ADR-HE-N` citing the prior record, not by in-place rewrite. In-place
  amendment is acceptable only before a record has been consumed, and requires a dated change-note
  (see HE-1 v1.1).
