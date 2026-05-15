# Stage Templates — Output forms across the three-stage pipeline

Source: `s3-spec-writer-architecture.md` §1 (artifact set), §2 (voice-output contract), §3 (traceability), §4 (three-stage pipeline), §6 (tension preservation per stage).

This document gives the concrete templates the spec-writer applies. Use the appropriate template by request shape: per-session spec section for ordinary convening output; Stage 1/2/3 templates at phase boundaries; living-document templates for tension ledger / decision index / voice manifest updates.

---

## Traceability schema

Three trace anchors layer to support drop-down granularity per s3 §3.

### D-IDs — decisions

- Format: `D-NNN` (zero-padded to three digits at minimum; expands as needed).
- Scope: global sequential across the entire spec corpus. D-001 is the first decision ever locked; D-NNN is monotonically incremented.
- Assignment authority: spec-writer auto-assigns at the moment a voice anchors a commitment. Auto-assigned IDs become canonical at session close after operator audit. Operator may renumber, merge, or split at the boundary; not retroactively across sessions per s3 §3.4.
- Placement: inline at the commitment point in spec content, e.g., *"The harness emits a `validator.fail` event on every gate failure (D-047)."*
- Index entry shape (in `council-decision-index.md`):
  ```
  | D-ID | Voice spec | Contributing voices | Originating session | Status |
  |---|---|---|---|---|
  | D-047 | s8-c5-validation-contract-spec.md | C5 (anchor), C9 (consultant) | s8 | locked |
  ```

### T-IDs — tensions

- Format: `T-NNN` for Layer-1 surfaced tensions; `T-perm-N` for the locked Layer-3 permanent tensions (T-perm-1, T-perm-2, T-perm-3 — do not assign new T-perm-N without explicit operator promotion).
- Scope: global sequential.
- Assignment: spec-writer assigns at the moment a TENSION block is ingested per s3 §3.1. The orchestrator emits TENSION blocks without IDs; the spec-writer adds the ID.
- Placement: inline at the TENSION block's appearance in the spec section. Cross-referenced from the permanent tension ledger when the tension is or becomes Layer 3.
- Ledger entry shape (in `council-tension-ledger.md`):
  ```
  | T-ID | Parties | Issue | Originating session | Last touched | Status |
  |---|---|---|---|---|---|
  | T-perm-1 | C4, C10 | capability vs. gating | s7 | s14 | Permanent — tunable parameter `per_tool_gate_level × per_mcp_server_trust_tier` |
  | T-014 | C5, C8 | in-loop vs. out-of-loop validator-judge boundary | s8 | s11 | Active |
  ```

### CCR-IDs — cross-cutting receipts

- Format: `CCR-NNN`. Global sequential.
- Assignment: spec-writer assigns at ingestion of each Convening Block + CCR pair.
- Placement: appears once in the section's metadata header (see below); cross-referenced from spec content that touches a flagged concern.

### Section metadata header

Every spec section that drew from a council convening carries a header per s3 §3.2:

```markdown
> **Section anchor:** Cn (primary) / Cn (co-primary)
> **Consulted voices:** Cn, Cn
> **Convening Block:** [Block ID — typically the section's own ID]
> **CCR:** CCR-NNN
> **Originating session:** sN
```

Per-section attribution gives a fast structural map. Inline D-ID attribution gives granular detail. Lines that are neither commitments nor section headers carry no attribution overhead, keeping prose readable. Per-line attribution is rejected — it produces citation noise that obscures content.

---

## Per-session spec section template

This is the most common output. Given an orchestrator envelope plus voice contributions, produce a spec section.

```markdown
## §X.Y — [Section title — what this section commits to]

> **Section anchor:** Cn (primary)
> **Consulted voices:** Cn, Cn
> **Convening Block:** [Block ID]
> **CCR:** CCR-NNN
> **Originating session:** sN

### Convening Block

[Verbatim from orchestrator output. Do not paraphrase.]

### Cross-Cutting Receipt (CCR-NNN)

[Verbatim CCR table from orchestrator output.]

### Synthesis

[Layer C synthesis. Primary voice's load-bearing prose anchors the section. Inline D-IDs at commitments. Consultant annotations cited inline (e.g., "C9 refines this with…"). Co-primaries jointly anchor with explicit acknowledgment.]

[The harness emits a `validator.fail` event on every gate failure (D-047). C5 anchors the fail-class taxonomy at four classes (transient / permanent / Reflexion-recoverable / unknown-defer); C9 (consultant) refines that the unknown-defer class routes through tight-budget transient retry to permanent-fail-exit (D-048).]

### TENSION block (T-NNN)

[Verbatim TENSION block from orchestrator output, if any. Omit the block entirely if voices agreed — do not write "No tensions surfaced".]

### Consistency report (light)

[CCR ↔ commitment alignment finding only, for per-session ingestion. See `consistency-check.md` §1 for full check; light check is enough at per-session granularity.]
```

