---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.99
cleared_at: 2026-07-11T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/b18-keepalive-design-decision-record.md (DDR for B-18-KEEPALIVE; DESIGN LOCKED before this session)
  - .harness/clearance/Spec_Harness_Runtime-v1_98-cleared-2026-07-10.md (immediate predecessor)
  - design-substrate/ADR-D3.md (§1.5:189-190 — boot prewarm + keep-alive cadence authority)
  - .harness/post-phase-8-forward-register.md (B-18 / U-1 registration)
  - PR (B-18-KEEPALIVE, R-FS-2 Wave 1)
merge_commit: (squash-merge of the B-18-KEEPALIVE PR)
reviewer_chain:
  - main-agent artifact review (prewarm() eligibility gate; bare-handle bypass rationale; best-effort-must-not-fail-bootstrap; _keepalive_loop cancel+await before _shutdown; 1h-TTL exclusion; self-disable after 3 failures; R2 re-defer)
  - grok post-build diff review (operator-designated out-of-family reviewer; see DDR §11)
---

# Clearance — `Spec Harness Runtime v1.99`

v1.99 materializes **B-18-KEEPALIVE** (R-FS-2 Wave 1) — the **ADR-D3 §1.5:189-190 boot pre-warm + daemon keep-alive** contract. Fully opt-in (both flags default-off); no wire-behavior change when flags are False (byte-identical to v1.98 at the dispatch layer).

## Surfaces landed

**RuntimeConfig fields (opt-in, env-keyed via BOTH loaders):**
- `prompt_cache_boot_prewarm: bool = False` — fire best-effort prewarm at stage-5 LOOP_INIT for BOTH `harness run` and daemon.
- `prompt_cache_keepalive: bool = False` — spawn 5m-TTL daemon keep-alive loop (240s interval).
- `prompt_cache_prewarm_model: str | None = None` — file/CLI-only fallback model string when routing_manifest yields no Anthropic binding; does NOT gate correctness.

**C-RT-15 `RuntimeLLMDispatcher` additions:**
- `prewarm_model: str | None = None` field.
- `PrewarmOutcome(StrEnum): WARMED / SKIPPED_NOT_ELIGIBLE / SKIPPED_NO_ANTHROPIC / FAILED`.
- `async prewarm() → PrewarmOutcome` — Anthropic-only; gates on `frozen_tool_superset` non-vacuity (≥4096-tok combined prefix); model resolution: routing_manifest first → prewarm_model fallback → SKIPPED_NOT_ELIGIBLE; sends `max_tokens=1` via `_dispatch_anthropic` directly (bypasses HITL/retry wrapper); attributes cost to `workflow_id="__prewarm__"`; swallows all exceptions → FAILED.

**`HarnessContext` + `_MutableHarnessContext`:** `bare_llm_dispatcher: Any = None` stashed at stage 5 for daemon keep-alive access without routing through the 3-layer wrapper.

**Stage-5 LOOP_INIT:** stashes bare handle; if `config.prompt_cache_boot_prewarm`, calls `await bare_dispatcher.prewarm()` in try/except — MUST NOT propagate as `BootstrapFailure`.

**`cli/app.py` daemon extension:** `_keepalive_loop(ctx, bare, *, sleep_fn, interval=240.0)` spawned when `config.prompt_cache_keepalive and bare.cache_ttl == "5m"` (1h-TTL excluded). Self-disables after 3 consecutive FAILED outcomes. Cancelled+awaited in `finally` BEFORE `await _shutdown(ctx)`.

**N7 single-epoch reality:** one daemon ctx → one `active_system_prompt` + `frozen_tool_superset` → one canonical prewarm epoch per daemon lifetime.

**R2 disposition (RE-DEFER):** C11 "skip keep-alive under cost-ceiling pressure" carve-out remains deferred — no committed cost-ceiling signal in substrate; building one would be X-AL-3. The opt-in-default-off + 5m-only defaults already bound the C11 risk.

## Verification

- Hermetic test suite (NO paid calls): 7.1–7.8 all passing.
- `ruff check` + `ruff format` clean on all modified files.
- pyright strict 0/0/0 on touched packages (verified via `just check`).
- IS / CP / OD / AS / ADR / CXA specs UNCHANGED.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Remaining registered B-18 follow-ons (NOT this arc): version_sha cohort identity + slice 3c (ADR-D4 §1.8 PARALLELIZATION concurrent-cache pre-warm), `B-18-LANEB-PROMPT-SEMVER`.
- See `.harness/clearance/README.md` for marker discipline.
