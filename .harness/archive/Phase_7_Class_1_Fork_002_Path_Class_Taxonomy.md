# Phase 7 — Class 1 Fork Record 002 — Path-Class Taxonomy

*Back-flow routing record. Detected during Fork 001 resolution. Operator
authorized in-session resolution 2026-05-15. RESOLVED same session.*

---

## §1 State

| Field | Value |
|---|---|
| Fork class | **Class 1** (governance artifact drifted from canonical spec) |
| Detected at | Phase 7 Session 1, sub-phase 7a — during Fork 001 edit-site location |
| Status | **RESOLVED** — drift corrected in-workspace 2026-05-15 per operator authorization |

## §2 Defect

`Phase_7_Meta_Architecture_v1.md §7.2` anti-leakage rule **IS-AL-1** named the
four H_T path classes **"(artifact / cache / state / secret)"** — a taxonomy
inconsistent with the canonical contract.

| Artifact | 4 path classes |
|---|---|
| `Spec_Information_Substrate_v1.md §1` (C-IS-01 — canonical contract) | Skills / Prompts / Routing manifest / State-ledger |
| `harness-is/CLAUDE.md §4.2` IS-AL-1 | `SKILLS` / `PROMPTS` / `ROUTING_MANIFEST` / `STATE_LEDGER` |
| `Phase_7_Meta_Architecture_v1.md §7.2` IS-AL-1 (pre-fix) | `artifact / cache / state / secret` ❌ |

"cache" and "secret" are not C-IS-01 path classes. Same drift pattern as
Fork 001 (governance artifact diverged from canonical spec).

## §3 Resolution

Single drift site: `Phase_7_Meta_Architecture_v1.md` §7.2 IS-AL-1 (one line).
Corrected to `(`SKILLS` / `PROMPTS` / `ROUTING_MANIFEST` / `STATE_LEDGER`)` —
byte-consistent with `harness-is/CLAUDE.md §4.2` IS-AL-1 and the canonical
C-IS-01 §1 four-class set.

No other site carried the wrong taxonomy (verified by workspace grep). The
Entry Directive §8.5 IS-AL-1 row carries no 4-class enumeration — unaffected.

Surface-1 scaffolding (`Phase_7a_Substitution_Scaffolding.md §1`) already used
the canonical C-IS-01 names — correct as authored; no rework.

## §4 Reconciliation owed

Same as Fork 001 §7: the corrected `design-substrate/Phase_7_Meta_Architecture_v1.md`
diverges from the design-phase Claude.ai canonical source until pushed back
(or this workspace's copy formally designated canonical).
