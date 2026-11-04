# Fork record — Runtime resume: superseded-record refusal and `harness resume`

**Class:** 1 (design-substrate amendment), absorbed through a documented bundled back-flow source arc
(CLAUDE.md §11.4). The integration lead accepted the B-310 v4 definition and broadened B-314 under the
accepted release campaign (LIT `arhugula-harness-trial-193`, `cmt-fe2c7b08-00c3-4838-8b9e-562d34699de4`).
One combined candidate covers B-310, B-313 and the B-314 prerequisite (work record
`cmt-9a055b8f-010e-47ae-88f4-de8a21817bbc`). No new H_T primitive or cross-axis edge. Authorities are
pinned in `.harness/runtime-resume-contract-authority.md` (Proposed; not cleared).

## Fork

- **What the contract requires.** The accepted operator surfaces are CLI and MCP (B-312 excludes a
  separate HTTP surface). A CLI operator must be able to resume a durable workflow-layer pause through
  `api.resume` without a second claim, journal or approval store (B-310), and each root refusal must
  reach the operator as a closed typed value with its own exit code (B-313).
- **Why current source cannot meet it.** The CLI has no `resume` subcommand and defines exits 0–5
  only. The journal holds one record kind, so a workflow-layer record stays resumable after a later
  run of the same workflow paused engine-natively, completed or failed: a resume would replay a stale
  pause over newer state (B-314 broadened scope).
- **What the existing seams provide.** Every fresh root run enters the MCP tool `run_workflow` and its
  root admission; journal appends already serialize under one cross-process lock; the resume claim
  already refuses a record that is no longer the latest.

## Disposition

- Runtime spec **v1.137** (Proposed, numbered after Proposed v1.135 and v1.136; amends no site they
  amend):
  - a second journal record kind, the supersession record, appended by the fresh-run root admission;
  - a `superseded` read attribution, the refusal `ResumePauseRecordSupersededError`, and the
    pause-state accessor's `superseded` failure cause and audit value (with a companion OD C-OD-30.5.1
    amendment that this arc names but does not author);
  - a ninth arm `pause-record-superseded` on the B-313 v2 closed value;
  - the `harness resume` subcommand, exits 6 and 7, the failure-mode row, and the replaced exit-5
    row (b).
- Plan **v2.68** adds U-RT-160, delivered as portions 160a (Runtime prerequisite) and 160b (CLI).
- No source, test or operator-guide change is made by this arc.

## Open

- The original B-314 obligation, a safe resume path for engine-native pauses, stays OPEN.
- B-311 (daemon resume and its MCP refusal reply) and B-315 (approval collection) are not defined.
- The HITL probe (spec §I.11) decides whether a Runtime-side refusal is needed before acceptance.
- Cross-binding supersession (disposition `cmt-1ba063e7`): no binding exception. Spec Rule B7 records
  that current bindings cannot carry the invariant and names the missing shared authority, an
  installation-level per-tenant pause-journal root. After HOLD `cmt-1087cb00` (disposition
  `cmt-8b76cb48`) that root is the only journal location for read, write, supersession and claim; the
  binding-cell fan-out is removed. Its storage selection and binding evidence (owner Buford) and the
  C-IS-01 companion (owner profile-coder; authored at IS spec v1.17 §1.1 and IS plan v2.11 U-IS-21)
  are prerequisites
  outside this delta. No implementation is accepted and `harness resume` is not exposed until both are
  ratified and applied; witnesses I.2 case (d) and I.14 then gate acceptance. After HOLD `cmt-b64cde80`
  the durable snapshot capture resolves the same root (Rule B3), and journals already persisted under a
  STATE_LEDGER cell get a fail-closed cutover with no migration and no legacy read by any journal
  operation; after HOLD `cmt-e4e959b9` (disposition `cmt-49143c9e`) the operator-only `harness-inspect`
  keeps its read-only pre-upgrade inventory (Rule B8, witness I.15). An unresolved root refuses a resume as `protocol-not-bound` (Rule B7 item 3).
- The companion OD C-OD-30.5.1 amendment is authored at `Spec_Operational_Discipline_v1_43.md` and OD
  plan v2.37 unit U-OD-62 (owner profile-coder, same claim); it needs ratification before Runtime
  implementation ratification.
- Whether a child run can share its root's workflow_id is pinned by a witness, not assumed.

## Clearance

Owed after independent review of the exact head:
- ratification of spec v1.137 and plan v2.68, then their markers and derived head rows, filed by the
  integration lead;
- an integration collision check against the A3 v1.134/v2.65 fold and the Proposed A5 and A4 deltas,
  including the U-RT-160 unit ID.
