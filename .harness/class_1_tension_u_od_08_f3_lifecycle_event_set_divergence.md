# Class 1 Tension — U-OD-08 F3 lifecycle-event-class set diverges from spec §6.1

**Filed:** 2026-05-16 (Phase 7 sub-phase 7b, OD axis-stream, L3 batch)
**Unit:** U-OD-08 — Map F3 lifecycle events to span events
**Plan body:** `Implementation_Plan_Operational_Discipline_v2_1.md` §3.2.5 (preserved verbatim through v2.7)
**Spec contract:** `Spec_Operational_Discipline_v1_3.md` C-OD-06 §6.1 (§1–§13 preserved verbatim from v1.2; canonical §6.1 at `Spec_Operational_Discipline_v1_2.md` line 378 + table lines 382–389)
**Class:** 1 (halt-execution) — verbatim divergence; routing target = Phase 6 plan revision-pass OR Phase 5 spec revision-pass per operator disposition.

## Defect

U-OD-08 AC #1 asserts `F3LifecycleEventClass` "enumerates exactly **8** values per §6.1 verbatim".
U-OD-08 AC #3 enumerates the 8 plan members with per-class span-event names + attribute namespace sets, also claiming "per §6.1 verbatim".

The plan's 8-member set is **disjoint on 5 of 8 members** from the spec §6.1 table. The cardinality (8) matches; the member set does not.

| Plan §3.2.5 `F3LifecycleEventClass` (AC #1 / AC #3) | Spec §6.1 "eight event classes" table |
|---|---|
| `CHAT_INVOCATION` → span event `"chat"` + `{anthropic., gen_ai.}` | `workflow.start` → span attr on root span + `engine.*` |
| `TOOL_INVOCATION` → `"execute_tool"` + `{mcp., skill., sandbox., files., memory.}` | `step.boundary` → span event on parent + (no namespace) |
| `FALLBACK_TRIGGERED` → `"fallback.triggered"` + `{fallback., engine.}` | `fallback.triggered` → span event on parent + new sibling span + `fallback.*` |
| `FALLBACK_EXHAUSTED` → `"fallback.exhausted"` + `{fallback., engine.}` | `retry.attempt` → span event on parent + new sibling span + `retry.*` |
| `BREAKER_TRIPPED` → `"breaker.tripped"` + `{harness.breaker., engine.}` | `breaker.tripped` → span event on parent + `harness.breaker.*` |
| `RETRY_ATTEMPT` → `"retry.attempt"` + `{retry., engine.}` | `lease.acquired` → span event on parent + `lease.*` |
| `HITL_INVOCATION` → `"hitl.invocation.responded"` + `{hitl.}` | `lease.released` → span event on parent + `lease.*` |
| `SUBAGENT_DISPATCH` → `"subagent.dispatched"` + `{subagent.}` | `workflow.resumed` → span attr on root span + `engine.*` |

Shared members (3): `fallback.triggered`, `retry.attempt`, `breaker.tripped` (with differing namespace sets — e.g. spec `fallback.triggered` has namespace `fallback.*` only; plan adds `engine.`).
Plan-only members (5): `CHAT_INVOCATION`, `TOOL_INVOCATION`, `FALLBACK_EXHAUSTED`, `HITL_INVOCATION`, `SUBAGENT_DISPATCH`.
Spec-only members (5): `workflow.start`, `step.boundary`, `lease.acquired`, `lease.released`, `workflow.resumed`.

The plan's AC #3 namespace sets and span-event names are therefore **not** transcribed from §6.1; AC #1's "verbatim" claim and AC #3's "verbatim" claim are internally contradictory against the cited contract.

The spec §6.1 set is the ADR-F3 v1.1 capability-floor (iv) "observable lifecycle (eight event classes)" — workflow/step/lease/breaker/retry/fallback. The plan's set is a different taxonomy (invocation-shaped: chat/tool/hitl/subagent). The OD subdirectory `CLAUDE.md` §1.1 cites yet a *third* F3 set (`fallback.triggered / fallback.exhausted / breaker.tripped / retry.attempt / lease.acquired / lease.released / topology.fanout.opened / topology.fanout.closed`) — three distinct 8-sets across the artifact corpus. The F3 event set is not canonically pinned.

## Why both audits missed it

- The verbatim audit (`verbatim_audit_od_plan.md` line 70) checked U-OD-08 for **cardinality only** — "`F3LifecycleEventClass` 'exactly 8 per §6.1' — spec §6.1 maps 8 lifecycle event classes. Cardinality clean." It did not check the member set byte-exact, so U-OD-08 is absent from the 10-unit verbatim-divergence list.
- The materializability audit (`materializability_audit_od_plan.md` line 104/260) CLEARED U-OD-08 on carrier-reachability grounds (`F3LifecycleEventClass`/`LifecycleEventMapping` in-unit; cross-axis edge declared). Member-set verbatim conformance is not that audit's axis.

This is the same internal-contradiction shape (`"verbatim" claim against a non-matching set`) the verbatim audit caught for U-OD-02/04/09/11/12/14/30/32/33 — U-OD-08 is a 10th instance the cardinality-only spot-check skipped.

## Disposition required (operator)

Two candidate resolutions, same review class as the v2.5 verbatim-conformance pass:

- **Option A — conform plan to spec §6.1.** Re-author U-OD-08 `F3LifecycleEventClass` + `F3_LIFECYCLE_EVENT_MAPPINGS` + AC #1/#3 to the spec §6.1 table (`workflow.start / step.boundary / fallback.triggered / retry.attempt / breaker.tripped / lease.acquired / lease.released / workflow.resumed` with the §6.1 span-placement + namespace + sampling columns). Phase 6 OD plan revision-pass. No spec change. This is the v2.5-pattern fix.
- **Option B — spec revision.** If the plan's invocation-shaped taxonomy is the intended F3 mapping, the spec §6.1 table (and the ADR-F3 v1.1 capability-floor (iv) "eight event classes" enumeration it transcribes) is wrong. Phase 5 spec revision-pass + ADR-F3 council convening. Higher cost; only if the operator judges the plan's set canonical.

Option A recommended (the spec/ADR are the senior artifacts in the authority chain; the plan diverged).

## Status

🛑 OPEN — U-OD-08 HALTED. Not landed. Skipped in the L3 batch; downstream U-OD-10 (consumes `F3LifecycleEventClass`) inherits the block. No code written for U-OD-08.

---

## ✅ RESOLVED — OD plan v2.8 (2026-05-16)

Resolved by the `implementation-planner` OD-plan v2.8 revision pass (`design-substrate/Implementation_Plan_Operational_Discipline_v2_8.md`), operator-ratified 2026-05-16. See v2.8 §0.2 defect table. The unit is unblocked; lands when OD-7b resumes.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** OD plan v2.8 §0.2 defect table (F3LifecycleEventClass conformed to spec §6.1 8-value set; unit unblocked).

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
