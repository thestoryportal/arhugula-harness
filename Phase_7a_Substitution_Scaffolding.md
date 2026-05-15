# Phase 7 — Sub-phase 7a Substitution Scaffolding

*7a substitution-scaffolding ledger. Operator-authored Convention-mechanism
declarations standing in for not-yet-built H_T primitives. NOT canonical —
each section is retired per its X-AL-2 retirement criterion. Authority:
Phase_7_Session_1_Entry_Directive_v1.md §6.2; Phase_7_Meta_Architecture_v1.md
§10.1.3 + §5.2.*

---

## §1 Surface 1 — Path conventions  [substitutes H_T-IS-1; C-IS-01 §1]

**Mechanism:** Convention. The 4-class path semantics below are declared here;
Read/Write/Glob operations during 7a obey these roots via prompt-discipline.
**Retirement:** this section retires when U-IS-01 + U-IS-02 + U-IS-03 land
(the typed path-class registry supersedes this convention).

### §1.1 The 4 canonical artifact classes (per C-IS-01 §1)

| Path class       | C-IS-01 residence contract                          | 7a convention root (provisional)        |
|------------------|-----------------------------------------------------|-----------------------------------------|
| SKILLS           | SKILL.md-as-directory; one folder per skill         | `.harness/skills/`                      |
| PROMPTS          | plain-text-file-in-git; one file per prompt         | `.harness/prompts/`                     |
| ROUTING_MANIFEST | single file in git; per-role/-class/-step model map | `.harness/routing.manifest.json`        |
| STATE_LEDGER     | two-mode: JSONL event ledger + git commit stream    | JSONL: `.harness/state.jsonl`; commit stream: workspace git repo |

### §1.2 Prompt-discipline rule

During 7a, all H_T artifact Read/Write/Glob operations resolve against the
roots in §1.1. `Glob` enumerates a path class against its declared root only.

### §1.3 Anti-leakage (IS-AL-1)

The H_T path-class roots live under `.harness/` (H_T-canonical runtime root).
They are NOT `.claude/` — `.claude/skills/` hosts the four H_E Phase 7-specific
skills (execution-harness scaffolding), which are categorically distinct from
the H_T SKILLS path class. `.harness/` ≠ `.claude/`; this convention is a
substitution, not the typed registry (IS-AL-1).

### §1.4 Provisional-binding note

The §1.1 root strings are 7a-provisional. C-IS-01 §1 defers canonical path
strings to implementation; the typed binding lands at U-IS-01/U-IS-02. If
the IS plan v2.2 unit declarations bind different strings, reconcile at
U-IS-01 landing (this section retires at that point regardless).

---

## §2 Surface 2 — State ledger  [substitutes H_T-IS-5; C-IS-05 §5]

**Mechanism:** Shell-out. The state ledger is a JSONL file at
`.harness/state.jsonl` (STATE_LEDGER path class, §1.1). During 7a:
entries are produced via `Bash(python -c 'import json…')`, appended via
`Bash(cat <<EOF >> .harness/state.jsonl)`, and consumed via `Read`.
**Retirement:** retires when U-IS-07 lands (typed entry shape); full
H_T-IS-5 retirement per U-IS-07/08/09/10.

### §2.1 Entry shape — canonical 6-field tuple (C-IS-05 §5)

| Field            | Type / format             | Semantic                                    |
|------------------|---------------------------|---------------------------------------------|
| action_id        | identifier, unique/action | identifies the action this entry records    |
| idempotency_key  | identifier, stable/op     | harness-canonical join key (ADD §2.2)       |
| actor            | identifier                | agent / sub-agent / operator originator     |
| response_hash    | SHA-256 digest            | hash of canonical-JSON of the payload       |
| timestamp        | monotonic timestamp       | wall-clock instant the entry was written    |
| prior_event_hash | SHA-256 digest OR zeros   | hash of prior entry; all-zeros at inception |

### §2.2 7a-provisional field formats (C-IS-05 defers these to implementation)

| Field           | 7a-provisional convention                                            |
|-----------------|----------------------------------------------------------------------|
| action_id       | UUID v4                                                              |
| idempotency_key | hex string (Stripe-style); keying tuple per C-IS-07 §7.1 deferred per §7.4 |
| timestamp       | RFC 3339 UTC (e.g. `2026-05-15T12:00:00Z`)                           |

Provisional; reconciled at U-IS-07 landing.

### §2.3 Scope boundary vs surface 3

`response_hash` + `prior_event_hash` are entry *fields* (shape declared
here); their *computation* (SHA-256 + RFC 8785 canonicalization) is
surface 3 (hash-chain). Surface 2 establishes the file + shape + append
convention only.

