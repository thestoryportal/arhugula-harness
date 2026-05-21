# Class 3 Tension — Meta-Architecture HITL palette-value drift from canonical CP spec

**Filed:** 2026-05-20 — surfaced during systems-architect mode 3 orientation against `[[fork-cp-20-hitl-gate-composer-underspec]]` HEAD `2a15504`.
**Surfaced by:** `systems-architect` skill mode 3 orientation read of `Phase_7_Meta_Architecture_v1.md` §5 substitution-table H_T-CP-20 row vs canonical CP spec v1.9 §16.1.
**Defect class:** Class 3 — citation-precision drift in a Phase 7 governance file; non-blocking; canonical spec wins per authority chain.

---

## Defect

`Phase_7_Meta_Architecture_v1.md` §5 substitution-table row for H_T-CP-20 (line 23 + line 384) declares the H_T HITL 4-response palette values as:

```
APPROVE / APPROVE_WITH_NOTE / DEFER / REJECT
```

Canonical CP spec v1.9 §16.1 (the load-bearing spec contract per authority chain `CLAUDE.md` §1.3) declares the 4-response palette as:

```
APPROVE / EDIT / REJECT / RESPOND
```

(Verified at U-CP-37 unit declaration: `enum HITLResponse { APPROVE, EDIT, REJECT, RESPOND }` per Implementation_Plan_Control_Plane_v2_1.md:1939; ratified at C-CP-16 §16.1.)

The Meta-Architecture file values (`APPROVE_WITH_NOTE`, `DEFER`) do not appear anywhere in the CP spec v1.9 contract.

## Class 3 classification rationale

| Criterion | Reading |
|---|---|
| Defect locus | Phase 7 governance file (`Phase_7_Meta_Architecture_v1.md`) — Phase 7 substitution-table descriptive prose, NOT a canonical design-phase spec contract |
| Authority chain priority | CP spec v1.9 §16.1 wins per `CLAUDE.md` §1.3 (ADR → ADD → PRD → **spec** → plan; Meta-Architecture is Phase-7-execution governance, sibling to spec, not ancestor) |
| Blocking? | No — the Meta-Architecture row is descriptive characterization of H_E surface coverage gaps; the canonical palette values live at CP spec + the materialized typed library (`harness-cp/src/harness_cp/hitl_response_palette.py`) |
| Silent-absorption hazard? | Low — no downstream artifact materializes against the Meta-Architecture values; the spec contract + typed library are the load-bearing surfaces |
| Pattern match | `[[spec-prose-plan-body-drift-pattern]]` — descriptive prose diverges from canonical contract; contract is unambiguous; file Class 3 |

## Resolution

**No in-pass patch.** Per workspace `CLAUDE.md` §4.3 silent-absorption hazard, patching Meta-Architecture inside the current systems-architect arc (which is opening C-RT-18 spec authoring, not addressing Phase 7 governance hygiene) would be silent absorption of unrelated drift.

**Routed to next Meta-Architecture revision pass** touching the H_T-CP-20 substitution row OR a dedicated Class 3 cleanup arc. Suggested replacement text:

```
H_T-CP-20 | `AskUserQuestion` tool + permission-prompt approval; no 4-response palette; no `hitl.*` / `audit.*` namespaces | Covers: HITL invocation surface. Does NOT cover: 4-response palette (APPROVE / EDIT / REJECT / RESPOND per C-CP-16 §16.1); namespace emission | U-CP-46
```

(Two-character delta from current text: `APPROVE_WITH_NOTE / DEFER` → `EDIT / RESPOND`.)

## Affected lines

- `Phase_7_Meta_Architecture_v1.md` line 23 (§5 substitution table row)
- `Phase_7_Meta_Architecture_v1.md` line 384 (§? second occurrence in narrative — verify line at patch time)

## Status footer

| Field | Value |
|---|---|
| Filed | 2026-05-20 |
| HEAD at filing | `2a15504` |
| Class | 3 (informational; non-blocking) |
| Resolution policy | Defer to next Meta-Architecture revision pass touching the H_T-CP-20 row OR dedicated Class 3 cleanup arc |
| Authority chain | CP spec v1.9 §16.1 wins; Meta-Architecture absorbs at revision pass |
| Status | **OPEN** — bounded informational drift |
| Related | `[[fork-cp-20-hitl-gate-composer-underspec]]` (surfacing context) |

---

*End of Class 3 record. Tracked at `MEMORY.md` index. No blocking effect on Phase 7 7b composer arcs.*
