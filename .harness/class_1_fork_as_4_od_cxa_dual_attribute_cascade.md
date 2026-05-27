# Class 1 Fork — AS-4 dual-attribute `sandbox.violation` OD/CXA ingestion cascade

**Filed:** 2026-05-26 (post-batch-19 AS-4 RETIRED close; AS plan v1.4 §3 adjacent-cascades patch arc)
**Status:** **RATIFIED-AND-APPLIED 2026-05-26** — operator ratified Option A (paired single-arc: OD §C-OD-05 sub-note + CXA §0.4-shape convention seam) at §6 Q1+Q2+Q3 + ratify-apply-now timing at Q4; applied at OD spec v1.12 → v1.13 + CXA v2.11 → v2.12 same session.
**Halt target:** AS plan v1.4 §3 (b) + (c) FM-2-deferred cascades — patch arc cannot proceed without operator routing decisions at §6
**Routing target:** OD spec v1.12 → v1.13 (§C-OD-05 namespace ingestion OR §C-OD-06 lifecycle event mapping — discrimination owed) + CXA v2.11 → v2.12 (§2.3.6 AS↔OD edge enumeration — typed vs convention discrimination owed). Out-of-scope: AS plan v1.4 §3 (a) HIGH semantic stretch (acknowledged spec-internal projection — owed at future ADR-D2 / F4 enum revision arc) + (d) ADR-D2 §1.7.X reference frame (X-AL-3 foreclosed — out-of-scope at Phase 7).
**Detection mode:** Session-open survey of FM-2-deferred adjacent cascades after batch-19 AS-4 close; advisor-flagged scope sanity before direct spec/CXA edits.

---

## §1 — Empirical-verification details

### §1.1 The AS-side amendment (LANDED at AS spec v1.6, preserved at v1.7)

AS spec v1.6 §15.8 + §15.9 + §15.10 (per fork `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` Reading B arc 1 landing, ratified 2026-05-25):

- §15.8 NEW `MCPInvocationFailClass` 4-value StrEnum (`transport` / `protocol_error` / `schema_violation` / `timeout`) — MCP-protocol-layer fail-class taxonomy, sibling to F4 process-execution taxonomy at C-AS-04 §4.1.
- §15.9 NEW `mcp.fail.class` attribute on the `sandbox.violation` child span — **dual-attribute emission discipline** with §15.2 row 3 `sandbox.fail.class` (both attrs co-emitted on the same span when an MCP-protocol-layer failure surfaces a sandbox violation).
- §15.10 NEW best-effort projection table MCP-shape → F4-shape for cross-layer audit-ledger continuity.

