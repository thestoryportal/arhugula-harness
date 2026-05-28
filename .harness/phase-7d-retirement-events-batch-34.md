# Phase 7d Retirement Events — Batch 34

| Field | Value |
|---|---|
| Batch number | 34 |
| Filed at | 2026-05-28 (post PR #19 `OD-3 HarnessCompositeSampler` merge to main at `b39dc50` — substrate retired + SDK boundary wired at `_DEFAULT_SAMPLER`) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; STILL-BOUNDED → PARTIAL transit per harness-od/CLAUDE.md §4.1 H_T-OD-3 retirement-criterion ladder |
| Predecessor batch | `phase-7d-retirement-events-batch-33.md` (2026-05-28 — H_T-OD-6 PARTIAL → RETIRE-READY transit via PR #18 4-OD-B cluster merge; this batch is the same-arc sibling closure landing PR #19 OD-3 sampler substrate) |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → PARTIAL transit (H_T-OD-3). Cumulative RETIRED count unchanged at 37/54 (68.5%); RETIRE-READY count unchanged at 1/54 (1.9%); PARTIAL count increments 3/54 → 4/54 (7.4%); STILL-BOUNDED count decrements 11/54 → 10/54 (18.5%); STILL-BOUNDED-INDEFINITELY count unchanged at 2/54 (3.7%); pipeline-advanced 41/54 → 42/54 = 77.8% (+1 net advancement — STILL-BOUNDED → PARTIAL is the first promotion tier into the pipeline). Cardinality check: 37 + 1 + 4 + 10 + 2 = 54 ✓.**

This batch records the substrate-retirement transit for **H_T-OD-3** (Composite Sampler per OD spec v1.2 C-OD-09 §9.2 always-sampled discipline + §10.1 base-rate set + §10.3 persona × deployment-surface envelope; carriers `harness-od/src/harness_od/composite_sampler.py` + `harness-od/src/harness_od/sampling_mode.py`; Meta-Architecture §5.4 row OD-3 Composite Sampler) from STILL-BOUNDED → PARTIAL via PR #19 merge:

| Commit | Artifact | Authority |
|---|---|---|
| `b39dc50` | `harness-od/src/harness_od/composite_sampler.py` NEW — `HarnessCompositeSampler(Sampler)` ABC subclass + `build_default_sampler` factory returning `ParentBased(root=HarnessCompositeSampler(...))`; `harness-od/src/harness_od/sampling_mode.py` EXTEND — NEW `is_always_sampled(event_name)` helper decomposing `ALWAYS_SAMPLED_EVENT_CLASSES` frozenset into `_ALWAYS_SAMPLED_LITERALS` + `_ALWAYS_SAMPLED_PREFIXES`; `harness-runtime/src/harness_runtime/lifecycle/tracer_provider.py` `_DEFAULT_SAMPLER` swapped from `ParentBased(root=ALWAYS_ON)` → `build_default_sampler()` | PR #19 squash-merge to main 2026-05-28 |
| (this commit) | `.harness/phase-7d-retirement-events-batch-34.md` (this file) — retirement event filing documenting Criterion A + B structural transit at substrate layer | X-AL-2 first conjunct + harness-od/CLAUDE.md §4.1 H_T-OD-3 retirement ladder |
| (this commit) | `harness-od/CLAUDE.md` §4.1 row STILL-BOUNDED → PARTIAL transition for H_T-OD-3; cumulative-counts line refresh per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit | Workspace bookkeeping discipline per `.harness/phase-7d-retirement-ledger-v2.md` |
| (this commit) | Memory entry `h-t-od-3-partial-batch-34.md` documenting the STILL-BOUNDED → PARTIAL transit + latent-substrate-bug closure pattern | Workspace memory discipline |

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + harness-od/CLAUDE.md §4.1 retirement-ladder:

> H_T-OD-3 (Composite Sampler): STILL-BOUNDED gate on project-authored composite head/tail sampler subclass + integration at materialize_sampler_stage. (post-batch-2 span-emission activity makes this materially relevant)
> PARTIAL transit closes the STILL-BOUNDED gate at substrate authoring + SDK-boundary integration.
> RETIRE-READY transit gates on (a) tail-keep-on-classification at the collector boundary per §9.1 + (b) persona-tier-aware base_rate envelope per §10.3 (both deferred per §9.3 implementer-discretion clause).
> RETIRED transit gates on operator deployment exercising the sampler against real workload + verifying §9.2 always-sampled-set members observed at OTLP collector.

Under that discipline, H_T-OD-3 transitions STILL-BOUNDED → **PARTIAL** via PR #19:

- **Criterion A** (cited unit IDs landed). MET at this batch. `HarnessCompositeSampler` class subclasses `opentelemetry.sdk.trace.sampling.Sampler` with `should_sample(parent_context, trace_id, name, kind, attributes, links, trace_state) -> SamplingResult` returning `RECORD_AND_SAMPLE` for any `name` matching §9.2 always-sampled set (via `is_always_sampled`); delegates to `TraceIdRatioBased(base_rate)` otherwise. `build_default_sampler(base_rate=1.0)` factory wraps in `ParentBased(root=...)` per OTel canonical pattern. Substrate at `harness-od/src/harness_od/sampling_mode.py` extends with `is_always_sampled(event_name)` helper decomposing `ALWAYS_SAMPLED_EVENT_CLASSES` into `_ALWAYS_SAMPLED_LITERALS` + `_ALWAYS_SAMPLED_PREFIXES` (dot-anchored — `audit.*` matches `audit.signature.write` but not `audit` alone).

- **Criterion B structural-MET at this batch.** Three binding-chain stages empirically verified for the SDK-boundary substrate:
  - Stage 1 (carrier landed) — `HarnessCompositeSampler` + `build_default_sampler` exposed at `harness-od/src/harness_od/composite_sampler.py`; 54 tests at `harness-od/tests/test_composite_sampler.py` verify §9.2 literals + dot-anchored prefixes at base_rate=0 still sample, base-rate boundary behavior (0/1), ParentBased preservation (sampled-parent inherits to children at base_rate=0; unsampled-parent forecloses even for always-sampled name).
  - Stage 2 (production consumer site) — `harness-runtime/src/harness_runtime/lifecycle/tracer_provider.py:_DEFAULT_SAMPLER` swapped from `ParentBased(root=ALWAYS_ON)` to `build_default_sampler()` invocation; every `TracerProvider` constructed via `materialize_tracer_provider_stage(config, ...)` now binds the project-authored composite sampler.
  - **Stage 3 (e2e exercise PASS against real substrate) — NOT MET at this batch.** Production workflow has not yet executed a real OTel span emission path against an OTLP collector observing §9.2 always-sampled-set members at production runtime; the deployment-time exercise that confirms the substrate's contract semantic against real ingest is owed at a follow-on operator-bound deployment.

- **PARTIAL → RETIRE-READY gates remaining** (per §9.3 implementer-discretion clause + advisor 28th application clarity at PR #19):
  - Tail-keep-on-classification at the collector boundary per §9.1 (deferred per spec).
  - Persona-tier-aware base_rate envelope per §10.3 (deferred until `persona_tier` plumbed at materializer).
  - §9.2 4 conditional-by-attribute rows attribute-refinement (`files.operation` kind ∈ {upload,delete}; `memory.operation` kind ∈ {write,update,delete}; `validator.fail.*` permanence=permanent; `subagent.span` root-only) — MVP over-samples conservatively; refining via `attributes` lookup is a follow-on arc.

## §1 Latent substrate bug closure

PR #19 surfaced + closed a **latent substrate bug** at `harness-od/src/harness_od/sampling_mode.py`:

- Pre-PR-#19 `ALWAYS_SAMPLED_EVENT_CLASSES: frozenset[str]` carried `"audit.*"` and `"validator.fail.*"` as literal frozenset members per OD spec v1.2 §9.2 fidelity-grammar.
- Pre-PR-#19 `sampling_decision(cell_id, event_class, base_rate) -> SamplingDecision` did `event_class in ALWAYS_SAMPLED_EVENT_CLASSES` set-membership lookup at the substrate boundary.
- Set membership against literal `"audit.*"` would have returned `False` for concrete span names like `"audit.signature.write"` or `"validator.fail.semantic_inconsistency"` — exactly the spans §9.2 declares inviolable.
- **ZERO non-self callers existed at pre-PR-#19 HEAD** (grep verified via 28th `[[advisor-before-substantive-work-for-cross-axis-blockers]]` application); production never exercised the bug at the substrate layer.
- PR #19 closes the bug at the substrate via Option (i) per advisor — NEW `_ALWAYS_SAMPLED_LITERALS` + `_ALWAYS_SAMPLED_PREFIXES` private carriers derived once at module load + NEW public `is_always_sampled(event_name)` helper resolving both. Legacy `sampling_decision` delegates to `is_always_sampled` preserving back-compat contract.

Pattern catalogued at memory `[[od-3-substrate-latent-bug-sampling-mode]]` — when adding lookup helpers consuming spec-fidelity-verbatim substrates, grep callers + audit storage shape vs lookup contract; if zero callers, the substrate's API contract has never been exercised against real inputs.

## §2 Sub-row substitution-status table

Pre-batch-34 OD-axis bucket (post-batch-33):

| Substitution | Status | Source |
|---|---|---|
| H_T-OD-1 (deferral envelope) | STILL-BOUNDED | No `deferral_envelope` import in `harness-runtime/` |
| H_T-OD-2 (OTel SDK base + GenAI semconv) | RETIRED batch-2 (2026-05-20) | LIVE at `lifecycle/llm_dispatch.py` |
| H_T-OD-3 (Composite Sampler) | **STILL-BOUNDED → PARTIAL at this batch (batch-34)** | `HarnessCompositeSampler` + SDK-boundary wiring at `_DEFAULT_SAMPLER`; tail-keep + persona-envelope gate RETIRE-READY |
| H_T-OD-4 (Pre-Collector redaction SpanProcessor) | STILL-BOUNDED | Stock `BatchSpanProcessor`; zero redaction references |
| H_T-OD-5 (Cost-attribution 5-step chain) | RETIRED batch-32 (2026-05-28) | mech-β AC #8 green on main |
| H_T-OD-6 (Local-first OTLP ingestion) | RETIRE-READY (transited at batch-33 this same arc) | 4-OD-B cluster landed; deployment-time opt-in gates RETIRED |
| H_T-OD-7 (Preservation invariants 5-dimension) | STILL-BOUNDED | Library carrier only; no runtime enforcement loop |
| H_T-OD-8 (aggregate manifest + Stage 3b inversion) | RETIRED (v1 §1 authoring-only) | Authoring-close |

Post-batch-34 OD-axis bucket: 2 RETIRED + 1 RETIRE-READY + 1 PARTIAL + 3 STILL-BOUNDED + 1 (OD-8 authoring-close) = 8.

Workspace-layer cumulative post-batch-34: **37/54 RETIRED (68.5%) + 1/54 RETIRE-READY (1.9%) + 4/54 PARTIAL (7.4%) + 10/54 STILL-BOUNDED (18.5%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)**. Pipeline-advanced (R+RR+P): 42/54 = 77.8% (+1 from batch-33; STILL-BOUNDED → PARTIAL is the first tier promotion into the pipeline-advanced bucket per X-AL-2).

## §3 Adjacent observations

(a) **First STILL-BOUNDED → PARTIAL transit in OD-axis post-batch-2.** OD-axis previously held 4 STILL-BOUNDED rows (OD-1, OD-3, OD-4, OD-7); batch-34 reduces to 3 (OD-3 promoted). OD-4 RedactionSpanProcessor is the natural next gate (also flagged "materially relevant post-batch-2" at harness-od/CLAUDE.md §4.1).

(b) **Joint same-arc cross-batch within-OD-axis advancement.** Batches 33 + 34 land on the same retirement-arc (PRs #18 + #19 merged single session); first ledger event where TWO OD-axis bucket members advance via the same upstream merge-cluster on the same calendar day. Joint same-arc transit pattern sibling to batch-31+32 AS-8d + OD-5 (different axes) but distinct shape (within-axis at batch-33+34).

(c) **Substrate latent bug closure as side-effect of substantive arc.** OD-3 PARTIAL transit IS the substrate-bug closure — the bug existed at `sampling_mode.py` since its authoring at OD plan v2.5 conformance revision (`ALWAYS_SAMPLED_EVENT_CLASSES` literal storage + spec-fidelity-verbatim discipline) but the bug never surfaced because ZERO callers existed pre-PR-#19. Promotion event = bug-closure event = substrate-retirement event collapsed into single batch transit. Pattern catalogued for future "substrate-only-retired-arcs-surface-latent-bugs" sub-species candidate at workflow-doc revision.

(d) **No CXA cascade.** PR #19 ZERO cross-axis cascade verified at PR description; sampling_mode.py + composite_sampler.py + tracer_provider.py changes all intra-runtime-OD-axis composition; no edge change at CXA v2.15.

(e) **Workspace `CLAUDE.md` §2.3 + §2.4 row bumps still deferred** per batch-33 carry; sibling-cite cascade at workspace index continues unblocking.

## §4 Filing footer

| Field | Value |
|---|---|
| Authored at | 2026-05-28 (this commit) |
| Authoring authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 |
| Predecessor | `phase-7d-retirement-events-batch-33.md` (same-arc sibling; H_T-OD-6 PARTIAL → RETIRE-READY) |
| Successor | (TBD — next batch on next retirement-shape event) |
