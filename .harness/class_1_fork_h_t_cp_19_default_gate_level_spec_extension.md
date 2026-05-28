# Class 1 Fork — H_T-CP-19 default_gate_level CP-spec extension (workflow_driver.py hardcoded GateLevel.AUTO)

**Filed:** 2026-05-27 at H_T-CP-19 PARTIAL → RETIRE-READY arc filing, pre-substantive-work.
**Workspace HEAD at filing:** `993b4df` (main, post CXA v2.15 ToolContract seam landing).
**Routing class:** Class 1 (halt-execution; X-AL-3 silent-absorption prevention per workspace `CLAUDE.md` §4.4 + Meta-Architecture §7.7 — no silent H_T design extension at Phase 7 execution).
**Surfaced by:** `[[h-t-cp-19-retire-ready-gate-spec-extension-bounded]]` memory anchor + `harness-cp/CLAUDE.md` §4.1 retirement status table (H_T-CP-19 PARTIAL gate framing).

---

## §1 — The gap

### §1.1 Production binding (hardcoded MVP default)

`harness-cp/src/harness_cp/workflow_driver.py:738` hardcodes `parent_gate_level=GateLevel.AUTO` when composing `StepExecutionContext` at workflow-driver entry:

```python
# line 730-744 (post CXA v2.15 + adjacent arcs)
# parent_gate_level = AUTO; parent_sandbox_tier = TIER_1_PROCESS;
# parent_entry_hash = "" (child shares parent ledger writer per
# C-RT-17 §14.7.4); tenant_id = None (multi-tenancy not at v1.6 stack).
step_context = StepExecutionContext(
    workflow_id=manifest_entry.workflow_id,
    parent_action_id=(
        f"workflow:{manifest_entry.workflow_id}:step:{step_index}"
    ),
    parent_gate_level=GateLevel.AUTO,        # ← hardcoded MVP default
    parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
    parent_actor=ctx.ledger_writer.actor,
    parent_entry_hash="",
    parent_idempotency_key=step_idempotency_key_pre,
    tenant_id=None,
    step_index=step_index,
)
```

### §1.2 Explicit deferral (documented self-acknowledgment)

`harness-cp/src/harness_cp/workflow_driver_types.py:163-168` explicitly documents the deferral at the `StepExecutionContext` docstring:

> - `parent_gate_level`: the seed input for the C-CP-12 §12.2 sub-agent gate-level composition formula. v1.6 MVP default: `GateLevel.AUTO` (matches the harness solo-developer persona; **operator surfaces this via a future `WorkflowManifestEntry.default_gate_level` field per v1.7+ extension**). Per C-CP-12 §12.4 "deferred to implementation discretion" — source of the seed is implementation-discretion-bounded.

This documents the v1.7+ design-extension that has not yet been authored. The deferral has been documented at the production code layer since v1.6 (cluster 5 CP composition arc); the spec has not yet absorbed the corresponding `WorkflowManifestEntry.default_gate_level` field declaration.

### §1.3 Retirement gate framing

`harness-cp/CLAUDE.md` §4.1 retirement status table lists H_T-CP-19 as PARTIAL:

> **H_T-CP-19** (D5 cross-deployment monotonicity — batch 11, U-CP-26+U-CP-27+U-CP-43 landed; workflow_driver uses static GateLevel.AUTO only)

PARTIAL → RETIRE-READY gate (per §4.1 7-PARTIAL gate enumeration): "CP-19 on multi-deployment runtime scenario". The actual structural gate has two layers:

1. **CP-spec extension layer:** `WorkflowManifestEntry.default_gate_level` field declaration (canonical spec authority for operator-surfaced gate-level seed). NOT YET AUTHORED.
2. **Production binding layer:** `workflow_driver.py:738` reads from `manifest_entry.default_gate_level` instead of hardcoded `GateLevel.AUTO`. GATED ON LAYER 1.
3. **e2e exercise layer:** multi-deployment fixture exercising cross-deployment monotonicity via operator-supplied gate-level seeds at different DeploymentSurface tiers. GATED ON LAYERS 1+2.

