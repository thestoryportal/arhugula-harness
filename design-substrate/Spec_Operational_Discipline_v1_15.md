# Spec: Operational Discipline — v1.15 (delta over v1.14)

---

## Change-note (v1.14 → v1.15)

**Scope of revision.** Fidelity-pure citation-correction patch closing OD spec v1.13/v1.14 §"Adjacent observations" finding (a) as **phantom-as-described** and applying a canonical-reading amendment at v1.15 to correct row-number + section-cite drift introduced at v1.13 §C-OD-05 sub-note and propagated through v1.14 §C-OD-08 §8.4. ZERO contract change; ZERO signature change; ZERO acceptance-criterion change; ZERO behavior change; ZERO cross-axis cascade. Single-file delta-only-spec-file authoring per established convention.

**Empirical posture (load-bearing).** Per `design-substrate/Spec_Operational_Discipline_v1_2.md` line 333 (preserved verbatim through v1.14 per delta-only-spec-file convention), §C-OD-05 §5.1 row 5 is the canonical `sandbox.*` namespace declaration:

> `| 5 | sandbox.* | ADR-D2 v1.1 §1.7.1 + ADR-F4 v1.1 §Consequences (a); declared at C-AS-15 §15.2 | 7 | C-AS-15 §15.2 | Ingest verbatim under F4-canonical-naming-honored-at-source-D-ADR rule |`

The row declares **7 attributes** with cite to **C-AS-15 §15.2** (attribute table). Row 10 in v1.2 is `audit.*` (line 338), NOT `sandbox.*`. §15.4 in AS spec v1 is the always-sampled events sub-section (`sandbox.violation` + `sandbox.tier_escalation`), NOT the attribute-table declaration site. Both row-number ("row 10") and section-cite ("§15.4") at v1.13 sub-note + v1.14 §C-OD-08 §8.4 are drift from the canonical v1.2 row 5 + §15.2 declaration.

**AS spec attribute-count lineage (empirical-verification).** `design-substrate/Spec_Action_Surface_v1.md` §15.2 declares 7 attributes (line 1320: "Seven `sandbox.*` attribute names"); v1.4 footer note at line 169 + v1.6 framing both reference "the `sandbox.*` 7-attribute namespace" — no 6-attribute lineage exists at AS spec v1 baseline. The v1.13 finding (a) framing ("AS spec v1.2 §15.1 documented 6-attribute `sandbox.*` namespace") is **incorrect at empirical-verification** — AS v1 declared 7 from the v1 baseline; no 6 → 7 cardinality event occurred.

**Routing.** Per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + workspace precedent for inline cite-correction patches (CP spec v1.14 §1.2 cite-shape correction 2026-05-24; runtime spec v1.16 phantom-cite resolution 2026-05-22): fidelity-pure citation correction where empirical posture is conclusive does NOT require a separate fork doc filing. v1.15 applies inline canonical-reading amendment with origin-of-drift documented at adjacent observations (lineage logging, not blame framing). Per delta-only-spec-file convention: v1.13 + v1.14 files PRESERVED VERBATIM; v1.15 authors the canonical-reading amendment table that downstream readers MUST apply when interpreting v1.13 sub-note + v1.14 §C-OD-08 §8.4 sites.

---

## §1 Canonical-reading amendment table (v1.15 NEW)

Per delta-only-spec-file convention, the v1.13 + v1.14 file bodies are PRESERVED VERBATIM. The following table maps every drift site in those files to its corrected canonical reading. Readers of v1.13 + v1.14 MUST apply these substitutions when interpreting row-number + section-cite tokens at the listed sites.

### §1.1 Row-number drift (sandbox.* → row 5)

The v1.13 sub-note + v1.14 §C-OD-08 §8.4 reference `sandbox.*` ingestion at "row 10". The canonical row at v1.2 is **row 5** (line 333). Row 10 in v1.2 is `audit.*` (line 338).

