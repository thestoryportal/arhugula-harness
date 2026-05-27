# Class 2 Fork Record — OD spec C-OD-04 §4.3 declared-but-not-emitted attributes

**Filed:** 2026-05-27 (post-v1.20 publication at HEAD `c326c03`; pre-substantive advisor-flagged routing per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 18th application context).
**Class:** 2 (in-execution operator decision; no defect — the spec declares the attributes at canonical tiers; production does not emit them; the gap is policy-axis, not architectural-defect-axis).
**Status:** RATIFIED-AND-APPLIED 2026-05-27 — Path A ratified by operator + applied at production via single-arc emission widening. Co-published this session: `llm_dispatch.py` static `_PROVIDER_SERVER_ADDRESS` + `_PROVIDER_SERVER_PORT` maps for anthropic / openai + `_parse_ollama_host` helper threading `RuntimeConfig.ollama_host` per advisor 2026-05-27 correction to fork §3 static-map framing (ollama-specific: static `localhost` would be a factual lie in telemetry when operator binds a remote daemon; OTel Conditionally Required "If `server.address` is set" gating licenses skipping emission when value unknown); `RuntimeLLMDispatcher.ollama_host: str | None = None` new field; `materialize_llm_dispatcher_stage` kwarg threading; bootstrap stage 5 wire-up at `stage_5_loop_init.py:138`; 3 NEW span attributes emitted at `llm_dispatch.py:343-360` (`gen_ai.conversation.id` from `step_context.workflow_id` per HIERARCHY_CORRELATION_KEY constant; `server.address` per provider; `server.port` gated on `server.address`); 7 NEW tests at `test_lifecycle_llm_dispatch.py` covering `gen_ai.conversation.id` sourcing + hosted-provider static emission + ollama 4-case matrix (unset, localhost full URL, remote URL, host-only-no-port). 1091/1091 harness-runtime tests pass (was 1084 + 4 skipped; +7 new). Pyright clean at `llm_dispatch.py` (0 errors). Closes v1.20 §"Adjacent observations" (f)+(g) as CLOSED-via-Path-A-production-emission. ZERO spec change owed per fork §3 framing — v1.20 §4.3 already declares the tiers; production catches up to spec. **Posture precedent established: declared at canonical OTel tiers ⇒ emitted at production.** Symmetric with v1.16 Tension 004 D-2 + D-3 re-litigation framing (harness emits ≥ OTel Conditionally Required floor).
**Surfaced by:** v1.20 §"Adjacent observations" (f)+(g); pre-classified Class 2 routing target at v1.19 § publication; advisor diagnosis 2026-05-27 (this session) — only carries of the 8 v1.20-tracked findings that point at real spec/production divergence; all others are monitors / upstream / informational.

---

## 1. The decision

OD spec v1.20 §C-OD-04 §4.3 declares 3 attributes at non-empty tier-classifications:

| Attribute | Tier (v1.20 §4.3) | OTel 1.41.0 Requirement Level |
|---|---|---|
| `gen_ai.conversation.id` | Conditionally Required (per v1.19 §1.1 redistribution) | Conditionally Required "when available" |
| `server.port` | Conditionally Required (per v1.19 §1.1 redistribution) | Conditionally Required "If `server.address` is set" |
| `server.address` | Recommended (Development) | Recommended |

**Production emission state at HEAD `c326c03`** (grep verified this session):

```
$ grep -rn "set_attribute.*\(gen_ai.conversation.id\|server.port\|server.address\)" harness-{runtime,od,cp,as,is,core,cxa}/src
# returns: zero matches
```

Declared at OD canonical tier-table (`harness-od/src/harness_od/otel_genai_base.py:163-173`); declared at attribute-class enforcement (`harness-od/src/harness_od/attribute_class_enforcement.py:70`); declared at content-structure-discipline allowlist (`harness-od/src/harness_od/content_structure_discipline.py:86-91`). NEVER emitted at any production span site.

The decision is policy: **do these attributes route to (Path A) "emit at production to close the spec/code gap" or (Path B) "downgrade tier classification to reflect reality" or (Path C) "document harness-stricter-than-OTel posture explicitly"?** All three are conformant per OTel "emit-more-often-than-Conditionally-Required is fine" framing — the question is which posture OD-axis canonically takes.

---

## 2. What's actually missing at production

Current state (verified 2026-05-27 at `c326c03`):

| Surface | Current state | Gap to emission |
|---|---|---|
| `harness-runtime/.../lifecycle/llm_dispatch.py:341-342` | Emits 3 Required (Stable) attrs (`gen_ai.provider.name`, `gen_ai.operation.name`, `gen_ai.request.model`) at every GenAI span | No `set_attribute` calls for the 3 Conditionally Required / Recommended attrs |
| `gen_ai.conversation.id` source | `WorkflowManifestEntry.workflow_id` exists; `StepExecutionContext.workflow_id` exists (per CP spec v1.12 §25.2.1 9th-field absorption 2026-05-24); not currently threaded into LLM dispatch span emission | Thread `workflow_id` from driver → dispatcher → span emission; the data is in scope |
| `server.address` source | Provider base URLs known per provider (Anthropic = `api.anthropic.com`; OpenAI = `api.openai.com`; Ollama = configurable, default `localhost`) | Static map at dispatcher; trivial |
| `server.port` source | Standard per provider (443 for hosted; configurable for Ollama) | Same static map; emit only when `server.address` is set, per OTel Conditionally Required rule |

