# Phase 7d Retirement Events — Batch 37

| Field | Value |
|---|---|
| Batch number | 37 |
| Filed at | 2026-05-28 (post-batch-36 OD-3 RETIRE-READY arc; gate-text-stale-vs-production-landings audit of OD-1 row) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 + workflow v1.12 §7.4.7.3.C retirement-tier-transit audit-template applied at `harness-od/CLAUDE.md` §4.1 OD-1 row |
| Predecessor batch | `phase-7d-retirement-events-batch-36.md` (2026-05-28 — H_T-OD-3 PARTIAL → RETIRE-READY via OD spec v1.27 + materializer wrap) |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → RETIRED transit (H_T-OD-1) via doc-hygiene reclassification. Cumulative RETIRED count increments 37/54 → 38/54 (70.4%); STILL-BOUNDED count decrements 10/54 → 9/54 (16.7%); RETIRE-READY + PARTIAL + STILL-BOUNDED-INDEFINITELY counts unchanged. Pipeline-advanced 42/54 → 43/54 = 79.6% (+1.8 percentage points). Cardinality check: 38 + 2 + 3 + 9 + 2 = 54 ✓.**

This batch records the **STILL-BOUNDED → RETIRED transit** for H_T-OD-1 (deferral envelope) via **gate-text-stale-vs-production-landings audit** per workflow v1.12 §7.4.7.2 sub-species 10. The pre-batch-37 gate text at `harness-od/CLAUDE.md` §4.1 row 141 + §4.1 STILL-BOUNDED → PARTIAL gates row 178 framed retirement as gated on "runtime composer importing `deferral_envelope` + scope-deferral typed primitive replacing `CLAUDE.md`-prose convention at runtime." Empirical audit performed this session against the OD spec v1.2 C-OD-03 §3 contract + production grep across all axis source trees discriminates:

| Check | Finding | Authority |
|---|---|---|
| 1. OD spec C-OD-03 §3 contract surface | **Static deferral-signature declaration.** §3.1 12 committed surfaces; §3.2 5 deferred-surface categories; §3.3 boundary invariants enforced at static layer (frozen Pydantic + cardinality pins). "Specific selection-validation mechanism (static schema vs. runtime probe vs. compile-time emission)" explicitly **deferred to implementer discretion** at line 263. NO mandate for a runtime enforcement loop. | OD spec v1.2 §3 line 213–264 |
| 2. U-OD-03 plan acceptance criteria | Substrate `deferral_envelope.py` at `harness-od/src/harness_od/deferral_envelope.py` IS the contract realization — 6-entry `COMMITTED_AT_D6_SURFACES` per acc #2 + 23-entry `DEFERRED_SURFACES` per acc #5 strict-coverage reading + §3.3 boundary-invariant `assert` at module load (lines 312–319). **No runtime consumer site cited at U-OD-03 acceptance criteria.** | `Implementation_Plan_Operational_Discipline_v2_1.md` §3.1.3 U-OD-03 |
| 3. CLAUDE.md-prose scope-deferral convention grep | **Zero hits** for "scope deferrals CLAUDE.md-prose convention" or equivalent across `harness-{runtime,cp,as,od,core}/` at HEAD. The two adjacent grep hits (`harness-runtime/.../config/loader.py:14` C-RT-03 surfaces; `harness-as/.../sandbox_tier_composition.py:19-32` AS sandbox-tier composition) reference different contracts (C-RT-03 + AS internal), not C-OD-03 deferral-envelope. **No prose convention exists to "replace"** — the gate text references a phantom convention. | empirical grep this session |
| 4. H_E substitution surface | **Categorical mismatch — never engaged.** Per Phase 7 Meta-Architecture §5.5 OD-axis row 1: H_T-OD-1 substitution mechanism = `ToolSearch` (categorical mismatch). H_E's `ToolSearch` is a code search primitive; the H_T deferral envelope is a typed declaration of design-time-vs-deployment-binding-time surface commitments. The two are categorically unrelated; H_E surface was never standing in for the H_T primitive. No substitution invocation site to retire. | Meta-Architecture §5.5 row 1 |

**Discriminator outcome:** Spec is pure design-time AND no prose convention exists AND H_E surface is categorical-mismatch (never engaged). The OD-1 gate text was structurally stale-vs-spec — framing a runtime composer as close criterion that the spec doesn't authorize. Authoring a runtime enforcement loop on the 23 `DEFERRED_SURFACES` would be **X-AL-3 silent extension** under cover of gate-text framing.

