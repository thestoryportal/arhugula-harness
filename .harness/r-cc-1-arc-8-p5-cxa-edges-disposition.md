# R-CC-1 arc #8 — P5 CXA edges (capability item #5): U-CP-12 / U-CP-52 disposition

**Filed:** 2026-06-12 · **Posture:** mode-agnostic (process-substrate; grounds `design-substrate/` + `harness-*/src/` at HEAD `0288f5c` by direct read; authors only this `.harness/` file + the inventory/dashboard). **Authority:** `.harness/capability-completion-inventory-v1.md` item #5 ("GROUND → fork-or-confirm-defer"); `Project_Roadmap_v1.md` §5.17 R-CC-1. **Decorrelation:** advisor (pre-authoring — pushed to pin the U-CP-52 contract rather than resolve it by assertion; that read flipped U-CP-52 from defer to close) + out-of-family Codex (the U-CP-52 close rests on a code-claim; verified against the carrier). **X-AL-3:** ZERO `design-substrate/**` or `harness-*/src` edit — trivially clean.

This is the **last** capability-completion item (#5). With it dispositioned, the R-CC-1 capability frontier is complete (#1–#9 landed; #3/#7 deferred-by-design; #10/#11 ratified-bounded) → **R-CL-Q1 opens**.

---

## 0. The two edges + the disposition in one line

| CXA edge | Carrier(s) | P5 said | This arc (grounded at HEAD) |
|---|---|---|---|
| **U-CP-12 → U-IS-07** | `per_class_attribute_composition.py` | D (deferred) | **CONFIRM-DEFER** — phase-2-runtime convention; declarative-only, no producer-emit moment. No build owed. |
| **U-CP-52 → U-IS-07/11** | `hitl_placement.py` / `hitl_timeout_degradation.py` (CP-side) | D (deferred) | **MATERIALIZED-AT-RUNTIME → CLOSE (D→C)** — the runtime HITL gate composer's 8b-HITL F2-write discharges it. No build owed. |

**Neither is a fork.** Both CP source units are already ratified **NOT-APPLICABLE at the CP-axis** (CP spec v1.25 §16.5.10; the U-RT-35 tension fork `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` **CLOSED 2026-05-29**, batches 46+47). A fork would route to a design-phase CP-side composer that nothing would call — over-excavation against a ratified, closed disposition.

---

## 1. Grounding evidence (HEAD `0288f5c`, direct read)

### 1.1 U-CP-12 → U-IS-07 — declarative-only, no producer

- **Carrier** `harness-cp/src/harness_cp/per_class_attribute_composition.py` (230 lines): enums (`SamplingRate`, `RetrySurfaceKind`) + Pydantic shapes (`PerClassAttributeSet`, `SamplingDisposition`) + two **static tuples** (`PER_CLASS_ATTRIBUTE_SETS`, `SAMPLING_DISPOSITIONS`, C-CP-05 §5.2/§5.4) + one pure helper `required_attributes_for(event_class)`. **Zero** `ledger`/`append`/`emit_`/`EntryPayload`/`StateLedgerEntry` symbols.
- **Consumers:** `multi_agent_span_hierarchy.py` (CP) + `cp_is_wiring.py` (runtime) import the **static data / `SamplingRate` enum** only. `required_attributes_for`/`PER_CLASS_ATTRIBUTE_SETS`/`SAMPLING_DISPOSITIONS` have **zero external call/reference sites** (grep returned nothing outside the carrier).
- **7c audit concurrence** (`.harness/cxa_7c_audit_cp_buckets.md` row 4): "`per_class_attribute_composition.py` imports only `harness_core`/`harness_cp`; `workflow.checkpoint` is a span-name string. No `StateLedgerEntry` import — checkpoint composition is a runtime emission concern." → **phase-2-runtime**.
- **Ratified:** CP spec v1.25 §16.5.10 reclassifies U-CP-12 NOT-APPLICABLE (declarative-only; "no atomic unit owed"; fork doc line 182/244).

**Disposition: CONFIRM-DEFER.** There is no producer-emit moment to wire. The lifecycle checkpoint-span emission (a runtime concern, distinct from a CP-side state-ledger composer) is the materialized path for the event-class taxonomy this module defines. **Re-open trigger:** `per_class_attribute_composition` gains a runtime composer-action moment owing a *distinct* CP-side state-ledger entry — not anticipated; the module is declarative by design.

### 1.2 U-CP-52 → U-IS-07/11 — materialized at the runtime HITL gate composer

The P5 "D — NO composer at HEAD" read the **CP-side** carriers (`hitl_placement.py` `hitl_gate` = `NotImplementedError`; `hitl_timeout_degradation.py` composes no `StateLedgerEntry`) and concluded the seam was unwired. That read is correct *for the CP side* — and is exactly why §16.5.10 reclassified U-CP-52 **runtime-axis-composed**. But the **runtime side** materializes the seam:

- **`harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py`** (`RuntimeHITLGateComposer`, C-RT-18 §14.8, 1167 lines) runs a **4-substep audit-write at step 4h** (§14.8.2):
  - **8a-HITL** compose `CPAuditLedgerEntry` (HITL gate action; handles the **timeout path** — `gate_result is None` → partial entry, lines 715-733).
  - **8b-HITL** F2-write the HITL action via **`self.ledger_writer.append(f2_payload, f2_key)`** (line 790) — `ledger_writer: LedgerWriter` is the **IS state ledger**; `EntryPayload`/`WriteKey` from `harness_is.state_ledger_write`. Action keyed by the HITL **placement** position: `compose_hitl_action_id(parent_action_id, placement.position)` → `f"hitl:{parent_action_id}:{placement.position.value}"`.
  - 8c-HITL CP→OD convert · 8d-HITL `audit_writer.append` (the separate OD audit path).
- **Bound in production:** `stage_5_loop_init.py:329` (`hitl_inference`) + `:417` (`hitl_sub_agent`). Config-reachable — fires whenever a HITL placement is configured (`hitl_placements` non-empty); like the entire HITL feature, it is placement-gated, not always-firing (arc #5's default e2e had `hitl_placements=()`, so it did not fire there — that is config, not a missing producer).
- **8b-HITL F2-write = U-IS-07 (`EntryPayload` shape) + U-IS-11 (append)** to the IS state ledger, recording the HITL **placement** gate action incl. timeout. This **is** the U-CP-52 → U-IS-07/11 seam, materialized at the runtime composer.
- The fork doc (line 183) said this exact site "should author `emit_hitl_gate_state_ledger_entry` at the runtime composer site (C-RT-18 §14.8) — distinct from CP-axis emission discipline." **It has been authored** — inlined as 8b-HITL rather than as a standalone `emit_*` function.

**Disposition: MATERIALIZED-AT-RUNTIME → reclassify D→C** (runtime-delegated, convention-level — CP composes nothing per the ratified NOT-APPLICABLE, the runtime gate composer discharges the F2 state-ledger write). Structurally identical to the P5 §1.2 **C** classification of `U-CP-34 → U-IS-08/09` (discharged inside the IS append, no separate CP producer-emit). **No build owed.**

---

## 2. What genuinely remains residual (separate from these two edges — already dispositioned)

The grounding surfaced that the *honest* HITL residuals are **distinct** from the U-CP-52 → U-IS-07/11 state-ledger edge, and each is already dispositioned elsewhere:

| Residual | Surface | Status | Where dispositioned |
|---|---|---|---|
| HITL **timeout-degradation policy** (`on_hitl_timeout` / `TimeoutDegradationKind`) is producer-gated | `hitl_timeout_degradation.py` / `hitl_placement.py:157` (`on_timeout` registry method) | CONFIRM-DEFER — zero non-test callers (the L8 wall-clock-wait loop that would call it does not exist) | **Item #11 / arc #6** (`class_2_fork_llm_as_router_layer3_contract_shape_vs_defer.md` lane reclassification). NOT the U-CP-52 state-ledger edge. |
| CXA §2.3.2 lists U-CP-52's targets as U-IS-07/11, but the one *genuine* incidental IS coupling is `Identifier` → **U-IS-12** (idempotency-key), which the row omits | `hitl_timeout_degradation.py:31` `import Identifier` | Class 3 CXA doc-fidelity (mis-target) | **R-CL-Q1 doc-hygiene** (7c audit already flagged it — `cxa_7c_audit_cp_buckets.md` lines 84/176; tracking-not-discovering). |
| Runtime spec §12.3 (line 2627) still enumerates U-CP-12 + U-CP-52 as source units (the **Gap C canonical-vs-materialized differential**) | `Spec_Harness_Runtime_v1.md` §12.3 | Class 3 runtime-spec doc-hygiene | **R-CL-Q1 doc-hygiene** (U-RT-35 fork line 346 already routed Gap C "to next runtime-spec revision pass"; tracking-not-discovering). |
| CXA §2.3.2 CP→IS "36 edges" header vs the verbatim table's **38** (CP-unit × IS-target) pairs | CXA §2.3.2 / CP plan §3.6 | Class 3 CXA arithmetic defect | **R-CL-Q1 doc-hygiene** (7c audit lines 88/174; pre-existing, independent of this arc). |

These four are **all Class 3 doc-fidelity**, all already flagged in the 7c audit, and all route to the R-CL-Q1 doc-hygiene pass alongside the §2.3-vs-§2.1 aggregate count + the C-RT-30 §14.19/§30 collision. **No operator gate is owed** — no real build option exists for item #5.

---

## 3. Forward-only correction of the P5 record (reference, don't rewrite)

Per the workspace stale-carry / forward-only discipline, the frozen `.harness/r-cl-p5-cxa-cost-validator-verification.md` §1.2/§5 bodies are **not** rewritten. This arc *sharpens* their re-open framing:

- **P5 §1.2** classified both edges **D** with "Authoring a runtime-layer composer = X-AL-3 per `class_1_tension_u_rt_35...`." That fork **CLOSED 2026-05-29**, and U-CP-12/U-CP-52 were its two **NOT-APPLICABLE exceptions** (§16.5.10), not members of the U-CP-74..79 composer cohort. So the implied re-open trigger ("a CP-side composer lands, same route as U-CP-74..79") never applied to these two.
- The corrected dispositions: **U-CP-12** = phase-2-runtime convention, no producer-emit moment (confirm-defer); **U-CP-52** = materialized at the runtime gate composer (close, D→C). P5 reached the right *outcome* (no build owed at the CP side) for the right CP-side reason; it just did not check the runtime materialization for U-CP-52.

---

## 4. Net

- **Item #5 dispositioned: 1 close (U-CP-52, D→C) + 1 confirm-defer (U-CP-12). No fork. No build owed.**
- **R-CC-1 capability frontier COMPLETE.** #1–#9 landed; #3 (LLM_AS_ROUTER) + #7 (EMBEDDING) deferred-by-design; #10 (cost) + #11 (HITL OQ-6) ratified-bounded; #5 dispositioned here.
- **`next_action` → R-CL-Q1** — DevEx + code-review + simplification, once, on the now-capability-complete harness. The four Class 3 doc-fidelity residuals above fold into its doc-hygiene pass.
