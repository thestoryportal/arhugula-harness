# Class 1 Tension — harness runtime / entrypoint design gap

**Status:** ✅ PARTIALLY-CLOSED (verified workspace-wide audit 2026-05-20; status-line refreshed 2026-05-27) — **Track A RESOLVED** at `Spec_Harness_Runtime_v1.md` v1.1→v1.3: Python API (C-RT-08 §8 `async run(workflow, config=None) -> RunResult`) + bootstrap orchestrator (C-RT-02 §2 9-stage) + admin CLI stubs (C-RT-13 §13) + LLM dispatch composer (C-RT-15 §14.5 U-RT-52 merged 2026-05-20 at `2b945ab`) all landed. **Track B DEFERRED-PARTITION** (operator-facing DevEx plane: `__main__`, `harness run` CLI, workflow-file loader, daemon, TUI) per spec §3 line 281 + §8 line 167 — operator-owned future scoping arc, not the original gap. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

**Filed:** 2026-05-16 — Phase 7 sub-phase 7b, pre-OD-axis kickoff investigation.
**Defect class:** Class 1 — H_T design surface missing from the design corpus;
surfaced at execution-time. Routes to operator for a new-design decision (design
back-flow deprecated 2026-05-15 — see [[design-substrate-divergence]]).

## Defect

The design corpus does **not** specify a runnable runtime / composition-root /
entrypoint for H_T. Everything built across IS (17/17), AS (33/33), CP (44/57)
is a **library** — Pydantic schemas, contracts, primitives. Nothing in the
corpus wires the axis libraries into a *startable process* a multi-LLM workflow
can run on.

## Evidence (exhaustive corpus search)

Searched all `Implementation_Plan_*` (IS v2.3 / AS v1.2 / CP v2.9 / OD v2.7 /
Harness_Core v1.1), `Cross_Axis_Composition_Document_v2_1.md`,
`Phase_7_Meta_Architecture_v1.md` §6 self-hosting gradient, `PRD_v1_1.md`,
`Architectural_Design_Document_v1_3.md`, all ADRs.

- **No atomic unit** of the ~139 declares an entrypoint signature — no `main()`,
  no `__main__`, no CLI handler, no `async def run_harness(...)`, no agent loop,
  no daemon startup, no `HarnessBootstrap` composition root.
- **U-OD-34** (terminal OD aggregate exporter) produces a metadata *manifest*
  (`SubstrateSeamExportsManifest`), not a process.
- **U-CP-55** (CP terminal aggregate exporter) — composition *manifest*, not a
  process.
- **CXA v2.1** wires 101 typed cross-axis *edges* between library types; it does
  not produce a runnable artifact.
- **Meta-Architecture §6** self-hosting gradient describes when H_E substitutions
  *retire*, not a runnable H_T that would host them.
- **PRD v1.1** specifies observable behavior at the operator surface (run-event,
  cost-attribution, replay-resumption) — not how to *start* the harness.
- **ADR-F4** workflow lifecycle specifies the lifecycle *contract*, not a process
  that runs it.

No spec section, ADR, or plan unit mentions "composition root", "entrypoint",
"agent loop", "`__main__`", or a harness startup sequence.

## What is missing

No artifact specifies:
1. A composition root that imports the axis seam exports (U-IS-17, U-AS-33,
   U-CP-54/55, U-OD-34), instantiates the cross-axis edges, and wires them.
2. A `main()` / CLI / agent-loop entrypoint — the runnable process surface.
3. A bootstrap/initialization order (path-class registry → Skills + gate
   policies → routing core + engine selection → OTel + cost attribution →
   workflow loop).

## Consequence

"Deploy for production usage" is not reachable from the current corpus. Phase 7
can complete every atomic unit and CXA edge and still have **no startable
harness**. Standing one up is **new H_T design** — X-AL-3 forbids silent design
extension at execution-time, so this cannot be autonomously built; it requires a
design artifact authored first.

Corpus scale (verified 2026-05-16): **144 atomic units** — core 1 / IS 17 /
AS 33 / CP 58 / OD 35 (per `CLAUDE.md` §2.4; IS/AS confirmed by full-plan grep,
CP/OD canonical because v2.7/v2.9 plan files are deltas) + 101 CXA edges. None
declares a runtime. Built source confirms: zero `__main__`, zero `def main(`,
zero `[project.scripts]` across all `harness-*` packages.

## Tension with deferring runtime design past Phase 7 closure

Deferring is **structurally blocked at 7d, not merely awkward.** X-AL-2:
retirement = (units landed) ∧ (substituted H_E surface no longer invoked at
substitution site). Without a runtime, nothing invokes H_T primitives — they are
library code on disk; the H_E surface stays the only thing actually invoked. 7d
closure would be forced to declare all 49 substitutions "bounded residual" — the
sub-phase is gutted, not closed.

