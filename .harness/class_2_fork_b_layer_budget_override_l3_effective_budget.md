# Class 2 (in-execution, FULL-SPEC-pre-authorized) — `B-LAYER-BUDGET-OVERRIDE`: the L3 router timeout honors the §3.1 effective (override-resolved) budget

**Status:** ✅ BUILT (2026-06-19) — bundled-absorption arc co-landing CP spec v1.42 → **v1.43** (in-place C-CP-02 §2.5.3 amendment) + clearance marker + `harness-cp/src` (the override resolver + the L3 site) + `harness-runtime/src` (the dormant dispatcher seam) + by-execution tests. Materializes the cleared C-CP-03 §3.1 per-workload-class × per-persona-tier budget-tuning surface that ships **built-but-vacuous** (zero production callers).
**Filed at:** R-FS-1 standalone arc `B-LAYER-BUDGET-OVERRIDE` (the 13th standalone `B-*` arc since the FROZEN order completed)
**Locus:** `harness-cp/.../layer_budget.py` (`effective_layer_budget_ms` — the `budgets`-tuple-aware override resolver) + `harness-cp/.../routing_core_surface.py` (`infer()`'s L3 timeout) + `harness-runtime/.../llm_dispatch.py` (the dormant `RuntimeLLMDispatcher.budgets` threading seam) vs cleared `Spec_Control_Plane` C-CP-03 §3.1 + C-CP-02 §2.5.3 + `.harness/beyond-mvp-capability-boundary-ledger.md` (the B-LAYER-BUDGET-OVERRIDE registration)
**Classification:** Class 2 (in-execution; FULL-SPEC directive 2026-06-12 pre-authorizes the build + design back-flow). **NO operator gate** (see below).
**Routing:** Bundled-absorption per workspace `CLAUDE.md` §11.4.

## What was built

C-CP-03 §3.1 commits the per-layer time-budget as **per-workload-class operator-tunable**, with the tuning surface **"per layer × per workload class × per persona tier"** — and names the router layer explicitly: *"the higher-tier persona caps budget tighter **on `llm_as_router`**."* The override carrier was built (`LayerBudget.per_workload_override` / `per_persona_override` + `effective_budget`, U-CP-06) but **vacuous** (`[[built-but-vacuous-reground-ledger-asis]]`: zero production callers — only its def + `test_layer_budget.py`). The R-impl-1 L3 `asyncio.wait_for` timeout (the first + only site enforcing a real wall-clock layer budget) read the **flat** `time_budget_ms`, with an in-code note registering the override-honoring as a "forward arc / X-AL-3".

The build materializes the §3.1 surface at that site:

1. **The resolver** — `effective_layer_budget_ms(budgets, layer, workload_class, persona_tier)` (`layer_budget.py`): the `budgets`-tuple-aware sibling of `effective_budget`. The L3 site receives the operator-bound `budgets` tuple, so the override maps must resolve against THAT tuple — `effective_budget` reads the module-global `DEFAULT_LAYER_BUDGETS` and so **physically cannot serve the site** (the structural proof the ledger named). Precedence per U-CP-06: per-workload → per-persona → the flat default; passed-tuple → DEFAULT → 200 ms fall-through (mirroring the removed `_layer_time_budget_ms`).
2. **The L3 site** — `infer()` (`routing_core_surface.py`) resolves the L3 timeout via `effective_layer_budget_ms(budgets, LLM_AS_ROUTER, request.workload_class, request.persona_tier)`. The orphaned flat `_layer_time_budget_ms` (its sole caller) is removed. The over-cautious "NOT honored / X-AL-3 forward arc" comment is retired.
3. **The dormant dispatcher seam** — `RuntimeLLMDispatcher.budgets: tuple[LayerBudget, ...] = DEFAULT_LAYER_BUDGETS` (`llm_dispatch.py`), threaded to `infer(budgets=self.budgets)` (was hardcoded `DEFAULT_LAYER_BUDGETS`). Production stage-5 leaves it default → byte-identical; a future operator-config / test supplies override-bearing budgets.

## Why NO operator gate (lead with §3.1; the X-AL-3 reversal)

The in-code note at `routing_core_surface.py` (a prior R-impl session + Codex) read honoring overrides at L3 as "changing the §2.5.3 flat-budget contract (X-AL-3)". **Re-grounding the cleared spec overturns that as over-cautious** (`[[cleared-spec-resolves-it-before-first-principles-fix]]`):

- **§3.1 (cleared at v1.2, PRESERVED VERBATIM) affirmatively commits the override at the router layer** — "per layer × per workload class × per persona tier … the higher-tier persona caps budget tighter **on `llm_as_router`**." So honoring it **fulfils** a cleared contract; it does not extend the design. The surface is built-but-vacuous, not absent.
- **No committed invariant is sacrificed.** Contrast B4-Slice-4's *role* relaxation, which gated because runtime §14.5.3 invariant 2 *explicitly forbade* per-step role. §3.1 is the opposite — it *commits* the override. This is the gate-discriminator on its build-the-committed-surface side (`[[feedback-gate-only-on-meaningful-architecture-change]]`, `[[grounding-reveals-claude-closeable-slice-close-honestly]]` spec'd→build).
- **No ratified "flat-only at L3" decision exists** in the fork/clearance ledger (the advisor-required check): the v1.36 clearance shows §2.5.3 was about making the timeout *enforceable at all* (the Codex round-1 [P2]); override-honoring was registered "build later," not "decided never."

