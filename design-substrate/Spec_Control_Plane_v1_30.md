# Spec: Control Plane — v1.30 (delta over v1.29)

---

## Change-note (v1.29 → v1.30)

**Scope of revision.** Canonical-reading amendment at §16.5.12.2 + §16.5.12.3 collapsing the workflow-vs-engine-layer composer signature split into a single uniform pattern across all 6 §16.5.2 composers per `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` Reading (C) operator-ratified 2026-05-31 (Q1=C uniform resolver-closure / Q2=v1.30 canonical-reading amendment at §16.5.12.2 / Q3=ZERO cross-axis cascade per Reading C / Q4=PR-2 + PR-3 collapse into single PR-stack body). v1.29 §16.5.12 + §16.5.3 chapeau substantive content + v1.28 §16.5.6.X audit-stub disposition + v1.27 §16.5 substantive content + v1.26 β.i resolution + v1.25 NEW §16.5 sub-section authoring all PRESERVED VERBATIM per delta-only-spec-file convention.

**Trigger.** PR-2 impl-arc opening 2026-05-31 per workspace CLAUDE.md §10.9 standing posture amendment 5 (probe-first discipline). Empirical probe at HEAD `4294d41` discriminated the workflow/engine-layer split at v1.29 §16.5.12.2 against composer signatures at HEAD: NONE of the 4 workflow-layer composer signatures (U-CP-14 / U-CP-27 / U-CP-30 / U-CP-37) accept `harness_context` as a parameter. The v1.29 §16.5.12.2 recipe column for workflow-layer composers reads `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` but `harness_context` is not in the composer body's lexical scope; the recipe cannot be executed against existing signatures. The recipe presumed a composer-signature reshape that v1.29 did not author.

Three readings surfaced at the fork doc §3:
- **(A)** ctx-passthrough with `HarnessContext` re-home to `harness-core` (cross-axis carrier-home reshuffle + cross-axis cascade)
- **(B)** caller-resolves + passes `Identifier` value (HALT-on-resolver-failure posture shifts composer-site → caller-site at §16.5.12.5)
- **(C)** uniform `procedural_tier_snapshot_resolver: Callable[[], Identifier]` mirror of §16.5.12.3 engine-layer pattern (collapses the split; ZERO cross-axis cascade)

Operator AskUserQuestion 2026-05-31 ratified Reading (C). v1.30 applies it at canonical-reading layer; v1.29 §16.5.12.2 table + sub-bullets PRESERVED VERBATIM per delta-only-spec-file convention; downstream readers apply v1.30 §1 canonical substitutions when interpreting v1.29 §16.5.12.2 + §16.5.12.3 + §16.5.12.4 + §16.5.12.5 + §16.5.12.7.

---

## §1 — Canonical-reading amendment at §16.5.12.2 (workflow/engine split collapse)

### §1.1 — Uniform composer signature shape

All 6 §16.5.2 composers — both workflow-layer (U-CP-14 / U-CP-27 / U-CP-30 / U-CP-37) and engine-layer (U-CP-49 / U-CP-50) — gain a uniform kw-only parameter at the composer function signature:

```python
procedural_tier_snapshot_resolver: Callable[[], Identifier]
```

The parameter is REQUIRED at every composer signature (no default; caller MUST supply at every invocation). The resolver is invoked at composer-body emission time:

```python
procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()
```

This single uniform recipe SUPERSEDES the v1.29 §16.5.12.2 6-row table's per-composer-axis split. The v1.29 table preserved verbatim per delta-only-spec-file convention; canonical reading at v1.30 is the uniform shape above for all 6 composers.

The U-CP-30 class method (`PauseResumeProtocol.emit_pause_resume_state_ledger_entry`) accepts the resolver as a kw-only method parameter; the class body does NOT capture the resolver at construction time per `[[carrier-home-defect-pattern]]` discipline (would inject runtime-axis surface into a CP-axis class — non-issue here, the resolver is a `Callable[[], Identifier]` not a `HarnessContext`, but the per-call kw-only parameter pattern is preserved for consistency with the 5 free-function composers).