Second-order: 7c wires 101 cross-axis edges between library *types*. A
composition root routinely surfaces seam defects (a field/hook/cardinality the
edge needs). If discovered after 7c closes, 7c reopens. Cleanest fence:
**runtime design completes before 7c starts.** OD-axis 7b (32 units) does not
depend on the runtime spec — it is the one safely-concurrent track.

## Routing target

Operator — decide whether to author a runtime/composition-root design artifact
in-CLI (back-flow deprecated; design-substrate/ is canonical and edited here).
Candidate: a new `Spec_Harness_Runtime_v1.md` + a runtime plan unit (e.g.
`U-RUNTIME-01` or a `harness-runtime/` package), authored via the
systems-architect → spec-writer → implementation-planner skill chain, then
implemented as a 7b/7c follow-on.

Recommendation: author the runtime design now, *before* the OD → 7c → 7d march.
It is cheapest to surface a gap of this size before more units depend on
assumptions about how the process starts. OD-axis work can proceed in parallel
(it does not depend on the runtime spec), but the corpus should not be declared
Phase-7-complete until the runtime surface exists.

## Operator decision (2026-05-16)

Operator ruled: this is **Phase 2** — not merely runtime integration but the
DevEx agentic plane (the operating brain of the workflow, plus personalized
operator features). It gets its own full-rigor design pipeline (research →
brainstorm → ADD → PRD → spec → implementation plan, adversarial throughout),
authored in-CLI, in a dedicated scoping session the operator will run within
~1 day.

Sequencing ruled: **finish Phase 1 OD-7b now** (land as much of the existing
spec as possible); Phase 2 scoping starts from an integration baseline taken
against the completed Phase 1 implementation. Standing discipline for the
remainder of Phase 1: no Phase 1 implementation may create a tension for
Phase 2, and vice versa — flag any OD/7c/7d unit that touches runtime,
composition-root, or DevEx-plane concerns.

**Status:** OPEN — deferred to Phase 2 scoping session (operator-owned).
Phase 1 OD-7b proceeds in parallel.

## Phase 1 → Phase 2 hand-off observations (collated 2026-05-16)

OD-7b surfaced concrete Phase-1 surfaces that are *materializable as library
code* but whose *runtime behavior* cannot be exercised or verified without the
Phase 2 composition root. Inputs for the Phase 2 scoping session:

- **U-OD-23 `emit_eval_as_child_span`** — creates the child span via the global
  tracer provider (`get_tracer_provider()`). Real parent→child trace
  inheritance is unverified until a composition root calls
  `set_tracer_provider(...)`. The harness needs a defined tracer-provider
  bootstrap site.
- **U-OD-19 / U-OD-20** — `ReplaySemanticDivergenceError` and related are
  structured return-records, not emitted at a live tracer provider; emission
  wiring is Phase 2.
- **U-OD-26 `validate_eval_span_routing`** — consumes a caller-supplied
  `EvalSpanRouting` observation; the composition root that wires actual span →
  routing observation is Phase 2.
- **U-OD-27** — in-process OTLP collector + ring-buffer trace storage + TUI
  trace browser, landed as a LIBRARY surface only (no running collector, no
  live TUI, no sqlite connection, no daemon). The live collector process, the
  TUI, the sqlite ring-buffer rotation, and the no-network-egress enforcement
  are all Phase-2 runtime concerns. This unit is the closest OD surface to the
  Phase 2 DevEx/runtime plane — the Phase 2 design should treat the in-process
  collector + TUI as a runtime component it instantiates.
- **F3 lifecycle event taxonomy is unpinned** — appears in 3 divergent forms
  (OD plan `F2_LIFECYCLE_EVENT_MAPPINGS` / OD spec C-OD-06 §6.1 / OD
  `CLAUDE.md` §1.1). Spec is authoritative per the §1.3 authority chain, but
  the divergence should be reconciled (Class 3 corpus-hygiene; folds into the
  OD-plan v2.8 revision pass, not Phase 2).

---

## Audit reconciliation (2026-05-20)

**Verified status:** DEFERRED-PARTITION

**Resolving artifact / evidence:** Track A RESOLVED — Spec_Harness_Runtime_v1.md v1.1→v1.3 authored at Phase 2 scoping session; api.py docstring lines 15-20 explicitly cite this record as resolved. Python API (C-RT-08 §8 — async run(workflow, config=None) -> RunResult), bootstrap orchestrator (C-RT-02 §2 — 9 stages), admin CLI stubs (C-RT-13 §13 — harness-inspect / harness-shutdown), LLM dispatch composer (C-RT-15 §14.5 — U-RT-52 merged 2026-05-20 at 2b945ab) all landed. Track B (operator-facing DevEx plane — __main__, harness run CLI, workflow-file loader, daemon, TUI) is explicit deferred partition per spec §3 line 281 + §8 line 167 — operator-owned future scoping arc, not the original gap.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
