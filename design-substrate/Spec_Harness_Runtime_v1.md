# Specification — Harness Runtime v1.1

## Change-note (v1 → v1.1)

**Scope of revision.** Adversarial-review absorption pass per `.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md` (P2-S4-CK gate, 2026-05-19). 7 Class 2 + 3 Class 1 findings absorbed. No Phase-7 §2.7.6 fork engaged; no upstream-phase artifact revision required. Trace-discipline novelty adaptation cleared at the gate.

**Sub-decisions.** F2-01 (fail-class taxonomy) resolved as **Reading 1** per operator decision 2026-05-19: runtime-local fail classes legitimate as distinct from CP validator-fail-taxonomy (different scope: bootstrap-stage failures vs workflow-step failures). New C-RT-14 enumerates the runtime-local set and its relationship to CP's taxonomy.

**Sections revised (substantive).**
- §"ADR scope" — ADR §-citations canonicalized to `§Decision` / `§Consequences` (per actual ADR-F1..F5 + D-ADR section structure verified from the source files).
- §"Cross-axis citation substrate" — axis-spec contract IDs corrected to verified C-NN identifiers (prior v1 cited C-IS-11/14/15 which don't exist; C-CP-04 was misidentified as routing manifest; C-AS-08 was misidentified as tool contract; multiple §-numbers added).
- §"Trace-discipline novelty" — back-flow-shape sketch added (F1-01).
- §3 C-RT-03 — Version-evolution invariant added (F2-04).
- §4 C-RT-04 — Version-evolution invariant added; `providers` field re-typed against new `ProviderClient` Protocol (F2-04, F2-06).
- §5 C-RT-05 — `ProviderClient` Protocol introduced inline; per-provider construction now satisfies the protocol (F2-06).
- §8 C-RT-08 — Idempotency-and-concurrency invariant added: serial calls safe and equivalent to independent runs; concurrent calls from same process surface typed `ConcurrentRunNotSupported` (F2-05).
- §9 C-RT-09 — Version-evolution invariant added (F2-04).
- §12 C-RT-12 — Per-bucket wiring-contract sub-subsections added for the 24 phase-2-runtime edges (F2-07).
- §14 NEW C-RT-14 — Runtime-local fail-class taxonomy + relationship to CP `validator_fail_taxonomy` (F2-01 Reading 1).
- §15 open question #4 — reworded to reflect C-RT-08's pinned decision (F1-02).
- §16 Coherence pass — re-run for v1.1.

**Sections preserved verbatim from v1.** §"Trace-discipline novelty" header + first three paragraphs; §"Axis declaration"; §"Scope and out-of-scope"; §1 C-RT-01; §2 C-RT-02; §6 C-RT-06; §7 C-RT-07; §10 C-RT-10; §11 C-RT-11; §13 C-RT-13; §15 open questions #1, #2, #3, #5, #6, #7.

**Status posture.** Proposed → **Proposed (v1.1)**. P2-S4-CK clearance pending operator confirmation of this revision pass.

**Downstream absorption owed.** Plan v2 §14 traceability table needs one new row for C-RT-14 (fail-class taxonomy) and updated C-RT-12 entry referencing the new per-bucket sub-subsections. Plan revision is a separate small task; not blocking Session 5 entry.

---

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Harness_Runtime_v1.md` |
| Status | **Proposed (v1.1)** — Phase 2 Session 4 runtime-spec authoring + adversarial-review absorption; P2-S4-CK clearance pending |
| Date | 2026-05-19 (v1.1) |
| Phase | Phase 2 (Track A — runtime integration) Session 4 |
| Axis | **Runtime** (new sibling axis under `harness-runtime/`; composition root + bootstrap + ingress for the IS/AS/CP/OD library substrate) |
| Source-set | F-P2-1 / F-P2-2 / F-P2-3 / F-P2-4 / F-P2-5 fork resolutions; `.harness/phase-2-session-1-framing.md` (D-P2-1..D-P2-6); `.harness/phase-2-session-2-track-a-strawman.md`; `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2 (the 50-unit Track A plan); `.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md` (v1.1 revision driver); ADR-F1 v1.2, F2 v1.2, F3 v1.1, F4 v1.1, F5 v1.1; ADR-D1 v1.2, D2 v1.2, D6 v1.2; ADD v1.3; landed code across `harness-{core,is,as,cp,od,cxa}/` |
| Entry authorization | Operator directive at Session 4 open 2026-05-19; Session 3 close commit `36dbc54` (Track A plan v2 landed + adversarial-reviewed) |
| Exit gate | This spec filed at v1.1; `harness-adversarial-reviewer` second pass on v1.1 returns no Class 3 findings AND no new Class 2 findings (or operator clears them); Session 5 entry directive authored at session close |
| Revision | v1 (2026-05-19 initial) → v1.1 (2026-05-19 adversarial-review absorption) |

---

## Trace-discipline novelty (read first)

This is the workspace's **first net-new axis spec**. The four existing axis specs (IS / AS / CP / OD) inherit a fixed trace structure: each contract names a PRD requirement (R-{AXIS}-NN), an ADR commitment, and a persona linkage. The runtime axis cannot honor that structure unchanged:

- **PRD v1.1 has no R-RT-* requirements.** The PRD predates the runtime axis. The runtime *enables* every R-IS/AS/CP/OD-* requirement (the library is unrunnable without it); it does not introduce net-new observable behavior of its own.
- **Persona is explicitly uncommitted** per workspace `CLAUDE.md` §1 framing. The runtime spec touches no persona-dependent decision (operator-facing surfaces are deferred to Track B per F-P2-2).
- **The source-of-truth for runtime commitments is the F-P2-N fork resolutions.** Five operator-ratified architectural decisions (composition-root package placement, ingress shape, three lifecycle ownerships) anchor this spec.

**Adapted trace convention for this spec:**

| Standard field | Runtime-axis substitution |
|---|---|
| `PRD requirement(s) satisfied` | `PRD enablement` — names the R-{AXIS}-NN requirements the contract enables (composition-level inheritance, not direct satisfaction). |
| `ADR commitment(s) honored` | Unchanged. Every contract cites ≥1 ADR by ID + version + section. |
| `Persona linkage` | Replaced by `Fork-resolution provenance` — names which F-P2-N fork (and which session ratified it) the contract derives from. For contracts not derived from a fork, this field reads `n/a (general runtime discipline)`. |

This adaptation is itself a candidate Class 1 review surface. **Adversarial review at P2-S4-CK 2026-05-19 judged the adaptation sufficient at this gate.** Re-evaluable at any future aggregate review.

**Back-flow shape if re-evaluation flips the verdict.** A PRD v1.2 amendment introducing a new §N Runtime requirements section would carry the R-RT-* requirements that today's runtime contracts implicitly enable. Candidate R-RT-* shape: one requirement per F-P2-N fork's observable consequence (e.g., R-RT-01 "the runtime starts under H_E with bounded bootstrap time"; R-RT-02 "the runtime exposes a single async Python ingress accepting a workflow object"; etc.). Exact shape is operator-decided at back-flow time, not pre-pinned here.

---

## Axis declaration

The **Runtime axis** owns the composition root, bootstrap sequencing, in-process lifecycle ownership for provider clients + tracer provider + collector daemon, the Python API ingress surface (`harness_runtime.run(workflow)`), shutdown sequencing, and the runtime instantiation of the cross-axis composition substrate (terminal exporter manifest import + 24 phase-2-runtime CXA edges).

The Runtime axis is *not* a fifth axis at the design layer — it does not introduce new schemas, contracts, or invariants over IS/AS/CP/OD library content. It is the axis at the *execution* layer that turns the four library axes into a startable process under H_E (Claude Code CLI as Phase-7 execution surface) and, eventually, a self-hosted H_T.

Package: `harness-runtime/` (workspace member; new under Phase 2 Track A).

---

## ADR scope

ADR citations follow the canonical convention verified from each ADR file: F-ADRs use `§Status / §Context / §Decision / §Rationale / §Consequences / §Alternatives considered / §References`; D-ADRs add `§1.N` subsection structure under `§Decision`.

| ADR | Version | Role in this spec |
|---|---|---|
| ADR-F1 | v1.2 | `§Decision` — Multi-LLM commitment. The runtime constructs three async provider clients (`anthropic.AsyncAnthropic`, `openai.AsyncOpenAI`, `ollama.AsyncClient`) under capability-aware abstraction. NOT LiteLLM. |
| ADR-F2 | v1.2 | `§Decision` — State ledger primitive. The runtime reattaches the state-ledger chain at bootstrap stage 1 and wraps the IS writer for audit-ledger composition at stage 4. |
| ADR-F3 | v1.1 | `§Decision` — Index primitive. The runtime reattaches the content-addressed index + semantic cache at bootstrap stage 1. |
| ADR-F4 | v1.1 | `§Decision` + `§Consequences (b)(iv)` — Workflow lifecycle primitive. The runtime accepts a `WorkflowObject` at ingress and hands it to CP's lifecycle loop. Drain at shutdown polls a runtime-owned flag at CP lifecycle boundaries. `§Consequences (b)(iv)` is also the trace target for OD spec C-OD-20 collector placement, transitively. |
| ADR-F5 | v1.1 | `§Decision` — Observability substrate primitive. The runtime constructs the OTel `TracerProvider`, registers it globally via `set_tracer_provider(...)`, and starts the in-process OTLP collector daemon. |
| ADR-D1 | v1.2 | `§Decision §1.1` (engine-class taxonomy) — informs `EngineClass` enum the runtime binds to provider clients at stage 3a/3b. |
| ADR-D2 | v1.2 | `§Decision §1.1` (deployment-surface × blast-radius matrix) + `§1.3` (per-MCP-transport sandbox-tier floor) — sandbox-tier dispatch binding at stage 2 honors these. |
| ADR-D6 | v1.2 | `§Decision §1.2` (unified span schema ingestion contract) + `§1.7` (local-first OTLP collector commitment) — TracerProvider resource attributes carry the 12-namespace tags; collector daemon supervision derives from §1.7. |
| ADD v1.3 | — | ADR consolidation. The runtime spec inherits the coherent architectural overview at the composition layer. |

Other ADRs (D3 validation, D4 cost, D5 topology) are honored *transitively* — the runtime instantiates CP/OD primitives that themselves honor those ADRs; the runtime spec does not restate them.

---

## Cross-axis citation substrate

The runtime spec consumes the following contracts from the four axis specs at composition time. Contract IDs verified against actual axis-spec contract enumerations (IS v1 has C-IS-01..10; CP v1.3 has C-CP-01..24; OD v1.4 has C-OD-01..23; AS v1.3 has C-AS-01..16).

| Source spec | Contracts consumed | Composition shape |
|---|---|---|
| `Spec_Information_Substrate_v1.md` | C-IS-01 §1 (canonical filesystem path contract); C-IS-05 §5 (state-ledger entry shape signature, 6-field); C-IS-06 §6 (hash-chain integrity construction discipline); C-IS-07 §7 (state-ledger read/write contract pair); C-IS-08 §8 (workload-class-opt-in shadow-Git checkpoint contract); C-IS-09 §9 (workload-class-opt-in worktree-isolation contract); C-IS-10 §10 (substrate seam exports surface) | Runtime instantiates `PathResolver(binding)` per C-IS-01, `WorktreeIsolationManager(...)` per C-IS-09, shadow-Git supervisor per C-IS-08, ledger writer wrapper per C-IS-05+06+07 at stage 1; imports C-IS-10 exports at stage 6 |
| `Spec_Action_Surface_v1.md` | C-AS-01 §1 (4-tier sandbox-isolation enumeration); C-AS-02 §2 (per-tool sandbox-tier `max()` composition); C-AS-05 §5 (`fetch_secret(name, scope, tier) -> SecretRef` signature); C-AS-08 §8 (secret-fetch structure-not-content audit composition); C-AS-10 §10 (per-MCP-transport sandbox-tier floor); C-AS-15 §15 (sandbox-bounded span schema `sandbox.*`); C-AS-16 §16 (AS substrate seam exports surface) | Runtime loads skills + registers tool contracts at stage 2 (note: tool-contract *registration site* is not formally a C-AS-NN contract — see risk surface #4); starts MCP host + clients honoring C-AS-10; binds sandbox-tier dispatch per C-AS-01+02; secret resolution via C-AS-05 with C-AS-08 audit; imports C-AS-16 exports at stage 6 |
| `Spec_Control_Plane_v1_3.md` | C-CP-01 §1 (capability-aware multi-LLM provider abstraction); C-CP-02 §2 (layered cheapest-deterministic-first routing strategy); C-CP-04 §4 (cross-family fallback chain composition); C-CP-05 §5 (F3 capability-floor lifecycle event surface); C-CP-06 §6 (manifest-declaration invocation discipline with per-step opt-in override); C-CP-07 §7 (engine class committed per deployment surface); C-CP-09 §9 (`engine.*` span attribute namespace); C-CP-10 (topology pattern — first contract in the multi-agent topology cluster C-CP-10..C-CP-22); C-CP-24 (cross-axis composition exports) | Runtime constructs provider clients (stage 3a) honoring C-CP-01; builds routing manifest + binds reliability primitives at stage 3b honoring C-CP-02+04+05; binds override evaluator + topology dispatcher + lifecycle emission at stage 5 honoring C-CP-06+09+10; imports C-CP-24 exports at stage 6 |
| `Spec_Operational_Discipline_v1_4.md` | C-OD-01 §1 (9-cell deployment-surface × persona-tier matrix; §1.2 7-value `CollectorPlacement` enum after v1.4 FF-2 resolution); C-OD-20 §20.1 (per-cell OTLP collector placement + F4 process-tier reachability); OD spec contracts for cost-attribution chain (within C-OD-01..23 range; specific §-pin verified at U-RT-31 landing); OD audit-ledger schema (within C-OD-01..23 range; specific §-pin verified at U-RT-32 landing) | Runtime constructs TracerProvider per stage 4; collector daemon supervisor honors C-OD-01 §1.2 enum + C-OD-20 §20.1 placement matrix; cost-attribution + audit-ledger writers wire to landed OD primitives (exact contract §-pins resolved at unit landing — see risk surface #4) |
| `Cross_Axis_Composition_Document_v2_3.md` | §3 Pattern P1 22 genuine typed seams; §2.3 24 phase-2-runtime edges; the 5 terminal aggregate exporter manifests | Runtime imports terminal exporter manifests for side-effect at stage 6 (see C-RT-12 §12.1), wires the 24 phase-2-runtime edges per per-bucket sub-subsections (C-RT-12 §12.2–§12.6), verifies Pattern P1 identity-equality at L11 |

**Note on partial §-precision.** Two cross-axis citations resolve to a *contract range* rather than a specific §-pin: cost-attribution and audit-ledger schema in OD. These were originally cited as C-OD-12 and a single C-OD ID in v1; verification against OD v1.4 + its predecessor v1.2/v1.3 (which carry the unrevised §2..§19 + §21..§23 content) is deferred to unit landing at U-RT-31 / U-RT-32, since the OD v1.4 file is amendment-only and full enumeration requires reading the predecessor. This is acceptable per the canonical convention's "verify at consumption time" pattern for amendment-only spec files. If the resolved §-pin reveals a contract gap (cost-attribution or audit-ledger writer not in fact specified), surface as Class 1 fork at U-RT-31/U-RT-32 landing.

---

## Scope and out-of-scope

| In-scope (Runtime axis owns) | Out-of-scope (other axes / Track B / future) |
|---|---|
| 9-stage canonical `BootstrapStage` enum + ordering invariants | Algorithm for selecting which `TopologyPattern` a workflow uses (Track B) |
| `RuntimeConfig` input schema | Operator-facing config file format (Track B); CLI argument parsing (Track B) |
| `HarnessContext` post-bootstrap shape (frozen) | Operator-facing context exposure (Track B) |
| `ProviderClient` Protocol (new at v1.1) | Per-provider SDK internals; provider-agnostic message format (CP spec; not runtime) |
| Async provider SDK lifecycle (F-P2-4) | The capability-aware routing algorithm itself (CP spec) |
| TracerProvider construction + global registration (F-P2-3) | OTel attribute schemas + 12-namespace map (OD spec) |
| In-process OTLP collector daemon supervision (F-P2-5) | TUI trace browser (Track B); collector ring-buffer/sqlite internals (OD spec) |
| `harness_runtime.run(workflow)` Python API (F-P2-2) | CLI `run` subcommand (Track B); markdown workflow authoring (Track B); MCP-server-triggered workflows (Track B); operator-typed prompt → workflow generation (Track B) |
| `RunResult` shape | Operator-facing result formatting (Track B) |
| Shutdown order (drain → flush → close) | Distributed shutdown coordination (out of scope for Track A) |
| Drain semantics (runtime-owned flag-polling) | CP-native drain primitive (does not exist; if CP later adds one, U-RT-44 refactors to delegate) |
| CXA wiring obligations (terminal exporter manifest import + 24 phase-2-runtime edges) | The 22 genuine typed CXA seams themselves (axis spec content; runtime only verifies identity-equality) |
| Admin stub semantics (`harness-inspect`, `harness-shutdown`) | Richer admin IPC (Track B); operator-facing inspection UI (Track B) |
| Runtime-local fail-class taxonomy (new at v1.1 — see C-RT-14) | CP `validator_fail_taxonomy` (orthogonal — CP owns workflow-step-level fail classes) |
| 5 F-P2-N fork resolutions as recorded canonical decisions | Track B definitional pass (separate authoring stream) |

---

## §1 C-RT-01 — Canonical `BootstrapStage` enum (9 values, fixed order)

**Contract surface.** Enum.

**PRD enablement.** Enables every R-IS/AS/CP/OD-* requirement at composition (no runtime, no requirement satisfaction). Specifically gates R-CP-* multi-LLM-routing requirements and R-OD-* observability requirements that depend on bootstrap ordering.

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (CP_CLIENTS at stage 3a precedes CP_ROUTING at stage 3b); ADR-F5 v1.1 §Decision (OD stage 4 must come after IS stage 1 since OD audit writer wraps IS ledger writer).

**Fork-resolution provenance.** F-P2-3 + F-P2-4 + F-P2-5 (the three lifecycle-ownership forks fix the stage-4 OD bundle and the stage-3a CP_CLIENTS responsibility).

**Specification content.**

The runtime defines exactly nine bootstrap stages, in this fixed order:

| Index | Enum member | Owner of work |
|---|---|---|
| 0 | `PREAMBLE` | Config resolution (RuntimeConfig materialization, sub-config derivation) |
| 1 | `IS` | Path-class registry, worktree + shadow-Git, state-ledger reattach, content-addressed index + semantic cache reattach |
| 2 | `AS` | Skills load, tool-contract registration, MCP host startup + client connect, sandbox-tier dispatch binding |
| 3a | `CP_CLIENTS` | Async provider SDK client construction (anthropic / openai / ollama), capability-aware abstraction binding |
| 3b | `CP_ROUTING` | Routing manifest construction, engine selection, retry/breaker/idempotency runtime binding, HITL placement registry, sub-agent handoff registry |
| 4 | `OD` | TracerProvider construction + global registration, BatchSpanProcessor + OTLP exporter, in-process collector daemon, ring-buffer + sqlite rotation, cost attribution chain, audit-ledger writer |
| 5 | `LOOP_INIT` | Per-step override evaluator runtime binding, topology dispatcher runtime binding, lifecycle event emission hook |
| 6 | `CXA_WIRING` | Terminal aggregate exporter manifest import (side-effect), 24 phase-2-runtime CXA edges wired |
| 7 | `INGRESS_ACCEPT` | Accept `WorkflowObject` via `run()`; hand to CP lifecycle |

`BootstrapStage` is a Python `enum.Enum` with `len(BootstrapStage) == 9` and `list(BootstrapStage) == [PREAMBLE, IS, AS, CP_CLIENTS, CP_ROUTING, OD, LOOP_INIT, CXA_WIRING, INGRESS_ACCEPT]`. The two stage-3 members (`CP_CLIENTS`, `CP_ROUTING`) are sequenced adjacent and both correspond to file-naming convention `stage_3a_*.py` / `stage_3b_*.py`. There is no `stage_8`; INGRESS_ACCEPT is the terminal bootstrap stage.

**Invariants.**

- No stage runs before its strict predecessor completes successfully. Stage failures roll back already-completed stages in reverse order (see C-RT-10).
- Each stage emits exactly one `workflow_event_class` lifecycle event on entry and exit (per ADR-F5 §Decision).
- The enum is immutable across runtime versions within v1; adding a stage is a major-version event (v2.0).

**Deferred to implementation discretion.** Specific span name and event attribute set per stage (deferred to OD spec + landed `harness_cp.lifecycle_event_span_map`); specific file layout under `bootstrap/` (canonical naming above is binding, internal organization is implementation-discretion).

---

## §2 C-RT-02 — Bootstrap orchestrator + stage-ordering invariants

**Contract surface.** Surface contract.

**PRD enablement.** Enables all axes — bootstrap is the precondition for any runtime behavior.

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (ledger reattach is stage 1; audit writer at stage 4 wraps it); ADR-F5 v1.1 §Decision (tracer provider at stage 4 must precede any axis primitive that calls `get_tracer_provider()`).

**Fork-resolution provenance.** F-P2-3 + F-P2-4 + F-P2-5.

**Specification content.**

The orchestrator (`harness_runtime.bootstrap.__init__`) executes the 9 stages from C-RT-01 in order. Each stage is implemented as a single module (`stage_0_preamble.py`, ..., `stage_7_ingress.py`, with `stage_3a_cp_clients.py` + `stage_3b_cp_routing.py` for the split). Each stage module exposes a single entry point `async def execute(ctx: HarnessContext) -> StageResult` that mutates `ctx` in place during bootstrap (the immutability invariant of `HarnessContext` per C-RT-04 holds only *post-bootstrap*).

**Forward invariants (must hold at successful completion of each stage):**

| After stage | Post-condition |
|---|---|
| 0 PREAMBLE | `ctx.config: RuntimeConfig` populated; sub-configs (path bindings, secrets, OTel, collector) materialized |
| 1 IS | `ctx.path_resolver`, `ctx.worktree_manager`, `ctx.shadow_git`, `ctx.ledger_writer`, `ctx.index`, `ctx.cache` all non-None; ledger chain reattached and verified |
| 2 AS | `ctx.skills`, `ctx.tool_contracts`, `ctx.mcp_host`, `ctx.mcp_clients`, `ctx.sandbox_dispatch` all non-None; MCP clients in READY state |
| 3a CP_CLIENTS | `ctx.providers: dict[str, ProviderClient]` has entries for `anthropic`, `openai`, `ollama`; each client passes an async ping (see C-RT-05 for `ProviderClient` Protocol) |
| 3b CP_ROUTING | `ctx.routing_manifest`, `ctx.engine_selector`, `ctx.fallback_chain`, `ctx.retry_breaker`, `ctx.hitl_registry`, `ctx.handoff_registry` all non-None |
| 4 OD | `opentelemetry.trace.get_tracer_provider()` returns the runtime-registered provider; `ctx.collector_daemon` is running (health-check ok); `ctx.cost_chain`, `ctx.audit_writer` non-None |
| 5 LOOP_INIT | `ctx.override_evaluator`, `ctx.topology_dispatcher`, `ctx.lifecycle_emitter` all non-None |
| 6 CXA_WIRING | All 5 terminal exporter manifests imported; all 24 phase-2-runtime edges wired (test fixture exercises each) |
| 7 INGRESS_ACCEPT | `ctx` frozen; `harness_runtime.run` accepts a `WorkflowObject` and dispatches |

**Failure-mode taxonomy.** Per the runtime-local fail-class set at C-RT-14. The orchestrator surfaces stage failures via `RT-FAIL-BOOTSTRAP` (permanent; cause-attribution identifies the specific stage) or `RT-FAIL-PARTIAL-ROLLBACK-REQUIRED` (stage N+1 fails after stage N completed; rollback executes reverse-order shutdown for stages 0..N). Stage-internal transient failures use `RT-FAIL-TRANSIENT` (bounded retry; persistent escalates to `RT-FAIL-BOOTSTRAP`).

**Deferred to implementation discretion.** Retry intervals at stage-internal bounded retry (suggest 200ms × 2^attempt); structured-error type hierarchy (suggest one exception class per stage with `BootstrapStage` field); concurrent stage execution within an axis (e.g., parallel client construction at stage 3a) is implementation-discretion as long as the post-conditions hold.

---

## §3 C-RT-03 — `RuntimeConfig` schema

**Contract surface.** Schema.

**PRD enablement.** Enables R-CP-* (multi-LLM routing requires per-provider config); R-OD-* (observability requires OTel endpoint + sampler config); R-IS-* (state ledger requires path bindings).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (provider keys allowlist); ADR-D6 v1.2 §Decision §1.2 (unified span schema — 12-namespace resource attrs).

**Fork-resolution provenance.** F-P2-2 (config-vs-CLI ingress split).

**Specification content.**

`RuntimeConfig` is a Pydantic v2 `BaseModel` (frozen). The schema is the contract; field order and type discipline are normative.

| Field | Type | Required | Semantic |
|---|---|---|---|
| `deployment_surface` | `DeploymentSurface` (harness-core enum) | yes | Local / hybrid / cloud — drives OTel resource attrs + collector placement |
| `repository_root` | `pathlib.Path` | yes | Absolute path; must exist; basis for `.harness/` and PATH_CLASS_REGISTRY resolution |
| `path_bindings` | `PathBindingConfig` (sub-model) | yes | Inputs to `PathResolver(binding)`; validated against `WorkloadManifestOptInSchema` |
| `provider_secrets` | `ProviderSecretsConfig` (sub-model) | yes | Keyring allowlist *keys* only; no secret values in config |
| `otel` | `OTelConfig` (sub-model) | yes | OTLP endpoint, sampler mode, additional resource attrs |
| `collector` | `CollectorConfig` (sub-model) | yes | Ring buffer size, sqlite rotation thresholds, placement-matrix selection |
| `mcp_clients` | `list[MCPClientConfig]` | no (default `[]`) | MCP client connection configs |
| `default_topology` | `TopologyPattern` (CP enum) | yes | The TopologyPattern the runtime dispatches when no per-workflow override is set |
| `tenant_id` | `str | None` | no | Multi-tenant separation key per OD audit-ledger; None = single-tenant mode |

**Invariants.**

- `model_config = ConfigDict(frozen=True, extra='forbid')` — frozen post-construction; unknown keys rejected.
- `repository_root.is_absolute()` and `repository_root.exists()`.
- `provider_secrets` contains only allowlist keys; runtime resolves values via `keyring`. No secret value ever appears in `RuntimeConfig` instances or in span attributes.
- Precedence at construction: kwargs to `run()` > environment variables > defaults. (No file-loading; that is Track B.)
- **Version evolution (added at v1.1).** Adding an *optional* field is a minor version bump (v1.N → v1.(N+1)); existing callers continue to work. Adding a *required* field is a major bump (v1 → v2); existing callers without the field surface typed `IncompatibleConfigVersion` at materialization. Removing a field is always a major bump; the field stays through one minor version marked `Deprecated` (Pydantic field metadata) with a runtime warning. Type-narrowing of an existing field (e.g., from `str` to a `Literal[...]`) is a major bump. Type-widening is a minor bump.

**Failure-mode taxonomy.**

| Fail class | Trigger |
|---|---|
| `RT-FAIL-CONFIG` (permanent) | Required field missing; unknown field present; `repository_root` not absolute or not existing; type mismatch |
| `RT-FAIL-CONFIG-VERSION` (permanent) | Incompatible config version per Version evolution clause above |
| `RT-FAIL-SECRET-MISSING` (permanent; deferred to stage 0 secret resolution) | `provider_secrets` references an allowlist key not present in keyring — raises typed `SecretFailClass` per AS C-AS-05 §5 |

**Deferred to implementation discretion.** Exact field names for `OTelConfig` and `CollectorConfig` (inherited from OD spec C-OD-01 §1.2 + C-OD-20 §20.1 conventions); env-var naming (suggest `HARNESS_*` prefix); kwargs-vs-env precedence resolver implementation; specific `Deprecated` warning text.

---

## §4 C-RT-04 — `HarnessContext` schema (frozen post-bootstrap)

**Contract surface.** Schema.

**PRD enablement.** Enables all axes — `HarnessContext` is the post-bootstrap handle through which `run()` reaches every wired component.

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision; ADR-F2 v1.2 §Decision; ADR-F3 v1.1 §Decision; ADR-F4 v1.1 §Decision; ADR-F5 v1.1 §Decision (the context holds primitives for each ADR-F).

**Fork-resolution provenance.** F-P2-1 (`harness-runtime/` is the package that owns this type).

**Specification content.**

`HarnessContext` is a Pydantic v2 `BaseModel`. Bootstrap mutates it stage-by-stage; at stage 7 INGRESS_ACCEPT it is frozen and handed to `run()`.

| Field | Type | Populated at stage | Semantic |
|---|---|---|---|
| `config` | `RuntimeConfig` (frozen) | 0 | Resolved configuration |
| `path_resolver` | `harness_is.PathResolver` | 1 | Path-class registry handle |
| `worktree_manager` | `harness_is.WorktreeIsolationManager` | 1 | Worktree isolation |
| `shadow_git` | `ShadowGitSupervisor` (runtime-defined) | 1 | Shadow-Git checkpoint/rollback supervisor |
| `ledger_writer` | `LedgerWriter` (runtime-defined, wraps IS) | 1 | State-ledger writer wrapper |
| `index` | `ContentAddressedIndex` (IS landed) | 1 | Index handle |
| `cache` | `SemanticCache` (IS landed) | 1 | Semantic cache handle |
| `skills` | `dict[SkillID, Skill]` | 2 | Loaded skills indexed by ID |
| `tool_contracts` | `dict[ToolName, ToolContract]` | 2 | Registered tool contracts |
| `mcp_host` | `MCPHost` (FastMCP) | 2 | MCP host handle |
| `mcp_clients` | `dict[ClientName, MCPClient]` | 2 | Connected MCP clients |
| `sandbox_dispatch` | `SandboxDispatchTable` | 2 | Sandbox-tier dispatch |
| `providers` | `dict[str, ProviderClient]` | 3a | `ProviderClient` is the runtime-defined Protocol at C-RT-05. Concrete values: `{'anthropic': AsyncAnthropic, 'openai': AsyncOpenAI, 'ollama': AsyncClient}` (each structurally implements `ProviderClient`) |
| `routing_manifest` | `RoutingManifest` (CP R-2 schema) | 3b | Runtime routing manifest |
| `engine_selector` | `EngineSelector` (CP) | 3b | Engine-class binding |
| `fallback_chain` | `FallbackChain` (CP) | 3b | Cross-family fallback chain |
| `retry_breaker` | `RetryBreakerRegistry` (CP) | 3b | Retry/breaker/idempotency primitives bound |
| `hitl_registry` | `HITLPlacementRegistry` (CP) | 3b | HITL placement registry |
| `handoff_registry` | `HandoffRegistry` (CP) | 3b | Sub-agent handoff + brief registry |
| `tracer_provider` | `opentelemetry.sdk.trace.TracerProvider` | 4 | Constructed + globally registered |
| `collector_daemon` | `CollectorDaemonHandle` (runtime-defined) | 4 | In-process OTLP collector supervisor handle |
| `cost_chain` | `CostAttributionChain` (OD) | 4 | 5-step cost-attribution chain |
| `audit_writer` | `AuditLedgerWriter` (runtime-defined, wraps IS+OD) | 4 | Multi-tenant audit-ledger writer |
| `override_evaluator` | `PerStepOverrideEvaluator` (CP) | 5 | Override evaluator runtime |
| `topology_dispatcher` | `TopologyDispatcher` (CP, runtime-bound) | 5 | TopologyPattern dispatcher |
| `lifecycle_emitter` | `LifecycleEventEmitter` (runtime-defined) | 5 | Emits `workflow_event_class` events |
| `drained_flag` | `asyncio.Event` | 0 (initialized) | Set by signal handler; polled by CP loop for drain |

**Invariants.**

- `model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)`. Mutation during bootstrap is via a separate `_MutableHarnessContext` builder; at stage 7 the builder is materialized into the frozen final form.
- Every field is non-`None` at stage 7 EXCEPT `mcp_clients` (empty dict permitted if no clients configured) and `tenant_id`-derived audit-writer scoping.
- `tracer_provider` field is informational only; consumers should call `opentelemetry.trace.get_tracer_provider()` per ADR-F5 §Decision.
- **Version evolution (added at v1.1).** `HarnessContext` is an internal type (consumers reach into specific fields, not the whole context); field-additions are minor; field-removals or type-changes are major (consumers break). The type is not part of any operator-facing surface in Track A.

**Failure-mode taxonomy.** Construction failure of any field surfaces as the relevant stage's failure (per C-RT-02 and C-RT-14).

**Deferred to implementation discretion.** Internal `_MutableHarnessContext` builder shape; whether `providers` keys are string literals or an enum (suggest enum from `harness_core` if landed); whether `tenant_id` defaults wrap audit-writer scoping or live separately on the writer.

---

## §5 C-RT-05 — Provider SDK lifecycle (F-P2-4 absorption) + `ProviderClient` Protocol

**Contract surface.** Surface contract + lifecycle obligations + Protocol definition.

**PRD enablement.** Enables R-CP-* multi-LLM routing requirements — the routing core cannot route without constructed clients.

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (three providers under capability-aware abstraction; NOT LiteLLM); ADR-D2 v1.2 §Decision §1.1 (sandbox tier — provider clients respect sandbox-tier reachability).

**Fork-resolution provenance.** F-P2-4 ratified 2026-05-19.

**Specification content.**

The runtime owns construction, lifetime, and close of three async provider clients. Construction occurs at stage 3a CP_CLIENTS; close occurs at the final shutdown step in reverse order (see C-RT-10).

**`ProviderClient` Protocol (new at v1.1):**

The three async clients have no shared base class across the three SDKs. The runtime defines a structural `Protocol` (PEP 544) that each concrete client implements via duck-typing:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProviderClient(Protocol):
    """Structural protocol every async provider client satisfies.

    Methods are intentionally minimal — the CP capability-aware abstraction
    layer is what dispatches to provider-specific methods. ProviderClient
    only carries lifecycle obligations the runtime owns.
    """
    async def aclose(self) -> None:
        """Close the underlying SDK client + connections. Idempotent."""
        ...
```

Implementation note: `anthropic.AsyncAnthropic` exposes `.close()` (awaitable in recent versions); `openai.AsyncOpenAI` exposes `.close()` (awaitable); `ollama.AsyncClient` may not expose a public close. Runtime wraps each in a thin adapter (per-provider module under `harness_runtime/lifecycle/providers.py`) so all three satisfy `ProviderClient.aclose()` uniformly. Adapters are runtime-defined; the Protocol is the canonical contract.

**Construction table:**

| Provider | Underlying SDK class | Adapter satisfies | Construction | aclose() implementation |
|---|---|---|---|---|
| Anthropic | `anthropic.AsyncAnthropic` | `ProviderClient` | `AsyncAnthropic(api_key=keyring_resolve('anthropic_key'), ...)` | `await client.close()` |
| OpenAI | `openai.AsyncOpenAI` | `ProviderClient` | `AsyncOpenAI(api_key=keyring_resolve('openai_key'), ...)` | `await client.close()` |
| Ollama | `ollama.AsyncClient` | `ProviderClient` | `AsyncClient(host=config.ollama_host or default)` | `await client.close()` if exposed; else best-effort connection cleanup (adapter handles) |

**Invariants.**

- All clients are **async variants** (matches `async def run(...)` posture per C-RT-08). Sync variants (`anthropic.Anthropic`, `openai.OpenAI`, `ollama.Client`) MUST NOT be constructed by the runtime.
- Each concrete client passes `isinstance(client, ProviderClient)` (per `@runtime_checkable`) when accessed via its adapter.
- Secret resolution at construction time goes through AS `secret_fetch` per C-AS-05 §5; allowlist enforced; secret never logged or emitted as span attribute.
- Construction errors (auth failure, network failure on initial ping) surface as stage 3a failure with provider identity attached to the typed error.
- Capability-aware abstraction binding at C-RT-04's `providers` field hands the 3 adapters to CP `provider_capabilities` per C-CP-01 §1.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-SECRET-MISSING` (permanent) | Secret allowlist key missing from keyring | Stage 3a fails; no rollback (no prior runtime state to undo) |
| `RT-FAIL-TRANSIENT` (transient) | Initial async ping fails with network error | Bounded retry (max 3 per stage policy); persistent → escalation to `RT-FAIL-PROVIDER-AUTH` or `RT-FAIL-PROVIDER-UNREACHABLE` |
| `RT-FAIL-PROVIDER-AUTH` (permanent) | Auth failure (401 / 403 from provider) | No retry; surface typed error naming the provider |
| `RT-FAIL-PROVIDER-DEGRADED` (degraded) | Ollama local-tier unreachable AND `RuntimeConfig.ollama_optional == True` | Surface typed warning; stage continues with 2-provider context; routing core sees Ollama as unavailable per C-CP-01 |

**Deferred to implementation discretion.** Async ping mechanism (suggest a low-cost `count_tokens` or model-list call per provider); whether `ollama_optional` is a top-level `RuntimeConfig` field or under `ProviderSecretsConfig`; specific keyring service-name convention (suggest `harness-runtime`); adapter module organization under `harness_runtime/lifecycle/providers.py`.

---

## §6 C-RT-06 — TracerProvider lifecycle (F-P2-3 absorption)

**Contract surface.** Surface contract + lifecycle obligations.

**PRD enablement.** Enables R-OD-* observability requirements — no observability before TracerProvider registered.

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision (tracer-provider is foundational); ADR-D6 v1.2 §Decision §1.2 (unified span schema — 12-namespace resource attrs).

**Fork-resolution provenance.** F-P2-3 ratified 2026-05-19.

**Specification content.**

The runtime constructs and globally registers the OTel `TracerProvider` at stage 4 OD, before any axis primitive's first span emission.

**Construction sequence (at stage 4):**

1. Build `Resource` with attributes from `RuntimeConfig.deployment_surface` plus all 12 OTel namespace tags per ADR-D6 §Decision §1.2 + OD spec C-OD-01 §1 conventions.
2. Construct `TracerProvider(resource=resource, sampler=sampler_from_config)`.
3. Attach `BatchSpanProcessor(OTLPSpanExporter(endpoint=config.otel.endpoint, ...))` per OD spec C-OD-20 §20.1 collector-placement matrix.
4. Call `opentelemetry.trace.set_tracer_provider(provider)` — the global registration that landed OD `operator_burden_eval_primitives.py`'s `get_tracer_provider()` call depends on.

**Invariants.**

- `set_tracer_provider(...)` is called exactly once per process; double-registration is a runtime error (also see C-RT-08 idempotency invariant).
- The call precedes execution of every subsequent stage (5, 6, 7) AND any code path that emits a span.
- Resource attributes are immutable after registration; mutations require process restart.
- Provider stored on `HarnessContext.tracer_provider` for diagnostic introspection only; consumers acquire tracers via `opentelemetry.trace.get_tracer(...)` (which uses the global provider).
- On shutdown (per C-RT-10): `provider.force_flush(timeout_millis=...)` then `provider.shutdown()` — both awaitable.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-CONFIG` (permanent) | OTLP endpoint URL malformed (caught at C-RT-03 validation) | Surfaces at stage 0, not stage 4 |
| `RT-FAIL-TRANSIENT` (transient — collector reachability) | OTLP exporter cannot reach endpoint on first attempt | Construction does not require reachability (BSP buffers); reachability surfaces as collector-daemon health (C-RT-07) and downstream span-drop metrics |
| `RT-FAIL-CONCURRENT-REGISTRATION` (permanent) | `set_tracer_provider` called twice in same process | Typed error; possible indicator of orchestrator bug or `run()` concurrent-invocation violation (see C-RT-08) |

**Deferred to implementation discretion.** Sampler choice (suggest `ParentBased(TraceIdRatioBased)` mapped from `RuntimeConfig.otel.sampler_mode`); `BatchSpanProcessor` tuning constants (suggest OD spec defaults); exporter protocol (suggest gRPC; HTTP/protobuf accepted via config).

---

## §7 C-RT-07 — In-process OTLP collector daemon lifecycle (F-P2-5 absorption)

**Contract surface.** Surface contract + supervision contract.

**PRD enablement.** Enables R-OD-* observability requirements that depend on a running collector (TUI trace browser per OD — TUI is Track B; collector is Track A).

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision; ADR-D6 v1.2 §Decision §1.7 (local-first OTLP collector commitment).

**Fork-resolution provenance.** F-P2-5 ratified 2026-05-19.

**Specification content.**

OD spec C-OD-20 §20.1 defines the collector placement matrix; landed `harness_od.local_first_otlp_collector` exposes the collector as a *library* (ring-buffer + sqlite rotation + no-network-egress policy). The runtime owns the *daemon* that runs the library as an in-process supervised component.

**Supervisor obligations (the runtime piece):**

- Start the daemon at stage 4, after TracerProvider registration so that spans flow through BSP → OTLP exporter → daemon → ring-buffer + sqlite.
- Expose a health check (typed: `healthy | degraded | failed`). Daemon reports health every N seconds (configurable, default 10s).
- On daemon crash, restart bounded: max 3 restarts within 60 seconds. After bounded-restart exhaustion, surface as harness-level `degraded` state; do not crash the harness (spans will be dropped at BSP buffer overflow; cost attribution continues from in-memory state).
- On structured stop (during C-RT-10 shutdown): flush daemon buffers to sqlite, close sqlite cleanly, terminate daemon process/thread, await termination with timeout.
- No-network-egress invariant per OD §Decision §1.7 is preserved by the daemon library; the supervisor does not weaken it.

**Daemon implementation mode.** Implementation-discretion: the supervisor may run the daemon as a separate process (subprocess), as an asyncio task in the same process, or as a thread. Choice affects crash-isolation properties but not the supervisor contract.

**Invariants.**

- Daemon lifecycle is strictly contained within harness process lifecycle. No collector survives harness shutdown; no collector persists across runs (sqlite file persists when on-disk persistence is configured; daemon does not).
- Collector binding at `local_first_otlp_collector.bind_in_process_collector(...)` per OD spec is called once at stage 4.
- sqlite trace-storage location is **OD-internal** per OD plan v2.6 §0.9 (`OD-internal` framing): the collector library owns the sqlite path semantics, not the IS `PATH_CLASS_REGISTRY`. The 4-value IS `PATH_CLASS_REGISTRY` (`SKILLS` / `PROMPTS` / `ROUTING_MANIFEST` / `STATE_LEDGER`) intentionally does NOT carry a trace-storage class; adding one would be an X-AL-3 architectural extension surfaced at Phase 7 execution. **At Track A** the collector store is in-memory (`closure_invariant = FRESH_ON_RESTART_OPTIONAL_PERSISTENCE_BETWEEN_RESTARTS` per OD C-OD-19 §19.2), which satisfies the spec floor without requiring a path resolver. Future on-disk persistence routes through an OD-internal path resolution (not the IS registry).

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-COLLECTOR-PATH` (permanent) | sqlite path unwritable (when on-disk persistence configured; in-memory store at Track A bypasses) | Stage 4 fails; rollback stage 3a/3b/2/1/0 |
| `RT-FAIL-TRANSIENT` (transient) | Daemon initial start fails (e.g., port-bind conflict if subprocess mode uses local port) | Bounded retry per supervisor policy |
| `RT-FAIL-COLLECTOR-DEGRADED` (degraded) | Daemon crashes ≤3 times in 60s but recovers | Continue with logged degradation event |
| `RT-FAIL-HARNESS-DEGRADED` (degraded; ongoing) | Daemon crashes >3 times in 60s | Harness continues in degraded mode; surface as ongoing degradation event in audit ledger |

**Deferred to implementation discretion.** Daemon implementation mode (subprocess / asyncio task / thread); health-check cadence (suggest 10s); restart-bound configuration knobs; backpressure mode when buffer fills (drop oldest vs drop newest — suggest drop oldest per OD ring-buffer semantics).

**Risk surface.** OD spec C-OD-20 §20.1 (after v1.4 FF-2 resolution) committed the 7-value `CollectorPlacement` enum and the per-cell placement matrix; it does not explicitly specify daemon supervision semantics (start / health / structured-stop / restart-bound). The contracts above are runtime-axis additions. If P2-S4-CK v1.1 second pass finds that supervision semantics should live in OD spec instead, escalate to back-flow with an OD spec amendment per `Project_Workflow_v1_8.md` §2.7.6.

---

## §8 C-RT-08 — `run()` Python API contract (F-P2-2 absorption)

**Contract surface.** Signature contract.

**PRD enablement.** Enables every R-IS/AS/CP/OD-* requirement that depends on workflow execution (i.e., nearly all of them).

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (run() hands to CP lifecycle loop).

**Fork-resolution provenance.** F-P2-2 ratified 2026-05-19 (Track A ingress = Python API placeholder; operator-facing ingress deferred to Track B).

**Specification content.**

The Track A operator-facing API is exactly one async function exposed at the `harness_runtime` package root:

```python
async def run(
    workflow: WorkflowObject,
    *,
    config: RuntimeConfig | None = None,
) -> RunResult:
    ...
```

**Invariants.**

- **Async-only.** No sync wrapper in Track A. If a synchronous-call surface is later needed, it is Track B's responsibility to add it (and to choose whether via `asyncio.run` wrapping or via a separate threading entry).
- **Single-workflow-object input.** The function accepts exactly one `WorkflowObject` per call. Multi-workflow ingest is Track B (and out of scope for Track A entirely).
- **`config=None` default behavior:** materialize `RuntimeConfig` from defaults + env vars per C-RT-03 precedence. Equivalent to `await run(workflow, config=RuntimeConfig())`.
- **Bootstrap on each invocation OR cached `HarnessContext` reuse?** Track A specifies bootstrap-per-call (no cached context). Track B may add a cached-context entry point with operator-facing lifecycle (`harness_runtime.start() → ctx; await ctx.run(workflow); await ctx.shutdown()`); Track A does not preclude this but does not implement it.
- **Unknown `WorkflowObject` type → typed rejection.** If the input does not conform to the `WorkflowObject` contract (see C-RT-09 risk note), surface typed `InvalidWorkflowError` before bootstrap begins.
- **Idempotency and concurrency (added at v1.1).** Serial invocations are safe and equivalent to independent runs: each call performs a fresh bootstrap → execute → shutdown cycle with no shared state across calls (no cached `HarnessContext`, no cached provider clients, no cached tracer provider). **Concurrent invocations from the same process surface typed `ConcurrentRunNotSupported`** — the second concurrent call detects an existing in-flight `HarnessContext` (via process-local lock initialized at module import) and fails fast before stage 0. Rationale: C-RT-06's `set_tracer_provider(...)` is one-per-process; a second concurrent `run()` would fail at stage 4. Fail-fast at ingress is cleaner. Cached-context model (which would support concurrency) is Track B.

**Risk surface — `WorkflowObject` shape.** F-P2-2 deferred operator-facing ingress to Track B, including the workflow-source format. Track A still needs to type the in-process object that CP's lifecycle loop accepts. CP spec does not currently expose a typed `WorkflowObject` contract. Three options at landing time (Class 1 surface):

1. CP spec extends to expose a `WorkflowObject` contract (likely path; routes via `phase-7-back-flow-routing` with a CP amendment).
2. `harness-core` introduces a thin `WorkflowObject` carrier type the runtime + CP both consume.
3. Runtime defines `WorkflowObject` locally as a structural protocol (duck-typed against CP lifecycle loop expectations).

The choice is made at U-RT-42 landing time, not now. The contract here is the *signature shape*; the typed argument's source is open.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-INVALID-WORKFLOW` (permanent) | `InvalidWorkflowError` | Pre-bootstrap rejection; no `HarnessContext` constructed |
| `RT-FAIL-BOOTSTRAP` (permanent) | Bootstrap failure (any stage) | Per C-RT-02 rollback; surface typed `BootstrapError` with `BootstrapStage` field |
| `RT-FAIL-CONCURRENT-RUN` (permanent) | Second concurrent `run()` invocation detected | Fail fast; existing in-flight run continues unaffected |
| (downstream) | Workflow-execution failures | Per CP lifecycle loop contracts; surfaced through `RunResult` |

**Deferred to implementation discretion.** Sync convenience wrapper (Track B); cached-context entry point (Track B); `WorkflowObject` typed source (per risk surface above); process-local lock implementation (suggest `asyncio.Lock` initialized at module import).

---

## §9 C-RT-09 — `RunResult` shape

**Contract surface.** Schema.

**PRD enablement.** Enables R-OD-* observability requirements (RunResult carries trace IDs + audit-ledger head for inspection).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (audit-ledger head exposure); ADR-F5 v1.1 §Decision (trace ID exposure).

**Fork-resolution provenance.** n/a (general runtime discipline).

**Specification content.**

`RunResult` is a Pydantic v2 `BaseModel` (frozen).

| Field | Type | Semantic |
|---|---|---|
| `status` | `Literal['completed', 'drained', 'failed']` | Terminal status of the workflow execution |
| `workflow_id` | `harness_core.identity.WorkflowID` | Identity of the executed workflow |
| `terminal_state` | `dict[str, Any]` | Workflow's terminal state object per CP lifecycle loop contract |
| `audit_ledger_head_hash` | `str` (hex) | Post-execution audit-ledger head hash for verification |
| `trace_ids` | `list[str]` | Root span trace IDs emitted by the workflow execution |
| `cost_attribution` | `CostAttribution` (OD type) | Aggregated 5-step cost-attribution rollup |
| `failure_cause` | `FailureCause | None` | None unless `status == 'failed'` |

**Invariants.**

- `model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)`.
- `status == 'failed'` implies `failure_cause is not None`.
- `status == 'drained'` indicates `drained_flag` was set during execution and CP loop responded at next lifecycle boundary.
- `audit_ledger_head_hash` always present; `terminal_state` may be `{}` for trivial workflows.
- **Version evolution (added at v1.1).** `RunResult` is part of the operator-facing API surface. Adding an *optional* field is a minor bump; adding a *required* field (i.e., one without a default) breaks consumers that construct `RunResult` from kwargs and is a major bump. Removing a field is always a major bump. Renaming is a major bump. Type-widening of an existing field is minor; type-narrowing is major.

**Failure-mode taxonomy.** `RunResult` is a return value, not an operation; it doesn't fail. Failure modes attach to the workflow execution that produces it (see C-RT-08, C-RT-14, CP lifecycle loop contracts).

**Deferred to implementation discretion.** Exact `FailureCause` enumeration (suggest mirror of CP `validator_fail_taxonomy` 5-class set + a 6th `BootstrapFailure` for pre-execution failures; alternatively reuse C-RT-14 runtime-local fail-class set).

---

## §10 C-RT-10 — Shutdown sequence contract

**Contract surface.** Surface contract.

**PRD enablement.** Enables every R-OD-* requirement that depends on flush-completion (audit ledger consistency, span visibility).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (ledger chain head consistency); ADR-F5 v1.1 §Decision (BSP flush before exit).

**Fork-resolution provenance.** n/a (general runtime discipline).

**Specification content.**

Shutdown executes in **reverse-stage order**: stages constructed last close first. The orchestrator's shutdown entry point is `async def shutdown(ctx: HarnessContext, *, timeout: float = 30.0) -> None`.

**Sequence:**

1. **Drain** (per C-RT-11): set `ctx.drained_flag`; refuse new ingress; allow in-flight workflow steps to complete or surface timeout.
2. **Flush observability state**: `await tracer_provider.force_flush(timeout_millis=...)`; sync ledger writers (`fsync` on `.harness/state.jsonl`); flush cost-attribution chain in-memory state to audit ledger.
3. **Close stage-5/4/3b/3a resources in reverse order:**
   - Stop lifecycle emitter (no-op; emitter holds no state).
   - Stop topology dispatcher / override evaluator (no-op).
   - Stop collector daemon (structured-stop per C-RT-07).
   - `await tracer_provider.shutdown()` — closes BSP + exporter.
   - Close audit writer (no-op; wraps IS writer which is below).
   - Close cost chain (no-op).
   - Close CP routing state (no-op; routing manifest is in-memory).
   - `await client.aclose()` for each provider in `ctx.providers` (per `ProviderClient` Protocol at C-RT-05).
4. **Close stage-2 resources:** disconnect MCP clients; close MCP host.
5. **Close stage-1 resources:** close IS ledger writer (final fsync); close index + cache; release worktree leases.
6. **Verify post-shutdown invariants:**
   - All provider clients closed (idempotent re-close is no-op per `ProviderClient.aclose()`).
   - Collector daemon process/thread terminated.
   - Audit-ledger chain head hash is consistent with last `audit_ledger_head_hash` returned by any `RunResult`.
   - No background task remaining on the asyncio event loop owned by the harness.

**Invariants.**

- Shutdown is idempotent: calling `shutdown(ctx)` twice is safe (second call is a no-op or surfaces a typed `AlreadyShutDown` warning).
- Total shutdown time bounded by `timeout` parameter; exceeding the bound surfaces typed `ShutdownTimeout` with a list of resources that failed to close.
- Resources that fail to close cleanly are surfaced individually; shutdown does not abort on first failure.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-PARTIAL-SHUTDOWN` (partial) | One resource fails to close cleanly | Shutdown completes; failed resources reported in `ShutdownReport` |
| `RT-FAIL-SHUTDOWN-TIMEOUT` (permanent) | Shutdown exceeds `timeout` | Surface `ShutdownTimeout`; process should exit regardless (force-kill upstream) |

**Deferred to implementation discretion.** Default `timeout` value (suggest 30.0s); `ShutdownReport` exposure (returned by `shutdown` or logged-only); whether stage-6 CXA wiring requires unwinding (it doesn't; module imports are not unwound).

---

## §11 C-RT-11 — Drain semantics (runtime-owned flag-polling)

**Contract surface.** Surface contract.

**PRD enablement.** Enables graceful R-OD-* audit-ledger consistency on shutdown.

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (lifecycle boundaries are the natural drain checkpoints).

**Fork-resolution provenance.** n/a (general runtime discipline); resolves the F2-05 adversarial-review finding from `.harness/Adversarial_Review_phase_2_session_3_track_a_plan.md` (drain ownership ambiguity).

**Specification content.**

CP spec does not currently expose a native drain primitive. Track A specifies drain at the runtime layer using a flag-polling pattern:

- `HarnessContext.drained_flag: asyncio.Event` is initialized at stage 0 and shared across all bootstrap stages.
- A signal handler (installed at stage 7 on the orchestrator's behalf, listening for `SIGTERM` / `SIGINT`) sets the flag.
- The CP workflow lifecycle loop polls `ctx.drained_flag.is_set()` at each lifecycle boundary (per-step entry, per-step exit, per-topology-dispatch entry). On detecting the flag, the loop:
  1. Completes the current in-flight step (no mid-step interruption).
  2. Returns a `RunResult` with `status='drained'` and the partial terminal state.

  *(v1.2 amendment, 2026-05-20):* an earlier draft committed step 2 to emit a `WorkflowEventClass.DRAINED` event. The canonical `harness_core.workflow_event_class` enum is closed at 8 per C-CP-05 §5.1 with no `DRAINED` value; alignment failed at U-RT-41 landing per spec §16 open question #9. The emit step is STRUCK from C-RT-11. Drain observability survives without it via the two remaining surfaces above: `ctx.drained_flag` (asyncio.Event signal-level observability) + `RunResult.status='drained'` (terminal-return observability). This resolves `[[fork-drained-event-class]]` Path B.
- After flag-set, `harness_runtime.run(...)` rejects new invocations with typed `HarnessDraining` error.

**Invariants.**

- The flag is one-way: once set, it stays set for the remaining process lifetime. A new harness invocation requires process restart.
- Drain bounded-wait timeout (per `shutdown(ctx, timeout=...)` parameter) bounds how long shutdown waits at step 1 of C-RT-10. Exceeding the bound forces shutdown to proceed regardless; in-flight step may be in inconsistent state (CP lifecycle is responsible for transactional discipline if it claims it).
- The flag does NOT propagate into sub-agent or sub-workflow boundaries that run outside the harness process (e.g., a long MCP tool call). Those continue to completion; the harness drain waits or times out.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-DRAIN-TIMEOUT` (transient) | Drain times out before in-flight step completes | Shutdown proceeds; `RunResult.status == 'drained'`; downstream observability reflects partial-completion |

**Risk surface.** If CP later surfaces a native drain primitive (e.g., a CP-level `WorkflowDrainController` type), refactor `harness-runtime/` to delegate drain to CP. This contract becomes a thin adapter. Until then, drain ownership is runtime-axis-local.

**Deferred to implementation discretion.** Signal-handler installation site (suggest at stage 7 INGRESS_ACCEPT); whether to expose a Python API for programmatic drain in addition to signal-handler (suggest yes: `ctx.drained_flag.set()` is the API); behavior under repeated `SIGTERM` (suggest second signal escalates to immediate-stop bypassing drain).

---

## §12 C-RT-12 — CXA wiring obligations

**Contract surface.** Surface contract + per-bucket wiring contracts.

**PRD enablement.** Enables every cross-axis observable behavior that depends on runtime wiring (CP-emitted audit entries reaching IS ledger chain; OD-emitted breaker spans reaching CP namespace ingestion; etc.).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (CP→IS ledger composition); ADR-F5 v1.1 §Decision (OD→CP namespace ingestion).

**Fork-resolution provenance.** D-P2-2 ratified 2026-05-19 (24 phase-2-runtime CXA edges in scope for Track A).

**Specification content.**

The runtime is responsible for two distinct CXA categories at stage 6:

### §12.1 Terminal aggregate exporter manifest import (side-effect)

The composition root imports the 5 terminal aggregate exporter manifests so their import-time side-effects realize. Per CXA v2.3 §3, the 22 genuine Pattern P1 typed seams are realized at module-import time; the composition root's import of the consumer modules is what causes them to load and bind their producer references.

| Manifest | Module |
|---|---|
| IS substrate seam exports | `harness_is.substrate_seam_exports` (per IS C-IS-10 §10) |
| AS substrate seam exports | `harness_as.as_substrate_seam_exports` (per AS C-AS-16 §16) |
| CP namespace export manifest | `harness_cp.cp_namespace_export_manifest` (per CP C-CP-24) |
| CP cross-axis composition manifest | `harness_cp.cp_cross_axis_composition_manifest` (per CP C-CP-24) |
| OD substrate seam exports aggregate | `harness_od.substrate_seam_exports_aggregate_manifest` (per OD spec; specific §-pin verified at U-RT-33 landing) |

Verification (separate from wiring): for each of the 22 typed seams, the runtime emits a Pattern P1 identity-equality assertion (`consumer_module.SYMBOL is producer_module.SYMBOL`). Verification lives in tests, not in runtime code. (See plan v2 U-RT-51.)

### §12.2 Phase-2-runtime edges: AS → IS (1 edge)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-AS-27 → U-IS-11 | AS skill-load completion site (skill-discovery emission) | IS ledger append via `ctx.ledger_writer.append(entry)` | `StateLedgerEntry` (per C-IS-05 §5) carrying skill-load metadata | Skill-load event appears in `.harness/state.jsonl` with chain integrity intact (verifiable via C-IS-06 §6) |

Wiring contract: at stage 6, the runtime hands `ctx.ledger_writer.append` to the AS skill-load completion site via callback registration. Plan v2 U-RT-34.

### §12.3 Phase-2-runtime edges: CP → IS (17 edges)

Source units: U-CP-12, U-CP-14, U-CP-27, U-CP-30, U-CP-34, U-CP-37, U-CP-49, U-CP-50, U-CP-52. Target units: U-IS-07, U-IS-08, U-IS-09, U-IS-11. (Note: target-unit IDs reference plan-level units; the *contract* target is C-IS-05 §5 entry shape + C-IS-07 §7 read/write contract pair.)

All 17 edges are ledger-emission patterns. The wiring contract is uniform:

| Wiring contract | Per-edge instance |
|---|---|
| Callable signature | `Callable[[StateLedgerEntry], EntryHash]` |
| Payload type | `StateLedgerEntry` (C-IS-05 §5 6-field shape) |
| Post-wiring invariant | At each enumerated CP source unit's emission site, the spec'd IS ledger entry is appended; `chain_verification` (C-IS-06 §6) passes post-emission |

Wiring contract per-edge: at stage 6, the runtime hands `ctx.ledger_writer.append` to each of the 9 CP source units via callback registration (the 17 edges aggregate across the 9 source units; some source units emit multiple entry variants). Plan v2 U-RT-35 (split-allowed per the plan if signature divergence surfaces at any source unit).

### §12.4 Phase-2-runtime edges: OD → IS (2 edges)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-OD-30 → U-IS-11 | OD audit-emission site | IS ledger append via `ctx.audit_writer.append(tenant_id, audit_entry)` | `AuditLedgerEntry` (OD-spec'd; specific §-pin verified at U-RT-32 landing) wrapping into `StateLedgerEntry` | OD audit entry reaches IS chain; `chain_verification` passes |
| U-OD-34 → U-IS-17 | OD terminal-exporter manifest declaration | IS terminal-exporter manifest string reference resolution | Manifest string reference (not a value) | Manifest string ID resolves at composition; downstream import-time consumers see consistent string |

Plan v2 U-RT-36.

### §12.5 Phase-2-runtime edges: OD → AS (1 edge)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-OD-34 → U-AS-33 | OD terminal-exporter manifest declaration (AS namespace verification target) | AS namespace exports surface (per C-AS-16 §16) | Manifest string reference | AS namespace verification runs at bootstrap; mismatch surfaces typed |

Plan v2 U-RT-37.

### §12.6 Phase-2-runtime edges: OD → CP (3 edges, inversion/manifest)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-OD-09 → U-CP-54 | OD `harness.breaker.*` namespace export (F-CP-01 Stage 3b inversion) | CP namespace ingestion at composition | Namespace declaration (typed; per CP C-CP-09 §9 `engine.*` pattern, applied to `harness.breaker.*`) | CP ingestion of `harness.breaker.*` observable |
| U-OD-34 → U-CP-54 | OD terminal-exporter manifest declaration (CP namespace target) | CP namespace export manifest (per C-CP-24) | Manifest string reference | Manifest reference resolves |
| U-OD-34 → U-CP-55 | OD terminal-exporter manifest declaration (CP carry-forward target — F2-12 inheritance) | CP cross-axis composition manifest (per C-CP-24) | Manifest string reference (F2-12 carry-forward) | Manifest reference resolves; dashboard bindings observable |

Plan v2 U-RT-38.

**Invariants (across §12.1–§12.6).**

- The 5 manifest imports (§12.1) occur before any of the 24 edges wire; manifest imports are a precondition.
- Pattern P1 identity-equality holds for all 22 typed seams (verified at L11 tests; runtime code asserts this only in debug builds — see C-RT-12 deferred clause).
- Each of the 24 phase-2-runtime edges is exercised by at least one integration test (per plan v2 U-RT-34..U-RT-38 acceptance criteria).
- Edge wiring failures surface at stage 6 as typed errors naming the (source-unit, target-unit) pair.

**Deferred to implementation discretion.** Whether `cxa_phase2_runtime_edges.py` is a single module or split per-bucket (suggest single module with per-bucket section structure for readability); whether Pattern P1 verification runs in debug builds (suggest yes via env var `HARNESS_VERIFY_P1=1`); edge wiring callable signature beyond the per-bucket tables above (e.g., for §12.3 the registration mechanism — callback vs decorator vs explicit table — is implementation-discretion).

---

## §13 C-RT-13 — Admin stub semantics

**Contract surface.** Surface contract.

**PRD enablement.** Enables operator-facing inspection and shutdown of a running harness (Track A minimum; richer admin UX is Track B).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (state-ledger read-only inspection); ADR-F5 v1.1 §Decision (collector sqlite read-only inspection).

**Fork-resolution provenance.** F-P2-2 (admin stubs are the Track-A-allowed CLI surface; operator-facing `run` is Track B).

**Specification content.**

The runtime exposes two admin CLI stubs via `[project.scripts]` in `pyproject.toml`:

**`harness-inspect` (read-only).**

- Opens state ledger (`.harness/state.jsonl`) and collector sqlite (path resolved via PATH_CLASS_REGISTRY per C-IS-01 §1) in **read-only mode**. No writes.
- Dumps a summary: ledger head hash + last N entries (N from CLI flag, default 10); last N spans from collector (default 10); current cost-attribution rollup if available.
- Runs against a **stopped harness** (does not require a running process); does not modify any state.
- Exits 0 on success; nonzero on file-not-found or read-error.

**`harness-shutdown` (signal-running-instance).**

- Reads pidfile (location resolved via PATH_CLASS_REGISTRY; suggest `.harness/runtime.pid`).
- Sends `SIGTERM` to the pid.
- Optionally waits for process exit with `--wait <seconds>` (default: no wait).
- Exits 0 on signal delivery success; nonzero on pidfile-missing or signal-delivery error.
- The receiving harness instance's signal handler is responsible for the actual drain → shutdown sequence (per C-RT-10 + C-RT-11).

**Pidfile lifecycle.** The harness writes its pidfile at stage 7 INGRESS_ACCEPT and removes it at the end of `shutdown()`. Pidfile contents are the pid only. Stale pidfiles (process not running) surface as `harness-shutdown` typed error.

**Invariants.**

- `harness-inspect` MUST NOT write to any file. Tested by chmod-readonly fixture.
- `harness-shutdown` MUST NOT touch state ledger / collector sqlite / configuration files. It only reads pidfile and emits a signal.
- Richer admin IPC (e.g., a unix socket protocol for query / drain / status) is explicitly Track B.

**Failure-mode taxonomy.** Per C-RT-14:

| Command | Fail class | Trigger |
|---|---|---|
| `harness-inspect` | `RT-FAIL-INSPECT-PATH` (permanent) | Ledger / sqlite path missing or unreadable |
| `harness-shutdown` | `RT-FAIL-ADMIN-PIDFILE` (permanent) | Pidfile missing; pid not running; signal delivery denied |

**Deferred to implementation discretion.** CLI argument parsing library (suggest `argparse` stdlib; no `click` / `typer` per framework-pull discipline at this layer); output format (suggest human-readable default + `--json` flag); pidfile location (default `.harness/runtime.pid`; configurable via `RuntimeConfig`).

---

## §14 C-RT-14 — Runtime-local fail-class taxonomy (new at v1.1; Reading 1 absorption of F2-01)

**Contract surface.** Enum + relationship contract.

**PRD enablement.** Enables every R-IS/AS/CP/OD-* requirement that needs typed failure surfaces at the runtime boundary.

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (workflow lifecycle includes failure surfaces); ADR-F5 v1.1 §Decision (failures emit observability events).

**Fork-resolution provenance.** Adversarial-review finding F2-01 at P2-S4-CK 2026-05-19, resolved Reading 1 by operator: runtime axis owns runtime-local fail classes orthogonal to CP's `validator_fail_taxonomy`.

**Specification content.**

The runtime axis introduces a fail-class enumeration distinct from CP's workflow-step-level `validator_fail_taxonomy` (5-class set at landed `harness_cp.validator_fail_taxonomy`). The two are orthogonal: CP's taxonomy covers *workflow-step* failures (validator-fail, transient, permanent at the step boundary); the runtime taxonomy covers *bootstrap-stage* and *runtime-lifecycle* failures (config, secret, provider, collector, bootstrap, shutdown).

**Runtime-local fail-class enumeration:**

| Fail class | Severity | Surface | Recovery |
|---|---|---|---|
| `RT-FAIL-CONFIG` | permanent | Stage 0 PREAMBLE | None; operator fixes config |
| `RT-FAIL-CONFIG-VERSION` | permanent | Stage 0 PREAMBLE | None; operator migrates config |
| `RT-FAIL-SECRET-MISSING` | permanent | Stage 0 (validation) or stage 3a (resolution) | None; operator adds secret to keyring |
| `RT-FAIL-TRANSIENT` | transient | Any stage (stage-internal bounded retry) | Bounded retry; escalates if persistent |
| `RT-FAIL-PROVIDER-AUTH` | permanent | Stage 3a CP_CLIENTS | None; operator fixes provider credentials |
| `RT-FAIL-PROVIDER-UNREACHABLE` | permanent | Stage 3a CP_CLIENTS (after RT-FAIL-TRANSIENT escalation) | None; operator fixes network/provider availability |
| `RT-FAIL-PROVIDER-DEGRADED` | degraded | Stage 3a CP_CLIENTS (Ollama-optional path) | Continue with reduced provider set |
| `RT-FAIL-COLLECTOR-PATH` | permanent | Stage 4 OD | None; operator fixes path permissions |
| `RT-FAIL-COLLECTOR-DEGRADED` | degraded | Stage 4 OD or runtime | Bounded restart; observability survives |
| `RT-FAIL-HARNESS-DEGRADED` | degraded (ongoing) | Runtime | Continue in degraded mode; downstream observability reflects |
| `RT-FAIL-BOOTSTRAP` | permanent | Any stage failing the bootstrap orchestrator | Reverse-order rollback per C-RT-02; surface to caller |
| `RT-FAIL-PARTIAL-ROLLBACK-REQUIRED` | partial | Stage N+1 fails after stage N completes | Reverse-order shutdown for stages 0..N |
| `RT-FAIL-INVALID-WORKFLOW` | permanent | `run()` pre-bootstrap input validation | None; caller passes wrong type |
| `RT-FAIL-CONCURRENT-RUN` | permanent | `run()` ingress concurrency lock | None; caller serializes or uses cached-context (Track B) |
| `RT-FAIL-CONCURRENT-REGISTRATION` | permanent | `set_tracer_provider` double-call | None; indicator of orchestrator bug |
| `RT-FAIL-DRAIN-TIMEOUT` | transient | C-RT-11 drain wait | Shutdown proceeds; partial-completion observable |
| `RT-FAIL-PARTIAL-SHUTDOWN` | partial | C-RT-10 shutdown | Surface in `ShutdownReport` |
| `RT-FAIL-SHUTDOWN-TIMEOUT` | permanent | C-RT-10 shutdown wait | Process force-exit upstream |
| `RT-FAIL-INSPECT-PATH` | permanent | `harness-inspect` admin stub | None; operator fixes path |
| `RT-FAIL-ADMIN-PIDFILE` | permanent | `harness-shutdown` admin stub | None; operator verifies running harness |

**Relationship to CP `validator_fail_taxonomy`:**

| Dimension | Runtime taxonomy (this spec) | CP `validator_fail_taxonomy` |
|---|---|---|
| Scope | Bootstrap-stage + runtime-lifecycle failures | Workflow-step-level validator failures inside CP loop |
| Lifetime | Process-startup, ingress, shutdown | Per-step within an executing workflow |
| Cause attribution | Stage / lifecycle phase / resource | Validator category per C-CP-05 §5 |
| Recovery | Per row above | Per CP `validator_fail_transient_staircase` |
| Audit-ledger emission | RT failures emit via C-RT-04 `audit_writer` at C-RT-14 emission site | CP validator failures emit per CP audit-emission contract |

The two taxonomies are **orthogonal and composable**: a workflow execution that completes bootstrap successfully but then has a validator failure within CP emits a CP `validator_fail_taxonomy` value via CP's emission site; a workflow that fails *before* CP loop starts (e.g., bootstrap failure) emits an `RT-FAIL-*` value via the runtime's emission site. No fail-class is in both taxonomies; cause-attribution disambiguates.

**Invariants.**

- Each `RT-FAIL-*` value is a Python `str` enum member at `harness_runtime.fail_classes.RuntimeFailClass`.
- Every failure surfaced by the runtime carries exactly one `RuntimeFailClass` value (no plural; no untagged failures).
- Every `RT-FAIL-*` permanent / partial value emits an audit-ledger entry via `ctx.audit_writer` (C-RT-04) before propagating; transient failures emit at escalation only.
- Severity column above is normative: permanent / transient / degraded / partial / ongoing-degraded.

**Failure-mode taxonomy.** N/A — this contract *is* the failure-mode taxonomy.

**Deferred to implementation discretion.** Exact enum class name (suggest `RuntimeFailClass`); whether `RT-FAIL-*` string values are stable across versions (recommended: stable, since they appear in audit ledger and operator-facing logs); cause-attribution payload shape attached to each failure surface (suggest a Pydantic `RuntimeFailureCause` model per row).

---

## §15 Spec-to-plan traceability

Each Track A plan v2 unit cites at least one contract in this spec. Coverage matrix:

| Plan unit | Spec contract(s) | Notes |
|---|---|---|
| U-RT-00 | (this spec entirely — U-RT-00 IS the spec authoring unit) | Hard gate |
| U-RT-01 | C-RT-02 §1 layout | Package scaffold matches stage-file naming |
| U-RT-02 | C-RT-03, C-RT-04 | Types are direct implementations of the schemas |
| U-RT-03 | C-RT-01 | Enum is direct implementation |
| U-RT-04..U-RT-08 | C-RT-03 sub-models | Config sub-models |
| U-RT-09..U-RT-12 | C-RT-02 stage 1 invariants | IS bootstrap stage |
| U-RT-13..U-RT-16 | C-RT-02 stage 2 invariants | AS bootstrap stage |
| U-RT-17..U-RT-20 | C-RT-05 (incl. `ProviderClient` Protocol), C-RT-02 stage 3a invariants | Provider SDK lifecycle |
| U-RT-21..U-RT-26 | C-RT-02 stage 3b invariants | CP routing wiring |
| U-RT-27..U-RT-32 | C-RT-06, C-RT-07, C-RT-02 stage 4 invariants | OD observability runtime |
| U-RT-33 | C-RT-12 §12.1 | Terminal aggregate exporter manifest import |
| U-RT-34 | C-RT-12 §12.2 | AS → IS edge |
| U-RT-35 | C-RT-12 §12.3 | CP → IS 17 edges |
| U-RT-36 | C-RT-12 §12.4 | OD → IS 2 edges |
| U-RT-37 | C-RT-12 §12.5 | OD → AS 1 edge |
| U-RT-38 | C-RT-12 §12.6 | OD → CP 3 edges |
| U-RT-39..U-RT-41 | C-RT-02 stage 5 invariants | Loop activation |
| U-RT-42 | C-RT-08 (incl. v1.1 idempotency invariant), C-RT-09 | Python API + result shape |
| U-RT-43 | C-RT-02 | Bootstrap orchestrator |
| U-RT-44 | C-RT-11 | Drain semantics |
| U-RT-45..U-RT-46 | C-RT-10 | Shutdown sequence |
| U-RT-47..U-RT-48 | C-RT-13 | Admin stubs |
| U-RT-49..U-RT-51 | C-RT-02 + C-RT-12 verification | E2E + Pattern P1 verification |
| (cross-cutting) | C-RT-14 | Every U-RT-NN that surfaces a failure emits via the runtime-local fail-class taxonomy |

Every U-RT-NN unit traces to ≥1 spec contract. ✓

---

## §16 Open questions and known risk surfaces (carry into review)

These are explicit open questions surfaced at authoring time. Each must either be resolved at P2-S4-CK adversarial review or carried as a candidate Class 1 fork at unit-landing time.

1. **Trace-discipline adaptation acceptable?** Front-matter §"Trace-discipline novelty" substitutes `PRD enablement` for `PRD requirement(s) satisfied` and `Fork-resolution provenance` for `Persona linkage`. **Cleared at P2-S4-CK 2026-05-19 (v1 review).** Carries forward as a candidate Class 1 fork for any future aggregate review; back-flow shape sketched in front-matter.
2. **`WorkflowObject` shape source.** C-RT-08 risk note enumerates three options. The decision lands at U-RT-42 implementation, not here. P2-S4-CK should pressure-test whether the spec should pin it now. (v1.1: carried — still open.)
3. **Collector daemon supervision contract in OD spec vs Runtime spec.** C-RT-07 specifies supervision here. P2-S4-CK should verify whether this contract belongs in OD spec instead (OD C-OD-20 §20.1 currently covers placement matrix but not supervision semantics). (v1.1: carried — still open.)
4. **Async-only `run()` posture (decided).** C-RT-08 has pinned async-only as a normative invariant at Track A (no sync wrapper). **Open for re-evaluation:** does any anticipated Track A integration scenario require a sync surface? (v1.1: reworded from over-open phrasing per F1-02.)
5. **Pidfile location and CLI naming.** C-RT-13 picks `.harness/runtime.pid` and `harness-inspect` / `harness-shutdown` command names. P2-S4-CK should verify these don't collide with prior workspace conventions. (v1.1: carried — still open.)
6. **Tenant identity scope.** C-RT-03 includes optional `tenant_id`; C-RT-04 routes it through audit writer. P2-S4-CK should verify the routing is complete (does cost attribution also need per-tenant scoping?). (v1.1: carried — still open.)
7. **Bootstrap-per-call vs cached context.** C-RT-08 specifies bootstrap-per-call for Track A. P2-S4-CK should verify this is acceptable for any anticipated Track A integration test scenarios (cached-context optimization is Track B). v1.1 added the concurrency invariant (`RT-FAIL-CONCURRENT-RUN`) which makes the bootstrap-per-call discipline enforceable, partially closing this. (v1.1: partially closed; carry forward the cached-context-Track-B side.)
8. **(v1.1 new) OD cost-attribution + audit-ledger §-pins.** Cross-axis citation substrate cites these as "specific §-pin verified at U-RT-31 / U-RT-32 landing." If verification at landing surfaces that the contracts don't exist (i.e., OD spec doesn't formally specify cost-chain or audit-writer), surface as Class 1 fork.
9. **(v1.1 new) `WorkflowEventClass.DRAINED` event-name landed-axis alignment.** C-RT-11 introduces a `DRAINED` event; per Workflow §2.5.2 Pattern P1-PHASE-5 discipline, event-name verb forms must align across axis specs. If landed `harness_core.workflow_event_class` enum doesn't carry `DRAINED`, U-RT-41 lands an aligned name. Surface as Class 1 fork at U-RT-41 landing if alignment fails.

---

## §17 Coherence pass — self-audit at v1.1 filing

| Dimension | Check | Result |
|---|---|---|
| Front-matter completeness | Change-note, Status block, source-set, ADR scope, cross-axis citation substrate, scope table all present | ✅ PASS |
| Trace adaptation explicit | §"Trace-discipline novelty" called out before first contract; back-flow shape sketched at v1.1 | ✅ PASS |
| Per-contract structure | Every C-RT-NN (1..14) has: Contract surface · PRD enablement · ADR commitment · Fork-resolution provenance · Specification content · Invariants · Failure-mode taxonomy (where applicable) · Deferred to implementation discretion | ✅ PASS |
| ADR citations canonicalized (v1.1) | Every ADR cite includes version + canonical §-section (`§Decision` / `§Consequences` / `§N.M` for D-ADRs) verified against source ADR files | ✅ PASS |
| Cross-axis citations corrected (v1.1) | C-IS-01..10, C-AS-01..16, C-CP-01..24, C-OD-01..23 contract IDs verified against source spec enumerations; §-pins included where verified; partial-precision items explicitly flagged | ✅ PASS (with §-pin verification deferred to U-RT-31/32 landing per cross-axis substrate note) |
| Plan trace completeness | §15 covers all 50 U-RT-NN units; C-RT-12 sub-subsections map 1:1 with U-RT-33..U-RT-38 | ✅ PASS |
| Open-questions explicit | §16 enumerates 9 candidate Class 1 fork surfaces; #1 cleared with carry-forward; #4 reworded per F1-02; #7 partially closed by v1.1 concurrency invariant | ✅ PASS |
| Failure modes per operational contract | C-RT-02, 03, 05, 06, 07, 08, 10, 11, 13 each have failure-mode taxonomy; all reference runtime-local fail classes at C-RT-14 | ✅ PASS |
| Schema vs prose discipline | Tables for matrices, Pydantic-style prose for schemas, no mixing within a contract | ✅ PASS |
| Schema version-evolution (v1.1) | C-RT-03, C-RT-04, C-RT-09 each carry Version evolution invariant | ✅ PASS |
| No restated ADR/PRD content | Contracts derive but do not restate | ✅ PASS |
| Deferred-to-implementation explicit | Every operational contract has explicit deferred list | ✅ PASS |
| Scope boundary clean | §"Scope and out-of-scope" table separates Track A from Track B / future; row added at v1.1 for runtime-local fail-class taxonomy (orthogonal to CP) | ✅ PASS |
| Fail-class taxonomy orthogonality (v1.1) | C-RT-14 enumerates runtime-local taxonomy with explicit orthogonality table against CP `validator_fail_taxonomy` | ✅ PASS |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Harness_Runtime_v1.md` |
| Status | Proposed (v1.1) — Phase 2 Session 4 runtime-spec authoring + adversarial-review absorption |
| Predecessor | v1 (2026-05-19 initial authoring) |
| Substrate consumed | F-P2-1..F-P2-5 fork resolution records; `.harness/phase-2-session-1-framing.md`; `.harness/phase-2-session-2-track-a-strawman.md`; `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2; `.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md`; ADR-F1..F5; ADR-D1, D2, D6; ADD v1.3; `Cross_Axis_Composition_Document_v2_3.md` §2.3, §3; landed code across `harness-{core,is,as,cp,od,cxa}/`; per-axis spec contract enumerations verified at v1.1 |
| Successor | `harness-runtime/` package landing per Track A plan v2 (Session 5 onward); per-axis spec amendments triggered by U-RT-NN unit landings that surface gaps (per `Project_Workflow_v1_8.md` §2.7.6 back-flow); plan v2 minor revision to add C-RT-14 row in §14 traceability |
| Revision policy | In-CLI per workspace `CLAUDE.md` §4.3 (design-substrate/ canonical; back-flow deprecated 2026-05-15) |
| Adversarial review | v1: P2-S4-CK 2026-05-19 (`.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md`) — 0 Class 3 / 7 Class 2 / 3 Class 1; revision pass produces v1.1. v1.1: P2-S4-CK second pass pending operator request. |
| Date | 2026-05-19 (v1.1) |
