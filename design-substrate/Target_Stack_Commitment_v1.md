# Target Stack Commitment v1 — Phase 6.5 Session 1 (δ) Deliverable

*Canonical operator-decision artifact committing the target stack (language, ecosystem, tooling) the v2.3 implementation plans materialize against. Filed at Phase 6.5 Session 1 close. Governs Phase 7 execution at the new Claude Code CLI workspace.*

---

## §1 Status block

| Field | Value |
|---|---|
| Artifact | `Target_Stack_Commitment_v1.md` |
| Type | Operator decision artifact; target stack commitment record |
| Status | **Filed** — operator-committed at Phase 6.5 Session 1 close |
| Date | 2026-05-15 |
| Phase | Phase 6.5 (pre-transition arc) Session 1 (δ — Target Stack Commitment) |
| Authority | Operator directive 2026-05-14 (Phase 6.5 arc entry; full pre-transition rigor); `Phase_6_5_Session_1_Kickoff.md` §2 scope |
| Predecessor | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Phase 6 close); `Phase_6_5_Session_1_Kickoff.md` (this session's kickoff) |
| Successor (immediate) | `Phase_6_5_Session_1_Close_Handoff.md` (session close); `Phase_6_5_Session_2_Kickoff.md` (next-session prompt) |
| Successor (consumption) | Phase 6.5 Sessions 2 (α), 4 (η), 6 (ε), 7 (β) per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.4 |
| Workflow authority | `Project_Workflow_v1_7.md` §7 fidelity-grammar; Workflow v1.8 §6.5 (pending Session 5 authoring) |
| Filing destination | `/mnt/user-data/outputs/Target_Stack_Commitment_v1.md` → operator pushes to `/mnt/project/` |

---

## §2 Constraints enumeration

Twelve constraints govern stack selection, cited to a single source artifact + section each. Tightest binders identified at §2.2.

### §2.1 Constraint inventory

| ID | Constraint | Source | Stack-shape implication |
|---|---|---|---|
| C-STK-01 | **Multi-LLM provider integration as capability-aware abstraction** — thin core (generation, streaming, tool-use) + per-provider capability-introspection. First-class Anthropic feature surface (prompt caching at 0.1× cache-read cost, extended-thinking budgets, batch API, MCP host). First-class local-tier (Ollama / vLLM / llama.cpp). LCD-style abstraction (LiteLLM-class) explicitly rejected. | ADR-F1 v1.2 §Decision + §Rationale (b) | Ecosystem must have actively maintained native SDKs across hosted majors AND library coverage for local-tier servers. Provider-specific feature surfaces must be reachable without LCD flattening. [HIGH] |
| C-STK-02 | **Filesystem + git as canonical state substrate** with JSONL append-only state-ledger, hash-chained provenance via SHA-256, RFC 8785 JCS canonicalization baseline, and the Anthropic long-running-harness pattern (`init.sh` + `feature_list.json` + `claude-progress.txt`). Concurrent-write coordination via worktree-isolation. | ADR-F2 v1.2 §Decision + §Rationale (a.1) | Stack needs (a) git library binding, (b) JCS canonicalization library, (c) SHA-256 hashing (stdlib-acceptable), (d) JSONL/JSON serialization with stable ordering. No mandatory database engine. [HIGH] |
| C-STK-03 | **Durable-execution / stateless-reducer launch-pause-resume pattern** with per-workload-class engine selection. HITL interrupt/resume structurally identical to durable-execution checkpoint. Engine candidates substrate-TBD per workload class. | ADR-F3 v1.1 §Decision + §Context | Stack must permit a per-axis durable-execution shape composing against F2 substrate; pre-binding to a specific durable-execution library precluded by C-STK-12. Implies sufficient async/concurrency primitives. [HIGH] |
| C-STK-04 | **Four-tier sandbox isolation** (process / container / microVM / full-VM) with `max()`-composed per-tool tier assignment. Process-tier tech committed by host-OS-case. Docker-on-OCI as container-tier design-time default. | ADR-F4 v1.1 §Decision | Stack needs subprocess/spawn primitives with resource-limit hooks, git worktree library, Docker client binding, process-tier tech-per-host-OS-case reachable from chosen language. [HIGH] |
| C-STK-05 | **Tier-aware OS-keyring secret-fetch abstraction** — `fetch_secret(name, scope) -> SecretRef`; dev-tech committed at OS-keyring abstraction layer with specific library deferred to language-ecosystem D-ADR. Structure-not-content audit composition. | ADR-F5 v1.1 §Decision + §Consequences (c) | Language ecosystem must offer a mature OS-keyring binding (macOS Keychain / Linux Secret Service / Windows Credential Manager). Substrate enumerates `python-keyring`, `keytar`, `@napi-rs/keyring`, `zalando/go-keyring`. [HIGH] |
| C-STK-06 | **MCP client first-class across STDIO + HTTP transports** with MCP 2025-06-18 spec compliance. HTTP transport requires OAuth 2.1 + RFC 8707 + RFC 9728 + PKCE. STDIO carries zero protocol-level auth; sandbox is the only boundary. | ADR-D2 v1.1; Cluster 4 §2.3.3 [HIGH] | Language ecosystem needs production-grade MCP client SDK, OAuth 2.1 client library with PKCE + RFC 8707, STDIO process management. [HIGH] |
| C-STK-07 | **Reliability primitives — full-jitter retry, Stripe-style idempotency, per-{provider,model} circuit breakers**. Idempotency key construction: `sha256(conversation_id ‖ step_index ‖ tool ‖ canonical_args)`. Breakers durable across restarts. | ADR-D3 v1.2; Cluster 4 §2.2.7 [HIGH] | Stack needs primitives sufficient to implement the contract directly without framework lock-in (per C-STK-12). Async-context-aware retry composition is non-trivial; library availability matters. [HIGH] |
| C-STK-08 | **Schema validation library for contract enforcement** at validator gates with five-class fail taxonomy and staircase escalation. Validator outputs canonicalized for ledger-hashing. Signing-key resolution composes against F5. | ADR-D5 v1.3 §1.10 + §References | Ecosystem must have a production schema-validation library with JSON Schema or equivalent, typed parsing with structured failure modes, discrimination for the five fail-classes. Pydantic (Python), Zod (TS), serde + jsonschema (Rust) are canonical reference shapes. [HIGH] |
| C-STK-09 | **OTel GenAI semconv 1.41.0 with 12-namespace unified span schema** ingestion contract. Sensitive-data default-off + structure-not-content discipline. Provider-discriminator (`gen_ai.provider.name`) cross-namespace. Cost-attribution-per-span with replay-aware dedup. | ADR-D6 v1.2 §1.2 + §1.2.2 | Stack needs actively maintained OpenTelemetry SDK with GenAI semconv 1.41.0 surface, OTLP exporter (gRPC + HTTP), span-attribute APIs supporting the additive 12-namespace pattern. GenAI conventions currently at Development tier per OTel docs [HIGH — verified at `opentelemetry.io/docs/specs/semconv/gen-ai/` this session] — SDKs supporting them are language-uneven. |
| C-STK-10 | **Cross-platform host-OS support at design-time** — macOS, Linux, Windows. Each host-OS surfaces a distinct process-tier sandbox mechanism (per C-STK-04) and a distinct keychain primitive (per C-STK-05). | ADR-F4 v1.1 §Decision (host-OS-case mapping); ADR-F5 v1.1 §Context; Persona §5 | Stack must support all three host-OS targets without per-OS port forking. [HIGH] |
| C-STK-11 | **Persona ecosystem affinity — pragmatic-mixed**: Anthropic primitives preserved where they fit; vendor-neutral abstraction where they don't. Feature-erasure on abstraction unacceptable as design property. | Persona_Document_v1.md §7 | Implies ecosystem maturity asymmetry weighting: ecosystems with mature Anthropic + OpenAI + MCP SDKs are preferred. Substrate signal: production agent-harness convergence is Python-first or TypeScript-first. [MODERATE] |
| C-STK-12 | **Minimal-framework principle for foundational substrate** — AVOID LangGraph / Temporal / LangChain / similar as foundational. H_T's design must emerge from atomic-unit implementation per v2.3 plans, NOT be pre-empted by a framework. Libraries-as-primitives acceptable; frameworks-as-foundation precluded. | `Phase_6_5_Session_1_Kickoff.md` §2.1 item 12 | Stack selection prioritizes ecosystems where the relevant primitives compose without requiring a framework as glue. Filters out stack profiles whose ecosystem-idiomatic shape is framework-first. [HIGH] |

### §2.2 Tightest-binding constraints

Four constraints disproportionately narrow the candidate set:

- **C-STK-09 (OTel GenAI SDK maturity)** — GenAI semconv 1.41.0 is at Development tier in the OTel spec; SDKs ship GenAI attributes at uneven cadence. Python is the lead instrumentation language; TS is one revision behind on `@opentelemetry/instrumentation-openai`; Rust + Go lack production GenAI-specific contrib coverage.
- **C-STK-06 (MCP client maturity)** — Official SDKs exist for Python, TypeScript, Rust, Go, Java (Spring AI), C# (Microsoft), Kotlin (JetBrains), Ruby, Swift, PHP. Python and TypeScript are the most mature.
- **C-STK-05 (OS-keyring bindings)** — substrate names four bindings: `python-keyring`, `keytar` / `@napi-rs/keyring`, `zalando/go-keyring`. Rust has community options (`keyring-rs`) but is not in the F5-named set.
- **C-STK-12 (minimal-framework principle)** — disqualifies ecosystems whose idiomatic shape for agent-harness work is framework-first.

Combined, these reduce the practical candidate set to **Python**, **TypeScript / Node.js**, **Rust** (with **Go** as a probe candidate).

---

## §3 Stack candidate matrix

### §3.1 Candidate × evaluation-axis matrix

Per-cell entries: short justification + inline confidence tag. Rating glyphs (●●● strong / ●●○ solid / ●○○ workable / ○○○ blocked-or-deferred) are scannability aids.

| Axis | Python | TypeScript / Node | Rust | Go |
|---|---|---|---|---|
| A1: Anthropic SDK + Claude Agent SDK | ●●● Official Anthropic Python SDK + official Claude Agent SDK in Python. [HIGH — `platform.claude.com/docs/en/api/client-sdks`; `code.claude.com/docs/en/agent-sdk/overview`] | ●●● Official Anthropic TS SDK + official Claude Agent SDK in TS. TS Agent SDK bundles native Claude Code binary. [HIGH — same sources] | ●○○ No official Anthropic Rust SDK on the published list. [HIGH — Rust absent from official SDK page] | ●●○ Official Anthropic Go SDK exists. No official Claude Agent SDK in Go. [HIGH] |
| A2: Multi-provider SDK + local-tier (Ollama / vLLM / llama.cpp) | ●●● OpenAI Python SDK + Anthropic + Google GenAI + Ollama-python all canonical. vLLM is Python-native. llama.cpp has `llama-cpp-python`. [HIGH] | ●●○ OpenAI Node + Anthropic TS SDKs official. Ollama JS client exists. vLLM has no first-party JS SDK; HTTP-only. [MODERATE — local-tier coverage thinner than Python] | ●○○ Community-only Anthropic + OpenAI Rust SDKs. No canonical local-tier Rust client. HTTP-via-reqwest workable. [MODERATE — substantial bridging cost] | ●●○ Official Anthropic + OpenAI Go SDKs. Ollama Go bindings present. vLLM HTTP-only. [MODERATE] |
| A3: OTel GenAI semconv SDK status | ●●● Lead instrumentation language. `opentelemetry-python-contrib/instrumentation-genai` ships multiple libraries (OpenAI agents v2, Google GenAI, others). [HIGH — verified at `github.com/open-telemetry/opentelemetry-python-contrib`] | ●●○ `@opentelemetry/instrumentation-openai` implements semconv 1.36.0. [HIGH — verified at npm] | ●○○ OTel Rust SDK mature; GenAI-specific contrib effectively absent. [SPECULATIVE — substrate signal; not exhaustively verified] | ●○○ OTel Go SDK mature; GenAI contrib effectively absent. [SPECULATIVE] |
| A4: MCP SDK host + client | ●●● Official `modelcontextprotocol/python-sdk` (FastMCP server + client). Most mature among officials. [HIGH] | ●●● Official `modelcontextprotocol/typescript-sdk` runs on Node + Bun + Deno; v2 SDK with Standard Schema (Zod v4 / Valibot / ArkType). [HIGH] | ●●○ Official `modelcontextprotocol/rust-sdk` exists. Maturity less than Python/TS. [HIGH on existence; MODERATE on maturity] | ●●● Official `modelcontextprotocol/go-sdk` (Google-maintained). OAuth helper + extensions package. [HIGH] |
| A5: OS-keyring binding | ●●● `python-keyring` named in ADR-F5 substrate; mature; macOS / Linux / Windows. [HIGH] | ●●○ `keytar` (legacy) + `@napi-rs/keyring` (modern). Both named in F5. [HIGH] | ●●○ `keyring-rs` exists; NOT named in ADR-F5 substrate enumeration. [SPECULATIVE — F5-named set is Python/Node/Go only] | ●●● `zalando/go-keyring` named in ADR-F5. [HIGH] |
| A6: Schema validation | ●●● Pydantic v2 — canonical reference shape called out at C-STK-08; excellent for validator-gate construction. [HIGH] | ●●● Zod v4 — canonical reference shape; MCP TS SDK has peer-dep on Zod. [HIGH] | ●●○ `serde` + `jsonschema` — performance superior, ergonomic cost higher. [HIGH] | ●●○ Standard `encoding/json` + `go-playground/validator` or `gojsonschema`; less unified. [MODERATE] |
| A7: Async / concurrency for durable-execution + retry | ●●○ `asyncio` mature; structured concurrency via `anyio` / `asyncio.TaskGroup`. GIL-bound for CPU-bound work; agent-harness work is I/O-bound. [HIGH] | ●●○ Single-threaded event loop + worker threads. Excellent for I/O-bound async. [HIGH] | ●●● Tokio + Rust async/await is the strongest primitive set. [MODERATE — qualitative] | ●●● Goroutines + channels are arguably cleanest for stateless-reducer. [MODERATE] |
| A8: Cross-platform host-OS support | ●●● First-class on macOS / Linux / Windows. [HIGH] | ●●● Node first-class on all three. [HIGH] | ●●● Rust first-class on all three. [HIGH] | ●●● Go first-class on all three. [HIGH] |
| A9: Framework-density risk vs minimal-framework principle | ●○○ **Highest framework-pull risk.** Python agent-harness corpus is LangGraph / LangChain / LlamaIndex / CrewAI idiomatic at substantial corpus density. Discipline-dischargeable. [MODERATE — substrate Cluster 1 V2 + Pattern Reference Catalog] | ●●○ Moderate framework-pull. Mastra TS-native and growing; LangGraph.js less idiomatic than Python. [MODERATE] | ●●● Lowest framework-pull. Rust agent-harness corpus is small; libraries-as-primitives is idiomatic. [HIGH — by absence] | ●●● Low framework-pull. [HIGH — by absence] |
| A10: Developer ergonomics + iteration velocity | ●●● Pydantic + uv + pyright + ruff is the fastest design-iteration loop. [HIGH — qualitative corpus signal] | ●●○ Node + tsx / Bun + tsc + Zod fast iteration; type-system ergonomics weaker than Python+Pydantic on schema-heavy code. [MODERATE] | ●○○ Slowest iteration (compile cycles + borrow-checker). Excellent for production correctness. [HIGH] | ●●○ Faster compile cycles than Rust; less expressive type system than TS / Python. [MODERATE] |

### §3.2 Axis-asymmetric differentiators

Three axes carry disproportionate selection weight:

- **A1 (Anthropic + Agent SDK)** cleanly separates Python + TS from Rust (Go partial).
- **A3 (OTel GenAI SDK)** separates Python from the rest.
- **A9 (framework-density)** pulls opposite — Python carries highest framework-pull risk; Rust + Go lowest.

---

## §4 Tradeoff deliberation summary

Three tensions resolved during deliberation:

### §4.1 Tension 1 — C-STK-11 (ecosystem maturity) ↔ C-STK-12 (minimal-framework)

C-STK-12 is a foundational-substrate prohibition, not a transitive-dep prohibition. The Anthropic SDK, Pydantic, and MCP SDK are not frameworks in this sense (no inversion-of-control; no idiomatic execution loop the harness adopts as its own). Python's framework-pull risk is real but bounded — it lives at the foundational-substrate boundary where governance (Phase 6.5 Session 6 bootstrap substrate, CLAUDE.md design constraints, per-PR review against v2.3 atomic-unit decomposition) is reachable.

**Resolution:** C-STK-11 wins. Python's framework-pull risk is dischargeable by discipline. The discipline mechanism (Session 6 bootstrap substrate) is already in the arc plan. [HIGH] on resolution; [MODERATE] on discipline holding in practice — Session 6 deliverable to validate.

### §4.2 Tension 2 — SDK-maturity cluster vs primitives-purity cluster

Building H_T in Rust means writing or maintaining significant SDK-bridging infrastructure on top of HTTP for Anthropic, MCP host, OTel GenAI mappings, and Claude Agent SDK semantics. Each is doable in Rust; together they are weeks-to-months of bridging work [SPECULATIVE — not benchmarked].

**C9 (Reliability & Recovery) consultation:** The retry-with-full-jitter + per-`{provider, model}` circuit-breaker + idempotency-key contract C-STK-07 commits to is implementable in any of the four candidates without a framework. The async-primitives strength of Rust (Tokio) or Go (goroutines) is real but is not load-bearing for the C9 contract at the persona's tens-concurrent scale — Python's `asyncio` and Node's event loop are entirely sufficient. The C9 discipline does not push toward Rust; it pushes for the contract to be implementable and observable, which is true in all four candidates. [HIGH] on the C9 view per c9-reliability-recovery SKILL discipline.

**Resolution:** SDK-maturity cluster wins decisively. Primitives-purity gain in Rust / Go does not justify the SDK build-cost. [HIGH].

### §4.3 Tension 3 — TS vs Python at the Anthropic primitive surface

Both have official Anthropic SDK + official Claude Agent SDK + official MCP SDK. Two tiebreakers materialize:

**Tiebreaker 1 — Local-tier coverage (C-STK-01).** vLLM is Python-native; no first-party JS / TS SDK [HIGH — vLLM is a Python project]. `llama.cpp` canonical binding is `llama-cpp-python` [HIGH]. Local tier reachable from TS via HTTP, but ergonomic cost asymmetric across local-tier providers. Python is the language the local-tier corpus is written in.

**Tiebreaker 2 — OTel GenAI lag.** **C7 (Observability Architect) consultation:** The 12-namespace unified span schema ADR-D6 v1.2 commits to is implementable on top of OTel base SDK in any of the four candidates — the additive namespaces (`anthropic.*`, `mcp.*`, `skill.*`, `managed_agents.*`, `sandbox.*`, `hitl.*`, `harness.breaker.*`, `retry.*`, `secret.*`, `engine.*`, OTel base, cross-cutting attributes) are project-authored attribute schemas. The Python opentelemetry-python-contrib instrumentation-genai libraries reduce boilerplate for `gen_ai.*`; TS boilerplate higher but tractable; Rust / Go work back to manual span emission. Build-cost gradient: Python << TS << Rust ≈ Go. C7 weakly prefers Python on build-cost grounds; not load-bearing on correctness-of-observability. [HIGH] on the C7 view per c7-observability SKILL discipline.

**Resolution:** Python wins on both tiebreakers. TS would be the call if local-tier coverage were less central or if the Standard Schema ecosystem were judged decisive against Pydantic. Neither holds under the v2.3 plans' commitments. [HIGH].

---

## §5 Operator decision

### §5.1 Committed primary language

**Python 3.12+** as the primary language for H_T (the multi-LLM agent harness specified by ADRs + ADD v1.3 + specs + v2.3 plans).

Stated per the four-thing architectural-recommendation discipline:

- **The pattern:** Python 3.12+ with libraries-as-primitives composition. Per-axis monorepo with `uv` workspace members (`harness-is/`, `harness-as/`, `harness-cp/`, `harness-od/`, `harness-cxa/`, plus `harness-core/`) mirroring the v2.3 plan axes. Type-checked via `pyright` (strict), lint+format via `ruff`, tested via `pytest`. Schema validation via Pydantic v2. Multi-LLM via per-provider official SDKs (anthropic, openai, ollama) coordinated under the capability-aware abstraction ADR-F1 v1.2 commits to. OTel observability via `opentelemetry-api` + `opentelemetry-sdk` + `opentelemetry-exporter-otlp` + `opentelemetry-instrumentation-genai` contrib libraries selectively. Secrets via `python-keyring`. MCP host + client via `modelcontextprotocol/python-sdk` (FastMCP).
- **The problem it solves:** Materializing the v2.3 plans against an ecosystem where every named substrate library (per ADR References) has a production-grade Python implementation, while keeping build-cost trajectory tractable for solo-operator-with-LLM execution at Phase 7.
- **The failure mode it prevents:** Bridging-cost overrun. Rust or Go means writing SDK-equivalent infrastructure for Anthropic + MCP host + OTel GenAI mappings + Claude Agent SDK semantics before v2.3 atomic units can be executed.
- **The conditions under which it stops being worth the cost:** (i) Session 6 bootstrap substrate cannot in practice hold framework-pull discipline; (ii) bridging-arc to multi-tenant materializes at scale where Python's GIL-bounded CPU-per-process becomes binding (downstream of design horizon); (iii) Phase 7 surfaces an empirical reliability defect class traceable to Python's runtime model.

### §5.2 Committed tooling decisions (12 items per Kickoff §2.1)

| # | Decision area | Commitment | Rationale + confidence |
|---|---|---|---|
| 1 | Programming language | Python 3.12+ | §5.1; min version for `match` statement + improved error messages + structural typing maturity. [HIGH] |
| 2 | Package manager | `uv` (workspace-aware) | Lockfile-first; materially faster than poetry / pip+venv. Aligns with C-STK-12 by avoiding framework-style dep solvers. [MODERATE — recent agent-harness substrate convergence signal] |
| 3 | Type checker | `pyright` (strict mode) | Faster than mypy on large codebases; better LSP integration; better Pydantic v2 interop. [MODERATE] |
| 4 | Linter / formatter | `ruff` (single tool for both) | Replaces flake8 + black + isort. Speed + unified config. [MODERATE] |
| 5 | Test runner | `pytest` + `pytest-asyncio` | Canonical for Python async; required for testing C9 retry / breaker primitives. [HIGH] |
| 6 | Repo structure | Monorepo with axis-subdirectory uv workspace (`harness-{is,as,cp,od,cxa}/` + shared `harness-core/`) | Mirrors v2.3 plans' axis decomposition; uv workspaces support multi-package without framework. [HIGH on shape; MODERATE on exact subdivision — Session 2 audit informs] |
| 7 | Git posture | Conventional commits; commit-per-unit-cluster (coarser than per atomic unit); PR-per-axis-cluster; feature branches off `main` | Aligns with v2.3 atomic-unit decomposition without one-commit-per-unit overhead. [MODERATE] |
| 8 | CI substrate | Defer to post-bootstrap milestone | Per Kickoff §2.1 explicit allowance; CI substrate is operationalization, not foundational. [HIGH on deferral allowance] |
| 9 | Multi-LLM SDK stance | Per-provider official SDKs (`anthropic`, `openai`, `ollama`) under capability-aware abstraction per ADR-F1 v1.2 §Decision. **NOT LiteLLM.** | F1 v1.2 §Rationale (b) explicit. [HIGH] |
| 10 | OTel SDK | `opentelemetry-api` + `opentelemetry-sdk` + `opentelemetry-exporter-otlp` (gRPC + HTTP); `opentelemetry-instrumentation-genai` libraries adopted selectively; 12-namespace project-authored attribute schemas per ADR-D6 v1.2 §1.2 | Per ADR-D6 v1.2. [HIGH] |
| 11 | Local-deployment ergonomics | `python-keyring` (per F5 named); SQLite via stdlib `sqlite3` (per OD axis ledger commitments) | Per ADR-F5 v1.1 + OD axis plan. [HIGH] |
| 12 | Core dependency stance | **Minimal-framework**: NO LangGraph / LangChain / Temporal / CrewAI / LlamaIndex as foundational. Pydantic + httpx + asyncio + per-provider SDKs as primitives. Discipline enforced via Session 6 bootstrap substrate (CLAUDE.md design constraints). | Per C-STK-12 + Tension 1 resolution. [HIGH on commitment; MODERATE on discipline holding in practice] |

### §5.3 Decision scope and what it does NOT commit

This artifact commits the language + tooling + dependency stance. It does NOT commit:

- Specific library bindings beyond those named at §5.2 (further library selections are downstream D-ADRs per Pattern Reference Catalog v1.0 §11.3.2 derivative classification)
- Specific durable-execution engine selection per workload class (F3 deferred — composes with stack)
- Specific OTel collector vendor (local-development OTLP collector substrate is the relevant primitive; vendor binding deferred)
- Exact module-level decomposition within each axis subdirectory (Session 2 α audit informs)
- `uv` workspace lockfile vs per-package lockfile granularity (Phase 7 detail)
- Per-`instrumentation-genai` library adoption at v1.0 milestone vs build manually (Phase 7 detail)

---

## §6 Alternatives considered + reasons for rejection

### §6.1 TypeScript / Node.js — second-best, retained as documented alternative

**Posture:** Genuine alternative; the call against TS is on tiebreakers, not on capability.

**Trade analysis:**

| Gain (TS over Python) | Cost (TS over Python) |
|---|---|
| Lower framework-pull risk (A9) | Local-tier ergonomics asymmetric: vLLM HTTP-only; `llama.cpp` no canonical TS binding; Ollama JS workable [HIGH] |
| Standard Schema ecosystem unity (Zod v4 / Valibot / ArkType) flowing from MCP TS SDK through validator gates | OTel GenAI instrumentation one revision behind Python (1.36.0 vs 1.41.0 spec) [HIGH] |
| Single-runtime story (Node + Bun + Deno) | Pyright strict mode is stricter than `tsc --strict` on schema-heavy code |
| TS Agent SDK bundles Claude Code binary | Less Anthropic-engineering primary-source coverage in TS substrate |

**Reason for rejection:** Local-tier coverage (Tiebreaker 1 §4.3) and OTel GenAI lead (Tiebreaker 2 §4.3) jointly favor Python. The TS option would be selected if the operator judged framework-discipline-by-ecosystem more reliable than framework-discipline-by-governance — a coherent position the operator did not take.

**Status:** Retained-not-rejected at the language-decision level; not selected. Re-evaluable if local-tier or OTel constraints shift materially downstream.

### §6.2 Rust — deferred-not-rejected

**Posture:** Strongest on framework-purity (A9) and async-primitives (A7); weakest on SDK-maturity cluster (A1, A2, A3) and developer-iteration velocity (A10).

**Reason for rejection:** SDK build-cost imposed on Anthropic + MCP host + OTel GenAI + Claude Agent SDK equivalents is weeks-to-months of bridging work [SPECULATIVE — not benchmarked but qualitatively consistent with substrate]. C9 consultation (§4.2) confirmed Rust's async-primitives advantage is not load-bearing for the C9 contract at the persona's tens-concurrent scale.

**Status:** Deferred-not-rejected. Re-evaluable if Phase 7 surfaces a reliability defect class traceable to Python's runtime model.

### §6.3 Go — probe candidate, deferred-not-rejected

**Posture:** Comparable to TS on most axes; sharper A3 (OTel GenAI) gap. Official MCP Go SDK (Google-maintained) is a real advantage.

**Reason for rejection:** Same SDK-build-cost reasoning as Rust on A1 (no Claude Agent SDK in Go), A3 (no production GenAI contrib), and A6 (less unified schema validation). Loses to TS on the same axes where TS already loses to Python.

**Status:** Deferred-not-rejected.

### §6.4 LiteLLM-class lowest-common-denominator gateway abstraction

**Status:** Explicitly precluded by ADR-F1 v1.2 §Rationale (b). Not a stack-language alternative; a SDK-stance alternative. Documented here for completeness: rejected at Phase 3a; not reopened at this session.

---

## §7 Tradeoff acknowledgments — known limitations of the committed stack

Five limitations acknowledged at commit time:

1. **Framework-pull risk (A9) is real and not eliminated.** The Python agent-harness corpus is LangGraph / LangChain / LlamaIndex / CrewAI idiomatic. Discipline mechanism (Session 6 bootstrap substrate) must hold in practice. [MODERATE on discipline holding; Session 6 deliverable to validate]
2. **GIL-bounded CPU concurrency.** Python's GIL bounds CPU-bound parallelism within a process. Agent-harness work is I/O-bound at design horizon; the limitation is non-binding currently but becomes binding under multi-tenant scale-out (ADR-F2 §(c) condition). [HIGH on technical claim; MODERATE on relevance horizon]
3. **OTel GenAI semconv is at Development tier**, not Stable [HIGH — verified at `opentelemetry.io/docs/specs/semconv/gen-ai/` this session]. Schema revisions will occur; the 12-namespace ADR-D6 v1.2 contract must absorb upstream changes. Python is the lead language for absorbing these — the upside of the lag risk.
4. **Pydantic v2 + Pyright strict mode + uv workspaces is a relatively new toolchain combination.** Each is mature individually; the combined experience is less benchmarked. [MODERATE]
5. **Local-tier coverage advantage assumes vLLM / Ollama / llama.cpp remain reachable.** If local-tier evolves toward Rust / Go-native servers (e.g., a llama.cpp Rust re-implementation gaining canonical status), Python's local-tier advantage narrows. [SPECULATIVE — no current signal]

---

## §8 Forward implications — what downstream sessions absorb

### §8.1 Per-session inheritance

| Downstream session | Inheritance from this commitment |
|---|---|
| Session 2 (α — Pre-flight executability audit) | Validates v2.3 atomic units' executability against Python 3.12+ + uv + pyright + ruff + pytest + Pydantic v2 + opentelemetry-python + python-keyring + FastMCP. Audits §5.2 commitments against per-unit signature feasibility. Identifies any plan unit requiring fork (Class 1 / 2) under the committed stack. |
| Session 3 (ζ — F3-02 IS-axis revision pass) | IS plan v2.2 revision composes against §5.2 item 11 (sqlite stdlib for OD ledger). [HIGH] |
| Session 4 (η + θ — Chicken-and-egg meta-architecture) | H_T ↔ H_E substitution mapping authored against §5.1 + §5.2 — substitutions where Claude Code CLI (H_E) provides primitives H_T's Python stack will eventually own. |
| Session 5 (γ — Workflow v1.8 promotion) | §2.7 absorbs §5.1 + §5.2 as canonical stack commitment for Phase 7. |
| Session 6 (ε — Claude Code CLI bootstrap substrate) | CLAUDE.md design constraints encode §5.2 item 12 (minimal-framework discipline); custom skills enforce Pydantic + ruff + pytest patterns; sub-agent boundaries align with §5.2 item 6 axis-subdirectory shape. |
| Session 7 (β — Phase 7 Session 1 Entry Directive) | Substrate inventory includes §5.1 + §5.2 commitments as canonical for Phase 7 new-workspace entry. |

### §8.2 Phase 7 implications

Phase 7 executes at new Claude Code CLI workspace per Workflow DP-4 default. Phase 7's H_T build proceeds against §5.1 + §5.2 as committed substrate. Forks discovered at Phase 7 execution that affect the stack commitment route back to this artifact for revision per `Phase_7_Kickoff_Prompt.md` §6 back-flow discipline.

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `Target_Stack_Commitment_v1.md` |
| Status | Filed at session close 2026-05-15 |
| Phase | Phase 6.5 Session 1 (δ) close |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; Phase 6.5 Session 1 Kickoff §2.3 recommended structure |
| Predecessor | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md`; `Phase_6_5_Session_1_Kickoff.md` |
| Successor (immediate) | `Phase_6_5_Session_1_Close_Handoff.md`; `Phase_6_5_Session_2_Kickoff.md` |
| Companion arc artifact | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Filing destination | `/mnt/user-data/outputs/Target_Stack_Commitment_v1.md` → operator pushes to `/mnt/project/` |
| Date | 2026-05-15 |

---

*End of Target Stack Commitment v1. Operator-committed at Phase 6.5 Session 1 (δ) close. Governs Phase 7 H_T build against the v2.3 implementation plans.*
