# R-003 checkpoint — orientation complete, implementation pending

**Roadmap entry:** `R-003` (Project_Roadmap_v1.md §5.2) — producer-site lifts of `EntryPayload.procedural_tier_snapshot_ref`.
**State:** ORIENTATION COMPLETE 2026-05-31; **RESUME AT: Cluster A (runtime dispatchers).**
**Posture:** phase-7 (edits `harness-*/src` + tests). **cross_axis: yes. advisor_required: yes (already satisfied — see §1).**

A fresh session should read THIS file (not re-derive) and start implementing Cluster A. The hard analysis below is settled.

---

## §1 — What's already resolved (do NOT re-litigate)

1. **X-AL-3 risk CLEARED — this is NOT a Class 1 scope-extension fork.** The field owner is **IS spec v1.3 §C-IS-05 §5.1** (in `design-substrate/Spec_Information_Substrate_v1.md`, v1.3 change-note). §5.1 states a **general principle**: `procedural_tier_snapshot_ref = None` is canonical for entries written *outside an active workflow context* (bootstrap-stage + operator-explicit administrative entries); *active-workflow-context* emissions must populate it. IS §5.1 gates IS-2 retirement on "full producer-site lift completion" with the ~13 sites "deferred to follow-on per-axis arcs" — R-003 is one. CP spec §16.5.12.1's "6 §16.5.2 composers in scope at this amendment" was CP's *amendment-scoping*, not a global cap. So lifting workflow-context sites is spec-intended phase-7 work. (Advisor consulted 2026-05-31, 55th `[[advisor-before-substantive-work-for-cross-axis-blockers]]` application — caught that I'd anchored on the CP restatement; IS §5.1 is the settling authority.)

2. **Operator scope decision (AskUserQuestion 2026-05-31) = Option A:** *lift the 4 workflow-step sites; document sites 5/6/7 as `None`-canonical.* This is the ratified scope. Do not expand it without a new operator AUQ.

## §2 — Per-site classification + plan

| # | Site | Class | Action |
|---|---|---|---|
| 1 | `harness-cp/.../sibling_ledger_entry_composition.py` `construct_sibling_ledger_entry` (~:144) | workflow-context | **LIFT** (Cluster B) — thread resolved value from the runtime caller `RuntimeCpIsWiring.emit_sibling_ledger_entry`, which already holds `self.procedural_tier_snapshot_resolver`. The bare CP helper takes a new `procedural_tier_snapshot_ref: Identifier \| None = None` param. (NOTE: the second Explore report mis-claimed "no resolver needed" — that conflated IS-computed `response_hash`/`prior_event_hash` with the producer-supplied sidecar; the sidecar IS producer-supplied, so site 1 does need the value, supplied by the caller.) |
| 2 | `harness-cp/.../workflow_driver.py` `_append_step_ledger_entry` (~:1360) | workflow-context | **LIFT** (Cluster B) — add `procedural_tier_snapshot_resolver: Callable[[], Identifier] \| None` to the `DriverContext` Protocol (~:264-359, after `cp_is_wiring`) + to the concrete `HarnessContext`; invoke at the `EntryPayload(...)` construction. harness-cp does NOT depend on harness-runtime — resolver arrives via the Protocol, never an import. |
| 3 | `harness-runtime/.../lifecycle/sub_agent_dispatch.py` `RuntimeSubAgentDispatcher._compose_and_persist_audit` 8b `f2_payload` (~:474) | workflow-context | **LIFT** (Cluster A) — add `procedural_tier_snapshot_resolver: Callable[[], Identifier]` field to the `@dataclass(slots=True)` (~:351-413, after `time_source`); invoke at the `f2_payload = EntryPayload(...)`. |
| 4 | `harness-runtime/.../lifecycle/hitl_gate_composer.py` `RuntimeHITLGateComposer._compose_and_persist_audit` 8b-HITL `f2_payload` (~:770) | workflow-context | **LIFT** (Cluster A) — add the same field to the `@dataclass(slots=True)` (~:545-658); invoke at the `f2_payload = EntryPayload(...)`. |
| 5 | `harness-runtime/.../lifecycle/audit_writer.py` `append` (~:120) | OUTSIDE (audit-wrap of pre-signed OD entries; separate ledger family) | **DOCUMENT** `None`-canonical per IS §5.1 — code comment, no lift. |
| 6 | `harness-runtime/.../lifecycle/as_is_wiring.py` `append` secret-fetch (~:110) | OUTSIDE (fires at bootstrap/provider-construction) | **DOCUMENT** `None`-canonical — code comment, no lift. |
| 7 | `harness-is/.../shadow_git_rollback.py` `perform_rollback` (~:114) | OUTSIDE (administrative/recovery) | **DOCUMENT** `None`-canonical — code comment, no lift. |

## §3 — The canonical pattern to mirror

`harness-runtime/.../lifecycle/cp_is_wiring.py` already does this for the 6 §16.5 composers:
- `RuntimeCpIsWiring` (~:98-119) holds `procedural_tier_snapshot_resolver: Callable[[], Identifier]`.
- Built by `make_procedural_tier_snapshot_resolver(ctx)` (from `harness_runtime.lifecycle.procedural_tier_snapshot`), a closure that re-resolves over the captured `ctx` at every call (U-RT-112 AC #8 direct-compute; no caching).
- Resolver returns `Identifier` (lowercase 64-char hex). `Identifier` from `harness_is.state_ledger_entry_schema`.

## §4 — The one architectural wrinkle to handle (Cluster A)

`RuntimeSubAgentDispatcher` + `RuntimeHITLGateComposer` are constructed at **bootstrap stage 5 (LOOP_INIT)**, but `cp_is_wiring` builds its resolver at **stage 6 (CXA_WIRING)**. The resolver factory only needs `ctx.skills` (stage 2) + `ctx.routing_manifest` (stage 3b), both populated by stage 5 — so **build the resolver at stage 5** and thread it into both dispatcher ctors. (Two resolver closures over the same `ctx`, one at stage 5 + the existing one at stage 6, are equivalent and both correct; do not try to share unless trivial.) Find the stage-5 construction sites: grep `RuntimeSubAgentDispatcher(` + `RuntimeHITLGateComposer(` under `harness-runtime/src/harness_runtime/bootstrap/`.

## §5 — Verification + close shape

- **Test pattern:** mirror `harness-cp/tests/test_procedural_tier_resolver_v1_30_apply.py` — zero-arg resolver fixture returning `Identifier("b"*64)`; assert `captured_payload.procedural_tier_snapshot_ref == expected_ref`; + a HALT test (resolver raises → no ledger write).
- **Must pass (R-003 verification, integration):** each lifted site populates the sidecar via the resolver closure; no lifted site bypasses it; documented sites keep `None`.
- **Close shape:** PR-per-cluster (Cluster A runtime, Cluster B CP). Run `uv sync --all-packages` then `uv run pytest` (harness-runtime + harness-cp) green before merge.
- **Cascade:** landing Cluster A + B + the 5/6/7 docs unblocks `R-001-h-t-is-2-retired` (IS-2 PARTIAL → RETIRED). After both clusters merge, refresh roadmap §5.2 R-003 → RESOLVED + dashboard per §12.

## §6 — Suggested resume command

Fresh session: the SessionStart hook will say `next=R-003`. Type `continue` → read this checkpoint → implement Cluster A (sub_agent_dispatch + hitl_gate_composer), test, PR. No advisor re-run needed (the cross-axis blocker is resolved at §1); call advisor only if a NEW cross-axis question surfaces mid-impl.
