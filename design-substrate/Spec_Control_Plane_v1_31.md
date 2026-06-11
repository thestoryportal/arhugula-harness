# Spec: Control Plane — v1.31 (delta over v1.30)

---

## Change-note (v1.30 → v1.31)

**Scope of revision.** NEW §29 / C-CP-29 — `PromptSelectionManifest`, the CP-axis prompt-selection contract (R-PM-1 cascade PR #3 per `.harness/r-pm-1-prompts-management-design-v1.md` §4.2 + §6 row #3). Authors the per-role / per-workload prompt-version selection surface — operator-supplied bindings resolving `(role, workload) → version_sha` — mirroring the C-CP-01 §1.3 `RoutingManifest` per-role/workload binding shape exactly. This closes the R-PM-1 design's **selection-ownership split** (tension (i), IS ⊥ CP, probe-resolved by the `RoutingManifest` precedent): authoring/versioning is IS (the `PromptManifest.versions` content-addressed store, IS spec v1.7 §5.3); per-role/workload **selection-binding is CP** (this contract). The resolver yields a `version_sha`; the IS store resolves `version_sha → content`; the runtime (consumer site) injects the content as a system prompt via the runtime spec v1.44 §14.5.2 translate-time injection seam (PR #1).

v1.30 §1 canonical-reading amendment + §16.5.12.X lineage + v1.29 §16.5.12 + §16.5.3 chapeau + v1.28 §16.5.6.X + v1.27 §16.5 + v1.26 β.i + v1.25 §16.5 + §25–§28 (C-CP-25 ValidatorFramework / C-CP-26 PauseResumeProtocol / C-CP-27 PerServerTrustEvaluator+MCPClientNamespaceEmitter / C-CP-28 validator post-evaluate hook) substantive content all PRESERVED VERBATIM per delta-only-spec-file convention. §29 is **purely additive** — it introduces a new contract and does not amend, reinterpret, or supersede any prior section.

**Trigger.** R-PM-1 cascade PR #3 impl-arc opening 2026-06-11 per workspace CLAUDE.md §10.9 standing posture amendment 5 (probe-first discipline). Empirical probe at HEAD discriminated: (a) the runtime LLM dispatch keys routing on `_MVP_DEFAULT_AGENT_ROLE` and discards the role discriminator until R-300-second-provider — `RoutingManifest.per_role_bindings` has **no runtime indexer** (`grep 'per_role_bindings['` → empty); (b) `workload_class` IS a genuine runtime dimension (a required parameter of `run_bootstrap`, threaded from the caller's `WorkflowObject.workload_class`). So per-workload selection is behavior-driving end-to-end while per-role bindings are carried faithfully against the default role — exactly the routing precedent.

**No new ADR.** §29 is a CP-axis contract authored under the cleared R-PM-1 design (PR #505); it touches no foundational ADR (the injection mechanism's ADR-F1 fidelity was settled at PR #1 — `ProviderAgnosticPayload` stays frozen). Per `[[adr-vs-fork-spec-plan-granularity]]` a spec-granularity surface uses a spec amendment, not an ADR.

**Cite convention (adversarial review F3-01).** The §29 mirror-cites `C-CP-01 §1.3` (RoutingManifest) / `C-CP-03 §3.5` (RoleRoutingBinding) / `C-CP-04 §4.1` (WorkloadRoutingOverride) are **factor-out-domain-cites** — they name the parent contracts under which `RoleRoutingBinding` / `WorkloadRoutingOverride` were operator-ratified FACTOR-OUTs (`.harness/class_1_tension_role_routing_binding_underspec.md`, R-2/W-2 schemas, CP plan v2.10). The factored-out field shapes are not byte-tabled in a spec section; these cites name the domain authority, not a byte-resolving section. This is the identical convention the cleared `harness-cp/src/harness_cp/routing_manifest_residence.py` already uses for the same types; §29 propagates it.

---

## §29 (NEW) C-CP-29 — PromptSelectionManifest

### §29.1 Canonical signature(s)

The prompt-selection surface mirrors the C-CP-01 §1.3 `RoutingManifest` (frozen + `extra="forbid"`; a `manifest_version` plus per-role / per-workload binding maps). Residence: `harness-cp/src/harness_cp/prompt_selection_manifest.py`.

```python
class PromptBinding(BaseModel):
    """Names the active prompt version by content-addressed sha (mirrors
    RoleRoutingBinding; frozen + extra=forbid)."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    version_sha: str  # an authored member of the IS PromptManifest.versions store

class PromptSelectionManifest(BaseModel):
    """Canonical role × workload → prompt-version source (mirrors RoutingManifest)."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    manifest_version: int
    per_role_bindings: Mapping[AgentRole, PromptBinding] = {}        # default empty
    per_workload_overrides: Mapping[WorkloadClass, PromptBinding] = {}  # default empty

def resolve_active_prompt_version_sha(
    manifest: PromptSelectionManifest, *, role: AgentRole, workload: WorkloadClass,
) -> str | None: ...

def validate_prompt_selection_manifest(
    manifest: PromptSelectionManifest,
) -> PromptSelectionManifestValidationError | None: ...
```

`AgentRole` is the U-CP-00c open-string newtype; `WorkloadClass` is the harness-core `WorkloadClass` (U-CP-00). Both binding maps **default to empty** — the "empty binding falls through" semantics (zero config burden; the local-first default, C11). This is the empty-defaultable refinement over `RoutingManifest`'s all-required shape, justified by the fall-through semantics and consistent with the IS `PromptManifest.versions: tuple = ()` empty-default precedent (IS spec v1.7 §5.3).

The concrete on-disk format (JSON/YAML/TOML) is deferred to implementation discretion (mirrors C-CP-01 §1.3); the operator supplies the manifest on `RuntimeConfig.prompt_selection_manifest` (a `PromptSelectionManifest | None`, default `None`).

### §29.2 Resolution precedence

`resolve_active_prompt_version_sha` resolves the selected version by the same precedence `RoutingManifest` uses for workload-override-on-top-of-role:

1. `per_workload_overrides[workload]` → its `version_sha` (a workload override sits "on top of" role bindings, mirroring `WorkloadRoutingOverride` per C-CP-04 §4.1);
2. else `per_role_bindings[role]` → its `version_sha` (mirroring `RoleRoutingBinding` per C-CP-03 §3.5);
3. else `None`.

`None` means **no selection** → the runtime consumer falls through to the manifest's standing `active_prompt_version` (the #496 / PR-#1 single inline active prompt). The resolver is **pure** (no I/O, no IS-store consultation) — CP-axis-isolated; it yields an sha identity only.

### §29.3 Cross-axis store-membership — runtime-deferred

A bound `version_sha` MUST be an authored member of the IS `PromptManifest.versions` store. This is a **cross-axis (CP selection ↔ IS store) check** and is **runtime-deferred** — `validate_prompt_selection_manifest` is **structural-only** (it checks `manifest_version >= 1`), exactly as `validate_routing_manifest` defers the per-role model-presence check against the U-AS-29 catalog to a cross-axis runtime check (C-CP-01 §1.3 acceptance #3). The CP-side validator MUST NOT consult the IS store (axis isolation: `harness-cp` does not import the IS prompt store for this surface).

### §29.4 Runtime consumer-site obligation

The runtime is the consumer site that composes the CP resolver (§29.2) with the IS store (IS spec v1.7 §5.3) and the §14.5.2 injection seam. The reconciliation MUST run at bootstrap **stage 0 PREAMBLE** — after `ctx.prompt_manifest` is copied from `RuntimeConfig` and **before the first procedural-tier snapshot is computed** (the stage-3b CP producer sites create the snapshot resolver and emit snapshot-bearing ledger entries) and before the stage-5 LLM-dispatcher injection reader. (Reconciling at stage 0 rather than stage 5 is load-bearing: a later reconciliation would leave the stage-3b producer-site `procedural_tier_snapshot_ref` entries computed against the *un-reconciled* `active_prompt_version` while the dispatcher reads the selected version — inconsistent audit hashes.) The runtime MUST:

1. **validate the manifest structurally** — `validate_prompt_selection_manifest` (§29.3); on a non-`None` result **fail-loud** (`InvalidPromptSelectionManifestError`, parity with `build_routing_manifest`'s `InvalidRoutingManifestError`), never apply an invalid manifest;
2. resolve the selected sha via `resolve_active_prompt_version_sha(selection, role=_MVP_DEFAULT_AGENT_ROLE, workload=<run workload_class>)` (per-workload keyed on the genuine run workload; per-role on the MVP-default role — the runtime has no per-step role at MVP, faithful to routing's own un-indexed `per_role_bindings`);
3. on `None` (no selection configured, or no match) → leave `active_prompt_version` unchanged (the #496/PR-#1 inline active prompt);
4. on a selected sha → reconcile `prompt_manifest.active_prompt_version` **onto the matching store member** (not merely redirect the injection reader), so BOTH the §14.5.2 injection reader (`active_prompt_version.content`) and the C-IS-05 §5.2 procedural-tier hash reader (`active_prompt_version.version_sha`) read the SAME selected version — **content/hash coherence by construction** (a redirect-injection-only design would reintroduce the content↔hash drift that the IS spec v1.6 §5.2 `version_sha == prompt_version_sha(content)` derive-invariant closed, one layer up);
5. on a selected sha with **no matching store member** → **fail-loud / detect-then-refuse**: raise `RT-FAIL-PROMPT-SELECTION-UNAUTHORED` (a version must be authored in the store before it can be selected). Never silently fall through to the inline prompt.

Residence: `harness-runtime/src/harness_runtime/lifecycle/prompt_selection.py` (`reconcile_active_prompt_via_selection` + `PromptSelectionUnauthoredError` + `InvalidPromptSelectionManifestError`), invoked at `stage_0_preamble.execute`. The reconciliation uses `model_copy(update={"active_prompt_version": <member>})`; the selected member is already an authored store member satisfying the IS content↔sha + membership invariants, so the copy (which skips `PromptManifest`'s `mode="after"` validator) is invariant-preserving.

### §29.5 Failure-mode taxonomy

| Failure | Surface | Posture |
|---|---|---|
| `manifest_version < 1` (validator contract) | `validate_prompt_selection_manifest` → `PromptSelectionManifestValidationError(reason=...)` | Returned (recoverable validation result; mirrors `RoutingManifestValidationError`) |
| `manifest_version < 1` (consumer site) | `InvalidPromptSelectionManifestError` at stage-0 reconciliation | **Raised** (the runtime consumer enforces the structural contract — parity with `build_routing_manifest`'s `InvalidRoutingManifestError`; surfaces as a `BootstrapFailure` at `BootstrapStage.PREAMBLE`) |
| Bound `version_sha` not an authored store member | `RT-FAIL-PROMPT-SELECTION-UNAUTHORED` (`PromptSelectionUnauthoredError`) at stage-0 reconciliation | **Raised** (detect-then-refuse; surfaces as a `BootstrapFailure` at `BootstrapStage.PREAMBLE` — a config/authoring error the operator must correct). Distinct from the per-dispatch step-level `RT-FAIL-PROMPT-INJECTION-CONFLICT` (§14.5.2). |

### §29.6 Invariants

1. **Fall-through default.** An empty manifest (or `RuntimeConfig.prompt_selection_manifest is None`) selects nothing → byte-identical to the #496/PR-#1 inline-active behavior. Selection only *adds* resolution; it never gates whether dispatch runs (variability-in-values, not control-flow).
2. **Precedence.** Workload override > role binding > fall-through (§29.2), uniform with `RoutingManifest`.
3. **Content/hash coherence.** When selection drives the active version, the injected system prompt content and the C-IS-05 §5.2 procedural-tier hash component reflect the SAME version (§29.4 step 3).
4. **Fail-loud membership.** A bound sha with no store member never silently degrades to the inline prompt (§29.4 step 4).
5. **CP purity.** The CP resolver + validator never consult the IS store (the store consultation is the runtime consumer site; the CP→IS seam is the CXA registration owed at cascade PR #5).

### §29.7 Deferred to implementation discretion

- The on-disk manifest format (JSON/YAML/TOML) and its residence path-class (the prompt-selection manifest is operator-supplied on `RuntimeConfig`; a dedicated `PathClass` residence is not authored at v1.31 — unlike `RoutingManifest`'s `PathClass.ROUTING_MANIFEST`, since the inline `RuntimeConfig` supply path suffices for the capability landing).
- **Per-step override** (vs per-role / per-workload) — the `RoutingManifest` precedent has `per_workload_overrides` but no per-step prompt override; R-PM-1 design OQ-3 leaves a finer per-step prompt-selection granularity to a bounded follow-on iff a workload exercises it.
- Real **per-role** runtime indexing — deferred to R-300-second-provider (when the runtime gains a per-step agent-role dimension); per-role bindings are carried + resolved against the MVP-default role until then.

---

## §-preserved-verbatim

| Section | v1.30 status | v1.31 status |
|---|---|---|
| §1 — §16.5.12.X canonical-reading lineage | v1.30 | PRESERVED VERBATIM |
| §16.5.1 — §16.5.12.7 substantive content | v1.25–v1.30 | PRESERVED VERBATIM |
| §25 C-CP-25 — ValidatorFramework | v1.10+ | PRESERVED VERBATIM |
| §26 C-CP-26 — PauseResumeProtocol (+ §26.8 ResumeContext) | v1.10/v1.16 | PRESERVED VERBATIM |
| §27 C-CP-27 — PerServerTrustEvaluator + MCPClientNamespaceEmitter | v1.10 | PRESERVED VERBATIM |
| §28 C-CP-28 — validator post-evaluate hook | v1.24 | PRESERVED VERBATIM |

§29 is additive; no prior section is amended, reinterpreted, or superseded.

---

## §-adjacent observations (NOT patched per FM-2)

- **(a) Selection-ownership split (tension (i), IS ⊥ CP) — probe-resolved, no new ADR.** The `RoutingManifest.per_role_bindings` / `per_workload_overrides` precedent (C-CP-03 §3.5 / C-CP-04 §4.1) pre-resolves the split; prompts follow the same seam as Skills (IS-versioned, CP-bound). §29 records the CP half; IS spec v1.7 §5.3 holds the authoring/versioning half.
- **(b) MVP-default-role honesty (`[[r-cxa-seam-wiring-is-producer-discovery]]`).** The runtime has no per-step agent role at MVP; `RoutingManifest.per_role_bindings` is itself role-keyed only at R-300-second-provider (verified: no runtime indexer at HEAD). §29 carries `per_role_bindings` faithfully (resolved against `_MVP_DEFAULT_AGENT_ROLE`) but does NOT build a hollow per-role runtime indexer — per-workload selection (the genuine runtime dimension) is the behavior-driving e2e path.
- **(c) CXA seam owed at PR #5.** The CP→IS store-consultation seam (selection sha → `PromptManifest.versions` member) is composed at the runtime consumer site (§29.4); its `Cross_Axis_Composition_Document` registration is owed at R-PM-1 cascade PR #5 (after the producers exist), per the design §6 cascade.
- **(d) Cross-axis cascade verification.** §29 introduces no cite cascade owed at AS / OD / IS / runtime specs / ADRs (the runtime consumer realizes §29.4; the IS store + the §14.5.2 injection seam are pre-existing PR #2/#1 surfaces). The IS spec v1.7 §5.3 store-store-member language already anticipated "PR #3's CP selection layer is what would drive it" — §29 is that driver.

---

## §-filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_31.md` |
| Authored at | Phase 7 sub-phase 7b — R-PM-1 cascade PR #3 (CP prompt-selection), 2026-06-11 |
| Authoring authority | `.harness/r-pm-1-prompts-management-design-v1.md` §4.2 + §6 row #3 (cleared design, PR #505); R-PM-1 §5.16 + R-CC-1 §5.17 |
| Predecessor | `Spec_Control_Plane_v1_30.md` (v1.30) |
| Co-published | harness-cp impl `harness-cp/src/harness_cp/prompt_selection_manifest.py` (+ test `harness-cp/tests/test_prompt_selection_manifest.py`) + runtime consumer `harness-runtime/src/harness_runtime/lifecycle/prompt_selection.py` + `RuntimeConfig.prompt_selection_manifest` field + bootstrap stage-5 reconciliation + runtime tests (`test_prompt_selection.py` + `test_bootstrap.py` e2e) + clearance marker `.harness/clearance/Spec_Control_Plane-v1_31-cleared-2026-06-11.md` + `harness-cp/CLAUDE.md` §1.2 row bump + roadmap fixed-point refresh |
| Revision policy | Delta-only spec file per workspace `CLAUDE.md` §2.3 convention; v1.30 body + §25–§28 PRESERVED VERBATIM; §29 is purely additive |

---

*End of `Spec_Control_Plane_v1_31.md`. Parent guidance at workspace root `CLAUDE.md`. R-PM-1 design at `.harness/r-pm-1-prompts-management-design-v1.md`. IS authoring/versioning half at `Spec_Information_Substrate_v1.md` v1.7 §5.3; runtime injection seam at `Spec_Harness_Runtime_v1.md` v1.44 §14.5.2.*
