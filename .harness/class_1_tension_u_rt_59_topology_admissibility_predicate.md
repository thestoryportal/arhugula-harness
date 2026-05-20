# Class 1 Tension: topology admissibility predicate semantic mismatch (U-RT-59 step 4)

**Class:** 1 — load-bearing semantic defect at the composer's topology gate.
**Filed:** 2026-05-20, Phase 7 sub-phase 7b, U-RT-59 landing arc (post-merge follow-up).
**Status:** OPEN — partial-landing absorbed at U-RT-59 follow-up (gate dropped to advisory at v1.6 MVP); strict admissibility gating owed to follow-on arc.

---

## Surfacing event

Advisor cross-check on U-RT-59 post-landing 2026-05-20 (committed at `2f27244` to `main`) surfaced: the composer's step-4 admissibility gate is functionally broken for the common case.

**Spec prose** (§14.7.2 step 4):
> "Verify topology admissibility. `topology = ctx.topology_dispatcher.dispatch(payload.child_manifest_entry)` (returns `TopologyPattern` enum value per C-CP-10 §10.1). `admissible = is_admissible(topology, payload.child_manifest_entry.workload_class)` (per C-CP-10 §10.3). If not admissible, raise typed `SubAgentDispatchTopologyInadmissibleError` mapping to a new fail class."

**Real predicate semantics** (`harness-cp/src/harness_cp/topology_pattern.py:90-101`):

```python
def is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool:
    """Return whether `pattern` is §10.3 cross-pattern admissible at `workload`.

    Answers the C-CP-10 §10.3 question: is `pattern` an admissible *non-primary*
    cross-pattern option at `workload`? ... A False result here means
    "not annotated as cross-pattern admissible at §10.3", not "inadmissible
    outright" — primary-pattern selection is committed separately at C-CP-11 §11.1.
    """
    return (pattern, workload) in _CROSS_PATTERN_ADMISSIBLE
```

**The admissible cross-pattern set is 5 cells** (`_CROSS_PATTERN_ADMISSIBLE`):

- `HIERARCHICAL_DELEGATION + SOFTWARE_ENGINEERING`
- `HIERARCHICAL_DELEGATION + RESEARCH`
- `DECENTRALIZED_HANDOFF + PIPELINE_AUTOMATION`
- `PARALLELIZATION + RESEARCH`
- `PARALLELIZATION + CONTENT_CREATION`

**Every workload's primary topology returns False.** The simplest realistic child sub-agent shape is `SubAgentDispatchPayload(child_manifest_entry=manifest_with_SINGLE_THREADED_LINEAR, workload_class=SOFTWARE_ENGINEERING)`. Under the spec-literal gate, this raises `RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE` — every common-case sub-agent dispatch is rejected.

The U-RT-59 tests passed only because the fixture defaulted to `HIERARCHICAL_DELEGATION + SOFTWARE_ENGINEERING` (an admissible cross-pattern cell). The fixture choice was made during test debugging when the strict gate rejected SINGLE_THREADED_LINEAR; the semantic mismatch was not surfaced.

---

## Routing per `Project_Workflow_v1_8.md` §2.7.6

**Class 1.** The spec uses the wrong predicate name for the intended semantic. `is_admissible` answers "is this an admissible *non-primary* alternative?"; the composer's intent at step 4 is "is this topology *admissible at all* for this workload?" The two differ — primary topologies are admissible (the workload's default per C-CP-11 §11.1) but return False from `is_admissible` because §10.3's table is non-primary-only.

**Partial-landing absorbed at U-RT-59 follow-up** (operator ratification 2026-05-20):

- Drop the strict gate at v1.6 MVP.
- Composer still calls `is_admissible(topology, workload_class)` advisorially (discards result) — preserves the spec-named callsite for documentation traceability.
- Composer proceeds to span emission regardless of the predicate result.
- `SubAgentDispatchTopologyInadmissibleError` type preserved in the module for future strict-gate revival (after C-CP-11 primary-topology lookup is composed at runtime).
- AC #5b retirement criterion narrowed: the topology dispatcher + advisory admissibility predicate are operational at production callsite; the strict gate condition is owed.

**Resolution surface (operator decision required at follow-on arc):**

| Path | Description | Cost surface |
|---|---|---|
| **A — primary-or-cross-pattern check** | Compose a runtime helper `is_primary_or_cross_pattern(topology, workload)` that returns True if `topology == workload.primary_topology` per C-CP-11 §11.1 OR `is_admissible(topology, workload)`. Requires importing the C-CP-11 §11.1 primary-topology lookup table at runtime (may need OD or runtime-side carrier authoring). Restores the gate with correct semantics. | Medium — depends on C-CP-11 carrier availability |
| **B — strict cross-pattern only** | Document explicitly that v1.6 MVP sub-agent dispatch requires the child manifest topology to be a non-primary cross-pattern cell. Workflow authors must pick from the 5 admissible cells. Keeps the spec-literal gate; restricts usability. | Trivial (documentation only) |
| **C — drop the gate permanently** | Composer never gates on admissibility. Spec §14.7.2 step 4 → "topology is dispatched + emitted to span attrs; admissibility is observable at the trace surface, not gated." Removes the failure class. | Trivial (current v1.6 MVP behavior — make permanent via spec revision) |

Recommended at follow-on arc: **Path A** (restore strict gate with correct semantics). Path C is acceptable if operator decides observability suffices for admissibility surfacing.

---

## Workspace progress impact

**U-RT-59 follow-up commit lands** (post `2f27244`):
- `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` step 4 modified: gate dropped; advisory call only.
- `test_lifecycle_sub_agent_dispatch.py::test_topology_inadmissible_raises_typed_error_pre_span` replaced with `test_topology_advisory_admissibility_does_not_gate_at_v1_6_mvp` (verifies no-raise + span emission + child runner invoked for the SINGLE_THREADED_LINEAR + SOFTWARE_ENGINEERING common case).
- `SubAgentDispatchTopologyInadmissibleError` retained in module for future strict-gate revival.

**Retirement event amendment** (.harness/phase-7d-retirement-events-batch-4.md):
- H_T-CP-10 RETIRED narrowed: condition B is "TopologyPattern dispatcher operational + `is_admissible` predicate callable at production callsite (advisory)". Strict-gate retirement criterion is owed to follow-on arc.
- No retirement re-classification; the H_T substitution criterion ("topology dispatcher no longer requires `CLAUDE.md`-prose substitution") is still met — runtime invokes the dispatcher at production execution path even without strict gating.

---

## Related forks

- `[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]` — sister Class 1 from U-RT-59 landing (INFERENCE_STEP binding deferred).
- `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` — sister Class 1 from U-RT-59 landing (CP→OD audit-write deferred).
- `[[class_3_tension_u_rt_59_spec_prose_drift]]` — Class 3 from U-RT-59 landing (5 spec-prose drifts rolled).

Three forks (this one + the two prior) form the U-RT-59 follow-on backlog.

---

## Filing footer

| Field | Value |
|---|---|
| Filed by | Advisor cross-check post-landing on `2f27244` |
| Operator ratification | 2026-05-20 (Path "Drop the gate; file Class 1 + follow-up commit" per AskUserQuestion: "admissibility gate") |
| Resolution target | Follow-on arc; recommended Path A (primary-or-cross-pattern check with C-CP-11 lookup) |
| Re-evaluation trigger | When the C-CP-11 primary-topology lookup is composed at runtime OR when a sub-agent dispatch with a strict admissibility constraint is operator-authored |
