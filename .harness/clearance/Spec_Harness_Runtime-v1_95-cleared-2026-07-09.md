---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.95
cleared_at: 2026-07-10T03:55:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/u1-cache-breakpoint-slice1-design.md (design lineage; slice 2 = registered follow-on)
  - .harness/u1-slice1-c10-blast-radius-verdict.md (C10 vet — carries to slice 2)
  - .harness/post-phase-8-forward-register.md (B-18 / U-1)
  - PR (U-1 slice 2, branch feat/u1-slice2-system-block-cache-breakpoint)
merge_commit: (squash-merge of the U-1 slice-2 PR)
reviewer_chain:
  - fresh-context impl subagent against the precise design
  - decorrelated advisor (transcript-aware) + out-of-family just codex-review (caught + fixed a paid-call e2e-gating [P2])
  - main-agent artifact review (core emission logic + OpenAI/Ollama-untouched + the OQ-1 un-defer)
  - spec-writer-style apply pass (change-note + version bump + OQ-1/OQ-2 un-defer)
---

# Clearance — `Spec Harness Runtime v1.95`

v1.95 materializes **U-1 slice 2** (forward register B-18) — extends the v1.94 tools-block cache breakpoint to the **full ADR-D3 §1.5 parent position `[system_prompt + frozen_tool_superset]`** by resolving the §14.5.2 **OQ-1** deferral (structured/multi-block `system` content) + **OQ-2** (prompt-caching interaction).

At translate-time (`ProviderAgnosticPayload` FROZEN — ADR-F1): when a system prompt is present alongside a bound `frozen_tool_superset`, extended-thinking is off, and the **combined** `[tools + system]` prefix clears the ≥4096-tok floor, the Anthropic `system` becomes a one-block content array with `cache_control` on it, and the tool superset is sent UNMARKED — exactly one breakpoint on the last system block, caching `[tools + system]` (Anthropic caches `tools → system` in order). Otherwise the v1.94 slice-1 behavior holds verbatim (marker on the last client tool block; plain-string system). The `frozen_tool_superset is not None` gate is load-bearing (advisor-confirmed): marking `system` over an unstable per-step `payload.tools` would write a never-read cache each step. OpenAI/Ollama untouched; `None`+`None` → byte-identical legacy.

**Verification.** pyright 0/0/0; ruff+format clean; 13 slice-2 offline tests (system-marked array + unmarked tools; exactly-one-breakpoint; floor-via-system-length; no-system keeps slice-1 tools marker; below-floor plain string; extended-thinking; byte-stability; None-legacy; no-mutation; OpenAI+Ollama keep `role:"system"` form) + 2 full-chain witnesses; **full `harness-runtime/tests/` non-e2e = 2320 passed, 0 failures**. The combined `[tools+system]` live cache-hit e2e is written + double-gated (`@pytest.mark.e2e` + `HARNESS_LIVE_ANTHROPIC_CACHE_E2E=1`, the codex-review-hardened opt-in) — a paid call, NOT fired.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Slice 3 (`sub_agent_breakpoint` + `frozen_tool_superset_per_privilege_tier` + cacheable-epoch primitive + ADR-D4 §1.8 pre-warm) + a system-only-breakpoint path (huge system, no tools) remain registered follow-ons at B-18.
- See `.harness/clearance/README.md` for marker discipline.
