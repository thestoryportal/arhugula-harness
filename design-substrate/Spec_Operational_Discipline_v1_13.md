# Specification — Operational Discipline v1.13

## Change-note (v1.12 → v1.13)

**Scope of revision.** AS-4 dual-attribute `sandbox.violation` OD/CXA ingestion cascade Class 1 fork resolution apply pass per `.harness/class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §6 (operator-ratified 2026-05-26 option A — paired single-arc: OD §C-OD-05 sub-note + CXA §0.4-shape convention seam). NEW §C-OD-05 `sandbox.*` row sub-note acknowledging the AS spec v1.6 §15.9 dual-attribute co-emission discipline (`mcp.fail.class` co-emitted with `sandbox.fail.class` on the `sandbox.violation` child span when an MCP-protocol-layer failure surfaces a sandbox violation).

**Narrow-scope framing (explicit).** The arc lands ONLY the §C-OD-05 sub-note. The dual-attribute discipline is classified as **substrate-layer namespace ingestion footnote**, NOT a lifecycle-event classification — §C-OD-06 §6.1 is PRESERVED VERBATIM at v1.13 per the operator-ratified Option A scope. The discrimination between substrate-layer (§C-OD-05) and contract-layer (§C-OD-06) was an explicit fork ambiguity at §6 Q1; operator selected substrate-layer per Option A.

---

## §C-OD-05 `sandbox.*` namespace ingestion row — sub-note amendment (v1.13 NEW)

### Authority chain

- AS spec v1.6 §15.8 + §15.9 + §15.10 (per fork `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` Reading B arc 1 landing, ratified 2026-05-25) introduced `MCPInvocationFailClass` 4-value StrEnum + `mcp.fail.class` attribute on the `sandbox.violation` child span + best-effort projection table MCP-shape → F4-shape.
- OD spec v1.2 §C-OD-05 §5.1 row 10 (preserved verbatim through v1.12) declares the `sandbox.*` namespace ingestion at the OD audit-ledger via `Spec_Action_Surface_v1.md` C-AS-15 §15.4 cross-axis citation.
- AS-side dual-attribute co-emission discipline lands at AS spec v1.6 §15.9; OD-side ingestion contract at §C-OD-05 row 10 had not been updated to acknowledge the co-emitted `mcp.fail.class` attribute on the same span.
- `.harness/class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §1.2 documented the gap; §6 Q1 ratified Option A (substrate-layer sub-note at §C-OD-05) over Option D (contract-layer §C-OD-06 lifecycle event mapping).

### Amendment text

The v1.2 §C-OD-05 §5.1 row 10 declaration at `design-substrate/Spec_Operational_Discipline_v1_2.md` (preserved verbatim through v1.12) ingests the `sandbox.*` namespace per `Spec_Action_Surface_v1.md` C-AS-15 §15.4 (always-sampled — security-critical). The row remains canonical at v1.13.

**v1.13 sub-note (NEW).** The `sandbox.*` namespace ingestion at OD audit-ledger consumes the `sandbox.violation` child span with **dual-attribute co-emission** discipline per AS spec v1.6 §15.9: the `sandbox.violation` span carries both `sandbox.fail.class` (per F4 process-execution taxonomy at C-AS-04 §4.1) AND `mcp.fail.class` (per `MCPInvocationFailClass` MCP-protocol-layer taxonomy at C-AS-15 §15.8) when an MCP-protocol-layer failure surfaces a sandbox violation. The OD audit-ledger ingests both attributes; the dual-attribute co-emission is structural for cross-layer audit-ledger continuity per AS §15.10 best-effort projection table.

**Ingestion-posture invariants at v1.13.**

1. **Single-attribute case** — when a sandbox violation surfaces from process-execution layer (escape attempt / OOM / signal / exit-nonzero / policy-override / timeout at process layer), only `sandbox.fail.class` is emitted on `sandbox.violation`. OD ingestion path unchanged from v1.2-v1.12.

2. **Dual-attribute case** — when a sandbox violation surfaces from MCP-protocol layer (transport / protocol_error / schema_violation / timeout at MCP layer), both `sandbox.fail.class` (best-effort projection per AS §15.10) AND `mcp.fail.class` (raw MCP-layer fail-class per AS §15.8) are co-emitted on the same `sandbox.violation` span. OD ingestion stores both as separate attributes; audit-ledger queries MAY join on either or both per consumer discretion.

