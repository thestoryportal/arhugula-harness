---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.70
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — marks the registered §14.22.7 follow-on B-EFFECT-FENCE-PER-TOOL BUILT: the §14.22 C-RT-31 effect fence now exempts a declared-idempotent tool from the per-(run, step, tool) reserve [gate gains `AND NOT contract.idempotent`], so only declared-non-idempotent tools are fenced. Conservative-impl refinement to the at-most-once-for-non-idempotent intent, NOT a committed-invariant relaxation; the §14.22 C-RT-31 carrier is PRESERVED VERBATIM. Co-amends AS spec C-AS-03 §3.1 v1.11 → v1.12.)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-EFFECT-FENCE-PER-TOOL spine BUILT note)
  - design-substrate/Spec_Action_Surface_v1.md (the AS-side ToolContract.idempotent field, co-amended v1.11 → v1.12)
  - design-substrate/Spec_Harness_Runtime_v1.md (v1.60 §14.22 — the C-RT-31 fence + the §14.22.7 registration of B-EFFECT-FENCE-PER-TOOL; v1.67 §14.22.7 B-EFFECT-FENCE-DURABLE-AUTO, the named-follow-on-is-BUILD precedent; PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — BUILD-vs-gate discriminator: fence-all-when-active is the conservative IMPL of the §14.22 line-142 at-most-once-for-NON-idempotent intent (NOT a committed invariant; §14.22.7 NAMES this follow-on, the DURABLE-AUTO precedent); the tool-intrinsic-vs-invocation-dependent strict-semantic catch (a per-tool flag is sound only as a strict all-invocations property; default fence-by-default)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate)
  - out-of-family Codex review at the impl-diff PR (decorrelated; <pending>)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.70`

v1.70 marks the registered §14.22.7 follow-on **`B-EFFECT-FENCE-PER-TOOL` BUILT**. The §14.22 C-RT-31 `RuntimeEffectFence` now EXEMPTS a declared-idempotent tool from the per-(run, step, tool) at-most-once reserve: the dispatch fence gate gains one conjunct — `(effect_fencing_explicit OR run_engine_class ∈ durable-set) AND NOT contract.idempotent`. An idempotent tool fires + is **safely retryable** (the v1.60 interim fail-closed an idempotent tool's transient retry, which is over-conservative — re-running an idempotent tool is safe). Default `idempotent=False` → fenced (byte-identical to v1.69).

**BUILD-not-gate.** Fence-all-when-active is the conservative IMPL of the §14.22 stated intent ("at-most-once EXECUTION of a non-idempotent tool-step effect", line 142) — NOT a committed invariant. §14.22.7 explicitly NAMED `B-EFFECT-FENCE-PER-TOOL` as a follow-on ("per-tool idempotency classification to fence only declared-non-idempotent tools"), exactly as it named `B-EFFECT-FENCE-DURABLE-AUTO` (v1.67, BUILD-not-gate). The §14.22 C-RT-31 carrier (fence schema, `try_reserve` at-most-once, the §22.1 fail-closed `EffectFenceReservedUncommittedError`) is PRESERVED VERBATIM; the dispatch signature is UNCHANGED (the gate reads the already-in-scope per-tool `contract`).

**The strict tool-intrinsic semantic is the safety anchor (advisor catch).** Idempotency for a write tool is `(tool, args)`-dependent — which is why the fence keys per-invocation. A per-tool `idempotent` flag is sound ONLY as a strict all-invocations property (AS C-AS-03 §3.1 v1.12); the default `false` is the conservative fence-by-default (undeclared tools stay fenced); a mis-declaration is the contract author's responsibility. The exemption never weakens the at-most-once guarantee for a genuinely-non-idempotent effect.

**No new contract / fail-class / §5.2-hash change.** The gate refinement + the per-server `MCPClientConfig.default_idempotent` are runtime-/config-internal; `ToolContract.idempotent` is an additive AS field with a safe default. CP / IS / OD / ADR specs UNCHANGED; AS spec C-AS-03 §3.1 co-amends v1.11 → v1.12.

Reviewed during clearance (verified by execution): an idempotent tool under a durable run is NOT fenced (re-dispatch fires twice, no fence error) (`test_effect_fence_exempts_idempotent_tool_under_durable_run`); the exemption holds under explicit opt-in too (`..._under_explicit_optin`); the default (idempotent=False) durable + explicit-opt-in negative controls still fence (unchanged); the PRODUCTION per-server `default_idempotent` → host-factory converter stamps `ToolContract.idempotent=True` (`test_converter_stamps_per_server_idempotent_default` + a defaults-False negative); and — the advisor's pre-push `[[full-chain-witness-not-half-proofs]]` catch — a FULL-CHAIN witness drives the REAL `_build_default_policy_converter` → host registry → fence exempts with NO proxy converter (`test_effect_fence_exempts_idempotent_via_production_converter_full_chain`), closing the discovered-tool seam (the over-applying direction = fence silently disabled = unsafe, so witnessed end-to-end). harness-runtime non-e2e passed / 13 skipped; harness-as 318 passed; pyright 0/0/0.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-as + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh). Co-cleared with AS spec v1.12.