| Site | Original token | Canonical reading at v1.15 |
|---|---|---|
| v1.13 line 11 (heading) | "§C-OD-05 `sandbox.*` namespace ingestion row — sub-note amendment" — section heading | Heading PRESERVED; the row referenced is **row 5** (not row 10). |
| v1.13 line 16 (authority chain) | "v1.2 §C-OD-05 §5.1 row 10 (preserved verbatim through v1.12) declares the `sandbox.*` namespace" | "v1.2 §C-OD-05 §5.1 **row 5**" |
| v1.13 line 22 (post-amendment text) | "v1.2 §C-OD-05 §5.1 row 10 declaration ... ingests the `sandbox.*` namespace per `Spec_Action_Surface_v1.md` C-AS-15 §15.4" | "v1.2 §C-OD-05 §5.1 **row 5** declaration ... ingests the `sandbox.*` namespace per `Spec_Action_Surface_v1.md` C-AS-15 **§15.2** (with §15.4 sampling-discipline cite preserved as supplementary always-sampled posture)" |
| v1.13 line 42 (ASCII diagram) | "OD audit-ledger ingests sandbox.* namespace per C-OD-05 §5.1 row 10" | "row 5" |
| v1.13 line 70 (finding (b) text) | "OD spec v1.2 §C-OD-05 §5.1 row 4 declares `mcp.*` namespace ingestion via `Spec_Action_Surface_v1.md` C-AS-14 §14.8 (`mcp.tool.call` span family)" | "row 2 ... C-AS-14 §14.3 (mcp.* attribute table)" — row 4 → row 2 + §14.8 → §14.3. §14.8 is the audit-floor / sampling section (per v1.2 line 498 cite), NOT the attribute-table declaration site. §14.8 preserved as supplementary cite where the context is sampling/audit-floor posture (per §1.2). |
| v1.14 line 9 (change-note) | "§C-OD-05 §5.1 rows 4 + 10 are NOT touched" | "rows **2 + 5** are NOT touched" (row 2 = `mcp.*`; row 5 = `sandbox.*`) |
| v1.14 line 9 (change-note) | "The v1.13 §C-OD-05 row 10 sub-note" | "row 5 sub-note" |
| v1.14 line 22 (authority chain) | "v1.13 §C-OD-05 §5.1 row 10 sub-note" | "row 5 sub-note" |
| v1.14 line 31 (rule text) | "§C-OD-05 §5.1 row 10" | "row 5" |
| v1.14 line 35 (definition) | "`sandbox.violation` pulls under row 10 (`sandbox.*` per C-AS-15 §15.4)" | "row 5 (`sandbox.*` per C-AS-15 §15.2)" |
| v1.14 line 35 (definition) | "`mcp.tool.call` pulls under row 4 (`mcp.*` per C-AS-14 §14.3)" | "row 2 (`mcp.*` per C-AS-14 §14.3)" — cite §14.3 PRESERVED (correct at v1.2); row number 4 → 2 |
| v1.14 line 50 (worked-example table row 1) | "§C-OD-05 row 10 (`sandbox.*` via C-AS-15 §15.4) — NOT row 4 (`mcp.*` via C-AS-14 §14.3)" | "row 5 (`sandbox.*` via C-AS-15 §15.2) — NOT row 2 (`mcp.*` via C-AS-14 §14.3)" |
| v1.14 line 51 (worked-example table row 2) | "§C-OD-05 row 10 (`sandbox.*` via C-AS-15 §15.4)" | "row 5 (`sandbox.*` via C-AS-15 §15.2)" |
| v1.14 line 53 (paragraph) | "the same §C-OD-05 row 10" | "row 5" |
| v1.14 line 55 | "v1.13 §C-OD-05 §5.1 row 10 sub-note" | "row 5 sub-note" |
| v1.14 line 63 (§8.4.2 table) | "`sandbox.*` (row 10) \| row 10" | "row 5 \| row 5" |
| v1.14 line 65 (§8.4.2 table) | "`mcp.*` (row 4) \| row 4" | "row 2 \| row 2" |
| v1.14 line 81 (§8.4.4) | "row 10 `sandbox.*` declares the 7-attribute `sandbox.*` set per C-AS-15 §15.2 ... ingested at row 10 even though row 10's declared attribute set" | "row 5 ... ingested at row 5 even though row 5's declared attribute set". Cite **§15.2 PRESERVED VERBATIM** — §8.4.4 already cites the correct section. |
| v1.14 line 83 (§8.4.4) | "row 10 = 7 attrs" | "row 5 = 7 attrs" |
| v1.14 line 94 (preservation list) | "v1.13 row 10 sub-note preserved" | "row 5 sub-note preserved" |
| v1.14 line 123 (downstream table) | "§C-OD-05 row 10 sub-note pair" | "row 5 sub-note pair" |
| v1.14 line 135 (filing footer) | "v1.13 §C-OD-05 row 10 sub-note precedent" | "row 5 sub-note precedent" |
| v1.14 line 138 (filing footer) | "v1.13 row 10 sub-note preserved" | "row 5 sub-note preserved" |
| v1.14 line 142 (filing footer) | "§C-OD-05 §5.1 row 10 sub-note" | "row 5 sub-note" |