**Disposition: STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY** (mirror H_T-OD-8 v1 §1 authoring-close pattern). The substrate `deferral_envelope.py` IS the C-OD-03 contract realization at U-OD-03 landing; §3.3 boundary invariants enforced at static layer; no runtime enforcement gate mandated by spec; H_E substitution never engaged. Per X-AL-2 retirement criterion: (cited unit IDs landed: U-OD-03 at design-time) ∧ (substituted H_E surface no longer invoked at substitution site: vacuously true — never invoked).

Operator-ratified routing (α) at AskUserQuestion 2026-05-28 over (β) STILL-BOUNDED-INDEFINITELY + (γ) Class 1 fork + (δ) X-AL-3 build.

---

## §1 Criterion verification

- **Criterion A** (cited unit IDs landed). MET. U-OD-03 substrate at `harness-od/src/harness_od/deferral_envelope.py` carries the 6-entry `COMMITTED_AT_D6_SURFACES` per plan acc #2 + 23-entry `DEFERRED_SURFACES` per plan acc #5 + §3.3 boundary-invariant assert at module load. Tests at `harness-od/tests/test_deferral_envelope.py` verify acc #1 through acc #7.

- **Criterion B** (substituted H_E surface no longer invoked at substitution site). MET vacuously. H_E surface = `ToolSearch` (categorical mismatch per Meta-Architecture §5.5 row 1); never engaged as a substitution invocation site for the H_T primitive. Production grep at HEAD: zero invocations of `ToolSearch` at any axis source tree as a deferral-envelope substitute (the categorical mismatch precludes such invocations from ever having existed).

**No further in-CLI close pathway** — retirement is structural at authoring close; substrate-IS-the-contract pattern mirror to H_T-OD-8 (aggregate manifest + Stage 3b inversion authoring-only RETIRED at v1 §1).

---

## §2 Sub-row substitution-status table

Pre-batch-37 OD-axis bucket (post-batch-36):

| Substitution | Status | Source |
|---|---|---|
| H_T-OD-1 (deferral envelope) | **STILL-BOUNDED → RETIRED at this batch (batch-37)** | Substrate at `deferral_envelope.py` IS contract realization; H_E ToolSearch categorical-mismatch never engaged; per workflow v1.12 §7.4.7.2 sub-species 10 audit |
| H_T-OD-2 (OTel SDK base + GenAI semconv) | RETIRED batch-2 (2026-05-20) | LIVE at `lifecycle/llm_dispatch.py` |
| H_T-OD-3 (Composite Sampler) | RETIRE-READY (batch-36) | gate (a) + gate (b) closed; deployment-time-opt-in-gate terminal |
| H_T-OD-4 (Pre-Collector redaction SpanProcessor) | PARTIAL (refined) | gate (a) §13.1 partially closed at PR #25; per-session toggle + gate (b) §13.2 deferred |
| H_T-OD-5 (Cost-attribution 5-step chain) | RETIRED batch-32 (2026-05-28) | mech-β AC #8 green on main |
| H_T-OD-6 (Local-first OTLP ingestion) | RETIRE-READY (batch-33) | 4-OD-B cluster landed; deployment-time-opt-in-gate terminal |
| H_T-OD-7 (Preservation invariants 5-dimension) | STILL-BOUNDED | Library carrier only; no runtime enforcement loop |
| H_T-OD-8 (aggregate manifest + Stage 3b inversion) | RETIRED (v1 §1 authoring-only) | Authoring-close |

Post-batch-37 OD-axis bucket: **4 RETIRED + 2 RETIRE-READY + 1 PARTIAL + 1 STILL-BOUNDED + 0 STILL-BOUNDED-INDEFINITELY = 8**.

Workspace-layer cumulative post-batch-37: **38/54 RETIRED (70.4%) + 2/54 RETIRE-READY (3.7%) + 3/54 PARTIAL (5.6%) + 9/54 STILL-BOUNDED (16.7%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)**. Pipeline-advanced (R+RR+P): **43/54 = 79.6%** (+1.8 percentage points from batch-36; out-of-pipeline → RETIRED tier promotion).

OD-axis pipeline-advanced: **7/8 = 87.5%** (was 6/8 = 75.0% at batch-36). Only H_T-OD-7 remains at STILL-BOUNDED.

**Workspace crosses 70% RETIRED threshold at batch-37** (38/54 = 70.4%; was 37/54 = 68.5% at batch-36).

---

