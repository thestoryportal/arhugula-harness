---
artifact: design-substrate/Spec_Operational_Discipline_v1_28.md
version: v1.28
cleared_at: 2026-06-10T23:40:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/post-mvp-full-closure-plan-v1.md (Phase P4 line 149 — OD tail-keep bounded-buffer bounds; line 45 Category-1 Claude-closeable)
  - Project_Roadmap_v1.md §5.15 R-CL-P4 (spec-completion deferrals; OD buffer bounds sub-part)
  - design-substrate/Spec_Operational_Discipline_v1_27.md §2(a) (the bounded-buffer carve-out this delta closes)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - advisor() pre-substantive decision-fork (caught the R-CL-P4 OD-buffer scope gap; confirmed build-not-park)
  - empirical impl-grounding pass (C-OD-09 §9.3 + closure-plan line 45 Cat-1 build-vs-fork discriminator)
  - mode-agnostic / Phase-7 bundled-absorption posture (workspace CLAUDE.md §11.4)
supersedes:
superseded_by:
---

# Clearance — `Spec_Operational_Discipline v1.28`

v1.28 closes the v1.27 §2(a) bounded-buffer carve-out — the MVP `TailKeepSpanProcessor` did not bound its per-trace buffer by trace count or per-trace span count, an explicit "follow-on arc per §9.3 implementer-discretion." The follow-on is materialized: two operator-tunable ceilings (`CollectorConfig.tail_keep_max_buffered_traces` + `tail_keep_max_spans_per_trace`, both default 4096, both validated `> 0`) bound the production buffer (drop-oldest trace eviction + per-trace overflow-span drop, both counted), contained by a pathological-producer e2e test. This is a Category-1 Claude-closeable sub-part of R-CL-P4 — distinct from R-CL-P4's two IS-axis design-gated forks (prompts/`active_prompt_version` + keying-tuple D-ADR), which remain blocked on operator ratification.

This is a Phase-7 bundled-absorption arc (design-substrate spec delta + `harness-od/src` + `harness-runtime/src` landed together), legitimate per workspace `CLAUDE.md` §11.4. The change is a thin canonical-reading reconciliation closing an implementer-discretion deferral — the same delta shape v1.27 used for §9.3 elements (a)/(b)/(c). ZERO new contract; ZERO new C-OD-NN field; the two ceilings are runtime-impl `CollectorConfig` fields, not spec contract fields. The eviction-policy choice + alternative consideration are documented at the carrier module docstring per the v1.27 element-(a) "rationale in docstring" pattern.

Verification: `harness-od/tests/test_tail_keep_span_processor.py` (drop-oldest eviction + per-trace overflow + bounds-don't-affect-legitimate); `harness-runtime/tests/test_config_collector_config.py` (defaults + `> 0` validation for both new fields); `harness-runtime/tests/test_lifecycle_span_processor.py::test_production_surface_threads_collector_buffer_bounds` (e2e config→materializer→enforced bound). 983 OD+runtime tests green; pyright 0 errors; overlay-check clean (zero new C-OD-NN contract).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The v1.27 §2(a) body is preserved verbatim (frozen change-note describing the v1.27 MVP state); v1.28 records the subsequent closure.
- See `.harness/clearance/README.md` for marker discipline.