3. **Best-effort projection acknowledgement** — AS §15.10 projection table is best-effort (acknowledged HIGH semantic stretch at row 3 `schema_violation → policy_override`). OD audit-ledger DOES NOT re-validate the projection; the raw `mcp.fail.class` attribute is the canonical MCP-layer fail-class declaration; `sandbox.fail.class` is the projection into F4 for cross-layer continuity. Future ADR-D2 / F4 enum revision MAY add a F4 `contract_violation` value to absorb the semantic stretch cleanly (out-of-scope at v1.13 per FM-2 + X-AL-3).

### Cross-axis ingestion path (informative)

```
AS (sandbox runtime) emits sandbox.violation span
  ├── sandbox.fail.class       (F4 process-execution projection — best-effort per AS §15.10)
  └── mcp.fail.class           (MCPInvocationFailClass raw — per AS §15.9 dual-attribute discipline)
    │
    ▼
OD audit-ledger ingests sandbox.* namespace per C-OD-05 §5.1 row 10
  → both attributes stored on the audit-ledger entry for the violation span
  → audit-ledger queries (per C-OD-10 §10.4) MAY join on either or both attribute values
  → always-sampled per AS C-AS-15 §15.4 + OD C-OD-05 §5.3 ingestion-posture invariants
```

The ingestion path is **substrate-layer** — no new lifecycle event class is introduced at §C-OD-06. The MCP-protocol-layer failure is treated as a fail-class projection into the existing `sandbox.violation` lifecycle event, NOT as a new lifecycle event class.

---

## Sections preserved verbatim at v1.13

Per FM-2 no-extension discipline + Option A narrow scope, the v1.13 amendment touches ONLY §C-OD-05 §5.1 row 10 sub-note. The following sections are PRESERVED VERBATIM from their authoring versions through v1.13:

- §C-OD-04 §4.1 (canonical-reading amendment at v1.12 — preserved verbatim at v1.13)
- §C-OD-04 §4.2 / §4.3 / §4.4 / §4.5 (v1.2 — preserved verbatim through v1.13 per delta-only convention)
- §C-OD-05 §5.1 rows 1-9 + rows 11-15 (v1.2 — preserved verbatim; only row 10 sub-note added at v1.13)
- §C-OD-05 §5.2 + §5.3 (ingestion-posture invariants; F2-12 forward-compatibility note — preserved verbatim)
- **§C-OD-06 (F3 capability-floor (iv) lifecycle event-to-span-event mapping) — PRESERVED VERBATIM at v1.13 per Option A ratification (Option D §6.1 new row was explicitly NOT-SELECTED at fork §6 Q1)**
- §C-OD-07 through §C-OD-33 (all v1.2-v1.11 lineage content preserved per delta-only-spec-file convention)
- All v1.3 through v1.12 substantive amendments

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **`sandbox.*` namespace cardinality drift.** AS spec v1.2 §15.1 documented 6-attribute `sandbox.*` namespace; AS spec v1.6 §15.9 extends to 7 attributes (`sandbox.tier`, `sandbox.tech`, `sandbox.provider`, `sandbox.fail.class`, `sandbox.policy.assigned_tier_reason`, `sandbox.cost.tier_overhead_ms`, `sandbox.cost.tier_overhead_usd`) PLUS the `sandbox.violation`-span-specific co-emission of `mcp.fail.class`. OD spec v1.2 §C-OD-05 §5.1 row 10 cite-shape currently says "6-attribute" implicitly via AS §15.4 reference. The cite-shape ambiguity is pre-existing at v1.2 and NOT patched at v1.13 per FM-2 — owed at a separate apply-pass arc if operator routes a §C-OD-05 row 10 cardinality refresh.

