"""B-23 — `compose_cost_f2_entry_core` injective-key regression tests.

advisor() flagged (post round-5 out-of-family Codex review) that rounds 1-5
each closed ONE aliasing case at a time on the F2 identity's colon-joined
segments (burden_count, tenant, run-id, `_single`, span_id, empty-string
tenant) rather than the underlying defect class: a bare
`f"...:{workflow_id}:{parent_action_id}:..."` join is not injective when a
segment (e.g. `parent_action_id`, which is literally
`f"workflow:{workflow_id}:step:{n}"`) contains the `:` join separator.
These tests exercise that closed class directly against the shared helper,
independent of any one composer.
"""

from __future__ import annotations

from pathlib import Path

from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_write import read_ledger
from harness_runtime.lifecycle.cost_attribution_f2_write import compose_cost_f2_entry_core
from harness_runtime.lifecycle.state_ledger import LedgerWriter

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-cost-attribution")


def _build_ledger_writer(tmp_path: Path) -> LedgerWriter:
    path = tmp_path / "state.jsonl"
    path.touch()
    handle = JsonlLedgerHandle(canonical_path=path, exists=True, entry_count=0)
    return LedgerWriter(handle=handle, actor=_ACTOR)


def test_colon_shifted_workflow_and_parent_action_id_do_not_alias(tmp_path: Path) -> None:
    """`parent_action_id` is production-shaped as `workflow:{wf}:step:{n}` —
    a colon-containing value. A naive colon-join collapses
    `(workflow_id="a", parent_action_id="b:c")` and
    `(workflow_id="a:b", parent_action_id="c")` onto the same string; the
    length-prefixed encoding must keep them distinct."""
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        ledger_writer=ledger_writer,
        procedural_tier_snapshot_resolver=None,
        parent_idempotency_key="parent-idem",
        dispatch_disambiguator="span-1",
    )
    ref_a = compose_cost_f2_entry_core(workflow_id="a", parent_action_id="b:c", **common)
    ref_b = compose_cost_f2_entry_core(workflow_id="a:b", parent_action_id="c", **common)

    assert ref_a is not None
    assert ref_b is not None
    assert str(ref_a) != str(ref_b)

    entries = read_ledger(ledger_writer.handle)
    cost_action_ids = {str(e.action_id) for e in entries if str(e.action_id).startswith("cost:")}
    assert len(cost_action_ids) == 2


def test_colon_shifted_parent_idempotency_key_and_disambiguator_do_not_alias(
    tmp_path: Path,
) -> None:
    """Same class, adjacent segment pair — `parent_idempotency_key` and
    `dispatch_disambiguator` shifted across their shared `:` boundary."""
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        ledger_writer=ledger_writer,
        procedural_tier_snapshot_resolver=None,
        workflow_id="wf",
        parent_action_id="workflow:wf:step:0",
    )
    ref_a = compose_cost_f2_entry_core(
        parent_idempotency_key="x", dispatch_disambiguator="y:z", **common
    )
    ref_b = compose_cost_f2_entry_core(
        parent_idempotency_key="x:y", dispatch_disambiguator="z", **common
    )

    assert ref_a is not None
    assert ref_b is not None
    assert str(ref_a) != str(ref_b)


def test_tenant_none_vs_empty_string_do_not_alias(tmp_path: Path) -> None:
    """`tenant_id=None` (no-tenant) and `tenant_id=""` (explicit, legal-but-
    falsy) must not collapse onto the same F2 identity — the presence flag
    distinguishes them regardless of the value segment's content."""
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        ledger_writer=ledger_writer,
        procedural_tier_snapshot_resolver=None,
        workflow_id="wf",
        parent_action_id="workflow:wf:step:0",
        parent_idempotency_key="parent-idem",
        dispatch_disambiguator="span-1",
    )
    ref_none = compose_cost_f2_entry_core(tenant_id=None, **common)
    ref_empty = compose_cost_f2_entry_core(tenant_id="", **common)

    assert ref_none is not None
    assert ref_empty is not None
    assert str(ref_none) != str(ref_empty)


def test_tenant_value_containing_colon_does_not_alias_across_boundary(tmp_path: Path) -> None:
    """A tenant_id containing `:` must not shift into the workflow_id
    segment under a naive join."""
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        ledger_writer=ledger_writer,
        procedural_tier_snapshot_resolver=None,
        parent_action_id="workflow:wf:step:0",
        parent_idempotency_key="parent-idem",
        dispatch_disambiguator="span-1",
    )
    ref_a = compose_cost_f2_entry_core(tenant_id="t:1", workflow_id="wf", **common)
    ref_b = compose_cost_f2_entry_core(tenant_id="t", workflow_id="1:wf", **common)

    assert ref_a is not None
    assert ref_b is not None
    assert str(ref_a) != str(ref_b)
