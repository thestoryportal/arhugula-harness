# Phase 2 — Work-Ahead Outline

**Status:** PRE-SCOPING SUMMARY. Not a design artifact. This outline collates what
Phase 2 must cover from the Phase 1 hand-off record; it makes no design decisions.
Phase 2's actual artifacts (research → brainstorm → ADD → PRD → spec → implementation
plan) are operator-owned and authored in a dedicated scoping pipeline per
`class_1_tension_runtime_entrypoint_design_gap.md`.

**Authored:** 2026-05-17, Phase 7 close-out. **Sources:**
`class_1_tension_runtime_entrypoint_design_gap.md`, `phase-7d-retirement-ledger.md`,
root `CLAUDE.md` §3.

---

## 0. Framing — why Phase 2 exists

Phase 1 built H_T as a **library**. 144 atomic units across core/IS/AS/CP/OD plus
the CXA cross-axis seams are landed as Pydantic schemas, contracts, and primitives.
Verified: **zero `__main__`, zero `def main(`, zero `[project.scripts]`** across all
`harness-*` packages. Nothing wires the axis libraries into a *startable process*.

Phase 2 makes the harness **run**. The operator ruled it is not merely runtime
integration — it is the **DevEx agentic plane**: the operating brain of the workflow
plus personalized operator features. It gets its own full-rigor design pipeline,
adversarial throughout.

---

## 1. Composition root + bootstrap

The wiring layer that turns the library into an object graph.

- **`HarnessBootstrap` composition root** — imports the four axis terminal seam
  exports (U-IS-17, U-AS-33, U-CP-54/55, U-OD-34), instantiates the 22 genuine typed
  cross-axis seams (CXA v2.3), wires them into a live dependency graph.
- **Bootstrap/initialization order** — a defined startup sequence: path-class
  registry → Skills + gate policies → routing core + engine selection → OTel
  tracer-provider + cost attribution → workflow loop.
- **Tracer-provider bootstrap site** — a defined `set_tracer_provider(...)` call site.
  U-OD-23's `emit_eval_as_child_span` uses the global provider; real parent→child
  trace inheritance is unverified until the composition root sets it.
- **Dependency injection** — how the ~144 unit library is assembled and which
  component owns each lifetime.

## 2. Entrypoint + process surface

The runnable artifact.

- **`main()` / `__main__` / `[project.scripts]`** — the process entry. None exists today.
- **CLI handler / agent loop / daemon startup** — how an operator starts the harness
  and how a multi-LLM workflow is submitted to it.
- **Process lifecycle** — start, run, drain, shutdown; crash recovery entry.

## 3. Runtime workflow engine — activating the CP library

The CP axis is the largest landed library (58 units) and the most inert without a runtime.

- **Workflow lifecycle loop** — actually executes `WorkflowManifestEntry` chains,
  runs the per-step override evaluator, emits the audit ledger.
- **Multi-LLM routing core at runtime** — closes the §9 Class 2 surface. Today the
  harness runs single-LLM (`--model`); ADR-F1 v1.2's multi-LLM commitment is met in
  design + landed code but **unmet at runtime**. Phase 2 stands up per-provider SDKs
  (`anthropic` / `openai` / `ollama`) under the capability-aware abstraction.
- **Reliability primitives live** — hand-rolled retry / breaker / idempotency
  actually firing in the request path.
- **Engine selection + replay/resumption** — the 5-class `ResumptionKind` taxonomy
  and replay-disposition mapping executing against real session state.
- **Topology dispatch** — the 6-class `TopologyPattern` enum actually selecting and
  running an execution shape (single-threaded-linear, orchestrator-workers, etc.).

## 4. Observability + operational runtime

The OD axis landed as library surfaces; Phase 2 makes them live processes.

- **Live OTel tracer provider** — real span emission and parent→child inheritance
  (U-OD-23, U-OD-19/20 emission wiring).
- **In-process OTLP collector as a running process** (U-OD-27) — ring-buffer trace
  storage, sqlite ring-buffer rotation, no-network-egress enforcement. Landed today
  as library only; the daemon, the live collector, the sqlite connection are Phase 2.
- **TUI trace browser** — live, against the running collector.
- **Cost attribution** — the 5-step chain emitting at a live provider.
- **HITL primitives** — the 4-response palette wired to a real operator surface
  (U-OD-26's `EvalSpanRouting` observation needs a composition root to feed it).

## 5. DevEx agentic plane — the genuinely new design surface

This is the part Phase 2 *designs*, not just integrates. Under-specified by intent —
the operator's scoping pipeline defines it. Known framing only:

- **The operating brain of the workflow** — the agentic plane that drives the harness,
  beyond mechanical composition-root wiring.
- **Personalized operator features** — operator-facing capabilities (scope TBD by the
  Phase 2 research/brainstorm phase).
- U-OD-27's in-process collector + TUI is the closest existing OD surface to this
  plane; Phase 2 design should treat it as a runtime component the DevEx plane
  instantiates.

## 6. Substitution retirement — 7d full closure

Phase 7 sub-phase 7d is partial-closed; full closure is a Phase 2 deliverable.

- **45 bounded-residual substitutions** (IS 8 / AS 5 / CP 21 / OD 7 / CXA 4) — all have
  condition A met (units landed), condition B unmet (no runtime). Stand up the runtime,
  then per-substitution runtime-trace verification of condition B → retire.
- **2 dormant cross-axis cascades** fire once their endpoints retire:
  §6.3.1 (H_T-CP-1 → H_T-AS-8, `anthropic.*` namespace unblock);
  §6.3.2 (H_T-OD-2 + H_T-CP-24 → H_T-CXA-5, F-CP-01 Stage 3b inversion seam).
- **§9 Class 2 multi-LLM surface** closes at the Phase 2 7d exit gate (requires
  U-CP-01 runtime retirement).

## 7. Deployment

- **"Deploy for production usage"** becomes reachable for the first time.
- **CI substrate** — deferred to post-bootstrap milestone per `Target_Stack_Commitment_v1.md`;
  Phase 2 is the milestone that unblocks it.
- Packaging, process supervision, configuration surface.

---

## Workflow — how Phase 2 is built

Per the operator ruling, Phase 2 runs a **full-rigor design pipeline** before any
implementation: research → brainstorm → ADD → PRD → spec → implementation plan, with
adversarial review throughout. Authored in-CLI; `design-substrate/` is canonical
(design back-flow deprecated 2026-05-15). Candidate artifacts: a
`Spec_Harness_Runtime_v1.md` + a runtime implementation plan (e.g. a `harness-runtime/`
package), via the systems-architect → spec-writer → implementation-planner skill chain.

Phase 2 implementation likely mirrors Phase 7's structure: atomic-unit decomposition,
topological-sort traversal, acceptance-criteria-driven landing.

**Discipline carried from Phase 1:** no Phase 1 ↔ Phase 2 cross-tension creation;
runtime/composition-root/DevEx concerns surfaced during Phase 1 are flagged, not
absorbed (collated in `class_1_tension_runtime_entrypoint_design_gap.md`).
