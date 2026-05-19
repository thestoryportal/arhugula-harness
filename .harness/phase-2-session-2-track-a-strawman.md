# Phase 2 — Session 2: Track A Runtime Strawman

**Charter:** sketch the composition-root shape, bootstrap order, entrypoint surface,
and agent-loop placement against the existing contract corpus. Sketch artifact, not
implementation plan. Surface Class 1 forks; do not resolve them.

**Authored:** 2026-05-19. **Authority:** D-P2-6 (Phase 2 Session 1 framing). **Successor:**
Session 3 atomic-decomposition plan + Track B definitional pass (when opened).

---

## 1. Empirical grounding — the runtime gap is complete

Verified against `harness-{core,is,as,cp,od,cxa}/src/` at commit `2206d4a`:

| Surface | Status |
|---|---|
| `__main__`, `def main(`, `[project.scripts]` | **Zero** across all 6 packages |
| Anthropic / OpenAI / Ollama client construction | **Zero** — no `anthropic.Anthropic(...)`, `openai.OpenAI(...)`, `ollama.Client(...)` anywhere |
| `set_tracer_provider(...)` | **Zero** — U-OD-23 calls `get_tracer_provider()` but nothing configures one |
| `harness-cxa/src/harness_cxa/` | **Empty** — only `__init__.py`; the 22 genuine typed CXA seams live as cross-axis imports inside the axis packages, not in `harness-cxa/` |
| Terminal aggregate exporters (U-IS-17, U-AS-33, U-CP-54/55, U-OD-34) | **Manifests**, not wiring — explicitly *"composition surfaces live at the source units; this exports references only"* |

The runtime gap is not theoretical. The composition root brings the runnable process
into existence; nothing today instantiates a provider client, configures a tracer, or
starts a loop.

---

## 2. Composition-root shape — sketch

The composition root owns: (a) importing source units from the 4 axis packages
+ `harness-core`, (b) instantiating cross-axis seams declared in CXA v2.3's 22 genuine
typed edges, (c) constructing the runtime objects with concrete lifetimes (provider
clients, tracer provider, in-process OTLP collector, audit ledger writer), (d) handing
control to the workflow loop, (e) graceful drain on shutdown.

It is **not** a new axis. It is the wiring layer above the existing axes.

**Responsibility decomposition (sketch — not a unit list):**

- **Foundational bootstrap** — load `harness-core` shared types; resolve config
  (CLI args, env, config file precedence — TBD); resolve persona/deployment-surface
  posture from the F1-F5 commitments.
- **IS bootstrap** — initialize the state ledger (`.harness/state.jsonl` per the
  resolved Class 1 fork from Phase 7), path-class registry, content-addressed index,
  semantic cache.
- **AS bootstrap** — load tool contracts, start MCP host + connect MCP clients,
  initialize sandbox-tier dispatch, load Skills filesystem.
- **CP bootstrap** — construct provider clients (anthropic / openai / ollama under the
  capability-aware abstraction); initialize routing core, retry/breaker/idempotency
  primitives, workflow lifecycle, topology dispatcher, sub-agent handoff registry,
  HITL placement registry.
- **OD bootstrap** — configure the OTel tracer provider (this is the
  `set_tracer_provider(...)` site U-OD-23 depends on); start the in-process OTLP
  collector + ring-buffer + sqlite rotation; initialize audit ledger writer, cost
  attribution chain, HITL primitives.
- **CXA wiring** — instantiate the 22 genuine typed seams (Pattern P1 byte-exact
  per CXA v2.3 §3); per D-P2-2, additionally wire all 24 phase-2-runtime CXA edges.
- **Workflow ingress** — receive the workflow to run (mechanism TBD — Class 1 below),
  hand to CP's workflow lifecycle loop.
- **Shutdown** — drain in-flight calls, flush tracer + audit ledger, close clients +
  collector.

The package this lives in is a Class 1 fork (§5).

---

## 3. Bootstrap order — per the runtime-gap tension record, sketched against landed code

The tension record specifies: path-class registry → Skills + gate policies → routing
core + engine selection → OTel + cost attribution → workflow loop. Per-stage sketch:

| Stage | Existing landed surface | What composition root does | Gap |
|---|---|---|---|
| 1. Path-class registry | IS: path-class taxonomy, content-addressed index, state ledger entry shape | Materialize the registry; create / verify `.harness/state.jsonl`; reattach existing index | None on the contract side; ingress source TBD |
| 2. Skills + gate policies | AS: Skills filesystem, tool contracts, sandbox tiers; CP: gate policies | Load Skills from filesystem; register tools; bind sandbox-tier dispatch | Per CP-AL-3 (action-safety): trust gradient configuration — operator decision |
| 3. Routing core + engine selection | CP: routing manifest (U-CP-04 R-2/W-2 schemas, FULL-LAND), engine class candidates, fallback chain composition | Construct provider clients; build routing manifest from config; bind engine selection | **Provider SDK lifecycle ownership** — Class 1 (§5) |
| 4. OTel + cost attribution | OD: 12-namespace OTel schema, cost-attribution 5-step chain, in-process collector + TUI surfaces (U-OD-27 — LIBRARY surface only) | Configure tracer provider; start collector daemon; bind cost-attribution emission | **Tracer provider init site** — Class 1 (§5); U-OD-27 collector daemon needs the runtime to start it |
| 5. Workflow loop | CP: workflow lifecycle, manifest entry schema, per-step override evaluator, audit-ledger emission | Receive workflow input → dispatch through CP lifecycle | **Workflow ingress** — Class 1 (§5) |

