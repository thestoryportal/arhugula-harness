# Class 1 Fork — `mcp.*` namespace cross-emission on non-`mcp.tool.call` spans — ingestion ownership ambiguity

**Filed:** 2026-05-26 (post-AS-4 dual-attribute cascade close at `0c22efc`; OD spec v1.13 §"Adjacent observations" finding (b) routed to operator-discretion arc per fork §6 Option A scope-narrowing).
**Status:** **RATIFIED-AND-APPLIED 2026-05-26** — operator ratified Q0 = Class 2 (in-execution decision); Q1 = Reading A (parent-span-class rule at §C-OD-08 NEW §8.4) per assistant recommendation; Q2 = (α) single NEW §8.4 sub-section; Q3 = (a) ratify-apply-now (paired publication); Q4 = mixed (ii) — adopt with empirical-state footer rationale. Applied at OD spec v1.13 → v1.14 same session.
**Halt target:** None at present. Production EMITS both attributes correctly at `runtime_tool_dispatcher.py:261-282`; no production consumer dispatches on attribute-prefix at OD ingestion side; OD spec v1.13 sub-note resolved row-10 ingestion routing for the AS-4 arc. Finding (b) flags a residual spec-coherence question, NOT a halt-execution defect. **§6 Q0 ratifies classification (Class 1 / Class 2 / Class 3 / no-fork-needed).**
**Routing target candidates:** OD spec v1.13 → v1.14 (§C-OD-08 namespace collision discipline extension OR §C-OD-05 §5.1 row 4 + row 10 cross-row coordination). Out-of-scope at PROPOSED stage: AS spec amendment (AS §15.9 + §15.10 are canonical at the producer side; finding (b) is at the OD-side ingestion routing layer).
**Detection mode:** OD spec v1.13 §"Adjacent observations" finding (b) — explicit forward-cite to future operator-discretion arc per v1.13 successor cell ("v1.14 next operator-discretion arc — candidates: ... §C-OD-08 namespace collision discrimination per v1.13 adjacent finding (b)"). User invocation 2026-05-26.

---

## §1 — Empirical-verification details

### §1.1 The AS-side producer (LANDED at AS spec v1.6 + production at `runtime_tool_dispatcher.py`)

AS spec v1.6 §15.9 dual-attribute co-emission discipline:

- `sandbox.violation` child span carries BOTH `sandbox.fail.class` (F4 process-execution taxonomy per §15.2 row 3) AND `mcp.fail.class` (MCP-protocol taxonomy per §15.8) when an MCP-protocol-layer failure surfaces a sandbox violation.
- `mcp.fail.class` attribute prefix-namespace is `mcp.*` (per the attribute name); span-class namespace at emission site is `sandbox.violation` (under `sandbox.*` namespace pull).
- §15.10 best-effort projection table acknowledges semantic stretch at the projection MCP-shape → F4-shape — but does NOT govern ingestion routing at OD axis.

Production at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:261-282` (`_emit_sandbox_violation` helper):

```
with tracer.start_as_current_span("sandbox.violation") as span:
    _set(span, ATTR_MCP_FAIL_CLASS, mcp_fail_class.value)        # "mcp.fail.class"
    _set(span, ATTR_SANDBOX_FAIL_CLASS, projected.value)         # "sandbox.fail.class"