Production landing at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` (`_emit_sandbox_violation` helper) opens `sandbox.violation` child span with both attributes when an `MCPInvocationFailClass` failure projects onto the F4 enum.

### §1.2 The OD-side gap (NOT patched at OD spec v1.12)

OD spec v1.11 → v1.12 amendment scope was narrow per FM-2 (GenAI span-name format fork only). The dual-attribute `sandbox.violation` ingestion is undocumented at OD axis:

- **§C-OD-05 namespace ingestion table:** declares 15 namespaces consumed by the OD audit-ledger. Row for `sandbox.*` (per `Spec_Action_Surface_v1.md` C-AS-15 §15.4) currently documents only single-attribute `sandbox.fail.class` (per v1.2 lineage preserved through v1.12). The co-emitted `mcp.fail.class` on the same span is silent at OD axis.
- **§C-OD-06 lifecycle event mapping:** F3 capability-floor (iv) lifecycle event-to-span-event mapping; does not currently enumerate MCP-protocol-layer failure as a lifecycle-event source.

Empirical grep across `design-substrate/Spec_Operational_Discipline_v1*.md`: zero hits on `mcp.fail.class` (the attribute landed at AS axis 2026-05-26 and has not yet propagated to OD).

### §1.3 The CXA-side gap (NOT patched at CXA v2.11)

CXA v2.11 §2.3.6 currently enumerates **10 inbound AS→OD edges** (AS axis emitting into OD audit-ledger / observability ingestion). The `sandbox.violation` event is consumed via the existing `sandbox.*` namespace pull. The dual-attribute co-emission discipline at AS §15.9 is structurally:

- **either** a new edge declaration (cardinality changes; aggregate 100→101; AS→OD inbound 10→11; CXA §2.1 + §2.4 per-axis attribution refresh required),
- **or** a convention-level seam declaration (sub-total at §2.1 47→48; typed-edge counts unchanged; mirrors the §0.4 alias-term seam landed 2026-05-26).

The structural discrimination is undocumented.

### §1.4 ADR-D2 reference frame (X-AL-3 foreclosed)

Fork doc §6 of the AS-4 F4 enum fork notes ADR-D2 v1.2 §1.7 + §1.7.1 reference frame UNCHANGED at AS spec v1.6 amendment — `MCPInvocationFailClass` is AS-spec-internal contract additive, NOT an ADR-D2 §1.7.X declaration site extension. **This fork preserves that posture per X-AL-3 (Meta-Architecture §7.7) no-silent-design-extension at Phase 7 execution.** ADR-D2 §1.7.X extension is out-of-scope here.

---

## §2 — The structural question

When an AS-axis amendment adds a cross-namespace co-emission discipline (`mcp.fail.class` co-emitted with `sandbox.fail.class` on the `sandbox.violation` event), the downstream-axis (OD) ingestion contract and cross-axis (CXA) edge enumeration must absorb the discipline. The structural question is:

**(i)** *Where does the dual-attribute ingestion contract live at OD axis* — §C-OD-05 (namespace ingestion table extends `sandbox.*` row with `mcp.fail.class` co-attribute note) or §C-OD-06 (lifecycle event mapping table gains a new row for MCP-protocol-layer failure as a lifecycle-event source)?

**(ii)** *What is the typed-vs-convention classification of the dual-attribute cross-axis seam at CXA* — new typed edge at §2.3.6 (cardinality aggregate 100→101) or convention-level seam declaration at §0.4-equivalent shape (sub-total §2.1 47→48; typed-edge count preserved)?

**(iii)** *Are (i) and (ii) one paired-publication arc or two independent arcs* — does OD §C-OD-05/06 amendment presuppose CXA edge classification, or can they land independently?

---

## §3 — Routing options

### Option A — Paired single-arc publication (OD §C-OD-05 sub-note + CXA §0.4-shape convention seam)

**Shape:** OD spec v1.12 → v1.13 NARROW: §C-OD-05 `sandbox.*` row extends with footnote/sub-note acknowledging `mcp.fail.class` co-emission discipline per AS spec v1.6 §15.9. CXA v2.11 → v2.12 NARROW: §0.4-equivalent convention-level seam declaration (NOT new typed edge); §2.1 sub-total 47→48; typed-edge count preserved at 30 genuine / 24 phase-2-runtime; aggregate preserved at 100.

**Pros:**
- Mirrors the §0.4 alias-term convention seam pattern landed 2026-05-26 (proven shape).
- Minimal cite-cascade footprint (no per-axis attribution recompute).
- Single ratification arc; clean pairing of OD note + CXA seam.

**Cons:**
- Convention-level seam may under-classify a structural runtime invariant (the dual-attribute discipline IS a typed-edge-shaped relationship between AS-emitter and OD-consumer at runtime).

### Option B — Paired single-arc publication (OD §C-OD-05 sub-note + CXA new typed edge at §2.3.6)

**Shape:** OD spec amendment as Option A. CXA v2.11 → v2.12 declares new typed edge at §2.3.6 row 11; aggregate 100→101; genuine 30→31; AS→OD inbound 10→11; §2.1 + §2.4 per-axis attribution refresh.

**Pros:**
- Honors the structural runtime invariant (dual-attribute co-emission IS a typed edge at runtime).
- Documents the attribute-level co-emission discipline as a first-class cross-axis composition surface.

**Cons:**
- Cardinality refresh footprint is non-trivial (per-axis CLAUDE.md bucket counts at all 4 axis subdirs need bump per the convention established at `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` bucket-count refresh arc `c413d40`).
- Sets precedent for attribute-level co-emission disciplines being typed edges (may trigger sibling-discovery across other co-emission disciplines at AS / CP / OD axes).

### Option C — Independent arcs (OD spec amendment first; CXA discrimination deferred)

**Shape:** OD spec v1.12 → v1.13 NARROW: §C-OD-05 sub-note as Option A. CXA discrimination filed at a separate fork doc; CXA v2.11 preserved verbatim at this arc.

**Pros:**
- Smallest single-arc footprint.
- Preserves CXA discrimination for fresh-context-window ratification (per `[[fork-cp-spec-section-25-contract-id-collision]]` two-arc resolution precedent).

**Cons:**
- Splits a structurally-paired publication across two arcs.
- The OD-side amendment alone is informationally incomplete (an OD consumer reading §C-OD-05 has no CXA-side handle on the typed-vs-convention classification of the source seam).

### Option D — §C-OD-06 lifecycle event mapping path (MCP-protocol-layer failure as F3 lifecycle-event source)

**Shape:** OD spec v1.12 → v1.13 amends §C-OD-06 §6.1 lifecycle event mapping table with a new row enumerating MCP-protocol-layer failure as an F3 capability-floor (iv) lifecycle-event source. CXA-side amendment per Option A or B.

**Pros:**
- More semantically structural than a §C-OD-05 footnote (lifecycle-event mapping is the contract-bearing surface; namespace ingestion is the substrate surface).
- May surface useful cross-axis discrimination between `transport`/`protocol_error`/`schema_violation`/`timeout` as lifecycle events vs. fail-class-only attribute projections.

**Cons:**
- Larger amendment scope at OD axis (§C-OD-06 §6.1 table extension, not a §C-OD-05 footnote).
- May over-classify the discipline (the AS amendment is best-effort projection per §15.10; lifecycle-event classification is a stronger semantic claim than the AS amendment intends).

---

## §4 — Recommendation (sized for systems-architect Mode 3 input)

**Tentative recommendation: Option A — paired single-arc publication (OD §C-OD-05 sub-note + CXA §0.4-shape convention seam).**

**Rationale:**

1. **AS-side amendment shape.** AS spec v1.6 §15.10 explicitly frames the MCP-shape → F4-shape projection as "best-effort" + acknowledges HIGH semantic stretch at row 3 (`schema_violation → policy_override`). The amendment is NOT claiming a typed-edge-shaped runtime invariant — it is documenting a structural correspondence for audit-ledger continuity. A convention-level CXA seam matches the AS-side framing.

2. **Mirroring the §0.4 alias-term convention precedent.** The 2026-05-26 §0.4 cross-axis citation convention seam (AS §14.1 alias-term ↔ OD §C-OD-04 §4.1) landed at CXA v2.11 as a convention-level seam (sub-total §2.1 46→47; typed-edge counts unchanged). The dual-attribute discipline is structurally similar — a cross-axis spec-level contract that does NOT promote to typed runtime edge.

3. **Bucket-count refresh footprint.** Option B requires per-axis CLAUDE.md bucket-count refresh across all 4 axis subdirs (per `c413d40` precedent); Option A does not. Smaller cite-cascade footprint at this arc.

4. **§C-OD-05 vs §C-OD-06 (Option A vs Option D).** §C-OD-05 is the namespace ingestion table (substrate surface); §C-OD-06 is the F3 lifecycle event mapping (contract surface). The AS amendment is best-effort projection at the namespace layer, not a lifecycle-event classification. §C-OD-05 footnote is the appropriate amendment site.

**Concerns the architect should weigh:**

- Under-classification risk at Option A (the dual-attribute co-emission IS a structural runtime invariant; convention-level seam may under-document this).
- Precedent risk at Option B (typed-edge precedent for attribute-level co-emission may trigger sibling-discovery cascades across other co-emission disciplines that are currently convention-level).
- Split-arc risk at Option C (informational incompleteness at OD-only arc).

---

## §5 — Cross-axis cascade analysis

**Within this fork's scope:**

| Artifact | Amendment owed | Magnitude |
|---|---|---|
| OD spec v1.12 → v1.13 | §C-OD-05 `sandbox.*` row sub-note (per Option A/B) OR §C-OD-06 §6.1 new row (per Option D) | Narrow — single section amendment |
| CXA v2.11 → v2.12 | §0.4-shape convention seam (per Option A) OR §2.3.6 new typed edge (per Option B) | Narrow if Option A; cardinality refresh footprint if Option B |

**Out-of-this-fork's scope (preserved per FM-2):**

- AS plan v1.4 §3 (a) HIGH semantic stretch — future ADR-D2 / F4 enum revision arc.
- AS plan v1.4 §3 (d) ADR-D2 §1.7.X reference frame — X-AL-3 foreclosed at Phase 7.
- Runtime spec v1.27 finding (g) `_PROVIDER_OPERATIONS` enum-conformance carry (sibling to OD v1.12 finding (f), already STRUCK at v1.27 amendment scope — NOT this fork).

**Per-axis CLAUDE.md updates owed:**

- Workspace `CLAUDE.md` §2.3 OD spec row + CXA row version bumps per ratified option.
- `harness-od/CLAUDE.md` cross-axis citation table row addition (if Option B).
- `harness-as/CLAUDE.md` cross-axis citation table row addition (if Option B).
- `harness-cxa/CLAUDE.md` aggregate counts refresh (if Option B).

---

## §6 — Ambiguities (operator ratification required)

1. **Q1 — §C-OD-05 vs §C-OD-06.** Recommended Option A (§C-OD-05 footnote). Operator selects between Options A/B (§C-OD-05 sub-note) and Option D (§C-OD-06 lifecycle event row).

2. **Q2 — Typed edge vs convention seam at CXA.** Recommended convention seam (Option A). Operator selects between convention seam (Options A/C/D) and typed edge (Option B).

3. **Q3 — Paired vs split arcs.** Recommended paired single-arc (Option A). Operator selects between paired (Options A/B/D) and split (Option C).

4. **Q4 — Timing.** Ratify + apply now (single session continuation), OR defer to a fresh context window per `[[fork-cp-spec-section-25-contract-id-collision]]` two-arc precedent. Recommended: ratify + apply now (scope is narrow at Option A; fresh context not required).

---

## §7 — Filing footer

| Field | Value |
|---|---|
| Filed | 2026-05-26 |
| Filing authority | Operator request to patch AS plan v1.4 §3 adjacent cascades |
| Predecessor cascade-flagging arc | AS plan v1.4 §3 (FM-2 deferral declaration; 2026-05-26 at AS-4 RETIRED close) |
| Predecessor AS-side amendment | AS spec v1.6 (Reading B arc 1 — `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md`) |
| Routing | Operator ratification at §6 → systems-architect Mode 3 recommendation if requested → spec-writer apply pass at ratified option |
| Halt-on-application | OD spec v1.12 + CXA v2.11 + per-axis CLAUDE.md updates blocked until operator ratifies §6 Q1-Q4 — **CLEARED at §8 closure** |

---

## §8 — Closure block (Option A apply-pass LANDED — same session 2026-05-26)

### §8.1 Operator ratification

Operator-ratified 2026-05-26 via AskUserQuestion 2-question dispatch:

- **Q1+Q2+Q3 — Routing option**: A) Paired single-arc, OD §C-OD-05 sub-note + CXA convention seam.
- **Q4 — Timing**: Ratify + apply now (single session continuation).

### §8.2 Apply-pass deltas (this session)

| Artifact | Delta | Magnitude |
|---|---|---|
| OD spec v1.12 → v1.13 (`design-substrate/Spec_Operational_Discipline_v1_13.md` NEW) | Delta-only file: NEW §C-OD-05 §5.1 row 10 sub-note declaring dual-attribute co-emission ingestion-posture invariants (3 invariants); §C-OD-06 §6.1 lifecycle event mapping PRESERVED VERBATIM per Option A ratification; 4 adjacent findings surfaced NOT-patched per FM-2 | ~140 lines NEW file |
| CXA v2.11 → v2.12 (`design-substrate/Cross_Axis_Composition_Document_v2_12.md` NEW) | Delta-only file: NEW §0.4 spec-level seam declaration (AS spec v1.6 §15.9 ↔ OD spec v1.13 §C-OD-05 row 10 sub-note); §2.1 convention-level sub-total 47 → 48; ZERO aggregate matrix change; ZERO typed-edge change; ZERO per-axis attribution change; ZERO §2.3.x per-bucket enumeration change | ~80 lines NEW file |
| Workspace `CLAUDE.md` §2.3 OD row | v1.12 → v1.13 row update; prepended new delta entry; all v1.12-and-earlier history preserved verbatim | 1 row update |
| Workspace `CLAUDE.md` §2.3 CXA row | v2.11 → v2.12 row update; prepended new delta entry; all v2.11-and-earlier history preserved verbatim | 1 row update |
| AS plan v1.4 §3 (b) FM-2 deferral | Status updated inline: RESOLVED at this fork apply-pass arc | 1 line annotation |
| AS plan v1.4 §3 (c) FM-2 deferral | Status updated inline: RESOLVED at this fork apply-pass arc | 1 line annotation |

### §8.3 Out-of-scope items (preserved per §1.4 + §5)

- AS plan v1.4 §3 (a) HIGH semantic stretch — owed at future ADR-D2 / F4 enum revision arc (X-AL-3 + FM-2).
- AS plan v1.4 §3 (d) ADR-D2 §1.7.X reference frame — X-AL-3 foreclosed at Phase 7.
- 4 adjacent findings at OD spec v1.13 §"Adjacent observations" (sandbox.* cardinality drift; mcp.* namespace cross-emission; Tension 004 D-2/D-3/D-4 carries; gen_ai.system vs gen_ai.provider.name divergence) — NOT patched per FM-2.
- 4 adjacent findings at CXA v2.12 §0.5 (mcp.* namespace cross-emission framing; schema_violation HIGH semantic stretch; gen_ai.system divergence; _PROVIDER_OPERATIONS non-§4.2-conformance) — NOT patched per FM-2.

### §8.4 Verification

- ZERO production-code change at this arc (apply-pass is spec-only).
- ZERO test change at this arc.
- ZERO carrier code change at this arc.
- The AS-side amendment (AS spec v1.6 §15.9 dual-attribute discipline) was already empirically landed at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` (`_emit_sandbox_violation` helper) per AS-4 Reading B arc 2 landing 2026-05-25-26; v1.13 OD spec + v2.12 CXA simply absorb the spec-level documentation of the discipline at the OD axis + CXA axis.