### §2.4 Anti-leakage (IS-AL-3, IS-AL-4)

IS-AL-3: H_E conversation history `(role, content, tool_calls,
tool_results)` ≠ the 6-field H_T entry shape. IS-AL-4: the `Bash`
shell-out is a substitution, not the C-IS-05/C-IS-06 typed contract
(that lands at U-IS-07/08/09/10).

---

## §3 Surface 3 — Hash-chain  [substitutes H_T-IS-6; C-IS-06 §6]

**Mechanism:** Shell-out. State-ledger hash-chain integrity is
constructed at write-time via `Bash` invocation of Python stdlib
(`hashlib.sha256` + `json`). **Retirement:** retires when
U-IS-08 + U-IS-09 + U-IS-10 land.

### §3.1 The 4-step discipline (C-IS-06 §6.1–§6.4)

1. canonicalize(entry) -> deterministic bytes
2. response_hash = SHA-256(canonicalize(entry))
3. chain construct: prior_event_hash links entry N to entry N-1
4. verify_chain: re-canonicalize, re-hash, check linkage + inception

### §3.2 7a canonicalization convention

C-IS-06 §6.1 names RFC 8785 JSON Canonicalization Scheme (JCS) as the
baseline candidate; the library binding is deferred to a downstream
D-ADR. The 7a state-ledger entry (§2.1) has six all-string fields and
no numeric values; JCS's only non-trivial divergence is numeric
serialization. Therefore the 7a substitution uses Python stdlib:

    json.dumps(entry, sort_keys=True, separators=(',', ':'),
               ensure_ascii=False).encode('utf-8')

— which is byte-faithful to RFC 8785 JCS for all-string entries. A
true JCS library binding becomes mandatory when any numeric field is
introduced; deferred per C-IS-06 §6.1 + §6 Deferred-to-implementation.

### §3.3 Chain construction (C-IS-06 §6.3)

- prior_event_hash stored as 64-hex-char string.
- Inception (entry 1): prior_event_hash = "0"*64 (ALL_ZEROS_SENTINEL,
  32 zero bytes).
- Entry N>1: prior_event_hash = response_hash of entry N-1
  = SHA-256(canonicalize(entry N-1)).

### §3.4 Hash-input scoping  [PROVISIONAL — under-specified by C-IS-06]

C-IS-06 §6.2 writes "response_hash = SHA-256(canonicalize(entry))",
but response_hash is itself a field of entry — self-reference. C-IS-06
does not state which fields are excluded from the canonicalization
input. 7a-provisional resolution: response_hash is computed over the
entry with the response_hash field omitted; prior_event_hash IS
included (it is known before hashing). verify_chain re-canonicalizes
identically. This scoping is reconciled at U-IS-08 (canonicalize) /
U-IS-09 (chain construct) / U-IS-10 (verify).

### §3.5 Anti-leakage (IS-AL-4)

The `Bash`+stdlib hash-chain is a substitution, not the C-IS-06 typed
contract. "We have a Python script that does SHA-256 chaining" does
NOT mean U-IS-08/09/10 are complete (IS-AL-4 anti-pattern, verbatim).

---

## §4 Surface 4 — MCP server  [substitutes H_T-AS-2; C-AS-03 §3.1]

**Mechanism:** MCP-server. H_T tools are authored at a FastMCP server
(`scaffolding/mcp/server.py`), registered in `.mcp.json` local scope.
Strict Pydantic v2 schemas server-side; namespacing + description-as-
prompt via FastMCP. The MCP server *process* is the X-AL-1 substrate
boundary (H_E <-> H_T).
**Retirement:** retires when U-AS-04 → U-AS-09 land (typed ToolContract).

### §4.1 Server + registration

- Server: `scaffolding/mcp/server.py` — `FastMCP("harness-7a-scaffold")`.
- Registered in `.mcp.json` as a stdio server.
- NOT in `src/harness_*/` (X-AL-3 — those trees are atomic-unit landings).
- Tool inputs are flat typed parameters; tool outputs are Pydantic v2
  models (FastMCP idiom — generates validated schemas by construction).

### §4.2 Representative tools (≥3 per axis; ≥12 total — 7a exit-crit #3)

12 tools landed at `scaffolding/mcp/server.py` — 3 per axis, 12 total.
Per-tool `[substitutes H_T-…]` tags verified byte-exact against
Meta-Architecture §5.

