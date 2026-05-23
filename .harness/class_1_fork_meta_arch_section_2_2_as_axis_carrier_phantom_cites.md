# Class 1 Fork — Meta-Architecture §2.2 AS-axis carrier-cite phantom cites (parallel-axis recurrence)

**Filed:** 2026-05-23 at Meta-Arch v1.2 → v1.3 bundled spec-writer arc — spec-writer FM-1 HALT condition surfaced during empirical verification of operator-ratified §12.3 cite shapes at sibling fork `.harness/class_1_fork_meta_arch_cp_spec_renumbering_drift.md`.
**Status:** OPEN.
**Scope:** Phase 7 design-substrate cite-fidelity discipline; halt-execution Class 1 per `Project_Workflow_v1_8.md` §2.7.6 + workspace `CLAUDE.md` §4.3.
**Surfaced by:** `spec-writer` skill FM-1 + FM-3 disciplines triggered at empirical AS plan v1 unit-body verification of §12.3 ratified cite shapes (U-AS-20..U-AS-27 + AS-axis primitive home for memory/files). Empirical verification shows cited unit IDs implement SECRETS surface, not Skills/memory/files surface.
**Disposition:** Land H_T-CP-19 alone at Meta-Arch v1.3 (clean CP-axis cites); HALT H_T-CP-15/16/17 application at sibling fork §12.3 until §2.2 H_T-AS-6/7/8 carrier-cite recurrence is resolved.

---

## 1. The recurrence-pattern surface

Sibling fork `class_1_fork_meta_arch_cp_spec_renumbering_drift.md` §1 documents Meta-Arch §2.3 CP-axis sub-table carrying phantom cites due to mis-anchoring at authoring time (CP spec v1.2 dated 6 days before Meta-Arch authoring; cites never empirically verified). §10.6 (k) of that fork's systems-architect recommendation explicitly predicted recurrence at parallel axes (§5.2 IS / §5.3 AS / §5.5 OD / §5.6 CXA audit surface).

This fork files the recurrence at **§2.2 AS-axis sub-table** (lines 194..202 at Meta-Arch v1.2). Empirical evidence at this arc confirms the recurrence-pattern hypothesis for 3 of 9 §2.2 rows (H_T-AS-6 / H_T-AS-7 / H_T-AS-8 carrier-cite cells).

## 2. Empirical evidence

**Method.** For each §2.2 row at H_T-AS-6, H_T-AS-7, H_T-AS-8, cross-check the cited carrier-unit IDs against the canonical AS plan v1 (3853-line base file) section-heading-declared unit body titles.

**Findings.**

| Meta-Arch §2.2 row | Carrier cite at v1.2 | AS plan v1 unit-body title at cited ID | Mismatch class |
|---|---|---|---|
| H_T-AS-6 "SkillFrontmatter schema + Skills loading discipline" (anchor C-AS-05 + C-AS-06 + C-AS-07) | `U-AS-20 → U-AS-24` | U-AS-20: "Declare `fetch_secret` signature + `SecretRef` opaque type + tier-aware resolution mechanism table" (line 1006). U-AS-21: "Enforce negative-observation invariants (secrets absent from prompts, logs, ledger)" (1060). U-AS-22: `SecretAllowlistEntry` (1107). U-AS-23: secret-passthrough constraints (1155). U-AS-24: `SecretFailClass` enum (1198). | **PHANTOM — full row.** Cited units implement SECRETS surface, not Skills frontmatter |
| H_T-AS-7 "Skills filesystem residence + reachability" (anchor C-AS-08 §8) | `U-AS-25, U-AS-26, U-AS-27` | U-AS-25: `outputs_hash` structure-not-content fingerprint formula (1265). U-AS-26: secret-fetch audit-ledger composition against C-IS-05 + C-IS-06 (1305). U-AS-27: per-fetch emission discipline + span emission alongside (1360). | **PHANTOM — full row.** Cited units implement secret-fetch audit-ledger emission, not Skills filesystem |
| H_T-AS-8 "Anthropic + MCP primitive observability (15-namespace exports)" (anchor C-AS-13 + C-AS-14) | `U-AS-28 → U-AS-32` | U-AS-28: "Declare eleven-primitive enumeration + per-primitive × workload-class adoption-depth matrix" (1418). U-AS-29: per-D1-engine-class composition overlay + per-sub-agent-role × model-binding contract (1469). U-AS-30: Anthropic-API graceful-degradation per primitive (1535). U-AS-31: "Declare six Anthropic-primitive attribute namespaces" (1605). U-AS-32: sampling discipline + audit-floor commitments (1660). | **PARTIAL ALIGNMENT.** Anthropic primitive enumeration AT U-AS-28; six-namespace attribute schemas AT U-AS-31 (`anthropic.*`/`mcp.*`/`skill.*`/`managed_agents.*`/`files.*`/`memory.*`). Cite "15-namespace exports" overstates count (6 namespaces declared at §14.4, not 15); Skills-filesystem-loading binding at U-AS-28 body (line 1462 + tests `test_skills_loads_from_filesystem_via_u_is_01_and_u_is_02` at 1465) crosses cited row boundary |

**Where Skills + memory + files surfaces actually materialize at AS plan v1:**

