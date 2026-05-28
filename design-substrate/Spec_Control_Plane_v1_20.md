# Spec Control Plane (v1.20)

*Delta over v1.19. v1.20 lands the long-deferred `WorkflowManifestEntry.default_gate_level` field declaration at §6.1.Y per Reading A absorption of `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` (operator-ratified 2026-05-27 Q1=A + Q2=apply-now + Q3=defer-layer-3-e2e). The extension closes the X-AL-3 silent-absorption gap at `harness-cp/src/harness_cp/workflow_driver.py:738` hardcoded `parent_gate_level=GateLevel.AUTO` documented at `workflow_driver_types.py:163-168` as "v1.7+ extension". Per CP spec v1.6 §6 line 333 explicit anti-extension invariant — "v1.7+ extension to surface them via operator-authored `WorkflowManifestEntry` extension fields is a Workflow §4.1.2 Class-2 amendment to this contract" — this v1.20 publication IS the ratified Workflow §4.1.2 Class-2 amendment. All other v1.19 + v1.18 + ... + v1.2 substantive content preserved verbatim by reference.*

## §0 Change note (v1.19 → v1.20)

### §0.1 Revision context — H_T-CP-19 default_gate_level spec-extension landing

Per `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` (filed 2026-05-27 at H_T-CP-19 PARTIAL → RETIRE-READY arc, operator-ratified same session): the `WorkflowManifestEntry.default_gate_level: GateLevel | None = None` field is the long-deferred v1.7+ extension explicitly anticipated at:

- `harness-cp/src/harness_cp/workflow_driver_types.py:163-168` (StepExecutionContext docstring): "operator surfaces this via a future `WorkflowManifestEntry.default_gate_level` field per v1.7+ extension"
- CP spec v1.6 §6 line 333 (anti-extension invariant): "v1.7+ extension to surface them via operator-authored `WorkflowManifestEntry` extension fields is a Workflow §4.1.2 Class-2 amendment to this contract, NOT a Phase-7 implementation-time amendment (per X-AL-3)"

v1.20 IS the ratified Workflow §4.1.2 Class-2 amendment. Reading A selected per fork §3.1 architect Mode-3 recommendation:

- **Optional + default None** (`default_gate_level: GateLevel | None = None`) — smallest possible spec extension; backward-compatible per Pydantic v2 Optional discipline; ZERO downstream-consumer disruption (100+ existing test fixtures + manifest construction sites unaffected).
- Workflow_driver composition site at `workflow_driver.py:738` reads `manifest_entry.default_gate_level if manifest_entry.default_gate_level is not None else GateLevel.AUTO` — preserves v1.6 MVP behavior at construction sites that do not surface the field; operator-supplied values flow through unchanged.

ZERO cross-axis cascade per fork §3.3 cascade analysis — `WorkflowManifestEntry.default_gate_level` is intra-CP-axis field; no CXA bucket touches, no OD/AS/IS/ADR cascade.

### §0.2 Sections revised

§0 (this change note); §6.1.Y (NEW sub-section authoring `default_gate_level` field declaration). All other sections preserved verbatim from v1.19 (which preserved verbatim from v1.18 + ... + v1.2 per delta-only-spec-file convention).

### §0.3 §6.1.Y — `default_gate_level` field declaration (NEW)

**NEW §6.1.Y** added to `WorkflowManifestEntry` field-set declaration:

> **§6.1.Y `default_gate_level`** (v1.20 NEW): Optional operator-surfaced seed for the C-CP-12 §12.2 sub-agent gate-level composition formula at the workflow_driver per-step composition site.
>
> **Type:** `GateLevel | None`
> **Default:** `None`
> **Semantics:** When None (the v1.6-and-prior MVP behavior), workflow_driver composes `StepExecutionContext` with `parent_gate_level=GateLevel.AUTO` (matches the harness solo-developer persona). When operator-supplied (not None), workflow_driver reads from this field directly per the formula `parent_gate_level = manifest_entry.default_gate_level if manifest_entry.default_gate_level is not None else GateLevel.AUTO` at `harness-cp/src/harness_cp/workflow_driver.py:738`-area composition site.
>
> **Authority anchor:** ADR-D5 v1.4 §1.3 declares cross-deployment monotonicity at the `GateLevel.{AUTO, ASK, DENY}` 3-class enum layer; operator-surfaced gate-level seed at WorkflowManifestEntry is conformant to this anchor; no external-authority contradiction.
>
> **Closes:** H_T-CP-19 spec-extension layer (layer 1 of 3) per Meta-Architecture §5.4 row + `harness-cp/CLAUDE.md` §4.1 PARTIAL → RETIRE-READY gate. Production binding (layer 2) lands at workflow_driver.py composition site read; multi-deployment e2e fixture (layer 3) is deferred to a future arc per fork §3.2 Q3=defer-layer-3-e2e ratification.
>
> **Pydantic v2 carrier:** `harness-cp/src/harness_cp/workflow_manifest_entry.py` adds the field at position-end (12th field; was 11 at v2.12 `entry_version` addition). Pydantic v2 Optional discipline preserves construction-time omission across the existing 100+ test fixtures + manifest construction sites (zero downstream-consumer disruption per fork §2.1 Reading A scope analysis).

### §0.4 Anti-extension invariant — updated