The §2.5.3 amendment narrows the enforced budget VALUE (flat → §3.1-effective) while preserving the v1.36 "Timeout = exhaustion" requirement → bundled-absorption (spec + impl together) under the FULL-SPEC directive, NOT an operator gate.

## Production-dormancy is honest (the non-vacuity scoping — advisor's #4)

This is **capability-built, production-dormant** — NOT "fires in production":
- Production never reaches L3 today (`router=None` + the DECLARATIVE echo always resolves), so the L3 timeout site is inert.
- The runtime dispatcher binds the DEFAULT budgets (no operator override surface is wired) — the new `budgets` seam is the dormant threading path that LETS a future deployment supply overrides.
- Live firing additionally depends on the **UNOWNED routing-activation gate** (the same gate L2/L3 share, per the spine ledger) that makes traffic reach L3.

The non-vacuity witness lives at `infer()`: a real per-persona / per-workload override governing a real router timeout (with a flat-default negative control), NOT a production-firing claim.

## Scope + out-of-scope

In scope: the L3 router timeout honoring the §3.1 override + the resolver + the dormant dispatcher seam. OUT: deterministic-layer (DECLARATIVE / EMBEDDING) wall-clock enforcement (`route()` reads only `budget_exhausted`, enforces no wall-clock there — a separate arc); the R-impl-2 "200 ms empirically unmeetable by a local router" default recalibration (this arc changes WHICH budget is enforced, not the default value); a `RuntimeConfig` budget surface (no spec commits one — if added later, both env-loaders per `[[runtimeconfig-scalar-needs-both-env-loaders]]`).

## Decorrelated review (pre-merge)

advisor (full-transcript, per `CLAUDE.md` §13.1) — confirmed the X-AL-3 reversal is sound; steered to (1) lead with §3.1's affirmative on-`llm_as_router` commitment and DROP the shaky "effective"-reading of §2.5.3 (the §3.1 cite there sources the word *LayerBudget*, not `effective_budget()`); (2) frame the §2.5.3 edit as a real small amendment + version bump, not "doc-hygiene"; (3) verify the no-gate discriminator via a ledger grep for a ratified "flat-only at L3" (none found); (4) the non-vacuity overclaim trap — witness at `infer()`, dispatcher seam dormant/activation-gated, never "fires in production"; (5) don't balloon scope or add a RuntimeConfig budget surface. All applied. Out-of-family Codex review at the impl-diff PR (decorrelated; pending).

## Verification

- harness-cp: `test_routing_core_surface.py` — `test_infer_l3_honors_per_persona_budget_override` (the discriminating witness: a 1 ms per-persona override governs over a HUGE 5 s flat default → the 30 ms router times out → raise; SAME router with NO override → the flat default governs → success — both branches in one self-discriminating test) + `test_infer_l3_honors_per_workload_budget_override`; `test_layer_budget.py` — 4 `effective_layer_budget_ms` resolver units (flat default / per-persona / per-workload-precedes-per-persona / DEFAULT-tuple fallback).
- harness-runtime: `test_lifecycle_llm_dispatch.py` — `test_layer3_budget_override_threads_through_dispatcher_seam` (the dormant seam threads `self.budgets` end-to-end through the real dispatcher, the override resolving via the test-only `layer_decisions` seam) + `test_dispatcher_budgets_field_defaults_to_module_default`.
- Gates: whole-workspace pyright 0/0/0 · ruff · harness-cp 1093 passed + 1 xfailed · harness-runtime 1961 passed / 10 skipped (non-e2e) · decorrelated review advisor (pre-build X-AL-3 reversal + scope + non-vacuity) + out-of-family Codex (pre-merge).