## §3 Adjacent observations

(a) **FIRST sub-species 10 closure in retirement ledger.** Sub-species 10 `gate-text-stale-vs-production-landings` was catalogued at workflow v1.12 §7.4.7.2 publication 2026-05-28 (this session). H_T-OD-1 disposition at batch-37 is the **first empirical closure event** under sub-species 10 — the gate text was empirically falsified against C-OD-03 spec authority + production-grep verification; reclassification is doc-hygiene scope, not substantive retirement. Workflow v1.12 §7.4.7.3.C audit-template directly enabled the closure — pre-substantive empirical verification at advisor pre-arc consultation surfaced the discriminator (Check 1 spec-reads-pure-design-time + Check 2 zero-hits-grep) BEFORE any X-AL-3 silent extension code was authored.

(b) **Mirror precedent: H_T-OD-8 RETIRED-as-authoring-only.** OD-8 retired at v1 §1 (aggregate manifest + Stage 3b inversion = authoring-only artifact; no runtime consumer site). OD-1 disposition at batch-37 mirrors that shape: substrate landed at U-OD-03 authoring time; contract realization complete at substrate construction; no runtime consumer mandated by spec; retirement is authoring-close. **Common ancestor**: H_T primitive whose contract is "the typed declaration itself" rather than "a runtime behavior."

(c) **Distinct from sub-species 7.deployment-time-opt-in-gate.** Sub-species 7 members (AS-8d batch-31 + OD-5 batch-32 + OD-6 batch-33 + OD-3 batch-36) close at RETIRE-READY with operator deployment-time opt-in as the gate to RETIRED. OD-1 at batch-37 closes directly STILL-BOUNDED → RETIRED with no deployment-time gate because the spec doesn't mandate one. Different closure-event-class.

(d) **Substitution-mechanism-categorical-mismatch as RETIRED criterion.** Per Meta-Architecture §5.5 row 1, OD-1 H_E surface is `ToolSearch` ≠ deferral envelope — categorical mismatch noted at design-time. The categorical mismatch means X-AL-2 second conjunct ("substituted H_E surface no longer invoked at substitution site") is **vacuously satisfied**: the H_E surface was never invoked as a substitution because it categorically couldn't have stood in. This is a distinct retirement-criterion satisfaction shape from the substantive-substitution-retired shape (e.g., OD-2 GenAI binding LIVE at production).

(e) **ZERO cross-axis cascade.** Intra-OD-axis doc-hygiene only. NO OD spec / OD plan / CP spec / AS spec / runtime spec / CXA / ADR / ADD / PRD amendment. NO production code change. NO test addition. NO carrier change.

(f) **OD-axis approaches axis-closure ceiling pre-deployment.** Post-batch-37: 4 RETIRED + 2 RETIRE-READY + 1 PARTIAL + 1 STILL-BOUNDED. Only OD-7 remains at STILL-BOUNDED; OD-4 PARTIAL second-gate closure is the other major lever. Path to OD-axis 8/8 pipeline-advanced (100%) is OD-7 substrate arc (mirror this batch's reclassification audit OR substantive substrate arc).

(g) **Empirical validation of advisor pre-substantive consultation discipline.** 31st application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`. Advisor at arc opening flagged X-AL-3 risk + recommended Check 1 + Check 2 verification path BEFORE any code authored. Both checks discriminated cleanly; routing to doc-hygiene scope avoided silent design extension. Same discipline-validation pattern as batch-29 + batch-30 (sub-species 7 operator-discretion ratification closures).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-37.md` |
| Filed at | 2026-05-28 |
| Phase | Phase 7 sub-phase 7d — substitution retirement |
| Predecessor batch | batch-36 (H_T-OD-3 PARTIAL → RETIRE-READY) |
| Co-published artifacts | `harness-od/CLAUDE.md` §4.1 OD-1 row transit + cumulative-counts line refresh + STILL-BOUNDED → PARTIAL gates section refresh + workspace `CLAUDE.md` cumulative-counts cite refresh + memory entries |
| Cross-axis cascade | ZERO (intra-OD-axis doc-hygiene only) |
| Production code change | ZERO |
| Test addition | ZERO |
| Spec / plan amendment | ZERO |
| Advisor application count this arc | 31st — pre-substantive consultation at arc opening flagged X-AL-3 silent extension risk + recommended Check 1 (spec-reads-pure-design-time) + Check 2 (grep-for-prose-convention) verification path; both checks discriminated cleanly to doc-hygiene scope |
