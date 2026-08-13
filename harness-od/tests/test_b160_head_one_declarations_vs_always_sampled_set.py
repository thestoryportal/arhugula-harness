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

**Two more, as a CONDITIONAL subtype.** A first draft excluded `mcp.trust.evaluate`
(head=1.0 iff `audit_required`) and the operator-burden span (head=1.0 iff `degrade`) on
the premise that §9.2's conditional rows covered them. **That premise is false** — those
four rows are `files.operation`, `memory.operation`, `validator.fail.*` and
`subagent.span` (`sampling_mode.py:176-190`), none of which is either name. So the class
is **six** span families in two shapes: four unconditional, two conditional, none of them
reachable by the floor the contracts declare.

**What this witness does NOT claim.** It does not say which side is wrong. Repairing the
implementation side is *not* sufficient on its own — `ParentBased(root=…)` never consults
a non-root child's name, so membership alone cannot deliver the floor for a child span
(the `B-137` dependency B-160 already carries). This module pins the divergence so it
cannot be closed silently in either direction.
"""

from __future__ import annotations

import pathlib

import harness_od.hitl_operator_burden_namespace as _burden_ns
import harness_od.hitl_webhook_namespace as _webhook_ns
import harness_od.mcp_trust_namespace as _trust_ns
import harness_od.pause_resume_namespace as _pause_ns
from harness_od.sampling_mode import ALWAYS_SAMPLED_EVENT_CLASSES

#: Span names whose owning C-OD-3x contract declares an UNCONDITIONAL head=1.0.
#: DERIVED from each namespace's own `SPAN_SITE_*` constant rather than re-typed as
#: literals (out-of-family Codex): a literal table would keep checking the OLD names if a
#: contract added or renamed a span site while keeping its generic sampling sentence, and
#: since the old names stay absent the assertion would stay green over a changed contract.
_DECLARED_HEAD_ONE: dict[str, str] = {
    _webhook_ns.SPAN_SITE_HITL_WEBHOOK_DELIVER: "C-OD-32.3",
    _webhook_ns.SPAN_SITE_HITL_WEBHOOK_ATTEMPT: "C-OD-32.3",
    _pause_ns.SPAN_SITE_PAUSE_CAPTURED: "C-OD-30.3",
    _pause_ns.SPAN_SITE_RESUME_ATTEMPTED: "C-OD-30.3",
}

#: The CONDITIONAL subtype of the same class — a floor that applies only under a stated
#: attribute. A first draft excluded these on the false premise that §9.2's conditional
#: rows covered them. They do not: those four rows are `files.operation`,
#: `memory.operation`, `validator.fail.*` and `subagent.span`
#: (`sampling_mode.py:176-190`). So these two are ALSO untracked floor cases.
_DECLARED_HEAD_ONE_CONDITIONAL: dict[str, str] = {
    _trust_ns.SPAN_SITE_MCP_TRUST_EVALUATE: "C-OD-31 (head=1.0 iff audit_required)",
    _burden_ns.SPAN_SITE_HITL_OPERATOR_BURDEN_EVALUATED: "C-OD-33 (head=1.0 iff degrade)",
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


def test_the_conditional_subtype_is_untracked_too() -> None:
    """The CONDITIONAL half of the class — two more untracked floor cases.

    A first draft of this module excluded these, claiming §9.2's conditional rows handled
    them. They do not: those rows are `files.operation`, `memory.operation`,
    `validator.fail.*` and `subagent.span`. Neither `mcp.trust.evaluate` nor the
    operator-burden span appears in the set OR in that conditional resolver, so when their
    stated condition holds the sampler still takes the base-rate path and can DROP them.
    """
    for name in _DECLARED_HEAD_ONE_CONDITIONAL:
        assert name not in ALWAYS_SAMPLED_EVENT_CLASSES, (
            f"{name} entered the floor set — re-ground B-160's conditional subtype"
        )

    conditional_rows = {"files.operation", "memory.operation", "validator.fail.*", "subagent.span"}
    assert conditional_rows <= set(ALWAYS_SAMPLED_EVENT_CLASSES), (
        "the §9.2 conditional rows moved — the exclusion reasoning above must be re-read"
    )
    assert not (set(_DECLARED_HEAD_ONE_CONDITIONAL) & conditional_rows), (
        "a conditional declaration became a §9.2 conditional row — that would CLOSE half "
        "of B-160's conditional subtype and must be recorded, not absorbed silently"
    )
