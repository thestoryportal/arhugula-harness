---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.97
cleared_at: 2026-07-10T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/u1-slice3b-epoch-partition-design.md (fork resolution + council probe-resolution + epoch primitive design + lane split)
  - .harness/u1-slice3-findings-and-f1-c10-gap.md (§Correction — the two fresh-session questions this slice resolves)
  - design-substrate/ADR-D3.md (§1.5 line 188 ttl contract; §1.8.1 skill semantic-version precedent)
  - .harness/post-phase-8-forward-register.md (B-18 / U-1)
  - PR (U-1 slice 3b, branch u1-slice3b-cacheable-epoch-ttl)
merge_commit: (squash-merge of the U-1 slice-3b PR)
reviewer_chain:
  - decorrelated advisor (transcript-aware) — validated the BUILD fork-resolution + the ttl-council probe-resolution; caught the missing config-coercion→selection witness (added as the load-bearing operator-path test)
  - out-of-family just codex-review (gpt-5.5, subscription) — independently confirmed the list→frozenset[WorkloadClass] coercion by execution; flagged the cache-ttl observability gap [P2] (registered as B-18-CACHE-TTL-OBSERVABILITY, deferred)
  - main-agent artifact review (dispatch translate seam + stage-5 binding + the ttl orthogonality to slice-1/2/3a placement/content)
---

# Clearance — `Spec Harness Runtime v1.97`

v1.97 materializes the **ttl-selection half of the ADR-D3 §1.5 cacheable-epoch contract** (line 188) as **U-1 slice 3b** (forward register B-18). The `RuntimeLLMDispatcher` (C-RT-15) gains a `cache_ttl: Literal["5m","1h"] = "5m"` field, bootstrap-stage-5-bound via `cacheable_epoch.select_cache_ttl(workload_class, config.prompt_cache_long_ttl_workloads)`. The run's `workload_class` selects `"1h"` iff it is a member of the new operator opt-in `RuntimeConfig.prompt_cache_long_ttl_workloads: frozenset[WorkloadClass]`, else `"5m"`. At translate-time (`_payload_to_anthropic_kwargs`; `ProviderAgnosticPayload` FROZEN), the selected ttl replaces the previously-hardcoded `{"ttl": "5m"}` on the `cache_control` breakpoint — tools block (slice 1) OR system block (slice 2). The ttl is orthogonal to which block is marked (slice 1/2) and to the superset content (slice 3a). Default empty opt-in → every class `"5m"` → **byte-identical to pre-slice-3b**. OpenAI/Ollama untouched.

**Fork resolution + council probe-resolution** (`.harness/u1-slice3b-epoch-partition-design.md`). The slice-3 findings' fork ("is `major-version-of-system-prompt` derivable → BUILD, or absent → X-AL-3 back-flow?") is **probe-resolved to BUILD**: Anthropic's cache is byte-exact, so `active_prompt_version.version_sha` IS the cache-correct system-prompt key (a coarser semantic-major key would be a cache-hit bug) — the back-flow branch is foreclosed. The prescribed C2⊥C11 ttl council is **probe-resolved**: ADR-D3 §1.5 lines 188-190 already commit the ttl values (5m/1h) + 1hr cost-ceiling trigger + keep-alive cadence, so convening would re-litigate a §10.2-cleared surface (`[[probe-resolves-fork-prescribed-council]]`). Persona §6 records the cost ceiling as per-class + operator-asserted (no cell matrix), so "cost-ceiling cells" = the operator opt-in field; the 1hr tier gates a cost optimization (5m is always correct) → file/CLI-only collection field, NOT env-keyed.

**Two lanes not collapsed** (advisor correction). Lane A (version_sha-keyed epoch → this pure Phase-7 build) vs Lane B (a semantic-major field on `PromptVersion`, the skill `frontmatter.version` analogue per ADR-D3 §1.8.1 — an IS-spec amendment, NOT required since version_sha is the cache key; registered `B-18-LANEB-PROMPT-SEMVER`). The version_sha cohort identity + the ADR-D4 §1.8 fan-out pre-warm (3c — its only consumer, high-blast-radius) ship together in a dedicated session.

**Deferred, decorrelation-validated follow-on `B-18-CACHE-TTL-OBSERVABILITY`.** Both reviewers (advisor + Codex [P2]) converged: `_extract_anthropic_cache_request_attrs` scans only `payload.messages`, so the tools/system-block breakpoint's `anthropic.cache_ttl_seconds` is unrecorded — a **pre-existing** gap (slices 1/2/3a's 5m marker is equally unobserved; the marker lives on the translated kwargs, not the frozen payload). The wire behavior IS correct (Anthropic caches for the selected ttl) and the EFFECT is observable via `anthropic.cache_read/creation_input_tokens`; only the request-side `cache_ttl_seconds` attr is deferred. Closing it uniformly across slices 1/2/3a/3b is a shared response-bundle-path refactor → its own arc, not folded here (surgical discipline).

**Verification.** pyright 0/0/0 on all touched files + full harness-runtime src+tests; ruff+format clean; 14 slice-3b tests (select_cache_ttl pure selection incl. None-workload + empty/member/non-member; **config coercion → `frozenset[WorkloadClass]` enum members → `select_cache_ttl` 1h/5m, the load-bearing operator-path witness**; config rejects an unknown class fail-loud; translate-seam ttl emission on tools + system blocks for 1h + default 5m; ttl-orthogonal-to-placement; **full-chain dispatcher witness: `cache_ttl="1h"` reaches the wire marker; default is 5m on the wire**); **full `harness-runtime/tests/` non-e2e = 2340 passed** (= 2329 slice-3a baseline + 11; then +3 config witnesses added post-review); existing slice-1/2/3a cache tests 34 passed / 2 skipped (byte-identity preserved).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The version_sha cohort identity + slice 3c (ADR-D4 §1.8 PARALLELIZATION pre-warm), `B-18-LANEB-PROMPT-SEMVER`, and `B-18-CACHE-TTL-OBSERVABILITY` remain registered follow-ons at B-18.
- See `.harness/clearance/README.md` for marker discipline.
