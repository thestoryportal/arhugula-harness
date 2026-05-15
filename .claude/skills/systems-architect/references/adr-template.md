# ADR Template — Canonical Form

The Architectural Decision Record template used in Phases 3a, 3b, and 3d of the harness engineering workflow. Every ADR conforms to this template; the systems architect skill produces ADRs (in Phase 3d, only by reference) that match this structure.

ADRs are durable artifacts. Once Accepted, an ADR is not edited; it is Superseded by a new ADR.

---

## Section structure

```
# ADR-{ID}: {short imperative title}

## Status
{Proposed | Accepted | Superseded by ADR-{ID}}
Date: {YYYY-MM-DD}

## Context
{What forced this decision. What constraints apply. What prior decisions
constrain it (cite by ADR ID). What substrate research informs it (cite
by deliverable + section). One to three paragraphs. State the persona
constraints if persona-dependent.}

## Decision
{One sentence stating the chosen option. Imperative voice. No hedging.
This is the load-bearing line of the ADR.}

## Rationale
{Why this option over alternatives. Tie to substrate evidence (cite by
specific section or claim, not "the substrate"). Tie to persona
constraints if persona-dependent. State the failure mode this decision
prevents and the conditions under which it stops being worth the cost.}

## Consequences
{What becomes possible. What becomes harder. What is now constrained
downstream (which D-ADRs or I-ADRs depend on this). What operational
discipline this implies (gates, validators, observability needs). What
permanent tensions this engages (T-perm-1, T-perm-2, T-perm-3 if
applicable).}

## Alternatives considered
{At least two alternatives. For each:
- Option name
- Why it was a candidate
- Why it was rejected (specific, not generic)
A "do nothing" alternative is acceptable if the ADR is about an
addition, not a choice between concrete options.}

## References
{Substrate citations: deliverable + section, formatted per V3
specificity rules. Prior ADR dependencies: ADR-IDs. Persona document
references: Persona_Document_v{version} §{section}. External sources
follow V3 citation rules — single retrievable source per citation.}
```

---

## Section-by-section guidance

### Status

- **Proposed.** Drafted, not yet accepted. Awaiting council deliberation, adversarial review, or integration verification.
- **Accepted.** Cleared all checkpoints. Load-bearing. Other decisions may depend on it.
- **Superseded by ADR-{ID}.** Replaced by a later ADR that addresses the same decision space. The superseded ADR is preserved (not deleted) for traceability.

Date is the date of last status change.

### Context

The context section answers: *why does this decision need to be made now, and what shapes the decision space?*

Three failure modes:

| Failure mode | Symptom | Correction |
|---|---|---|
| Generic context | "The harness needs to handle multiple workloads." | Replace with the specific persona-document or substrate citation that surfaced the constraint. |
| Solution in context | "Because we want to use Temporal..." | Move the solution to Decision; context describes the problem only. |
| Missing dependency | Context references a constraint without citing the ADR or substrate that established it. | Add the citation; if no citation exists, the decision is not yet authorable. |

### Decision

One sentence. Imperative or declarative voice. No "we recommend" or "we propose" — by the time the ADR is filed Accepted, the decision is made.

**Examples of well-formed Decision lines:**

- "Adopt a thin-client provider abstraction over Anthropic, OpenAI, and a configurable third LLM provider, exposing only generation, streaming, and tool-use surfaces."
- "Use the local filesystem (with git-as-checkpointing) as the durable substrate for shared state and Skills artifacts."
- "Sandbox isolation strength is policy-driven by tool trust level, with three tiers (in-process, container, microVM) selected per tool by the action surface contract."

**Antipatterns:**

- "Consider using..." (hedging)
- "We will use Temporal because it is reliable." (decision + rationale conflated; rationale belongs in Rationale)
- "Multi-LLM support, durable execution, and sandbox isolation." (multiple decisions; each gets its own ADR)

### Rationale

Rationale is *why this option, citing evidence*. Three required elements:

1. **The pattern this decision follows or rejects.** Cite the substrate's pattern catalog or cluster deliverable.
2. **The failure mode this decision prevents.** State the failure mode in production-discipline terms (e.g., "prevents single-vendor lock-in causing migration cost on provider price change").
3. **The condition under which this decision stops being worth the cost.** State explicitly. If the decision has no such condition, state that and explain why.

### Consequences

Consequences are downstream effects, not justifications. Three required elements:

