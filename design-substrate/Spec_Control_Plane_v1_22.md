# Spec: Control Plane — v1.22 (delta over v1.21)

---

## Change-note (v1.21 → v1.22)

**Scope of revision.** Fidelity-pure citation-correction patch partially closing v1.21 §"Adjacent observations" (c) — *"v1.20 §0.7 (i) — 3 other v1.7+ deferred WorkflowManifestEntry fields preserved at anti-extension invariant"* — at the **tenant_id** axis only. Disposition: **CLOSED-as-binding-fix-not-schema-extension** 2026-05-27. The `parent_sandbox_tier` + `parent_entry_hash` axes preserve the v1.6 anti-extension invariant verbatim; only the tenant_id axis is lifted because empirical orientation surfaced that tenant_id is per-deployment scoping (sourced from `RuntimeConfig.tenant_id` via `HarnessContext.tenant_id`), NOT per-workflow operator-surfaced like the CP-19 `default_gate_level` precedent at CP spec v1.20 §6.1.Y.

**Arc shape divergence from CP-19 precedent.** CP-19 (`parent_gate_level`) was a Workflow §4.1.2 Class-2 amendment because the deferral comment named `WorkflowManifestEntry.default_gate_level` as the explicit v1.7+ extension surface. The tenant_id deferral comment at `workflow_driver_types.py:189-192` (pre-v1.22) explicitly named the alternate surface: *"tenant_id sourced from future `HarnessContext.tenant_id` or `RuntimeConfig.tenant_id`"* — both runtime-layer surfaces, NOT WorkflowManifestEntry. Therefore the lift is a **binding fix** (no spec §6.1.Z field declaration, no Workflow §4.1.2 Class-2 amendment, no fork doc ratification) — the smallest possible arc shape per advisor 2026-05-27 pre-substantive orientation.

**Empirical orientation that foreclosed CP-19-precedent ceremony.** Production audit at HEAD `9c1f54f`:
- `tenant_id: str | None` is **already plumbed end-to-end** through `RuntimeConfig` (types.py:1010) → `StepExecutionContext` (workflow_driver_types.py:214) → 4 composition sites (sub_agent_dispatch.py:498 / hitl_gate_composer.py:792 / llm_dispatch.py:514 / audit_writer.py:109).
- `audit_writer._tenant_tag(tenant_id)` (audit_writer.py:97) maps falsy → `_SINGLE_TENANT_TAG` sentinel; downstream `_action_id_for` + `read_for_tenant` consume the tag uniformly.
- The ONLY blocker was the hardcoded `tenant_id=None` at `workflow_driver.py:764` (post-lift: `tenant_id=ctx.tenant_id`).
- CP spec base text (v1.2) and all v1.3..v1.21 delta files contain **ZERO** `tenant_id` references — the v1.20 §0.7 (i) carry framing was the only spec-side mention, and it was orientation-narrative not contract.

**Authoring lineage.** Sub-species at workflow v1.9 §7.4.7.2: **3.binding-fix-not-schema-extension** — distinct from the 6 prior species 3 sub-species (3.code-resolution / 3.fork-doc-closure / 3.workflow-grammar / 3.empirical-verification-of-external-authority / 3.same-session-immediate-sequel / 3.retirement-event-filing-arc). Shared common-ancestor "resolved-but-carry-stale-inherited"; distinct closure-event-class is **arc-shape-reframe at advisor pre-substantive consultation** (the v1.20 §0.7 (i) carry framing implied CP-19-precedent shape — Reading D wider scope; empirical orientation at the advisor pass discriminated tenant_id as binding-fix-shape; CP-19-precedent shape preserved as canonical for `parent_sandbox_tier` + `parent_entry_hash` only). Sub-species set at species 3 now SEVEN in 5 consecutive arcs (v1.22 OD / v1.23 OD / v1.24 OD / v1.21 CP / v1.22 CP).

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state + advisor pre-substantive orientation that foreclosed fork-doc-ratification ceremony. The advisor 21st application this session (per `[[advisor-before-substantive-work-for-cross-axis-blockers]]`) caught the framing-error before any spec or plan amendment landed; operator AskUserQuestion confirmed binding-fix shape over fork-doc-ceremony.

