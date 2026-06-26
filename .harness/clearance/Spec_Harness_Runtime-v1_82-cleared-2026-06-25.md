---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.82
cleared_at: 2026-06-25T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Control_Plane_v1_65.md §3 (registered B-FANOUT-CRASH-RESUME-MAYBE-RAN-UNFENCED-EXTERNAL — "extend the C-RT-31 fence to the managed-agents sink")
  - design-substrate/Spec_Harness_Runtime_v1.md §14.22 C-RT-31 (the effect fence — try_reserve / capture_output / read_output / clear_claim / try_consume_refire + the v1.60–v1.73 tool-dispatcher fence integration this delta mirrors for managed-agents) + §14.20 C-RT-28 (the managed-agents dispatcher carrier)
  - harness-runtime/src/harness_runtime/lifecycle/managed_agents_dispatch.py (the effect_fence + effect_fencing_explicit fields + the leading-domain-tag _compose_managed_agents_idempotency_key + the dispatch fence gate + capture-on-success)
  - harness-runtime/src/harness_runtime/bootstrap/factories/managed_agents_dispatcher_factory.py (threads a RuntimeEffectFence over the shared .harness/effect-fence dir + config.effect_fencing)
  - design-substrate/Spec_Control_Plane_v1_67.md (the paired CONSUMER delta — the CP fence-recoverable classifier extension)
  - .harness/clearance/Spec_Control_Plane-v1_67-cleared-2026-06-25.md (the paired CP marker — full reviewer chain)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor (full-transcript) — the LEAF-vs-recursive distinction that makes the arc sound (managed-agents never reconstructs harness-side → result-fidelity by construction; the #746 recursive-RESULT-fidelity [P1] does not transfer); the disposition-matrix risk surface (non-success / poll-exhausted leaving the fence ambiguous; the SKIP_AS_FIRED empty-fold cell); the payload-independent-key constraint.
  - out-of-family Codex (gpt-5.5, 3-round) — R1 [P1] a test-helper pyright redeclaration (FIXED); R2 [P2] the fence-key collision against a TOOL_STEP whose tool_id=="managed_agents" (FIXED by leading the digest with the domain tag + a disjointness regression guard); R3 clean. Full detail in the paired CP v1.67 marker.
  - by-execution witnesses: 14 real-fence dispatcher witnesses through a counting vendor port (test_managed_agents_dispatch_effect_fence.py) — the full disposition matrix + at-most-once across crash-resume + durability across a fresh fence instance + the tool-key disjointness + the _DURABLE_AUTO_FENCE_ENGINE_CLASSES drift guard; the existing 15 managed-agents dispatch tests + the full harness-runtime regression (238 passed / 3 e2e-skipped); pyright 0/0/0; ruff clean.
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.82`

v1.82 is a **change-note-level bundled-absorption** delta (co-published with `harness-runtime` + `harness-cp` impl + tests + the paired CP delta v1.67) — the build of the registered R-FS-1 arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-UNFENCED-EXTERNAL`, the PRIMARY (runtime) half.

- **The §14.22 C-RT-31 effect fence is EXTENDED to the §14.20 C-RT-28 MANAGED_AGENTS vendor-session sink.** `ManagedAgentsStepDispatcher` gains additive `effect_fence` + `effect_fencing_explicit` fields (default None/False → byte-identical to pre-arc); the stage-5 factory threads a `RuntimeEffectFence` over the same `.harness/effect-fence` dir as the tool dispatcher. The dispatch reserves before `create_session`, captures the outcome after a validated success ONLY, and on a lost reserve applies the key-bound directive (RE_FIRE / SKIP_AS_FIRED → empty-but-keyed outcome / ABORT) else the captured-output split (suppress / ambiguous → §26.2 PAUSE) — the v1.60–v1.73 tool-dispatcher fence gate VERBATIM.
- **The fence key is payload-independent + collision-free by construction.** `H("managed_agents" : parent_idempotency_key : step_id)` — the domain tag LEADS the digest (a trailing tag would collide with a tool whose `tool_id == "managed_agents"`; out-of-family Codex [P2]). NO agent_id → a resumed agent-swap is SUPPRESSED (parity-or-stricter vs the tool-swap).

## Caveats for Phase 7 consumers

- Change-note-level + ADDITIVE. **No new contract** (additive fields on C-RT-28), **no new fail-class** (reuses `EffectFenceAmbiguousUncommittedError` / `EffectFenceAbortedError` + the §26.2 EFFECT_FENCE_AMBIGUOUS pause), **no §5.2-hash change** (the fence claim/output is a sidecar, not in the §6 chain), **no `StepDispatcher` Protocol widening**, **no new CXA edge**. The §14.20.1–.7 + §14.22.1–.9 + the v1.59–v1.81 narrative PRESERVED VERBATIM. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.
- **MANAGED_AGENTS is a LEAF** — result-fidelity holds by construction (a suppress folds the captured outcome verbatim), the contrast with the reverted #746 SUBAGENT recursive-child slice. A non-success terminal / poll-exhausted dispatch captures NO output → a resume is genuinely ambiguous → §26.2 PAUSE, never a false suppress of a failed outcome.
- **Paired CP delta v1.67 is the CONSUMER half** (the fence-recoverable classifier extension + the same-kind guard); the two land together.
