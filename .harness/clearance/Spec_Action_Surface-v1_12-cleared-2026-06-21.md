---
artifact: design-substrate/Spec_Action_Surface_v1.md
version: v1.12
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — one additive optional `ToolContract.idempotent: bool = False` field at C-AS-03 §3.1, the AS-side leg of the runtime `B-EFFECT-FENCE-PER-TOOL` arc. Read ONLY by the runtime effect fence (§14.22/§14.22.7) to exempt declared-idempotent tools from the at-most-once reserve. Additive with a safe fence-by-default; the v1.11 `forces_*`/`is_deterministic_inhouse` additive-discriminator precedent. NOT a sandbox discriminator — does NOT enter the §2.2/§2.3 sandbox_tier_floor composition.)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-EFFECT-FENCE-PER-TOOL spine BUILT note)
  - design-substrate/Spec_Harness_Runtime_v1.md (the runtime §14.22.7 follow-on this AS leg cascades from; co-amended v1.69 → v1.70)
  - design-substrate/Spec_Action_Surface_v1.md (v1.11 — the forces_*/is_deterministic_inhouse additive-discriminator precedent this mirrors; PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — BUILD-vs-gate discriminator: fence-all is the conservative IMPL of the at-most-once-for-non-idempotent intent (NOT a committed invariant); §14.22.7 NAMES per-tool as the follow-on; the tool-intrinsic-vs-invocation-dependent strict-semantic catch (a per-tool flag is sound only as an all-invocations property; default fence-by-default)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; additive field, no operator gate)
  - out-of-family Codex review at the impl-diff PR (decorrelated; <pending>)
supersedes:
superseded_by:
---

# Clearance — `Spec_Action_Surface v1.12`

v1.12 adds one optional `ToolContract.idempotent: bool = False` field at C-AS-03 §3.1 — the **AS-side leg** of the R-FS-1 standalone arc **`B-EFFECT-FENCE-PER-TOOL`** (the runtime §14.22.7 follow-on). The runtime effect fence (§14.22 C-RT-31) reads it to EXEMPT a declared-idempotent tool from the per-(run, step, tool) at-most-once reserve.

**Strict, tool-intrinsic, all-invocations semantic.** `idempotent=true` asserts every invocation re-executes with NO additional external effect, for ALL arguments (a pure read trivially qualifies; a PUT-style set-to-value qualifies; an append/send/counter-increment does NOT — those keep the default `false` and stay fenced). This strictness is load-bearing: idempotency for a write/mutate tool is `(tool, args)`-dependent (which is why the fence keys per-invocation), so a per-tool flag is sound ONLY for the tool-intrinsic all-invocations property. Default `false` = treat as non-idempotent → fenced (byte-identical to pre-v1.12).

**NO operator gate.** Additive optional field with a safe fence-by-default; sacrifices no AS invariant (the v1.11 `forces_*`/`is_deterministic_inhouse` additive-discriminator precedent — "additive with safe defaults; every existing contract resolves byte-identically"). `idempotent` does NOT enter the §2.2/§2.3 `sandbox_tier_floor` composition — it is a fence-only concern read by the runtime, distinct from the v1.11 sandbox-tier discriminators. The AS↔runtime registration seam threads it (`RawContractInput.idempotent` + the converter + the per-server `MCPClientConfig.default_idempotent`). No `minimum_tier`/`blast_radius_tier`/`required_secrets`/`forces_*` change; no C-AS-02 composition change; no AS-AL rule.

Reviewed during clearance (verified by execution): the converter threads `idempotent` RawContractInput → ToolContract (default False) (`test_tool_contract_idempotent_threads_through_converter`); the RawContractInput field-set assertion updated; harness-as 318 passed; pyright 0/0/0.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-as + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh). Co-cleared with runtime spec v1.70.