### §1.2 — Per-composer recipe (uniform; SUPERSEDES v1.29 §16.5.12.2 table)

| Composer | Recipe at v1.30 |
|---|---|
| U-CP-14 `emit_override_state_ledger_entry` | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |
| U-CP-27 `emit_workload_class_selection_state_ledger_entry` | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |
| U-CP-30 `PauseResumeProtocol.emit_pause_resume_state_ledger_entry` (class method) | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |
| U-CP-37 `emit_hitl_tool_call_rewriting_state_ledger_entry` | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |
| U-CP-49 `emit_pause_captured_state_ledger_entry` | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |
| U-CP-50 `emit_resume_attempted_state_ledger_entry` | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |

ALL 6 rows use the uniform resolver-closure recipe. The workflow-vs-engine-layer split at v1.29 §16.5.12.2 is COLLAPSED at v1.30 canonical reading.

### §1.3 — §16.5.12.3 composer signature extension (uniform across all 6)

v1.29 §16.5.12.3 authored the kw-only parameter at the 3 engine-layer composers; v1.30 extends the same shape to the 3 workflow-layer composers + the 1 workflow-layer class method (U-CP-30). The signature extension at v1.30 is symmetric across all 6:

```python
# Workflow-layer composer signature (U-CP-14 / U-CP-27 / U-CP-37):
async def emit_override_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    post_override_step_config: Mapping[str, Any],
    actor: ActorIdentity,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],  # NEW at v1.30
) -> WriteResult: ...

# Workflow-layer class method (U-CP-30):
class PauseResumeProtocol:
    async def emit_pause_resume_state_ledger_entry(
        self,
        *,
        workflow_id: str,
        step_id: str,
        protocol_event_kind: PauseResumeProtocolEventKind,
        event_sequence_id: int,
        protocol_state_snapshot: Mapping[str, Any],
        actor: ActorIdentity,
        ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
        procedural_tier_snapshot_resolver: Callable[[], Identifier],  # NEW at v1.30
    ) -> WriteResult: ...

# Engine-layer composer signature (U-CP-49 / U-CP-50) — UNCHANGED from v1.29 §16.5.12.3:
async def emit_pause_captured_state_ledger_entry(
    *,
    # ... existing kw-only params ...,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],  # v1.29 + v1.30
) -> WriteResult: ...
```

Both `ledger_writer` and `procedural_tier_snapshot_resolver` are REQUIRED kw-only parameters at every composer signature (no default; caller MUST supply at every invocation). This preserves the §16.5.7 `ledger_writer` floor and authors the sibling resolver floor at the same composer-signature surface. Python semantics: §16.5.7's enumeration is non-exclusive; additional kw-only parameters are admissible without spec contradiction.

### §1.4 — §16.5.12.4 runtime wiring (uniform across all 6)

v1.29 §16.5.12.4 authored the resolver-closure binding at runtime composition time for engine-layer composers via `make_procedural_tier_snapshot_resolver(harness_context)` per IS spec v1.3 §5.2 amendment 2. v1.30 extends the same wiring shape to ALL 6 composers — workflow-layer + engine-layer composer construction sites all bind `procedural_tier_snapshot_resolver` at runtime composition time via the same U-RT-112 factory.

