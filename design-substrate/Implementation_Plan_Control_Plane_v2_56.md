# Implementation Plan: Control Plane — v2.56 (PROPOSED delta over cleared v2.55)

**Status: PROPOSED — not cleared.** Grounded on cleared v2.55; implements proposed CP spec v1.128.
Buford owns numbering and fold at filing.

## U-CP-106 — typed resume refusal (A4)

**Source:** `harness-cp/src/harness_cp/workflow_driver_types.py` (`ChildResumeRefusal` tenth value,
`ResumeRefusal`, `RunResult.resume_refusal` + FAILED-only validator, `ChildResumeRefusedError` one
stored refusal); `harness-cp/src/harness_cp/workflow_driver.py` (three pre-step guards, two typed
fan-out gate-owning mismatches, refused terminals rendering fail class and carrier from one merged
value).

**Acceptance criteria:**
1. Each of the three pre-step guards returns FAILED with `resume_refusal == {hitl-gate-config-changed}`,
   unchanged fail-class text, and no step dispatched; an unchanged resume carries no refusal.
2. Both fan-out gate-owning branch checks return the same typed refusal.
3. A refused terminal (both fan-out families) carries the union of reasons and signing fact, and its
   fail class is the sorted rendering of that same value. The owed witness, for PARALLELIZATION and
   for ORCHESTRATOR_WORKERS, has two children refuse concurrently in one resume, with disjoint
   reasons and differing signing facts, both recorded before the barrier ends. It asserts the
   complete reason union, `audit_signing_failed` true (the OR) and the fail class rendered from that
   union with the `audit-signing-failed` suffix. Mutations that keep only the first or only the last
   recorded refusal must turn these tests red at the applicable source head. A regression in the
   same module keeps v1.124 §0.4: under `proceed`, a refusal still in flight when the barrier
   deadline cancels its branch leaves the run PARTIAL with `resume_refusal` `None` and no suffix.
   *Historical limit:* the preparation's terminal-union check records one refusal carrying several
   reasons. It cannot distinguish a first- or last-record selector, so it is not this witness.
4. The value rejects an empty reason set; `RunResult` rejects a refusal on any non-FAILED status; a
   multi-reason error exposes `reasons` and refuses a single `reason`.
5. A genuinely failed step whose text names the reason carries no refusal.
6. Mutations that must fail a test: deleting a leaf carrier; dropping the terminal carrier while
   keeping its text; selecting the first or the last recorded refusal instead of the union
   (criterion 3).
7. Ruff and pyright clean on the touched files; existing refusal, gate-config and topology suites pass.

Delivery portions (by content; commits are recorded in the fork record). **Unit 1** — the value, its consumers and the refused terminals: criteria 3-5 (criterion 3's
two-child matrix and selection mutants are owed; no preparation head carries them); criterion 6's terminal-carrier-deletion mutation; the applicable Unit-1 regression checks (value, FAILED-status, multi-reason, terminal-union and genuine-failure sections). **Unit 2** — the three pre-step guards and two fan-out gate-owning checks: criteria 1-2; criterion 6's leaf-carrier-deletion mutation; the completed CP test module and the producer and topology regressions of criterion 7. Mutation, full lint/type and topology proof at each unit's head is still owed; a narrow owning-test pass does not cover the broad regressions.