Net: data sources for all 3 attributes exist at production; no infrastructure is missing. The gap is at the emission site, not at the data layer.

---

## 3. The three sub-paths

### Path A — Emit at production (close spec/code gap by widening emission)

**Shape.** Extend `harness-runtime/.../lifecycle/llm_dispatch.py` GenAI span emission from 3 attrs → 6 attrs. Add `_PROVIDER_SERVER_ADDRESS` + `_PROVIDER_SERVER_PORT` per-provider static maps. Thread `workflow_id` from `StepExecutionContext` through `attribute_llm_dispatch_cost(...)` (or sibling) into the span emission site. Co-publish helper update + tests.

**Scope of work.**

- Add static maps at `llm_dispatch.py` for `server.address` + `server.port` per provider key.
- Widen span emission to 6 `set_attribute` calls.
- Thread `workflow_id` from `StepExecutionContext` → dispatcher kwarg → span emission (likely already passes through; needs verification).
- Update helper carrier expectations at `harness-od/src/harness_od/otel_genai_base.py` test fixture (no Pydantic change; helper already declares the attributes).
- Add ~6-8 new tests at `test_llm_dispatch.py` verifying emission of each new attribute per provider + Conditionally Required gating logic.

**Spec change owed.** None — v1.20 §4.3 already declares the tiers; production catches up to spec.

**Effort estimate.** Small: ~3-5 commits across 1 session. Realistic at CC pace: 30-60 min.

**Retirements unlocked.** None directly — but closes the v1.20 (f)+(g) carry. Removes the "declared-but-not-emitted" divergence pattern from the workspace pattern catalogue.

**Risk.** Low. The data sources exist. The Conditionally Required emission gating is straightforward (emit when value is non-None). No new infrastructure.

**Architectural ramifications.** Establishes a posture: "OD-axis spec is the authority; production conforms to spec." Sets precedent for future spec-declared-but-not-emitted findings — they get closed by widening emission.

### Path B — Downgrade tier classification (close spec/code gap by narrowing spec)

**Shape.** Amend OD spec v1.20 → v1.21 §C-OD-04 §4.3 to move the 3 attributes from Conditionally Required / Recommended → Opt-In (or remove from declared set entirely). Reflects production reality: harness chose not to emit them, so they should not be declared at non-Opt-In tiers.

**Scope of work.**

- New OD spec v1.21 delta with NEW §1 canonical-reading amendment table redistributing the 3 attributes.
- Helper update at `otel_genai_base.py` — `BASE_LAYER_ATTRIBUTES` set re-tiers entries.
- Helper test re-shape (cardinality refresh).
- Workspace `CLAUDE.md` OD spec row v1.20 → v1.21 bump.
- Co-publish with U-OD-04 plan AC adjustment if cardinality test breaks.

**Spec change owed.** Substantive (tier redistribution; same shape as v1.19 §1.1 amendment).

**Effort estimate.** Medium: ~3-5 commits across 1 session. Realistic at CC pace: 30-45 min.

**Retirements unlocked.** None — closes carry by tier-redistribution.

**Risk.** Low. Same shape as v1.19; established pattern.

**Architectural ramifications.** Establishes a posture: "Production reality is the authority; spec conforms to production." Sets precedent: future declared-but-not-emitted findings get closed by downgrading the spec. **This is structurally opposed to Path A.** The choice between A and B is a one-time precedent-setting decision for OD axis posture.

### Path C — Document harness-stricter-than-OTel posture (no behavior change)

**Shape.** Amend OD spec v1.20 → v1.21 §C-OD-04 §4.3 to add explicit prose acknowledging the declared-but-not-emitted divergence as policy posture (e.g., "OD spec declares the canonical OTel tier classification; production emission is governed independently at OD plan AC #4 emission policy; the declared-vs-emitted gap is documented design choice"). Keep tiers at canonical OTel classifications; do not change emission.

**Scope of work.**

- Minor OD spec v1.20 → v1.21 delta with NEW prose footer at §4.3 or §4.5.
- Workspace `CLAUDE.md` OD spec row bump.
- No helper change; no test change.

**Spec change owed.** Minor (prose addition; no contract / tier / cardinality change).

**Effort estimate.** Tiny: ~1-2 commits across 1 session. Realistic at CC pace: 10-15 min.

**Retirements unlocked.** None — does not close (f)+(g); merely documents the divergence as accepted policy.

**Risk.** None.

