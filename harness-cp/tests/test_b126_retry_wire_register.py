"""Drift catchers for the `retry.*` wire surface — register row `B-126`.

`B-126` named three different cardinalities for one namespace (export manifest
4, code schema 6, wire 8) and observed that only the first was verified. The
grounding pass corrected the wire figure to TEN and found the divergence is not
a discretion free-for-all: `retry.*` is declared at TWO contract venues, and six
of the seven keys beyond C-CP-03 §3.5 are MANDATED by name at Runtime §14.6 /
§14.9. `RETRY_WIRE_REGISTER` records them; these tests keep the record true.

Two sweeps, deliberately different in shape, because either alone has a hole:

  * `test_every_retry_literal_in_src_is_declared_somewhere` — the BROAD sweep.
    Every `retry.`-prefixed string literal anywhere in `harness-*/src` must
    belong to one of the three declared buckets. Catches a new key of ANY shape
    (attribute, span name, sampling key) added without declaring it.
  * `test_emitted_attribute_keys_match_the_declared_emitted_set` — the PRECISE
    sweep. The keys actually SET as span attributes must equal the CP-declared
    subset plus the register's `emitted=True` rows. Catches an `emitted` flag
    that lies in either direction, which the broad sweep cannot see.

Together they also foreclose the cheap way to silence either one: relabelling an
emitted attribute as a span NAME keeps the broad union intact but drops it out
of the precise sweep's expectation, so the precise test fails.

Line numbers in `declaring_authority` strings are NOT asserted — the Runtime
spec is a delta chain whose line offsets move on every unrelated amendment, so
pinning them here would manufacture failures in arcs that touched nothing. The
named FILE is asserted to exist; the offsets are a reader's aid.
"""

from __future__ import annotations

import re
from pathlib import Path

