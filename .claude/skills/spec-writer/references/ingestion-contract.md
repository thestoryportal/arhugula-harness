# Ingestion Contract — Layer A / B / C protocol

Source: `s3-spec-writer-architecture.md` §2 (voice-output shape contract). This document is the per-layer detail. The SKILL.md gives the high-level posture; this document gives the operational rules.

The contract has three layers, each with a distinct treatment. Get the layer wrong and you violate the architecture's load-bearing principle: structured material that is data must round-trip; narrative material that is reasoning must synthesize without homogenizing.

---

## Layer A — Voice identity declarations

**What it is.** The seven orchestrator-driven fields each voice declares once in its voice spec (per `s2-orchestrator-design.md` §8): question types this voice anchors; question types this voice consults on; scope-keyword profile; cross-cutting concerns owned; standing pre-check obligations; consultant posture; co-primaries and known permanent tensions. Plus the five spec-writer-driven obligations folded into existing components per `s3-spec-writer-architecture.md` §8.1: decision-claim vocabulary, voice-output shape preference, capability domains, final-spec contract responsibility, tradeoff-space contribution to permanent tensions.

**Where it appears.** In each voice spec's component 3 (activation triggers), component 4 (scope boundary), component 6 (output shape), component 7 (tension flags), and component 8 (cross-cutting concern obligations).

**How to ingest.** Verbatim copy into the voice identity manifest (`council-voice-manifest.md`). Never paraphrase. Never summarize. The manifest is a regenerable derivative — when a voice spec changes, regenerate the manifest entry from source. Hand-edits to the manifest are rejected; they will be overwritten next regeneration.

**Why verbatim.** The orchestrator reads the manifest at routing time per s2 §8 to score voices against prompts. If the manifest paraphrases the voice's keyword profile or cross-cutting obligations, the orchestrator's routing decisions are made against paraphrased data. Routing accuracy depends on Layer A round-tripping cleanly from voice spec to manifest to orchestrator.

**Manifest entry shape:**

```markdown
## Cn — [Final voice name]

**Source spec:** `sN-cn-{slug}-spec.md`

### Anchored question types
[verbatim from voice spec §3]

### Consulted question types
[verbatim from voice spec §3]

### Scope-keyword profile
[verbatim from voice spec §3 — strong-trigger band, anti-trigger keywords, negative keywords]

### Cross-cutting concerns owned
[verbatim from voice spec §4 / §8 — sole / joint / standing pre-check]

### Standing pre-check obligations
[verbatim from voice spec §8]

### Consultant posture
[verbatim from voice spec §8 — how this voice contributes when consulted]

### Co-primaries and known permanent tensions
[verbatim from voice spec §7 — likely co-primary voices; known permanent tensions this voice participates in]

### Decision-claim vocabulary
[verbatim from voice spec §4 — what kinds of commitments this voice makes]

### Voice-output shape preference
[verbatim from voice spec §6 — narrative / structured / hybrid leaning N or S]

### Capability domains
[verbatim from voice spec §4 — which capability cuts at PRD stage]

### Final-spec contract responsibility
[verbatim from voice spec §4 — concrete contracts/parameters at final-spec stage]

### Tradeoff-space contributions
[verbatim from voice spec §7 — for each permanent tension this voice participates in, the high-cost and low-cost endpoints]
```

---

## Layer B — Orchestrator envelope

**What it is.** The three structured artifacts the orchestrator emits per convening, per `s2-orchestrator-design.md` §3 / §5 / §6 and the orchestrator skill's `references/output-templates.md`:

- Convening Block (question type, voices convened, routing rationale, voices considered not convened, pre-check status)
- CCR (six concerns × Touched / Owner status / Pre-check note)
- TENSION block (parties, issue, positions, stakes, status) — emitted only when voices disagreed

**Where it appears.** As the structural frame of an orchestrator response. Convening Block first, CCR immediately after, voice contributions in turn, TENSION block at the end if any.

**How to ingest.**

- **Convening Block** — placed at the head of the spec section that drew from this convening. **Verbatim.** Field-by-field. The spec-writer adds a CCR-ID to the Convening Block's "Pre-check status" line on ingestion.
- **CCR** — placed adjacent to its Convening Block (immediately following). **Verbatim table.** Six rows preserved; field values preserved. The spec-writer assigns the CCR-ID at ingestion.
- **TENSION block** — placed inline at the point of contention in the synthesized Layer C content. **Verbatim block text.** The spec-writer assigns a T-ID at ingestion (per s3 §3.1 — orchestrator emits without T-ID; spec-writer assigns).