| Surface | Materialization site | Evidence |
|---|---|---|
| Skills primitive filesystem-loading binding | **U-AS-28** body (lines 1418..1467) | `skills_loads_from_filesystem_path` signature at 1452; cross-axis IS binding row 1 §13.2 at 1462; rollback boundary "Skills filesystem-loading binding" at 1467 |
| Skills frontmatter / version_sha semantic distinction | **U-AS-31** body (lines 1605..1658) | `skill.id` / `skill.version_sha` / `skill.frontmatter.version` attribute schema at §14.4 (line 1647); `test_skill_span_requires_both_version_fields` (1656) |
| `skill.*` attribute namespace (6 attributes) | **U-AS-31** body | §14.4 SKILL schema enumerated at 1647 |
| `files.*` attribute namespace (8 attributes) | **U-AS-31** body | `test_files_namespace_eight_attributes_per_spec_14_6` (1656) |
| `memory.*` attribute namespace (6 attributes) | **U-AS-31** body | `test_memory_namespace_six_attributes_per_spec_14_7` (1656) |
| Memory tool primitive per §13.2 row | **U-AS-28** body | "Memory tool: per-workload selection with backend per §13.6" at line 1461 acceptance criterion #6 |
| Files tool primitive per §13.2 row | **U-AS-28** body | "Files API: surface-conditioned r-managed/hybrid / o-local" at line 1461 acceptance criterion #6 |

## 3. Cross-fork dependency

**Sibling fork §12.3 ratified cite shapes** for H_T-CP-15/16/17 borrowed the §2.2 phantom carrier-cites:

| Sibling fork row | §12.3 ratified disposition | Empirical phantom |
|---|---|---|
| H_T-CP-15 | "STRIKE U-CP-33 → U-CP-37 with cross-axis cite U-AS-20..U-AS-27 (Skills authoring + filesystem residence) + U-CP-28..U-CP-30" | U-AS-20..U-AS-27 = SECRETS, not Skills. Cite borrowed from §2.2 H_T-AS-6+H_T-AS-7 carrier phantom |
| H_T-CP-16 | "STRIKE C-CP-16 §16 + carrier; cross-axis cite to AS-axis primitive home + observability namespace `C-AS-14 §14 (memory.* namespace export)`" | The AS-axis "primitive home" implied U-AS-* IDs; the actual materialization is at U-AS-28 (Memory tool primitive per §13.2 row body) + U-AS-31 (memory.* attribute schema). The §12.3 disposition lacks a verified unit ID set |
| H_T-CP-17 | Parallel to H_T-CP-16 | Same — files surface at U-AS-28 + U-AS-31 body, not at the unit IDs §12.3 implicitly inherited from §2.2 H_T-AS-7 carrier |

**Applying the §12.3 dispositions verbatim would propagate the §2.2 phantom cites** — same root-cause defect class as the original Class 1 fork being closed. Spec-writer FM-1 + FM-3 disciplines preclude this.

## 4. Disposition for this arc (PARTIAL-APPLY)

Per `[[halt-route-split-AC-pattern]]`:

| Sibling-fork §12.3 row | This-arc disposition |
|---|---|
| **H_T-CP-19** | **APPLY** at Meta-Arch v1.2 → v1.3. All 3 cited units (U-CP-26 / U-CP-27 / U-CP-43) empirically verified at CP plan v2.1+v2.4 base; contracts match `Implements:` anchors; tiebreaker §12.1 mechanically grounded |
| **H_T-CP-15** | **HALT** — sibling-fork §12.3 disposition borrowed §2.2 H_T-AS-6/7 phantom cites; new cite shape owed |
| **H_T-CP-16** | **HALT** — same |
| **H_T-CP-17** | **HALT** — same |

## 5. Routing target

**Class 1 (halt-execution).** Per workspace CLAUDE.md §4.3 + `Project_Workflow_v1_8.md` §2.7.6. Routing target: design-phase back-flow → Meta-Architecture revision (v1.3 → v1.4) absorbing §2.2 H_T-AS-6/7/8 carrier-cite re-anchoring + sibling-fork H_T-CP-15/16/17 re-ratification against verified AS-side cite shapes.

**Resolution path:**

