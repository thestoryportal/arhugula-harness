# Remaining Build Audit Report

> **Audit type:** repository-wide spec-to-implementation diff for all remaining arcs/units that need to be built.
> **Posture:** mode-agnostic (process-substrate; reads `design-substrate/`, `harness-*/src/`, `.harness/`; authors only `.harness/audit/`). No `design-substrate/**` or `harness-*/src/**` edits — no X-AL-3 surface touched.
> **Grounded at:** HEAD `46012d5` (2026-06-20). Denominator derived deterministically from the canonical-head spec/plan files + the `tools/semantic_overlay/` overlay; every load-bearing claim re-grounded by direct read (overlay/subagent output is presence-not-correctness).
> **Companion deliverables:** `.harness/audit/Remaining_Build_Register.csv` (48 rows — per-item itemization) + `.harness/audit/Closure_Gate_v1.md` (the binding "fully closed" predicate that consumes this inventory). **§11 records the second-pass hidden-omission refinement (RB-EXP-01, RB-CXA-02/03, RB-GOV-08).**
> **Lifecycle:** this report + register are a **point-in-time snapshot at HEAD `46012d5`**, NOT a maintained parallel source of truth (that would re-create the R-IF-114 drift defect). The **live** authorities are `.harness/arc-ledger.yaml` + `just overlay` (both CI-gated); re-ground against those at each arc-open. Registered in the loop at `Project_Roadmap_v1.md` §5.1 `R-IF-115`.

---

## 1. Executive summary

**This is a near-complete harness, not an early-stage build.** The denominator check is decisive:

- **108 canonical-head contracts** (`C-AS` 16, `C-CP` 30, `C-IS` 11, `C-OD` 19, `C-RT` 32) — **zero are genuinely unimplemented.** The overlay reports 6 `contract_without_code` orphans, but **all 6 are phantoms**: 5 (`C-CP-00`, `C-CP-30`, `C-CP-37`, `C-CP-43`, `C-OD-3`) appear *only in superseded version files* (the design-substrate retains the full delta chain), and `C-IS-11` is an *explicitly documented corrected non-existent cite* (runtime spec L2160: *"prior v1 cited C-IS-11/14/15 which don't exist"*). The genuine specified-but-unimplemented-contract count is **0**.
- **195 canonical-head units; zero genuinely unimplemented.** The symmetric unit diff (head units − units cited in `harness-*/src`) leaves 7 candidates, all resolved as non-gaps: 5 are implemented + tested with the src cite carried on a *contract* (`C-RT-*`) rather than the `U-*` token (U-CP-100→`routing_core_surface.py`, U-RT-82→memory e2e, U-RT-85→validator ×7 tests, U-RT-133→`llm_dispatch.py:547-553`, U-RT-01→package smoke); U-RT-00 is a range-notation boundary marker ("U-RT-00 through U-RT-109"), not a real unit; U-RT-91 is a validator-composer unit defined only in a superseded plan version (parallel to the contract phantoms). The 141 *excess* code-cited units (329 cited > 195 head) confirm code implements the full historical unit set the head delta-plans no longer re-table — so the head count *under*-states what is built.
- **CXA: 31/31 typed seams wired** (the overlay's HARD gate — 0 missing endpoints).
- **Substitutions: 54/54 RETIRED**, and the retirement claim is corroborated — **no `harness-*/src/` path invokes the H_E scaffold MCP** (`harness-7a-scaffold`); the 5 `scaffold` strings in src are benign plan-internal comments.
- All Tier-A Phase-8 closure residuals and nearly all Tier-B forward-activation surfaces are **RESOLVED with live e2e proof** (multi-LLM routing #213/#281/#283; sandbox tiers R-410/411/412; deployment R-420/421/430/440; multi-tenant R-500/R-008; external MCP/Files/managed-agents/memory R-800/810/820/830).

**What "remaining" actually means here.** The genuinely-remaining build surface is well-characterized and concentrated. It is **not** missing axis primitives — it is:

1. **R-FS-1 forward feature arcs** — 14 *registered-forward* (decompose-at-open) + 1 *gated* arc under the single ACTIVE umbrella program `R-FS-1` (operator FULL-SPEC directive 2026-06-12: nothing deferred). These are mostly **runtime + CP** completeness slices (concurrent-fan-out inter-step data, the pause-resume family for the 4 non-`ORCHESTRATOR_WORKERS` topologies, effect-fence refinements, per-step HITL/routing/model folds). One is a new **AS** surface (per-tool idempotency classification), one is **OD** (tail conditional sampling, *gated* on R-420/R-421).
2. **The R-CL quality/close track** — 6 phases **BLOCKED behind R-FS-1** by operator design (run quality ONCE on the complete harness): Q1 DevEx/code-review/simplification, Q2 security, Q3 QA closure, Q4 portable packaging + deployment, D1 documentation suite, C1 closure certification + ship. **These are the largest remaining surface by effort** and are correctly sequenced last.
3. **Bounded-residuals + dormant activations** — CP-16 memory + OD-6 OTLP are RETIRED-AS-BOUNDED-RESIDUAL (built + proven, production-dormant until deployed); layered routing is built + proven but production-inert until a 2nd provider is credentialed.
4. **Two open residual records** — the F1-01 WAL exactly-once duplicate (OPEN, low-severity, tracked, fix-shape ready) and one **likely-stale OPEN fork** (engine-durable-resume; its own re-open trigger has since fired and been built).
5. **Hidden / governance gaps** the trackers don't frame as build arcs — per-package READMEs (all 7 missing), 14 code-without-cite traceability orphans, the overlay's superseded-version phantom-scoping, scaffold MCP dev-tooling residue, and one stale-ACTIVE roadmap entry (R-IF-114).
6. **Proposed / undecomposed surfaces** — dashboard iteration-2, the Surface-X research register, and ICM methodology adoption (audit-only).

**Bottom line for planning:** there is no hidden mass of unbuilt axis code. The remaining program is (a) ~15 bounded runtime/CP completeness arcs, (b) a deliberately-deferred 6-phase quality/close/ship track, and (c) a thin layer of doc/traceability/tooling hygiene. The single highest-value *audit* finding is that the overlay's "6 unimplemented contracts" reading is **false** (all phantoms) — a future audit must scope the overlay to canonical heads or repeat this misread.

---

## 2. Audit coverage

| Surface | Covered | Method |
|---|---|---|
| `design-substrate/**` (247 .md; ADRs, ADD, PRD, per-axis specs/plans, runtime, CXA, workflow) | ✅ | Canonical-head identification + contract/unit denominator extraction (Python regex over heads) |
| `harness-core/is/as/cp/od/cxa/runtime` (`src` + `tests`) | ✅ | Overlay `code_without_cite` + module/test counts + targeted reads |
| Overlay (`tools/semantic_overlay/`) | ✅ | `just overlay` + `just overlay-query --orphans` (contract/code/CXA/substitution orphan classes) |
| `.harness/` trackers (arc-ledger, spine ledger, forward register, capability inventory, roadmap dashboard) | ✅ | Direct read |
| `.harness/class_*_fork_*.md` / `class_*_tension_*.md` (~163 docs) | ✅ | Subagent triage (verbatim status lines) + re-grounding of the load-bearing OPEN one |
| `Project_Roadmap_v1.md` §5 R-NNN catalog (89 yaml entries) | ✅ | Python status extraction |
| Substitutions (`.harness/substitutions.yaml`, 54 rows) | ✅ | Scaffold-invocation grep cross-check + bounded-residual triage |
| MCP/server boundary (`.mcp.json`, `scaffolding/mcp/`, runtime `mcp_*`) | ✅ | Direct inspection |
| Governance/docs/examples/tests/config (`README`, `examples/`, `deploy/`, `tests/`, `harness.toml.example`) | ✅ | Structure scan |

**Out of scope by hard rule:** editing `design-substrate/**` or `harness-*/src/**` (X-AL-3); deciding operator-gated scope (FULL-SPEC vs ratify-residual) — surfaced, not decided.

---

## 3. Method

Per the advisor steer, the audit works **from the canonical denominator, not from the trackers**. The trackers (arc-ledger, spine ledger, forward register) are the workspace's *claim* about remaining work; the audit checks that claim against the canonical contract/unit keyspace and reports what it misses.

1. **Denominator extraction.** Identified the canonical-head spec/plan files (the design-substrate is a delta chain that retains every version): CP spec `v1_43`, OD spec `v1_30`, runtime spec `v1` (living, internal v1.65), IS spec `v1`, AS spec `v1`; plans CP `v2_37`, OD `v2_28`, runtime `v2_48`, IS `v2_6`, AS `v1_4`, core `v1_2`; CXA `v2_20`. Extracted all `C-*` and `U-*` IDs from heads only → 108 contracts, 195 units.
2. **Deterministic orphan check.** `just overlay-query --orphans` → `contract_without_code` (6), `code_without_cite` (14), `cxa_seam_missing_endpoint` (0, HARD), `substitution_without_carrier` (44, advisory).
3. **Per-orphan resolution (contracts).** Each `contract_without_code` orphan checked for presence in any canonical head → 5 absent (superseded-only phantoms), 1 a documented corrected non-cite. Net real gap: 0.
3b. **Symmetric unit diff (the "implied-missing units" check).** Intersected the 195 head units with the unit IDs cited across `harness-*/src` (329 distinct) → 7 head units not cited in src; each re-grounded (src + tests + plan): 5 implemented + tested under a contract-cite, U-RT-00 a range-marker non-unit, U-RT-91 a superseded-version validator unit. Net real gap: 0. (The 141 excess code-cited units confirm the head delta-plans under-count the built set.)
4. **Substitution cross-check (task item 7).** Grepped `harness-*/src/` for `harness-7a-scaffold` and `scaffold` → no production invocation of the H_E scaffold MCP. Retirement claim corroborated.
5. **Fork-doc triage.** Subagent scanned ~163 `class_*` docs for genuinely-OPEN status lines (verbatim); the one OPEN result re-grounded by direct read.
6. **Tracker enumeration.** Arc-ledger (frozen/standalone/registered/gated), forward register Tier A/B, roadmap §5 R-NNN catalog (status histogram), capability-completion inventory — read for the tracked-remaining set.
7. **Lifecycle completeness.** For accounted-for axes, noted impl + test + doc presence; impl-without-doc (READMEs) and impl-without-cite (traceability) recorded as findings even where code exists.

---

## 4. Missing units by domain

> **Framing:** there are **no fully-missing canonical-head units or contracts**. "Missing" below means *registered-forward / partial / unwired / gated / dormant* per the user's taxonomy. Full per-item detail (canonical source, evidence, dependency, proposed artifact, action) is in `Remaining_Build_Register.csv`; this section is the narrative grouping.

### 4.1 harness-runtime (largest forward surface)
The 7th package (136 src modules, 170 test files) absent from the original axis list; it owns most forward arcs.
- **RB-RT-01 B-INTERSTEP-NONLINEAR** — concurrent-fan-out inter-step output recording (B-INTERSTEP shipped sequential-write only).
- **RB-RT-02/03 effect-fence refinements** — §22.1 operator-resolvable PAUSE (interim is fail-closed FAILED); auto-activate under durable engines.
- **RB-RT-04 B-EDIT-CARRIER-DURABLE-ASYNC-RESUME** — functional EDIT on the durable-async resume path (wrap-time SYNC only today).
- **RB-RT-05 B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION** — accurate `routing.layer` on the inner gen_ai span (observability fidelity; production-dormant).
- **RB-RT-06 F1-01 WAL exactly-once** — a same-`run_id` re-drive of a completed WAL run double-emits `cp.resume-attempted`; OPEN/low-severity/fix-shape-ready.

### 4.2 harness-cp (+ runtime)
- **RB-CP-01 B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT** — extend output-carrying replay beyond LINEAR EVENT_SOURCED_REPLAY.
- **RB-CP-02..05 pause-resume family** — EVALUATOR_OPTIMIZER, PARALLELIZATION, DECENTRALIZED_HANDOFF, HIERARCHICAL_DELEGATION `cascade_policy=pause` (only ORCHESTRATOR_WORKERS materialized; the others fail honestly with `*-pause-resume-not-yet-materialized`).
- **RB-CP-06 B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD** — per-step `StepOverride.hitl_placement` fold (design-fork-first; semantics unspecified).
- **RB-CP-07 B-HITL-WRAP-FAIL-CLASS-SURFACING** — precise RT-FAIL surface (CP can't import runtime exception types).
- **RB-CP-08 B-ROUTING-MANIFEST-MODEL-FOLD** — smart-fold per-step model override with routing_activation (needs a `StepEffectiveBinding` source discriminator).
- **RB-CP-09 / RB-CP-10 minor** — richer `pause_context_reader` body (operator WON'T-FIX 2026-05-24, but FULL-SPEC arguably re-opens); U-CP-22 anchor-validation + per-step gate-level surfacing.

### 4.3 harness-as (+ runtime)
- **RB-AS-01 B-EFFECT-FENCE-PER-TOOL** — a *new* `ToolContract` idempotency classification (the only genuinely-new cross-axis surface in the forward set; design-fork-first).
- **RB-AS-02 skills cost estimate** — description-length proxy, not token-counting (§14.17.7); confirmed at HEAD.

### 4.4 harness-od (+ runtime)
- **RB-OD-01 B-TAIL-CONDITIONAL-SAMPLING** — **GATED** on R-420/R-421; non-root/tail conditional sampling per §9.2 (B7 delivered the root half; the sampler conservatively over-captures today).

### 4.5 harness-core / harness-is / harness-cxa — accounted-for (no gap)
- **RB-CORE-01 / RB-IS-01 / RB-CXA-01** — complete. CORE shared types carry the cross-axis seams; IS has all 11 head contracts carried (C-IS-11 is a phantom non-contract); CXA is 31/31 wired (HARD gate). New cross-axis edges ride the per-axis forward arcs rather than being standalone gaps.

### 4.6 Unit-completeness verification (across all axes)
The symmetric head-unit-vs-code diff (§3 step 3b) is the mechanism for "implied missing units." Result: of 195 head units, **188 are directly cited in `src` and the remaining 7 all resolve to non-gaps** — **zero unimplemented head units**. The 7 candidates and their resolution:

| Candidate | src cite | resolution |
|---|---|---|
| U-CP-100 | 0 (test: `test_routing_core_surface.py`) | Implemented — L3 LLM_AS_ROUTER `infer()` branch in `routing_core_surface.py`; src cites the contract, not the U-* token |
| U-RT-01 | 0 (test: `test_package_smoke.py`) | Foundational unit, "PRESERVED VERBATIM" in plan lineage; implemented |
| U-RT-82 | 0 (test: `test_u_rt_82_memory_tool_filesystem_e2e.py`) | Implemented — memory-tool filesystem backend (dedicated e2e) |
| U-RT-85 | 0 (7 test files) | Implemented — validator framework |
| U-RT-133 | 0 (test: `test_lifecycle_llm_dispatch.py`) | Implemented — router-injection binding at `llm_dispatch.py:547-553` |
| U-RT-00 | 0 / 0 | **Not a real unit** — a range-notation boundary ("U-RT-00 through U-RT-109") |
| U-RT-91 | 0 / 0 | Validator-composer unit defined only in superseded plan v2_21 (implemented under the validator framework; superseded-version cite, parallel to the contract phantoms) |

**Caveat (RB-DOC-05):** the 5 implemented-but-not-src-cited units (and U-RT-91) are a *cite-traceability* observation, not an implementation gap — the U-* token lives in the test name / the src carries the contract cite. Folds into the cite-hygiene work (RB-DOC-02).

---

## 5. Missing arcs by dependency edge

The forward arcs are **not** independent; they hang off already-closed parents (`parent_arc` in `arc-ledger.yaml`). The dependency edges:

```
B-INTERSTEP (closed) ──────────────▶ B-INTERSTEP-NONLINEAR (RB-RT-01)
B-ENGINE-OUTPUT-REPLAY (closed) ───▶ B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT (RB-CP-01)
B-FANOUT-PAUSE (closed) ───────────▶ B-FANOUT-PAUSE-EVALUATOR-OPTIMIZER (RB-CP-02)
                            ├────────▶ B-FANOUT-PAUSE-PARALLELIZATION   (RB-CP-03)
                            ├────────▶ B-HANDOFF-PAUSE                  (RB-CP-04)
                            └────────▶ B-HIERARCHICAL-PAUSE             (RB-CP-05)
B-EFFECT-FENCE (closed) ───────────▶ B-EFFECT-FENCE-HITL-ROUTE  (RB-RT-02, also needs B-ENGINE-OUTPUT-REPLAY)
                            ├────────▶ B-EFFECT-FENCE-PER-TOOL   (RB-AS-01)
                            └────────▶ B-EFFECT-FENCE-DURABLE-AUTO (RB-RT-03)
B-HITL-PLACEMENT-PER-STEP-PRODUCER (closed) ▶ B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD (RB-CP-06)
B-EDIT-CARRIER (closed) ───────────▶ B-EDIT-CARRIER-DURABLE-ASYNC-RESUME (RB-RT-04)
                            └────────▶ B-HITL-WRAP-FAIL-CLASS-SURFACING (RB-CP-07)
B-L2-EMBEDDING-ACTIVATION (closed) ▶ B-ROUTING-MANIFEST-MODEL-FOLD (RB-CP-08)
B-L2-FALLBACK-COMPOSITION (closed) ▶ B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION (RB-RT-05)
B7 (closed) + R-420/R-421 (closed) ▶ B-TAIL-CONDITIONAL-SAMPLING (RB-OD-01, GATED)
R-FS-1 (ACTIVE) ───────────────────▶ R-CL-Q1 ▶ R-CL-Q2 ▶ R-CL-Q3 ▶ R-CL-Q4 ▶ (R-CL-D1) ▶ R-CL-C1
```

**Observations:**
- Every forward feature arc's parent is already closed → none is blocked by an *unbuilt* dependency (they are "registered, not yet decomposed").
- The **only hard gate** in the feature set is `B-TAIL-CONDITIONAL-SAMPLING` on `R-420/R-421` (both already RESOLVED — so the gate is effectively clear; the arc is decompose-ready).
- The **R-CL track is one long chain** gated on R-FS-1's completion (the standalone `B-*` register reaching empty). This is the macro dependency edge governing the whole program's tail.

---

## 6. Temporary substitutions that must be retired (task item 7)

**Status: the 54-row substitution ledger is 54/54 RETIRED, and the production-code retirement is verified** (no `harness-*/src/` path invokes the `harness-7a-scaffold` MCP). The remaining items are **bounded-residuals (dormant, not unbuilt)** and **dev-tooling residue (cleanup)**, not native-primitive gaps:

| Item | Row | Disposition | What remains |
|---|---|---|---|
| **CP-16** Memory tool production backend | RB-SUB-01 | RETIRED-AS-BOUNDED-RESIDUAL | FILESYSTEM/SQLite/S3/Neon all built + live-proven; "residual" = production exercise is deployment-gated, not unbuilt. Ratify-as-closed or fold standing activation into R-CL-Q4. |
| **OD-6** OTLP sqlite ingestion | RB-SUB-02 | RETIRED-AS-BOUNDED-RESIDUAL | `flush_to_sqlite` dormant at LOCAL by design (head-based sampling); exercised against the R-420 real collector. Dormant production substrate, not a build arc. |
| **Scaffold MCP server** | RB-SUB-03 | Retired-in-code, not cleaned from config | `.mcp.json` still registers `harness-7a-scaffold` → `scaffolding/mcp/server.py`; `scaffolding/mcp/` (server.py + telemetry.py) persists. No src invokes it. Optional cleanup at Phase-7d/8 / R-CL-Q4 close. |

The 44 `substitution_without_carrier` overlay advisories are expected (most carriers are named in rationale, not docstrings) — not a finding; the carrier files exist (e.g. `memory_tool_managed_db.py`, `files_api.py`), they simply lack a `H_T-*` docstring tag.

**Conclusion on item 7:** every H_T primitive that H_E temporarily stood in for now has a native implementation. No primitive *still needs* native implementation. Two are dormant-until-deployed; one config registration + one scaffolding dir are uncleaned dev-tooling.

---

## 7. Repo governance / documentation gaps

| Gap | Row | Severity | Tracked home |
|---|---|---|---|
| **All 7 packages lack `README.md`** | RB-DOC-01 | MEDIUM | R-CL-D1 (docs suite) |
| **14 code files without a spec/contract cite** (overlay `code_without_cite`) — real impls (docker/e2b drivers, files_api, memory backends, redaction, cli, strict-safe-loader) lacking a `C-*`/`U-*` cite | RB-DOC-02 | LOW | R-CL-Q1/D1 |
| **Overlay scans superseded spec versions** → 6 phantom `contract_without_code` orphans (the "6 unimplemented contracts" reading is FALSE) | RB-DOC-03 | LOW | `tools/semantic_overlay/` head-scoping |
| **R-IF-114 stale-ACTIVE** — dashboard-generate test rot likely resolved by #673's schema-backed arc-ledger overhaul + CI `--check` gate; status not refreshed | RB-GOV-07 | LOW | roadmap §5 refresh |
| **The R-CL quality/close track (Q1–Q4, D1, C1)** — 6 BLOCKED phases; the largest remaining surface, deliberately gated behind R-FS-1 | RB-GOV-01..06 | HIGH | R-FS-1 completion |
| **Root `tests/` = 1 file; examples cover only `topology`** | RB-DOC-04 | LOW | optional breadth |

Note: per-package tests are *comprehensive* (170 runtime / 97 cp / 53 od / 35 as / 21 is test files); the doc/traceability gaps are real but the **test coverage is not** a hole.

**Audit-altitude caveat.** The test/doc presence check above is at *file-count* altitude (package-level test-file counts + README presence), not *per-unit* (one assertion per the 195 head units). At this maturity — 4,565+ passing non-e2e tests, per-unit e2e proofs cited throughout the trackers — file-count altitude is an acceptable audit depth; a per-unit test-coverage matrix is itself part of R-CL-Q3 (QA + 100%-evidence closure), not this audit. Flagged so a reader does not over-read "comprehensive" as a certified per-unit guarantee.

---

## 8. High-risk hidden gaps

These are the gaps a tracker-transcription would miss — surfaced by the independent denominator check:

1. **The overlay's contract-orphan reading is a false positive (HIGHEST audit value).** `just overlay-query --orphans` reports 6 `contract_without_code`. Read naively, that says "6 specified contracts have no implementation." **All 6 are phantoms** — 5 cite only superseded plan/spec versions (the delta chain retains every version), and `C-IS-11` is a documented *corrected non-existent* cite. The genuine gap is **0**. Risk: every future audit/agent that trusts the overlay's contract orphan list will chase non-existent work. Fix: scope the overlay's contract scan to canonical heads (RB-DOC-03).
2. **One likely-stale OPEN fork (RB-RT-07).** `class_2_fork_engine_durable_resume_no_production_producer.md` (filed 2026-06-12) is the *only* genuinely-OPEN fork of ~163 — but its core premise ("engine-layer recovery loop has no production producer; the real gap is the workflow-layer api.run resume") has since been overtaken: the E arc (WAL_SEGMENT + RECONCILER_LOOP recovery, U-CP-93..97 / U-RT-121..124) and `api.resume` (C-RT-35) landed. Its own re-open trigger ("re-open when a real WAL-segment / reconciler-loop recovery loop lands") **fired and was built**. Risk: a session could re-open a resolved architectural fork. Action: re-ground and close-or-rescope (RB-RT-07).
3. **`harness-runtime` is invisible to the user's axis grouping.** The largest package (136 src) is not one of the 6 design axes; most forward arcs live there. An audit grouped only by IS/AS/CP/OD/CXA/core would systematically under-count the remaining surface. (Handled here as its own domain; the workspace's own `REPO_SURFACE_MAP.md` stub also omits it.)
4. **FULL-SPEC directive vs ratified WON'T-FIX closes.** The operator's 2026-06-12 directive ("nothing deferred… no exceptions") *supersedes* confirm-defer/bounded-residual closes — which re-opens items previously closed as residual: the `pause_context_reader` richer body (WON'T-FIX 2026-05-24, RB-CP-09), CP-16/OD-6 bounded-residuals, and the minor field-level scopes. Whether these are *built* or *re-ratified* is a genuine operator scoping call the trackers leave implicit.
5. **Dev-tooling retirement residue (RB-SUB-03).** Production code no longer invokes the scaffold MCP, but `.mcp.json` + `scaffolding/mcp/` persist — a 100%-retirement claim with uncleaned scaffolding could mask whether the X-AL-2 "surface no longer invoked" condition was checked at the *config* layer too. (It is, in src; the config is just uncleaned.)

---

## 9. Recommended build sequence

Derived from the actual `parent_arc` / `depends_on` edges (§5) and the operator FULL-SPEC sequencing, **not** an invented order.

**Phase A — R-FS-1 forward feature arcs (the standalone `B-*` register; drives R-FS-1 to resolution).** Order by load-bearing value (the roadmap_status next-selector already recommends the first two):
1. `B-ROUTING-MANIFEST-MODEL-FOLD` (RB-CP-08) — completes per-step model override under routing-activation.
2. `B-INTERSTEP-NONLINEAR` (RB-RT-01) — concurrent-fan-out inter-step data (unblocks effective multi-agent topologies).
3. The **pause-resume family** (RB-CP-02..05) + `B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT` (RB-CP-01) — durable resume across all topologies (each closes a `*-pause-resume-not-yet-materialized` honest-FAILED branch).
4. The **effect-fence family** (RB-RT-02, RB-AS-01, RB-RT-03) — at-most-once → operator-resolvable; per-tool classification (design-fork-first); durable-auto.
5. HITL/edit folds (RB-CP-06, RB-RT-04, RB-CP-07) + `B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION` (RB-RT-05).
6. `B-TAIL-CONDITIONAL-SAMPLING` (RB-OD-01) — gate (R-420/R-421) already clear.
7. **Residual cleanups** that FULL-SPEC re-opens: RB-RT-06 (F1-01 WAL exactly-once), RB-RT-07 (re-ground/close the stale fork), RB-CP-09/10 (re-ratify or build), RB-AS-02 (token-counting), RB-SUB-01/02 (ratify-as-closed).

**Phase B — governance/doc hygiene (can run in parallel; cheap):** RB-DOC-03 (overlay head-scoping), RB-GOV-07 (close stale R-IF-114), RB-DOC-02 (add the 14 cites), RB-SUB-03 (scaffold cleanup). RB-DOC-01 (READMEs) folds into R-CL-D1.

**Phase C — the R-CL quality/close track (BLOCKED until R-FS-1 resolves; the macro tail):** Q1 DevEx/simplification → Q2 security → Q3 QA closure → Q4 portable packaging + deployment (absorbs RB-ACT-02 standing deploy + RB-SUB-03) → D1 docs suite (absorbs RB-DOC-01) → C1 closure certification + ship. Plus RB-ACT-03 (persona TEAM_BINDING e2e) and RB-ACT-01 (multi-provider activation) as operator-gated activations.

**Phase D — elective:** RB-PROP-01 (dashboard iter-2), RB-PROP-02 (Surface-X research, seed-on-question), RB-PROP-03 (ICM adoption, decide-3-gates-first).

> **Operator gates (surface, don't auto-fire):** multi-provider credentials (RB-ACT-01), standing deployment (RB-ACT-02/Q4), live persona e2e (RB-ACT-03), FULL-SPEC-vs-ratify on the residuals (RB-CP-09, RB-SUB-01/02), and the ICM 3-gate decision (RB-PROP-03). Per `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`, drive each to its gate; never auto-fire a paid call or relocate secrets.

---

## 10. Appendix: evidence by file/path

**Denominator (canonical heads):**
- Contracts (108): extracted from `Spec_Control_Plane_v1_43.md`, `Spec_Operational_Discipline_v1_30.md`, `Spec_Harness_Runtime_v1.md`, `Spec_Information_Substrate_v1.md`, `Spec_Action_Surface_v1.md` + plans `Implementation_Plan_Control_Plane_v2_37.md`, `…Operational_Discipline_v2_28.md`, `…Harness_Runtime_v2_48.md`, `…Information_Substrate_v2_6.md`, `…Action_Surface_v1_4.md`, `…Harness_Core_v1_2.md`, `Cross_Axis_Composition_Document_v2_20.md`.
- Units (195 head; 329 distinct cited in `harness-*/src`): `head_units − code_cited = 7` (U-CP-100, U-RT-00/01/82/85/91/133 — all resolved as non-gaps, §4.6); `code_cited − head_units = 141` (AS 17, CP 41, IS 10, OD 42, RT 31 — superseded-version units the head delta-plans no longer re-table; confirms code implements ≥329 units, i.e. the head count under-states the built set). U-RT-113..133 extraction verified present in heads (extraction sound).

**Overlay (`just overlay` / `just overlay-query --orphans`, HEAD `46012d5`):**
- `source files: 329; files carrying a cite: 315 (95.7%); distinct contracts cited: 125; distinct units cited: 327; CXA seams: 31/31 wired (HARD gate green).`
- `contract_without_code` (6, all phantoms): C-CP-00 (Spec_Control_Plane_v1_38.md, absent from head v1_43), C-CP-30/C-CP-37 (Impl_Plan_CP_v2_31.md, head is v2_37), C-CP-43 (Impl_Plan_CP_v2_6/v2_7), C-IS-11 (corrected non-existent cite — runtime spec L2160), C-OD-3 (Spec_OD_v1_8.md, head is v1_30).
- `code_without_cite` (14): `harness-od/src/harness_od/redaction_token_audit.py`; `harness-runtime/src/harness_runtime/{bootstrap/stage_3b_cp_routing.py, cli/__main__.py, lifecycle/cp_as_wiring.py, lifecycle/docker_tool_execution_driver.py, lifecycle/e2b_tool_execution_driver.py, lifecycle/escalation_prompt.py, lifecycle/files_api.py, lifecycle/hitl_auto_approve_policy.py, lifecycle/memory_tool_encrypted.py, lifecycle/memory_tool_managed_db.py, lifecycle/memory_tool_s3.py, lifecycle/redaction_token_audit_map.py, lifecycle/strict_safe_loader.py}`.

**Substitution cross-check:**
- `grep -rln harness-7a-scaffold harness-*/src` → NONE. `grep -rln scaffold harness-*/src` → 5 benign hits (`cost_formula.py` "plan-internal scaffolding"/"Module-private scaffold"; `cli/app.py` "scaffolding; U-RT-106 lands the concrete one-shot"; `lifecycle_emitter.py`; `collector_daemon.py`). Scaffold MCP registered in `.mcp.json` → `scaffolding/mcp/server.py` + `telemetry.py` (uncleaned).

**MCP boundary (native, built):** `harness-runtime/src/harness_runtime/lifecycle/{mcp_server.py, mcp_host.py, mcp_client_host.py, mcp_backed_ask_user_question_surface.py, step_mcp_trust_tier.py}`; `bootstrap/factories/mcp_client_host_factory.py`.

**Trackers (the workspace's own remaining-work claim, cross-checked):**
- `.harness/arc-ledger.yaml` — snapshot: frozen 11/11, standalone_closed 16, standalone_gated 1, standalone_resolved 2, **standalone_registered 14**.
- `.harness/beyond-mvp-capability-boundary-ledger.md` — spine (per-arc rationale; Bucket B + minor field-level scopes).
- `.harness/post-phase-8-forward-register.md` — Tier A (closed) / Tier B (mostly closed; B-13 memory done, B-15/16/17 proposed).
- `.harness/capability-completion-inventory-v1.md` — "genuine open set is ~11 units; nearly every forward surface RESOLVED with live e2e proof."
- `Project_Roadmap_v1.md` §5 (89 yaml entries): 76 RESOLVED, 5 ACTIVE (R-FS-1 + R-IF-114 + 3 recurring lanes), 1 APPLIED-PENDING-OPERATOR-E2E (R-CL-P3), 6 BLOCKED (R-CL-Q1..Q4, D1, C1).
- `.harness/roadmap_status.md` — dashboard (16 standalone `B-*` closed; 14 forward + 1 gated).

**Open residual records:**
- `.harness/r-fs-1-e-impl-3c-f1-01-wal-exactly-once.md` (Status: 🔵 OPEN, low-severity, tracked; fix-shape ready).
- `.harness/class_2_fork_engine_durable_resume_no_production_producer.md` (Status: OPEN, awaiting operator scoping — likely stale per §8.2).
- `.harness/residual_closure_pause_context_reader_richer_body.md` (CLOSED-as-WON'T-FIX 2026-05-24; FULL-SPEC arguably re-opens).

**Package shape:** core 8 src / 4 test · IS 20 / 21 · AS 34 / 35 · CP 72 / 97 · OD 57 / 53 · CXA 2 / 3 · runtime 136 / 170. All 7 `tests/` dirs present; all 7 `README.md` absent. `examples/` (minimal.toml + workflows/topology), `deploy/` (self-hosted-local + managed-cloud), `harness.toml.example` present.

---

---

## 11. Second-pass refinement — hidden-omission probes

A second adversarial pass targeted 8 hidden-omission categories with **empirical probes** (not re-reading). The headline: the first pass's "near-complete" conclusion **holds under adversarial scrutiny** — the probes surfaced 4 new findings (all LOW except one MEDIUM API-surface gap) and **5 clean confirmations**. Net new register rows: **RB-EXP-01, RB-CXA-02, RB-CXA-03, RB-GOV-08** (register now 48 rows).

| # | Category | Probe + result | Finding |
|---|---|---|---|
| 1 | **Implied interfaces with no concrete contract** | Scanned all `src` for `Protocol`/`ABC`/`abstractmethod`: **66 interfaces**; only 5 files carry a Protocol without a `C-*` cite — and those are **external-SDK structural shims** (`FilesApiClientProtocol`, `S3ClientProtocol`, `FernetLike`, `ManagedSqlConnection/Cursor`), legitimately not H_T contracts (same files as RB-DOC-02). | **CLEAN** — no implied H_T interface lacks a contract; the 5 are external structural typing (folds into RB-DOC-02 cite hygiene). |
| 2 | **Package exports that should exist but do not** | Compared each package `__init__.py`: `harness-as` curates `__all__`=191, core=18, is=27, runtime=25 — but **`harness-cp` (71 modules), `harness-od` (56), and `harness-cxa` have EMPTY `__init__.py` (0 exports, no `__all__`)**. | **NEW → RB-EXP-01 (MEDIUM).** No package-root public API for cp/od/cxa. Submodule imports work (`from harness_cp import workflow_driver`), so not a functional break, but the discipline is inconsistent and matters for R-CL-Q4 packaging + DX. Decide curate-vs-internal-only. |
| 3 | **Workflow steps with no executable surface** | Enumerated `StepKind` (6 members) + the `StepKindDispatcherRegistry` binding at `stage_5_loop_init.py:627`: **TOOL_STEP always bound; INFERENCE_STEP + SUB_AGENT_DISPATCH provider-gated; MANAGED_AGENTS surface-gated; DECLARATIVE_STEP + HITL_STEP are driver-native** (handled inline at `workflow_driver.py:2188`, not via the registry). `StepKindDispatcherNotBoundError` fail-closes the gated ones off-surface. | **CLEAN (with nuance)** — all 6 StepKinds have an executable surface, split across 2 mechanisms (registry for 4, driver-native for 2). A reader inspecting only the dispatcher registry would wrongly think DECLARATIVE/HITL are unbound — documentation nuance, not a gap. |
| 4 | **MCP boundary lacking protocol/schema/process artifacts** | Inspected the native MCP server: `mcp_server.py` (U-RT-62, `HarnessMCPServer` over FastMCP) exposes the `run_workflow` tool, registered at bootstrap stage 2, wired into `api.py` + `stage_2_as` + `stage_5_loop_init`, with per-session `ContextVar` ctx isolation + outbound `ctx.elicit(...)` HITL. The X-AL-1 boundary (H_T-as-MCP-server) is fully realized. | **CLEAN** — the native MCP server process + protocol (`run_workflow`) + per-session schema all exist. Only residue = the scaffold MCP (already RB-SUB-03). |
| 5 | **Cross-axis composition promises lacking orchestration/wiring** | (a) Reconciled the seam counts: the overlay's HARD gate tracks **31** `PATTERN_P1_SEAMS` (`test_cxa_pattern_p1.py:296` asserts `==31`; lines 481-493 **also fail on any un-enumerated cross-axis import** → complete w.r.t. real imports), while the CXA doc §2.1 says **37** genuine typed. (b) `harness-cxa/src` has only `cp_audit_conversion.py` — the seam wiring lives in `harness-runtime/lifecycle/`. | **NEW → RB-CXA-03 (LOW):** the 31-vs-37 is a *definitional collision* (code cross-axis-import seams vs plan-canonical typed seams incl. shared-core/runtime-mediated), **not 6 unwired seams** — composition is fully wired + gated. **NEW → RB-CXA-02 (LOW):** `harness-cxa` is a near-stub; CLAUDE.md §3.3's "hosts CXA seam instantiation" is aspirational vs runtime-resident reality. |
| 6 | **Tests/examples/fixtures missing for present modules** | Diffed every `src` module against test-file references: 2 candidates (`rate_table_bridge.py`, `strict_safe_loader.py`) — both re-grounded as **tested indirectly** (cost-formula tests; manifest-loader + track-b e2e). | **CLEAN** — 0 genuinely-untested src modules. (Examples breadth remains RB-DOC-04: only `topology` worked example.) |
| 7 | **Roadmap items lacking implementation anchors** | RESOLVED R-NNN entries are PR-anchored (cross-checked against the arc-ledger PR refs). The items *without* an implementation anchor are the **14 registered-forward arcs + B-16 + RB-PROP surfaces — by design** (decompose-at-open / undecomposed), already in the register; plus **R-IF-114 stale-ACTIVE** (RB-GOV-07). | **CLEAN (covered)** — no RESOLVED item is anchor-phantom; the anchorless items are intentionally-deferred (registered) and already captured. |
| 8 | **Retirement/archive/governance surfaces that should be active** | `.harness/archive/` active (root-historical + archived forks); **85 clearance markers**; CI `x-al-3-guard.yml` + `ci.yml` + `dashboard-deploy.yml` active. Only the **local advisory pre-commit hook is unset** (`core.hooksPath` not configured this checkout). | **Mostly CLEAN.** **NEW → RB-GOV-08 (LOW, informational):** the opt-in `.githooks/pre-commit` is not enabled locally — by design; the CI X-AL-3 guard is the hard backstop. Plus the scaffold residue (RB-SUB-03). |

**Second-pass verdict.** The adversarial probes did **not** uncover a hidden mass of unbuilt surface — they confirm the harness is near-complete and well-governed. The one materially actionable new item is **RB-EXP-01** (cp/od/cxa lack a curated public-export surface), which is a packaging/DX decision best folded into R-CL-Q4 + R-CL-D1. Everything else is doc/count-reconciliation hygiene (RB-CXA-02/03, RB-GOV-08) — the same "looks like a gap, isn't" class as the first pass's phantom-orphan finding.

---

*End of report. Companion register: `.harness/audit/Remaining_Build_Register.csv` (48 rows). Audit posture: mode-agnostic; no design-substrate or src edits. §11 = second-pass hidden-omission refinement.*