**Why verbatim.** The envelope's stable field structure is the contract that lets downstream readers re-parse the spec without trusting the spec-writer's editorial layer. If a future tool wants to extract all CCRs that flagged blast-radius as Touched-deferred, it greps for the table structure. Paraphrasing the envelope breaks every such tool.

**Lint at ingestion (mandatory).** Verify the envelope is well-formed before ingesting:

- Convening Block has all five fields populated (question type, voices convened, routing rationale, voices considered not convened, pre-check status). Empty *"voices considered, not convened"* must say "None" explicitly — absent field is malformed.
- CCR has all six concerns addressed. Touched concerns each have a substantive pre-check note (not just "Yes" or "addressed"). Owner status is one of {convened, handled-by-reference, deferred}.
- TENSION block (if present) has parties, issue, positions, stakes, status. Status is one of {open, escalated to Layer 2, promoted to Layer 3}.

If lint fails, **do not ingest silently** — surface the malformed envelope as a finding and either (a) ask the operator to re-run the orchestrator, or (b) accept ingestion of the malformed envelope only with a flag in the spec section noting the malformation. Default to (a) unless the operator explicitly opts for (b).

---

## Layer C — Voice contribution per topic

**What it is.** The convened voices' substantive contributions — primary's load-bearing position, consultants' annotations (concur-with-rationale / surface-tension / propose-refinement), co-primaries' joint anchoring. Prose. Reasoning. The actual content of the convening.

**Where it appears.** Between the CCR and the TENSION block in an orchestrator response. Primary first; co-primary if applicable; consultants in turn.

**How to ingest.** **Synthesize into spec content with attribution preserved and asymmetry respected.** This is the only layer where the spec-writer is permitted to paraphrase, and even here the discipline is strict.

### Synthesis discipline

Five rules apply:

1. **Preserve attribution.** Every paragraph in the synthesized prose that drew from a voice's contribution must carry an attribution signal — either an inline reference (*"C5's gate-classification taxonomy…"*) or a section-level metadata header that anchors the section to a primary voice. Sections with zero voice attributions are FM-1 (synthesis flattening) in progress; refactor before emitting.

2. **Respect asymmetry.** The primary voice's position becomes the load-bearing prose of the spec section — its commitments anchor the section. Consultant contributions appear as inline annotations: a concur-with-rationale becomes a brief reinforcing paragraph cited to the consultant; a refinement becomes a follow-on clause; a surfaced tension becomes a TENSION block at that point. Co-primaries get equal billing with explicit joint anchoring noted in the section's metadata header. Normalizing voices to equal billing defeats the orchestrator's structural choice in s2 §4.

3. **Don't homogenize.** If C4 frames a constraint as "this gates writes too aggressively" and C10 frames it as "this is the minimum gate", both phrasings survive into the spec. Smoothed disagreement is dishonest. The synthesis preserves voice signal — read the output and ask: can a reader tell whose answer this is at a glance? If no, you've collapsed voices into a generic "council voice".

4. **Don't add commitments.** The spec section may contain only commitments that voices in the convening anchored. If you find yourself writing a sentence that asserts a commitment no voice articulated, stop — that's the spec-writer making architectural decisions, which is exactly what this skill is not. Surface the gap as a transition delta report item or a follow-on-convening request.

