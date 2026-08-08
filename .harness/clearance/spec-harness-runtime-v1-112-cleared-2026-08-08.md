---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.112
cleared_at: 2026-08-08T00:00:00-06:00
clearance_type: ratified-fork-apply-pass
back_reference:
  - .harness/class_2_fork_b116_breaker_failure_semantics_harness_internal_faults.md (FILED PR #1265; the per-member disposition question this leg resolves)
  - .harness/council/b116-breaker-semantics/DELIVERABLE.md (merged PR #1267 — the operator-convened FULL council workflow's UNANIMOUS corrected package; E1 primaries C9/C11 → consultants C1/C7 → cross-read with seam #5 resolved by C9 concession → E2 adversarial 8 findings incl. one halt-class → operator-authorized E2b bounded reconcile)
  - operator ratification 2026-08-07 — Reading (II), taken after reviewing the full deliberation ledger in-session (the held "questions first" gate resolved by direct document review)
  - .harness/forward-register.yaml row `B-116` (status `operator_gated` → `open` — the impl leg U-RT-152 and the `B-116-t3` OD leg are owed; the row flips to `closed` only when BOTH merge)
  - PR '#pending' (this arc)
merge_commit: pending
reviewer_chain:
  - ratified-fork apply pass — applies the operator-ratified **Reading (II)** and the council-unanimous DELIVERABLE package and EXTENDS NOTHING beyond them. The amendment's CONTENT is fixed by the DELIVERABLE's ratified reading, normative test, 7-row table, guard shape and binding terms t1–t5; the determinations this leg made are recorded at contract altitude in the change-note so a reviewer can overturn rather than discover them.
  - empirical grounding pass at this leg — the spec head verified at **v1.111** before editing; §14.6's step-4 fail-fast bullet, D2, §14.6.1 and §14.6.2 re-read directly at HEAD `969846a0`; **every count re-verified programmatically**: the fail-fast set's FIVE members re-read at `_classify_provider_exception` (`retry_breaker_fallback.py:272`, incl. the B-114 seventh-raise-site nuance in its docstring); `LLMDispatchPayloadShapeError` raise sites counted **28** in `llm_dispatch.py` (= the council's 3 pre-flight + 25 response-parsing split; the `:323` pre-flight exemplar read directly); `LLMDispatchProviderUnreachableError` raise sites counted **3** (`:1525`/`:1549`/`:1865`); the charge site `record_failure(cause=breaker_cause)` re-read at `:1028` on the cause-`None` branch; Probes B/C re-resolved to their council definitions (chain-length amplifier; null-topology) before being carried into plan ACs.
  - out-of-family Codex E3 — NOT run at ratification (weekly quota floor until Sat 2026-08-09 ~08:43; recorded deviation, carried forward from the council record). Review duty at this leg: harness-adversarial-reviewer + fresh-context Opus rounds (records appended below as they run).
supersedes: spec-harness-runtime-v1-111-cleared-2026-08-05.md
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.112`

v1.112 is the `B-116` spec leg: TWO amendment sites, both inside §14.6 — a NEW **§14.6.3** (*Breaker-failure semantics for deterministic harness-internal faults*) and ONE strict append at step 4's fail-fast bullet. §14.6.3 contracts the ratified Reading (II) — a breaker failure means "this provider-model is unhealthy" — via the recovery-model normative test (*a fault charges the provider-model breaker only if a half-open trial call could return a different result than the trip did, for a reason attributable to the `{provider, model}` the breaker is keyed to*), fixes the 7-row per-member disposition table (2 count / 4 waived / 1 prospective-conditional), the four-type waiver tuple enumerated BY NAME, binding terms t1–t5 (waived-charge span-attribute pair; the in-venue floor record with the `B-116-t3` OD leg registered as a NAMED closure gate; the durable-persistence pin; no HITL), C9's trip-threshold revisit-trigger, and the dead-half-open-latch residual stated honestly (zero `attempt_half_open` production call sites; forward row `B-118` owns the debt).

What was reviewed during clearance: the full council deliberation ledger (charter, 8 contributions, E2 review, DELIVERABLE) was re-surfaced to the operator in-session and the ratification taken on the documents themselves; every count claim in the DELIVERABLE was re-verified programmatically at HEAD before being carried into contract text. Deferrals: the impl leg (Runtime plan v2.60 U-RT-152); the `B-116-t3` OD leg (OD §9.2 roster 18 → 19); the `B-115` (b′) leg (its type joins the waiver tuple only on confirmed determinism). ZERO new `C-RT-*` numbers, ZERO CXA rows (aggregate frozen at 111), ZERO OD roster delta at this leg, ZERO `harness-*/src|tests` edits.

Caveat for Phase 7 consumers: the waiver is CONTRACTED but NOT YET BUILT — until U-RT-152 lands, the shipped composer still charges every fail-fast member; code written against §14.6.3's waiver semantics before that merge is ahead of the implementation.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
