# Implementation Plan: Control Plane — v2.31 (delta over v2.30)

---

## Change-note (v2.30 → v2.31)

**Scope of revision.** Single-arc canonical-reading amendment at U-CP-74..U-CP-79 absorbing CP spec v1.29 → v1.30 §1.1–§1.6 canonical-reading collapse of the workflow/engine composer signature split per `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` Reading (C) operator-ratified 2026-05-31 (Q1=C uniform resolver-closure / Q2=v1.30 canonical-reading amendment at §16.5.12.2 / Q3=ZERO cross-axis cascade per Reading C / Q4=PR-2 + PR-3 collapse into single PR-stack body). v2.30 unit bodies + DAG + coverage matrix PRESERVED VERBATIM per delta-only-plan-chain convention.

**Trigger.** Probe-first discipline at PR-2 impl-arc opening 2026-05-31 surfaced that the v1.29 §16.5.12.2 workflow-layer recipe column (`procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)`) references `harness_context` which is NOT in the workflow-layer composer body's lexical scope at HEAD. Reading C collapses to the §16.5.12.3 engine-layer pattern uniformly across all 6 composers, avoiding (A) `HarnessContext` carrier-home reshuffle cross-axis cascade and (B) §16.5.12.5 HALT-posture shift composer-site → caller-site.

---

## §1 — Canonical-reading amendment at U-CP-74..U-CP-79

### §1.1 — Uniform composer signature (canonical-reading layer)

All 6 §16.5.2 composer atomic units (U-CP-74 / U-CP-75 / U-CP-76 / U-CP-77 / U-CP-78 / U-CP-79) carry a uniform composer signature extension at v2.31 canonical-reading layer: each composer gains a kw-only parameter `procedural_tier_snapshot_resolver: Callable[[], Identifier]` (REQUIRED; no default) per CP spec v1.30 §1.1 + §1.3 + §1.4.

The composer body invokes the resolver at emission time and populates `EntryPayload.procedural_tier_snapshot_ref` with the returned `Identifier` per CP spec v1.30 §1.2. Per-composer recipes:

| Atomic unit | CP source | Signature extension (v2.31 canonical reading) |
|---|---|---|
| U-CP-74 | `emit_override_state_ledger_entry` | `+ procedural_tier_snapshot_resolver: Callable[[], Identifier]` (kw-only, required) |
| U-CP-75 | `emit_workload_class_selection_state_ledger_entry` | `+ procedural_tier_snapshot_resolver: Callable[[], Identifier]` (kw-only, required) |
| U-CP-76 | `PauseResumeProtocol.emit_pause_resume_state_ledger_entry` (class method) | `+ procedural_tier_snapshot_resolver: Callable[[], Identifier]` (kw-only, required) |
| U-CP-77 | `emit_hitl_tool_call_rewriting_state_ledger_entry` | `+ procedural_tier_snapshot_resolver: Callable[[], Identifier]` (kw-only, required) |
| U-CP-78 | `emit_pause_captured_state_ledger_entry` | `+ procedural_tier_snapshot_resolver: Callable[[], Identifier]` (kw-only, required; PRESERVED VERBATIM from v1.29 §16.5.12.3) |
| U-CP-79 | `emit_resume_attempted_state_ledger_entry` | `+ procedural_tier_snapshot_resolver: Callable[[], Identifier]` (kw-only, required; PRESERVED VERBATIM from v1.29 §16.5.12.3) |

The v2.30 acceptance-criteria for U-CP-74..U-CP-79 (action_id + idempotency-key derivation + outcome-bytes recipe + actor projection + 5-field EntryPayload composition + post-resolve-pre-return firing-site discipline + invariants) are PRESERVED VERBATIM. The v2.31 canonical reading adds two acceptance-criterion extensions per unit:

- **AC v2.31-NEW-α (resolver-invocation):** the composer body invokes `procedural_tier_snapshot_resolver()` exactly once per emission per CP spec v1.30 §1.2 + §1.6 caching-scope mode 1 (per-emission re-resolve; mode 2 admissible at consumer implementer-discretion).
- **AC v2.31-NEW-β (HALT-on-resolver-failure):** the composer propagates resolver-raise to caller per CP spec v1.30 §1.5; ledger_writer is NOT awaited if resolver raises.

Test coverage extends per-unit with: (1) sidecar-populated test verifying `EntryPayload.procedural_tier_snapshot_ref == resolver_returned_identifier`; (2) HALT-on-raise test verifying composer propagates the exception and does NOT invoke ledger_writer. Coverage authored at `harness-cp/tests/test_procedural_tier_resolver_v1_30_apply.py` (single new test module covering all 6 composers + signature-shape probe + HALT-posture probe; 11 NEW tests).

### §1.2 — Runtime wiring (consumer-site)

The runtime wiring layer at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` (the `RuntimeCpIsWiring` frozen dataclass) gains a NEW `procedural_tier_snapshot_resolver: Callable[[], Identifier]` field (sibling to `ledger_writer`). Each of the 6 wiring methods on `RuntimeCpIsWiring` threads `procedural_tier_snapshot_resolver=self.procedural_tier_snapshot_resolver` into the per-composer CP-axis call.

The `materialize_cp_is_wiring_stage` factory gains a `procedural_tier_snapshot_resolver: Callable[[], Identifier]` parameter (REQUIRED, positional after `ledger_writer`). The bootstrap stage 6 (`stage_6_cxa_wiring.execute`) builds the resolver via `make_procedural_tier_snapshot_resolver(ctx)` at stage 6 entry (where `ctx.skills` per stage 2 + `ctx.routing_manifest` per stage 3b are populated) and threads it into the factory call. The `_MutableHarnessContext` exposes the same `.skills` + `.routing_manifest` attribute surfaces as the eventual frozen `HarnessContext`; the cast at stage 6 is structural per the resolver's narrow consumption (skills + routing_manifest only).

### §1.3 — Per-unit body amendment scope (delta-only-plan-chain)

v2.30 unit bodies for U-CP-74..U-CP-79 PRESERVED VERBATIM at the file text layer. The v2.31 canonical reading applies the signature extension + AC v2.31-NEW-α + AC v2.31-NEW-β additively. Downstream readers consult v2.31 §1.1 + §1.2 when interpreting U-CP-74..U-CP-79 signature + AC text at v2.30.

ZERO new atomic units; ZERO removed units; ZERO DAG topology change (U-CP-74..U-CP-79 within-axis edges + cross-axis edges preserved at v2.30 cardinality); ZERO coverage matrix structural delta (the 6 §16.5 composers still cover C-CP-14 / C-CP-15 / C-CP-16 / C-CP-30 / C-CP-37 / C-CP-49 / C-CP-50 per v2.28+); ZERO cross-axis cascade per fork doc §5 Q3 ratification.

---

## §2 — Sections preserved verbatim

| Section | v2.30 status | v2.31 status |
|---|---|---|
| §0 — change-note lineage | v2.28+ lineage | PRESERVED VERBATIM |
| §1 — unit decomposition framework | v2.0+ | PRESERVED VERBATIM |
| §2 — atomic unit bodies (U-CP-00 through U-CP-79) | v2.30 lineage | PRESERVED VERBATIM (file text); v2.31 §1.1 canonical-reading amendment applies at U-CP-74..U-CP-79 |
| §3 — DAG + topology + Kahn execution | v2.0+ | PRESERVED VERBATIM (ZERO edge change at v2.31) |
| §4 — coverage matrix | v2.0+ | PRESERVED VERBATIM (ZERO contract coverage delta at v2.31) |

---

## §3 — Adjacent observations (NOT patched per FM-2)

- **(a) Caching-scope canonicalization carry preserved.** CP spec v1.29 §16.5.12.6 + v1.30 §1.6 enumerate two admissible caching shapes (per-emission vs. per-composer-construction factory closure) without committing CP-spec preference. v2.31 acceptance-criterion-α defaults to per-emission re-resolve; per-composer-construction factory-closure mode admissible at implementer-discretion per CP spec v1.29 §16.5.12.6.

- **(b) Typed-exception surface at HALT remains implementer-discretion.** CP spec v1.29 §16.5.12.5 + v1.30 §1.5 commit HALT posture without committing a typed `ProceduralTierResolutionError` shape. v2.31 acceptance-criterion-β tests against a generic Exception subclass per the spec's discretion clause.

- **(c) `[[strike-revision-on-refined-second-tier-reason]]` does NOT apply at v2.31.** v2.30 unit bodies are NOT STRUCK at v2.31 canonical reading; they are extended additively. Distinct closure-event-class from workflow v1.13 §7.4.7.2 species 2.

- **(d) PR-stack collapse per fork doc §5 Q4.** v2.30 + earlier-planned PR-2 (9 ctx-access producer sites at v1.29 §16.5.12.2 workflow-layer recipe) + PR-3 (3 engine-layer producer sites at v1.29 §16.5.12.3) collapse into single PR-2 at v2.31 per fork doc §5 Q4 explicit ratification. All 6 composers ship at the uniform shape in a single PR.

- **(e) Sub-species candidate at workflow v1.13 §7.4.7.2: `cascade-split-collapse-to-uniform-via-empirical-probe`** mirrors CP spec v1.30 §3 (c) adjacent observation. Catalogued at workspace session notes for future workflow-doc revision pass.

- **(f) `[[probe-first-discipline]]` empirical validation.** PR #94 standing posture amendment 5 caught the structural ambiguity at PR-2 opening in 3 minutes; v2.31 closure validates the discipline empirically. NOT patched per FM-2.

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_31.md` |
| Authored at | Phase 7 sub-phase 7b CP-axis cascade closure arc, 2026-05-31 |
| Authoring authority | `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` Reading (C) operator-ratified AskUserQuestion 2026-05-31 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_30.md` (v2.30) |
| Co-published | CP spec v1.29 → v1.30 NEW delta + impl arc at `harness-cp/src/harness_cp/per_step_override_evaluator.py` + `workload_binding_engine_class_selection.py` + `pause_resume_protocol.py` + `hitl_as_tool_call_rewriting.py` + runtime impl at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` + `harness-runtime/src/harness_runtime/bootstrap/stage_6_cxa_wiring.py` + 11 NEW tests at `harness-cp/tests/test_procedural_tier_resolver_v1_30_apply.py` + adapted tests at 6 sibling composer test modules + harness-runtime CP→IS wiring tests + harness-as secret-fetch-audit test + harness-cp sibling-ledger test (2 stale-carry refreshes from PR #89 IS spec v1.3 absorption) + clearance marker at `.harness/clearance/Spec_Control_Plane-v1_30-cleared-2026-05-31.md` + clearance marker at `.harness/clearance/Implementation_Plan_Control_Plane-v2_31-cleared-2026-05-31.md` + fork-doc Status update PROPOSING → ✅ APPLIED-AS-READING-C + workspace `CLAUDE.md` row bumps |
| Test results | 3533 passed / 10 skipped / 0 failed (was 3522/10/0 pre-arc; +11 NEW v1.30 sanity tests at the new dedicated test module) |
| Revision policy | Delta-only plan chain per workspace `CLAUDE.md` §2.4 convention; v2.30 body PRESERVED VERBATIM; downstream readers apply v2.31 §1 canonical reading when interpreting v2.30 U-CP-74..U-CP-79 signature + AC text |

---

*End of `Implementation_Plan_Control_Plane_v2_31.md`. Parent guidance at workspace root `CLAUDE.md`. Fork doc at `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` (Status: ✅ APPLIED-AS-READING-C).*