This fork addresses LAYER 1 — the X-AL-3 silent-absorption prevention gap. Layers 2+3 are downstream impl + e2e arcs.

### §1.4 Why Class 1 (not Class 3)

Per `Project_Workflow_v1_8.md` §2.7.6 + workspace `CLAUDE.md` §4.4:

- **X-AL-3 invariant:** "no silent H_T design extension at Phase 7 execution. New H_T primitives surfaced at execution-time route to design-phase back-flow (Class 1) before implementation proceeds." Adding a new field to `WorkflowManifestEntry` IS a new H_T design extension — it expands the spec contract surface.
- **Authority chain compliance:** `WorkflowManifestEntry` is canonical at CP spec v1.6 §6.x (with v1.17 §6.5 absorbing the `StepEffectiveBinding.persona_tier` extension per `[[fork-u-rt-94-webhook-delivery-composer-binding-chain-absence]]`). Field-set extension routes through Phase 5 spec revision-pass.
- **Cascade scope:** field addition triggers CP plan v2.23 → v2.24 absorption at U-CP-13 or U-CP-14 (the WorkflowManifestEntry-carrying atomic unit) + harness-cp impl + harness-runtime impl (workflow_driver.py:738 read) + retirement event filing. Multi-axis arc.

Three convergent Class 1 triggers. Not Class 3 because: (a) the extension is not pure documentation-drift; it adds a new contract surface; (b) downstream consumers will need to absorb the new field; (c) the X-AL-3 silent-absorption discipline is workspace-canonical and explicitly applies to spec extensions surfaced at Phase 7.

---

## §2 — Four readings (operator decision required)

### §2.1 Reading A — Minimal additive: optional field with documented MVP default

**Spec extension:** Add `default_gate_level: GateLevel | None = None` (Optional, default None) to `WorkflowManifestEntry` at CP spec v1.6 §6.x canonical-reading amendment. NEW §6.x.Y sub-section authoring the field semantics.

**Production binding:** `workflow_driver.py:738` reads `manifest_entry.default_gate_level if manifest_entry.default_gate_level is not None else GateLevel.AUTO` — preserves MVP behavior for manifests that don't surface the field; operator-surfaced manifests use the operator's value.

**Scope:** ~6-8 commits — CP spec v1.19 → v1.20 NEW §6.x.Y + CP plan v2.23 → v2.24 single-unit-body amendment + harness-cp impl (WorkflowManifestEntry Pydantic field + StepExecutionContext composition site read) + harness-runtime impl tests + workspace CLAUDE.md row bumps + fork doc Status refresh.

**Authority:** ADR-D5 v1.4 + ADR-F3 v1.1 → CP spec v1.20 §6.x.Y → CP plan v2.24 → impl. Cite chain resolves at apply-time.

**Discriminator:** A is the smallest possible spec extension. Backward-compatible at the wire-protocol layer (Optional + default None). Zero downstream-consumer disruption. NOT yet sufficient for RETIRE-READY — multi-deployment e2e (layer 3) remains outstanding.

### §2.2 Reading B — Required field with explicit default at construction

**Spec extension:** Add `default_gate_level: GateLevel = GateLevel.AUTO` (non-Optional, default AUTO) to `WorkflowManifestEntry`. NEW §6.x.Y sub-section + AUTO-as-default discipline.

**Production binding:** `workflow_driver.py:738` reads `manifest_entry.default_gate_level` directly (no None-check).