5. **Imperative for commitments; paraphrased-voice for rationale.** Style split per s3 §7 FM-1 mitigation: spec commitments (the system-level facts the harness must satisfy) read in imperative spec voice — *"The harness emits a `validator.fail` event with classification {transient, permanent, Reflexion-recoverable}"*. Spec rationale (the voice's reasoning for the commitment) reads in paraphrased voice — *"C5 anchors transient and permanent as the load-bearing classes; Reflexion-recoverable was added to give the in-loop retry path a visible signal"*. The split keeps voice content visible as voice content.

### Per-voice shape adaptation

Voices declare different output-shape preferences in their spec (component 6, per s3 §8.1). The synthesizer respects them:

- **Narrative-leaning voices (C1).** Synthesize into prose paragraphs with named-pattern references. Tables only if the voice's contribution itself was a table; otherwise prose.
- **Structured-leaning voices (C7, C8, C9, C10, C11).** Tables, attribute catalogs, parameter rows are the natural form. Ingest tables verbatim where the voice produced them. Prose only for the rationale around the table, not as a substitute for it.
- **Hybrid voices (C2, C3, C4, C5, C6).** Match the voice's per-topic preference. C5's gate contracts are structured (tables of validator kind × pass condition × fail class); C5's boundary reasoning is narrative. Ingest each in its natural form.

When in doubt, read the voice spec's §6 to see what form the voice declared, and match.

### Verbatim-vs-synthesize decision tree

For each chunk of voice contribution:

```
Is this content a structured surface the voice declared as ingest-verbatim?
  (per voice §6 — e.g., C7 attribute catalogs, C9 backoff tables, C10 gate-policy tables)
  ├─ YES → ingest verbatim. Add D-ID inline at each row's commitment.
  └─ NO → continue.

Is this content reasoning prose (rationale, tradeoff explanation, seam framing)?
  ├─ YES → synthesize. Apply five-rule discipline above.
  └─ NO → continue.

Is this content a TENSION between voices?
  ├─ YES → that's Layer B (orchestrator-emitted TENSION block). Ingest verbatim.
  └─ NO → ambiguous case; ask the operator before ingesting.
```

The ambiguous bucket is rare in practice. Most voice content is either declared-structured (table) or declared-narrative (prose) and the §6 of the source voice spec resolves the question.

---

## Voice-by-voice shape preference quick reference

For convenience during ingestion. Authoritative source is each voice spec's §6.

| Voice | Preference | Structured surfaces (verbatim) | Narrative surfaces (synthesize) |
|---|---|---|---|
| C1 — Orchestration | Narrative | (rare — pattern catalogs if present) | architectural reasoning, topology choice rationale, named-pattern references |
| C2 — Context Engineering | Hybrid leaning structured | parameter-bearing claims, prompt-structure tables | altitude reasoning, tradeoff explanation |
| C3 — State, Memory & Persistence | Structured (primary) / narrative (seams) | tier tables, checkpoint parameters, GC values | C2 / C1 / C9 seam discussions |
| C4 — Tools & Integration | Hybrid leaning structured | tool-contract tables, idempotency-posture rows | tradeoff and architectural reasoning |
| C5 — Validation Contract | Hybrid leaning structured | gate-contract tables, fail-class taxonomies | boundary and seam reasoning |
| C6 — Model Strategy & Routing | Hybrid leaning structured | per-role configuration tables, fallback chains | posture and seam reasoning |
| C7 — Observability | Hybrid leaning structured | attribute catalogs, cost-attribution tables, redaction rules, sampling policy | instrumentation philosophy, structure-not-content rationale |
| C8 — Eval Engineer | Structured | eval primitive catalogs, alignment thresholds, regression tables, eval-set-design tables, Husain-loop-stage tables, meta-eval cadence, drift windows, per-voice eval-contract review | (minimal) |
| C9 — Reliability & Recovery | Structured | backoff tables, timeout tables, idempotency-mechanism tables, breaker-config tables, fallback-trigger tables, graceful-degradation tables, rate-limit-storm tables, observable-trace-event tables | (minimal) |
| C10 — Action Safety | Structured | gate-policy tables, blast-radius classification, trust-gradient matrices, sandbox-isolation tables, secrets-handling tables, cross-deployment tables, breaker-subscription tables, HITL-escalation tables, observable-trace-event tables | (minimal) |
| C11 — Operator Loop & Local Deployment | Structured-leaning | operator-experience contracts, local-deployment configuration tables (library / schema / file path / parameter name) | tradeoff and boundary-framing prose |

Sole-narrative voices (C1) are the minority. Most of the slate is structured-leaning, which makes verbatim ingestion the dominant case. When in doubt, lean toward verbatim — paraphrasing structured commitments is FM-1 (synthesis flattening); ingesting a narrative paragraph as if structured is harmless if attribution survives.

---

## What ingestion does NOT do

- **Does not select what to ingest.** All Layer B is ingested verbatim. All Layer C is synthesized. Selectivity is the orchestrator's job (which voices, which question type) — not the spec-writer's.
- **Does not fact-check voice claims.** If C5 anchors a commitment that contradicts what C9 said in s12, the consistency check (per `consistency-check.md`) flags it — but the spec-writer does not adjudicate. The flag goes to the operator.
- **Does not improve prose style.** Voice prose is voice prose. The synthesizer paraphrases only when synthesizing across overlapping voice content; even then, the goal is preservation, not style.
- **Does not infer absent voices' positions.** Per s3 §5, selective convening means absent voices are absent — no "[voice not convened]" markers, no inferred default positions. Two structural exceptions (CCR handled-by-reference, permanent-tension carry-forward) are the only mechanisms by which an absent voice appears.
