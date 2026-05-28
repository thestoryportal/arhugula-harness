# Class 1 Fork — H_T-AS-8f `managed_agents.*` namespace producer-site absence + production-only exclusion semantic

**Status:** ✅ RATIFIED 2026-05-28 (operator AskUserQuestion same-session as filing per accelerated single-session ratification cycle; apply arc opens at next commit)

**Operator ratification (2026-05-28):**

| Q | Answer | Note |
|---|---|---|
| Q1 | **(C) DEFER INDEFINITELY (mirror AS-8e files.* per runtime spec v1.17 §14.C ratification precedent)** | Honors AS spec C-AS-13 §13.2 design declaration excluding managed_agents at local-development for all workload classes; advisor-blessed; ~1 commit apply arc. Reading B (operator-opt-in mirror AS-8d) dropped pre-ratification as category error per advisor pre-substantive consultation. |

**Filed at:** 2026-05-28

**Filer:** spec-writer skill (FM-1 trigger at H_T-AS-8f gate-text re-verification, 25th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`)

**Surfaced by:** Empirical re-verification of H_T-AS-8f retirement gate at `harness-as/CLAUDE.md:174` immediately after AS-8d apply-arc close (`2aa2687` 2026-05-28). Re-verification surfaced that AS-8f's structural posture **diverges from AS-8d** and **matches AS-8e** along the production-deployment-surface-exclusion axis — the sister-fork template does NOT transplant.

**Classification:** Class 1 (halt-execution; design-declaration cite-anchoring + retirement-gate routing decision surfaced at Phase 7 execution per X-AL-3 + Workflow v1.10 §2.7.6 + Phase_7_Kickoff_Prompt.md §6).

---

## §1 — The gap

AS spec C-AS-14 §14.5 declares a 3-attribute `managed_agents.*` namespace on a `managed_agents.runtime` span:

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `managed_agents.runtime_ms` | int | Runtime in milliseconds | unbounded (metric) |
| `managed_agents.session_id` | string | Per-session identifier | high (per-session) |
| `managed_agents.billable_seconds` | float | × $0.08/3600 = cost | unbounded (metric) |

AS-side schema substrate LANDED at U-AS-31 (`MANAGED_AGENTS` enum member + 3-attribute carrier at `harness-as/src/harness_as/anthropic_attribute_namespaces.py:211-216`). Sampling policy LANDED at U-AS-32 (`AuditFloorScope.MANAGED_AGENTS_RUNTIME_ALWAYS_SAMPLED` at `harness-as/src/harness_as/anthropic_primitive_sampling.py:81`; `managed_agents.runtime → HEAD_1_0_ALWAYS` at line 51). OD-side ingestion LANDED at `harness-od/src/harness_od/namespace_map.py:126` + `harness-od/src/harness_od/content_structure_discipline.py:138-141` + `harness-od/src/harness_od/as_source_namespace_verification.py:51` + `harness-od/src/harness_od/sampling_mode.py:119`.

**Gap 1 — no producer site at H_T runtime.** `grep -rn "managed_agents" harness-runtime/src/` returns **ZERO** matches. No `managed_agents.runtime` span is emitted by any callsite in H_T runtime.

**Gap 2 — no managed_agents invocation surface at H_T.** H_T runtime does NOT integrate the Anthropic managed_agents beta SDK. There is no `AgentCreateParams` consumption site, no `managed_agents.client` binding, no Anthropic Agents API call invocation chain. The producer-side absence is **not** an unauthored emission step on an existing event — it is the absence of the entire event (no managed_agents invocation happens at H_T).

**Gap 3 — design declaration EXCLUDES managed_agents at local-development surface.** The exclusion is canonically declared at THREE anchors:

- **ADR-D3 v1.1 §1.8.1** declares the `managed_agents.runtime` span scope verbatim: `managed_agents.runtime (Managed Agents only; v1.1 — F2-04 namespace unified)`. The parenthetical "Managed Agents only" is the design statement — emission is gated on the Managed Agents primitive being adopted, not on H_T-internal events.
- **AS-axis spec C-AS-13 §13.2 adoption-depth matrix** carries `surface_qualifier = DeploymentSurface.LOCAL_DEVELOPMENT` with note `"X at local-development"` across **all four workload classes** (software-engineering / content-creation / pipeline-automation / research). Per `harness-as/src/harness_as/anthropic_primitive_adoption.py:61` (`MANAGED_AGENTS = "managed_agents"`) the canonical adoption-depth binding for this primitive is **excluded at local-development** uniformly.
- **AS-axis enforcement test** at `harness-as/tests/test_anthropic_primitive_adoption.py:183` (`test_managed_agents_excluded_at_local_development`) asserts `binding.surface_qualifier is DeploymentSurface.LOCAL_DEVELOPMENT` AND `"X at local-development" in binding.notes` for every workload class — failing if the exclusion is ever lifted at local-dev binding.

Net consequence: **H_T cannot emit `managed_agents.runtime` spans at its current operational surface (local-development bootstrap) because (i) H_T has no managed_agents invocation site and (ii) the AS spec design-declaration explicitly EXCLUDES managed_agents adoption at this surface.** The producer-side absence is not a defect; it is a faithful materialization of the spec's deployment-surface-conditioned adoption-depth matrix.

---

## §2 — Two readings (Reading B dropped as category error)

**Reading A — IN-SCOPE-NOW: production-deployment binding authoring.** Author Anthropic managed_agents beta SDK integration at H_T runtime + ManagedAgentsSpanEmitter carrier + production-deployment-surface composer extension. Requires:

- New H_T runtime contract surface for managed_agents primitive (parallel to but structurally distinct from Memory tool C-RT-22 — Memory is client-side per ADR-D3 §1.1 #11; managed_agents is server-side per ADR-D3 distinct from Memory tool).
- New `harness-runtime/src/harness_runtime/lifecycle/managed_agents_dispatch.py` module per Memory-tool precedent (`memory_tool_dispatch.py` separate-module convention).
- New `RuntimeConfig.managed_agents_config: ManagedAgentsConfig | None = None` field + stage factory + composer-body invocation.
- AS spec §14.5 footer producer-site reference (sibling to v1.5 §14.7 memory.* footer pattern).
- AS spec C-AS-13 §13.2 adoption-depth matrix amendment to lift the LOCAL_DEVELOPMENT exclusion at managed-cloud surface only — preserving the local-dev exclusion verbatim.

Pros: closes AS-8f STILL-BOUNDED → RETIRED at production deployment surface. Demonstrates a second AS-axis primitive landing at a managed-cloud surface (after the eventual Files arc).

Cons: requires Anthropic managed_agents beta SDK availability + stability + integration scope. H_T at local-development surface CANNOT exercise the binding — the e2e gates on production deployment surface. The scope is materially heavier than AS-8d (skill.*) which could be exercised at local-dev. Estimated cost: ~8-12 commits including runtime spec extension + plan extension + 3-attribute computation at SDK callback + production binding + production e2e exercise. **Blocked at local-dev** — even with binding-chain authored, retirement criterion B requires production-surface empirical observation, which is NOT available in-CLI.

**Reading B (DROPPED as category error).** A naive sister-fork shape would propose "IN-SCOPE-MVP: schema-stub + operator-opt-in emission" mirroring AS-8d Reading B. **This reading does not exist meaningfully for AS-8f.** The AS spec's adoption-depth matrix declares the design statement that managed_agents is excluded at local-development for all workload classes. An operator-opt-in hook at local-dev would either be dead code (violating Q1=B's "MET-when-bound" semantic) or would force-emit at a surface the spec explicitly excludes (violating X-AL-3). The schema-stub already exists (carrier MET); there is no intermediate "stub + gated emission" shape between Reading A (production binding) and Reading C (DEFER INDEFINITELY).

**Reading C — DEFER INDEFINITELY (mirror H_T-AS-8e `files.*` per runtime spec v1.17 §14.C).** Mark AS-8f as STILL-BOUNDED-INDEFINITELY per X-AL-2 bounded-residual; document the production-deployment-surface gate as design-declaration-honored rather than design-extension-deferred; route resolution to a future H_T managed-cloud surface arc at operator-discretion timing.

Pros: discipline-pure under X-AL-3 (no Phase-7-time design extension at a surface the spec explicitly excludes at H_T's current operational binding). Pure honoring of the AS spec C-AS-13 §13.2 adoption-depth matrix design declaration. Matches AS-8e precedent for "schema-substrate-MET + production-surface-design-gated". No carrier-text staleness (the existing CLAUDE.md row "Gates on Anthropic managed_agents beta SDK integration into H_T (separate H_T primitive landing)" already names the gate accurately — fork doc upgrades it to canonical INDEFINITE routing per runtime spec §14.C parallel).

Cons: AS-axis active-substitution view ceiling at 8/9 RETIRED-or-RETIRE-READY (AS-8f joins AS-8e in the INDEFINITE bucket; AS-axis falls from 11 active substitutions to 9 active substitutions post-classification). No additional in-CLI close achievable for AS-8f at any future in-CLI session.

Estimated cost: **1 commit** — STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY row refresh at `harness-as/CLAUDE.md:174` + AS spec v1.7 §14.5 footer note documenting production-only exclusion + runtime spec NEW §14.D (sibling to §14.C Files-indefinite-defer ratification) declaring managed_agents-indefinite-defer at local-dev binding + workspace ledger v2 batch-26 retirement event filing.

---

## §3 — Operator decision

**Q1 — Scope reading.**

- (A) IN-SCOPE-NOW production-deployment binding authoring + AS spec §14.5 footer producer-site reference + AS C-AS-13 §13.2 adoption-depth matrix amendment to permit managed-cloud surface binding
- (C) **DEFER INDEFINITELY** (mirror H_T-AS-8e files.* per runtime spec v1.17 §14.C ratification precedent) — STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY + runtime spec NEW §14.D declaration **(RECOMMENDED — advisor-blessed)**

**Note on absent Q2-Q5.** AS-8d's fork doc carried Q2 (activation-surface design) / Q3 (enum disposition) / Q4 (loader+emitter residence) / Q5 (cross-axis cascade) because the activation surface design was the substantive open question. AS-8f has **no activation surface to design** — managed_agents is invoked by the Anthropic API surface (server-side per ADR-D3 §1.1 #10), not at an H_T-internal event. There is no taxonomy-divergence, no residence ambiguity, no cross-axis edge candidate (OD ingestion already declared at `namespace_map.py:126`). The Q-set is genuinely small: Q1 alone determines the routing.

**Recommendations (advisor-blessed):** Q1 = **C** (DEFER INDEFINITELY). Justification: (i) AS spec C-AS-13 §13.2 design declaration EXCLUDES managed_agents at local-development for all workload classes; (ii) H_T's current operational surface IS local-development bootstrap; (iii) honoring the design declaration via INDEFINITE routing is discipline-pure under X-AL-3; (iv) Reading A is blocked-at-local — even if authored, retirement criterion B (production-surface empirical observation) cannot be exercised in-CLI; (v) AS-8e precedent for INDEFINITE routing at production-deployment-surface-gated namespaces is the structural template.

---

## §4 — Downstream cascade

### IF Q1 = A selected

**Spec amendments:**
- Runtime spec v1.32 → v1.33 — NEW §14.NN C-RT-NN `ManagedAgentsSpanEmitter` contract surface + Anthropic managed_agents beta SDK integration Protocol declaration. Sibling to §14.12 C-RT-22 (`MemoryToolRegistry`) Memory-tool precedent but structurally server-side per ADR-D3 §1.1 #10 vs #11 distinction.
- Runtime spec — NEW field `RuntimeConfig.managed_agents_config: ManagedAgentsConfig | None = None` at §3 C-RT-02.
- Runtime spec — NEW field `HarnessContext.managed_agents_emitter: ManagedAgentsSpanEmitter | None` at §4 C-RT-04.
- AS spec v1.7 → v1.8 — §14.5 footer note documenting H_T-as-managed-agents-consumer producer-site reference (sibling to §14.7 memory.* v1.5 footer pattern).
- AS spec v1.7 → v1.8 — §13.2 adoption-depth matrix amendment: lift LOCAL_DEVELOPMENT exclusion at managed-cloud + hybrid surfaces; PRESERVE exclusion at local-development. Test `test_managed_agents_excluded_at_local_development` PRESERVED (local-dev exclusion verbatim).

**Plan amendments:**
- Runtime plan v2.28 → v2.29 — NEW L-N cluster (~5-8 atomic units) decomposing the C-RT-NN landing.
- AS plan v1.4 — §0 change-note absorbing AS spec §14.5 footer + §13.2 matrix amendment (1 new AC for managed-cloud surface binding test).

**Production binding:**
- NEW `harness-runtime/src/harness_runtime/lifecycle/managed_agents_dispatch.py` — `ManagedAgentsSpanEmitter` class + Anthropic managed_agents beta SDK invocation surface + emit method computing `runtime_ms` + `session_id` + `billable_seconds` from SDK response.
- Stage-N factory at `harness-runtime/src/harness_runtime/bootstrap/` — `materialize_managed_agents_emitter_stage`.
- Production-deployment-surface composer extension — managed-cloud-only invocation gate.

**Cross-axis cascade:**
- Q5 implicit β (no new CXA edge): CXA v2.15 unchanged. OD ingestion already declared at `namespace_map.py:126` + `as_source_namespace_verification.py:51` + sampling at `sampling_mode.py:119`. Cross-namespace ingestion at OD §C-OD-05 + §C-OD-06 already enumerates `managed_agents.` in the 7-AS-source-namespace set; no new ingestion contract owed.

**Retirement gate transit:**
- AS-8f STILL-BOUNDED → STILL-BOUNDED-AT-PRODUCTION (carrier MET at runtime; emission MET-when-deployed-to-managed-cloud + operator-bound `RuntimeConfig.managed_agents_config` non-None + Anthropic managed_agents beta SDK active). NOT RETIRE-READY at apply-arc close — RETIRE-READY transit gates on production deployment, NOT on in-CLI carrier-binding-chain landing alone.
- True RETIRED gates on operator deployment-time exercise observing `managed_agents.runtime` span at production tracer backend. NOT an in-CLI close at any in-CLI session.

### IF Q1 = C selected (RECOMMENDED)

**Spec amendments:**
- AS spec v1.7 → v1.8 — §14.5 footer note documenting H_T-runtime managed_agents-production-only exclusion + STILL-BOUNDED-INDEFINITELY routing per X-AL-2 bounded-residual + cite to AS C-AS-13 §13.2 adoption-depth matrix design declaration + cite to ADR-D3 §1.8.1 "Managed Agents only" span scope.
- Runtime spec v1.32 → v1.33 — NEW §14.D `H_T-AS-8f managed_agents.* indefinite-defer ratification` sub-section (sibling to v1.17 §14.C `H_T-CP-17 files.* indefinite-defer ratification`). Declares: (i) managed_agents arc deferred indefinitely at local-development binding per AS spec C-AS-13 §13.2 design declaration; (ii) no managed_agents executable consumer contract authored at v1.33; (iii) re-opens at future H_T managed-cloud surface arc when production deployment materializes.

**Plan amendments:**
- AS plan v1.4 — §0 change-note absorbing AS spec §14.5 footer (no new AC; preserves existing `test_managed_agents_excluded_at_local_development` enforcement).
- Runtime plan v2.28 — NO amendment.

**Production binding:**
- NONE.

**Cross-axis cascade:**
- NONE. (OD ingestion already declared; namespace-side schema already MET; the deferral is at producer-side production-binding only.)

**Retirement gate transit:**
- AS-8f STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY.
- Workspace ledger v2 batch-26 retirement event filed at `.harness/phase-7d-retirement-events-batch-26.md`.
- AS-axis active-substitution view (excluding INDEFINITE deferrals): **8/9 RETIRED-or-RR (88.9%)** preserved (was 8/10 = 80.0% pre-classification; AS-8f leaves the active denominator).
- AS-axis raw ledger: 8/11 RETIRED + 1/11 RETIRE-READY + 0/11 PARTIAL + 2/11 STILL-BOUNDED-INDEFINITELY = **9/11 pipeline-advanced** (was 8/11 RETIRED + 1 RR + 0 P + 2 SB; SB-INDEFINITE is the terminal state for production-surface-gated namespaces under X-AL-2 bounded-residual).

---

## §5 — Pattern catalogued

**Sub-species: `production-only-namespace-exclusion-at-design-declaration`.**

Same structural shape as `H_T-AS-8e files.*` (STILL-BOUNDED-INDEFINITELY per runtime spec v1.17 §14.C). Both share:

- AS-side schema substrate LANDED at carrier-namespace declaration.
- OD-side ingestion substrate LANDED at cross-namespace ingestion table.
- Runtime producer-site ABSENT.
- Production-deployment-surface gate explicit at design declaration (NOT a defect; a faithful materialization of the spec's deployment-surface-conditioned adoption posture).
- Fork doc files INDEFINITE routing at Phase 7 execution time per X-AL-3 (no silent design extension at a surface the spec explicitly excludes).

**Distinctive feature of AS-8f vs AS-8e:** AS-8e (files.*) deferral was negotiated at the H_T-CP-16/17 fork resolution (Memory-only scope ratified, Files-arc-deferred 2026-05-23). AS-8f (managed_agents.*) deferral is **already implicit at the AS spec C-AS-13 §13.2 adoption-depth matrix design declaration** — the fork doc surfaces the cite-anchoring (matrix + ADR-D3 §1.8.1 + enforcement test triad) and ratifies INDEFINITE routing without requiring a new Memory-vs-managed_agents scope negotiation. Cleaner ratification surface than AS-8e.

**Distinctive feature of AS-8f vs AS-8d:** AS-8d (skill.*) Reading B operator-opt-in was viable because skill.* is REQUIRED across all workload classes — H_T at local-development can opt into emission. AS-8f has no such viability — Reading B is a category error because the design declaration excludes the namespace at local-dev. Sister-fork shape does NOT transplant. Documented at §2 Reading B dropped.

**Pattern repeated since AS-8e:** 2nd application of `production-only-namespace-exclusion-at-design-declaration` sub-species. First was AS-8e files.* (2026-05-23). Now AS-8f managed_agents.* (2026-05-28). Predicted future application: any Anthropic primitive with `surface_qualifier ≠ LOCAL_DEVELOPMENT` adoption-depth matrix rows would inherit the same shape.

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | spec-writer skill (FM-1 trigger at H_T-AS-8f gate-text re-verification) |
| Source of detection | Empirical re-verification at `harness-as/CLAUDE.md:174` post-AS-8d apply-arc close (`2aa2687` 2026-05-28); 25th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`. Advisor pre-substantive consultation surfaced the structural-divergence-from-AS-8d framing + Reading-B-as-category-error + AS-8e-as-template-not-AS-8d. |
| Classification | Class 1 (halt-execution; design-declaration cite-anchoring + retirement-gate routing decision surfaced at Phase 7 execution per X-AL-3 + Workflow v1.10 §2.7.6) |
| Ratification owed | Operator AskUserQuestion at fork doc re-open — Q1 only (A vs C) |
| Apply-arc shape | Per Q1=C (RECOMMENDED): ~1 commit (AS spec §14.5 footer + runtime spec NEW §14.D + harness-as/CLAUDE.md row refresh + batch-26 retirement event filing). Per Q1=A: ~8-12 commits including Anthropic managed_agents beta SDK integration scope. |
| Stop-point | Filing-only at PROPOSING status. Ratification + apply arc deferred to operator-discretion follow-on session per advisor convention. |
| Status | PROPOSING |

---

## §7 — Companion ledger anchors

- `harness-as/CLAUDE.md:174` H_T-AS-8f row — STILL-BOUNDED, current gate-text "No producer site. Gates on Anthropic managed_agents beta SDK integration into H_T (separate H_T primitive landing). Beta SDK shape: `AgentCreateParams` per Anthropic SDK docs; integration is a separate multi-commit arc" — refresh at Q1=C apply arc to STILL-BOUNDED-INDEFINITELY with cite to this fork doc + runtime spec §14.D + AS spec §14.5 footer.
- `.harness/phase-7d-retirement-ledger-v2.md` — AS-8f sub-row decomposition (per batch-24 ledger v2 layer) currently carries STILL-BOUNDED; refresh at Q1=C apply arc to STILL-BOUNDED-INDEFINITELY.
- `design-substrate/Spec_Action_Surface_v1.md` §14.5 — production-only exclusion footer note authored at Q1=C apply arc.
- `design-substrate/Spec_Harness_Runtime_v1.md` §14.D (NEW) — indefinite-defer ratification authored at Q1=C apply arc, parallel to existing §14.C Files-indefinite-defer.
- `design-substrate/Phase_7_Meta_Architecture_v1.md` §2.2 H_T-AS-8 row — UNCHANGED (monolithic-view AS-8 row preserved verbatim; sub-row decomposition layer carries AS-8f INDEFINITE classification at retirement-ledger v2 + harness-as/CLAUDE.md only, per X-AL-3 + advisor pre-substantive consultation 2026-05-28 decision to preserve Meta-Arch §2.2 view verbatim).