The wiring home per v1.29 §16.5.12.4 PRESERVED VERBATIM: `harness-runtime/src/harness_runtime/lifecycle/` per-composer factory function. At HEAD the wiring layer is consolidated at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` (the `RuntimeCpIsWiring` frozen dataclass + the `materialize_cp_is_wiring_stage` factory function); v1.30 authors the resolver-closure binding at this single wiring home for all 6 composers.

The `RuntimeCpIsWiring` dataclass gains a `procedural_tier_snapshot_resolver: Callable[[], Identifier]` field (sibling to the existing `ledger_writer` field); `materialize_cp_is_wiring_stage` gains a `procedural_tier_snapshot_resolver` parameter; bootstrap stage 6 (`stage_6_cxa_wiring.execute`) builds the resolver via `make_procedural_tier_snapshot_resolver(ctx)` at stage 6 entry (where `ctx.skills` per stage 2 + `ctx.routing_manifest` per stage 3b are both populated) and threads it into `materialize_cp_is_wiring_stage`. Each per-composer wiring method on `RuntimeCpIsWiring` threads `procedural_tier_snapshot_resolver=self.procedural_tier_snapshot_resolver` into the per-composer CP-axis call.

### §1.5 — §16.5.12.5 failure-mode posture (uniform across all 6)

v1.29 §16.5.12.5 authored the HALT-on-resolver-failure posture at composer-site for engine-layer composers; v1.30 extends the same posture to ALL 6 composers. The composer-site HALT discipline is uniform: if `procedural_tier_snapshot_resolver()` raises at composer invocation (programming error at composition time per U-RT-112 AC #1 pure-function semantics; transient retry does NOT apply), the composer MUST propagate the exception to its caller.

§16.5.12.5 sub-bullets (workflow-context emission cannot emit `None` sidecar / resolver failure modes are programming errors / typed-exception surface is implementer-discretion) PRESERVED VERBATIM at v1.30; they apply uniformly to all 6 composers.

### §1.6 — §16.5.12.7 invariants (uniform across all 6)

v1.29 §16.5.12.7 invariants 1–6 PRESERVED VERBATIM at v1.30. The invariants are stated at the §16.5.2 6-composer surface; v1.30's signature uniformity is a refinement that does not change the invariant text.

---

## §2 — Sections preserved verbatim

| Section | v1.29 status | v1.30 status |
|---|---|---|
| §16.5.12.1 — Field scope and authority | Authored at v1.29 | PRESERVED VERBATIM |
| §16.5.12.2 — Per-composer population recipe (table) | Authored at v1.29 with workflow/engine split | PRESERVED VERBATIM (file text); canonical reading at v1.30 §1.2 SUPERSEDES |
| §16.5.12.3 — Composer signature extension at engine-layer composers | Authored at v1.29 for 3 engine-layer | PRESERVED VERBATIM (file text); canonical reading at v1.30 §1.3 extends to all 6 |
| §16.5.12.4 — Runtime wiring at engine-layer composers | Authored at v1.29 for engine-layer | PRESERVED VERBATIM (file text); canonical reading at v1.30 §1.4 extends to all 6 |
| §16.5.12.5 — Failure-mode posture (composer-site) | Authored at v1.29 | PRESERVED VERBATIM (file text); canonical reading at v1.30 §1.5 applies uniformly |
| §16.5.12.6 — Caching scope (composer-site implementer-discretion) | Authored at v1.29 | PRESERVED VERBATIM |
| §16.5.12.7 — Invariants | Authored at v1.29 | PRESERVED VERBATIM |
| §16.5.3 chapeau (5-field framing refresh) | Canonical-reading amendment at v1.29 | PRESERVED VERBATIM |
| §16.5.1 — §16.5.11 substantive content | v1.25–v1.28 lineage | PRESERVED VERBATIM |

The v1.29 §16.5.12.2 table is preserved at file text; the v1.30 §1.2 uniform recipe table is the canonical reading. The workflow/engine split language at v1.29 §16.5.12.2 sub-bullets ("5 workflow-layer composers ... call `resolve_procedural_tier_snapshot(harness_context)` directly" / "3 engine-layer composers without ctx-access ... accept `procedural_tier_snapshot_resolver` as a kw-only parameter") is SUPERSEDED at v1.30 canonical reading by the uniform signature pattern at §1.1 + §1.3.

---

## §3 — Adjacent observations (NOT patched per FM-2)

- **(a) `[[spec-recipe-references-symbol-not-in-composer-scope]]` sub-species cardinality.** v1.29 §16.5.12.2 workflow-layer recipe column was the first instance of the sub-species (recipe references `harness_context` not in composer scope). v1.30 closes the instance; cardinality 1 at the catalogue. Awaits second instance before workflow-doc promotion per workflow v1.13 §7.4.7.2 sub-species column candidate at fork doc §6 provenance.

- **(b) `[[strike-revision-on-refined-second-tier-reason]]` does NOT apply at v1.30.** v1.29 §16.5.12.2 workflow-layer recipe sub-bullets are SUPERSEDED at canonical reading, not STRUCK on a refined second-tier reason. The face-value reading at v1.29 (workflow-layer composers can access `harness_context`) is empirically false at HEAD; the canonical reading at v1.30 is the structural correction, not a STRIKE preservation. Distinct closure-event-class from workflow v1.13 §7.4.7.2 species 2.

- **(c) Sub-species candidate at workflow v1.13 §7.4.7.2: `cascade-split-collapse-to-uniform-via-empirical-probe`.** v1.29 authored a workflow/engine cascade split at §16.5.12.2; PR-2 impl-arc probe surfaced that the split's workflow-half is structurally impossible against existing composer signatures; canonical reading at v1.30 collapses to the uniform engine-half pattern. Distinct closure-event-class from prior species 3 sub-species (resolved-but-carry-stale lineage) — this operates on cascade-design-vs-impl-feasibility. Cardinality 1; awaits second instance before workflow-doc promotion.

- **(d) Cross-axis cascade verification.** Reading C closure verified via grep at design-substrate/: ZERO cite cascade owed at AS spec / OD spec / IS spec / runtime spec / ADR-F1..D6 / ADD / PRD / CXA v2.17. The §16.5.12.2 workflow/engine framing is intra-CP-spec; collapsing it to uniform shape does not propagate. NOT patched per FM-2 — confirms Q3=ZERO cross-axis cascade ratification.

- **(e) Probe-first discipline empirical validation.** The 3-minute empirical probe at PR-2 impl-arc opening surfaced the structural ambiguity that would have manifested as an X-AL-3 violation 30+ minutes into impl arc had the discipline been skipped. v1.30 is the canonical apply pass closure of the probe finding. Validates standing posture amendment 5 (probe-first at substantive arc opening per workspace CLAUDE.md §10.9). NOT patched at CP spec; pattern catalogued at workspace session notes.

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_30.md` |
| Authored at | Phase 7 sub-phase 7b CP-axis cascade closure arc, 2026-05-31 |
| Authoring authority | `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` Reading (C) operator-ratified AskUserQuestion 2026-05-31 |
| Predecessor | `Spec_Control_Plane_v1_29.md` (v1.29) |
| Co-published | CP plan v2.30 → v2.31 single-arc absorption at U-CP-74..U-CP-79 + impl arc at `harness-cp/src/harness_cp/per_step_override_evaluator.py` + `workload_binding_engine_class_selection.py` + `pause_resume_protocol.py` + `hitl_as_tool_call_rewriting.py` + runtime impl at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` + `harness-runtime/src/harness_runtime/bootstrap/stage_6_cxa_wiring.py` + clearance marker at `.harness/clearance/Spec_Control_Plane-v1_30-cleared-2026-05-31.md` + fork-doc Status update + workspace `CLAUDE.md` row bump + `harness-cp/CLAUDE.md` row bump |
| Revision policy | Delta-only spec file per workspace `CLAUDE.md` §2.3 convention; v1.29 body PRESERVED VERBATIM; downstream readers apply v1.30 §1 canonical substitutions when interpreting v1.29 §16.5.12.2 + §16.5.12.3 + §16.5.12.4 + §16.5.12.5 + §16.5.12.7 |

---

*End of `Spec_Control_Plane_v1_30.md`. Parent guidance at workspace root `CLAUDE.md`. Fork doc at `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` (Status: ✅ APPLIED-AS-READING-C).*
