"""Identity-alias module — U-CORE-01.

Declares the nine cross-cutting identity `str`-newtype aliases consumed at
signature positions across the IS / AS / CP / OD axis plans. Each is a distinct
nominal type under `pyright` strict: a bare `str` is NOT assignable where an
alias is required, and no two aliases are interchangeable.

Seven aliases are traced to a committing spec contract per the U-CORE-01
`Implements` line. Two — `UnitId` and `ReferenceToUnit` — are **explicitly
plan-internal**, non-traced carrier-convenience newtypes (operator-ratified
Q-R1-5): `UnitId` is the atomic-unit identifier domain (`"U-CP-22"` etc.) the
plans use; `ReferenceToUnit` is consumed only at CP U-CP-41.

Where the committing contract defers the concrete identifier format (e.g.
C-IS-05 §5 does not pin the `action_id` byte format), the alias is `str`-typed
and the format is deliberately not pinned (acceptance criterion #6 — no spec
extension).

Authority: Implementation_Plan_Harness_Core_v1_1.md §2 U-CORE-01 (acceptance
criteria #3, #6); C-IS-05 §5; C-CP-05 §5.2; C-CP-13 §13.4; C-AS-03 §3;
C-CP-01 §1.
"""

from __future__ import annotations

from typing import NewType

# --- traced identity aliases -------------------------------------------------

ActionID = NewType("ActionID", str)
"""C-IS-05 §5 — the F2 state-ledger entry-shape `action_id` field."""

EntryID = NewType("EntryID", str)
"""C-IS-05 §5 — state-ledger entry identifier."""

WorkflowID = NewType("WorkflowID", str)
"""C-CP-05 §5.2 — `workflow.id` identifier carried on lifecycle event spans."""

StepID = NewType("StepID", str)
"""C-CP-05 §5.2 — step-boundary identifier."""

ThreadID = NewType("ThreadID", str)
"""C-CP-05 §5.2 — `thread_id`, the idempotent-write keying-tuple member."""

StageID = NewType("StageID", str)
"""C-CP-13 §13.4 — handoff/stage identifier."""

ContractID = NewType("ContractID", str)
"""C-AS-03 §3 / C-CP-01 §1 — tool/routing contract identifier."""

# --- plan-internal aliases (non-traced; operator-ratified Q-R1-5) ------------

UnitId = NewType("UnitId", str)
"""Plan-internal — the atomic-unit identifier domain (e.g. ``"U-CP-22"``).

Not traced to a spec/ADR section; a carrier-convenience newtype.
"""

ReferenceToUnit = NewType("ReferenceToUnit", str)
"""Plan-internal — a reference to an atomic unit; consumed only at CP U-CP-41.

Not traced to a spec/ADR section; a carrier-convenience newtype.
"""
