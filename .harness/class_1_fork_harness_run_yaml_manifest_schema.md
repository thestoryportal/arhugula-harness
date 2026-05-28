# Class 1 Fork — `harness run` YAML/TOML Workflow Manifest Schema (SF-1)

**Filed:** 2026-05-28 (Phase 7 sub-phase 7b post-Gate-G1-ratification arc).
**Class:** 1 — NEW H_T design surface under X-AL-3. Operator-ratified at Gate G1 (en bloc, 2026-05-28) that there will be a schema; this fork authors the schema body for separate ratification per Phase 2a design substrate §10 Gate G2.
**Predecessor:** `.harness/phase_2_track_b_design_substrate.md` v1.1 §3.3 + §5 SF-1 declaration.
**Status:** PROPOSING — operator ratifies the schema body before SF-1 closes + Phase 2b U-RT-104 (manifest loader) implementation opens.
**Sub-questions resolved en bloc at G1:** Q-B1=(a) step-list / Q-B2=(c) YAML+TOML both / Q-B3=(a) explicit version / Q-B4=(a) closed schema / Q-H=(b) strictyaml.

---

## §1 Scope

This fork authors the **YAML/TOML workflow manifest schema** that `harness run <workflow-file>` parses into a `WorkflowObject` Protocol-satisfying instance per the existing C-RT-08 surface. The schema is a NEW H_T design surface (X-AL-3 — no silent extension at Phase 7); ratification is REQUIRED before Phase 2b U-RT-104 + U-RT-105 implementation opens.

**Out of scope (sibling forks / future arcs):**
- Daemon protocol (Q-A=α at G1 forecloses SF-2; FastMCP server is the daemon)
- CLI flag library + argparse details (operator-discretion at impl arc per Q-I=(c) Typer recommendation)
- Schema versioning beyond v1 (forward-compat — versions ≥2 are future arcs)

---

## §2 Authority anchors

| Anchor | Source | Constraint |
|---|---|---|
| **C-RT-08 `WorkflowObject` Protocol** | runtime spec §8 + `harness-runtime/src/harness_runtime/api.py:67` | 5 read-only properties: `workflow_id`, `workload_class`, `manifest_entry`, `steps`, `default_model_binding`. Schema MUST project to all 5. |
| **C-CP-06 `WorkflowManifestEntry`** | CP spec v1.20 §6.1 + `workflow_manifest_entry.py` | 12 mandatory + optional fields (workflow_id, workload_class, persona_tier mandatory; 9 with defaults). Schema MUST project to required fields; MAY omit optional fields (loader supplies Pydantic defaults). |
| **C-CP-25 §25.2 `WorkflowStep`** | CP spec v1.6 §25.2 + `workflow_driver_types.py` | 3 fields: `step_id: StepID`, `step_kind: StepKind`, `step_payload: Mapping[str, Any]`. `step_payload` opaque to driver per §25.3.3 step-body-opaque invariant. |
| **ADR-F1 v1.2 mandatory fields** | ADR-F1 §1.2 | `workload_class` + `persona_tier` mandatory — no defaults. Schema MUST require these. |
| **Pydantic v2 `ConfigDict(extra="forbid")`** | All carrier classes | Closed schema at carrier layer. Q-B4=(a) ratification at G1 mirrors this at YAML/TOML loader layer. |
| **Workspace stack discipline** | Workspace `CLAUDE.md` §3.1 | Python 3.12+ / Pydantic v2 / hand-rolled where no existing-stack solution meets AC. strictyaml + tomllib (stdlib) chosen per Q-H + Q-B2. |

---

## §3 Schema body — `WorkflowManifest` v1

### §3.1 Top-level shape

```yaml
# harness workflow manifest v1
version: 1                    # REQUIRED — Q-B3=(a) explicit version

workflow:                     # REQUIRED — projects to WorkflowObject fields
  workflow_id: string         # REQUIRED — stable identity
  workload_class: enum        # REQUIRED — ADR-F1 v1.2 mandatory
  persona_tier: enum          # REQUIRED — ADR-F1 v1.2 mandatory

  # Optional WorkflowManifestEntry fields (loader supplies Pydantic defaults if absent)
  engine_class: enum          # OPTIONAL — defaults per CP spec v1.6 §6.1
  topology_pattern: enum      # OPTIONAL — defaults to SINGLE_THREADED_LINEAR
  entry_version: integer      # OPTIONAL — defaults to 1
  default_gate_level: enum    # OPTIONAL — defaults to GateLevel.AUTO per CP spec v1.20 §6.1.Y

  # Optional collections (empty tuple defaults)
  layer_budgets: list         # OPTIONAL — list of LayerBudget shapes
  fallback_chain: object      # OPTIONAL — FallbackChain shape; default empty
  hitl_placements: list       # OPTIONAL — list of HITLPlacement shapes
  sub_agent_briefs: list      # OPTIONAL — for fan-out patterns; default null
  per_step_overrides: object  # OPTIONAL — map of StepID → StepOverride

default_model_binding:        # REQUIRED — projects to WorkflowObject.default_model_binding
  provider: string            # REQUIRED — e.g. "anthropic", "openai", "ollama"
  model: string               # REQUIRED — e.g. "claude-opus-4-7"

steps:                        # REQUIRED — non-empty list of WorkflowStep
  - step_id: string           # REQUIRED — unique within workflow
    step_kind: enum            # REQUIRED — StepKind enum member (INFERENCE_STEP, TOOL_STEP, etc.)
    step_payload: object       # REQUIRED — opaque mapping; driver-discretion per C-CP-25 §25.3.3
```