CP spec v1.6 §6 line 333 anti-extension invariant declared that **4** MVP-default-bounded fields (parent_gate_level + parent_sandbox_tier + parent_entry_hash + tenant_id at StepExecutionContext per workflow_driver_types.py:192-194 enumeration) are deferred-to-implementation-discretion at v1.6. v1.20 lifts **1 of 4** of those fields (parent_gate_level, via the `default_gate_level` field at WorkflowManifestEntry) to operator-surfaceable. The remaining 3 (sandbox_tier, entry_hash, tenant_id) preserve the v1.6 anti-extension invariant verbatim — future extensions of those 3 are separate Workflow §4.1.2 Class-2 amendments owed at their respective retirement events.

### §0.5 Status posture

Proposed (v1.19) → **Proposed (v1.20)**. v1.20 is an additive amendment — one new field at WorkflowManifestEntry + one new §6.1.Y sub-section + one anti-extension invariant scope-narrowing. No prior field change; no prior contract change; no acceptance criterion change at any prior contract.

### §0.6 Cross-axis cascade — ZERO

Per fork §3.3 cascade analysis verified at filing:

- IS: NO cascade (field is CP-resident)
- AS: NO cascade
- CP: YES (intra-axis — spec §6.1.Y + plan + impl)
- OD: NO cascade (no audit-namespace touch)
- CXA: NO cascade (no cross-axis edge change)
- Runtime: YES (consumer-side — workflow_driver.py composition site read)
- ADR: NO cascade (ADR-D5 v1.4 anchor unchanged)

ZERO cross-axis cascade is the strongest indicator that Reading A is well-scoped.

### §0.7 Adjacent defects surfaced (not patched per FM-2)

(i) **3 other v1.7+ deferred fields preserved at anti-extension invariant.** Per workflow_driver_types.py:192-194 enumeration, `parent_sandbox_tier` + `parent_entry_hash` + `tenant_id` remain at v1.6 hardcoded defaults pending their respective retirement events. NOT patched at v1.20 per FM-2 (Reading D wider scope was rejected at fork §3.1 architect recommendation — A keeps scope tight to H_T-CP-19).

(ii) **Layer-3 multi-deployment e2e fixture deferred.** Per fork §3.2 Q3=defer-layer-3-e2e ratification: H_T-CP-19 RETIRE-READY at layer-2 close (production binding read); RETIRE-READY → RETIRED waits on multi-deployment e2e fixture at a future arc. NOT patched at v1.20 per Q3 ratification scope.

### §0.8 Downstream absorption owed (post-v1.20)

(a) Workspace `CLAUDE.md` §2.3 CP spec row bump (v1.19 → v1.20). **Patched at v1.20 co-publication.**
(b) CP plan v2.23 → v2.24 single-unit-body amendment at U-CP-13 absorbing the new field. **Patched at v1.20 co-publication via v2.25 plan delta.**
(c) `harness-cp/src/harness_cp/workflow_manifest_entry.py` field addition + GateLevel import. **Patched at v1.20 co-publication.**
(d) `harness-cp/src/harness_cp/workflow_driver.py:738` composition site read. **Patched at v1.20 co-publication.**
(e) `harness-cp/src/harness_cp/workflow_driver_types.py:163-168` docstring retired (deferral language → applied language). **Patched at v1.20 co-publication.**
(f) `harness-cp/tests/test_workflow_manifest_entry.py` 3 NEW tests covering the field. **Patched at v1.20 co-publication.**
(g) `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` Status line refresh: PROPOSING → ✅ APPLIED. **Patched at v1.20 co-publication.**
(h) Retirement event filing — H_T-CP-19 PARTIAL → RETIRE-READY transit at batch-21 (separate retirement-event filing arc; operator-discretion timing per existing 7d cadence).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_20.md` |
| Version | v1.20 |
| Filing event | H_T-CP-19 `default_gate_level` spec-extension landing per `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` Reading A absorption (operator-ratified 2026-05-27 Q1=A + Q2=apply-now + Q3=defer-layer-3-e2e). Workflow §4.1.2 Class-2 amendment per CP spec v1.6 §6 line 333 anti-extension invariant self-declaration. 2026-05-27 |
| Predecessor | `Spec_Control_Plane_v1_19.md` (preserved verbatim outside the §0 + §6.1.Y NEW amendment sites enumerated at §0.2) |
| Successor | (none — current canonical) |
| Field-set delta | WorkflowManifestEntry: 11 fields → 12 fields (NEW `default_gate_level: GateLevel | None = None` at position-end) |
| Cross-axis cascade | ZERO per §0.6 (intra-CP-axis only) |
| H_T-CP-19 status | Spec-extension layer (layer 1 of 3) **APPLIED at v1.20**; production binding layer (layer 2) **APPLIED at v1.20 co-publication** (workflow_driver.py:738 composition site read); multi-deployment e2e layer (layer 3) **DEFERRED to future arc** per fork Q3 ratification. PARTIAL → RETIRE-READY transit owed at batch-21 retirement event filing. |
| Operator authority | `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` Q1=A + Q2=apply-now + Q3=defer-layer-3-e2e ratification 2026-05-27 |
| Related forks | (parent) `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` |
| Related memory | `[[h-t-cp-19-retire-ready-gate-spec-extension-bounded]]` (status advances PARTIAL → spec-layer-APPLIED) |
| Date | 2026-05-27 |
