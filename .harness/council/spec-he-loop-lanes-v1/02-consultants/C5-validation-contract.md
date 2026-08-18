# E1 A2 — C5 validation / contract (consultant, reacting to C9/C10/C7)

## Reactions to primaries

| primary finding | reaction | evidence | resulting fix text |
|---|---|---|---|
| **C9-F4** (retry-param table; reuse `agy_review.py` `remaining_review_timeout`?) | **FALSIFY** the reuse premise; keep the finding | `agy_review.py:22,37,461-463,476,508,556,449-457`: `remaining_review_timeout(deadline)` is a monotonic single-pass **budget decrementer** across sequential segments (`TOTAL_REVIEW_TIMEOUT_SECONDS=1260.0`); no retry loop; `report_process_failure` returns immediately on non-{124,127}; 124/127 → unavailable, zero re-attempt. It supplies `total_budget_s` only. | C-HE-16 new clause: "`review_wrapper_common.py` MUST define its own retry loop; it MAY reuse the `TOTAL_REVIEW_TIMEOUT_SECONDS`-shaped deadline as `total_budget_s` only. Table: `{per_attempt_timeout: total_budget_s, max_attempts: 2, backoff_base_ms: 0, backoff_cap_ms: 0, total_budget_s: 1260}` — a review retry is one bounded re-invocation on `transient`, not a polling loop; exhaustion → `HITL-recoverable`, not `permanent-fail-exit` (a wedged reviewer login is human-fixable)." |
| **C10-F3** (validate disposition writer vs `producer`) | **FALSIFY** the mechanism; finding stands | `finding_id` = `<producer>:<head_sha>:<location-hash>:<n>` (spec) and the append-only invariant forbids `producer` differing across rows sharing a `finding_id` — comparing the disposition row's `producer` to the finding's `producer` compares a field to itself. No field records who appends the disposition. | C-HE-24 §4: envelope gains `disposition_actor: <null|actor_id>` populated only on disposition rows; emitter MUST reject any row where `disposition_actor` equals the `producer` substring of `finding_id`. Same field serves C7-F4 (`adjudicator_identity`) — author once. |
| **C7-F11** (`base_sha`/`diff_digest` locus) | **REFINE** — pick the locus | C-HE-25 aggregates per arc; a verdict is per round/channel; `head_sha` already lives in the envelope; `base_sha`/`diff_digest` are wrapper-known, correctly absent from the per-channel schema. | Envelope becomes `{ts, arc_id, lane_id, head_sha, base_sha, diff_digest, round_n, disposition, unique_catch, disposition_actor}`. |
| **C7-F4** (`adjudicator_identity`) | **REFINE** — merge into `disposition_actor` | Two names for one concept invites drift (one path populates one, a reviewer checks the other). | C-HE-29 §3's neither-family rule = the C-HE-24 §4 self-disposition ban applied to the shadow-trial actor set; no separate field. |
| **C9 T4 wording** (primitive-side attempt-rate bound) | **TENSION** | A rate-refusal is a new fail path distinct from `lease_contended`; the §9 gate contract has one row for both. | Split C-HE-06 §9: contention keeps `lease_contended`; primitive-side rate refusal (if C9-F3 lands) gets `cause_attribution: lease_acquire_rate_exceeded`, same `fail-class: transient-retry`. |

## Own findings