### §3.2 TOML equivalent

```toml
version = 1

[workflow]
workflow_id = "string"
workload_class = "enum"
persona_tier = "enum"
engine_class = "enum"         # optional
topology_pattern = "enum"     # optional
entry_version = 1             # optional
default_gate_level = "enum"   # optional

[default_model_binding]
provider = "string"
model = "string"

[[steps]]
step_id = "string"
step_kind = "enum"
step_payload = { key = "value" }  # opaque mapping
```

### §3.3 Field-by-field projection contract

| YAML/TOML field | Projects to | Validation rule | Default |
|---|---|---|---|
| `version` | (loader-internal) | MUST equal `1`; loader raises `UnsupportedManifestVersionError` for other values | (none — required) |
| `workflow.workflow_id` | `WorkflowObject.workflow_id` + `WorkflowManifestEntry.workflow_id` | non-empty string | (none — required) |
| `workflow.workload_class` | `WorkflowObject.workload_class` + `WorkflowManifestEntry.workload_class` | MUST be valid `WorkloadClass` enum member (StrEnum value) | (none — required per ADR-F1) |
| `workflow.persona_tier` | `WorkflowManifestEntry.persona_tier` | MUST be valid `PersonaTier` enum member | (none — required per ADR-F1) |
| `workflow.engine_class` | `WorkflowManifestEntry.engine_class` | MUST be valid `EngineClass` enum member; admissibility verified against U-CP-16 candidate mapping | (none — caller-supplied; no Pydantic default at v1.20 carrier) |
| `workflow.topology_pattern` | `WorkflowManifestEntry.topology_pattern` | MUST be valid `TopologyPattern` enum member; admissibility verified against U-CP-22 `is_topology_permitted` | (none — caller-supplied) |
| `workflow.entry_version` | `WorkflowManifestEntry.entry_version` | positive integer | `1` per CP plan v2.12 §2.2 (added 2026-05-19) |
| `workflow.default_gate_level` | `WorkflowManifestEntry.default_gate_level` | MUST be valid `GateLevel` enum member OR null | `None` (loader passes through; driver uses `GateLevel.AUTO`) |
| `workflow.layer_budgets` | `WorkflowManifestEntry.layer_budgets` | list of `LayerBudget` shapes; each item a closed-schema object | `()` empty tuple |
| `workflow.fallback_chain` | `WorkflowManifestEntry.fallback_chain` | `FallbackChain` shape; closed-schema object | `FallbackChain.default()` (per CP carrier default) |
| `workflow.hitl_placements` | `WorkflowManifestEntry.hitl_placements` | list of `HITLPlacement` shapes; placement-kind ordering enforced per U-CP-38 | `()` empty tuple |
| `workflow.sub_agent_briefs` | `WorkflowManifestEntry.sub_agent_briefs` | list of `SubAgentBrief` shapes OR null | `None` |
| `workflow.per_step_overrides` | `WorkflowManifestEntry.per_step_overrides` | map of step_id (string) → `StepOverride` shape | `{}` empty dict |
| `default_model_binding.provider` | `WorkflowObject.default_model_binding.provider` | non-empty string; validated against routing-manifest registered providers | (none — required) |
| `default_model_binding.model` | `WorkflowObject.default_model_binding.model` | non-empty string | (none — required) |
| `steps[].step_id` | `WorkflowStep.step_id` | non-empty string; unique within `steps[]` (loader-enforced) | (none — required) |
| `steps[].step_kind` | `WorkflowStep.step_kind` | MUST be valid `StepKind` enum member | (none — required) |
| `steps[].step_payload` | `WorkflowStep.step_payload` | opaque mapping (any keys/values); MUST be a JSON-serializable object | (none — required; empty `{}` allowed) |

---

## §4 Loader contract (`WorkflowManifestLoader`)

### §4.1 Public surface

