# Phase 2 — Class 1 Forks F-P2-3 / F-P2-4 / F-P2-5: Runtime Lifecycle Ownership

**Status:** ✅ **RESOLVED 2026-05-19** — operator ratification, batched.
**Source:** Phase 2 Session 2 Track A strawman, `phase-2-session-2-track-a-strawman.md` §6.
**Type:** Lifecycle-ownership pins; assigns three runtime concerns to `harness-runtime/`.
**Predecessor:** F-P2-1 (`phase_2_fork_F-P2-1_runtime_package_placement.md`) — placed `harness-runtime/`; this resolution assigns its responsibilities.

---

## Shared defect pattern

All three forks share an identical structure verified against landed code at commit `4b2a80b`:

| Surface | Axis-landed contract | Missing lifecycle |
|---|---|---|
| OTel tracer provider | OD 12-namespace OTel schema + `BatchSpanProcessor` window/size constants + U-OD-23 `get_tracer_provider()` consumption | Nobody calls `set_tracer_provider(...)` |
| Provider SDK clients | CP `provider_capabilities.py` capability-aware abstraction; ADR-F1 v1.2 per-provider-SDK commitment | Nobody constructs `anthropic.Anthropic(...)`, `openai.OpenAI(...)`, `ollama.Client(...)` |
| In-process OTLP collector | OD `local_first_otlp_collector.py`, `per_cell_collector_placement_matrix.py`, `per_sandbox_tier_otlp_reachability.py` — landed as library (schemas + constants) | No daemon, no live collector process, no sqlite ring-buffer rotation, no TUI, no no-network-egress enforcement |

The pattern: **the axis owns the contract surface (schemas, enums, abstractions) — landed; the lifecycle (construct, configure, start, drain, close) is unspecified and unlanded.** That is the runtime gap, instanced three times.

---

## Resolution

For all three: **`harness-runtime/` owns the lifecycle**. Existing axis specs remain authoritative for contracts.

### F-P2-3 — Tracer provider initialization site

- **Owner:** `harness-runtime/`
- **Bootstrap stage:** 4 (OTel + cost attribution per the runtime-gap order)
- **Responsibilities:** construct the OTel SDK `TracerProvider`; configure the OTLP exporter against the runtime config; call `set_tracer_provider(...)` before any axis primitive emits a span; drain + shutdown on graceful close.
- **Contract authority remains:** OD spec — `Spec_Operational_Discipline_v1_4.md` (12-namespace attribute schema, `BatchSpanProcessor` constants).

### F-P2-4 — Provider SDK lifecycle ownership

- **Owner:** `harness-runtime/`
- **Bootstrap stage:** 3 (routing core + engine selection)
- **Responsibilities:** construct `anthropic.Anthropic(...)`, `openai.OpenAI(...)`, `ollama.Client(...)` from runtime config (API keys via `keyring` per ADR-F5 v1.1); hand to CP's routing core via dependency injection; close clients on graceful shutdown.
- **Contract authority remains:** CP spec — `Spec_Control_Plane_v1_3.md` C-CP-01 (capability-aware multi-LLM provider abstraction); ADR-F1 v1.2 (per-provider-SDK commitment).

### F-P2-5 — In-process OTLP collector daemon start

- **Owner:** `harness-runtime/`
- **Bootstrap stage:** 4 (alongside tracer provider)
- **Responsibilities:** start the in-process OTLP collector daemon; manage the ring-buffer + sqlite rotation; enforce no-network-egress per OD spec; drain + shutdown on graceful close. TUI lifecycle is operator-surface — likely Track B's domain.
- **Contract authority remains:** OD spec — `Spec_Operational_Discipline_v1_4.md` §20.1 collector placement matrix, §20.2 BatchSpanProcessor async emission discipline.

---

## What this resolves

| Question | Resolved |
|---|---|
| Who calls `set_tracer_provider(...)`? | `harness-runtime/` at bootstrap stage 4 |
| Who constructs the provider SDK clients (anthropic/openai/ollama)? | `harness-runtime/` at bootstrap stage 3 |
| Who starts the in-process OTLP collector daemon? | `harness-runtime/` at bootstrap stage 4 |
| Where are these recorded in the spec corpus? | Deferred — recorded either in a future `Spec_Harness_Runtime_v1.md` (likely emerging from Session 3 atomic-decomposition) or via small per-axis spec amendments. The ownership is pinned; the recording site is downstream. |

---

## What this does NOT resolve

- **The collector daemon's process model** (same-process asyncio task vs separate OS process) — Session 3+ implementation detail; may also touch Track B for TUI process-model considerations.
- **TUI lifecycle** — F-P2-5 ratified covers the *collector daemon*; the TUI trace browser is an operator-facing surface and likely belongs to Track B.
- **Exporter configuration source** — where does the harness read OTLP endpoint config from? CLI flag, config file, env var. Session 3 atomic-decomposition pins this; not a fork.
- **Provider SDK config source** — API keys via `keyring` per ADR-F5; but model/region/endpoint config sources need pinning at Session 3.
- **Spec recording site for these ownership pins** — see table above; deferred to either a new harness-runtime spec or per-axis amendments at Session 3 atomic-decomposition.

---

## Scope implications for Track A

This resolution **completes the lifecycle-owner pins** for the three load-bearing runtime surfaces. Combined with F-P2-1 (package placement) and F-P2-2 (Python-API ingress), Session 3 atomic-decomposition now has every prerequisite for the composition-root unit decomposition:

- Where the composition root lives: `harness-runtime/` (F-P2-1).
- What it accepts as input: a workflow object via Python API (F-P2-2).
- What it constructs and owns the lifecycle of: tracer provider, provider SDK clients, collector daemon (F-P2-3/4/5).
- What it does NOT own: contracts (axis specs remain authoritative); operator-facing ingress and TUI (Track B).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `phase_2_forks_F-P2-3_4_5_runtime_lifecycle_ownership.md` |
| Authority | Operator ratification at Phase 2 Session 2 close, 2026-05-19 |
| Predecessors | `phase-2-session-2-track-a-strawman.md` §6; F-P2-1 (package placement) |
| Successor | Session 3 atomic-decomposition consumes all three resolutions; the spec recording site (harness-runtime spec or per-axis amendments) is pinned at Session 3 |
