# Adversarial Review — Phase 2 Session 4 runtime spec

## Summary
- **Mode:** Phase-7 pre-implementation review (P2-S4-CK — Session 4 close gate before Session 5 unit landing opens)
- **Artifact reviewed:** `design-substrate/Spec_Harness_Runtime_v1.md` (13 contracts C-RT-01..C-RT-13; first net-new axis spec; adapted trace convention)
- **Anchoring inputs cross-checked:** F-P2-1..F-P2-5 fork resolutions; Session 3 plan v2 at `.harness/phase-2-session-3-track-a-atomic-decomposition.md`; existing axis specs (IS v1, AS v1.3, CP v1.3, OD v1.4) as discipline benchmark; ADR-F1..F5 + ADR-D1/D2/D6 + ADD v1.3 (per CLAUDE.md version pins); `Project_Workflow_v1_8.md` §2.5 specification exit criteria + §2.5.2 Pattern P1-PHASE-5 / P2-PHASE-5 discipline clauses
- **Date:** 2026-05-19
- **Finding count by class:** Class 3: 0 · Class 2: 7 · Class 1: 3
- **Highest-severity finding:** F2-01 (failure-mode taxonomy divergence from CP C-CP-05 canonical fail-class enumeration)
- **Disposition recommendation:** **Current-phase spec revision before Session 5 unit landing opens** per §4.1.2. No Class 3 findings; no Phase-7 §2.7.6 fork engaged; no upstream-phase artifact revision required at this point (the trace-novelty open question is correctly surfaced in §15 #1 and does not force back-flow at this review).

---

## Class 3 findings (severe — phase re-opening)

*None.*

Discriminator (c) framing-contamination walk: spec preserves multi-LLM (3 async providers), persona-uncommitted (front-matter explicit), stack-honored (Pydantic v2 / asyncio / no LiteLLM / hand-rolled retry-breaker / per-provider SDKs), deployment-surface uncommitted (driven by `RuntimeConfig.deployment_surface`). Pass.

Discriminator (b) upstream-phase-revision walk: trace-discipline adaptation is *explicitly surfaced* in §"Trace-discipline novelty" as a candidate Class 1 review surface; the spec does not silently assume PRD coverage. The adaptation question is correctly *deferred* to this review, not *absorbed* — which is the correct posture. If reviewer (this skill) had determined the adaptation insufficient, the finding would be Class 3 with mandatory PRD v1.2 amendment back-flow. **The adaptation is judged sufficient at this review** — the runtime axis genuinely enables (does not satisfy) PRD requirements; the substitution mapping is principled; the open question is acknowledged. No PRD amendment required at this gate. (Re-evaluable at any future P5-CK-style aggregate review.)

---

## Class 2 findings (moderate — current-phase spec revision)

### F2-01 — Failure-mode taxonomy diverges from CP-axis canonical fail-class enumeration
- **Location:** C-RT-02 §2 ("permanent / transient / partial-rollback-required"); C-RT-05 §5 ("permanent / transient / permanent (auth) / degraded"); C-RT-06 §6 ("permanent / transient"); C-RT-07 §7 ("permanent / transient / degraded / permanent (degraded harness)"); C-RT-08 §8 ("permanent / permanent / (downstream)"); C-RT-10 §10 ("partial / permanent"); C-RT-11 §11 ("transient").
- **Defect:** The runtime spec introduces fail classes (`permanent`, `transient`, `degraded`, `partial`, `partial-rollback-required`, `permanent (degraded harness)`) without explicit alignment to the CP-axis canonical fail-class enumeration the workspace has already settled. Per workspace `CLAUDE.md` §1.1, CP owns "retry / breaker / idempotency" and per `Spec_Control_Plane_v1_3.md` the validator-fail taxonomy is a 5-class enumeration. Spec discipline §"Failure-mode taxonomy completeness" in this skill's substrate notes that fail classes should align to the canonical set (per C5 / C-CP-* contract) with `cause_attribution`. The runtime spec creates a parallel enumeration without explanation.
- **Discriminator:** (a) — substantive content gap in current-phase artifact; resolution does not require CP-spec revision (runtime can re-state in CP-canonical classes OR can explicitly declare runtime-axis-local classes with rationale).
- **Evidence:** Direct quotes above. CP spec exposes a 5-class validator-fail taxonomy per landed module `harness_cp.validator_fail_taxonomy`; the runtime spec does not cite this taxonomy in any failure-mode table.
- **Decision-claim label:** *proposing* — two readings supported by the text:
  - **Reading 1:** runtime axis legitimately needs runtime-specific classes (bootstrap-stage-failure, partial-rollback) that don't fit the CP validator-fail taxonomy (which is workflow-step-level). Resolution: declare runtime-axis-local fail-class set explicitly with rationale; cite CP taxonomy as orthogonal.
  - **Reading 2:** runtime spec should reuse the CP taxonomy (extended if necessary via a CP spec amendment). Resolution: surface as a Class 1 fork to CP back-flow.
  - Operator picks the reading; reviewer does not.
- **Resolution path:** Add an explicit subsection in §"Trace-discipline novelty" or a new contract C-RT-14 enumerating the runtime fail-class set and its relationship to CP's validator-fail taxonomy. If Reading 2 is chosen, file CP amendment per `Project_Workflow_v1_8.md` §2.7.6.

### F2-02 — ADR scope table cites ADR sections by descriptive label, not verified §-numbers
- **Location:** §"ADR scope" table — every row uses §-labels like "§Multi-LLM", "§Observability substrate", "§State ledger primitive", "§Workflow lifecycle", "§Sandbox tier", "§OTel schema". Same pattern repeats throughout C-RT-NN contracts ("ADR-F5 v1.1 §Observability substrate (tracer-provider is foundational)").
- **Defect:** Pattern P2-PHASE-5 body-citation-alignment discipline (§2.5.2 of workflow) requires "Citations to upstream artifacts ... bumped to the latest revised version." Implicit: citations are to *specific verified sections*. Existing axis-spec citations (per Explore agent's structural survey of IS v1, CP v1.3, OD v1.4) follow the format `ADR-F2 v1.2 §Decision` or `ADR-D3 v1.1 §1.5 + §1.7.1` — version-pinned with specific section numbers (or `§Decision` / `§Consequences` for canonical ADR top-level sections). The runtime spec uses descriptive content labels (`§Multi-LLM`) that may or may not correspond to actual ADR section titles.
- **Discriminator:** (a) — substantive content fidelity gap; resolution requires verifying each ADR section name and either bumping the citation to the canonical name or to a specific §-number.
- **Evidence:** Direct quotes above. Compare against the canonical citation format observed in OD/CP/IS/AS specs per the Explore agent's structural survey.
- **Decision-claim label:** *decided* — the spec consistently uses descriptive labels; the canonical convention is verified-section-titles or §-numbers.
- **Resolution path:** Read each cited ADR file (`design-substrate/ADR-F1.md`, etc.), verify section structure, and replace descriptive labels with verified `§<TitleOrNumber>` form. If an ADR has no section matching the spec's intended meaning, treat as a candidate ADR-amendment back-flow surface.

### F2-03 — Cross-axis citation substrate table cites axis-spec contracts without verified §-numbers
- **Location:** §"Cross-axis citation substrate" table — rows like "`Spec_Information_Substrate_v1.md` | C-IS-01 path-class taxonomy; C-IS-05 state-ledger entry shape (6-field); C-IS-07/08/09/11 ledger composition primitives; C-IS-14/15 shadow-Git checkpoint/rollback".
- **Defect:** Same pattern as F2-02 but for cross-axis spec citations. The spec asserts contract IDs (C-IS-05, C-AS-02, C-CP-04, C-OD-12, etc.) without §-pinned citations and without verifying those contract IDs match the source spec's actual contract enumeration. Existing axis-spec cross-axis tables (per Explore agent's structural survey) cite as `Spec_Information_Substrate_v1.md C-IS-05 §5 (state-ledger entry shape signature)` — file + contract + §-number + descriptive label.
- **Discriminator:** (a) — citation precision below canonical bar.
- **Evidence:** Direct quote above; contrast with canonical format from Explore agent's survey.
- **Decision-claim label:** *decided*.
- **Resolution path:** Verify each cited contract exists at the cited spec file with the asserted ID; bump every citation to include `§N` section pin. If any cited contract ID does not resolve (e.g., C-AS-02 may be named differently), surface as candidate axis-spec back-flow.

### F2-04 — `RuntimeConfig` and `HarnessContext` schemas omit version-evolution discipline
- **Location:** C-RT-03 §3 (`RuntimeConfig`); C-RT-04 §4 (`HarnessContext`); C-RT-09 §9 (`RunResult`). All three schemas declare fields, types, and invariants; none state how schema evolution is handled across runtime-spec versions.
- **Defect:** Spec-discipline §"Schema completeness" check question: "every data schema has field-level types, required/optional discipline, validation rules, **and version-evolution discipline**." The three Pydantic schemas omit the version-evolution dimension. What happens when v2 adds a new required field to `RuntimeConfig`? Are configs from v1 callers rejected, auto-migrated, or warned? `HarnessContext` is internal so this is lower-stakes, but `RuntimeConfig` and `RunResult` cross the public API boundary.
- **Discriminator:** (a) — schema completeness gap.
- **Evidence:** Search of C-RT-03/04/09 contract bodies — `model_config = ConfigDict(frozen=True, ...)` is specified but no version-evolution clause.
- **Decision-claim label:** *decided*.
- **Resolution path:** Add a "Version evolution" sub-bullet to each schema's Invariants section stating the migration / breakage discipline. Likely: `RuntimeConfig` adds-required-field is a v2 major bump; adds-optional-field is v1.1 minor; deprecated-field stays through one minor version with warning.

### F2-05 — `run()` idempotency / concurrency posture unstated
- **Location:** C-RT-08 §8 `run()` Python API contract.
- **Defect:** Spec-discipline §"Contract precision" check: every interface signature has "typed inputs, typed outputs, error contract, **idempotency posture**, and observability obligations." C-RT-08 covers inputs, outputs, errors, observability (via lifecycle events implicitly through C-RT-02), but does not state idempotency. Concrete unanswered questions:
  - Is it safe to call `run(workflow_A)` concurrently from two coroutines? (bootstrap-per-call implies a fresh `HarnessContext` per call, but two concurrent calls would each register a TracerProvider — and `set_tracer_provider` is one-per-process per C-RT-06; concurrent calls would fail at the second)
  - Is calling `run(workflow_A)` twice in series after a successful first call equivalent to two independent runs?
- **Discriminator:** (a) — contract precision gap below spec-discipline bar.
- **Evidence:** C-RT-08 Invariants section enumerates async-only, single-workflow-object input, config-None default, bootstrap-per-call OR cached-context distinction, unknown-type rejection. Idempotency / concurrency posture absent.
- **Decision-claim label:** *decided*.
- **Resolution path:** Add an idempotency-and-concurrency invariant clause to C-RT-08. Likely: serial calls are safe and equivalent to independent runs; concurrent calls from the same process surface typed `ConcurrentRunNotSupported` (C-RT-06's one-TracerProvider-per-process forces this in Track A; Track B may add a cached-context model that supports it).

### F2-06 — `HarnessContext.providers` field types value as `AsyncClient` (non-existent common base)
- **Location:** C-RT-04 §4 table row: `providers | dict[str, AsyncClient] | 3a | {'anthropic': AsyncAnthropic, 'openai': AsyncOpenAI, 'ollama': AsyncClient}`.
- **Defect:** `AsyncClient` is not a common base class across `anthropic.AsyncAnthropic`, `openai.AsyncOpenAI`, and `ollama.AsyncClient` — these are three independent classes from three independent SDKs. There is no shared interface they implement. The type annotation `dict[str, AsyncClient]` either references a non-existent symbol or is intended as a placeholder. Same ambiguity at C-RT-05 close column ("`await client.close()`" for each — but the actual method names and signatures differ across the three SDKs).
- **Discriminator:** (a) — schema completeness gap; the spec needs to specify either a runtime-defined protocol/abstraction the three clients implement, or `dict[str, Any]` with a per-provider lookup discipline.
- **Evidence:** Direct quote above; cross-reference with the `anthropic`, `openai`, `ollama` SDK type hierarchies (per Explore agent: three independent classes, no common ABC).
- **Decision-claim label:** *decided*.
- **Resolution path:** Either (a) introduce a runtime-defined `ProviderClient` Protocol the three async clients structurally implement (CP capability-aware abstraction layer probably already does this — verify and cite); OR (b) type as `dict[ProviderName, AnthropicClient | OpenAIClient | OllamaClient]` (sum-type, explicit); OR (c) `dict[ProviderName, Any]` with a per-provider close-method-name table. Option (a) is cleanest; (b) is most type-safe; (c) is escape-hatch.

### F2-07 — C-RT-12 specifies 24 phase-2-runtime edges but omits per-edge wiring contract
- **Location:** C-RT-12 §12 — "B. 24 phase-2-runtime edges (per CXA v2.3 §2.3 reclassification)" table enumerates source units and target units per bucket. Subsequent prose: "For each edge, the runtime wires the producer call site to the consumer surface at composition time. Plan v2 U-RT-34 / U-RT-35 / U-RT-36 / U-RT-37 / U-RT-38 enumerate the unit-level decomposition."
- **Defect:** The contract enumerates *which* edges must wire but not *what wiring contract* the runtime owes. For each edge, what is the wiring callable's signature? What payload does the producer hand the consumer? What invariants must hold post-wiring? Currently the spec defers entirely to the plan ("Plan v2 U-RT-34..38 enumerate"), but the plan is a *plan*, not a *contract* — it specifies units of work, not the contract those units satisfy. This is a spec-vs-plan boundary inversion: the contract should live in the spec; the plan should cite the contract.
- **Discriminator:** (a) — substantive content gap; the spec under-specifies an obligation it asserts.
- **Evidence:** Direct quote above. Compare with C-RT-08 which specifies the `run()` signature in the spec body (`async def run(workflow: WorkflowObject, *, config: RuntimeConfig | None = None) -> RunResult`), not in the plan.
- **Decision-claim label:** *decided*.
- **Resolution path:** Either (a) add per-bucket wiring-contract sub-subsections to C-RT-12 (one each for AS→IS, CP→IS×17-as-class, OD→IS, OD→AS, OD→CP), each specifying the wiring callable signature + the payload type + the post-wiring invariant; OR (b) extract C-RT-12 into 5 separate contracts (one per bucket) with per-contract precision. Option (a) is lighter and matches the spec's overall granularity choice.

---

## Class 1 findings (minor — documentation drift)

### F1-01 — Trace-novelty back-flow path unspecified
- **Location:** §"Trace-discipline novelty" final paragraph: "if `harness-adversarial-reviewer` finds the substitution insufficient at P2-S4-CK, escalate to back-flow per `Project_Workflow_v1_8.md` §2.7.6 with a PRD v1.2 amendment proposal".
- **Defect:** Section names the back-flow trigger condition but doesn't sketch what a PRD v1.2 amendment would look like (would it add §N Runtime requirements? introduce R-RT-* requirements that each axis inherits at composition?). The §15 open question #1 surfaces the same question but neither location proposes a concrete back-flow path. This is minor because P2-S4-CK has just *cleared* the adaptation, so the back-flow is not triggered — but for future re-evaluation, the path is undocumented.
- **Resolution:** Inline drop a 1-2 line sketch of what a PRD amendment would carry, OR explicitly state "if back-flow triggered, the amendment shape is operator-decided at that time, not pre-pinned here."

### F1-02 — §15 open question #4 phrasing is over-open relative to spec invariant
- **Location:** §15 open question #4: "Async-only `run()` posture. C-RT-08 forbids a sync wrapper at Track A. P2-S4-CK should verify this is operator-acceptable (no integration scenario blocked by lack of sync surface)."
- **Defect:** C-RT-08 has already pinned async-only as a normative invariant ("**Async-only.** No sync wrapper in Track A"). The open question reads as if the decision were still open, when in fact the spec has decided it. The question is whether to *revisit*, not whether to *decide*. Phrasing should reflect the difference.
- **Resolution:** Reword the open question to "C-RT-08 has pinned async-only. Open for re-evaluation: does any anticipated Track A integration scenario require a sync surface?" OR simply remove the question if the decision is settled.

### F1-03 — `Spec_Operational_Discipline_v1_4.md` vs the skill's `Spec_Operational_Discipline_v1_3.md` reference
- **Location:** Spec front-matter §"ADR scope" and §"Cross-axis citation substrate" cite `Spec_Operational_Discipline_v1_4.md` correctly per workspace `CLAUDE.md` table (OD v1.4 is canonical).
- **Defect:** None in the spec — the spec correctly cites v1.4. This finding is a *positive verification* against the adversarial reviewer skill's own §"Reference files" section which cites `Spec_Operational_Discipline_v1_3.md`. The reviewer skill's reference list is stale; the artifact under review uses the correct version. Surfaced as Class 1 for transparency, applies to the *skill*'s reference list, not the artifact.
- **Resolution:** Out of scope for this review — skill reference list update is separate maintenance.

---

## Findings considered and rejected (transparency)

| Check | Outcome |
|---|---|
| **A1 — Silent grounding collapse.** Did the spec cite primary sources for every substantive claim? | Pass with caveats. ADR + cross-axis citations are present at every contract (though F2-02 and F2-03 flag citation precision). No "engineering best practices" claims without source. Implementation suggestions in "Deferred to implementation discretion" sections are explicitly hedged. |
| **A2 — Silent scope narrowing.** Does the spec cover all five F-P2-N fork resolutions? | Pass. F-P2-1 (composition root home) → implied by C-RT-04 + spec axis declaration; F-P2-2 (ingress) → C-RT-08; F-P2-3 (TracerProvider) → C-RT-06; F-P2-4 (provider SDK) → C-RT-05; F-P2-5 (collector daemon) → C-RT-07. All five surfaced. |
| **A4 — Fabricated citations.** Do contract IDs cited from axis specs (C-IS-05, C-CP-04, etc.) resolve? | Partial pass. CP v2.10 R-2/W-2 + C-CP-04 routing manifest verified through CLAUDE.md cross-reference. F2-03 flags broader citation verification as substantive gap. No fabricated CITATIONS detected; some unverified §-numbers (caught at F2-02/F2-03). |
| **A5 — Missing uncertainty signals.** No `[HIGH] / [MODERATE] / [SPECULATIVE]` tags anywhere in spec. | Pass. Existing axis specs (per Explore agent structural survey) do not use these tags either — the convention in this workspace is "Deferred to implementation discretion" subsections, which the runtime spec uses consistently. Convention-aligned. |
| **A8 — Framing contamination (highest-value vector).** Did the spec pre-commit persona / single-LLM / stack disallowed by `CLAUDE.md`? | Pass. Multi-LLM commitment honored (3 async providers explicitly required, NOT LiteLLM). Persona uncommitted (explicitly stated in front-matter trace-novelty section + §15 open question #6 surfaces tenant identity correctly as uncommitted). Stack honored: Pydantic v2, asyncio, hand-rolled retry/breaker, FastMCP, keyring, OTel. Deployment surface configurable via `RuntimeConfig.deployment_surface`. |
| **A9 — Cross-project context bleed.** Are claims grounded to design-substrate/ + workspace artifacts? | Pass. Every contract cites either an ADR, an axis spec, a fork resolution record, the strawman, or the plan. No cross-project drift. |
| **Spec exit criteria §2.5 — every ADR commitment honored.** Each ADR in §"ADR scope" must be honored by ≥1 spec element. | Pass with one note. F1/F2/F4/F5/D2/D6 → directly mapped to C-RT-NN contracts. F3 (index primitive) → covered by C-RT-02 stage-1 post-condition (`ctx.index` non-None) + C-RT-04 field, but no contract is *primarily* about ADR-F3 — coverage is implicit. Acceptable for an axis-spec where index instantiation is a one-line obligation, not a contract-bearing surface. |
| **Spec exit criteria §2.5 — every PRD requirement satisfied.** Adapted per §"Trace-discipline novelty" — runtime *enables* PRD requirements at composition; does not directly satisfy. | Pass conditional on the trace-novelty adaptation being acceptable (which this review judges sufficient at this gate; re-evaluable). |
| **Pattern P1-PHASE-5 mechanical-alignment (workflow §2.5.2 clause i).** Namespace names + event-name verb forms + attribute-set enumerations align with source-axis specs. | Pass with caveats. Spec defers all namespace/attribute schema to OD spec (C-RT-06 invariants: "consumers acquire tracers via `opentelemetry.trace.get_tracer(...)`"). No namespace names asserted in spec body that could drift. WorkflowEvent class `DRAINED` (C-RT-11) is a new event-name not in landed `harness_core.workflow_event_class` — requires alignment check at U-RT-41 landing (flag as a Class-1 surface for that unit, not a finding here). |
| **Pattern P2-PHASE-5 body-citation-alignment (workflow §2.5.2 clause ii).** Citations bumped to latest revised versions. | Partial pass. ADR versions cited match CLAUDE.md table. F2-02 flags ADR §-citation precision; F2-03 flags axis-spec §-citation precision. Version-pinning correct; §-pinning loose. |
| **Spec-vs-plan boundary discipline.** Spec stays normative; doesn't restate implementation. | Pass with F2-07 caveat. Most contracts correctly delegate implementation to plan or to existing landed modules. F2-07 flags C-RT-12 as a *under*-specified contract that pushed too much to the plan. |
| **Trace-discipline novelty acceptability.** Is "PRD enablement" + "Fork-resolution provenance" sufficient substitute for the canonical fields? | Pass at this review gate. The substitution is principled (runtime axis genuinely lacks PRD coverage; F-P2-N forks are the legitimate authority source). Open question #1 in §15 correctly carries the question forward for future re-evaluation. No silent absorption. |
| **7 open questions in §15 — none silently absorbed.** | Pass. All 7 surfaced explicitly with the candidate-Class-1 framing. F1-02 flags #4 as over-open in phrasing (the spec has decided it). |
| **Track-B scope creep.** Does any contract poach Track-B responsibility? | Pass. CLI `run` correctly absent (only `harness-inspect` + `harness-shutdown` admin stubs); markdown workflow authoring absent; topology selection algorithm absent (C-RT-04 holds `topology_dispatcher` from CP; C-RT-08 says "Track A *dispatches* what config selects; selection algorithm is Track B"). TUI absent. Cached-context model explicitly deferred at C-RT-08. Pidfile + SIGTERM is admin-minimum; richer IPC explicitly Track B. |
| **Sub-agent boundary (CP-AL-1).** Does the spec conflate H_E sub-agent topology with H_T TopologyPattern? | Pass. C-RT-04 holds `topology_dispatcher` from CP `TopologyPattern` 6-class enum — H_T territory. No H_E sub-agent topology references. |

---

## Cross-artifact pattern detection

Single-artifact review; cross-artifact patterns do not apply across documents. Within this artifact:

- F2-02 + F2-03 are the **same shape applied to two different citation surfaces** (ADR §-citations and axis-spec §-citations). The single underlying defect is "spec uses descriptive labels where the canonical convention uses verified §-pins." Resolution path is the same: one verification + bump pass against the cited artifacts. Recommend treating as a single revision task.

---

## Disposition

**Recommendation: current-phase spec revision before Session 5 unit landing opens.** Per §4.1.2, 7 Class 2 findings → fork to spec revision (not phase re-opening). No Class 3 findings means no §2.7.6 Phase-7 fork is engaged; the trace-novelty adaptation is judged sufficient at this gate; no upstream artifact (PRD, ADR, ADD, axis specs) needs revision.

**Suggested revision order (one pass):**

1. **F2-02 + F2-03** — single verification pass against cited ADR files and axis-spec files; bump all citations to `§<verified-N-or-title>` form. Highest pickup-value because it's mechanical and applies to many citations.
2. **F2-01** — Operator picks Reading 1 or Reading 2 for fail-class taxonomy. If Reading 1, add C-RT-14 (or sub-section in §"Trace-discipline novelty") explaining the runtime-local class set vs CP's validator-fail taxonomy. If Reading 2, file CP back-flow.
3. **F2-04** — Add Version-evolution sub-bullets to C-RT-03/04/09 schemas.
4. **F2-05** — Add idempotency-and-concurrency invariant to C-RT-08.
5. **F2-06** — Pick option (a)/(b)/(c) for `providers` typing; update C-RT-04 + C-RT-05 accordingly.
6. **F2-07** — Add per-bucket wiring-contract sub-subsections to C-RT-12 (recommended) OR extract into per-bucket contracts.
7. **F1-01** — Inline 1-2 line back-flow-shape sketch in §"Trace-discipline novelty" OR explicit "operator-decided at that time."
8. **F1-02** — Reword §15 open question #4 to reflect that C-RT-08 has decided async-only.
9. **F1-03** — out-of-scope for this artifact revision (skill-reference-list maintenance).

After revision, this skill does not need to re-review unless the operator wants a second pass. The defects are precision-and-completeness; a single revision cycle suffices.

---

*Authored 2026-05-19 by `harness-adversarial-reviewer` skill in Phase-7 pre-implementation review mode (P2-S4-CK gate) against the U-RT-00 hard-gate deliverable. Report is read-only with respect to the spec; resolution paths describe defect-shape, not replacement text. No Phase-7 §2.7.6 fork engaged. The trace-novelty adaptation is cleared at this gate but carries forward as §15 open question #1 for future re-evaluation. Operator decides revision scope.*