```python
# harness_runtime.lifecycle.workflow_manifest_loader

from pathlib import Path
from harness_runtime.api import WorkflowObject

class WorkflowManifestLoader:
    """Loads a YAML or TOML manifest file into a WorkflowObject (C-RT-08 Protocol).

    File extension dispatch (Q-B2=(c) at G1):
    - `.yaml` / `.yml` → strictyaml.load (Q-H=(b))
    - `.toml`           → tomllib.load (stdlib)
    - other            → UnsupportedManifestFormatError

    Validation timing (Q-N=(a) at G1): EAGER — all schema + enum + uniqueness
    + admissibility checks performed at .load() time; .load() either returns a
    valid WorkflowObject or raises a typed exception.
    """

    @classmethod
    def load(cls, path: Path) -> WorkflowObject: ...
```

### §4.2 Typed exception taxonomy

| Exception | Trigger | Routing |
|---|---|---|
| `UnsupportedManifestFormatError` | File extension not in `{.yaml, .yml, .toml}` | CLI exit code 2 |
| `UnsupportedManifestVersionError` | `version` field absent OR not equal to 1 | CLI exit code 2 |
| `ManifestParseError` | YAML/TOML syntax error; strictyaml/tomllib raise | CLI exit code 2 |
| `ManifestSchemaError` | Required field missing, unknown field present, type mismatch | CLI exit code 2 |
| `ManifestEnumValueError` | Enum field value not in target StrEnum | CLI exit code 2 |
| `ManifestStepIDCollisionError` | Two `steps[].step_id` values equal | CLI exit code 2 |
| `ManifestAdmissibilityError` | `(workload_class, engine_class)` not in U-CP-16 candidate mapping OR `topology_pattern` not in U-CP-22 admissibility | CLI exit code 2 |

All exceptions inherit from `WorkflowManifestLoadError` base for catch-all handling at CLI layer.

### §4.3 Invariants

1. **Closed schema (Q-B4=(a)).** Unknown top-level fields OR unknown nested fields raise `ManifestSchemaError`. NO silent passthrough.
2. **Eager validation (Q-N=(a)).** All checks at `.load()`; no deferred-validation patterns. A `.load()` that returns a value means the value satisfies the WorkflowObject Protocol byte-exact.
3. **Enum-value strictness.** Enum fields parse via target StrEnum's `__class__(value)` constructor — case-sensitive; rejects implicit type coercion (strictyaml's design intent per Q-H=(b)).
4. **Step-ID uniqueness.** `steps[].step_id` set MUST have cardinality equal to `len(steps)`.
5. **Path-class neutrality.** Manifest file path is operator-supplied; loader does NOT consult IS PATH_CLASS_REGISTRY (manifest is workspace-external dev artifact, not state-ledger content).
6. **Default-supplying discipline.** Optional fields absent from manifest are passed through as `None` to `WorkflowManifestEntry` constructor; Pydantic carrier defaults apply OR validation rejects per carrier class discipline (no loader-side default-supplying that bypasses Pydantic).
7. **Idempotency.** `WorkflowManifestLoader.load(p)` is deterministic; repeated invocations on the same file return equal `WorkflowObject` instances (frozen Pydantic models satisfy `__eq__`).

---

## §5 Open sub-decisions (operator ratifies before SF-1 closes)

These are NOT en-bloc-ratified at G1 because they require schema-level architectural decisions not surfaced at design substrate §6 Q-set.

| Q | Question | Recommendation |
|---|---|---|
| **Q-S1** | Should `step_payload` be schema-validated per-`step_kind` (e.g., INFERENCE_STEP requires `prompt:` field; TOOL_STEP requires `tool_name:`)? OR remain fully opaque per C-CP-25 §25.3.3? | **Opaque** — preserve C-CP-25 §25.3.3 step-body-opaque invariant; per-step-kind validation lives at the step-kind dispatcher (runtime layer), not the manifest loader. Lowers Track B coupling to per-axis schemas. |
| **Q-S2** | YAML format: support multi-document manifests (multiple `---`-separated workflows per file) at v1? | **No** — single workflow per file at v1. Multi-document is iteration-2 (composes with `harness run --workflow=<id>` selector). |
| **Q-S3** | TOML/YAML format equivalence: enforce both parsers produce byte-equal `WorkflowObject` for equivalent inputs (round-trip property)? | **Yes** — invariant 8 added. Equivalent inputs ⇒ equivalent `WorkflowObject`. Test via `test_yaml_toml_equivalent_inputs_produce_equivalent_workflow`. |
| **Q-S4** | Schema documentation: ship a JSON Schema alongside `WorkflowManifest` v1 for IDE auto-completion? | **No at v1** — premature. Operator-facing docs live at `docs/workflow_manifest_schema.md` (markdown) at Phase 2b. JSON Schema is iteration-2. |
| **Q-S5** | Environment-variable interpolation: support `${VAR_NAME}` in string fields (e.g., `provider: ${LLM_PROVIDER}`)? | **No at v1** — operator can use `harness run --provider=...` CLI flag layer per Q-I + A4 layered config. Interpolation is config-layer concern, not manifest-layer. |
| **Q-S6** | `step_payload` JSON-serializability check: enforce at load time via `json.dumps(payload)` round-trip? | **Yes** — invariant 9 added. Closes potential silent-Pydantic-coercion bugs (e.g., `datetime` objects in payload). Eager validation per Q-N. |

