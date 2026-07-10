---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.98
cleared_at: 2026-07-10T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/clearance/Spec_Harness_Runtime-v1_97-cleared-2026-07-10.md (registered the B-18-CACHE-TTL-OBSERVABILITY deferral this marker closes)
  - .harness/u1-slice3b-epoch-partition-design.md (§B-18 follow-on register — the observability follow-on decomposition)
  - design-substrate/Spec_Action_Surface_v1.md (§14.2 C-AS-14 anthropic.* attribute contract — already position-agnostic; UNCHANGED)
  - design-substrate/ADR-D3.md (§ anthropic.* observability namespace; cache_breakpoint_id "which of ≤4 breakpoints hit")
  - .harness/post-phase-8-forward-register.md (B-18 / U-1)
  - PR (U-1 B-18-CACHE-TTL-OBSERVABILITY, branch u1-b18-cache-ttl-observability)
merge_commit: (squash-merge of the B-18-CACHE-TTL-OBSERVABILITY PR)
reviewer_chain:
  - out-of-family just codex-review (gpt-5.5, subscription) — decorrelated diff review of the generalized wire-kwargs scan + the three-path kwargs threading (advisor was unavailable this session; codex is the standing decorrelated reviewer per CLAUDE.md §13.1)
  - main-agent artifact review (the tools→system→messages prefix-order scan; the three Anthropic dispatch paths thread the translated kwargs; msg-{index} preservation for the pre-B-18 message path; negative control — no marker → attrs absent)
---

# Clearance — `Spec Harness Runtime v1.98`

v1.98 closes the decorrelation-validated deferral **`B-18-CACHE-TTL-OBSERVABILITY`** registered at v1.97 (both the advisor and out-of-family Codex converged on it during the slice-3b ttl review). **Pure observability — no wire-behavior change** (byte-identical dispatch; the selected ttl already reached the wire `cache_control` marker at v1.94 slice 1 / v1.97 slice 3b).

**The gap.** `_extract_anthropic_cache_request_attrs` scanned only `payload.messages`, but the U-1 (B-18) `cache_control` breakpoint is placed on the **tools** block (slice 1 / 3a) or the **system** block (slice 2) at translate-time on the wire kwargs — never on the frozen `ProviderAgnosticPayload`. So `anthropic.cache_breakpoint_id` + `anthropic.cache_ttl_seconds` went **unrecorded** for the common slice-1/2/3a/3b case; only an atypical message-content-block `cache_control` (a caller-constructed shape) was ever observed. The *effect* was observable via `anthropic.cache_read/creation_input_tokens`, but the request-side attrs — including the slice-3b operator signal that a selected `1h` ttl took effect — were not.

**The fix (single source of truth).** The extractor now scans the **TRANSLATED wire kwargs** (`tools → system → messages`, Anthropic's prefix-cache order) — the authoritative record of what was actually sent — rather than the frozen payload. Threading a separate ttl value from the translate seam would create a *second* authority that can drift from the marker actually on the wire; scanning the wire kwargs reads the one truth. `_anthropic_response_bundle` gains a `request_kwargs` parameter, threaded by all three Anthropic dispatch paths (plain `_dispatch_anthropic` / `_dispatch_anthropic_with_memory` / `_dispatch_anthropic_with_hitl_tool_loop`). `cache_breakpoint_id` now reports the breakpoint **position** — `"tools"` / `"system"` / `"msg-{index}"` (low cardinality ≤4 per C-AS-14 §14.2) — with the message path preserving the pre-B-18 `"msg-{index}"` value verbatim.

**Contract scope.** The AS spec C-AS-14 §14.2 row is already position-agnostic ("which of ≤4 breakpoints hit", low cardinality) — this impl is now *more* conformant to it, not a contract change. Only the Runtime spec's implementation-mechanism description (§14.2 canonical attribute-reference table) narrowed the extraction to "message content blocks (`msg-{index}`)"; v1.98 generalizes that prose to the translated-wire-kwargs scan. IS / CP / OD / AS / ADR / CXA specs UNCHANGED. The v1.2→v1.3 historical change-note (which described the original messages-only mechanism) is left verbatim as frozen lineage.

**Verification.** pyright 0/0/0 on the touched src + test files; ruff+format clean; 4 new B-18 observability witnesses through the REAL dispatch chain (tools-block breakpoint → span `cache_breakpoint_id == "tools"` + `cache_ttl_seconds == 300`; system-block breakpoint → `"system"` + 300; selected `cache_ttl="1h"` → `"tools"` + 3600 — the slice-3b operator signal; negative control — no bound superset + plain `payload.tools` → request-side cache attrs ABSENT from the span). The pre-B-18 message-content-block test preserved verbatim (`msg-0` + 3600). Full `harness-runtime/tests/test_lifecycle_llm_dispatch.py` + `test_cacheable_epoch_ttl_slice3b.py` = 128 passed; **full `harness-runtime/tests/` non-e2e = 2347 passed** (= 2343 slice-3b baseline + 4 B-18 observability tests), 10 skipped, 0 failures.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Remaining registered B-18 follow-ons (NOT this arc): version_sha cohort identity + slice 3c (ADR-D4 §1.8 PARALLELIZATION concurrent-cache pre-warm — high-blast-radius fan-out, dedicated session) and `B-18-LANEB-PROMPT-SEMVER` (operator-declared semantic-version field on `PromptVersion`; IS-spec amendment, NOT required since version_sha is the cache key).
- See `.harness/clearance/README.md` for marker discipline.
