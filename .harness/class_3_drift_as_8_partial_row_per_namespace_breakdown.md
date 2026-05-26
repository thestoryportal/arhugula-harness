# Class 3 drift — H_T-AS-8 PARTIAL row per-namespace breakdown

| Field | Value |
|---|---|
| Class | 3 (informational drift; non-blocking) |
| Filed at | 2026-05-26 (AS-8 discriminator audit) |
| Filed by | discriminator-audit pass per `phase-7-substitution-retirement` skill §3.2 |
| Affected artifact | `harness-as/CLAUDE.md` §4.1 H_T-AS-8 row text |
| HEAD at filing | worktree HEAD this session |

---

## §1 Scope

This drift surfaces during the AS-8 discriminator audit prerequisite to the anthropic.* 6-attr emission close (this session). The H_T-AS-8 PARTIAL row text at `harness-as/CLAUDE.md` §4.1 is stale on **two fronts**:

1. **`memory.*` 6-attribute namespace fully landed at production**, but the PARTIAL row text describes memory.* as "not yet routed at runtime composers" alongside skill/files/managed_agents. Producer span site is `memory_tool_dispatch.py:286-338` opening `memory.operation` span with all 6 attrs (`memory.operation.kind` / `memory.path` / `memory.backend` / `memory.bytes_read` / `memory.bytes_written` / `memory.context_editing_active`) per AS spec C-AS-14 §14.7. Consumer chain at `llm_dispatch.py:354` invokes `execute_with_memory_callbacks` with bound `memory_tool_registry`. Production-emitting since L9-octies arc landing (`42c9a30`, 2026-05-23).

2. **PARTIAL row text aggregates 4 distinct namespace statuses into one prose sentence.** Per-namespace state per AS spec C-AS-14 §14.1 6-namespace enumeration:

| Namespace | Spec attrs | Production | Producer site |
|---|---|---|---|
| `anthropic.*` | 10 | 10/10 (post this arc) | `llm_dispatch.py:386-432` gen_ai span |
| `mcp.*` | 7 | 7/7 | `mcp_client_namespace_emitter.py:73-79` + `runtime_tool_dispatcher.py:375` |
| `memory.*` | 6 | 6/6 | `memory_tool_dispatch.py:286-338` `memory.operation` span |
| `skill.*` | 6 | 0/6 | NO PRODUCER (Skills loading runtime composer not yet authored) |
| `files.*` | 8 | 0/8 | NO PRODUCER (Files arc deferred indefinitely per runtime spec v1.17 §14.C) |
| `managed_agents.*` | 3 | 0/3 | NO PRODUCER (managed_agents SDK not yet integrated) |

**Post-arc summary:** 3/6 namespaces complete; 3/6 absent at producer-site layer; 0/6 partial.

---

## §2 Why this is Class 3 (not Class 1)

- **No contract violation.** AS spec C-AS-14 unchanged; all consumer-side schemas at harness-od carrier modules (`namespace_map.py`, `content_structure_discipline.py`, `attribute_class_enforcement.py`) align with spec.
- **No production bug.** `memory.*` emission is correct; the PARTIAL row text drifted post-L9-octies without an update arc.
- **No retirement-criterion impact.** AS-8 remains PARTIAL — the 3 absent namespaces each gate on an unbuilt H_T primitive (per §3 below). RETIRED close is not on the table at this arc regardless of the drift fix.

---

## §3 AS-8 RETIRED gate per remaining namespace

Each of the 3 absent namespaces is bounded on a different unbuilt H_T primitive. Documentation owed at retirement-ledger v2 §6 row 80 (AS-8) per §4 below.

| Namespace | RETIRED gate | Estimated arc shape |
|---|---|---|
| `skill.*` | Producer site authoring at Skills loading path (`skill.activation` span site). Likely under AS-axis or harness-cp Skills loader. Skills loading mechanism is H_E ✓ native per AS-AL-3 but the AS-side observability emission needs a producer composer step. | ~3-5 commits: add SkillActivationSpanEmitter carrier; invoke at Skills-load site; tests. |
| `files.*` | Files arc deferred indefinitely per runtime spec v1.17 §14.C (Memory-only scope per Class 1 fork ratification 2026-05-23). Operator-discretion timing on opening Files arc. | Deferred indefinitely. Not gated on observability — gated on Files API surface authoring decision. |
| `managed_agents.*` | managed_agents Anthropic SDK integration not yet present in H_T. Beta SDK shape: `AgentCreateParams` per Anthropic SDK `/anthropics/anthropic-sdk-python` docs. Integration is a separate H_T primitive landing. | Deferred — out-of-scope for current AS plan execution. |

**Implication.** Full H_T-AS-8 RETIRED closure requires 3 separate multi-commit arcs across 2 unbuilt H_T primitives (Files + managed_agents) and 1 producer-site-authoring (Skills observability). The "anthropic.* 6-attr close" arc this session moves the RETIRED gate from 2 namespace-completes + 1 partial → 3 namespace-completes + 0 partial. Pipeline-advance within PARTIAL tier.

---

## §4 Recommended doc updates

| File | Update |
|---|---|
| `harness-as/CLAUDE.md` §4.1 H_T-AS-8 row | Replace prose with per-namespace table per §1 above + cite this drift doc for full breakdown + acknowledge this arc's `anthropic.*` 6-attr close (10/10 LANDED). |
| `.harness/phase-7d-retirement-ledger-v2.md` §6 row 80 | (Optional, not patched at this arc per FM-2) — refresh per-namespace state from "anthropic.* cache subset live, remaining 6 anthropic.* attrs + mcp.* namespace still bounded" framing (pre-L9-sexies + pre-this-arc) to current state. Out-of-scope for narrow-scope arc per operator AskUserQuestion. |

---

## §5 Adjacent observations (not patched)

(a) **Class 1 fork candidate — span-name drift.** AS spec §14.1 anchors `anthropic.*` on parent span `llm.inference`; production emits at `gen_ai.{provider}.{operation}` per OTel semconv 1.41.0. Two readings: spec stale (Class 3) or production rename owed (Class 1). Surfaced at AS-8 discriminator audit; operator scoped current arc to anthropic.* attrs only. Future filing owed if a reader follows the spec `llm.inference` cite and finds it unreachable.

(b) **AS-8 retirement-ID structural shape.** Each of the 6 namespaces under AS-8 gates on a different production composer site. Single retirement-ID covering 6 independent producer-site landings creates "all-or-nothing" closure friction — partial advance through within-tier promotions (PARTIAL → PARTIAL-ADVANCE) is the only available transition until all 3 absent namespaces land. Decomposition into AS-8a (`anthropic.*`) / AS-8b (`mcp.*`) / AS-8c (`memory.*`) / AS-8d (`skill.*`) / AS-8e (`files.*`) / AS-8f (`managed_agents.*`) at retirement-ledger v2 §6 layer would enable per-namespace RETIRED closes. Out-of-scope for this arc; route to operator-discretion design-phase back-flow if decomposition is desired.

---

## Filing footer

| Field | Value |
|---|---|
| Class | 3 |
| Filed | 2026-05-26 |
| Resolution | Patched at this arc (`harness-as/CLAUDE.md` §4.1 row refresh); other items deferred per §3 + §5 |
| Predecessor | None — first AS-8 per-namespace breakdown filing |