**Co-publication this session.** Production binding lift at `harness-cp/src/harness_cp/workflow_driver.py:764` + DriverContext Protocol extension (NEW `tenant_id: str | None` field) + `workflow_driver_types.py` deferral comment refresh + HarnessContext `tenant_id` `@computed_field` property reading `self.config.tenant_id` + 4 NEW tests at `harness-cp/tests/test_workflow_driver.py` + _FakeCtx fixture updates across 4 test files. 1799/1799 harness-cp + harness-runtime tests pass + 4 skipped. ZERO cross-axis cascade at production / contract / signature / AC layers (verified via grep this session — tenant_id flow is intra-binding-chain; no downstream-consumer artifact changes; CXA v2.15 unchanged).

---

## §1 Finding-closure-disposition refresh

### §1.1 v1.21 §"Adjacent observations" (c) — PARTIALLY CLOSED at tenant_id axis

**Carry-text at v1.21.** *"(c) v1.20 §0.7 (i) — 3 other v1.7+ deferred WorkflowManifestEntry fields preserved at anti-extension invariant. Carried verbatim. `parent_sandbox_tier` + `parent_entry_hash` + `tenant_id` still hardcoded at workflow_driver.py:750/752/754 per empirical grep at HEAD `79865d6`. GENUINE; future operator-discretion arc(s) per Reading D wider scope."*

**Disposition at v1.22.** **PARTIALLY CLOSED-as-binding-fix-not-schema-extension** 2026-05-27 (tenant_id axis only). Post-v1.22 lift: `workflow_driver.py:764` reads `ctx.tenant_id` instead of hardcoded `None`; HarnessContext exposes the value via `@computed_field` property reading `self.config.tenant_id`; DriverContext Protocol declares the field. The `parent_sandbox_tier` + `parent_entry_hash` axes preserve the v1.6 anti-extension invariant verbatim per FM-2 narrow-scope discipline — future operator-discretion arcs.

**Reading D foreclosed for tenant_id only.** v1.21 (c) "Reading D wider scope" framing implied uniform CP-19-precedent treatment of all 3 fields. Empirical orientation at v1.22 advisor pre-substantive consultation discriminated tenant_id as the per-deployment surface (already plumbed via RuntimeConfig + HarnessContext); the v1.7+ deferral comment at `workflow_driver_types.py:189-192` explicitly named `HarnessContext.tenant_id` / `RuntimeConfig.tenant_id` as the source, not `WorkflowManifestEntry`. The other 2 fields preserve CP-19-precedent shape as canonical — their lifts WILL require Workflow §4.1.2 Class-2 amendments when their respective retirement events open.

### §1.2 Disposition summary

| v1.21 (c) sub-axis | Closure event | Closure commit | Status at v1.22 |
|---|---|---|---|
| `tenant_id` | Binding fix at workflow_driver.py:764 + DriverContext Protocol + HarnessContext computed property | (this arc — co-published with v1.22 spec delta) | **CLOSED-as-binding-fix** |
| `parent_sandbox_tier` | (not closed at v1.22 per FM-2) | — | **PRESERVED VERBATIM** |
| `parent_entry_hash` | (not closed at v1.22 per FM-2) | — | **PRESERVED VERBATIM** |

v1.21 (c) text REFINED at v1.22 §0.7 — original 3-field framing narrows to 2-field carry (`parent_sandbox_tier` + `parent_entry_hash`). v1.21 file body PRESERVED VERBATIM per delta-only-spec-file convention; v1.22 §1 is the canonical-reading amendment for the disposition layer.

---

## §2 Cross-artifact cite-cascade disposition (v1.22 NEW)

