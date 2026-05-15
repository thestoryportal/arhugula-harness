# Pipeline — Fork Queue

*Forks awaiting operator decision. The review-ahead lane (and the coding lane,
on its own spec-read) appends here; neither edits canonical artifacts
(`review-pipeline.md` §3). Operator resolves; an applicator skill (`spec-writer`
/ `implementation-planner`) applies; the reviewer re-checks. Updated 2026-05-15.*

## Open forks — operator decision owed

Items 1–8 dispositioned by the pilot review-ahead pass
(`.harness/adversarial_review_cp_od_v25_reclearance.md`, 2026-05-15). The
reviewer classifies and recommends a resolution *shape* — it does not decide.
Item 9 surfaced by the coding lane's own spec-read.

| # | Item | Class (§4.1 / §2.7.6) | Blocks | Resolution shape |
|---|---|---|---|---|
| 1 | **U-CP-43** — 4-axis `GateLevelInput` diverges from CP spec §19.1: `per_tool_gate_level` absent, `deployment_surface` plan-added, `MCP_TRUST`/`DEPLOYMENT_SURFACE` floors spec-silent | Class 3 / **Class 1 halt** | U-CP-43 | spec-silence design gap — operator decision on whether §19.1 extends or the plan conforms; routes to CP spec or CP plan revision |
| 2 | **U-OD-09** — acc #2 Required/Conditional tier split has no OD spec §7.1 basis | Class — / **Class 1 halt** | U-OD-09 | spec-silence — operator decides spec basis or plan conforms |
| 3 | **U-CP-08** — `FallThroughCause` design gap (silent H_T design extension if invented at the unit) | — / **Class 1** | U-CP-08 | back-flow: CP spec/ADR — needs the cause taxonomy committed upstream |
| 4 | **U-CP-23** — single-vs-dual `default_pattern` structural mismatch | Class 2 / **Class 2** (non-halting) | — (U-CP-23 clears) | operator picks the structural reading; non-blocking for landing |
| 5 | **U-CP-11** — LEASE naming call | — / **Class 2** | U-CP-11 | operator naming decision |
| 6 | **U-OD-28** — `CollectorPlacement` / §20.1 surface — conformance target undetermined | — / **Class 2** *(proposing)* | U-OD-28 | operator resolves the §20.1 conformance target |
| 7 | **U-OD-29** — plan `TIER_0..TIER_3` diverges from ADR-D2 §1.7.1 canonical `{tier-1..tier-4}`; the plan's §1.2 citation is also wrong (§1.2 is the provider-class enum) | — / **Class 1** (authority-chain-determinate) | U-OD-29 | conform plan to ADR-D2 §1.7.1 — determinate, like §4A; operator-accept → `implementation-planner` revision |
| 8 | **F1-01** — U-CP-22 v2.5 acc #3 silently SCREAMING_SNAKE_CASE-renders §10.3 workload identifiers without declaring the edit in §0.3 (stem-match preserved) | Class 1 / **Class 3** (informational) | — | inline doc-hygiene fix to CP plan v2.5 §0.3 change-note |
| 9 | **U-AS-07** — §3.1 signature types `ToolContract.required_secrets` as final `List<SecretAllowlistEntry>`, but `SecretAllowlistEntry` is declared by U-AS-22 (which depends on U-AS-07); U-AS-22 line 1125 says it "populates the previously-empty-shape field at U-AS-07" — the plan never specifies U-AS-07's interim materialization shape | — / **Class 2** *(provisional — coding-lane classification; AS not yet under review-ahead)* | U-AS-07 | operator picks U-AS-07's interim `required_secrets` element-type shape (empty-only / placeholder / U-AS-22 redefines model); routes to AS plan clarification |

**Note on items 1, 2, 3:** the pilot reviewer confirmed these are pre-existing
spec-silence design gaps the plans themselves declared and carried — NOT
defects introduced by the §4A conformance pass. The conformance pass correctly
conformed everything authority-chain-determinate and correctly refused to
silently absorb the spec-silence items (X-AL-3 honoured).

## Resolved forks

| Item | Resolution | Date |
|---|---|---|
| Tension 001 — C-IS-03 §3 "four" vs 5 rows | spec fixed in-CLI; block cleared | 2026-05-15 |
| Tension 002 — TopologyPattern enum 3-way divergence | operator signed off Set 2 (spec C-CP-10 §10.1); conformed at 4 loci | 2026-05-15 |
| Tension 003 — `WorkloadClass` undeclared | declared in `harness-core` via new U-CP-00 | 2026-05-15 |
| Tension 004 — U-OD-04 span schema divergence | subsumed into OD §4A audit; conformed in OD plan v2.5 | 2026-05-15 |
