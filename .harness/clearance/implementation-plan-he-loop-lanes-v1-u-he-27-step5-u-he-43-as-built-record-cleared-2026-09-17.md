---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-09-17 (U-HE-27 Step 5 tick with its applied-2026-09-17 record; U-HE-43 as-built plan record — Unit-status paragraph and Steps 1–4 ticks; no step text, contract number, row label or ordering changes)
cleared_at: 2026-09-17T17:30:00Z
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-27 Step 5: ticked, with the apply record inline and the 'expect 404 today' expectation marked historical; U-HE-43 section: dated Unit-status paragraph above the steps in the #1519 shape; Steps 1, 2–3, 4 ticked)"
  - ".harness/plan/evidence-log-he-loop-lanes.md (the 2026-09-17T08:04:12Z apply entry carries the outcome record: second confirm on digest 81cd03a786a668fa after the 07:01Z rollback, tiebreaker PASS on #1555/#1556, protection persists, verify PASS)"
  - "PR #1550 (U-HE-43 merged 2026-09-17, e0b8c36a9), PR #1553 (tiebreaker watches required checks only, e73dfe48c), PR #1557 (rtk paren shape version-gated + 71 Phase-0 pins re-pinned, c4cd81f1a), PR #1558 (the terminating refresh recording #1555/#1556/#1557)"
  - ".harness/clearance/implementation-plan-he-loop-lanes-v1-u-he-38-39-42-as-built-record-cleared-2026-09-16.md (the Rev 2026-09-16 record this one follows; unchanged here)"
  - ".harness/forward-register.yaml B-250, B-251, B-252 (the U-HE-43 readings registered rather than absorbed), B-253 (the tiebreaker's un-refreshed landings, registered on this same PR)"
---

What changed and why it is a record, not an extension:

Two units get the plan record the #1519 shape established. U-HE-27's Step 5 —
the ONE operator decision that unit surfaces — is ticked with the fact of its
application inline (date, digest, the one rollback and its cause, the PASS,
the verify), and its "expect 404 today" instruction is marked historical: a
protected `main` now returns the live policy. U-HE-43 gets a dated Unit-status
paragraph stating what shipped and where the shipped reducer diverges from the
plan's sketch (catch-rounds, pending-while-undisposed, the evidence digest in
the delivery identity, the bounded HITL detail, emission outside the lock, the
`*-shadow` lens rule), and which register rows carry the readings the spec
does not state. Four step boxes are ticked. A tick means the step was carried
out; it never asserts that the plan's sketch is what shipped.

No contract number, field name, schema, row label, step text or §6 ordering
changes; the spec text of C-HE-08 and C-HE-29 is untouched. Operator may
reverse by a dated plan note.
