# R-700 Phase-8 Closure Accounting — DRAFT

> **Status: Claude-executable DRAFT for operator Phase-8 review/ratification.** This compiles the definitive remaining-to-full-harness-closure log requested by the operator (2026-06-01) and banked at `.harness/R-700-closure-accounting-draft-checkpoint.md`. It feeds `R-700-phase-8-substitution-accounting` (still BLOCKED — the operator owns the final Phase-8 numbers + the bounded-residual sign-offs for AS-8e / AS-8f / OD-6). **Posture: mode-agnostic** (process-substrate compilation; reads `design-substrate/` + `harness-*/CLAUDE.md` §4.1 + `.harness/` ledger; authors only this `.harness/` file + the roadmap/dashboard refresh). Not a design-substrate amendment — no X-AL-3 / clearance marker owed.
>
> **Compiled at HEAD `d27fa65` (post-PR-#206), 2026-06-01.** Primary sources: live per-axis `harness-{is,as,cp,od}/CLAUDE.md` §4.1 tables; `.harness/phase-7d-retirement-ledger-v2.md` §7 + §11; `design-substrate/Phase_7_Meta_Architecture_v1.md` §5; `Project_Roadmap_v1.md` §5; batch records `batch-{1..51}`.

---

## Headline finding (read this first)

**The published dashboard figure `48/54 RETIRED + 49/54 pipeline-advanced` is internally impossible, and the per-axis "only 3 rows open" framing under-counts the open set.** Both follow from one root cause: **the 5 CXA substitution rows have no per-axis `§4.1` file, and the ledger's own CXA corrective accounting was explicitly "never adopted into the workspace cumulative counts — pending operator routing"** (ledger §11.1a line 278).

- `48 RETIRED + 49 pipeline-advanced` implies **≤ 1 PARTIAL** (pipeline-advanced = RETIRED + RETIRE-READY + PARTIAL; RETIRE-READY bucket is empty post-batch-51). But there are **3 PARTIAL rows**: `OD-4`, `CXA-1`, `CXA-4`. The arithmetic cannot hold.
- The per-axis `§4.1` view surfaces only 3 non-RETIRED rows (`OD-4`, `AS-8e`, `AS-8f`). The **true open set is 8 rows** — the extra 5 (`CXA-1/2/3/4` + `CP-17`) live outside the per-axis `§4.1` surface (CXA has no `§4.1`; `CP-17`'s SB-INDEF reclassification at batch-44 isn't framed as "open").

**Reconciled per-row count: `46 RETIRED + 3 PARTIAL + 2 STILL-BOUNDED + 3 STILL-BOUNDED-INDEFINITELY = 54`** → pipeline-advanced **49/54 = 90.7%** (this half *matches* the published headline; the RETIRED-vs-PARTIAL split is where the drift lives).

**This is a bookkeeping refinement, NOT a regression.** No substitution that was closed has re-opened. The 5 rows that move the published `48` down to `46–47` are all *already-known* deferred surfaces: `CXA-1/2/3/4` are Phase-2-runtime-deferred (typed composers wired + tested at 7c, zero production callers) and `CP-17` is deferred-by-design (Files-arc Memory-only MVP scope). The published `48` simply counted some of them as advanced/closed without folding them through the live per-row state.

**The integer is a range, `46–47`, not a single value** — see the bookkeeping ambiguities at §A.3. The published operator-ratified `48/54` is **not** overwritten by this draft; it is carried forward as a flagged Phase-8 ratification item (§C) for the operator to settle.

---

# PART A — The 54-row substitution closure log

The canonical substitution map (`Phase_7_Meta_Architecture_v1.md` §5.7) declares **49 substitutions** (IS 9 / AS 6 / CP 21 / OD 8 / CXA 5). The **54-row "raw ledger" view** is the §5 map after the `H_T-AS-8` monolithic row was decomposed into 6 sub-rows `AS-8a..8f` at retirement batch-24 (+5). Both denominators are legitimate; this log uses the **54-row ledger view** (the operator's request + the dashboard's denominator).

Disposition classes: **substantive-RETIRED** / **RETIRED-AS-AUTHORING-ONLY** (the H_T contract is the typed declaration itself, no runtime behavior; sub-species 10 categorical-mismatch closes) / **RETIRED-AS-BOUNDED-RESIDUAL** (production substrate dormant at MVP; substantive close deferred to a real deployment surface; X-AL-2 §5.3) / **PARTIAL** / **STILL-BOUNDED** / **STILL-BOUNDED-INDEFINITELY** (deferred-by-design).

### A.1 IS axis — 9 rows · 9 RETIRED (7 substantive + 2 authoring-only) · IS-axis 9/9 = 100%

| ID | Substitutes | Disposition | Closed | Note |
|---|---|---|---|---|
| H_T-IS-1 | Path-class registry / workflow-canonical resolver | substantive-RETIRED | batch-1 (2026-05-20) | `stage_1_is.py` `materialize_path_registry`; convention surface displaced |
| H_T-IS-2 | Artifact-tier registry + cross-tier traceability | substantive-RETIRED | batch-50 (2026-05-31) | append-time `procedural_tier_snapshot_ref` sidecar enforced at every active-workflow producer site (R-003 cascade complete) |
| H_T-IS-4 | Atomic-deploy primitive (commit-grain reversibility) | RETIRED-AS-AUTHORING-ONLY | batch-39 | categorical-mismatch: operator `Bash(git *)` IS the canonical deploy substrate per ADR-F2, not a transitional substitution |
| H_T-IS-5 | State-ledger entry shape (6-field) | substantive-RETIRED | batch-1 (2026-05-20) | `lifecycle/state_ledger.py` driver-invoked at `workflow_driver.py:397-417` |
| H_T-IS-6 | Hash-chain integrity (SHA-256 / JCS) | substantive-RETIRED | batch-1 (2026-05-20) | `entry_hash.py` in-process `hashlib`; chain-verify at reattach |
| H_T-IS-7 | F2 read/write contract pair (JSONL) | substantive-RETIRED | batch-1 (2026-05-20) | `state_ledger_write` + `state_ledger_read` both materialized at bootstrap |
| H_T-IS-8 | Shadow-Git checkpoint cadence | substantive-RETIRED | batch-1 (2026-05-20) | `shadow_git_checkpoint.py:91` manifest-driven cadence gate |
| H_T-IS-9 | Worktree isolation (workload-opt-in) | substantive-RETIRED | batch-1 (2026-05-20) | `worktree_isolation.py` manifest-driven opt-in + concurrency-cap |
| H_T-IS-10 | Substrate seam exports manifest | RETIRED-AS-AUTHORING-ONLY | v1 §1 | per-axis authoring artifact |

### A.2 AS axis — 11 rows · 9 RETIRED (8 substantive + 1 authoring-only) + 2 STILL-BOUNDED-INDEFINITELY · AS-axis 9/11 = 81.8%

| ID | Substitutes | Disposition | Closed | Note |
|---|---|---|---|---|
| H_T-AS-1 | SandboxTier 4-tier + monotonicity | substantive-RETIRED | batch-20 (2026-05-20) | `lifecycle/sandbox_dispatch.py` 6-provider×tier table |
| H_T-AS-2 | Tool-contract schema | substantive-RETIRED | batch-16 (2026-05-24) | joint close with H_T-CP-18; `ToolContract` enforced at `RuntimeToolDispatcher` |
| H_T-AS-4 | `sandbox.*` 7-attr namespace | substantive-RETIRED | batch-19 (2026-05-26) | Reading B arc 2; `_emit_sandbox_violation` dual fail-class span |
| H_T-AS-5 | Sandbox-event idempotency-key | substantive-RETIRED | batch-23 (2026-05-28) | gate-text reframe → idempotency-key attribute on `sandbox.violation` span |
| H_T-AS-8a | `anthropic.*` 10-attr namespace | substantive-RETIRED | batch-24 (2026-05-28) | LANDED at `llm_dispatch.py` gen_ai span |
| H_T-AS-8b | `mcp.*` 7-attr namespace | substantive-RETIRED | batch-24 (2026-05-28) | LANDED at `runtime_tool_dispatcher.py` |
| H_T-AS-8c | `memory.*` 6-attr namespace | substantive-RETIRED | batch-24 (2026-05-28) | LANDED at `memory_tool_dispatch.py` |
| H_T-AS-8d | `skill.*` 6-attr namespace | substantive-RETIRED | batch-31 (2026-05-28) | mech-β deployment-time-opt-in-gate; producer chain at runtime spec v1.32 C-RT-27 |
| **H_T-AS-8e** | **`files.*` 8-attr namespace** | **STILL-BOUNDED-INDEFINITELY** | **—** | **Files arc DEFERRED INDEFINITELY per runtime spec v1.17 §14.C Memory-only MVP scope → roadmap R-005** |
| **H_T-AS-8f** | **`managed_agents.*` 3-attr namespace** | **STILL-BOUNDED-INDEFINITELY** | **—** | **DEFER INDEFINITELY per `class_1_fork_as_8f_...` Q1=(C); production-only exclusion → roadmap R-006** |
| H_T-AS-9 | Substrate seam exports manifest | RETIRED-AS-AUTHORING-ONLY | v1 §1 | per-axis authoring artifact |

> **Row-identity note (AS-3 ↔ AS-9).** Meta-Arch §5.3 lists the AS base as `{AS-1, AS-2, AS-3, AS-4, AS-5, AS-8}` — `AS-3` = "3-valued GateLevel AUTO/ASK/DENY". The live `harness-as/CLAUDE.md` §4.1 *retirement* table drops `AS-3` and adds `AS-9` (substrate-seam-exports authoring), keeping the count at 11 (post-AS-8 decomposition). `AS-3`'s gate semantic is governed at the CP-axis HITL surface (`H_T-CP-20` 4-response palette). This is a documentation seam, not a count change — AS stays 11 either way. Flagged at §A.3 as one driver of the 46-vs-47 integer ambiguity.

### A.3 CP axis — 22 CP-axis-local rows (21 canonical per Meta-Arch §5.4) · 21 RETIRED (17 substantive + 3 authoring-only + 1 bounded-residual) + 1 STILL-BOUNDED-INDEFINITELY · CP-axis 21/22 = 95.5%

| ID | Substitutes | Disposition | Closed | Note |
|---|---|---|---|---|
| H_T-CP-1 | Routing core + ProviderCapabilities (multi-LLM) | substantive-RETIRED | batch-1 (U-RT-52, 2026-05-20) | runtime LLM call site at `lifecycle/llm_dispatch.py` per C-RT-15 |
| H_T-CP-2 | Layered routing strategy | substantive-RETIRED | (early batch) | composer landed |
| H_T-CP-3 | Per-layer time-budget + `retry.*` | substantive-RETIRED | (early batch) | `retry_breaker.py` |
| H_T-CP-4 | Fallback chain + cross-family fallback | substantive-RETIRED | (early batch) | `fallback_chain.py` |
| H_T-CP-5 | Routing attr namespaces + sampling | substantive-RETIRED | (early batch) | routing namespace |
| H_T-CP-6 | Workflow-manifest schema + per-step override + audit | substantive-RETIRED | batch-2 | operator `RoutingManifest` validated; `resolve_step_binding` per-step |
| H_T-CP-8 | F2-substrate-join contract | substantive-RETIRED | batch-47 | sub-species 7e (composer-library-complete-no-H_E-surface) |
| H_T-CP-9 | ResumptionKind 5-class + `engine.*` | substantive-RETIRED | batch-48 | sub-species 7a; CP spec v1.6 §25.5 v1.4 carve-out |
| H_T-CP-10 | TopologyPattern 6-class + admissibility | substantive-RETIRED | (per §4.1) | `SINGLE_THREADED_LINEAR` MVP slice |
| H_T-CP-11 | Per-workload commitment table + D4 tunable | substantive-RETIRED | batch-30 | sub-species 7a; v1.6 MVP cascade_policy carve-out |
| H_T-CP-12 | Sandbox-tier dispatch (cross-deployment monotonicity) | RETIRED-AS-AUTHORING-ONLY | batch-40 | sub-species 10 categorical-mismatch |
| H_T-CP-13 | Sub-agent handoff schemas | substantive-RETIRED | (per §4.1) | `RuntimeHandoffRegistry` |
| H_T-CP-14 | Multi-agent span hierarchy + `topology.*`/`subagent.*` | substantive-RETIRED | batch-29 | sub-species 7a; v1.6 MVP single-sub-agent slice |
| **H_T-CP-16** | **Memory primitives + `memory.*` consumption** | **RETIRED-AS-BOUNDED-RESIDUAL** | **batch-44** | indefinite-defer per sub-species 7g; gated on Files-API surface authoring |
| **H_T-CP-17** | **Files primitives + `files.*` consumption** | **STILL-BOUNDED-INDEFINITELY** | **—** | **reclassified batch-44 per runtime spec v1.17 §14.C Files-arc ratified scope** |
| H_T-CP-18 | MCP integration + per-server trust + `mcp.*` | substantive-RETIRED | batch-16 | joint close with H_T-AS-2 |
| H_T-CP-19 | D5 cross-deployment monotonicity | substantive-RETIRED | batch-22 | first sub-species 7 close; Layer-3 e2e reframed scope |
| H_T-CP-20 | HITL primitive + 4-response palette + `hitl.*`/`audit.*` | substantive-RETIRED | batch-8 | `RuntimeHITLGateComposer` invokes `ask_user_question_surface.ask(...)` |
| H_T-CP-21 | ValidatorFailClass 5-class + operator-burden eval | substantive-RETIRED | batch-17 | corrective close (restored batch-15 DOWN-classification) |
| H_T-CP-22 | Pause/resume protocol + state-summary + material-diff | substantive-RETIRED | batch-18 | workflow-layer composer close |
| H_T-CP-23 | Bridging-arc composition (F1+D1+D4) | RETIRED-AS-AUTHORING-ONLY | batch-41 | sub-species 10 categorical-mismatch |
| H_T-CP-24 | Substrate seam exports / authoring artifact | RETIRED-AS-AUTHORING-ONLY | v1 §1 | per-axis authoring artifact (the CP-axis-local 22nd row) |

> **Bookkeeping ambiguity (the 55→54 / 46-vs-47 driver).** Summing the *per-axis-local* tables gives **55** (IS 9 + AS 11 + **CP-local 22** + OD 8 + CXA 5). Exactly one row must drop to reach the canonical **54**, because Meta-Arch §5.4 declares CP as **21 entries** (§5.7 total = 49; Meta-Arch itself documents a "21-entry-vs-23-row" CP carry-forward at v1.4 §0.4(d)). The natural drop is the CP-axis-local authoring extra (`H_T-CP-24`, paralleling that the canonical-49 may not separately count each axis's seam-exports artifact). **If CP contributes 21 to the 54 (= 20 RETIRED + `CP-17` SB-INDEF): RETIRED = 46, pipeline-advanced = 49** (matches the published pipeline figure). **If instead `CP-17` is the out-of-canonical extra (CP = 21 RETIRED in-54): RETIRED = 47, SB-INDEF = 2, pipeline-advanced = 50.** The `AS-3↔AS-9` seam (§A.2) is the second contributor. The drifted ledger cannot resolve this to a single integer; **`46–47 RETIRED` is the honest range.** Both candidates agree the published `48` over-counts substantive-RETIRED by 1–2.

### A.4 OD axis — 8 rows · 7 RETIRED (3 substantive + 3 authoring-only + 1 bounded-residual) + 1 PARTIAL · OD-axis 7/8 = 87.5%

| ID | Substitutes | Disposition | Closed | Note |
|---|---|---|---|---|
| H_T-OD-1 | Deferral envelope | RETIRED-AS-AUTHORING-ONLY | batch-37 | sub-species 10 categorical-mismatch (zero runtime callers) |
| H_T-OD-2 | OTel SDK base + GenAI semconv binding | substantive-RETIRED | batch-2 (2026-05-20) | `RuntimeLLMDispatcher.dispatch` gen_ai span |
| H_T-OD-3 | Composite Sampler (head/tail gradient) | substantive-RETIRED | batch-51 (2026-06-01) | `HarnessCompositeSampler` live at MVP via `materialize_tracer_provider_stage`; 7a-scaffold sampler replaced (gate-text-stale audit) → closes R-007 |
| **H_T-OD-4** | **Pre-Collector redaction SpanProcessor** | **PARTIAL (refined)** | **— (batch-35)** | **the one genuinely-open per-axis-§4.1 substitution: §13.1 per-session redaction toggle (session-control substrate) + §13.2 opaque-token tokenization still deferred → roadmap R-008** |
| H_T-OD-5 | Cost-attribution 5-step chain | substantive-RETIRED | batch-32 (2026-05-28) | mech-β AC #8; U-OD-40 validator+webhook LANDED |
| **H_T-OD-6** | **Local-first OTLP ingestion (in-process collector + sqlite)** | **RETIRED-AS-BOUNDED-RESIDUAL** | **batch-51 (2026-06-01)** | **FIRST bounded-residual close in the ledger; `flush_to_sqlite` dormant at MVP (zero callers) → boundary unmoved → bounded-residual per X-AL-2 §5.3; gated on R-420/R-421 → closes R-009** |
| H_T-OD-7 | Preservation invariants (5-dimension) | RETIRED-AS-AUTHORING-ONLY | batch-38 | sub-species 10 categorical-mismatch (static deferral-signature contract) |
| H_T-OD-8 | Aggregate manifest + Stage 3b inversion | RETIRED-AS-AUTHORING-ONLY | v1 §1 | per-axis authoring artifact |

### A.5 CXA axis — 5 rows · 1 RETIRED + 2 PARTIAL + 2 STILL-BOUNDED · **no per-axis `§4.1` file** (status from ledger §7 + §11.1a/b/c only)

This is the axis that drives the headline reconciliation: it is invisible to the per-axis `§4.1` "open rows" view. CXA edge-counts (13/36/24/26/1) are *edges within* each substitution, not separate substitutions — CXA is **5 substitutions** (Meta-Arch §5.6 lines 482-486). Confirmed stable through HEAD (only batch-42 transited a CXA row).

| ID | Substitutes | Disposition | Closed | Note |
|---|---|---|---|---|
| H_T-CXA-1 | AS → IS substrate consumption (13 edges) | **PARTIAL** | — | composer `lifecycle/as_is_wiring.py` materialized + 7c-tested end-to-end → IS append; **zero production callers of `emit_secret_fetch_audit_entry` outside tests** (AS secret-fetch driver path absent) |
| H_T-CXA-2 | CP → IS substrate consumption (36 edges) | **STILL-BOUNDED** | — | `cp_is_wiring.py` PARTIAL-LAND (1 of 17 spec §12.3 edges; 16 DEFERRED per `class_1_tension_u_rt_35_cp_is_wiring_gaps.md`); zero production callers |
| H_T-CXA-3 | CP → AS substrate consumption (24 edges) | **STILL-BOUNDED** | — | no `lifecycle/cp_as_wiring.py` module (consistent with spec §12 — no CP→AS stage); typed edges anchored at 7c Pattern-P1 import surface only; audit-empty per ledger §11.1b (cardinality-1 termination) |
| H_T-CXA-4 | OD → IS / AS / CP substrate consumption (26 edges) | **PARTIAL** | batch-42 | 3 composer stages fire at bootstrap; **OD audit-write seam fully exercised at production** (6 `audit_writer.append` callers via `cp_audit_to_od_audit`); ~5 of 26 edges materialized |
| H_T-CXA-5 | OD → CP inversion (`harness.breaker.*`) | **substantive-RETIRED** | batch-3 (2026-05-20) | production `harness.breaker.*` emission at `retry_breaker_fallback.py` (U-RT-58); inversion seam fires end-to-end. **Belatedly recognized at ledger §11.1a (carried STILL-BOUNDED-DOWNSTREAM through batches 22-41 — 38-batch / 8-day stale-carry)** |

### A.6 Reconciled tally

| Disposition class | Rows | IDs |
|---|---|---|
| substantive-RETIRED | **36** | IS-1/2/5/6/7/8/9 (7); AS-1/2/4/5/8a/8b/8c/8d (8); CP-1/2/3/4/5/6/8/9/10/11/13/14/18/19/20/21/22 (17); OD-2/3/5 (3); CXA-5 (1) |
| RETIRED-AS-AUTHORING-ONLY | **9** | IS-4, IS-10, AS-9, CP-12, CP-23, CP-24, OD-1, OD-7, OD-8 |
| RETIRED-AS-BOUNDED-RESIDUAL | **2** | CP-16, OD-6 |
| **→ Total RETIRED** | **46–47** | (range per the §A.3 CP-21-vs-22 / AS-3↔AS-9 bookkeeping ambiguity) |
| PARTIAL | **3** | OD-4, CXA-1, CXA-4 |
| STILL-BOUNDED | **2** | CXA-2, CXA-3 |
| STILL-BOUNDED-INDEFINITELY | **3** | AS-8e, AS-8f, CP-17 |
| **GRAND TOTAL** | **54** | ✓ |

- **Pipeline-advanced (RETIRED + RETIRE-READY + PARTIAL) = 49/54 = 90.7%** — matches the published dashboard figure (RETIRE-READY bucket empty; 46 RETIRED + 3 PARTIAL = 49).
- **Non-pipeline-advanced = 5/54** — `CXA-2`, `CXA-3` (STILL-BOUNDED) + `AS-8e`, `AS-8f`, `CP-17` (STILL-BOUNDED-INDEFINITELY).

### A.7 The full open set — 8 rows (vs the 3 the per-axis `§4.1` view shows)

| Row | Class | Roadmap | Path to close |
|---|---|---|---|
| H_T-OD-4 | PARTIAL | **R-008** (BLOCKED, phase-7) | §13.1 per-session redaction toggle + §13.2 opaque-token tokenization. The one genuinely-open MVP-surface substitution. |
| H_T-AS-8e | SB-INDEFINITE | **R-005** (DEFERRED) | bounded-residual close at Phase 8 (Files-arc indefinite-defer; runtime spec v1.17 §14.C). Operator sign-off. |
| H_T-AS-8f | SB-INDEFINITE | **R-006** (DEFERRED) | bounded-residual close at Phase 8 (managed_agents production-only exclusion). Operator sign-off. |
| H_T-CP-17 | SB-INDEFINITE | (no R-entry — CP-axis §4.1 shows "fully RETIRED") | Files-arc indefinite-defer (batch-44). **Owed: an R-NNN entry parallel to R-005/R-006, OR fold into the Phase-8 bounded-residual sign-off.** |
| H_T-CXA-1 | PARTIAL | (no R-entry) | AS secret-fetch driver path landing → production callers of `emit_secret_fetch_audit_entry`. Phase-2-runtime-deferred. |
| H_T-CXA-2 | STILL-BOUNDED | (no R-entry) | remaining 16 of 17 CP→IS §12.3 edges (`class_1_tension_u_rt_35_cp_is_wiring_gaps.md`). |
| H_T-CXA-3 | STILL-BOUNDED | (no R-entry) | CP→AS runtime composer (or Memory-only-scope canonical-narrowing per ledger §11.1b α/β). |
| H_T-CXA-4 | PARTIAL | (no R-entry) | remaining ~21 of 26 OD→multi edges (or operator canonical-scope narrowing, parallel to AS-8e/8f). |

> **Gap surfaced for the roadmap:** the 4 CXA non-RETIRED rows + `CP-17` have **no `R-NNN` work-item entries** (the R-002 Surface-I decomposition pass surveyed only `harness-*/CLAUDE.md` §4.1, which excludes CXA and didn't flag CP-17 as open). Phase-8 ratification should either author CXA `R-NNN` entries or formally fold these 5 rows into the bounded-residual / Phase-2-runtime-deferred carry. **Recommend: a follow-on `R-002`-style Surface-I decomposition pass over the CXA axis + CP-17.** (Flagged at §C.)

---

# PART B — All remainings BEYOND substitutions (infra-gated Surface V + MVP config)

Surface V (`R-410..R-440`) is the "make the harness real beyond a single LOCAL developer machine" register, plus `R-100-mvp-config-discovery`. These are **not substitution rows** — they are forward feature/deployment work, mostly **operator/infra-gated** (cannot be closed by Claude alone; they need a real container runtime, a real server, a real OTLP collector, or a real secrets backend).

**Deployment matrix context.** `deployment_matrix.py` = a 12-cell `persona_tier × deployment_surface` grid; each cell maps to a sandbox-provider class. Personas: `SOLO_DEVELOPER` / `TEAM` / `ORG` (per ADR-D5 HITL palette + persona-tier plumbing). Surfaces: `LOCAL_DEVELOPMENT` / `SELF_HOSTED_SERVER` / `MANAGED_CLOUD` (ADR-D2 graduated-isolation; ADR-F4 4-tier blast-radius). MVP runs the `SOLO_DEVELOPER × LOCAL_DEVELOPMENT` cell only. Authority: ADR-D2 (per-deployment-surface sandbox provider), ADR-F4 (TIER_1..TIER_4 blast-radius), ADR-F5 (tier-aware secret-fetch), C-AS-15 §15 (sandbox tier schema).

### R-410 — Real TIER_2_CONTAINER sandbox execution
- **Summary.** Make a tool call resolved to `TIER_2_CONTAINER` actually execute inside a container boundary, not in-process FastMCP stdio. **The honest heart of Surface V.**
- **Status.** `PROPOSED` (live/infra-gated). Claude-executable up to the point a real container runtime is provisioned — but **almost certainly opens a Class 1 fork first.**
- **Vendor / mechanism.** Real container runtime — Docker / Podman / `runc`-class.
- **Persona / surface.** `≥ LOCAL` / `SELF_HOSTED` per `deployment_matrix.py` (CONTAINER provider class at TIER_2).
- **Spec cites.** `C-AS-15 §15` (sandbox tier schema); **runtime spec v1.41 §14.9.8** (`SandboxDecisionResolver` — note: no `C-RT-NN` ID; the resolver returns a tier *decision* but **no code path enforces isolation today** — `mcp_client_host.call_tool` always uses in-process FastMCP stdio regardless of tier).
- **The honest gap.** At HEAD the sandbox tier/provider are **observability + policy annotations only**. The execution-driver contract — how a resolved tier maps to an *actual* sandbox mechanism — is unspecified beyond the §14.9.8 resolver. Wiring real execution will surface a Class 1 spec fork. `council_required: conditional:nameable-tension` (C10 action-safety/blast-radius wants real isolation ⊥ C11 operator-loop/local-deployment wants minimal provisioning burden). `advisor_required: yes`.
- **Cascade.** Blocks R-411.

### R-411 — Real TIER_3 microVM sandbox execution
- **Summary.** Extend executable isolation up the ladder: `TIER_3`-resolved TOOL_STEP runs under a microVM / shared-kernel boundary; `EXTERNAL_REVERSIBLE` blast-radius enforced.
- **Status.** `PROPOSED` (infra-gated). **Depends on R-410** (inherits the same execution-driver contract question).
- **Vendor / mechanism.** gVisor / Kata / shared-kernel container.
- **Persona / surface.** per `deployment_matrix.py` (gVisor/Kata at TIER_3).
- **Spec cites.** `C-AS-15 §15`.
- **Notes.** Once R-410 settles the execution-driver pattern, R-411 + R-412 are provider-class additions. Blocks R-412.

### R-412 — Real TIER_4 full-VM / firecracker sandbox execution
- **Summary.** `TIER_4`-resolved TOOL_STEP runs in a full VM; `EXTERNAL_IRREVERSIBLE` / `FULL_VM` blast-radius.
- **Status.** `PROPOSED` (infra-gated). **Depends on R-411 + R-421** (co-gates on a real MANAGED_CLOUD surface). Deferred-far per ADR-D2.
- **Vendor / mechanism.** firecracker / full-VM.
- **Persona / surface.** **`MANAGED_CLOUD`-only** per `deployment_matrix.py` (FULL_VM reserved exclusively for the managed-cloud surface).
- **Spec cites.** `C-AS-15 §15`; ADR-D2 graduated-isolation.

### R-420 — SELF_HOSTED_SERVER deployment e2e
- **Summary.** Run the harness daemon at the first real non-LOCAL surface: a real long-running server + real OTLP collector + tier-level secrets backend. **Unblocks R-421 + R-430 + R-440.**
- **Status.** `PROPOSED` (`halt-route-to-operator` — needs operator infra provisioning before any execution).
- **Vendor / mechanism.** real long-running server + real OTLP collector + tier-level secrets backend.
- **Persona / surface.** `SELF_HOSTED_SERVER`.
- **Spec cites.** `C-RT-29 §14.18` (daemon mode, FastMCP Unix-socket); `C-OD-09 §9.1`.
- **must_pass.** daemon runs at SELF_HOSTED against a real collector; tail-keep wrapping active (`deployment_surface != LOCAL`); per-cell `base_rate` matches the SELF_HOSTED cell; secrets resolve via a tier-level backend (not env fallback). `advisor_required: yes`; `council_required: conditional:nameable-tension`.

### R-421 — MANAGED_CLOUD deployment e2e
- **Summary.** Exercise the harness at the managed-cloud surface: cloud env + cloud secrets + FULL_VM + managed collector.
- **Status.** `PROPOSED` (operator/infra-gated). **Depends on R-420.**
- **Vendor / mechanism.** cloud environment + cloud secrets manager + FULL_VM + managed OTLP collector.
- **Persona / surface.** `MANAGED_CLOUD`.
- **Spec cites.** `C-RT-29 §14.18`; `C-OD-13 §13.1`. Secrets via in-sandbox encrypted-fs per ADR-F5; MANAGED_CLOUD per-cell sampler + redaction posture.

### R-430 — OTLP tail-keep preservation validation
- **Summary.** Verify the §10.2 classification-trigger preservation semantic against a **real** OTLP collector (the drop/keep decision is collector-side).
- **Status.** `PROPOSED` (infra-gated). **Depends on R-420.**
- **Vendor / mechanism.** real OTLP collector.
- **Persona / surface.** `SELF_HOSTED+`.
- **Spec cites.** `C-OD-09 §9.1`, `§9.2`.
- **Notes.** `TailKeepSpanProcessor` buffer logic already exists in-process and is bypassed at LOCAL by design (§9.1 head-based mandate). **This is the surface that the OD-3 batch-51 audit reclassified out of the OD-3 retirement gate** — observing collector-side preservation is *production-feature-validation*, NOT an X-AL-2 retirement criterion. (See §A.4 OD-3 + ledger §11.4i.)

### R-440 — Tier-level secrets backend
- **Summary.** Wire a real tier-level secrets backend beyond the LOCAL keyring + env-fallback shipped today.
- **Status.** `PROPOSED` (infra-gated). **Depends on R-420.**
- **Vendor / mechanism.** Vault / cloud secrets manager.
- **Persona / surface.** `SELF_HOSTED` (tier-level backend) vs `MANAGED_CLOUD` (in-sandbox encrypted-fs).
- **Spec cites.** ADR-F5 §1; `C-AS-05 §5.1` `fetch_secret`.
- **Notes.** At HEAD `provider_secrets.py` documents tier-level vs in-sandbox backends but ships **only** LOCAL keyring + env-fallback (PR #16 binding-fix). Mirror precedent `[[pr-16-keyring-env-fallback-adr-f5]]`.

### R-100-mvp-config-discovery — `harness.toml` auto-discovery
- **Summary.** Spec §3.7 declares `harness.toml` is discovered at "workspace root" by default; the impl never wired it. `DEFAULT_CONFIG_FILE_NAME` (`config_source.py:43`) is a dead constant. **Does NOT block the MVP** (worked around in R-100 via `just run` passing `--config`).
- **Status.** `BLOCKED` (phase-7) on `.harness/class_1_fork_harness_toml_default_discovery_unimplemented.md` (PROPOSING) — needs operator fork-ratification.
- **Vendor / mechanism.** n/a (CLI config-load).
- **Persona / surface.** `LOCAL` (`SOLO_DEVELOPER`).
- **Spec cites.** `C-RT-30 §3.7` (line 391); `C-RT-29 §14.18.1`.
- **The gap.** "Workspace root" is undefined (CWD vs the config's own `repository_root` — circular). Fork readings: (A) CWD discovery / (B) upward search / (C) spec amendment dropping the clause. This is the only **non-infra-gated** Part B item (Claude-executable once the fork is ratified). Mirror precedent `[[harness-run-minimal-config-recipe]]`.

---

# PART C — Flagged Phase-8 ratification items (operator owns these)

1. **The substantive-RETIRED integer.** Per-row truth reconciles to **`46–47 RETIRED` (pipeline-advanced 49–50/54)**, not the published `48/54`. The delta is the un-folded CXA accounting (ledger §11.1a line 278: CXA corrective "never adopted into the cumulative — pending operator routing") + the `CP-17` SB-INDEF reclassification not framed as open + the CP 21-vs-22 / AS-3↔AS-9 bookkeeping ambiguities (§A.3). **No work regressed.** Operator decides: adopt the corrected `46–47` (and which integer), or keep the published `48` with a documented carve-out. **This draft does NOT overwrite the dashboard's `48/54`.**
2. **CXA + CP-17 work-item coverage.** 5 open rows (`CXA-1/2/3/4` + `CP-17`) have no `R-NNN` entries. Recommend an `R-002`-style Surface-I decomposition pass over the CXA axis + CP-17, or a formal fold into the Phase-2-runtime-deferred / bounded-residual carry.
3. **Bounded-residual sign-offs** for `AS-8e` (R-005), `AS-8f` (R-006), `OD-6` (batch-51) — the Phase-8 disposition the operator owns per Surface VIII.
4. **The genuinely-open MVP substitution** `OD-4` (R-008): §13.1 per-session toggle + §13.2 tokenization. The only non-deferred, non-infra-gated substitution remaining.

---

## Provenance + method

- **48/54 is internally impossible** — sourced at ledger §11.5 (line 449-450) `48 RETIRED / 49 pipeline-advanced`, contradicted by ≥3 PARTIAL rows (OD-4 §A.4 + CXA-1/CXA-4 §A.5).
- **CXA never folded in** — ledger §11.1a line 278 (verbatim: corrective counts adoption "is a separate doc-hygiene scope decision pending operator routing").
- **Stale-subagent guard** — a first-pass compilation read the 2026-05-20 ledger §7 snapshot and mis-reported CP-1..5/10/13 as STILL-BOUNDED; corrected against live `harness-cp/CLAUDE.md` §4.1 (CP-1 RETIRED line 232; CP-axis 21/22, PARTIAL bucket empty since batch-48). CXA rows confirmed stable batch-42→HEAD (only batch-42 transited CXA-4).
- **Ledger self-inconsistency is documented, not invented** — e.g. batch-48 cardinality line `harness-cp/CLAUDE.md:177` reads "45 + 0 + 3 + 0 + 3 = 51 active + 3 indef = 54" (internally contradictory); the ledger admits "cardinality drift propagated through every batch-cardinality check since batch-3" (§11.1a line 274).
- **Advisor pass** (this arc) confirmed the thesis as load-bearing, directed the `46–47` range framing + the two named bookkeeping ambiguities, and directed *not* overwriting the operator-ratified `48/54`.