1. **What becomes possible.** Capabilities unlocked.
2. **What becomes harder.** Capabilities constrained or precluded.
3. **What is now constrained downstream.** Which derivative decisions are now constrained, and how.

If the decision engages a permanent tension, name it explicitly: "This decision engages T-perm-{N} (axis A ↔ axis B); the tension is resolved by..." or "...formally accepted as..."

### Alternatives considered

At least two alternatives. The alternative-rejection reasoning is *specific*:

- ❌ "Rejected because it's too complex."
- ✅ "Rejected because adopting it requires a Kubernetes deployment surface, which is precluded by Phase 2 persona's local-development design-time target (Persona_Document_v1 §3)."

Common alternative classes:

- **Status quo / do-nothing** — when the ADR proposes an addition.
- **Alternative substrate** — when the ADR chooses among substrates (e.g., Temporal vs. Restate vs. DBOS for durable execution).
- **Alternative shape** — when the ADR chooses among shapes for the same substrate (e.g., supervisor-worker vs. peer-to-peer for multi-agent topology).
- **Alternative scope** — when the ADR chooses how much of a problem to address (e.g., "filesystem-as-substrate for state only" vs. "for state + Skills + artifacts").

### References

Format per V3's citation specificity rules. Each citation must resolve to a single retrievable source.

**Acceptable:**

- `Pattern Reference Catalog v1.0 §11.3.1`
- `Cluster 5 V2 §3 D5 (HITL synchrony)`
- `Persona_Document_v1 §3 (workload shape)`
- `ADR-F1 (provider abstraction)`
- `Anthropic, "Building Effective Agents," Dec 2024, anthropic.com/engineering/building-effective-agents`

**Not acceptable:**

- `the substrate research` (no specific section)
- `Anthropic engineering posts` (not a single source)
- `the persona document` (no specific section)
- `prior ADRs` (no specific IDs)

---

## Worked example (illustrative — not a real ADR)

```
# ADR-F1: Provider abstraction

## Status
Accepted
Date: 2026-XX-XX

## Context
The project commits to multi-LLM support (V3 system prompt §project_context).
Persona_Document_v1 §3 surfaces three providers as in-scope: Anthropic,
OpenAI, and a configurable third. Pattern Reference Catalog v1.0 §10.4
documents three provider-abstraction shapes observed in production
harnesses: thin-client, full-featured-portable-API, model-agnostic-router.
Decision needed before any other F or D ADR can be authored, because all
downstream LLM-touching components depend on the abstraction shape.

## Decision
Adopt a thin-client provider abstraction over Anthropic, OpenAI, and one
configurable third provider, exposing only generation, streaming, and
tool-use surfaces.

## Rationale
The thin-client pattern (Pattern Reference Catalog §10.4 P-IS-2) preserves
provider-specific features (Anthropic prompt caching, OpenAI structured
outputs) at the call site rather than abstracting them into a lowest-
common-denominator API. The failure mode prevented is feature-erasure on
abstraction (catalog §10.4 documents this as the dominant failure of
full-featured portable APIs). The condition under which this decision
stops being worth the cost: when ≥2 providers converge on identical
feature surfaces, the call-site cost of the thin client exceeds the
benefit of feature-preservation.

## Consequences
Possible: provider-specific feature use (caching, structured outputs,
adaptive thinking) at every call site. Harder: provider switching at
runtime — every call site must declare its provider explicitly. Constrains
downstream: D-ADR on prompt-cache strategy must be authored per provider;
D-ADR on structured-output enforcement must be authored per provider.
Engages T-perm-2 (information substrate ↔ operational discipline) at
the call-site granularity; resolved by leaving feature-preservation
to call site.

## Alternatives considered
- Full-featured portable API (e.g., LiteLLM-style). Rejected because
  feature-erasure on abstraction is documented as the dominant failure
  mode (Pattern Reference Catalog §10.4 P-IS-2 alternative-failure).
- Single-provider commitment with later-adapter pattern. Rejected because
  V3 §project_context commits to multi-LLM by design; single-provider
  contradicts project framing.

## References
- Pattern Reference Catalog v1.0 §10.4
- Cluster 5 V2 §3 F1 classification
- Persona_Document_v1 §3
- V3 system prompt §project_context
```

This example is **illustrative only** — it does not represent a filed ADR and should not be cited as such. The systems architect skill operating in Phase 3d would consume real filed ADRs, not author new ones.
