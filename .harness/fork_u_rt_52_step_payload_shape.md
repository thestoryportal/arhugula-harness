# Fork — U-RT-52 `step.step_payload` shape pin (Class 3 informational)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d, U-RT-52 close arc.
**Trigger:** Implementation of `RuntimeLLMDispatcher.dispatch` per `Spec_Harness_Runtime_v1.md` v1.2 §14.5 (C-RT-15). The contract narrative describes "`WorkflowStep` carries the step input payload" and "Dispatches to the provider's underlying SDK method", but does NOT pin `step.step_payload: Mapping[str, Any]` to a canonical neutral shape.
**Fork class:** **Class 3 informational** — non-blocking; composer must pick a convention to dispatch; convention is recoverable from ADR-F1 v1.2 + C-CP-01 §1.1 without architectural decision.
**Pattern reference:** `[[spec-prose-plan-body-drift-pattern]]` — descriptive prose under-specifies a load-bearing surface; treat as Class 3, land against the canonical reading, file the residual.

---

## §1 Observed gap

### §1.1 Spec §14.5 v1.2 silence

`design-substrate/Spec_Harness_Runtime_v1.md` v1.2 §14.5 C-RT-15 §Specification content step 1 + step 3:

> 1. Resolves the `ProviderClient` adapter via `ctx.providers` … using `binding.model_binding.provider`.
>
> 3. Dispatches to the provider's underlying SDK message-construction method (provider-specific: `anthropic.AsyncAnthropic.messages.create` / `openai.AsyncOpenAI.chat.completions.create` / `ollama.AsyncClient.chat`).

The spec narrative leaps from "WorkflowStep carries the step input payload" to "dispatches to the provider SDK" without specifying how the composer extracts `messages` / `tools` / `params` from the opaque `Mapping[str, Any]` declared at `harness_cp.workflow_driver_types.WorkflowStep.step_payload`.

### §1.2 The canonical neutral payload shape already exists

`harness_cp.cp_shared_types.ProviderAgnosticPayload` (declared at U-CP-00c L0 carrier, faithful FACTOR-OUT of C-CP-01 §1.1):

```python
class ProviderAgnosticPayload(BaseModel):
    """A provider-neutral inference payload.

    Per ADR-F1 v1.2 §Decision provider-neutral thin core + C-CP-01 §1.1
    (the generate/stream/tool_use ``(messages, tools, params)`` 3-tuple)."""

    messages: tuple[Mapping[str, Any], ...]
    tools: tuple[Mapping[str, Any], ...] | None
    params: Mapping[str, Any]
```

The type lands at v2.8 of the CP plan as a load-bearing L0 carrier. ADR-F1 v1.2 + C-CP-01 §1.1 both commit to this 3-tuple as the provider-neutral surface.

### §1.3 The composer cannot ship without a convention

`anthropic.AsyncAnthropic.messages.create` requires `messages` + `max_tokens`; `openai.AsyncOpenAI.chat.completions.create` requires `messages`; `ollama.AsyncClient.chat` requires `messages`. The composer must unpack `step.step_payload` into provider-SDK kwargs somehow. Three options:

| Option | Convention | Trade-off |
|---|---|---|
| A | `step.step_payload` IS `ProviderAgnosticPayload` shape | Composer pydantic-validates payload → `ProviderAgnosticPayload`; per-provider branch translates → SDK kwargs. Aligns with ADR-F1 v1.2 + C-CP-01 §1.1. |
| B | `step.step_payload` IS pre-shaped SDK kwargs already | Composer `**`-unpacks directly. Provider-shape leaks to caller; non-portable. |
| C | Halt — file Class 1 back-flow | Treat the spec gap as architectural; route to Phase 5 spec revision. |

---

## §2 Operator ratification

**Decision (2026-05-20):** **Option A** — `step.step_payload` IS `ProviderAgnosticPayload` shape (messages / tools / params).

**Rationale:** ADR-F1 v1.2 provider-neutral commitment + C-CP-01 §1.1 explicit 3-tuple substrate + `ProviderAgnosticPayload` carrier already lands at L0 + the spec narrative consistently cites the neutral payload across §14.5 itself ("the provider's underlying SDK method"). The convention is recoverable from the authority chain without re-litigation. Class 3 informational — record + amend spec; do not halt.

**Anthropic cache attribute scope:** all 4 per `Spec_Action_Surface_v1.md` C-AS-14 §14.2 (`cache_creation_input_tokens` + `cache_read_input_tokens` + `cache_breakpoint_id` + `cache_ttl_seconds`). Composer extracts breakpoint_id + ttl_seconds best-effort from request `cache_control` directives; returns `None` when absent.

**OTel context-manager phrasing:** spec §14.5 invariants phrase `async with tracer.start_as_current_span(...)`. OpenTelemetry's tracer CM is **synchronous**. Composer uses plain `with` inside the async function. Class 3 spec-prose-imprecision; record in spec amendment.

---

## §3 Resolution arc

1. **Land Option A convention in implementation** — composer pydantic-validates `step.step_payload` → `ProviderAgnosticPayload`; per-provider helpers translate to SDK kwargs.
2. **File typed error class** — `LLMDispatchPayloadShapeError` mapping to `RT-FAIL-PAYLOAD-SHAPE` surfaces when payload coercion fails; preserves driver-side fail attribution.
3. **Amend Spec_Harness_Runtime_v1.md §14.5** — bump v1.2 → v1.3 with explicit pin on `step.step_payload` shape + the 2 prose corrections (cache attribute count + sync `with`).
4. **Cross-link in module docstring** — `harness_runtime.lifecycle.llm_dispatch` references this fork file for the convention provenance.

---

## §4 Status

**RESOLVED 2026-05-20 same-day.** Option A landed at U-RT-52 close arc. Spec v1.3 amendment landed at `Spec_Harness_Runtime_v1.md` §14.5.