The synthesis subsection is where FM-1 (synthesis flattening) lives. Read it back and verify: voice asymmetry is preserved, no homogenized "council voice", no commitments without an anchor voice, imperative for commitments and paraphrased-voice for rationale.

---

## Stage 1 — Design doc

`council-design-doc-v1.md`. Produced at phase 1 close. Voice-by-voice integration of all session-level artifacts.

```markdown
# Council Design Doc — v1

[One-paragraph framing: this doc transforms the eleven voice specs (s4–s14), the two utility specs (s2–s3), the phase-2 prep reconciliation (s15-prep), and the three living documents into a single voice-organized integrated artifact. Phase 2 reads this when individual SKILL.md drafting begins.]

## Reading order

[Map of the doc — which voice lives in which section, where to find tensions, where to find the tension ledger reference.]

## C1 — Orchestration & Control

[Aggregated content from s4, with cross-references to voices that interact with C1's commitments. Include all C1-anchored commitments by D-ID. Include the section metadata headers for every original section. TENSION blocks inline as sidebars with full block text; permanent tensions get a "see ledger T-perm-N" footer.]

## C2 — Context Engineering

[Same pattern.]

[... C3 through C11 ...]

## Permanent tension ledger summary

[High-level summary of `council-tension-ledger.md`'s Permanent entries. Full ledger is the canonical source.]

## Decision index summary

[High-level summary of `council-decision-index.md`. Full index is the canonical source.]

## Voice identity manifest summary

[High-level summary of `council-voice-manifest.md`. Full manifest is the canonical source.]
```

**No new content.** The design doc is a *transformation* of existing artifacts. If you find yourself writing prose that didn't exist in any voice spec, that's a sign you've slipped from "transform" to "decide" — refactor.

**Cross-references.** Every voice section names which other voices' commitments it interacts with. C1's section names C5 (Reflexion topology), C9 (retry as control flow), C11 (HITL placement). Use D-IDs for the cross-references, not paraphrased excerpts.

---

## Stage 2 — PRD

`council-prd-v1.md`. Synthesized from the design doc by reorganizing voice-anchored content into capability-anchored content. Same content; different cut.

```markdown
# Council PRD — v1

[One-paragraph framing: this PRD reorganizes the design doc by capability rather than by voice. Same commitments; different access pattern. Implementation planning reads this.]

## Capability map

[List of capability sections. Each names contributing voices.]

## Capability A — [name, e.g., "Failure recovery"]

> **Contributing voices:** C1 (control flow), C9 (retry mechanics), C11 (HITL escalation)
> **Source design-doc sections:** §C1.3, §C9.4, §C11.2

### Open Decisions for this capability

[Layer-1 TENSIONs that affect this capability area. Permanent tensions get one-line "see Permanent tensions appendix T-perm-N" pointers.]

### Requirements

[Capability requirements, drawn from the design doc's voice sections. Each requirement carries a D-ID. Each requirement's rationale paragraph cites the contributing voice.]

[The harness must support graceful degradation under provider outage (D-047, D-091, D-104). C9 anchors the fallback-trigger condition vocabulary; C6 anchors the per-role fallback chain composition; C11 anchors the operator-experience contract for capability-shortfall escalation.]

[... more requirements ...]

[... more capabilities ...]

## Permanent tensions appendix

[Layer-3 permanent tensions. Each entry: parties, issue, T-ID, ledger reference. Final spec promotes these to tunable parameters.]
```

**Capability cuts** are not predetermined — they emerge during integration. Common ones: failure recovery, tool surface, validation pipeline, observability, action safety, model strategy, operator experience, eval methodology. The PRD assembly may surface a *missed* capability cut, in which case the transition delta report flags it.

**Transition delta report (Stage 1→2).** Produced when integration surfaces unresolved items.

```markdown
## Stage 1→2 Transition Delta Report

### Decisions reorganized
[D-IDs that moved from voice anchoring to capability anchoring without semantic change. Most decisions land here.]

### Decisions transformed
[D-IDs that changed shape during the cut — e.g., a commitment that lived in C9's section as "retry on transient fail" appears in the failure-recovery capability section as "transient-fail retry composes with permanent-fail breaker trip per breaker subscription policy". Note the change rationale per D-ID.]

### Decisions dropped
[D-IDs that did not survive the cut — typically because the cut exposed a contradiction the design doc smoothed, and resolution requires a decision the council hasn't anchored. Each dropped D-ID is a candidate for a targeted convening.]

### Capability gaps
[Capability areas where voices haven't anchored a commitment that the PRD needs. Each is a candidate for a targeted convening.]

### Recommended targeted convenings
[List of (capability, voices, scope) triples. Operator decides whether to convene.]
```

Operator review of the delta report gates the stage transition.

---

## Stage 3 — Final specification

`council-final-spec-v1.md`. Synthesized from the PRD by expanding requirements into concrete contracts, parameters, and operator-tunable knobs. Implementation reads this.