| Step | Action | Authority |
|---|---|---|
| 1 | `systems-architect` skill against §2.2 AS-axis sub-table + sibling §12.3 H_T-CP-15/16/17 dispositions. Produce per-row recommendation citing AS plan v1 unit-body empirical surfaces (U-AS-28 + U-AS-31 + U-AS-33 + cross-axis CP cites where applicable) | `systems-architect` SKILL.md §4A.3 tension-resolution mode |
| 2 | Operator ratification of refined cite shapes (per-row or aggregate) | Operator AskUserQuestion |
| 3 | `spec-writer` re-invocation for §2.2 (H_T-AS-6/7/8 carrier-cite amendments) + §2.3 (H_T-CP-15/16/17 cross-axis cite amendments) + §5.4 (H_T-CP-16/17 retirement-column amendments) bundled at Meta-Arch v1.3 → v1.4 | `spec-writer` SKILL.md |
| 4 | Sibling fork §13 amendment closing H_T-CP-15/16/17 row dispositions against verified cite shapes (replacing §12.3 phantom-bearing dispositions) | `phase-7-back-flow-routing` |
| 5 | Re-evaluate `[[advisor-before-substantive-work-for-cross-axis-blockers]]` trigger conditions — this is now the **5th** phantom-cite/mis-anchoring fork in the 3-session cluster; pattern generalizes further (now: any cite-shape borrowed from another section without empirical verification of the borrowed cite's accuracy is suspect) | Memory update |

## 6. Parallel-axis audit scope (predicted further recurrences)

Per the recurrence-pattern observation at sibling-fork §10.6 (k) + Meta-Arch v1.1 §5.8: this surfacing strengthens the prior of analogous mis-anchoring at:

- **§2.1 IS-axis sub-table** (10 rows) — carrier-cite column
- **§2.4 OD-axis sub-table** (8 rows) — carrier-cite column
- **§2.5 CXA sub-table** (5 seams) — carrier-cite column
- **§5.2 IS / §5.3 AS / §5.5 OD / §5.6 CXA substitution-table** Retirement column — analogous audit to the §5.4 γ-audit at v1.1
- **§6 self-hosting milestone gradient** — per-primitive retirement gradient cited unit IDs
- **§7 anti-leakage rules** (18 axis + 3 cross-cutting) — cited surface IDs

Audit passes against these surfaces are OPERATOR-DISCRETION and remain DEFERRED. Each pass surface is bounded but the aggregate audit cost is multi-session work. Routing is per workspace `CLAUDE.md` §4.3 + per-axis adversarial-review cadence.

## 7. Memory update owed

`[[advisor-before-substantive-work-for-cross-axis-blockers]]` trigger condition surface expanded:

> Cross-fork phantom-cite propagation: when a sibling fork's ratified cite shape borrows unit IDs or contract anchors from another Meta-Arch section, verify the borrowed cites empirically before applying. Borrowing from §2.X catalog tables is NOT verification — those tables are subject to the same authoring-time mis-anchoring defect class.

`[[fork-meta-arch-cp-spec-renumbering-drift]]` index entry update: add "spawned sibling fork `class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites.md` 2026-05-23 during v1.3 bundled spec-writer arc — §12.3 cite shapes for H_T-CP-15/16/17 borrowed §2.2 H_T-AS-6/7 phantom cites; H_T-CP-19 only landed at v1.3; 3 rows + sibling fork await §2.2 systems-architect re-recommendation".

## 8. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites.md` |
| Filed at | 2026-05-23, bundled-arc spec-writer FM-1 HALT |
| Filing authority | `spec-writer` SKILL.md FM-1 + FM-3 + workspace `CLAUDE.md` §4.3 Class 1 back-flow routing |
| Status | OPEN |
| Sibling forks | `class_1_fork_meta_arch_cp_spec_renumbering_drift.md` (operator-aware; this fork is the recurrence at §2.2 AS-axis) |
| Routing target | `systems-architect` skill at follow-on arc |

---

*End of fork doc filing. v1.3 absorbing arc applies H_T-CP-19 only; H_T-CP-15/16/17 + §2.2 carrier-cite recurrence carried at this fork until resolved.*

---

## 6. Systems-architect recommendation (2026-05-23, follow-on arc)

**Skill invocation.** `systems-architect` skill §4A.3 tension-resolution mode invoked at follow-on arc post-`7f64b1f`. Scope per fork §5 step 1: per-row cite-shape recommendation against the §2.2 H_T-AS-6/7/8 carrier-cite surface + sibling-fork `class_1_fork_meta_arch_cp_spec_renumbering_drift.md` §12.3 H_T-CP-15/16/17 dispositions (now invalidated by §2 empirical evidence). Operator-decision authority preserved per §4A.4.

### 6.1 Precise tension statement (deepened scope)

The new finding at §2 expands the phantom surface beyond the original "carrier-cite" framing at fork §1. Empirical reading of canonical AS spec v1.3 contract anchors:

| Spec contract | AS spec v1.3 actual content | Meta-Arch §2.2 reading |
|---|---|---|
| C-AS-05 §5 | `fetch_secret(name, scope, tier) -> SecretRef` signature (SECRETS) | Cited at H_T-AS-6 anchor as "SkillFrontmatter schema + Skills loading discipline" |
| C-AS-06 §6 | Per-tool `required_secrets` allowlist (SECRETS) | Cited at H_T-AS-6 anchor |
| C-AS-07 §7 | Secret-fetch `secret.fail.class` taxonomy (SECRETS) | Cited at H_T-AS-6 anchor |
| C-AS-08 §8 | Secret-fetch structure-not-content audit composition (SECRETS) | Cited at H_T-AS-7 anchor as "Skills filesystem residence + reachability" |
| C-AS-13 §13 | **Eleven-primitive Anthropic-adoption-depth matrix** (Skills = primitive #1; Files API = #10; Memory tool = #11) | Cited at H_T-AS-8 anchor as "Anthropic + MCP primitive observability" |
| C-AS-14 §14 | **Six Anthropic-primitive attribute namespace declarations** (`anthropic.*`/`mcp.*`/`skill.*`/`managed_agents.*`/`files.*`/`memory.*`) | Cited at H_T-AS-8 anchor as "15-namespace exports" |

**The phantom surface at §2.2 is full row-replacement for H_T-AS-6 and H_T-AS-7** (both anchor + carrier columns reference SECRETS contracts/units). H_T-AS-8 is partial — anchor cites (C-AS-13 + C-AS-14) verify empirically correct; the row label "15-namespace exports" is wrong (canonical is 6 per C-AS-14 §14.1 table); carrier cites U-AS-28..U-AS-32 partially align (U-AS-28 carries Anthropic primitive enumeration; U-AS-31 carries the 6 namespace attribute schemas; U-AS-29/U-AS-30/U-AS-32 carry composition / graceful-degradation / sampling rather than core observability).

### 6.2 Authority-chain placement

Per workspace `CLAUDE.md` §1.3: **ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1**. The authoritative reading for Skills + memory + files primitive surfaces:

| Position | Artifact | Statement |
|---|---|---|
| **F-level commitment** | ADR-F5 v1.1 | Skills are an architectural commitment of the harness (F5 anchor) |
| **D-level specialization** | ADR-D3 v1.2 §1.1 line 79 | "1. **Skills system** (SKILL.md frontmatter; three-level progressive disclosure; agentskills.io open standard)" — Skills is primitive #1 in the eleven-primitive enumeration; **AS-axis-homed** per ADR-D3's "F2 → D3" derivation chain |
| **D-level specialization** | ADR-D3 v1.2 §1.1 lines 19, 79, 93 | Files API = primitive #10; Memory tool = primitive #11 (F2-11 Reading 2 closure) — both AS-axis-homed |
| **D-level specialization** | ADR-D3 v1.2 §1.8.1 (line 9 + line 17) | **"New §1.8.1 sub-section declares the six `*.` attribute namespaces at D3 source"** — namespaces (`anthropic.*`/`mcp.*`/`skill.*`/`managed_agents.*`/`files.*`/`memory.*`) homed at D3-source / AS-axis |
| **Spec-layer contract** | AS spec v1.3 C-AS-13 §13 (line 914) | Honors ADR-D3 §1.1 — eleven-primitive enumeration + matrix |
| **Spec-layer contract** | AS spec v1.3 C-AS-14 §14 (line 1034) | Honors ADR-D3 §1.8 + §1.8.1 — six attribute namespaces; `skill.*` at §14.4 / `files.*` at §14.6 / `memory.*` at §14.7 |
| **Plan-layer materialization** | AS plan v1 U-AS-28 (line 1418) | Primary producer of C-AS-13 (eleven-primitive enumeration matrix + per-primitive composition); includes Skills filesystem-loading binding (`skills_loads_from_filesystem_path` signature at line 1452, AC #6 at line 1461, IS binding at line 1462) |
| **Plan-layer materialization** | AS plan v1 U-AS-31 (line 1605) | Primary producer of C-AS-14 (six attribute namespace declarations); §14.4 `skill.*` 6-attribute schema with `version_sha` ↔ `frontmatter.version` semantic distinction enforced; §14.6 `files.*` 8-attribute schema; §14.7 `memory.*` 6-attribute schema |

**Authority-chain conclusion.** The Skills + Files API + Memory tool surfaces are **AS-axis-homed by ADR-D3 v1.2 §1.1** (D-level commitment) and **AS-axis-materialized at U-AS-28 + U-AS-31** (plan-level). The Meta-Arch §2.2 H_T-AS-6/7 anchor cites (C-AS-05/06/07/08) are **fully misaligned** with this authority chain — those C-AS contracts are SECRETS, a separate AS-axis surface (per AS spec v1.3 §5..§8 + plan U-AS-20..U-AS-27).

### 6.3 §2 discipline analysis

**Five-axis decomposition (§2.1).**

The H_T-AS-6/7/8 row triple at Meta-Arch §2.2 mixes three concerns:

- **Skills primitive declaration + filesystem-loading binding** (H_T-AS-6 + H_T-AS-7) — AS-axis primary, IS-axis consumer (for filesystem path-class)
- **Anthropic-primitive enumeration including Skills/Files/Memory** (H_T-AS-8) — AS-axis primary
- **Anthropic-primitive observability namespaces** (H_T-AS-8) — AS-axis primary, OD-axis consumer

The §2.2 rows decompose them into three primitive IDs but ALL THREE materialize at the SAME pair of plan units (U-AS-28 + U-AS-31) via different acceptance criteria + tests. This suggests the original Meta-Arch row decomposition may have been authored against a hypothetical AS-axis primitive map that never landed at plan level.

**Probabilistic-deterministic boundary (§2.2).**

These rows are all on the **deterministic** side — typed primitive enumerations, attribute namespace schemas, filesystem-residence binding contracts. The cite-fidelity defect is purely on the deterministic-side bookkeeping (which contract anchors which plan unit body), not a reliability-property mislocation. Reliability is unaffected.

**Decision ordering (§2.3).**

The misalignment is at the **D-level** (D3 specialization of F2). D3 is foundational-derivative (F2 → D3 → AS spec → AS plan). The Meta-Arch §2.2 mis-anchoring DOES NOT change any F-level commitment; it is a documentary-layer drift at the substitution-mapping catalog. The §2.2 rows themselves describe accurate H_T surfaces (Skills/Files/Memory ARE AS-axis primitives); only the cite IDs are wrong.

**Cross-axis verification (§2.5).**

A cross-axis tension at H_T-AS-7 "Skills filesystem residence" carries an IS-axis composition surface: `skills_loads_from_filesystem_path` at U-AS-28 line 1452 explicitly invokes U-IS-01 + U-IS-02 (canonical path contract from IS-axis path-class registry). The H_T-AS-7 cross-axis-posture cell at Meta-Arch §2.2 says "IS consumer (U-IS-01, U-IS-02, U-IS-08, U-IS-09, U-IS-10, U-IS-11)" — that subset is broadly correct (filesystem ops + state-ledger composition). The cross-axis posture is verified clean; only the AS-axis carrier-cite column is phantom.

### 6.4 Per-row recommended cite shapes

Per skill §4A.4: these are **recommendations**, not decisions. Each row's empirical evidence is provided; operator decides per-row.

#### 6.4.1 Meta-Arch §2.2 H_T-AS-6 — SkillFrontmatter schema + Skills loading discipline

| Column | Current at v1.2 (preserved at v1.3) | Recommended cite shape | Evidence |
|---|---|---|---|
| Anchor | `C-AS-05 + C-AS-06 + C-AS-07` (SECRETS — PHANTOM) | `C-AS-13 §13.1 row 1 (Skills primitive #1 per ADR-D3 v1.2 §1.1) + C-AS-14 §14.4 (skill.* attribute namespace + version_sha semantic distinction)` | ADR-D3 v1.2 §1.1 line 79; AS spec v1.3 C-AS-13 §13.1 row 1 (line 932); AS spec v1.3 C-AS-14 §14.4 |
| Carrier | `U-AS-20 → U-AS-24` (SECRETS — PHANTOM) | `U-AS-28 (Skills primitive #1 declaration + filesystem-loading binding + AC #6) + U-AS-31 (skill.* 6-attribute namespace with version_sha ↔ frontmatter.version semantic distinction; §14.4 schema)` | AS plan v1 U-AS-28 line 1418 + AC #6 at line 1461 + skills_loads_from_filesystem_path at line 1452; U-AS-31 line 1605 + §14.4 schema at line 1647 |
| Cross-axis posture | "AS-internal" (preserved at v1.2) | Recommend amend to "AS-internal (primitive declaration) + IS consumer (U-IS-01 + U-IS-02 for filesystem-residence binding per U-AS-28 AC #6 line 1462)" | U-AS-28 body line 1462 explicit cross-axis IS binding |

#### 6.4.2 Meta-Arch §2.2 H_T-AS-7 — Skills filesystem residence + reachability

| Column | Current at v1.2 (preserved at v1.3) | Recommended cite shape | Evidence |
|---|---|---|---|
| Anchor | `C-AS-08 §8` (SECRETS — PHANTOM) | `C-AS-13 §13.1 row 1 + §13.2 row 1 (Skills filesystem-residence per ADR-D3 §1.1 + per-workload adoption-depth matrix)` | AS spec v1.3 §13.1/§13.2; ADR-D3 v1.2 §1.1 + §1.2 |
| Carrier | `U-AS-25, U-AS-26, U-AS-27` (secret-fetch audit — PHANTOM) | `U-AS-28 (skills_loads_from_filesystem_path + IS binding per AC #6)` — **single unit; row may be candidate for consolidation with H_T-AS-6 per §6.5 below** | U-AS-28 line 1452/1461/1462 |
| Cross-axis posture | "IS consumer (U-IS-01, U-IS-02, U-IS-08, U-IS-09, U-IS-10, U-IS-11)" — broadly correct | Recommend amend to narrower "IS consumer (U-IS-01 + U-IS-02 canonical-path contract per U-AS-28 line 1452)" — the U-IS-08..11 portion describes state-ledger composition which is H_T-AS-5's surface, not H_T-AS-7's | AS plan v1 U-AS-28 line 1452 + AC #6 |

#### 6.4.3 Meta-Arch §2.2 H_T-AS-8 — Anthropic + MCP primitive observability (15-namespace exports)

| Column | Current at v1.2 (preserved at v1.3) | Recommended cite shape | Evidence |
|---|---|---|---|
| Row label | "Anthropic + MCP primitive observability (15-namespace exports)" | **"Anthropic + MCP primitive observability (6 attribute namespaces per C-AS-14 §14)"** — 15 is wrong; canonical is 6 per C-AS-14 §14.1 table | AS spec v1.3 §14.1 table: 6 namespaces |
| Anchor | `C-AS-13 + C-AS-14` — broadly correct | **PRESERVE** (already aligned) | AS spec v1.3 §13 + §14 |
| Carrier | `U-AS-28 → U-AS-32` — partial alignment | Recommend narrow to **`U-AS-28 (eleven-primitive enumeration + adoption-depth matrix) + U-AS-31 (six namespace attribute schemas; §14.4 skill.*/§14.6 files.*/§14.7 memory.* etc.)`** — U-AS-29/U-AS-30/U-AS-32 carry composition overlay / graceful-degradation / sampling discipline rather than core primitive observability surface | AS plan v1 U-AS-28 + U-AS-31 are the primary observability surface producers |
| Cross-axis posture | "IS consumer" | PRESERVE | (filesystem-residence + state-ledger consumers via U-AS-28 binding) |

#### 6.4.4 Sibling-fork §12.3 H_T-CP-15 — Skills enabling discipline (CP-side composition)

**Empirical reading.** The "CP-side composition" qualifier at the Meta-Arch §2.3 row label describes CP-axis composition of an AS-axis Skills primitive. CP-axis composition site = U-CP-28..U-CP-30 (HandoffContext + SubAgentBrief schema — which references skills-loading via brief per CP spec C-CP-13 §13). AS-axis primitive home = U-AS-28 + U-AS-31.

| Site | Recommended cite shape (replaces sibling-fork §12.3 phantom-bearing disposition) |
|---|---|
| §2.3 anchor | `C-AS-13 §13.1 row 1 + §13.2 row 1 (Skills primitive home, AS-axis per ADR-D3 v1.2 §1.1) + C-AS-14 §14.4 (skill.* attribute namespace) + C-CP-13 §13 (HandoffContext + SubAgentBrief composing skills via brief)` |
| §2.3 carrier | `U-AS-28 (Skills primitive #1 declaration + filesystem-loading binding) + U-AS-31 (skill.* attribute namespace) + U-CP-28 + U-CP-29 + U-CP-30 (HandoffContext + SubAgentBrief + StateSummary schemas)` |
| §5.4 retirement | **N/A — H_T-CP-15 is absent from §5.4** per the v1 21-entry-vs-23-row discrepancy (carry-forward pre-existing, not in this arc scope) |

**Authority chain trace.** ADR-D3 v1.2 §1.1 (Skills AS-axis) → C-AS-13 §13.1 row 1 (Skills primitive) → C-AS-14 §14.4 (skill.* namespace) → U-AS-28 + U-AS-31 (material-location). CP-side: CP spec C-CP-13 §13 (HandoffContext schema referencing brief) → U-CP-28..U-CP-30 (HandoffContext + SubAgentBrief + StateSummary plan-unit bodies).

#### 6.4.5 Sibling-fork §12.3 H_T-CP-16 — Memory primitives + memory.* consumption

| Site | Recommended cite shape |
|---|---|
| §2.3 anchor | `C-AS-13 §13.1 row 11 (Memory tool primitive #11 per ADR-D3 v1.2 §1.1 + F2-11 Reading 2) + C-AS-14 §14.7 (memory.* attribute namespace 6-attribute schema)` |
| §2.3 carrier | `U-AS-28 (Memory tool primitive #11 per AC #6 at AS plan v1 line 1461; "Memory tool: per-workload selection with backend per §13.6") + U-AS-31 (memory.* 6-attribute namespace at §14.7)` |
| §5.4 retirement | Parallel: `U-AS-28 + U-AS-31` (material-location-resident cross-axis cite per §5.1.1) |

**Authority chain trace.** ADR-D3 v1.2 §1.1 line 79 + §1.1 lines 17-19 (F2-11 Reading 2: Memory tool added as primitive 11) → C-AS-13 §13.1 row 11 → C-AS-14 §14.7 (memory.* namespace per ADR-D3 §1.8.1 declaration) → U-AS-28 AC #6 + U-AS-31 §14.7 schema.

#### 6.4.6 Sibling-fork §12.3 H_T-CP-17 — Files primitives + files.* consumption

| Site | Recommended cite shape (parallel to H_T-CP-16) |
|---|---|
| §2.3 anchor | `C-AS-13 §13.1 row 10 (Files API primitive #10 per ADR-D3 v1.2 §1.1 + F2-11 Reading 2) + C-AS-14 §14.6 (files.* attribute namespace 8-attribute schema)` |
| §2.3 carrier | `U-AS-28 (Files API primitive #10 per AC #6 at AS plan v1 line 1461; "Files API: surface-conditioned r-managed/hybrid / o-local") + U-AS-31 (files.* 8-attribute namespace at §14.6)` |
| §5.4 retirement | Parallel: `U-AS-28 + U-AS-31` |

**Authority chain trace.** ADR-D3 v1.2 §1.1 lines 17-19 (F2-11 Reading 2: Files API added as primitive 10) → C-AS-13 §13.1 row 10 → C-AS-14 §14.6 (files.* namespace) → U-AS-28 AC #6 + U-AS-31 §14.6 schema.

### 6.5 Surfaced ambiguities for operator decision

The empirical reading above resolves anchor-and-carrier columns cleanly. Three load-bearing ambiguities remain for operator decision:

**Ambiguity (a) — H_T-AS-6 + H_T-AS-7 row consolidation.** Both rows materialize at the same plan unit (U-AS-28). The original §2.2 row split decomposes "SkillFrontmatter schema + Skills loading discipline" (H_T-AS-6) from "Skills filesystem residence + reachability" (H_T-AS-7) but the material location is single — U-AS-28's body carries both surfaces as a unified primitive. Two operator-decision options:

- **Option (a.i) Preserve the row split** at §2.2; cite U-AS-28 + U-AS-31 at both rows; document that the rows decompose conceptually rather than materially.
- **Option (a.ii) Consolidate at v1.4** into a single H_T-AS-6+7 row (renumbered if needed); preserves material-location-resident fidelity; reduces §2.2 row count from 9 → 8 (and §2.6 catalog aggregate cell from 49 → 48); back-references rippling through §3..§13 may be invalidated.

**Recommend (a.i)** — row preservation preserves Meta-Arch §2.6 aggregate count + downstream catalog cites; the conceptual split is cleanly documented at the row-label level even if material location is unified.

**Ambiguity (b) — H_T-AS-8 row label correction.** The "15-namespace exports" cite is wrong (canonical = 6 per C-AS-14 §14.1). Two options:

- **Option (b.i)** Correct row label at this fork's absorbing arc — "6 attribute namespaces per C-AS-14 §14"
- **Option (b.ii)** Defer to a separate label-correction arc; treat as documentation-only drift

**Recommend (b.i)** — label correction is a single-token replacement with verifiable byte-exact source (AS spec v1.3 §14.1 table). Bundling at the §2.2 absorbing arc is FM-2-compliant (single-arc scope).

**Ambiguity (c) — Cross-fork dependency between this fork's §6 recommendation and sibling-fork §12.3 dispositions for H_T-CP-15/16/17.** The §6.4.4/§6.4.5/§6.4.6 recommendations REPLACE sibling-fork §12.3 phantom-bearing dispositions. Two routing options:

- **Option (c.i) Bundle §2.2 + sibling-fork §2.3/§5.4 amendments at single Meta-Arch v1.3 → v1.4 absorbing arc** — single commit; preserves cross-row coherence; spec-writer applies both fork's §6 + sibling §12.3-replacement-by-§6.4.4-5-6 in one pass.
- **Option (c.ii) Separate arcs** — §2.2 corrections at v1.4; sibling-fork H_T-CP-15/16/17 at v1.5. Smaller per-arc scope but cross-row coherence delayed.

**Recommend (c.i)** — the §2.2 fixes UNBLOCK the sibling-fork §12.3-replacement dispositions (cross-fork dependency is causal); bundling preserves the operator-ratified "single bundled arc" intent from the original sibling-fork operator decision; cross-row coherence at single commit.

### 6.6 Tiebreaker check

**Single verifiable fact:** ADR-D3 v1.2 §1.8.1 declares the six `*.` attribute namespaces (`anthropic.*` / `mcp.*` / `skill.*` / `managed_agents.*` / `files.*` / `memory.*`) at D3 source. If this declaration stands, the recommendation determinate.

**Verification command:**

```bash
grep -nE "§1\.8\.1|six.*attribute namespace|anthropic\.\*.*mcp\.\*.*skill" design-substrate/ADR-D3.md | head
```

**Expected result:** ADR-D3 v1.2 change-note explicitly states "new §1.8.1 sub-section declares the six `*.` attribute namespaces at D3 source per Pattern P1 mechanical-alignment discipline" (line 9 + line 17 + line 21 of ADR-D3.md per empirical verification at this arc).

**If the tiebreaker fact does NOT verify** (e.g., ADR-D3 §1.8.1 is silent or homes namespaces at a different axis): the recommendation requires re-grounding against the foundational F5 (Skills) commitment + the ADD v1.3 §3.3.2 synthesis. Surface to operator before applying.

### 6.7 §2.7.6 fork class

**Class 1 (halt-execution).** Per workspace `CLAUDE.md` §4.3 + `Project_Workflow_v1_8.md` §2.7.6. Class 1 status preserved from §5 of this fork. Resolution unblocks:

1. `phase-7-substitution-retirement` skill re-invocation for H_T-CP-15/16/17 against verified cross-axis cites (per §6.4.4/§6.4.5/§6.4.6)
2. Sibling-fork `class_1_fork_meta_arch_cp_spec_renumbering_drift.md` full close (4/7 rows now applied at v1.3; with this recommendation absorbed, 7/7 §10.4 rows will be applied)
3. Parallel-axis audit cadence per §6 of this fork (predicted further recurrences at §2.1 IS / §2.4 OD / §2.5 CXA carrier-cite columns)

### 6.8 Explicit operator-decides marker

**The operator decides.** This recommendation is appended per `systems-architect` skill §4A.3. Per §4A.4, the skill does NOT decide and does NOT edit the Meta-Arch artifact. Operator ratification (per-row or aggregate, with §6.5 ambiguity disposition) routes the recommendation to `spec-writer` skill at the absorbing arc.

### 6.9 Routing for ratified outcome

| Step | Action | Authority |
|---|---|---|
| 1 | Operator ratification per-row (§6.4.1..§6.4.6) + per-ambiguity (§6.5 a/b/c) | Operator AskUserQuestion at follow-on arc |
| 2 | `spec-writer` skill applies ratified §2.2 + §2.3 + §5.4 + §5.8 amendments to Meta-Arch v1.3 → v1.4 (or v1.4 + v1.5 if §6.5 (c.ii) selected) | `spec-writer` SKILL.md FM-1..FM-6 discipline |
| 3 | Sibling fork `class_1_fork_meta_arch_cp_spec_renumbering_drift.md` §13 update — H_T-CP-15/16/17 status APPLIED at v1.4; fork advances to APPLIED-EXCEPT-(missing-primitives + §2.2-AS-axis-recurrence-CLOSED) | `phase-7-back-flow-routing` skill |
| 4 | This fork §7 update — status OPEN → APPLIED (or PARTIALLY-APPLIED if §6.5 (a.ii) deferred) | This fork |
| 5 | Re-invocation `phase-7-substitution-retirement` for H_T-CP-15/16/17 against verified cite shapes | `phase-7-substitution-retirement` skill, per-row arcs |
| 6 | Optional parallel-axis audit kickoff (per §6 of this fork) | Operator-discretion timing |

---

*End of §6 systems-architect recommendation. Recommendation appended per skill §4A.3. Operator decides per-row + per-ambiguity at follow-on AskUserQuestion. Fork status preserved as OPEN pending operator ratification + spec-writer absorbing arc.*

---

## 7. v1.4 absorbing-arc application footer (2026-05-23, same session as §6)

**Operator ratification.** AskUserQuestion 2026-05-23 selected "Ratify all 6 rows + all 3 ambiguities per recommended (a.i + b.i + c.i)":
- All 6 per-row cite shapes at §6.4.1..§6.4.6 ratified verbatim
- Ambiguity (a.i): preserve H_T-AS-6/7 row split at §2.2 (no row consolidation)
- Ambiguity (b.i): correct H_T-AS-8 "15-namespace exports" → "6 namespaces per C-AS-14 §14" row-label at this arc
- Ambiguity (c.i): bundle §2.2 + sibling-fork §2.3/§5.4 at single Meta-Arch v1.3 → v1.4 absorbing arc

**Spec-writer absorbing arc.** Meta-Arch v1.3 → v1.4 applied at single commit this session. Eleven amendment sites: 3 §2.2 + 3 §2.3 + 2 §5.4 + 2 §5.8 per-finding + 1 §5.8 summary. Status block (Version + Status + Date) amended. New §0.4 change-note documenting all sites + preservation + audit + verbatim round-trip + FM checks. ZERO cross-axis cascade per §6.7 + new §0.4. All non-amended sections preserved verbatim from v1.3.

**Per-row application status:**

| §6 row | v1.4 disposition | Cite shape applied |
|---|---|---|
| §6.4.1 H_T-AS-6 (§2.2) | ✓ APPLIED | Anchor `C-AS-13 §13.1 row 1 + C-AS-14 §14.4`; carrier `U-AS-28 + U-AS-31`; cross-axis-posture amended for IS binding |
| §6.4.2 H_T-AS-7 (§2.2) | ✓ APPLIED | Anchor `C-AS-13 §13.1+§13.2 row 1`; carrier `U-AS-28`; cross-axis-posture narrowed |
| §6.4.3 H_T-AS-8 (§2.2) | ✓ APPLIED | Row label "15-namespace" → "6 namespaces per C-AS-14 §14"; carrier narrowed to `U-AS-28 + U-AS-31` |
| §6.4.4 H_T-CP-15 (§2.3) | ✓ APPLIED | Anchor `C-AS-13 + C-AS-14 §14.4 + C-CP-13 §13`; carrier `U-AS-28 + U-AS-31 + U-CP-28..30` |
| §6.4.5 H_T-CP-16 (§2.3 + §5.4 + §5.8) | ✓ APPLIED | Anchor `C-AS-13 §13.1 row 11 + C-AS-14 §14.7`; carrier `U-AS-28 + U-AS-31` at both §2.3 + §5.4; §5.8 disposition RESOLVED at v1.4 |
| §6.4.6 H_T-CP-17 (§2.3 + §5.4 + §5.8) | ✓ APPLIED | Anchor `C-AS-13 §13.1 row 10 + C-AS-14 §14.6`; carrier `U-AS-28 + U-AS-31` at both §2.3 + §5.4; §5.8 disposition RESOLVED at v1.4 |

**Ambiguity application status:**

| Ambiguity | Ratification | v1.4 disposition |
|---|---|---|
| (a) H_T-AS-6/7 row consolidation | a.i — preserve split | ✓ Rows preserved at §2.2; §2.6 catalog aggregate cell preserved |
| (b) H_T-AS-8 label correction | b.i — in-place correction | ✓ Row label amended at §2.2 line 257 |
| (c) Bundle scope | c.i — single arc | ✓ Single bundled commit applied |

**§5.8 audit-summary table cumulative status.**

| Bucket | v1.1 baseline | v1.2 | v1.3 | v1.4 |
|---|---|---|---|---|
| Resolved at v1.1 α fix | 1 (H_T-CP-18) | 1 | 1 | 1 |
| Phantom — full row | 3 (H_T-CP-16/17/19) | 3 | 2 (H_T-CP-19 → RESOLVED) | **0** (H_T-CP-16/17 → RESOLVED) |
| Partial — cite-shape gap | 2 (H_T-CP-20/21) | 2 (both RESOLVED at v1.2 per-finding cells; bucket label unchanged) | 2 | 2 |
| Clean | 17 | 17 | 17 | 17 |
| Total H_T-CP-* §5.8 phantom-or-partial findings | 5 | 5 | 5 | 5 |
| Cumulative RESOLVED | 1 (v1.1 H_T-CP-18) | 3 (+v1.2 H_T-CP-20/21) | 4 (+v1.3 H_T-CP-19) | **6** (+v1.4 H_T-CP-16/17) |

**Cross-fork dependency resolved.** Sibling fork `class_1_fork_meta_arch_cp_spec_renumbering_drift.md` §12.3 phantom-bearing dispositions for H_T-CP-15/16/17 (which borrowed §2.2 H_T-AS-6/7 phantoms) are now REPLACED by this fork's §6.4.4/§6.4.5/§6.4.6 ratified dispositions applied at v1.4. Sibling fork §14 footer appended this session documenting the resolution (status advance PARTIALLY-APPLIED → APPLIED-EXCEPT-missing-primitives).

**Fork status post-§7.** OPEN → **APPLIED**.

**Outstanding items (post-§7).**

1. **§4.4.3 CP-axis classification + H_T-AS-6/7/8 rationale descriptors** (Meta-Arch lines ~427-429 + ~450-452) carry-forward at v1.4 per FM-2 single-scope. Routed to follow-on cross-row coherence-pass arc per Meta-Arch v1.4 §0.4 adjacent defects (i) + (ii). Includes the parallel "15-namespace" stale cite at §4.4.3 H_T-AS-8 row mirror.
2. **Parallel-axis audit cadence** (per §6 of this fork): §2.1 IS / §2.4 OD / §2.5 CXA carrier-cite columns + §5.2 IS / §5.3 AS / §5.5 OD / §5.6 CXA γ-audit. Operator-discretion timing.
3. **Sibling-fork §10.5 missing-primitive additions** (4 NEW v1.10/v1.11 contracts: §17.4 hitl_gate / §25 ValidatorFramework / §26 PauseResumeProtocol / §27 MaterialDiffPolicy) remain OPEN at separate routing track.
4. **Per-row `phase-7-substitution-retirement` re-invocation** for H_T-CP-15/16/17 against v1.4 cite shapes (operator-discretion timing per X-AL-2 criterion verification).

**Pattern reinforcement (5th phantom-cite/mis-anchoring fork in 3-session cluster).** This fork's resolution closes the §2.2 AS-axis recurrence cleanly. Memory pattern at `[[advisor-before-substantive-work-for-cross-axis-blockers]]` trigger surface confirmed expanded per §7 of this fork: borrowing cite shapes from another Meta-Arch section without empirical verification is a phantom-cite vector. Spec-writer FM-1+FM-3 empirical-verification pass at apply-time is the structural safeguard against cross-fork phantom propagation.

ZERO cross-axis cascade. L9-septies + 10-CP-D cluster closes stand. H_T-CP-18 batch-10 RETIRE-READY at `eb4475d` stands. 2751/2751 tests stand.

---

*End of §7 v1.4 absorbing-arc application. Fork doc status post-§7: APPLIED. All §6 ratified amendments landed at Meta-Arch v1.4. Sibling-fork H_T-CP-15/16/17 surface RESOLVED at this fork. Parallel-axis audit + §4.4.3 coherence-pass + §10.5 missing-primitives + per-row retirement filings carried at follow-on arcs.*