| Tool                  | Axis | Substitutes | Body            |
|-----------------------|------|-------------|-----------------|
| `read_file`           | AS   | H_T-AS-2    | real H_E-equiv  |
| `write_file`          | AS   | H_T-AS-2    | real H_E-equiv  |
| `run_bash`            | AS   | H_T-AS-2    | real H_E-equiv  |
| `append_state_ledger` | IS   | H_T-IS-5    | schema-faithful stub |
| `read_state_ledger`   | IS   | H_T-IS-5    | schema-faithful stub |
| `verify_hash_chain`   | IS   | H_T-IS-6    | schema-faithful stub |
| `route_llm_call`      | CP   | H_T-CP-1    | schema-faithful stub |
| `invoke_with_retry`   | CP   | H_T-CP-3    | schema-faithful stub |
| `hitl_prompt`         | CP   | H_T-CP-20   | schema-faithful stub |
| `emit_span`           | OD   | H_T-OD-2    | schema-faithful stub |
| `redact_span`         | OD   | H_T-OD-4    | schema-faithful stub |
| `record_cost`         | OD   | H_T-OD-5    | schema-faithful stub |

**Tool-body fidelity (operator-approved, this session):** surface 4 is
scoped to the tool-authoring surface per §4.3 — NOT axis logic. IS/CP/OD
tool bodies are schema-faithful stubs returning deterministic representative
values; the Pydantic v2 schema is the deliverable. `read_file` / `write_file`
/ `run_bash` perform their real op (pure H_E-equivalent filesystem/shell, no
axis logic). Axis logic lands at the atomic-unit consumptions.

**Citation note:** the 7a candidate set named an `audit_append` tool; no
distinct §5 OD substitution row exists for an audit-ledger primitive, so the
third OD tool is `redact_span` substituting H_T-OD-4 (SpanProcessor
pre-export redaction). OD spans OD-2 / OD-4 / OD-5.

### §4.3 Bounded scope (H_T-AS-2; Meta-Architecture §5.3)

Covers: tool-schema authoring + namespacing + description-as-prompt at
the MCP boundary. Does NOT cover: strict-mode contract verification
harness-side; `minimum_tier`/`blast_radius_tier` (H_T-AS-1); cross-tool
dependency declaration.

### §4.4 Anti-leakage (AS-AL-2, X-AL-1)

AS-AL-2: H_E built-in tools ≠ user-extensible H_T tools — all H_T tool
surface lives behind the MCP server boundary. X-AL-1: the boundary is
the MCP server *process* (process isolation, not convention).

---

## §5 Surface 5 — Sub-agent spawning  [substitutes H_T-CP-10 partial; C-CP-10 §10]

**Mechanism:** H_E-direct. Sub-agents are spawned via the H_E `Agent`
tool with a free-text prompt supplied inline at spawn time — no artifact
file lands at 7a. The 5 named sub-agents (sa-is / sa-as / sa-cp / sa-od /
sa-cxa) are specified at `Sub_Agent_Boundary_Specification_v1.md` §3 and
activate at the 7a → 7b boundary (sa-is activation window).
**Retirement:** this surface does NOT retire the way §1–§4 do. Per
`Sub_Agent_Boundary_Specification_v1.md` §5.2.3, what retires at U-CP-22
landing is the *substitution claim* — that H_E orchestrator-workers
stands in for H_T-CP-10. The H_E sub-agents themselves carry NO retirement
criterion; they remain active H_E execution-time scaffolding for the full
Phase 7 workspace lifetime. This §5 ledger entry retires (substitution
claim discharged) at U-CP-22; the `Agent` tool keeps being used after.

### §5.1 Scope boundary (H_T-CP-10 partial; Meta-Architecture §5.4)

Covers: a single implicit orchestrator-workers pattern. Does NOT cover:
the TopologyPattern 6-class enum, the admissibility predicate, or
`CascadePolicy` — those are C-CP-10 §10 contracts landing at U-CP-22
(CP plan v2.3 Cluster 4).

### §5.2 Anti-leakage — CP-AL-1 (the load-bearing rule)

CP-AL-1 verbatim per the Meta-Architecture §7.4 citation grammar:

> **CP-AL-1.** H_E sub-agent topology (orchestrator-workers via `Agent`
> tool) ≠ H_T TopologyPattern 6-class enum (ORCHESTRATOR_WORKERS /
> DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION /
> ROUTING / SEQUENTIAL_PIPELINE)
>
> *Anti-pattern foreclosed:* Concluding "we already have
> orchestrator-workers" implies H_T-CP-10 is met