(b) **`mcp.*` namespace cross-emission on non-mcp-tool-call spans.** The AS §15.9 amendment introduces `mcp.fail.class` on the `sandbox.violation` span — a span outside the `mcp.tool.call` namespace surface. OD spec v1.2 §C-OD-05 §5.1 row 4 declares `mcp.*` namespace ingestion via `Spec_Action_Surface_v1.md` C-AS-14 §14.8 (`mcp.tool.call` span family). The cross-emission of an `mcp.*`-named attribute on a non-`mcp.tool.call` span (`sandbox.violation`) is a namespace-boundary observation; AS §15.9 frames this as a co-emission discipline (NOT a namespace re-classification). OD ingestion path at v1.13 sub-note treats the `mcp.fail.class` attribute as `sandbox.*`-row-ingested (per the parent span's namespace classification at `sandbox.violation`), NOT as `mcp.*`-row-ingested. Future operator-discretion arc MAY surface this as a namespace ownership ambiguity worth explicit discrimination at §C-OD-08 namespace collision discipline; NOT patched at v1.13 per FM-2.

(c) **Tension 004 D-2/D-3/D-4 carries.** OD spec v1.12 §"Adjacent observations" (a)/(b)/(c) flagged the Tension 004 enum cardinality / attribute tiers / base metric divergences as unresolved. v1.13 does NOT touch §C-OD-04 §4.2/§4.3/§4.5 — those carries remain at v1.13 per the narrow Option A scope.

(d) **`gen_ai.system` vs `gen_ai.provider.name` divergence.** OD spec v1.12 §"Adjacent observations" (f) flagged the attribute-name divergence at production. v1.13 does NOT touch this carry.

---

## Downstream artifacts requiring absorption at follow-on arcs

Cross-file back-references (per spec-writer skill §5) — flagged for downstream absorption; NOT touched at this v1.13 spec arc:

| Artifact | Required change | Owner |
|---|---|---|
| `Cross_Axis_Composition_Document_v2_12.md` (NEW this session) | NEW §0.4-shape convention seam declaration: AS spec v1.6 §15.9 ↔ OD spec v1.13 §C-OD-05 row 10 sub-note. §2.1 convention-level sub-total 47 → 48. | This session apply-pass arc (sibling commit per fork §6 Q3 Option A paired publication) |
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.12 → v1.13 row update | This session apply-pass arc |
| Workspace `CLAUDE.md` §2.3 CXA row | v2.11 → v2.12 row update | This session apply-pass arc |
| AS plan v1.4 §3 (b) + (c) FM-2 deferral declarations | Status update: RESOLVED at fork ratification + this apply-pass arc | Operator-discretion (AS plan v1.4 → v1.5 delta-only change-note OR fork doc §8 closure block) |
| `harness-od/CLAUDE.md` cross-axis citation table | NO change owed (Option A convention-level seam does not require per-axis CLAUDE.md edge enumeration update per CXA v2.11 §0.2 "Per-axis attribution UNCHANGED" precedent) | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.13 (canonical-reading amendment to v1.2 §C-OD-05 §5.1 row 10 — NEW sub-note; v1.2 file PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | `.harness/class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §6 (operator-ratified 2026-05-26 Option A — paired single-arc: OD §C-OD-05 sub-note + CXA §0.4-shape convention seam) |
| Supersedes | None — additive sub-note acknowledging AS spec v1.6 §15.9 dual-attribute co-emission discipline at the OD ingestion contract layer |
| Scope of revision | NARROW: §C-OD-05 §5.1 row 10 sub-note ONLY |
| Sections revised | §C-OD-05 §5.1 row 10 (NEW sub-note on dual-attribute co-emission) |
| Sections preserved verbatim | §C-OD-04 §4.1/§4.2/§4.3/§4.4/§4.5; §C-OD-05 §5.1 rows 1-9 + 11-15; §C-OD-05 §5.2 + §5.3; **§C-OD-06 (explicitly preserved per Option A ratification);** §C-OD-07..§C-OD-33; all v1.3-v1.12 substantive amendments |
| Adjacent findings surfaced | 4 (per "Adjacent observations" section above); NOT patched per FM-2 |
| Cross-file absorption owed | 4 artifacts (per "Downstream artifacts" table above) — 3 owed at this session apply-pass arc (CXA v2.12 + workspace CLAUDE.md rows), 1 owed at operator-discretion (AS plan v1.4 §3 (b)+(c) status update) |
| Authority anchor | AS spec v1.6 §15.8 + §15.9 + §15.10 (Reading B arc 1 ratified 2026-05-25); fork `class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §6 (operator-ratified 2026-05-26 Option A) |
| Predecessor | v1.12 (GenAI span-name format §4.1 amendment — preserved verbatim outside §C-OD-05 §5.1 row 10) |
| Successor | v1.14 (next operator-discretion arc — candidates: Tension 004 D-2/D-3/D-4 absorption per v1.12 (a)/(b)/(c) carries; or §C-OD-08 namespace collision discrimination per v1.13 adjacent finding (b)) |
