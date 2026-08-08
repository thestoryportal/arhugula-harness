# Council Charter — B-116 breaker-failure semantics

**Convened:** 2026-08-07, operator-authorized via AUQ ("Hold — I want the council first"), main @ `6db21f14`.
**Question:** Should DETERMINISTIC harness-internal faults count toward a provider-model circuit-breaker's failure state?
**Decision surface:** the per-member disposition table at `.harness/class_2_fork_b116_breaker_failure_semantics_harness_internal_faults.md` §5 — readings (I) candidate-failed vs (II) provider-health per-member split.
**Spine-tension (named in advance, §10.9 gate PASSED):** C9 ⊥ C11 — *a breaker that under-counts fails to protect a genuinely failing chain* (reliability) vs *a breaker that over-counts opens every healthy provider's breaker on one operator misconfiguration* (operator-loop/local-first; probe-verified harm).
**Convening (dyadic-plus):** primaries C9 + C11 (the tension holders); consultants C1 (chain-advance/orchestration semantics), C7 (what breaker telemetry MEANS to an observer). Cap justified: the genuine domain center is two voices; C1/C7 react, not deliberate first.
**Grounding pack (each voice pre-binds to these, not SKILL.md memory):** the §1–§5 filing; `retry_breaker_fallback.py:272,358-370,662-665,1006-1028`; `retry_breaker.py:192-263`; C-CP-03 §3.4-§3.5; C-OD-07 §7.1; Runtime §14.6 D2 + step-4 bullet (`Spec_Harness_Runtime_v1.md:4122,4145`); C-MEM-19 disclaimer; probes A–D transcripts (in filing §3).
**Stages:** E1 (A1 primaries independent → A2 consultants react → B cross-read debate) → E2 adversarial → consolidated reconcile (operator checkpoint) → ratification AUQ. Codex leg: quota-floor fallback per checkpoint discipline (advisor + adversarial carry the decorrelation; noted deviation from spec E3).
**Ledger:** this tree, additive-only, orchestrator-written from returned agent markdown.