---

## 4. Entrypoint surface — sketch

Per the uv workspace stack commitment: a `[project.scripts]` entry registers a CLI
command pointing at a `main()` in the composition-root package. Invocation shape:

```
uv run harness <subcommand> [options]
# or
python -m harness <subcommand> [options]
```

Subcommand surface (sketch — Track B will refine):
- `harness run <workflow>` — start the agent loop against a workflow source.
- `harness inspect` — query landed state / audit ledger / collector traces.
- `harness shutdown` — drain a running harness gracefully.

The CLI is the *operator's* surface to the harness. Track B's DevEx agentic plane will
expand this — the strawman pins only the minimum runnable entry, not the operator
experience design.

---

## 5. Agent-loop placement — sketch only; Track B decides shape

Per CP-AL-1, the runtime must select a `TopologyPattern` from the 6-class CP enum
(single-threaded-linear / orchestrator-workers / decentralized-handoff /
hierarchical-delegation / evaluator-optimizer / parallelization). The composition root
*dispatches* through the selected topology — it does not implement a topology.

**Which topology the bootstrap harness exhibits is a Track B decision**, not a Track A
sketch call. Track A's responsibility is: select-at-bootstrap from config, dispatch via
CP's topology dispatcher. Topology selection algorithm + default + per-workflow override
are Track B persona/design surfaces.

---

## 6. Class 1 forks surfaced (do not resolve in this session)

| # | Fork | Source | Disposition |
|---|---|---|---|
| F-P2-1 | **Composition-root package placement** — new `harness-runtime/` vs co-locate in `harness-cxa/` vs another option. Runtime-gap record names new package as candidate. | §2 + repo layout | ✅ **RESOLVED 2026-05-19** — new `harness-runtime/` package per operator ratification. See `phase_2_fork_F-P2-1_runtime_package_placement.md`. |
| F-P2-2 | **Workflow ingress** — what does the runtime actually *run*? The corpus specifies workflow lifecycle contracts but not the ingress source. CLI argument pointing at a manifest file? Stdin? MCP-server-triggered? Operator-typed prompt? | §3 stage 5; §4 | ✅ **RESOLVED 2026-05-19** — Python-API placeholder for Track A (`harness_runtime.run(workflow)`); operator-facing ingress deferred to Track B's definitional pass. See `phase_2_fork_F-P2-2_workflow_ingress.md`. Shrinks Track A: no workflow-file format, no discovery, no CLI argument parsing in Track A. |
| F-P2-3 | **Tracer provider initialization site** — U-OD-23's `get_tracer_provider()` requires a configured provider; no spec section names who configures it, when in bootstrap, or against what exporter endpoint. | §3 stage 4 | Composition-root concern but the *contract* needs a clear pin — likely an OD-spec addition naming the configuration site. |
| F-P2-4 | **Provider SDK lifecycle ownership** — anthropic / openai / ollama clients have construction + close lifetimes. The CP routing core consumes them but no spec section names the owner. | §3 stage 3 | Composition-root surface; the *owning module* needs a contract pin. |
| F-P2-5 | **In-process OTLP collector daemon start** — U-OD-27 is library-only ("no running collector, no live TUI, no sqlite connection, no daemon"). The runtime starts the daemon — the spec doesn't say when or how. | §2 OD bootstrap; §3 stage 4 | Composition-root concern; likely an OD-spec addition or a Phase 2 runtime-spec section. |

The five forks split: F-P2-1 is a placement call (operator decision, not a spec defect).
F-P2-2 through F-P2-5 are spec-surface gaps — runtime-discovered contract gaps per the
[[spec-tension-record-pattern]]. They route to in-CLI spec-fix discipline before
Session 3 (atomic-decomposition plan) can specify the corresponding units.

---

## 7. What Session 3 needs from this strawman

- The composition-root responsibility decomposition (§2) is the unit-cluster skeleton.
- The bootstrap order (§3) is the unit dependency order.
- The five Class 1 forks (§6) must each be resolved (operator decision or spec
  revision) before the units they touch can be specified.
- The entrypoint surface (§4) and agent-loop placement (§5) are sketch-level only;
  Track B refines them.

The strawman is now ground for both Session 3 and Track B's eventual definitional pass.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `phase-2-session-2-track-a-strawman.md` |
| Authored at | Phase 2 Session 2, 2026-05-19 |
| Authority | D-P2-6 (Phase 2 Session 1 framing) |
| Successor | Class 1 fork resolution → Session 3 atomic-decomposition plan; Track B (when opened) grounds against §2–§5 |
| Revision policy | Sketch artifact; revisions land as Track A progresses |