| id | class | contract | quote | defect | fix |
|---|---|---|---|---|---|
| C5-F1 | **1** | C-HE-24 §1/§2, C-HE-06 §9 | `code ← <check>:<fail_class>:<cause_attribution>` e.g. `merge-door-lease-acquire:transient-retry:lease_contended` | No field named `cause_attribution` exists in the core or envelope; `finding_type` is singular and maps to `fail_class`. `code` cannot be constructed from a stored field. | Add `cause_attribution: <string>` to the envelope (not the ratified core — the envelope is declared outside the ratified shape, so T3 is not re-opened). Every `producer` emitting a fail-class-bearing row (C-HE-06 §9, C-HE-16 §3, C-HE-31 checks) MUST populate it; §2's `code` reads it from the envelope. |
| C5-F2 | **1** | C-HE-06 §8/§9 | "at most 12 attempts (≈ 1 h) before routing to the HITL queue" | Exhaustion is an unlabeled terminal; the taxonomy's default `transient-retry → permanent-fail-exit` fallthrough contradicts what §8 specifies (HITL). | Add to §9: "Exhaustion of §8's budget (12 attempts) is `HITL-recoverable` with `cause_attribution: lease_acquire_budget_exhausted` — an explicit exception to the default fallthrough, because a wedged lease is human-actionable." |
| C5-F3 | 2 | C-HE-06 §5/§9 | "restart from step (ii) and re-issue step (iv) once" | The reconcile/re-issue is a second stateful decision point with no gate-contract row and no fail-class on its own exhaustion. | Add §9 row `merge-door-reconcile`: hybrid (ground-truth query + one bounded re-invocation) · input: lease payload + `pr` · output: MERGED / re-issue-then-recheck / exhausted · exhaustion fail-class `permanent-fail-exit`, `cause_attribution: merge_reissue_exhausted`. |
| C5-F4 | 2 | C-HE-15 §4 | `findings: [{severity, location, message}]` | `severity` value set never declared; the only enum in the corpus is `Finding.severity` `# hard | warn | info` (a comment; `:1050` gates on `== "hard"` only) — a different projection layer. A schema with no enum cannot reject a malformed severity. | Add "`severity ∈ {P1, P2, P3}` (merge-gate convention, distinct from `Finding.severity`'s `{hard,warn,info}`); schema sets `additionalProperties: false` on `findings[]` items and enumerates `severity`; out-of-enum → `REVIEWER_UNAVAILABLE`." |
| C5-F5 | 2 | C-HE-31 §4, §8.1 | "demoted to advisory automatically … zero false positives across … 20 merged arcs" | No §8.1 row verifies the promotion/demotion state machine; not pass/fail-decidable. | Add §8.1 row: `tools/test_mechanized_checks.py::test_promotion_demotion_state_machine` (synthetic 20-arc replay: 0 rejections → promote; ≥2 → demote + finding row) · layer2 · local + CI. |
| C5-F6 | 3 | C-HE-16 §3 | "MUST record `{permanent|transient, reason, channel}`" | No mapping from the `{permanent,transient}` axis to `fail_class` in `code`. | "`REVIEWER_UNAVAILABLE(permanent)` → `fail_class: permanent-fail-exit`; `(transient)` → `transient-retry`." |

## Position on T3 / T6 / T7

- **T3** RECONCILE(wording): agree with C7's ACCEPT on field-count/projection; the ratified shape as exercised needs `cause_attribution` and `disposition_actor` — both in the envelope, so T3 substance is not re-opened.
- **T6** RECONCILE(wording), orthogonal axis: no position on the GitHub-serialization citation; the reconcile step needs its own gate row + exhaustion fail-class (C5-F3).
- **T7** RECONCILE(wording), building on C10: demotion-emits-row is sound; the state machine has zero §8.1 coverage (C5-F5).

## Verified at HEAD

`agy_review.py:22,37,449-457,461-463,476,508,556` · `codex_review.py`, `review_wrapper_common.py`, `review_schemas/` absent · `codex_context_guard.py:113-117` (`severity: str  # hard | warn | info` comment-only), `:1050` (`== "hard"`) · spec lines 205-206, 366, 383, 494-497, 503.

## Voice self-check

C5 can name where fail-class/cause_attribution/disposition-actor fields are missing but has no standing on whether adding them to the envelope is "additive" in C-HE-24 §2's consumer-sweep sense — a C7/C9 question C5 did not re-run.
