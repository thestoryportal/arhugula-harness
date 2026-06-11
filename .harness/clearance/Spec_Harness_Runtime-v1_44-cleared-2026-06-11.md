---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.44
cleared_at: 2026-06-11T18:30:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (bundled-absorption — design-substrate + harness-runtime/src + harness-is/src + tests)
back_reference:
  - .harness/r-pm-1-prompts-management-design-v1.md §4.1 (R-PM-1 4-layer design — cascade PR #1 INJECTION layer, the load-bearing piece)
  - .harness/class_1_fork_prompts_management_surface_active_prompt_version.md DP-5 (the prompts-management fork, re-opened at PR #1 injection scope)
  - Project_Roadmap_v1.md §5.16 R-PM-1 + §5.17 R-CC-1 (capability-completion arc #2 — the active frontier)
  - design-substrate/Spec_Information_Substrate_v1.md v1.6 §5.2 (the IS-carrier side — inline content + derive-invariant; co-published this arc)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - advisor() pre-substantive decision-fork (approved the cleared design's impl approach; required TWO reachability proofs — dispatch-composition through real dispatch(...) + the stage-5 bootstrap seam, the exact seam #496 left inert — and symmetric coverage across all 5 dispatch helpers; minor notes on step-level (not bootstrap-abort) conflict error + the frozen-payload ADR-F1 affirmation, both applied)
  - out-of-family Codex review (pending this arc — the decorrelated diff reviewer)
  - harness-adversarial-reviewer Phase-7 pre-merge review (pending this arc)
  - empirical code-grounding (3 translate fns + 5 dispatch helpers threaded; ProviderAgnosticPayload stays frozen → cost-attribution + §14.2 anthropic.* attrs untouched; verify-by-execution: harness-runtime 1584 + harness-is 140 green incl. proof-a (4 dispatch paths) + proof-b (bootstrap stage-5 seam) + 2 conflict tests; pyright 0, ruff clean, overlay 31/31)
  - primary-source grounding (claude-api reference — Anthropic system= top-level kwarg vs OpenAI/Ollama role:"system" message; the provider-asymmetry linchpin for the translate-time seam)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4; X-AL-3 guard satisfied by the paired fork doc + this design artifact)
supersedes: design-substrate/Spec_Harness_Runtime_v1.md v1.43
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.44`

v1.44 authors **NEW §14.5.2 — translate-time per-provider system injection** within the C-RT-15 dispatch composer, closing the load-bearing R-PM-1 cascade PR #1 gap: v1.42 bound the prompts carrier onto `HarnessContext`, but **nothing reached the model** — no path routed an active prompt's content to any provider as a system prompt.

**What changed.** §14.5.2 authors:
- **FR-1** — the dispatcher carries a new `active_system_prompt: str | None` binding, resolved at bootstrap stage 5 from `ctx.prompt_manifest.active_prompt_version.content or None`. Empty/None → no injection (byte-identical to v1.43 — the local-first default).
- **FR-2** — the three `_payload_to_{anthropic,openai,ollama}_kwargs` translate fns gain a `system` parameter, injecting per-provider: Anthropic top-level `system=` kwarg; OpenAI/Ollama leading `{"role":"system"}` message. Threaded through **all 5** dispatch helpers (plain anthropic, memory-tool variant, HITL-tool-loop variant, openai, ollama).
- **FR-3** — conflict precedence is **fail-loud** (`detect-then-refuse`): an active prompt + a payload-carried competing system source RAISES `RT-FAIL-PROMPT-INJECTION-CONFLICT` (the new fail class, extending the §14.5 taxonomy; **step-level** — propagates to the driver except-boundary as a step-failure; does NOT abort bootstrap).

**Why this mechanism (ADR-F1-faithful).** A system prompt is **not uniformly representable** in the neutral 3-tuple (Anthropic = top-level `system=` kwarg; OpenAI/Ollama = `role:"system"` message entry — primary source: the `claude-api` reference), so injection happens at the per-provider translate seam and `ProviderAgnosticPayload` stays **frozen and unchanged**. This is "per-provider feature use at the call site" per ADR-F1 §Decision/§Consequences (a); lifting a provider-divergent `system` field into the neutral record is the LCD-union move §Rationale (b) forecloses. Keeping the payload frozen is *why* cost-attribution + the §14.2 `anthropic.*` request-attr extraction stay untouched → **ADR-F1-faithful → no new ADR** (fork + spec amendment, not a foundational ADR touch).

**Carve-outs for Phase 7 consumers.**
- **Known operational consequence** (framed honestly at §14.5.2): for OpenAI/Ollama a leading `role:"system"` message is the *idiomatic* per-step system prompt, so configuring an active prompt will **hard-error** any workflow that already carries its own system message. That is the intended v1 contract (surface the collision, do not silently pick). The escape valve is a configurable `merge`/`replace` policy (R-PM-1 design OQ-5), a bounded follow-on iff a real workload needs both sources.
- **Scope** — v1.44 authors ONLY §14.5.2 (within C-RT-15) + its fail-class extension. The minimal inline `content` carrier + the `version_sha == digest(content)` derive-invariant are IS-axis-owned (IS spec v1.6 §5.2, co-published). The fuller prompts surface (multi-version PROMPTS store, CP per-role/workload selection, OD per-tier governance) is the PR #2/#3/#4 cascade — NOT this arc. String-only system content (no Anthropic `system`-array `cache_control` blocks) at v1.44 (OQ-1).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
