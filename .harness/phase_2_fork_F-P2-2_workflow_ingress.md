# Phase 2 — Class 1 Fork F-P2-2: Workflow Ingress

**Status:** ✅ **RESOLVED 2026-05-19** — operator ratification.
**Source:** Phase 2 Session 2 Track A strawman, `phase-2-session-2-track-a-strawman.md` §6.
**Type:** Track A/B decomposition decision; defers a DevEx-territory spec section to Track B.

---

## Defect

The corpus specifies *what a workflow's customization shape is* (C-CP-06 §6.1 —
`WorkflowManifestEntry` with workload class, engine class, topology, fallback chain, HITL
placements, etc.) and *implies workflows are decorated Python functions or markdown-driven
declarative definitions* (C-CP-06 §6.2 + Persona §7). It does **not** specify:

- Where workflow definitions live (filesystem location).
- How they are discovered/loaded at runtime.
- How the operator invokes a specific workflow when starting the harness.
- What the runtime entry signature looks like.

Workflow ingress is the operator's first point of contact with the harness — DevEx
territory by definition.

## Options surfaced

1. **Python-API placeholder for Track A; defer operator-facing ingress to Track B.** Track
   A assumes `from harness_runtime import run; run(workflow_object)` as the entry. No CLI
   ingress, no discovery, no operator-facing surface in Track A.
2. **Pin a minimal baseline now** — author a new contract (e.g., C-CP-25 "Workflow ingress
   and discovery") with filesystem-discoverable workflows and `harness run <workflow_id>`
   CLI. Track B layers richer ingress on top.
3. **Defer F-P2-2 entirely until Track B opens.** Specify everything else in Track A;
   workflow-ingress unit is the last landed, after Track B.

## Resolution

**Option 1 — Python-API placeholder for Track A; defer operator-facing ingress to Track B.**

Operator-ratified rationale:
- Workflow ingress is DevEx territory; Track B's definitional pass is the right surface to
  design "how does the operator start a workflow" (CLI? operator prompt? MCP-triggered?
  markdown registry? all of the above?).
- Track A doesn't need to pre-lock a baseline that Track B may want to change.
- A Python entry is sufficient for Track A to scaffold composition root + bootstrap +
  lifecycle dispatch and to write tests that exercise the bootstrap end-to-end without an
  operator-facing surface.
- Avoids X-AL-3 risk on a genuinely-new DevEx design surface.

## What this resolves

| Question | Resolved |
|---|---|
| Track A runtime entry signature | Python API: `harness_runtime.run(workflow: <WorkflowDefinition>) -> <WorkflowResult>` (exact signature pinned at Session 3 atomic-decomposition; uses the existing `WorkflowManifestEntry` + a callable body per C-CP-06 §6.2 implication) |
| Workflow discovery mechanism in Track A | None — caller passes the workflow object directly |
| Filesystem location for workflow definitions in Track A | None — workflow lives in-process at the call site |
| CLI subcommand for running a workflow in Track A | None — `harness` CLI in Track A is admin-only (e.g., `harness inspect`, `harness shutdown`); `harness run` is Track B's design call |
| Markdown-driven workflow authoring | Track B; Track A is Python-only |
| Operator-typed prompt → workflow generation | Track B (likely a core DevEx-plane primitive) |
| MCP-server-triggered workflows | Track B |

## What this does NOT resolve

- The exact `run()` signature, return type, and async/sync posture — pinned at Session 3
  atomic-decomposition for the composition-root entry unit.
- The Track B operator-facing ingress design — that is Track B's definitional pass + design
  pipeline. The full ingress contract (likely a new CP spec section or a new harness-runtime
  spec) emerges from Track B.
- F-P2-3 (tracer provider init site), F-P2-4 (provider SDK lifecycle ownership), F-P2-5
  (in-process OTLP collector daemon start) remain open.

## Scope implications for Track A

This resolution **shrinks** Track A meaningfully:
- No workflow-file format design.
- No filesystem discovery / registration mechanism.
- No markdown spec parser.
- No CLI workflow-argument parsing.
- The atomic-decomposition's "workflow ingress" surface collapses to a single Python entry
  function on the composition root, exercised in tests by constructing workflow objects
  directly.

## Filing footer

| Field | Value |
|---|---|
| Artifact | `phase_2_fork_F-P2-2_workflow_ingress.md` |
| Authority | Operator ratification at Phase 2 Session 2 close, 2026-05-19 |
| Predecessor | `phase-2-session-2-track-a-strawman.md` §6 |
| Successor | Session 3 atomic-decomposition pins the `run()` signature; Track B's definitional pass owns operator-facing ingress design |
