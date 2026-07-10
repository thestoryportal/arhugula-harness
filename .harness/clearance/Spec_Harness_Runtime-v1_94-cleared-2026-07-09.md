---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.94
cleared_at: 2026-07-10T02:20:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/u1-cache-breakpoint-slice1-design.md (council-converged C4/C2/C6 design)
  - .harness/u1-slice1-c10-blast-radius-verdict.md (C10 blast-radius vet — Option A acceptable)
  - .harness/post-phase-8-forward-register.md (B-18 / U-1)
  - PR (U-1 slice-1 cache_control breakpoint, branch feat/u1-frozen-tool-superset-cache-breakpoint)
merge_commit: (squash-merge of the U-1 slice-1 PR)
reviewer_chain:
  - design-phase council C4 (tools) + C2 (context/caching) + C6 (epoch) — genuine SKILL.md adoption, converged design
  - C10 (action-safety / blast-radius) vet — Option A (full superset visible per step, execution gating intact) acceptable at single-privilege-tier top-level dispatch; no committed least-privilege-visibility contract
  - advisor() full-transcript (design scoping + the probe-first slice discriminator)
  - main-agent impl review — corrected the marker-position defect (marker must skip server-side tool blocks) + added the memory-skip witness
  - spec-writer-style apply pass (change-note + version bump)
---

# Clearance — `Spec Harness Runtime v1.94`

v1.94 materializes **U-1 slice 1** (forward register B-18) — the executable, tools-block half of the **ADR-D3 §1.5 prompt-cache breakpoint placement contract**. The `RuntimeLLMDispatcher` (C-RT-15) gains an optional `frozen_tool_superset` field, bound at bootstrap stage 5 to the deterministic union of every MCP-host `tool_registry` `ToolContract` (Anthropic-projected, name-sorted, `input_schema` recursively key-canonicalized, dedup-by-name, memory-tool def appended when memory-capable). At translate-time only (`ProviderAgnosticPayload` stays frozen — ADR-F1), the Anthropic branch sends the frozen superset as `tools` with a `cache_control` breakpoint on the last **client** tool block, gated on extended-thinking-OFF + the ≥4096-tok non-vacuity floor. `None` → byte-identical legacy path; OpenAI/Ollama untouched.

**Blast-radius (C10-vetted).** Sending the full superset per step changes tool VISIBILITY (the model sees all registered tools, not the step's declared subset) but NOT execution — the `RuntimeToolDispatcher` registry/trust/sandbox/effect-fence gate is unchanged (`payload.tools` is visibility-only; `RuntimeToolDispatcher` dispatches by registry-resolved `tool_id` with no membership check). C10 found no committed least-privilege-VISIBILITY contract; acceptable at single-privilege-tier top-level dispatch (slice 1 is single-threaded-linear). Conditions carried forward: the superset is computed from the dispatch's OWN top-level registry (never a captured parent set); sub-agent/downgraded dispatchers stay `None` → fall back to `payload.tools`; slice-3 `frozen_tool_superset_per_privilege_tier` remains REQUIRED before multi-tenant binding.

**Impl-review correction (recorded).** The first-pass impl placed the breakpoint on the LAST superset block, which is the appended-last server-side memory tool (`type`+`name`, no `input_schema`) in memory-capable runs — an unverified silent-cache-miss risk. Corrected in review: the marker lands on the last block bearing an `input_schema` (a client tool), never a server-side block; witnessed by `test_memory_server_tool_block_never_receives_the_marker`.

**Verification.** pyright 0/0/0 on changed src; 14 offline tests (incl. byte-stability, deterministic-order, None-no-regression, below-floor-no-marker, extended-thinking-skip, memory-skip) + 2 full-chain witnesses (marker reaches the wire through the real dispatch chain; None = legacy verbatim); ruff + format clean. The live cache-hit e2e (`cache_creation_input_tokens > 0` then `cache_read_input_tokens > 0`) is written + `@pytest.mark.e2e`-gated but NOT fired — a paid Anthropic call, surfaced as the one operator gate.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Slice 2 (OQ-1 system-array → full `[tools + system]` §1.5 position) + slice 3 (sub-agent breakpoint + epoch primitive + pre-warm) remain registered follow-ons at B-18.
- See `.harness/clearance/README.md` for marker discipline.