| Artifact | Site | Disposition at v1.22 |
|---|---|---|
| `harness-cp/src/harness_cp/workflow_driver.py:262-319` | DriverContext Protocol — NEW `tenant_id: str | None` field | **CO-PUBLISHED this arc** |
| `harness-cp/src/harness_cp/workflow_driver.py:764` | StepExecutionContext composition — `tenant_id=ctx.tenant_id` | **CO-PUBLISHED this arc** |
| `harness-cp/src/harness_cp/workflow_driver_types.py:189-202` | Deferral comment refresh — tenant_id paragraph rewritten; 4 → 2 deferred-fields enumeration | **CO-PUBLISHED this arc** |
| `harness-runtime/src/harness_runtime/types.py` HarnessContext | NEW `@computed_field` property `tenant_id` reading `self.config.tenant_id` | **CO-PUBLISHED this arc** |
| `harness-cp/tests/test_workflow_driver.py` | _FakeCtx `tenant_id` field + 4 NEW tests | **CO-PUBLISHED this arc** |
| `harness-cp/tests/test_workflow_driver_drain.py` / `_envelope.py` / `_validator_hook.py` | _FakeCtx tenant_id fixture additions | **CO-PUBLISHED this arc** |
| Workspace `CLAUDE.md` §2.3 CP spec row | v1.21 row narrative | **CO-PUBLISHED this arc** — bumped to v1.22 |
| `harness-cp/CLAUDE.md` §1.2 spec version cite | "v1.21 + plan v2.26" current | **CO-PUBLISHED this arc** — bumped to "v1.22 + plan v2.26" (no CP plan delta this arc; binding fix is intra-production scope) |
| Peer artifacts at design-substrate/ | ZERO v1.21 (c) tenant_id-specific cites | **NO change owed** — verified via grep this session |
| CP plan v2.26 | No tenant_id-specific atomic unit cited at production code layer | **NO change owed** — production binding is intra-driver-composition (not an atomic unit boundary; mirrors how v1.6 MVP defaults are not unit-decomposed) |
| CXA v2.15 | No cross-axis edge change | **NO change owed** — verified via grep |
| Retirement events ledger | tenant_id is NOT on the 49-row substitution table (it's deferred-field cleanup, not H_T substitution retirement) | **NO change owed** |

---

## §3 Sections preserved verbatim at v1.22

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v1.22 amendment touches ONLY the NEW §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade disposition + §3 sections-preserved-verbatim. The following sections are PRESERVED VERBATIM:

- **§6.1.Y** (v1.20 `WorkflowManifestEntry.default_gate_level: GateLevel | None = None` field declaration)
- **§0.4** (v1.20 anti-extension invariant scope-narrowing)
- **v1.21 §1.1 + §1.2 + §1.3** (batch-21 closure disposition)
- **v1.21 §"Adjacent observations" (a)+(b)+(d)+(e)** (other carries; (c) refined per v1.22 §1)
- **All v1.2–v1.21 lineage substantive amendments**

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.21 (c) `tenant_id` axis — PARTIALLY CLOSED at v1.22 §1.1.** Removed from §0.7 (i) carry at tenant_id sub-axis.

(b) **v1.21 (c) `parent_sandbox_tier` axis — preserved verbatim at v1.22.** Future operator-discretion arc per CP-19-precedent shape (Workflow §4.1.2 Class-2 amendment expected — the AS sandbox-tier surface IS per-workflow operator-surfaceable per ADR-D2 sandbox-tier-floor pattern). GENUINE.

(c) **v1.21 (c) `parent_entry_hash` axis — preserved verbatim at v1.22.** Future arc gates on `LedgerWriter.last_appended_entry_hash` API extension per `workflow_driver_types.py:180-185` deferral comment. GENUINE.

(d) **v1.21 (d) Layer-3 multi-deployment e2e fixture — CLOSED at batch-22.** Per `[[fork-h-t-cp-19-default-gate-level-spec-extension]]` Layer 3 e2e reframe; H_T-CP-19 RETIRED at batch-22 close (`9c1f54f`). v1.21 (d) framing "GENUINE; operator-discretion timing per Q3 ratification" became stale at batch-22 close. Sub-species: 3.retirement-event-filing-arc (sibling pattern). **NOT patched at v1.22 per FM-2** — single-focus arc on tenant_id; v1.23 candidate.

(e) **NEW at v1.22 — sub-species 3.binding-fix-not-schema-extension catalogued.** v1.22 §1.1 closure is the SEVENTH sub-species refinement of species 3 (resolved-but-carry-stale-inherited) at workflow v1.9 §7.4.7.2. Distinct closure-event-class: **arc-shape-reframe at advisor pre-substantive consultation foreclosed CP-19-precedent ceremony**. Pattern catalogued: when a deferred-field carry framing implies uniform-shape treatment ("3 fields", "Reading D wider scope"), empirical orientation at the advisor pass MUST discriminate per-field — surface enumeration (HarnessContext / RuntimeConfig vs WorkflowManifestEntry) is load-bearing for arc-shape selection. Sub-species set at species 3 now SEVEN in 5 consecutive arcs. Workflow v1.9 §7.4.7.2 "Sub-species" column extension increasingly warranted. NOT patched per FM-2.

(f) **`workflow_driver_types.py` enumeration cardinality refresh.** v1.22 lift narrows "4 deferred-to-MVP-default fields" → "2 preserved (parent_sandbox_tier + parent_entry_hash)" with parent_gate_level (lifted at v1.20) + tenant_id (lifted at v1.22) explicitly carved out. Production comment co-published this arc; no spec change. Catalogued for observation only.

(g) **DriverContext Protocol structural extension — NOT a CP spec contract amendment.** The Protocol lives at `harness_cp.workflow_driver.DriverContext` (production code, not spec); the v1.22 amendment adds a `tenant_id: str | None` field annotation. CP spec C-CP-25 §25.2 contracts cover `StepExecutionContext` (consumed by the driver) but NOT `DriverContext` (which is the structural substrate the driver consumes — adjacent to but not part of the spec contract surface). No CP spec C-CP-NN contract changes at v1.22.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.22 (Fidelity-pure citation-correction patch partially closing v1.21 §"Adjacent observations" (c) at tenant_id axis only — **CLOSED-as-binding-fix-not-schema-extension** 2026-05-27; NEW §1 + §2 + §3; sub-species 3.binding-fix-not-schema-extension catalogued at §"Adjacent observations" (e); v1.21 + earlier files PRESERVED VERBATIM) |
| Trigger | Operator-routed v1.7+ deferred WorkflowManifestEntry field advancement arc — operator chose tenant_id 2026-05-27; advisor pre-substantive orientation discriminated arc-shape (binding fix vs CP-19-precedent fork ceremony); operator AskUserQuestion confirmed binding-fix shape |
| Supersedes | v1.21 (c) tenant_id sub-axis carry (parent_sandbox_tier + parent_entry_hash sub-axes preserved verbatim) |
| Scope of revision | NARROW: NEW §1 + §2 + §3. ZERO contract / signature / AC change at any C-CP-NN. ZERO Workflow §4.1.2 Class-2 amendment (binding fix is NOT a schema extension). Co-publication: workflow_driver.py + workflow_driver_types.py + HarnessContext computed property + 4 NEW tests + 4 _FakeCtx fixture updates + workspace CLAUDE.md row. |
| Production binding | `workflow_driver.py:764` reads `ctx.tenant_id` instead of hardcoded `None`; DriverContext Protocol declares `tenant_id: str | None`; HarnessContext exposes via `@computed_field` reading `self.config.tenant_id`. ZERO behavior change at `RuntimeConfig.tenant_id = None` (the v1.6 MVP single-tenant default preserved). |
| Cross-axis cascade | ZERO. Verified via grep at HEAD. CXA v2.15 unchanged; no inbound/outbound edge changes; no per-axis attribution refresh owed. |
| Authority anchor | `workflow_driver_types.py:189-192` v1.7+ deferral comment naming `HarnessContext.tenant_id` / `RuntimeConfig.tenant_id` as canonical source surface (pre-v1.22 text); the deferral comment IS the canonical authority for the binding-fix shape |
| Predecessor | v1.21 (batch-21 retirement event filing carry closure) |
| Successor | (none — current canonical) |
| Date | 2026-05-27 |
