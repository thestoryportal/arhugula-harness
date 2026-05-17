# Implementation Plan — Operational Discipline (OD axis) — v2.11

**Status: Proposed.**

**Revision:** v2.11 — Phase 7 sub-phase 7c prerequisite pass, in-CLI revision. Resolves the **OD-outbound cross-axis placeholder carrier IDs** (`U-AS-NN` / `U-CP-NN`) carried in §4.5.2 / §4.5.3 and in nine unit-body `Depends on` declarations. v2.11 is a **Form A citation-precision delta** over v2.10: no contract re-decomposed, no signature changed, no acceptance criterion changed, no unit added or removed (count unchanged at 35). Predecessor: v2.10 (FF-3 — U-OD-29 `SandboxTier`).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 authority chain; `phase-7-cross-axis-composition` SKILL §4.2 Pattern P1 + §7 (placeholder carrier ID = Class 1 → Form A citation-precision revision; F3-02 precedent).

**Entry authorization:** Phase 7 7c prerequisite pass, operator-authorized 2026-05-16. Companion artifact: `Cross_Axis_Composition_Document_v2_2.md`; resolution table `.harness/cxa_7c_placeholder_resolution.md`.

---

## §0 Change-note

### §0.1 Trigger

Sub-phase 7c entry-gate orientation (`.harness/cxa_7c_prerequisites_report.md`, Prereq 1) found that CXA v2.1 §2.3.5/§2.3.6 and the OD plan §4.5.2/§4.5.3 enumerations — and nine OD unit-body cross-axis `Depends on` declarations — cite `U-AS-NN` / `U-CP-NN` / `U-IS-NN` **placeholder carrier IDs** that were never resolved to canonical carrier unit IDs (and, at U-OD-27, two placeholders for OD→IS edges that OD plan v2.4 deleted; see §0.5). Per Pattern P1 byte-exact verification a placeholder carrier ID is a verification failure; resolution is a Form A citation-precision revision (the F3-02 precedent — OD plan v2.4 resolved exactly one such IS-side row, `U-IS-NN → U-IS-12`).

### §0.2 Resolution method

Each placeholder resolved to its canonical carrier unit by the **cited contract anchor** against the producer-axis plan coverage table (AS plan v1, CP plan v2). No carrier ID invented (X-AL-3 / `CLAUDE.md` I-2). Every contract anchor resolved to exactly one carrier unit; no Class 1 escalation. Full evidence: `.harness/cxa_7c_placeholder_resolution.md`.

### §0.3 The resolution — OD → AS (§4.5.2)

| Source unit | v2.1–v2.10 placeholder | Contract anchor | v2.11 canonical carrier |
|---|---|---|---|
| U-OD-17 | `U-AS-NN` | C-AS-12 §12.1 | **U-AS-14** |
| U-OD-19 | `U-AS-NN` | C-AS-15 §15.6 | **U-AS-19** |
| U-OD-23 | `U-AS-NN` | C-AS-15 §15.4 | **U-AS-18** |
| U-OD-23 | `U-AS-NN` | C-AS-14 §14.2 | **U-AS-31** |
| U-OD-29 | `U-AS-NN` | C-AS-12 §12.4 | **U-AS-15** |
| U-OD-33 | `U-AS-NN` | C-AS-12 §12.1 | **U-AS-14** |
| U-OD-33 | `U-AS-NN` | C-AS-15 §15.6 | **U-AS-19** |
| U-OD-33 | `U-AS-NN` | C-AS-12 §12.4 | **U-AS-15** |

### §0.4 The resolution — OD → CP (§4.5.3)

| Source unit | v2.1–v2.10 placeholder | Contract anchor | v2.11 canonical carrier |
|---|---|---|---|
| U-OD-17 | `U-CP-NN` | C-CP-19 (refined → §19.2) | **U-CP-43** |
| U-OD-19 | `U-CP-NN` | C-CP-14 §14.1 | **U-CP-32** |
| U-OD-21 | `U-CP-NN` | C-CP-04 | **U-CP-09** |
| U-OD-23 | `U-CP-NN` | C-CP-20 §20.6 | **U-CP-46** |
| U-OD-26 | `U-CP-NN` | C-CP-21 §21.5 | **U-CP-47** |
| U-OD-30 | `U-CP-NN` | C-CP-20 §20.4 | **U-CP-46** |
| U-OD-33 | `U-CP-NN` | C-CP-19 (refined → §19.2) | **U-CP-43** |

