# Class 1 Fork — YAML manifest loader `step_payload` scalar coercion gap

**Status:** ✅ APPLIED-AS-READING-A (operator-ratified 2026-05-29; Q-set Q1=A + Q2=α + Q3→routes-to-PR-#80 + Q4=b)

**Ratification record (2026-05-29):**

| Q | Decision | Disposition at apply arc |
|---|---|---|
| Q1 (loader fix scope) | **A — Replace `strictyaml.dirty_load` with `pyyaml.safe_load` via thin StrictSafeLoader subclass** | NEW `harness-runtime/.../lifecycle/strict_safe_loader.py` (78 lines; 4 strictness features preserved: duplicate-key, non-empty-flow-style ban, anchor/alias ban, native scalar typing). `workflow_manifest_loader.py:_parse_yaml` updated; `_coerce_int_fields` retired; `_check_version` simplified. `harness-runtime/pyproject.toml`: `strictyaml>=1.7` retired; `pyyaml>=6.0` declared. Spec v1.38 → v1.39 + plan v2.40 → v2.41 absorbed at apply PR. |
| Q2 (minimal.yaml fixture fix) | **α — Switch to `pipeline-automation` + `single-threaded-linear`** | Both `minimal.yaml` AND sibling `minimal.toml` updated for fixture-pair equivalence at the v1.39 typed-scalar layer. `step_payload: { max_tokens: 8 }` exercises the native-int code path post-Reading-A apply. Probe reproduction confirmed at integration test level. |
| Q3 (loader admissibility gate) | **→ routes-to-PR-#80** | Sibling fork resolution; closed as ✅ APPLIED-AS-READING-A at PR #81 (apply for filing PR #80; spec v1.37 → v1.38). Both PRs required for operator-facing YAML CLI to ship runnable; PR #79 apply stacks on PR #80 apply per advisor-recommended sequential-rollback-boundary. |
| Q4 (Q-S3 invariant re-anchoring) | **b — Land Q1 fix such that §14.19.4 invariant 8 becomes empirically true** | Spec v1.39 §14.19.4 invariant 8 canonical-reading amendment confirms operational truth at the typed-scalar layer. Pre-v1.39 invariant was vacuous for typed `step_payload`; v1.39 closes the asymmetry. |
| Q-H=b re-litigation (G2 ratification) | **Re-litigated and superseded at v1.39** | Q-H=b chose strictyaml-via-strictness at Phase 2a G2 2026-05-28. v1.39 preserves the strictness motivation via 78-line SafeLoader subclass; gains YAML 1.1 native scalar typing. The strictness features (duplicate-key, no-flow-style, no-anchors/aliases) are exhaustively preserved at the shim. The scalar-coercion consequence Q-H=b did NOT consider is closed at v1.39. |
| Cross-axis cascade | **NONE** | Runtime spec v1.39 + runtime plan v2.41 + production code + tests + workspace `CLAUDE.md` §2.3 + §2.4 row bumps + clearance marker at `.harness/clearance/Spec_Harness_Runtime-v1_39-cleared-2026-05-29.md`. NO CP / AS / OD / IS / CXA / ADR / ADD / PRD touch. Target_Stack_Commitment_v1 §5.1 PRESERVED VERBATIM (operates at framework-pull-discipline layer; YAML parser implementation is intra-runtime-axis). |

**Apply arc:** separate apply PR landing alongside this filing PR per workspace precedent at PR #66 apply-after-filing-#65 + PR #81 apply-after-filing-#80. Stacks on PR #81 (sibling PR #80 apply) per advisor-recommended sequential-rollback-boundary; PR #80 apply lands first (smaller blast radius), PR #79 apply lands second (parser replacement).

**Filed at:** 2026-05-29

**Filer:** use-the-product probe (post-PR-#78 session)

**Surfaced by:** End-to-end `harness run` probe against `harness-runtime/tests/integration/fixtures/track_b/minimal.yaml`. Probe goal was to observe what's load-bearing vs ceremonially closed at HEAD. Probe drove through bootstrap stages 0-6 successfully, reached real Anthropic LLM dispatch, and ultimately got `status: completed` + `verify_chain status=valid` — but ONLY after switching from `.yaml` to `.toml` manifest. The YAML path was structurally blocked at LLM SDK boundary.

**Classification:** Class 1 (halt-execution; structural defect in advertised operator-facing CLI path per Phase 7 Meta-Architecture §7 X-AL-3 + Workflow §2.7.6 + Phase_7_Kickoff_Prompt.md §6). YAML manifest loading is canonicalized at runtime spec v1.35 §14.19 C-RT-30 + plan U-RT-104 as first-class operator surface; the gap blocks the documented happy path.

---

## §1 — The gap

`harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py:249` invokes `strictyaml.dirty_load(...)` to load YAML manifests. **`strictyaml.dirty_load` returns every scalar as `str` regardless of source form** — `max_tokens: 8` arrives as `"8"`, not `8`.

The loader coerces exactly TWO fields back to int at the boundary (`_coerce_int_fields` at `:324`):
- `version` (top-level)
- `workflow.entry_version`

Every other scalar — including everything inside `steps[*].step_payload` — is left as `str`. The docstring at `:328-330` makes this explicit:

> `version` was handled at `_check_version`. step_payload scalars stay opaque per AC #14.19.4 invariant 9 (JSON-serializability at U-RT-105).

The "JSON-serializability" invariant is a check, not a transformation. Strings ARE JSON-serializable; the invariant is satisfied trivially. But the LLM SDK at the dispatch boundary needs **native types** — `client.messages.create(max_tokens=8, ...)` expects `int`, not `str`.

### Empirical reproduction at HEAD (probe trace, 2026-05-29)

Bootstrap-eligible `minimal.yaml` modified to use `pipeline-automation` workload + `single-threaded-linear` topology + `max_tokens: 8` payload:

```
workflow_id: track-b-minimal
... (full bootstrap completes; CP_CLIENTS validates Anthropic key against /v1/models 200 OK) ...
status: failed
detail: workflow execution returned status='failed' with fail_class='step-failure:
        RetryBreakerFallbackExhaustedError: RT-FAIL-FALLBACK-EXHAUSTED: fallback
        chain exhausted after candidate anthropic:claude-haiku-4-5 (chain
        traversal complete)'
```

Same workflow shape transcribed to `.toml` (tomllib preserves int types per `_build_carrier` boundary comment at `:316-317`):

```
status: completed
workflow: track-b-minimal
ledger: e9c26365ef7303e9a4dd424b95ca633f35a4d78117b7c91312f3ddb4878910fa
```

State-ledger persisted 2 entries (genesis + step row); `verify_chain` returned `status=valid`.

### Net consequence

**Operators cannot run any `inference-step` workflow via YAML manifest at HEAD.** The advertised first-class YAML support per runtime spec §14.19 + plan U-RT-104 is structurally broken for the primary happy path (LLM dispatch via Anthropic / OpenAI SDK, both of which require `int` `max_tokens`). TOML manifests work; YAML manifests don't.

The minimal.yaml fixture as shipped also exhibits two adjacent fixture-level defects independent of the loader (carried at §4 below); both must be fixed for YAML to ship operator-runnable examples regardless of resolution path chosen here.

---

## §2 — Readings

**Reading A — Loader-level fix: replace `strictyaml.dirty_load` with a YAML parser that preserves native scalar types.** Most natural candidate: `pyyaml.safe_load` (preserves int / float / bool from YAML scalar context per YAML 1.1/1.2 spec, same as TOML). Removes the boundary-coercion problem at its root.

Pros: closes the gap structurally; YAML and TOML reach the SDK with identical type shape; no `step_payload`-specific code path required.

Cons: loses strictyaml's specific safety features (duplicate-key detection, no-flow-style enforcement, typed schema-driven parsing). Per runtime spec v1.35 §14.19.4 invariant 4: "closed schema per Q-B4=a" — strictyaml was chosen at Phase 2a G2 ratification (operator Q-H=b) specifically because of its strictness. Replacing it requires re-litigating that decision OR layering a duplicate-key check on top of pyyaml. Strictness via schema (Reading B) is the principled alternative.

**Reading B — Loader-level fix: use `strictyaml.load(...)` with an explicit `Map`/`Seq` schema derived from `WorkflowManifest` Pydantic model.** strictyaml supports typed schemas that coerce scalars at parse time (`Int()`, `Float()`, `Bool()`, etc). Define a schema mirroring the `WorkflowManifest` shape; strictyaml coerces at load.

Pros: preserves strictyaml strictness commitment; types coerce at the YAML boundary, no post-load deep-walk needed. Aligns with runtime spec v1.35 §14.19.4 invariant 4 "closed schema" framing.

Cons: schema authoring + maintenance burden — `step_payload: dict[str, Any]` is unbounded by design (per `:140` field declaration + opaque-step-body invariant at C-CP-25 §25.3.3 step-body-opaque). strictyaml's `Any()` falls back to scalar→str. Authoring `step_payload`-specific schemas defeats the opacity. May need a hybrid: schema for the top-level + `Any()` for step_payload + post-load deep-coerce ONLY inside step_payload.

**Reading C — Loader-level fix: post-load deep-coerce step_payload via best-effort scalar inference.** Recursively walk `step_payload` post-`dirty_load`; attempt `int(s)` then `float(s)` then preserve `str`; recurse into `dict` / `list`. Preserves strictyaml choice for the manifest envelope; closes the gap inside step_payload only.

Pros: minimal blast radius — single function added at `_build_carrier`; opaque step_payload contract preserved at API surface (still `dict[str, Any]`); existing strictyaml strictness on the manifest envelope unchanged.

Cons: silent type corruption hazard when operator genuinely wants `"8"` as a string (e.g., an opaque identifier that happens to be numeric). Inference is irreversible at the boundary — once `"8"` → `8`, can't recover the source intent. Operators relying on string-typed identifiers in payload break silently.

**Reading D — Documentation-only: declare YAML manifests cannot carry typed scalars in `step_payload`; require operators to use TOML for any workflow with typed payload.** Update minimal.yaml fixture to use a step shape that doesn't need int coercion (e.g., string-only payload), OR retire minimal.yaml in favor of minimal.toml as the canonical example. Document the constraint at runtime spec §14.19 + harness CLI help text + project README.

Pros: zero code change; honest about the actual capability boundary; respects the strictyaml-via-Q-H=b ratification.

Cons: degrades the "YAML / TOML round-trip equivalence" claim at runtime spec v1.35 §14.19.4 invariant 8 (per Q-S3 ratification: "YAML and TOML manifests of equivalent content load identically"). YAML manifests cannot be equivalent to TOML manifests for the most common step shape (LLM dispatch). The Q-S3 invariant becomes vacuous for real workflows.

**Reading E — Hybrid: ship minimal.yaml fix immediately (string-only payload) as a stopgap; route the structural decision (A vs B vs C vs D) to a follow-on design-phase arc with proper Q-H= re-litigation + Q-S3 invariant re-anchoring.** Treats the loader behavior as deliberate (Q-H=b ratified strictyaml); treats the fixture defect as a separable concern; defers the structural question to a clearer scoping.

Pros: unblocks the documented happy path immediately for YAML readers; preserves design-phase decision discipline. Each arc has bounded scope.

Cons: leaves the structural gap open across an unbounded time horizon; the immediate-fix and the deferred-fix may diverge.

---

## §3 — Operator decisions

**Q1 — Scope reading.**

- (A) Loader fix via `pyyaml.safe_load` (replace strictyaml; re-litigate Q-H=b)
- (B) Loader fix via `strictyaml.load(...)` with schema (preserves strictyaml; honors Q-H=b)
- (C) Loader fix via post-load deep-coerce inside `step_payload` only (RECOMMENDED — minimal blast radius; preserves opacity contract; documents the silent-corruption hazard as a known tradeoff with operator-visible warning)
- (D) Documentation-only; YAML cannot carry typed payload
- (E) Hybrid — fixture fix now, structural decision deferred

**Q2 — `minimal.yaml` fixture fix (independent of Q1; fixture is broken regardless of loader resolution).** Per probe finding #7, the shipped `minimal.yaml` declares `workload_class: software-engineering` + `topology_pattern: evaluator-optimizer`. Both fail bootstrap: `evaluator-optimizer` is unmaterialized at C-CP-25 v1.4 MVP scope (only `SINGLE_THREADED_LINEAR` ships); and at the YAML loader's admissibility gate, `software-engineering` + `single-threaded-linear` is rejected (probe finding #14: YAML loader's admissibility check is stricter than runtime — the working integration test at `test_track_b_e2e.py::test_ac1_real_anthropic_single_step_succeeds` uses exactly this combo by bypassing the loader). Possible fixture fixes:

- (α) Switch fixture to `workload_class: pipeline-automation` + `topology_pattern: single-threaded-linear` (admissibility-OK combo; runs at MVP) — but the YAML scalar coercion gap still blocks `inference-step` with typed payload
- (β) Switch fixture to a `step_kind` that doesn't need typed payload (e.g., a fixture-tier no-op step that exists for shape testing only) — narrowest fix; doesn't exercise LLM dispatch
- (γ) Switch fixture to `.toml` extension; retire minimal.yaml entirely — most honest if Q1=D is chosen
- (δ) Drop minimal.yaml from `harness-runtime/tests/integration/fixtures/track_b/` since its existence implies operator-runnable example that doesn't exist at HEAD

**Q3 — YAML loader admissibility gate (probe finding #14, adjacent to but distinct from the scalar coercion gap).** The loader rejects `software-engineering` + `single-threaded-linear` per per-workload-class topology admissibility table at `harness-cp/src/harness_cp/per_workload_class_topology.py:91-99`. The runtime accepts it (verified at `test_ac1_real_anthropic_single_step_succeeds`). One of these two must be wrong:

- (i) Loader admissibility check is correct; integration test exploits an unintended bypass; fix the test
- (ii) Runtime acceptance is correct; loader admissibility check is over-strict; relax the loader (RECOMMENDED — runtime is the authority; admissibility table at MVP excludes the only materialized topology for `software-engineering`, making the workload structurally unrunnable per probe finding #6)
- (iii) Both are correct under different framings; document the loader's stricter check as a design-time guard distinct from runtime admissibility

**Q4 — Q-S3 invariant re-anchoring.** Runtime spec v1.35 §14.19.4 invariant 8 ("YAML and TOML manifests of equivalent content load identically") is empirically false at HEAD for any workflow with typed `step_payload` scalars. Either:

- (a) Amend §14.19.4 invariant 8 to acknowledge the scalar-coercion asymmetry (carve-out clause: "modulo step_payload scalar coercion per Q-H=b strictyaml choice")
- (b) Land Q1 fix (A/B/C) such that the invariant becomes true (RECOMMENDED if Q1 ∈ {A, B, C})
- (c) Document the invariant as forward-looking ("will hold post-§14.19.X amendment")

**Q5 — Cross-axis cascade.** None at v1.35 amendment per the §14.19.6 cross-axis-cascade-survey scope. Verified: no IS / AS / CP / OD / CXA / ADR cite of the loader's scalar coercion behavior beyond runtime spec internal references.

---

## §4 — Adjacent observations

### (a) Probe finding catalogue (17 findings; the load-bearing ones are Q1-eligible; the rest are scope-adjacent)

**Critical (Q1-eligible):**
- (16) strictyaml dirty_load stringifies all scalars
- (17) YAML manifests cannot reach successful LLM call at HEAD

**Structural / MVP-scope (informational; route separately):**
- (5) Only `SINGLE_THREADED_LINEAR` topology materialized at C-CP-25 v1.4 MVP
- (6) `software-engineering` workload's permitted topologies (`{EVALUATOR_OPTIMIZER, ORCHESTRATOR_WORKERS}`) are both unmaterialized at MVP → workload unrunnable via CLI
- (14) YAML loader's admissibility check stricter than runtime's

**UX / ergonomics (catalogued but bounded by Phase 7 MVP scope discipline):**
- (1) `--config` marked optional but `RuntimeConfig` has 4 no-default fields
- (2) Bootstrap requires 4 `PathBinding` entries even for workflows using none
- (3) Ollama daemon required by default; `ollama_optional=true` required to skip
- (4) `routing_manifest` default-factory docstring at `harness-runtime/src/harness_runtime/types.py:1170-76` claims empty is "sufficient for stage 3b" — runtime rejects empty `fallback_chains` at stage 3b

**Positive (load-bearing surfaces verified working):**
- (8) Bootstrap reaches real production wiring at CP_CLIENTS (live `GET /v1/models` against Anthropic + OpenAI; both 200 OK with .env keys)
- (9) Workflow execution reaches actual LLM dispatch via fallback chain
- (10) Typed-error chain works end-to-end (`RT-FAIL-CLI-MANIFEST-ADMISSIBILITY` / `RT-FAIL-BOOTSTRAP` / `RT-FAIL-WORKFLOW`)
- (11) State-ledger persistence works (post-fix; 2 entries observed: genesis + step row)
- (12) OTel exporter degrades silently on collector-unavailable (UNAVAILABLE retries log but don't block — reasonable production behavior)
- (13) Hash chain integrity verified via formal `verify_chain` → `status=valid`

### (b) Silent-corruption hazard at Reading C

The post-load deep-coerce inference (Reading C) is irreversible. If an operator authors a step_payload field that genuinely needs to be `str` but the string content parses as a number (e.g., `tenant_id: "12345"`, `version: "1.0"`, `id: "100"`), inference converts to int / float silently. The conversion is invisible at the loader boundary and surfaces only at downstream consumption (where the operator may not realize the type changed).

Mitigations if Reading C is chosen:
- Emit a `WARNING` log entry per inferred coercion (`workflow_manifest_loader: coerced step_payload[s1].params.max_tokens from str to int via best-effort inference`)
- Document the inference algorithm at runtime spec §14.19.X (operator-visible contract)
- Provide an opt-out (e.g., `RuntimeConfig.yaml_payload_coercion: Literal["infer", "preserve"] = "infer"`) so operators who need string-typed payload can disable inference
- Provide a YAML escape syntax convention (e.g., quoted scalars `tenant_id: "12345"` always preserve as `str`, unquoted `max_tokens: 8` infer; this is actually YAML 1.2's native rule — and is the rule strictyaml `dirty_load` discards)

### (c) Reading B schema authoring cost estimate

Per runtime spec v1.35 §14.19.4 invariant 9 (`step_payload` JSON-serializability) + C-CP-25 §25.3.3 step-body-opaque invariant, `step_payload` is bounded only by JSON-serializability — `dict[str, Any]` with arbitrary nesting. Authoring a strictyaml schema that captures "any JSON-serializable value" with native type preservation requires reimplementing JSON-schema-equivalent type inference inside strictyaml's `Map`/`Seq`/`Str`/`Int`/`Float`/`Bool`/`MapPattern`/`SeqPattern`/`Any` combinators. strictyaml does not ship a `Json()` or `Native()` combinator. The schema would either:

- Enumerate every concrete payload shape per `step_kind` enum (CP plan v2.x carries `inference-step` / `tool-step` / `subagent-step` / `validator-step` / `hitl-step` shapes — 5 schemas to author + maintain in lockstep with the CP plan)
- Use `Any()` and accept the same str-fallback gap (Reading C is then the only resolution)

Schema authoring cost is therefore non-trivial and creates a CP-plan-shape-coupled maintenance surface that the loader currently avoids by treating step_payload opaquely.

### (d) Q-H=b ratification context (Phase 2a G2, 2026-05-28)

Per runtime spec v1.35 §14.18.5 + workspace `CLAUDE.md` row v1.35: Q-H=b ratified strictyaml en-bloc with Q-A..Q-N. The Q-H question was framed as "YAML parser choice: (a) PyYAML / (b) strictyaml" without explicit treatment of the scalar coercion behavior. The probe surfaces that the Q-H=b choice has a load-bearing consequence at the LLM-dispatch boundary that may not have been fully considered at G2 ratification. Re-litigating Q-H per Reading A is in-scope at this fork's apply arc if the operator chooses Q1=A.

### (e) Probe methodology durability

The probe surfaced 17 distinct findings (3 critical / 7 structural-or-UX / 7 positive). Each was anchored at a specific empirical observation (HTTP response code, error class name, file:line cite, config table value, etc.). Per workspace pattern `[[verification-shape-sharpened-grep-vs-e2e]]`: end-to-end exercise against real substrate sharpens grep-only verification. The probe pattern is durable — future closure-mode arcs SHOULD include an analogous use-the-product check before claiming Reading α' vacuous-second-conjunct closure (sub-species 7d) where production-execution coverage is feasible.

### (f) State-ledger composer fan-out at successful run

The successful TOML run produced exactly 2 state-ledger entries — genesis + step row. ZERO entries from U-CP-74 (override; `per_step_overrides={}` → expected silent-skip per workflow_driver firing site landed at PR #78), U-CP-76 (pause-resume; no pause/resume → expected silent-skip), U-CP-77 (HITL; no HITL placement → expected silent-skip per fork doc `class_1_tension_emit_override_audit_entry_consumer_chain_absence.md` Reading D bounded-defer), U-CP-78 / U-CP-79 (engine-layer; NotImplementedError stubs per fork `class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §11). The minimal-workflow shape exercises the genesis + step lifecycle only — does NOT exercise the fan-out surfaces that batch-45 H_T-RT-35 RETIRED-via-Reading-α' transit relied on for vacuous-second-conjunct closure. **This is consistent with the batch-45 close** — the Reading D bounded-defers correctly identified that production firing sites for the 4 unhandled composers are absent at MVP; the probe confirms operator-runnable workflows do not exercise them. The probe does NOT contradict the batch-45 close; it confirms the substrate-level absence is structural at MVP scope, not a fix-on-the-table.

### (g) PR #78 U-CP-74 firing site untested by this probe

PR #78 wired `emit_override_state_ledger_entry` at the workflow_driver post-`resolve_step_binding` site under `if binding.override_applied:`. The probe's minimal.yaml has `per_step_overrides={}` so `override_applied=False` always — the firing site silent-skipped throughout the probe. PR #78's tests at `test_cp_is_caller_site_integration.py` exercise the firing site at unit-test scope (4 cases passed). A future probe arc could author a workflow with `per_step_overrides` populated to exercise the U-CP-74 firing site through `harness run` end-to-end — would emit a 3rd state-ledger entry with `action_id="cp.per-step-override-application"`. NOT in scope at this fork doc; routes to use-the-product probe v2 at operator discretion.

---

## §5 — Filing footer

| Field | Value |
|---|---|
| Artifact | `class_1_fork_yaml_loader_step_payload_scalar_coercion_gap.md` |
| Status | PROPOSING |
| Filed at | 2026-05-29 |
| Surfaced by | use-the-product probe (post-PR-#78 session); 54th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (advisor convened pre-probe to frame the use-the-product question) |
| Authority anchors | runtime spec v1.35 §14.19 C-RT-30 WorkflowManifestLoader + §14.19.4 invariants 8 + 9 + Q-H=b Phase 2a G2 ratification (2026-05-28); CP spec C-CP-25 §25.3.3 step-body-opaque invariant; Phase 7 Meta-Architecture §7.7 X-AL-3 silent design extension rule |
| Empirical anchors | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py:249` (`strictyaml.dirty_load`); `:324-330` (`_coerce_int_fields` + docstring on step_payload opacity); `:140` (`step_payload: dict[str, Any]` field declaration); `harness-runtime/tests/integration/fixtures/track_b/minimal.yaml` (broken fixture); `harness-runtime/tests/integration/test_track_b_e2e.py:674-887` (working test bypasses loader) |
| Resolution path | Per CLAUDE.md §4.3 Class 1 → halt Phase 7 sub-phase execution; route to design-phase back-flow at runtime spec v1.36+ amendment + plan U-RT-104/U-RT-106 revision per chosen reading. Apply arc per ratified Q-set will land at follow-on PR with clearance marker per CLAUDE.md §4.5 |
| Cross-axis cascade | None at v1.35 amendment per §14.19.6 (verified: no IS/AS/CP/OD/CXA/ADR cite of loader scalar coercion behavior beyond runtime spec internal). Cascade scope expands ONLY if Q1=A (strictyaml replacement may surface in Target_Stack_Commitment_v1 §5.1 spec line) |
