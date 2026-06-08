# Council Workflow — the genuine multi-agent deliberation → review → reconcile-to-zero loop

*Synthesis of the lived workflow, the HIL guidance that keeps it on track, and the two reusable YAML specs. Distilled from the context-memory grounding council arc (roadmap `R-IF-council-context-memory`; PR #292; provenance pointer at `.harness/council/context-memory-grounding/`). This doc is the prose companion to the machine-readable specs.*

| Artifact | Path | Use |
|---|---|---|
| **Harness-layer-aware spec** | `.harness/council/council-workflow.harness-aware.yaml` | Run a council over a *harness* design/planning question; auto-selects the cN voices for the layer. |
| **Generic spec** | `.harness/council/council-workflow.generic.yaml` | Same shape/flow, voices parameterized — for *any* task with a nameable cross-perspective tension. |
| **/command (harness)** | `.claude/commands/council-workflow.md` → `/council-workflow` | Quick-invoke the harness-aware workflow. |
| **/command (generic)** | `.claude/commands/council-generic.md` → `/council-generic` | Quick-invoke the generic workflow. |

---

## 1. What it is

A council is **decorrelated multi-perspective deliberation**, pressure-tested by **adversarial** + **out-of-family** review, converged by **reconcile-to-zero**. Its value is *surfaced tension*, not consensus — so the whole design fights two failure modes: **primary-collapse** (consultants rubber-stamp the primary) and **correlation** (every reviewer is the same model family seeing the same thing). Use it only when a tension between two or more voices can be **named in advance**; otherwise route to a single voice + `advisor()`.

## 2. The shape / flow

```
pre-convene  ─ nameable-tension gate · identify layer/roster · set spine-tension · open charter+ledger
   │
E1 council   ─ A1 primaries (INDEPENDENT, blind)
   │           A2 consultants REACT to the primaries' real output (surface-tension/refine; concurrence rejected)
   │           B  cross-read DEBATE (voices engage peer positions BY NAME: cohere/conflict/refine) + primary confirm-back
   │           → reconciled-to-internal-zero
E2 adversarial#1 ─ genuine red-team; findings classified Class 1/2/3
E2b reconcile ─ council responds (accept/reconcile/rebut) → reconciled-to-zero  [gate before out-of-family]
E3 decorrelated ─ Codex (out-of-family, COLD primer) + advisor (in-family, transcript-aware); weight DIVERGENCE
E3b reconcile ─ council responds → reconciled-to-zero
E4 gate      ─ single bounded adversarial #2 residual sweep + re-verify-at-HEAD → CLEAR / CLEAR-WITH-FOLD / LOOP-BACK
close        ─ fold residuals · conscious versioned deliverable (vN + change-note) · register in roadmap · commit · PR
```

**Reorder the operator may take:** collapse E2b + E3b into ONE consolidated reconcile *after* all reviewer input (adversarial + Codex + advisor) is gathered — the council answers the merged finding-set in one pass. Preserves reconcile-to-zero, fewer full-council convenings. (This arc did so.)

**Mechanism (non-negotiable):** every voice/reviewer pass is a **genuine invocation** — a dedicated agent that FIRST adopts its `cN`/skill and then acts. Never the core agent reading a skill as reference (ventriloquism). The orchestrator composes the envelope + writes the ledger; it does not speak for the voices.

## 3. Council-skill-agnostic pre-invocation + the harness layer router

The workflow is **agnostic to which voices convene until invocation**. The harness-aware spec carries a `layer_voice_map` (per CLAUDE.md §1.1 axis ownership + §10.7 slate):

| Layer | Primaries | Consultants (cross-cutting) |
|---|---|---|
| **IS** (context/memory/state) | C2, C3 | C1, C5, C7, C9, (+C8 eval) |
| **AS** (tools/MCP/sandbox/skills) | C4, C10 | C5, C7, C9, C1 |
| **CP** (routing/retry/workflow/topology) | C1, C5, C6, C9 | C7, C8, C10, C2 |
| **OD** (HITL/audit/cost/observability) | C7, C8, C11 | C5, C9, C1, C10 |
| **CXA** (cross-axis) | C1, C2 | C5, C7, C9, C10, C8 |

Multi-axis → union the touched layers' primaries (cap the *primary* set at 2-3 by genuine center) + dedup consultants. Promote a consultant to first-class when the evidence is squarely its domain (this arc promoted **C8/eval** because the fresh research was eval-gates). The **generic spec** drops this map and **parameterizes** the roster — the caller declares primaries/consultants for any task.

## 4. The HIL guidance (the gates that keep it on track)

These are the genuine gates from the lived arc — honor them unless the operator explicitly waives ("**without HIL**"), and even then stop at destructive/irreversible/outward-facing boundaries.

1. **Halt before each *full-council* convening** (E1, E2b, E3b / the consolidated reconcile) — surface the prior result, await go-ahead. Single-reviewer stages (E2, E3-Codex, E4) do **not** trip this gate.
2. **Phase separation** — run phases as *separate* workflow invocations with an orchestrator checkpoint between; never bundle the isolated deliberation and the cross-read debate in one run.
3. **Convening sequence** — primaries (independent) → consultants (introduced to *react* to the primaries) → cross-read debate. **Not** all-voices-blind-parallel; consultants must see the primaries' real output. *(This arc was corrected mid-stream on exactly this.)*
4. **Decorrelated-reviewer wiring** — Codex gets a **descriptive primer only** (never the council's conclusions, never the adversarial findings, never advisor's eval); advisor is transcript-aware; **weight where Codex disagrees** with the Claude-family reviewers. 3-way convergence → ship; divergence → dig.
5. **Reconcile-to-zero per pairwise gate** before advancing.
6. **Genuine invocation**, always (see §2).
7. **Proportionality when the spine is proportionality-vs-canon** — triage every input *decision-moving / citation-enriching / confirmatory*; enrichments must earn their place against the success metric + the persona filter; don't fold all citations.

## 5. Operational discipline (failure modes this arc hit)

- **Rate-limit:** fan out **gently** — small sequential waves (peak ≤ 2-3 concurrent) + a retry wrapper. A burst of many concurrent agents trips the server burst-ceiling (all fail at once).
- **Don't race contended state:** never run a competing roadmap/dashboard refresh while a concurrent session owns those files — the SessionStart audit + §12.2.1 fixed point self-heal it.
- **Ledger writes** flow through the orchestrator from returned agent markdown (no parallel-write races) — the FM-H lesson the arc itself surfaced.
- **Posture:** council work is additive-only; obey CLAUDE.md §11 posture + X-AL-3.

## 6. Reading order for a fresh session

`COUNCIL-WORKFLOW.md` (this doc) → the relevant YAML spec → the council orchestrator skill (`.claude/skills/council/council-orchestrator/`) → the lived-precedent provenance pointer (`.harness/council/context-memory-grounding/`).
