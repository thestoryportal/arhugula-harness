# Cross-Axis Composition Document (v2.12)

*Delta over v2.11. v2.12 declares a second spec-level cross-axis citation convention seam: the AS spec v1.6 §15.9 dual-attribute `sandbox.violation` co-emission discipline (`mcp.fail.class` co-emitted with `sandbox.fail.class`) cross-references OD spec v1.13 §C-OD-05 §5.1 row 10 sub-note as the canonical ingestion-contract owner. This is a convention-level seam (spec ↔ spec citation discipline), NOT a typed runtime edge — no aggregate matrix change, no per-axis attribution change, no new cross-axis cascade at the runtime layer. Mirrors the v2.11 §0.4 alias-term convention seam shape. All v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.11 → v2.12)

### §0.1 Revision context — AS §15.9 dual-attribute co-emission ↔ OD §C-OD-05 row 10 sub-note ingestion-contract spec-level seam

Per `.harness/class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §6 operator-ratified 2026-05-26 Option A (paired single-arc: OD §C-OD-05 sub-note + CXA §0.4-shape convention seam):

- **AS spec v1.5 → v1.6** introduced dual-attribute co-emission discipline at §15.9: the `sandbox.violation` child span carries both `sandbox.fail.class` (per F4 process-execution taxonomy at C-AS-04 §4.1) AND `mcp.fail.class` (per `MCPInvocationFailClass` MCP-protocol-layer taxonomy at C-AS-15 §15.8) when an MCP-protocol-layer failure surfaces a sandbox violation. AS spec v1.7 preserved §15.9 verbatim.
- **OD spec v1.12 → v1.13** acknowledges the dual-attribute discipline at §C-OD-05 §5.1 row 10 (NEW sub-note) — the OD audit-ledger ingests both attributes; the dual-attribute co-emission is structural for cross-layer audit-ledger continuity per AS §15.10 best-effort projection table.
- **Architectural ownership**: AS axis owns the dual-attribute co-emission discipline at the producer (sandbox runtime); OD axis owns the ingestion contract at the consumer (audit-ledger). Future ADR-D2 / F4 enum revision MAY add a F4 `contract_violation` value to absorb the projection's HIGH semantic stretch (out-of-scope per X-AL-3 + FM-2 at v2.12).

The Option A ratification creates a spec-level cross-axis citation seam: AS spec body cites OD spec body's ingestion contract via the dual-attribute discipline; OD spec body cites AS spec body's co-emission discipline via the §C-OD-05 sub-note. The seam is bidirectional at the spec-citation layer.

### §0.2 Scope of v2.12 amendment

v2.12 is a **convention-declaration amendment**, not a typed-edge amendment (matches v2.11 §0.2 shape):

- **NEW §0.4 sub-section** — declares the spec-level seam at a documentation layer
- **Aggregate matrix at §2.1**: UNCHANGED (100 typed edges; 30 genuine; 24 phase-2-runtime — v2.11 cardinality preserved)
- **Per-axis attribution at §2.4**: UNCHANGED (no new runtime edge; convention-level citation seams are not counted at axis-attribution layer)
- **§2.3.x per-bucket enumerations**: UNCHANGED (no row added at any §2.3.x bucket — the seam is convention-level, not a typed runtime edge between atomic units)
- **Convention-level sub-total at §2.1**: 47 → 48 (one new convention-level seam declared at §0.4)

All other v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.

### §0.3 Why this is convention-level, not typed (per fork §6 Q2 ratification)

A typed cross-axis seam in this document's enumeration carries (a) a producer atomic unit, (b) a consumer atomic unit, (c) a typed payload schema, and (d) a runtime data-flow direction.

The AS §15.9 ↔ OD §C-OD-05 row 10 sub-note seam is **convention-level** because:

1. **Best-effort projection framing at AS §15.10.** The AS amendment explicitly frames the MCP-shape → F4-shape projection as best-effort (HIGH semantic stretch acknowledged at row 3). The amendment is NOT claiming a typed-edge-shaped runtime invariant — it is documenting a structural correspondence for audit-ledger continuity.

2. **No new producer or consumer atomic unit.** The producer (sandbox runtime emitting `sandbox.violation` span at AS axis) and consumer (OD audit-ledger ingesting `sandbox.*` namespace) are pre-existing atomic units with pre-existing runtime data flow. The dual-attribute discipline extends the attribute set on an existing span; it does NOT introduce a new atomic unit or a new runtime data flow.

3. **No new runtime data-flow direction.** The OD ingestion path for `sandbox.violation` was already enumerated at the existing `sandbox.*` namespace ingestion row (§C-OD-05 row 10 in the v1.2-lineage table). The dual-attribute discipline modifies the *attribute payload* on that pre-existing edge; it does NOT introduce a new edge.

Per fork §6 Q2, operator ratified convention seam (Option A) over typed edge (Option B). The ratification rationale at fork §4 noted: (i) AS-side amendment shape is best-effort projection, not typed-edge invariant; (ii) precedent at v2.11 §0.4 alias-term seam (also convention-level); (iii) cardinality refresh footprint at Option B was non-trivial and disproportionate to the amendment's structural weight.

### §0.4 NEW spec-level seam declaration

| Producer side | Consumer side | Seam shape | Authority anchor |
|---|---|---|---|
| **AS spec v1.6 §15.9** (dual-attribute co-emission on `sandbox.violation` child span: `sandbox.fail.class` + `mcp.fail.class`) | **OD spec v1.13 §C-OD-05 §5.1 row 10 sub-note** (canonical ingestion-contract for the dual-attribute discipline at the OD audit-ledger) | Spec-vs-spec citation convention. AS spec cites OD ingestion contract via the dual-attribute discipline (AS §15.9 producer side); OD spec cites AS co-emission discipline via the §C-OD-05 row 10 sub-note (OD §5.1 row 10 consumer side). No NEW runtime data flow; modifies attribute payload on a pre-existing edge. No NEW atomic-unit consumer. | `.harness/class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §6 operator-ratified 2026-05-26 Option A |

