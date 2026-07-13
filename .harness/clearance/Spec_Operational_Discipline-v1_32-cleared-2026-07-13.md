---
artifact: design-substrate/Spec_Operational_Discipline_v1_32.md
version: v1.32
cleared_at: 2026-07-13T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/r-fs-2-final-closure-implementation-plan-v1.md §5 Wave 4
  - .harness/b19-breaker-ambient-attrs-redundancy-analysis.md
  - .harness/b-gapd-toolonly-bootstrap-closure-record.md
merge_commit: <filled at PR merge>
reviewer_chain:
  - operator AskUserQuestion ratification 2026-07-12 (build vs skip-and-close)
  - operator AskUserQuestion ratification 2026-07-12 (amend-once-both-attrs vs cooldown_ms-only-now)
  - advisor() decision-fork review (scope-control against speculative-classifier creep)
supersedes: Spec_Operational_Discipline_v1_31.md
---

# Clearance — `Spec_Operational_Discipline v1.32`

Additive amendment to C-OD-07 §7.1: re-introduces `harness.breaker.cause` + `harness.breaker.cooldown_ms` (CP v1.1's dropped ambient 4-attribute set), landed as two new optional `breaker.tripped` event attributes rather than true ambient state. Grew the canonical schema 7 → 9 attributes; the four non-optional attributes are unchanged. Bundled-absorption arc per root `CLAUDE.md` §11.4 — this spec delta lands in the same PR as the `harness-od` / `harness-cp` / `harness-runtime` code changes (schema module, breaker state machine, CP composition mirror, cardinality checks) and their test updates.

Build-time grounding established that `harness.breaker.cause` is a typed, forward-compatible slot that is vacuous today — no call site in the current runtime can non-speculatively populate any of the four spec-committed values (capability-shortfall pre-empts before the breaker is consulted; the fail-fast exception types don't map to auth_failure; the transient bucket is undifferentiated; the runtime's only real auth-vs-transient discriminator is a bootstrap-only ping classifier that never reaches per-step dispatch). This was surfaced to the operator as a genuine, narrowly-scoped second gate (not a relitigation of build-vs-skip) and ratified as "amend once, both attrs now" — `cooldown_ms` populated, `cause` present and always `None` until a follow-on classifier arc. `harness.breaker.cooldown_ms` is real and unconditionally populated at every trip (`cooldown_seconds * 1000`, no new clock/ambient-state machinery).

No ADR revision — ADR-D6 v1.2 §1.2.1's `harness.breaker.*` substrate anchor is unchanged, only the attribute count widens. No CP spec file edit is owed — the current CP spec head (`Spec_Control_Plane_v1_96.md`) does not re-table this namespace in prose (delta-only convention); the code-level composition mirror (`harness_cp.retry_fallback_namespace` + `cp_namespace_export_manifest`) is the load-bearing enforcement surface and is updated in the same PR.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- A pre-existing, unrelated drift was found and flagged (not fixed) during this arc: the CP-side `HARNESS_BREAKER_NAMESPACE_SCHEMA`'s 7 pre-v1.32 entries carry attribute names that do not match OD's canonical §7.1 emission names — a Class-3 finding the runtime's count-only cardinality check cannot catch, out of scope for this arc.
- See `.harness/clearance/README.md` for marker discipline.
