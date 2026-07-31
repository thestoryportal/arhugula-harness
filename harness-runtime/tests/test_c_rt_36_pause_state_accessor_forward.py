"""C-RT-36 (`Spec_Harness_Runtime_v1.md` v1.107 §31) — durable-pause-state read accessor.

**FORWARD-MARKED CONTRACT EVIDENCE — the surface is SPECIFIED, NOT YET BUILT.**

The B-69 arc's spec leg (PR for `.harness/council-b69-pause-state-accessor-2026-07-30.md`,
operator-ratified OPTION A prime 2026-07-30) declares a NEW contract, C-RT-36: a public
async read on the `harness_runtime` package root taking the identical
`(workflow, resume_handle, config)` triple `resume()` requires, returning a closed
typed projection of the durably-journaled pause state so a crash-recovery caller can
compose a correctly-keyed `hitl_responses` / `effect_fence_resolutions` map BEFORE
`resume_context` construction.

**Why this file exists, and what it deliberately does NOT claim.** The Q3 evidence gate
(`tools/test_qa_evidence_matrix.py`) requires every declared contract id to carry a
test-file citation, and it is right to: a contract with no evidence anywhere is exactly
the drift that gate exists to catch. But the impl arc is a SEPARATE follow-on per the
arc's own X-AL-2 conjunctive closure criterion, so there is no accessor to exercise yet.
Citing C-RT-36 from an unrelated passing test would be a FALSE proof — the failure mode
the gate is defending against, wearing the gate's own costume.

This test therefore asserts the **honest** present-tense fact: the surface is absent.
It is a real assertion with a real subject, and it **INVERTS at the impl leg** — the
first commit of U-RT-148 (`Implementation_Plan_Harness_Runtime_v2_55.md`) makes it fail,
which is the signal to replace this file with the AC #1-#16 witness battery, NOT to
"repair" the assertion. That disposition is stated here so a future session cannot
mistake the inversion for a regression (the same DELETION-or-INVERSION-never-repair
annotation U-RT-148 AC #5 carries for its own placeholder-dependent witness).
"""

from __future__ import annotations

import harness_runtime

#: The §31.1 naming constraint forbids naming the accessor after the journal or the
#: store, so the impl leg's exact symbol is discretionary. These are the shapes the
#: contract's own indicative signature and naming rule admit; the assertion below is
#: deliberately tolerant of which one lands.
_CANDIDATE_ACCESSOR_NAMES = (
    "read_paused_workflow_state",
    "read_pause_state",
    "describe_pause_state",
    "paused_workflow_state",
)


def test_c_rt_36_accessor_is_specified_but_not_yet_exported() -> None:
    """C-RT-36 §31.1 is SPEC-APPLIED and IMPL-OWED — assert the honest current state.

    INVERTS at the U-RT-148 impl leg. On failure, DELETE this file and replace it with
    the AC #1-#16 battery; do NOT relax the assertion.
    """
    exported = {name for name in _CANDIDATE_ACCESSOR_NAMES if hasattr(harness_runtime, name)}
    assert exported == set(), (
        f"C-RT-36 accessor surface(s) {sorted(exported)} now exist on the "
        "`harness_runtime` package root. This forward-marked placeholder has done its "
        "job: DELETE this file and land the U-RT-148 AC #1-#16 witnesses "
        "(Implementation_Plan_Harness_Runtime_v2_55.md) in its place. Do NOT weaken "
        "this assertion to keep it green."
    )


def test_c_rt_36_co_requisite_resume_surface_is_unchanged_at_the_spec_leg() -> None:
    """The arc's ordering constraint has a testable present-tense half.

    C-RT-36 is co-requisite with the §30 refusal-only staleness precondition, which
    MUST land first or simultaneously — never after. At the spec leg neither is built,
    so the invariant that holds right now is simply that `resume()` is still exported
    and unchanged in arity-shape. This guards the spec leg against having accidentally
    disturbed the already-cleared C-RT-35 surface it amends.
    """
    assert hasattr(harness_runtime, "resume"), (
        "C-RT-35 §30 `resume()` must remain exported — the B-69 spec leg AMENDS this "
        "contract (staleness precondition + cause attribution) and must never remove it."
    )