---

## §6 Spec extension sites (deliverables at Gate G4)

| Spec | Section | Amendment | Author |
|---|---|---|---|
| `Spec_Harness_Runtime_v1.md` v1.34 → v1.35 | NEW §14.N C-RT-NN `WorkflowManifestLoader` | Authors §4 loader contract + §4.2 typed exception taxonomy + §4.3 invariants 1-9 (post-Q-S resolution) | spec-writer skill |
| Runtime plan v2.30 → v2.31 | NEW U-RT-104 + U-RT-105 (per design substrate §7 sketch) | Decomposes loader implementation: U-RT-104 = strictyaml/tomllib parsers + schema validation; U-RT-105 = projection to WorkflowObject | implementation-planner skill |

---

## §7 Phase 2b implementation deliverables (post-Gate G6)

| Deliverable | Location | Author |
|---|---|---|
| `WorkflowManifestLoader` class | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` | U-RT-104 |
| Typed exceptions | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` (same module) | U-RT-104 |
| `WorkflowManifest` Pydantic carrier (loader-internal intermediate) | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` | U-RT-104 |
| `WorkflowObject` projection helpers | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` | U-RT-105 |
| Unit tests (~30: per-field validation + per-exception trigger + round-trip YAML↔TOML) | `harness-runtime/tests/test_workflow_manifest_loader.py` | U-RT-104 + U-RT-105 |
| Operator-facing docs (schema reference + examples) | `docs/workflow_manifest_schema.md` | Phase 2b doc arc |
| Example manifests (3-5 per workload class) | `examples/workflows/*.yaml` + `*.toml` | Phase 2b doc arc |
| Dep additions | `harness-runtime/pyproject.toml` | Phase 2b: `strictyaml>=1.7` + (tomllib is stdlib at Python 3.11+) |

---

## §8 Cross-axis cascade verification

**ZERO cross-axis cascade.** Verified:

| Artifact | Touched? | Reason |
|---|---|---|
| CP spec / plan | NO | Schema CONSUMES CP carriers (WorkflowManifestEntry, WorkflowStep) via projection; ZERO mutation of CP contracts. Enum admissibility checks call existing U-CP-16 + U-CP-22 helpers; no new CP surface. |
| AS spec / plan | NO | Schema does NOT touch AS surface (tools/MCP/sandbox/skills). Per-tool config lives at `RuntimeConfig.routing_manifest` per C-RT-03; not at workflow manifest. |
| OD spec / plan | NO | Schema does NOT touch OD surface (HITL/audit/cost/observability). |
| IS spec / plan | NO | Per §4.3 invariant 5 — manifest file is workspace-external; no PATH_CLASS_REGISTRY. |
| CXA | NO | Intra-runtime-axis schema; no typed cross-axis edge added. |
| ADR-F1 v1.2 | NO | Schema PROJECTS to ADR-F1-mandated `workload_class` + `persona_tier`; ZERO ADR amendment. |
| Other ADRs | NO | No F-class architectural decision touched. |
| ADD v1.3 / PRD v1.1 | NO | Observable behavior + architectural overview unchanged. |
| Workspace `CLAUDE.md` | YES (post-impl) | §2.3 runtime spec row + §2.4 runtime plan row bumps at v1.35 + v2.31 publication. |

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_harness_run_yaml_manifest_schema.md` |
| Class | 1 — NEW H_T design surface under X-AL-3 |
| Sub-fork ID | SF-1 (per design substrate §5) |
| Status | PROPOSING |
| Predecessor | `.harness/phase_2_track_b_design_substrate.md` v1.1 §3.3 + §5 SF-1 declaration |
| Successor | Operator Q-S ratification (Q-S1 through Q-S6) → spec/plan amendment → U-RT-104 + U-RT-105 implementation |
| Authority | Gate G1 en-bloc ratification (2026-05-28) for Q-B1/B2/B3/B4/H/N; Q-S1-S6 ratification owed at G2 close |
| Cross-axis cascade | ZERO — verified §8 |
| Foreclosure note | SF-2 (daemon protocol) foreclosed at G1 per Q-A=(α) — FastMCP server is daemon; ZERO new IPC contract |
