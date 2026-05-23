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
