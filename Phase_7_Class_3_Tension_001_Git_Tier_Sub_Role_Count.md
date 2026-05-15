# Phase 7 — Class 3 Spec Tension Record 001 — Git Tier Sub-Role Count

*Spec-tension record. Authored at tension detection during Phase 7 sub-phase
7b atomic-unit execution. Design-phase back-flow is deprecated (operator
directive 2026-05-15); spec fixes occur in Claude Code CLI sessions. This
record tracks the tension and the block-clearing decision per the
`Phase_7_Class_1_Fork_00N` pattern.*

---

## §1 Detection state

| Field | Value |
|---|---|
| Tension class | **Class 3** (determinate; non-halting — spec-prose defect, no implementation ambiguity) |
| Detected at | Phase 7 Session 1, sub-phase 7b, atomic unit **U-IS-04** (combined git tier sub-role taxonomy) |
| Detected | 2026-05-15 |
| Halt point | U-IS-04 implementation — surfaced before code execution |
| Status | **RESOLVED** — spec corrected in-CLI 2026-05-15; block cleared (§5) |

## §2 Defect

`Spec_Information_Substrate_v1.md` §3 (C-IS-03) contradicts itself on the
git-tier sub-role count.

**Spec prose said "four" — 5 occurrences in §3:**
- L178 contract surface — "Four-sub-role git tier composition"
- L182 ADR paraphrase — "ADR-F2 v1.2 §Decision (combined git tier serving
  four-sub-role composition)"
- L188 spec content — "serves four sub-roles"
- L198 co-residence contract — "All four sub-roles share the same git repository"
- L206 cross-sub-role invariant — "the four sub-roles share that ledger"

**Every authoritative source enumerates five:**
- `Spec_Information_Substrate_v1.md` §3 **table** — 5 rows: Versioning,
  State-ledger via commit stream, JSONL event ledger, Shadow-Git
  checkpointing, Worktree-isolation.
- `ADR-F2.md` §Decision (L19) — enumerates 5 distinct sub-roles
  ("versioning … plus … commit stream + JSONL event ledger … plus …
  shadow-Git checkpointing … plus … worktree-isolation"). Never says "four".
- ADD §2.2 Synthesis (quoted verbatim at spec §3 L182) — 5 items.
- `Implementation_Plan_Information_Substrate_v2_1.md` §2 U-IS-04 — `Inputs`
  cites "sub-role table (**5 rows**)"; signature enum `GitTierSubRole` has
  **5** values; acceptance #1 — "exactly **5** values."

## §3 Why Class 3 (not Class 1)

The defect is a stale spec count-word, not a substantive ambiguity. Every
authoritative source — the spec's own table, ADR-F2, the ADD, and the
execution-authority plan — agrees on the **same 5 named sub-roles**. The
correct implementation is determinate; U-IS-04 (execution authority) is
unambiguous. Execution does not truly halt — the unit is implementable as
written. Likely origin: "four" predates the spec splitting the state-ledger
surface into two rows (commit-stream + JSONL).

Not Class 1 — there is no halt-worthy ambiguity and no upstream-authority
defect (ADR-F2 is correct at 5).

## §4 Resolution

Spec corrected in-CLI 2026-05-15 (design-phase back-flow deprecated per
operator directive; `design-substrate/` is the canonical source). All 5
occurrences in `Spec_Information_Substrate_v1.md` §3: "four" → "five".

| File | Sites |
|---|---|
| `design-substrate/Spec_Information_Substrate_v1.md` | §3 L178, L182, L188, L198, L206 |

The L182 ADR paraphrase was safe to correct to "five-sub-role" — ADR-F2
§Decision itself enumerates 5 (the paraphrase, not the ADR, was wrong). No
ADR / ADD / plan change required — those artifacts were already consistent
at 5.

## §5 Block-clearing decision

| Field | Value |
|---|---|
| Decision | **CLEARED to proceed to U-IS-04 code execution.** |
| Authority | Operator directive 2026-05-15 — spec tensions fixed in-CLI; on a determinate fix, proceed to code after the spec correction + this record. |
| Rationale | The 5-value `GitTierSubRole` enum is determinate (ADR-F2 + ADD + spec table + plan all agree). Spec prose corrected; no residual ambiguity. |
| U-IS-04 implementation | Proceeds with the 5-value `GitTierSubRole` enum per the U-IS-04 signature + acceptance #1. |

## §6 Adjacent items (directed by the unit body — NOT tensions)

| # | Item | Disposition |
|---|---|---|
| 6.1 | `composition_with` for `STATE_LEDGER_VIA_COMMIT_STREAM` — spec §3 composition column cites a sibling *sub-role*, not a contract ID. | Empty list `[]` — acceptance #4 anchors to "contract ID per spec §3 column"; that row has none. |
| 6.2 | `JSONL_EVENT_LEDGER` composition — spec §3 column cites C-IS-05 + C-IS-06; the U-IS-04 signature *comment* says "C-IS-05/06/07". | Use spec — `[C-IS-05, C-IS-06]`. Acceptance #4 explicitly governs by the spec §3 column. Signature comment "/07" noted, not adopted. |
| 6.3 | `ContractID` type named in the signature but undefined. | Modelled as an opaque `str` NewType (same pattern as `WorkflowClass` at U-IS-02). |