**Architectural ramifications.** Punts the precedent question. Documents the gap as accepted-policy without choosing A or B. **This is the "neither" path** — the carries become "documented-accepted-divergence" rather than "open-divergence", which is a softer disposition than CLOSED.

### Path W (alternative) — Defer; preserve carries verbatim

**Shape.** No spec / production change. The carries at v1.20 §"Adjacent observations" (f)+(g) remain verbatim at v1.21, v1.22, etc. Future operator-discretion arc reopens.

**When to pick.** If the routing decision is not yet ready, or if other arcs are higher priority. Status remains OPEN per this fork doc.

---

## 4. Recommendation

**Assistant-level discriminator analysis** (non-binding; operator decides):

The choice between Path A and Path B is precedent-setting for OD-axis posture across the workspace. Workspace history suggests Path A precedent at one historical arc (the v1.16 Tension 004 D-2 + D-3 re-litigation was Path-A-shaped: spec declared 9-operation enum + 4-tier table per OTel 1.41.0 archived text; production conformed via helper carrier expansion). The v1.16 framing was explicitly "mirror-OTel" — and the harness emitted MORE often than OTel's Conditionally Required floor (stricter posture).

By symmetry with v1.16, Path A maintains posture consistency: declared at canonical OTel tiers ⇒ emitted at production. Path B reverses the v1.16 posture (declared at canonical OTel tiers ⇒ NOT emitted ⇒ tier downgraded retroactively).

Path C is the least-substance move. It does not close the divergence; it documents it. Workspace pattern catalogue would gain a NEW disposition shape: "documented-accepted-divergence." That's a new species. Given the FOURTH species of stale-carry was just catalogued at v1.18 §5 two days ago, adding a FIFTH species this fast may signal lineage-extension-for-its-own-sake rather than substantive resolution.

**Tentative recommendation: Path A** for posture consistency with v1.16 + tractable scope + clean closure of the v1.20 (f)+(g) carries + ZERO new species in the pattern catalogue.

**Defer to operator.** The precedent-setting nature of the A-vs-B choice is operator-owned. Path A vs B is not a technical defect routing; it is an architectural posture decision about which axis (spec or production) is the canonical authority when they disagree.

---

## 5. Cross-axis cascade

ZERO at the spec semantics layer for any path:

- AS spec: no §15.x / §14.x reference to `gen_ai.conversation.id` / `server.*` (verified via grep).
- CP spec: no §25.x reference; `StepExecutionContext.workflow_id` exists at §25.2.1 (per v1.12 9th-field absorption) but is not currently consumed for span attribute emission.
- CXA: no edge at any §2.3.x bucket for these attributes; they are OD-axis canonical attributes per §C-OD-04 ownership.
- ADR-D6 §1.2: 12-namespace OTel schema; `gen_ai.*` namespace is OD-canonical; no ADR layer change.

Path A cross-axis surface: CP spec may benefit from a `StepExecutionContext`-cite footer note at OD spec §C-OD-04 §4.3 (`gen_ai.conversation.id` data source). NOT a contract amendment. NOT a cross-axis edge. Doc-hygiene only.

---

## 6. Filing footer

| Field | Value |
|---|---|
| Filed | 2026-05-27 at HEAD `c326c03` (post-v1.20 publication) |
| Authority anchor | OD spec v1.20 §"Adjacent observations" (f)+(g) self-classification "Class 2 in-execution operator-discretion routing target"; OTel GenAI semantic conventions 1.41.0 archived text at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` |
| Pre-substantive empirical verification | Production grep at HEAD `c326c03` for `set_attribute.*\(gen_ai.conversation.id\|server.port\|server.address\)` returns ZERO matches across all harness-*/src — divergence confirmed genuine at current HEAD per v1.18 §5 strengthened discipline (third prospective application this session) |
| Routing target | Operator-discretion at next session; expected ratification shape: Path letter + arc-opening authorization |
| Successor disposition | Spec v1.20 (f)+(g) carries remain OPEN at v1.21+ until ratification. Removal from "Adjacent observations" carry list occurs at the v1.X delta that applies the ratified path. |
| Advisor application | 19th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — advisor flagged at session opening that (f)+(g) are the only substantive carries of the 8 v1.20-tracked; that closing them silently = silent absorption per CLAUDE.md §4.3 worst-failure-mode; that the substantive routing is "surface as Class 2" not "close in OD spec arc on assistant authority." Recommendation taken: file this fork doc rather than open another zero-behavior-change OD spec delta. |
| Pattern catalogue | Class 2 fork docs are rare (this is the third in workspace history alongside `class_2_fork_tool_invocation_composer_scope.md` 2026-05-20 + `class_2_tension_phase_2_session_5_harness_context_axis_type_mapping.md`). Pattern: when a spec-declared surface lacks production emission AND the spec is itself the canonical authority for the tier classification, the routing is "Class 2 operator decision on posture" rather than "Class 1 spec-vs-implementation halt." This is the second instance of that pattern after the tool-invocation composer scope decision (`class_2_fork_tool_invocation_composer_scope.md`). |