### §0.5 IS-side unit-body carries — propagation of the OD plan v2.4 §4.5.1 resolution

OD plan v2.4 §0.4.2 revised the §4.5.1 OD→IS enumeration (6-row → 4-row) but did **not** propagate the resolution into the affected unit bodies' `Depends on` declarations — v2.4 §0.6 noted "within-axis topology unaffected" and left the unit-body cross-axis terms unchanged (confirmed at OD plan v2.6 §3.7.1, which preserved the U-OD-27 `Depends on` verbatim). Two unit bodies therefore still carry `U-IS-NN` placeholders inconsistent with the v2.4-canonical §4.5.1. v2.11 propagates the v2.4 resolution into both bodies — a restatement of an already-canonical v2.4 decision, not a new decision:

- **U-OD-30** — body `Depends on` carried `U-IS-NN (C-IS-14 §14.2)`, `U-IS-NN (C-IS-13 §13.5)`. OD plan v2.4 **remapped** these (→ **U-IS-11** C-IS-10 §10.5; → **U-IS-10** C-IS-10 §10.3). v2.11 writes the remap into the body.
- **U-OD-27** — body `Depends on` carried `U-IS-NN (cross-axis: IS — C-IS-13 §13.2)`, `U-IS-NN (cross-axis: IS — C-IS-08 §8.4)`. OD plan v2.4 §0.4.2 **deleted** both rows from §4.5.1: the cited contracts are non-resolving in IS spec v1.2, and sqlite substrate residence + ring-buffer eviction are OD-axis-**internal**, not IS-axis primitives — the v2.3 §4.5.1 rows falsely declared OD→IS edges where none exist. v2.11 **strikes** both `U-IS-NN` cross-axis terms from the U-OD-27 body `Depends on` (leaving `[U-OD-01, U-OD-23]`); U-OD-27 is not an OD→IS cross-axis source. U-OD-27's within-axis content, signatures, `SpanRow`/`EvictionAction` in-unit declarations, and acceptance criteria are unchanged.

### §0.6 Per-unit `Depends on` revision (Form A — citation precision)

The cross-axis terms of each affected unit's `Depends on` declaration and the matching "Cross-axis dependency resolution" prose are revised; **all within-axis terms, signatures, acceptance criteria, Inputs, and rollback boundaries are preserved verbatim.**

| Unit | v2.10 cross-axis `Depends on` terms | v2.11 cross-axis `Depends on` terms |
|---|---|---|
| U-OD-17 | `U-AS-NN (cross-axis: AS — C-AS-12 §12.1), U-CP-NN (cross-axis: CP — C-CP-19)` | `U-AS-14 (cross-axis: AS — C-AS-12 §12.1), U-CP-43 (cross-axis: CP — C-CP-19 §19.2)` |
| U-OD-19 | `U-AS-NN (cross-axis: AS — C-AS-15 §15.6), U-CP-NN (cross-axis: CP — C-CP-14 §14.1)` | `U-AS-19 (cross-axis: AS — C-AS-15 §15.6), U-CP-32 (cross-axis: CP — C-CP-14 §14.1)` |
| U-OD-21 | `U-CP-NN (cross-axis: CP — C-CP-04 cross-family fallback chain)` | `U-CP-09 (cross-axis: CP — C-CP-04 cross-family fallback chain)` |
| U-OD-23 | `U-AS-NN (cross-axis: AS — C-AS-15 §15.4 + C-AS-14 §14.2), U-CP-NN (cross-axis: CP — C-CP-20 §20.6)` | `U-AS-18 (cross-axis: AS — C-AS-15 §15.4), U-AS-31 (cross-axis: AS — C-AS-14 §14.2), U-CP-46 (cross-axis: CP — C-CP-20 §20.6)` |
| U-OD-26 | `U-CP-NN (cross-axis: CP — C-CP-21 §21.5)` | `U-CP-47 (cross-axis: CP — C-CP-21 §21.5)` |
| U-OD-29 | `U-AS-01 (cross-axis: AS — SandboxTier enum, C-AS-01 §1.1), U-AS-NN (cross-axis: AS — C-AS-12 §12.4 sandbox-tier reachability)` | `U-AS-01 (cross-axis: AS — SandboxTier enum, C-AS-01 §1.1), U-AS-15 (cross-axis: AS — C-AS-12 §12.4 sandbox-tier reachability)` |
| U-OD-27 | `U-OD-01, U-OD-23, U-IS-NN (cross-axis: IS — C-IS-13 §13.2), U-IS-NN (cross-axis: IS — C-IS-08 §8.4)` | `U-OD-01, U-OD-23` (both `U-IS-NN` cross-axis terms struck — see §0.5; U-OD-27 is not an OD→IS source) |
| U-OD-30 | `U-IS-NN (cross-axis: IS — C-IS-14 §14.2), U-IS-NN (cross-axis: IS — C-IS-13 §13.5), U-CP-NN (cross-axis: CP — C-CP-20 §20.4)` | `U-IS-11 (cross-axis: IS — C-IS-10 §10.5), U-IS-10 (cross-axis: IS — C-IS-10 §10.3), U-CP-46 (cross-axis: CP — C-CP-20 §20.4)` |
| U-OD-33 | `U-AS-NN (cross-axis: AS — C-AS-12 §12.1 …), U-AS-NN (cross-axis: AS — C-AS-15 §15.6 …), U-AS-NN (cross-axis: AS — C-AS-12 §12.4 …), U-CP-NN (cross-axis: CP — C-CP-19 …)` | `U-AS-14 (cross-axis: AS — C-AS-12 §12.1), U-AS-19 (cross-axis: AS — C-AS-15 §15.6), U-AS-15 (cross-axis: AS — C-AS-12 §12.4), U-CP-43 (cross-axis: CP — C-CP-19 §19.2)` |

