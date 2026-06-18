# Class 1 Fork — B-HITL-PLACEMENT-PER-STEP-PRODUCER (the workflow→per-step HITL placement producer that makes the wrap-time gates fire in production)

**Filed:** 2026-06-18 · R-FS-1 standalone `B-*` arc **B-HITL-PLACEMENT-PER-STEP-PRODUCER** (the NINTH standalone arc since the FROZEN order completed; surfaced by the B-TOOL-GATE #653 Codex [P1] decorrelated finding; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` registered as a follow-on by #653, now BUILT). Bundled-absorption posture: **runtime spec v1.60 → v1.61 (§14.8.2-step-1 reconciliation) + CP spec v1.40 → v1.41 (NEW §25.3 `StepExecutionContext.hitl_placements` field) + `harness-cp/src` + `harness-runtime/src` + by-execution tests + 2 clearance markers — NO operator gate.**

**Status:** ✅ RESOLVED + BUILT. **Impl-against-cleared-spec** on the FOLD + PRE_ACTION-coupling (spec'd at runtime §14.8.1 + §14.8.4) + a **faithful-materialization reconciliation** of the §14.8.2-step-1 read surface. This is filed as back-flow + the build-record because it (a) edits `design-substrate/**` (two small reconciliation/field deltas) and (b) registers a follow-on whose fold semantics are genuinely under-specified.

---

## §1 The gap (the B-TOOL-GATE #653 Codex [P1] finding)

The wrap-time HITL gate composer (`RuntimeHITLGateComposer`, all three sites — inference `PRE_ACTION`, sub-agent `SUB_AGENT_BOUNDARY`, tool `PRE_ACTION` per B-TOOL-GATE #653) fires only when its step-1 placement read is non-empty. Runtime spec §14.8.2 step 1 read `step.hitl_placements` "populated at workflow-binding time per U-CP-13 + U-CP-38". But:

- `hitl_placements` is declared at the **WORKFLOW** level (`WorkflowManifestEntry.hitl_placements`, C-CP-17 §17.3) — a `tuple[HITLPlacement, ...]`.
- The per-step `WorkflowStep` the driver dispatches is frozen + `extra="forbid"` and carries **only** `step_id`/`step_kind`/`step_payload` — workflow *body*, not config (C-CP-25 §25.2: "the manifest carries config incl. HITL placements; the step sequence carries the declarative body steps").
- **No src bound the workflow-level placements onto the per-step steps.** So `step.hitl_placements` was **always `()`** through the real `WorkflowManifestLoader`→driver path → **no wrap-time HITL gate fired in production for ANY step kind.** Every existing gate e2e test attaches placements via a `_StepWithPlacements` proxy (`[[test-bypass-as-runtime-truth-pattern]]` at workspace scale).

This is the unbuilt half of the B3 spine-ledger "placement composition is a placeholder" residual.

---

## §2 Spec'd-ness decomposition (advisor-decomposed, 2 rounds — the fork-vs-impl decision)

The advisor's discriminator: read the governing runtime **§14.8.1 + §14.8.2** directly (not the composer docstring paraphrase) and decompose, rather than pre-emptively forking the whole arc.

| Sub-decision | Spec status | Disposition |
|---|---|---|
| **Fold semantics** (does a workflow placement apply to all steps? how does the composer select?) | **SPEC'd** — §14.8.1 wrap-asymmetry footnote: the composer "overlays the existing inner composers per `WorkflowManifestEntry.hitl_placements` declarations"; §17.1 trigger table: each placement applies to "all cells"; the composer filters by its `applicable_placements` set (§14.8.2 step 2). | impl-to-cleared-spec |
| **PRE_ACTION → {inference, tool} coupling** | **SPEC'd** — §14.8.4: PRE_ACTION "wraps `INFERENCE_STEP` inner dispatchers (and future `TOOL_STEP` dispatchers)". The inference+tool double-gate is intended, not an artifact to suppress. | impl-to-cleared-spec |
| **Read surface / producer mechanism** | **Under-specified** — §14.8.2 step-1 named `step.hitl_placements`, but the frozen 3-field `WorkflowStep` cannot carry config, and the named producer (U-CP-13 override evaluator) outputs `StepEffectiveBinding`, not `step`. The "populated at workflow-binding time" text always referenced a producer that never existed. | **faithful-materialization reconciliation** (the read surface is named concretely; not a new design surface) — bundled-absorption, NOT a fork-halt |
| **Per-step `StepOverride.hitl_placement` override fold** (singular override × workflow tuple) | **SILENT** at C-CP-06 §6.2 (specifies only `f3_invocation` per-step overrides; the `hitl_placement` field is an impl addition with no §6.2 prose) | **follow-on** `B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD` (design-fork-first — its add-vs-replace semantics are a genuine decision) |

**No operator gate** (`[[feedback-gate-only-on-meaningful-architecture-change]]`): additive + opt-in (default `()` → byte-identical; a gate fires only when the operator declares a placement), no committed-invariant sacrifice, no new contract / fail-class / manifest field. The declaration surface (`WorkflowManifestEntry.hitl_placements`) + the per-step context (`StepExecutionContext`) already exist; wiring an existing manifest value onto the per-step context is a binding fix (the `tenant_id` / `parent_gate_level` precedent).

---

## §3 The build

**Read surface = `StepExecutionContext.hitl_placements` (CP spec v1.41 §25.3, additive defaulted field).** Chosen over two alternatives:
- (a) widening `WorkflowStep` with a placements field — rejected: violates the §25.2 config/body split (placements are config, not body).
- (b) carrying placements on `StepEffectiveBinding` — rejected: `StepEffectiveBinding.model_dump(...)` feeds the §16.5.4 per-step override outcome-hash (`compose_override_entry_payload`), so a field there would shift the override-entry hash for override-bearing steps (a hash-coherence regression) and is semantically wrong (a workflow placement is not a per-step override). `StepExecutionContext` is NOT hashed into any ledger entry, so it is inert to §5.2 + §16.5.4.

**Producer = the CP driver.** `hitl_placements=manifest_entry.hitl_placements` is set at all **5** per-step `StepExecutionContext` construction sites (`harness-cp/src/harness_cp/workflow_driver.py`): the `SINGLE_THREADED_LINEAR` per-step site + the parallelization fanout parent + the EVALUATOR_OPTIMIZER per-step site + the orchestrator context + the hierarchical/decentralized spawning context. Branch children inherit it via `compose_branch_child_context`'s `model_copy` (the mechanism shared by every branch-based topology) — so all 6 topologies are covered.

**Composer reads `step_context.hitl_placements`** (`harness-runtime/.../hitl_gate_composer.py` step 1), reconciling runtime §14.8.2 step-1 (`step` → `step_context`). A `getattr(step, "hitl_placements", ())` fallback is preserved as a test-proxy compat surface only (never populated in production).

**Import cycle broken.** `harness_cp.hitl_placement` imported `StepExecutionContext`/`WorkflowStep` from `workflow_driver_types` for the `hitl_gate` signature; that import moved under `TYPE_CHECKING` (the annotations are string-only via `from __future__ import annotations`), so `workflow_driver_types` can import `HITLPlacement` at runtime for the new field with no cycle and no `model_rebuild` fragility.

---

## §4 Decorrelated review + non-vacuity verification

- **advisor (full-transcript, 2 rounds):** round 1 forced the §14.8.1/§14.8.2 read that decomposed fork-vs-impl (the read confirmed fold + PRE_ACTION are spec'd → impl-to-cleared-spec, not a whole-arc fork); round 2 confirmed the no-operator-gate determination + the §6.2-silent → scope-split (the per-step override fold is the genuine fork candidate, registered as the follow-on) + the build-time completeness/negative-control/broader-suite obligations.
- **out-of-family Codex (on the diff):** pre-merge (pending at filing).

**Non-vacuity (the deliverable; cf. B-TOOL-GATE #653 wired-but-production-dead):**
- **Composer reads the producer surface** — `test_lifecycle_hitl_gate_composer.py::test_dispatch_reads_placements_from_step_context_gate_fires`: a PLAIN `WorkflowStep` (no `hitl_placements`) + a `step_context` carrying a PRE_ACTION placement → the gate fires (surface invoked, inner dispatched on APPROVE). The plain step forces the read off `step_context`.
- **Negative control** — `test_dispatch_empty_step_context_placements_delegates_to_inner`: plain step + empty `step_context` placements → no surface call, no HITL spans, no ledger/audit write (byte-identical to pre-arc).
- **Producer wires the manifest across topologies, by-execution through the real `execute_workflow`** — `test_workflow_driver.py::test_driver_surfaces_manifest_placements_onto_step_context[SINGLE_THREADED_LINEAR|DECENTRALIZED_HANDOFF]`: the dispatched step's `step_context.hitl_placements` carries the manifest's declared placements (linear = direct construction; decentralized-handoff = inherited via `compose_branch_child_context`). Negative control: empty manifest → `()`.
- **FULL-CHAIN witness (advisor pre-merge catch — the producer + composer halves composed in ONE real run, NOT two half-proofs).** `test_run_workflow_elicitation_e2e.py::test_e2e_manifest_placement_fires_gate_via_producer`: a workflow declaring `hitl_placements=(PRE_ACTION,)` at the **manifest** + dispatching a **PLAIN `WorkflowStep`** (no proxy), run through the real `run_workflow` MCP tool → `execute_workflow` → real `RuntimeHITLGateComposer` → the gate fires (`ctx.elicit` invoked once; `hitl.gate.evaluated` span emitted; SUCCESS). This witnesses producer → `step_context` → real composer → gate in one run — the chain the proxy-based round-trip test bypasses (it would pass even if the producer were broken). The advisor flagged that the original producer test (capturing dispatcher, no composer) + composer test (hand-built `step_context`, bare binding) never met — the exact B-TOOL-GATE #653 compositional-gap shape; this test closes it.
- **Excluded-cell sanity (advisor secondary catch — a newly production-reachable failure mode).** `test_lifecycle_hitl_gate_composer.py::test_dispatch_declared_placement_on_excluded_cell_raises_sanely`: a declared placement on an EXCLUDED `(TEAM_BINDING, PURE_PATTERN_NO_ENGINE)` cell → the composer raises the typed `HITLCellExcludedError` (C-CP-18 §18.1; driver surfaces FAILED), NOT a crash. The "byte-identical" claim is scoped to EMPTY placements; a DECLARED placement activates real gate behavior incl. this raise (previously untested + unreachable in production).

**Scope — wrap-time gates only.** VALIDATOR_ESCALATION fires via the §14.15 mid-step re-entry path on validator outcome (`next_action == ESCALATE_HITL`), NOT a step-read placement, and its gate dispatch is itself a separate future arc → OUT of scope (documented, not silently absorbed).

**Gates:** pyright 0/0/0 (changed files); ruff (format + check) clean; harness-cp 1063 passed + 1 xfailed; harness-runtime 1933 passed / 10 skipped (non-e2e); CXA-P1 34; harness-cxa 28 / harness-od 950 / harness-core 26; the 6 new tests green.

---

## §5 Files

- `design-substrate/Spec_Harness_Runtime_v1.md` — v1.60 → v1.61 (§14.8.2 step-1 read-surface reconciliation).
- `design-substrate/Spec_Control_Plane_v1_41.md` — NEW v1.41 delta (additive §25.3 `StepExecutionContext.hitl_placements`).
- `harness-cp/src/harness_cp/workflow_driver_types.py` — `StepExecutionContext.hitl_placements` field + `HITLPlacement` import.
- `harness-cp/src/harness_cp/hitl_placement.py` — move `workflow_driver_types` import under `TYPE_CHECKING` (cycle break).
- `harness-cp/src/harness_cp/workflow_driver.py` — `hitl_placements=manifest_entry.hitl_placements` at all 5 per-step context constructions.
- `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` — step-1 reads `step_context.hitl_placements` (step fallback for proxies).
- `harness-cp/tests/test_workflow_driver.py` + `harness-runtime/tests/test_lifecycle_hitl_gate_composer.py` — by-execution tests.
- `.harness/clearance/Spec_Harness_Runtime-v1_61-cleared-2026-06-18.md` + `.harness/clearance/Spec_Control_Plane-v1_41-cleared-2026-06-18.md`.
- `.harness/beyond-mvp-capability-boundary-ledger.md` — BUILT note + `B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD` follow-on registration.