### §8.5 Pattern catalogued

**`[[fm2-deferred-cascade-paired-publication]]`** — when an AS-side amendment surfaces an OD-side ingestion-contract gap + a CXA-side edge-classification ambiguity, the patched-cascade scope is a **paired single-arc publication** at the convention-level seam shape (mirrors v2.11 §0.4 alias-term seam precedent). Pattern:

1. **Fork doc first.** File the Class 1 fork doc with §6 ambiguity discriminations (operator ratification surface) — DO NOT silently absorb at the OD/CXA spec edits.
2. **Operator ratifies Option A vs B vs C vs D.** Option A = paired convention seam; Option B = paired typed edge (cardinality refresh footprint); Option C = split arcs; Option D = §C-OD-06 lifecycle path.
3. **Apply at delta-only spec files.** OD spec vN → vN+1 + CXA vM → vM+1 both publish as delta-only files; predecessor files preserved verbatim per delta-only-spec-file convention.
4. **Closure block at fork doc §8.** Document the apply-pass deltas; surface adjacent findings NOT-patched per FM-2; catalogue the pattern.

Sibling to `[[fork-cp-spec-section-25-contract-id-collision]]` (two-arc fork resolution: arc 1 = ratify+apply at canonical spec; arc 2 = cascade-absorption across plans/CLAUDE.md). The dual-attribute cascade is a **single-arc** variant (paired publication closes the cascade in one session) because the cite-cascade footprint at Option A is small (no per-axis CLAUDE.md bucket-count refresh).

### §8.6 Status

**CLOSED-APPLIED 2026-05-26.** AS plan v1.4 §3 (b) + (c) FM-2 deferrals RESOLVED. Adjacent findings at OD spec v1.13 §"Adjacent observations" + CXA v2.12 §0.5 preserved as future operator-discretion arcs per FM-2.