### §1.2 Section-cite drift at attribute-declaration sites (sandbox.* §15.4 → §15.2; mcp.* §14.8 → §14.3)

The v1.13 sub-note + v1.14 §C-OD-08 §8.4 reference AS spec C-AS-15 **§15.4** as the cross-axis citation for the `sandbox.*` namespace ingestion row. AS spec v1.2 declares the canonical citation at **§15.2** (the 7-attribute table at lines 1320-1327). §15.4 is the always-sampled-events sub-section (`sandbox.violation` + `sandbox.tier_escalation`); it is a sibling section, NOT the attribute-table declaration site that §C-OD-05 row 5 cites.

The parallel drift exists at v1.13 finding (b) text (line 70) for `mcp.*`: cite to **C-AS-14 §14.8** ("mcp.tool.call span family"). AS spec v1.2 declares the canonical mcp.* attribute table at **§14.3** (per OD v1.2 line 330 row 2 cite). §14.8 is the audit-floor commitment section (per v1.2 line 498 cite); it is a sibling section, NOT the attribute-table declaration site.

The corrected canonical reading at v1.15:

- **C-AS-15 §15.2** is the attribute-declaration cite for `sandbox.*` (per v1.2 row 5). §15.4 is preserved as supplementary cite ONLY when the context is always-sampled posture (`sandbox.violation` / `sandbox.tier_escalation` head=1.0).
- **C-AS-14 §14.3** is the attribute-declaration cite for `mcp.*` (per v1.2 row 2). §14.8 is preserved as supplementary cite ONLY when the context is audit-floor commitment posture (`mcp.tool.call` head=1.0 with tail-keep-on-trust-tier-floor-violations per v1.2 line 498 framing).

The v1.13 line 22 conflation — citing "§15.4 (always-sampled — security-critical)" as the attribute-namespace declaration — is the structural origin of the §15.2 drift; v1.13 line 70 — citing "§14.8 (`mcp.tool.call` span family)" as the namespace declaration — is the structural origin of the §14.3 drift. Downstream §8.4 sites at v1.14 propagated these section-cite drifts.

§15.2 substitutions at v1.14 §C-OD-08 §8.4 sites (line 35 definition; line 50 table row 1; line 51 table row 2) per §1.1 above. §14.3 substitution at v1.13 line 70 finding (b) per §1.1 above. v1.14 line 35 + line 50 row 2 "row 4 (mcp.* per C-AS-14 §14.3)" reference: **cite §14.3 is correct; only row number drifts** (row 4 → row 2 per §1.1).

**Supplementary cites preserved verbatim where context is sampling/audit-floor posture.** Specifically: any §C-OD-05 cite to `sandbox.violation` / `sandbox.tier_escalation` always-sampled events continues to cite §15.4 (or §15.4 + §15.2 paired); any cite to `mcp.tool.call` audit-floor head=1.0 commitment continues to cite §14.8 (or §14.8 + §14.3 paired). The split is real (attribute-table declaration vs sampling/audit-floor posture); v1.15 respects the split.

### §1.3 Drift NOT present at v1.14 (verified)

- v1.14 line 64 (§8.4.2 table) "`hitl.*` (row 6)" — **CORRECT** at v1.2 (row 6 = `hitl.*` per line 334).
- v1.14 line 35 (definition) "row 1 (`anthropic.*` per C-AS-14 §14.2)" — **CORRECT** at v1.2 (row 1 = `anthropic.*` per line 329).
- v1.14 line 35 (definition) "row 6 (`hitl.*` per C-CP-20 §20.6)" — **CORRECT** at v1.2 (line 334).
- v1.14 line 81 §8.4.4 cite "per C-AS-15 §15.2" — **CORRECT** at v1.2 row 5 cite (already canonical at v1.14).
- AS-spec sandbox.* attribute count = **7** (NOT 6) — empirically verified at AS spec v1 §15.2 lines 1320-1327 + v1.4 footer line 169 + v1.6 §15 framing.

---

## §2 Finding-(a) closure (v1.13 + v1.14 §"Adjacent observations" finding (a))

**Closed as phantom.** v1.13 finding (a) + v1.14 finding (a) ("`sandbox.*` namespace cardinality drift — AS spec v1.6 §15.9 extends `sandbox.*` to 7 attrs ... OD spec v1.2 §C-OD-05 §5.1 row 10 cite-shape says '6-attribute' implicitly via AS §15.4 reference") is **incorrect at empirical-verification** on three claims:

1. **Row reference.** Claims "row 10" — canonical at v1.2 is **row 5** (row 10 = `audit.*`).
2. **Section cite.** Claims "AS §15.4 reference" implies "6-attribute" — AS §15.4 is the always-sampled-events sub-section, NOT an attribute-count declaration. The canonical attribute-count declaration at AS §15.2 is **7**, declared at AS v1 baseline + preserved verbatim through v1.7.
3. **Cardinality event.** Claims a "6 → 7 attribute" extension — no such extension event exists in the AS spec lineage. AS spec v1 declared 7 attributes at §15.2 (lines 1320-1327); the count has been stable since v1 baseline. AS v1.6 §15.9 adds the **co-emission** of `mcp.fail.class` (a separate-namespace attribute on the same `sandbox.violation` span); it does NOT extend the `sandbox.*` attribute set itself.

The "cardinality drift" framing was a forecast of a defect that never landed; the actual defect was the row-number + section-cite drift introduced at v1.13 sub-note authoring and propagated through v1.14 §C-OD-08 §8.4.

**Disposition at v1.15.** Finding (a) is **CLOSED-as-phantom**. No cardinality refresh arc owed. The real defect (row-number + section-cite drift) is resolved at v1.15 §1 canonical-reading amendment table above.

---

## §3 Origin-of-drift documentation (lineage; not blame)

The row-number + section-cite drift has two distinct structural origins, one per namespace:

**Sandbox.* drift origin (row 10 / §15.4).** Introduced at v1.13 sub-note authoring (2026-05-26 first arc — AS-4 dual-attribute cascade per `class_1_fork_as_4_od_cxa_dual_attribute_cascade.md` §6 Option A ratification at `ff67bc7..0c22efc`). The sub-note authoring at v1.13 §C-OD-05 §5.1 conflated "row 10" + "§15.4 (always-sampled — security-critical)" cite with the attribute-table declaration site (row 5 + §15.2). Propagated through v1.14 §C-OD-08 §8.4 authoring (2026-05-26 second arc — `mcp.*` namespace cross-emission per `class_1_fork_mcp_namespace_cross_emission_ingestion_ownership.md` §6 Reading A ratification at `c646577..65692bc`).

**Mcp.* drift origin (row 4 / §14.8).** Introduced at v1.13 finding (b) text authoring (same arc as sandbox.* origin — AS-4 dual-attribute cascade `ff67bc7..0c22efc`). The finding (b) prose at v1.13 line 70 conflated "row 4" + "§14.8 (`mcp.tool.call` span family)" cite with the attribute-table declaration site (row 2 + §14.3). Propagated through v1.14 §C-OD-08 §8.4 "Definition of parent-span-class" + §8.4.1 worked-example table + §8.4.2 anticipated-cases table (all citing "row 4 (`mcp.*`)" — cite §14.3 was correctly inherited; only the row number drifted).

The drift is documented at the lineage level (NOT as a blame finding) per workspace `CLAUDE.md` §8 I-1 byte-exact discipline + I-5 Class-3 informational routing: cite-shape drift surfaced post-arc-landing routes to apply-pass canonical-reading amendment at the next operator-discretion spec revision, NOT to retroactive halt-execution back-flow at the original arcs.

Both originating fork-doc + their applied spec versions (v1.13 + v1.14) remain canonical and PRESERVED VERBATIM; v1.15 §1 is the canonical-reading amendment that downstream readers apply when interpreting those files.

---

## §4 Sections preserved verbatim at v1.15

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v1.15 amendment touches ONLY the NEW §1 canonical-reading amendment table + §2 finding-(a) closure + §3 origin-of-drift documentation (all within this v1.15 delta file). The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1/§4.2/§4.3/§4.4/§4.5** (v1.12-lineage GenAI span format)
- **§C-OD-05 §5.1 rows 1-15** (v1.2-lineage; v1.13 row 5 sub-note preserved verbatim per §1 canonical reading)
- **§C-OD-05 §5.2 + §5.3** (ingestion-posture invariants; F2-12 forward-compatibility note)
- **§C-OD-06 (lifecycle event mapping)** — preserved verbatim through v1.14
- **§C-OD-07 (`harness.breaker.*` schema)** — preserved verbatim
- **§C-OD-08 §8.1 + §8.2 + §8.3** — preserved verbatim from v1.2 lineage
- **§C-OD-08 §8.4 (v1.14 NEW — parent-span-class ingestion routing rule)** — preserved verbatim per §1 canonical reading
- **§C-OD-09 through §C-OD-33** (all v1.2-v1.14 lineage content preserved per delta-only-spec-file convention)
- All v1.3 through v1.14 substantive amendments

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **OD spec v1.13 finding (a) — CLOSED-as-phantom at v1.15 §2.** Removed from "Adjacent observations" carry; no longer a deferred apply-pass arc.