```markdown
# Council Final Specification — v1

[One-paragraph framing: this spec expands PRD requirements into concrete contracts, parameters, and tunables. Permanent tensions are encoded as tunable parameters with documented tradeoff space, not resolutions. Implementation reads this.]

## Capability A — [name]

[For each requirement from the PRD:]

### Requirement A.1 — [name]

> **Contributing voices:** Cn, Cn
> **Source PRD section:** §A.1

#### Contract

[Concrete contract. Schema, signature, parameter list, valid-value ranges. The voice-owned "final-spec contract responsibility" per s3 §8.1 / voice spec §4 lands here.]

#### Parameters

[For each parameter — name, type, valid range, default, semantics. Each parameter row is a commitment with a D-ID.]

#### Tradeoff space

[For tunable parameters that promote permanent tensions — the documented tradeoff space per s3 §6.3. What "permissive" means; what "strict" means; what "balanced" means; how the operator chooses.]

[... more requirements ...]

## Permanent tensions — tunable parameter encoding

[For each Layer-3 permanent tension, the tunable parameter that encodes it.]

### T-perm-1 — capability vs. gating (C4 ↔ C10)

**Tunable parameter:** `per_tool_gate_level × per_mcp_server_trust_tier`

**Tradeoff space:**
- At `per_tool_gate_level=permissive`, C4's capability surface is fully exposed; tools execute without per-call gating. Cost: low gate friction. Risk: capability misuse.
- At `per_tool_gate_level=strict`, C10's gating dominates; every tool call passes through the gate decision. Cost: latency, gate-decision overhead. Risk: capability friction.
- The two-axis tunable allows per-tool and per-MCP-server policies to differ.

**Default:** `balanced`. Tunable per deployment.

[... more permanent tensions ...]

## Acknowledged structural tensions

[Permanent tensions that resist parameterization. Each entry names the tension, references the ledger, states the spec's intentional silence on resolution, and points to the voices' positions.]
```

**Transition delta report (Stage 2→3).** Same structure as Stage 1→2 delta report. Surfaces requirements that resist concrete contract/parameter expansion — typically because the parameterization assumes operator behavior the council hasn't specified.

---

## Living-document templates

### Permanent tension ledger (`council-tension-ledger.md`)

Canonical source for permanent tensions. Operator-edited at session close (status field).

```markdown
# Council Tension Ledger

## Active tensions

| T-ID | Parties | Issue | Originating session | Last touched | Status |
|---|---|---|---|---|---|
| T-014 | C5, C8 | in-loop vs. out-of-loop validator-judge boundary | s8 | s11 | Active |

## Permanent tensions (Layer 3)

### T-perm-1 — capability vs. gating

- **Parties:** C4, C10
- **Issue:** Maximizing tool surface is in tension with gating to constrain blast radius. Both voices' load-bearing concerns are real; the council confirms this as structural.
- **Positions:**
  - **C4:** [verbatim from voice spec — high-cost / low-cost endpoints]
  - **C10:** [verbatim from voice spec — high-cost / low-cost endpoints]
- **Tunable parameter (final-spec stage):** `per_tool_gate_level × per_mcp_server_trust_tier`
- **Originating session:** s7 (surfaced); s14 (confirmed permanent)
- **Last touched:** s14
- **Status:** Permanent

[... T-perm-2, T-perm-3 ...]

## Dormant tensions

[Entries auto-flagged when no voice has spoken on them in three sessions. Operator decides promote / archive / reactivate.]
```

### Decision index (`council-decision-index.md`)

Derivative — regenerated from voice specs. Do not hand-edit.

```markdown
# Council Decision Index

| D-ID | Voice spec | Contributing voices | Originating session | Capability domain | Status |
|---|---|---|---|---|---|
| D-001 | s4-c1-orchestration-spec.md | C1 | s4 | control flow | locked |
| D-002 | s4-c1-orchestration-spec.md | C1 | s4 | control flow | locked |
| ... | ... | ... | ... | ... | ... |
| D-047 | s8-c5-validation-contract-spec.md | C5, C9 (consultant) | s8 | validation pipeline | locked |
```

### Voice identity manifest (`council-voice-manifest.md`)

Derivative — regenerated from voice specs. Per the per-voice template in `ingestion-contract.md` §"Layer A".

---

## What never changes during stage transitions

These are the invariants per s3 §4 / §3 / §6:

- D-IDs survive every transition. Stage-2 PRD lines trace to Stage-1 design doc lines trace to a session and voice. If a transition would erase a D-ID, that's FM-2 (stage drift) — refactor.
- Permanent tension parties survive. T-perm-1 is C4 ↔ C10 in the design doc, in the PRD, and in the final spec. If a transition would re-attribute a permanent tension to different voices, that's a structural error — refactor.
- Voice attribution is *traversable* even if not inline. Final-spec sections cite PRD sections; PRD sections cite design-doc sections; design-doc sections carry voice metadata headers. The decision index is the master traversal table — given any D-ID at any stage, the index returns originating voice and session.

If you find yourself wanting to break one of these invariants for "clarity" or "concision", stop. The invariants are FM-2 / FM-5 mitigations. They are load-bearing.
