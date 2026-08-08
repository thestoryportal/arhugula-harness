# Implementation Plan: Operational Discipline — v2.33 (delta over v2.32)

*v2.33 is the OD plan leg of the **`B-133`** arc — the realization debt OD spec v1.37's honest-scope paragraph registered and did not repair. `Spec_Operational_Discipline_v1_38.md` §1 adds **NEW §C-OD-09 §9.2.1** (five normative terms: the tail consumer resolves §9.2 against span EVENT names as well as span names; the carrier forwards immediately; the §10.2 keep flag is mirrored but not widened; the HEAD half is a DECLARED BOUND; bookkeeping is bounded). This delta authors **ONE NEW atomic unit, U-OD-59**, carrying that subsection's realization at the shipped substrate and its witness set. All sections except the §0 change note and the NEW U-OD-59 body + coverage delta below are PRESERVED VERBATIM from v2.32 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.32 → v2.33)

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_32.md` (v2.32 — the `B-116-t3` leg's OD plan delta; NEW U-OD-58).

### §0.2 Why this delta exists

v2.32 §1.2 states plainly what U-OD-58 did **not** own: *"The floor's END-TO-END REALIZATION at the SDK boundary. Registered as `B-133`. This unit lands the roster row and its witnesses; it does not make the event survive a base-rate drop of the wrapper span that carries it."* `B-133`'s close-out sequenced that work as *probe first, then repair*. **Both steps are executed at this leg**, and the probe is what authorizes the repair rather than a prediction of it.

**The probe result, recorded before the unit body so the unit reads as a consequence of it.** A REAL exhausted dispatch was driven through the REAL `HarnessCompositeSampler` + the REAL `TailKeepSpanProcessor` across seven configurations covering all three event-shaped members. **Zero spans reached the exporter at either consumer, for every member.** The full arm table is at OD spec v1.38 §0.1; the mechanism is that the carrier span `harness.runtime.retry_breaker_fallback` is in **neither** §9.2 (by name) **nor** §10.2 (by trigger predicate), so it buffers and drops at root close.

### §0.3 Sections revised

§0 (this change note, including the NEW §0.9 out-of-family adjudication and §0.10 witness-homing correction and §0.11 merge-gate BLOCK); §1 (the NEW U-OD-59 body); §2 (coverage delta). All other sections — every existing `U-OD-NN` body including U-OD-58, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.32.

### §0.4 Scope discipline

ADDITIVE — ONE NEW atomic unit (U-OD-59), the next free OD unit ID after v2.32's U-OD-58 (verified: no `U-OD-59` occurrence anywhere in `design-substrate/` or `.harness/` before this filing). **ZERO amended units** — neither U-OD-11 (which owns `sampling_mode.py`) nor the tail-keep processor's own carrier unit has its acceptance criteria rewritten, per the `B-97`(a) → U-RT-149 and `B-96` → U-RT-150 precedent that a landed unit is not retroactively re-scoped by a later contract amendment. **ZERO new contract IDs** (C-OD-09 exists; §9.2.1 is a subsection of its own material). **ZERO roster change** (§9.2 stays at nineteen — this unit changes how the roster is RESOLVED, never what is in it). **ZERO new namespace.** **ZERO new cluster.** **ONE new DAG node + TWO new intra-axis edges** (U-OD-11 → U-OD-59 for the `is_always_sampled` SSOT; U-OD-58 → U-OD-59 because the roster's nineteenth member is one of the three the arm exists to deliver). **ZERO cross-axis edges; ZERO CXA rows** — verified, not assumed: `tail_keep_span_processor.py` imports only `harness_od.*` and the OTel SDK, gains no new import at this unit, and exposes no new symbol outside `harness-od/`.

### §0.5 A close-out hypothesis that grounding FALSIFIED — recorded, not inherited

`B-133` close-out step (2) says of the head consumer: *"the HEAD surface at a head-based-dev cell samples at 1.0 anyway, so the head arm may need nothing — confirm rather than assume."* **Confirmed, and it is FALSE.** Enumerating `PER_CELL_BASE_RATE_ENVELOPE` against `PER_DEPLOYMENT_SURFACE_SAMPLING` at this filing returns **two** `HEAD_BASED_DEV` cells, not one, and the second is not at 1.0:

| Cell | §9.1 mode | §10.3 default | tail processor engaged? |
|---|---|---|---|
| solo-developer × local-development | `HEAD_BASED_DEV` | 1.0 | no |
| **team-binding × local-development** | **`HEAD_BASED_DEV`** | **0.5** (min 0.1) | **no** |

`span_processor.py:368` wraps the BSP with `TailKeepSpanProcessor` only when `deployment_surface != LOCAL_DEVELOPMENT`, so at `team-binding × local-development` there is **no tail consumer at all** and the head half is a live exposure. The head half still cannot be repaired at this unit's venue — a span's events do not exist at span creation — so it is carried as a **declared bound** (OD spec v1.38 §9.2.1 term 4) with a witness that ASSERTS the drop and names it as the bound, rather than a comment that hopes it is vacuous. **The prediction was not inherited; the enumeration is.**

### §0.6 A pre-existing bookkeeping defect the probe surfaced, registered rather than absorbed

`[HIGH]` While grounding where the new arm should return, a second probe asked whether the **existing** name-matching arm leaks its trace buffer. It does: a trace whose ROOT close is an always-sampled span (`sandbox.violation` with one ordinary buffered child) leaves `buffered_trace_count == 1` after the root closes, because that arm returns before the root-close materialization step. A control trace with an ordinary root returns `0`.

This is **PRE-EXISTING and outside this arc's authorized scope** — repairing it would change shipped behaviour for every name-shaped always-sampled root, which OD spec v1.38 does not authorize. It is **registered as forward row `B-136`**, not silently fixed and not silently ignored. What this unit **does** owe is that its own arm must not EXTEND the leak, and that is a real risk rather than a theoretical one: on the dispatch path the carrier span **is** routinely the root close (observed directly at the positive control), so an unconditional early return here would put the common case into the leaking shape. AC #6 and its PD-8 probe (iv) close that.

### §0.7 A witness that the PD-8 probe found was NOT load-bearing, and how it was sharpened

`[HIGH]` PD-8 probe (ii) — make the event lookup return `False` unconditionally, i.e. revert to name-check-only — was run and returned **26 failed / 6 passed**. Among the six passing was the trigger-flag mirror witness, which asserted only **membership** (`"ordinary.root" in names and "sibling.work" in names`). That assertion is satisfied **without** the arm: the span's own `validator.fail.permanence=permanent` attribute sets the keep flag on the buffered path, so both spans forward at root close either way.

The witness was **sharpened rather than dropped**: it now asserts export **ORDER** (`== ["ordinary.root", "sibling.work"]`), which the arm alone produces — the arm forwards the carrier immediately (root first, eviction-safe, bypassing the buffer) whereas the buffered path materializes in insertion order (sibling first). **Re-run under the identical mutation after sharpening**, W6 moved from the passing set to the failing set — the mutation-kill demonstrated by measurement rather than asserted. *(The figure first recorded here, "27 failed / 5 passed", was **stale and did not even sum to the roster**: it was measured before W13/W14 existed, and the merge gate's lens-2 caught the arithmetic. Every probe figure in this plan has since been RE-MEASURED against the final roster at AC #9's table; none is carried forward from an earlier roster.)* *This is recorded because a witness that passes under the mutation it exists to catch is exactly the "presence-not-correctness" failure the workspace checklist names, and finding it is what the probe is for.*

### §0.8 PD-8 probe (iii) returned GREEN — and the honest reading is narrower than "cost, not correctness"

`[HIGH]` Probe (iii) moved the event arm **above** the name arm. **0 failed / 70 passed**, unchanged.

An earlier drafting called this *"a **cost** property, not a correctness one"*. That claims more than was measured, and the merge gate's lens-3 supplied the precise form, adopted here: **no witness distinguishes the two orderings**, and the only observable divergence would be on a span the name arm deliberately holds back — the **non-root succeeded `subagent.span`** — where running the event arm first would forward a span the §9.2 root-conditional gate meant to buffer. That divergence **narrows `B-136`'s territory**, not this arm's, and no witness reaches it today.

The ordering is therefore **left name-first for cost and NOT asserted** — the same shipped outcome as before, but stated as *"unconstrained by the current witness set"* rather than as a proven equivalence. *Recorded rather than quietly reworded: a green probe described as proving more than it measured is the same defect class as a stale count.*

---

### §0.9 An out-of-family finding against this arc's own commit, adjudicated by measurement

`[HIGH]` Codex round 1 against commit `ff63c725` returned ONE P1: at `TAIL_BASED_PROD` cells with `base_rate < 1` the head sampler drops the carrier at span **creation**, so no `ReadableSpan` reaches the new tail arm and §9.2.1 term 4's coverage claim is false. **It was grounded at the wiring and then measured, not accepted or declined on argument** — and it is **CORRECT**.

`tracer_provider.py` resolves `build_default_sampler(base_rate=PER_CELL_BASE_RATE_ENVELOPE[cell].default_rate)` **unconditionally**, and states in the same function that *"the current default sampler ignores the mode … Future units may wire mode-conditional samplers."* Measured through the real composition, 4,000 carriers per cell:

| Cell | head base-rate | event carriers reaching `on_end` | exported |
|---|---|---|---|
| `team-binding × self-hosted-server` | 0.1 | **10.4%** | 10.4% |
| `multi-tenant-compliance × managed-cloud` | 0.2 | **20.9%** | 20.9% |
| `solo-developer × self-hosted-server` | 1.0 | 100% | 100% |

**The arm is real but PARTIAL: of the carriers that reach the tail it delivers 100%** (420/420 and 837/837). **What was defective was the contract TEXT, not the unit** — term 4's *"every `TAIL_BASED_PROD` cell … is covered by terms 1–3"* is RETRACTED in OD spec v1.38 and replaced by the per-cell admission table plus the statement that the head bound reaches **five of eight** ACTIVE cells.

**A second framing was falsified by the same run**, and recording it matters more than recording the first. The finding is **not** that "everything the tail preserves is equally starved": a §9.2 member realized as a **root span name** is admitted at **100%** even at base-rate 0.1 (measured 4,000/4,000 for `sandbox.violation`), because the head resolves `is_always_sampled` against the span name. Only **event-carried** members and **non-root** spans are starved — the latter including non-root §10.2 triggers, measured at **~9%** preservation. **The floor's realization depends on the member's emission SHAPE**, which is exactly what `B-133` named.

**Disposition: fix the text here, register the architecture there.** AC #5 is restated below and two witnesses are added (**W13** at the two production cells, **W14** the shape asymmetry) on the W5 pattern — asserting the bound and NAMING it as one. The architecture question (an unconditionally admitting head in `TAIL_BASED_PROD` mode with the ratio moved into the tail consumer) is **registered as `B-137`**: it spans every class the tail preserves and multiplies admitted volume by `1/base_rate` at every production cell, and it **merges** with `B-133`'s open F-08 residual, since today's ~20% multi-tenant admission is the ceiling on this arm's added keep-volume and candidate A removes it. **No architecture change at this leg.**

### §0.10 Witness homing across the axis boundary — a correction, recorded as one

`[HIGH]` The witness set was first authored as a SINGLE module at
`harness-od/tests/`. That was wrong, and CI said so before any reviewer did: the
**`axis-isolation — harness-od`** leg syncs **only** `harness-od` + its declared
dependencies (`uv sync --package harness-od` prunes every sibling) and then runs
`harness-od/tests`. Five witnesses drive a REAL `RetryBreakerFallbackDispatcher`
— a `harness_runtime` surface — so collection failed outright with
`ModuleNotFoundError: harness_runtime`. **`harness-od` does not declare
`harness-runtime` and must not**: OD is the consumer-most-downstream axis, and
adding that dependency would invert the axis graph to silence a test.

**The split is the honest homing, not an `e2e`-marker dodge.**

| Half | Home | Why |
|---|---|---|
| **W1–W5** (real dispatch) | `harness-runtime/tests/test_b133_event_aware_tail_floor_real_dispatch.py` | Genuinely runtime-homed — runtime is what composes the tail processor with a real dispatcher in production, and runtime tests already import `harness_od` freely (runtime depends on every axis) |
| **W6–W14** (processor contract) | `harness-od/tests/test_b133_event_aware_tail_floor.py` | Exercise OD surfaces only, with spans built directly through a `TracerProvider` — the OD lane pins the processor's own contract **with no runtime present** |

**W13/W14 stayed in OD deliberately, and that was checked rather than assumed.**
They read the §10.3 envelope and compose `build_default_sampler` +
`TailKeepSpanProcessor` — all OD surfaces — so the production-cell bound needs no
runtime to state it. An AST sweep confirms the OD module's import roots are
exactly `{harness_core, harness_od, opentelemetry, pytest, typing}`.

**An unrelated defect the split introduced and the recount caught.** Both
`tests/` directories are packages (`__init__.py`), so two modules sharing a
basename resolve to the same importable `tests.<name>`: the first-imported file
won and pytest attributed **its** 30 cases to **both** paths — 60 collected where
35 exist, with the runtime file's own five witnesses never running. The joint
collect listing `harness-runtime/tests/…::test_w12_…`, a witness that exists only
in the OD module, is what exposed it. Repo-wide basename uniqueness holds across
all **515** test modules; the `_real_dispatch` suffix restores it, and the
recount returns **30 + 5 = 35**, the pre-split total exactly.

**Verified BOTH ways, by execution.** (i) The isolation lane was simulated
in-process with `harness_runtime` made unimportable via a meta-path finder:
**1156 passed** on `harness-od/tests`. (ii) That probe is load-bearing — replayed
against the pre-split module it reproduces the CI failure exactly
(`ERROR harness-od/tests/test_b133_event_aware_tail_floor.py`, collection
interrupted). (iii) Zero `harness_runtime` imports remain anywhere under
`harness-od/tests` (AST-verified, not grep-verified).

**No witness changed.** All fourteen are preserved verbatim modulo imports,
fixtures and module docstrings; every name is unchanged, and the PD-8 red-sets
below now span the two modules and say so.

### §0.11 The merge gate's BLOCK — a measured witness gap, and the two witnesses that close it

`[HIGH]` The decorrelated 3-lens merge gate on PR #1276 returned lens-1 APPROVE, lens-2 APPROVE (one Class-3 arithmetic nit), **lens-3 BLOCK** — and the BLOCK was a real, measured hole in this unit's own witness set, not a style objection.

**The mutation.** Reduce `_carries_always_sampled_event` to `is_always_sampled(events[0].name, events[0].attributes)` — scan only the FIRST event. **It passed all 65 cases then in the suite** while reinstating `B-133` outright.

**Why every witness missed it.** Each one happened to put a §9.2 member FIRST among its carrier's events, so nothing constrained the scan position. That is the "presence-not-correctness" shape this plan already caught once at §0.7 — and it recurred, at a different surface, which is the honest thing to record.

**The shape is PRODUCTION-REACHABLE, and it was reproduced end-to-end rather than argued.** When a candidate's breaker is already OPEN with an unexpired cooldown, `retry_breaker_fallback` sets `skip_reason = "breaker-open"`, emits the NON-member `retry.skipped` on the **outer** span, and advances the chain; at exhaustion it emits `fallback.exhausted` on that **same** span. A dispatch with both candidates pre-opened produces, measured:

```
['retry.skipped', 'retry.skipped', 'fallback.exhausted', 'exception']
```

— member THIRD. Under the mutant that carrier exports nothing.

**Two witnesses close it, and at least one exercises the real ordering.** **W16** (runtime-homed) drives exactly that dispatch — both breakers pre-opened, an injected clock so the cooldown never elapses, and an assertion that **no provider call occurred**, so the shape cannot silently drift onto a retry path. **W15** (OD-homed, four parametrized orderings) pins the same contract on the processor alone with no runtime present, and generalizes across the non-member vocabulary (`retry.skipped`, `tool_retry.exhausted`, `gen_ai.eval.alignment_floor.drift_detected`, `exception`); each case first ASSERTS its leading events really are non-members, so a future roster change cannot make it vacuous. **PD-8 probe (vii)** is the mutation itself: **5 failed / 65 passed** — W15(×4) + W16, and nothing else.

**Two fold-ins from the same gate.** Lens-2's Class-3 nit: probe (ii)'s recorded "27 failed / 5 passed" did not sum to its roster and predated W13/W14 — **every** probe figure has been re-measured (AC #9) and §0.7 now says so. Lens-1's two accuracy nits are applied at the helper docstring: the claim that the scan "never runs on an always-sampled span" is **false** for the non-root succeeded `subagent.span` the name arm holds back — corrected in the DOCSTRING, not by moving the arm, since lens-2 adjudicated the placement as contracted by §9.2.1 term 1 — and the cost note now states what `span.events` actually costs (a lock, a deque copy and a tuple build per access, read once and bound here) instead of "a single truthiness test".

**Roster: 14 → 16 witnesses, 35 → 40 cases** (OD 30 → 34, runtime 5 → 6).

---

## §1 U-OD-59 — the §9.2.1 event-aware always-sampled arm at the tail-keep consumer

**Implements:** C-OD-09 §9.2.1 terms 1–5 (NEW at OD spec v1.38 §1) — the event-aware realization of the §9.2 floor at the tail consumer, plus the declared HEAD bound.

**Depends on:** [**U-OD-11**, **U-OD-58**]. U-OD-11 owns `harness-od/src/harness_od/sampling_mode.py` and declares `is_always_sampled` — the SSOT term 1 requires both resolutions to share (verified by direct read: the module docstring line 1 names U-OD-11). U-OD-58 landed §9.2's nineteenth row `fallback.exhausted`, one of the three event-shaped members this arm exists to deliver, so the arm's member coverage is only complete atop it.

**Consumed by (cross-axis):** **NONE.** `tail_keep_span_processor.py` is OD-owned; it is constructed at `harness-runtime/.../lifecycle/span_processor.py` through its **existing, unchanged** constructor signature. This unit adds no parameter, no exported symbol and no import outside `harness_od.*`, so no new cross-package consumption is introduced and no CXA row is owed.

**Files affected (logical):**

- `harness-od/src/harness_od/tail_keep_span_processor.py` — a module-level `_carries_always_sampled_event` helper (~8 functional lines) + the event-aware arm in `on_end` (~6 functional lines) + the module-docstring section recording the mechanism, the empirical grounding and the declared head bound.
- `harness-od/tests/test_b133_event_aware_tail_floor.py` — **NEW**, the OD-only witnesses **W6–W15** (34 cases under parametrization) + the PD-8 probe table. **`harness_runtime`-FREE by rule** (§0.10).
- `harness-runtime/tests/test_b133_event_aware_tail_floor_real_dispatch.py` — **NEW**, the REAL-dispatch witnesses **W1–W5 + W16** (6 cases). Cross-axis-homed deliberately (§0.10); the `_real_dispatch` suffix keeps repo-wide test-basename uniqueness, which both `tests/` packages structurally require.
- `harness-od/src/harness_od/composite_sampler.py` — **NOT EDITED, deliberately.** The head consumer is the declared bound (term 4); editing it would be the venue-(b) extension this arc has no authority for. AC #5 asserts the bound by execution instead.
- `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` + `harness-od/src/harness_od/harness_breaker_schema.py` — **NOT EDITED.** The three emission sites are byte-unchanged; AC #8 asserts this by absence.

**Scale:** ~14 functional `src` lines in one module; the remainder is the witness set and the docstring record. **No `src` line changed at the codex round-1 absorption** — that round moved contract TEXT and added two witnesses; the arm itself was found correct for what it can see.

**Thread / async posture.** `on_end` is called by the OTel SDK on whichever thread ends the span, and `TailKeepSpanProcessor` carries **no lock today** (plain `dict` buffers). The arm matches that posture exactly — it is a pure read over `span.events` followed by the same `self._downstream.on_end(...)` call and the same `self._keep` / `self._materialize_trace_decision` bookkeeping the existing arms already perform. **No lock is added, no `async` is introduced, and no new shared mutable state is created**, so the module's concurrency profile is unchanged. *(Verified by direct read rather than assumed: the module contains no `Lock`, no `async def`, and no `threading` import.)*

### §1.1 Acceptance criteria — by EXECUTION

1. **The positive control is run FIRST, end-to-end, and its result is recorded before any repair is written.** A REAL `RetryBreakerFallbackDispatcher.dispatch` driven to exhaustion through a `TracerProvider` wired with the REAL `HarnessCompositeSampler` **and** the REAL `TailKeepSpanProcessor`, at both `base_rate=0.0` (head half) and `base_rate=1.0` + tail processor (tail half), covering **all three** event-shaped members via real dispatch shapes — chain exhaustion (`fallback.exhausted`), capability-shortfall exhaustion (`fallback.triggered`), charging-fault exhaustion at `fail_threshold=1` (`breaker.tripped`). **`B-133` closes on the RESULT, not on the expectation**: had the run shown survival, the row would close with that finding and no repair. *(Executed; result at OD spec v1.38 §0.1 — zero spans at both consumers for all three members.)*
2. **Term 1 — the tail consumer resolves BOTH shapes through the SAME SSOT.** After the span-name resolution fails, the span's event names resolve against `is_always_sampled`, with **event attributes passed through**. Asserted structurally rather than by inspection: the witness set is parametrized over `ALWAYS_SAMPLED_EVENT_CLASSES` **itself**, so every current and future roster member is covered the moment it lands — the parametrize-literal drift gap v2.32 §0.7 found at the name arm is closed here by construction rather than by a hand-maintained list. Wildcard rows are exercised at a concrete descendant name, as the SDK boundary sees them. Witness: **W11**.
3. **Terms 1–2 — all three event-shaped members survive the tail, through the REAL processor chain.** Each driven by its own REAL dispatch shape and asserted **without `force_flush`**, so survival is attributable to the arm and not to the drain path's keep-all. Witnesses: **W2** (`fallback.exhausted`), **W3** (`fallback.triggered`), **W4** (`breaker.tripped`).
4. **The counterfactual is asserted, not described.** The carrier span fails **both** name-shaped predicates (`is_always_sampled(span.name, span.attributes)` and `is_classification_trigger(span)` are both `False`) while carrying the always-sampled event — so if either ever became `True` by name, the arm would be redundant and this witness would go red. Paired with a **live control**: a carrier whose events are all non-members is still dropped. Witness: **W1**.
5. **Term 4 — the HEAD bound is pinned honestly, named as a bound, and pinned WHERE IT ACTUALLY BITES.** Three witnesses, because one was not enough and the shortfall was found by out-of-family review rather than by this plan. **(a)** The head sampler at `base_rate=0.0` still drops the event carrier, paired with the discriminator that a span **NAMED** `fallback.exhausted` survives the SAME sampler — which makes *event-shaped, not name-shaped* the operative cause rather than an inference (**W5**). **(b)** At the two REAL production `TAIL_BASED_PROD` cells, resolved from `PER_CELL_BASE_RATE_ENVELOPE` rather than hard-coded, most event carriers **never reach `on_end` at all** — and, in the same witness, **every carrier that does reach it is exported**, so the residual is attributed to *admission* and not to *classification* (**W13**, parametrized over `team-binding × self-hosted-server` and `multi-tenant-compliance × managed-cloud`; it also asserts the cell really is `TAIL_BASED_PROD` at a sub-1.0 rate, so an envelope or mode-map move turns it red instead of letting it assert nothing). **(c)** At that SAME cell and rate, a §9.2 member realized as a **root span name** is admitted at 100% — the shape asymmetry, without which W13 would read as "sampling drops things", which is not a finding (**W14**). *A green witness in this group asserts the bound EXISTS; none of them is a repair and none may be read as one.*
6. **Terms 3 + 5 — bookkeeping.** (a) An event-matching span that is ALSO a §10.2 classification trigger sets the per-trace keep flag and its buffered siblings are preserved — asserted by export **ORDER**, per §0.7, because membership alone does not discriminate the arm (**W6**). (b) An event-carried `breaker.tripped` forwards its own carrier but does **NOT** flag its trace — the `B-123` boundary, pinned so widening it is deliberate and test-visible (**W7**). (c) An event-matching ROOT close materializes its trace decision, leaving `buffered_trace_count == 0` — the `B-136` leak is NOT extended to the dispatch path (**W10**, and the same assertion carried on W2/W4/W7).
7. **Conservative-absent survives the new arm, and non-matching spans are untouched.** A `files.operation` event with **no** `kind` forwards (never under-sample the §9.3 floor); with a mutation `kind` forwards; with a non-mutation `kind` does **not** (**W8**, parametrized three ways). A span carrying only non-member events still buffers, still takes the §10.2 decision, and leaves `dropped_span_count` / `dropped_trace_count` exactly as before (**W9**). The name arm's own spans forward without any event scan (**W12**) — the cost posture, pinned as discretion per §0.8, not as contract.
8. **Zero emission-site changes, zero head-sampler edit, zero CP delta, zero CXA rows.** Assert by absence: `harness-runtime/.../lifecycle/retry_breaker_fallback.py`, `harness-od/src/harness_od/harness_breaker_schema.py`, `harness-od/src/harness_od/composite_sampler.py` and every `harness-cp/` file are **untouched** in this arc's diff. *This unit widens a consumer's classification; if the diff reaches an emission site or the head sampler, the scope claim is false.*
9. **PD-8 — the arm is load-bearing, demonstrated by mutation.** Five probes, each applied, observed, restored, re-verified green. **Restoration is by file copy from a pre-probe backup, never `git checkout`** — the working tree carries uncommitted arc content a checkout would destroy.

| # | Mutation | Measured — scope for EVERY figure: both witness modules + `test_tail_keep_span_processor.py`, **70** baseline |
|---|---|---|
| i | Delete the event-aware arm from `on_end` | equivalent to (ii) by construction |
| ii | `_carries_always_sampled_event` returns `False` (name-check-only) | **34 failed / 36 passed** — W2, W3, W4, W6, W7, W8(×2), W10, W11(×19), W13(×2), W15(×4), W16 |
| iii | Move the event arm ABOVE the name arm | **0 failed / 70 passed** — the honest reading is at §0.8 |
| iv | Drop the root-close `_materialize_trace_decision` | **5 failed / 65 passed** — W2, W4, W6, W7, W10 |
| v | Drop `event.attributes` from the lookup | **1 failed / 69 passed** — W8's non-mutation case |
| vi | Head sampler made unconditionally admitting (a `B-137` candidate-A sketch) | **4 failed / 66 passed** — EXACTLY the bound witnesses W5, W13(×2), W14 |
| vii | **First-event-only scan** — the merge gate's BLOCK (§0.11) | **5 failed / 65 passed** — W15(×4), W16 |

10. **The full OD suite and the runtime breaker / sampling-adjacent suites pass unmodified — AND the OD suite passes with `harness_runtime` UNIMPORTABLE.** The second half is the `axis-isolation — harness-od` contract (§0.10) and is asserted by execution, not by inspection: the lane was simulated in-process with a meta-path finder refusing `harness_runtime`, returning **1156 passed**, and the same probe replayed against the pre-split module reproduces the CI collection failure — so a future witness that reaches for a runtime surface from `harness-od/tests` fails there rather than at CI. `harness-od/tests/` in full, plus `harness-runtime/tests/test_lifecycle_retry_breaker_fallback.py`, `test_lifecycle_span_processor.py` and `test_lifecycle_tracer_provider.py` — the three modules that construct or exercise the amended consumer. **Zero edits to any pre-existing test module**: the arm only ever ADDS keeps, so a pre-existing drop assertion that broke would mean the arm over-forwards.

### §1.2 What this unit does NOT own

- **The HEAD half of the floor.** Declared bound per OD spec v1.38 §9.2.1 term 4, asserted at AC #5, **not repaired**. Closing it requires giving the three members a span shape at emission — a NEW primitive routing through workspace `CLAUDE.md` §4.3 back-flow per X-AL-3. *Stated so a green W5 is not misread as a discharge.*
- **The §10.2 tail-keep trigger half** (`B-123`). This leg's positive control **answers** its step-(1) probe — an event-carried `breaker.tripped` does not flag its trace — and the finding is recorded as a cross-reference at OD spec v1.38 §0.1 and pinned by W7. **`B-123` is NOT closed here**; it owns its own disposition, and term 3 declines to widen `is_classification_trigger` deliberately.
- **The `B-136` name-arm buffer leak.** Pre-existing, surfaced by this leg's probe (§0.6), registered rather than repaired — fixing it would change shipped behaviour for name-shaped always-sampled roots, outside this arc's authority. This unit owes only that its own arm does not extend it (AC #6c).
- **The `B-124` inert `validator.fail.permanence` row and the `B-125` `harness.breaker.tool_id` homonym.** Same family, neither a precondition, neither repaired.
- **The F-08 per-tenant keep-volume measurement.** `B-133` close-out step (3), sequenced after realization and **still OPEN**. This unit makes the measurement meaningful for the first time and deliberately does not make it; **no acceptance criterion depends on a volume figure**, and none is asserted. Carried as a named residual on the closed `B-133` row per the `B-104` precedent.

---

## §2 Coverage matrix delta (v2.32 → v2.33)

| Contract surface | Units covering (delta) |
|---|---|
| C-OD-09 §9.2.1 terms 1–5 (NEW at OD spec v1.38 — the `B-133` event-aware tail arm + the declared HEAD bound) | **U-OD-59 (NEW)** |

DAG: U-OD-59 added as a new node; in-degree per its `Depends on` (**U-OD-11**, **U-OD-58**) — **two new intra-axis edges, U-OD-11 → U-OD-59 and U-OD-58 → U-OD-59**; no existing edge removed or rewired; **no cross-axis edge**.

---

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_33.md` (delta over v2.32) |
| Authored at | Phase 7 — the `B-133` realization leg (2026-08-08) |
| Authoring authority | `Spec_Operational_Discipline_v1_38.md` §1 (the subsection this unit realizes); forward-register row `B-133` close-out steps (1) + (2) |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_32.md` (v2.32 — the `B-116-t3` leg) |
| Siblings (same arc) | `Spec_Operational_Discipline_v1_38.md` — filed in the SAME PR, together with the implementation, per the #1272 precedent |
| Unit-count change | **+1** (NEW U-OD-59) |
| Cluster-count change | None |
| DAG topology change | One new node (U-OD-59); two new intra-axis edges (U-OD-11 → U-OD-59; U-OD-58 → U-OD-59); **zero cross-axis edges** |
| Cross-axis cascade | **NONE** — verified, not assumed: the amended consumer is OD-owned, gains no import outside `harness_od.*`, and its constructor signature is unchanged, so the runtime construction site is byte-unchanged. CXA aggregate stays frozen at 111 |
| Empirical grounding | The `B-133` positive control (AC #1), run end-to-end BEFORE the repair: zero spans exported at both consumers for all three event-shaped members. Two further probes recorded: the falsified head-cell hypothesis (§0.5) and the pre-existing name-arm buffer leak (§0.6) |
| Register consequence | **`B-133` CLOSES at this leg** (steps 1 + 2 executed; step 3 carried as a named OPEN residual on the closed row). **`B-136` newly registered.** `B-123` gains a cross-reference clause recording this leg's probe finding and is **NOT** closed |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