The "Cross-axis dependency resolution" prose paragraph of each of these **nine** units is revised to name the resolved carrier in place of `U-AS-NN` / `U-CP-NN` / `U-IS-NN` (for U-OD-27, the prose is revised to record that the two mis-routed edges are struck). No other unit-body text changes.

### §0.7 §4.5.2 / §4.5.3 enumeration revision

§4.5.2 (AS-consuming, 10 edges) and §4.5.3 (CP-consuming, 12 edges) `Cross-axis target` columns are revised from placeholder to canonical carrier per §0.3 / §0.4. §4.5.1 (IS-consuming, 4 edges) is unchanged from the v2.4 canonical enumeration. §4.5.4 aggregate cross-axis breakdown unchanged at 26 (IS 4 / AS 10 / CP 12).

### §0.8 Dependency-graph delta

Within-axis OD DAG: **unchanged.** All 35 units preserved; Kahn topological sort unchanged; acyclicity preserved. The revision touches only **cross-axis** edges. For eight of the nine units it is carrier identification only (placeholder → canonical; cross-axis edge cardinality unchanged, only the target unit ID made precise). For **U-OD-27** the cross-axis edge cardinality changes 2 → 0 (the two mis-routed OD→IS edges struck per §0.5) — this conforms the unit body to the already-canonical OD plan v2.4 §4.5.1 4-edge enumeration; no within-axis edge and no other unit is affected (U-OD-27 remains a within-axis leaf). Axis-level acyclicity (IS < AS < CP < OD) holds: every resolved carrier sits in a strictly-lower axis than its OD consumer.

### §0.9 Coverage matrix delta

None. Citation precision changes no contract→unit coverage mark. Every OD-spec contract anchor retains its covering unit.

### §0.10 Scope + sections preserved verbatim from v2.10

Revised: §4.5.2, §4.5.3, and the cross-axis `Depends on` term + "Cross-axis dependency resolution" prose of U-OD-17 / U-OD-19 / U-OD-21 / U-OD-23 / U-OD-26 / U-OD-27 / U-OD-29 / U-OD-30 / U-OD-33. Every other §0–§11 section — all signatures, all acceptance criteria, all Inputs, §4.5.1, §4.5.4, §4.6, §5–§11 — is **preserved verbatim from v2.10** (which itself preserved v2.9/v2.8/v2.7 verbatim except its noted deltas).

### §0.11 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_11.md` |
| Status | Proposed — Phase 7 7c prerequisite pass |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_10.md` (preserved verbatim except §0, §4.5.2, §4.5.3, and 9 unit-body cross-axis `Depends on` declarations) |
| Companion | `Cross_Axis_Composition_Document_v2_2.md`; `.harness/cxa_7c_placeholder_resolution.md` |
| Authored at | Phase 7 sub-phase 7c, 2026-05-16 (in-CLI) |
| Note | The resolved carrier IDs are plan-level `Depends on` declarations; the typed cross-axis imports are instantiated at 7c bucket wiring (the 7b OD code declared cross-axis deps in docstrings and deferred the imports to 7c). v2.11 carries no code change. |