from harness_cp.retry_fallback_namespace import (
    RETRY_NAMESPACE_SCHEMA,
    RETRY_SPAN_AND_EVENT_NAMES,
    RETRY_WIRE_REGISTER,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

#: Any `retry.`-prefixed literal. `"retry.*"` (the namespace NAME, as it appears
#: in the export manifest) deliberately does NOT match — `*` is outside the
#: class, and the namespace name is not a wire key.
_RETRY_LITERAL = re.compile(r'"(retry\.[a-z_.]+)"')

#: An attribute key in emission position: the first argument of
#: `set_attribute(...)`, or a key of an `attributes={...}` mapping.
_SET_ATTRIBUTE_KEY = re.compile(r'set_attribute\(\s*"(retry\.[^"]+)"')
_ATTRIBUTE_DICT_KEY = re.compile(r'"(retry\.[^"]+)"\s*:')

#: The `retry.`-prefixed subset of C-CP-03 §3.5. The sixth schema member is
#: `engine.replay_disposition`, which rides the `engine.*` namespace and is
#: correctly NOT a `retry.*` wire key.
_CP_DECLARED = frozenset(
    a.attribute_name for a in RETRY_NAMESPACE_SCHEMA if a.attribute_name.startswith("retry.")
)

_REGISTERED = frozenset(e.attribute_name for e in RETRY_WIRE_REGISTER)
_REGISTERED_EMITTED = frozenset(e.attribute_name for e in RETRY_WIRE_REGISTER if e.emitted)


def _src_modules() -> list[Path]:
    return [
        m for src in sorted(_REPO_ROOT.glob("harness-*/src")) for m in sorted(src.rglob("*.py"))
    ]


def _sweep(pattern: re.Pattern[str]) -> dict[str, set[str]]:
    """Every match of `pattern`, mapped to the modules it was found in."""
    found: dict[str, set[str]] = {}
    for module in _src_modules():
        for key in pattern.findall(module.read_text(encoding="utf-8")):
            found.setdefault(key, set()).add(module.relative_to(_REPO_ROOT).as_posix())
    return found


def test_the_sweep_reads_a_populated_source_tree() -> None:
    """A sweep over an empty file list passes every set comparison vacuously."""
    modules = _src_modules()
    assert len(modules) > 100, f"source sweep found only {len(modules)} modules"


def test_every_retry_literal_in_src_is_declared_somewhere() -> None:
    """The BROAD sweep — no undeclared `retry.`-prefixed literal in `src`.

    Expected set is the three buckets unioned. The register's `emitted=False`
    rows ARE expected here: they appear as literals in their own declaration,
    which is exactly where a mandated-but-unwired key should be visible.
    """
    expected = _CP_DECLARED | _REGISTERED | frozenset(RETRY_SPAN_AND_EVENT_NAMES)
    found = _sweep(_RETRY_LITERAL)

    undeclared = {k: sorted(v) for k, v in found.items() if k not in expected}
    assert not undeclared, (
        "undeclared `retry.*` literal(s) — add each to RETRY_WIRE_REGISTER with "
        f"its authorizing clause, or to RETRY_SPAN_AND_EVENT_NAMES: {undeclared}"
    )

    unused = expected - set(found)
    assert not unused, f"declared `retry.*` name(s) with no site in src: {sorted(unused)}"


def test_emitted_attribute_keys_match_the_declared_emitted_set() -> None:
    """The PRECISE sweep — the wire's attribute keys, exactly.

    This is `B-126`'s corrected count of TEN, re-derived by a sweep shape
    independent of the one that produced it: 5 CP-declared + 5 registered.
    """
    found = set(_sweep(_SET_ATTRIBUTE_KEY)) | set(_sweep(_ATTRIBUTE_DICT_KEY))
    expected = _CP_DECLARED | _REGISTERED_EMITTED

    assert found == expected, (
        "emitted `retry.*` attribute keys diverge from the declared set "
        f"(unregistered: {sorted(found - expected)}; "
        f"declared-emitted but never set: {sorted(expected - found)})"
    )
    assert len(found) == 10


def test_the_register_is_disjoint_from_the_cp_declared_schema() -> None:
    """The register is what §3.5 does NOT declare — overlap means one is wrong."""
    assert not (_REGISTERED & _CP_DECLARED)
    assert len(_CP_DECLARED) == 5
    assert len(RETRY_NAMESPACE_SCHEMA) == 6  # the sixth is `engine.replay_disposition`
    assert len(RETRY_WIRE_REGISTER) == 7


def test_names_are_not_attribute_keys() -> None:
    """A span/event name must never be counted as a wire attribute."""
    names = frozenset(RETRY_SPAN_AND_EVENT_NAMES)
    assert len(RETRY_SPAN_AND_EVENT_NAMES) == len(names) == 3
    assert not (names & _CP_DECLARED)
    assert not (names & _REGISTERED)


def test_unemitted_keys_are_exactly_the_two_b145_registers() -> None:
    """The mandated-but-unwired set is DATA, so closing it must edit this line.

    `retry.backoff_ms` and `retry.cause_class` are named at four Runtime step
    bullets and set by zero producers (`B-145`). Wiring either one flips its
    `emitted` flag, and this assertion forces that edit rather than letting the
    gap quietly disappear — or quietly grow.
    """
    unemitted = {e.attribute_name for e in RETRY_WIRE_REGISTER if not e.emitted}
    assert unemitted == {"retry.backoff_ms", "retry.cause_class"}


def test_every_registered_key_cites_an_authority_that_resolves() -> None:
    """Each row names a clause, and the spec file it names exists at HEAD."""
    for entry in RETRY_WIRE_REGISTER:
        assert "§" in entry.declaring_authority, entry.attribute_name
        cited = re.findall(r"([A-Za-z_0-9]+\.md)", entry.declaring_authority)
        assert cited, f"{entry.attribute_name} names no artifact"
        for name in cited:
            assert (_REPO_ROOT / "design-substrate" / name).is_file(), name


def test_most_of_the_wire_surface_beyond_cp_is_mandated_not_discretionary() -> None:
    """`B-126`'s load-bearing correction, pinned.

    The row was filed on the premise that these keys ride an unbounded
    telemetry-volume discretion lane. Grounding found the opposite: only
    `retry.skipped.candidate` is pure discretion; the other six are mandated by
    name. A future arc that re-reads this surface as "all discretionary" fails
    here.
    """
    discretionary = {e.attribute_name for e in RETRY_WIRE_REGISTER if not e.binding}
    assert discretionary == {"retry.skipped.candidate"}