Clarifier per `Sub_Agent_Boundary_Specification_v1.md` §5.2.2 + §5.2.4:
the H_E orchestrator-workers pattern *coincidentally* maps to the
`ORCHESTRATOR_WORKERS` enum value — this coincidence does NOT satisfy
H_T-CP-10. The 6-class enum operates at H_T *runtime*; Phase 7
build-time sub-agent spawning is an H_E orchestration decision, not an
H_T topology decision.

### §5.3 Related anti-leakage (X-AL-1, X-AL-3)

X-AL-1: sub-agents operate H_E-side; they do NOT cross the MCP server
boundary (the H_E ↔ H_T substrate boundary). X-AL-3: sub-agents
implementing per-axis atomic units MUST NOT silently extend H_T design
— new H_T primitives surfaced at sub-agent execution-time route to
design-phase back-flow (Class 1 fork) before implementation proceeds.

### §5.4 Cross-reference

`Sub_Agent_Boundary_Specification_v1.md` — §3 (5 sub-agents), §5
(CP-AL-1 application), §6 (per-sub-agent scope boundaries against the
4 axes).

---

## §6 Surface 6 — OTel emission  [substitutes H_T-OD-2 + H_T-OD-4; C-OD §5.5]

**Mechanism:** MCP-server. OpenTelemetry SDK is wired into the
scaffolding MCP server at `scaffolding/mcp/telemetry.py`; every tool
invocation emits one span at the MCP server boundary; spans export via
OTLP to a user-launched Collector. **Retirement:** H_T-OD-2 retires when
U-OD-04 → U-OD-08 land (OTel SDK base); H_T-OD-4 retires when
U-OD-13 → U-OD-16 land (SpanProcessor redaction).

### §6.1 Module + wiring

- `scaffolding/mcp/telemetry.py` — `_build_tracer()` configures a
  `TracerProvider` with a service `Resource`; `traced(span_name)` is a
  decorator applied between `@mcp.tool()` and each tool function
  (`functools.wraps` preserves the signature, so FastMCP schema
  generation is unaffected).
- All 12 representative tools (§4.2) are span-instrumented. Span names:
  `read_file` → `files.read.completed`, `write_file` →
  `files.write.completed` (byte-exact to the §10.1.6 smoke-test span
  names); the other 10 → `mcp.tool.{name}`.
- NOT in `src/harness_*/` (X-AL-3 — atomic-unit landings only).

### §6.2 Exporters

| Exporter | Target | Gating |
|----------|--------|--------|
| `ConsoleSpanExporter` | **stderr** | always on |
| OTLP gRPC | `OTEL_EXPORTER_OTLP_ENDPOINT` | on only when that env var is set |

Console export targets **stderr**, NOT stdout — stdout is the stdio MCP
JSON-RPC channel and must not be polluted. This satisfies 7a
exit-criterion #5 ("OTel emission visible at MCP server boundary")
directly. OTLP export to the user-launched Collector subprocess
(H_T-OD-6) is gated on the endpoint env var so the default run stays
clean when no Collector is up.

### §6.3 Bounded scope (H_T-OD-2 + H_T-OD-4; Meta-Architecture §5.5)

Covers: OTel SDK base at the MCP server boundary; per-tool span
emission; the SpanProcessor injection seam. Does NOT cover: H_E-internal
events (closed surface); cross-process OTel context propagation;
multi-tenant redaction discipline; the OTel Collector + sqlite
ring-buffer (that is H_T-OD-6, operator-launched per exit-criterion #5,
NOT one of the 9 surfaces).

### §6.4 7a-PROVISIONAL notes

- **GenAI semconv 1.41.0** (cited at the H_T-OD-2 substitution row) is
  deferred. The 12 representative tools are not LLM calls, so the
  `Resource` carries service identity only (`service.name` +
  `service.version`). Full GenAI semconv attributes land at
  U-OD-04 → U-OD-08.