**Pre-existing typed edge that the convention seam annotates** (informative; NOT a NEW edge at v2.12):

- Runtime data flow: AS sandbox runtime emits `sandbox.violation` span with `sandbox.*` namespace attributes → OD audit-ledger ingests `sandbox.*` namespace per AS C-AS-15 §15.4 always-sampled discipline + OD C-OD-05 §5.1 row 10 ingestion-contract.
- v2.12 convention seam annotates this pre-existing edge with: "the attribute payload at this edge carries the dual-attribute co-emission discipline per AS §15.9 + OD §5.1 row 10 sub-note when an MCP-protocol-layer failure surfaces."

### §0.5 Adjacent observations (NOT patched per FM-2)

(a) **`mcp.*` namespace cross-emission on non-`mcp.tool.call` spans.** OD spec v1.13 §"Adjacent observations" (b) flagged the cross-emission of an `mcp.*`-named attribute on a non-`mcp.tool.call` span as a namespace-boundary observation. CXA v2.12 inherits the framing: the dual-attribute seam at §0.4 does NOT promote `mcp.*` ingestion onto the `sandbox.violation` span — the `mcp.fail.class` attribute is `sandbox.*`-row-ingested (per the parent span's namespace classification). Future operator-discretion arc MAY surface this as a namespace ownership ambiguity at §2.3.6 AS↔OD edge enumeration if the discrimination becomes load-bearing for downstream runtime behavior; NOT patched at v2.12 per FM-2.

(b) **`schema_violation → policy_override` HIGH semantic stretch (AS §15.10 row 3).** Fork §5 + AS plan v1.4 §3 (a) flagged the projection stretch as acknowledged spec-internal and owed at future ADR-D2 / F4 enum revision arc. v2.12 does NOT touch the ADR-D2 reference frame per X-AL-3 + FM-2.

(c) **`gen_ai.system` vs `gen_ai.provider.name` divergence at production** (OD spec v1.12 §"Adjacent observations" (f); CXA v2.11 §0.5 (b)). Unchanged at v2.12; separate apply-pass arc owed.

(d) **`_PROVIDER_OPERATIONS` non-§4.2-enum-conformance at production** (runtime spec v1.27 adjacent observation; CXA v2.11 §0.5 (c)). Unchanged at v2.12; separate apply-pass arc owed.

### §0.6 Status

Proposed (v2.11) → **Proposed (v2.12)**. v2.12 is an additive convention-declaration amendment — one new convention-level seam at §0.4. No aggregate matrix change; no typed-edge change; no per-axis attribution change; no cross-axis cascade at runtime layer.

### §0.7 Downstream artifacts requiring absorption

Cross-file back-references — flagged for downstream absorption; not all owed at this v2.12 publication:

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 CXA row | v2.11 → v2.12 row update | This session (sibling commit) |
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.12 → v1.13 row update | This session (sibling commit) |
| AS plan v1.4 §3 (b) + (c) FM-2 deferral declarations | Status update: RESOLVED at fork ratification + this apply-pass arc | Operator-discretion (AS plan v1.4 → v1.5 delta-only change-note OR fork doc §8 closure block) |
| `harness-cxa/CLAUDE.md` (if it cites CXA version) | v2.11 → v2.12 cite refresh if applicable | Operator-discretion |
| Per-axis `harness-{as,cp,od}/CLAUDE.md` (if any cite CXA §2.x convention-level sub-total 47) | Cite refresh to 48 if applicable | Operator-discretion |

---

## §1 Filing footer

| Field | Value |
|---|---|
| Version | v2.12 (delta-only convention-declaration amendment; v2.11 file preserved verbatim per delta-only convention) |
| Trigger | `.harness/class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §6 operator-ratified 2026-05-26 Option A (paired single-arc: OD §C-OD-05 sub-note + CXA §0.4-shape convention seam); co-published with OD spec v1.12 → v1.13 amendment (sibling commit this session) |
| Scope of revision | NARROW: NEW §0.4 spec-level seam declaration ONLY |
| Sections revised | NEW §0.4 |
| Sections preserved verbatim | All v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content |
| Aggregate matrix delta | None |
| Per-axis attribution delta | None |
| §2.3.x per-bucket enumeration delta | None |
| Convention-level sub-total delta | 47 → 48 (at §2.1 aggregate sub-total) |
| Cross-axis cascade | None at runtime layer; spec-level only |
| Authority anchor | AS spec v1.6 §15.9 + OD spec v1.13 §C-OD-05 §5.1 row 10 sub-note + fork §6 Option A |
| Predecessor | `Cross_Axis_Composition_Document_v2_11.md` (preserved verbatim outside the §0.4 NEW declaration) |
| Successor | v2.13 (next operator-discretion arc; candidates: other adjacent findings absorption per §0.5 (a)/(b)/(c)/(d); other operator-ratified amendments) |