**Scope:** ~6-8 commits — same as Reading A but field-construction-site discipline differs (default is at field declaration, not at consumer's None-check).

**Authority:** Same as Reading A.

**Discriminator:** B forces every WorkflowManifestEntry construction site to either accept the default or surface explicitly. Slightly more visible to authors. Backward-compatible because Pydantic v2 field-default discipline preserves construction-time omission. Risk: any test fixture that uses `WorkflowManifestEntry(**partial_kwargs)` continues working only if the default is preserved at field declaration.

### §2.3 Reading C — Defer indefinitely + document the gate explicitly

**Spec extension:** None. Instead, add a §6.x.Y note to CP spec v1.20 explicitly documenting that `parent_gate_level` is `GateLevel.AUTO` at v1.20-and-prior with the future extension to `WorkflowManifestEntry.default_gate_level` deferred indefinitely pending multi-deployment runtime scenario. Same content as v1.6 docstring at workflow_driver_types.py, but canonicalized at spec layer.

**Production binding:** Unchanged. `workflow_driver.py:738` stays hardcoded.

**Scope:** ~2 commits — CP spec v1.19 → v1.20 NEW §6.x.Y deferral declaration + workspace CLAUDE.md row bump.

**Authority:** Same as Reading A.

**Discriminator:** C is the cheapest. Preserves the current MVP behavior with an explicit spec-layer deferral cite — closes the X-AL-3 silent-absorption gap by canonicalizing the deferral. Does NOT unblock H_T-CP-19 PARTIAL → RETIRE-READY (layer 1 stays gated). Appropriate if operator judges that the multi-deployment runtime scenario is genuinely out of scope at v1.20 horizon.

### §2.4 Reading D — Wider scope: absorb all 4 deferred-to-MVP-default fields together

**Spec extension:** Add 4 fields to `WorkflowManifestEntry` per workflow_driver_types.py:192-194 deferred enumeration: `default_gate_level: GateLevel`, `default_sandbox_tier: SandboxTier`, `enable_explicit_entry_hash: bool`, `tenant_id: str | None`. NEW §6.x.Y multi-field sub-section.

**Production binding:** `workflow_driver.py:738` reads all 4 fields from manifest_entry; defaults preserved at field-declaration layer per Reading A or B shape.

**Scope:** ~12-15 commits — larger spec section + multi-field plan absorption + runtime read at 4 callsites + multi-axis impl (HarnessContext threading for tenant_id; LedgerWriter API extension for entry_hash) + e2e fixture refresh.

**Authority:** Same as Reading A but wider span. Cross-axis cascade likely at LedgerWriter API extension (touches IS).

**Discriminator:** D consolidates the future v1.7+ debt enumerated at workflow_driver_types.py:192-194 into a single arc. Higher landing cost; fewer follow-on arcs over time. Risk: forces decisions on 3 other fields that may not be operator-priority at this arc; could delay H_T-CP-19 unblock by adjacent-decision pressure.

---

## §3 — Recommended routing (architect Mode-3)

### §3.1 Recommendation: Reading A (operator confirms)

**Why A over B:** Optional + default None is the least-invasive shape against the existing 100+ test fixtures + manifest construction sites in `harness-cp/`. Backward-compatible posture per Pydantic v2 Optional field discipline. Construction-site disruption = 0.

**Why A over C:** A unblocks H_T-CP-19 layer 1 (spec extension) directly, enabling layer 2 (production binding) and layer 3 (multi-deployment e2e) to proceed at operator-discretion timing. C canonicalizes the deferral but does not advance the retirement state.

**Why A over D:** D conflates 4 separate deferral decisions into one arc; operator may not have decided on all 4 simultaneously. A keeps scope tight to the H_T-CP-19 gate; the other 3 fields (sandbox_tier, entry_hash, tenant_id) get their own forks when their retirement events surface.

### §3.2 Recommended sequencing

1. **This arc (fork ratification + Reading A apply):** ~6-8 commits — CP spec v1.20 + CP plan v2.24 + harness-cp Pydantic field + harness-cp StepExecutionContext composition site read + harness-runtime impl tests + workspace CLAUDE.md row bumps + fork doc Status refresh.
2. **Follow-on arc (RETIRE-READY promotion):** ~1 commit — retirement event filing transitioning H_T-CP-19 PARTIAL → RETIRE-READY at production-binding-MET layer.
3. **Future arc (RETIRE-READY → RETIRED):** multi-deployment e2e fixture exercising cross-deployment monotonicity per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline. Operator-discretion timing — gates on real multi-deployment runtime scenario.

### §3.3 Cascade scope (per architect §5 sibling fork analysis)

- **CXA cascade:** ZERO. No cross-axis edge change — `WorkflowManifestEntry.default_gate_level` is intra-CP-axis field; no CXA bucket touches.
- **OD cascade:** ZERO. No OD-axis touch.
- **AS cascade:** ZERO.
- **Runtime cascade:** workflow_driver.py:738 read site only; no other runtime touch.
- **ADR cascade:** ZERO. ADR-D5 v1.4 (cross-deployment monotonicity) anchor unchanged; the spec extension is below ADR threshold per X-AL-3.
- **Test cascade:** test fixtures constructing `WorkflowManifestEntry` need either no change (Optional + default None per A) or default-AUTO preservation per Pydantic v2 (B).

ZERO cross-axis cascade is the strongest indicator that Reading A is well-scoped.

### §3.4 Tiebreaker check

External authority: ADR-D5 v1.4 §1.3 declares cross-deployment monotonicity at the `GateLevel.{AUTO, ASK, DENY}` 3-class enum layer. Operator-surfaced gate-level seed at WorkflowManifestEntry is conformant to this anchor; no external-authority contradiction.

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Class | 1 (halt-execution; X-AL-3 silent-absorption prevention) |
| Filed | 2026-05-27 |
| HEAD | `993b4df` (main, post CXA v2.15) |
| Routing target | CP spec v1.19 → v1.20 NEW §6.x.Y `WorkflowManifestEntry.default_gate_level` field (Reading A) + CP plan v2.23 → v2.24 absorption + harness-cp + harness-runtime impl + retirement event |
| Blocks | NOT a hard block on other work. H_T-CP-19 PARTIAL → RETIRE-READY is the unblock target. |
| Predecessor | Memory `[[h-t-cp-19-retire-ready-gate-spec-extension-bounded]]` (gate framing; filed 2026-05-22) |
| Adjacent | `[[fork-u-rt-94-webhook-delivery-composer-binding-chain-absence]]` (CP spec v1.17 §6.5 StepEffectiveBinding.persona_tier extension precedent — same shape: optional field with documented default + multi-commit cascade) |
| Operator decision required | Q1 = Reading selection (A / B / C / D); Q2 = timing (apply-now-this-session / defer-to-next-session / hold-pending-multi-deployment-context); Q3 = layer-3 multi-deployment e2e scoping (in-scope-now / deferred-to-future-arc). |
| Authority anchors | CP spec v1.6 §6.x WorkflowManifestEntry canonical home + v1.17 §6.5 StepEffectiveBinding extension precedent + ADR-D5 v1.4 §1.3 GateLevel 3-class enum + workflow_driver_types.py:163-168 deferral self-documentation |

---

## §5 — Cross-axis cascade analysis (architect §5 frame)

| Axis | Cascade present? | Notes |
|---|---|---|
| IS | NO | Field is CP-resident; no IS contract touch |
| AS | NO | No AS-side carrier change |
| CP | YES (intra-axis) | Spec §6.x + plan + impl |
| OD | NO | No OD audit-namespace touch; no `cp_audit_to_od_audit` converter change |
| CXA | NO | No cross-axis edge change |
| Runtime | YES (consumer-side) | workflow_driver.py:738 read site only |
| ADR | NO | ADR-D5 v1.4 anchor unchanged |

ZERO cross-axis cascade verified at filing.

---

## §6 — Open routing decision

**Status: PROPOSING — awaiting operator ratification of Reading + timing + layer-3 scope.**

Pre-substantive work HALTED per X-AL-3 + workspace `CLAUDE.md` §4.4 silent-absorption prevention. Resolution arc opens on operator ratification.

---

*End of Class 1 fork doc. Filing event-record for H_T-CP-19 PARTIAL → RETIRE-READY HALTED pending resolution. Companion memory entry `[[fork-h-t-cp-19-default-gate-level-spec-extension]]` to be written post-ratification per workspace convention.*