- **`RedactingSpanProcessor` is a schema-faithful stub.** The OTel
  `SpanProcessor` ABC delivers an *immutable* `ReadableSpan` to
  `on_end`, so true structure-not-content redaction cannot mutate the
  span at the processor — real OTel redaction is exporter-side. The
  stub subclasses the `SpanProcessor` ABC and marks the H_T-OD-4
  injection seam at `on_end` as a documented no-op (forwards spans
  unchanged to the delegate). The `redact_span` tool (§4.2) demonstrates
  the redaction *transform* separately. Real redaction-before-export
  lands at U-OD-13 → U-OD-16. (Same provisional-flag discipline as
  §3.4's hash-input-scoping under-specification.)

### §6.5 Anti-leakage (OD-AL-1, OD-AL-3, X-AL-1)

OD-AL-1: H_E telemetry (closed Claude Code analytics) ≠ harness
observability substrate. OD-AL-3: all OTel emission during 7a happens
at the MCP server boundary (H_T-authored code) — H_E does NOT
participate in OTel emission. OD-AL-3 is the canonical concretization
of X-AL-1: the substrate boundary is enforced at OD by "no H_E
participation in OTel emission", not by convention.

---

## §7 Surface 7 — HITL primitive  [substitutes H_T-CP-20 partial; C-CP-20 §20]

**Mechanism:** H_E-direct. Human-in-the-loop is the H_E `AskUserQuestion`
tool + permission-prompt approval — no artifact lands at 7a.
**Retirement:** retires when U-CP-46 lands (the typed HITL primitive +
4-response palette supersedes the bare `AskUserQuestion` mechanism).

### §7.1 Scope boundary (H_T-CP-20 partial; Meta-Architecture §5.4)

Covers: the HITL *invocation* surface. Does NOT cover: the 4-response
palette (APPROVE / APPROVE_WITH_NOTE / DEFER / REJECT), or `hitl.*` /
`audit.*` namespace emission — C-CP-20 §20 contracts landing at U-CP-46.

### §7.2 Anti-leakage

No dedicated CP-AL letter rule binds HITL; the Meta-Architecture §5
H_E-classification disposition governs:

> H_T-CP-20: `AskUserQuestion` mechanism present; 4-response palette +
> namespaces absent.

X-AL-3 binds — the 4-response palette is a design contract, not an
execution-time extension. Note: the `hitl_prompt` MCP tool (§4.2)
returns a representative `response_class` drawn from the palette
vocabulary, but that is a schema-faithful stub — it does NOT constitute
the H_T-CP-20 palette primitive.

---

## §8 Surface 8 — Sandbox-tier dispatch  [substitutes H_T-CP-12 partial; C-CP-12 §12]

**Mechanism:** H_E-direct. `--permission-mode` set at session open, plus
per-tool allow/deny by convention — no artifact lands at 7a.
**Retirement:** retires when U-CP-26 + U-CP-27 land.

### §8.1 Scope boundary (H_T-CP-12 partial; Meta-Architecture §5.4)

Covers: coarse default-downgrade via permission mode. Does NOT cover:
the monotonic-descent invariant, override-with-audit, cross-deployment
monotonicity, or dispatch-audit composition — C-CP-12 §12 contracts
landing at U-CP-26 + U-CP-27.

### §8.2 Related primitive (H_T-AS-1)

The same H_E `--permission-mode` mechanism ALSO substitutes H_T-AS-1
(4-tier blast-radius gating: Tier-1 `plan` / Tier-2 default + `deny` /
Tier-3 `acceptEdits` / Tier-4 `bypassPermissions`; retires at
U-AS-01 + U-AS-02). Surface 8's primary substitution authority per
§6.2 of the Entry Directive is H_T-CP-12; the H_T-AS-1 overlap is
recorded so retirement at U-CP-26/27 is NOT mistaken for retiring the
H_T-AS-1 substitution (the two retire on independent unit landings).

### §8.3 Anti-leakage

Meta-Architecture §5 disposition:

> H_T-CP-12: permission-mode gradient ≠ sandbox-tier dispatch.

The 4 permission modes are not the H_T sandbox-tier dispatch primitive.
X-AL-3 binds.

---

## §9 Surface 9 — Workflow conventions  [substitutes H_T-CP-6 partial; C-CP-06 §6]

**Mechanism:** Convention. `CLAUDE.md` carries workflow conventions as
prose; per-step override via operator-edited prompt.
**Retirement:** retires when U-CP-13 + U-CP-14 land (the typed
`WorkflowManifestEntry` schema supersedes the prose convention).

### §9.1 Scope boundary (H_T-CP-6 partial; Meta-Architecture §5.4)

Covers: human-readable workflow declaration. Does NOT cover: the typed
`WorkflowManifestEntry` schema, the programmatic per-step override
evaluator, or audit composition — C-CP-06 §6 contracts landing at
U-CP-13 + U-CP-14.

### §9.2 Anti-leakage — CP-AL-5

CP-AL-5 verbatim per the Meta-Architecture §7.4 citation grammar:

> **CP-AL-5.** H_E `CLAUDE.md` (prose convention loaded into system
> prompt) ≠ typed `WorkflowManifestEntry` schema with per-step override
> evaluator + audit
>
> *Anti-pattern foreclosed:* Treating `CLAUDE.md` declarations as
> functional substitute for typed workflow manifest entries

X-AL-3 also binds — the typed manifest schema is a design contract.
