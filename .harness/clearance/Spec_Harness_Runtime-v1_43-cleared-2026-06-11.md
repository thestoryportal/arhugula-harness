---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.43
cleared_at: 2026-06-11T16:30:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (bundled-absorption — design-substrate + harness-runtime/src + tests)
back_reference:
  - .harness/class_1_fork_sandbox_tier_driver_selection_silent_in_process.md (the Class-1 fork this delta resolves — FR-1/FR-2, operator-ratified Reading A+ 2026-06-11)
  - .harness/capability-completion-inventory-v1.md §2 row 1 + §4 step 1 (R-CC-1 arc #1 — sandbox tier→driver production selection)
  - Project_Roadmap_v1.md §5.17 R-CC-1 (capability-completion program — the active frontier)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - operator AskUserQuestion 2026-06-11 (DP-1 ratified as Reading A+ — deployment-surface-aware default; FR-1/FR-2 confirmed forced by the F4/D2 guarantee posture)
  - advisor() decision-fork passes (X-AL-3 classification = net-new selection contract → Class-1 fork; probe-first foreclosed the C10⊥C11 council via the guarantee-posture probe; floor-vs-exact reconciliation against ADR-D2 §1.1 → cells are floors → A+ composes safely, no ADR-D2 back-flow)
  - harness-adversarial-reviewer Phase-7 pre-merge review (APPROVE — no Class-1 halt-blocker; 1 Class-2 + 3 Class-1 doc-precision findings, all applied this arc: C-AS-09 claim scoped to §1.1 + §1.3 STDIO floor disclosed; §14.9.9 inv-1 scoped to the factory boundary; fork Reading-A→A+ supersession; span-label deferral noted)
  - out-of-family Codex review (no discrete correctness/security/maintainability bugs; independent pyright 0-errors)
  - empirical code-grounding (4 drivers exist + e2e-proven with no production caller; DeploymentSurface first-class at RuntimeConfig; both factories receive config.deployment_surface; verify-by-execution 1576 harness-runtime tests pass)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4; X-AL-3 guard satisfied by the paired fork doc)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.43`

v1.43 authors **NEW §14.9.9 — the tool-execution-driver selection contract**, closing the R-CC-1 capability-completion arc #1 security gap: the runtime resolved + floor-enforced + span-emitted a sandbox tier (e.g. `TIER_2_CONTAINER`) while the stage-5 factory bound **no** `tool_execution_driver`, so a tool demanding container isolation silently executed in-process (TIER_1) yet passed the tier-floor check and reported `sandbox.tier=container`. §14.9.9 authors the factory's driver-selection obligation (FR-1 — select a driver delivering ≥ the resolved tier, per-server-uniform) + a fail-loud two-branch delivery contract (FR-2 — `detect-then-refuse`; selection-time and dispatch-time both RAISE, never silent in-process) + the new `RT-FAIL-SANDBOX-DRIVER-UNAVAILABLE` fail class (the 9th, extending the §14.9.5 taxonomy whose "8" count is preserved verbatim).

The fix was **forced by the F4/D2 blast-radius guarantee posture** (probe-verified at fork §2: ADR-F4 §Decision graduated-isolation; ADR-D2 §1.1/§1.3 "sandbox is the only boundary; container-tier minimum prevents kernel-CVE-class escape") — a resolved tier that is floor-passed and span-reported but not delivered is a flat violation. The deployment-surface-aware default (operator-ratified **Reading A+**) is realized as `MCPClientConfig` impl-discretion (`local-development → honest TIER_1_PROCESS` out-of-box; `self-hosted-server`/`managed-cloud → fail-safe-high TIER_2_CONTAINER` which FR-2(i) refuses to run without a driver), floor-verified safe against the ADR-D2 §1.1 raise-only cell-floors. The three `MCPClientConfig` `default_*` tier fields are reconciled through one surface-aware helper (`resolve_effective_sandbox_defaults`) shared by the stage-3a converter + stage-5 resolver so the §14.9.4 tier-floor never spuriously violates on a bare config.

**Carve-outs for Phase 7 consumers.** §14.9.9 binds the EXISTING §14.9.8 resolved tier to a delivering driver; it does NOT alter tier derivation. The §14.9.8 flat per-server-uniform Reading-B resolver still **bypasses the full `sandbox_tier_floor` per-cell composition** — including the ADR-D2 §1.3 STDIO `tier-3-microvm` transport-floor (a bare STDIO local-dev server resolves to TIER_1, below that floor). That non-enforcement is the pre-existing §14.9.8 composition gap, carried forward and explicitly scoped as a distinct future arc at the §14.9.9 Scope boundary; v1.43 neither closes nor widens it. The "consistent with C-AS-09" claim is scoped to the §1.1 cell-floor only (change-note + fork §7, F2-01 refinement). Invariant 1 ("delivered-tier ≥ resolved-tier; > TIER_1 never in-process") is enforced at the **factory boundary** (mirroring §14.9.6 inv 1); an operator hand-constructing a `RuntimeToolDispatcher` directly with the tier-agnostic in-process driver is the hand-built case per §14.9.8 and the operator's responsibility (F1-01 refinement).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
