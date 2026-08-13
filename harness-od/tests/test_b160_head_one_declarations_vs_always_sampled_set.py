"""B-160 grounding witness — the head=1.0 divergence is a CLASS, not an instance.

`B-160` was registered from the B-71 leak analysis with one known case
(`hitl.webhook.deliver`), and its close-out set a grounding step before any repair:
*"check whether any OTHER C-OD-3x namespace declares head=1.0 without §9.2 membership —
if so this is a class, not an instance."*

**It is a class.** Four unconditional `head=1.0` declarations across **two** contracts are
absent from `ALWAYS_SAMPLED_EVENT_CLASSES`, which §9.2 defines as exactly that floor.

**Why this is not the B-153 category mistake.** That precedent turned on a genuine
category error — span names were being counted as attributes. Here the set's own members
are span/event names of the same shape as the missing ones (`hitl.gate.evaluated`,
`hitl.invocation.opened`, `topology.fanout.opened`, `mcp.tool.call`), and no wildcard
covers the absentees: the `hitl.invocation.*` members are enumerated individually and
there is no `hitl.*` or `pause.*` wildcard (unlike `audit.*` / `validator.fail.*`). So the
four names belong to the set by shape and are simply not in it.

**Conditional declarations are deliberately excluded** from the class. `mcp.trust.evaluate`
(head=1.0 only when `audit_required`) and the operator-burden spans (head=1.0 only on
`degrade=true`) are conditional rows, which §9.2 handles through its four conditional
entries; they are not evidence of the same divergence and are not asserted here.

**What this witness does NOT claim.** It does not say which side is wrong. Repairing the
implementation side is *not* sufficient on its own — `ParentBased(root=…)` never consults
a non-root child's name, so membership alone cannot deliver the floor for a child span
(the `B-137` dependency B-160 already carries). This module pins the divergence so it
cannot be closed silently in either direction.
"""

from __future__ import annotations

import pathlib

import harness_od.hitl_webhook_namespace as _webhook_ns
import harness_od.pause_resume_namespace as _pause_ns
from harness_od.sampling_mode import ALWAYS_SAMPLED_EVENT_CLASSES

#: Span names whose owning C-OD-3x contract declares an UNCONDITIONAL head=1.0.
_DECLARED_HEAD_ONE: dict[str, str] = {
    "hitl.webhook.deliver": "C-OD-32.3",
    "hitl.webhook.attempt": "C-OD-32.3",
    "pause.captured": "C-OD-30.3",
    "resume.attempted": "C-OD-30.3",
}


def test_the_contracts_really_do_declare_unconditional_head_one() -> None:
    """Ground the CONTRACT side before asserting anything about the set.

    Read off the namespace modules that carry the declarations verbatim, so this witness
    fails loudly if a contract is reworded rather than silently re-basing on stale text.
    """
    webhook_doc = pathlib.Path(_webhook_ns.__file__).read_text()
    assert "Webhook spans head=1.0 (always-sampled" in webhook_doc

    pause_doc = pathlib.Path(_pause_ns.__file__).read_text()
    assert "`pause.captured` head=1.0 (always-sampled" in pause_doc
    assert "`resume.attempted` head=1.0" in pause_doc


def test_the_divergence_is_a_class_across_two_contracts() -> None:
    """**The grounding result B-160's close-out asked for.**

    All four unconditional head=1.0 names are missing from the §9.2 floor set, and they
    come from two different contracts — so the repair is a conformance sweep, not a
    one-name edit.
    """
    missing = {n: c for n, c in _DECLARED_HEAD_ONE.items() if n not in ALWAYS_SAMPLED_EVENT_CLASSES}

    assert missing == _DECLARED_HEAD_ONE, (
        "the divergence changed — re-ground B-160 before acting on its close-out; "
        f"still-missing={sorted(missing)}"
    )
    assert len(set(missing.values())) == 2, (
        f"expected the class to span TWO contracts, got {sorted(set(missing.values()))}"
    )


def test_the_set_is_span_name_shaped_so_these_names_belong_in_it() -> None:
    """Rules out the B-153 category mistake — the reason this is a real divergence.

    If the set were a different taxonomy (as span-names-vs-attributes was at B-153), the
    absentees would be a category error rather than a gap. It is not: the set already
    carries span/event names of exactly this shape.
    """
    for exemplar in (
        "hitl.gate.evaluated",
        "hitl.invocation.opened",
        "topology.fanout.opened",
        "mcp.tool.call",
    ):
        assert exemplar in ALWAYS_SAMPLED_EVENT_CLASSES

    # ...and no wildcard covers the absentees, unlike `audit.*` / `validator.fail.*`.
    wildcards = {m for m in ALWAYS_SAMPLED_EVENT_CLASSES if m.endswith("*")}
    assert wildcards, "expected the set to carry at least one wildcard family"
    for missing_name in _DECLARED_HEAD_ONE:
        prefixes = {w[:-1] for w in wildcards}
        assert not any(missing_name.startswith(p) for p in prefixes), (
            f"{missing_name} IS wildcard-covered — B-160's premise needs re-grounding"
        )