```

Both attributes emitted on the same `sandbox.violation` span. Production is structurally consistent with AS §15.9.

### §1.2 The OD-side ingestion-routing ambiguity (v1.13 sub-note resolved one reading; finding (b) flags the residual)

OD spec v1.13 §C-OD-05 §5.1 row 10 sub-note (NEW at v1.13 per AS-4 dual-attribute cascade fork):

> OD ingestion path at v1.13 sub-note treats the `mcp.fail.class` attribute as `sandbox.*`-row-ingested (per the parent span's namespace classification at `sandbox.violation`), NOT as `mcp.*`-row-ingested.

This is the **parent-span-class rule** — when an attribute uses prefix-A but appears on a span-class-B, ingestion routes via row-B (parent-span classification), not row-A (attribute prefix).

AS spec v1.6 §15 footer item (i) frames `mcp.fail.class` as living within the existing `mcp.*` namespace at attribute layer ("NEW `mcp.fail.class` attribute is at AS-axis sandbox.* namespace, not a new top-level namespace, so §C-OD-05 row count unchanged"). OD v1.13 sub-note adopted parent-span-class routing as a one-off.

**The residual ambiguity (finding (b)):** the prefix `mcp.` on the attribute name is in tension with the parent-span-class `sandbox.*` ingestion routing. §C-OD-08 namespace collision discipline does NOT currently arbitrate this case — its rules (no-override invariant + OTel-canonical-value + no-rename) govern naming/precedence between additive layers and OTel canonical layer, not ingestion-row ownership for cross-namespace attributes on a single span.

If a second specialization-namespace co-emission case lands (e.g., `topology.*` attribute on `sandbox.exit` span, or `audit.*` attribute on `hitl.invocation.responded` span), the parent-span-class rule from v1.13 sub-note will need to be re-applied case-by-case — or canonicalized at §C-OD-08. (Note: OTel canonical `gen_ai.*` attributes are out of scope here — they live at §C-OD-04 base layer, NOT §C-OD-05 specialization rows; routing rule applies only to specialization-namespace co-emission.)

### §1.3 The CXA-side posture (NOT a fork target)

CXA v2.12 §0.4-shape convention seam declaration (NEW at v2.12 per AS-4 dual-attribute cascade fork) handles the spec ↔ spec citation discipline at the CXA convention-level layer. The CXA cardinality is already at coherent posture (100/30/48/24). Finding (b) is purely at OD axis ingestion-routing canonicalization layer; CXA does NOT need amendment under any §6 reading.

### §1.4 ADR-D6 reference frame (X-AL-3 foreclosed)

ADR-D6 v1.2 §1.2 Namespace collision discipline is the upstream anchor for §C-OD-08. Extending §C-OD-08 with a new sub-section authoring ingestion-row arbitration would be an additive specification — NOT an ADR amendment — preserving X-AL-3 (Meta-Architecture §7.7) at this fork.

---

## §2 — The structural question

When an attribute uses namespace-prefix-A (e.g., `mcp.*`) but is emitted on a span-class-B (e.g., `sandbox.violation`, under `sandbox.*` namespace pull), which §C-OD-05 §5.1 row owns the OD audit-ledger ingestion contract?

**Reading A** — Parent-span-class rule canonicalized at §C-OD-08 (NEW sub-section §8.4). v1.13 row-10 sub-note becomes a worked example; future cross-namespace co-emission cases inherit the canonical rule automatically.

**Reading B** — Status-quo. v1.13 sub-note is sufficient as a one-off precedent. §C-OD-08 unchanged. Close finding (b) as WON'T-FIX with rationale: production emits both attrs correctly; no consumer dispatches on attribute-prefix; structural ambiguity is theoretical.

**Reading C** — Dual-row ingestion canonicalized at §C-OD-08 (NEW sub-section §8.4). `mcp.fail.class` on `sandbox.violation` ingested via BOTH row 4 (`mcp.*` attribute-prefix) AND row 10 (`sandbox.*` parent-span). §C-OD-08 §8.4 authors cross-row coordination discipline (e.g., row-priority on collision, attribute-set partitioning between rows).

**Reading D** — Downgrade classification. Finding (b) is doc-hygiene / informational (Class 3), not architectural. Log at Phase 7 execution log + `Canonical_Substrate_Inventory.md`; no spec amendment owed. The v1.13 sub-note IS the canonicalization; finding (b) overstates the residual concern.

---

## §3 — Production-state empirical verification (2026-05-26 at HEAD `0c22efc`)

| Verification | Result |
|---|---|
| `_emit_sandbox_violation` emits both `mcp.fail.class` + `sandbox.fail.class` on `sandbox.violation` span | ✓ verified at `runtime_tool_dispatcher.py:280-282` |
| Production consumer reads `mcp.fail.class` from non-`mcp.tool.call` span | ✗ zero hits (grep across `harness-*/src/`; only test assertions read the attribute) |
| OD-side `namespace_map.py` dispatches per-attribute on namespace prefix | ✗ structural reference table only (NamespaceMapRow tuples); no ingestion routing logic |
| OD-side ingestion-row dispatch on attribute prefix in any consumer | ✗ zero hits (`cp_source_namespace_verification.py` + `as_source_namespace_verification.py` are set-membership verifiers, not per-attribute routers) |
| Tests assert `sandbox.violation` span carries both attrs | ✓ `test_lifecycle_runtime_tool_dispatcher.py:542-630` (4 assertions per fail-class) |

**Inference:** finding (b) is doc-coherence layer. No production behavior depends on the §C-OD-08 canonicalization choice. This empirical posture biases toward Reading B or Reading D.

---

## §4 — Authority chain

| Layer | Artifact | Section |
|---|---|---|
| ADR | ADR-D6 v1.2 §1.2 | Namespace collision discipline (anchor for C-OD-08) |
| ADD | `Architectural_Design_Document_v1_3.md` | §2.4 Synthesis (sandbox.tier / sandbox.tech / sandbox.fail.class three-attribute structural anchor) |
| Spec (OD) | `Spec_Operational_Discipline_v1_13.md` §C-OD-08 §8.1-§8.3 | Current collision discipline — naming/override only |
| Spec (OD) | `Spec_Operational_Discipline_v1_13.md` §C-OD-05 §5.1 row 10 sub-note | v1.13 NEW sub-note — parent-span-class rule worked example |
| Spec (AS) | `Spec_Action_Surface_v1.md` v1.6 §15.9 + §15.10 | Producer-side dual-attribute discipline; downstream-absorption item (i) frames `mcp.fail.class` as `sandbox.*`-row at attribute layer |
| Spec (CXA) | `Cross_Axis_Composition_Document_v2_12.md` §0.4 | Convention-level seam declaration (AS §15.9 ↔ OD §C-OD-05 row 10) |
| Production | `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:261-282` | `_emit_sandbox_violation` helper — emits both attrs |

---

## §5 — Scope discipline

**In-scope at this fork (PROPOSED):**

- (a) Classification of finding (b) — Class 1 / Class 2 / Class 3 / no-fork-needed
- (b) Selection between Reading A / B / C / D
- (c) Scope discrimination if Reading A or C selected — §C-OD-08 sub-section authoring locus + ingestion-row coordination text
- (d) Apply-timing discrimination — paired-publication / split-arc / defer

**Out-of-scope at this fork (FM-2 + X-AL-3):**

- AS spec amendment (producer side is canonical; this fork is consumer-routing layer only)
- CXA amendment (v2.12 §0.4 already handles spec ↔ spec citation discipline)
- ADR-D6 amendment (X-AL-3 foreclosed)
- Resolution of other OD spec v1.13 adjacent findings (a) / (c) / (d) — those carry under their own future arcs

---

## §6 — Operator AskUserQuestion ambiguities

**Q0 — Classification.** Is finding (b) a Class 1 halt-execution fork, Class 2 in-execution operator decision, Class 3 informational observation, or no-fork-needed (the v1.13 sub-note IS the canonicalization and finding (b) overstates the residual)?

- (i) Class 1 — halt-execution defect requiring design-phase routing
- (ii) Class 2 — in-execution operator decision routing to a §C-OD-08 amendment arc
- (iii) Class 3 — informational, log and close
- (iv) no-fork-needed — close finding (b) as resolved at v1.13 sub-note

**Q1 — Reading selection (if Q0 = Class 1 or Class 2).** Which reading?

- (A) Reading A — Parent-span-class rule canonicalized at §C-OD-08 NEW §8.4
- (B) Reading B — Status-quo. WON'T-FIX with rationale
- (C) Reading C — Dual-row ingestion canonicalized at §C-OD-08 NEW §8.4
- (D) Reading D — Downgrade to Class 3 (equivalent to Q0 = Class 3)

**Q2 — Scope (if Q1 = A or C).** §C-OD-08 amendment locus shape:

- (α) Single NEW §8.4 sub-section authoring the canonical rule + worked example (small footprint)
- (β) §8.4 sub-section + §C-OD-05 §5.1 row 4 + row 10 cross-row coordination note (medium footprint)
- (γ) §8.4 sub-section + §C-OD-05 cross-row coordination + §C-OD-06 lifecycle event mapping note for cases where cross-namespace co-emission surfaces lifecycle events (large footprint)

**Q3 — Apply timing (if Q1 = A or C).** When?

- (a) Ratify-apply-now (single-session, paired with this filing) per `[[fm2-deferred-cascade-paired-publication]]` precedent
- (b) Ratify-now, apply at next operator-discretion arc (split, fresh context window)
- (c) Defer ratification + apply to next session

**Q4 — Empirical-state weight.** Production emits both attrs correctly + no consumer dispatches on attribute-prefix. Does this empirical posture bias toward Reading B/D over A/C?

- (i) Yes — finding (b) is doc-hygiene only; Reading B or D is appropriate
- (ii) No — spec-coherence canonicalization is load-bearing for future cross-namespace co-emission cases that may not yet exist; Reading A or C is appropriate
- (iii) Mixed — adopt Reading A or C BUT document the empirical-state inference at the §C-OD-08 §8.4 footer as rationale

---

## §7 — Adjacent findings (NOT-PATCHED at this filing per FM-2)

(a) **OD spec v1.13 finding (a) — `sandbox.*` namespace cardinality drift.** AS spec v1.6 §15.9 extends `sandbox.*` to 7 attrs + co-emission of `mcp.fail.class`; OD spec v1.2 §C-OD-05 row 10 cite-shape says "6-attribute" implicitly. Pre-existing at v1.2; OWED at separate apply-pass arc.

(b) **OD spec v1.13 finding (c) + (d) — Tension 004 D-2/D-3/D-4 carries + `gen_ai.system` vs `gen_ai.provider.name` divergence.** Unchanged carries from v1.12; OWED at their own future arcs.

(c) **CXA v2.12 §0.5 findings.** Four findings (mcp.* cross-emission framing duplicated as (a); schema_violation → policy_override HIGH semantic stretch; gen_ai.system divergence; `_PROVIDER_OPERATIONS` non-§4.2-conformance). Carried at CXA layer; OWED at future operator-discretion arcs.

(d) **AS plan v1.4 §3 (a) HIGH semantic stretch.** Future ADR-D2 / F4 enum revision arc per X-AL-3 + FM-2.

---

## §8 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_mcp_namespace_cross_emission_ingestion_ownership.md` |
| Filed | 2026-05-26 |
| Authoring authority | Operator-invocation "open arc on adjacent finding 1(b)" 2026-05-26 (post-AS-4 dual-attribute cascade close at `0c22efc`) |
| Detection mode | OD spec v1.13 §"Adjacent observations" finding (b) + v1.13 successor-cell forward-cite |
| Empirical-verification | `grep -rn "mcp.fail.class"` across `harness-*/src/` — zero non-`runtime_tool_dispatcher.py` producer hits; zero non-test consumer hits; OD-side `namespace_map.py` is structural reference, not router |
| Advisor trigger | 12th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — advisor caught Class 1 over-classification risk before any spec edit |
| Status | **RATIFIED-AND-APPLIED 2026-05-26** |
| Ratification | Q0 = Class 2; Q1 = Reading A (parent-span-class rule); Q2 = (α) single NEW §8.4; Q3 = (a) ratify-apply-now; Q4 = mixed (ii) empirical-state footer. Q1 + Q4 deferred to assistant recommendation; Q0 + Q2 + Q3 directly ratified by operator. |
| Apply pass | OD spec v1.13 → v1.14: NEW §C-OD-08 §8.4 sub-section authoring parent-span-class ingestion routing rule + v1.13 row 10 sub-note as worked example + empirical-state footer noting no consumer currently routes on attribute-prefix at OD ingestion. |
| Predecessor | `class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` (RATIFIED-AND-APPLIED 2026-05-26) — finding (b) was explicitly carried at that fork's apply-pass as NOT-patched per FM-2 |
| Successor | OD spec v1.14 closes the §C-OD-08 canonicalization residual. Remaining v1.13 adjacent findings (a)/(c)/(d) carry; CXA §0.5 findings carry; AS plan v1.4 §3 (a) carries — all owed at their own future arcs per FM-2. |