(b) **OD spec v1.13 finding (c) — Tension 004 D-2/D-3/D-4 carries.** Carried verbatim from v1.13/v1.14. v1.15 does NOT touch §C-OD-04 §4.2/§4.3/§4.5.

(c) **OD spec v1.13 finding (d) — `gen_ai.system` vs `gen_ai.provider.name` divergence.** Carried verbatim from v1.13/v1.14. v1.15 does NOT touch this carry.

(d) **v1.14 finding (d) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.14. v1.15 does NOT touch this carry.

(e) **AS-spec v1 §15.4 footnote on always-sampled posture.** §1.2 of v1.15 preserves §15.4 as supplementary cite when the context is always-sampled posture (e.g., `sandbox.violation` head=1.0 framing). No section-cite drift exists at v1.14 line 81 §8.4.4 ("per C-AS-15 §15.2") — that cite was already canonical at v1.14. Documenting for clarity that the §15.2 vs §15.4 split is real (attribute-declaration vs sampling-events) and the v1.15 amendment respects the split.

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.14 → v1.15 row update with v1.15 change-note narrative; v1.14 + v1.13 lineage preserved | This session apply-pass arc |
| `harness-od/CLAUDE.md` | NO change owed — v1.15 is fidelity-pure citation correction at OD spec layer; no cross-axis citation table touched. | n/a |
| CXA v2.12 | NO change owed — §1 canonical-reading amendment is OD-internal row-number + section-cite correction; CXA §0.4 convention-level seam at v2.12 references "v1.13 §C-OD-05 row 10 sub-note" — that cite at CXA v2.12 inherits the §1.1 canonical reading (row 10 → row 5). CXA file NOT edited per delta-only convention; downstream readers apply v1.15 §1 mapping. | Future CXA revision arc if operator routes a CXA cite-refresh (NOT owed at v1.15 per FM-2 no-extension discipline) |
| AS spec v1.7 | NO change owed — AS spec is canonical declaration site at §15.2 (7 attrs); v1.15 corrects OD-side cite drift, not AS-side content. | n/a |
| AS plan v1.4 | NO change owed — plan-side cites U-AS-17 / U-AS-18 reference AS §15.2 + §15.9 directly, not via OD row numbers. | n/a |
| ADR-D6 v1.2 | NO change owed per X-AL-3 (Meta-Architecture §7.7) — v1.15 is at spec layer, not ADR amendment. | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.15 (fidelity-pure citation-correction patch authoring NEW §1 canonical-reading amendment table + §2 finding-(a) closure + §3 origin-of-drift documentation; v1.14 + v1.13 files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | v1.13/v1.14 §"Adjacent observations" finding (a) re-evaluation per operator-routed cluster-1 open-arc 2026-05-26; empirical-verification confirmed finding (a) phantom-as-described; real defect = row-number + section-cite drift at v1.13 sub-note + v1.14 §C-OD-08 §8.4 |
| Supersedes | None — additive canonical-reading amendment at v1.15 closing v1.13/v1.14 finding (a) as phantom and correcting drift via downstream-reader substitution rules |
| Scope of revision | NARROW: NEW §1 canonical-reading amendment table + §2 finding-(a) closure + §3 origin-of-drift documentation. NO file edit to v1.13 or v1.14; downstream readers apply §1 substitutions when interpreting those files. |
| Contract change | ZERO — fidelity-pure citation correction; no field-set, no signature, no AC, no behavior change |
| Cross-axis cascade | ZERO — OD-internal row-number + section-cite correction; CXA v2.12 cite refresh deferred per FM-2 (downstream readers apply §1.1 mapping in-context) |
| Authority anchor | Workspace `CLAUDE.md` §8 I-1 byte-exact discipline + §4.3 Class 3 informational routing + workspace precedent for inline cite-correction patches (CP spec v1.14 2026-05-24; runtime spec v1.16 2026-05-22) |
| Predecessor | v1.14 (`mcp.*` namespace cross-emission Class 2 fork resolution — NEW §C-OD-08 §8.4 parent-span-class ingestion routing rule; preserved verbatim) |
| Successor | v1.16 (next operator-discretion arc — candidates: Tension 004 D-2/D-3/D-4 absorption per v1.13/v1.14 carry (b); `gen_ai.system` vs `gen_ai.provider.name` per carry (c); §8.4.2 anticipated cases empirical-verification per carry (d)) |
