# Implementation Plan: Operational Discipline — v2.37 (delta over v2.36)

*Delta-only file. The v2.36 body and every existing `U-OD-NN` body are PRESERVED VERBATIM. This is the
OD plan leg of `Spec_Operational_Discipline_v1_43.md`, the companion to Runtime spec v1.137 Rule A4.*

**Status:** Cleared for source consumption by
`.harness/clearance/implementation-plan-operational-discipline-v2-37-cleared-2026-11-04.md` (ratification `cmt-7cc5fc50`).

---

## §0 Change-note (v2.36 → v2.37)

**Predecessor:** `Implementation_Plan_Operational_Discipline_v2_36.md`.

**Why.** OD spec v1.43 adds a sixth identifier, `superseded`, to the C-OD-30.5.1 cause attribution.
Without a unit the OD vocabulary has no execution authority, and Runtime plan v2.68 U-RT-160 portion
160a (accessor change, criterion 14) cannot proceed.

**Scope.** One new unit, `U-OD-62`, the next free OD unit ID after `U-OD-61` (verified at authoring:
no other `U-OD-62` in `design-substrate/` or `.harness/`). No existing unit amended, no new contract
number, no signature change to a landed unit. Owner assignment: integration-lead disposition LIT
`cmt-1ba063e7`, under claim `cmt-792618a5`.

## §1 NEW atomic unit — U-OD-62

### U-OD-62 — C-OD-30.5.1 sixth cause identifier `superseded`

**Source.** `harness-od/src/harness_od/pause_resume_namespace.py`: `PauseStateCauseAttribution`
(`:482-498`) gains `SUPERSEDED = "superseded"`; its docstring says six identifiers and cites Runtime
v1.137 Rule A4. No other source file changes in this unit.

**Tests.** `harness-od/tests/test_pause_resume_namespace.py` and
`harness-od/tests/test_pause_state_audit_payload_b69.py`, extended for the criteria below.

**Acceptance criteria** (OD spec v1.43 §2):

1. The enum has exactly six members with the six spec values; the existing five are unchanged.
2. The cross-surface identity witness compares the OD and Runtime accessor cause sets as exactly six
   equal strings; a seventh, missing or renamed member on either side fails it.
3. A failed-read audit payload with cause `superseded` carries `workflow_id` and the cause and no
   token or per-variant counts; a successful-read payload carries no cause.
4. Values outside the six are rejected at construction.
5. Each prior cause still yields its own identifier.

**Dependencies and gates.** Starts only after OD spec v1.43 and this plan are ratified and applied.
Lands no later than the Runtime U-RT-160 160a accessor change, since that change converts the sixth
value by value (`PauseStateCauseAttribution(cause.value)`) and would otherwise raise `ValueError`.
Runtime v1.137 witness I.13 is the installed fresh-process emission witness for both units.

**Not delivered here.** The Runtime accessor, refusal and CLI (U-RT-160); any other §30.5 change.

## §2 Coverage delta

C-OD-30.5.1 cause-attribution row → `U-OD-62`. No other coverage row changes.
